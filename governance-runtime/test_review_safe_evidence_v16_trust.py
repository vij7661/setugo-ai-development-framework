from __future__ import annotations

import base64
import copy
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from review_safe_evidence_v16_trust import (
    AUTHORITY_EFFECT,
    BootstrapRoot,
    CanonicalizationError,
    PinnedBootstrapTrustSet,
    canonical_bytes,
    canonical_sha256,
    load_strict_json,
    registry_digest,
    registry_signature_message,
    signed_record_signature_message,
    validate_bootstrap_trust_set,
    validate_governance_key_registry_chain,
    verify_signed_governance_record,
)


def _priv(seed_byte: int) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(bytes([seed_byte]) * 32)


def _pub_b64(priv: Ed25519PrivateKey) -> str:
    raw = priv.public_key().public_bytes_raw()
    return base64.b64encode(raw).decode("ascii")


def _sig_b64(priv: Ed25519PrivateKey, message: bytes) -> str:
    return base64.b64encode(priv.sign(message)).decode("ascii")


ROOT1 = _priv(1)
ROOT2 = _priv(2)
ROOT3 = _priv(3)
ROOT4 = _priv(4)
ISSUER = _priv(10)
ATTACKER = _priv(11)


def trust() -> PinnedBootstrapTrustSet:
    return PinnedBootstrapTrustSet(
        trust_set_id="bootstrap-v16-test",
        threshold_control_domains=2,
        roots=(
            BootstrapRoot("root-1", "root-key-1", "root-domain-1", _pub_b64(ROOT1)),
            BootstrapRoot("root-2", "root-key-2", "root-domain-2", _pub_b64(ROOT2)),
            BootstrapRoot("root-3", "root-key-3", "root-domain-3", _pub_b64(ROOT3)),
        ),
        candidate_control_domain_ids=frozenset({"candidate-domain"}),
    )


def key_entry(
    *,
    state: str = "ACTIVE",
    control_domain: str = "issuer-domain",
    roles: list[str] | None = None,
    public_key_b64: str | None = None,
    valid_from: int = 1,
    revoked_at: int | None = None,
) -> dict:
    return {
        "issuer_id": "issuer-1",
        "key_id": "issuer-key-1",
        "control_domain_id": control_domain,
        "algorithm": "ED25519",
        "public_key_b64": public_key_b64 or _pub_b64(ISSUER),
        "roles": roles or ["RAW_EVIDENCE_CAPTURE_AUTHORITY", "REVIEWER_QUALIFICATION_AUTHORITY"],
        "state": state,
        "valid_from_registry_sequence": valid_from,
        "revoked_at_registry_sequence": revoked_at,
    }


def make_registry(
    *,
    sequence: int = 1,
    generation_id: str = "gen-1",
    predecessor: str = "GENESIS",
    key: dict | None = None,
    signers: tuple[tuple[str, str, Ed25519PrivateKey], ...] | None = None,
) -> dict:
    record = {
        "schema_version": 1,
        "object_type": "GOVERNANCE_KEY_REGISTRY",
        "registry_id": "registry-1",
        "candidate_id": "candidate-1",
        "generation_id": generation_id,
        "sequence": sequence,
        "predecessor_registry_digest": predecessor,
        "keys": [key or key_entry()],
        "registry_digest": "",
        "bootstrap_signatures": [],
    }
    record["registry_digest"] = registry_digest(record)
    signers = signers or (
        ("root-1", "root-key-1", ROOT1),
        ("root-2", "root-key-2", ROOT2),
    )
    msg = registry_signature_message(record["registry_digest"])
    record["bootstrap_signatures"] = [
        {
            "root_id": rid,
            "key_id": kid,
            "algorithm": "ED25519",
            "signature_b64": _sig_b64(priv, msg),
        }
        for rid, kid, priv in signers
    ]
    return record


