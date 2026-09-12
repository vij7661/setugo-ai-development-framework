#!/usr/bin/env python3
"""Assemble a clean review packet and refuse output unless deterministic preflight passes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from review_packet_preflight import git_blob_sha1, validate_packet, PACKET_READY

def assemble(repo_root: Path, manifest: Mapping[str, Any]) -> str:
    prompt = manifest.get("review_prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("manifest.review_prompt must be non-empty")
    candidate = str(manifest["candidate_commit"])
    packet = (
        "# Governed Clean Independent Review Packet\n\n"
        f"Exact candidate commit: `{candidate}`\n\n"
        "## Review instructions\n\n"
        + prompt.rstrip()
        + "\n\n## Exact review surface\n\n"
    )
    for item in manifest["required_artifacts"]:
        path = str(item["path"])
        expected = str(item["git_blob_sha"])
        source = repo_root / path
        raw = source.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"non-UTF8 review artifact: {path}") from exc
        actual = git_blob_sha1(raw)
        if actual != expected:
            raise ValueError(
                f"artifact blob mismatch before packet assembly: {path}: {actual} != {expected}"
            )
        packet += (
            f"<!-- BEGIN EXACT ARTIFACT path={path} blob={expected} -->\n"
            + content
            + f"<!-- END EXACT ARTIFACT path={path} -->\n\n"
        )
    return packet

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    packet = assemble(repo_root, manifest)
    report = validate_packet(packet, manifest)
    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["result"] != PACKET_READY:
        out = Path(args.output)
        if out.exists():
            out.unlink()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2
    Path(args.output).write_text(packet, encoding="utf-8", newline="")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
