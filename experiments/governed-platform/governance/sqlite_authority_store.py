"""SQLite-backed transactional proof for authoritative intent linearization.

This is a harness reference implementation, not the production persistence choice.
It demonstrates that idempotency uniqueness, event append, and state-version advance
can occur inside one database transaction.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def initialize_store(path: str | Path) -> None:
    with sqlite3.connect(path, timeout=5.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS authority_state (singleton INTEGER PRIMARY KEY CHECK(singleton=1), state_version INTEGER NOT NULL)"
        )
        conn.execute("INSERT OR IGNORE INTO authority_state(singleton, state_version) VALUES (1, 0)")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS intents (
                actor_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                intent_hash TEXT NOT NULL,
                authoritative_event_id TEXT NOT NULL UNIQUE,
                PRIMARY KEY(actor_id, idempotency_key)
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS event_log (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                actor_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                intent_hash TEXT NOT NULL
            )"""
        )


def commit_intent(path: str | Path, request: dict) -> dict:
    required = ("actor_id", "idempotency_key", "intent_hash", "event_id", "expected_state_version")
    missing = [k for k in required if request.get(k) in (None, "")]
    if missing:
        return {"decision": "BLOCK", "reason": "missing request fields: " + ",".join(missing)}
    try:
        expected = int(request["expected_state_version"])
    except (TypeError, ValueError):
        return {"decision": "BLOCK", "reason": "expected state version malformed"}

    conn = sqlite3.connect(path, timeout=5.0, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            "SELECT intent_hash, authoritative_event_id FROM intents WHERE actor_id=? AND idempotency_key=?",
            (request["actor_id"], request["idempotency_key"]),
        ).fetchone()
        if existing is not None:
            conn.execute("ROLLBACK")
            if existing[0] == request["intent_hash"]:
                return {"decision": "DUPLICATE", "reason": "intent already linearized", "authoritative_event_id": existing[1]}
            return {"decision": "BLOCK", "reason": "idempotency key reused for different intent"}

        current = conn.execute("SELECT state_version FROM authority_state WHERE singleton=1").fetchone()
        if current is None:
            conn.execute("ROLLBACK")
            return {"decision": "BLOCK", "reason": "authority state missing"}
        if expected != int(current[0]):
            conn.execute("ROLLBACK")
            return {"decision": "STALE", "reason": "lost authoritative state-version race", "state_version": int(current[0])}

        conn.execute(
            "INSERT INTO intents(actor_id,idempotency_key,intent_hash,authoritative_event_id) VALUES (?,?,?,?)",
            (request["actor_id"], request["idempotency_key"], request["intent_hash"], request["event_id"]),
        )
        conn.execute(
            "INSERT INTO event_log(event_id,actor_id,idempotency_key,intent_hash) VALUES (?,?,?,?)",
            (request["event_id"], request["actor_id"], request["idempotency_key"], request["intent_hash"]),
        )
        conn.execute("UPDATE authority_state SET state_version=state_version+1 WHERE singleton=1")
        conn.execute("COMMIT")
        return {"decision": "APPEND", "reason": "intent atomically linearized", "authoritative_event_id": request["event_id"], "state_version": expected + 1}
    except sqlite3.IntegrityError:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        return {"decision": "BLOCK", "reason": "database uniqueness constraint rejected conflicting authoritative append"}
    finally:
        conn.close()


def snapshot(path: str | Path) -> dict:
    with sqlite3.connect(path, timeout=5.0) as conn:
        version = conn.execute("SELECT state_version FROM authority_state WHERE singleton=1").fetchone()[0]
        intents = conn.execute("SELECT actor_id,idempotency_key,intent_hash,authoritative_event_id FROM intents ORDER BY actor_id,idempotency_key").fetchall()
        events = conn.execute("SELECT sequence,event_id,actor_id,idempotency_key,intent_hash FROM event_log ORDER BY sequence").fetchall()
    return {
        "state_version": version,
        "intents": [list(row) for row in intents],
        "events": [list(row) for row in events],
    }
