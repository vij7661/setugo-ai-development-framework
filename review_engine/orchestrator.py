from __future__ import annotations

from dataclasses import replace
from typing import Callable

from .context_compiler import ContextCompiler
from .memory import VersionedMemoryStore
from .models import (
    ReviewArtifact,
    ReviewDecision,
    ReviewerConfig,
    ReviewerResponse,
    ReviewRequest,
)

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
MATERIALITY_ORDER = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
UNCERTAINTY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

ReviewerInvoker = Callable[[ReviewerConfig, dict], ReviewerResponse]


def _max_enum(a: str, b: str | None, order: dict[str, int]) -> str:
    if a not in order:
        raise ValueError(f"invalid platform signal: {a}")
    if b is None:
        return a
    if b not in order:
        raise ValueError(f"invalid reviewer-proposed signal: {b}")
    return a if order[a] >= order[b] else b


def _effective_signals(request: ReviewRequest, r1: ReviewerResponse) -> dict:
    """Platform facts are a floor; R1 may escalate but cannot downgrade them."""
    proposed = r1.proposed_signals
    return {
        "risk": _max_enum(request.risk, proposed.get("risk"), RISK_ORDER),
        "materiality": _max_enum(request.materiality, proposed.get("materiality"), MATERIALITY_ORDER),
        "uncertainty": _max_enum(request.uncertainty, proposed.get("uncertainty"), UNCERTAINTY_ORDER),
        "external_action": bool(request.external_action or proposed.get("external_action", False)),
        "mutation_requested": bool(request.mutation_requested or proposed.get("mutation_requested", False)),
        "requirement_ambiguity": bool(request.requirement_ambiguity or proposed.get("requirement_ambiguity", False)),
        # R1 cannot make incomplete platform evidence become complete.
        "evidence_complete": bool(request.evidence_complete and proposed.get("evidence_complete", True)),
    }


def _needs_r2(signals: dict) -> bool:
    return (
        RISK_ORDER[signals["risk"]] >= RISK_ORDER["MEDIUM"]
        or MATERIALITY_ORDER[signals["materiality"]] >= MATERIALITY_ORDER["MATERIAL"]
        or signals["external_action"]
        or signals["mutation_requested"]
        or signals["uncertainty"] == "HIGH"
    )


def _material_findings(response: ReviewerResponse) -> tuple:
    return tuple(f for f in response.findings if f.material)


