from __future__ import annotations

from contextlib import closing
import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path

from runtime_slice_exp_o import (
    AgentWorker,
    AuthorityKernel,
    DurableEvidenceSpool,
    LocalEnforcementPoint,
    McpGateway,
    SimulatedWorkerCrash,
)


class ExpOPilot3RuntimeSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)

        self.kernel = AuthorityKernel(b"kernel-test-key-exp-o")
        self.lep = LocalEnforcementPoint(self.kernel, b"lep-gateway-test-key-exp-o")
        self.gateway = McpGateway(self.lep.gateway_verification_key, root / "gateway.db")
        self.spool_path = root / "spool.db"
        self.spool = DurableEvidenceSpool(self.spool_path)
        self.worker = AgentWorker(
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            lep=self.lep,
            gateway=self.gateway,
            spool=self.spool,
        )
        self.contract = {
            "effect_contract_id": "contract-1",
            "base_sha": "base-123",
            "allowed_action_classes": ["WRITE"],
            "allowed_resources": ["src/app.py"],
            "forbidden_resources": ["prod/**"],
            "max_changed_files": 1,
            "destructive_effect_allowed": False,
            "semantic_correspondence_required": True,
        }
        self.effect = {
            "effect_contract_id": "contract-1",
            "base_sha": "base-123",
            "action_class": "WRITE",
            "target_resources": ["src/app.py"],
            "changed_files": ["src/app.py"],
            "destructive_effect": False,
            "provenance_trust_classes": ["MODEL_PROPOSAL"],
        }
        self.capability = self.kernel.issue_capability(
            subject_id="worker-a",
            subject_key_thumbprint="key-a",
            issued_at_ms=1_000,
            expires_at_ms=100_000,
            freshness_class="WORKSPACE_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-1",
            base_sha="base-123",
        )

    def _request(self, **overrides):
        kwargs = {
            "capability": self.capability,
            "effect_contract": self.contract,
            "effect": self.effect,
            "idempotency_key": "intent-1",
            "now_ms": 2_000,
            "origin_available": True,
            "online_authority_confirmed": False,
            "semantic_verified": True,
        }
        kwargs.update(overrides)
        return self.worker.request_effect(**kwargs)

    def test_p3_01_no_capability_denied_before_gateway_effect(self) -> None:
        result = self._request(capability=None)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "PLATFORM_CAPABILITY_REQUIRED")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_02_tampered_capability_signature_fails(self) -> None:
        tampered = copy.deepcopy(self.capability)
        tampered["payload"]["allowed_resources"].append("prod/release.yml")
        result = self._request(capability=tampered)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "CAPABILITY_SIGNATURE_INVALID")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_03_worker_identity_replay_fails(self) -> None:
        other_spool = DurableEvidenceSpool(Path(self.tmp.name) / "spool-b.db")
        other = AgentWorker(
            worker_id="worker-b",
            worker_key_thumbprint="key-b",
            lep=self.lep,
            gateway=self.gateway,
            spool=other_spool,
        )
        result = other.request_effect(
            capability=self.capability,
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="intent-b",
            now_ms=2_000,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "WORKER_IDENTITY_MISMATCH")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_04_epoch_advance_invalidates_old_capability(self) -> None:
        self.kernel.advance_epoch("worker-a")
        result = self._request()
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "AUTHORITY_EPOCH_STALE")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_05_workspace_exact_threshold_passes_and_plus_one_fails(self) -> None:
        exact = self._request(idempotency_key="threshold-exact", now_ms=16_000)
        self.assertTrue(exact["authorized"])
        self.assertEqual(self.gateway.effect_count(), 1)

        stale = self._request(
            idempotency_key="threshold-stale",
            now_ms=16_001,
            origin_available=False,
        )
        self.assertFalse(stale["authorized"])
        self.assertEqual(stale["reason"], "STALE_AUTHORITY_FAIL_CLOSED")
        self.assertEqual(self.gateway.effect_count(), 1)

    def test_p3_05_external_mutation_requires_online_authority(self) -> None:
        external_capability = self.kernel.issue_capability(
            subject_id="worker-a",
            subject_key_thumbprint="key-a",
            issued_at_ms=1_000,
            expires_at_ms=100_000,
            freshness_class="EXTERNAL_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-1",
            base_sha="base-123",
        )
        result = self._request(
            capability=external_capability,
            idempotency_key="external-offline",
            origin_available=False,
            online_authority_confirmed=False,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "ONLINE_AUTHORITY_REQUIRED")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_06_scope_widening_is_denied(self) -> None:
        widened = copy.deepcopy(self.effect)
        widened["target_resources"] = ["prod/release.yml"]
        widened["changed_files"] = ["prod/release.yml"]
        result = self._request(effect=widened)
        self.assertFalse(result["authorized"])
        self.assertIn(
            result["reason"],
            {"CAPABILITY_RESOURCE_SCOPE_EXCEEDED", "FORBIDDEN_RESOURCE_TOUCHED"},
        )
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_06_base_sha_and_destructive_widening_are_denied(self) -> None:
        stale = copy.deepcopy(self.effect)
        stale["base_sha"] = "wrong-base"
        stale_result = self._request(effect=stale, idempotency_key="wrong-base")
        self.assertFalse(stale_result["authorized"])
        self.assertEqual(stale_result["reason"], "BASE_SHA_STALE_OR_MISMATCHED")

        destructive = copy.deepcopy(self.effect)
        destructive["destructive_effect"] = True
        destructive_result = self._request(effect=destructive, idempotency_key="destructive")
        self.assertFalse(destructive_result["authorized"])
        self.assertEqual(destructive_result["reason"], "DESTRUCTIVE_EFFECT_FORBIDDEN")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_07_untrusted_same_path_needs_semantic_verification(self) -> None:
        result = self._request(semantic_verified=False)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "CONTENT_CORRESPONDENCE_NOT_DETERMINISTICALLY_ESTABLISHED")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_08_direct_gateway_bypass_without_permit_fails(self) -> None:
        result = self.gateway.execute(
            permit=None,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="bypass-none",
            now_ms=2_000,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "LEP_PERMIT_REQUIRED")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_08_fabricated_permit_fails(self) -> None:
        fake = {"payload": {"worker_id": "worker-a"}, "signature": "00" * 32}
        result = self.gateway.execute(
            permit=fake,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="bypass-fake",
            now_ms=2_000,
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "LEP_PERMIT_SIGNATURE_INVALID")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_09_gateway_partition_has_zero_effect(self) -> None:
        self.gateway.reachable = False
        result = self._request(idempotency_key="partitioned")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "MCP_GATEWAY_UNREACHABLE")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_10_intent_is_durable_before_gateway_attempt(self) -> None:
        self.gateway.reachable = False
        self._request(idempotency_key="intent-before-effect")
        records = self.spool.records()
        self.assertGreaterEqual(len(records), 2)
        self.assertEqual(records[0]["record_type"], "EXECUTION_INTENT")
        self.assertEqual(records[-1]["record_type"], "EXECUTION_RESULT")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_11_crash_retry_is_exactly_once_at_gateway(self) -> None:
        with self.assertRaises(SimulatedWorkerCrash):
            self._request(idempotency_key="crash-retry", crash_after_gateway=True)
        self.assertEqual(self.gateway.effect_count(), 1)
        self.assertIsNone(self.spool.result_for_idempotency_key("crash-retry"))

        result = self.worker.reconcile_and_retry(
            capability=self.capability,
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="crash-retry",
            now_ms=2_001,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertTrue(result["authorized"])
        self.assertEqual(result["decision"], "IDEMPOTENT_REPLAY")
        self.assertFalse(result["executed"])
        self.assertEqual(self.gateway.effect_count(), 1)
        saved = self.spool.result_for_idempotency_key("crash-retry")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["gateway_decision"], "IDEMPOTENT_REPLAY")

    def test_p3_12_replacement_requires_reconciliation_and_new_binding(self) -> None:
        denied = self.kernel.issue_replacement(
            self.capability,
            new_subject_id="worker-b",
            new_subject_key_thumbprint="key-b",
            issued_at_ms=2_500,
            expires_at_ms=100_000,
            spool_reconciled=False,
        )
        self.assertFalse(denied["issued"])

        self.assertTrue(self.spool.verify()["verified"])
        replacement = self.kernel.issue_replacement(
            self.capability,
            new_subject_id="worker-b",
            new_subject_key_thumbprint="key-b",
            issued_at_ms=2_500,
            expires_at_ms=100_000,
            spool_reconciled=True,
        )
        self.assertTrue(replacement["issued"])

        old_result = self._request(idempotency_key="old-after-replacement", now_ms=3_000)
        self.assertFalse(old_result["authorized"])
        self.assertEqual(old_result["reason"], "CAPABILITY_REVOKED_OR_MISSING")

        replacement_spool = DurableEvidenceSpool(Path(self.tmp.name) / "replacement-spool.db")
        replacement_worker = AgentWorker(
            worker_id="worker-b",
            worker_key_thumbprint="key-b",
            lep=self.lep,
            gateway=self.gateway,
            spool=replacement_spool,
        )
        new_result = replacement_worker.request_effect(
            capability=replacement["capability"],
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="new-worker",
            now_ms=3_000,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertTrue(new_result["authorized"])
        self.assertEqual(self.gateway.effect_count(), 1)

    def test_p3_13_spool_reopen_preserves_chain(self) -> None:
        self._request(idempotency_key="spool-reopen")
        before = self.spool.records()
        reopened = DurableEvidenceSpool(self.spool_path)
        self.assertEqual(reopened.records(), before)
        self.assertTrue(reopened.verify()["verified"])

    def test_p3_14_persisted_evidence_tamper_is_detected(self) -> None:
        self._request(idempotency_key="tamper")
        with closing(sqlite3.connect(self.spool_path)) as conn:
            conn.execute(
                "UPDATE evidence_records SET payload_json = ? WHERE sequence = 1",
                ('{"tampered":true}',),
            )
            conn.commit()
        result = self.spool.verify()
        self.assertFalse(result["verified"])
        self.assertEqual(result["state"], "RECORD_HASH_MISMATCH")

    def test_p3_14_record_deletion_is_detected(self) -> None:
        self._request(idempotency_key="delete")
        with closing(sqlite3.connect(self.spool_path)) as conn:
            conn.execute("DELETE FROM evidence_records WHERE sequence = 1")
            conn.commit()
        result = self.spool.verify()
        self.assertFalse(result["verified"])
        self.assertEqual(result["state"], "SEQUENCE_GAP_OR_REORDER")

    def test_p3_15_permit_is_bound_to_exact_effect_and_idempotency(self) -> None:
        auth = self.lep.authorize(
            self.capability,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="permit-bound",
            now_ms=2_000,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertTrue(auth["authorized"])

        changed = copy.deepcopy(self.effect)
        changed["changed_files"] = []
        changed_result = self.gateway.execute(
            permit=auth["permit"],
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=changed,
            idempotency_key="permit-bound",
            now_ms=2_000,
        )
        self.assertFalse(changed_result["authorized"])
        self.assertEqual(changed_result["reason"], "PERMIT_EFFECT_BINDING_MISMATCH")

        key_result = self.gateway.execute(
            permit=auth["permit"],
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="different-key",
            now_ms=2_000,
        )
        self.assertFalse(key_result["authorized"])
        self.assertEqual(key_result["reason"], "PERMIT_IDEMPOTENCY_BINDING_MISMATCH")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_p3_16_clean_control_executes_once_with_complete_evidence(self) -> None:
        result = self._request(idempotency_key="clean-control")
        self.assertTrue(result["authorized"])
        self.assertTrue(result["executed"])
        self.assertEqual(result["decision"], "EXECUTED")
        self.assertEqual(self.gateway.effect_count(), 1)
        records = self.spool.records()
        self.assertEqual([r["record_type"] for r in records], ["EXECUTION_INTENT", "EXECUTION_RESULT"])
        self.assertTrue(self.spool.verify()["verified"])


if __name__ == "__main__":
    unittest.main()
