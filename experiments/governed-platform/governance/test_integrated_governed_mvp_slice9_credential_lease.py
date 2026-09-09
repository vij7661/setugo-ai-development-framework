from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from integrated_governed_mvp_credential_lease import (
    CredentialLeaseGate,
    ReferenceCredentialBroker,
    canonical_hash,
    derive_credential_lease_id,
)

SYNTHETIC_SECRET = "SYNTHETIC-SLICE9-SECRET-NEVER-PERSIST"


class Slice9CredentialLeaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.broker_db = root / "broker.sqlite3"
        self.lease_db = root / "leases.sqlite3"

    def tearDown(self) -> None:
        self.tmp.cleanup()

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

    def _terminal_binding_hash(self, **overrides):
        return canonical_hash(self._binding_material(**overrides))

    def _remote_key(self, terminal_execution_id: str, binding_hash: str) -> str:
        return canonical_hash({
            "domain": "integrated-governed-mvp-slice8-remote-idempotency",
            "terminal_execution_id": terminal_execution_id,
            "binding_hash": binding_hash,
        })

    def _upstream(self, **overrides):
        binding = self._binding_material(**overrides)
        binding_hash = canonical_hash(binding)
        key = self._remote_key(binding["terminal_execution_id"], binding_hash)
        bound = {**binding, "remote_idempotency_key": key}
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
            "remote_idempotency_key": key,
            "remote_receipt_hash": "reference-receipt-hash",
            "remote_result_digest": canonical_hash(remote_result),
            "remote_result": remote_result,
            "production_remote_side_effect_claimed": False,
        }
        evidence = {**evidence_body, "remote_completion_hash": canonical_hash(evidence_body)}
        body = {
            "state": overrides.get("state", "REMOTE_EXECUTION_COMPLETED"),
            "reason": "reference Slice8 completion",
            "successful_remote_completion": overrides.get("successful_remote_completion", True),
            "production_remote_side_effect_claimed": False,
            "bound_remote_execution": bound,
            "remote_completion_evidence": evidence,
        }
        return {**body, "result_hash": canonical_hash(body)}

    def _profile(self, **overrides):
        profile = {
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
        profile.update(overrides)
        return {**deepcopy(profile), "profile_snapshot_hash": canonical_hash(profile)}

    def _request(self, **overrides):
        lineage_overrides = {k: v for k, v in overrides.items() if k in self._binding_material()}
        request = {
            "lease_request_id": "lease-request-1",
            "project_id": lineage_overrides.get("project_id", "project-1"),
            "task_id": lineage_overrides.get("task_id", "task-1"),
            "effect_id": lineage_overrides.get("effect_id", "effect-1"),
            "action": lineage_overrides.get("action", "RELEASE"),
            "artifact_sha": lineage_overrides.get("artifact_sha", "abc123"),
            "state_version": lineage_overrides.get("state_version", 7),
            "terminal_execution_id": lineage_overrides.get("terminal_execution_id", "term-exec-1"),
            "terminal_binding_hash": self._terminal_binding_hash(**lineage_overrides),
            "authority_snapshot_hash": "authority-snapshot-hash",
            "provider_id": "provider-a",
            "credential_profile_id": "profile-a",
            "resource_class": "repository",
        }
        request.update(overrides)
        return request

    def _new_gate(self, *, provider="provider-a", profile="profile-a", secret=SYNTHETIC_SECRET):
        broker = ReferenceCredentialBroker(self.broker_db, secrets={(provider, profile): secret})
        return CredentialLeaseGate(self.lease_db, broker), broker

    def _issue(self, *, upstream=None, request=None, profile=None, now_epoch=100):
        gate, broker = self._new_gate()
        result = gate.issue(
            upstream_result=upstream or self._upstream(),
            lease_request=request or self._request(),
            current_profile=profile or self._profile(),
            now_epoch=now_epoch,
        )
        return gate, broker, result

    def test_s9_01_exact_valid_binding_issues_one_bounded_lease(self):
        gate, broker, result = self._issue()
        self.assertEqual("LEASE_ISSUED", result["state"])
        self.assertTrue(result["successful_lease"])
        self.assertEqual(1, broker.issue_count())
        self.assertFalse(result["production_side_effect_claimed"])

    def test_s9_02_exact_replay_returns_same_lease_without_widening(self):
        gate, broker = self._new_gate()
        first = gate.issue(upstream_result=self._upstream(), lease_request=self._request(), current_profile=self._profile(), now_epoch=100)
        second = gate.issue(upstream_result=self._upstream(), lease_request=self._request(), current_profile=self._profile(), now_epoch=101)
        self.assertEqual("LEASE_REPLAYED", second["state"])
        self.assertEqual(first["bound_lease"]["credential_lease_id"], second["bound_lease"]["credential_lease_id"])
        self.assertEqual(1, broker.issue_count())

    def test_s9_03_invalid_upstream_denies_before_broker_access(self):
        gate, broker, result = self._issue(upstream=self._upstream(successful_remote_completion=False))
        self.assertEqual("DENY_UPSTREAM_BINDING", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_04_provider_substitution_denies(self):
        gate, broker, result = self._issue(request=self._request(provider_id="provider-b"))
        self.assertEqual("DENY_CREDENTIAL_PROFILE", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_05_profile_substitution_denies(self):
        gate, broker, result = self._issue(request=self._request(credential_profile_id="profile-b"))
        self.assertEqual("DENY_CREDENTIAL_PROFILE", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_06_lineage_widening_denies(self):
        for field, value in [("project_id", "project-2"), ("task_id", "task-2"), ("effect_id", "effect-2"), ("action", "DEPLOY"), ("artifact_sha", "moved"), ("state_version", 8)]:
            with self.subTest(field=field):
                gate, broker, result = self._issue(request=self._request(**{field: value}))
                self.assertEqual("DENY_SCOPE_WIDENING", result["state"])
                self.assertEqual(0, broker.issue_count())

    def test_s9_07_model_or_worker_replacement_credential_identity_denies(self):
        gate, broker, result = self._issue(request=self._request(model_credential_profile_id="evil-profile", worker_provider_id="provider-b"))
        self.assertEqual("DENY_CREDENTIAL_PROFILE", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_08_raw_secret_input_denies_before_lease(self):
        for field in ("api_key", "token", "password", "secret", "raw_secret"):
            with self.subTest(field=field):
                gate, broker, result = self._issue(request=self._request(**{field: SYNTHETIC_SECRET}))
                self.assertEqual("DENY_RAW_SECRET_INPUT", result["state"])
                self.assertEqual(0, broker.issue_count())

    def test_s9_09_not_yet_valid_profile_denies(self):
        gate, broker, result = self._issue(profile=self._profile(not_before_epoch=110), now_epoch=100)
        self.assertEqual("DENY_PROFILE_STALE_OR_REVOKED", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_10_expired_profile_denies(self):
        gate, broker, result = self._issue(profile=self._profile(expires_at_epoch=100), now_epoch=100)
        self.assertEqual("DENY_PROFILE_STALE_OR_REVOKED", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_11_revoked_profile_denies_prior_lease_use(self):
        gate, broker, issued = self._issue()
        result = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(profile_status="REVOKED"), now_epoch=101)
        self.assertEqual("LEASE_REVOKED", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_12_stale_profile_epoch_or_snapshot_denies(self):
        gate, broker, issued = self._issue()
        result = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(profile_epoch=4), now_epoch=101)
        self.assertEqual("DENY_PROFILE_STALE_OR_REVOKED", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_13_expired_lease_cannot_retry_refresh(self):
        gate, broker, issued = self._issue()
        expires = issued["bound_lease"]["lease_expires_at_epoch"]
        result = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(), now_epoch=expires)
        self.assertEqual("LEASE_EXPIRED", result["state"])
        replay = gate.issue(upstream_result=self._upstream(), lease_request=self._request(), current_profile=self._profile(), now_epoch=expires)
        self.assertNotIn(replay["state"], {"LEASE_ISSUED", "LEASE_REPLAYED"})

    def test_s9_14_explicit_lease_revocation_denies_handle_use(self):
        gate, broker, issued = self._issue()
        gate.revoke(issued["bound_lease"]["credential_lease_id"])
        result = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(), now_epoch=101)
        self.assertEqual("LEASE_REVOKED", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_15_same_lease_id_changed_binding_denies(self):
        gate, broker, issued = self._issue()
        changed = deepcopy(issued)
        changed["bound_lease"]["artifact_sha"] = "moved"
        result = gate.consume(upstream_result=self._upstream(), lease_result=changed, current_profile=self._profile(), now_epoch=101)
        self.assertEqual("DENY_LEASE_REBIND", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_16_exact_allowed_action_intersection_succeeds(self):
        gate, broker, issued = self._issue()
        result = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(), now_epoch=101)
        self.assertEqual("LEASE_CONSUMED_REFERENCE_ONLY", result["state"])
        self.assertEqual(1, broker.consume_count())

    def test_s9_17_broad_profile_cannot_widen_terminal_authority(self):
        profile = self._profile(allowed_actions=["RELEASE", "DEPLOY", "MERGE"])
        gate, broker, result = self._issue(request=self._request(action="DEPLOY"), profile=profile)
        self.assertEqual("DENY_SCOPE_WIDENING", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_18_broad_terminal_authority_cannot_widen_profile_policy(self):
        upstream = self._upstream(action="DEPLOY")
        request = self._request(action="DEPLOY")
        gate, broker, result = self._issue(upstream=upstream, request=request, profile=self._profile(allowed_actions=["RELEASE"]))
        self.assertEqual("DENY_SCOPE_WIDENING", result["state"])
        self.assertEqual(0, broker.issue_count())

    def test_s9_19_governed_records_never_contain_raw_secret(self):
        gate, broker, issued = self._issue()
        gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(), now_epoch=101)
        serialized = json.dumps(gate.governed_records(), sort_keys=True)
        self.assertNotIn(SYNTHETIC_SECRET, serialized)
        self.assertIn("credential_profile_id", serialized)

    def test_s9_20_failure_diagnostics_never_contain_raw_secret(self):
        gate, broker = self._new_gate()
        broker.set_failure_detail(f"provider rejected secret={SYNTHETIC_SECRET}")
        result = gate.issue(upstream_result=self._upstream(), lease_request=self._request(), current_profile=self._profile(), now_epoch=100)
        serialized = json.dumps(result, sort_keys=True) + json.dumps(gate.governed_records(), sort_keys=True)
        self.assertNotIn(SYNTHETIC_SECRET, serialized)

    def test_s9_21_restart_preserves_metadata_without_secret_in_governed_store(self):
        gate, broker, first = self._issue()
        gate2 = CredentialLeaseGate(self.lease_db, ReferenceCredentialBroker(self.broker_db, secrets={("provider-a", "profile-a"): SYNTHETIC_SECRET}))
        replay = gate2.issue(upstream_result=self._upstream(), lease_request=self._request(), current_profile=self._profile(), now_epoch=101)
        self.assertEqual("LEASE_REPLAYED", replay["state"])
        self.assertEqual(first["bound_lease"]["credential_lease_id"], replay["bound_lease"]["credential_lease_id"])
        self.assertNotIn(SYNTHETIC_SECRET, json.dumps(gate2.governed_records(), sort_keys=True))

    def test_s9_22_lease_evidence_hash_binds_all_nonsecret_fields(self):
        gate, broker, issued = self._issue()
        evidence = deepcopy(issued["lease_evidence"])
        supplied = evidence.pop("lease_evidence_hash")
        self.assertEqual(supplied, canonical_hash(evidence))
        for field, value in [("provider_id", "provider-b"), ("credential_profile_id", "profile-b"), ("project_id", "project-2"), ("task_id", "task-2"), ("effect_id", "effect-2"), ("action", "DEPLOY"), ("artifact_sha", "moved"), ("state_version", 8), ("profile_epoch", 4), ("lease_expires_at_epoch", 199)]:
            with self.subTest(field=field):
                changed = deepcopy(evidence)
                changed[field] = value
                self.assertNotEqual(supplied, canonical_hash(changed))

    def test_s9_23_credential_possession_cannot_become_terminal_authority(self):
        gate, broker, issued = self._issue()
        result = gate.consume(upstream_result=self._upstream(state="MODEL_SAYS_AUTHORIZED"), lease_result=issued, current_profile=self._profile(), now_epoch=101)
        self.assertEqual("DENY_UPSTREAM_BINDING", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_24_forged_or_replaced_secret_handle_denies(self):
        gate, broker, issued = self._issue()
        changed = deepcopy(issued)
        changed["bound_lease"]["opaque_secret_handle"] = "forged-handle"
        result = gate.consume(upstream_result=self._upstream(), lease_result=changed, current_profile=self._profile(), now_epoch=101)
        self.assertEqual("LEASE_CONSUMPTION_DENIED", result["state"])
        self.assertEqual(0, broker.consume_count())

    def test_s9_25_no_real_production_action_claim(self):
        gate, broker, issued = self._issue()
        consumed = gate.consume(upstream_result=self._upstream(), lease_result=issued, current_profile=self._profile(), now_epoch=101)
        self.assertFalse(issued["production_side_effect_claimed"])
        self.assertFalse(consumed["production_side_effect_claimed"])
        self.assertFalse(consumed["lease_evidence"]["production_side_effect_claimed"])

    def test_platform_lease_id_is_deterministic(self):
        self.assertEqual(derive_credential_lease_id(self._request()), derive_credential_lease_id(deepcopy(self._request())))

    def test_synthetic_future_provider_is_data_driven(self):
        broker = ReferenceCredentialBroker(self.broker_db, secrets={("future-provider-x", "profile-x"): SYNTHETIC_SECRET})
        gate = CredentialLeaseGate(self.lease_db, broker)
        result = gate.issue(
            upstream_result=self._upstream(),
            lease_request=self._request(provider_id="future-provider-x", credential_profile_id="profile-x"),
            current_profile=self._profile(provider_id="future-provider-x", credential_profile_id="profile-x"),
            now_epoch=100,
        )
        self.assertEqual("LEASE_ISSUED", result["state"])
        self.assertEqual("future-provider-x", result["bound_lease"]["provider_id"])


if __name__ == "__main__":
    unittest.main()
