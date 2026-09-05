from __future__ import annotations

from dataclasses import asdict

from .memory import VersionedMemoryStore
from .models import ReviewArtifact, ReviewFinding, ReviewerResponse, ReviewRequest
from .truth_contract import epistemic_protocol_instructions


def _shared_memory_view(memory: VersionedMemoryStore) -> list[dict]:
    """Return reviewer-visible shared state without general review evidence.

    Frozen prior reviews required for adjudication are passed explicitly by the
    context compiler; they must not arrive through ambient shared memory.
    """
    return [asdict(r) for r in memory.reviewer_visible() if r.memory_class != "REVIEW_EVIDENCE"]


def _truth_protocol() -> dict:
    return epistemic_protocol_instructions()


def _finding_view(finding: ReviewFinding) -> dict:
    return {
        "finding_id": finding.finding_id,
        "reviewer_role": finding.reviewer_role,
        "severity": finding.severity,
        "material": finding.material,
        "summary": finding.summary,
        "violated_invariant": finding.violated_invariant,
        "evidence_refs": list(finding.evidence_refs),
        "affected_scope": list(finding.affected_scope),
        "first_invalid_claim": finding.first_invalid_claim,
    }


class ContextCompiler:
    """Build role-specific context without leaking protected or anchoring data."""

    def compile_r1(self, request: ReviewRequest, memory: VersionedMemoryStore) -> dict:
        return {
            "role": "R1",
            "request_id": request.request_id,
            "user_input": request.user_input,
            "memory": _shared_memory_view(memory),
            "instructions": {
                "authority": "advisory_generation_only",
                "must_not_self_authorize": True,
                "truth_and_veracity_contract": _truth_protocol(),
            },
        }

    def compile_r2(
        self,
        request: ReviewRequest,
        artifact: ReviewArtifact,
        memory: VersionedMemoryStore,
    ) -> dict:
        return {
            "role": "R2",
            "request_id": request.request_id,
            "user_input": request.user_input,
            "artifact": {
                "artifact_id": artifact.artifact_id,
                "version": artifact.version,
                "artifact_hash": artifact.artifact_hash,
                "content": artifact.content,
            },
            "memory": _shared_memory_view(memory),
            "instructions": {
                "mode": "independent_detector_challenger",
                "find_first_material_failure": True,
                "do_not_rewrite_artifact": True,
                "do_not_assume_r1_correct": True,
                "do_not_grant_authority": True,
                "truth_and_veracity_contract": _truth_protocol(),
            },
        }

    def compile_r3_phase_a(
        self,
        request: ReviewRequest,
        artifact: ReviewArtifact,
        memory: VersionedMemoryStore,
    ) -> dict:
        return {
            "role": "R3",
            "phase": "INDEPENDENT",
            "request_id": request.request_id,
            "user_input": request.user_input,
            "artifact": {
                "artifact_id": artifact.artifact_id,
                "version": artifact.version,
                "artifact_hash": artifact.artifact_hash,
                "content": artifact.content,
            },
            "memory": _shared_memory_view(memory),
            "instructions": {
                "mode": "independent_verifier",
                "prior_reviewer_positions_hidden": True,
                "do_not_grant_authority": True,
                "truth_and_veracity_contract": _truth_protocol(),
            },
        }

    def compile_r3_phase_b(
        self,
        request: ReviewRequest,
        artifact: ReviewArtifact,
        memory: VersionedMemoryStore,
        *,
        frozen_independent_response: ReviewerResponse,
        frozen_material_findings: tuple[ReviewFinding, ...],
        r1_response: ReviewerResponse,
        r2_response: ReviewerResponse,
    ) -> dict:
        frozen_independent_response.validate()
        if frozen_independent_response.role != "R3":
            raise ValueError("phase B requires frozen R3 independent response")
        if frozen_independent_response.artifact_hash != artifact.artifact_hash:
            raise ValueError("R3 independent response is stale for current artifact")
        for finding in frozen_material_findings:
            finding.validate()
            if finding.reviewer_role != "R3":
                raise ValueError("phase B frozen material findings must belong to R3")

        return {
            "role": "R3",
            "phase": "ADJUDICATION",
            "request_id": request.request_id,
            "artifact_hash": artifact.artifact_hash,
            "frozen_independent_view": frozen_independent_response.output,
            "frozen_material_findings": [_finding_view(f) for f in frozen_material_findings],
            "prior_reviews": {
                "R1": r1_response.output,
                "R2": r2_response.output,
            },
            "memory": _shared_memory_view(memory),
            "instructions": {
                "independent_view_is_frozen": True,
                "compare_against_authoritative_evidence": True,
                "majority_vote_is_not_authority": True,
                "do_not_grant_authority": True,
                "every_frozen_material_finding_requires_explicit_closure": True,
                "resolved_finding_ids_must_reference_only_frozen_material_findings": True,
                "omission_does_not_resolve_a_finding": True,
                "truth_and_veracity_contract": _truth_protocol(),
            },
        }
