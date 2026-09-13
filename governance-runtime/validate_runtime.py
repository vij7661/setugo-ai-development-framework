#!/usr/bin/env python3
"""R12 fail-closed wrapper for live governance runtime validation.

The R11 validator is retained verbatim as validate_runtime_legacy.py for audit
history. This entrypoint adds governed-Git object resolution and executed-result
evidence binding before the legacy structural validator may report success.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

import validate_runtime_legacy as _legacy

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _fail(message: str) -> None:
    raise AssertionError(message)


def _git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _require_commit(value: object, field: str) -> str:
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        _fail(f"{field} must be a lowercase 40-character Git SHA")
    if _git("cat-file", "-e", f"{value}^{{commit}}").returncode != 0:
        _fail(f"{field} does not resolve to a governed Git commit")
    return value


def _require_path_at_commit(commit: str, path: object, field: str) -> None:
    if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
        _fail(f"{field} path invalid")
    if _git("cat-file", "-e", f"{commit}:{path}").returncode != 0:
        _fail(f"{field} is not present at governed Git commit")


def _tree_for_commit(commit: str) -> str:
    proc = _git("rev-parse", f"{commit}^{{tree}}")
    if proc.returncode != 0:
        _fail("candidate commit tree cannot be resolved")
    value = proc.stdout.decode("ascii", errors="strict").strip()
    if not SHA40.fullmatch(value):
        _fail("candidate tree resolution malformed")
    return value


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _load_execution_evidence(work: Mapping[str, Any]) -> None:
    latest = work.get("latest_result")
    if not isinstance(latest, Mapping):
        _fail("active_workstream.latest_result malformed")
    binding = latest.get("execution_evidence")
    if not isinstance(binding, Mapping):
        _fail("LATEST_RESULT_EXECUTED_EVIDENCE_REQUIRED")
    rel = binding.get("path")
    supplied_sha = binding.get("sha256")
    if not isinstance(rel, str) or not rel or rel.startswith("/") or ".." in Path(rel).parts:
        _fail("latest_result.execution_evidence.path invalid")
    if not isinstance(supplied_sha, str) or not SHA256.fullmatch(supplied_sha):
        _fail("latest_result.execution_evidence.sha256 invalid")
    path = REPO_ROOT / rel
    if not path.is_file():
        _fail("LATEST_RESULT_EXECUTED_EVIDENCE_FILE_MISSING")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != supplied_sha:
        _fail("LATEST_RESULT_EXECUTED_EVIDENCE_HASH_MISMATCH")
    try:
        record = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _fail("LATEST_RESULT_EXECUTED_EVIDENCE_MALFORMED")
    if not isinstance(record, Mapping):
        _fail("LATEST_RESULT_EXECUTED_EVIDENCE_MALFORMED")

    head = _require_commit(work.get("head_commit"), "active_workstream.head_commit")
    if record.get("candidate_commit") != head:
        _fail("LATEST_RESULT_EVIDENCE_CANDIDATE_COMMIT_MISMATCH")
    actual_tree = _tree_for_commit(head)
    if record.get("candidate_tree") != actual_tree:
        _fail("LATEST_RESULT_EVIDENCE_CANDIDATE_TREE_MISMATCH")
    if record.get("terminal_status") != "EXECUTED":
        _fail("LATEST_RESULT_EVIDENCE_NOT_EXECUTED")
    if not isinstance(record.get("environment_identity"), str) or not record.get("environment_identity"):
        _fail("LATEST_RESULT_EVIDENCE_ENVIRONMENT_IDENTITY_REQUIRED")
    for key in ("runner_identity_digest", "executed_test_set_digest"):
        value = record.get(key)
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            _fail(f"LATEST_RESULT_EVIDENCE_{key.upper()}_INVALID")

    passed, total, failures = latest.get("passed"), latest.get("total"), latest.get("failures")
    if record.get("passed") != passed or record.get("total") != total or record.get("failures") != failures:
        _fail("LATEST_RESULT_EVIDENCE_RESULT_MISMATCH")
    exit_code = record.get("process_exit_code")
    if not isinstance(exit_code, int):
        _fail("LATEST_RESULT_EVIDENCE_PROCESS_EXIT_REQUIRED")
    if isinstance(passed, int) and isinstance(total, int) and passed == total and exit_code != 0:
        _fail("LATEST_RESULT_EVIDENCE_PASS_EXIT_MISMATCH")

    supplied_record_digest = record.get("record_digest")
    material = {k: v for k, v in record.items() if k != "record_digest"}
    if not isinstance(supplied_record_digest, str) or supplied_record_digest != _canonical_digest(material):
        _fail("LATEST_RESULT_EVIDENCE_RECORD_DIGEST_INVALID")


def _r12_preflight() -> None:
    state = json.loads((ROOT / "session-state.json").read_text(encoding="utf-8"))
    if not isinstance(state, Mapping):
        _fail("session-state malformed")
    runtime = state.get("runtime") if isinstance(state.get("runtime"), Mapping) else {}
    work = state.get("active_workstream") if isinstance(state.get("active_workstream"), Mapping) else {}
    handoff = state.get("execution_handoff") if isinstance(state.get("execution_handoff"), Mapping) else {}
    review = state.get("independent_review") if isinstance(state.get("independent_review"), Mapping) else {}

    normative_commit = _require_commit(runtime.get("normative_contract_commit"), "runtime.normative_contract_commit")
    _require_path_at_commit(normative_commit, runtime.get("normative_contract_path"), "runtime.normative_contract")
    handoff_commit = _require_commit(runtime.get("handoff_contract_commit"), "runtime.handoff_contract_commit")
    _require_path_at_commit(handoff_commit, runtime.get("handoff_contract_path"), "runtime.handoff_contract")

    for key in (
        "head_commit", "preregistration_commit", "frozen_acceptance_harness_commit",
        "first_mechanism_commit", "preserved_failure_record_commit",
    ):
        _require_commit(work.get(key), f"active_workstream.{key}")
    _require_commit(handoff.get("candidate_commit"), "execution_handoff.candidate_commit")
    reviewed = review.get("current_reviewed_artifact_commit")
    if reviewed is not None:
        _require_commit(reviewed, "independent_review.current_reviewed_artifact_commit")

    _load_execution_evidence(work)


def main() -> int:
    _r12_preflight()
    return _legacy.main()


if __name__ == "__main__":
    raise SystemExit(main())
