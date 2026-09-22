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

CASE_METADATA = {
    "test_ca1_self_consistent_context_plus_forged_complete_receipt": {"id": "CA-1", "blocking_guard": "expectation_authority_invalid"},
    "test_ca2_correctly_keyed_token_for_different_bundle": {"id": "CA-2", "blocking_guard": "evidence_token_mismatch"},
    "test_ca3_fabricated_manifest_plus_matching_caller_commit": {"id": "CA-3", "blocking_guard": "authority_reviewed_commit_mismatch"},
    "test_ca4_fabricated_retrieval_bytes_plus_forged_receipt": {"id": "CA-4", "blocking_guard": "retrieval_and_delivery_binding_rejected"},
    "test_ca5_zip_named_bin_plus_fake_schedule_diversity": {"id": "CA-5", "blocking_guard": "archive_and_schedule_attack_rejected"},
    "test_ca6_authority_plan_absent_but_caller_plan_self_consistent": {"id": "CA-6", "blocking_guard": "qualification_authority_plan_missing"},
    "test_ca7_prior_artifact_deleted_but_index_unchanged": {"id": "CA-7", "blocking_guard": "indexed_prior_artifact_missing"},
    "test_ca8_reviewer_suite_modified_after_source_freeze": {"id": "CA-8", "blocking_guard": "reviewer_suite_hash_drift"},
    "test_ca9_caller_pass_with_failed_predicate": {
        "id": "CA-9",
        "blocking_guard": "disposition_promotable",
        "guard_semantics": "FALSE means failed predicates derive CHANGES_REQUIRED; a caller-supplied PASS cannot override that derived disposition.",
    },
    "test_ca10_missing_protocol_with_self_consistent_record": {
        "id": "CA-10",
        "blocking_guard": "r5_protocol_unavailable",
        "fault_injection": "AuthorityHandle.with_missing_r5_protocol_for_test() sets protocol_available=False for this negative test only; the frozen R5 protocol remains present in the authority root.",
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
    for test_name, metadata in CASE_METADATA.items():
        outcome = result.case_outcomes.get(test_name, {"rejected": False, "failure": "test_not_executed"})
        rejected = bool(outcome.get("rejected"))
        row = {
            "id": metadata["id"],
            "test": test_name,
            "rejected": rejected,
            "blocking_guard": metadata["blocking_guard"] if rejected else "COMPOUND_ATTACK_SURVIVED",
            "blocking_guard_semantics": "guard/control identifier; FALSE or failed guard means the attack is rejected; this field is not a positive disposition",
            "failure": outcome.get("failure"),
            "source": "reviewer_exp_m_r2e_compound_suite.py",
        }
        for key in ("guard_semantics", "fault_injection"):
            if key in metadata:
                row[key] = metadata[key]
        cases.append(row)
    survivors = [case["id"] for case in cases if not case["rejected"]]
    return {
        "schema": "EXP-M-R2E-COMPOUND/v2",
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
