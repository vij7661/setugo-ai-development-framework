from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
import copy
import json
import unittest

import review_safe_evidence_v16_trust as trust_module
from review_safe_evidence_v16_trust import (
    BootstrapRoot,
    PinnedBootstrapTrustSet,
    canonical_bytes,
    load_strict_json,
    signed_record_signature_message,
    validate_bootstrap_trust_set,
    validate_governance_key_registry_chain,
    validate_governance_key_registry_chain_json,
    validation_profile_digest,
    verify_signed_governance_record,
    verify_signed_governance_record_json,
)
from test_review_safe_evidence_v16_trust import (
    ISSUER,
    ROOT1,
    _pub,
    _sig,
    head_for,
    key_entry,
    make_registry,
    make_signed_record,
    resign_registry,
    trust,
)


class _ReadOnlyAdversarialMapping(Mapping):
    """A non-dict Mapping must never be trusted as an owned validation object."""

    def __init__(self, data: dict):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class StrictIngressIdentityTests(unittest.TestCase):
    def test_load_strict_json_preserves_non_nfc_string_value(self):
        value = load_strict_json('{"record_id":"e\\u0301"}')
        self.assertEqual(value["record_id"], "e\u0301")
        self.assertNotEqual(value["record_id"], "é")

    def test_strict_json_rejects_non_nfc_signed_record_identifier(self):
        reg = make_registry()
        rec = make_signed_record(registry=reg)
        rec["record_id"] = "e\u0301"
        rec["signature_b64"] = _sig(ISSUER, signed_record_signature_message(rec))
        result = verify_signed_governance_record_json(
            json.dumps(rec, separators=(",", ":")),
            registry_chain_json=[json.dumps(reg, separators=(",", ":"))],
            bootstrap_trust=trust(),
            expected_current_registry_head=head_for([reg]),
            expected_candidate_id="candidate-1",
            expected_generation_id="gen-1",
            expected_record_type="RAW_EVIDENCE_CAPTURE",
        )
        self.assertFalse(result["valid"])
        self.assertIn("SIGNED_RECORD_ID_NOT_CANONICAL_NFC", result["problems"])

    def test_strict_json_rejects_non_nfc_registry_identifier(self):
        reg = make_registry()
        reg["registry_id"] = "e\u0301"
        resign_registry(reg)
        result = validate_governance_key_registry_chain_json(
            [json.dumps(reg, separators=(",", ":"))],
            trust(), expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("KEY_REGISTRY_ID_NOT_CANONICAL_NFC" in p for p in result["problems"]))


class CrossTierKeyReuseTests(unittest.TestCase):
    def test_genesis_governance_key_cannot_reuse_bootstrap_root_key(self):
        reg = make_registry(key=key_entry(public_key_b64=_pub(ROOT1)))
        result = validate_governance_key_registry_chain([reg], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN" in p for p in result["problems"]))

    def test_later_governance_key_cannot_reuse_bootstrap_root_key(self):
        r1 = make_registry()
        root_alias = key_entry(
            issuer_id="issuer-root-alias", key_id="issuer-root-alias-key",
            control_domain="issuer-root-alias-domain", public_key_b64=_pub(ROOT1),
            valid_from=2,
        )
        r2 = make_registry(
            sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"],
            keys=[key_entry(), root_alias],
        )
        result = validate_governance_key_registry_chain([r1, r2], trust(), expected_candidate_id="candidate-1")
        self.assertFalse(result["valid"])
        self.assertTrue(any("BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN" in p for p in result["problems"]))


class MutableIngressTests(unittest.TestCase):
    def test_bootstrap_mutable_root_list_is_rejected(self):
        good = trust()
        bad = PinnedBootstrapTrustSet(
            good.trust_set_id, good.threshold_control_domains,
            list(good.roots),  # type: ignore[arg-type]
            good.candidate_control_domain_ids, good.trust_set_digest,
        )
        result = validate_bootstrap_trust_set(bad)
        self.assertFalse(result["valid"])
        self.assertIn("BOOTSTRAP_ROOT_CONTAINER_MUST_BE_TUPLE", result["problems"])

    def test_bootstrap_mutable_candidate_domain_set_is_rejected(self):
        good = trust()
        bad = PinnedBootstrapTrustSet(
            good.trust_set_id, good.threshold_control_domains,
            good.roots, set(good.candidate_control_domain_ids),  # type: ignore[arg-type]
            good.trust_set_digest,
        )
        result = validate_bootstrap_trust_set(bad)
        self.assertFalse(result["valid"])
        self.assertIn("BOOTSTRAP_CANDIDATE_DOMAIN_CONTAINER_MUST_BE_FROZENSET", result["problems"])

    def test_custom_mapping_registry_is_rejected_before_authority_validation(self):
        reg = make_registry()
        result = validate_governance_key_registry_chain(
            [_ReadOnlyAdversarialMapping(reg)], trust(), expected_candidate_id="candidate-1"
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("NON_PLAIN_JSON_CONTAINER" in p for p in result["problems"]))

    def test_custom_mapping_signed_record_is_rejected_before_authority_validation(self):
        reg = make_registry()
        rec = _ReadOnlyAdversarialMapping(make_signed_record(registry=reg))
        result = verify_signed_governance_record(
            rec, registry_chain=[reg], bootstrap_trust=trust(),
            expected_current_registry_head=head_for([reg]),
            expected_candidate_id="candidate-1", expected_generation_id="gen-1",
            expected_record_type="RAW_EVIDENCE_CAPTURE",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("NON_PLAIN_JSON_CONTAINER" in p for p in result["problems"]))


class ValidationProfileTests(unittest.TestCase):
    def test_validation_profile_digest_changes_when_schema_field_set_changes(self):
        before = validation_profile_digest()
        old = trust_module.REGISTRY_TOP_LEVEL_FIELDS
        try:
            trust_module.REGISTRY_TOP_LEVEL_FIELDS = frozenset(set(old) | {"future_load_bearing_field"})
            after = validation_profile_digest()
            self.assertNotEqual(before, after)
        finally:
            trust_module.REGISTRY_TOP_LEVEL_FIELDS = old

    def test_validation_profile_digest_changes_when_signature_domain_changes(self):
        before = validation_profile_digest()
        old = trust_module.SIGNED_RECORD_SIGNATURE_DOMAIN
        try:
            trust_module.SIGNED_RECORD_SIGNATURE_DOMAIN = old + "DRIFT"
            after = validation_profile_digest()
            self.assertNotEqual(before, after)
        finally:
            trust_module.SIGNED_RECORD_SIGNATURE_DOMAIN = old


class CanonicalizationProfileTests(unittest.TestCase):
    def test_non_bmp_and_bmp_object_keys_use_declared_codepoint_order(self):
        value = {"\U00010000": 1, "\ue000": 2}
        self.assertEqual(canonical_bytes(value), '{"\ue000":2,"\U00010000":1}'.encode("utf-8"))

    def test_control_character_uses_lowercase_u_escape(self):
        self.assertEqual(canonical_bytes({"x": "\x01"}), b'{"x":"\\u0001"}')


if __name__ == "__main__":
    unittest.main()
