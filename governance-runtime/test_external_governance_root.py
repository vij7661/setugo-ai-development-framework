#!/usr/bin/env python3
from __future__ import annotations

import unittest

from external_governance_root import (
    EXTERNAL_REPOSITORY,
    EXTERNAL_REPOSITORY_ID,
    EXPECTED_PUBLIC_KEY_DER_SHA256,
    TRUST_ROOT_ID,
    TRUST_ROOT_PEM_PATH,
    validate_public_key_bytes,
    validate_repository_metadata,
    validate_root_metadata,
)

VALID_PEM = b"-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAhmU2zsYGvlLOwxCHAx2WyfWZTZMebwYLd5ZeK4XE5O0=\n-----END PUBLIC KEY-----\n"


def valid_repo():
    return {
        "id": EXTERNAL_REPOSITORY_ID,
        "full_name": EXTERNAL_REPOSITORY,
        "private": False,
        "archived": True,
    }


def valid_metadata():
    return {
        "schema_version": 1,
        "trust_root_id": TRUST_ROOT_ID,
        "algorithm": "Ed25519",
        "public_key_path": TRUST_ROOT_PEM_PATH,
        "public_key_der_sha256": EXPECTED_PUBLIC_KEY_DER_SHA256,
        "authority_scope": "TESTING_MANUAL_GOVERNANCE_ATTESTATION_VERIFICATION_ONLY",
        "private_key_location": "EXTERNAL_OFF_REPOSITORY_USER_CONTROLLED",
        "private_key_must_never_be_committed": True,
        "authority_effect": "NONE_BY_ITSELF",
    }


class ExternalGovernanceRootTests(unittest.TestCase):
    def test_archived_public_exact_repository_is_supported(self):
        ok, reason = validate_repository_metadata(valid_repo())
        self.assertTrue(ok, reason)

    def test_unarchived_repository_fails_closed(self):
        payload = valid_repo()
        payload["archived"] = False
        ok, reason = validate_repository_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("not archived", reason)

    def test_private_repository_fails_closed(self):
        payload = valid_repo()
        payload["private"] = True
        ok, reason = validate_repository_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("must be public", reason)

    def test_repository_identity_rebinding_fails_closed(self):
        payload = valid_repo()
        payload["full_name"] = "attacker/governance-root"
        ok, reason = validate_repository_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("identity mismatch", reason)

    def test_repository_id_rebinding_fails_closed(self):
        payload = valid_repo()
        payload["id"] = 1
        ok, reason = validate_repository_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("repository id mismatch", reason)

    def test_exact_external_root_metadata_is_supported(self):
        ok, reason = validate_root_metadata(valid_metadata())
        self.assertTrue(ok, reason)

    def test_trust_root_id_rebinding_fails_closed(self):
        payload = valid_metadata()
        payload["trust_root_id"] = "ATTACKER_ROOT"
        ok, reason = validate_root_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("trust_root_id", reason)

    def test_external_metadata_fingerprint_rebinding_fails_closed(self):
        payload = valid_metadata()
        payload["public_key_der_sha256"] = "0" * 64
        ok, reason = validate_root_metadata(payload)
        self.assertFalse(ok)
        self.assertIn("public_key_der_sha256", reason)

    def test_exact_external_public_key_is_supported(self):
        ok, reason = validate_public_key_bytes(VALID_PEM)
        self.assertTrue(ok, reason)

    def test_candidate_generated_replacement_public_key_fails_closed(self):
        attacker_pem = b"-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAgoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=\n-----END PUBLIC KEY-----\n"
        ok, _ = validate_public_key_bytes(attacker_pem)
        self.assertFalse(ok)

    def test_empty_external_public_key_fails_closed(self):
        ok, reason = validate_public_key_bytes(b"")
        self.assertFalse(ok)
        self.assertIn("missing", reason)


if __name__ == "__main__":
    unittest.main()
