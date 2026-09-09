from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from integrated_governed_mvp_terminal_executor import (
    SimulatedExecutorCrash,
    TerminalExecutor,
    canonical_hash,
)


class DurableIdempotentAdapter:
    """Separate durable adapter ledger used to falsify the side-effect/local-record gap."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS durable_adapter_effects (
                    terminal_execution_id TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    @property
    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM durable_adapter_effects").fetchone()[0]

    def recover(self, terminal_execution_id: str, binding_hash: str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT binding_hash, result_json FROM durable_adapter_effects WHERE terminal_execution_id=?",
                (terminal_execution_id,),
            ).fetchone()
            if row is None:
                return None
            if row["binding_hash"] != binding_hash:
                raise ValueError("adapter idempotency identity rebound to different binding")
            return json.loads(row["result_json"])

    def execute_once(self, terminal_execution_id: str, binding_hash: str, binding):
        result = {"status": "LOCAL_REFERENCE_APPLIED"}
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT binding_hash, result_json FROM durable_adapter_effects WHERE terminal_execution_id=?",
                (terminal_execution_id,),
            ).fetchone()
            if row is not None:
                if row["binding_hash"] != binding_hash:
                    conn.rollback()
                    raise ValueError("adapter idempotency identity rebound to different binding")
                conn.rollback()
                return json.loads(row["result_json"])
            conn.execute(
                "INSERT INTO durable_adapter_effects(terminal_execution_id,binding_hash,result_json) VALUES(?,?,?)",
                (terminal_execution_id, binding_hash, json.dumps(result, sort_keys=True)),
            )
            conn.commit()
        return result


class Slice7OptionBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.executor_db = root / "terminal-executor.sqlite3"
        self.adapter_db = root / "durable-adapter.sqlite3"
        self.executor = TerminalExecutor(self.executor_db)
        self.adapter = DurableIdempotentAdapter(self.adapter_db)
        self.now_epoch = 100
        self.request = {
            "terminal_execution_id": "term-exec-option-b",
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

    def tearDown(self):
        self.tmp.cleanup()

    def _receipt(self):
        body = {
            "state": "AUTHORIZED_FOR_TERMINAL_ACTION",
            "reason": "exact bound external terminal approval is valid",
            "authorized": True,
            "terminal_authority": True,
            "release_completion_authority": True,
            "actual_side_effect_performed": False,
            "bound_lineage": {
                "project_id": "project-1",
                "task_id": "task-1",
                "effect_id": "effect-1",
                "action": "RELEASE",
                "artifact_sha": "abc123",
                "state_version": 7,
            },
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

    def _run(self, **overrides):
        values = {
            "terminal_request": self.request,
            "current_state": self.current_state,
            "current_authority": self.current_authority,
            "now_epoch": self.now_epoch,
            "adapter": self.adapter,
        }
        values.update(overrides)
        return self.executor.execute(**values)

    def test_s7_22_expired_authority_denies_even_with_valid_receipt(self):
        authority = self._authority(expires_at_epoch=100)
        result = self._run(current_authority=authority)
        self.assertEqual("DENY_AUTHORITY_FRESHNESS", result["state"])
        self.assertEqual(0, self.adapter.count)

    def test_s7_23_revoked_authority_denies(self):
        result = self._run(current_authority=self._authority(status="REVOKED"))
        self.assertEqual("DENY_AUTHORITY_FRESHNESS", result["state"])
        self.assertEqual(0, self.adapter.count)

    def test_s7_24_not_yet_valid_and_lineage_substitution_deny(self):
        cases = (
            {"not_before_epoch": 101},
            {"authority_id": "authority-2"},
            {"project_id": "project-2"},
            {"task_id": "task-2"},
            {"effect_id": "effect-2"},
            {"action": "MERGE"},
            {"artifact_sha": "def456"},
            {"state_version": 8},
        )
        for index, overrides in enumerate(cases):
            with self.subTest(overrides=overrides):
                adapter = DurableIdempotentAdapter(Path(self.tmp.name) / f"adapter-{index}.sqlite3")
                result = self._run(adapter=adapter, current_authority=self._authority(**overrides))
                self.assertEqual("DENY_AUTHORITY_FRESHNESS", result["state"])
                self.assertEqual(0, adapter.count)

    def test_s7_25_tampered_authority_snapshot_hash_denies(self):
        authority = deepcopy(self.current_authority)
        authority["expires_at_epoch"] = 999
        result = self._run(current_authority=authority)
        self.assertEqual("DENY_AUTHORITY_FRESHNESS", result["state"])
        self.assertEqual(0, self.adapter.count)

    def test_s7_26_crash_after_adapter_side_effect_before_local_completion_recovers_once(self):
        with self.assertRaises(SimulatedExecutorCrash):
            self._run(crash_point="after_adapter_before_completion")
        self.assertEqual(1, self.adapter.count)
        result = self._run()
        self.assertEqual("TERMINAL_EXECUTION_RECOVERED", result["state"])
        self.assertEqual(1, self.adapter.count)

    def test_s7_27_reopen_after_side_effect_precompletion_crash_recovers_once(self):
        with self.assertRaises(SimulatedExecutorCrash):
            self._run(crash_point="after_adapter_before_completion")
        reopened_executor = TerminalExecutor(self.executor_db)
        reopened_adapter = DurableIdempotentAdapter(self.adapter_db)
        result = reopened_executor.execute(
            terminal_request=self.request,
            current_state=self.current_state,
            current_authority=self.current_authority,
            now_epoch=self.now_epoch,
            adapter=reopened_adapter,
        )
        self.assertEqual("TERMINAL_EXECUTION_RECOVERED", result["state"])
        self.assertEqual(1, reopened_adapter.count)

    def test_s7_28_adapter_identity_rebinding_is_rejected(self):
        result = self._run()
        self.assertEqual("TERMINAL_EXECUTION_COMPLETED", result["state"])
        original_count = self.adapter.count
        changed = deepcopy(self.request)
        changed["artifact_sha"] = "def456"
        changed["authorization_receipt"] = self._receipt()
        # Directly prove the durable adapter itself refuses one identity with another binding.
        with self.assertRaises(ValueError):
            self.adapter.execute_once(
                self.request["terminal_execution_id"],
                canonical_hash({"different": "binding"}),
                {"different": "binding"},
            )
        self.assertEqual(original_count, self.adapter.count)

    def test_s7_29_plain_callable_adapter_is_rejected(self):
        calls = []

        def plain_callable(binding):
            calls.append(binding)
            return {"status": "SHOULD_NOT_RUN"}

        result = self._run(adapter=plain_callable)
        self.assertEqual("TERMINAL_EXECUTION_FAILED", result["state"])
        self.assertEqual([], calls)

    def test_s7_30_completion_binds_current_authority_snapshot_hash(self):
        result = self._run()
        evidence = result["completion_evidence"]
        self.assertEqual(
            self.current_authority["authority_snapshot_hash"],
            evidence["authority_snapshot_hash"],
        )
        material = deepcopy(evidence)
        supplied = material.pop("completion_hash")
        self.assertEqual(canonical_hash(material), supplied)
        material["authority_snapshot_hash"] = "tampered"
        self.assertNotEqual(canonical_hash(material), supplied)


if __name__ == "__main__":
    unittest.main()
