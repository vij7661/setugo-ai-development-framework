"""EXP-O Pilot 16 SQLite WAL + subprocess termination falsification prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any, Mapping

KILL_POINTS = (
    "AFTER_BEGIN_BEFORE_AUTHORITY_INSERT",
    "AFTER_AUTHORITY_INSERT_BEFORE_COMMIT",
    "AFTER_AUTHORITY_COMMIT_BEFORE_ACK",
    "AFTER_TAKEOVER_INSERT_BEFORE_COMMIT",
    "AFTER_TAKEOVER_COMMIT_BEFORE_ACK",
    "AFTER_EFFECT_INSERT_BEFORE_COMMIT",
    "AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE",
    "AFTER_EVIDENCE_UPDATE_BEFORE_COMMIT",
    "AFTER_CONSUMED_UPDATE_BEFORE_COMMIT",
    "AFTER_CONSUMED_COMMIT_BEFORE_ACK",
)
EXIT_KILLED = 75


def canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()


def digest(v: Any) -> str:
    return hashlib.sha256(canonical(v)).hexdigest()


def deny(reason: str, **extra: Any) -> dict[str, Any]:
    out = {"authorized": False, "decision": "DENY", "reason": reason}
    out.update(extra)
    return out


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=5.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=OFF")
    return conn


def init_db(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS authority (id INTEGER PRIMARY KEY AUTOINCREMENT, logical_id TEXT NOT NULL, term INTEGER NOT NULL, commit_index INTEGER NOT NULL, owner TEXT NOT NULL, lease_epoch INTEGER NOT NULL, semantic_digest TEXT, effect_digest TEXT, idempotency_key TEXT, status TEXT NOT NULL, result_id TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS effects (idempotency_key TEXT PRIMARY KEY, effect_digest TEXT NOT NULL, result_id TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY CHECK(id=1), max_term INTEGER NOT NULL, max_index INTEGER NOT NULL, max_epoch INTEGER NOT NULL)")
        if conn.execute("SELECT 1 FROM meta WHERE id=1").fetchone() is None:
            conn.execute("INSERT INTO meta(id,max_term,max_index,max_epoch) VALUES(1,0,0,0)")
    finally:
        conn.close()


def _kill(point: str | None, expected: str) -> None:
    if point == expected:
        os._exit(EXIT_KILLED)


def _payload_required(p: Mapping[str, Any]) -> bool:
    return all(p.get(k) not in (None, "") for k in ("logical_id", "term", "commit_index", "owner", "lease_epoch", "semantic_digest", "effect_digest", "idempotency_key"))


def _insert_authority(conn: sqlite3.Connection, p: Mapping[str, Any], status: str = "ACTIVE") -> None:
    conn.execute(
        "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
        (p["logical_id"], int(p["term"]), int(p["commit_index"]), p["owner"], int(p["lease_epoch"]), p.get("semantic_digest"), p.get("effect_digest"), p.get("idempotency_key"), status),
    )
    conn.execute("UPDATE meta SET max_term=MAX(max_term,?), max_index=MAX(max_index,?), max_epoch=MAX(max_epoch,?) WHERE id=1", (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])))


def worker_authority(path: str, p: Mapping[str, Any], kill_point: str | None) -> dict[str, Any]:
    if not _payload_required(p):
        return deny("AUTHORITY_BINDING_INCOMPLETE")
    conn = connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _kill(kill_point, "AFTER_BEGIN_BEFORE_AUTHORITY_INSERT")
        active = conn.execute("SELECT * FROM authority WHERE logical_id=? AND status='ACTIVE' ORDER BY id DESC", (p["logical_id"],)).fetchall()
        if active:
            current = active[0]
            cur = (int(current["term"]), int(current["commit_index"]), int(current["lease_epoch"]))
            proposed = (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"]))
            if proposed <= cur:
                conn.rollback()
                return deny("STALE_OR_NONADVANCING_AUTHORITY")
            conn.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (p["logical_id"],))
        _insert_authority(conn, p)
        _kill(kill_point, "AFTER_AUTHORITY_INSERT_BEFORE_COMMIT")
        conn.commit()
        _kill(kill_point, "AFTER_AUTHORITY_COMMIT_BEFORE_ACK")
        return {"authorized": True, "decision": "COMMITTED_AUTHORITY"}
    finally:
        conn.close()


def worker_takeover(path: str, p: Mapping[str, Any], kill_point: str | None) -> dict[str, Any]:
    if not _payload_required(p):
        return deny("AUTHORITY_BINDING_INCOMPLETE")
    conn = connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        active = conn.execute("SELECT * FROM authority WHERE logical_id=? AND status='ACTIVE' ORDER BY id DESC", (p["logical_id"],)).fetchall()
        if not active:
            conn.rollback(); return deny("ACTIVE_AUTHORITY_REQUIRED")
        cur = active[0]
        if (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])) <= (int(cur["term"]), int(cur["commit_index"]), int(cur["lease_epoch"])):
            conn.rollback(); return deny("STALE_OR_NONADVANCING_TAKEOVER")
        conn.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (p["logical_id"],))
        _insert_authority(conn, p)
        _kill(kill_point, "AFTER_TAKEOVER_INSERT_BEFORE_COMMIT")
        conn.commit()
        _kill(kill_point, "AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        return {"authorized": True, "decision": "COMMITTED_TAKEOVER"}
    finally:
        conn.close()


def worker_effect(path: str, p: Mapping[str, Any], kill_point: str | None) -> dict[str, Any]:
    key, eff, sem = str(p.get("idempotency_key", "")), str(p.get("effect_digest", "")), str(p.get("semantic_digest", ""))
    conn = connect(path)
    try:
        existing = conn.execute("SELECT * FROM effects WHERE idempotency_key=?", (key,)).fetchone()
        if existing is not None:
            if existing["effect_digest"] != eff:
                return deny("IDEMPOTENCY_EFFECT_REBINDING_DENIED")
            return {"authorized": False, "decision": "RECONCILED", "executed": False, "result_id": existing["result_id"]}
        active = conn.execute("SELECT * FROM authority WHERE status='ACTIVE' AND idempotency_key=? ORDER BY id DESC", (key,)).fetchall()
        if len(active) != 1:
            return deny("UNIQUE_ACTIVE_AUTHORITY_REQUIRED")
        a = active[0]
        if a["effect_digest"] != eff or a["semantic_digest"] != sem:
            return deny("AUTHORITY_BINDING_MISMATCH")
        result_id = digest({"idempotency_key": key, "effect_digest": eff})
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO effects(idempotency_key,effect_digest,result_id) VALUES(?,?,?)", (key, eff, result_id))
        _kill(kill_point, "AFTER_EFFECT_INSERT_BEFORE_COMMIT")
        conn.commit()
        _kill(kill_point, "AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE authority SET result_id=? WHERE id=?", (result_id, int(a["id"])))
        _kill(kill_point, "AFTER_EVIDENCE_UPDATE_BEFORE_COMMIT")
        conn.commit()
        return {"authorized": True, "decision": "EFFECT_COMMITTED", "executed": True, "result_id": result_id}
    finally:
        conn.close()


def worker_consume(path: str, p: Mapping[str, Any], kill_point: str | None) -> dict[str, Any]:
    key = str(p.get("idempotency_key", ""))
    conn = connect(path)
    try:
        effect = conn.execute("SELECT * FROM effects WHERE idempotency_key=?", (key,)).fetchone()
        if effect is None:
            return deny("EFFECT_REQUIRED_BEFORE_CONSUME")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE authority SET status='CONSUMED', result_id=? WHERE status='ACTIVE' AND idempotency_key=?", (effect["result_id"], key))
        if conn.total_changes == 0:
            conn.rollback(); return deny("ACTIVE_AUTHORITY_REQUIRED")
        _kill(kill_point, "AFTER_CONSUMED_UPDATE_BEFORE_COMMIT")
        conn.commit()
        _kill(kill_point, "AFTER_CONSUMED_COMMIT_BEFORE_ACK")
        return {"authorized": False, "decision": "CONSUMED", "result_id": effect["result_id"]}
    finally:
        conn.close()


def recover(path: str | Path, anchor_path: str | Path | None = None) -> dict[str, Any]:
    init_db(path)
    conn = connect(path)
    try:
        meta = conn.execute("SELECT max_term,max_index,max_epoch FROM meta WHERE id=1").fetchone()
        active = conn.execute("SELECT * FROM authority WHERE status='ACTIVE' ORDER BY id").fetchall()
        consumed = conn.execute("SELECT * FROM authority WHERE status='CONSUMED' ORDER BY id").fetchall()
        effects = {r["idempotency_key"]: r for r in conn.execute("SELECT * FROM effects")}
        if len(active) > 1:
            logicals = [r["logical_id"] for r in active]
            if len(logicals) != len(set(logicals)):
                return deny("DUPLICATE_ACTIVE_AUTHORITY", recovery_status="CORRUPT")
        if anchor_path is not None and Path(anchor_path).exists():
            anchor = json.loads(Path(anchor_path).read_text())
            observed = (int(meta["max_term"]), int(meta["max_index"]), int(meta["max_epoch"]))
            required = (int(anchor["term"]), int(anchor["commit_index"]), int(anchor["lease_epoch"]))
            if observed < required:
                return deny("ANCHORED_HIGHER_FENCE_MISSING", recovery_status="STALE_ROLLBACK_BLOCKED")
        for row in list(active) + list(consumed):
            if any(row[k] in (None, "") for k in ("semantic_digest", "effect_digest", "idempotency_key")):
                return deny("AUTHORITY_BINDING_INCOMPLETE", recovery_status="CORRUPT")
        for row in consumed:
            effect = effects.get(row["idempotency_key"])
            if effect is None or row["result_id"] in (None, "") or effect["result_id"] != row["result_id"]:
                return deny("CONSUMED_EFFECT_IDENTITY_MISSING", recovery_status="RECONCILIATION_REQUIRED")
        if len(active) == 0:
            if consumed:
                row = consumed[-1]
                return {"authorized": False, "decision": "RECOVERED_CONSUMED", "recovery_status": "RECOVERED_CONSUMED", "result_id": row["result_id"]}
            return deny("NO_ACTIVE_AUTHORITY", recovery_status="EMPTY")
        if len(active) != 1:
            return deny("ACTIVE_AUTHORITY_AMBIGUOUS", recovery_status="CORRUPT")
        row = active[0]
        effect = effects.get(row["idempotency_key"])
        if effect is not None:
            if effect["effect_digest"] != row["effect_digest"]:
                return deny("EFFECT_LEDGER_REBINDING_CORRUPTION", recovery_status="CORRUPT")
            return {"authorized": False, "decision": "RECONCILED", "recovery_status": "RECOVERED_EFFECT", "result_id": effect["result_id"]}
        return {"authorized": True, "decision": "ALLOW_RECOVERED_AUTHORITY", "recovery_status": "AUTHORITATIVE", "authority": dict(row)}
    finally:
        conn.close()


def authority_payload(*, logical_id: str = "auth-1", term: int = 1, commit_index: int = 1, owner: str = "r1", lease_epoch: int = 1, semantic_digest: str = "semantic-A", effect_digest: str = "effect-A", idempotency_key: str = "intent-1") -> dict[str, Any]:
    return {"logical_id": logical_id, "term": term, "commit_index": commit_index, "owner": owner, "lease_epoch": lease_epoch, "semantic_digest": semantic_digest, "effect_digest": effect_digest, "idempotency_key": idempotency_key}


def write_anchor(path: str | Path, *, term: int, commit_index: int, lease_epoch: int) -> None:
    Path(path).write_bytes(canonical({"term": term, "commit_index": commit_index, "lease_epoch": lease_epoch}))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--op", required=True, choices=("init", "authority", "takeover", "effect", "consume", "recover"))
    ap.add_argument("--payload", default="{}")
    ap.add_argument("--kill-point")
    ap.add_argument("--anchor")
    args = ap.parse_args(argv)
    init_db(args.db)
    p = json.loads(args.payload)
    if args.op == "init": result = {"ok": True}
    elif args.op == "authority": result = worker_authority(args.db, p, args.kill_point)
    elif args.op == "takeover": result = worker_takeover(args.db, p, args.kill_point)
    elif args.op == "effect": result = worker_effect(args.db, p, args.kill_point)
    elif args.op == "consume": result = worker_consume(args.db, p, args.kill_point)
    else: result = recover(args.db, args.anchor)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
