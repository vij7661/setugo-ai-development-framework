import unittest

from semantic_invariants import (
    authorize_semantic_routing,
    extract_structured_invariants,
    semantic_compatibility_gate,
    validate_invariant_completeness,
)


class ExpFSemanticInvariantTests(unittest.TestCase):
    def _policy(self):
        return {
            "task_class": "GOVERNANCE_RELEASE",
            "policy_ref": "task-policy-v1",
            "required_invariant_ids": ["INV-AUTH-001", "INV-VERIFY-001"],
        }

    def _contract(self):
        return {
            "semantic_invariants": [
                {
                    "id": "INV-AUTH-001",
                    "source": "governance-policy-v1",
                    "scope": "consequential-actions",
                    "strength": "MUST_NOT",
                    "predicate": {"subject": "model", "action": "self_authorize_consequential_action", "polarity": "FORBID"},
                },
                {
                    "id": "INV-VERIFY-001",
                    "source": "governance-policy-v1",
                    "scope": "release-gate",
                    "strength": "MUST",
                    "predicate": {"subject": "release_gate", "action": "require_independent_verification", "polarity": "REQUIRE"},
                },
            ]
        }

    def _preserving_candidate(self):
        return {
            "semantic_claims": [
                {"subject": "model", "action": "self_authorize_consequential_action", "polarity": "FORBID"},
                {"subject": "release_gate", "action": "require_independent_verification", "polarity": "REQUIRE"},
            ]
        }

    def test_reworded_self_authorization_is_detected_as_semantic_contradiction(self):
        candidate = {"semantic_claims": [
            {"surface_text": "An autonomous agent may approve its own routine deployment.", "subject": "model", "action": "self_authorize_consequential_action", "polarity": "REQUIRE"},
            {"surface_text": "Independent verification remains mandatory before release.", "subject": "release_gate", "action": "require_independent_verification", "polarity": "REQUIRE"},
        ]}
        gate = semantic_compatibility_gate(self._contract(), candidate)
        self.assertFalse(gate["compatible"])
        self.assertEqual(gate["reason"], "semantic contradiction detected")

    def test_asserted_compatibility_cannot_override_semantic_contradiction(self):
        candidate = self._preserving_candidate()
        candidate["semantic_claims"][0]["polarity"] = "REQUIRE"
        candidate["compatible"] = True
        decision = authorize_semantic_routing(self._contract(), candidate, self._policy())
        self.assertFalse(decision["authorized"])

    def test_missing_semantic_claim_fails_closed(self):
        candidate = {"semantic_claims": [{"subject": "model", "action": "self_authorize_consequential_action", "polarity": "FORBID"}]}
        gate = semantic_compatibility_gate(self._contract(), candidate)
        self.assertFalse(gate["compatible"])
        self.assertIn("INV-VERIFY-001", gate["missing_invariants"])

    def test_contract_omission_of_policy_required_invariant_fails_closed(self):
        contract = self._contract()
        contract["semantic_invariants"] = contract["semantic_invariants"][:1]
        completeness = validate_invariant_completeness(self._policy(), contract)
        self.assertFalse(completeness["complete"])
        self.assertEqual(["INV-VERIFY-001"], completeness["missing_invariant_ids"])
        decision = authorize_semantic_routing(contract, {"semantic_claims": [
            {"subject": "model", "action": "self_authorize_consequential_action", "polarity": "FORBID"}
        ]}, self._policy())
        self.assertFalse(decision["authorized"])
        self.assertEqual("required semantic invariants omitted", decision["reason"])

    def test_model_visible_contract_cannot_define_its_own_required_catalog(self):
        contract = self._contract()
        contract["semantic_invariants"] = contract["semantic_invariants"][:1]
        contract["required_invariant_ids"] = ["INV-AUTH-001"]
        result = validate_invariant_completeness(self._policy(), contract)
        self.assertFalse(result["complete"])

    def test_missing_external_task_policy_fails_closed(self):
        decision = authorize_semantic_routing(self._contract(), self._preserving_candidate())
        self.assertFalse(decision["authorized"])
        self.assertEqual("external invariant completeness policy required", decision["reason"])

    def test_ambiguous_invariant_cannot_be_green(self):
        contract = self._contract(); contract["semantic_invariants"][0]["ambiguous"] = True
        with self.assertRaises(ValueError): extract_structured_invariants(contract)

    def test_normative_strength_and_polarity_must_agree(self):
        contract = self._contract(); contract["semantic_invariants"][0]["predicate"]["polarity"] = "REQUIRE"
        with self.assertRaises(ValueError): extract_structured_invariants(contract)

    def test_duplicate_invariant_identity_fails_closed(self):
        contract = self._contract(); contract["semantic_invariants"].append(dict(contract["semantic_invariants"][0]))
        with self.assertRaises(ValueError): extract_structured_invariants(contract)

    def test_invariant_hash_changes_when_semantics_change(self):
        first = extract_structured_invariants(self._contract())["invariant_hash"]
        contract = self._contract(); contract["semantic_invariants"][1]["predicate"]["action"] = "require_security_review"
        self.assertNotEqual(first, extract_structured_invariants(contract)["invariant_hash"])

    def test_exact_semantic_preservation_is_authorized(self):
        decision = authorize_semantic_routing(self._contract(), self._preserving_candidate(), self._policy())
        self.assertTrue(decision["authorized"])
        self.assertEqual(["INV-AUTH-001", "INV-VERIFY-001"], decision["gate"]["invariant_ids"])


if __name__ == "__main__":
    unittest.main()
