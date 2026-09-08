from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Set


CONTEXT_ONLY = "CONTEXT_ONLY"
GOVERNED_EVIDENCE = "GOVERNED_EVIDENCE"
VALID_AUTHORITY_CLASSES = {CONTEXT_ONLY, GOVERNED_EVIDENCE}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def validate_memory_item(item: Dict[str, Any]) -> None:
    if not isinstance(item, dict):
        raise ValueError("memory item must be object")
    authority_class = item.get("authority_class")
    if authority_class not in VALID_AUTHORITY_CLASSES:
        raise ValueError("unknown or missing memory authority_class")
    if not item.get("memory_id"):
        raise ValueError("memory_id required")
    if authority_class == GOVERNED_EVIDENCE:
        required = {"evidence_id", "provenance", "content_sha256"}
        missing = sorted(k for k in required if not item.get(k))
        if missing:
            raise ValueError(f"governed memory evidence missing: {','.join(missing)}")


def admissible_evidence_ids(frozen_evidence: Iterable[Dict[str, Any]], memory_items: Iterable[Dict[str, Any]]) -> Set[str]:
    ids: Set[str] = set()
    for evidence in frozen_evidence:
        evidence_id = evidence.get("evidence_id")
        if evidence_id:
            ids.add(str(evidence_id))
    for item in memory_items:
        validate_memory_item(item)
        if item["authority_class"] == GOVERNED_EVIDENCE:
            ids.add(str(item["evidence_id"]))
    return ids


def evaluate_admissibility(
    *,
    mandatory_evidence_ids: Iterable[str],
    frozen_evidence: Iterable[Dict[str, Any]],
    memory_items: Iterable[Dict[str, Any]],
    frozen_disposition: str,
) -> Dict[str, Any]:
    memory = list(memory_items)
    for item in memory:
        validate_memory_item(item)
    admissible = admissible_evidence_ids(frozen_evidence, memory)
    mandatory = sorted(set(str(x) for x in mandatory_evidence_ids))
    missing = [e for e in mandatory if e not in admissible]

    context_only_ids = sorted(item["memory_id"] for item in memory if item["authority_class"] == CONTEXT_ONLY)
    governed_memory_ids = sorted(item["memory_id"] for item in memory if item["authority_class"] == GOVERNED_EVIDENCE)

    promotable = frozen_disposition == "PASS" and not missing
    result = {
        "mandatory_evidence_ids": mandatory,
        "admissible_evidence_ids": sorted(admissible),
        "missing_mandatory_evidence_ids": missing,
        "context_only_memory_ids": context_only_ids,
        "governed_memory_evidence_ids": governed_memory_ids,
        "frozen_disposition": frozen_disposition,
        "promotable": promotable,
        "memory_independent_authority": False,
    }
    result["decision_sha256"] = sha256_json(result)
    return result


def evidence_winner(*, frozen_claim: str, memory_claims: List[Dict[str, Any]]) -> str:
    for item in memory_claims:
        validate_memory_item(item)
    # Context-only memory never overrides frozen governed evidence.
    return frozen_claim
