from __future__ import annotations

import json
import pickle
import unittest
from unittest.mock import patch

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import base_control, strict_event


STRICT = "REQUIREMENT_CANDIDATE"


def positive_execution_event():
    return strict_event() | {"reference_evidence_id": "ECC-V5-E1-POS"}


class ECCV6EligibilityProvenance(unittest.TestCase):
    def genuine_result(self):
        return boundary.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )

    def test_caller_constructed_perfect_dictionary_is_not_eligible(self):
        forged = {
            "evaluation_class": STRICT,
            "candidate_eligible": True,
            "candidate_kind": "execution",
            "status": "VERIFIED",
            "verified": True,
            "allowed": True,
        }
        self.assertFalse(boundary.candidate_result_eligible(forged))

    def test_genuine_boundary_result_has_non_dictionary_provenance_type_and_is_eligible(self):
        result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertIsNot(type(result), dict)
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_plain_dict_copy_of_genuine_result_loses_eligibility(self):
        result = self.genuine_result()
        copied = dict(result)
        self.assertFalse(boundary.candidate_result_eligible(copied))

    def test_json_roundtrip_of_genuine_result_loses_process_local_provenance(self):
        result = self.genuine_result()
        reconstructed = json.loads(json.dumps(result))
        self.assertFalse(boundary.candidate_result_eligible(reconstructed))

    def test_pickle_cannot_launder_process_local_provenance(self):
        result = self.genuine_result()
        with self.assertRaises((TypeError, pickle.PicklingError)):
            pickle.dumps(result)

    def test_post_issuance_field_addition_invalidates_seal(self):
        result = self.genuine_result()
        result["caller_added_field"] = "launder"
        self.assertFalse(boundary.candidate_result_eligible(result))

    def test_post_issuance_favorable_status_substitution_invalidates_seal(self):
        result = self.genuine_result()
        result["status"] = "VERIFIED_DENY"
        self.assertFalse(boundary.candidate_result_eligible(result))

    def test_post_issuance_kind_substitution_invalidates_seal(self):
        result = self.genuine_result()
        result["candidate_kind"] = "equivalence"
        result["status"] = "EQUIVALENT"
        self.assertFalse(boundary.candidate_result_eligible(result))

    def test_copying_serialized_fields_and_marker_from_genuine_result_is_not_enough(self):
        genuine = self.genuine_result()
        forged = {k: v for k, v in genuine.items()}
        forged["candidate_eligible"] = True
        self.assertFalse(boundary.candidate_result_eligible(forged))

    def test_consumption_rechecks_runtime_policy(self):
        result = self.genuine_result()
        self.assertTrue(boundary.candidate_result_eligible(result))
        with patch.object(boundary, "verify_runtime_policy", return_value=False):
            self.assertFalse(boundary.candidate_result_eligible(result))

    def test_direct_strict_core_result_cannot_be_upgraded_by_marker_injection(self):
        raw = boundary.strict_core.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )
        self.assertEqual(raw.get("evaluation_class"), STRICT)
        raw["candidate_eligible"] = True
        raw["candidate_kind"] = "execution"
        self.assertFalse(boundary.candidate_result_eligible(raw))

    def test_boundary_failure_remains_ineligible_and_unsealed(self):
        with patch.object(boundary, "verify_runtime_policy", return_value=False):
            failed = boundary.assess_control_execution_candidate(
                base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
            )
        self.assertEqual(failed["status"], "CANDIDATE_BOUNDARY_POLICY_INVALID")
        self.assertFalse(boundary.candidate_result_eligible(failed))


if __name__ == "__main__":
    unittest.main()
