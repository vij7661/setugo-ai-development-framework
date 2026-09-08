from __future__ import annotations

import hashlib
import json

_ALLOWED_CORE = {
    "schema_version",
    "review_id",
    "candidate_sha",
    "base_sha",
    "decision_target",
    "evidence",
    "blind_review_required",
}

_FORBIDDEN_BLIND = {
    "proposer_identity",
    "proposer_name",
    "proposer_conclusion",
    "recommended_disposition",
    "prior_reviewer_verdict",
    "reviewer_consensus",
    "promotion_state",
    "approval_status",
    "senior_approval",
}


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(obj):
    return hashlib.sha256(_canon(obj)).hexdigest()


def build_reviewer_packet(source_packet: dict) -> dict:
    if not isinstance(source_packet, dict):
        raise ValueError("source_packet must be object")
    required = {"review_id", "candidate_sha", "base_sha", "decision_target", "evidence", "blind_review_required"}
    missing = sorted(required - set(source_packet))
    if missing:
        raise ValueError(f"missing required fields: {missing}")

    unknown = sorted(set(source_packet) - _ALLOWED_CORE - _FORBIDDEN_BLIND)
    if unknown:
        raise ValueError(f"unknown fields fail closed: {unknown}")

    blind = bool(source_packet["blind_review_required"])
    packet = {
        "schema_version": 1,
        "review_id": source_packet["review_id"],
        "candidate_sha": source_packet["candidate_sha"],
        "base_sha": source_packet["base_sha"],
        "decision_target": source_packet["decision_target"],
        "evidence": source_packet["evidence"],
        "blind_review_required": blind,
    }

    if not blind:
        for key in sorted(_FORBIDDEN_BLIND):
            if key in source_packet:
                packet[key] = source_packet[key]

    packet["packet_sha256"] = _sha(packet)
    return packet


def validate_blind_packet(packet: dict) -> dict:
    blind = bool(packet.get("blind_review_required"))
    leaked = sorted(k for k in _FORBIDDEN_BLIND if k in packet)
    valid = not (blind and leaked)
    result = {
        "blind_review_required": blind,
        "leaked_anchor_fields": leaked,
        "valid": valid,
        "decision_target_sha256": hashlib.sha256(str(packet.get("decision_target", "")).encode("utf-8")).hexdigest(),
        "evidence_sha256": _sha(packet.get("evidence", [])),
    }
    result["validation_sha256"] = _sha(result)
    return result
