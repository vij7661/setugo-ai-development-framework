#!/usr/bin/env python3
from __future__ import annotations

import unittest

import qualification_boundary_policy_v4 as policy
from external_governance_root import (
    EXTERNAL_REPOSITORY,
    EXTERNAL_REPOSITORY_ID,
    EXTERNAL_ROOT_COMMIT,
    EXPECTED_PUBLIC_KEY_DER_SHA256,
    TRUST_ROOT_ID,
)


class ExternalRootPolicyBindingRegressionTests(unittest.TestCase):
    def test_policy_version_is_bumped_for_material_external_root_change(self):
        self.assertEqual(policy.POLICY_VERSION, 6)

    def test_policy_hash_material_binds_exact_external_root(self):
        material = policy._policy_material()
        self.assertEqual(material["manual_authority_external_repository"], EXTERNAL_REPOSITORY)
        self.assertEqual(material["manual_authority_external_repository_id"], EXTERNAL_REPOSITORY_ID)
        self.assertEqual(material["manual_authority_external_root_commit"], EXTERNAL_ROOT_COMMIT)
        self.assertEqual(material["manual_authority_trust_root_id"], TRUST_ROOT_ID)
        self.assertEqual(material["manual_authority_public_key_der_sha256"], EXPECTED_PUBLIC_KEY_DER_SHA256)
        self.assertTrue(material["manual_authority_external_root_must_be_public"])
        self.assertTrue(material["manual_authority_external_root_must_be_archived"])


if __name__ == "__main__":
    unittest.main()
