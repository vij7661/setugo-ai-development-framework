from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import threading
import unittest

from integrated_governed_mvp_terminal_executor import (
    SimulatedExecutorCrash,
    TerminalExecutor,
    canonical_hash,
)


class CountingAdapter:
    def __init__(self, *, fail: bool = False, override: dict | None = None):
        self.count = 0
        self.fail = fail
        self.override = override or {}
        self.lock = threading.Lock()
        self._results: dict[str, tuple[str, dict]] = {}

    def recover(self, terminal_execution_id: str, binding_hash: str):
        with self.lock:
            stored = self._results.get(terminal_execution_id)
            if stored is None:
                return None
            stored_hash, result = stored
            if stored_hash != binding_hash:
                raise ValueError("adapter idempotency identity rebound")
            return deepcopy(result)

    def execute_once(self, terminal_execution_id: str, binding_hash: str, binding):
        with self.lock:
            stored = self._results.get(terminal_execution_id)
            if stored is not None:
                stored_hash, result = stored
                if stored_hash != binding_hash:
                    raise ValueError("adapter idempotency identity rebound")
                return deepcopy(result)
            if self.fail:
                raise RuntimeError("adapter boom")
            result = {"status": "LOCAL_REFERENCE_APPLIED", **self.override}
            self._results[terminal_execution_id] = (binding_hash, deepcopy(result))
            self.count += 1
            return result


class TerminalExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "terminal-executor.sqlite3"
        self.executor = TerminalExecutor(self.db_path)
        self.now_epoch = 100
        self.request = {
            "terminal_execution_id": "term-exec-1",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "expected_state_version": 7,
        }
        self.request["authorization_receipt"] = self._receipt()
        self.current_state = {
            "project_id": "project-1",
            "state_version": 7,
            "artifact_sha": "abc123",
        }
        self.current_authority = self._authority()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _receipt(self, **lineage_overrides):
        lineage = {
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
        }
        lineage.update(lineage_overrides)
        body = {
            "state": "AUTHORIZED_FOR_TERMINAL_ACTION",
            "reason": "exact bound external terminal approval is valid",
            "authorized": True,
            "terminal_authority": True,
            "release_completion_authority": True,
            "actual_side_effect_performed": False,
            "bound_lineage": lineage,
            "authority_id": "authority-1",
            "review_evidence_refs": ["review:abc123"],
            "authority_evidence_refs": ["human:authority-1"],
        }
        return {**body, "receipt_hash": canonical_hash(body)}

    def _authority(self, **overrides):
        body = {
            "authority_id": "authority-1",
            "status": "ACTIVE",
            "not_before_epoch": 50,
            "expires_at_epoch": 150,
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
        }
        body.update(overrides)
        return {**body, "authority_snapshot_hash": canonical_hash(body)}

    def _run(self, adapter=None, **overrides):
        values = {
            "terminal_request": self.request,
            "current_state": self.current_state,
            "current_authority": self.current_authority,
            "now_epoch": self.now_epoch,
            "adapter": adapter or CountingAdapter(),
        }
        values.update(overrides)
        return self.executor.execute(**values)

    def test_s7_01_exact_valid_release_executes_once(self):
        adapter = CountingAdapter()
        result = self._run(adapter)
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual(1, adapter.count)
        self.assertTrue(result["successful_completion"])

    def test_s7_02_merge_executes_only_merge(self):
        adapter = CountingAdapter()
        req = {**self.request, "action": "MERGE", "authorization_receipt": self._receipt(action="MERGE")}
        result = self._run(adapter, terminal_request=req, current_authority=self._authority(action="MERGE"))
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual("MERGE", result["bound_execution"]["action"])

    def test_s7_03_deploy_executes_only_deploy(self):
        adapter = CountingAdapter()
        req = {**self.request, "action": "DEPLOY", "authorization_receipt": self._receipt(action="DEPLOY")}
        result = self._run(adapter, terminal_request=req, current_authority=self._authority(action="DEPLOY"))
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual("DEPLOY", result["bound_execution"]["action"])

    def test_s7_04_complete_executes_only_complete(self):
        adapter = CountingAdapter()
        req = {**self.request, "action": "COMPLETE", "authorization_receipt": self._receipt(action="COMPLETE")}
        result = self._run(adapter, terminal_request=req, current_authority=self._authority(action="COMPLETE"))
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual("COMPLETE", result["bound_execution"]["action"])

    def test_s7_05_missing_or_non_authorized_receipt_denies(self):
        adapter = CountingAdapter()
        req = {**self.request, "authorization_receipt": {}}
        result = self._run(adapter, terminal_request=req)
        self.assertEqual("DENY_AUTHORIZATION_RECEIPT", result["state"])
        self.assertEqual(0, adapter.count)

    def test_s7_06_tampered_receipt_hash_denies(self):
        adapter = CountingAdapter()
        receipt = deepcopy(self.request["authorization_receipt"])
        receipt["authority_id"] = "tampered"
        req = {**self.request, "authorization_receipt": receipt}
        result = self._run(adapter, terminal_request=req)
        self.assertEqual("DENY_AUTHORIZATION_RECEIPT", result["state"])
        self.assertEqual(0, adapter.count)

    def test_s7_07_request_receipt_substitution_denies(self):
        for field, changed in (
            ("project_id", "other-project"),
            ("task_id", "other-task"),
            ("effect_id", "other-effect"),
            ("action", "MERGE"),
            ("artifact_sha", "other-sha"),
            ("expected_state_version", 8),
        ):
            with self.subTest(field=field):
                adapter = CountingAdapter()
                req = {**self.request, field: changed, "terminal_execution_id": f"exec-{field}"}
                result = self._run(adapter, terminal_request=req)
                self.assertEqual("DENY_BINDING", result["state"])
                self.assertEqual(0, adapter.count)

    def test_s7_08_moved_current_artifact_denies(self):
        adapter = CountingAdapter()
        state = {**self.current_state, "artifact_sha": "moved456"}
        result = self._run(adapter, current_state=state)
        self.assertEqual("DENY_CURRENT_STATE", result["state"])
        self.assertEqual(0, adapter.count)

    def test_s7_09_stale_or_future_current_state_version_denies(self):
        for version in (6, 8):
            with self.subTest(version=version):
                adapter = CountingAdapter()
                state = {**self.current_state, "state_version": version}
                result = self._run(adapter, current_state=state)
                self.assertEqual("DENY_CURRENT_STATE", result["state"])
                self.assertEqual(0, adapter.count)

    def test_s7_10_same_execution_id_changed_binding_rejected(self):
        first_adapter = CountingAdapter()
        self._run(first_adapter)
        second_adapter = CountingAdapter()
        req = {
            **self.request,
            "action": "MERGE",
            "authorization_receipt": self._receipt(action="MERGE"),
        }
        result = self._run(
            second_adapter,
            terminal_request=req,
            current_authority=self._authority(action="MERGE"),
        )
        self.assertEqual("DENY_IDEMPOTENCY_REBIND", result["state"])
        self.assertEqual(0, second_adapter.count)

    def test_s7_11_exact_replay_does_not_invoke_adapter_again(self):
        first_adapter = CountingAdapter()
        self._run(first_adapter)
        second_adapter = CountingAdapter()
        replay = self._run(second_adapter)
        self.assertEqual("TERMINAL_EXECUTION_REPLAYED", replay["state"])
        self.assertEqual(1, first_adapter.count)
        self.assertEqual(0, second_adapter.count)

    def test_s7_12_crash_before_adapter_retry_executes_once(self):
        adapter = CountingAdapter()
        with self.assertRaises(SimulatedExecutorCrash):
            self._run(adapter, crash_point="before_adapter")
        self.assertEqual(0, adapter.count)
        result = self._run(adapter)
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual(1, adapter.count)

    def test_s7_13_crash_after_durable_execution_recovers_without_duplicate(self):
        adapter = CountingAdapter()
        with self.assertRaises(SimulatedExecutorCrash):
            self._run(adapter, crash_point="after_durable_execution")
        self.assertEqual(1, adapter.count)
        second_adapter = CountingAdapter()
        result = self._run(second_adapter)
        self.assertEqual("TERMINAL_EXECUTION_RECOVERED", result["state"])
        self.assertEqual(0, second_adapter.count)

    def test_s7_14_concurrent_identical_requests_converge(self):
        adapter = CountingAdapter()
        results = []
        errors = []

        def worker():
            try:
                results.append(self._run(adapter))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual([], errors)
        self.assertEqual(1, adapter.count)
        self.assertEqual(6, len(results))
        self.assertTrue(all(result["successful_completion"] for result in results))

    def test_s7_15_adapter_failure_is_not_completion(self):
        adapter = CountingAdapter(fail=True)
        result = self._run(adapter)
        self.assertEqual("TERMINAL_EXECUTION_FAILED", result["state"])
        self.assertFalse(result["successful_completion"])
        self.assertIsNone(result["completion_evidence"])

    def test_s7_16_adapter_cannot_widen_action_or_target(self):
        for override in ({"action": "MERGE"}, {"artifact_sha": "other-sha"}):
            with self.subTest(override=override):
                req = {**self.request, "terminal_execution_id": f"exec-{next(iter(override))}"}
                adapter = CountingAdapter(override=override)
                result = self._run(adapter, terminal_request=req)
                self.assertEqual("TERMINAL_EXECUTION_FAILED", result["state"])
                self.assertFalse(result["successful_completion"])

    def test_s7_17_ci_or_model_claim_cannot_replace_authorization(self):
        adapter = CountingAdapter()
        req = {
            **self.request,
            "ci_status": "SUCCESS",
            "model_claim": "RELEASE_COMPLETED",
            "authorization_receipt": {},
        }
        result = self._run(adapter, terminal_request=req)
        self.assertEqual("DENY_AUTHORIZATION_RECEIPT", result["state"])
        self.assertEqual(0, adapter.count)

    def test_s7_18_completion_hash_is_deterministic_and_bound(self):
        result = self._run(CountingAdapter())
        evidence = result["completion_evidence"]
        material = deepcopy(evidence)
        supplied = material.pop("completion_hash")
        self.assertEqual(canonical_hash(material), supplied)
        material["artifact_sha"] = "tampered"
        self.assertNotEqual(canonical_hash(material), supplied)

    def test_s7_19_reopen_preserves_replay_idempotency(self):
        first_adapter = CountingAdapter()
        self._run(first_adapter)
        reopened = TerminalExecutor(self.db_path)
        second_adapter = CountingAdapter()
        result = reopened.execute(
            terminal_request=self.request,
            current_state=self.current_state,
            current_authority=self.current_authority,
            now_epoch=self.now_epoch,
            adapter=second_adapter,
        )
        self.assertEqual("TERMINAL_EXECUTION_REPLAYED", result["state"])
        self.assertEqual(0, second_adapter.count)

    def test_s7_20_fresh_authorized_execution_remains_live_after_failures(self):
        failed_req = {**self.request, "terminal_execution_id": "failed-exec"}
        failed = self._run(CountingAdapter(fail=True), terminal_request=failed_req)
        self.assertEqual("TERMINAL_EXECUTION_FAILED", failed["state"])

        fresh_req = {**self.request, "terminal_execution_id": "fresh-exec"}
        adapter = CountingAdapter()
        result = self._run(adapter, terminal_request=fresh_req)
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        self.assertEqual(1, adapter.count)

    def test_s7_21_no_result_claims_real_production_side_effect(self):
        result = self._run(CountingAdapter())
        self.assertFalse(result["production_side_effect_claimed"])
        self.assertFalse(result["completion_evidence"]["production_side_effect_claimed"])
        text = repr(result).lower()
        self.assertNotIn("production_merge_occurred", text)
        self.assertNotIn("production_deploy_occurred", text)


if __name__ == "__main__":
    unittest.main()
