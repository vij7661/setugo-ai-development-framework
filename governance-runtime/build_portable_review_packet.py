#!/usr/bin/env python3
"""Build a self-contained review export from an exact governed commit.

The exported Actions artifact contains:
- a human-readable Markdown review packet;
- the exact ReviewRequest;
- a detached manifest;
- raw canonical repository files under raw-artifacts/.

Raw-file hashes, not fenced Markdown reconstruction, are the byte-authoritative integrity layer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from review_protocol import build_portable_review_bundle, verify_portable_review_bundle, verify_review_request

REVIEW_ARTIFACT_PATHS = [
    "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md",
    "governance-runtime/review_protocol.py",
    "governance-runtime/test_review_protocol.py",
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


def git_show_bytes(commit: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--ci-run-id", required=False, default="unknown")
    parser.add_argument("--builder-head", required=False, default="unknown")
    args = parser.parse_args()

    request_path = Path(args.request)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    ok, reason = verify_review_request(request)
    if not ok:
        raise SystemExit(f"INVALID_REVIEW_REQUEST: {reason}")

    review_id = request["review_request_id"]
    reviewed_commit = request["artifact"]["commit"]
    subprocess.run(["git", "cat-file", "-e", f"{reviewed_commit}^{{commit}}"], check=True)

    output_dir = Path(args.output_dir)
    raw_root = output_dir / "raw-artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_root.mkdir(parents=True, exist_ok=True)

    embedded = []
    manifest_entries = []
    for path in REVIEW_ARTIFACT_PATHS:
        raw = git_show_bytes(reviewed_commit, path)
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"NON_UTF8_REVIEW_ARTIFACT:{path}:{exc}") from exc
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

    reference_summaries = {}
    for ref in request.get("evidence_refs", []):
        if not isinstance(ref, dict):
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
            reference_summaries[key] = {"ref": ref_value, "source": "REVIEW_REQUEST_EMBEDDED_REFERENCE"}

    evidence_summary = {
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "repository_access_required": False,
        "packet_builder": "GITHUB_ACTIONS",
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
        "reference_summaries": reference_summaries,
        "raw_artifacts_authoritative_for_byte_integrity": True,
        "markdown_is_convenience_representation": True,
    }

    portable_bundle = build_portable_review_bundle(
        request=request,
        artifacts=embedded,
        evidence_summary=evidence_summary,
    )
    bundle_ok, bundle_reason = verify_portable_review_bundle(request=request, bundle=portable_bundle)
    if not bundle_ok:
        raise SystemExit(f"INVALID_PORTABLE_BUNDLE:{bundle_reason}")

    output_contract = {
        "review_request_id": review_id,
        "reviewed_artifact_commit": reviewed_commit,
        "reviewer": {"provider": "<reviewer self-claim; not authentication>", "model": "<reviewer self-claim; not authentication>"},
        "disposition": "PASS | BOUNDED_PASS | FAIL | NOT_TESTED | INSUFFICIENT_EVIDENCE | CHANGES_REQUIRED",
        "findings": [{"id":"F1","severity":"CRITICAL | HIGH | MEDIUM | LOW","title":"...","evidence":"...","impact":"...","required_change":"..."}],
        "evidence_assessment": "...",
        "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
    }

    parts = [
        f"# Independent Review Packet — {review_id}",
        "",
        "## Reviewer instructions",
        "",
        "- Repository/browser access required: **NO**.",
        "- Review only this export and its raw-artifacts/ directory.",
        "- Do not assume the proposer conclusion.",
        "- Do not mark PASS merely because CI is green.",
        f"- Exact reviewed candidate commit: `{reviewed_commit}`.",
        f"- Exact review request: `{review_id}`.",
        "- IMPORTANT: reviewer/provider/model fields in your JSON are content claims only. Manual relay does not authenticate provider identity.",
        "- Byte-integrity verification must use the raw files under `raw-artifacts/` and the detached manifest, not text reconstructed from Markdown fences.",
        "",
        "## Required output",
        "",
        "Return exactly one JSON object matching:",
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
        f"Logical portable-bundle SHA-256: `{portable_bundle['bundle_hash']}`",
    ]

    # Markdown copies are for reviewer convenience; hashes refer to raw exports above.
    for item in embedded:
        path, content = item["path"], item["content"]
        language = "python" if path.endswith(".py") else "json" if path.endswith((".json", ".jsonl")) else "yaml" if path.endswith((".yml", ".yaml")) else "markdown"
        parts.extend(["", f"## Convenience copy: `{path}`", f"```{language}", content.rstrip("\n"), "```"])

    packet_body = "\n".join(parts) + "\n"
    packet_body_sha256 = sha256_text(packet_body)
    packet = packet_body + (
        "\n## Export integrity\n\n"
        f"- packet_body_sha256: `{packet_body_sha256}`\n"
        f"- logical_bundle_sha256: `{portable_bundle['bundle_hash']}`\n"
        f"- review_request_id: `{review_id}`\n"
        f"- reviewed_candidate_commit: `{reviewed_commit}`\n"
        "- repository_access_required: `false`\n"
        "- raw_artifacts_are_byte_authoritative: `true`\n"
    )
    packet_file_sha256 = sha256_text(packet)
    packet_name = f"{review_id}-portable-review-packet.md"
    manifest_name = f"{review_id}.manifest.json"
    request_name = f"{review_id}.request.json"
    (output_dir / packet_name).write_text(packet, encoding="utf-8")
    (output_dir / request_name).write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": 3,
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "repository_access_required": False,
        "bundle_storage": "GITHUB_ACTIONS_ARTIFACT_EXPORT",
        "bundle_filename": packet_name,
        "request_filename": request_name,
        "bundle_body_sha256": packet_body_sha256,
        "bundle_file_sha256": packet_file_sha256,
        "logical_bundle_sha256": portable_bundle["bundle_hash"],
        "raw_artifacts_are_byte_authoritative": True,
        "covered_evidence_refs": request.get("evidence_refs", []),
        "embedded_artifacts": manifest_entries,
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
    }
    (output_dir / manifest_name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Independent local reproducibility check over exported raw bytes.
    for item in manifest_entries:
        raw = (output_dir / item["raw_export_path"]).read_bytes()
        if sha256_bytes(raw) != item["content_sha256"] or len(raw) != item["bytes_utf8"]:
            raise SystemExit(f"RAW_REPRODUCIBILITY_CHECK_FAILED:{item['path']}")

    print(
        "PORTABLE_REVIEW_EXPORT_BUILT "
        f"request={review_id} candidate={reviewed_commit} file_sha256={packet_file_sha256} "
        f"logical_bundle_sha256={portable_bundle['bundle_hash']} raw_artifacts={len(manifest_entries)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
