#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
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


def generate_manifest(
    *, phase: str, repository: str, authoritative_source_sha: str, candidate_sha: str,
    checker_sha: str, policy_id: str, policy_version: int, policy_hash: str,
    required_checks: list[str], required_review_type: str, authority_required: bool,
    environment: str, artifact_digest: str, known_reds: list[Any], open_findings: list[Any],
    next_action: str,
) -> dict[str, Any]:
    manifest = {
        "schema_version": 1,
        "phase": phase,
        "repository": repository,
        "authoritative_source_sha": authoritative_source_sha,
        "candidate_sha": candidate_sha,
        "checker_sha": checker_sha,
        "policy_id": policy_id,
        "policy_version": policy_version,
        "policy_hash": policy_hash,
        "required_checks": required_checks,
        "required_review_type": required_review_type,
        "authority_required": authority_required,
        "environment": environment,
        "artifact_digest": artifact_digest,
        "known_reds": known_reds,
        "open_findings": open_findings,
        "next_action": next_action,
    }
    return validate_manifest(manifest)


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
    return {"result": "PREFLIGHT_PASS", "candidate_sha": head, "branch": branch, "manifest_digest": manifest_digest(manifest)}


def post_action_verify(repo: Path, *, expected_branch: str, expected_tip: str, required_ancestor: str) -> dict[str, Any]:
    _require_hex("expected_tip", expected_tip, 40)
    _require_hex("required_ancestor", required_ancestor, 40)
    tip = _git(repo, "rev-parse", expected_branch)
    if tip != expected_tip:
        raise GovernanceError(f"post-action branch tip mismatch: expected {expected_tip}, got {tip}")
    _git(repo, "merge-base", "--is-ancestor", required_ancestor, expected_tip)
    return {"result": "POST_ACTION_VERIFIED", "branch": expected_branch, "tip": tip, "required_ancestor": required_ancestor}


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


def audit_pr_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for item in records:
        result = dict(item)
        result["lifecycle_state"] = classify_pr(
            merged=bool(item.get("merged")),
            open_state=item.get("state") == "open",
            draft=bool(item.get("draft")),
            review_required=bool(item.get("review_required")),
            review_satisfied=bool(item.get("review_satisfied")),
            superseded=bool(item.get("superseded")),
            historical_only=bool(item.get("historical_only")),
        )
        out.append(result)
    return out


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


def build_review_packet(repo: Path, manifest: dict[str, Any], paths: list[str]) -> str:
    validate_manifest(manifest)
    if manifest["required_review_type"] != "MANUAL_INDEPENDENT_REVIEW":
        raise GovernanceError("review packet builder requires MANUAL_INDEPENDENT_REVIEW manifest")
    if not paths:
        raise GovernanceError("review packet requires at least one path")
    sections = [
        "# Manual Independent Review Packet",
        "",
        f"Candidate: `{manifest['candidate_sha']}`",
        f"Authoritative source: `{manifest['authoritative_source_sha']}`",
        f"Manifest SHA-256: `{manifest_digest(manifest)}`",
        "",
        "## Reviewer instruction",
        "Treat this packet as evidence only. Do not grant terminal authority. Identify concrete false-green paths, missing evidence, stale bindings, authority bypasses, and unsupported PASS conditions.",
        "",
        "## Included artifacts",
    ]
    seen: set[str] = set()
    for rel in paths:
        if rel in seen:
            raise GovernanceError(f"duplicate review packet path: {rel}")
        seen.add(rel)
        p = (repo / rel).resolve()
        try:
            p.relative_to(repo.resolve())
        except ValueError as exc:
            raise GovernanceError(f"path escapes repository: {rel}") from exc
        if not p.is_file():
            raise GovernanceError(f"review packet path is not a file: {rel}")
        data = p.read_bytes()
        digest = sha256_hex(data)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GovernanceError(f"review packet only supports UTF-8 text: {rel}") from exc
        sections += ["", f"### `{rel}`", f"- bytes: {len(data)}", f"- sha256: `{digest}`", "", "```text", text, "```"]
    return "\n".join(sections) + "\n"


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


