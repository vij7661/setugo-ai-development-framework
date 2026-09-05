from __future__ import annotations

from typing import Callable

from .context_compiler import ContextCompiler
from .memory import VersionedMemoryStore
from .models import ReviewArtifact, ReviewDecision, ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from .qualification import QualificationRegistry
from .truth_contract import evaluate_truth_contract

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
MATERIALITY_ORDER = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
UNCERTAINTY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
SEVERITY_ORDER = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
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
    proposed = r1.proposed_signals
    return {
        "risk": _max_enum(request.risk, proposed.get("risk"), RISK_ORDER),
        "materiality": _max_enum(request.materiality, proposed.get("materiality"), MATERIALITY_ORDER),
        "uncertainty": _max_enum(request.uncertainty, proposed.get("uncertainty"), UNCERTAINTY_ORDER),
        "external_action": bool(request.external_action or proposed.get("external_action", False)),
        "mutation_requested": bool(request.mutation_requested or proposed.get("mutation_requested", False)),
        "requirement_ambiguity": bool(request.requirement_ambiguity or proposed.get("requirement_ambiguity", False)),
        "evidence_complete": bool(request.evidence_complete and proposed.get("evidence_complete", True)),
    }


def _request_signals(request: ReviewRequest) -> dict:
    return {
        "risk": request.risk,
        "materiality": request.materiality,
        "uncertainty": request.uncertainty,
        "external_action": request.external_action,
        "mutation_requested": request.mutation_requested,
        "requirement_ambiguity": request.requirement_ambiguity,
        "evidence_complete": request.evidence_complete,
    }


def _needs_r2(signals: dict) -> bool:
    return (
        RISK_ORDER[signals["risk"]] >= RISK_ORDER["MEDIUM"]
        or MATERIALITY_ORDER[signals["materiality"]] >= MATERIALITY_ORDER["MATERIAL"]
        or signals["external_action"]
        or signals["mutation_requested"]
        or signals["uncertainty"] == "HIGH"
    )


def _effective_finding_material(finding: ReviewFinding) -> bool:
    """Platform-owned minimum materiality for reviewer findings.

    Reviewer materiality is evidence, not authority. HIGH/CRITICAL findings
    cannot be silently downgraded by setting material=false.
    """
    if finding.severity not in SEVERITY_ORDER:
        raise ValueError(f"invalid finding severity: {finding.severity}")
    return bool(finding.material or SEVERITY_ORDER[finding.severity] >= SEVERITY_ORDER["HIGH"])


def _truth_contract_findings(response: ReviewerResponse) -> tuple[ReviewFinding, ...]:
    # Direct in-process test adapters may omit epistemic evidence. Registered
    # production provider adapters are required to return it. When present, its
    # explicit failures become platform-visible findings.
    if not response.epistemic_review:
        return ()
    return evaluate_truth_contract(response.role, response.epistemic_review).findings


def _all_findings(response: ReviewerResponse) -> tuple[ReviewFinding, ...]:
    return tuple(response.findings) + _truth_contract_findings(response)


def _material_findings(response: ReviewerResponse) -> tuple[ReviewFinding, ...]:
    return tuple(f for f in _all_findings(response) if _effective_finding_material(f))


def _finding_payload(f: ReviewFinding) -> dict:
    return {
        "finding_id": f.finding_id,
        "severity": f.severity,
        "reviewer_material": f.material,
        "effective_material": _effective_finding_material(f),
        "summary": f.summary,
        "violated_invariant": f.violated_invariant,
        "evidence_refs": list(f.evidence_refs),
        "affected_scope": list(f.affected_scope),
        "first_invalid_claim": f.first_invalid_claim,
    }


