"""Durable execution gateway for Integrated Governed MVP Slice 2.

This layer consumes an exact Slice 1 authorization envelope, revalidates current
state before any new effect, durably binds one semantic intent to one effect,
and preserves replay/recovery evidence. It deliberately has no release,
completion, deploy, merge, or other terminal authority.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
import sqlite3
import threading
from typing import Any, Callable, Mapping

from integrated_governed_mvp import evaluate_governed_execution


class CrashInjected(RuntimeError):
    """Controlled crash point used only by the frozen Slice 2 acceptance harness."""


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ExecutionGateway:
    """SQLite-backed, fail-closed gateway for one isolated deterministic effect."""

    _locks_guard = threading.Lock()
    _locks: dict[str, threading.RLock] = {}

    _IMMUTABLE_CAPABILITY_FIELDS = (
        "capability_id",
        "project_id",
        "task_id",
        "subject_id",
        "issued_epoch",
        "allowed_actions",
        "artifact_classes",
    )

    def __init__(self, db_path: str, worker: Callable[[Mapping[str, Any]], Mapping[str, Any]]):
        self.db_path = os.path.abspath(db_path)
        self.worker = worker
        with self._locks_guard:
            self._lock = self._locks.setdefault(self.db_path, threading.RLock())
        with self._lock:
            self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _initialize(self) -> None:
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS gateway_ledger (
                    idempotency_key TEXT PRIMARY KEY,
                    binding_hash TEXT NOT NULL,
                    upstream_decision_hash TEXT NOT NULL,
                    effect_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    result_json TEXT,
                    result_hash TEXT,
                    evidence_json TEXT,
                    row_hash TEXT NOT NULL
                )
                """
            )
            connection.commit()

    @staticmethod
    def _deny(state: str, reason: str) -> dict[str, Any]:
        return {
            "state": state,
            "reason": reason,
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    @classmethod
    def _capability_lineage(cls, capability: Mapping[str, Any]) -> dict[str, Any]:
        return {field: deepcopy(capability.get(field)) for field in cls._IMMUTABLE_CAPABILITY_FIELDS}

    @classmethod
    def _capability_binding_matches(
        cls,
        upstream_capability: Mapping[str, Any],
        current_capability: Mapping[str, Any],
    ) -> bool:
        return cls._capability_lineage(upstream_capability) == cls._capability_lineage(current_capability)

    @staticmethod
    def _row_payload(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "idempotency_key": row["idempotency_key"],
            "binding_hash": row["binding_hash"],
            "upstream_decision_hash": row["upstream_decision_hash"],
            "effect_id": row["effect_id"],
            "status": row["status"],
            "result_json": row["result_json"],
            "result_hash": row["result_hash"],
            "evidence_json": row["evidence_json"],
        }

    @classmethod
    def _row_hash(cls, row: Mapping[str, Any]) -> str:
        return canonical_hash(cls._row_payload(row))

    @classmethod
    def _row_is_valid(cls, row: Mapping[str, Any]) -> bool:
        try:
            if row["status"] not in {"PENDING", "COMMITTED", "ACKED"}:
                return False
            if not all(isinstance(row[field], str) and row[field] for field in (
                "idempotency_key", "binding_hash", "upstream_decision_hash", "effect_id", "row_hash"
            )):
                return False
            if row["row_hash"] != cls._row_hash(row):
                return False
            if row["status"] == "PENDING":
                return row["result_json"] is None and row["result_hash"] is None and row["evidence_json"] is None
            if not all(isinstance(row[field], str) and row[field] for field in (
                "result_json", "result_hash", "evidence_json"
            )):
                return False
            result = json.loads(row["result_json"])
            evidence = json.loads(row["evidence_json"])
            if canonical_hash(result) != row["result_hash"]:
                return False
            if not isinstance(evidence, dict):
                return False
            if evidence.get("effect_id") != row["effect_id"]:
                return False
            if evidence.get("result_hash") != row["result_hash"]:
                return False
            if evidence.get("upstream_decision_hash") != row["upstream_decision_hash"]:
                return False
            if evidence.get("request_effect_binding_hash") != row["binding_hash"]:
                return False
            return True
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return False

    @staticmethod
    def _load_row(connection: sqlite3.Connection, idempotency_key: str) -> sqlite3.Row | None:
        return connection.execute(
            "SELECT * FROM gateway_ledger WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()

    @staticmethod
    def _semantic_binding(
        *,
        upstream_decision_hash: str,
        execution_request: Mapping[str, Any],
        artifact_binding: Mapping[str, Any],
        capability_lineage: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "upstream_decision_hash": upstream_decision_hash,
            "execution_request": deepcopy(dict(execution_request)),
            "artifact_binding": deepcopy(dict(artifact_binding)),
            "capability_lineage": deepcopy(dict(capability_lineage)),
        }

    @staticmethod
    def _successful_response(state: str, row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "state": state,
            "effect_id": row["effect_id"],
            "result": json.loads(row["result_json"]),
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    def _verify_upstream(self, upstream: Mapping[str, Any]) -> tuple[bool, str]:
        try:
            decision = upstream["decision"]
            supplied_hash = upstream["decision_hash"]
            if not isinstance(decision, Mapping) or not isinstance(supplied_hash, str):
                return False, "upstream decision envelope is malformed"
            if canonical_hash(decision) != supplied_hash:
                return False, "upstream decision hash does not match decision"
            recomputed = evaluate_governed_execution(
                route=upstream["route"],
                registry_entry=upstream["registry_entry"],
                normalized_model_result=upstream["normalized_model_result"],
                capability=upstream["capability"],
                execution_request=upstream["execution_request"],
                review_gate=upstream["review_gate"],
                now_epoch=upstream["decision_now_epoch"],
                now_iso=upstream["decision_now_iso"],
            )
            if recomputed != decision:
                return False, "upstream decision does not recompute from its bound inputs"
            return True, "upstream decision integrity verified"
        except (KeyError, TypeError, ValueError):
            return False, "upstream decision envelope is malformed"

    def _fresh_current_authorized(
        self,
        *,
        upstream: Mapping[str, Any],
        current_registry_entry: Mapping[str, Any],
        current_capability: Mapping[str, Any],
        execution_request: Mapping[str, Any],
        now_epoch: int,
        now_iso: str,
    ) -> bool:
        try:
            decision = evaluate_governed_execution(
                route=upstream["route"],
                registry_entry=current_registry_entry,
                normalized_model_result=upstream["normalized_model_result"],
                capability=current_capability,
                execution_request=execution_request,
                review_gate=upstream["review_gate"],
                now_epoch=now_epoch,
                now_iso=now_iso,
            )
        except (KeyError, TypeError, ValueError):
            return False
        return decision.get("decision") == "AUTHORIZED_FOR_ISOLATED_EXECUTION" and bool(
            decision.get("consequential_execution_authorized", False)
        )

    def execute(
        self,
        *,
        upstream: Mapping[str, Any],
        current_registry_entry: Mapping[str, Any],
        current_capability: Mapping[str, Any],
        execution_request: Mapping[str, Any],
        current_artifact_binding: Mapping[str, Any],
        idempotency_key: str,
        now_epoch: int,
        now_iso: str,
        crash_at: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(idempotency_key, str) or not idempotency_key:
            return self._deny("DENIED_BINDING", "idempotency key is missing")

        upstream_ok, upstream_reason = self._verify_upstream(upstream)
        if not upstream_ok:
            return self._deny("DENIED_UPSTREAM_INTEGRITY", upstream_reason)

        decision = upstream.get("decision", {})
        if decision.get("decision") != "AUTHORIZED_FOR_ISOLATED_EXECUTION" or not decision.get(
            "consequential_execution_authorized", False
        ):
            return self._deny("DENIED_UPSTREAM", "upstream decision does not authorize isolated execution")

        try:
            upstream_request = upstream["execution_request"]
            upstream_artifact = upstream["artifact_binding"]
            upstream_capability = upstream["capability"]
            upstream_decision_hash = upstream["decision_hash"]
        except KeyError:
            return self._deny("DENIED_UPSTREAM_INTEGRITY", "upstream binding material is incomplete")

        capability_lineage = self._capability_lineage(current_capability)
        binding_material = self._semantic_binding(
            upstream_decision_hash=upstream_decision_hash,
            execution_request=execution_request,
            artifact_binding=current_artifact_binding,
            capability_lineage=capability_lineage,
        )
        binding_hash = canonical_hash(binding_material)

        with self._lock:
            with self._connect() as connection:
                row = self._load_row(connection, idempotency_key)

                # Once an idempotency key has a durable semantic identity, semantic
                # rebinding dominates later generic binding/current-state errors.
                if row is not None:
                    if not self._row_is_valid(row):
                        return self._deny(
                            "BLOCKED_AMBIGUOUS_DURABLE_STATE",
                            "durable execution ledger is malformed or internally conflicting",
                        )
                    if row["binding_hash"] != binding_hash:
                        return self._deny(
                            "DENIED_IDEMPOTENCY_REBIND",
                            "idempotency key is already bound to different execution semantics",
                        )

                if dict(execution_request) != dict(upstream_request):
                    return self._deny("DENIED_BINDING", "execution request differs from upstream binding")
                if dict(current_artifact_binding) != dict(upstream_artifact):
                    return self._deny("DENIED_BINDING", "artifact binding differs from upstream binding")
                if not self._capability_binding_matches(upstream_capability, current_capability):
                    return self._deny("DENIED_BINDING", "capability lineage differs from upstream binding")

                # A committed or acknowledged effect is historical fact. Exact replay
                # returns that durable result and never re-executes the worker.
                if row is not None and row["status"] in {"COMMITTED", "ACKED"}:
                    replay_state = "RECOVERED_REPLAY" if row["status"] == "COMMITTED" else "REPLAYED"
                    if row["status"] == "COMMITTED":
                        evidence = json.loads(row["evidence_json"])
                        evidence["disposition"] = replay_state
                        updated = dict(row)
                        updated["status"] = "ACKED"
                        updated["evidence_json"] = json.dumps(
                            evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                        )
                        updated["row_hash"] = self._row_hash(updated)
                        connection.execute(
                            "UPDATE gateway_ledger SET status = ?, evidence_json = ?, row_hash = ? WHERE idempotency_key = ?",
                            (updated["status"], updated["evidence_json"], updated["row_hash"], idempotency_key),
                        )
                        connection.commit()
                        row = self._load_row(connection, idempotency_key)
                    return self._successful_response(replay_state, row)

                if not self._fresh_current_authorized(
                    upstream=upstream,
                    current_registry_entry=current_registry_entry,
                    current_capability=current_capability,
                    execution_request=execution_request,
                    now_epoch=now_epoch,
                    now_iso=now_iso,
                ):
                    return self._deny(
                        "DENIED_CURRENT_STATE",
                        "fresh use-time qualification, capability, scope, or review state is not authorized",
                    )

                recovered_pending = row is not None and row["status"] == "PENDING"
                effect_id = (
                    row["effect_id"]
                    if recovered_pending
                    else "eff-" + canonical_hash({"idempotency_key": idempotency_key, "binding_hash": binding_hash})[:32]
                )

                if row is None:
                    pending = {
                        "idempotency_key": idempotency_key,
                        "binding_hash": binding_hash,
                        "upstream_decision_hash": upstream_decision_hash,
                        "effect_id": effect_id,
                        "status": "PENDING",
                        "result_json": None,
                        "result_hash": None,
                        "evidence_json": None,
                    }
                    pending["row_hash"] = self._row_hash(pending)
                    connection.execute(
                        """
                        INSERT INTO gateway_ledger (
                            idempotency_key, binding_hash, upstream_decision_hash, effect_id,
                            status, result_json, result_hash, evidence_json, row_hash
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            pending["idempotency_key"], pending["binding_hash"], pending["upstream_decision_hash"],
                            pending["effect_id"], pending["status"], pending["result_json"], pending["result_hash"],
                            pending["evidence_json"], pending["row_hash"],
                        ),
                    )
                    connection.commit()

                if crash_at == "BEFORE_EFFECT_COMMIT":
                    raise CrashInjected("injected before effect commit")

                effect_request = {
                    "effect_id": effect_id,
                    "idempotency_key": idempotency_key,
                    "upstream_decision_hash": upstream_decision_hash,
                    "execution_request": deepcopy(dict(execution_request)),
                    "artifact_binding": deepcopy(dict(current_artifact_binding)),
                    "capability_lineage": deepcopy(capability_lineage),
                    "request_effect_binding_hash": binding_hash,
                }
                result = deepcopy(dict(self.worker(effect_request)))
                result_json = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                result_hash = canonical_hash(result)
                disposition = "RECOVERED_AND_EXECUTED" if recovered_pending else "EXECUTED"
                evidence = {
                    "upstream_decision_hash": upstream_decision_hash,
                    "capability_lineage": deepcopy(capability_lineage),
                    "effect_id": effect_id,
                    "result_hash": result_hash,
                    "request_effect_binding_hash": binding_hash,
                    "disposition": disposition,
                    "terminal_authority": False,
                    "release_completion_authority": False,
                }
                evidence_json = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                committed = {
                    "idempotency_key": idempotency_key,
                    "binding_hash": binding_hash,
                    "upstream_decision_hash": upstream_decision_hash,
                    "effect_id": effect_id,
                    "status": "COMMITTED",
                    "result_json": result_json,
                    "result_hash": result_hash,
                    "evidence_json": evidence_json,
                }
                committed["row_hash"] = self._row_hash(committed)
                connection.execute(
                    """
                    UPDATE gateway_ledger
                    SET status = ?, result_json = ?, result_hash = ?, evidence_json = ?, row_hash = ?
                    WHERE idempotency_key = ?
                    """,
                    (
                        committed["status"], committed["result_json"], committed["result_hash"],
                        committed["evidence_json"], committed["row_hash"], idempotency_key,
                    ),
                )
                connection.commit()

                if crash_at == "AFTER_EFFECT_COMMIT_BEFORE_RESPONSE":
                    raise CrashInjected("injected after durable effect commit before response")

                evidence["disposition"] = disposition
                acknowledged = dict(committed)
                acknowledged["status"] = "ACKED"
                acknowledged["evidence_json"] = json.dumps(
                    evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                )
                acknowledged["row_hash"] = self._row_hash(acknowledged)
                connection.execute(
                    "UPDATE gateway_ledger SET status = ?, evidence_json = ?, row_hash = ? WHERE idempotency_key = ?",
                    (acknowledged["status"], acknowledged["evidence_json"], acknowledged["row_hash"], idempotency_key),
                )
                connection.commit()
                row = self._load_row(connection, idempotency_key)
                return self._successful_response(disposition, row)

    def effect_count(self) -> int:
        with self._lock:
            with self._connect() as connection:
                return int(
                    connection.execute(
                        "SELECT COUNT(*) FROM gateway_ledger WHERE result_json IS NOT NULL"
                    ).fetchone()[0]
                )

    def list_effect_ids(self) -> list[str]:
        with self._lock:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT effect_id FROM gateway_ledger WHERE result_json IS NOT NULL ORDER BY effect_id"
                ).fetchall()
                return [str(row[0]) for row in rows]

    def get_evidence(self, idempotency_key: str) -> dict[str, Any]:
        with self._lock:
            with self._connect() as connection:
                row = self._load_row(connection, idempotency_key)
                if row is None or not self._row_is_valid(row) or row["evidence_json"] is None:
                    return {}
                return json.loads(row["evidence_json"])

    def request_terminal_action(self, action: str, context: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "state": "TERMINAL_AUTHORITY_REQUIRED",
            "authorized": False,
            "action": action,
            "context": deepcopy(dict(context)),
            "terminal_authority": False,
            "release_completion_authority": False,
            "reason": "terminal action requires a separate external authority gate",
        }