def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


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

    p_ready = sub.add_parser("readiness")
    p_ready.add_argument("manifest")
    p_ready.add_argument("checks_json")
    p_ready.add_argument("--review-state", required=True)
    p_ready.add_argument("--authority-state", required=True)
    p_ready.add_argument("--last-red-json")

    p_att = sub.add_parser("build-unsigned-attestation")
    p_att.add_argument("manifest")
    p_att.add_argument("--authority-class", required=True)
    p_att.add_argument("--decision-scope", required=True)
    p_att.add_argument("--evidence-ref", required=True)
    p_att.add_argument("--trust-root-id", required=True)
    p_att.add_argument("--output", required=True)

    p_packet = sub.add_parser("build-review-packet")
    p_packet.add_argument("manifest")
    p_packet.add_argument("--repo", default=".")
    p_packet.add_argument("--path", action="append", required=True)
    p_packet.add_argument("--output", required=True)

    p_audit = sub.add_parser("audit-prs")
    p_audit.add_argument("prs_json")

    p_post = sub.add_parser("post-action-verify")
    p_post.add_argument("--repo", default=".")
    p_post.add_argument("--expected-branch", required=True)
    p_post.add_argument("--expected-tip", required=True)
    p_post.add_argument("--required-ancestor", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-manifest":
            manifest = _load_json(args.manifest)
            validate_manifest(manifest)
            print(json.dumps({"result": "VALID", "manifest_digest": manifest_digest(manifest)}, sort_keys=True))
        elif args.command == "canonicalize":
            value = _load_json(args.json_file)
            data = canonical_json(value)
            Path(args.output).write_bytes(data)
            print(json.dumps({"result": "WRITTEN", "sha256": sha256_hex(data)}, sort_keys=True))
        elif args.command == "verify-signature-shape":
            text = Path(args.signature_b64_file).read_text(encoding="ascii").strip()
            raw = validate_signature_b64(text)
            print(json.dumps({"result": "VALID_SHAPE", "bytes": len(raw)}, sort_keys=True))
        elif args.command == "preflight":
            print(json.dumps(preflight(Path(args.repo), _load_json(args.manifest), expected_branch=args.expected_branch), sort_keys=True))
        elif args.command == "readiness":
            report = readiness_report(
                _load_json(args.manifest), checks=_load_json(args.checks_json), review_state=args.review_state,
                authority_state=args.authority_state, last_red=_load_json(args.last_red_json) if args.last_red_json else None,
            )
            print(json.dumps(report, sort_keys=True))
        elif args.command == "build-unsigned-attestation":
            att = build_unsigned_attestation(
                _load_json(args.manifest), authority_class=args.authority_class, decision_scope=args.decision_scope,
                evidence_ref=args.evidence_ref, trust_root_id=args.trust_root_id,
            )
            Path(args.output).write_bytes(canonical_json(att))
            print(json.dumps({"result": "UNSIGNED_ATTESTATION_WRITTEN", "sha256": sha256_hex(canonical_json(att))}, sort_keys=True))
        elif args.command == "build-review-packet":
            packet = build_review_packet(Path(args.repo), _load_json(args.manifest), args.path)
            Path(args.output).write_text(packet, encoding="utf-8")
            print(json.dumps({"result": "REVIEW_PACKET_WRITTEN", "sha256": sha256_hex(packet.encode('utf-8'))}, sort_keys=True))
        elif args.command == "audit-prs":
            print(json.dumps(audit_pr_records(_load_json(args.prs_json)), sort_keys=True))
        elif args.command == "post-action-verify":
            print(json.dumps(post_action_verify(Path(args.repo), expected_branch=args.expected_branch, expected_tip=args.expected_tip, required_ancestor=args.required_ancestor), sort_keys=True))
        return 0
    except (GovernanceError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"result": "FAIL_CLOSED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
