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
    """Authorize routing only after the policy layer recomputes compatibility."""
    gate = compatibility_gate(contract, candidate)
    if not gate["compatible"]:
        return {"authorized": False, "reason": gate["reason"], "gate": gate}
    return {"authorized": True, "reason": "policy-layer invariant gate passed", "gate": gate}


def _performance_index(records: list[dict], role: str, task_class: str) -> dict[str, dict]:
    """Build reviewer performance from independently adjudicated evidence only."""
    index: dict[str, dict] = {}
    for record in records:
        reviewer = record.get("reviewer_id")
        rate = record.get("false_positive_rate")
        if not reviewer or not record.get("independently_adjudicated", False):
            continue
        if record.get("role") != role or record.get("task_class") != task_class:
            continue
        if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
            continue
        if not record.get("evidence_ref") or not isinstance(record.get("performance_epoch"), int):
            continue
        prior = index.get(reviewer)
        if prior is None or record["performance_epoch"] > prior["performance_epoch"]:
            index[reviewer] = record
    return index


def evaluate_review_convergence(policy: dict, reviews: list[dict], performance_records: list[dict] | None = None) -> dict:
    """Apply review convergence using externally adjudicated reviewer performance.

    Reviewers cannot self-report the metric that determines their own eligibility.
    Performance evidence is scoped to role/task class and must be independently
    adjudicated, versioned by performance_epoch, and linked to evidence_ref.
    """
    ceiling = policy.get("max_reviews")
    threshold = policy.get("false_positive_rate_threshold")
    required_agreement = policy.get("required_qualified_agreement")
    role = policy.get("review_role")
    task_class = policy.get("task_class")
    if not isinstance(ceiling, int) or ceiling < 1:
        raise ValueError("max_reviews must be a positive pre-registered integer")
    if not isinstance(required_agreement, int) or required_agreement < 1 or required_agreement > ceiling:
        raise ValueError("required_qualified_agreement must be between 1 and max_reviews")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("false_positive_rate_threshold must be between 0 and 1")
    if not isinstance(role, str) or not role or not isinstance(task_class, str) or not task_class:
        raise ValueError("review_role and task_class must be pre-registered")

    performance = _performance_index(performance_records or [], role, task_class)
    considered = reviews[:ceiling]
    qualified = []
    demoted = []
    missing_performance_evidence = []
    duplicate_reviewers = []
    seen_reviewers = set()
    for review in considered:
        reviewer = review.get("reviewer_id")
        if not reviewer:
            demoted.append("UNKNOWN")
            continue
        if reviewer in seen_reviewers:
            duplicate_reviewers.append(reviewer)
            continue
        seen_reviewers.add(reviewer)
        record = performance.get(reviewer)
        if record is None:
            missing_performance_evidence.append(reviewer)
            demoted.append(reviewer)
            continue
        if record["false_positive_rate"] > threshold:
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
        decision = "CEILING_REACHED_ESCALATE"
    else:
        decision = "CONTINUE_REVIEW"
    return {
        "decision": decision,
        "reviews_considered": len(considered),
        "qualified_reviews": len(qualified),
        "demoted_reviewers": demoted,
        "missing_performance_evidence": missing_performance_evidence,
        "duplicate_reviewers": duplicate_reviewers,
        "ceiling_reached": len(considered) >= ceiling,
    }