def make_signed_record(
    *,
    registry_sequence: int = 1,
    generation_id: str = "gen-1",
    role: str = "RAW_EVIDENCE_CAPTURE_AUTHORITY",
    signer: Ed25519PrivateKey = ISSUER,
    issuer_id: str = "issuer-1",
    key_id: str = "issuer-key-1",
    payload: dict | None = None,
) -> dict:
    payload = payload or {"evidence_id": "e-1", "bytes_digest": "a" * 64}
    record = {
        "schema_version": 1,
        "object_type": "SIGNED_GOVERNANCE_RECORD",
        "record_type": "RAW_EVIDENCE_CAPTURE",
        "record_id": "record-1",
        "candidate_id": "candidate-1",
        "generation_id": generation_id,
        "snapshot_id": None,
        "issued_registry_sequence": registry_sequence,
        "issuer_id": issuer_id,
        "key_id": key_id,
        "required_role": role,
        "payload_digest": canonical_sha256(payload),
        "payload": payload,
        "signature_algorithm": "ED25519",
        "signature_b64": "",
    }
    record["signature_b64"] = _sig_b64(signer, signed_record_signature_message(record))
    return record


class CanonicalizationTests(unittest.TestCase):
    def test_canonicalization_reorders_keys_and_normalizes_unicode(self):
        a = {"b": 2, "a": "e\u0301"}
        b = {"a": "\u00e9", "b": 2}
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual(canonical_sha256(a), canonical_sha256(b))

    def test_float_is_forbidden(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": 1.25})

    def test_normalized_key_collision_is_forbidden(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"e\u0301": 1, "\u00e9": 2})

    def test_strict_json_rejects_duplicate_keys(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"a":1,"a":2}')

    def test_strict_json_rejects_normalized_duplicate_keys(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"e\\u0301":1,"\\u00e9":2}')

    def test_strict_json_rejects_float_tokens(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"x":1.5}')


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_requires_at_least_two_control_domains(self):
        t = PinnedBootstrapTrustSet(
            trust_set_id="t",
            threshold_control_domains=2,
            roots=(
                BootstrapRoot("r1", "k1", "same", _pub_b64(ROOT1)),
                BootstrapRoot("r2", "k2", "same", _pub_b64(ROOT2)),
            ),
        )
        result = validate_bootstrap_trust_set(t)
        self.assertFalse(result["valid"])
        self.assertIn("BOOTSTRAP_THRESHOLD_EXCEEDS_DISTINCT_DOMAINS", result["problems"])

    def test_candidate_controlled_bootstrap_root_is_rejected(self):
        t = PinnedBootstrapTrustSet(
            trust_set_id="t",
            threshold_control_domains=2,
            roots=(
                BootstrapRoot("r1", "k1", "candidate-domain", _pub_b64(ROOT1)),
                BootstrapRoot("r2", "k2", "other", _pub_b64(ROOT2)),
            ),
            candidate_control_domain_ids=frozenset({"candidate-domain"}),
        )
        result = validate_bootstrap_trust_set(t)
        self.assertFalse(result["valid"])
        self.assertTrue(any("BOOTSTRAP_ROOT_CANDIDATE_CONTROLLED" in x for x in result["problems"]))

    def test_valid_bootstrap_still_does_not_claim_provisioning_proof(self):
        result = validate_bootstrap_trust_set(trust())
        self.assertTrue(result["valid"])
        self.assertFalse(result["trust_anchor_provisioning_proven"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], AUTHORITY_EFFECT)


