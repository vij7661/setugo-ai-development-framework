from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GENESIS = "GENESIS"
BUSY_TIMEOUT_MS = 30_000


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _event_hash(session_id: str, seq: int, event_type: str, payload: dict, previous_hash: str) -> str:
    body = {"session_id": session_id, "seq": seq, "event_type": event_type, "payload": payload, "previous_hash": previous_hash}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SessionEvent:
    session_id: str
    seq: int
    event_type: str
    payload: dict
    previous_hash: str
    event_hash: str
    created_at: str


@dataclass(frozen=True)
class SessionSummary:
    session_id: str
    started_at_utc: str
    updated_at_utc: str
    event_count: int
    final_state: str | None
    final_reasons: tuple[str, ...]
    artifact_hash: str | None
    chain_valid: bool


class SQLiteSessionStore:
    """Single-node append-only, hash-linked review evidence ledger.

    Tamper-evident, not externally immutable against privileged database rewrite.
    Production needs WORM/external anchoring.
    A session identifier represents exactly one review lifecycle; replaying a new
    REQUEST_RECEIVED under an existing identifier is rejected atomically.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=BUSY_TIMEOUT_MS / 1000)
        conn.row_factory = sqlite3.Row
        conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_events (
                    session_id TEXT NOT NULL, seq INTEGER NOT NULL, event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(session_id, seq), UNIQUE(event_hash)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_review_events_session ON review_events(session_id, seq)")

    def append(self, session_id: str, event_type: str, payload: dict) -> SessionEvent:
        if not session_id or not event_type:
            raise ValueError("session_id and event_type required")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            latest = conn.execute(
                "SELECT seq, event_hash, event_type FROM review_events WHERE session_id=? ORDER BY seq DESC LIMIT 1",
                (session_id,),
            ).fetchone()
            if event_type == "REQUEST_RECEIVED" and latest is not None:
                raise ValueError("request/session id already exists; start a new review with a new request_id")
            if event_type != "REQUEST_RECEIVED" and latest is None:
                raise ValueError("session must begin with REQUEST_RECEIVED")

            seq = 1 if latest is None else int(latest["seq"]) + 1
            previous_hash = GENESIS if latest is None else latest["event_hash"]
            digest = _event_hash(session_id, seq, event_type, payload, previous_hash)
            conn.execute(
                "INSERT INTO review_events(session_id, seq, event_type, payload_json, previous_hash, event_hash) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, seq, event_type, _canonical(payload), previous_hash, digest),
            )
            row = conn.execute(
                "SELECT * FROM review_events WHERE session_id=? AND seq=?",
                (session_id, seq),
            ).fetchone()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self._from_row(row)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> SessionEvent:
        return SessionEvent(
            session_id=row["session_id"],
            seq=int(row["seq"]),
            event_type=row["event_type"],
            payload=json.loads(row["payload_json"]),
            previous_hash=row["previous_hash"],
            event_hash=row["event_hash"],
            created_at=row["created_at"],
        )

    def events(self, session_id: str) -> tuple[SessionEvent, ...]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM review_events WHERE session_id=? ORDER BY seq", (session_id,)).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def validate_chain(self, session_id: str) -> bool:
        previous = GENESIS
        expected_seq = 1
        events = self.events(session_id)
        if events and events[0].event_type != "REQUEST_RECEIVED":
            return False
        final_seen = False
        for event in events:
            if event.seq != expected_seq or event.previous_hash != previous:
                return False
            if final_seen:
                return False
            expected_hash = _event_hash(event.session_id, event.seq, event.event_type, event.payload, event.previous_hash)
            if event.event_hash != expected_hash:
                return False
            if event.event_type == "FINAL_DECISION":
                final_seen = True
            previous = event.event_hash
            expected_seq += 1
        return True

    def latest_decision(self, session_id: str) -> SessionEvent | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM review_events WHERE session_id=? AND event_type='FINAL_DECISION' ORDER BY seq DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def list_sessions(self, *, limit: int = 100) -> tuple[SessionSummary, ...]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT session_id, MIN(created_at) AS started_at, MAX(created_at) AS updated_at, COUNT(*) AS event_count
                   FROM review_events GROUP BY session_id ORDER BY MAX(created_at) DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        summaries: list[SessionSummary] = []
        for row in rows:
            session_id = row["session_id"]
            decision = self.latest_decision(session_id)
            payload = {} if decision is None else decision.payload
            summaries.append(
                SessionSummary(
                    session_id=session_id,
                    started_at_utc=row["started_at"],
                    updated_at_utc=row["updated_at"],
                    event_count=int(row["event_count"]),
                    final_state=payload.get("state"),
                    final_reasons=tuple(str(v) for v in payload.get("reasons", [])),
                    artifact_hash=payload.get("artifact_hash"),
                    chain_valid=self.validate_chain(session_id),
                )
            )
        return tuple(summaries)
