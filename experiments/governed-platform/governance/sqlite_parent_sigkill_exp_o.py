"""EXP-O Pilot 17: externally killed SQLite worker at coordinated cut points."""
from __future__ import annotations

import argparse
import json
import os
import signal
import time
from typing import Any, Mapping

from sqlite_process_crash_exp_o import (
    authority_payload,
    connect,
    deny,
    digest,
    init_db,
    recover,
    write_anchor,
)

READY_POINTS = (
    "READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT",
    "READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT",
    "READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK",
    "READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT",
    "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK",
    "READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT",
    "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE",
    "READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT",
)


def _ready_and_block(point: str | None, expected: str) -> None:
    if point != expected:
        return
    print(json.dumps({"ready": expected, "pid": os.getpid(), "self_termination": False}), flush=True)
    # Block indefinitely. The parent is the only intended terminator for a fault case.
    while True:
        signal.pause()


def _required(p: Mapping[str, Any]) -> bool:
    return all(p.get(k) not in (None, "") for k in (
        "logical_id", "term", "commit_index", "owner", "lease_epoch",
        "semantic_digest", "effect_digest", "idempotency_key",
    ))


def authority_op(path: str, p: Mapping[str, Any], point: str | None) -> dict[str, Any]:
    if not _required(p):
        return deny("AUTHORITY_BINDING_INCOMPLETE")
    conn = connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ready_and_block(point, "READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT")
        active = conn.execute(
            "SELECT * FROM authority WHERE logical_id=? AND status='ACTIVE' ORDER BY id DESC",
            (p["logical_id"],),
        ).fetchall()
        if active:
            cur = active[0]
            current = (int(cur["term"]), int(cur["commit_index"]), int(cur["lease_epoch"]))
            proposed = (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"]))
            if proposed <= current:
                conn.rollback()
                return deny("STALE_OR_NONADVANCING_AUTHORITY")
            conn.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (p["logical_id"],))
        conn.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
            (p["logical_id"], int(p["term"]), int(p["commit_index"]), p["owner"], int(p["lease_epoch"]),
             p["semantic_digest"], p["effect_digest"], p["idempotency_key"], "ACTIVE"),
        )
        conn.execute(
            "UPDATE meta SET max_term=MAX(max_term,?), max_index=MAX(max_index,?), max_epoch=MAX(max_epoch,?) WHERE id=1",
            (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])),
        )
        _ready_and_block(point, "READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT")
        conn.commit()
        _ready_and_block(point, "READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK")
        return {"authorized": True, "decision": "COMMITTED_AUTHORITY"}
    finally:
        conn.close()


def takeover_op(path: str, p: Mapping[str, Any], point: str | None) -> dict[str, Any]:
    if not _required(p):
        return deny("AUTHORITY_BINDING_INCOMPLETE")
    conn = connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        active = conn.execute(
            "SELECT * FROM authority WHERE logical_id=? AND status='ACTIVE' ORDER BY id DESC", (p["logical_id"],)
        ).fetchall()
        if not active:
            conn.rollback(); return deny("ACTIVE_AUTHORITY_REQUIRED")
        cur = active[0]
        if (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])) <= (
            int(cur["term"]), int(cur["commit_index"]), int(cur["lease_epoch"])
        ):
            conn.rollback(); return deny("STALE_OR_NONADVANCING_TAKEOVER")
        conn.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (p["logical_id"],))
        conn.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
            (p["logical_id"], int(p["term"]), int(p["commit_index"]), p["owner"], int(p["lease_epoch"]),
             p["semantic_digest"], p["effect_digest"], p["idempotency_key"], "ACTIVE"),
        )
        conn.execute(
            "UPDATE meta SET max_term=MAX(max_term,?), max_index=MAX(max_index,?), max_epoch=MAX(max_epoch,?) WHERE id=1",
            (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])),
        )
        _ready_and_block(point, "READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT")
        conn.commit()
        _ready_and_block(point, "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        return {"authorized": True, "decision": "COMMITTED_TAKEOVER"}
    finally:
        conn.close()


def effect_op(path: str, p: Mapping[str, Any], point: str | None) -> dict[str, Any]:
    key = str(p.get("idempotency_key", ""))
    eff = str(p.get("effect_digest", ""))
    sem = str(p.get("semantic_digest", ""))
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
        _ready_and_block(point, "READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT")
        conn.commit()
        _ready_and_block(point, "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE authority SET result_id=? WHERE id=?", (result_id, int(a["id"])))
        conn.commit()
        return {"authorized": True, "decision": "EFFECT_COMMITTED", "executed": True, "result_id": result_id}
    finally:
        conn.close()


def consume_op(path: str, p: Mapping[str, Any], point: str | None) -> dict[str, Any]:
    key = str(p.get("idempotency_key", ""))
    conn = connect(path)
    try:
        effect = conn.execute("SELECT * FROM effects WHERE idempotency_key=?", (key,)).fetchone()
        if effect is None:
            return deny("EFFECT_REQUIRED_BEFORE_CONSUME")
        conn.execute("BEGIN IMMEDIATE")
        active = conn.execute("SELECT id FROM authority WHERE status='ACTIVE' AND idempotency_key=?", (key,)).fetchall()
        if len(active) != 1:
            conn.rollback(); return deny("ACTIVE_AUTHORITY_REQUIRED")
        conn.execute("UPDATE authority SET status='CONSUMED', result_id=? WHERE id=?", (effect["result_id"], int(active[0]["id"])))
        _ready_and_block(point, "READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT")
        conn.commit()
        return {"authorized": False, "decision": "CONSUMED", "result_id": effect["result_id"]}
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--op", choices=("init", "authority", "takeover", "effect", "consume", "recover"), required=True)
    ap.add_argument("--payload", default="{}")
    ap.add_argument("--ready-point")
    ap.add_argument("--anchor")
    args = ap.parse_args(argv)
    init_db(args.db)
    payload = json.loads(args.payload)
    if args.op == "init": result = {"ok": True}
    elif args.op == "authority": result = authority_op(args.db, payload, args.ready_point)
    elif args.op == "takeover": result = takeover_op(args.db, payload, args.ready_point)
    elif args.op == "effect": result = effect_op(args.db, payload, args.ready_point)
    elif args.op == "consume": result = consume_op(args.db, payload, args.ready_point)
    else: result = recover(args.db, args.anchor)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
