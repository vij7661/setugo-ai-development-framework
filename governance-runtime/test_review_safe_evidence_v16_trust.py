from __future__ import annotations

import base64
import copy
from dataclasses import replace
import json
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import review_safe_evidence_v16_trust as trust_module
from review_safe_evidence_v16_trust import (
    AUTHORITY_EFFECT, BootstrapRoot, CanonicalizationError, PinnedBootstrapTrustSet,
    PinnedRegistryHead, RECORD_TYPE_REQUIRED_ROLE, authority_policy_digest,
    bootstrap_trust_set_digest, canonical_bytes, canonical_sha256, load_strict_json,
    registry_digest, registry_signature_message, signed_record_signature_message,
    validate_bootstrap_trust_set, validate_governance_key_registry_chain,
    validate_pinned_registry_head, verify_signed_governance_record,
    verify_signed_governance_record_json,
)


def _priv(b: int) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(bytes([b]) * 32)


def _pub(priv: Ed25519PrivateKey) -> str:
    return base64.b64encode(priv.public_key().public_bytes_raw()).decode("ascii")


def _sig(priv: Ed25519PrivateKey, msg: bytes) -> str:
    return base64.b64encode(priv.sign(msg)).decode("ascii")


ROOT1, ROOT2, ROOT3, ROOT4, ISSUER, ATTACKER = (_priv(i) for i in (1, 2, 3, 4, 10, 11))
ROOT_INFO = {
    "root-1": ("root-key-1", "root-domain-1", ROOT1),
    "root-2": ("root-key-2", "root-domain-2", ROOT2),
    "root-3": ("root-key-3", "root-domain-3", ROOT3),
}


def finalize_trust(t: PinnedBootstrapTrustSet) -> PinnedBootstrapTrustSet:
    return replace(t, trust_set_digest=bootstrap_trust_set_digest(t))


def trust(*, threshold: int = 2, roots: tuple[BootstrapRoot, ...] | None = None,
          candidate_domains: frozenset[str] = frozenset({"candidate-domain"}),
          trust_set_id: str = "bootstrap-v16-test") -> PinnedBootstrapTrustSet:
    roots = roots or (
        BootstrapRoot("root-1", "root-key-1", "root-domain-1", _pub(ROOT1)),
        BootstrapRoot("root-2", "root-key-2", "root-domain-2", _pub(ROOT2)),
        BootstrapRoot("root-3", "root-key-3", "root-domain-3", _pub(ROOT3)),
    )
    return finalize_trust(PinnedBootstrapTrustSet(trust_set_id, threshold, roots, candidate_domains, ""))


def key_entry(*, issuer_id="issuer-1", key_id="issuer-key-1", state="ACTIVE",
              control_domain="issuer-domain", roles=None, public_key_b64=None,
              valid_from=1, revoked_at=None) -> dict:
    return {
        "issuer_id": issuer_id,
        "key_id": key_id,
        "control_domain_id": control_domain,
        "algorithm": "ED25519",
        "public_key_b64": public_key_b64 or _pub(ISSUER),
        "roles": roles or ["RAW_EVIDENCE_CAPTURE_AUTHORITY", "REVIEWER_QUALIFICATION_AUTHORITY"],
        "state": state,
        "valid_from_registry_sequence": valid_from,
        "revoked_at_registry_sequence": revoked_at,
    }


def _sign_registry(record: dict, *, trust_obj: PinnedBootstrapTrustSet | None = None, signers=None) -> None:
    trust_obj = trust_obj or trust()
    signers = signers or (("root-1", "root-key-1", ROOT1), ("root-2", "root-key-2", ROOT2))
    rows = []
    root_index = {(r.root_id, r.key_id): r for r in trust_obj.roots}
    for rid, kid, priv in signers:
        root = root_index.get((rid, kid))
        domain = root.control_domain_id if root is not None else "attacker-domain"
        msg = registry_signature_message(
            record["registry_digest"], trust_set_id=trust_obj.trust_set_id,
            trust_set_digest=trust_obj.trust_set_digest,
            root_id=rid, key_id=kid, control_domain_id=domain,
        )
        rows.append({"root_id": rid, "key_id": kid, "algorithm": "ED25519", "signature_b64": _sig(priv, msg)})
    record["bootstrap_signatures"] = rows


