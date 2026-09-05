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
        review.get("foundation_lineage"),
    )


def verify_independent_reviews(reviews: list[dict], required_independent: int = 2, *, require_foundation_diversity: bool = True) -> dict:
    """Require genuinely distinct reviewer lineages, not merely different IDs/paths."""
    if not isinstance(required_independent, int) or required_independent < 1:
        raise ValueError("required_independent must be a positive integer")
    usable = []
    seen_ids = set()
    seen_lineages = set()
    seen_foundations = set()
    correlated = []
    for review in reviews:
        reviewer_id = review.get("reviewer_id")
        lineage = reviewer_lineage(review)
        foundation = review.get("foundation_lineage")
        if not reviewer_id or any(part in (None, "") for part in lineage):
            correlated.append(reviewer_id or "UNKNOWN")
            continue
        if reviewer_id in seen_ids or lineage in seen_lineages:
            correlated.append(reviewer_id)
            continue
        if require_foundation_diversity and foundation in seen_foundations:
            correlated.append(reviewer_id)
            continue
        seen_ids.add(reviewer_id)
        seen_lineages.add(lineage)
        seen_foundations.add(foundation)
        usable.append(review)
    passes = len(usable) >= required_independent
    return {
        "independent": passes,
        "independent_count": len(usable),
        "required_independent": required_independent,
        "correlated_or_invalid_reviewers": correlated,
        "foundation_diversity_required": require_foundation_diversity,
    }
