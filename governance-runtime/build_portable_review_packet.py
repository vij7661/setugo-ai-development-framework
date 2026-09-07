#!/usr/bin/env python3
"""Build deterministic review-context and external-evidence exports.

Platform review authority comes only from AUTOMATIC_API or USER_INITIATED_API
execution through a trusted provider adapter. This builder creates integrity-
bound context artifacts that may accompany or archive a ReviewRequest and may
also be used for external evidence gathering. Possession, inspection, or return
of an export never authenticates reviewer/provider identity and never creates a
platform review execution.

The historical single-file container field names are retained for backward
compatibility with the frozen GOV-PORTABLE-002 tests. Their semantics are now
explicitly external-evidence/context transport, not review authority.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from review_protocol import (
    build_portable_review_bundle,
    verify_portable_review_bundle,
    verify_review_request,
)

BASE_CONTEXT_PATHS = [
    "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md",
    "governance-runtime/review_protocol.py",
    "governance-runtime/validate_runtime.py",
    "governance-runtime/session-state.json",
    "governance-runtime/shared-memory.json",
    "governance-runtime/decision-log.jsonl",
    "governance-runtime/build_portable_review_packet.py",
    ".github/workflows/live-conversation-governance.yml",
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def git_show_bytes(commit: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout


def required_context_paths(request: Mapping[str, Any]) -> list[str]:
    """Derive exact context coverage from the ReviewRequest plus stable runtime files."""
    paths: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        if path and path not in seen:
            seen.add(path)
            paths.append(path)

    for path in BASE_CONTEXT_PATHS:
        add(path)
    for ref in request.get("evidence_refs", []):
        if not isinstance(ref, Mapping):
            raise ValueError("review request evidence ref is malformed")
        if ref.get("type") in {"file", "artifact"}:
            value = ref.get("ref")
            if not isinstance(value, str) or not value:
                raise ValueError("file evidence ref requires non-empty path")
            add(value)
    return paths


def build_single_file_container(
    *,
    request: Mapping[str, Any],
    embedded_artifacts: list[Mapping[str, Any]],
    evidence_summary: Mapping[str, Any],
    output_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one UTF-8 JSON document that reconstructs exact reviewed bytes."""
    records: list[dict[str, Any]] = []
    for item in embedded_artifacts:
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not path or not isinstance(content, str):
            raise ValueError("single-file artifact requires path and UTF-8 content")
        raw = content.encode("utf-8")
        records.append({
            "path": path,
            "encoding": "utf-8",
            "hash_basis": "RAW_GIT_BLOB_UTF8_BYTES_RECONSTRUCTED_BY_UTF8_ENCODING",
            "bytes_utf8": len(raw),
            "content_sha256": sha256_bytes(raw),
            "content": content,
        })

    payload: dict[str, Any] = {
        "schema_version": 1,
        "container_type": "SINGLE_FILE_MANUAL_REVIEW_EXPORT",
        "authority_class": "EXTERNAL_EVIDENCE_CONTEXT_EXPORT",
        "review_request_id": request["review_request_id"],
        "reviewed_candidate_commit": request["artifact"]["commit"],
        "repository_access_required": False,
        "manual_relay_upload_files_required": 1,
        "all_required_artifacts_embedded": True,
        "byte_reconstruction_rule": "UTF8_ENCODE_EACH_ARTIFACT_CONTENT_EXACTLY",
        "content_cannot_authenticate_reviewer_identity": True,
        "cannot_satisfy_platform_review_gate_by_itself": True,
        "review_request": deepcopy(dict(request)),
        "required_output": deepcopy(dict(output_contract)),
        "evidence_summary": deepcopy(dict(evidence_summary)),
        "artifacts": records,
    }
    payload_hash = sha256_bytes(canonical_json_bytes(payload))
    container = deepcopy(payload)
    container["container_payload_sha256"] = payload_hash
    return container