class RegistryTests(unittest.TestCase):
    def test_two_independent_bootstrap_domains_authenticate_genesis_registry(self):
        r = make_registry()
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(len(result["bootstrap_authenticated_control_domains"]), 2)
        self.assertFalse(result["qualified"])

    def test_single_bootstrap_signature_cannot_authenticate_registry(self):
        r = make_registry(signers=(("root-1", "root-key-1", ROOT1),))
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("THRESHOLD_NOT_MET" in x for x in result["problems"]))

    def test_unknown_root_signature_does_not_count(self):
        r = make_registry(
            signers=(
                ("root-1", "root-key-1", ROOT1),
                ("attacker-root", "attacker-key", ROOT4),
            )
        )
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNER_UNKNOWN" in x for x in result["problems"]))

    def test_recompute_registry_digest_after_tamper_does_not_replace_bootstrap_signatures(self):
        r = make_registry()
        forged = copy.deepcopy(r)
        forged["keys"][0]["roles"].append("EFFECT_TOKEN_ISSUER_AUTHORITY")
        forged["registry_digest"] = registry_digest(forged)
        result = validate_governance_key_registry_chain([forged], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNATURE_INVALID" in x for x in result["problems"]))

    def test_registry_extra_unsigned_top_level_field_is_rejected(self):
        r = make_registry()
        r["candidate_controlled"] = False
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("TOP_LEVEL_FIELDS_NOT_EXACT" in x for x in result["problems"]))

    def test_registry_rotation_requires_exact_predecessor_and_new_generation(self):
        r1 = make_registry()
        r2 = make_registry(
            sequence=2,
            generation_id="gen-2",
            predecessor=r1["registry_digest"],
            key=key_entry(valid_from=1),
        )
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertTrue(result["valid"], result["problems"])

        bad = copy.deepcopy(r2)
        bad["generation_id"] = "gen-1"
        bad["registry_digest"] = registry_digest(bad)
        msg = registry_signature_message(bad["registry_digest"])
        bad["bootstrap_signatures"] = [
            {"root_id": "root-1", "key_id": "root-key-1", "algorithm": "ED25519", "signature_b64": _sig_b64(ROOT1, msg)},
            {"root_id": "root-2", "key_id": "root-key-2", "algorithm": "ED25519", "signature_b64": _sig_b64(ROOT2, msg)},
        ]
        result2 = validate_governance_key_registry_chain([r1, bad], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result2["valid"])
        self.assertTrue(any("REQUIRES_NEW_GENERATION" in x for x in result2["problems"]))

    def test_registry_chain_predecessor_mismatch_is_rejected(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor="f" * 64)
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("PREDECESSOR_MISMATCH" in x for x in result["problems"]))

    def test_registry_chain_cannot_remove_prior_key(self):
        r1 = make_registry()
        new_key = key_entry(public_key_b64=_pub_b64(ATTACKER))
        new_key["key_id"] = "issuer-key-2"
        r2 = make_registry(
            sequence=2,
            generation_id="gen-2",
            predecessor=r1["registry_digest"],
            key=new_key,
        )
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("KEY_REMOVAL_FORBIDDEN" in x for x in result["problems"]))

    def test_registry_chain_cannot_swap_public_key_under_existing_key_id(self):
        r1 = make_registry()
        swapped = key_entry(public_key_b64=_pub_b64(ATTACKER))
        r2 = make_registry(
            sequence=2,
            generation_id="gen-2",
            predecessor=r1["registry_digest"],
            key=swapped,
        )
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("KEY_IDENTITY_MUTATION_FORBIDDEN:issuer-key-1:public_key_b64" in x for x in result["problems"]))

    def test_registry_chain_cannot_expand_roles_on_existing_key(self):
        r1 = make_registry()
        expanded = key_entry(
            roles=[
                "RAW_EVIDENCE_CAPTURE_AUTHORITY",
                "REVIEWER_QUALIFICATION_AUTHORITY",
                "EFFECT_TOKEN_ISSUER_AUTHORITY",
            ]
        )
        r2 = make_registry(
            sequence=2,
            generation_id="gen-2",
            predecessor=r1["registry_digest"],
            key=expanded,
        )
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("KEY_IDENTITY_MUTATION_FORBIDDEN:issuer-key-1:roles" in x for x in result["problems"]))


