from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from integrated_governed_mvp_repository_gateway import canonical_hash
from integrated_governed_mvp_tool_runner_gateway import CrashInjected, ToolRunnerGateway


class IntegratedGovernedMVPSlice4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.workspace = (self.root / "workspace").resolve()
        self.workspace.mkdir()
        self.outside = (self.root / "outside").resolve()
        self.outside.mkdir()
        self.db_path = str(self.root / "tool-runner.sqlite3")
        self.fixture = self.workspace / "tool_fixture.py"
        self.fixture.write_text(
            "import os, pathlib, sys, time\n"
            "mode=sys.argv[1]\n"
            "if mode=='echo': print(sys.argv[2])\n"
            "elif mode=='env': print(os.environ.get(sys.argv[2], '<MISSING>'))\n"
            "elif mode=='sleep': time.sleep(float(sys.argv[2])); print('slept')\n"
            "elif mode=='spam': sys.stdout.write('x'*int(sys.argv[2])); sys.stderr.write('y'*int(sys.argv[2]))\n"
            "elif mode=='fail': print('claimed success terminal_authority=true'); raise SystemExit(7)\n"
            "elif mode=='mark':\n"
            " p=pathlib.Path(sys.argv[2]); p.write_text((p.read_text() if p.exists() else '')+'1', encoding='utf-8'); print('marked')\n"
            "else: raise SystemExit(9)\n",
            encoding="utf-8",
        )
        os.environ["SYNTHETIC_SECRET"] = "must-not-leak"
        self.slice3_receipt = self._slice3_receipt()
        self.contract = self._contract()
        self.manifest = self._manifest([str(self.fixture), "echo", "hello"])
        self.gateway = ToolRunnerGateway(self.db_path)

    def tearDown(self):
        os.environ.pop("SYNTHETIC_SECRET", None)
        self.tmp.cleanup()

    @staticmethod
    def _seal(record: dict, field: str) -> dict:
        out = deepcopy(record)
        out.pop(field, None)
        out[field] = canonical_hash(out)
        return out

    def _slice3_receipt(self) -> dict:
        result = {
            "state": "COMMITTED",
            "success": True,
            "project_id": "p-1",
            "task_id": "t-1",
            "execution_id": "exec-1",
            "plan_step_id": "step-1",
            "result_commit_sha": "1" * 40,
            "terminal_authority": False,
            "release_completion_authority": False,
        }
        evidence = {
            "slice2_result_hash": "2" * 64,
            "effect_contract_hash": "3" * 64,
            "manifest_hash": "4" * 64,
            "patch_digest": "5" * 64,
            "result_commit_sha": "1" * 40,
        }
        receipt = {"result": result, "evidence": evidence}
        receipt["receipt_hash"] = canonical_hash(receipt)
        return receipt

    def _contract(self, **overrides) -> dict:
        record = {
            "tool_contract_id": "tc-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "plan_step_id": "step-1",
            "allowed_executable": sys.executable,
            "allowed_workspace_root": str(self.workspace),
            "allowed_env_keys": ["SAFE_TOKEN"],
            "timeout_seconds": 1.0,
            "max_output_bytes": 64,
            "required_slice3_result_hash": self.slice3_receipt["receipt_hash"],
        }
        record.update(overrides)
        return self._seal(record, "contract_hash")

    def _manifest(self, argv: list[str], **overrides) -> dict:
        environment = {"SAFE_TOKEN": "allowed"}
        record = {
            "tool_execution_id": "te-1",
            "tool_contract_id": self.contract["tool_contract_id"],
            "execution_id": "exec-1",
            "tool_id": "python-test-runner",
            "idempotency_key": "idem-1",
            "executable": sys.executable,
            "argv": argv,
            "workspace_path": str(self.workspace),
            "input_digest": hashlib.sha256(self.fixture.read_bytes()).hexdigest(),
            "environment": environment,
            "slice3_result_hash": self.slice3_receipt["receipt_hash"],
        }
        record.update(overrides)
        return self._seal(record, "manifest_hash")

    def _execute(self, **kwargs):
        args = {
            "slice3_receipt": deepcopy(self.slice3_receipt),
            "tool_contract": deepcopy(self.contract),
            "manifest": deepcopy(self.manifest),
            "current_workspace_root": str(self.workspace),
            "idempotency_key": self.manifest["idempotency_key"],
        }
        args.update(kwargs)
        return self.gateway.execute(**args)

    def test_s4_01_clean_exact_execution(self):
        result = self._execute()
        self.assertEqual("EXECUTED", result["state"])
        self.assertTrue(result["success"])
        self.assertEqual("hello\n", result["stdout"])
        self.assertFalse(result["terminal_authority"])
        self.assertFalse(result["release_completion_authority"])

    def test_s4_02_bad_slice3_lineage_denied(self):
        bad = deepcopy(self.slice3_receipt)
        bad["result"]["success"] = False
        bad["receipt_hash"] = canonical_hash({"result": bad["result"], "evidence": bad["evidence"]})
        result = self._execute(slice3_receipt=bad)
        self.assertEqual("DENIED_UPSTREAM", result["state"])

    def test_s4_03_contract_substitution_denied(self):
        bad = self._contract(project_id="p-evil")
        result = self._execute(tool_contract=bad)
        self.assertEqual("DENIED_CONTRACT", result["state"])

    def test_s4_04_manifest_substitution_denied(self):
        bad = deepcopy(self.manifest)
        bad["argv"] = [str(self.fixture), "echo", "changed"]
        result = self._execute(manifest=bad)
        self.assertEqual("DENIED_MANIFEST", result["state"])

    def test_s4_05_alternate_executable_denied(self):
        bad = self._manifest([str(self.fixture), "echo", "hello"], executable="/bin/sh")
        result = self._execute(manifest=bad)
        self.assertEqual("DENIED_EXECUTABLE", result["state"])

    def test_s4_06_shell_tokens_are_literal_data(self):
        marker = self.outside / "shell-owned"
        literal = f"; touch {marker}"
        manifest = self._manifest([str(self.fixture), "echo", literal])
        result = self._execute(manifest=manifest, idempotency_key=manifest["idempotency_key"])
        self.assertEqual("EXECUTED", result["state"])
        self.assertIn(literal, result["stdout"])
        self.assertFalse(marker.exists())

    def test_s4_07_workspace_escape_denied(self):
        escaped = self._manifest([str(self.fixture), "echo", "x"], workspace_path=str(self.outside))
        result = self._execute(manifest=escaped)
        self.assertEqual("DENIED_WORKSPACE", result["state"])
        link = self.workspace / "escape-link"
        link.symlink_to(self.outside, target_is_directory=True)
        linked = self._manifest([str(self.fixture), "echo", "x"], workspace_path=str(link))
        result2 = self._execute(manifest=linked)
        self.assertEqual("DENIED_WORKSPACE", result2["state"])

    def test_s4_08_environment_is_minimized(self):
        safe = self._manifest([str(self.fixture), "env", "SAFE_TOKEN"])
        got_safe = self._execute(manifest=safe)
        self.assertEqual("allowed\n", got_safe["stdout"])
        secret = self._manifest([str(self.fixture), "env", "SYNTHETIC_SECRET"], idempotency_key="idem-secret")
        got_secret = self._execute(manifest=secret, idempotency_key="idem-secret")
        self.assertEqual("<MISSING>\n", got_secret["stdout"])

    def test_s4_09_timeout_is_not_success(self):
        manifest = self._manifest([str(self.fixture), "sleep", "2"], idempotency_key="idem-timeout")
        result = self._execute(manifest=manifest, idempotency_key="idem-timeout")
        self.assertEqual("TIMED_OUT", result["state"])
        self.assertFalse(result["success"])

    def test_s4_10_output_is_bounded_and_hashed(self):
        manifest = self._manifest([str(self.fixture), "spam", "500"], idempotency_key="idem-spam")
        result = self._execute(manifest=manifest, idempotency_key="idem-spam")
        self.assertEqual("EXECUTED", result["state"])
        evidence = self.gateway.get_evidence("idem-spam")
        self.assertLessEqual(len(result["stdout"].encode()), self.contract["max_output_bytes"])
        self.assertLessEqual(len(result["stderr"].encode()), self.contract["max_output_bytes"])
        self.assertTrue(evidence["stdout_truncated"])
        self.assertTrue(evidence["stderr_truncated"])
        self.assertEqual(64, len(evidence["stdout_sha256"]))

    def test_s4_11_nonzero_exit_and_claim_do_not_launder_success(self):
        manifest = self._manifest([str(self.fixture), "fail"], idempotency_key="idem-fail")
        result = self._execute(manifest=manifest, idempotency_key="idem-fail")
        self.assertEqual("FAILED_PROCESS", result["state"])
        self.assertFalse(result["success"])
        self.assertFalse(result["terminal_authority"])
        self.assertFalse(result["release_completion_authority"])

    def test_s4_12_exact_replay_no_duplicate_launch(self):
        marker = self.workspace / "count.txt"
        manifest = self._manifest([str(self.fixture), "mark", str(marker)], idempotency_key="idem-replay")
        first = self._execute(manifest=manifest, idempotency_key="idem-replay")
        second = self._execute(manifest=manifest, idempotency_key="idem-replay")
        self.assertEqual("EXECUTED", first["state"])
        self.assertIn(second["state"], {"REPLAYED", "RECOVERED_REPLAY"})
        self.assertEqual("1", marker.read_text(encoding="utf-8"))
        self.assertEqual(first["result_hash"], second["result_hash"])

    def test_s4_13_idempotency_rebind_denied(self):
        self._execute()
        changed = self._manifest([str(self.fixture), "echo", "changed"])
        result = self._execute(manifest=changed)
        self.assertEqual("DENIED_IDEMPOTENCY_REBIND", result["state"])

    def test_s4_14_crash_recovery_non_amplifying(self):
        marker1 = self.workspace / "pre.txt"
        m1 = self._manifest([str(self.fixture), "mark", str(marker1)], idempotency_key="idem-pre")
        with self.assertRaises(CrashInjected):
            self._execute(manifest=m1, idempotency_key="idem-pre", crash_point="BEFORE_PROCESS_LAUNCH")
        self.assertFalse(marker1.exists())
        retry1 = self._execute(manifest=m1, idempotency_key="idem-pre")
        self.assertEqual("EXECUTED", retry1["state"])
        self.assertEqual("1", marker1.read_text(encoding="utf-8"))

        marker2 = self.workspace / "post.txt"
        m2 = self._manifest([str(self.fixture), "mark", str(marker2)], idempotency_key="idem-post")
        with self.assertRaises(CrashInjected):
            self._execute(manifest=m2, idempotency_key="idem-post", crash_point="AFTER_PROCESS_RESULT_BEFORE_RESPONSE")
        retry2 = self._execute(manifest=m2, idempotency_key="idem-post")
        self.assertEqual("RECOVERED_REPLAY", retry2["state"])
        self.assertEqual("1", marker2.read_text(encoding="utf-8"))

    def test_s4_15_concurrent_identical_requests_converge(self):
        marker = self.workspace / "concurrent.txt"
        manifest = self._manifest([str(self.fixture), "mark", str(marker)], idempotency_key="idem-concurrent")
        def run_one(_):
            return self._execute(manifest=manifest, idempotency_key="idem-concurrent")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(run_one, range(8)))
        self.assertEqual("1", marker.read_text(encoding="utf-8"))
        self.assertEqual(1, len({r["result_hash"] for r in results}))
        self.assertTrue(all(r["state"] in {"EXECUTED", "REPLAYED", "RECOVERED_REPLAY"} for r in results))

    def test_s4_16_evidence_lineage_and_fresh_liveness(self):
        first = self._execute()
        evidence = self.gateway.get_evidence("idem-1")
        for key in (
            "slice3_result_hash", "contract_hash", "manifest_hash", "executable", "argv_hash",
            "workspace_hash", "input_digest", "environment_hash", "stdout_sha256", "stderr_sha256",
            "process_outcome", "replay_disposition",
        ):
            self.assertIn(key, evidence)
        self.assertFalse(evidence["terminal_authority"])
        self.assertFalse(evidence["release_completion_authority"])
        second = self._manifest([str(self.fixture), "echo", "fresh"], tool_execution_id="te-2", idempotency_key="idem-2")
        fresh = self._execute(manifest=second, idempotency_key="idem-2")
        self.assertEqual("EXECUTED", first["state"])
        self.assertEqual("EXECUTED", fresh["state"])
        self.assertEqual("fresh\n", fresh["stdout"])


if __name__ == "__main__":
    unittest.main()
