#!/usr/bin/env python3
"""Deterministic preflight gate for clean independent-review packets.

This validator is intentionally repository/network independent. It verifies the
assembled packet bytes against a declarative review-surface manifest and fails
closed before a packet can be sent to an independent reviewer.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

SHA1_40 = re.compile(r"^[0-9a-f]{40}$")
SHA256_64 = re.compile(r"^[0-9a-f]{64}$")
BEGIN_ARTIFACT = re.compile(
    r"<!-- BEGIN EXACT ARTIFACT path=(?P<path>\S+) blob=(?P<blob>[0-9a-f]{40}) -->\n"
)
END_ARTIFACT_TEMPLATE = r"<!-- END EXACT ARTIFACT path={path} -->"

PACKET_READY = "PACKET_READY"
PACKET_INVALID = "PACKET_INVALID"

@dataclass(frozen=True)
class Check:
    check_id: str
    status: str
    detail: str

def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()

def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value

def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")
    return value

def verify_manifest(manifest: Mapping[str, Any]) -> tuple[bool, str]:
    try:
        if manifest.get("schema_version") != 1:
            return False, "unsupported manifest schema"
        if manifest.get("packet_class") not in {
            "CLEAN_INDEPENDENT_REVIEW",
            "GOVERNED_INDEPENDENT_REVIEW",
        }:
            return False, "invalid packet_class"
        commit = manifest.get("candidate_commit")
        if not isinstance(commit, str) or not SHA1_40.fullmatch(commit):
            return False, "candidate_commit must be exact lowercase 40-char Git SHA"
        artifacts = _require_list(manifest.get("required_artifacts"), "required_artifacts")
        if not artifacts:
            return False, "required_artifacts must not be empty"
        paths: set[str] = set()
        for idx, item in enumerate(artifacts):
            item = _require_mapping(item, f"required_artifacts[{idx}]")
            path, blob = item.get("path"), item.get("git_blob_sha")
            if not isinstance(path, str) or not path or path in paths:
                return False, "artifact paths must be unique non-empty strings"
            if not isinstance(blob, str) or not SHA1_40.fullmatch(blob):
                return False, f"artifact {path} git_blob_sha invalid"
            if item.get("review_surface", "FULL_TEXT") != "FULL_TEXT":
                return False, f"artifact {path} must be FULL_TEXT review surface"
            paths.add(path)
        for key in ("required_clause_ids", "required_case_ids", "forbidden_strings"):
            _require_list(manifest.get(key, []), key)
        return True, "manifest verified"
    except (TypeError, ValueError):
        return False, "manifest malformed"

def _extract_artifacts(packet_text: str) -> tuple[dict[str, tuple[str, str]], list[str]]:
    """Return path -> (declared blob, exact content) and structural errors."""
    found: dict[str, tuple[str, str]] = {}
    errors: list[str] = []
    matches = list(BEGIN_ARTIFACT.finditer(packet_text))
    for i, match in enumerate(matches):
        path = match.group("path")
        blob = match.group("blob")
        if path in found:
            errors.append(f"duplicate embedded artifact: {path}")
            continue
        content_start = match.end()
        end_re = re.compile(END_ARTIFACT_TEMPLATE.format(path=re.escape(path)))
        end_match = end_re.search(packet_text, content_start)
        if not end_match:
            errors.append(f"missing END marker for artifact: {path}")
            continue
        segment = packet_text[content_start:end_match.start()]
        found[path] = (blob, segment)
    return found, errors

def _definition_present(packet_text: str, identifier: str) -> bool:
    pattern = re.compile(
        rf"(?m)^#{{1,6}}\s+{re.escape(identifier)}(?:\s|$|—|-)"
    )
    return bool(pattern.search(packet_text))

def validate_packet(packet_text: str, manifest: Mapping[str, Any]) -> dict[str, Any]:
    ok, reason = verify_manifest(manifest)
    if not ok:
        return {
            "schema_version": 1,
            "result": PACKET_INVALID,
            "checks": [asdict(Check("MANIFEST", "FAIL", reason))],
        }

    checks: list[Check] = []
    embedded, structural_errors = _extract_artifacts(packet_text)
    if structural_errors:
        for err in structural_errors:
            checks.append(Check("ARTIFACT_STRUCTURE", "FAIL", err))

    required_paths = {str(x["path"]) for x in manifest["required_artifacts"]}
    embedded_paths = set(embedded)

    for item in manifest["required_artifacts"]:
        path = str(item["path"])
        expected_blob = str(item["git_blob_sha"])
        if path not in embedded:
            checks.append(Check("ARTIFACT_PRESENT", "FAIL", f"{path}: MISSING"))
            continue
        declared_blob, content = embedded[path]
        raw = content.encode("utf-8")
        actual_blob = git_blob_sha1(raw)
        if declared_blob != expected_blob:
            checks.append(Check(
                "ARTIFACT_DECLARED_BLOB",
                "FAIL",
                f"{path}: marker={declared_blob} expected={expected_blob}",
            ))
        elif actual_blob != expected_blob:
            checks.append(Check(
                "ARTIFACT_HASH",
                "FAIL",
                f"{path}: HASH_MISMATCH actual={actual_blob} expected={expected_blob}",
            ))
        else:
            checks.append(Check("ARTIFACT_HASH", "PASS", f"{path}: PRESENT+HASH_MATCH"))

    extras = sorted(embedded_paths - required_paths)
    if extras and manifest.get("reject_unlisted_artifacts", True):
        checks.append(Check("UNLISTED_ARTIFACT", "FAIL", ",".join(extras)))
    else:
        checks.append(Check("UNLISTED_ARTIFACT", "PASS", "none"))

    for identifier in manifest.get("required_clause_ids", []):
        if not isinstance(identifier, str) or not identifier:
            checks.append(Check("CLAUSE_DEFINITION", "FAIL", "invalid clause id in manifest"))
        elif _definition_present(packet_text, identifier):
            checks.append(Check("CLAUSE_DEFINITION", "PASS", identifier))
        else:
            checks.append(Check("CLAUSE_DEFINITION", "FAIL", f"{identifier}: MISSING_DEFINITION"))

    for identifier in manifest.get("required_case_ids", []):
        if not isinstance(identifier, str) or not identifier:
            checks.append(Check("CASE_DEFINITION", "FAIL", "invalid case id in manifest"))
        elif _definition_present(packet_text, identifier):
            checks.append(Check("CASE_DEFINITION", "PASS", identifier))
        else:
            checks.append(Check("CASE_DEFINITION", "FAIL", f"{identifier}: MISSING_DEFINITION"))

    for forbidden in manifest.get("forbidden_strings", []):
        if not isinstance(forbidden, str) or not forbidden:
            checks.append(Check("CLEAN_ROOM", "FAIL", "invalid forbidden string in manifest"))
        elif forbidden in packet_text:
            checks.append(Check("CLEAN_ROOM", "FAIL", f"forbidden prior-review text present: {forbidden!r}"))
        else:
            checks.append(Check("CLEAN_ROOM", "PASS", f"absent: {forbidden!r}"))

    candidate = str(manifest["candidate_commit"])
    required_candidate_occurrences = int(manifest.get("min_candidate_commit_occurrences", 1))
    occurrences = packet_text.count(candidate)
    if occurrences < required_candidate_occurrences:
        checks.append(Check(
            "CANDIDATE_BINDING",
            "FAIL",
            f"candidate SHA occurrences={occurrences}, required>={required_candidate_occurrences}",
        ))
    else:
        checks.append(Check("CANDIDATE_BINDING", "PASS", f"candidate SHA occurrences={occurrences}"))

    packet_sha = sha256(packet_text.encode("utf-8"))
    failed = any(c.status == "FAIL" for c in checks)
    return {
        "schema_version": 1,
        "result": PACKET_INVALID if failed else PACKET_READY,
        "candidate_commit": candidate,
        "packet_sha256": packet_sha,
        "required_artifact_count": len(required_paths),
        "embedded_artifact_count": len(embedded_paths),
        "required_clause_count": len(manifest.get("required_clause_ids", [])),
        "required_case_count": len(manifest.get("required_case_ids", [])),
        "checks": [asdict(c) for c in checks],
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    packet_path = Path(args.packet)
    manifest_path = Path(args.manifest)
    packet_text = packet_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = validate_packet(packet_text, manifest)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["result"] == PACKET_READY else 2

if __name__ == "__main__":
    raise SystemExit(main())
