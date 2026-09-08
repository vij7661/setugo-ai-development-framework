from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


class LedgerError(RuntimeError):
    pass


class IdempotencyConflict(LedgerError):
    pass


class VersionConflict(LedgerError):
    pass


class AuthorityClaimRejected(LedgerError):
    pass


class CompletionConflict(LedgerError):
    pass


class InjectedFailure(LedgerError):
    pass


class SimulatedCrashAfterCommit(LedgerError):
    pass


@dataclass(frozen=True)
class TransitionResult:
    event_id: str
    project_id: str
    idempotency_key: str
    version: int
    state: dict[str, Any]
    result_digest: str
    outbox_id: str | None
    replayed: bool


class AuthoritativeStateLedger:
    """Single-database deterministic reference ledger for Slice 5.

    Authority is created only by apply_command's SQLite transaction.  Worker/model
    outputs are never accepted as state/version/completion authority inputs.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        return con

    def _initialize(self) -> None:
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS project_state(
                    project_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL CHECK(version >= 0),
                    state_json TEXT NOT NULL,
                    state_digest TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS accepted_events(
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    command_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    command_digest TEXT NOT NULL,
                    expected_version INTEGER NOT NULL,
                    prior_version INTEGER NOT NULL,
                    result_version INTEGER NOT NULL,
                    result_state_json TEXT NOT NULL,
                    result_digest TEXT NOT NULL,
                    UNIQUE(project_id, idempotency_key)
                );
                CREATE TABLE IF NOT EXISTS outbox(
                    outbox_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL UNIQUE REFERENCES accepted_events(event_id),
                    project_id TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    effect_payload_json TEXT NOT NULL,
                    effect_digest TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING','COMPLETED')),
                    completion_digest TEXT,
                    completion_attempts INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    @staticmethod
    def _event_id(project_id: str, idempotency_key: str) -> str:
        return "evt_" + hashlib.sha256(f"{project_id}\0{idempotency_key}".encode()).hexdigest()[:32]

    @staticmethod
    def _outbox_id(event_id: str) -> str:
        return "obx_" + hashlib.sha256(event_id.encode()).hexdigest()[:32]

    @staticmethod
    def _validate_text(value: str, label: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} required")
        return value

    @staticmethod
    def _apply_transition(current: dict[str, Any], command_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if command_type != "PATCH_STATE":
            raise ValueError("unsupported command_type")
        if not isinstance(payload, dict):
            raise ValueError("payload must be object")
        set_values = payload.get("set", {})
        delete_keys = payload.get("delete", [])
        if not isinstance(set_values, dict) or not isinstance(delete_keys, list):
            raise ValueError("PATCH_STATE requires object set and list delete")
        if any(not isinstance(k, str) or not k for k in set_values):
            raise ValueError("state keys must be nonempty strings")
        if any(not isinstance(k, str) or not k for k in delete_keys):
            raise ValueError("delete keys must be nonempty strings")
        nxt = json.loads(_canon(current))
        for key, value in set_values.items():
            nxt[key] = value
        for key in delete_keys:
            nxt.pop(key, None)
        return nxt

    def apply_command(
        self,
        *,
        project_id: str,
        idempotency_key: str,
        command_type: str,
        payload: dict[str, Any],
        expected_version: int,
        effect_type: str | None = None,
        effect_payload: dict[str, Any] | None = None,
        authority_claims: dict[str, Any] | None = None,
        fault: str | None = None,
    ) -> TransitionResult:
        self._validate_text(project_id, "project_id")
        self._validate_text(idempotency_key, "idempotency_key")
        self._validate_text(command_type, "command_type")
        if authority_claims:
            raise AuthorityClaimRejected("worker/model authority claims are not accepted")
        if not isinstance(expected_version, int) or expected_version < 0:
            raise ValueError("expected_version must be nonnegative integer")
        if effect_type is None and effect_payload is not None:
            raise ValueError("effect_type required when effect_payload supplied")
        if effect_type is not None:
            self._validate_text(effect_type, "effect_type")
            if effect_payload is None:
                effect_payload = {}
            if not isinstance(effect_payload, dict):
                raise ValueError("effect_payload must be object")

        command = {
            "project_id": project_id,
            "idempotency_key": idempotency_key,
            "command_type": command_type,
            "payload": payload,
            "expected_version": expected_version,
            "effect_type": effect_type,
            "effect_payload": effect_payload,
        }
        command_digest = _digest(command)
        event_id = self._event_id(project_id, idempotency_key)
        committed = False
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute(
                "SELECT * FROM accepted_events WHERE project_id=? AND idempotency_key=?",
                (project_id, idempotency_key),
            ).fetchone()
            if existing is not None:
                if existing["command_digest"] != command_digest:
                    raise IdempotencyConflict("idempotency key rebound to different intent")
                outbox = con.execute("SELECT outbox_id FROM outbox WHERE event_id=?", (existing["event_id"],)).fetchone()
                con.commit()
                committed = True
                return TransitionResult(
                    event_id=existing["event_id"],
                    project_id=project_id,
                    idempotency_key=idempotency_key,
                    version=existing["result_version"],
                    state=json.loads(existing["result_state_json"]),
                    result_digest=existing["result_digest"],
                    outbox_id=outbox["outbox_id"] if outbox else None,
                    replayed=True,
                )

            row = con.execute("SELECT version,state_json FROM project_state WHERE project_id=?", (project_id,)).fetchone()
            current_version = row["version"] if row else 0
            current_state = json.loads(row["state_json"]) if row else {}
            if current_version != expected_version:
                raise VersionConflict(f"expected version {expected_version}, authoritative version {current_version}")

            next_state = self._apply_transition(current_state, command_type, payload)
            next_version = current_version + 1
            state_json = _canon(next_state)
            state_digest = _digest({"project_id": project_id, "version": next_version, "state": next_state})
            result_digest = _digest(
                {
                    "event_id": event_id,
                    "command_digest": command_digest,
                    "prior_version": current_version,
                    "result_version": next_version,
                    "state_digest": state_digest,
                }
            )
            con.execute(
                "INSERT INTO accepted_events VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    event_id, project_id, idempotency_key, command_type, _canon(payload), command_digest,
                    expected_version, current_version, next_version, state_json, result_digest,
                ),
            )
            if fault == "after_event_insert":
                raise InjectedFailure(fault)

            if row:
                updated = con.execute(
                    "UPDATE project_state SET version=?,state_json=?,state_digest=? WHERE project_id=? AND version=?",
                    (next_version, state_json, state_digest, project_id, current_version),
                ).rowcount
                if updated != 1:
                    raise VersionConflict("authoritative state changed concurrently")
            else:
                con.execute(
                    "INSERT INTO project_state(project_id,version,state_json,state_digest) VALUES(?,?,?,?)",
                    (project_id, next_version, state_json, state_digest),
                )
            if fault == "after_state_update":
                raise InjectedFailure(fault)

            outbox_id = None
            if effect_type is not None:
                outbox_id = self._outbox_id(event_id)
                effect_record = {"effect_type": effect_type, "effect_payload": effect_payload}
                con.execute(
                    "INSERT INTO outbox(outbox_id,event_id,project_id,effect_type,effect_payload_json,effect_digest,status) VALUES(?,?,?,?,?,?, 'PENDING')",
                    (outbox_id, event_id, project_id, effect_type, _canon(effect_payload), _digest(effect_record)),
                )
            if fault == "after_outbox_insert":
                raise InjectedFailure(fault)

            con.commit()
            committed = True
            result = TransitionResult(
                event_id=event_id,
                project_id=project_id,
                idempotency_key=idempotency_key,
                version=next_version,
                state=next_state,
                result_digest=result_digest,
                outbox_id=outbox_id,
                replayed=False,
            )
            if fault == "after_commit":
                raise SimulatedCrashAfterCommit("simulated process death after durable commit")
            return result
        except Exception:
            if not committed:
                con.rollback()
            raise
        finally:
            con.close()

    def get_state(self, project_id: str) -> tuple[int, dict[str, Any]]:
        with self._connect() as con:
            row = con.execute("SELECT version,state_json FROM project_state WHERE project_id=?", (project_id,)).fetchone()
            return (row["version"], json.loads(row["state_json"])) if row else (0, {})

    def counts(self, project_id: str) -> dict[str, int]:
        with self._connect() as con:
            events = con.execute("SELECT COUNT(*) c FROM accepted_events WHERE project_id=?", (project_id,)).fetchone()["c"]
            outbox = con.execute("SELECT COUNT(*) c FROM outbox WHERE project_id=?", (project_id,)).fetchone()["c"]
            return {"events": events, "outbox": outbox}

    def pending_outbox(self, project_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as con:
            if project_id is None:
                rows = con.execute("SELECT * FROM outbox WHERE status='PENDING' ORDER BY outbox_id").fetchall()
            else:
                rows = con.execute("SELECT * FROM outbox WHERE status='PENDING' AND project_id=? ORDER BY outbox_id", (project_id,)).fetchall()
            return [dict(r) for r in rows]

    def complete_outbox(self, outbox_id: str, completion_evidence_digest: str, *, authority_claims: dict[str, Any] | None = None) -> bool:
        if authority_claims:
            raise AuthorityClaimRejected("worker/model completion claims are not authority")
        self._validate_text(outbox_id, "outbox_id")
        self._validate_text(completion_evidence_digest, "completion_evidence_digest")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT status,completion_digest FROM outbox WHERE outbox_id=?", (outbox_id,)).fetchone()
            if row is None:
                raise LedgerError("outbox item not found")
            if row["status"] == "COMPLETED":
                if row["completion_digest"] != completion_evidence_digest:
                    raise CompletionConflict("completion evidence rebound")
                con.commit()
                return False
            con.execute(
                "UPDATE outbox SET status='COMPLETED',completion_digest=?,completion_attempts=completion_attempts+1 WHERE outbox_id=? AND status='PENDING'",
                (completion_evidence_digest, outbox_id),
            )
            con.commit()
            return True

    def audit(self, project_id: str) -> dict[str, Any]:
        problems: list[str] = []
        with self._connect() as con:
            events = con.execute("SELECT * FROM accepted_events WHERE project_id=? ORDER BY result_version,event_id", (project_id,)).fetchall()
            state = con.execute("SELECT * FROM project_state WHERE project_id=?", (project_id,)).fetchone()
            expected_prior = 0
            for event in events:
                if event["prior_version"] != expected_prior or event["result_version"] != expected_prior + 1:
                    problems.append(f"version_lineage:{event['event_id']}")
                recomputed_result = _digest(
                    {
                        "event_id": event["event_id"],
                        "command_digest": event["command_digest"],
                        "prior_version": event["prior_version"],
                        "result_version": event["result_version"],
                        "state_digest": _digest({"project_id": project_id, "version": event["result_version"], "state": json.loads(event["result_state_json"])}),
                    }
                )
                if recomputed_result != event["result_digest"]:
                    problems.append(f"result_digest:{event['event_id']}")
                expected_prior = event["result_version"]
            if events and (state is None or state["version"] != expected_prior):
                problems.append("state_version_mismatch")
            if not events and state is not None and state["version"] != 0:
                problems.append("state_without_events")
            outbox_rows = con.execute("SELECT * FROM outbox WHERE project_id=?", (project_id,)).fetchall()
            event_ids = {e["event_id"] for e in events}
            for row in outbox_rows:
                if row["event_id"] not in event_ids:
                    problems.append(f"orphan_outbox:{row['outbox_id']}")
                expected = _digest({"effect_type": row["effect_type"], "effect_payload": json.loads(row["effect_payload_json"])})
                if expected != row["effect_digest"]:
                    problems.append(f"effect_digest:{row['outbox_id']}")
        return {"valid": not problems, "problems": problems, "event_count": len(events), "final_version": expected_prior}