def make_registry(*, sequence=1, generation_id="gen-1", predecessor="GENESIS",
                  key=None, keys=None, signers=None, trust_obj: PinnedBootstrapTrustSet | None = None,
                  policy_digest: str | None = None) -> dict:
    if key is not None and keys is not None:
        raise ValueError("key xor keys")
    trust_obj = trust_obj or trust()
    record = {
        "schema_version": 1,
        "object_type": "GOVERNANCE_KEY_REGISTRY",
        "registry_id": "registry-1",
        "candidate_id": "candidate-1",
        "generation_id": generation_id,
        "trust_set_id": trust_obj.trust_set_id,
        "trust_set_digest": trust_obj.trust_set_digest,
        "authority_policy_digest": policy_digest or authority_policy_digest(),
        "sequence": sequence,
        "predecessor_registry_digest": predecessor,
        "keys": copy.deepcopy(keys if keys is not None else [key or key_entry()]),
        "registry_digest": "",
        "bootstrap_signatures": [],
    }
    record["registry_digest"] = registry_digest(record)
    _sign_registry(record, trust_obj=trust_obj, signers=signers)
    return record


def resign_registry(record: dict, *, trust_obj: PinnedBootstrapTrustSet | None = None) -> None:
    trust_obj = trust_obj or trust()
    record["registry_digest"] = registry_digest(record)
    _sign_registry(record, trust_obj=trust_obj)


def head_for(chain: list[dict], *, trust_obj: PinnedBootstrapTrustSet | None = None) -> PinnedRegistryHead:
    trust_obj = trust_obj or trust()
    r = chain[-1]
    return PinnedRegistryHead(
        anchor_id=f"head-{r['sequence']}",
        trust_set_id=trust_obj.trust_set_id,
        trust_set_digest=trust_obj.trust_set_digest,
        authority_policy_digest=r["authority_policy_digest"],
        registry_id=r["registry_id"],
        candidate_id=r["candidate_id"],
        sequence=r["sequence"],
        generation_id=r["generation_id"],
        registry_digest=r["registry_digest"],
    )


def make_signed_record(*, registry=None, registry_sequence=None, generation_id=None,
                       record_type="RAW_EVIDENCE_CAPTURE", declared_role=None,
                       issued_registry_digest=None, trust_set_id=None, trust_set_digest=None,
                       policy_digest=None, signer=ISSUER, issuer_id="issuer-1",
                       key_id="issuer-key-1", payload=None) -> dict:
    registry = registry or make_registry()
    payload = payload or {"evidence_id": "e-1", "bytes_digest": "a" * 64}
    sequence = registry["sequence"] if registry_sequence is None else registry_sequence
    generation = registry["generation_id"] if generation_id is None else generation_id
    digest = registry["registry_digest"] if issued_registry_digest is None else issued_registry_digest
    role = declared_role if declared_role is not None else RECORD_TYPE_REQUIRED_ROLE.get(
        record_type, "RAW_EVIDENCE_CAPTURE_AUTHORITY"
    )
    record = {
        "schema_version": 1,
        "object_type": "SIGNED_GOVERNANCE_RECORD",
        "record_type": record_type,
        "record_id": "record-1",
        "candidate_id": "candidate-1",
        "generation_id": generation,
        "snapshot_id": None,
        "trust_set_id": registry["trust_set_id"] if trust_set_id is None else trust_set_id,
        "trust_set_digest": registry["trust_set_digest"] if trust_set_digest is None else trust_set_digest,
        "authority_policy_digest": registry["authority_policy_digest"] if policy_digest is None else policy_digest,
        "issued_registry_sequence": sequence,
        "issued_registry_digest": digest,
        "issuer_id": issuer_id,
        "key_id": key_id,
        "required_role": role,
        "payload_digest": canonical_sha256(payload),
        "payload": payload,
        "signature_algorithm": "ED25519",
        "signature_b64": "",
    }
    record["signature_b64"] = _sig(signer, signed_record_signature_message(record))
    return record


