#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_FAILURE_CLASSES = {
    "CODE_DEFECT",
    "FIXTURE_DEFECT",
    "EVIDENCE_PACKAGING_DEFECT",
    "GOVERNANCE_DEFECT",
    "ENVIRONMENT_DEFECT",
    "EXTERNAL_INFRASTRUCTURE_FAILURE",
}
ALLOWED_PR_STATES = {"ACTIVE", "REVIEW_PENDING", "QUALIFIED", "SUPERSEDED", "HISTORICAL"}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "phase",
    "repository",
    "authoritative_source_sha",
    "candidate_sha",
    "checker_sha",
    "policy_id",
    "policy_version",
    "policy_hash",
    "required_checks",
    "required_review_type",
    "authority_required",
    "environment",
    "artifact_digest",
    "known_reds",
    "open_findings",
    "next_action",
}


class GovernanceError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_hex(name: str, value: str, size: int) -> None:
    matcher = HEX40 if size == 40 else HEX64
    if not isinstance(value, str) or not matcher.fullmatch(value):
        raise GovernanceError(f"{name} must be {size} lowercase hex characters")


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        raise GovernanceError("missing manifest fields: " + ", ".join(missing))
    extras = sorted(set(manifest) - REQUIRED_MANIFEST_FIELDS)
    if extras:
        raise GovernanceError("unexpected manifest fields: " + ", ".join(extras))
    if manifest["schema_version"] != 1:
        raise GovernanceError("schema_version must be 1")
    for field in ("authoritative_source_sha", "candidate_sha", "checker_sha"):
        _require_hex(field, manifest[field], 40)
    _require_hex("policy_hash", manifest["policy_hash"], 64)
    digest = manifest["artifact_digest"]
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise GovernanceError("artifact_digest must use sha256:<64-hex>")
    _require_hex("artifact_digest", digest.split(":", 1)[1], 64)
    if not isinstance(manifest["required_checks"], list) or not all(isinstance(x, str) and x for x in manifest["required_checks"]):
        raise GovernanceError("required_checks must be a non-empty-string list")
    if len(set(manifest["required_checks"])) != len(manifest["required_checks"]):
        raise GovernanceError("required_checks contains duplicates")
    if not isinstance(manifest["known_reds"], list) or not isinstance(manifest["open_findings"], list):
        raise GovernanceError("known_reds/open_findings must be lists")
    if not isinstance(manifest["authority_required"], bool):
        raise GovernanceError("authority_required must be boolean")
    if manifest["required_review_type"] not in {"NONE", "MANUAL_INDEPENDENT_REVIEW"}:
        raise GovernanceError("required_review_type must be NONE or MANUAL_INDEPENDENT_REVIEW")
    if not isinstance(manifest["policy_version"], int) or manifest["policy_version"] < 1:
        raise GovernanceError("policy_version must be positive integer")
    for field in ("phase", "repository", "policy_id", "environment", "next_action"):
        if not isinstance(manifest[field], str) or not manifest[field].strip():
            raise GovernanceError(f"{field} must be non-empty string")
    return manifest


def manifest_digest(manifest: dict[str, Any]) -> str:
    validate_manifest(manifest)
    return sha256_hex(canonical_json(manifest))


def validate_signature_b64(signature_b64: str, expected_len: int = 64) -> bytes:
    try:
        raw = base64.b64decode(signature_b64, validate=True)
    except Exception as exc:
        raise GovernanceError("signature is not valid base64") from exc
    if len(raw) != expected_len:
        raise GovernanceError(f"signature must decode to exactly {expected_len} bytes")
    return raw


def build_unsigned_attestation(manifest: dict[str, Any], *, authority_class: str, decision_scope: str, evidence_ref: str, trust_root_id: str) -> dict[str, Any]:
    validate_manifest(manifest)
    if not evidence_ref.startswith("sha256:"):
        raise GovernanceError("evidence_ref must be sha256-bound")
    _require_hex("evidence_ref", evidence_ref.split(":", 1)[1], 64)
    return {
        "schema_version": 1,
        "candidate_sha": manifest["candidate_sha"],
        "authority_class": authority_class,
        "decision_scope": decision_scope,
        "evidence_ref": evidence_ref,
        "source_kind": "MANUAL_GOVERNANCE_ATTESTATION",
        "qualification_policy_id": manifest["policy_id"],
        "qualification_policy_version": manifest["policy_version"],
        "qualification_policy_hash": manifest["policy_hash"],
        "trust_root_id": trust_root_id,
    }


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode:
        raise GovernanceError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def preflight(repo: Path, manifest: dict[str, Any], *, expected_branch: str | None = None) -> dict[str, Any]:
    validate_manifest(manifest)
    head = _git(repo, "rev-parse", "HEAD")
    if head != manifest["candidate_sha"]:
        raise GovernanceError(f"candidate SHA mismatch: HEAD={head} manifest={manifest['candidate_sha']}")
    _git(repo, "cat-file", "-e", f"{manifest['authoritative_source_sha']}^{{commit}}")
    _git(repo, "merge-base", "--is-ancestor", manifest["authoritative_source_sha"], manifest["candidate_sha"])
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if expected_branch and branch != expected_branch:
        raise GovernanceError(f"branch mismatch: expected {expected_branch}, got {branch}")
    return {
        "result": "PREFLIGHT_PASS",
        "candidate_sha": head,
        "branch": branch,
        "manifest_digest": manifest_digest(manifest),
    }


