from __future__ import annotations

import copy
import unittest

from v24_v6_adversarial_evidence_binding import (
    REQUIRED_ADVERSARIAL_CHECKS,
    construction_frontier,
    evidence_record_digest,
    validate_mandatory_adversarial_evidence,
)

COMMIT = "1" * 40
TREE = "2" * 40
ENV = "3" * 64
RUN = "RUN-R12-001"
ROUND = "ROUND-R12-001"


def record(check_id: str) -> dict:
    row = {
        "check_id": check_id,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_contract_digest": ENV,
        "run_id": RUN,
        "round_id": ROUND,
        "terminal_state": "EXECUTED",
        "result": "PASS",
        "execution_evidence_digest": "4" * 64,
        "producer_identity": "EXTERNAL-EXECUTOR",
        "witness_identity": "INDEPENDENT-WITNESS",
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_authored": False,
        "currentness_state": "CURRENT",
        "record_digest": "",
    }
    row["record_digest"] = evidence_record_digest(row)
    return row


def valid_records() -> list[dict]:
    return [record(x) for x in sorted(REQUIRED_ADVERSARIAL_CHECKS)]


def validate(rows):
    return validate_mandatory_adversarial_evidence(
        records=rows,
        expected_candidate_commit=COMMIT,
        expected_candidate_tree=TREE,
        expected_environment_contract_digest=ENV,
        expected_run_id=RUN,
        expected_round_id=ROUND,
        forbidden_producer_identities=("CANDIDATE",),
    )


class R12AdversarialEvidenceBindingTests(unittest.TestCase):
    def test_exact_executed_evidence_set_binds(self):
        result = validate(valid_records())
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["record_count"], len(REQUIRED_ADVERSARIAL_CHECKS))
        self.assertEqual(len(result["binding_digest"]), 64)

    def test_name_only_attestation_cannot_validate(self):
        result = validate([])
        self.assertFalse(result["valid"])
        for check_id in REQUIRED_ADVERSARIAL_CHECKS:
            self.assertIn(f"ADVERSARIAL_EVIDENCE_REQUIRED_CHECK_MISSING:{check_id}", result["problems"])

    def test_missing_record_fails_closed(self):
        rows = valid_records()[:-1]
        missing = sorted(REQUIRED_ADVERSARIAL_CHECKS)[-1]
        result = validate(rows)
        self.assertFalse(result["valid"])
        self.assertIn(f"ADVERSARIAL_EVIDENCE_REQUIRED_CHECK_MISSING:{missing}", result["problems"])

    def test_duplicate_record_fails_closed(self):
        rows = valid_records()
        rows.append(copy.deepcopy(rows[0]))
        result = validate(rows)
        self.assertFalse(result["valid"])
        self.assertIn(f"ADVERSARIAL_EVIDENCE_CHECK_DUPLICATE:{rows[0]['check_id']}", result["problems"])

    def test_candidate_tree_environment_and_run_replay_fail_closed(self):
        mutations = (
            ("candidate_tree", "9" * 40, "ADVERSARIAL_EVIDENCE_CANDIDATE_TREE_MISMATCH"),
            ("environment_contract_digest", "8" * 64, "ADVERSARIAL_EVIDENCE_ENVIRONMENT_MISMATCH"),
            ("run_id", "OLD-RUN", "ADVERSARIAL_EVIDENCE_RUN_MISMATCH"),
            ("round_id", "OLD-ROUND", "ADVERSARIAL_EVIDENCE_ROUND_MISMATCH"),
        )
        for field, value, prefix in mutations:
            with self.subTest(field=field):
                rows = valid_records()
                rows[0][field] = value
                rows[0]["record_digest"] = evidence_record_digest(rows[0])
                result = validate(rows)
                self.assertFalse(result["valid"])
                self.assertTrue(any(x.startswith(prefix + ":") for x in result["problems"]), result["problems"])

    def test_unexecuted_nonpass_stale_and_self_authored_fail_closed(self):
        mutations = (
            ("terminal_state", "NOT_EXECUTED", "ADVERSARIAL_EVIDENCE_NOT_EXECUTED"),
            ("result", "FAIL", "ADVERSARIAL_EVIDENCE_NOT_PASS"),
            ("currentness_state", "STALE", "ADVERSARIAL_EVIDENCE_STALE"),
            ("candidate_self_authored", True, "ADVERSARIAL_EVIDENCE_SELF_AUTHORED_FORBIDDEN"),
            ("authority_origin", "CANDIDATE_BRANCH", "ADVERSARIAL_EVIDENCE_AUTHORITY_ORIGIN_INVALID"),
        )
        for field, value, prefix in mutations:
            with self.subTest(field=field):
                rows = valid_records()
                rows[0][field] = value
                rows[0]["record_digest"] = evidence_record_digest(rows[0])
                result = validate(rows)
                self.assertFalse(result["valid"])
                self.assertTrue(any(x.startswith(prefix + ":") for x in result["problems"]), result["problems"])

    def test_record_digest_tamper_fails_closed(self):
        rows = valid_records()
        rows[0]["record_digest"] = "0" * 64
        result = validate(rows)
        self.assertFalse(result["valid"])
        self.assertTrue(any(x.startswith("ADVERSARIAL_EVIDENCE_RECORD_DIGEST_MISMATCH:") for x in result["problems"]))

    def test_candidate_identity_cannot_produce_or_witness_evidence(self):
        rows = valid_records()
        rows[0]["producer_identity"] = "CANDIDATE"
        rows[0]["record_digest"] = evidence_record_digest(rows[0])
        result = validate(rows)
        self.assertFalse(result["valid"])
        self.assertTrue(any(x.startswith("ADVERSARIAL_EVIDENCE_PRODUCER_FORBIDDEN:") for x in result["problems"]))

    def test_frontier_is_non_authoritative(self):
        result = construction_frontier()
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")
        self.assertEqual(result["scientific_execution_state"], "CLOSED_PENDING_R12_SUCCESSOR_REVIEW")


if __name__ == "__main__":
    unittest.main()
