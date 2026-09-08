from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
import sqlite3
import tempfile
import unittest

from integrated_governed_mvp import evaluate_governed_execution
from integrated_governed_mvp_execution_gateway import (
    CrashInjected,
    ExecutionGateway,
    canonical_hash,
)


class IntegratedGovernedMVPSlice2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "gateway.sqlite3")
        self.route = {
            "provider": "groq",
            "model": "model-a",
            "sku": "sku-a",
            "deployment_path": "api-a",
            "qualification_ref": "q-1",
            "qualification_epoch": 7,
        }
        self.registry = {
            **self.route,
            "qualification_expires_epoch": 100,
            "eligible": True,
            "revoked": False,
        }
        self.capability = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "expires_at": "2030-01-01T00:00:00Z",
            "allowed_actions": ["WRITE", "RELEASE", "DEPLOY", "MERGE"],
            "artifact_classes": ["CODE", "TEST"],
            "revoked": False,
        }
        self.request = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "action": "WRITE",
            "artifact_classes": ["CODE"],
        }
        self.model_result = {
            "evidence_eligible": True,
            "authorized_scope": ["CODE"],
            "changed_artifacts": ["CODE"],
            "review_requested": False,
        }
        self.review_gate = {"state": "CLEAR", "evidence_refs": ["ev-1"]}
        self.artifact = {
            "artifact_id": "src/example.py",
            "artifact_class": "CODE",
            "revision": "sha-artifact-a",
        }
        self.worker_calls = 0

    def tearDown(self):
        self.tmp.cleanup()

    def worker(self, effect_request):
        self.worker_calls += 1
        return {
            "status": "SUCCESS",
            "worker_effect": "LOCAL_DETERMINISTIC_WRITE",
            "effect_request_hash": canonical_hash(effect_request),
            "claimed_authority": "RELEASE",
        }

    def make_upstream(self, **overrides):
        values = {
            "route": deepcopy(self.route),
            "registry_entry": deepcopy(self.registry),
            "normalized_model_result": deepcopy(self.model_result),
            "capability": deepcopy(self.capability),
            "execution_request": deepcopy(self.request),
            "review_gate": deepcopy(self.review_gate),
            "now_epoch": 10,
            "now_iso": "2026-09-07T00:00:00Z",
        }
        values.update(overrides)
        decision = evaluate_governed_execution(**values)
        envelope = {
            "decision": decision,
            "decision_hash": canonical_hash(decision),
            "route": deepcopy(values["route"]),
            "registry_entry": deepcopy(values["registry_entry"]),
            "normalized_model_result": deepcopy(values["normalized_model_result"]),
            "capability": deepcopy(values["capability"]),
            "execution_request": deepcopy(values["execution_request"]),
            "review_gate": deepcopy(values["review_gate"]),
            "decision_now_epoch": values["now_epoch"],
            "decision_now_iso": values["now_iso"],
            "artifact_binding": deepcopy(self.artifact),
        }
        return envelope

    def execute(self, gateway=None, **overrides):
        gateway = gateway or ExecutionGateway(self.db_path, self.worker)
        values = {
            "upstream": self.make_upstream(),
            "current_registry_entry": deepcopy(self.registry),
            "current_capability": deepcopy(self.capability),
            "execution_request": deepcopy(self.request),
            "current_artifact_binding": deepcopy(self.artifact),
            "idempotency_key": "idem-1",
            "now_epoch": 11,
            "now_iso": "2026-09-07T00:01:00Z",
        }
        values.update(overrides)
        return gateway.execute(**values)

    def test_s2_01_clean_exact_decision_performs_one_effect(self):
        result = self.execute()
        self.assertEqual(result["state"], "EXECUTED")
        self.assertEqual(self.worker_calls, 1)
        self.assertFalse(result["terminal_authority"])

    def test_s2_02_non_authorizing_upstream_states_fail_before_effect(self):
        cases = []
        cases.append({})
        denied_registry = deepcopy(self.registry)
        denied_registry["revoked"] = True
        cases.append({"registry_entry": denied_registry})
        cases.append({"review_gate": {"state": "REVIEW_REQUIRED", "evidence_refs": ["ev-r"]}})
        cases.append({"review_gate": {"state": "HUMAN_REQUIRED", "evidence_refs": ["ev-h"]}})
        terminal_request = deepcopy(self.request)
        terminal_request["action"] = "RELEASE"
        cases.append({"execution_request": terminal_request})

        missing = self.make_upstream()
        missing["decision"] = {}
        missing["decision_hash"] = canonical_hash({})
        result = self.execute(upstream=missing, idempotency_key="s2-02-missing")
        self.assertEqual(result["state"], "DENIED_UPSTREAM")

        forged = self.make_upstream()
        forged["decision"] = {**forged["decision"], "decision": "AUTHORIZED_FOR_ISOLATED_EXECUTION", "reason": "forged"}
        result = self.execute(upstream=forged, idempotency_key="s2-02-forged")
        self.assertEqual(result["state"], "DENIED_UPSTREAM_INTEGRITY")

        for index, override in enumerate(cases[1:], start=1):
            upstream = self.make_upstream(**override)
            result = self.execute(upstream=upstream, idempotency_key=f"s2-02-{index}")
            self.assertEqual(result["state"], "DENIED_UPSTREAM")
        self.assertEqual(self.worker_calls, 0)

    def test_s2_03_substitution_against_upstream_binding_fails_before_effect(self):
        mutations = []
        request = deepcopy(self.request); request["action"] = "MERGE"; mutations.append({"execution_request": request})
        request = deepcopy(self.request); request["artifact_classes"] = ["TEST"]; mutations.append({"execution_request": request})
        request = deepcopy(self.request); request["subject_id"] = "worker-2"; mutations.append({"execution_request": request})
        cap = deepcopy(self.capability); cap["issued_epoch"] = 4; mutations.append({"current_capability": cap})
        for index, mutation in enumerate(mutations):
            result = self.execute(idempotency_key=f"s2-03-{index}", **mutation)
            self.assertEqual(result["state"], "DENIED_BINDING")
        self.assertEqual(self.worker_calls, 0)

    def test_s2_04_fresh_revocation_expiry_and_qualification_drift_fail(self):
        cap = deepcopy(self.capability); cap["revoked"] = True
        self.assertEqual(self.execute(current_capability=cap, idempotency_key="s2-04-r")["state"], "DENIED_CURRENT_STATE")
        cap = deepcopy(self.capability); cap["expires_at"] = "2026-09-07T00:00:30Z"
        self.assertEqual(self.execute(current_capability=cap, idempotency_key="s2-04-e")["state"], "DENIED_CURRENT_STATE")
        registry = deepcopy(self.registry); registry["qualification_epoch"] = 8
        self.assertEqual(self.execute(current_registry_entry=registry, idempotency_key="s2-04-q")["state"], "DENIED_CURRENT_STATE")
        self.assertEqual(self.worker_calls, 0)

    def test_s2_05_exact_replay_returns_exact_prior_durable_result(self):
        first = self.execute()
        second = self.execute()
        self.assertEqual(first["result"], second["result"])
        self.assertEqual(first["effect_id"], second["effect_id"])
        self.assertEqual(second["state"], "REPLAYED")
        self.assertEqual(self.worker_calls, 1)

    def test_s2_06_idempotency_semantic_rebind_fails_and_preserves_original(self):
        first = self.execute()
        changed = deepcopy(self.request); changed["artifact_classes"] = ["TEST"]
        denied = self.execute(execution_request=changed)
        self.assertEqual(denied["state"], "DENIED_IDEMPOTENCY_REBIND")
        replay = self.execute()
        self.assertEqual(replay["effect_id"], first["effect_id"])
        self.assertEqual(self.worker_calls, 1)

    def test_s2_07_crash_before_effect_commit_has_zero_effect_then_retry_once(self):
        with self.assertRaises(CrashInjected):
            self.execute(crash_at="BEFORE_EFFECT_COMMIT")
        self.assertEqual(ExecutionGateway(self.db_path, self.worker).effect_count(), 0)
        result = self.execute(gateway=ExecutionGateway(self.db_path, self.worker))
        self.assertEqual(result["state"], "RECOVERED_AND_EXECUTED")
        self.assertEqual(self.worker_calls, 1)
        self.assertEqual(ExecutionGateway(self.db_path, self.worker).effect_count(), 1)

    def test_s2_08_crash_after_effect_commit_replays_exact_result_without_duplicate(self):
        with self.assertRaises(CrashInjected):
            self.execute(crash_at="AFTER_EFFECT_COMMIT_BEFORE_RESPONSE")
        self.assertEqual(self.worker_calls, 1)
        gateway = ExecutionGateway(self.db_path, self.worker)
        self.assertEqual(gateway.effect_count(), 1)
        result = self.execute(gateway=gateway)
        self.assertEqual(result["state"], "RECOVERED_REPLAY")
        self.assertEqual(self.worker_calls, 1)
        self.assertEqual(gateway.effect_count(), 1)

    def test_s2_09_restart_preserves_idempotency_and_non_rebind(self):
        first = self.execute()
        restarted = ExecutionGateway(self.db_path, self.worker)
        replay = self.execute(gateway=restarted)
        self.assertEqual(replay["effect_id"], first["effect_id"])
        changed_artifact = deepcopy(self.artifact); changed_artifact["revision"] = "sha-artifact-b"
        denied = self.execute(gateway=restarted, current_artifact_binding=changed_artifact)
        self.assertEqual(denied["state"], "DENIED_IDEMPOTENCY_REBIND")
        self.assertEqual(self.worker_calls, 1)

    def test_s2_10_worker_terminal_claim_cannot_mint_authority(self):
        result = self.execute()
        self.assertEqual(result["result"]["claimed_authority"], "RELEASE")
        self.assertFalse(result["terminal_authority"])
        self.assertFalse(result["release_completion_authority"])

    def test_s2_11_terminal_action_is_separate_external_gate(self):
        self.execute()
        gateway = ExecutionGateway(self.db_path, self.worker)
        terminal = gateway.request_terminal_action("RELEASE", {"effect_id": gateway.list_effect_ids()[0]})
        self.assertEqual(terminal["state"], "TERMINAL_AUTHORITY_REQUIRED")
        self.assertFalse(terminal["authorized"])
        self.assertEqual(self.worker_calls, 1)

    def test_s2_12_malformed_partial_conflicting_durable_state_fails_closed(self):
        first = self.execute()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "UPDATE gateway_ledger SET result_hash = ? WHERE idempotency_key = ?",
                ("tampered", "idem-1"),
            )
            connection.commit()
        gateway = ExecutionGateway(self.db_path, self.worker)
        denied = self.execute(gateway=gateway)
        self.assertEqual(denied["state"], "BLOCKED_AMBIGUOUS_DURABLE_STATE")
        self.assertEqual(self.worker_calls, 1)
        self.assertEqual(gateway.effect_count(), 1)
        self.assertEqual(first["effect_id"], gateway.list_effect_ids()[0])

    def test_s2_13_concurrent_identical_retries_converge(self):
        def invoke(_):
            gateway = ExecutionGateway(self.db_path, self.worker)
            return self.execute(gateway=gateway)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(invoke, range(8)))
        self.assertEqual(len({item["effect_id"] for item in results}), 1)
        self.assertEqual(len({canonical_hash(item["result"]) for item in results}), 1)
        self.assertEqual(self.worker_calls, 1)
        self.assertEqual(ExecutionGateway(self.db_path, self.worker).effect_count(), 1)

    def test_s2_14_current_artifact_binding_drift_fails_before_effect(self):
        changed = deepcopy(self.artifact); changed["revision"] = "sha-artifact-b"
        result = self.execute(current_artifact_binding=changed)
        self.assertEqual(result["state"], "DENIED_BINDING")
        self.assertEqual(self.worker_calls, 0)

    def test_s2_15_evidence_has_exact_decision_capability_effect_result_lineage(self):
        result = self.execute()
        evidence = ExecutionGateway(self.db_path, self.worker).get_evidence("idem-1")
        upstream = self.make_upstream()
        self.assertEqual(evidence["upstream_decision_hash"], upstream["decision_hash"])
        self.assertEqual(evidence["capability_lineage"]["capability_id"], "cap-1")
        self.assertEqual(evidence["capability_lineage"]["issued_epoch"], 3)
        self.assertEqual(evidence["effect_id"], result["effect_id"])
        self.assertEqual(evidence["result_hash"], canonical_hash(result["result"]))
        self.assertIn(evidence["disposition"], {"EXECUTED", "REPLAYED", "RECOVERED_AND_EXECUTED", "RECOVERED_REPLAY"})
        self.assertTrue(evidence["request_effect_binding_hash"])

    def test_s2_16_fresh_second_authorized_request_remains_live_after_recovery_history(self):
        with self.assertRaises(CrashInjected):
            self.execute(crash_at="AFTER_EFFECT_COMMIT_BEFORE_RESPONSE")
        self.execute(gateway=ExecutionGateway(self.db_path, self.worker))
        second_request = deepcopy(self.request)
        second_request["task_id"] = "t-2"
        second_capability = deepcopy(self.capability)
        second_capability["task_id"] = "t-2"
        second_capability["capability_id"] = "cap-2"
        second_request["capability_id"] = "cap-2"
        second_artifact = deepcopy(self.artifact)
        second_artifact["artifact_id"] = "src/second.py"
        second_artifact["revision"] = "sha-artifact-2"
        upstream = self.make_upstream(capability=second_capability, execution_request=second_request)
        upstream["artifact_binding"] = deepcopy(second_artifact)
        gateway = ExecutionGateway(self.db_path, self.worker)
        second = gateway.execute(
            upstream=upstream,
            current_registry_entry=deepcopy(self.registry),
            current_capability=second_capability,
            execution_request=second_request,
            current_artifact_binding=second_artifact,
            idempotency_key="idem-2",
            now_epoch=11,
            now_iso="2026-09-07T00:01:00Z",
        )
        self.assertEqual(second["state"], "EXECUTED")
        self.assertEqual(gateway.effect_count(), 2)
        self.assertEqual(self.worker_calls, 2)


if __name__ == "__main__":
    unittest.main()