def classify_pr(*, merged: bool, open_state: bool, draft: bool, review_required: bool, review_satisfied: bool, superseded: bool, historical_only: bool) -> str:
    if historical_only:
        return "HISTORICAL"
    if superseded:
        return "SUPERSEDED"
    if merged:
        return "QUALIFIED"
    if open_state and review_required and not review_satisfied:
        return "REVIEW_PENDING"
    if open_state:
        return "ACTIVE"
    return "HISTORICAL"


def validate_evidence_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for record in records:
        ref = record.get("evidence_ref")
        if not isinstance(ref, str) or not ref.startswith("sha256:"):
            raise GovernanceError("every evidence record requires sha256 evidence_ref")
        _require_hex("evidence_ref", ref.split(":", 1)[1], 64)
        if ref in seen:
            raise GovernanceError(f"duplicate evidence_ref: {ref}")
        seen.add(ref)
        out.append(record)
    return out


def readiness_report(manifest: dict[str, Any], *, checks: dict[str, str], review_state: str, authority_state: str, last_red: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_manifest(manifest)
    missing = [name for name in manifest["required_checks"] if checks.get(name) != "SUCCESS"]
    blockers = list(manifest["open_findings"])
    if missing:
        blockers.append({"type": "CHECKS_NOT_GREEN", "checks": missing})
    if manifest["required_review_type"] == "MANUAL_INDEPENDENT_REVIEW" and review_state != "VERIFIED_PASS":
        blockers.append({"type": "MANUAL_REVIEW_NOT_VERIFIED", "state": review_state})
    if manifest["authority_required"] and authority_state != "VERIFIED":
        blockers.append({"type": "HUMAN_AUTHORITY_NOT_VERIFIED", "state": authority_state})
    return {
        "schema_version": 1,
        "phase": manifest["phase"],
        "candidate_sha": manifest["candidate_sha"],
        "manifest_digest": manifest_digest(manifest),
        "checks": checks,
        "review_state": review_state,
        "authority_state": authority_state,
        "known_red_count": len(manifest["known_reds"]),
        "last_red": last_red,
        "blockers": blockers,
        "ready": not blockers,
        "next_action": manifest["next_action"] if not blockers else "RESOLVE_BLOCKERS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A0 deterministic governance automation")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate-manifest")
    p_validate.add_argument("manifest")

    p_canon = sub.add_parser("canonicalize")
    p_canon.add_argument("json_file")
    p_canon.add_argument("--output", required=True)

    p_sig = sub.add_parser("verify-signature-shape")
    p_sig.add_argument("signature_b64_file")

    p_pre = sub.add_parser("preflight")
    p_pre.add_argument("manifest")
    p_pre.add_argument("--repo", default=".")
    p_pre.add_argument("--expected-branch")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-manifest":
            manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
            validate_manifest(manifest)
            print(json.dumps({"result": "VALID", "manifest_digest": manifest_digest(manifest)}, sort_keys=True))
        elif args.command == "canonicalize":
            value = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
            Path(args.output).write_bytes(canonical_json(value))
            print(json.dumps({"result": "WRITTEN", "sha256": sha256_hex(canonical_json(value))}, sort_keys=True))
        elif args.command == "verify-signature-shape":
            text = Path(args.signature_b64_file).read_text(encoding="ascii").strip()
            raw = validate_signature_b64(text)
            print(json.dumps({"result": "VALID_SHAPE", "bytes": len(raw)}, sort_keys=True))
        elif args.command == "preflight":
            manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
            print(json.dumps(preflight(Path(args.repo), manifest, expected_branch=args.expected_branch), sort_keys=True))
        return 0
    except (GovernanceError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"result": "FAIL_CLOSED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