class SignedRecordTests(unittest.TestCase):
    def verify(self, record: dict, chain: list[dict] | None = None, **kwargs):
        return verify_signed_governance_record(
            record,
            registry_chain=chain or [make_registry()],
            bootstrap_trust=trust(),
            expected_candidate_id="candidate-1",
            expected_generation_id=kwargs.pop("expected_generation_id", "gen-1"),
            expected_record_type="RAW_EVIDENCE_CAPTURE",
            required_role=kwargs.pop("required_role", "RAW_EVIDENCE_CAPTURE_AUTHORITY"),
            **kwargs,
        )

    def test_valid_signed_record_authenticates_but_never_qualifies(self):
        result = self.verify(make_signed_record())
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["issuer_signature_verified"])
        self.assertTrue(result["authority_registry_verified"])
        self.assertFalse(result["trust_anchor_provisioning_proven"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], AUTHORITY_EFFECT)

    def test_payload_tamper_and_sha_recompute_without_signature_fails(self):
        r = make_signed_record()
        forged = copy.deepcopy(r)
        forged["payload"]["evidence_id"] = "attacker-value"
        forged["payload_digest"] = canonical_sha256(forged["payload"])
        result = self.verify(forged)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])

    def test_attacker_signature_with_untrusted_key_fails(self):
        r = make_signed_record(signer=ATTACKER)
        result = self.verify(r)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])

    def test_unknown_key_id_fails_even_if_attacker_signs(self):
        r = make_signed_record(signer=ATTACKER, issuer_id="attacker", key_id="attacker-key")
        result = self.verify(r)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_KEY_NOT_IN_CURRENT_REGISTRY", result["problems"])

    def test_role_mismatch_fails(self):
        r = make_signed_record(role="REVIEWER_QUALIFICATION_AUTHORITY")
        result = self.verify(r)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH", result["problems"])

    def test_registry_key_without_required_role_fails(self):
        reg = make_registry(key=key_entry(roles=["REVIEWER_QUALIFICATION_AUTHORITY"]))
        r = make_signed_record()
        result = self.verify(r, [reg])
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_ISSUER_ROLE_NOT_AUTHORIZED", result["problems"])

    def test_candidate_controlled_issuer_domain_fails_even_with_valid_signature(self):
        reg = make_registry(key=key_entry(control_domain="candidate-domain"))
        r = make_signed_record()
        result = self.verify(r, [reg])
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_ISSUER_CANDIDATE_CONTROLLED_DOMAIN", result["problems"])

    def test_explicit_forbidden_domain_fails_even_with_valid_signature(self):
        r = make_signed_record()
        result = self.verify(r, forbidden_control_domain_ids=frozenset({"issuer-domain"}))
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_ISSUER_FORBIDDEN_CONTROL_DOMAIN", result["problems"])

    def test_revoked_current_key_cannot_grant_current_authority(self):
        r1 = make_registry()
        revoked = key_entry(state="REVOKED", valid_from=1, revoked_at=2)
        r2 = make_registry(
            sequence=2,
            generation_id="gen-2",
            predecessor=r1["registry_digest"],
            key=revoked,
        )
        record = make_signed_record(registry_sequence=1, generation_id="gen-2")
        result = self.verify(record, [r1, r2], expected_generation_id="gen-2")
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_KEY_NOT_CURRENTLY_ACTIVE", result["problems"])

    def test_generation_binding_cannot_be_changed_without_resigning(self):
        r = make_signed_record()
        forged = copy.deepcopy(r)
        forged["generation_id"] = "gen-2"
        result = self.verify(forged)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_GENERATION_MISMATCH", result["problems"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])

    def test_record_extra_field_is_rejected_even_when_signature_was_valid_before_extra_field(self):
        r = make_signed_record()
        r["candidate_controlled"] = False
        result = self.verify(r)
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_FIELDS_NOT_EXACT", result["problems"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])


if __name__ == "__main__":
    unittest.main()