class CanonicalizationTests(unittest.TestCase):
    def test_canonicalization_reorders_keys_and_normalizes_unicode(self):
        self.assertEqual(canonical_bytes({"b": 2, "a": "e\u0301"}), canonical_bytes({"a": "é", "b": 2}))

    def test_float_is_forbidden(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": 1.25})

    def test_large_integer_outside_interoperable_range_is_forbidden(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": 2**53})

    def test_lone_surrogate_is_rejected_as_canonicalization_error(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": "\ud800"})
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"x":"\\ud800"}')

    def test_normalized_key_collision_is_forbidden(self):
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"e\u0301": 1, "é": 2})

    def test_strict_json_rejects_duplicate_keys(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"a":1,"a":2}')

    def test_strict_json_rejects_float_tokens(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"x":1.5}')

    def test_strict_json_rejects_normalized_duplicate_keys(self):
        with self.assertRaises(CanonicalizationError):
            load_strict_json('{"e\\u0301":1,"\\u00e9":2}')


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_requires_at_least_two_control_domains(self):
        t = trust(roots=(
            BootstrapRoot("r1", "k1", "same", _pub(ROOT1)),
            BootstrapRoot("r2", "k2", "same", _pub(ROOT2)),
        ))
        self.assertFalse(validate_bootstrap_trust_set(t)["valid"])

    def test_candidate_controlled_bootstrap_root_is_rejected(self):
        t = trust(roots=(
            BootstrapRoot("r1", "k1", "candidate-domain", _pub(ROOT1)),
            BootstrapRoot("r2", "k2", "other", _pub(ROOT2)),
        ))
        self.assertFalse(validate_bootstrap_trust_set(t)["valid"])

    def test_duplicate_root_public_key_material_is_rejected(self):
        t = trust(roots=(
            BootstrapRoot("r1", "k1", "d1", _pub(ROOT1)),
            BootstrapRoot("r2", "k2", "d2", _pub(ROOT1)),
        ), candidate_domains=frozenset())
        self.assertTrue(any("PUBLIC_KEY_REUSE" in x for x in validate_bootstrap_trust_set(t)["problems"]))

    def test_registry_signature_message_binds_root_and_trust_set_identity(self):
        d = "a" * 64
        td = trust().trust_set_digest
        a = registry_signature_message(d, trust_set_id="t1", trust_set_digest=td, root_id="r1", key_id="k1", control_domain_id="d1")
        b = registry_signature_message(d, trust_set_id="t1", trust_set_digest=td, root_id="r2", key_id="k2", control_domain_id="d2")
        c = registry_signature_message(d, trust_set_id="t2", trust_set_digest=td, root_id="r1", key_id="k1", control_domain_id="d1")
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)

    def test_valid_bootstrap_still_does_not_claim_provisioning_proof(self):
        r = validate_bootstrap_trust_set(trust())
        self.assertTrue(r["valid"], r["problems"])
        self.assertFalse(r["qualified"])
        self.assertFalse(r["trust_anchor_provisioning_proven"])
        self.assertEqual(r["authority_effect"], AUTHORITY_EFFECT)

    def test_trust_set_digest_rejects_threshold_downgrade_under_reused_label(self):
        strict = trust(threshold=3)
        r = make_registry(trust_obj=strict, signers=(("root-1", "root-key-1", ROOT1), ("root-2", "root-key-2", ROOT2)))
        self.assertFalse(validate_governance_key_registry_chain([r], strict, expected_candidate_id="candidate-1")["valid"])
        downgraded_reusing_digest = PinnedBootstrapTrustSet(
            strict.trust_set_id, 2, strict.roots, strict.candidate_control_domain_ids, strict.trust_set_digest
        )
        self.assertFalse(validate_bootstrap_trust_set(downgraded_reusing_digest)["valid"])
        downgraded = finalize_trust(replace(downgraded_reusing_digest, trust_set_digest=""))
        result = validate_governance_key_registry_chain([r], downgraded, expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])

    def test_trust_set_digest_rejects_root_membership_change_under_reused_label(self):
        original = trust()
        changed = PinnedBootstrapTrustSet(
            original.trust_set_id, original.threshold_control_domains,
            original.roots[:2], original.candidate_control_domain_ids, original.trust_set_digest,
        )
        self.assertIn("BOOTSTRAP_TRUST_SET_DIGEST_MISMATCH", validate_bootstrap_trust_set(changed)["problems"])

    def test_trust_set_digest_rejects_candidate_exclusion_change_under_reused_label(self):
        original = trust()
        changed = PinnedBootstrapTrustSet(
            original.trust_set_id, original.threshold_control_domains, original.roots,
            frozenset(), original.trust_set_digest,
        )
        self.assertIn("BOOTSTRAP_TRUST_SET_DIGEST_MISMATCH", validate_bootstrap_trust_set(changed)["problems"])

    def test_registry_signature_message_binds_trust_set_digest(self):
        d = "a" * 64
        a = registry_signature_message(d, trust_set_id="same", trust_set_digest="1" * 64, root_id="r1", key_id="k1", control_domain_id="d1")
        b = registry_signature_message(d, trust_set_id="same", trust_set_digest="2" * 64, root_id="r1", key_id="k1", control_domain_id="d1")
        self.assertNotEqual(a, b)