class ReviewEngine:
    """Governed R1 -> conditional R2 -> conditional R3 product orchestration."""

    def __init__(
        self,
        invoker: ReviewerInvoker,
        *,
        context_compiler: ContextCompiler | None = None,
        session_store=None,
        qualification_registry: QualificationRegistry | None = None,
    ) -> None:
        self._invoke = invoker
        self._contexts = context_compiler or ContextCompiler()
        self._sessions = session_store
        self._qualifications = qualification_registry

    def _emit(self, session_id: str, event_type: str, payload: dict) -> None:
        if self._sessions is not None:
            self._sessions.append(session_id, event_type, payload)

    def _qualification_failure(self, config: ReviewerConfig, *, risk: str, task_type: str) -> str | None:
        if self._qualifications is None:
            return None
        decision = self._qualifications.evaluate(config, risk=risk, task_type=task_type)
        return None if decision.eligible else f"{config.role} not qualified: {decision.reason}"

    def _experimental_unqualified_failure(self, signals: dict, *, truth_review_required: bool = False) -> str | None:
        if self._qualifications is not None:
            return None
        if truth_review_required:
            return "EXPERIMENTAL_UNQUALIFIED mode cannot satisfy Truth & Veracity escalation"
        if _needs_r2(signals):
            return "EXPERIMENTAL_UNQUALIFIED mode cannot satisfy required independent review"
        if signals["requirement_ambiguity"]:
            return "EXPERIMENTAL_UNQUALIFIED mode cannot resolve authoritative requirement ambiguity"
        if not signals["evidence_complete"]:
            return "EXPERIMENTAL_UNQUALIFIED mode requires complete evidence"
        return None

    @staticmethod
    def _lineage_failure(r1: ReviewerConfig, r2: ReviewerConfig | None = None, r3: ReviewerConfig | None = None) -> str | None:
        if r2 is not None and r1.foundation_lineage == r2.foundation_lineage:
            return "R2 is not foundation-lineage independent from R1"
        if r3 is not None:
            if r3.foundation_lineage == r1.foundation_lineage:
                return "R3 is not foundation-lineage independent from R1"
            if r2 is not None and r3.foundation_lineage == r2.foundation_lineage:
                return "R3 is not foundation-lineage independent from R2"
        return None

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
        session_id = request.request_id
        task_type = str(request.platform_facts.get("task_type", "GENERAL"))
        self._emit(
            session_id,
            "REQUEST_RECEIVED",
            {
                "request_id": request.request_id,
                "risk_floor": request.risk,
                "materiality_floor": request.materiality,
                "external_action": request.external_action,
                "mutation_requested": request.mutation_requested,
                "requirement_ambiguity": request.requirement_ambiguity,
                "evidence_complete": request.evidence_complete,
                "assurance_mode": "GOVERNED" if self._qualifications is not None else "EXPERIMENTAL_UNQUALIFIED",
                "truth_contract_version": "TVC-1",
            },
        )

        def finish(decision: ReviewDecision) -> ReviewDecision:
            self._emit(
                session_id,
                "FINAL_DECISION",
                {
                    "state": decision.state,
                    "reasons": list(decision.reasons),
                    "artifact_hash": decision.artifact_hash,
                    "dissent": list(decision.dissent),
                },
            )
            return decision

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

        # Experimental mode is allowed only for bounded R1-only low-risk work.
        experimental_failure = self._experimental_unqualified_failure(_request_signals(request))
        if experimental_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (experimental_failure,)))

        q_failure = self._qualification_failure(r1, risk=request.risk, task_type=task_type)
        if q_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,)))

        r1_initial = self._invoke(r1, self._contexts.compile_r1(request, memory))
        r1_initial.validate()
        if r1_initial.role != "R1":
            raise ValueError("R1 invocation returned wrong role")
        artifact = ReviewArtifact(f"{request.request_id}:artifact", 1, r1_initial.output)
        signals = _effective_signals(request, r1_initial)
        r1_all_findings = _all_findings(r1_initial)
        r1_material = tuple(f for f in r1_all_findings if _effective_finding_material(f))
        self._emit(
            session_id,
            "R1_COMPLETED",
            {
                "artifact_hash": artifact.artifact_hash,
                "effective_signals": signals,
                "findings": [_finding_payload(f) for f in r1_all_findings],
                "material_finding_ids": [f.finding_id for f in r1_material],
                "epistemic_review": r1_initial.epistemic_review,
            },
        )

        # If R1 discovers a higher-risk interpretation, its own qualification
        # must cover that higher risk before its artifact can continue. A
        # self-reported material truth/veracity failure also forces independent
        # review rather than permitting R1-only convergence.
        experimental_failure = self._experimental_unqualified_failure(signals, truth_review_required=bool(r1_material))
        if experimental_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (experimental_failure,), artifact_hash=artifact.artifact_hash))
        q_failure = self._qualification_failure(r1, risk=signals["risk"], task_type=task_type)
        if q_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=artifact.artifact_hash))
        if signals["requirement_ambiguity"]:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("authoritative requirement ambiguity",), artifact_hash=artifact.artifact_hash))
        if not signals["evidence_complete"] and (
            RISK_ORDER[signals["risk"]] >= RISK_ORDER["HIGH"]
            or signals["external_action"]
            or signals["mutation_requested"]
        ):
            return finish(ReviewDecision("HUMAN_REQUIRED", ("incomplete evidence for consequential task",), artifact_hash=artifact.artifact_hash))

        needs_r2 = bool(r1_material) or _needs_r2(signals)
        if not needs_r2:
            self._emit(session_id, "ROUTE_DECISION", {"route": "R1_ONLY", "artifact_hash": artifact.artifact_hash})
            return finish(ReviewDecision("CONVERGED_PASS", ("platform policy permits R1-only finalization",), artifact.content, artifact.artifact_hash))

        route_reason = "R1_TRUTH_OR_SELF_FINDING_ESCALATION" if r1_material and not _needs_r2(signals) else "POLICY_R2_REQUIRED"
        self._emit(
            session_id,
            "ROUTE_DECISION",
            {"route": "R2_REQUIRED", "reason": route_reason, "artifact_hash": artifact.artifact_hash},
        )
        if r2 is None or not r2.enabled:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("R2 required but unavailable",), artifact_hash=artifact.artifact_hash))
        lineage_failure = self._lineage_failure(r1, r2)
        if lineage_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (lineage_failure,), artifact_hash=artifact.artifact_hash))
        q_failure = self._qualification_failure(r2, risk=signals["risk"], task_type=task_type)
        if q_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=artifact.artifact_hash))

        r2_response = self._invoke(r2, self._contexts.compile_r2(request, artifact, memory))
        r2_response.validate()
        if r2_response.role != "R2" or r2_response.artifact_hash != artifact.artifact_hash:
            raise ValueError("R2 response is not bound to current frozen artifact")
        r2_all_findings = _all_findings(r2_response)
        r2_material = tuple(f for f in r2_all_findings if _effective_finding_material(f))
        self._emit(
            session_id,
            "R2_COMPLETED",
            {
                "artifact_hash": artifact.artifact_hash,
                "findings": [_finding_payload(f) for f in r2_all_findings],
                "material_finding_ids": [f.finding_id for f in r2_material],
                "epistemic_review": r2_response.epistemic_review,
            },
        )
        if not r2_material:
            return finish(
                ReviewDecision(
                    "CONVERGED_PASS",
                    ("required independent R2 review found no material defect",),
                    artifact.content,
                    artifact.artifact_hash,
                    tuple(f.summary for f in r2_all_findings),
                )
            )

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
                "verified_review_targets": [_finding_payload(f) for f in r2_material],
            }
        )
        correction_context["instructions"].update(
            {
                "change_only_affected_scope": True,
                "preserve_unaffected_content": True,
                "reviewer_finding_is_evidence_not_release_authority": True,
            }
        )
        r1_revised = self._invoke(r1, correction_context)
        r1_revised.validate()
        if r1_revised.role != "R1":
            raise ValueError("correction invocation returned wrong role")
        revised = ReviewArtifact(artifact.artifact_id, 2, r1_revised.output)
        r1_revised_findings = _all_findings(r1_revised)
        self._emit(
            session_id,
            "R1_REVISED",
            {
                "previous_artifact_hash": artifact.artifact_hash,
                "artifact_hash": revised.artifact_hash,
                "trigger_finding_ids": [f.finding_id for f in r2_material],
                "findings": [_finding_payload(f) for f in r1_revised_findings],
                "epistemic_review": r1_revised.epistemic_review,
            },
        )
        if revised.artifact_hash == artifact.artifact_hash:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("material R2 finding produced no artifact revision",), artifact_hash=revised.artifact_hash))

        if r3 is None or not r3.enabled:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("material revision requires R3 but R3 is unavailable",), artifact_hash=revised.artifact_hash))
        lineage_failure = self._lineage_failure(r1, r2, r3)
        if lineage_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (lineage_failure,), artifact_hash=revised.artifact_hash))
        q_failure = self._qualification_failure(r3, risk=signals["risk"], task_type=task_type)
        if q_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=revised.artifact_hash))

        r3_independent = self._invoke(r3, self._contexts.compile_r3_phase_a(request, revised, memory))
        r3_independent.validate()
        if r3_independent.role != "R3" or r3_independent.artifact_hash != revised.artifact_hash:
            raise ValueError("R3 independent response is not bound to revised artifact")
        r3_all_findings = _all_findings(r3_independent)
        r3_material = tuple(f for f in r3_all_findings if _effective_finding_material(f))
        self._emit(
            session_id,
            "R3_INDEPENDENT_COMPLETED",
            {
                "artifact_hash": revised.artifact_hash,
                "findings": [_finding_payload(f) for f in r3_all_findings],
                "material_finding_ids": [f.finding_id for f in r3_material],
                "epistemic_review": r3_independent.epistemic_review,
            },
        )
        if not r3_material:
            return finish(ReviewDecision("CONVERGED_PASS", ("material revision independently verified by blinded R3",), revised.content, revised.artifact_hash))

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
        r3_adjudication_findings = _all_findings(r3_adjudication)
        unresolved = tuple(f for f in r3_adjudication_findings if _effective_finding_material(f))
        self._emit(
            session_id,
            "R3_ADJUDICATION_COMPLETED",
            {
                "artifact_hash": revised.artifact_hash,
                "findings": [_finding_payload(f) for f in r3_adjudication_findings],
                "unresolved_finding_ids": [f.finding_id for f in unresolved],
                "epistemic_review": r3_adjudication.epistemic_review,
            },
        )
        if unresolved:
            return finish(
                ReviewDecision(
                    "HUMAN_REQUIRED",
                    ("material conflict remains after staged R3 adjudication",),
                    artifact_hash=revised.artifact_hash,
                    dissent=tuple(f.summary for f in unresolved),
                )
            )
        return finish(
            ReviewDecision(
                "CONVERGED_PASS",
                ("R3 adjudication resolved material review findings without majority voting",),
                revised.content,
                revised.artifact_hash,
                tuple(f.summary for f in r3_all_findings),
            )
        )
