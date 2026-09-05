from __future__ import annotations

from typing import Callable

from .context_compiler import ContextCompiler
from .memory import VersionedMemoryStore
from .models import ReviewArtifact, ReviewDecision, ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from .qualification import QualificationRegistry

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
MATERIALITY_ORDER = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
UNCERTAINTY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
ReviewerInvoker = Callable[[ReviewerConfig, dict], ReviewerResponse]


def _max_enum(a: str, b: str | None, order: dict[str, int]) -> str:
    if a not in order: raise ValueError(f"invalid platform signal: {a}")
    if b is None: return a
    if b not in order: raise ValueError(f"invalid reviewer-proposed signal: {b}")
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


def _needs_r2(signals: dict) -> bool:
    return (
        RISK_ORDER[signals["risk"]] >= RISK_ORDER["MEDIUM"]
        or MATERIALITY_ORDER[signals["materiality"]] >= MATERIALITY_ORDER["MATERIAL"]
        or signals["external_action"] or signals["mutation_requested"] or signals["uncertainty"] == "HIGH"
    )


def _material_findings(response: ReviewerResponse) -> tuple[ReviewFinding, ...]:
    return tuple(f for f in response.findings if f.material)


def _finding_payload(f: ReviewFinding) -> dict:
    return {
        "finding_id": f.finding_id,
        "severity": f.severity,
        "material": f.material,
        "summary": f.summary,
        "violated_invariant": f.violated_invariant,
        "evidence_refs": list(f.evidence_refs),
        "affected_scope": list(f.affected_scope),
        "first_invalid_claim": f.first_invalid_claim,
    }


