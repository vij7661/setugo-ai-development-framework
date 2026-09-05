"""Deterministic semantic-invariant controls for EXP-F/F006.

Natural-language models may propose semantic claims, but authority is granted only
from explicit policy-owned canonical predicates. Synonyms/wording are evidence;
they never define the governing meaning themselves.
"""
from __future__ import annotations

import hashlib
import json

_ALLOWED_STRENGTH = {"MUST", "MUST_NOT"}
_ALLOWED_POLARITY = {"REQUIRE", "FORBID"}


def _stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_structured_invariants(contract: dict) -> dict:
    """Validate and freeze policy-owned semantic invariants.

    Each invariant must carry a canonical predicate. Ambiguous or incomplete
    semantic policy fails closed rather than being inferred from prose.
    """
    values = contract.get("semantic_invariants")
    if not isinstance(values, list) or not values:
        raise ValueError("semantic_invariants must be a non-empty explicit list")

    seen_ids: set[str] = set()
    normalized: list[dict] = []
    for raw in values:
        if not isinstance(raw, dict):
            raise ValueError("each semantic invariant must be an object")
        invariant_id = raw.get("id")
        strength = raw.get("strength")
        predicate = raw.get("predicate")
        source = raw.get("source")
        scope = raw.get("scope")
        if not isinstance(invariant_id, str) or not invariant_id.strip():
            raise ValueError("semantic invariant id is required")
        if invariant_id in seen_ids:
            raise ValueError("semantic invariant ids must be unique")
        if strength not in _ALLOWED_STRENGTH:
            raise ValueError("semantic invariant strength must be MUST or MUST_NOT")
        if not isinstance(predicate, dict):
            raise ValueError("semantic invariant predicate is required")
        subject = predicate.get("subject")
        action = predicate.get("action")
        polarity = predicate.get("polarity")
        if not all(isinstance(x, str) and x.strip() for x in (subject, action)):
            raise ValueError("semantic predicate subject/action are required")
        if polarity not in _ALLOWED_POLARITY:
            raise ValueError("semantic predicate polarity must be REQUIRE or FORBID")
        expected = "REQUIRE" if strength == "MUST" else "FORBID"
        if polarity != expected:
            raise ValueError("semantic predicate polarity conflicts with normative strength")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("semantic invariant source is required")
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError("semantic invariant scope is required")
        if raw.get("ambiguous") is True:
            raise ValueError("ambiguous semantic invariant requires adjudication")

        seen_ids.add(invariant_id)
        normalized.append(
            {
                "id": invariant_id,
                "source": source.strip(),
                "scope": scope.strip(),
                "strength": strength,
                "predicate": {
                    "subject": subject.strip(),
                    "action": action.strip(),
                    "polarity": polarity,
                },
            }
        )

    return {"invariants": normalized, "invariant_hash": _stable_hash(normalized)}


def semantic_compatibility_gate(contract: dict, candidate: dict) -> dict:
    """Compare candidate semantic claims to canonical predicates, not wording."""
    frozen = extract_structured_invariants(contract)
    claims = candidate.get("semantic_claims")
    if not isinstance(claims, list) or not claims:
        return {"compatible": False, "reason": "candidate semantic claims missing or malformed"}

    indexed: dict[tuple[str, str], set[str]] = {}
    malformed = []
    for claim in claims:
        if not isinstance(claim, dict):
            malformed.append(claim)
            continue
        subject = claim.get("subject")
        action = claim.get("action")
        polarity = claim.get("polarity")
        if not (isinstance(subject, str) and isinstance(action, str) and polarity in _ALLOWED_POLARITY):
            malformed.append(claim)
            continue
        indexed.setdefault((subject.strip(), action.strip()), set()).add(polarity)
    if malformed:
        return {"compatible": False, "reason": "candidate semantic claims malformed"}

    missing = []
    contradictions = []
    for invariant in frozen["invariants"]:
        predicate = invariant["predicate"]
        key = (predicate["subject"], predicate["action"])
        observed = indexed.get(key, set())
        expected = predicate["polarity"]
        opposite = "FORBID" if expected == "REQUIRE" else "REQUIRE"
        if opposite in observed:
            contradictions.append(
                {
                    "invariant_id": invariant["id"],
                    "subject": key[0],
                    "action": key[1],
                    "expected": expected,
                    "observed": opposite,
                }
            )
        if expected not in observed:
            missing.append(invariant["id"])

    if contradictions:
        return {
            "compatible": False,
            "reason": "semantic contradiction detected",
            "contradictions": contradictions,
            "missing_invariants": missing,
            "invariant_hash": frozen["invariant_hash"],
        }
    if missing:
        return {
            "compatible": False,
            "reason": "semantic invariants not demonstrated",
            "missing_invariants": missing,
            "invariant_hash": frozen["invariant_hash"],
        }
    return {
        "compatible": True,
        "reason": "all canonical semantic predicates preserved",
        "invariant_hash": frozen["invariant_hash"],
        "invariant_ids": [x["id"] for x in frozen["invariants"]],
    }


def authorize_semantic_routing(contract: dict, candidate: dict) -> dict:
    gate = semantic_compatibility_gate(contract, candidate)
    return {
        "authorized": bool(gate["compatible"]),
        "reason": "policy-layer semantic invariant gate passed" if gate["compatible"] else gate["reason"],
        "gate": gate,
    }
