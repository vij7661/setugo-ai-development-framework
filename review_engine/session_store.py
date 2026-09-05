from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GENESIS = "GENESIS"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _event_hash(session_id: str, seq: int, event_type: str, payload: dict, previous_hash: str) -> str:
    body = {
        "session_id": session_id,
        "seq": seq,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": previous_hash,
    }
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


class SQLiteSessionStore:
    """Single-node append-only, hash-linked review evidence ledger.

    The chain is tamper-evident but not externally immutable against a privileged
    database rewrite. Production needs external anchoring/WORM semantics.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_events (
                    session_id TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(session_id, seq),
                    UNIQUE(event_hash)
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
                "SELECT seq, event_hash FROM review_events WHERE session_id=? ORDER BY seq DESC LIMIT 1",
                (session_id,),
            ).fetchone()
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
            rows = conn.execute(
                "SELECT * FROM review_events WHERE session_id=? ORDER BY seq",
                (session_id,),
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def validate_chain(self, session_id: str) -> bool:
        previous = GENESIS
        expected_seq = 1
        for event in self.events(session_id):
            if event.seq != expected_seq or event.previous_hash != previous:
                return False
            expected_hash = _event_hash(event.session_id, event.seq, event.event_type, event.payload, event.previous_hash)
            if event.event_hash != expected_hash:
                return False
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