class ReviewEngine:
    """First executable product orchestration for R1 -> conditional R2 -> conditional R3.

    Models provide generation and critique. The engine owns routing and terminal
    state. A model response never grants production/release authority.
    """

    def __init__(self, invoker: ReviewerInvoker, *, context_compiler: ContextCompiler | None = None) -> None:
        self._invoke = invoker
        self._contexts = context_compiler or ContextCompiler()

    def run(
        self,
        request: ReviewRequest,
        *,
        r1: ReviewerConfig,
        r2: ReviewerConfig | None,
        r3: ReviewerConfig | None,
        memory: VersionedMemoryStore | None = None,
    ) -> ReviewDecision:
        memory = memory or VersionedMemoryStore()
        r1.validate()
        if r1.role != "R1":
            raise ValueError("primary configuration must be R1")
        if r2 is not None:
            r2.validate()
            if r2.role != "R2":
                raise ValueError("second configuration must be R2")
        if r3 is not None:
            r3.validate()
            if r3.role != "R3":
                raise ValueError("third configuration must be R3")

        r1_initial = self._invoke(r1, self._contexts.compile_r1(request, memory))
        r1_initial.validate()
        if r1_initial.role != "R1":
            raise ValueError("R1 invocation returned wrong role")

        artifact = ReviewArtifact(
            artifact_id=f"{request.request_id}:artifact",
            version=1,
            content=r1_initial.output,
        )
        signals = _effective_signals(request, r1_initial)

        if signals["requirement_ambiguity"]:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("authoritative requirement ambiguity",),
                artifact_hash=artifact.artifact_hash,
            )
        if not signals["evidence_complete"] and (
            RISK_ORDER[signals["risk"]] >= RISK_ORDER["HIGH"]
            or signals["external_action"]
            or signals["mutation_requested"]
        ):
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("incomplete evidence for consequential task",),
                artifact_hash=artifact.artifact_hash,
            )

        if not _needs_r2(signals):
            return ReviewDecision(
                "CONVERGED_PASS",
                ("platform policy permits R1-only finalization",),
                final_output=artifact.content,
                artifact_hash=artifact.artifact_hash,
            )

        if r2 is None or not r2.enabled:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("R2 required but unavailable",),
                artifact_hash=artifact.artifact_hash,
            )

        r2_response = self._invoke(r2, self._contexts.compile_r2(request, artifact, memory))
        r2_response.validate()
        if r2_response.role != "R2" or r2_response.artifact_hash != artifact.artifact_hash:
            raise ValueError("R2 response is not bound to current frozen artifact")

        r2_material = _material_findings(r2_response)
        if not r2_material:
            return ReviewDecision(
                "CONVERGED_PASS",
                ("required independent R2 review found no material defect",),
                final_output=artifact.content,
                artifact_hash=artifact.artifact_hash,
                dissent=tuple(f.summary for f in r2_response.findings),
            )

        # A material R2 finding triggers a scoped R1 correction attempt. The
        # correction prompt carries only the frozen finding scope; R2 does not
        # rewrite the artifact or grant authority.
        correction_context = self._contexts.compile_r1(request, memory)
        correction_context.update(
            {
                "mode": "SCOPED_CORRECTION",
                "artifact": {
                    "artifact_id": artifact.artifact_id,
                    "version": artifact.version,
                    "artifact_hash": artifact.artifact_hash,
                    "content": artifact.content,
                },
                "verified_review_targets": [
                    {
                        "finding_id": f.finding_id,
                        "summary": f.summary,
                        "severity": f.severity,
                        "violated_invariant": f.violated_invariant,
                        "affected_scope": list(f.affected_scope),
                        "first_invalid_claim": f.first_invalid_claim,
                    }
                    for f in r2_material
                ],
                "instructions": {
                    "change_only_affected_scope": True,
                    "preserve_unaffected_content": True,
                    "reviewer_finding_is_evidence_not_release_authority": True,
                },
            }
        )
        r1_revised = self._invoke(r1, correction_context)
        r1_revised.validate()
        if r1_revised.role != "R1":
            raise ValueError("correction invocation returned wrong role")

        revised = ReviewArtifact(
            artifact_id=artifact.artifact_id,
            version=2,
            content=r1_revised.output,
        )
        if revised.artifact_hash == artifact.artifact_hash:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("material R2 finding produced no artifact revision",),
                artifact_hash=revised.artifact_hash,
            )

        if r3 is None or not r3.enabled:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("material revision requires R3 but R3 is unavailable",),
                artifact_hash=revised.artifact_hash,
            )
        if r2.foundation_lineage == r3.foundation_lineage and RISK_ORDER[signals["risk"]] >= RISK_ORDER["HIGH"]:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("high-risk R3 is not foundation-lineage independent from R2",),
                artifact_hash=revised.artifact_hash,
            )

        r3_independent = self._invoke(r3, self._contexts.compile_r3_phase_a(request, revised, memory))
        r3_independent.validate()
        if r3_independent.role != "R3" or r3_independent.artifact_hash != revised.artifact_hash:
            raise ValueError("R3 independent response is not bound to revised artifact")

        r3_material = _material_findings(r3_independent)
        if not r3_material:
            return ReviewDecision(
                "CONVERGED_PASS",
                ("material revision independently verified by blinded R3",),
                final_output=revised.content,
                artifact_hash=revised.artifact_hash,
            )

        # Staged disclosure: only after R3's independent view is frozen do we
        # reveal earlier model outputs. One adjudication round is the MVP
        # ceiling; unresolved material conflict escalates to external authority.
        r3_adjudication = self._invoke(
            r3,
            self._contexts.compile_r3_phase_b(
                request,
                revised,
                memory,
                frozen_independent_response=r3_independent,
                r1_response=r1_revised,
                r2_response=r2_response,
            ),
        )
        r3_adjudication.validate()
        if r3_adjudication.role != "R3" or r3_adjudication.artifact_hash != revised.artifact_hash:
            raise ValueError("R3 adjudication response is not bound to revised artifact")

        unresolved = _material_findings(r3_adjudication)
        if unresolved:
            return ReviewDecision(
                "HUMAN_REQUIRED",
                ("material conflict remains after staged R3 adjudication",),
                artifact_hash=revised.artifact_hash,
                dissent=tuple(f.summary for f in unresolved),
            )

        return ReviewDecision(
            "CONVERGED_PASS",
            ("R3 adjudication resolved material review findings without majority voting",),
            final_output=revised.content,
            artifact_hash=revised.artifact_hash,
            dissent=tuple(f.summary for f in r3_independent.findings),
        )
