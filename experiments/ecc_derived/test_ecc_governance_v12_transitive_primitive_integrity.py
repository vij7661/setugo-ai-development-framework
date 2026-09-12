from __future__ import annotations

import unittest
from unittest.mock import patch

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import strict_cfg


class _FixedDigest:
    def __init__(self, digest):
        self._digest = digest

    def hexdigest(self):
        return self._digest


class ECCV12TransitivePrimitiveIntegrity(unittest.TestCase):
    def _reference_cfg(self):
        cfg = strict_cfg() | {"reference_evidence_id": "ECC-V5-E5-POS"}
        return cfg

    def _forged_argv_cfg(self):
        genuine = self._reference_cfg()
        forged = dict(genuine)
        # Permission remains identical because V11 already compares this semantic
        # field directly. V12 isolates the unclosed digest-only argv boundary.
        forged["permission_profile"] = genuine["permission_profile"]
        forged["argv"] = ["attacker", "--write", "/repo"]
        # Deliberately retain the genuine digest fields. Mutated digest primitives
        # can make strict recomputation falsely validate these stale digests.
        forged["argv_digest"] = genuine["argv_digest"]
        forged["canonical_digest"] = genuine["canonical_digest"]
        return genuine, forged

    def _forging_sha256(self, argv_digest, canonical_digest):
        def fake_sha256(data=b""):
            raw = bytes(data)
            if raw.lstrip().startswith(b"["):
                return _FixedDigest(argv_digest)
            return _FixedDigest(canonical_digest)
        return fake_sha256

    def test_hashlib_sha256_attribute_mutation_cannot_mint_forged_argv(self):
        expected, current = self._forged_argv_cfg()
        fake_sha256 = self._forging_sha256(
            expected["argv_digest"], expected["canonical_digest"]
        )
        with patch.object(boundary.strict_core.hashlib, "sha256", fake_sha256):
            result = boundary.check_tool_configuration_candidate(expected, current)
            self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result.get("status"), "TOOL_CONFIG_CURRENT")

    def test_json_dumps_attribute_mutation_cannot_mint_forged_argv(self):
        expected, current = self._forged_argv_cfg()
        original_dumps = boundary.strict_core.json.dumps
        genuine_material = {
            "tool_id": expected["tool_id"],
            "harness_id": expected["harness_id"],
            "transport": expected["transport"],
            "endpoint": expected["endpoint"],
            "argv": expected["argv"],
            "permission_profile": expected["permission_profile"],
            "credential_profile_fingerprint": expected["credential_profile_fingerprint"],
        }

        def fake_dumps(value, *args, **kwargs):
            if isinstance(value, list):
                return original_dumps(expected["argv"], *args, **kwargs)
            if isinstance(value, dict):
                return original_dumps(genuine_material, *args, **kwargs)
            return original_dumps(value, *args, **kwargs)

        with patch.object(boundary.strict_core.json, "dumps", fake_dumps):
            result = boundary.check_tool_configuration_candidate(expected, current)
            self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result.get("status"), "TOOL_CONFIG_CURRENT")

    def test_sha256_json_transitive_dependencies_are_runtime_bound(self):
        self.assertTrue(boundary.verify_runtime_policy())
        original = boundary.strict_core.hashlib.sha256
        with patch.object(boundary.strict_core.hashlib, "sha256", lambda data=b"": original(b"forged")):
            self.assertFalse(boundary.verify_runtime_policy())

    def test_json_dumps_transitive_dependency_is_runtime_bound(self):
        self.assertTrue(boundary.verify_runtime_policy())
        original = boundary.strict_core.json.dumps
        with patch.object(boundary.strict_core.json, "dumps", lambda value, *a, **k: original(value, *a, **k)):
            self.assertFalse(boundary.verify_runtime_policy())

    def test_reference_config_evidence_binds_permission_profile_and_actual_argv(self):
        record = boundary.reference_evidence._REFERENCE["ECC-V5-E5-POS"]
        self.assertEqual(record.get("permission_profile"), "r")
        self.assertEqual(record.get("argv"), ["x"])

    def test_permission_profile_drift_is_rejected_even_with_matching_digest_fields(self):
        expected = self._reference_cfg()
        current = dict(expected)
        current["permission_profile"] = "write"
        result = boundary.check_tool_configuration_candidate(expected, current)
        self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result.get("status"), "TOOL_CONFIG_CURRENT")

    def test_actual_argv_drift_is_rejected_even_with_matching_digest_fields(self):
        expected = self._reference_cfg()
        current = dict(expected)
        current["argv"] = ["attacker"]
        result = boundary.check_tool_configuration_candidate(expected, current)
        self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result.get("status"), "TOOL_CONFIG_CURRENT")

    def test_legitimate_exp_ecc_5_config_path_remains_positive(self):
        cfg = self._reference_cfg()
        result = boundary.check_tool_configuration_candidate(cfg, dict(cfg))
        self.assertEqual(result.get("status"), "TOOL_CONFIG_CURRENT")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_public_diagnostic_verifier_remains_positive_when_untampered(self):
        self.assertTrue(boundary.verify_runtime_policy())


if __name__ == "__main__":
    unittest.main()
