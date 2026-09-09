from __future__ import annotations

from copy import deepcopy
import tempfile
from pathlib import Path
import unittest

from integrated_governed_mvp_credential_lease import canonical_hash as s9_hash

try:
    from integrated_governed_mvp_external_side_effect import (
        ExternalSideEffectGateway,
        ReferenceExternalProvider,
        SimulatedCrash,
        canonical_hash,
        derive_external_idempotency_key,
    )
    MECHANISM_AVAILABLE = True
except ModuleNotFoundError:
    MECHANISM_AVAILABLE = False


class Slice10ExternalSideEffectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.provider_db = root / "provider.sqlite3"
        self.gateway_db = root / "gateway.sqlite3"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _require_mechanism(self):
        if not MECHANISM_AVAILABLE:
            self.fail("MECHANISM_NOT_IMPLEMENTED")

    def _binding_material(self, **overrides):
        body = {
            "terminal_execution_id": "term-exec-1",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
            "slice7_completion_hash": "slice7-completion-hash",
        }
        body.update({k: v for k, v in overrides.items() if k in body})
        return body

    def _upstream(self, **overrides):
        binding = self._binding_material(**overrides)
        binding_hash = s9_hash(binding)
        remote_key = s9_hash({
            "domain": "integrated-governed-mvp-slice8-remote-idempotency",
            "terminal_execution_id": binding["terminal_execution_id"],
            "binding_hash": binding_hash,
        })
        bound = {**binding, "remote_idempotency_key": remote_key}
        remote_result = {
            "status": "REMOTE_REFERENCE_APPLIED",
            "project_id": binding["project_id"],
            "task_id": binding["task_id"],
            "effect_id": binding["effect_id"],
            "action": binding["action"],
            "artifact_sha": binding["artifact_sha"],
            "state_version": binding["state_version"],
            "production_remote_side_effect_claimed": False,
        }
        evidence_body = {
            **binding,
            "binding_hash": binding_hash,
            "remote_idempotency_key": remote_key,
            "remote_receipt_hash": "reference-receipt-hash",
            "remote_result_digest": s9_hash(remote_result),
            "remote_result": remote_result,
            "production_remote_side_effect_claimed": False,
        }
        evidence = {**evidence_body, "remote_completion_hash": s9_hash(evidence_body)}
        result_body = {
            "state": overrides.get("state", "REMOTE_EXECUTION_COMPLETED"),
            "reason": "accepted Slice8 reference completion",
            "successful_remote_completion": overrides.get("successful_remote_completion", True),
            "production_remote_side_effect_claimed": False,
            "bound_remote_execution": bound,
            "remote_completion_evidence": evidence,
        }
        return {**result_body, "result_hash": s9_hash(result_body)}

    def _profile(self, **overrides):
        body = {
            "provider_id": "provider-a",
            "credential_profile_id": "profile-a",
            "profile_status": "ACTIVE",
            "allowed_actions": ["RELEASE"],
            "allowed_project_ids": ["project-1"],
            "allowed_resource_classes": ["repository"],
            "profile_epoch": 3,
            "not_before_epoch": 90,
            "expires_at_epoch": 200,
        }
        body.update(overrides)
        return {**deepcopy(body), "profile_snapshot_hash": s9_hash(body)}

    def _lease(self, *, upstream=None, profile=None, **overrides):
        upstream = upstream or self._upstream()
        profile = profile or self._profile()
        bound_remote = upstream["bound_remote_execution"]
        terminal_binding_hash = upstream["remote_completion_evidence"]["binding_hash"]
        base = {
            "lease_request_id": "lease-request-1",
            "project_id": bound_remote["project_id"],
            "task_id": bound_remote["task_id"],
            "effect_id": bound_remote["effect_id"],
            "action": bound_remote["action"],
            "artifact_sha": bound_remote["artifact_sha"],
            "state_version": bound_remote["state_version"],
            "terminal_execution_id": bound_remote["terminal_execution_id"],
            "terminal_binding_hash": terminal_binding_hash,
            "authority_snapshot_hash": "authority-snapshot-hash",
            "provider_id": profile["provider_id"],
            "credential_profile_id": profile["credential_profile_id"],
            "resource_class": "repository",
            "credential_lease_id": "cred-lease-reference-1",
            "profile_epoch": profile["profile_epoch"],
            "profile_snapshot_hash": profile["profile_snapshot_hash"],
            "lease_not_before_epoch": 100.0,
            "lease_expires_at_epoch": 130.0,
            "opaque_secret_handle": "opaque-reference-handle",
        }
        base.update(overrides)
        binding_material = {k: deepcopy(v) for k, v in base.items() if k not in {"opaque_secret_handle", "lease_binding_hash"}}
        base["lease_binding_hash"] = s9_hash(binding_material)
        evidence_body = deepcopy(base)
        evidence_body["production_side_effect_claimed"] = False
        evidence = {**evidence_body, "lease_evidence_hash": s9_hash(evidence_body)}
        return {
            "state": overrides.get("result_state", "LEASE_ISSUED"),
            "reason": "accepted Slice9 reference lease",
            "successful_lease": overrides.get("successful_lease", True),
            "production_side_effect_claimed": False,
            "bound_lease": base,
            "lease_evidence": evidence,
        }

    def _authority(self, **overrides):
        body = {
            "authority_status": "ACTIVE",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
            "not_before_epoch": 90,
            "expires_at_epoch": 200,
        }
        body.update(overrides)
        return {**body, "authority_snapshot_hash": canonical_hash(body) if MECHANISM_AVAILABLE else "pending"}

    def _request(self, *, upstream=None, lease=None, provider_id="provider-a", endpoint_id="endpoint-a", **overrides):
        self._require_mechanism()
        upstream = upstream or self._upstream()
        lease = lease or self._lease(upstream=upstream)
        bound_remote = upstream["bound_remote_execution"]
        bound_lease = lease["bound_lease"]
        body = {
            "side_effect_request_id": "side-effect-request-1",
            "project_id": bound_remote["project_id"],
            "task_id": bound_remote["task_id"],
            "effect_id": bound_remote["effect_id"],
            "terminal_execution_id": bound_remote["terminal_execution_id"],
            "remote_idempotency_key": bound_remote["remote_idempotency_key"],
            "credential_lease_id": bound_lease["credential_lease_id"],
            "credential_profile_id": bound_lease["credential_profile_id"],
            "provider_id": provider_id,
            "endpoint_id": endpoint_id,
            "action": bound_remote["action"],
            "resource_id": "repository:abc123",
            "artifact_sha": bound_remote["artifact_sha"],
            "state_version": bound_remote["state_version"],
            "payload_digest": canonical_hash({"artifact_sha": bound_remote["artifact_sha"], "action": bound_remote["action"]}),
            "authority_snapshot_hash": self._authority()["authority_snapshot_hash"],
            "lease_evidence_hash": lease["lease_evidence"]["lease_evidence_hash"],
        }
        body.update(overrides)
        body["external_idempotency_key"] = derive_external_idempotency_key(body)
        return body

    def _new(self, *, provider_id="provider-a", endpoint_id="endpoint-a"):
        self._require_mechanism()
        provider = ReferenceExternalProvider(self.provider_db, allowed_targets={(provider_id, endpoint_id)})
        gateway = ExternalSideEffectGateway(self.gateway_db, provider)
        return gateway, provider

    def _execute(self, *, upstream=None, lease=None, profile=None, authority=None, request=None, now_epoch=101, provider_id="provider-a", endpoint_id="endpoint-a", crash_point=None):
        self._require_mechanism()
        upstream = upstream or self._upstream()
        profile = profile or self._profile(provider_id=provider_id)
        lease = lease or self._lease(upstream=upstream, profile=profile)
        authority = authority or self._authority()
        request = request or self._request(upstream=upstream, lease=lease, provider_id=provider_id, endpoint_id=endpoint_id)
        gateway, provider = self._new(provider_id=provider_id, endpoint_id=endpoint_id)
        result = gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=profile,
            current_authority=authority,
            side_effect_request=request,
            now_epoch=now_epoch,
            crash_point=crash_point,
        )
        return gateway, provider, result, upstream, lease, profile, authority, request

    def test_s10_01_exact_lineage_applies_one_bounded_reference_effect(self):
        gateway, provider, result, *_ = self._execute()
        self.assertEqual("REFERENCE_EFFECT_APPLIED", result["state"])
        self.assertEqual(1, provider.effect_count())
        self.assertFalse(result["production_side_effect_claimed"])

    def test_s10_02_exact_replay_reuses_same_external_effect(self):
        gateway, provider = self._new()
        upstream, profile = self._upstream(), self._profile()
        lease = self._lease(upstream=upstream, profile=profile)
        authority = self._authority()
        request = self._request(upstream=upstream, lease=lease)
        first = gateway.execute(upstream_result=upstream, lease_result=lease, current_profile=profile, current_authority=authority, side_effect_request=request, now_epoch=101)
        second = gateway.execute(upstream_result=upstream, lease_result=lease, current_profile=profile, current_authority=authority, side_effect_request=request, now_epoch=102)
        self.assertEqual("REFERENCE_EFFECT_REPLAYED", second["state"])
        self.assertEqual(first["external_effect_evidence"]["external_effect_id"], second["external_effect_evidence"]["external_effect_id"])
        self.assertEqual(1, provider.effect_count())

    def test_s10_03_invalid_slice8_lineage_denies_before_provider_access(self):
        upstream = self._upstream(successful_remote_completion=False)
        lease = self._lease(upstream=self._upstream())
        gateway, provider = self._new()
        result = gateway.execute(upstream_result=upstream, lease_result=lease, current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(lease=lease), now_epoch=101)
        self.assertEqual("DENY_UPSTREAM_LINEAGE", result["state"])
        self.assertEqual(0, provider.dispatch_count())

    def test_s10_04_invalid_slice9_lease_denies_before_provider_access(self):
        lease = self._lease(successful_lease=False, result_state="LEASE_CONSUMPTION_DENIED")
        gateway, provider = self._new()
        result = gateway.execute(upstream_result=self._upstream(), lease_result=lease, current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(lease=self._lease()), now_epoch=101)
        self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
        self.assertEqual(0, provider.dispatch_count())

    def test_s10_05_provider_substitution_denies(self):
        request = self._request(provider_id="provider-b")
        gateway, provider = self._new()
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        self.assertEqual("DENY_TARGET_SUBSTITUTION", result["state"])
        self.assertEqual(0, provider.dispatch_count())

    def test_s10_06_endpoint_substitution_denies(self):
        request = self._request(endpoint_id="endpoint-b")
        gateway, provider = self._new()
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        self.assertEqual("DENY_TARGET_SUBSTITUTION", result["state"])
        self.assertEqual(0, provider.dispatch_count())

    def test_s10_07_scope_or_payload_widening_denies(self):
        for field, value in [("action", "DEPLOY"), ("artifact_sha", "moved"), ("state_version", 8), ("resource_id", "repository:other"), ("payload_digest", "forged")]:
            with self.subTest(field=field):
                request = self._request(**{field: value})
                request["external_idempotency_key"] = derive_external_idempotency_key(request)
                gateway, provider = self._new()
                result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
                self.assertEqual("DENY_SCOPE_WIDENING", result["state"])
                self.assertEqual(0, provider.dispatch_count())

    def test_s10_08_replacement_external_idempotency_key_denies(self):
        request = self._request()
        request["external_idempotency_key"] = "caller-forged-key"
        gateway, provider = self._new()
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        self.assertEqual("DENY_IDEMPOTENCY_REBIND", result["state"])
        self.assertEqual(0, provider.dispatch_count())

    def test_s10_09_same_external_key_changed_binding_denies(self):
        gateway, provider = self._new()
        upstream, profile, lease, authority = self._upstream(), self._profile(), self._lease(), self._authority()
        request = self._request()
        gateway.execute(upstream_result=upstream, lease_result=lease, current_profile=profile, current_authority=authority, side_effect_request=request, now_epoch=101)
        changed = deepcopy(request)
        changed["resource_id"] = "repository:other"
        result = gateway.execute(upstream_result=upstream, lease_result=lease, current_profile=profile, current_authority=authority, side_effect_request=changed, now_epoch=102)
        self.assertEqual("DENY_IDEMPOTENCY_REBIND", result["state"])
        self.assertEqual(1, provider.effect_count())

    def test_s10_10_raw_secret_input_denies_before_dispatch(self):
        for field in ("api_key", "token", "password", "secret", "raw_secret"):
            with self.subTest(field=field):
                request = self._request(**{field: "SYNTHETIC-RAW-SECRET"})
                gateway, provider = self._new()
                result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
                self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
                self.assertEqual(0, provider.dispatch_count())

    def test_s10_11_expired_or_revoked_authority_denies_dispatch(self):
        for authority in (self._authority(authority_status="REVOKED"), self._authority(expires_at_epoch=101)):
            gateway, provider = self._new()
            result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=authority, side_effect_request=self._request(), now_epoch=101)
            self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
            self.assertEqual(0, provider.dispatch_count())

    def test_s10_12_stale_or_revoked_lease_profile_denies_dispatch(self):
        for profile in (self._profile(profile_status="REVOKED"), self._profile(profile_epoch=4)):
            gateway, provider = self._new()
            result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=profile, current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
            self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
            self.assertEqual(0, provider.dispatch_count())

    def test_s10_13_timeout_before_provider_commit_has_no_effect(self):
        gateway, provider = self._new()
        provider.set_mode("timeout_before_commit")
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
        self.assertEqual("REFERENCE_EFFECT_FAILED", result["state"])
        self.assertEqual(0, provider.effect_count())

    def test_s10_14_timeout_after_provider_commit_becomes_outcome_unknown(self):
        gateway, provider = self._new()
        provider.set_mode("timeout_after_commit")
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
        self.assertEqual("OUTCOME_UNKNOWN_RECONCILE_REQUIRED", result["state"])
        self.assertEqual(1, provider.effect_count())

    def test_s10_15_reconciliation_recovers_same_external_effect(self):
        gateway, provider = self._new()
        provider.set_mode("timeout_after_commit")
        request = self._request()
        unknown = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        provider.set_mode("success")
        recovered = gateway.recover(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=102)
        self.assertEqual("RECONCILED_EXISTING_EFFECT", recovered["state"])
        self.assertEqual(1, provider.effect_count())
        self.assertEqual(unknown["external_idempotency_key"], recovered["external_effect_evidence"]["external_idempotency_key"])

    def test_s10_16_crash_after_provider_commit_recovers_without_duplicate(self):
        gateway, provider = self._new()
        request = self._request()
        with self.assertRaises(SimulatedCrash):
            gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101, crash_point="after_provider_commit_before_local_completion")
        reopened = ExternalSideEffectGateway(self.gateway_db, provider)
        recovered = reopened.recover(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=102)
        self.assertEqual("RECONCILED_EXISTING_EFFECT", recovered["state"])
        self.assertEqual(1, provider.effect_count())

    def test_s10_17_repeated_recovery_never_increments_provider_effect_count(self):
        gateway, provider = self._new()
        provider.set_mode("timeout_after_commit")
        request = self._request()
        gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        provider.set_mode("success")
        for now in (102, 103, 104):
            gateway.recover(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=now)
        self.assertEqual(1, provider.effect_count())

    def test_s10_18_revocation_after_ambiguity_allows_reconcile_not_mutating_retry(self):
        gateway, provider = self._new()
        provider.set_mode("timeout_after_commit")
        request = self._request()
        gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        dispatches = provider.dispatch_count()
        recovered = gateway.recover(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(authority_status="REVOKED"), side_effect_request=request, now_epoch=102)
        self.assertEqual("RECONCILED_EXISTING_EFFECT", recovered["state"])
        self.assertEqual(dispatches, provider.dispatch_count())

    def test_s10_19_mismatched_provider_success_response_denies(self):
        gateway, provider = self._new()
        provider.set_mode("mismatched_response")
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
        self.assertEqual("DENY_RESPONSE_INTEGRITY", result["state"])

    def test_s10_20_success_label_without_provider_commit_not_positive_evidence(self):
        gateway, provider = self._new()
        provider.set_mode("success_without_commit")
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
        self.assertEqual("REFERENCE_EFFECT_FAILED", result["state"])
        self.assertIsNone(result.get("external_effect_evidence"))

    def test_s10_21_provider_5xx_before_commit_does_not_mint_completion(self):
        gateway, provider = self._new()
        provider.set_mode("http_5xx")
        result = gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=self._request(), now_epoch=101)
        self.assertEqual("REFERENCE_EFFECT_FAILED", result["state"])
        self.assertEqual(0, provider.effect_count())

    def test_s10_22_records_and_diagnostics_never_contain_raw_secret(self):
        gateway, provider = self._new()
        request = self._request()
        provider.set_failure_detail("provider error secret=SYNTHETIC-RAW-SECRET")
        gateway.execute(upstream_result=self._upstream(), lease_result=self._lease(), current_profile=self._profile(), current_authority=self._authority(), side_effect_request=request, now_epoch=101)
        serialized = str(gateway.governed_records()) + str(provider.records())
        self.assertNotIn("SYNTHETIC-RAW-SECRET", serialized)

    def test_s10_23_bound_field_mutation_changes_or_invalidates_evidence_hash(self):
        gateway, provider, result, *_ = self._execute()
        evidence = result["external_effect_evidence"]
        self.assertTrue(gateway.validate_external_effect_evidence(evidence))
        for field in ("provider_id", "endpoint_id", "action", "resource_id", "artifact_sha", "state_version", "payload_digest", "credential_lease_id", "external_idempotency_key"):
            with self.subTest(field=field):
                changed = deepcopy(evidence)
                changed[field] = "tampered" if field != "state_version" else 999
                self.assertFalse(gateway.validate_external_effect_evidence(changed))

    def test_s10_24_provider_model_reviewer_ci_success_not_terminal_authority(self):
        gateway, provider, result, *_ = self._execute()
        self.assertFalse(result["terminal_authority_granted"])
        self.assertFalse(result["production_side_effect_claimed"])

    def test_s10_25_future_provider_endpoint_is_data_driven(self):
        gateway, provider, result, *_ = self._execute(provider_id="future-provider-x", endpoint_id="future-endpoint-y")
        self.assertEqual("REFERENCE_EFFECT_APPLIED", result["state"])
        self.assertEqual("future-provider-x", result["external_effect_evidence"]["provider_id"])
        self.assertEqual("future-endpoint-y", result["external_effect_evidence"]["endpoint_id"])

    def test_s10_26_no_result_claims_real_production_side_effect(self):
        gateway, provider, result, *_ = self._execute()
        self.assertFalse(result["production_side_effect_claimed"])
        self.assertFalse(result["external_effect_evidence"]["production_side_effect_claimed"])


if __name__ == "__main__":
    unittest.main()
