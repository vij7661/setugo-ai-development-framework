from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from integrated_governed_mvp_repository_gateway import canonical_hash
from integrated_governed_mvp_repository_gateway_v2 import RepositoryMutationGateway as RepositoryMutationGatewayV2
from integrated_governed_mvp_tool_runner_gateway import ToolRunnerGateway
from test_integrated_governed_mvp_slice3 import IntegratedGovernedMVPSlice3Tests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from authoritative_state_ledger_v2 import AuthoritativeStateLedger  # noqa: E402


class IntegratedGovernedMVPSlice1To5Tests(unittest.TestCase):
    """One real composition path across the accepted Slice1→Slice5 mechanisms."""

    def test_s1_to_s5_clean_chain_preserves_lineage_and_no_terminal_authority(self):
        s3_fixture = IntegratedGovernedMVPSlice3Tests(methodName="test_s3_01_clean_exact_manifest_commits_one_local_mutation")
        s3_fixture.setUp()
        try:
            # Slice1 is evaluated and consumed by the real Slice2 gateway inside
            # _make_slice2_receipt(); Slice2's exact receipt is then consumed by
            # the repaired real Slice3 gateway below.
            slice2_receipt = deepcopy(s3_fixture.slice2_receipt)
            self.assertIn(slice2_receipt["result"]["state"], {"EXECUTED", "REPLAYED", "RECOVERED_AND_EXECUTED", "RECOVERED_REPLAY"})
            self.assertFalse(slice2_receipt["result"]["terminal_authority"])

            slice3_gateway = RepositoryMutationGatewayV2(s3_fixture.repo_db)
            slice3_result = s3_fixture._mutate(gateway=slice3_gateway)
            self.assertEqual(slice3_result["state"], "COMMITTED")
            self.assertTrue(slice3_result["success"])
            self.assertFalse(slice3_result["terminal_authority"])
            for field in ("project_id", "task_id", "execution_id", "plan_step_id"):
                self.assertIsInstance(slice3_result[field], str)
                self.assertTrue(slice3_result[field])
            with sqlite3.connect(s3_fixture.repo_db) as con:
                row = con.execute(
                    "SELECT evidence_json FROM repository_mutations WHERE idempotency_key=?",
                    (s3_fixture.manifest["idempotency_key"],),
                ).fetchone()
            self.assertIsNotNone(row)
            slice3_evidence = json.loads(row[0])
            slice3_receipt = {"result": slice3_result, "evidence": slice3_evidence}
            slice3_receipt["receipt_hash"] = canonical_hash(slice3_receipt)
            self.assertEqual(slice3_evidence["slice2_result_hash"], slice2_receipt["receipt_hash"])

            # Slice4 consumes the exact real Slice3 receipt produced above.
            tool_fixture = s3_fixture.workspace / "chain_tool.py"
            tool_fixture.write_text("print('chain-ok')\n", encoding="utf-8")
            tool_db = str(s3_fixture.root / "slice4.sqlite3")
            tool_gateway = ToolRunnerGateway(tool_db)
            tool_contract = {
                "tool_contract_id": "tc-chain",
                "project_id": slice3_result["project_id"],
                "task_id": slice3_result["task_id"],
                "plan_step_id": slice3_result["plan_step_id"],
                "allowed_executable": sys.executable,
                "allowed_workspace_root": str(s3_fixture.workspace.resolve()),
                "allowed_env_keys": [],
                "timeout_seconds": 2.0,
                "max_output_bytes": 128,
                "required_slice3_result_hash": slice3_receipt["receipt_hash"],
            }
            tool_contract["contract_hash"] = canonical_hash(tool_contract)
            manifest = {
                "tool_execution_id": "te-chain",
                "tool_contract_id": tool_contract["tool_contract_id"],
                "execution_id": slice3_result["execution_id"],
                "tool_id": "python-chain-runner",
                "idempotency_key": "tool-chain-idem",
                "executable": sys.executable,
                "argv": [str(tool_fixture)],
                "workspace_path": str(s3_fixture.workspace.resolve()),
                "input_digest": hashlib.sha256(tool_fixture.read_bytes()).hexdigest(),
                "environment": {},
                "slice3_result_hash": slice3_receipt["receipt_hash"],
            }
            manifest["manifest_hash"] = canonical_hash(manifest)
            slice4_result = tool_gateway.execute(
                slice3_receipt=deepcopy(slice3_receipt),
                tool_contract=deepcopy(tool_contract),
                manifest=deepcopy(manifest),
                current_workspace_root=str(s3_fixture.workspace.resolve()),
                idempotency_key=manifest["idempotency_key"],
            )
            self.assertEqual(slice4_result["state"], "EXECUTED")
            self.assertTrue(slice4_result["success"])
            self.assertEqual(slice4_result["stdout"], "chain-ok\n")
            self.assertFalse(slice4_result["terminal_authority"])
            self.assertFalse(slice4_result["release_completion_authority"])

            # Slice5 persists an authoritative state transition whose payload is
            # explicitly bound to the exact Slice4 result hash. TransitionResult
            # is the ledger's typed API; no terminal authority is part of it.
            with tempfile.TemporaryDirectory() as ledger_tmp:
                ledger = AuthoritativeStateLedger(str(Path(ledger_tmp) / "ledger.sqlite3"))
                slice4_hash = canonical_hash(slice4_result)
                accepted = ledger.apply_command(
                    project_id=slice3_result["project_id"],
                    idempotency_key="slice5-chain-idem",
                    command_type="PATCH_STATE",
                    payload={"set": {"status": "verified", "slice4_result_hash": slice4_hash}},
                    expected_version=0,
                    effect_type="NOTIFY",
                    effect_payload={"slice4_result_hash": slice4_hash},
                )
                self.assertEqual(accepted.project_id, slice3_result["project_id"])
                self.assertEqual(accepted.version, 1)
                self.assertFalse(accepted.replayed)
                self.assertEqual(accepted.state["status"], "verified")
                self.assertEqual(accepted.state["slice4_result_hash"], slice4_hash)
                self.assertTrue(accepted.event_id)
                self.assertTrue(accepted.outbox_id)
                audit = ledger.audit(slice3_result["project_id"])
                self.assertTrue(audit["valid"], audit)
                self.assertEqual(audit["final_version"], 1)
                self.assertEqual(audit["event_count"], 1)
        finally:
            s3_fixture.tearDown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
