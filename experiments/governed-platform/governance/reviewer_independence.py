"""Reviewer-independence controls for governed verification."""
from __future__ import annotations


def reviewer_lineage(review: dict) -> tuple:
    return (
        review.get("provider"),
        review.get("model"),
        review.get("sku"),
        review.get("qualification_ref"),
        review.get("prompt_lineage"),
        review.get("context_lineage"),
    )


def verify_independent_reviews(reviews: list[dict], required_independent: int = 2) -> dict:
    """Require genuinely distinct reviewer lineages, not merely different IDs."""
    if not isinstance(required_independent, int) or required_independent < 1:
        raise ValueError("required_independent must be a positive integer")
    usable = []
    seen_ids = set()
    seen_lineages = set()
    correlated = []
    for review in reviews:
        reviewer_id = review.get("reviewer_id")
        lineage = reviewer_lineage(review)
        if not reviewer_id or any(part in (None, "") for part in lineage):
            correlated.append(reviewer_id or "UNKNOWN")
            continue
        if reviewer_id in seen_ids or lineage in seen_lineages:
            correlated.append(reviewer_id)
            continue
        seen_ids.add(reviewer_id)
        seen_lineages.add(lineage)
        usable.append(review)
    passes = len(usable) >= required_independent
    return {
        "independent": passes,
        "independent_count": len(usable),
        "required_independent": required_independent,
        "correlated_or_invalid_reviewers": correlated,
    }
