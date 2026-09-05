"""Tamper-evident evidence chaining for EXP-F F007."""
from __future__ import annotations

import hashlib
import json


def _canonical_payload(record: dict) -> dict:
    return {k: v for k, v in record.items() if k not in {"record_hash"}}


def compute_record_hash(record: dict) -> str:
    payload = json.dumps(_canonical_payload(record), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append_evidence_record(chain: list[dict], record: dict) -> dict:
    required = ("evidence_id", "project_id", "task_id", "execution_sha", "evidence_type", "content_hash")
    missing = [k for k in required if record.get(k) in (None, "")]
    if missing:
        return {"accepted": False, "reason": "missing evidence fields: " + ",".join(missing)}
    if not isinstance(chain, list) or not all(isinstance(x, dict) for x in chain):
        return {"accepted": False, "reason": "evidence chain malformed"}
    if any(x.get("evidence_id") == record["evidence_id"] for x in chain):
        return {"accepted": False, "reason": "duplicate evidence identity"}
    previous_hash = chain[-1].get("record_hash") if chain else "GENESIS"
    if chain and not previous_hash:
        return {"accepted": False, "reason": "previous record hash missing"}
    stored = dict(record)
    stored["sequence"] = len(chain)
    stored["previous_hash"] = previous_hash
    stored["record_hash"] = compute_record_hash(stored)
    return {"accepted": True, "reason": "evidence appended", "record": stored, "chain": [*chain, stored]}


def verify_evidence_chain(chain: list[dict], required_ids: set[str] | None = None) -> dict:
    if not isinstance(chain, list) or not all(isinstance(x, dict) for x in chain):
        return {"valid": False, "reason": "evidence chain malformed"}
    seen = set()
    previous_hash = "GENESIS"
    for index, record in enumerate(chain):
        evidence_id = record.get("evidence_id")
        if not evidence_id or evidence_id in seen:
            return {"valid": False, "reason": "missing or duplicate evidence identity", "index": index}
        seen.add(evidence_id)
        if record.get("sequence") != index:
            return {"valid": False, "reason": "evidence sequence mismatch", "index": index}
        if record.get("previous_hash") != previous_hash:
            return {"valid": False, "reason": "evidence chain link mismatch", "index": index}
        expected_hash = compute_record_hash(record)
        if record.get("record_hash") != expected_hash:
            return {"valid": False, "reason": "evidence record tampered", "index": index}
        previous_hash = record["record_hash"]
    required = required_ids or set()
    missing = sorted(required - seen)
    if missing:
        return {"valid": False, "reason": "required evidence missing", "missing": missing}
    return {"valid": True, "reason": "evidence chain verified", "head_hash": previous_hash, "evidence_ids": sorted(seen)}
