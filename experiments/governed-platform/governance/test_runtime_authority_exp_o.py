import copy
import unittest

from runtime_authority_exp_o import (
    ChangeClaimRegistry,
    append_evidence_record,
    checkpoint_due,
    create_checkpoint_and_anchor,
    evaluate_action_effect,
    evaluate_authority_freshness,
    reissue_for_replacement_worker,
    validate_sender_constrained_capability,
    verify_anchored_checkpoint,
)


def capability(**overrides):
    value = {
        "capability_id": "cap-o1",
        "capability_nonce": "nonce-o1",
        "subject_id": "worker-a",
        "subject_key_thumbprint": "key-a",
        "authority_epoch": 7,
        "resource_fence": 11,
        "freshness_class": "READ_ONLY",
        "revoked": False,
    }
    value.update(overrides)
    return value


def snapshot(**overrides):
    value = {
        "authority_epoch": 7,
        "minimum_resource_fence": 11,
        "age_ms": 0,
    }
    value.update(overrides)
    return value


def effect_contract(**overrides):
    value = {
        "effect_contract_id": "effect-o2",
        "base_sha": "base-123",
        "allowed_action_classes": ["WRITE_WORKSPACE"],
        "allowed_resources": ["repo:owner/repo:path:src/auth/**"],
        "forbidden_resources": ["repo:owner/repo:path:infra/prod/**"],
        "destructive_effect_allowed": False,
        "max_changed_files": 3,
        "semantic_correspondence_required": False,
    }
    value.update(overrides)
    return value


def action_effect(**overrides):
    value = {
        "effect_contract_id": "effect-o2",
        "base_sha": "base-123",
        "action_class": "WRITE_WORKSPACE",
        "target_resources": ["repo:owner/repo:path:src/auth/session.go"],
        "changed_files": ["repo:owner/repo:path:src/auth/session.go"],
        "destructive_effect": False,
        "provenance_trust_classes": ["APPROVED_PROJECT_STATE"],
    }
    value.update(overrides)
    return value


class PilotO1FreshnessAndFencingTests(unittest.TestCase):
    def test_read_at_exact_cache_threshold_is_allowed(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="READ_ONLY"),
            snapshot(age_ms=60_000),
            origin_available=False,
        )
        self.assertTrue(decision["authorized"])
        self.assertFalse(decision["external_authoritative_effect"])

    def test_read_one_ms_past_threshold_fails_closed_when_partitioned(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="READ_ONLY"),
            snapshot(age_ms=60_001),
            origin_available=False,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "STALE_AUTHORITY_FAIL_CLOSED")

    def test_stale_read_with_origin_reachable_requires_refresh_not_allow(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="READ_ONLY"),
            snapshot(age_ms=60_001),
            origin_available=True,
        )
        self.assertFalse(decision["authorized"])
        self.assertTrue(decision["requires_refresh"])
        self.assertEqual(decision["reason"], "AUTHORITY_REFRESH_REQUIRED")

    def test_workspace_at_exact_threshold_is_allowed_only_non_authoritatively(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="WORKSPACE_MUTATION"),
            snapshot(age_ms=15_000),
            origin_available=False,
        )
        self.assertTrue(decision["authorized"])
        self.assertFalse(decision["external_authoritative_effect"])

    def test_workspace_one_ms_past_threshold_fails_closed(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="WORKSPACE_MUTATION"),
            snapshot(age_ms=15_001),
            origin_available=False,
        )
        self.assertFalse(decision["authorized"])

    def test_epoch_mismatch_is_never_accepted_from_cache(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="WORKSPACE_MUTATION"),
            snapshot(authority_epoch=8, age_ms=1),
            origin_available=False,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "AUTHORITY_EPOCH_MISMATCH")

    def test_stale_resource_fence_is_denied(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="WORKSPACE_MUTATION", resource_fence=10),
            snapshot(minimum_resource_fence=11, age_ms=1),
            origin_available=True,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "STALE_RESOURCE_FENCE")

    def test_external_mutation_requires_online_authority(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="EXTERNAL_MUTATION"),
            snapshot(age_ms=0),
            origin_available=True,
            online_authority_confirmed=False,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "ONLINE_AUTHORITY_REQUIRED")

    def test_external_mutation_with_current_online_authority_can_pass(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="EXTERNAL_MUTATION"),
            snapshot(age_ms=25),
            origin_available=True,
            online_authority_confirmed=True,
        )
        self.assertTrue(decision["authorized"])
        self.assertTrue(decision["external_authoritative_effect"])

    def test_release_requires_resource_fence_even_with_online_confirmation(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="RELEASE_OR_PRODUCTION", resource_fence=None),
            snapshot(minimum_resource_fence=None),
            origin_available=True,
            online_authority_confirmed=True,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "RESOURCE_FENCE_REQUIRED")

    def test_release_with_online_authority_and_current_fence_can_pass(self):
        decision = evaluate_authority_freshness(
            capability(freshness_class="RELEASE_OR_PRODUCTION"),
            snapshot(age_ms=100),
            origin_available=True,
            online_authority_confirmed=True,
        )
        self.assertTrue(decision["authorized"])


