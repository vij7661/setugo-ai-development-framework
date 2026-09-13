"""R12 hardened independent-review protocol boundary.

R11 is preserved verbatim in review_protocol_legacy.py. This module re-exports
its non-authoritative helpers while replacing the material-review construction,
transport, semantic validation, grounding, and promotion boundary with fail-
closed R12 rules.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

import review_protocol_legacy as _legacy
from review_protocol_legacy import *  # noqa: F401,F403 - intentional compatibility surface

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMOTION_ELIGIBLE_REQUEST_STATES = frozenset({
    "REVIEW_REQUIRED", "PENDING_EXTERNAL_REVIEW", "REVIEW_RECEIVED", "REVIEW_VALIDATED",
})
_ISSUED_EXECUTIONS: dict[int, tuple[str, str, str, str, str]] = {}


def _git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _governed_commit_exists(commit: object) -> bool:
    return isinstance(commit, str) and bool(SHA40.fullmatch(commit)) and _git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def _mandatory_dimension_ids(request: Mapping[str, Any]) -> set[str]:
    dims = request.get("required_review_dimensions")
    if not isinstance(dims, list):
        return set()
    return {
        str(row.get("id"))
        for row in dims
        if isinstance(row, Mapping) and row.get("mandatory") is True and isinstance(row.get("id"), str) and row.get("id")
    }


def build_review_request(*, review_request_id: str, trigger: str, artifact_type: str, artifact_ref: str,
                         artifact_commit: str, proposer: Mapping[str, Any], required_reviewer: Mapping[str, Any],
                         blind_review_required: bool, review_questions: list[str],
                         evidence_refs: list[Mapping[str, Any]], material_authority_transition: bool = True,
                         standard_requires_review: bool = False, changed_paths: Sequence[str] | None = None,
                         required_review_dimensions: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    if material_authority_transition and required_review_dimensions is None:
        raise ValueError("material review requires semantic review dimensions")
    if material_authority_transition and required_review_dimensions is not None:
        if not any(isinstance(x, Mapping) and x.get("mandatory") is True for x in required_review_dimensions):
            raise ValueError("material review requires at least one mandatory semantic review dimension")
    return _legacy.build_review_request(
        review_request_id=review_request_id,
        trigger=trigger,
        artifact_type=artifact_type,
        artifact_ref=artifact_ref,
        artifact_commit=artifact_commit,
        proposer=proposer,
        required_reviewer=required_reviewer,
        blind_review_required=blind_review_required,
        review_questions=review_questions,
        evidence_refs=evidence_refs,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
        changed_paths=changed_paths,
        required_review_dimensions=required_review_dimensions,
    )


def verify_review_request(request: Mapping[str, Any]) -> tuple[bool, str]:
    ok, reason = _legacy.verify_review_request(request)
    if not ok:
        return ok, reason
    if request.get("material_authority_transition") is True:
        if request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
            return False, "material review request must use the semantic review schema"
        if not _mandatory_dimension_ids(request):
            return False, "material review request requires at least one mandatory review dimension"
    return True, "review request verified under R12"


def validate_review_semantics(*, request: Mapping[str, Any], evidence: Mapping[str, Any]) -> tuple[bool, str]:
    if request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
        return False, "legacy review is historical/non-authoritative and cannot satisfy material semantic validation"
    ok, reason = _legacy.validate_review_semantics(request=request, evidence=evidence)
    if not ok:
        return ok, reason
    if evidence.get("disposition") == "BOUNDED_PASS":
        mandatory = _mandatory_dimension_ids(request)
        if not mandatory:
            return False, "BOUNDED_PASS requires a non-empty mandatory review dimension set"
        coverage = evidence.get("review_coverage")
        if not isinstance(coverage, list):
            return False, "BOUNDED_PASS requires review coverage"
        statuses = {
            str(row.get("dimension_id")): str(row.get("status"))
            for row in coverage if isinstance(row, Mapping)
        }
        if any(statuses.get(d) != "TESTED_SUPPORTED" for d in mandatory):
            return False, "BOUNDED_PASS requires every mandatory review dimension to be TESTED_SUPPORTED"
        if any(status in DEFECT_DIMENSION_STATUSES for status in statuses.values()):
            return False, "BOUNDED_PASS cannot coexist with contradicted or defective review dimensions"
        assessment = evidence.get("evidence_assessment")
        if isinstance(assessment, str) and any(p.search(assessment) for p in PASS_CONTRADICTION_PATTERNS):
            return False, "free-text evidence assessment contradicts BOUNDED_PASS coverage"
    return True, "review semantic coverage validated under R12"


class AutomaticAPITransport:
    name = "AUTOMATIC_API"
    def __init__(self, provider_call, *, provider: str, model: str):
        if not callable(provider_call) or not provider or not model:
            raise ValueError("trusted API adapter requires configured provider/model identity")
        self.provider_call, self.provider, self.model = provider_call, provider, model


class UserInitiatedAPITransport:
    name = "USER_INITIATED_API"
    def __init__(self, provider_call, *, provider: str, model: str):
        if not callable(provider_call) or not provider or not model:
            raise ValueError("trusted API adapter requires configured provider/model identity")
        self.provider_call, self.provider, self.model = provider_call, provider, model


class ReviewOrchestrator:
    """Issue execution records only for exact platform transport classes.

    The process-local issuance registry deliberately prevents a caller-created
    DispatchResult or name-compatible transport object from authenticating
    itself. Final authority still requires the separately controlled external
    adapter boundary defined by the R12 execution contract.
    """
    def dispatch(self, request: Mapping[str, Any], transport) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        if type(transport) not in {AutomaticAPITransport, UserInitiatedAPITransport}:
            raise ValueError(f"unsupported or unregistered review transport: {getattr(transport, 'name', None)}")
        try:
            response = deepcopy(dict(transport.provider_call(deepcopy(dict(request)))))
        except Exception as exc:
            return DispatchResult(
                transport.name, "PENDING_EXTERNAL_REVIEW", str(request["review_request_id"]),
                canonical_hash(request), error_class=type(exc).__name__, identity_assurance="UNVERIFIED",
                review_class=PLATFORM_REVIEW_CLASS_BY_TRANSPORT.get(transport.name),
            )
        result = DispatchResult(
            transport.name,
            "REVIEW_RECEIVED",
            str(request["review_request_id"]),
            canonical_hash(request),
            response=response,
            reviewer_provider=transport.provider,
            reviewer_model=transport.model,
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
            review_class=PLATFORM_REVIEW_CLASS_BY_TRANSPORT[transport.name],
        )
        _ISSUED_EXECUTIONS[id(result)] = (
            result.payload_hash,
            str(result.reviewer_provider),
            str(result.reviewer_model),
            str(result.transport),
            str(result.review_class),
        )
        return result


def _execution_was_issued(execution: DispatchResult) -> bool:
    expected = _ISSUED_EXECUTIONS.get(id(execution))
    current = (
        str(execution.payload_hash),
        str(execution.reviewer_provider),
        str(execution.reviewer_model),
        str(execution.transport),
        str(execution.review_class),
    )
    return expected == current


def validate_review_evidence(*, request: Mapping[str, Any], evidence: Mapping[str, Any],
                             execution: DispatchResult) -> tuple[bool, str]:
    ok, reason = verify_review_request(request)
    if not ok:
        return False, reason
    if request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
        return False, "legacy review evidence is historical/non-authoritative"
    if not _execution_was_issued(execution):
        return False, "review execution lacks trusted orchestrator issuance; caller-declared identity is non-authoritative"
    ok, reason = _legacy.validate_review_evidence(request=request, evidence=evidence, execution=execution)
    if not ok:
        return ok, reason
    return validate_review_semantics(request=request, evidence=evidence)


def validate_shared_memory_grounding(*, authoritative_state: Mapping[str, Any],
                                     shared_memory: Mapping[str, Any]) -> tuple[bool, str]:
    ok, reason = _legacy.validate_shared_memory_grounding(
        authoritative_state=authoritative_state,
        shared_memory=shared_memory,
    )
    if not ok:
        return ok, reason
    pending = shared_memory.get("pending_reviews")
    if not isinstance(pending, list) or len(pending) != 1 or not isinstance(pending[0], Mapping):
        return False, "shared memory must contain exactly one grounded active pending-review entry"
    return True, "shared memory fully grounded to authority under R12"


def can_promote_material_transition(*, deterministic_gate_passed: bool, authoritative_state: Mapping[str, Any],
                                    shared_memory: Mapping[str, Any], review_request: Mapping[str, Any] | None,
                                    review_evidence: Mapping[str, Any] | None, review_execution: DispatchResult | None,
                                    trigger: str | None = None) -> bool:
    if not deterministic_gate_passed or review_request is None or review_evidence is None or review_execution is None:
        return False
    ok, _ = verify_review_request(review_request)
    if not ok or review_request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
        return False
    if review_request.get("material_authority_transition") is not True:
        return False
    if review_request.get("state") not in PROMOTION_ELIGIBLE_REQUEST_STATES:
        return False
    if not isinstance(trigger, str) or not trigger or trigger != review_request.get("trigger"):
        return False
    if review_evidence.get("disposition") not in PROMOTABLE_REVIEW_DISPOSITIONS:
        return False

    active = authoritative_state.get("independent_review")
    work = authoritative_state.get("active_workstream")
    if not isinstance(active, Mapping) or not isinstance(work, Mapping):
        return False
    if active.get("current_review_request_id") != review_request.get("review_request_id"):
        return False
    if active.get("current_review_status") not in PROMOTABLE_REVIEW_STATES:
        return False
    if active.get("current_review_trigger") != trigger:
        return False

    reviewed_commit = active.get("current_reviewed_artifact_commit")
    request_commit = review_request.get("artifact", {}).get("commit") if isinstance(review_request.get("artifact"), Mapping) else None
    if reviewed_commit is None or reviewed_commit != request_commit or work.get("head_commit") != request_commit:
        return False
    if not _governed_commit_exists(request_commit):
        return False

    grounded, _ = validate_shared_memory_grounding(authoritative_state=authoritative_state, shared_memory=shared_memory)
    if not grounded:
        return False
    valid, _ = validate_review_evidence(request=review_request, evidence=review_evidence, execution=review_execution)
    return bool(valid)
