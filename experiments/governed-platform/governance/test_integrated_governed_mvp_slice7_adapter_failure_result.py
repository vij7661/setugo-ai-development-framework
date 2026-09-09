from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from integrated_governed_mvp_terminal_executor import TerminalExecutor, canonical_hash


class DurableFailedResultAdapter:
    def __init__(self):
        self.count = 0
        self.result = None
        self.binding_hash = None

    def recover(self, terminal_execution_id, binding_hash):
        if self.result is None:
            return None
        if self.binding_hash != binding_hash:
            raise ValueError("binding rebound")
        return dict(self.result)

    def execute_once(self, terminal_execution_id, binding_hash, binding):
        self.count += 1
        self.binding_hash = binding_hash
        self.result = {"status": "FAILED", "reason": "reference adapter reports failure"}
        return dict(self.result)


class Slice7AdapterFailureResultTest(unittest.TestCase):
    def test_s7_15_structured_adapter_failure_cannot_become_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor = TerminalExecutor(Path(tmp) / "executor.sqlite3")
            receipt_body = {
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
            receipt = {**receipt_body, "receipt_hash": canonical_hash(receipt_body)}
            request = {
                "terminal_execution_id": "term-failed-result",
                "project_id": "project-1",
                "task_id": "task-1",
                "effect_id": "effect-1",
                "action": "RELEASE",
                "artifact_sha": "abc123",
                "expected_state_version": 7,
                "authorization_receipt": receipt,
            }
            authority_body = {
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
            authority = {**authority_body, "authority_snapshot_hash": canonical_hash(authority_body)}
            adapter = DurableFailedResultAdapter()
            result = executor.execute(
                terminal_request=request,
                current_state={"project_id": "project-1", "state_version": 7, "artifact_sha": "abc123"},
                current_authority=authority,
                now_epoch=100,
                adapter=adapter,
            )
            self.assertEqual(1, adapter.count)
            self.assertEqual("TERMINAL_EXECUTION_FAILED", result["state"])
            self.assertFalse(result["successful_completion"])
            self.assertIsNone(result["completion_evidence"])


if __name__ == "__main__":
    unittest.main()
