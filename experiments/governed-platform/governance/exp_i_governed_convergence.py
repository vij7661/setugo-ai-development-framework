from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple

from exp_i_claim_convergence_gate import (
    GateState,
    ReviewClaim,
    VerificationArtifact,
    evaluate_review_gate,
)
from tri_reviewer_convergence import decide_convergence


@dataclass(frozen=True)
class GovernedConvergenceDecision:
    state: str
    claim_gate_state: str
    reasons: Tuple[str, ...]
    terminal_convergence: bool
    reviewer_generated_authority: bool = False
    production_authority: bool = False


def governed_convergence(
    reviews: Iterable[ReviewClaim],
    verification: Optional[VerificationArtifact],
    convergence_signals: dict[str, Any],
) -> GovernedConvergenceDecision:
    """Compose claim-bound review validation with the existing EXP-I signal engine.

    The legacy convergence engine is not called unless the exact three-reviewer
    claim has passed platform-issued independent verification. Even then its
    terminal state is epistemic/governance convergence only and never production
    mutation/release authority.
    """
    claim = evaluate_review_gate(reviews, verification)

    if claim.state == GateState.INVALID_REVIEW_INPUT:
        return GovernedConvergenceDecision(
            state="INSUFFICIENT_EVIDENCE",
            claim_gate_state=claim.state.value,
            reasons=claim.reasons,
            terminal_convergence=False,
        )

    if claim.state == GateState.ESCALATE_INDEPENDENT_ADJUDICATION:
        return GovernedConvergenceDecision(
            state="HUMAN_REQUIRED",
            claim_gate_state=claim.state.value,
            reasons=claim.reasons,
            terminal_convergence=False,
        )

    if claim.state == GateState.REQUIRE_INDEPENDENT_VERIFICATION:
        return GovernedConvergenceDecision(
            state="INSUFFICIENT_EVIDENCE",
            claim_gate_state=claim.state.value,
            reasons=claim.reasons,
            terminal_convergence=False,
        )

    if claim.state == GateState.VERIFICATION_CONFLICT:
        return GovernedConvergenceDecision(
            state="HUMAN_REQUIRED",
            claim_gate_state=claim.state.value,
            reasons=claim.reasons,
            terminal_convergence=False,
        )

    if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
        raise AssertionError(f"unhandled claim gate state: {claim.state}")

    terminal = decide_convergence(convergence_signals)
    return GovernedConvergenceDecision(
        state=terminal.state,
        claim_gate_state=claim.state.value,
        reasons=claim.reasons + terminal.reasons,
        terminal_convergence=terminal.state in {
            "CONVERGED_PASS",
            "CONVERGED_WITH_DISSENT",
            "CONVERGED_FAIL",
        },
        reviewer_generated_authority=False,
        production_authority=False,
    )
