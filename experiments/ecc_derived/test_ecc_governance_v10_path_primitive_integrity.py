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


class ECCV10PathPrimitiveIntegrity(unittest.TestCase):
    def genuine_result(self):
        return boundary.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )

    def test_path_read_text_substitution_plus_dependency_tamper_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V10-EVIDENCE")
        forged_record = matching_execution_record(control, event)

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
        forged_text = json.dumps(forged_manifest, sort_keys=True)

        original_read_text = boundary.Path.read_text

        def spoof_read_text(path, *args, **kwargs):
            if str(path).endswith("ecc_governance_trust_manifest.json"):
                return forged_text
            return original_read_text(path, *args, **kwargs)

        with patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            malicious_strict,
        ), patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            malicious_reference,
        ), patch.object(boundary.Path, "read_text", spoof_read_text):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))

        self.assertNotEqual(result["status"], "VERIFIED")

    def test_path_read_text_alias_cannot_disable_legitimate_authority(self):
        with patch.object(boundary.Path, "read_text", return_value="{}"):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_path_read_bytes_alias_cannot_disable_legitimate_authority(self):
        with patch.object(boundary.Path, "read_bytes", return_value=b"public-path-alias-spoof"):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_path_resolve_alias_cannot_disable_legitimate_authority(self):
        with patch.object(boundary.Path, "resolve", side_effect=OSError("public path alias substituted")):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_path_is_file_alias_cannot_disable_legitimate_authority(self):
        with patch.object(boundary.Path, "is_file", return_value=False):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_path_is_symlink_alias_cannot_disable_legitimate_authority(self):
        with patch.object(boundary.Path, "is_symlink", return_value=True):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_legitimate_candidate_path_remains_positive(self):
        result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))


if __name__ == "__main__":
    unittest.main()
