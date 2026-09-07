#!/usr/bin/env python3
"""Build a self-contained independent-review packet from an exact governed commit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from review_protocol import verify_review_request

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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_show(commit: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.decode("utf-8")


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

    embedded = []
    for path in REVIEW_ARTIFACT_PATHS:
        content = git_show(reviewed_commit, path)
        embedded.append({
            "path": path,
            "content": content,
            "content_sha256": sha256_text(content),
            "bytes_utf8": len(content.encode("utf-8")),
        })

    evidence_summary = {
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "repository_access_required": False,
        "packet_builder": "GITHUB_ACTIONS",
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
        "note": "The reviewer must use only this packet; repository access is not required.",
    }

    output_contract = {
        "review_request_id": review_id,
        "reviewed_artifact_commit": reviewed_commit,
        "reviewer": {"provider": "anthropic", "model": "<exact Claude model used>"},
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

    parts = [
        f"# Independent Review Packet — {review_id}",
        "",
        "## Reviewer instructions",
        "",
        "- Reviewer: Claude / Anthropic.",
        "- Repository access required: **NO**.",
        "- Browser/tool access required: **NO**.",
        "- Review only the evidence embedded in this packet.",
        "- Do not assume the proposer conclusion.",
        "- Do not mark PASS merely because CI is green.",
        "- Required independence attestation: `BLIND_TO_PROPOSER_CONCLUSION`.",
        f"- Exact reviewed candidate commit: `{reviewed_commit}`.",
        f"- Exact review request: `{review_id}`.",
        "",
        "## Required output",
        "",
        "Return exactly one JSON object matching:",
        "",
        "```json",
        json.dumps(output_contract, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Exact ReviewRequest",
        "",
        "```json",
        json.dumps(request, indent=2, sort_keys=True, ensure_ascii=False),
        "```",
        "",
        "## Evidence summary",
        "",
        "```json",
        json.dumps(evidence_summary, indent=2, sort_keys=True, ensure_ascii=False),
        "```",
    ]

    manifest_entries = []
    for item in embedded:
        manifest_entries.append({
            "path": item["path"],
            "content_sha256": item["content_sha256"],
            "bytes_utf8": item["bytes_utf8"],
        })
        language = "python" if item["path"].endswith(".py") else "json" if item["path"].endswith((".json", ".jsonl")) else "yaml" if item["path"].endswith((".yml", ".yaml")) else "markdown"
        parts.extend([
            "",
            f"## Artifact: `{item['path']}`",
            "",
            f"SHA-256: `{item['content_sha256']}`",
            "",
            f"```{language}",
            item["content"].rstrip("\n"),
            "```",
        ])

    packet_body = "\n".join(parts) + "\n"
    packet_body_sha256 = sha256_text(packet_body)
    packet = packet_body + (
        "\n## Portable packet integrity\n\n"
        f"- packet_body_sha256: `{packet_body_sha256}`\n"
        f"- review_request_id: `{review_id}`\n"
        f"- reviewed_candidate_commit: `{reviewed_commit}`\n"
        "- repository_access_required: `false`\n"
        "- The detached governed manifest binds the SHA-256 of this entire exported file.\n"
    )
    packet_file_sha256 = sha256_text(packet)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_name = f"{review_id}-portable-review-packet.md"
    manifest_name = f"{review_id}.manifest.json"
    (output_dir / packet_name).write_text(packet, encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "review_request_id": review_id,
        "reviewed_candidate_commit": reviewed_commit,
        "repository_access_required": False,
        "bundle_storage": "GITHUB_ACTIONS_ARTIFACT_EXPORT",
        "bundle_filename": packet_name,
        "bundle_body_sha256": packet_body_sha256,
        "bundle_file_sha256": packet_file_sha256,
        "embedded_artifacts": manifest_entries,
        "builder_execution_head": args.builder_head,
        "builder_ci_run_id": str(args.ci_run_id),
    }
    (output_dir / manifest_name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        "PORTABLE_REVIEW_PACKET_BUILT "
        f"request={review_id} candidate={reviewed_commit} "
        f"file_sha256={packet_file_sha256} artifacts={len(manifest_entries)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
