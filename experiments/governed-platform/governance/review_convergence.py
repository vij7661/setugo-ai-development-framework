"""Governance primitives for review convergence and semantic invariant extraction.

These functions are deterministic policy-layer controls. Model output is evidence;
it never grants its own authority.
"""
from __future__ import annotations


def extract_domain_invariants(contract: dict) -> list[str]:
    """Return explicit semantic invariants required before compatibility review.

    Fail closed when the contract does not provide non-empty invariants. The
    platform must not infer consequential domain semantics from implementation
    similarity alone.
    """
    values = contract.get("domain_invariants")
    if not isinstance(values, list):
        raise ValueError("domain_invariants must be an explicit list")
    normalized = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("domain_invariants must contain non-empty strings")
        item = value.strip()
        if item not in normalized:
            normalized.append(item)
    if not normalized:
        raise ValueError("at least one domain invariant is required")
    return normalized


def compatibility_gate(contract: dict, candidate: dict) -> dict:
    """Gate compatibility on explicit preservation of every domain invariant."""
    invariants = extract_domain_invariants(contract)
    preserved = candidate.get("preserved_invariants")
    if not isinstance(preserved, list) or not all(isinstance(x, str) for x in preserved):
        return {"compatible": False, "reason": "candidate invariant evidence is missing or malformed"}
    missing = [item for item in invariants if item not in set(preserved)]
    if missing:
        return {"compatible": False, "reason": "domain invariants not preserved", "missing_invariants": missing}
    return {"compatible": True, "reason": "all explicit domain invariants preserved", "invariants": invariants}


def authorize_model_routing(contract: dict, candidate: dict) -> dict:
    """Authorize routing only after the policy layer recomputes compatibility.

    Callers cannot bypass invariant extraction by presenting an asserted PASS
    receipt. Routing authority is derived from this deterministic gate only.
    """
    gate = compatibility_gate(contract, candidate)
    if not gate["compatible"]:
        return {"authorized": False, "reason": gate["reason"], "gate": gate}
    return {
        "authorized": True,
        "reason": "policy-layer invariant gate passed",
        "gate": gate,
    }


def evaluate_review_convergence(policy: dict, reviews: list[dict]) -> dict:
    """Apply a pre-registered review ceiling and false-positive reviewer demotion.

    The ceiling and threshold must be registered before evaluation. Demoted
    reviewers cannot contribute to convergence. Duplicate reviewer identities are
    counted once so repeated submissions cannot manufacture agreement. Reaching
    the ceiling without sufficient qualified agreement returns HUMAN_REQUIRED.
    """
    ceiling = policy.get("max_reviews")
    threshold = policy.get("false_positive_rate_threshold")
    required_agreement = policy.get("required_qualified_agreement")
    if not isinstance(ceiling, int) or ceiling < 1:
        raise ValueError("max_reviews must be a positive pre-registered integer")
    if not isinstance(required_agreement, int) or required_agreement < 1 or required_agreement > ceiling:
        raise ValueError("required_qualified_agreement must be between 1 and max_reviews")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("false_positive_rate_threshold must be between 0 and 1")

    considered = reviews[:ceiling]
    qualified = []
    demoted = []
    duplicate_reviewers = []
    seen_reviewers = set()
    for review in considered:
        reviewer = review.get("reviewer_id")
        rate = review.get("false_positive_rate")
        if not reviewer or not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
            demoted.append(reviewer or "UNKNOWN")
            continue
        if reviewer in seen_reviewers:
            duplicate_reviewers.append(reviewer)
            continue
        seen_reviewers.add(reviewer)
        if rate > threshold:
            demoted.append(reviewer)
            continue
        qualified.append(review)

    approvals = [r for r in qualified if r.get("verdict") == "PASS"]
    rejections = [r for r in qualified if r.get("verdict") == "FAIL"]
    if len(approvals) >= required_agreement and not rejections:
        decision = "CONVERGED_PASS"
    elif len(rejections) >= required_agreement and not approvals:
        decision = "CONVERGED_FAIL"
    elif len(considered) >= ceiling:
        decision = "HUMAN_REQUIRED"
    else:
        decision = "CONTINUE_REVIEW"
    return {
        "decision": decision,
        "reviews_considered": len(considered),
        "qualified_reviews": len(qualified),
        "demoted_reviewers": demoted,
        "duplicate_reviewers": duplicate_reviewers,
        "ceiling_reached": len(considered) >= ceiling,
    }
