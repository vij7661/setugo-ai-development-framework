"""EXP-O Pilot 18: bounded SQLite storage-fault/corruption recovery harness.

This module is intentionally isolated from Pilots 14-17.  It exercises software-visible
SQLite failure/corruption only; it is not a physical power-loss or drive-durability model.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any, Mapping

from sqlite_process_crash_exp_o import (
    authority_payload,
    connect,
    deny,
    digest,
    init_db as _legacy_init_db,
    worker_authority,
    worker_consume,
    worker_effect,
    worker_takeover,
    write_anchor,
)

FAULT_DATABASE_FULL = "DATABASE_FULL"
FAULT_MAIN_TRUNCATION = "MAIN_DATABASE_TRUNCATION"
FAULT_MAIN_CORRUPTION = "MAIN_DATABASE_BYTE_CORRUPTION"
FAULT_WAL_TRUNCATION = "WAL_TRUNCATION"
FAULT_WAL_CORRUPTION = "WAL_BYTE_CORRUPTION"
FAULT_WAL_PAIR = "WAL_REMOVAL_OR_STALE_PAIR"
FAULT_STALE_DB = "DATABASE_SUBSTITUTION_BELOW_ANCHOR"
FAULT_EFFECT = "EFFECT_STATE_CORRUPTION"
FAULT_RELATIONAL = "RELATIONAL_INCONSISTENCY"


def init_db(path: str | Path) -> None:
    """Create the Pilot-18 schema without changing the earlier pilot schema contract."""
    _legacy_init_db(path)
    conn = connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS fault_pad (id INTEGER PRIMARY KEY, payload BLOB NOT NULL)")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def checkpoint(path: str | Path) -> None:
    conn = connect(path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def _storage_deny(reason: str, *, status: str = "STORAGE_CORRUPT", **extra: Any) -> dict[str, Any]:
    return deny(reason, recovery_status=status, storage_integrity=False, **extra)


def _anchor_tuple(anchor_path: str | Path | None) -> tuple[int, int, int] | None:
    if anchor_path is None or not Path(anchor_path).exists():
        return None
    try:
        data = json.loads(Path(anchor_path).read_text(encoding="utf-8"))
        return (int(data["term"]), int(data["commit_index"]), int(data["lease_epoch"]))
    except Exception:
        return None


def recover_strict(path: str | Path, anchor_path: str | Path | None = None) -> dict[str, Any]:
    """Recover only after SQLite and application relational integrity are established."""
    db = Path(path)
    if not db.exists():
        return _storage_deny("DATABASE_MISSING", status="STORAGE_ERROR")
    try:
        conn = sqlite3.connect(str(db), timeout=2.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        return _storage_deny("DATABASE_OPEN_FAILED", error=str(exc))
    try:
        try:
            quick = [str(r[0]) for r in conn.execute("PRAGMA quick_check").fetchall()]
            if quick != ["ok"]:
                return _storage_deny("SQLITE_INTEGRITY_CHECK_FAILED", integrity=quick[:8])
            tables = {str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            required = {"authority", "effects", "meta"}
            if not required.issubset(tables):
                return _storage_deny("REQUIRED_SCHEMA_MISSING", missing=sorted(required - tables))
            meta_rows = conn.execute("SELECT max_term,max_index,max_epoch FROM meta WHERE id=1").fetchall()
            if len(meta_rows) != 1:
                return _storage_deny("MONOTONIC_METADATA_INVALID")
            meta = meta_rows[0]
            authorities = conn.execute("SELECT * FROM authority ORDER BY id").fetchall()
            effects = conn.execute("SELECT * FROM effects ORDER BY idempotency_key").fetchall()
        except sqlite3.Error as exc:
            return _storage_deny("SQLITE_READ_OR_INTEGRITY_ERROR", error=str(exc))

        # Monotonic metadata must dominate every authority row, not merely be syntactically valid.
        observed = (int(meta["max_term"]), int(meta["max_index"]), int(meta["max_epoch"]))
        for row in authorities:
            try:
                row_fence = (int(row["term"]), int(row["commit_index"]), int(row["lease_epoch"]))
            except Exception:
                return _storage_deny("AUTHORITY_FENCE_MALFORMED")
            if row_fence > observed:
                return _storage_deny("MONOTONIC_METADATA_BELOW_AUTHORITY")
            if any(row[k] in (None, "") for k in ("logical_id", "owner", "semantic_digest", "effect_digest", "idempotency_key", "status")):
                return _storage_deny("AUTHORITY_BINDING_INCOMPLETE")
            if row["status"] not in ("ACTIVE", "STALE", "CONSUMED"):
                return _storage_deny("AUTHORITY_STATUS_INVALID")

        anchor = _anchor_tuple(anchor_path)
        if anchor_path is not None and anchor is None:
            return _storage_deny("INDEPENDENT_ANCHOR_UNREADABLE", status="STORAGE_ERROR")
        if anchor is not None and observed < anchor:
            return _storage_deny("ANCHORED_HIGHER_FENCE_MISSING", status="STALE_ROLLBACK_BLOCKED", observed=observed, required=anchor)

        active = [r for r in authorities if r["status"] == "ACTIVE"]
        consumed = [r for r in authorities if r["status"] == "CONSUMED"]
        by_key = {str(r["idempotency_key"]): r for r in effects}
        if len(by_key) != len(effects):
            return _storage_deny("DUPLICATE_EFFECT_IDEMPOTENCY_STATE")

        active_logical = [str(r["logical_id"]) for r in active]
        if len(active_logical) != len(set(active_logical)):
            return _storage_deny("DUPLICATE_ACTIVE_AUTHORITY")

        # Every effect must bind to exactly one authority history row with the same effect digest.
        for key, effect in by_key.items():
            linked = [r for r in authorities if str(r["idempotency_key"]) == key]
            if not linked:
                return _storage_deny("ORPHAN_EFFECT_STATE", status="RECONCILIATION_REQUIRED")
            if any(str(r["effect_digest"]) != str(effect["effect_digest"]) for r in linked):
                return _storage_deny("EFFECT_LEDGER_REBINDING_CORRUPTION")
            if effect["result_id"] in (None, ""):
                return _storage_deny("EFFECT_RESULT_ID_MISSING", status="RECONCILIATION_REQUIRED")

        for row in consumed:
            effect = by_key.get(str(row["idempotency_key"]))
            if effect is None or row["result_id"] in (None, "") or str(effect["result_id"]) != str(row["result_id"]):
                return _storage_deny("CONSUMED_EFFECT_IDENTITY_MISSING", status="RECONCILIATION_REQUIRED")

        if not active:
            if consumed:
                return {
                    "authorized": False,
                    "decision": "RECOVERED_CONSUMED",
                    "recovery_status": "RECOVERED_CONSUMED",
                    "storage_integrity": True,
                    "result_id": consumed[-1]["result_id"],
                }
            return deny("NO_ACTIVE_AUTHORITY", recovery_status="EMPTY", storage_integrity=True)
        if len(active) != 1:
            return _storage_deny("ACTIVE_AUTHORITY_AMBIGUOUS")

        row = active[0]
        effect = by_key.get(str(row["idempotency_key"]))
        if effect is not None:
            if str(effect["effect_digest"]) != str(row["effect_digest"]):
                return _storage_deny("EFFECT_LEDGER_REBINDING_CORRUPTION")
            return {
                "authorized": False,
                "decision": "RECONCILED",
                "recovery_status": "RECOVERED_EFFECT",
                "storage_integrity": True,
                "result_id": effect["result_id"],
            }
        return {
            "authorized": True,
            "decision": "ALLOW_RECOVERED_AUTHORITY",
            "recovery_status": "AUTHORITATIVE",
            "storage_integrity": True,
            "authority": dict(row),
        }
    finally:
        conn.close()


def _fill_transaction_until_full(conn: sqlite3.Connection) -> str:
    """Force SQLITE_FULL deterministically inside the current transaction."""
    pages = int(conn.execute("PRAGMA page_count").fetchone()[0])
    conn.execute(f"PRAGMA max_page_count={pages}")
    try:
        # Much larger than any spare room in the already allocated final page.
        conn.execute("INSERT INTO fault_pad(payload) VALUES(?)", (b"x" * (2 * 1024 * 1024),))
    except sqlite3.OperationalError as exc:
        text = str(exc).lower()
        if "full" not in text:
            raise
        return str(exc)
    raise AssertionError("DATABASE_FULL fault injection did not trigger")


def _reset_page_limit(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("PRAGMA max_page_count=1073741823")
    except sqlite3.Error:
        pass


def database_full_authority(path: str | Path, p: Mapping[str, Any]) -> dict[str, Any]:
    conn = connect(path)
    try:
        before = conn.execute("SELECT COUNT(*) FROM authority").fetchone()[0]
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
            (p["logical_id"], int(p["term"]), int(p["commit_index"]), p["owner"], int(p["lease_epoch"]), p["semantic_digest"], p["effect_digest"], p["idempotency_key"], "ACTIVE"),
        )
        conn.execute("UPDATE meta SET max_term=MAX(max_term,?),max_index=MAX(max_index,?),max_epoch=MAX(max_epoch,?) WHERE id=1", (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])))
        try:
            msg = _fill_transaction_until_full(conn)
        except Exception:
            conn.rollback(); raise
        conn.rollback()
        _reset_page_limit(conn)
        after = conn.execute("SELECT COUNT(*) FROM authority").fetchone()[0]
        return {"fault": FAULT_DATABASE_FULL, "fault_observed": True, "sqlite_error": msg, "rolled_back": before == after}
    finally:
        _reset_page_limit(conn); conn.close()


def database_full_takeover(path: str | Path, p: Mapping[str, Any]) -> dict[str, Any]:
    conn = connect(path)
    try:
        before = [tuple(r) for r in conn.execute("SELECT logical_id,term,commit_index,owner,lease_epoch,status FROM authority ORDER BY id")]
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (p["logical_id"],))
        conn.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
            (p["logical_id"], int(p["term"]), int(p["commit_index"]), p["owner"], int(p["lease_epoch"]), p["semantic_digest"], p["effect_digest"], p["idempotency_key"], "ACTIVE"),
        )
        conn.execute("UPDATE meta SET max_term=MAX(max_term,?),max_index=MAX(max_index,?),max_epoch=MAX(max_epoch,?) WHERE id=1", (int(p["term"]), int(p["commit_index"]), int(p["lease_epoch"])))
        try:
            msg = _fill_transaction_until_full(conn)
        except Exception:
            conn.rollback(); raise
        conn.rollback(); _reset_page_limit(conn)
        after = [tuple(r) for r in conn.execute("SELECT logical_id,term,commit_index,owner,lease_epoch,status FROM authority ORDER BY id")]
        return {"fault": FAULT_DATABASE_FULL, "fault_observed": True, "sqlite_error": msg, "rolled_back": before == after}
    finally:
        _reset_page_limit(conn); conn.close()


def database_full_effect(path: str | Path, p: Mapping[str, Any]) -> dict[str, Any]:
    key, eff = str(p["idempotency_key"]), str(p["effect_digest"])
    conn = connect(path)
    try:
        before = conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
        result_id = digest({"idempotency_key": key, "effect_digest": eff})
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO effects(idempotency_key,effect_digest,result_id) VALUES(?,?,?)", (key, eff, result_id))
        try:
            msg = _fill_transaction_until_full(conn)
        except Exception:
            conn.rollback(); raise
        conn.rollback(); _reset_page_limit(conn)
        after = conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
        return {"fault": FAULT_DATABASE_FULL, "fault_observed": True, "sqlite_error": msg, "rolled_back": before == after}
    finally:
        _reset_page_limit(conn); conn.close()


def copy_database(src: str | Path, dst: str | Path) -> None:
    checkpoint(src)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def mutate_main_byte(path: str | Path, *, offset: int = 0, value: int | None = None) -> dict[str, Any]:
    p = Path(path)
    data = bytearray(p.read_bytes())
    if not data:
        raise AssertionError("cannot corrupt empty database")
    offset = max(0, min(offset, len(data) - 1))
    before = data[offset]
    data[offset] = (before ^ 0xFF) if value is None else int(value) & 0xFF
    p.write_bytes(data)
    return {"fault": FAULT_MAIN_CORRUPTION, "fault_observed": data[offset] != before, "offset": offset}


def truncate_main(path: str | Path, *, keep_bytes: int) -> dict[str, Any]:
    p = Path(path)
    before = p.stat().st_size
    keep = max(1, min(int(keep_bytes), before - 1))
    with p.open("r+b") as f:
        f.truncate(keep)
    return {"fault": FAULT_MAIN_TRUNCATION, "fault_observed": p.stat().st_size < before, "before": before, "after": p.stat().st_size}


def mutate_authority_binding(path: str | Path, *, semantic_digest: str | None = None) -> None:
    conn = connect(path)
    try:
        conn.execute("UPDATE authority SET semantic_digest=? WHERE status='ACTIVE'", (semantic_digest,))
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def corrupt_meta_below_rows(path: str | Path) -> None:
    conn = connect(path)
    try:
        conn.execute("UPDATE meta SET max_term=0,max_index=0,max_epoch=0 WHERE id=1")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def corrupt_effect_digest(path: str | Path, new_digest: str) -> None:
    conn = connect(path)
    try:
        conn.execute("UPDATE effects SET effect_digest=?", (new_digest,))
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def delete_effect_rows(path: str | Path) -> None:
    conn = connect(path)
    try:
        conn.execute("DELETE FROM effects")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def create_duplicate_active(path: str | Path) -> None:
    conn = connect(path)
    try:
        row = conn.execute("SELECT * FROM authority WHERE status='ACTIVE' ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            raise AssertionError("active authority required")
        conn.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (row["logical_id"], int(row["term"]), int(row["commit_index"]), str(row["owner"]) + "-duplicate", int(row["lease_epoch"]), row["semantic_digest"], row["effect_digest"], row["idempotency_key"], "ACTIVE", row["result_id"]),
        )
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def create_live_wal_snapshot(base_path: str | Path, snapshot_path: str | Path, higher: Mapping[str, Any]) -> dict[str, Any]:
    """Copy a main DB + live WAL while a connection prevents last-close checkpoint cleanup."""
    base = Path(base_path)
    snap = Path(snapshot_path)
    init_db(base)
    first = authority_payload(logical_id=str(higher["logical_id"]), term=1, commit_index=1, owner="base", lease_epoch=1,
                              semantic_digest=str(higher["semantic_digest"]), effect_digest=str(higher["effect_digest"]), idempotency_key=str(higher["idempotency_key"]))
    worker_authority(str(base), first, None)
    checkpoint(base)
    keeper = connect(base)
    try:
        keeper.execute("PRAGMA wal_autocheckpoint=0")
        keeper.execute("BEGIN IMMEDIATE")
        keeper.execute("UPDATE authority SET status='STALE' WHERE logical_id=? AND status='ACTIVE'", (higher["logical_id"],))
        keeper.execute(
            "INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES(?,?,?,?,?,?,?,?,?,NULL)",
            (higher["logical_id"], int(higher["term"]), int(higher["commit_index"]), higher["owner"], int(higher["lease_epoch"]), higher["semantic_digest"], higher["effect_digest"], higher["idempotency_key"], "ACTIVE"),
        )
        keeper.execute("UPDATE meta SET max_term=?,max_index=?,max_epoch=? WHERE id=1", (int(higher["term"]), int(higher["commit_index"]), int(higher["lease_epoch"])))
        keeper.commit()
        wal = Path(str(base) + "-wal")
        if not wal.exists() or wal.stat().st_size <= 32:
            raise AssertionError("live WAL was not created")
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base, snap)
        shutil.copyfile(wal, Path(str(snap) + "-wal"))
        return {"wal_created": True, "wal_size": wal.stat().st_size, "main_size": base.stat().st_size}
    finally:
        keeper.close()


def truncate_wal(path: str | Path, *, remove_bytes: int = 64) -> dict[str, Any]:
    wal = Path(str(path) + "-wal")
    before = wal.stat().st_size
    after = max(1, before - int(remove_bytes))
    with wal.open("r+b") as f:
        f.truncate(after)
    return {"fault": FAULT_WAL_TRUNCATION, "fault_observed": wal.stat().st_size < before, "before": before, "after": wal.stat().st_size}


def mutate_wal_byte(path: str | Path, *, offset: int = 24) -> dict[str, Any]:
    wal = Path(str(path) + "-wal")
    data = bytearray(wal.read_bytes())
    if len(data) <= offset:
        raise AssertionError("WAL too small to corrupt")
    before = data[offset]
    data[offset] ^= 0xFF
    wal.write_bytes(data)
    return {"fault": FAULT_WAL_CORRUPTION, "fault_observed": data[offset] != before, "offset": offset}


def remove_wal(path: str | Path) -> dict[str, Any]:
    wal = Path(str(path) + "-wal")
    existed = wal.exists()
    if existed:
        wal.unlink()
    return {"fault": FAULT_WAL_PAIR, "fault_observed": existed and not wal.exists()}


def pair_main_and_wal(main_source: str | Path, wal_source_db: str | Path, dst: str | Path) -> dict[str, Any]:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(main_source, dst)
    src_wal = Path(str(wal_source_db) + "-wal")
    if not src_wal.exists():
        raise AssertionError("source WAL required")
    shutil.copyfile(src_wal, Path(str(dst) + "-wal"))
    return {"fault": FAULT_WAL_PAIR, "fault_observed": True}


__all__ = [
    "authority_payload", "checkpoint", "connect", "copy_database", "corrupt_effect_digest",
    "corrupt_meta_below_rows", "create_duplicate_active", "create_live_wal_snapshot",
    "database_full_authority", "database_full_effect", "database_full_takeover",
    "delete_effect_rows", "digest", "init_db", "mutate_authority_binding", "mutate_main_byte",
    "mutate_wal_byte", "pair_main_and_wal", "recover_strict", "remove_wal", "truncate_main",
    "truncate_wal", "worker_authority", "worker_consume", "worker_effect", "worker_takeover",
    "write_anchor",
]
