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
HANDOFF_PATH = "experiments/governed-platform/EXP-M-DETERMINISTIC-IMPLEMENTATION-R2E-REVIEW.md"
PREREGISTERED_AUTHORITY_COMMIT = "251647e5f44d394b761f1c6cdbb02a779901bc43"
AUTHORITY_ROOT_PATH = "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json"

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

EXPECTED_EVIDENCE_COMMAND_NAMES = (
    "source-freeze",
    "prior-evidence",
    "tests",
    "reviewer-core",
    "reviewer-authority",
    "reviewer-compound",
    "static-review-probes",
    "phases",
    "mutations",
    "self-falsification",
    "self-adjudication",
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


def verify_sep_sequence(source_commit: str, evidence_commit: str, packet_commit: str, handoff_commit: str | None = None) -> tuple[bool, tuple[str, ...], dict]:
    reasons: list[str] = []
    details: dict = {
        "source_commit": source_commit,
        "evidence_commit": evidence_commit,
        "packet_commit": packet_commit,
    }
    verifier_path = "governance-runtime/verify_exp_m_sep_sequence.py"
    try:
        details["verifier_source_path"] = verifier_path
        details["verifier_source_sha256_at_S"] = _sha256_at(source_commit, verifier_path)
    except subprocess.CalledProcessError:
        reasons.append("verifier_source_missing_at_S")

    try:
        source_tree = _git("rev-parse", f"{source_commit}^{{tree}}")
        evidence_tree = _git("rev-parse", f"{evidence_commit}^{{tree}}")
        packet_tree = _git("rev-parse", f"{packet_commit}^{{tree}}")
        handoff_tree = _git("rev-parse", f"{handoff_commit}^{{tree}}") if handoff_commit else None
    except subprocess.CalledProcessError:
        return False, ("sep_commit_missing",), details
    details.update(source_tree=source_tree, evidence_tree=evidence_tree, packet_tree=packet_tree)
    if handoff_commit:
        details.update(handoff_commit=handoff_commit, handoff_tree=handoff_tree)

    try:
        evidence_parent = _git("rev-parse", f"{evidence_commit}^")
        packet_parent = _git("rev-parse", f"{packet_commit}^")
        handoff_parent = _git("rev-parse", f"{handoff_commit}^") if handoff_commit else None
    except subprocess.CalledProcessError:
        reasons.append("sep_parent_resolution_failed")
    else:
        details["evidence_parent"] = evidence_parent
        details["packet_parent"] = packet_parent
        if handoff_commit:
            details["handoff_parent"] = handoff_parent
        if evidence_parent != source_commit:
            reasons.append("evidence_not_direct_child_of_source")
        if packet_parent != evidence_commit:
            reasons.append("packet_not_direct_child_of_evidence")
        if handoff_commit and handoff_parent != packet_commit:
            reasons.append("handoff_not_direct_child_of_packet")

    try:
        freeze = _json_at(evidence_commit, FREEZE_PATH)
    except Exception:
        return False, ("source_freeze_missing_from_evidence_commit",), details

    if freeze.get("source_commit") != source_commit:
        reasons.append("source_freeze_commit_mismatch")
    if freeze.get("source_tree") != source_tree:
        reasons.append("source_freeze_tree_mismatch")
    if freeze.get("authority_effect") != "NONE" or freeze.get("exp_m_state") != "NOT_QUALIFIED" or freeze.get("live_provider_api_execution") is not False:
        reasons.append("source_freeze_authority_boundary_mismatch")

    if freeze.get("schema") != "EXP-M-SOURCE-FREEZE/v2":
        reasons.append("source_freeze_schema_mismatch")
    try:
        authority_root = _json_at(PREREGISTERED_AUTHORITY_COMMIT, AUTHORITY_ROOT_PATH)
    except Exception:
        reasons.append("preregistered_authority_root_unavailable")
        authority_root = {}
    if authority_root.get("root_id") != "EXP-M-R2E-AUTHORITY-ROOT-2":
        reasons.append("preregistered_authority_root_invalid")
    authority_ref = freeze.get("authority_reference") or {}
    current_policy = authority_root.get("current_source_identity_policy") or {}
    delivery_policy = authority_root.get("delivery_binding_policy") or {}
    if (
        authority_ref.get("root_commit") != PREREGISTERED_AUTHORITY_COMMIT
        or authority_ref.get("policy_id") != current_policy.get("policy_id")
        or authority_ref.get("delivery_binding_policy_id") != delivery_policy.get("policy_id")
    ):
        reasons.append("source_freeze_authority_reference_mismatch")
    policy_items = delivery_policy.get("items") or {}
    expected_delivery_body = {
        "request_id": str(delivery_policy.get("request_id", "")),
        "reviewed_commit": source_commit,
        "items": {
            str(item_id): {"sha256": str(meta.get("sha256", "")), "size": int(meta.get("size", -1))}
            for item_id, meta in sorted(policy_items.items())
        },
    }
    expected_delivery_hash = hashlib.sha256(
        (json.dumps(expected_delivery_body, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    ).hexdigest()
    expected_binding = {
        "policy_id": str(delivery_policy.get("policy_id", "")),
        "role": "DERIVED_BINDING_EVIDENCE",
        "authoritative": False,
        "request_id": expected_delivery_body["request_id"],
        "reviewed_commit": source_commit,
        "items": expected_delivery_body["items"],
        "manifest_hash": expected_delivery_hash,
    }
    if freeze.get("delivery_binding") != expected_binding:
        reasons.append("source_freeze_delivery_binding_mismatch")

    source_to_evidence = _diff_paths(source_commit, evidence_commit)
    evidence_to_packet = _diff_paths(evidence_commit, packet_commit)
    packet_to_handoff = _diff_paths(packet_commit, handoff_commit) if handoff_commit else []
    details["source_to_evidence_paths"] = source_to_evidence
    details["evidence_to_packet_paths"] = evidence_to_packet
    if handoff_commit:
        details["packet_to_handoff_paths"] = packet_to_handoff

    invalid_evidence = [p for p in source_to_evidence if not _allowed_evidence_path(p)]
    if invalid_evidence:
        reasons.append("source_to_evidence_non_evidence_path")
        details["invalid_evidence_paths"] = invalid_evidence

    if set(evidence_to_packet) != {PACKET_CONTENT_PATH}:
        reasons.append("evidence_to_packet_exact_path_mismatch")
        details["invalid_packet_paths"] = evidence_to_packet
    if handoff_commit and set(packet_to_handoff) != {HANDOFF_PATH}:
        reasons.append("packet_to_handoff_exact_path_mismatch")
        details["invalid_handoff_paths"] = packet_to_handoff

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
    if evidence_manifest.get("schema") != "EXP-M-R2E-EVIDENCE-MANIFEST/v4":
        reasons.append("evidence_manifest_schema_mismatch")
    self_attestation = evidence_manifest.get("manifest_self_attestation") or {}
    if self_attestation.get("included_in_artifacts") is not False:
        reasons.append("evidence_manifest_self_reference_policy_missing")
    reproducibility = evidence_manifest.get("reproducibility") or {}
    if reproducibility.get("third_party_python_dependencies") != []:
        reasons.append("reproducibility_third_party_dependency_unfrozen")
    if reproducibility.get("network_required_for_test_commands") is not False:
        reasons.append("reproducibility_network_boundary_missing")
    command_rows = list(evidence_manifest.get("commands") or ())
    command_names = [str(row.get("name", "")) for row in command_rows]
    if len(command_names) != len(set(command_names)):
        reasons.append("evidence_command_name_duplicate")
    if set(command_names) != set(EXPECTED_EVIDENCE_COMMAND_NAMES):
        reasons.append("evidence_command_set_mismatch")

    artifact_items = list(evidence_manifest.get("artifacts") or ())
    artifact_paths = [str(item.get("path", "")) for item in artifact_items]
    if len(artifact_paths) != len(set(artifact_paths)):
        reasons.append("evidence_manifest_duplicate_artifact_path")
    expected_evidence_paths = set(artifact_paths) | {EVIDENCE_MANIFEST_PATH}
    if set(source_to_evidence) != expected_evidence_paths:
        reasons.append("source_to_evidence_artifact_set_mismatch")
        details["missing_evidence_paths"] = sorted(expected_evidence_paths - set(source_to_evidence))
        details["extra_evidence_paths"] = sorted(set(source_to_evidence) - expected_evidence_paths)

    stdout_paths: list[str] = []
    for row in command_rows:
        name = str(row.get("name", ""))
        stdout_path = str(row.get("stdout_path", ""))
        stdout_paths.append(stdout_path)
        if row.get("exit_code") != 0:
            reasons.append(f"evidence_command_nonzero_exit:{name}")
        if stdout_path not in artifact_paths:
            reasons.append(f"evidence_command_stdout_not_artifact:{name}")
            continue
        try:
            capture_raw = _git_bytes(evidence_commit, stdout_path)
            capture = json.loads(capture_raw)
        except Exception:
            reasons.append(f"evidence_command_capture_unreadable:{name}")
            continue
        if hashlib.sha256(capture_raw).hexdigest() != str(row.get("stdout_sha256", "")):
            reasons.append(f"evidence_command_capture_hash_mismatch:{name}")
        if capture.get("schema") != "EXP-M-R2E-COMMAND-CAPTURE/v2":
            reasons.append(f"evidence_command_capture_schema_mismatch:{name}")
        if capture.get("source_commit") != source_commit or capture.get("source_tree") != source_tree:
            reasons.append(f"evidence_command_capture_source_mismatch:{name}")
        if capture.get("command_name") != name:
            reasons.append(f"evidence_command_capture_name_mismatch:{name}")
        if capture.get("command") != row.get("command") or capture.get("portable_command") != row.get("portable_command"):
            reasons.append(f"evidence_command_capture_command_mismatch:{name}")
        if capture.get("exit_code") != row.get("exit_code"):
            reasons.append(f"evidence_command_capture_exit_mismatch:{name}")

        command_source_path = row.get("command_source_path")
        command_source_sha = row.get("command_source_sha256")
        if command_source_path:
            try:
                actual_source_sha = _sha256_at(source_commit, str(command_source_path))
            except subprocess.CalledProcessError:
                reasons.append(f"evidence_command_source_missing:{name}")
            else:
                if actual_source_sha != command_source_sha or capture.get("command_source_sha256") != command_source_sha:
                    reasons.append(f"evidence_command_source_hash_mismatch:{name}")

        raw_stdout = str(capture.get("raw_stdout", "")).encode("utf-8")
        raw_stderr = str(capture.get("raw_stderr", "")).encode("utf-8")
        stdout_hash = hashlib.sha256(raw_stdout).hexdigest()
        stderr_hash = hashlib.sha256(raw_stderr).hexdigest()
        if stdout_hash != str(capture.get("raw_stdout_sha256", "")) or len(raw_stdout) != int(capture.get("raw_stdout_size", -1)):
            reasons.append(f"evidence_stdout_payload_integrity_mismatch:{name}")
        if stderr_hash != str(capture.get("raw_stderr_sha256", "")) or len(raw_stderr) != int(capture.get("raw_stderr_size", -1)):
            reasons.append(f"evidence_stderr_payload_integrity_mismatch:{name}")
        if stdout_hash != str(row.get("stdout_payload_sha256", "")) or len(raw_stdout) != int(row.get("stdout_payload_size", -1)):
            reasons.append(f"evidence_stdout_manifest_payload_mismatch:{name}")
        if stderr_hash != str(row.get("stderr_payload_sha256", "")) or len(raw_stderr) != int(row.get("stderr_payload_size", -1)):
            reasons.append(f"evidence_stderr_manifest_payload_mismatch:{name}")

        result_path = row.get("result_path")
        if result_path:
            if result_path not in artifact_paths:
                reasons.append(f"evidence_command_result_not_artifact:{name}")
                continue
            try:
                result_raw = _git_bytes(evidence_commit, str(result_path))
            except subprocess.CalledProcessError:
                reasons.append(f"evidence_command_result_missing:{name}")
                continue
            result_sha = hashlib.sha256(result_raw).hexdigest()
            result_size = len(result_raw)
            if (
                result_sha != str(row.get("result_sha256_at_command_exit", ""))
                or result_size != int(row.get("result_size_at_command_exit", -1))
                or result_sha != str(capture.get("result_sha256_at_command_exit", ""))
                or result_size != int(capture.get("result_size_at_command_exit", -1))
            ):
                reasons.append(f"evidence_command_result_binding_mismatch:{name}")
            if raw_stdout != result_raw:
                reasons.append(f"evidence_command_result_not_exact_stdout:{name}")
            if row.get("stdout_payload_identical_to_result") is not True or capture.get("stdout_payload_identical_to_result") is not True:
                reasons.append(f"evidence_command_result_identity_flag_mismatch:{name}")
    if len(stdout_paths) != len(set(stdout_paths)):
        reasons.append("evidence_command_stdout_path_duplicate")

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

    try:
        manifest_raw = _git_bytes(evidence_commit, EVIDENCE_MANIFEST_PATH)
        manifest_sha256 = hashlib.sha256(manifest_raw).hexdigest()
        packet_content = _git_bytes(packet_commit, PACKET_CONTENT_PATH).decode("utf-8")
    except Exception:
        reasons.append("packet_manifest_attestation_unverifiable")
    else:
        marker = f"Evidence manifest SHA-256 at E: {manifest_sha256}"
        if marker not in packet_content:
            reasons.append("packet_manifest_attestation_missing")
        details["evidence_manifest_sha256_at_E"] = manifest_sha256

    if handoff_commit:
        try:
            handoff_text = _git_bytes(handoff_commit, HANDOFF_PATH).decode("utf-8")
        except Exception:
            reasons.append("handoff_content_unreadable")
        else:
            for marker in (
                f"- S: {source_commit}",
                f"- E: {evidence_commit}",
                f"- P: {packet_commit}",
            ):
                if marker not in handoff_text:
                    reasons.append("handoff_identity_marker_missing")

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
    parser.add_argument("--handoff")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    ok, reasons, details = verify_sep_sequence(args.source, args.evidence, args.packet, args.handoff)
    payload = {
        "ok": ok,
        "reasons": list(reasons),
        "details": details,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
        "verification_command": "python governance-runtime/verify_exp_m_sep_sequence.py"
            + f" --source {args.source} --evidence {args.evidence} --packet {args.packet}"
            + (f" --handoff {args.handoff}" if args.handoff else ""),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        (ROOT / args.json_out).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