def verify_single_file_container(
    *,
    request: Mapping[str, Any],
    container: Mapping[str, Any],
    expected_paths: list[str] | None = None,
) -> tuple[bool, str]:
    try:
        material = deepcopy(dict(container))
        supplied_hash = material.pop("container_payload_sha256")
        if not isinstance(supplied_hash, str) or sha256_bytes(canonical_json_bytes(material)) != supplied_hash:
            return False, "single-file container payload hash is invalid"
        if container.get("schema_version") != 1 or container.get("container_type") != "SINGLE_FILE_MANUAL_REVIEW_EXPORT":
            return False, "single-file container schema/type invalid"
        if container.get("repository_access_required") is not False:
            return False, "single-file container must not require repository access"
        if container.get("manual_relay_upload_files_required") != 1:
            return False, "single-file container must require exactly one upload"
        if container.get("all_required_artifacts_embedded") is not True:
            return False, "single-file container does not assert complete embedding"
        if container.get("byte_reconstruction_rule") != "UTF8_ENCODE_EACH_ARTIFACT_CONTENT_EXACTLY":
            return False, "single-file reconstruction rule invalid"
        if container.get("review_request_id") != request.get("review_request_id"):
            return False, "single-file container rebound review request ID"
        if container.get("reviewed_candidate_commit") != request.get("artifact", {}).get("commit"):
            return False, "single-file container targets wrong candidate"
        embedded_request = container.get("review_request")
        if not isinstance(embedded_request, Mapping) or canonical_json_bytes(embedded_request) != canonical_json_bytes(request):
            return False, "single-file container rebound ReviewRequest semantics"

        artifacts = container.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            return False, "single-file container lacks artifacts"
        seen: list[str] = []
        for idx, item in enumerate(artifacts):
            if not isinstance(item, Mapping):
                return False, f"single-file artifact {idx} malformed"
            path = item.get("path")
            content = item.get("content")
            if not isinstance(path, str) or not path or not isinstance(content, str):
                return False, f"single-file artifact {idx} path/content invalid"
            if item.get("encoding") != "utf-8":
                return False, f"single-file artifact {path} encoding invalid"
            if item.get("hash_basis") != "RAW_GIT_BLOB_UTF8_BYTES_RECONSTRUCTED_BY_UTF8_ENCODING":
                return False, f"single-file artifact {path} hash basis invalid"
            raw = content.encode("utf-8")
            if item.get("bytes_utf8") != len(raw):
                return False, f"single-file artifact {path} byte length invalid"
            if item.get("content_sha256") != sha256_bytes(raw):
                return False, f"single-file artifact {path} content hash invalid"
            if path in seen:
                return False, f"single-file artifact duplicated: {path}"
            seen.append(path)
        if expected_paths is not None and set(seen) != set(expected_paths):
            return False, "single-file container artifact coverage differs from expected paths"
        return True, "single-file container verified"
    except (KeyError, TypeError, ValueError):
        return False, "single-file container malformed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--ci-run-id", required=False, default="unknown")
    parser.add_argument("--builder-head", required=False, default="unknown")
    args = parser.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    ok, reason = verify_review_request(request)
    if not ok:
        raise SystemExit(f"INVALID_REVIEW_REQUEST: {reason}")

    review_id = request["review_request_id"]
    reviewed_commit = request["artifact"]["commit"]
    subprocess.run(["git", "cat-file", "-e", f"{reviewed_commit}^{{commit}}"], check=True)

    try:
        context_paths = required_context_paths(request)
    except ValueError as exc:
        raise SystemExit(f"INVALID_CONTEXT_PATHS:{exc}") from exc

    output_dir = Path(args.output_dir)
    raw_root = output_dir / "raw-artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_root.mkdir(parents=True, exist_ok=True)

    embedded: list[dict[str, str]] = []
    manifest_entries: list[dict[str, Any]] = []
    for path in context_paths:
        try:
            raw = git_show_bytes(reviewed_commit, path)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"MISSING_REVIEW_CONTEXT_ARTIFACT:{path}") from exc
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"NON_UTF8_REVIEW_ARTIFACT:{path}:{exc}") from exc
        if content.encode("utf-8") != raw:
            raise SystemExit(f"UTF8_RECONSTRUCTION_MISMATCH:{path}")
        raw_path = raw_root / path
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw)
        digest = sha256_bytes(raw)
        embedded.append({"path": path, "content": content})
        manifest_entries.append({
            "path": path,
            "raw_export_path": f"raw-artifacts/{path}",
            "content_sha256": digest,
            "bytes_utf8": len(raw),
            "hash_basis": "RAW_GIT_BLOB_UTF8_BYTES",
        })
        if sha256_bytes(raw_path.read_bytes()) != digest:
            raise SystemExit(f"RAW_EXPORT_HASH_MISMATCH:{path}")

    reference_summaries: dict[str, Any] = {}
    for ref in request.get("evidence_refs", []):
        if not isinstance(ref, Mapping):
            raise SystemExit("INVALID_EVIDENCE_REF")
        ref_type, ref_value = ref.get("type"), ref.get("ref")
        key = f"{ref_type}:{ref_value}"
        if ref_type in {"file", "artifact", "portable_bundle"}:
            continue
        if ref_type == "ci_run":
            if str(ref_value) != str(args.ci_run_id):
                raise SystemExit("CI_RUN_EVIDENCE_REF_MISMATCH")
            reference_summaries[key] = {
                "ci_run_id": str(args.ci_run_id),
                "builder_head": args.builder_head,
                "source": "GITHUB_ACTIONS_BOUND_RUN",
            }
        else:
            reference_summaries[key] = {
                "ref": ref_value,
                "source": "REVIEW_REQUEST_EMBEDDED_REFERENCE",
            }

    evidence_summary = {
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "repository_access_required": False,
        "packet_builder": "GITHUB_ACTIONS",
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
        "reference_summaries": reference_summaries,
        "raw_artifacts_authoritative_for_byte_integrity": True,
        "single_file_container_reconstructs_raw_utf8_bytes": True,
        "markdown_is_convenience_representation": True,
        "authority_class": "EXTERNAL_EVIDENCE_CONTEXT_EXPORT",
        "provider_identity_authenticated_by_export": False,
    }

    portable_bundle = build_portable_review_bundle(
        request=request,
        artifacts=embedded,
        evidence_summary=evidence_summary,
    )
    bundle_ok, bundle_reason = verify_portable_review_bundle(
        request=request,
        bundle=portable_bundle,
    )
    if not bundle_ok:
        raise SystemExit(f"INVALID_PORTABLE_BUNDLE:{bundle_reason}")

    required_reviewer = request.get("required_reviewer", {})
    requested_provider = str(required_reviewer.get("provider", "unspecified"))
    requested_model = str(
        required_reviewer.get("model")
        or required_reviewer.get("model_class")
        or "unspecified"
    )
    required_dimensions = request.get("required_review_dimensions", [])

    output_contract: dict[str, Any] = {
        "review_request_id": review_id,
        "reviewed_artifact_commit": reviewed_commit,
        "reviewer": {
            "provider": "<content claim only>",
            "model": "<content claim only>",
        },
        "disposition": "PASS | BOUNDED_PASS | FAIL | NOT_TESTED | INSUFFICIENT_EVIDENCE | CHANGES_REQUIRED",
        "findings": [{
            "id": "F1",
            "severity": "CRITICAL | HIGH | MEDIUM | LOW",
            "title": "...",
            "evidence": "...",
            "impact": "...",
            "required_change": "...",
        }],
        "evidence_assessment": "...",
        "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
    }
    if required_dimensions:
        output_contract["review_coverage"] = [
            {
                "dimension_id": item["id"],
                "status": "TESTED_SUPPORTED | TESTED_DEFECT_FOUND | CONTRADICTED | NOT_TESTED | UNAVAILABLE | INACCESSIBLE | INSUFFICIENT",
                "evidence": ["<specific evidence reference or observation when tested>"],
                "assessment": "<what was actually tested/observed for this dimension>",
            }
            for item in required_dimensions
        ]

    single_container = build_single_file_container(
        request=request,
        embedded_artifacts=embedded,
        evidence_summary=evidence_summary,
        output_contract=output_contract,
    )
    single_ok, single_reason = verify_single_file_container(
        request=request,
        container=single_container,
        expected_paths=context_paths,
    )
    if not single_ok:
        raise SystemExit(f"INVALID_SINGLE_FILE_CONTAINER:{single_reason}")

    single_name = f"{review_id}-single-file-review.txt"
    single_path = output_dir / single_name
    single_path.write_text(
        json.dumps(single_container, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="",
    )
    persisted_single = json.loads(single_path.read_text(encoding="utf-8"))
    persisted_ok, persisted_reason = verify_single_file_container(
        request=request,
        container=persisted_single,
        expected_paths=context_paths,
    )
    if not persisted_ok:
        raise SystemExit(f"PERSISTED_SINGLE_FILE_INVALID:{persisted_reason}")
    single_file_sha256 = sha256_bytes(single_path.read_bytes())

    parts = [
        f"# Review Context Export — {review_id}",
        "",
        "## Provenance and authority notice",
        "",
        "- This export does not authenticate reviewer identity and does not create a platform review execution.",
        "- Platform review authority requires AUTOMATIC_API or USER_INITIATED_API through a trusted provider adapter.",
        "- If this export is manually given to another LLM, the returned material is external evidence. It remains USER_PROVIDED_EXTERNAL_CONTENT until the user explicitly identifies its source; user attestation still is not provider API authentication.",
        f"- Requested platform reviewer provider: `{requested_provider}`.",
        f"- Requested reviewer model/model-class: `{requested_model}`.",
        f"- Exact candidate: `{reviewed_commit}`.",
        f"- Exact ReviewRequest: `{review_id}`.",
        "- Repository/browser access required for this context export: **NO**.",
        "- Do not assume CI success or proposer conclusion proves correctness.",
        "- Re-encoding each artifact `content` string as UTF-8 must match its `bytes_utf8` and `content_sha256`.",
    ]
    if required_dimensions:
        parts.extend([
            "- Complete `review_coverage` for every required dimension if producing advisory external review content.",
            "- Do not claim PASS when any mandatory dimension is inaccessible, unavailable, untested, contradicted, or insufficient.",
        ])
    parts.extend([
        "",
        "## Expected review-shaped output contract",
        "```json",
        json.dumps(output_contract, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Exact ReviewRequest",
        "```json",
        json.dumps(request, indent=2, sort_keys=True, ensure_ascii=False),
        "```",
        "",
        "## Evidence coverage summary",
        "```json",
        json.dumps(evidence_summary, indent=2, sort_keys=True, ensure_ascii=False),
        "```",
        "",
        "## Raw artifact manifest",
        "```json",
        json.dumps(manifest_entries, indent=2, ensure_ascii=False),
        "```",
        "",
        f"Single-file context container: `{single_name}`",
        f"Single-file SHA-256: `{single_file_sha256}`",
        f"Single-file canonical payload SHA-256: `{single_container['container_payload_sha256']}`",
        f"Logical context-bundle SHA-256: `{portable_bundle['bundle_hash']}`",
    ])

    for item in embedded:
        path, content = item["path"], item["content"]
        language = (
            "python" if path.endswith(".py")
            else "json" if path.endswith((".json", ".jsonl"))
            else "yaml" if path.endswith((".yml", ".yaml"))
            else "markdown"
        )
        parts.extend([
            "",
            f"## Convenience copy: `{path}`",
            f"```{language}",
            content.rstrip("\n"),
            "```",
        ])

    packet_body = "\n".join(parts) + "\n"
    packet_body_sha256 = sha256_text(packet_body)
    packet = packet_body + (
        "\n## Export integrity\n\n"
        f"- packet_body_sha256: `{packet_body_sha256}`\n"
        f"- logical_bundle_sha256: `{portable_bundle['bundle_hash']}`\n"
        f"- single_file_container_sha256: `{single_file_sha256}`\n"
        f"- single_file_payload_sha256: `{single_container['container_payload_sha256']}`\n"
        f"- review_request_id: `{review_id}`\n"
        f"- reviewed_candidate_commit: `{reviewed_commit}`\n"
        "- repository_access_required: `false`\n"
        "- raw_artifacts_are_byte_authoritative: `true`\n"
        "- authority_class: `EXTERNAL_EVIDENCE_CONTEXT_EXPORT`\n"
        "- provider_identity_authenticated_by_export: `false`\n"
        "- manual_relay_upload_files_required: `1` (legacy compatibility field only)\n"
    )
    packet_file_sha256 = sha256_text(packet)
    packet_name = f"{review_id}-portable-review-packet.md"
    manifest_name = f"{review_id}.manifest.json"
    request_name = f"{review_id}.request.json"
    (output_dir / packet_name).write_text(packet, encoding="utf-8")
    (output_dir / request_name).write_text(
        json.dumps(request, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": 4 if required_dimensions else 3,
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "requested_reviewer": dict(required_reviewer),
        "required_review_dimensions": required_dimensions,
        "repository_access_required": False,
        "authority_class": "EXTERNAL_EVIDENCE_CONTEXT_EXPORT",
        "provider_identity_authenticated_by_export": False,
        "bundle_storage": "GITHUB_ACTIONS_ARTIFACT_EXPORT",
        "bundle_filename": packet_name,
        "request_filename": request_name,
        "bundle_body_sha256": packet_body_sha256,
        "bundle_file_sha256": packet_file_sha256,
        "logical_bundle_sha256": portable_bundle["bundle_hash"],
        "raw_artifacts_are_byte_authoritative": True,
        "single_file_container_filename": single_name,
        "single_file_container_schema": 1,
        "single_file_container_sha256": single_file_sha256,
        "single_file_container_payload_sha256": single_container["container_payload_sha256"],
        "single_file_embeds_all_raw_artifacts": True,
        "manual_relay_upload_files_required": 1,
        "single_file_reconstruction_basis": "UTF8_ENCODE_EACH_ARTIFACT_CONTENT_EXACTLY",
        "covered_evidence_refs": request.get("evidence_refs", []),
        "embedded_artifacts": manifest_entries,
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
    }
    (output_dir / manifest_name).write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    for item in manifest_entries:
        raw = (output_dir / item["raw_export_path"]).read_bytes()
        if sha256_bytes(raw) != item["content_sha256"] or len(raw) != item["bytes_utf8"]:
            raise SystemExit(f"RAW_REPRODUCIBILITY_CHECK_FAILED:{item['path']}")

    print(
        "REVIEW_CONTEXT_EXPORT_BUILT "
        f"request={review_id} candidate={reviewed_commit} requested_provider={requested_provider} "
        f"semantic_dimensions={len(required_dimensions)} file_sha256={packet_file_sha256} "
        f"single_file_sha256={single_file_sha256} "
        f"single_file_payload_sha256={single_container['container_payload_sha256']} "
        f"logical_bundle_sha256={portable_bundle['bundle_hash']} "
        f"raw_artifacts={len(manifest_entries)} authority_class=EXTERNAL_EVIDENCE_CONTEXT_EXPORT"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
