import copy
import unittest

from evidence_chain import append_evidence_record, verify_evidence_chain


class ExpFEvidenceChainTests(unittest.TestCase):
    def record(self, evidence_id="e1", content_hash="content-a"):
        return {
            "evidence_id": evidence_id,
            "project_id": "pilot1",
            "task_id": "EXP-F",
            "execution_sha": "sha-current",
            "evidence_type": "judge",
            "content_hash": content_hash,
        }

    def test_valid_chain_verifies(self):
        first = append_evidence_record([], self.record("e1"))
        second = append_evidence_record(first["chain"], self.record("e2", "content-b"))
        result = verify_evidence_chain(second["chain"], {"e1", "e2"})
        self.assertTrue(result["valid"])

    def test_modified_content_is_detected(self):
        first = append_evidence_record([], self.record("e1"))
        tampered = copy.deepcopy(first["chain"])
        tampered[0]["content_hash"] = "evil"
        self.assertFalse(verify_evidence_chain(tampered)["valid"])

    def test_missing_middle_record_is_detected(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        chain = append_evidence_record(chain, self.record("e2", "b"))["chain"]
        chain = append_evidence_record(chain, self.record("e3", "c"))["chain"]
        removed = [chain[0], chain[2]]
        self.assertFalse(verify_evidence_chain(removed)["valid"])

    def test_reordered_records_are_detected(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        chain = append_evidence_record(chain, self.record("e2", "b"))["chain"]
        reordered = [chain[1], chain[0]]
        self.assertFalse(verify_evidence_chain(reordered)["valid"])

    def test_substituted_record_is_detected(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        chain = append_evidence_record(chain, self.record("e2", "b"))["chain"]
        substituted = copy.deepcopy(chain)
        substituted[1]["evidence_id"] = "eX"
        self.assertFalse(verify_evidence_chain(substituted)["valid"])

    def test_duplicate_evidence_identity_cannot_append(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        result = append_evidence_record(chain, self.record("e1", "other"))
        self.assertFalse(result["accepted"])

    def test_required_evidence_missing_fails_closed(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        result = verify_evidence_chain(chain, {"e1", "e2"})
        self.assertFalse(result["valid"])
        self.assertEqual(["e2"], result["missing"])

    def test_previous_hash_mutation_is_detected(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        chain = append_evidence_record(chain, self.record("e2", "b"))["chain"]
        tampered = copy.deepcopy(chain)
        tampered[1]["previous_hash"] = "forged"
        self.assertFalse(verify_evidence_chain(tampered)["valid"])

    def test_sequence_mutation_is_detected(self):
        chain = append_evidence_record([], self.record("e1"))["chain"]
        tampered = copy.deepcopy(chain)
        tampered[0]["sequence"] = 9
        self.assertFalse(verify_evidence_chain(tampered)["valid"])

    def test_malformed_record_fails_closed(self):
        result = append_evidence_record([], {"evidence_id": "e1"})
        self.assertFalse(result["accepted"])


if __name__ == "__main__":
    unittest.main()
