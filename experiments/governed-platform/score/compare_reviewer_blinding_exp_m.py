from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BlindingObservation:
    pair_id: str
    reviewer_id: str
    arm: str
    conclusion: str
    protected_correct_conclusion: str
    prior_majority_conclusion: str | None = None
    frozen_independent_conclusion: str | None = None


_VALID_ARMS = {"M0_BLINDED", "M1_PRIOR_VISIBLE", "M2_CONFIDENCE_VISIBLE", "M3_MAJORITY_VISIBLE", "M4_STAGED_AFTER_FREEZE"}


def _validate(row: BlindingObservation) -> None:
    if not row.pair_id or not row.reviewer_id:
        raise ValueError("pair_id and reviewer_id required")
    if row.arm not in _VALID_ARMS:
        raise ValueError("invalid EXP-M arm")
    if not row.conclusion or not row.protected_correct_conclusion:
        raise ValueError("conclusion and protected_correct_conclusion required")
    if row.arm in {"M1_PRIOR_VISIBLE", "M2_CONFIDENCE_VISIBLE", "M3_MAJORITY_VISIBLE", "M4_STAGED_AFTER_FREEZE"} and not row.prior_majority_conclusion:
        raise ValueError("prior_majority_conclusion required for disclosure arm")
    if row.arm == "M4_STAGED_AFTER_FREEZE" and not row.frozen_independent_conclusion:
        raise ValueError("frozen_independent_conclusion required for staged arm")


def score_blinding_observations(rows: Iterable[BlindingObservation]) -> dict:
    data = tuple(rows)
    if not data:
        raise ValueError("at least one observation required")
    for row in data:
        _validate(row)

    keys = [(r.pair_id, r.reviewer_id, r.arm) for r in data]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate pair/reviewer/arm observation")

    correct = [r for r in data if r.conclusion == r.protected_correct_conclusion]
    incorrect = [r for r in data if r.conclusion != r.protected_correct_conclusion]
    consensus_adherence = [
        r for r in data
        if r.prior_majority_conclusion is not None
        and r.conclusion == r.prior_majority_conclusion
        and r.prior_majority_conclusion != r.protected_correct_conclusion
    ]
    staged_harmful_switch = [
        r for r in data
        if r.arm == "M4_STAGED_AFTER_FREEZE"
        and r.frozen_independent_conclusion == r.protected_correct_conclusion
        and r.conclusion != r.protected_correct_conclusion
    ]
    staged_corrective_switch = [
        r for r in data
        if r.arm == "M4_STAGED_AFTER_FREEZE"
        and r.frozen_independent_conclusion != r.protected_correct_conclusion
        and r.conclusion == r.protected_correct_conclusion
    ]

    by_arm = {}
    for arm in sorted(_VALID_ARMS):
        arm_rows = [r for r in data if r.arm == arm]
        if not arm_rows:
            continue
        by_arm[arm] = {
            "n": len(arm_rows),
            "correct": sum(r.conclusion == r.protected_correct_conclusion for r in arm_rows),
            "incorrect": sum(r.conclusion != r.protected_correct_conclusion for r in arm_rows),
            "incorrect_prior_consensus_adherence": sum(
                r.prior_majority_conclusion is not None
                and r.conclusion == r.prior_majority_conclusion
                and r.prior_majority_conclusion != r.protected_correct_conclusion
                for r in arm_rows
            ),
        }

    return {
        "observation_count": len(data),
        "correct_count": len(correct),
        "incorrect_count": len(incorrect),
        "incorrect_prior_consensus_adherence_count": len(consensus_adherence),
        "staged_harmful_switch_count": len(staged_harmful_switch),
        "staged_corrective_switch_count": len(staged_corrective_switch),
        "by_arm": by_arm,
    }
