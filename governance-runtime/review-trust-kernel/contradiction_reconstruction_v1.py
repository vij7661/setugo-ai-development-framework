from __future__ import annotations

from collections import defaultdict

PRIORITY = {
    "AUTHORITATIVE_IMPLEMENTATION": 6,
    "AUTHORITATIVE_DESIGN": 5,
    "AUTHORITATIVE_QA": 4,
    "ACCEPTED_DECISION": 3,
    "HISTORICAL_DISCUSSION": 2,
    "NON_AUTHORITATIVE_REASONING": 1,
}


def reconstruct(evidence):
    by_id = {}
    for e in evidence:
        eid=e.get("evidence_id")
        cls=e.get("source_class")
        claim=e.get("claim")
        if not eid or cls not in PRIORITY or claim is None or not e.get("provenance"):
            raise ValueError("malformed evidence")
        if eid in by_id:
            raise ValueError("duplicate evidence_id")
        by_id[eid]=dict(e)

    superseded=set()
    for e in by_id.values():
        for old in e.get("supersedes",[]):
            if old not in by_id:
                raise ValueError("unknown superseded evidence")
            superseded.add(old)

    current=[e for eid,e in by_id.items() if eid not in superseded]
    if not current:
        return {"status":"INSUFFICIENT_EVIDENCE","winner_claim":None,"winner_evidence_ids":[]}

    maxp=max(PRIORITY[e["source_class"]] for e in current)
    top=[e for e in current if PRIORITY[e["source_class"]]==maxp]
    claims=defaultdict(list)
    for e in top:
        claims[e["claim"]].append(e["evidence_id"])

    if len(claims)>1:
        return {
            "status":"UNRESOLVED_CONTRADICTION",
            "winner_claim":None,
            "winner_evidence_ids":[],
            "conflicting_claims":sorted(claims),
            "conflicting_evidence_ids":sorted(e["evidence_id"] for e in top),
        }

    claim=next(iter(claims))
    return {
        "status":"RESOLVED",
        "winner_claim":claim,
        "winner_evidence_ids":sorted(claims[claim]),
        "superseded_evidence_ids":sorted(superseded),
    }