class PilotO2IntentBindingTests(unittest.TestCase):
    def test_clean_trusted_effect_within_contract_can_pass(self):
        decision = evaluate_action_effect(effect_contract(), action_effect())
        self.assertTrue(decision["authorized"])

    def test_injected_forbidden_resource_is_denied(self):
        decision = evaluate_action_effect(
            effect_contract(),
            action_effect(
                target_resources=["repo:owner/repo:path:infra/prod/cleanup.sh"],
                changed_files=["repo:owner/repo:path:infra/prod/cleanup.sh"],
                provenance_trust_classes=["UNTRUSTED_USER_GENERATED_CONTENT"],
            ),
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "FORBIDDEN_RESOURCE_TOUCHED")

    def test_extra_file_outside_effect_contract_is_denied(self):
        decision = evaluate_action_effect(
            effect_contract(),
            action_effect(
                changed_files=[
                    "repo:owner/repo:path:src/auth/session.go",
                    "repo:owner/repo:path:src/payments/settlement.go",
                ],
                provenance_trust_classes=["TOOL_OUTPUT"],
            ),
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "RESOURCE_OUT_OF_EFFECT_CONTRACT")

    def test_same_path_untrusted_semantic_change_does_not_auto_authorize(self):
        decision = evaluate_action_effect(
            effect_contract(semantic_correspondence_required=True),
            action_effect(provenance_trust_classes=["UNTRUSTED_USER_GENERATED_CONTENT"]),
            semantic_verified=False,
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(
            decision["decision"], "INDEPENDENT_SEMANTIC_VERIFICATION_REQUIRED"
        )

    def test_same_path_semantic_effect_may_pass_only_after_separate_verification(self):
        decision = evaluate_action_effect(
            effect_contract(semantic_correspondence_required=True),
            action_effect(provenance_trust_classes=["UNTRUSTED_USER_GENERATED_CONTENT"]),
            semantic_verified=True,
        )
        self.assertTrue(decision["authorized"])
        self.assertTrue(decision["semantic_verified"])

    def test_changed_file_bound_is_enforced(self):
        files = [
            "repo:owner/repo:path:src/auth/a.go",
            "repo:owner/repo:path:src/auth/b.go",
            "repo:owner/repo:path:src/auth/c.go",
            "repo:owner/repo:path:src/auth/d.go",
        ]
        decision = evaluate_action_effect(
            effect_contract(max_changed_files=3), action_effect(changed_files=files)
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "CHANGED_FILE_BOUND_EXCEEDED")


class PilotO3PreventiveClaimTests(unittest.TestCase):
    def test_non_overlapping_exclusive_claims_are_both_granted(self):
        registry = ChangeClaimRegistry()
        a = registry.request_claim(
            task_id="A", base_sha="h1", resources=["repo:path:src/auth/**"], mode="EXCLUSIVE"
        )
        b = registry.request_claim(
            task_id="B", base_sha="h1", resources=["repo:path:src/payments/**"], mode="EXCLUSIVE"
        )
        self.assertEqual(a["disposition"], "EXCLUSIVE_GRANTED")
        self.assertEqual(b["disposition"], "EXCLUSIVE_GRANTED")

    def test_overlapping_exclusive_claim_is_prevented_before_execution(self):
        registry = ChangeClaimRegistry()
        registry.request_claim(
            task_id="A", base_sha="h1", resources=["repo:path:src/auth/**"], mode="EXCLUSIVE"
        )
        b = registry.request_claim(
            task_id="B",
            base_sha="h1",
            resources=["repo:path:src/auth/session.go"],
            mode="EXCLUSIVE",
        )
        self.assertEqual(b["disposition"], "WAITING_CONFLICT")
        self.assertIn("A", b["conflicts_with"])

    def test_parallel_proposals_may_run_but_require_combined_verification(self):
        registry = ChangeClaimRegistry()
        a = registry.request_claim(
            task_id="A", base_sha="h1", resources=["repo:path:src/auth/**"], mode="PARALLEL_PROPOSAL"
        )
        b = registry.request_claim(
            task_id="B",
            base_sha="h1",
            resources=["repo:path:src/auth/session.go"],
            mode="PARALLEL_PROPOSAL",
        )
        self.assertEqual(a["disposition"], "PARALLEL_PROPOSAL_GRANTED")
        self.assertEqual(b["disposition"], "PARALLEL_PROPOSAL_GRANTED")
        decision = registry.revalidate_for_integration("B", "h1")
        self.assertEqual(decision["decision"], "COMBINED_VERIFICATION_REQUIRED")

    def test_stale_base_forces_revalidation(self):
        registry = ChangeClaimRegistry()
        registry.request_claim(
            task_id="A", base_sha="h1", resources=["repo:path:src/auth/**"], mode="EXCLUSIVE"
        )
        decision = registry.revalidate_for_integration("A", "h2")
        self.assertEqual(decision["decision"], "REVALIDATION_REQUIRED")

    def test_current_exclusive_claim_still_does_not_imply_release(self):
        registry = ChangeClaimRegistry()
        registry.request_claim(
            task_id="A", base_sha="h1", resources=["repo:path:src/auth/**"], mode="EXCLUSIVE"
        )
        decision = registry.revalidate_for_integration("A", "h1")
        self.assertEqual(decision["decision"], "CURRENT_HEAD_VERIFICATION_REQUIRED")


class PilotO4WorkerRebindingTests(unittest.TestCase):
    def test_original_sender_binding_is_valid_before_revocation(self):
        decision = validate_sender_constrained_capability(
            capability(), worker_id="worker-a", worker_key_thumbprint="key-a"
        )
        self.assertTrue(decision["authorized"])

    def test_old_capability_cannot_be_replayed_by_replacement_worker(self):
        decision = validate_sender_constrained_capability(
            capability(), worker_id="worker-b", worker_key_thumbprint="key-b"
        )
        self.assertFalse(decision["authorized"])
        self.assertEqual(decision["reason"], "WORKER_IDENTITY_MISMATCH")

    def test_reissue_requires_durable_spool_reconciliation(self):
        result = reissue_for_replacement_worker(
            capability(),
            new_worker_id="worker-b",
            new_worker_key_thumbprint="key-b",
            new_capability_id="cap-o2",
            new_nonce="nonce-o2",
            spool_reconciled=False,
        )
        self.assertFalse(result["reissued"])
        self.assertEqual(result["reason"], "DURABLE_SPOOL_RECONCILIATION_REQUIRED")

    def test_replacement_gets_new_capability_and_old_one_is_revoked(self):
        result = reissue_for_replacement_worker(
            capability(),
            new_worker_id="worker-b",
            new_worker_key_thumbprint="key-b",
            new_capability_id="cap-o2",
            new_nonce="nonce-o2",
            spool_reconciled=True,
        )
        self.assertTrue(result["reissued"])
        self.assertTrue(result["old_capability"]["revoked"])
        self.assertEqual(result["new_capability"]["authority_epoch"], 8)
        self.assertNotEqual(
            result["new_capability"]["capability_id"],
            result["old_capability"]["capability_id"],
        )
        valid_new = validate_sender_constrained_capability(
            result["new_capability"], worker_id="worker-b", worker_key_thumbprint="key-b"
        )
        self.assertTrue(valid_new["authorized"])
        invalid_old = validate_sender_constrained_capability(
            result["old_capability"], worker_id="worker-a", worker_key_thumbprint="key-a"
        )
        self.assertFalse(invalid_old["authorized"])
        self.assertEqual(invalid_old["reason"], "CAPABILITY_REVOKED")

    def test_reissue_cannot_reuse_capability_id_or_nonce(self):
        same_id = reissue_for_replacement_worker(
            capability(),
            new_worker_id="worker-b",
            new_worker_key_thumbprint="key-b",
            new_capability_id="cap-o1",
            new_nonce="nonce-o2",
            spool_reconciled=True,
        )
        self.assertFalse(same_id["reissued"])
        same_nonce = reissue_for_replacement_worker(
            capability(),
            new_worker_id="worker-b",
            new_worker_key_thumbprint="key-b",
            new_capability_id="cap-o2",
            new_nonce="nonce-o1",
            spool_reconciled=True,
        )
        self.assertFalse(same_nonce["reissued"])


class PilotO5EvidenceAnchoringTests(unittest.TestCase):
    def _records(self):
        records = []
        append_evidence_record(records, {"kind": "patch", "digest": "a"})
        append_evidence_record(records, {"kind": "test", "result": "pass"})
        append_evidence_record(records, {"kind": "review", "result": "pass"})
        return records

    def test_intact_partition_with_independent_anchor_verifies(self):
        records = self._records()
        checkpoint, anchor = create_checkpoint_and_anchor(
            records,
            partition_id="project:p1/task:t1",
            anchor_trust_domain="independent-anchor-root",
        )
        result = verify_anchored_checkpoint(
            records, checkpoint, anchor, primary_trust_domain="primary-platform-root"
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["state"], "FULLY_ANCHORED")
        self.assertTrue(result["release_integrity_current"])

    def test_tamper_inside_anchored_range_is_detected(self):
        records = self._records()
        checkpoint, anchor = create_checkpoint_and_anchor(
            records,
            partition_id="project:p1/task:t1",
            anchor_trust_domain="independent-anchor-root",
        )
        tampered = copy.deepcopy(records)
        tampered[1]["payload"]["result"] = "different"
        result = verify_anchored_checkpoint(
            tampered, checkpoint, anchor, primary_trust_domain="primary-platform-root"
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["state"], "COVERED_RECORD_CHAIN_TAMPER_DETECTED")

    def test_anchor_root_mismatch_is_detected(self):
        records = self._records()
        checkpoint, anchor = create_checkpoint_and_anchor(
            records,
            partition_id="project:p1/task:t1",
            anchor_trust_domain="independent-anchor-root",
        )
        anchor["merkle_root"] = "0" * 64
        result = verify_anchored_checkpoint(
            records, checkpoint, anchor, primary_trust_domain="primary-platform-root"
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["state"], "ANCHOR_ROOT_MISMATCH")

    def test_same_admin_trust_domain_is_not_independent_anchor(self):
        records = self._records()
        checkpoint, anchor = create_checkpoint_and_anchor(
            records,
            partition_id="project:p1/task:t1",
            anchor_trust_domain="primary-platform-root",
        )
        result = verify_anchored_checkpoint(
            records, checkpoint, anchor, primary_trust_domain="primary-platform-root"
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["state"], "ANCHOR_NOT_INDEPENDENT")

    def test_uncheckpointed_tail_is_explicitly_degraded(self):
        records = self._records()
        checkpoint, anchor = create_checkpoint_and_anchor(
            records,
            partition_id="project:p1/task:t1",
            covered_count=2,
            anchor_trust_domain="independent-anchor-root",
        )
        result = verify_anchored_checkpoint(
            records, checkpoint, anchor, primary_trust_domain="primary-platform-root"
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["state"], "ANCHORED_WITH_UNCHECKPOINTED_TAIL")
        self.assertEqual(result["uncheckpointed_records"], 1)
        self.assertFalse(result["release_integrity_current"])

    def test_checkpoint_thresholds_use_earlier_record_or_time_limit(self):
        self.assertTrue(
            checkpoint_due(records_since_checkpoint=99, age_ms=10_000, high_risk=True)
        )
        self.assertTrue(
            checkpoint_due(records_since_checkpoint=100, age_ms=1, high_risk=True)
        )
        self.assertFalse(
            checkpoint_due(records_since_checkpoint=99, age_ms=9_999, high_risk=True)
        )
        self.assertTrue(
            checkpoint_due(records_since_checkpoint=999, age_ms=60_000, high_risk=False)
        )
        self.assertTrue(
            checkpoint_due(records_since_checkpoint=1_000, age_ms=1, high_risk=False)
        )
        self.assertFalse(
            checkpoint_due(records_since_checkpoint=999, age_ms=59_999, high_risk=False)
        )


if __name__ == "__main__":
    unittest.main()
