from __future__ import annotations

import copy
import hashlib
import json
import marshal
import unittest
from pathlib import Path
from unittest.mock import patch

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import base_control, strict_event


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


class ECCV9VerifierPrimitiveIntegrity(unittest.TestCase):
    def genuine_result(self):
        return boundary.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )

    def forged_inputs(self):
        control = base_control()
        event = positive_execution_event("FORGED-V9-EVIDENCE")
        record = matching_execution_record(control, event)
        return control, event, record

    def test_json_loads_substitution_plus_dependency_tamper_cannot_mint(self):
        control, event, forged_record = self.forged_inputs()

        def malicious_strict(*args, **kwargs):
            return favorable_execution_result()

        def malicious_reference(*args, **kwargs):
            return dict(forged_record)

        manifest_path = Path(boundary.__file__).resolve().parent / "ecc_governance_trust_manifest.json"
        trusted_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        forged_manifest = copy.deepcopy(trusted_manifest)
        forged_manifest["runtime_code_sha256"][
            "strict.assess_control_execution_candidate"
        ] = hashlib.sha256(marshal.dumps(malicious_strict.__code__)).hexdigest()
        forged_manifest["runtime_code_sha256"][
            "reference.lookup_reference_evidence"
        ] = hashlib.sha256(marshal.dumps(malicious_reference.__code__)).hexdigest()

        with patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            malicious_strict,
        ), patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            malicious_reference,
        ), patch.object(
            boundary.json,
            "loads",
            return_value=forged_manifest,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result["status"], "VERIFIED")

    def test_marshal_dumps_substitution_plus_dependency_tamper_cannot_mint(self):
        control, event, forged_record = self.forged_inputs()
        original_marshal_dumps = boundary.marshal.dumps
        trusted_strict = boundary.strict_core.assess_control_execution_candidate
        trusted_reference = boundary.reference_evidence.lookup_reference_evidence
        trusted_strict_bytes = original_marshal_dumps(trusted_strict.__code__)
        trusted_reference_bytes = original_marshal_dumps(trusted_reference.__code__)

        def malicious_strict(*args, **kwargs):
            return favorable_execution_result()

        def malicious_reference(*args, **kwargs):
            return dict(forged_record)

        def spoof_marshal(code):
            if code is malicious_strict.__code__:
                return trusted_strict_bytes
            if code is malicious_reference.__code__:
                return trusted_reference_bytes
            return original_marshal_dumps(code)

        with patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            malicious_strict,
        ), patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            malicious_reference,
        ), patch.object(
            boundary.marshal,
            "dumps",
            spoof_marshal,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result["status"], "VERIFIED")

    def test_json_dumps_substitution_cannot_mask_post_issuance_mutation(self):
        result = self.genuine_result()
        self.assertTrue(boundary.candidate_result_eligible(result))

        original_json_dumps = boundary.json.dumps
        trusted_serialization = original_json_dumps(
            dict(result), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        result["forged_extension"] = "MUTATED_AFTER_ISSUANCE"

        with patch.object(boundary.json, "dumps", return_value=trusted_serialization):
            self.assertFalse(boundary.candidate_result_eligible(result))

    def test_json_dumps_substitution_cannot_poison_new_candidate_seal(self):
        with patch.object(boundary.json, "dumps", return_value="{}"):
            result = self.genuine_result()

        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_marshal_alias_substitution_does_not_control_legitimate_candidate_authority(self):
        with patch.object(boundary.marshal, "dumps", return_value=b"public-alias-spoof"):
            result = self.genuine_result()

        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_legitimate_candidate_path_remains_positive(self):
        result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))


if __name__ == "__main__":
    unittest.main()