class ReviewEngine:
    """Governed R1 -> conditional R2 -> conditional R3 product orchestration."""

    def __init__(self, invoker: ReviewerInvoker, *, context_compiler: ContextCompiler | None = None, session_store=None, qualification_registry: QualificationRegistry | None = None) -> None:
        self._invoke = invoker
        self._contexts = context_compiler or ContextCompiler()
        self._sessions = session_store
        self._qualifications = qualification_registry

    def _emit(self, session_id: str, event_type: str, payload: dict) -> None:
        if self._sessions is not None: self._sessions.append(session_id, event_type, payload)

    def _qualification_failure(self, config: ReviewerConfig, *, risk: str, task_type: str) -> str | None:
        if self._qualifications is None: return None
        decision = self._qualifications.evaluate(config, risk=risk, task_type=task_type)
        return None if decision.eligible else f"{config.role} not qualified: {decision.reason}"

    def run(self, request: ReviewRequest, *, r1: ReviewerConfig, r2: ReviewerConfig | None, r3: ReviewerConfig | None, memory: VersionedMemoryStore | None = None) -> ReviewDecision:
        memory = memory or VersionedMemoryStore()
        session_id = request.request_id
        task_type = str(request.platform_facts.get("task_type", "GENERAL"))
        self._emit(session_id, "REQUEST_RECEIVED", {
            "request_id": request.request_id, "risk_floor": request.risk, "materiality_floor": request.materiality,
            "external_action": request.external_action, "mutation_requested": request.mutation_requested,
            "requirement_ambiguity": request.requirement_ambiguity, "evidence_complete": request.evidence_complete,
            "assurance_mode": "GOVERNED" if self._qualifications is not None else "EXPERIMENTAL_UNQUALIFIED",
        })

        def finish(decision: ReviewDecision) -> ReviewDecision:
            self._emit(session_id, "FINAL_DECISION", {
                "state": decision.state, "reasons": list(decision.reasons), "artifact_hash": decision.artifact_hash,
                "dissent": list(decision.dissent),
            })
            return decision

        r1.validate()
        if r1.role != "R1": raise ValueError("primary configuration must be R1")
        if r2 is not None:
            r2.validate()
            if r2.role != "R2": raise ValueError("second configuration must be R2")
        if r3 is not None:
            r3.validate()
            if r3.role != "R3": raise ValueError("third configuration must be R3")

        q_failure = self._qualification_failure(r1, risk=request.risk, task_type=task_type)
        if q_failure: return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,)))

        r1_initial = self._invoke(r1, self._contexts.compile_r1(request, memory))
        r1_initial.validate()
        if r1_initial.role != "R1": raise ValueError("R1 invocation returned wrong role")
        artifact = ReviewArtifact(f"{request.request_id}:artifact", 1, r1_initial.output)
        signals = _effective_signals(request, r1_initial)
        self._emit(session_id, "R1_COMPLETED", {"artifact_hash": artifact.artifact_hash, "effective_signals": signals})

        # If R1 discovers a higher-risk interpretation, its own qualification
        # must cover that higher risk before its artifact can continue.
        q_failure = self._qualification_failure(r1, risk=signals["risk"], task_type=task_type)
        if q_failure:
            return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=artifact.artifact_hash))
        if signals["requirement_ambiguity"]:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("authoritative requirement ambiguity",), artifact_hash=artifact.artifact_hash))
        if not signals["evidence_complete"] and (RISK_ORDER[signals["risk"]] >= RISK_ORDER["HIGH"] or signals["external_action"] or signals["mutation_requested"]):
            return finish(ReviewDecision("HUMAN_REQUIRED", ("incomplete evidence for consequential task",), artifact_hash=artifact.artifact_hash))

        if not _needs_r2(signals):
            self._emit(session_id, "ROUTE_DECISION", {"route": "R1_ONLY", "artifact_hash": artifact.artifact_hash})
            return finish(ReviewDecision("CONVERGED_PASS", ("platform policy permits R1-only finalization",), artifact.content, artifact.artifact_hash))

        self._emit(session_id, "ROUTE_DECISION", {"route": "R2_REQUIRED", "artifact_hash": artifact.artifact_hash})
        if r2 is None or not r2.enabled:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("R2 required but unavailable",), artifact_hash=artifact.artifact_hash))
        q_failure = self._qualification_failure(r2, risk=signals["risk"], task_type=task_type)
        if q_failure: return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=artifact.artifact_hash))

        r2_response = self._invoke(r2, self._contexts.compile_r2(request, artifact, memory))
        r2_response.validate()
        if r2_response.role != "R2" or r2_response.artifact_hash != artifact.artifact_hash:
            raise ValueError("R2 response is not bound to current frozen artifact")
        r2_material = _material_findings(r2_response)
        self._emit(session_id, "R2_COMPLETED", {
            "artifact_hash": artifact.artifact_hash,
            "findings": [_finding_payload(f) for f in r2_response.findings],
            "material_finding_ids": [f.finding_id for f in r2_material],
        })
        if not r2_material:
            return finish(ReviewDecision("CONVERGED_PASS", ("required independent R2 review found no material defect",), artifact.content, artifact.artifact_hash, tuple(f.summary for f in r2_response.findings)))

        correction_context = self._contexts.compile_r1(request, memory)
        correction_context.update({
            "mode": "SCOPED_CORRECTION",
            "artifact": {"artifact_id": artifact.artifact_id, "version": artifact.version, "artifact_hash": artifact.artifact_hash, "content": artifact.content},
            "verified_review_targets": [_finding_payload(f) for f in r2_material],
            "instructions": {"change_only_affected_scope": True, "preserve_unaffected_content": True, "reviewer_finding_is_evidence_not_release_authority": True},
        })
        r1_revised = self._invoke(r1, correction_context)
        r1_revised.validate()
        if r1_revised.role != "R1": raise ValueError("correction invocation returned wrong role")
        revised = ReviewArtifact(artifact.artifact_id, 2, r1_revised.output)
        self._emit(session_id, "R1_REVISED", {
            "previous_artifact_hash": artifact.artifact_hash, "artifact_hash": revised.artifact_hash,
            "trigger_finding_ids": [f.finding_id for f in r2_material],
        })
        if revised.artifact_hash == artifact.artifact_hash:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("material R2 finding produced no artifact revision",), artifact_hash=revised.artifact_hash))

        if r3 is None or not r3.enabled:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("material revision requires R3 but R3 is unavailable",), artifact_hash=revised.artifact_hash))
        if r2.foundation_lineage == r3.foundation_lineage and RISK_ORDER[signals["risk"]] >= RISK_ORDER["HIGH"]:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("high-risk R3 is not foundation-lineage independent from R2",), artifact_hash=revised.artifact_hash))
        q_failure = self._qualification_failure(r3, risk=signals["risk"], task_type=task_type)
        if q_failure: return finish(ReviewDecision("HUMAN_REQUIRED", (q_failure,), artifact_hash=revised.artifact_hash))

        r3_independent = self._invoke(r3, self._contexts.compile_r3_phase_a(request, revised, memory))
        r3_independent.validate()
        if r3_independent.role != "R3" or r3_independent.artifact_hash != revised.artifact_hash:
            raise ValueError("R3 independent response is not bound to revised artifact")
        r3_material = _material_findings(r3_independent)
        self._emit(session_id, "R3_INDEPENDENT_COMPLETED", {
            "artifact_hash": revised.artifact_hash,
            "findings": [_finding_payload(f) for f in r3_independent.findings],
            "material_finding_ids": [f.finding_id for f in r3_material],
        })
        if not r3_material:
            return finish(ReviewDecision("CONVERGED_PASS", ("material revision independently verified by blinded R3",), revised.content, revised.artifact_hash))

        r3_adjudication = self._invoke(r3, self._contexts.compile_r3_phase_b(request, revised, memory, frozen_independent_response=r3_independent, r1_response=r1_revised, r2_response=r2_response))
        r3_adjudication.validate()
        if r3_adjudication.role != "R3" or r3_adjudication.artifact_hash != revised.artifact_hash:
            raise ValueError("R3 adjudication response is not bound to revised artifact")
        unresolved = _material_findings(r3_adjudication)
        self._emit(session_id, "R3_ADJUDICATION_COMPLETED", {
            "artifact_hash": revised.artifact_hash,
            "findings": [_finding_payload(f) for f in r3_adjudication.findings],
            "unresolved_finding_ids": [f.finding_id for f in unresolved],
        })
        if unresolved:
            return finish(ReviewDecision("HUMAN_REQUIRED", ("material conflict remains after staged R3 adjudication",), artifact_hash=revised.artifact_hash, dissent=tuple(f.summary for f in unresolved)))
        return finish(ReviewDecision("CONVERGED_PASS", ("R3 adjudication resolved material review findings without majority voting",), revised.content, revised.artifact_hash, tuple(f.summary for f in r3_independent.findings)))