class RegistryTests(unittest.TestCase):
    def test_generation_identifier_cannot_be_reused_after_intervening_generation(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry())
        r3 = make_registry(sequence=3, generation_id="gen-1", predecessor=r2["registry_digest"], key=key_entry())
        self.assertFalse(validate_governance_key_registry_chain([r1, r2, r3], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_governance_registry_rejects_public_key_alias_across_two_identities(self):
        shared = _pub(ISSUER)
        r = make_registry(keys=[
            key_entry(public_key_b64=shared),
            key_entry(issuer_id="issuer-2", key_id="issuer-key-2", control_domain="d2", public_key_b64=shared),
        ])
        self.assertTrue(any("PUBLIC_KEY_REUSE" in x for x in validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["problems"]))

    def test_new_key_cannot_backdate_first_appearance(self):
        r1 = make_registry()
        k2 = key_entry(issuer_id="issuer-2", key_id="issuer-key-2", control_domain="d2", public_key_b64=_pub(ATTACKER), valid_from=1)
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], keys=[key_entry(), k2])
        self.assertFalse(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_recompute_registry_digest_after_tamper_does_not_replace_bootstrap_signatures(self):
        r = make_registry()
        f = copy.deepcopy(r)
        f["keys"][0]["roles"].append("EFFECT_TOKEN_ISSUER_AUTHORITY")
        f["registry_digest"] = registry_digest(f)
        self.assertTrue(any("SIGNATURE_INVALID" in x for x in validate_governance_key_registry_chain([f], trust(), expected_candidate_id="candidate-1")["problems"]))

    def test_registry_chain_cannot_expand_roles_on_existing_key(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry(roles=[
            "RAW_EVIDENCE_CAPTURE_AUTHORITY", "REVIEWER_QUALIFICATION_AUTHORITY", "EFFECT_TOKEN_ISSUER_AUTHORITY"
        ]))
        self.assertFalse(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_chain_cannot_remove_prior_key(self):
        r1 = make_registry()
        k2 = key_entry(issuer_id="issuer-2", key_id="issuer-key-2", control_domain="d2", public_key_b64=_pub(ATTACKER), valid_from=2)
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=k2)
        self.assertFalse(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_chain_cannot_swap_public_key_under_existing_key_id(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry(public_key_b64=_pub(ATTACKER)))
        self.assertFalse(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_chain_predecessor_mismatch_is_rejected(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor="f" * 64, key=key_entry())
        self.assertFalse(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_extra_unsigned_top_level_field_is_rejected(self):
        r = make_registry()
        r["candidate_controlled"] = False
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_rotation_requires_exact_predecessor_and_new_generation(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry())
        self.assertTrue(validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")["valid"])
        bad = copy.deepcopy(r2)
        bad["generation_id"] = "gen-1"
        resign_registry(bad)
        self.assertFalse(validate_governance_key_registry_chain([r1, bad], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_single_bootstrap_signature_cannot_authenticate_registry(self):
        r = make_registry(signers=(("root-1", "root-key-1", ROOT1),))
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_two_independent_bootstrap_domains_authenticate_genesis_registry(self):
        r = make_registry()
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["registry_currentness_anchored"])

    def test_unknown_root_signature_does_not_count(self):
        r = make_registry(signers=(("root-1", "root-key-1", ROOT1), ("attacker-root", "attacker-key", ROOT4)))
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_current_registry_authority_policy_digest_must_match_verifier_policy(self):
        fake_policy = "f" * 64
        r = make_registry(policy_digest=fake_policy)
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertIn("KEY_REGISTRY_CURRENT_AUTHORITY_POLICY_DIGEST_MISMATCH", result["problems"])


class SignedRecordTests(unittest.TestCase):
    def verify(self, record, chain=None, **kw):
        bootstrap = kw.pop("bootstrap_trust", trust())
        chain = chain or [make_registry(trust_obj=bootstrap)]
        head = kw.pop("expected_current_registry_head", head_for(chain, trust_obj=bootstrap))
        return verify_signed_governance_record(
            record, registry_chain=chain, bootstrap_trust=bootstrap,
            expected_current_registry_head=head, expected_candidate_id="candidate-1",
            expected_generation_id=kw.pop("expected_generation_id", chain[-1]["generation_id"]),
            expected_record_type=kw.pop("expected_record_type", record["record_type"]), **kw,
        )

    def test_attacker_signature_with_untrusted_key_fails(self):
        reg = make_registry()
        self.assertFalse(self.verify(make_signed_record(registry=reg, signer=ATTACKER), [reg])["valid"])

    def test_candidate_controlled_issuer_domain_fails_even_with_valid_signature(self):
        reg = make_registry(key=key_entry(control_domain="candidate-domain"))
        self.assertFalse(self.verify(make_signed_record(registry=reg), [reg])["valid"])

    def test_current_generation_record_at_current_registry_validates(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry())
        self.assertTrue(self.verify(make_signed_record(registry=r2), [r1, r2])["valid"])

    def test_explicit_forbidden_domain_fails_even_with_valid_signature(self):
        reg = make_registry()
        self.assertFalse(self.verify(make_signed_record(registry=reg), [reg], forbidden_control_domain_ids=frozenset({"issuer-domain"}))["valid"])

    def test_generation_binding_cannot_be_changed_without_resigning(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["generation_id"] = "gen-X"
        result = self.verify(rec, [reg], expected_generation_id="gen-1")
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])

    def test_payload_tamper_and_sha_recompute_without_signature_fails(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["payload"]["evidence_id"] = "evil"
        rec["payload_digest"] = canonical_sha256(rec["payload"])
        result = self.verify(rec, [reg])
        self.assertTrue(result["content_integrity_verified"])
        self.assertFalse(result["valid"])

    def test_pinned_registry_head_trust_set_mismatch_fails_closed(self):
        reg = make_registry()
        h = head_for([reg])
        bad = replace(h, trust_set_id="other")
        self.assertFalse(validate_pinned_registry_head(bad, trust(), expected_candidate_id="candidate-1")["valid"])
        self.assertFalse(self.verify(make_signed_record(registry=reg), [reg], expected_current_registry_head=bad)["valid"])

    def test_record_extra_field_is_rejected_even_when_signature_was_valid_before_extra_field(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["candidate_controlled"] = False
        self.assertFalse(self.verify(rec, [reg])["valid"])

    def test_registry_key_without_required_role_fails(self):
        reg = make_registry(key=key_entry(roles=["REVIEWER_QUALIFICATION_AUTHORITY"]))
        self.assertFalse(self.verify(make_signed_record(registry=reg), [reg])["valid"])

    def test_revoked_current_key_cannot_grant_current_authority(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry(state="REVOKED", revoked_at=2))
        self.assertFalse(self.verify(make_signed_record(registry=r2), [r1, r2])["valid"])

    def test_role_mismatch_fails(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg, declared_role="REVIEWER_QUALIFICATION_AUTHORITY")
        result = self.verify(rec, [reg])
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH", result["problems"])

    def test_stale_expected_generation_cannot_validate_under_newer_current_registry(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry())
        old = make_signed_record(registry=r1)
        result = self.verify(old, [r1, r2], expected_generation_id="gen-1")
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_EXPECTED_GENERATION_NOT_CURRENT", result["problems"])

    def test_stale_registry_prefix_cannot_override_newer_pinned_head(self):
        r1 = make_registry()
        r2 = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry(state="REVOKED", revoked_at=2))
        result = self.verify(make_signed_record(registry=r1), [r1], expected_current_registry_head=head_for([r1, r2]), expected_generation_id="gen-1")
        self.assertFalse(result["valid"])
        self.assertFalse(result["registry_currentness_anchor_matched"])

    def test_strict_json_ingress_rejects_duplicate_signed_record_keys(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        raw = json.dumps(rec, separators=(",", ":"))
        raw = raw.replace('"record_id":"record-1"', '"record_id":"record-1","record_id":"evil"')
        result = verify_signed_governance_record_json(
            raw, registry_chain_json=[json.dumps(reg, separators=(",", ":"))],
            bootstrap_trust=trust(), expected_current_registry_head=head_for([reg]),
            expected_candidate_id="candidate-1", expected_generation_id="gen-1",
            expected_record_type="RAW_EVIDENCE_CAPTURE",
        )
        self.assertFalse(result["valid"])

    def test_unknown_key_id_fails_even_if_attacker_signs(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg, signer=ATTACKER, issuer_id="attacker", key_id="attacker-key")
        result = self.verify(rec, [reg])
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_KEY_NOT_IN_ISSUANCE_REGISTRY", result["problems"])

    def test_valid_signed_record_authenticates_but_never_qualifies(self):
        reg = make_registry()
        result = self.verify(make_signed_record(registry=reg), [reg])
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["issuer_signature_verified"])
        self.assertTrue(result["authority_registry_verified"])
        self.assertTrue(result["registry_currentness_anchor_matched"])
        self.assertFalse(result["qualified"])
        self.assertFalse(result["currentness_anchor_provisioning_proven"])

    def test_record_type_role_policy_cannot_be_selected_by_caller(self):
        reg = make_registry(key=key_entry(roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"]))
        rec = make_signed_record(registry=reg, record_type="BLOCKER_RESOLUTION", declared_role="RAW_EVIDENCE_CAPTURE_AUTHORITY")
        result = self.verify(rec, [reg], expected_record_type="BLOCKER_RESOLUTION")
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH", result["problems"])
        self.assertIn("SIGNED_RECORD_ISSUER_ROLE_NOT_AUTHORIZED", result["problems"])

    def test_record_signed_for_registry_fork_a_rejected_under_fork_b(self):
        r1 = make_registry()
        fork_a = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], key=key_entry())
        extra = key_entry(issuer_id="issuer-2", key_id="issuer-key-2", control_domain="d2", public_key_b64=_pub(ATTACKER), roles=["REVIEWER_QUALIFICATION_AUTHORITY"], valid_from=2)
        fork_b = make_registry(sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"], keys=[key_entry(), extra])
        rec = make_signed_record(registry=fork_a)
        result = self.verify(rec, [r1, fork_b], expected_current_registry_head=head_for([r1, fork_b]))
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_MISMATCH", result["problems"])

    def test_unknown_record_type_fails_closed(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg, record_type="UNKNOWN_GOVERNANCE_ACTION", declared_role="RAW_EVIDENCE_CAPTURE_AUTHORITY")
        result = self.verify(rec, [reg], expected_record_type="UNKNOWN_GOVERNANCE_ACTION")
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_TYPE_POLICY_UNKNOWN", result["problems"])

    def test_record_signed_under_prior_policy_digest_cannot_be_reinterpreted_by_code_drift(self):
        reg = make_registry(key=key_entry(roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"]))
        rec = make_signed_record(registry=reg, record_type="BLOCKER_RESOLUTION", declared_role="RAW_EVIDENCE_CAPTURE_AUTHORITY")
        pre = self.verify(rec, [reg], expected_record_type="BLOCKER_RESOLUTION")
        self.assertFalse(pre["valid"])
        old = RECORD_TYPE_REQUIRED_ROLE["BLOCKER_RESOLUTION"]
        try:
            RECORD_TYPE_REQUIRED_ROLE["BLOCKER_RESOLUTION"] = "RAW_EVIDENCE_CAPTURE_AUTHORITY"
            post = self.verify(rec, [reg], expected_record_type="BLOCKER_RESOLUTION")
            self.assertFalse(post["valid"])
            self.assertTrue(any("AUTHORITY_POLICY_DIGEST_MISMATCH" in x for x in post["problems"]))
        finally:
            RECORD_TYPE_REQUIRED_ROLE["BLOCKER_RESOLUTION"] = old

    def test_signed_record_trust_set_digest_is_signature_bound(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["trust_set_digest"] = "f" * 64
        result = self.verify(rec, [reg])
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_SIGNATURE_INVALID", result["problems"])

    def test_pinned_head_trust_set_digest_mismatch_fails_closed(self):
        reg = make_registry()
        h = head_for([reg])
        bad = replace(h, trust_set_digest="f" * 64)
        result = self.verify(make_signed_record(registry=reg), [reg], expected_current_registry_head=bad)
        self.assertFalse(result["valid"])

    def test_pinned_head_authority_policy_digest_mismatch_fails_closed(self):
        reg = make_registry()
        h = head_for([reg])
        bad = replace(h, authority_policy_digest="f" * 64)
        result = self.verify(make_signed_record(registry=reg), [reg], expected_current_registry_head=bad)
        self.assertFalse(result["valid"])


class IdentifierCanonicalizationTests(unittest.TestCase):
    def test_bootstrap_root_id_requires_canonical_nfc(self):
        t = trust(roots=(
            BootstrapRoot("e\u0301", "k1", "d1", _pub(ROOT1)),
            BootstrapRoot("r2", "k2", "d2", _pub(ROOT2)),
        ), candidate_domains=frozenset())
        self.assertTrue(any("NOT_CANONICAL_NFC" in x for x in validate_bootstrap_trust_set(t)["problems"]))

    def test_governance_key_id_requires_canonical_nfc(self):
        r = make_registry(key=key_entry(key_id="e\u0301"))
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("NOT_CANONICAL_NFC" in x for x in result["problems"]))

    def test_control_domain_id_requires_canonical_nfc(self):
        r = make_registry(key=key_entry(control_domain="e\u0301"))
        result = validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("NOT_CANONICAL_NFC" in x for x in result["problems"]))


class SchemaIntegerTests(unittest.TestCase):
    def test_registry_sequence_rejects_boolean(self):
        r = make_registry(sequence=True)
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_pinned_head_sequence_rejects_boolean(self):
        r = make_registry()
        h = replace(head_for([r]), sequence=True)
        self.assertFalse(validate_pinned_registry_head(h, trust(), expected_candidate_id="candidate-1")["valid"])

    def test_signed_record_issuance_sequence_rejects_boolean(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg, registry_sequence=True)
        self.assertFalse(SignedRecordTests().verify(rec, [reg])["valid"])

    def test_key_validity_sequence_rejects_boolean(self):
        r = make_registry(key=key_entry(valid_from=True))
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_key_revocation_sequence_rejects_boolean(self):
        r = make_registry(key=key_entry(state="REVOKED", revoked_at=True))
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_registry_schema_version_rejects_boolean(self):
        r = make_registry()
        r["schema_version"] = True
        resign_registry(r)
        self.assertFalse(validate_governance_key_registry_chain([r], trust(), expected_candidate_id="candidate-1")["valid"])

    def test_signed_record_schema_version_rejects_boolean(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["schema_version"] = True
        rec["signature_b64"] = _sig(ISSUER, signed_record_signature_message(rec))
        self.assertFalse(SignedRecordTests().verify(rec, [reg])["valid"])


if __name__ == "__main__":
    unittest.main()
