"""Execute the frozen reviewer-authored CA-1..CA-10 suite and emit JSON."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

from reviewer_exp_m_r2e_mechanism_suite import MechanismIntegrityCompoundSuite  # noqa: E402
from verify_exp_m_test_integrity import SUITE_PATH, authoritative_case_contracts  # noqa: E402

OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-R2E-COMPOUND-RESULTS.json"

CASE_METADATA = {
    "test_ca1_real_forged_context_reaches_production_authority_check": {"id": "CA-1", "blocking_guard": "expectation_authority_invalid"},
    "test_ca2_real_mismatched_evidence_token_reaches_cas_verifier": {"id": "CA-2", "blocking_guard": "evidence_token_mismatch"},
    "test_ca3_real_fabricated_delivery_commit_reaches_authority_check": {"id": "CA-3", "blocking_guard": "authority_reviewed_commit_mismatch"},
    "test_ca4_real_forged_retrieval_and_delivery_bytes_reach_validators": {"id": "CA-4", "blocking_guard": "retrieval_and_delivery_binding_rejected"},
    "test_ca5_real_archive_and_schedule_inputs_reach_production_validators": {"id": "CA-5", "blocking_guard": "archive_and_schedule_attack_rejected"},
    "test_ca6_real_unauthorized_plan_reaches_authority_validator": {"id": "CA-6", "blocking_guard": "qualification_authority_plan_missing"},
    "test_ca7_real_deleted_indexed_artifact_reaches_unmodified_prior_verifier": {"id": "CA-7", "blocking_guard": "indexed_prior_artifact_deleted_after_source_freeze"},
    "test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier": {"id": "CA-8", "blocking_guard": "reviewer_suite_hash_drift"},
    "test_ca9_real_caller_pass_reaches_derived_disposition": {
        "id": "CA-9",
        "blocking_guard": "disposition_promotable",
        "guard_semantics": "FALSE means failed predicates derive CHANGES_REQUIRED; a caller-supplied PASS cannot override that derived disposition.",
    },
    "test_ca10_real_protocol_unavailable_state_reaches_production_validator": {
        "id": "CA-10",
        "blocking_guard": "r5_protocol_unavailable",
        "fault_injection": "A real AuthorityHandle input is instantiated with protocol_available=False and passed through production validate_capability; no test-only rejection shortcut is used.",
    },
}



class CaptureResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.case_outcomes: dict[str, dict] = {}

    def _name(self, test) -> str:
        return test._testMethodName

    def addSuccess(self, test):
        super().addSuccess(test)
        # Generic unittest success is not itself proof that the attack was
        # rejected. Rejection is derived later only when the frozen test method
        # also satisfies its explicit mechanism + assertion contract.
        self.case_outcomes[self._name(test)] = {"test_passed": True}

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.case_outcomes[self._name(test)] = {
            "rejected": False,
            "failure": self._exc_info_to_string(err, test),
        }

    def addError(self, test, err):
        super().addError(test, err)
        self.case_outcomes[self._name(test)] = {
            "rejected": False,
            "failure": self._exc_info_to_string(err, test),
        }


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_text(commit: str, path: str) -> str:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT, text=True)


def run() -> dict:
    source_commit = os.environ.get("EXP_M_SOURCE_COMMIT", "").strip()
    source_tree = os.environ.get("EXP_M_SOURCE_TREE", "").strip()
    if len(source_commit) != 40:
        raise RuntimeError("compound_source_identity_binding_required")
    if _git("rev-parse", "HEAD") != source_commit:
        raise RuntimeError("compound_source_identity_head_mismatch")
    actual_tree = _git("rev-parse", f"{source_commit}^{{tree}}")
    if source_tree and source_tree != actual_tree:
        raise RuntimeError("compound_source_identity_tree_mismatch")
    suite_source = _git_text(source_commit, SUITE_PATH)
    working_source = (ROOT / SUITE_PATH).read_text(encoding="utf-8")
    source_integrity = hashlib.sha256(working_source.encode()).hexdigest() == hashlib.sha256(suite_source.encode()).hexdigest()
    contracts = authoritative_case_contracts(suite_source)

    suite = unittest.TestSuite(
        MechanismIntegrityCompoundSuite(test_name)
        for test_name in CASE_METADATA
    )
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, resultclass=CaptureResult)
    result: CaptureResult = runner.run(suite)
    cases = []
    for test_name, metadata in CASE_METADATA.items():
        outcome = result.case_outcomes.get(test_name, {"test_passed": False, "failure": "test_not_executed"})
        contract = contracts.get(test_name, {})
        contract_valid = contract.get("valid") is True
        rejected = bool(outcome.get("test_passed")) and source_integrity and contract_valid
        failure = outcome.get("failure")
        if outcome.get("test_passed") and not source_integrity:
            failure = "authoritative_suite_worktree_source_mismatch"
        elif outcome.get("test_passed") and not contract_valid:
            failure = "authoritative_case_rejection_contract_invalid"
        row = {
            "id": metadata["id"],
            "test": test_name,
            "rejected": rejected,
            "blocking_guard": metadata["blocking_guard"] if rejected else "COMPOUND_ATTACK_SURVIVED",
            "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
            "failure": failure,
            "source": "reviewer_exp_m_r2e_mechanism_suite.py",
            "test_passed": bool(outcome.get("test_passed")),
            "rejection_contract_verified": contract_valid,
        }
        for key in ("guard_semantics", "fault_injection"):
            if key in metadata:
                row[key] = metadata[key]
        cases.append(row)
    survivors = [case["id"] for case in cases if not case["rejected"]]
    return {
        "schema": "EXP-M-R2E-COMPOUND/v3",
        "execution": {
            "source_commit": source_commit,
            "source_tree": actual_tree,
            "utc": datetime.now(timezone.utc).isoformat(),
            "command": "python governance-runtime/run_reviewer_compound_attacks.py",
            "interpreter": sys.executable,
        },
        "cases": cases,
        "case_count": len(cases),
        "survivors": survivors,
        "survivor_count": len(survivors),
        "all_rejected": not survivors and result.wasSuccessful() and source_integrity,
        "authoritative_suite_source_integrity": source_integrity,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }


def main() -> int:
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_rejected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
