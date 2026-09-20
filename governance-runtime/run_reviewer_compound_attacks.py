"""Execute the frozen reviewer-authored CA-1..CA-10 suite and emit JSON."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

from reviewer_exp_m_r2e_compound_suite import CompoundAttackSuite  # noqa: E402

OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-R2E-COMPOUND-RESULTS.json"

EXPECTED_REASONS = {
    "test_ca1_self_consistent_context_plus_forged_complete_receipt": ("CA-1", "expectation_authority_invalid"),
    "test_ca2_correctly_keyed_token_for_different_bundle": ("CA-2", "evidence_token_mismatch"),
    "test_ca3_fabricated_manifest_plus_matching_caller_commit": ("CA-3", "authority_reviewed_commit_mismatch"),
    "test_ca4_fabricated_retrieval_bytes_plus_forged_receipt": ("CA-4", "retrieval_and_delivery_binding_rejected"),
    "test_ca5_zip_named_bin_plus_fake_schedule_diversity": ("CA-5", "archive_and_schedule_attack_rejected"),
    "test_ca6_authority_plan_absent_but_caller_plan_self_consistent": ("CA-6", "qualification_authority_plan_missing"),
    "test_ca7_prior_artifact_deleted_but_index_unchanged": ("CA-7", "indexed_prior_artifact_missing"),
    "test_ca8_reviewer_suite_modified_after_source_freeze": ("CA-8", "reviewer_suite_hash_drift"),
    "test_ca9_caller_pass_with_failed_predicate": ("CA-9", "disposition_promotable"),
    "test_ca10_missing_protocol_with_self_consistent_record": ("CA-10", "r5_protocol_unavailable"),
}


class CaptureResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.case_outcomes: dict[str, dict] = {}

    def _name(self, test) -> str:
        return test._testMethodName

    def addSuccess(self, test):
        super().addSuccess(test)
        self.case_outcomes[self._name(test)] = {"rejected": True}

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


def run() -> dict:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CompoundAttackSuite)
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, resultclass=CaptureResult)
    result: CaptureResult = runner.run(suite)
    cases = []
    for test_name, (case_id, reason) in EXPECTED_REASONS.items():
        outcome = result.case_outcomes.get(test_name, {"rejected": False, "failure": "test_not_executed"})
        cases.append({
            "id": case_id,
            "test": test_name,
            "rejected": bool(outcome.get("rejected")),
            "rejection_reason": reason if outcome.get("rejected") else "COMPOUND_ATTACK_SURVIVED",
            "failure": outcome.get("failure"),
            "source": "reviewer_exp_m_r2e_compound_suite.py",
        })
    survivors = [case["id"] for case in cases if not case["rejected"]]
    return {
        "schema": "EXP-M-R2E-COMPOUND/v1",
        "execution": {
            "source_commit": _git("rev-parse", "HEAD"),
            "source_tree": _git("rev-parse", "HEAD^{tree}"),
            "utc": datetime.now(timezone.utc).isoformat(),
            "command": "python governance-runtime/run_reviewer_compound_attacks.py",
            "interpreter": sys.executable,
        },
        "cases": cases,
        "case_count": len(cases),
        "survivors": survivors,
        "survivor_count": len(survivors),
        "all_rejected": not survivors and result.wasSuccessful(),
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
