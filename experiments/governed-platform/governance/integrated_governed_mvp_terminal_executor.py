"""Integrated Governed MVP Slice 7 reference terminal executor.

Consumes an exact Slice 6 terminal-authorization receipt, revalidates current
external terminal authority at use time, and executes only through a durable
idempotent local reference adapter protocol. No remote production side effect
is implemented by this reference slice.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping


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
        and isinstance(receipt.get("authority_id"), str)
        and bool(receipt.get("authority_id"))
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


def _authority_material_valid(authority: Mapping[str, Any]) -> bool:
    if not isinstance(authority, Mapping):
        return False
    supplied = authority.get("authority_snapshot_hash")
    if not isinstance(supplied, str) or not supplied:
        return False
    material = deepcopy(dict(authority))
    material.pop("authority_snapshot_hash", None)
    if canonical_hash(material) != supplied:
        return False
    for field in ("authority_id", "project_id", "task_id", "effect_id", "artifact_sha"):
        if not isinstance(authority.get(field), str) or not authority.get(field):
            return False
    if authority.get("action") not in TERMINAL_ACTIONS:
        return False
    if authority.get("status") not in {"ACTIVE", "REVOKED"}:
        return False
    version = authority.get("state_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 0:
        return False
    for field in ("not_before_epoch", "expires_at_epoch"):
        value = authority.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
    return authority["not_before_epoch"] < authority["expires_at_epoch"]


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


def _authority_current(
    authority: Mapping[str, Any],
    *,
    now_epoch: int | float,
    request: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> bool:
    if not _authority_material_valid(authority):
        return False
    if not isinstance(now_epoch, (int, float)) or isinstance(now_epoch, bool):
        return False
    if authority.get("status") != "ACTIVE":
        return False
    if not (authority["not_before_epoch"] <= now_epoch < authority["expires_at_epoch"]):
        return False
    return (
        authority.get("authority_id") == receipt.get("authority_id")
        and authority.get("project_id") == request.get("project_id")
        and authority.get("task_id") == request.get("task_id")
        and authority.get("effect_id") == request.get("effect_id")
        and authority.get("action") == request.get("action")
        and authority.get("artifact_sha") == request.get("artifact_sha")
        and authority.get("state_version") == request.get("expected_state_version")
    )


def _adapter_protocol_valid(adapter: Any) -> bool:
    return callable(getattr(adapter, "recover", None)) and callable(getattr(adapter, "execute_once", None))


def _binding(request: Mapping[str, Any], current_authority: Mapping[str, Any] | None = None) -> dict[str, Any]:
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
        "authority_snapshot_hash": (current_authority or {}).get("authority_snapshot_hash"),
    }


def _result(
    state: str,
    reason: str,
    request: Mapping[str, Any],
    current_authority: Mapping[str, Any] | None = None,
    completion: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "state": state,
        "reason": reason,
        "successful_completion": state in SUCCESS_STATES,
        "production_side_effect_claimed": False,
        "bound_execution": _binding(request, current_authority),
        "completion_evidence": deepcopy(dict(completion)) if completion else None,
    }
    return {**body, "result_hash": canonical_hash(body)}


def _completion_evidence(
    request: Mapping[str, Any],
    current_authority: Mapping[str, Any],
    adapter_result: Mapping[str, Any],
) -> dict[str, Any]:
    body = {
        **_binding(request, current_authority),
        "adapter_result_digest": canonical_hash(adapter_result),
        "adapter_result": deepcopy(dict(adapter_result)),
        "production_side_effect_claimed": False,
    }
    return {**body, "completion_hash": canonical_hash(body)}


def _adapter_result_valid(adapter_result: Mapping[str, Any], binding: Mapping[str, Any]) -> bool:
    if not isinstance(adapter_result, Mapping):
        return False
    for field in ("project_id", "task_id", "effect_id", "action", "artifact_sha", "state_version"):
        if field in adapter_result and adapter_result.get(field) != binding.get(field):
            return False
    return True


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

    def _persist_completion(
        self,
        execution_id: str,
        completion: Mapping[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE terminal_executions SET status='COMPLETED', completion_json=?, failure_reason=NULL, response_delivered=0 WHERE terminal_execution_id=?",
                (json.dumps(completion, sort_keys=True, separators=(",", ":")), execution_id),
            )
            conn.commit()

    def _mark_failed(self, execution_id: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE terminal_executions SET status='FAILED', failure_reason=? WHERE terminal_execution_id=?",
                (reason, execution_id),
            )
            conn.commit()

    def execute(
        self,
        *,
        terminal_request: Mapping[str, Any],
        current_state: Mapping[str, Any],
        current_authority: Mapping[str, Any],
        now_epoch: int | float,
        adapter: Any,
        crash_point: str | None = None,
    ) -> dict[str, Any]:
        if not _request_valid(terminal_request):
            return _result("DENY_BINDING", "terminal execution request is malformed", terminal_request, current_authority)

        receipt = terminal_request["authorization_receipt"]
        if not _receipt_valid(receipt):
            return _result("DENY_AUTHORIZATION_RECEIPT", "Slice 6 authorization receipt is missing, malformed, non-authorized, or tampered", terminal_request, current_authority)

        if not _binding_matches_receipt(terminal_request, receipt):
            return _result("DENY_BINDING", "terminal execution request does not equal the Slice 6 receipt binding", terminal_request, current_authority)

        if not _current_state_valid(current_state):
            return _result("DENY_CURRENT_STATE", "current authoritative state is malformed", terminal_request, current_authority)

        if (
            current_state.get("project_id") != terminal_request.get("project_id")
            or current_state.get("state_version") != terminal_request.get("expected_state_version")
            or current_state.get("artifact_sha") != terminal_request.get("artifact_sha")
        ):
            return _result("DENY_CURRENT_STATE", "project, state version, or artifact no longer matches current authoritative state", terminal_request, current_authority)

        if not _authority_current(
            current_authority,
            now_epoch=now_epoch,
            request=terminal_request,
            receipt=receipt,
        ):
            return _result(
                "DENY_AUTHORITY_FRESHNESS",
                "current terminal authority is malformed, revoked, not current, expired, replaced, or lineage-mismatched",
                terminal_request,
                current_authority,
            )

        if not _adapter_protocol_valid(adapter):
            return _result(
                "TERMINAL_EXECUTION_FAILED",
                "terminal adapter does not implement durable recover/execute_once protocol",
                terminal_request,
                current_authority,
            )

        binding = _binding(terminal_request, current_authority)
        binding_hash = canonical_hash(binding)
        execution_id = terminal_request["terminal_execution_id"]

        # First persist the exact execution intent locally. This record is not a
        # completion claim; it exists so restart/retry can distinguish an
        # interrupted attempt from a new/rebound identity.
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM terminal_executions WHERE terminal_execution_id = ?",
                (execution_id,),
            ).fetchone()

            if row is not None:
                if row["binding_hash"] != binding_hash:
                    conn.rollback()
                    return _result("DENY_IDEMPOTENCY_REBIND", "terminal execution identity is already bound to different inputs", terminal_request, current_authority)

                if row["status"] == "COMPLETED":
                    completion = json.loads(row["completion_json"])
                    if row["response_delivered"]:
                        conn.rollback()
                        return _result("TERMINAL_EXECUTION_REPLAYED", "exact execution already completed", terminal_request, current_authority, completion)
                    conn.execute(
                        "UPDATE terminal_executions SET response_delivered = 1 WHERE terminal_execution_id = ?",
                        (execution_id,),
                    )
                    conn.commit()
                    return _result("TERMINAL_EXECUTION_RECOVERED", "recovered durable completion after interrupted response", terminal_request, current_authority, completion)
            else:
                conn.execute(
                    "INSERT INTO terminal_executions(terminal_execution_id,binding_hash,status) VALUES(?,?,?)",
                    (execution_id, binding_hash, "IN_PROGRESS"),
                )
            conn.commit()

        if crash_point == "before_adapter":
            raise SimulatedExecutorCrash("simulated crash before terminal adapter invocation")

        # The adapter is a separately durable idempotency boundary. Recovery is
        # checked before every execute_once call, including after process restart.
        try:
            recovered = adapter.recover(execution_id, binding_hash)
        except Exception as exc:
            reason = f"terminal adapter recovery failed: {type(exc).__name__}: {exc}"
            self._mark_failed(execution_id, reason)
            return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request, current_authority)

        recovered_from_adapter = recovered is not None
        if recovered_from_adapter:
            adapter_result = recovered
        else:
            try:
                adapter_result = adapter.execute_once(execution_id, binding_hash, deepcopy(binding))
            except Exception as exc:
                # A durable adapter can have committed its side effect before its
                # response path failed. Check recovery once before declaring failure.
                try:
                    recovered_after_error = adapter.recover(execution_id, binding_hash)
                except Exception:
                    recovered_after_error = None
                if recovered_after_error is None:
                    reason = f"terminal adapter failed: {type(exc).__name__}: {exc}"
                    self._mark_failed(execution_id, reason)
                    return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request, current_authority)
                adapter_result = recovered_after_error
                recovered_from_adapter = True

        if not _adapter_result_valid(adapter_result, binding):
            reason = "terminal adapter returned malformed or widened bound fields"
            self._mark_failed(execution_id, reason)
            return _result("TERMINAL_EXECUTION_FAILED", reason, terminal_request, current_authority)

        if crash_point == "after_adapter_before_completion" and not recovered_from_adapter:
            raise SimulatedExecutorCrash("simulated crash after durable adapter side effect before local completion commit")

        completion = _completion_evidence(terminal_request, current_authority, adapter_result)
        self._persist_completion(execution_id, completion)

        if crash_point == "after_durable_execution":
            raise SimulatedExecutorCrash("simulated crash after durable local terminal completion before response")

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE terminal_executions SET response_delivered=1 WHERE terminal_execution_id=?",
                (execution_id,),
            )
            conn.commit()

        state = "TERMINAL_EXECUTION_RECOVERED" if recovered_from_adapter else "TERMINAL_EXECUTION_COMPLETED"
        reason = (
            "recovered durable adapter result and completed local terminal evidence"
            if recovered_from_adapter
            else "exact authorized reference terminal action completed"
        )
        return _result(state, reason, terminal_request, current_authority, completion)
