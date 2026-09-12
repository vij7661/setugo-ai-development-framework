from __future__ import annotations

import types
import unittest
from unittest.mock import patch

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import (
    base_control,
    strict_event,
    declared,
    strict_executable,
    strict_envelope,
    cap_req,
    strict_manifest,
    strict_approval,
    strict_cfg,
)


STRICT = "REQUIREMENT_CANDIDATE"


def positive_execution_event(evidence_id="ECC-V5-E1-POS"):
    return strict_event() | {"reference_evidence_id": evidence_id}


def matching_execution_record(control, event, candidate="shaA", action_id="act1"):
    return {
        "kind": "execution",
        "candidate": candidate,
        "action_id": action_id,
        "control_id": control["control_id"],
        "control_version": control["version"],
        "control_digest": control["digest"],
        "process_identity": event["process_identity"],
        "action_sequence": event["verified_action_sequence"],
        "invocation_id": event["invocation_id"],
    }


def favorable_execution_result():
    return {
        "status": "VERIFIED",
        "verified": True,
        "allowed": True,
        "evaluation_class": STRICT,
    }


def matching_role_record(envelope):
    return {
        "kind": "role",
        "harness_id": envelope["harness_id"],
        "runtime_version": envelope["runtime_version"],
        "config_digest": envelope["config_digest"],
        "runtime_identity_digest": envelope["runtime_identity_digest"],
        "write_confinement": envelope["capabilities"]["write_confinement"],
    }


class ECCV11ModuleGlobalIntegrity(unittest.TestCase):
    def test_strict_helper_and_reference_store_mutation_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V11-C1") | {"execution_ok": False}
        forged_record = matching_execution_record(control, event)

        def malicious_strict(result, requirement_candidate):
            return favorable_execution_result()

        with patch.object(boundary.strict_core, "_strict", malicious_strict), patch.dict(
            boundary.reference_evidence._REFERENCE,
            {"FORGED-V11-C1": forged_record},
            clear=False,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result.get("status"), "VERIFIED")

    def test_reference_store_mutation_alone_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V11-REFERENCE")
        forged_record = matching_execution_record(control, event)

        with patch.dict(
            boundary.reference_evidence._REFERENCE,
            {"FORGED-V11-REFERENCE": forged_record},
            clear=False,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result.get("status"), "VERIFIED")

    def test_allowed_capability_global_mutation_cannot_promote_unknown_capability(self):
        envelope = strict_envelope() | {
            "reference_evidence_id": "FORGED-V11-ROLE",
            "capabilities": {"write_confinement": "FORGED_NATIVE"},
            "semantic_evidence": {"write_confinement": True},
        }
        required = {
            "write_confinement": {
                "allowed_classes": ["FORGED_NATIVE"],
                "semantic_evidence_required": True,
            }
        }
        forged_record = matching_role_record(envelope)
        mutated_allowed = set(boundary.strict_core._ALLOWED_CAP_CLASSES) | {"FORGED_NATIVE"}

        with patch.object(
            boundary.strict_core,
            "_ALLOWED_CAP_CLASSES",
            mutated_allowed,
        ), patch.dict(
            boundary.reference_evidence._REFERENCE,
            {"FORGED-V11-ROLE": forged_record},
            clear=False,
        ):
            result = boundary.qualify_role_binding_candidate(
                "R1", "user-selected-qualified-model", envelope, required
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result.get("status"), "ROLE_BINDING_ELIGIBLE")

    def test_public_covers_global_cannot_disable_legitimate_candidate_authority(self):
        event = positive_execution_event()
        with patch.object(boundary, "_COVERS", {"EXP-ECC-1"}):
            result = boundary.assess_control_execution_candidate(
                base_control(), event, candidate="shaA", action_id="act1"
            )
        self.assertEqual(result.get("status"), "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_same_code_new_function_globals_cannot_mint(self):
        original = boundary.strict_core.assess_control_execution_candidate
        malicious_globals = dict(original.__globals__)

        def malicious_assess(*args, **kwargs):
            return favorable_execution_result()

        malicious_globals["assess_control_execution"] = malicious_assess
        replacement = types.FunctionType(
            original.__code__,
            malicious_globals,
            name=original.__name__,
            argdefs=original.__defaults__,
            closure=original.__closure__,
        )
        replacement.__kwdefaults__ = original.__kwdefaults__

        event = positive_execution_event() | {"execution_ok": False}
        with patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            replacement,
        ):
            result = boundary.assess_control_execution_candidate(
                base_control(), event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result.get("status"), "VERIFIED")

    def test_legitimate_exp_ecc_1_through_5_candidate_paths_remain_positive(self):
        e1 = positive_execution_event()
        e2 = strict_executable() | {"reference_evidence_id": "ECC-V5-E2-POS"}
        e3 = strict_envelope() | {"reference_evidence_id": "ECC-V5-E3-POS"}
        a4 = strict_approval() | {"reference_evidence_id": "ECC-V5-E4-POS"}
        c5 = strict_cfg() | {"reference_evidence_id": "ECC-V5-E5-POS"}

        results = (
            boundary.assess_control_execution_candidate(
                base_control(), e1, candidate="shaA", action_id="act1"
            ),
            boundary.check_declared_executable_equivalence_candidate(declared(), e2),
            boundary.qualify_role_binding_candidate(
                "R1", "user-selected-qualified-model", e3, cap_req()
            ),
            boundary.authorize_power_activation_candidate(
                strict_manifest(),
                a4,
                ["WRITE"],
                role="R1",
                requested_resources=["repo"],
                current_sequence=7,
            ),
            boundary.check_tool_configuration_candidate(c5, dict(c5)),
        )
        expected = (
            "VERIFIED",
            "EQUIVALENT",
            "ROLE_BINDING_ELIGIBLE",
            "ACTIVATION_ALLOWED",
            "TOOL_CONFIG_CURRENT",
        )
        for result, status in zip(results, expected):
            with self.subTest(status=status):
                self.assertEqual(result.get("status"), status)
                self.assertTrue(boundary.candidate_result_eligible(result))

    def test_public_diagnostic_verifier_reports_current_policy_when_untampered(self):
        self.assertTrue(boundary.verify_runtime_policy())


if __name__ == "__main__":
    unittest.main()
