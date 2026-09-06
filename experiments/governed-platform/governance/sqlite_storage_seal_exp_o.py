"""Application-level integrity seals for EXP-O Pilot 18 disposable SQLite copies."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from sqlite_process_crash_exp_o import digest, deny
from sqlite_storage_fault_exp_o import connect, init_db, recover_strict


def init_sealed_db(path: str | Path) -> None:
    init_db(path)
    conn = connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS integrity_seals (kind TEXT NOT NULL, object_key TEXT NOT NULL, object_digest TEXT NOT NULL, PRIMARY KEY(kind,object_key))")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def _authority_obj(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": int(row["id"]), "logical_id": row["logical_id"], "term": int(row["term"]),
        "commit_index": int(row["commit_index"]), "owner": row["owner"], "lease_epoch": int(row["lease_epoch"]),
        "semantic_digest": row["semantic_digest"], "effect_digest": row["effect_digest"],
        "idempotency_key": row["idempotency_key"], "status": row["status"], "result_id": row["result_id"],
    }


def _effect_obj(row: sqlite3.Row) -> dict[str, Any]:
    return {"idempotency_key": row["idempotency_key"], "effect_digest": row["effect_digest"], "result_id": row["result_id"]}


def _meta_obj(row: sqlite3.Row) -> dict[str, Any]:
    return {"max_term": int(row["max_term"]), "max_index": int(row["max_index"]), "max_epoch": int(row["max_epoch"])}


def seal_state(path: str | Path) -> dict[str, int]:
    """Replace seals with digests of the current committed application state."""
    conn = connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS integrity_seals (kind TEXT NOT NULL, object_key TEXT NOT NULL, object_digest TEXT NOT NULL, PRIMARY KEY(kind,object_key))")
        auth = conn.execute("SELECT * FROM authority ORDER BY id").fetchall()
        effects = conn.execute("SELECT * FROM effects ORDER BY idempotency_key").fetchall()
        meta = conn.execute("SELECT max_term,max_index,max_epoch FROM meta WHERE id=1").fetchone()
        if meta is None:
            raise AssertionError("meta row required before sealing")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM integrity_seals")
        for row in auth:
            conn.execute("INSERT INTO integrity_seals(kind,object_key,object_digest) VALUES(?,?,?)", ("authority", str(row["id"]), digest(_authority_obj(row))))
        for row in effects:
            conn.execute("INSERT INTO integrity_seals(kind,object_key,object_digest) VALUES(?,?,?)", ("effect", str(row["idempotency_key"]), digest(_effect_obj(row))))
        conn.execute("INSERT INTO integrity_seals(kind,object_key,object_digest) VALUES(?,?,?)", ("meta", "1", digest(_meta_obj(meta))))
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        return {"authority": len(auth), "effects": len(effects), "meta": 1}
    finally:
        conn.close()


def verify_seals(path: str | Path) -> dict[str, Any]:
    db = Path(path)
    if not db.exists():
        return {"ok": False, "reason": "DATABASE_MISSING"}
    try:
        conn = sqlite3.connect(str(db), timeout=2.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            quick = [str(r[0]) for r in conn.execute("PRAGMA quick_check").fetchall()]
            if quick != ["ok"]:
                return {"ok": False, "reason": "SQLITE_INTEGRITY_CHECK_FAILED", "integrity": quick[:8]}
            tables = {str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "integrity_seals" not in tables:
                return {"ok": False, "reason": "INTEGRITY_SEALS_MISSING"}
            seals = {(str(r["kind"]), str(r["object_key"])): str(r["object_digest"]) for r in conn.execute("SELECT * FROM integrity_seals")}
            auth = conn.execute("SELECT * FROM authority ORDER BY id").fetchall()
            effects = conn.execute("SELECT * FROM effects ORDER BY idempotency_key").fetchall()
            meta = conn.execute("SELECT max_term,max_index,max_epoch FROM meta WHERE id=1").fetchone()
            if meta is None:
                return {"ok": False, "reason": "MONOTONIC_METADATA_MISSING"}
            actual: dict[tuple[str, str], str] = {}
            for row in auth:
                actual[("authority", str(row["id"]))] = digest(_authority_obj(row))
            for row in effects:
                actual[("effect", str(row["idempotency_key"]))] = digest(_effect_obj(row))
            actual[("meta", "1")] = digest(_meta_obj(meta))
            if set(actual) != set(seals):
                return {"ok": False, "reason": "SEALED_OBJECT_SET_MISMATCH", "expected_count": len(seals), "actual_count": len(actual)}
            mismatched = sorted(f"{k[0]}:{k[1]}" for k, value in actual.items() if seals.get(k) != value)
            if mismatched:
                return {"ok": False, "reason": "SEALED_OBJECT_DIGEST_MISMATCH", "objects": mismatched[:8]}
            return {"ok": True, "sealed_objects": len(actual)}
        except sqlite3.Error as exc:
            return {"ok": False, "reason": "SQLITE_SEAL_VERIFICATION_ERROR", "error": str(exc)}
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return {"ok": False, "reason": "DATABASE_OPEN_FAILED", "error": str(exc)}


def recover_sealed(path: str | Path, anchor_path: str | Path | None = None) -> dict[str, Any]:
    integrity = verify_seals(path)
    if not integrity.get("ok"):
        return deny(str(integrity.get("reason", "STORAGE_INTEGRITY_UNKNOWN")), recovery_status="STORAGE_CORRUPT", storage_integrity=False, integrity_evidence=integrity)
    result = recover_strict(path, anchor_path)
    result["seal_integrity"] = True
    return result


__all__ = ["init_sealed_db", "recover_sealed", "seal_state", "verify_seals"]
