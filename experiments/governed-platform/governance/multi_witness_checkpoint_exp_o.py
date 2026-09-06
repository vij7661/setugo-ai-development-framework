"""EXP-O Pilot 20: bounded 2-of-3 independently keyed checkpoint witnesses."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from external_integrity_anchor_exp_o import logical_state
from sqlite_process_crash_exp_o import deny
from sqlite_storage_fault_exp_o import recover_strict
from sqlite_storage_seal_exp_o import verify_seals

VERSION = "exp-o-pilot20-v1"
THRESHOLD = 2


def _canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode("utf-8")


def statement_for_db(path: str | Path, *, project: str, task: str, logical_state_id: str, generation: int) -> dict[str, Any]:
    state = logical_state(path)
    meta = state["meta"]
    return {
        "version": VERSION,
        "project": project,
        "task": task,
        "logical_state_id": logical_state_id,
        "generation": int(generation),
        "state_root": hashlib.sha256(_canonical(state)).hexdigest(),
        "fence": {"term": int(meta["max_term"]), "commit_index": int(meta["max_index"]), "lease_epoch": int(meta["max_epoch"])},
    }


def statement_digest(statement: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(dict(statement))).hexdigest()


def sign_witness(statement: Mapping[str, Any], *, witness_id: str, key_id: str, key: bytes) -> dict[str, Any]:
    sd = statement_digest(statement)
    unsigned = {"witness_id": witness_id, "key_id": key_id, "statement_digest": sd}
    tag = hmac.new(key, _canonical(unsigned), hashlib.sha256).hexdigest()
    return {**unsigned, "auth_tag": tag, "statement": dict(statement)}


def _verify_record(record: Mapping[str, Any], *, witness_config: Mapping[str, Mapping[str, Any]]) -> tuple[bool, str, str | None, dict[str, Any] | None]:
    try:
        witness_id = str(record["witness_id"]); key_id = str(record["key_id"])
        sd = str(record["statement_digest"]); tag = str(record["auth_tag"]); statement = dict(record["statement"])
    except Exception:
        return False, "WITNESS_RECORD_MALFORMED", None, None
    cfg = witness_config.get(witness_id)
    if cfg is None:
        return False, "UNKNOWN_WITNESS", witness_id, None
    if bool(cfg.get("revoked", False)):
        return False, "REVOKED_WITNESS", witness_id, None
    if str(cfg.get("key_id")) != key_id:
        return False, "WITNESS_KEY_SUBSTITUTION", witness_id, None
    key = cfg.get("key")
    if not isinstance(key, (bytes, bytearray)):
        return False, "WITNESS_KEY_UNAVAILABLE", witness_id, None
    actual_sd = statement_digest(statement)
    if not hmac.compare_digest(sd, actual_sd):
        return False, "WITNESS_STATEMENT_DIGEST_MISMATCH", witness_id, None
    unsigned = {"witness_id": witness_id, "key_id": key_id, "statement_digest": sd}
    expected = hmac.new(bytes(key), _canonical(unsigned), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(tag, expected):
        return False, "WITNESS_AUTH_FAILED", witness_id, None
    return True, "VALID", witness_id, statement


def verify_quorum(db_path: str | Path, records: Sequence[Mapping[str, Any]], *, witness_config: Mapping[str, Mapping[str, Any]],
                  expected_project: str, expected_task: str, expected_logical_state_id: str,
                  minimum_generation: int) -> dict[str, Any]:
    if len(witness_config) != 3:
        return deny("WITNESS_CONFIGURATION_INVALID", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False)
    groups: dict[str, dict[str, Any]] = {}
    invalid: list[str] = []
    for record in records:
        ok, reason, wid, stmt = _verify_record(record, witness_config=witness_config)
        if not ok or wid is None or stmt is None:
            invalid.append(reason); continue
        sd = statement_digest(stmt)
        g = groups.setdefault(sd, {"statement": stmt, "witnesses": set()})
        g["witnesses"].add(wid)
    candidates = [g for g in groups.values() if len(g["witnesses"]) >= THRESHOLD]
    if not candidates:
        return deny("WITNESS_QUORUM_INSUFFICIENT", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False,
                    valid_statement_groups={k: len(v["witnesses"]) for k, v in groups.items()}, invalid_records=invalid)
    if len(candidates) != 1:
        return deny("MULTIPLE_CONFLICTING_WITNESS_QUORUMS", recovery_status="WITNESS_EQUIVOCATION", witness_quorum=False)
    stmt = candidates[0]["statement"]
    voters = sorted(candidates[0]["witnesses"])
    if stmt.get("version") != VERSION:
        return deny("WITNESS_STATEMENT_VERSION_MISMATCH", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False)
    if str(stmt.get("project")) != expected_project or str(stmt.get("task")) != expected_task or str(stmt.get("logical_state_id")) != expected_logical_state_id:
        return deny("WITNESS_STATEMENT_SCOPE_MISMATCH", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False)
    try:
        generation = int(stmt["generation"])
    except Exception:
        return deny("WITNESS_STATEMENT_GENERATION_INVALID", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False)
    if generation < int(minimum_generation):
        return deny("WITNESS_QUORUM_ROLLBACK", recovery_status="TRUSTED_GENERATION_ROLLBACK_BLOCKED", witness_quorum=False,
                    observed_generation=generation, minimum_generation=int(minimum_generation))
    try:
        state = logical_state(db_path)
    except Exception as exc:
        return deny("LOGICAL_STATE_UNREADABLE", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False, error=str(exc))
    actual_root = hashlib.sha256(_canonical(state)).hexdigest()
    if not hmac.compare_digest(str(stmt.get("state_root")), actual_root):
        return deny("WITNESS_STATE_ROOT_MISMATCH", recovery_status="WITNESS_QUORUM_MISMATCH", witness_quorum=False)
    meta = state["meta"]
    try:
        f = stmt["fence"]
        signed_fence = (int(f["term"]), int(f["commit_index"]), int(f["lease_epoch"]))
        actual_fence = (int(meta["max_term"]), int(meta["max_index"]), int(meta["max_epoch"]))
    except Exception:
        return deny("WITNESS_FENCE_INVALID", recovery_status="WITNESS_QUORUM_UNVERIFIED", witness_quorum=False)
    if signed_fence != actual_fence:
        return deny("WITNESS_FENCE_MISMATCH", recovery_status="WITNESS_QUORUM_MISMATCH", witness_quorum=False)
    return {"authorized": False, "decision": "WITNESS_QUORUM_VERIFIED", "witness_quorum": True,
            "voters": voters, "generation": generation, "state_root": actual_root, "statement_digest": statement_digest(stmt)}


def recover_multi_witness(db_path: str | Path, records: Sequence[Mapping[str, Any]], *, witness_config: Mapping[str, Mapping[str, Any]],
                          expected_project: str, expected_task: str, expected_logical_state_id: str,
                          minimum_generation: int) -> dict[str, Any]:
    local = verify_seals(db_path)
    if not local.get("ok"):
        return deny(str(local.get("reason", "LOCAL_INTEGRITY_FAILED")), recovery_status="LOCAL_INTEGRITY_UNVERIFIED",
                    local_integrity=False, witness_quorum=False)
    q = verify_quorum(db_path, records, witness_config=witness_config, expected_project=expected_project,
                      expected_task=expected_task, expected_logical_state_id=expected_logical_state_id,
                      minimum_generation=minimum_generation)
    if not q.get("witness_quorum"):
        q["local_integrity"] = True
        return q
    r = recover_strict(db_path)
    r["local_integrity"] = True
    r["witness_quorum"] = True
    r["witness_voters"] = q["voters"]
    r["checkpoint_generation"] = q["generation"]
    r["witness_statement_digest"] = q["statement_digest"]
    return r


__all__ = ["THRESHOLD", "VERSION", "recover_multi_witness", "sign_witness", "statement_digest", "statement_for_db", "verify_quorum"]
