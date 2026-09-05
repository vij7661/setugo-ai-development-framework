from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class TriggerCase:
    case_id: str
    r1_correct: bool
    semantic_entropy: float | None
    sample_sufficient: bool
    policy_review_required: bool


@dataclass(frozen=True)
class StrategyResult:
    strategy: str
    reviewed_case_ids: tuple[str, ...]
    finalized_at_r1_case_ids: tuple[str, ...]
    r1_false_green_case_ids: tuple[str, ...]
    unnecessary_review_case_ids: tuple[str, ...]


def _validate_entropy(value: float | None) -> None:
    if value is None:
        return
    if not isinstance(value, (int, float)) or not isfinite(float(value)) or value < 0 or value > 1:
        raise ValueError("semantic_entropy must be null or finite in [0,1]")


def evaluate_strategy(
    cases: Iterable[TriggerCase],
    *,
    strategy: str,
    semantic_threshold: float | None = None,
) -> StrategyResult:
    rows = tuple(cases)
    if not rows:
        raise ValueError("at least one calibration case required")
    if len({c.case_id for c in rows}) != len(rows):
        raise ValueError("duplicate case_id")
    for c in rows:
        if not c.case_id:
            raise ValueError("case_id required")
        _validate_entropy(c.semantic_entropy)

    allowed = {"R1_ONLY", "SEMANTIC_ONLY", "GOVERNED_CONDITIONAL", "ALWAYS_REVIEW"}
    if strategy not in allowed:
        raise ValueError("invalid strategy")
    if strategy in {"SEMANTIC_ONLY", "GOVERNED_CONDITIONAL"}:
        if semantic_threshold is None or not 0 <= semantic_threshold <= 1:
            raise ValueError("semantic_threshold in [0,1] required")

    reviewed: list[str] = []
    finalized: list[str] = []
    false_green: list[str] = []
    unnecessary: list[str] = []

    for c in rows:
        if strategy == "R1_ONLY":
            needs_review = False
        elif strategy == "ALWAYS_REVIEW":
            needs_review = True
        else:
            semantic_trigger = (
                not c.sample_sufficient
                or c.semantic_entropy is None
                or c.semantic_entropy >= float(semantic_threshold)
            )
            if strategy == "SEMANTIC_ONLY":
                needs_review = semantic_trigger
            else:
                needs_review = c.policy_review_required or semantic_trigger

        if needs_review:
            reviewed.append(c.case_id)
            if c.r1_correct:
                unnecessary.append(c.case_id)
        else:
            finalized.append(c.case_id)
            if not c.r1_correct:
                false_green.append(c.case_id)

    return StrategyResult(
        strategy=strategy,
        reviewed_case_ids=tuple(reviewed),
        finalized_at_r1_case_ids=tuple(finalized),
        r1_false_green_case_ids=tuple(false_green),
        unnecessary_review_case_ids=tuple(unnecessary),
    )


def threshold_sweep(cases: Iterable[TriggerCase], thresholds: Iterable[float]) -> tuple[dict, ...]:
    rows = tuple(cases)
    output = []
    for threshold in thresholds:
        if not isinstance(threshold, (int, float)) or not 0 <= float(threshold) <= 1:
            raise ValueError("thresholds must be in [0,1]")
        for strategy in ("SEMANTIC_ONLY", "GOVERNED_CONDITIONAL"):
            result = evaluate_strategy(rows, strategy=strategy, semantic_threshold=float(threshold))
            output.append({
                "threshold": float(threshold),
                "strategy": strategy,
                "review_count": len(result.reviewed_case_ids),
                "r1_false_green_count": len(result.r1_false_green_case_ids),
                "unnecessary_review_count": len(result.unnecessary_review_case_ids),
                "reviewed_case_ids": result.reviewed_case_ids,
                "r1_false_green_case_ids": result.r1_false_green_case_ids,
            })
    return tuple(output)
