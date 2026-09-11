#!/usr/bin/env python3
from __future__ import annotations

import unittest

import manual_authority_verifier as testing_verifier
import qualification_boundary_policy_v4 as legacy
import qualification_boundary_policy_v7 as policy
import release_manual_authority_verifier as release_verifier
from external_governance_root import TRUST_ROOT_ID as TESTING_ROOT_ID
from release_external_governance_root import (
    RELEASE_TRUST_ROOT_ID,
    validate_release_repository_metadata,
    validate_release_root_metadata,
)

CANDIDATE = "f" * 40


class ReleaseR3PhaseScopedAuthorityTests(unittest.TestCase):
    def test_policy_v7_is_new_binding(self):
        self.assertEqual(policy.POLICY_VERSION, 7)
        self.assertNotEqual(policy.qualification_policy_hash(), legacy.qualification_policy_hash())
        material = policy._policy_material()
        self.assertTrue(material["cross_phase_root_reuse_forbidden"])
        self.assertEqual(material["release_authority_trust_root_id"], RELEASE_TRUST_ROOT_ID)

    def test_release_attestation_builder_selects_release_root(self):
        att = policy.build_unsigned_manual_attestation(
            candidate_sha=CANDIDATE,
            authority_class="HUMAN_RELEASE_AUTHORITY",
            decision_scope="TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
            evidence_ref="test-evidence",
        )
        self.assertEqual(att["trust_root_id"], RELEASE_TRUST_ROOT_ID)
        self.assertEqual(att["qualification_policy_version"], 7)

    def test_testing_attestation_builder_keeps_testing_root(self):
        att = policy.build_unsigned_manual_attestation(
            candidate_sha=CANDIDATE,
            authority_class="HUMAN_GOVERNANCE_OWNER",
            decision_scope="TERMINAL_ACTION:TESTING:READY_TO_BEGIN_RELEASE_QUALIFICATION",
            evidence_ref="test-evidence",
        )
        self.assertEqual(att["trust_root_id"], TESTING_ROOT_ID)

    def test_production_builder_fails_closed_without_production_root(self):
        with self.assertRaises(ValueError):
            policy.build_unsigned_manual_attestation(
                candidate_sha=CANDIDATE,
                authority_class="HUMAN_PRODUCTION_AUTHORITY",
                decision_scope="TERMINAL_ACTION:PRODUCTION:DEPLOY_PRODUCTION",
                evidence_ref="test-evidence",
            )

    def test_testing_verifier_rejects_release_authority_before_signature(self):
        ok, reason = testing_verifier.verify_manual_authority_attestation(
            {}, "",
            candidate_sha=CANDIDATE,
            required_authority_class="HUMAN_RELEASE_AUTHORITY",
            required_scope="TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
            qualification_policy_binding=policy.policy_binding(),
        )
        self.assertFalse(ok)
        self.assertIn("cannot satisfy RELEASE or PRODUCTION", reason)

    def test_release_verifier_rejects_testing_authority_before_signature(self):
        ok, reason = release_verifier.verify_release_authority_attestation(
            {}, "",
            candidate_sha=CANDIDATE,
            required_authority_class="HUMAN_GOVERNANCE_OWNER",
            required_scope="TERMINAL_ACTION:TESTING:READY_TO_BEGIN_RELEASE_QUALIFICATION",
            qualification_policy_binding=policy.policy_binding(),
        )
        self.assertFalse(ok)
        self.assertIn("cannot satisfy non-RELEASE", reason)

    def test_release_verifier_rejects_non_terminal_release_scope(self):
        ok, reason = release_verifier.verify_release_authority_attestation(
            {}, "",
            candidate_sha=CANDIDATE,
            required_authority_class="HUMAN_RELEASE_AUTHORITY",
            required_scope="REVIEW_FINDING_ADJUDICATION",
            qualification_policy_binding=policy.policy_binding(),
        )
        self.assertFalse(ok)
        self.assertIn("outside RELEASE terminal policy", reason)

    def test_release_root_metadata_requires_archived_public_identity(self):
        ok, _ = validate_release_repository_metadata({
            "id": 1364609306,
            "full_name": "vij7661/setugo-release-governance-root",
            "private": False,
            "archived": True,
        })
        self.assertTrue(ok)
        ok, _ = validate_release_repository_metadata({
            "id": 1364609306,
            "full_name": "vij7661/setugo-release-governance-root",
            "private": False,
            "archived": False,
        })
        self.assertFalse(ok)

    def test_release_root_metadata_is_scope_exact(self):
        payload = {
            "schema_version": 1,
            "trust_root_id": "SETUGO_RELEASE_GOVERNANCE_ED25519_V1",
            "algorithm": "Ed25519",
            "public_key_path": "trust-roots/SETUGO_RELEASE_GOVERNANCE_ED25519_V1.pem",
            "public_key_der_sha256": "91355cf1049a27aac52ea56f5ba1664054aded93500203cd23d557a710b0444c",
            "authority_scope": "RELEASE_TERMINAL_AUTHORITY_ATTESTATION_VERIFICATION_ONLY",
            "permitted_authority_class": "HUMAN_RELEASE_AUTHORITY",
            "permitted_decision_scopes": [
                "TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
                "TERMINAL_ACTION:RELEASE:BEGIN_PRODUCTION_QUALIFICATION",
            ],
            "private_key_location": "EXTERNAL_OFF_REPOSITORY_USER_CONTROLLED",
            "private_key_must_never_be_committed": True,
            "authority_effect": "NONE_BY_ITSELF",
        }
        ok, _ = validate_release_root_metadata(payload)
        self.assertTrue(ok)
        payload["permitted_decision_scopes"] = ["TERMINAL_ACTION:PRODUCTION:DEPLOY_PRODUCTION"]
        ok, _ = validate_release_root_metadata(payload)
        self.assertFalse(ok)

    def test_legacy_v4_release_path_now_fails_closed_on_testing_root(self):
        ok, reason = legacy.terminal_authority_allowed(
            phase="RELEASE",
            action="MERGE_RELEASE_CANDIDATE",
            candidate_sha=CANDIDATE,
            authority_binding={"attestation": {}, "signature_b64": ""},
        )
        self.assertFalse(ok)
        self.assertIn("cannot satisfy RELEASE or PRODUCTION", reason)


if __name__ == "__main__":
    unittest.main()
