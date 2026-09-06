from __future__ import annotations

import copy
import os
from pathlib import Path
import tempfile
import unittest

from runtime_process_exp_o import (
    GatewayProcessHarness,
    LoopbackMcpClient,
    ManualTrustedClock,
    ProcessBoundaryWorker,
    TrustedLocalEnforcementPoint,
    read_gateway_effect_count,
)
from runtime_slice_exp_o import (
    AuthorityKernel,
    DurableEvidenceSpool,
    LocalEnforcementPoint,
    McpGateway,
)


class ExpOPilot4TrustedTimeProcessBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.permit_key = b"exp-o-pilot4-permit-key"
        self.kernel = AuthorityKernel(b"exp-o-pilot4-kernel-key")
        self.lep_clock = ManualTrustedClock(2_000)
        self.lep = TrustedLocalEnforcementPoint(
            self.kernel,
            self.permit_key,
            clock_ms=self.lep_clock,
        )
        self.gateway_clock_path = self.root / "gateway-clock-ms.txt"
        self._set_gateway_clock(2_000)
        self.gateway_db = self.root / "gateway.db"
        self.ready_path = self.root / "gateway-ready.json"
        self.spool_path = self.root / "spool.db"
        self.spool = DurableEvidenceSpool(self.spool_path)

        self.contract = {
            "effect_contract_id": "contract-p4",
            "base_sha": "base-p4",
            "allowed_action_classes": ["WRITE"],
            "allowed_resources": ["src/app.py"],
            "forbidden_resources": ["prod/**"],
            "max_changed_files": 1,
            "destructive_effect_allowed": False,
            "semantic_correspondence_required": True,
        }
        self.effect = {
            "effect_contract_id": "contract-p4",
            "base_sha": "base-p4",
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
            effect_contract_id="contract-p4",
            base_sha="base-p4",
        )

    def _set_gateway_clock(self, value_ms: int) -> None:
        self.gateway_clock_path.write_text(str(int(value_ms)), encoding="utf-8")

    def _start_gateway(self) -> GatewayProcessHarness:
        harness = GatewayProcessHarness(
            db_path=self.gateway_db,
            ready_path=self.ready_path,
            clock_path=self.gateway_clock_path,
            permit_key=self.permit_key,
            enable_test_faults=True,
        )
        harness.start()
        self.addCleanup(harness.stop)
        return harness

    def _worker(self, client: LoopbackMcpClient, spool: DurableEvidenceSpool | None = None) -> ProcessBoundaryWorker:
        return ProcessBoundaryWorker(
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            lep=self.lep,
            client=client,
            spool=spool or self.spool,
        )

    def _request(self, worker: ProcessBoundaryWorker, **overrides):
        kwargs = {
            "capability": self.capability,
            "effect_contract": self.contract,
            "effect": self.effect,
            "idempotency_key": "intent-p4",
            "origin_available": True,
            "online_authority_confirmed": False,
            "semantic_verified": True,
            "untrusted_metadata": {},
        }
        kwargs.update(overrides)
        return worker.request_effect(**kwargs)

    def _permit(self, *, effect=None, idempotency_key="permit-p4"):
        result = self.lep.authorize(
            self.capability,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect_contract=self.contract,
            effect=effect or self.effect,
            idempotency_key=idempotency_key,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertTrue(result["authorized"], result)
        return result["permit"]

    def test_p4_01_legacy_pilot3_caller_time_can_backdate_security_decision(self) -> None:
        legacy_kernel = AuthorityKernel(b"legacy-kernel")
        legacy_key = b"legacy-permit"
        legacy_lep = LocalEnforcementPoint(legacy_kernel, legacy_key)
        legacy_gateway = McpGateway(legacy_key, self.root / "legacy-gateway.db")
        expired_cap = legacy_kernel.issue_capability(
            subject_id="worker-a",
            subject_key_thumbprint="key-a",
            issued_at_ms=1_000,
            expires_at_ms=1_500,
            freshness_class="WORKSPACE_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-p4",
            base_sha="base-p4",
        )
        # Conceptual trusted time is 10_000 ms, but the legacy caller supplies
        # 1_200 ms. The frozen Pilot 3 path accepts that caller value.
        auth = legacy_lep.authorize(
            expired_cap,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="legacy-backdate",
            now_ms=1_200,
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
        )
        self.assertTrue(auth["authorized"], auth)
        effect = legacy_gateway.execute(
            permit=auth["permit"],
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="legacy-backdate",
            now_ms=1_200,
        )
        self.assertTrue(effect["authorized"], effect)
        self.assertEqual(legacy_gateway.effect_count(), 1)

    def test_p4_02_trusted_lep_clock_ignores_worker_backdated_time_claim(self) -> None:
        expired_cap = self.kernel.issue_capability(
            subject_id="worker-a",
            subject_key_thumbprint="key-a",
            issued_at_ms=1_000,
            expires_at_ms=1_500,
            freshness_class="WORKSPACE_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-p4",
            base_sha="base-p4",
        )
        worker = self._worker(LoopbackMcpClient("http://127.0.0.1:1", timeout_s=0.1))
        result = self._request(
            worker,
            capability=expired_cap,
            idempotency_key="trusted-lep-time",
            untrusted_metadata={"now_ms": 1_200, "current_time": 1_200},
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "CAPABILITY_EXPIRED")
        self.assertEqual(result["trusted_enforcement_time_ms"], 2_000)
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_03_gateway_trusted_clock_ignores_worker_backdated_time_claim(self) -> None:
        permit = self._permit(idempotency_key="expired-permit")
        self._set_gateway_clock(7_001)
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        result = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="expired-permit",
            untrusted_metadata={"now_ms": 2_000, "timestamp": 2_000},
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "LEP_PERMIT_EXPIRED")
        self.assertEqual(result["gateway_time_ms"], 7_001)
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_04_exact_freshness_threshold_uses_trusted_lep_clock(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        worker = self._worker(client)
        self.lep_clock.set(16_000)
        self._set_gateway_clock(16_000)
        exact = self._request(
            worker,
            idempotency_key="freshness-exact",
            untrusted_metadata={"now_ms": 999_999_999},
        )
        self.assertTrue(exact["authorized"], exact)
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

        self.lep_clock.set(16_001)
        stale = self._request(
            worker,
            idempotency_key="freshness-stale",
            origin_available=False,
            untrusted_metadata={"now_ms": 1_000},
        )
        self.assertFalse(stale["authorized"])
        self.assertEqual(stale["reason"], "STALE_AUTHORITY_FAIL_CLOSED")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

    def test_p4_05_authoritative_gateway_runs_in_separate_process_over_http(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        health = client.health()
        self.assertNotEqual(int(gateway.info["pid"]), os.getpid())
        self.assertEqual(health["transport"], "loopback-http")
        worker = self._worker(client)
        result = self._request(worker, idempotency_key="separate-process")
        self.assertTrue(result["authorized"], result)
        self.assertEqual(result["gateway_instance_id"], gateway.info["gateway_instance_id"])
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

    def test_p4_06_http_without_permit_is_denied(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        result = client.execute(
            permit=None,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="no-permit",
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "LEP_PERMIT_REQUIRED")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_07_fabricated_and_tampered_permits_are_denied_over_http(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        fake = {"payload": {"worker_id": "worker-a"}, "signature": "00" * 32}
        fake_result = client.execute(
            permit=fake,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="fake-permit",
        )
        self.assertFalse(fake_result["authorized"])
        self.assertEqual(fake_result["reason"], "LEP_PERMIT_SIGNATURE_INVALID")

        permit = self._permit(idempotency_key="tampered-permit")
        tampered = copy.deepcopy(permit)
        tampered["payload"]["worker_id"] = "worker-b"
        tampered_result = client.execute(
            permit=tampered,
            worker_id="worker-b",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="tampered-permit",
        )
        self.assertFalse(tampered_result["authorized"])
        self.assertEqual(tampered_result["reason"], "LEP_PERMIT_SIGNATURE_INVALID")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_08_effect_and_idempotency_binding_survive_transport(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        permit = self._permit(idempotency_key="bound")
        changed = copy.deepcopy(self.effect)
        changed["changed_files"] = []
        changed_result = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=changed,
            idempotency_key="bound",
        )
        self.assertFalse(changed_result["authorized"])
        self.assertEqual(changed_result["reason"], "PERMIT_EFFECT_BINDING_MISMATCH")
        key_result = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="different-key",
        )
        self.assertFalse(key_result["authorized"])
        self.assertEqual(key_result["reason"], "PERMIT_IDEMPOTENCY_BINDING_MISMATCH")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_09_response_loss_after_commit_is_transport_unknown_not_false_failure(self) -> None:
        gateway = self._start_gateway()
        worker = self._worker(LoopbackMcpClient(gateway.base_url))
        result = self._request(
            worker,
            idempotency_key="drop-after-commit",
            fault_mode="DROP_RESPONSE_AFTER_COMMIT",
        )
        self.assertIsNone(result["authorized"])
        self.assertEqual(result["decision"], "TRANSPORT_OUTCOME_UNKNOWN")
        self.assertEqual(result["authoritative_outcome"], "UNKNOWN")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)
        types = [r["record_type"] for r in self.spool.records()]
        self.assertEqual(types, ["EXECUTION_INTENT", "TRANSPORT_OUTCOME_UNKNOWN"])

    def test_p4_10_retry_after_response_loss_recovers_without_duplicate_effect(self) -> None:
        gateway = self._start_gateway()
        worker = self._worker(LoopbackMcpClient(gateway.base_url))
        first = self._request(
            worker,
            idempotency_key="response-loss-retry",
            fault_mode="DROP_RESPONSE_AFTER_COMMIT",
        )
        self.assertEqual(first["decision"], "TRANSPORT_OUTCOME_UNKNOWN")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)
        retry = worker.reconcile_and_retry(
            capability=self.capability,
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="response-loss-retry",
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
            untrusted_metadata={"now_ms": -1},
        )
        self.assertTrue(retry["authorized"], retry)
        self.assertEqual(retry["decision"], "IDEMPOTENT_REPLAY")
        self.assertFalse(retry["executed"])
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

    def test_p4_11_gateway_restart_preserves_durable_idempotency(self) -> None:
        first_gateway = self._start_gateway()
        first_client = LoopbackMcpClient(first_gateway.base_url)
        worker = self._worker(first_client)
        first = self._request(worker, idempotency_key="restart-replay")
        self.assertTrue(first["executed"], first)
        first_instance = first["gateway_instance_id"]
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)
        first_gateway.stop()

        second_gateway = GatewayProcessHarness(
            db_path=self.gateway_db,
            ready_path=self.ready_path,
            clock_path=self.gateway_clock_path,
            permit_key=self.permit_key,
            enable_test_faults=True,
        )
        second_gateway.start()
        self.addCleanup(second_gateway.stop)
        self.assertNotEqual(first_instance, second_gateway.info["gateway_instance_id"])
        client = LoopbackMcpClient(second_gateway.base_url)
        permit = self._permit(idempotency_key="restart-replay")
        replay = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="restart-replay",
        )
        self.assertTrue(replay["authorized"], replay)
        self.assertEqual(replay["decision"], "IDEMPOTENT_REPLAY")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

    def test_p4_12_expired_permit_remains_expired_after_gateway_restart(self) -> None:
        permit = self._permit(idempotency_key="restart-expired")
        self._set_gateway_clock(7_001)
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        result = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=self.effect,
            idempotency_key="restart-expired",
            untrusted_metadata={"now_ms": 2_000},
        )
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "LEP_PERMIT_EXPIRED")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_13_same_idempotency_key_cannot_be_rebound_to_different_effect(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        worker = self._worker(client)
        first = self._request(worker, idempotency_key="same-key-different-effect")
        self.assertTrue(first["executed"], first)
        changed = copy.deepcopy(self.effect)
        changed["changed_files"] = []
        permit = self._permit(effect=changed, idempotency_key="same-key-different-effect")
        rebound = client.execute(
            permit=permit,
            worker_id="worker-a",
            worker_key_thumbprint="key-a",
            effect=changed,
            idempotency_key="same-key-different-effect",
        )
        self.assertFalse(rebound["authorized"])
        self.assertEqual(rebound["reason"], "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

    def test_p4_14_process_unavailable_is_transport_unknown_with_zero_new_effect(self) -> None:
        gateway = self._start_gateway()
        old_url = gateway.base_url
        gateway.stop()
        worker = self._worker(LoopbackMcpClient(old_url, timeout_s=0.2))
        result = self._request(worker, idempotency_key="process-down")
        self.assertIsNone(result["authorized"])
        self.assertEqual(result["authoritative_outcome"], "UNKNOWN")
        self.assertFalse(result["transport_complete"])
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 0)

    def test_p4_15_intent_is_durable_before_network_attempt_and_unknown_is_separate(self) -> None:
        gateway = self._start_gateway()
        old_url = gateway.base_url
        gateway.stop()
        worker = self._worker(LoopbackMcpClient(old_url, timeout_s=0.2))
        self._request(worker, idempotency_key="intent-before-http")
        records = self.spool.records()
        self.assertEqual(records[0]["record_type"], "EXECUTION_INTENT")
        self.assertEqual(records[0]["payload"]["transport"], "loopback-http")
        self.assertEqual(records[1]["record_type"], "TRANSPORT_OUTCOME_UNKNOWN")
        self.assertFalse(any(r["record_type"] == "EXECUTION_RESULT" for r in records))

    def test_p4_16_new_client_reconciles_after_response_loss_without_new_logical_intent(self) -> None:
        gateway = self._start_gateway()
        worker = self._worker(LoopbackMcpClient(gateway.base_url))
        first = self._request(
            worker,
            idempotency_key="restart-client-reconcile",
            fault_mode="DROP_RESPONSE_AFTER_COMMIT",
        )
        self.assertEqual(first["decision"], "TRANSPORT_OUTCOME_UNKNOWN")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)

        reopened_spool = DurableEvidenceSpool(self.spool_path)
        new_worker = self._worker(LoopbackMcpClient(gateway.base_url), spool=reopened_spool)
        result = new_worker.reconcile_and_retry(
            capability=self.capability,
            effect_contract=self.contract,
            effect=self.effect,
            idempotency_key="restart-client-reconcile",
            origin_available=True,
            online_authority_confirmed=False,
            semantic_verified=True,
            untrusted_metadata={},
        )
        self.assertEqual(result["decision"], "IDEMPOTENT_REPLAY")
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)
        types = [r["record_type"] for r in reopened_spool.records()]
        self.assertEqual(types.count("EXECUTION_INTENT"), 1)
        self.assertEqual(types.count("EXECUTION_RETRY"), 1)
        self.assertTrue(reopened_spool.verify()["verified"])

    def test_p4_17_transport_provenance_records_instance_and_replay_disposition(self) -> None:
        gateway = self._start_gateway()
        client = LoopbackMcpClient(gateway.base_url)
        worker = self._worker(client)
        result = self._request(worker, idempotency_key="provenance")
        self.assertEqual(result["transport"], "loopback-http")
        self.assertEqual(result["gateway_instance_id"], gateway.info["gateway_instance_id"])
        record = self.spool.result_for_idempotency_key("provenance")
        self.assertIsNotNone(record)
        self.assertEqual(record["transport"], "loopback-http")
        self.assertEqual(record["gateway_instance_id"], gateway.info["gateway_instance_id"])
        self.assertEqual(record["gateway_decision"], "EXECUTED")

    def test_p4_18_clean_control_crosses_process_boundary_exactly_once(self) -> None:
        gateway = self._start_gateway()
        worker = self._worker(LoopbackMcpClient(gateway.base_url))
        result = self._request(
            worker,
            idempotency_key="clean-control-p4",
            untrusted_metadata={"now_ms": -999, "current_time": 9_999_999_999},
        )
        self.assertTrue(result["authorized"], result)
        self.assertTrue(result["executed"], result)
        self.assertEqual(result["decision"], "EXECUTED")
        self.assertEqual(result["gateway_time_ms"], 2_000)
        self.assertEqual(read_gateway_effect_count(self.gateway_db), 1)
        records = self.spool.records()
        self.assertEqual([r["record_type"] for r in records], ["EXECUTION_INTENT", "EXECUTION_RESULT"])
        self.assertTrue(self.spool.verify()["verified"])


if __name__ == "__main__":
    unittest.main()
