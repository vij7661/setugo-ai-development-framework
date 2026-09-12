from __future__ import annotations

import unittest

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import base_control, strict_event


STRICT = "REQUIREMENT_CANDIDATE"


def positive_execution_event():
    return strict_event() | {"reference_evidence_id": "ECC-V5-E1-POS"}


def forged_execution_payload():
    return {
        "evaluation_class": STRICT,
        "candidate_eligible": True,
        "candidate_kind": "execution",
        "status": "VERIFIED",
        "verified": True,
        "allowed": True,
    }


class ECCV7SealCapability(unittest.TestCase):
    def test_module_does_not_export_raw_seal_capability(self):
        self.assertFalse(
            hasattr(boundary, "_seal_candidate_result"),
            "module-global seal helper lets callers mint boundary provenance directly",
        )

    def test_module_does_not_export_candidate_result_constructor(self):
        self.assertFalse(
            hasattr(boundary, "_CandidateEvaluationResult"),
            "candidate provenance constructor should remain closure-private",
        )

    def test_generic_typed_helper_cannot_mint_positive_candidate_authority(self):
        helper = getattr(boundary, "_typed", None)
        if helper is None:
            return
        result = helper("execution", forged_execution_payload(), eligible=True)
        self.assertFalse(
            boundary.candidate_result_eligible(result),
            "generic formatting helper must not be an alternate authority issuer",
        )

    def test_finish_positive_helper_cannot_mint_from_arbitrary_payload(self):
        helper = getattr(boundary, "_finish_positive", None)
        if helper is None:
            return
        result = helper("execution", forged_execution_payload())
        self.assertFalse(
            boundary.candidate_result_eligible(result),
            "internal finish helper must not be callable as a bypass around evidence checks",
        )

    def test_legitimate_candidate_entrypoint_still_issues_eligible_result(self):
        result = boundary.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_plain_forged_dictionary_remains_ineligible(self):
        self.assertFalse(boundary.candidate_result_eligible(forged_execution_payload()))

    def test_boundary_namespace_has_no_known_capability_bearing_shortcuts(self):
        exposed = {
            name
            for name in (
                "_seal_candidate_result",
                "_CandidateEvaluationResult",
                "_finish_positive",
            )
            if hasattr(boundary, name)
        }
        self.assertEqual(exposed, set())


if __name__ == "__main__":
    unittest.main()
