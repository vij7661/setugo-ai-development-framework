from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import digest
from v24_v6_r12_successor import (
    REQUIRED_ADVERSARIAL_CHECKS,
    SCIENTIFIC_EXECUTION_CLOSED,
    validate_adversarial_evidence_bundle,
    validate_execution_boundary_evidence,
)


COMMIT = "1" * 40
TREE = "2" * 40
ENV = "3" * 64
INTERPRETER = "4" * 64


def evidence_record(check_id: str, *, producer: str = "candidate-domain", witness: str = "review-domain"):
    row = {
        "check_id": check_id,
        "execution_state": "EXECUTED",
        "terminal_result": "PASS",
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "interpreter_contract_digest": INTERPRETER,
        "evidence_digest": "5" * 64,
        "run_id": "run-1",
        "round_id": "round-1",
        "producer_control_domain": producer,
        "witness_id": "external-witness-1",
        "witness_control_domain": witness,
        "witness_authority_origin": "EXTERNAL_REVIEW_BRANCH",
    }
    row["record_digest"] = digest(dict(row))
    return row


def evidence_bundle():
    records = [evidence_record(x) for x in sorted(REQUIRED_ADVERSARIAL_CHECKS)]
    return {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "interpreter_contract_digest": INTERPRETER,
        "records": records,
        "evidence_set_digest": digest({"record_digests": sorted(x["record_digest"] for x in records)}),
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def boundary_record():
    return {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "trusted_parent_git_blob_sha1": "6" * 40,
        "trusted_worker_git_blob_sha1": "7" * 40,
        "environment_digest": ENV,
        "interpreter_contract_digest": INTERPRETER,
        "execution_transcript_digest": "8" * 64,
        "actual_interpreter_flags": {
            "isolated": True,
            "no_site": True,
            "ignore_environment": True,
            "safe_path": True,
        },
        "trusted_parent_imported_candidate": False,
        "candidate_shared_trusted_result_state": False,
        "result_accounting_origin": "TRUSTED_PARENT",
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


class R12AdversarialEvidenceBindingTests(unittest.TestCase):
    def test_complete_executed_evidence_bundle_binds_but_never_qualifies(self):
        result = validate_adversarial_evidence_bundle(evidence_bundle())
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["required_check_count"], 6)
        self.assertEqual(result["bound_check_count"], 6)

    def test_name_only_attestation_is_rejected(self):
        b = evidence_bundle()
        b["records"] = [{"check_id": x} for x in sorted(REQUIRED_ADVERSARIAL_CHECKS)]
        b["evidence_set_digest"] = digest({"record_digests": []})
        result = validate_adversarial_evidence_bundle(b)
        self.assertFalse(result["valid"])
        self.assertTrue(any("NOT_EXECUTED" in p for p in result["problems"]))
        self.assertTrue(any("RECORD_DIGEST_MISMATCH" in p for p in result["problems"]))

    def test_missing_check_fails_closed(self):
        b = evidence_bundle()
        removed = b["records"].pop()["check_id"]
        b["evidence_set_digest"] = digest({"record_digests": sorted(x["record_digest"] for x in b["records"])})
        result = validate_adversarial_evidence_bundle(b)
        self.assertFalse(result["valid"])
        self.assertIn(f"R12_ADVERSARIAL_EVIDENCE_CHECK_MISSING:{removed}", result["problems"])

    def test_stale_candidate_binding_fails(self):
        b = evidence_bundle()
        b["records"][0]["candidate_commit"] = "9" * 40
        b["records"][0]["record_digest"] = digest({k: v for k, v in b["records"][0].items() if k != "record_digest"})
        b["evidence_set_digest"] = digest({"record_digests": sorted(x["record_digest"] for x in b["records"])})
        result = validate_adversarial_evidence_bundle(b)
        self.assertFalse(result["valid"])
        self.assertTrue(any("COMMIT_MISMATCH" in p for p in result["problems"]))

    def test_self_witness_fails(self):
        b = evidence_bundle()
        row = b["records"][0]
        row["witness_control_domain"] = row["producer_control_domain"]
        row["record_digest"] = digest({k: v for k, v in row.items() if k != "record_digest"})
        b["evidence_set_digest"] = digest({"record_digests": sorted(x["record_digest"] for x in b["records"])})
        result = validate_adversarial_evidence_bundle(b)
        self.assertFalse(result["valid"])
        self.assertTrue(any("WITNESS_NOT_INDEPENDENT" in p for p in result["problems"]))

    def test_unexecuted_or_nonpass_fails(self):
        for field, value, marker in (
            ("execution_state", "NOT_EXECUTED", "NOT_EXECUTED"),
            ("terminal_result", "FAIL", "NOT_PASS"),
        ):
            with self.subTest(field=field):
                b = evidence_bundle()
                row = b["records"][0]
                row[field] = value
                row["record_digest"] = digest({k: v for k, v in row.items() if k != "record_digest"})
                b["evidence_set_digest"] = digest({"record_digests": sorted(x["record_digest"] for x in b["records"])})
                result = validate_adversarial_evidence_bundle(b)
                self.assertFalse(result["valid"])
                self.assertTrue(any(marker in p for p in result["problems"]))


class R12ExecutionBoundaryEvidenceTests(unittest.TestCase):
    def test_valid_external_boundary_record_binds_but_never_qualifies(self):
        result = validate_execution_boundary_evidence(boundary_record())
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])

    def test_declared_flags_are_not_optional(self):
        for key in ("isolated", "no_site", "ignore_environment", "safe_path"):
            with self.subTest(key=key):
                r = boundary_record()
                r["actual_interpreter_flags"][key] = False
                result = validate_execution_boundary_evidence(r)
                self.assertFalse(result["valid"])
                self.assertIn(f"R12_EXECUTION_BOUNDARY_FLAG_NOT_TRUE:{key}", result["problems"])

    def test_parent_candidate_import_is_forbidden(self):
        r = boundary_record()
        r["trusted_parent_imported_candidate"] = True
        result = validate_execution_boundary_evidence(r)
        self.assertFalse(result["valid"])
        self.assertIn("R12_EXECUTION_BOUNDARY_PARENT_IMPORTED_CANDIDATE", result["problems"])

    def test_shared_result_state_is_forbidden(self):
        r = boundary_record()
        r["candidate_shared_trusted_result_state"] = True
        result = validate_execution_boundary_evidence(r)
        self.assertFalse(result["valid"])
        self.assertIn("R12_EXECUTION_BOUNDARY_SHARED_RESULT_STATE", result["problems"])

    def test_candidate_cannot_claim_authority_origin(self):
        r = boundary_record()
        r["authority_origin"] = "CANDIDATE"
        result = validate_execution_boundary_evidence(r)
        self.assertFalse(result["valid"])
        self.assertIn("R12_EXECUTION_BOUNDARY_AUTHORITY_ORIGIN_INVALID", result["problems"])


if __name__ == "__main__":
    unittest.main()
