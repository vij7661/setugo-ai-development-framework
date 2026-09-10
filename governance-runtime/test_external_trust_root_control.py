#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from verify_external_trust_root_control import (
    REQUIRED_STATUS_CONTEXT,
    RULESET_ID,
    TARGET_REF,
    validate_ruleset_document,
)


def valid_ruleset():
    return {
        "id": RULESET_ID,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"exclude": [], "include": [TARGET_REF]}},
        "bypass_actors": [],
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 0,
                    "require_code_owner_review": True,
                    "required_review_thread_resolution": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {"context": REQUIRED_STATUS_CONTEXT, "integration_id": 15368}
                    ],
                },
            },
        ],
    }


class ExternalTrustRootControlTests(unittest.TestCase):
    def assert_rejected(self, mutate, expected_fragment, *, require_admin_bypass_visibility=True):
        payload = valid_ruleset()
        mutate(payload)
        ok, reason = validate_ruleset_document(
            payload,
            require_admin_bypass_visibility=require_admin_bypass_visibility,
        )
        self.assertFalse(ok)
        self.assertIn(expected_fragment, reason)

    def test_valid_single_owner_ruleset_contract_is_supported(self):
        ok, reason = validate_ruleset_document(valid_ruleset())
        self.assertTrue(ok, reason)

    def test_strict_admin_evidence_missing_bypass_state_fails_closed(self):
        payload = valid_ruleset()
        del payload["bypass_actors"]
        ok, reason = validate_ruleset_document(payload)
        self.assertFalse(ok)
        self.assertIn("bypass state is missing", reason)

    def test_runner_visible_mode_does_not_claim_unobservable_bypass_state(self):
        payload = valid_ruleset()
        del payload["bypass_actors"]
        ok, reason = validate_ruleset_document(payload, require_admin_bypass_visibility=False)
        self.assertTrue(ok, reason)
        self.assertIn("runner-visible", reason)

    def test_runner_visible_mode_still_rejects_visible_nonempty_bypass_state(self):
        payload = valid_ruleset()
        payload["bypass_actors"] = [{"actor_type": "Integration", "actor_id": 1}]
        ok, reason = validate_ruleset_document(payload, require_admin_bypass_visibility=False)
        self.assertFalse(ok)
        self.assertIn("bypass actors", reason)

    def test_inactive_ruleset_fails_closed(self):
        self.assert_rejected(lambda p: p.__setitem__("enforcement", "disabled"), "not active")

    def test_wrong_target_ref_fails_closed(self):
        def mutate(p):
            p["conditions"]["ref_name"]["include"] = ["refs/heads/main"]
        self.assert_rejected(mutate, "phase/testing")

    def test_bypass_actor_fails_closed(self):
        self.assert_rejected(
            lambda p: p["bypass_actors"].append({"actor_type": "Integration", "actor_id": 1}),
            "bypass actors",
        )

    def test_missing_pull_request_rule_fails_closed(self):
        self.assert_rejected(
            lambda p: p.__setitem__("rules", [r for r in p["rules"] if r["type"] != "pull_request"]),
            "pull-request protection",
        )

    def test_nonzero_required_approval_count_is_rejected_in_single_owner_profile(self):
        def mutate(p):
            next(r for r in p["rules"] if r["type"] == "pull_request")["parameters"]["required_approving_review_count"] = 1
        self.assert_rejected(mutate, "single-owner")

    def test_missing_review_thread_resolution_fails_closed(self):
        def mutate(p):
            next(r for r in p["rules"] if r["type"] == "pull_request")["parameters"]["required_review_thread_resolution"] = False
        self.assert_rejected(mutate, "review-thread resolution")

    def test_missing_force_push_protection_fails_closed(self):
        self.assert_rejected(
            lambda p: p.__setitem__("rules", [r for r in p["rules"] if r["type"] != "non_fast_forward"]),
            "force-push protection",
        )

    def test_missing_deletion_protection_fails_closed(self):
        self.assert_rejected(
            lambda p: p.__setitem__("rules", [r for r in p["rules"] if r["type"] != "deletion"]),
            "deletion protection",
        )

    def test_non_strict_required_status_checks_fail_closed(self):
        def mutate(p):
            next(r for r in p["rules"] if r["type"] == "required_status_checks")["parameters"]["strict_required_status_checks_policy"] = False
        self.assert_rejected(mutate, "strict required-status-check")

    def test_missing_qualification_status_context_fails_closed(self):
        def mutate(p):
            next(r for r in p["rules"] if r["type"] == "required_status_checks")["parameters"]["required_status_checks"] = [{"context": "other-check"}]
        self.assert_rejected(mutate, "required status context")

    def test_simultaneous_candidate_pem_and_pin_change_cannot_satisfy_external_contract_by_itself(self):
        payload = copy.deepcopy(valid_ruleset())
        attacker_local_change = {
            "repo_pem_replaced": True,
            "in_repo_pin_replaced": True,
            "self_signed_attestation_created": True,
        }
        self.assertTrue(all(attacker_local_change.values()))
        ok, reason = validate_ruleset_document(payload)
        self.assertTrue(ok, reason)
        self.assertEqual(payload["bypass_actors"], [])


if __name__ == "__main__":
    unittest.main()
