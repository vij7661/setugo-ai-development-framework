"""Verify the EXP-M source -> evidence -> packet sequence."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path

from verify_exp_m_prior_evidence import verify_prior_evidence_index

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json"
EVIDENCE_MANIFEST_PATH = "experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json"
PACKET_CONTENT_PATH = "experiments/governed-platform/EXP-M-R2E-PACKET-CONTENT.md"

REVIEWER_SUITE_ANCHORS = (
    ("governance-runtime/reviewer_exp_m_r2e_suite.py", "04913502b7ea1dcb11d551b2bec27c5a8d9c4a8a"),
    ("governance-runtime/reviewer_exp_m_r2e_authority_suite.py", "a7b5e5ac59a3da745a6ac06d828763be59ab9668"),
    ("governance-runtime/reviewer_exp_m_r2e_compound_suite.py", "4c70788b9fc8c8ec93f5ea90bedc762c827f090a"),
)
REVIEWER_SUITE_PATHS = tuple(path for path, _ in REVIEWER_SUITE_ANCHORS)
FORBIDDEN_REVIEWER_SUITE_TOKENS = (
    "run_exp_m_mutations",
    "run_exp_m_deterministic",
    "_predicate_validators",
    "self_falsify_exp_m",
)


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _json_at(commit: str, path: str) -> dict:
    return json.loads(_git_bytes(commit, path))


def _sha256_at(commit: str, path: str) -> str:
    return hashlib.sha256(_git_bytes(commit, path)).hexdigest()


def _diff_paths(a: str, b: str) -> list[str]:
    out = _git("diff", "--name-only", a, b)
    return [x for x in out.splitlines() if x]


def _allowed_evidence_path(path: str) -> bool:
    return (
        path.startswith("experiments/governed-platform/EXP-M-")
        and (path.endswith(".json") or path.endswith(".txt"))
    )


def _allowed_packet_path(path: str) -> bool:
    return path.startswith("experiments/governed-platform/EXP-M-") and path.endswith(".md")


def verify_reviewer_suite_frozen(*, simulate_suite_mutation: bool = False) -> tuple[bool, tuple[str, ...]]:
    if simulate_suite_mutation:
        return False, ("reviewer_suite_hash_drift",)
    freeze_file = ROOT / FREEZE_PATH
    if not freeze_file.exists():
        return False, ("source_freeze_missing",)
    freeze = json.loads(freeze_file.read_text(encoding="utf-8"))
    source_commit = str(freeze.get("source_commit", ""))
    source_files = freeze.get("source_files") or {}
    reasons: list[str] = []
    for path, preregister_commit in REVIEWER_SUITE_ANCHORS:
        expected = source_files.get(path)
        if not expected:
            reasons.append(f"reviewer_suite_not_in_source_freeze:{path}")
            continue
        try:
            source_bytes = _git_bytes(source_commit, path)
        except subprocess.CalledProcessError:
            reasons.append(f"reviewer_suite_missing_from_source:{path}")
            continue
        actual = hashlib.sha256(source_bytes).hexdigest()
        if actual != expected:
            reasons.append("reviewer_suite_hash_drift")
        try:
            frozen_bytes = _git_bytes(preregister_commit, path)
        except subprocess.CalledProcessError:
            reasons.append(f"reviewer_suite_preregister_object_missing:{path}")
            continue
        if hashlib.sha256(frozen_bytes).hexdigest() != actual:
            reasons.append("reviewer_suite_preregister_hash_drift")
        source_text = source_bytes.decode("utf-8", errors="replace")
        if any(token in source_text for token in FORBIDDEN_REVIEWER_SUITE_TOKENS):
            reasons.append("reviewer_suite_forbidden_dependency")
    return not reasons, tuple(dict.fromkeys(reasons))


def verify_sep_sequence(source_commit: str, evidence_commit: str, packet_commit: str) -> tuple[bool, tuple[str, ...], dict]:
    reasons: list[str] = []
    details: dict = {
        "source_commit": source_commit,
        "evidence_commit": evidence_commit,
        "packet_commit": packet_commit,
    }

    try:
        source_tree = _git("rev-parse", f"{source_commit}^{{tree}}")
        evidence_tree = _git("rev-parse", f"{evidence_commit}^{{tree}}")
        packet_tree = _git("rev-parse", f"{packet_commit}^{{tree}}")
    except subprocess.CalledProcessError:
        return False, ("sep_commit_missing",), details
    details.update(source_tree=source_tree, evidence_tree=evidence_tree, packet_tree=packet_tree)

    try:
        evidence_parent = _git("rev-parse", f"{evidence_commit}^")
        packet_parent = _git("rev-parse", f"{packet_commit}^")
    except subprocess.CalledProcessError:
        reasons.append("sep_parent_resolution_failed")
    else:
        details["evidence_parent"] = evidence_parent
        details["packet_parent"] = packet_parent
        if evidence_parent != source_commit:
            reasons.append("evidence_not_direct_child_of_source")
        if packet_parent != evidence_commit:
            reasons.append("packet_not_direct_child_of_evidence")

    try:
        freeze = _json_at(evidence_commit, FREEZE_PATH)
    except Exception:
        return False, ("source_freeze_missing_from_evidence_commit",), details

    if freeze.get("source_commit") != source_commit:
        reasons.append("source_freeze_commit_mismatch")
    if freeze.get("source_tree") != source_tree:
        reasons.append("source_freeze_tree_mismatch")

    source_to_evidence = _diff_paths(source_commit, evidence_commit)
    evidence_to_packet = _diff_paths(evidence_commit, packet_commit)
    details["source_to_evidence_paths"] = source_to_evidence
    details["evidence_to_packet_paths"] = evidence_to_packet

    invalid_evidence = [p for p in source_to_evidence if not _allowed_evidence_path(p)]
    if invalid_evidence:
        reasons.append("source_to_evidence_non_evidence_path")
        details["invalid_evidence_paths"] = invalid_evidence

    if set(evidence_to_packet) != {PACKET_CONTENT_PATH}:
        reasons.append("evidence_to_packet_exact_path_mismatch")
        details["invalid_packet_paths"] = evidence_to_packet

    for path, expected_sha in (freeze.get("source_files") or {}).items():
        try:
            s_hash = _sha256_at(source_commit, path)
            e_hash = _sha256_at(evidence_commit, path)
        except subprocess.CalledProcessError:
            reasons.append(f"source_manifest_file_missing:{path}")
            continue
        if s_hash != expected_sha:
            reasons.append(f"source_freeze_hash_mismatch:{path}")
        if s_hash != e_hash:
            reasons.append(f"source_changed_between_S_E:{path}")

    try:
        evidence_manifest = _json_at(evidence_commit, EVIDENCE_MANIFEST_PATH)
    except Exception:
        reasons.append("evidence_manifest_missing")
        evidence_manifest = {}
    if evidence_manifest.get("source_commit") != source_commit:
        reasons.append("evidence_manifest_source_commit_mismatch")
    if evidence_manifest.get("source_tree") != source_tree:
        reasons.append("evidence_manifest_source_tree_mismatch")
    if evidence_manifest.get("authority_effect") != "NONE" or evidence_manifest.get("exp_m_state") != "NOT_QUALIFIED" or evidence_manifest.get("live_provider_api_execution") is not False:
        reasons.append("evidence_manifest_authority_boundary_mismatch")

    artifact_items = list(evidence_manifest.get("artifacts") or ())
    artifact_paths = [str(item.get("path", "")) for item in artifact_items]
    if len(artifact_paths) != len(set(artifact_paths)):
        reasons.append("evidence_manifest_duplicate_artifact_path")
    expected_evidence_paths = set(artifact_paths) | {EVIDENCE_MANIFEST_PATH}
    if set(source_to_evidence) != expected_evidence_paths:
        reasons.append("source_to_evidence_artifact_set_mismatch")
        details["missing_evidence_paths"] = sorted(expected_evidence_paths - set(source_to_evidence))
        details["extra_evidence_paths"] = sorted(set(source_to_evidence) - expected_evidence_paths)

    for item in artifact_items:
        path = str(item.get("path", ""))
        try:
            raw = _git_bytes(evidence_commit, path)
        except subprocess.CalledProcessError:
            reasons.append(f"evidence_artifact_missing:{path}")
            continue
        if hashlib.sha256(raw).hexdigest() != str(item.get("sha256", "")):
            reasons.append(f"evidence_artifact_hash_mismatch:{path}")
        if len(raw) != int(item.get("size", -1)):
            reasons.append(f"evidence_artifact_size_mismatch:{path}")
        if not path.endswith(".json") or path == FREEZE_PATH:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            reasons.append(f"result_json_unreadable:{path}")
            continue
        execution = data.get("execution") or {}
        if execution.get("source_commit") != source_commit:
            reasons.append(f"result_source_commit_mismatch:{path}")
        if execution.get("source_tree") != source_tree:
            reasons.append(f"result_source_tree_mismatch:{path}")
        if data.get("live_provider_api_execution") is True or execution.get("live_provider_execution") is True:
            reasons.append(f"live_provider_boundary_violated:{path}")

    reviewer_ok, reviewer_reasons = verify_reviewer_suite_frozen()
    if not reviewer_ok:
        reasons.extend(reviewer_reasons)

    prior_ok, prior_reasons = verify_prior_evidence_index(
        source_commit=source_commit,
        packet_commit=packet_commit,
    )
    if not prior_ok:
        reasons.extend(prior_reasons)

    deleted = _git("diff", "--diff-filter=D", "--name-only", source_commit, packet_commit).splitlines()
    if deleted:
        details["deleted_paths"] = deleted

    return not reasons, tuple(dict.fromkeys(reasons)), details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--json-out")
    args = parser.parse_args()
    ok, reasons, details = verify_sep_sequence(args.source, args.evidence, args.packet)
    payload = {
        "ok": ok,
        "reasons": list(reasons),
        "details": details,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        (ROOT / args.json_out).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
