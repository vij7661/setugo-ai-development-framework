"""Integrated Governed MVP Slice 7 reference terminal executor.

Consumes an exact Slice 6 terminal-authorization receipt and executes only a
local deterministic adapter. No remote merge/release/deploy/completion occurs.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Callable, Mapping


TERMINAL_ACTIONS = frozenset({"RELEASE", "DEPLOY", "MERGE", "COMPLETE"})
SUCCESS_STATES = frozenset({"TERMINAL_EXECUTION_COMPLETED", "TERMINAL_EXECUTION_REPLAYED", "TERMINAL_EXECUTION_RECOVERED"})


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _receipt_valid(receipt: Mapping[str, Any]) -> bool:
    if not isinstance(receipt, Mapping):
        return False
    supplied = receipt.get("receipt_hash")
    if not isinstance(supplied, str) or not supplied:
        return False
    material = deepcopy(dict(receipt))
    material.pop("receipt_hash", None)
    if canonical_hash(material) != supplied:
        return False
    return (
        receipt.get("state") == "AUTHORIZED_FOR_TERMINAL_ACTION"
        and receipt.get("authorized") is True
        and receipt.get("terminal_authority") is True
        and receipt.get("release_completion_authority") is True
        and receipt.get("actual_side_effect_performed") is False
        and isinstance(receipt.get("bound_lineage"), Mapping)
    )


def _request_valid(request: Mapping[str, Any]) -> bool:
    if not isinstance(request, Mapping):
        return False
    for field in ("terminal_execution_id", "project_id", "task_id", "effect_id", "artifact_sha"):
        if not isinstance(request.get(field), str) or not request.get(field):
            return False
    version = request.get("expected_state_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 0:
        return False
    return request.get("action") in TERMINAL_ACTIONS and isinstance(request.get("authorization_receipt"), Mapping)


def _current_state_valid(current_state: Mapping[str, Any]) -> bool:
    if not isinstance(current_state, Mapping):
        return False
    if not isinstance(current_state.get("project_id"), str) or not current_state.get("project_id"):
        return False
    if not isinstance(current_state.get("artifact_sha"), str) or not current_state.get("artifact_sha"):
        return False
    version = current_state.get("state_version")
    return isinstance(version, int) and not isinstance(version, bool) and version >= 0


def _binding(request: Mapping[str, Any]) -> dict[str, Any]:
    receipt = request.get("authorization_receipt") or {}
    return {
        "terminal_execution_id": request.get("terminal_execution_id"),
        "project_id": request.get("project_id"),
        "task_id": request.get("task_id"),
        "effect_id": request.get("effect_id"),
        "action": request.get("action"),
        "artifact_sha": request.get("artifact_sha"),
        "state_version": request.get("expected_state_version"),
        "authorization_receipt_hash": receipt.get("receipt_hash"),
    }


def _binding_matches_receipt(request: Mapping[str, Any], receipt: Mapping[str, Any]) -> bool:
    lineage = receipt.get("bound_lineage") or {}
    return (
        lineage.get("project_id") == request.get("project_id")
        and lineage.get("task_id") == request.get("task_id")
        and lineage.get("effect_id") == request.get("effect_id")
        and lineage.get("action") == request.get("action")
        and lineage.get("artifact_sha") == request.get("artifact_sha")
        and lineage.get("state_version") == request.get("expected_state_version")
    )


def _result(state: str, reason: str, request: Mapping[str, Any], completion: Mapping[str, Any] | None = None) -> dict[str, Any]:
    body = {
        "state": state,
        "reason": reason,
        "successful_completion": state in SUCCESS_STATES,
        "production_side_effect_claimed": False,
        "bound_execution": _binding(request),
        "completion_evidence": deepcopy(dict(completion)) if completion else None,
    }
    return {**body, "result_hash": canonical_hash(body)}


def _completion_evidence(request: Mapping[str, Any], adapter_result: Mapping[str, Any]) -> dict[str, Any]:
    body = {
        **_binding(request),
        "adapter_result_digest": canonical_hash(adapter_result),
        "adapter_result": deepcopy(dict(adapter_result)),
        "production_side_effect_claimed": False,
    }
    return {**body, "completion_hash": canonical_hash(body)}


class SimulatedExecutorCrash(RuntimeError):
    pass


class TerminalExecutor:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS terminal_executions (
                    terminal_execution_id TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    completion_json TEXT,
                    failure_reason TEXT,
                    response_delivered INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def execute(
        self,
        *,
        terminal_request: Mapping[str, Any],
        current_state: Mapping[str, Any],
        adapter: Callable[[Mapping[str, Any]], Mapping[str, Any]],
        crash_point: str | None = None,
    ) -> dict[str, Any]:
        if not _request_valid(terminal_request):
            return _result("DENY_BINDING", "terminal execution request is malformed", terminal_request)

        receipt = terminal_request["authorization_receipt"]
        if not _receipt_valid(receipt):
            return _result("DENY_AUTHORIZATION_RECEIPT", "Slice 6 authorization receipt is missing, malformed, non-authorized, or tampered", terminal_request)

        if not _binding_matches_receipt(terminal_request, receipt):
            return _result("DENY_BINDING", "terminal execution request does not equal the Slice 6 receipt binding", terminal_request)

        if not _current_state_valid(current_state):
            return _result("DENY_CURRENT_STATE", "current authoritative state is malformed", terminal_request)

        if (
            current_state.get("project_id") != terminal_request.get("project_id")
            or current_state.get("state_version") != terminal_request.get("expected_state_version")
            or current_state.get("artifact_sha") != terminal_request.get("artifact_sha")
        ):
            return _result("DENY_CURRENT_STATE", "project, state version, or artifact no longer matches current authoritative state", terminal_request)

        binding = _binding(terminal_request)
        binding_hash = canonical_hash(binding)
        execution_id = terminal_request["terminal_execution_id"]

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM terminal_executions WHERE terminal_execution_id = ?",
                (execution_id,),
            ).fetchone()

            if row is not None:
                if row["binding_hash"] != binding_hash:
                    conn.rollback()
                    return _result("DENY_IDEMPOTENCY_REBIND", "terminal execution identity is already bound to different inputs", terminal_request)

                if row["status"] == "COMPLETED":
                    completion = json.loads(row["completion_json"])
                    if row["response_delivered"]:
                        conn.rollback()
                        return _result("TERMINAL_EXECUTION_REPLAYED", "exact execution already completed", terminal_request, completion)
                    conn.execute(
                        "UPDATE terminal_executions SET response_delivered = 1 WHERE terminal_execution_id = ?",
                        (execution_id,),
                    )
                    conn.commit()
                    return _result("TERMINAL_EXECUTION_RECOVERED", "recovered durable completion after interrupted response", terminal_request, completion)

                if row["status"] == "FAILED":
                    reason = row["failure_reason"] or "prior adapter execution failed"
                    conn.rollback()
                    return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request)

            else:
                conn.execute(
                    "INSERT INTO terminal_executions(terminal_execution_id,binding_hash,status) VALUES(?,?,?)",
                    (execution_id, binding_hash, "IN_PROGRESS"),
                )

            if crash_point == "before_adapter":
                conn.rollback()
                raise SimulatedExecutorCrash("simulated crash before terminal adapter invocation")

            try:
                adapter_result = adapter(deepcopy(binding))
                if not isinstance(adapter_result, Mapping):
                    raise ValueError("adapter returned non-mapping result")
            except Exception as exc:  # bounded reference adapter failure
                reason = f"terminal adapter failed: {type(exc).__name__}: {exc}"
                conn.execute(
                    "UPDATE terminal_executions SET status='FAILED', failure_reason=? WHERE terminal_execution_id=?",
                    (reason, execution_id),
                )
                conn.commit()
                return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request)

            for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version"):
                if field in adapter_result and adapter_result.get(field) != binding.get(field):
                    reason = f"terminal adapter attempted to widen bound field: {field}"
                    conn.execute(
                        "UPDATE terminal_executions SET status='FAILED', failure_reason=? WHERE terminal_execution_id=?",
                        (reason, execution_id),
                    )
                    conn.commit()
                    return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request)

            completion = _completion_evidence(terminal_request, adapter_result)
            conn.execute(
                "UPDATE terminal_executions SET status='COMPLETED', completion_json=?, response_delivered=0 WHERE terminal_execution_id=?",
                (json.dumps(completion, sort_keys=True, separators=(",", ":")), execution_id),
            )
            conn.commit()

            if crash_point == "after_durable_execution":
                raise SimulatedExecutorCrash("simulated crash after durable terminal execution before response")

            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE terminal_executions SET response_delivered=1 WHERE terminal_execution_id=?",
                (execution_id,),
            )
            conn.commit()
            return _result("TERMINAL_EXECUTION_COMPLETED", "exact authorized reference terminal action completed", terminal_request, completion)
        finally:
            conn.close()
