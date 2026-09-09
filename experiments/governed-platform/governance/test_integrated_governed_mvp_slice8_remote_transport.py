from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import threading
import unittest

from integrated_governed_mvp_terminal_executor import canonical_hash
from integrated_governed_mvp_remote_transport import (
    RemoteTerminalService,
    RemoteTerminalTransport,
    SimulatedRemoteTransportFailure,
    derive_remote_idempotency_key,
)


class Slice8RemoteTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote_db = root / "remote.sqlite3"
        self.client_db = root / "client.sqlite3"
        self.service = RemoteTerminalService(self.remote_db)
        self.transport = RemoteTerminalTransport(self.client_db, self.service)
        self.completion = self._slice7_completion()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _slice7_completion(self, **overrides):
        bound = {
            "terminal_execution_id": "term-exec-1",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
            "authorization_receipt_hash": "auth-receipt-hash",
            "authority_snapshot_hash": "authority-snapshot-hash",
        }
        bound.update({k: v for k, v in overrides.items() if k in bound})
        evidence_body = {
            **bound,
            "adapter_result_digest": canonical_hash({"status": "LOCAL_REFERENCE_APPLIED"}),
            "adapter_result": {"status": "LOCAL_REFERENCE_APPLIED"},
            "production_side_effect_claimed": False,
        }
        evidence = {**evidence_body, "completion_hash": canonical_hash(evidence_body)}
        body = {
            "state": overrides.get("state", "TERMINAL_EXECUTION_COMPLETED"),
            "reason": "reference completion",
            "successful_completion": overrides.get("successful_completion", True),
            "production_side_effect_claimed": False,
            "bound_execution": bound,
            "completion_evidence": evidence,
        }
        return {**body, "result_hash": canonical_hash(body)}

    def _run(self, completion=None, **kwargs):
        return self.transport.execute(slice7_result=completion or self.completion, **kwargs)

    def test_s8_01_exact_valid_release_executes_once(self):
        result = self._run()
        self.assertEqual("REMOTE_EXECUTION_COMPLETED", result["state"])
        self.assertEqual(1, self.service.effect_count())
        self.assertTrue(result["successful_remote_completion"])

    def test_s8_02_merge_only_merge(self):
        completion = self._slice7_completion(action="MERGE")
        result = self._run(completion)
        self.assertEqual("MERGE", result["bound_remote_execution"]["action"])

    def test_s8_03_deploy_only_deploy(self):
        completion = self._slice7_completion(action="DEPLOY")
        result = self._run(completion)
        self.assertEqual("DEPLOY", result["bound_remote_execution"]["action"])

    def test_s8_04_complete_only_complete(self):
        completion = self._slice7_completion(action="COMPLETE")
        result = self._run(completion)
        self.assertEqual("COMPLETE", result["bound_remote_execution"]["action"])

    def test_s8_05_invalid_slice7_completion_denies(self):
        invalid = deepcopy(self.completion)
        invalid["successful_completion"] = False
        result = self._run(invalid)
        self.assertEqual("DENY_SLICE7_BINDING", result["state"])
        self.assertEqual(0, self.service.effect_count())

    def test_s8_06_changed_lineage_denies(self):
        changed = deepcopy(self.completion)
        changed["bound_execution"]["artifact_sha"] = "moved"
        result = self._run(changed)
        self.assertEqual("DENY_SLICE7_BINDING", result["state"])
        self.assertEqual(0, self.service.effect_count())

    def test_s8_07_caller_replacement_idempotency_key_rejected(self):
        result = self._run(remote_idempotency_key="caller-chosen")
        self.assertEqual("DENY_REMOTE_IDEMPOTENCY_REBIND", result["state"])
        self.assertEqual(0, self.service.effect_count())

    def test_s8_08_same_key_changed_binding_rejected(self):
        first = self._run()
        key = first["bound_remote_execution"]["remote_idempotency_key"]
        changed = self._slice7_completion(action="MERGE")
        result = self.transport.execute(slice7_result=changed, remote_idempotency_key=key)
        self.assertEqual("DENY_REMOTE_IDEMPOTENCY_REBIND", result["state"])
        self.assertEqual(1, self.service.effect_count())

    def test_s8_09_failure_before_remote_acceptance_retry_applies_once(self):
        with self.assertRaises(SimulatedRemoteTransportFailure):
            self._run(failure_point="before_remote_accept")
        self.assertEqual(0, self.service.effect_count())
        result = self._run()
        self.assertEqual("REMOTE_EXECUTION_COMPLETED", result["state"])
        self.assertEqual(1, self.service.effect_count())

    def test_s8_10_commit_before_ack_is_ambiguous_then_reconciled_once(self):
        first = self._run(failure_point="after_remote_commit_before_ack")
        self.assertEqual("REMOTE_OUTCOME_AMBIGUOUS", first["state"])
        self.assertEqual(1, self.service.effect_count())
        second = self._run()
        self.assertEqual("REMOTE_EXECUTION_RECONCILED", second["state"])
        self.assertEqual(1, self.service.effect_count())

    def test_s8_11_timeout_after_commit_does_not_directly_complete(self):
        result = self._run(failure_point="timeout_after_remote_commit")
        self.assertEqual("REMOTE_OUTCOME_AMBIGUOUS", result["state"])
        self.assertFalse(result["successful_remote_completion"])
        self.assertIsNone(result["remote_completion_evidence"])

    def test_s8_12_explicit_reconciliation_completes_without_second_effect(self):
        self._run(failure_point="timeout_after_remote_commit")
        result = self.transport.reconcile(self.completion)
        self.assertEqual("REMOTE_EXECUTION_RECONCILED", result["state"])
        self.assertEqual(1, self.service.effect_count())

    def test_s8_13_concurrent_duplicates_converge(self):
        results = []
        barrier = threading.Barrier(4)
        def worker():
            barrier.wait()
            results.append(self._run())
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(1, self.service.effect_count())
        self.assertEqual(4, len(results))
        self.assertTrue(all(r["state"] in {"REMOTE_EXECUTION_COMPLETED", "REMOTE_EXECUTION_REPLAYED", "REMOTE_EXECUTION_RECONCILED"} for r in results))

    def test_s8_14_remote_widening_response_rejected(self):
        self.service.set_response_override({"artifact_sha": "evil-target"})
        result = self._run()
        self.assertEqual("REMOTE_EXECUTION_FAILED", result["state"])
        self.assertFalse(result["successful_remote_completion"])

    def test_s8_15_structured_remote_failure_not_success(self):
        self.service.set_forced_failure({"status": "FAILED", "reason": "remote rejected"})
        result = self._run()
        self.assertEqual("REMOTE_EXECUTION_FAILED", result["state"])
        self.assertIsNone(result["remote_completion_evidence"])

    def test_s8_16_missing_or_malformed_remote_receipt_rejected(self):
        self.service.set_receipt_mode("missing")
        result = self._run()
        self.assertEqual("REMOTE_EXECUTION_FAILED", result["state"])
        self.assertIsNone(result["remote_completion_evidence"])

    def test_s8_17_restart_after_commit_before_ack_reconciles(self):
        self._run(failure_point="after_remote_commit_before_ack")
        service2 = RemoteTerminalService(self.remote_db)
        transport2 = RemoteTerminalTransport(self.client_db, service2)
        result = transport2.reconcile(self.completion)
        self.assertEqual("REMOTE_EXECUTION_RECONCILED", result["state"])
        self.assertEqual(1, service2.effect_count())

    def test_s8_18_completion_hash_binds_all_fields(self):
        result = self._run()
        evidence = result["remote_completion_evidence"]
        supplied = evidence["remote_completion_hash"]
        body = deepcopy(evidence)
        body.pop("remote_completion_hash")
        self.assertEqual(supplied, canonical_hash(body))
        body["artifact_sha"] = "changed"
        self.assertNotEqual(supplied, canonical_hash(body))

    def test_s8_19_self_report_cannot_replace_slice7_or_remote_receipt(self):
        invalid = deepcopy(self.completion)
        invalid["state"] = "MODEL_SAYS_COMPLETED"
        invalid["successful_completion"] = True
        result = self._run(invalid)
        self.assertEqual("DENY_SLICE7_BINDING", result["state"])

    def test_s8_20_no_production_remote_claim(self):
        result = self._run()
        self.assertFalse(result["production_remote_side_effect_claimed"])
        self.assertFalse(result["remote_completion_evidence"]["production_remote_side_effect_claimed"])

    def test_platform_owned_idempotency_key_is_deterministic(self):
        bound = self.completion["bound_execution"]
        binding_hash = canonical_hash(bound)
        key1 = derive_remote_idempotency_key(bound["terminal_execution_id"], binding_hash)
        key2 = derive_remote_idempotency_key(bound["terminal_execution_id"], binding_hash)
        self.assertEqual(key1, key2)


if __name__ == "__main__":
    unittest.main()
