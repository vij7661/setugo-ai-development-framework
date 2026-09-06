"""EXP-O Pilot 19: external authenticated logical-state integrity checkpoint.

HMAC-SHA256 is used only as a bounded prototype trust boundary. The signing key and
trusted minimum generation are verifier inputs and are never persisted in SQLite.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from sqlite_process_crash_exp_o import deny, digest
from sqlite_storage_fault_exp_o import recover_strict
from sqlite_storage_seal_exp_o import verify_seals

CHECKPOINT_VERSION = "exp-o-pilot19-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def logical_state(path: str | Path) -> dict[str, Any]:
    conn = sqlite3.connect(str(path), timeout=2.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        authorities = []
        for row in conn.execute("SELECT * FROM authority ORDER BY id"):
            authorities.append({
                "id": int(row["id"]), "logical_id": row["logical_id"], "term": int(row["term"]),
                "commit_index": int(row["commit_index"]), "owner": row["owner"], "lease_epoch": int(row["lease_epoch"]),
                "semantic_digest": row["semantic_digest"], "effect_digest": row["effect_digest"],
                "idempotency_key": row["idempotency_key"], "status": row["status"], "result_id": row["result_id"],
            })
        effects = []
        for row in conn.execute("SELECT * FROM effects ORDER BY idempotency_key"):
            effects.append({"idempotency_key": row["idempotency_key"], "effect_digest": row["effect_digest"], "result_id": row["result_id"]})
        meta = conn.execute("SELECT max_term,max_index,max_epoch FROM meta WHERE id=1").fetchone()
        if meta is None:
            raise ValueError("monotonic metadata missing")
        return {
            "authority": authorities,
            "effects": effects,
            "meta": {"max_term": int(meta["max_term"]), "max_index": int(meta["max_index"]), "max_epoch": int(meta["max_epoch"])},
        }
    finally:
        conn.close()


def logical_state_root(path: str | Path) -> str:
    return hashlib.sha256(_canonical(logical_state(path))).hexdigest()


def _unsigned_checkpoint(*, key_id: str, project: str, task: str, logical_state_id: str,
                         generation: int, state_root: str, fence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "version": CHECKPOINT_VERSION,
        "key_id": key_id,
        "project": project,
        "task": task,
        "logical_state_id": logical_state_id,
        "generation": int(generation),
        "state_root": state_root,
        "fence": {
            "term": int(fence["term"]),
            "commit_index": int(fence["commit_index"]),
            "lease_epoch": int(fence["lease_epoch"]),
        },
    }


def _tag(record_without_tag: Mapping[str, Any], key: bytes) -> str:
    return hmac.new(key, _canonical(dict(record_without_tag)), hashlib.sha256).hexdigest()


def issue_checkpoint(path: str | Path, checkpoint_path: str | Path, *, key: bytes, key_id: str,
                     project: str, task: str, logical_state_id: str, generation: int) -> dict[str, Any]:
    state = logical_state(path)
    meta = state["meta"]
    unsigned = _unsigned_checkpoint(
        key_id=key_id, project=project, task=task, logical_state_id=logical_state_id,
        generation=generation, state_root=hashlib.sha256(_canonical(state)).hexdigest(),
        fence={"term": meta["max_term"], "commit_index": meta["max_index"], "lease_epoch": meta["max_epoch"]},
    )
    record = dict(unsigned)
    record["auth_tag"] = _tag(unsigned, key)
    Path(checkpoint_path).write_bytes(_canonical(record))
    return record


def load_checkpoint(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_checkpoint(path: str | Path, record: Mapping[str, Any]) -> None:
    Path(path).write_bytes(_canonical(dict(record)))


def verify_checkpoint(db_path: str | Path, checkpoint_path: str | Path | None, *, trusted_keys: Mapping[str, bytes],
                      expected_project: str, expected_task: str, expected_logical_state_id: str,
                      minimum_generation: int) -> dict[str, Any]:
    if checkpoint_path is None or not Path(checkpoint_path).exists():
        return deny("EXTERNAL_CHECKPOINT_MISSING", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    try:
        record = load_checkpoint(checkpoint_path)
    except Exception as exc:
        return deny("EXTERNAL_CHECKPOINT_MALFORMED", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False, error=str(exc))
    required = {"version", "key_id", "project", "task", "logical_state_id", "generation", "state_root", "fence", "auth_tag"}
    if not required.issubset(record):
        return deny("EXTERNAL_CHECKPOINT_INCOMPLETE", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    key_id = str(record["key_id"])
    key = trusted_keys.get(key_id)
    if key is None:
        return deny("EXTERNAL_CHECKPOINT_UNKNOWN_KEY", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    unsigned = {k: record[k] for k in record if k != "auth_tag"}
    expected_tag = _tag(unsigned, key)
    if not hmac.compare_digest(str(record["auth_tag"]), expected_tag):
        return deny("EXTERNAL_CHECKPOINT_AUTH_FAILED", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    if record["version"] != CHECKPOINT_VERSION:
        return deny("EXTERNAL_CHECKPOINT_VERSION_MISMATCH", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    if str(record["project"]) != expected_project or str(record["task"]) != expected_task or str(record["logical_state_id"]) != expected_logical_state_id:
        return deny("EXTERNAL_CHECKPOINT_SCOPE_MISMATCH", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    try:
        generation = int(record["generation"])
    except Exception:
        return deny("EXTERNAL_CHECKPOINT_GENERATION_INVALID", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    if generation < int(minimum_generation):
        return deny("EXTERNAL_CHECKPOINT_ROLLBACK", recovery_status="TRUSTED_GENERATION_ROLLBACK_BLOCKED", external_integrity=False,
                    observed_generation=generation, minimum_generation=int(minimum_generation))
    try:
        state = logical_state(db_path)
    except Exception as exc:
        return deny("LOGICAL_STATE_UNREADABLE", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False, error=str(exc))
    actual_root = hashlib.sha256(_canonical(state)).hexdigest()
    if not hmac.compare_digest(str(record["state_root"]), actual_root):
        return deny("EXTERNAL_STATE_ROOT_MISMATCH", recovery_status="EXTERNAL_INTEGRITY_MISMATCH", external_integrity=False,
                    checkpoint_root=str(record["state_root"]), actual_root=actual_root)
    meta = state["meta"]
    f = record["fence"]
    try:
        checkpoint_fence = (int(f["term"]), int(f["commit_index"]), int(f["lease_epoch"]))
        actual_fence = (int(meta["max_term"]), int(meta["max_index"]), int(meta["max_epoch"]))
    except Exception:
        return deny("EXTERNAL_CHECKPOINT_FENCE_INVALID", recovery_status="EXTERNAL_INTEGRITY_UNVERIFIED", external_integrity=False)
    if checkpoint_fence != actual_fence:
        return deny("EXTERNAL_CHECKPOINT_FENCE_MISMATCH", recovery_status="EXTERNAL_INTEGRITY_MISMATCH", external_integrity=False)
    return {"authorized": False, "decision": "EXTERNAL_CHECKPOINT_VERIFIED", "external_integrity": True,
            "generation": generation, "state_root": actual_root, "fence": checkpoint_fence}


def recover_external(db_path: str | Path, checkpoint_path: str | Path | None, *, trusted_keys: Mapping[str, bytes],
                     expected_project: str, expected_task: str, expected_logical_state_id: str,
                     minimum_generation: int) -> dict[str, Any]:
    local = verify_seals(db_path)
    if not local.get("ok"):
        return deny(str(local.get("reason", "LOCAL_INTEGRITY_FAILED")), recovery_status="LOCAL_INTEGRITY_UNVERIFIED",
                    external_integrity=False, local_integrity=False, integrity_evidence=local)
    ext = verify_checkpoint(db_path, checkpoint_path, trusted_keys=trusted_keys, expected_project=expected_project,
                            expected_task=expected_task, expected_logical_state_id=expected_logical_state_id,
                            minimum_generation=minimum_generation)
    if not ext.get("external_integrity"):
        ext["local_integrity"] = True
        return ext
    result = recover_strict(db_path)
    result["local_integrity"] = True
    result["external_integrity"] = True
    result["checkpoint_generation"] = ext["generation"]
    result["checkpoint_state_root"] = ext["state_root"]
    return result


__all__ = ["CHECKPOINT_VERSION", "issue_checkpoint", "load_checkpoint", "logical_state", "logical_state_root",
           "recover_external", "verify_checkpoint", "write_checkpoint"]
