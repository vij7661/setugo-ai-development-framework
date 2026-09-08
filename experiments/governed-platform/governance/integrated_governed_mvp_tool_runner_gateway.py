from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import threading
from typing import Any

from integrated_governed_mvp_repository_gateway import canonical_hash


class CrashInjected(RuntimeError):
    pass


_LOCKS_GUARD = threading.Lock()
_LOCKS: dict[str, threading.RLock] = {}


def _lock_for(db_path: str) -> threading.RLock:
    key = str(Path(db_path).resolve())
    with _LOCKS_GUARD:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.RLock()
            _LOCKS[key] = lock
        return lock


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _valid_self_hash(record: Any, field: str) -> bool:
    if not isinstance(record, dict):
        return False
    supplied = record.get(field)
    if not isinstance(supplied, str) or len(supplied) != 64:
        return False
    material = deepcopy(record)
    material.pop(field, None)
    return canonical_hash(material) == supplied


def _bounded_decode(data: bytes, limit: int) -> tuple[str, bool]:
    clipped = data[:limit]
    return clipped.decode("utf-8", errors="replace"), len(data) > limit


class ToolRunnerGateway:
    """Reference Slice 4 tool-runner boundary.

    This is deliberately not an arbitrary-code security sandbox. It enforces the
    frozen argv/cwd/env/runtime/result contract for one platform-authorized local
    subprocess and retains durable idempotency/evidence state.
    """

    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).resolve())
        self._lock = _lock_for(self.db_path)
        with self._lock:
            self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_runs (
                    idempotency_key TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT,
                    evidence_json TEXT
                )
                """
            )
            conn.commit()

    @staticmethod
    def _deny(state: str) -> dict[str, Any]:
        return {
            "state": state,
            "success": False,
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    @staticmethod
    def _validate_upstream(receipt: Any) -> tuple[bool, str]:
        if not isinstance(receipt, dict):
            return False, "DENIED_UPSTREAM"
        supplied = receipt.get("receipt_hash")
        material = deepcopy(receipt)
        material.pop("receipt_hash", None)
        if not isinstance(supplied, str) or canonical_hash(material) != supplied:
            return False, "DENIED_UPSTREAM"
        result = receipt.get("result")
        evidence = receipt.get("evidence")
        if not isinstance(result, dict) or not isinstance(evidence, dict):
            return False, "DENIED_UPSTREAM"
        if result.get("success") is not True or result.get("state") not in {"COMMITTED", "EXECUTED", "RECOVERED_REPLAY", "REPLAYED"}:
            return False, "DENIED_UPSTREAM"
        if result.get("terminal_authority") is not False or result.get("release_completion_authority") is not False:
            return False, "DENIED_UPSTREAM"
        for key in ("project_id", "task_id", "execution_id", "plan_step_id"):
            if not isinstance(result.get(key), str) or not result.get(key):
                return False, "DENIED_UPSTREAM"
        return True, ""

    @staticmethod
    def _validate_contract(contract: Any, receipt: dict[str, Any]) -> tuple[bool, str]:
        if not _valid_self_hash(contract, "contract_hash"):
            return False, "DENIED_CONTRACT"
        required = {
            "tool_contract_id": str,
            "project_id": str,
            "task_id": str,
            "plan_step_id": str,
            "allowed_executable": str,
            "allowed_workspace_root": str,
            "allowed_env_keys": list,
            "timeout_seconds": (int, float),
            "max_output_bytes": int,
            "required_slice3_result_hash": str,
        }
        for key, typ in required.items():
            if not isinstance(contract.get(key), typ):
                return False, "DENIED_CONTRACT"
        if not contract["tool_contract_id"] or not contract["allowed_executable"] or not contract["allowed_workspace_root"]:
            return False, "DENIED_CONTRACT"
        if contract["timeout_seconds"] <= 0 or contract["max_output_bytes"] <= 0:
            return False, "DENIED_CONTRACT"
        if not all(isinstance(k, str) and k for k in contract["allowed_env_keys"]):
            return False, "DENIED_CONTRACT"
        if len(set(contract["allowed_env_keys"])) != len(contract["allowed_env_keys"]):
            return False, "DENIED_CONTRACT"
        result = receipt["result"]
        if contract["project_id"] != result["project_id"] or contract["task_id"] != result["task_id"] or contract["plan_step_id"] != result["plan_step_id"]:
            return False, "DENIED_CONTRACT"
        if contract["required_slice3_result_hash"] != receipt["receipt_hash"]:
            return False, "DENIED_CONTRACT"
        return True, ""

    @staticmethod
    def _validate_manifest(manifest: Any, contract: dict[str, Any], receipt: dict[str, Any], idempotency_key: str) -> tuple[bool, str]:
        if not _valid_self_hash(manifest, "manifest_hash"):
            return False, "DENIED_MANIFEST"
        for key in ("tool_execution_id", "tool_contract_id", "execution_id", "tool_id", "idempotency_key", "executable", "workspace_path", "input_digest", "slice3_result_hash"):
            if not isinstance(manifest.get(key), str) or not manifest.get(key):
                return False, "DENIED_MANIFEST"
        argv = manifest.get("argv")
        env = manifest.get("environment")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            return False, "DENIED_MANIFEST"
        if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
            return False, "DENIED_MANIFEST"
        if manifest["tool_contract_id"] != contract["tool_contract_id"]:
            return False, "DENIED_CONTRACT"
        if manifest["execution_id"] != receipt["result"]["execution_id"]:
            return False, "DENIED_MANIFEST"
        if manifest["slice3_result_hash"] != receipt["receipt_hash"]:
            return False, "DENIED_MANIFEST"
        if manifest["idempotency_key"] != idempotency_key or not idempotency_key:
            return False, "DENIED_MANIFEST"
        if set(env) - set(contract["allowed_env_keys"]):
            return False, "DENIED_MANIFEST"
        if len(manifest["input_digest"]) != 64 or any(c not in "0123456789abcdef" for c in manifest["input_digest"]):
            return False, "DENIED_MANIFEST"
        return True, ""

    @staticmethod
    def _workspace_state(manifest: dict[str, Any], contract: dict[str, Any], current_workspace_root: str) -> tuple[bool, Path | None]:
        try:
            allowed_lexical = Path(contract["allowed_workspace_root"])
            manifest_lexical = Path(manifest["workspace_path"])
            current_lexical = Path(current_workspace_root)
            allowed = allowed_lexical.resolve(strict=True)
            requested = manifest_lexical.resolve(strict=True)
            current = current_lexical.resolve(strict=True)
        except (OSError, RuntimeError):
            return False, None
        if not allowed.is_dir() or requested != allowed or current != allowed:
            return False, None
        # Exact lexical binding prevents replacing the declared workspace with a
        # symlink that merely resolves to another accepted-looking location.
        if os.path.abspath(str(manifest_lexical)) != os.path.abspath(str(allowed_lexical)):
            return False, None
        if os.path.abspath(str(current_lexical)) != os.path.abspath(str(allowed_lexical)):
            return False, None
        return True, allowed

    @staticmethod
    def _validate_input_digest(manifest: dict[str, Any], workspace: Path) -> bool:
        # The frozen reference runner treats argv[0] as the authorized input
        # artifact when it names a file. This binds the pre-authorized script/
        # test artifact bytes to the execution manifest without granting argv
        # any authority of its own.
        first = Path(manifest["argv"][0])
        try:
            candidate = first if first.is_absolute() else workspace / first
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(workspace)
            if not resolved.is_file():
                return False
            return _sha256_bytes(resolved.read_bytes()) == manifest["input_digest"]
        except (OSError, RuntimeError, ValueError):
            return False

    @staticmethod
    def _binding_hash(receipt: dict[str, Any], contract: dict[str, Any], manifest: dict[str, Any]) -> str:
        return canonical_hash({
            "slice3_result_hash": receipt["receipt_hash"],
            "contract_hash": contract["contract_hash"],
            "manifest_hash": manifest["manifest_hash"],
            "tool_execution_id": manifest["tool_execution_id"],
            "execution_id": manifest["execution_id"],
            "tool_id": manifest["tool_id"],
            "idempotency_key": manifest["idempotency_key"],
            "executable": manifest["executable"],
            "argv": manifest["argv"],
            "workspace_path": manifest["workspace_path"],
            "input_digest": manifest["input_digest"],
            "environment": manifest["environment"],
        })

    def _load(self, conn: sqlite3.Connection, key: str) -> sqlite3.Row | None:
        return conn.execute(
            "SELECT idempotency_key,binding_hash,status,result_json,evidence_json FROM tool_runs WHERE idempotency_key=?",
            (key,),
        ).fetchone()

    @staticmethod
    def _deserialize_row(row: sqlite3.Row) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        try:
            result = json.loads(row["result_json"]) if row["result_json"] else None
            evidence = json.loads(row["evidence_json"]) if row["evidence_json"] else None
            if result is not None and not isinstance(result, dict):
                return None, None
            if evidence is not None and not isinstance(evidence, dict):
                return None, None
            return result, evidence
        except (TypeError, json.JSONDecodeError):
            return None, None

    def _existing_result(self, row: sqlite3.Row, binding_hash: str) -> dict[str, Any] | None:
        if row["binding_hash"] != binding_hash:
            return self._deny("DENIED_IDEMPOTENCY_REBIND")
        if row["status"] == "INTENT":
            return None
        if row["status"] not in {"COMMITTED", "ACKED"}:
            return self._deny("BLOCKED_AMBIGUOUS_DURABLE_STATE")
        result, evidence = self._deserialize_row(row)
        if result is None or evidence is None:
            return self._deny("BLOCKED_AMBIGUOUS_DURABLE_STATE")
        expected_result_hash = result.get("result_hash")
        material = deepcopy(result)
        material.pop("state", None)
        material.pop("result_hash", None)
        if not isinstance(expected_result_hash, str) or canonical_hash(material) != expected_result_hash:
            return self._deny("BLOCKED_AMBIGUOUS_DURABLE_STATE")
        replay = deepcopy(result)
        replay["state"] = "RECOVERED_REPLAY" if row["status"] == "COMMITTED" else "REPLAYED"
        return replay

    @staticmethod
    def _run_process(executable: str, argv: list[str], cwd: Path, env: dict[str, str], timeout: float) -> tuple[str, int | None, bytes, bytes]:
        kwargs: dict[str, Any] = {
            "cwd": str(cwd),
            "env": dict(env),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": False,
        }
        if os.name == "posix":
            kwargs["start_new_session"] = True
        proc = subprocess.Popen([executable, *argv], **kwargs)
        try:
            out, err = proc.communicate(timeout=timeout)
            return "EXITED", proc.returncode, out, err
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                proc.kill()
            out, err = proc.communicate()
            return "TIMED_OUT", proc.returncode, out, err

    def execute(
        self,
        *,
        slice3_receipt: dict[str, Any],
        tool_contract: dict[str, Any],
        manifest: dict[str, Any],
        current_workspace_root: str,
        idempotency_key: str,
        crash_point: str | None = None,
    ) -> dict[str, Any]:
        ok, state = self._validate_upstream(slice3_receipt)
        if not ok:
            return self._deny(state)
        ok, state = self._validate_contract(tool_contract, slice3_receipt)
        if not ok:
            return self._deny(state)
        ok, state = self._validate_manifest(manifest, tool_contract, slice3_receipt, idempotency_key)
        if not ok:
            return self._deny(state)
        if manifest["executable"] != tool_contract["allowed_executable"]:
            return self._deny("DENIED_EXECUTABLE")
        if not Path(manifest["executable"]).is_absolute():
            return self._deny("DENIED_EXECUTABLE")
        try:
            executable = str(Path(manifest["executable"]).resolve(strict=True))
            allowed_executable = str(Path(tool_contract["allowed_executable"]).resolve(strict=True))
        except OSError:
            return self._deny("DENIED_EXECUTABLE")
        if executable != allowed_executable:
            return self._deny("DENIED_EXECUTABLE")
        workspace_ok, workspace = self._workspace_state(manifest, tool_contract, current_workspace_root)
        if not workspace_ok or workspace is None:
            return self._deny("DENIED_WORKSPACE")
        if not self._validate_input_digest(manifest, workspace):
            return self._deny("DENIED_MANIFEST")

        binding_hash = self._binding_hash(slice3_receipt, tool_contract, manifest)
        with self._lock:
            with self._connect() as conn:
                row = self._load(conn, idempotency_key)
                if row is not None:
                    existing = self._existing_result(row, binding_hash)
                    if existing is not None:
                        if existing["state"] == "RECOVERED_REPLAY":
                            conn.execute("UPDATE tool_runs SET status='ACKED' WHERE idempotency_key=?", (idempotency_key,))
                            conn.commit()
                        return existing
                else:
                    conn.execute(
                        "INSERT INTO tool_runs(idempotency_key,binding_hash,status,result_json,evidence_json) VALUES(?,?, 'INTENT', NULL, NULL)",
                        (idempotency_key, binding_hash),
                    )
                    conn.commit()

                if crash_point == "BEFORE_PROCESS_LAUNCH":
                    raise CrashInjected("BEFORE_PROCESS_LAUNCH")

                outcome, exit_code, stdout_raw, stderr_raw = self._run_process(
                    executable,
                    list(manifest["argv"]),
                    workspace,
                    dict(manifest["environment"]),
                    float(tool_contract["timeout_seconds"]),
                )
                max_bytes = int(tool_contract["max_output_bytes"])
                stdout, stdout_truncated = _bounded_decode(stdout_raw, max_bytes)
                stderr, stderr_truncated = _bounded_decode(stderr_raw, max_bytes)
                if outcome == "TIMED_OUT":
                    state = "TIMED_OUT"
                    success = False
                elif exit_code == 0:
                    state = "EXECUTED"
                    success = True
                else:
                    state = "FAILED_PROCESS"
                    success = False

                evidence = {
                    "slice3_result_hash": slice3_receipt["receipt_hash"],
                    "contract_hash": tool_contract["contract_hash"],
                    "manifest_hash": manifest["manifest_hash"],
                    "binding_hash": binding_hash,
                    "tool_execution_id": manifest["tool_execution_id"],
                    "execution_id": manifest["execution_id"],
                    "tool_id": manifest["tool_id"],
                    "executable": executable,
                    "argv_hash": canonical_hash(manifest["argv"]),
                    "workspace_hash": canonical_hash(str(workspace)),
                    "input_digest": manifest["input_digest"],
                    "environment_hash": canonical_hash(manifest["environment"]),
                    "process_outcome": outcome if outcome == "TIMED_OUT" else ("EXIT_ZERO" if exit_code == 0 else "EXIT_NONZERO"),
                    "exit_code": exit_code,
                    "stdout_sha256": _sha256_bytes(stdout_raw),
                    "stderr_sha256": _sha256_bytes(stderr_raw),
                    "stdout_bytes": len(stdout_raw),
                    "stderr_bytes": len(stderr_raw),
                    "stdout_truncated": stdout_truncated,
                    "stderr_truncated": stderr_truncated,
                    "replay_disposition": "FIRST_EXECUTION",
                    "terminal_authority": False,
                    "release_completion_authority": False,
                }
                durable = {
                    "state": state,
                    "success": success,
                    "tool_execution_id": manifest["tool_execution_id"],
                    "execution_id": manifest["execution_id"],
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "terminal_authority": False,
                    "release_completion_authority": False,
                }
                hash_material = deepcopy(durable)
                hash_material.pop("state", None)
                durable["result_hash"] = canonical_hash(hash_material)
                conn.execute(
                    "UPDATE tool_runs SET status='COMMITTED', result_json=?, evidence_json=? WHERE idempotency_key=?",
                    (_json(durable), _json(evidence), idempotency_key),
                )
                conn.commit()

                if crash_point == "AFTER_PROCESS_RESULT_BEFORE_RESPONSE":
                    raise CrashInjected("AFTER_PROCESS_RESULT_BEFORE_RESPONSE")

                conn.execute("UPDATE tool_runs SET status='ACKED' WHERE idempotency_key=?", (idempotency_key,))
                conn.commit()
                return durable

    def get_evidence(self, idempotency_key: str) -> dict[str, Any] | None:
        with self._lock:
            with self._connect() as conn:
                row = self._load(conn, idempotency_key)
                if row is None or row["status"] not in {"COMMITTED", "ACKED"}:
                    return None
                _, evidence = self._deserialize_row(row)
                return deepcopy(evidence) if evidence is not None else None
