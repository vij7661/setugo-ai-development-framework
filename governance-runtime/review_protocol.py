#!/usr/bin/env python3
"""Transport-neutral independent-review protocol for governed authority transitions.

Review policy determines whether review is NONE, RECOMMENDED, or REQUIRED.
Platform mode determines initiation only. Promotion validates grounding and review
evidence directly; callers cannot mint authority with an unverified review boolean.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Callable, Mapping, Protocol

SHA40 = re.compile(r"^[0-9a-f]{40}$")

MANDATORY_REVIEW_TRIGGERS = frozenset({
    "EXPERIMENT_ADJUDICATION",
    "MATERIAL_FAILURE_CLASSIFICATION",
    "FROZEN_ARTIFACT_CHANGE_AFTER_EXPOSURE",
    "MATERIAL_GOVERNANCE_CHANGE",
    "MATERIAL_EXTERNAL_EVIDENCE_PROMOTION",
    "AUTHORITATIVE_RETRACTION_OR_SUPERSESSION",
    "GOVERNED_REQUIREMENT_ACCEPTANCE",
    "TERMINAL_ACTION",
    "MATERIAL_DISAGREEMENT_RESOLUTION",
    "MATERIAL_AUTHORITY_TRANSITION",
})

PLATFORM_MODES = frozenset({"AUTO_MODE", "MANUAL_MODE"})
REVIEW_LEVELS = frozenset({"NONE", "RECOMMENDED", "REQUIRED"})
ALLOWED_TRANSPORTS = frozenset({"MANUAL_RELAY", "AUTOMATIC_API", "USER_INITIATED_API"})
ALLOWED_REQUEST_STATES = frozenset({
    "REVIEW_REQUIRED",
    "PENDING_EXTERNAL_REVIEW",
    "REVIEW_RECEIVED",
    "REVIEW_VALIDATED",
    "REVIEW_REJECTED",
    "SUPERSEDED_BEFORE_REVIEW",
})


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def review_required(
    trigger: str,
    *,
    material_authority_transition: bool = False,
    standard_requires_review: bool = False,
) -> bool:
    """Deterministically require review for known, material, or standard-marked transitions."""
    return (
        trigger in MANDATORY_REVIEW_TRIGGERS
        or bool(material_authority_transition)
        or bool(standard_requires_review)
    )


def evaluate_review_level(
    *,
    trigger: str,
    r1_recommends_review: bool,
    material_authority_transition: bool = False,
    standard_requires_review: bool = False,
) -> str:
    """Policy can force REQUIRED; R1 may only raise NONE to RECOMMENDED."""
    if review_required(
        trigger,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
    ):
        return "REQUIRED"
    return "RECOMMENDED" if r1_recommends_review else "NONE"


def plan_review_interaction(*, platform_mode: str, review_level: str) -> dict[str, Any]:
    if platform_mode not in PLATFORM_MODES:
        raise ValueError(f"unsupported platform mode: {platform_mode}")
    if review_level not in REVIEW_LEVELS:
        raise ValueError(f"unsupported review level: {review_level}")

    if review_level == "NONE":
        return {
            "action": "NO_REVIEW",
            "show_review_controls": False,
            "automatic_dispatch": False,
            "authoritative_transition_blocked": False,
        }
    if platform_mode == "AUTO_MODE":
        return {
            "action": "AUTOMATIC_API",
            "show_review_controls": False,
            "automatic_dispatch": True,
            "authoritative_transition_blocked": review_level == "REQUIRED",
        }
    return {
        "action": "SHOW_REVIEW_CONTROLS",
        "show_review_controls": True,
        "automatic_dispatch": False,
        "authoritative_transition_blocked": review_level == "REQUIRED",
        "recommended_buttons": ["ASK_REVIEWER_SLOT_1", "ASK_REVIEWER_SLOT_2"],
    }


def build_review_request(
    *,
    review_request_id: str,
    trigger: str,
    artifact_type: str,
    artifact_ref: str,
    artifact_commit: str,
    proposer: Mapping[str, Any],
    required_reviewer: Mapping[str, Any],
    blind_review_required: bool,
    review_questions: list[str],
    evidence_refs: list[Mapping[str, Any]],
    material_authority_transition: bool = False,
    standard_requires_review: bool = False,
) -> dict[str, Any]:
    if not review_required(
        trigger,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
    ):
        raise ValueError(f"trigger does not require independent review: {trigger}")
    if not SHA40.fullmatch(artifact_commit):
        raise ValueError("artifact_commit must be an exact lowercase 40-character Git SHA")
    if not review_request_id or not artifact_type or not artifact_ref:
        raise ValueError("review request identity and artifact identity are required")
    if not isinstance(proposer.get("provider"), str) or not proposer.get("provider"):
        raise ValueError("proposer provider identity is required")
    if not isinstance(proposer.get("model"), str) or not proposer.get("model"):
        raise ValueError("proposer model identity is required")
    if not isinstance(required_reviewer.get("provider"), str) or not required_reviewer.get("provider"):
        raise ValueError("required reviewer provider identity is required")
    if not review_questions:
        raise ValueError("at least one review question is required")

    request = {
        "schema_version": 2,
        "review_request_id": review_request_id,
        "trigger": trigger,
        "material_authority_transition": bool(material_authority_transition),
        "standard_requires_review": bool(standard_requires_review),
        "artifact": {
            "type": artifact_type,
            "ref": artifact_ref,
            "commit": artifact_commit,
        },
        "proposer": deepcopy(dict(proposer)),
        "required_reviewer": deepcopy(dict(required_reviewer)),
        "blind_review_required": bool(blind_review_required),
        "review_questions": deepcopy(review_questions),
        "evidence_refs": [deepcopy(dict(item)) for item in evidence_refs],
        "expected_output": {
            "required_fields": [
                "review_request_id",
                "reviewed_artifact_commit",
                "reviewer",
                "disposition",
                "findings",
                "evidence_assessment",
                "independence_attestation",
            ],
            "allowed_dispositions": [
                "PASS",
                "BOUNDED_PASS",
                "FAIL",
                "NOT_TESTED",
                "INSUFFICIENT_EVIDENCE",
                "CHANGES_REQUIRED",
            ],
        },
        "state": "REVIEW_REQUIRED",
    }
    request["request_hash"] = canonical_hash(request)
    return request


def verify_review_request(request: Mapping[str, Any]) -> tuple[bool, str]:
    try:
        material = deepcopy(dict(request))
        supplied_hash = material.pop("request_hash")
        if not isinstance(supplied_hash, str) or canonical_hash(material) != supplied_hash:
            return False, "review request hash is invalid"
        if request.get("schema_version") not in {1, 2}:
            return False, "unsupported review request schema"
        if not review_required(
            str(request.get("trigger", "")),
            material_authority_transition=bool(request.get("material_authority_transition", False)),
            standard_requires_review=bool(request.get("standard_requires_review", False)),
        ):
            return False, "review request is not bound to a mandatory-review condition"
        artifact = request.get("artifact")
        if not isinstance(artifact, Mapping) or not SHA40.fullmatch(str(artifact.get("commit", ""))):
            return False, "review artifact commit is invalid"
        if request.get("state") not in ALLOWED_REQUEST_STATES:
            return False, "review request state is invalid"
        return True, "review request verified"
    except (KeyError, TypeError, ValueError):
        return False, "review request is malformed"


def _evidence_key(item: Mapping[str, Any]) -> str:
    return f"{item.get('type', '')}:{item.get('ref', '')}"


def build_portable_review_bundle(
    *,
    request: Mapping[str, Any],
    artifacts: list[Mapping[str, Any]],
    evidence_summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a self-contained manual-review packet and prove request evidence coverage."""
    ok, reason = verify_review_request(request)
    if not ok:
        raise ValueError(reason)
    if not artifacts:
        raise ValueError("portable review bundle requires at least one embedded artifact")

    embedded: list[dict[str, Any]] = []
    artifact_paths: set[str] = set()
    for item in artifacts:
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not path or not isinstance(content, str):
            raise ValueError("portable artifact requires path and UTF-8 content")
        artifact_paths.add(path)
        embedded.append({
            "path": path,
            "content": content,
            "content_sha256": content_hash(content),
        })

    reference_summaries = evidence_summary.get("reference_summaries", {})
    if not isinstance(reference_summaries, Mapping):
        raise ValueError("evidence_summary.reference_summaries must be a mapping")

    for ref in request.get("evidence_refs", []):
        if not isinstance(ref, Mapping):
            raise ValueError("review request evidence ref is malformed")
        ref_type = ref.get("type")
        ref_value = ref.get("ref")
        if not isinstance(ref_type, str) or not isinstance(ref_value, str):
            raise ValueError("review request evidence ref requires type/ref")
        if ref_type in {"file", "artifact"}:
            if ref_value not in artifact_paths:
                raise ValueError(f"portable bundle missing referenced artifact: {ref_value}")
        elif ref_type == "portable_bundle":
            continue
        elif _evidence_key(ref) not in reference_summaries:
            raise ValueError(f"portable bundle missing evidence summary for: {_evidence_key(ref)}")

    bundle = {
        "schema_version": 2,
        "bundle_type": "SELF_CONTAINED_INDEPENDENT_REVIEW",
        "review_request": deepcopy(dict(request)),
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "repository_access_required": False,
        "artifacts": embedded,
        "covered_evidence_refs": [deepcopy(dict(item)) for item in request.get("evidence_refs", [])],
        "evidence_summary": deepcopy(dict(evidence_summary)),
    }
    bundle["bundle_hash"] = canonical_hash(bundle)
    return bundle


def verify_portable_review_bundle(
    *,
    request: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> tuple[bool, str]:
    try:
        ok, reason = verify_review_request(request)
        if not ok:
            return False, reason
        material = deepcopy(dict(bundle))
        supplied_hash = material.pop("bundle_hash")
        if not isinstance(supplied_hash, str) or canonical_hash(material) != supplied_hash:
            return False, "portable review bundle hash is invalid"
        if bundle.get("schema_version") not in {1, 2}:
            return False, "portable review bundle schema is invalid"
        if bundle.get("bundle_type") != "SELF_CONTAINED_INDEPENDENT_REVIEW":
            return False, "portable review bundle type is invalid"
        if bundle.get("repository_access_required") is not False:
            return False, "manual review bundle must not require repository access"
        embedded_request = bundle.get("review_request")
        if not isinstance(embedded_request, Mapping):
            return False, "portable review bundle lacks embedded ReviewRequest"
        if canonical_hash(embedded_request) != canonical_hash(request):
            return False, "portable review bundle rebound ReviewRequest semantics"
        if bundle.get("reviewed_artifact_commit") != request["artifact"]["commit"]:
            return False, "portable review bundle targets a different artifact commit"

        artifacts = bundle.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            return False, "portable review bundle lacks artifacts"
        artifact_paths: set[str] = set()
        for item in artifacts:
            if not isinstance(item, Mapping):
                return False, "portable review artifact is malformed"
            path = item.get("path")
            content = item.get("content")
            if not isinstance(path, str) or not path:
                return False, "portable review artifact path is invalid"
            if not isinstance(content, str) or item.get("content_sha256") != content_hash(content):
                return False, "portable review artifact content hash is invalid"
            artifact_paths.add(path)

        covered = bundle.get("covered_evidence_refs")
        if canonical_hash(covered) != canonical_hash(request.get("evidence_refs", [])):
            return False, "portable review bundle evidence coverage differs from ReviewRequest"
        summary = bundle.get("evidence_summary")
        if not isinstance(summary, Mapping):
            return False, "portable review bundle lacks evidence summary"
        reference_summaries = summary.get("reference_summaries", {})
        if not isinstance(reference_summaries, Mapping):
            return False, "portable review bundle reference summaries are invalid"

        for ref in request.get("evidence_refs", []):
            if not isinstance(ref, Mapping):
                return False, "review request evidence ref is malformed"
            ref_type = ref.get("type")
            ref_value = ref.get("ref")
            if ref_type in {"file", "artifact"}:
                if ref_value not in artifact_paths:
                    return False, f"portable review bundle missing referenced artifact: {ref_value}"
            elif ref_type == "portable_bundle":
                continue
            elif _evidence_key(ref) not in reference_summaries:
                return False, f"portable review bundle missing evidence summary for: {_evidence_key(ref)}"
        return True, "portable review bundle verified"
    except (KeyError, TypeError, ValueError):
        return False, "portable review bundle is malformed"


@dataclass(frozen=True)
class DispatchResult:
    transport: str
    state: str
    review_request_id: str
    payload_hash: str
    response: Mapping[str, Any] | None = None
    error_class: str | None = None
    portable_bundle_hash: str | None = None


class ReviewTransport(Protocol):
    name: str

    def dispatch(self, request: Mapping[str, Any]) -> DispatchResult:
        ...


class ManualRelayTransport:
    name = "MANUAL_RELAY"

    def __init__(self, portable_bundle: Mapping[str, Any]):
        self.portable_bundle = deepcopy(dict(portable_bundle))

    def dispatch(self, request: Mapping[str, Any]) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        bundle_ok, bundle_reason = verify_portable_review_bundle(request=request, bundle=self.portable_bundle)
        if not bundle_ok:
            raise ValueError(bundle_reason)
        return DispatchResult(
            transport=self.name,
            state="PENDING_EXTERNAL_REVIEW",
            review_request_id=str(request["review_request_id"]),
            payload_hash=canonical_hash(request),
            response=None,
            portable_bundle_hash=str(self.portable_bundle["bundle_hash"]),
        )


class _APITransportBase:
    def __init__(self, provider_call: Callable[[Mapping[str, Any]], Mapping[str, Any]]):
        self.provider_call = provider_call

    def dispatch(self, request: Mapping[str, Any]) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        response = deepcopy(dict(self.provider_call(deepcopy(dict(request)))))
        return DispatchResult(
            transport=self.name,
            state="REVIEW_RECEIVED",
            review_request_id=str(request["review_request_id"]),
            payload_hash=canonical_hash(request),
            response=response,
        )


class AutomaticAPITransport(_APITransportBase):
    name = "AUTOMATIC_API"


class UserInitiatedAPITransport(_APITransportBase):
    name = "USER_INITIATED_API"


class ReviewOrchestrator:
    def dispatch(self, request: Mapping[str, Any], transport: ReviewTransport) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        if transport.name not in ALLOWED_TRANSPORTS:
            raise ValueError(f"unsupported review transport: {transport.name}")
        try:
            result = transport.dispatch(deepcopy(dict(request)))
        except Exception as exc:
            return DispatchResult(
                transport=transport.name,
                state="PENDING_EXTERNAL_REVIEW",
                review_request_id=str(request["review_request_id"]),
                payload_hash=canonical_hash(request),
                response=None,
                error_class=type(exc).__name__,
            )
        if result.review_request_id != request.get("review_request_id"):
            raise ValueError("transport rebound review request identity")
        if result.payload_hash != canonical_hash(request):
            raise ValueError("transport changed review request semantics")
        return result


def _normalized_model_tokens(value: str) -> list[str]:
    return [part for part in re.split(r"[^a-z0-9]+", value.lower()) if part]


def _model_matches_class(model: str, model_class: str) -> bool:
    class_tokens = _normalized_model_tokens(model_class)
    model_tokens = _normalized_model_tokens(model)
    if not class_tokens:
        return False
    return all(token in model_tokens for token in class_tokens)


def validate_review_evidence(
    *,
    request: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[bool, str]:
    ok, reason = verify_review_request(request)
    if not ok:
        return False, reason
    try:
        if evidence.get("review_request_id") != request.get("review_request_id"):
            return False, "review evidence is bound to a different request"
        if evidence.get("reviewed_artifact_commit") != request["artifact"]["commit"]:
            return False, "review evidence is bound to a different artifact commit"
        reviewer = evidence.get("reviewer")
        if not isinstance(reviewer, Mapping):
            return False, "reviewer identity is missing"
        reviewer_provider = reviewer.get("provider")
        reviewer_model = reviewer.get("model")
        if not isinstance(reviewer_provider, str) or not reviewer_provider.strip():
            return False, "reviewer provider identity is missing"
        if not isinstance(reviewer_model, str) or not reviewer_model.strip():
            return False, "reviewer model identity is missing"

        proposer = request.get("proposer", {})
        if reviewer_provider == proposer.get("provider") and reviewer_model == proposer.get("model"):
            return False, "review independence is unproven: proposer and reviewer are identical"

        required = request.get("required_reviewer", {})
        required_provider = required.get("provider")
        if required_provider and reviewer_provider != required_provider:
            return False, "reviewer provider does not satisfy the required reviewer"
        required_model = required.get("model")
        if required_model and reviewer_model != required_model:
            return False, "reviewer model does not satisfy required exact model"
        required_model_class = required.get("model_class")
        if required_model_class and not _model_matches_class(reviewer_model, str(required_model_class)):
            return False, "reviewer model does not satisfy required model class"

        if request.get("blind_review_required") and evidence.get("independence_attestation") != "BLIND_TO_PROPOSER_CONCLUSION":
            return False, "blind-review attestation is missing"
        allowed = request.get("expected_output", {}).get("allowed_dispositions", [])
        if evidence.get("disposition") not in allowed:
            return False, "review disposition is not allowed"
        for field in ("findings", "evidence_assessment"):
            if field not in evidence:
                return False, f"review evidence missing required field: {field}"
        return True, "review evidence validated"
    except (KeyError, TypeError, ValueError):
        return False, "review evidence is malformed"


def validate_shared_memory_grounding(
    *,
    authoritative_state: Mapping[str, Any],
    shared_memory: Mapping[str, Any],
) -> tuple[bool, str]:
    """Bind shared-memory continuity to authoritative checkpoint before promotion."""
    try:
        if shared_memory.get("independent_authority") is not False:
            return False, "shared memory claims independent authority"
        work = authoritative_state.get("active_workstream")
        mem_work = shared_memory.get("current_work")
        if not isinstance(work, Mapping) or not isinstance(mem_work, Mapping):
            return False, "authoritative/shared workstream grounding is missing"
        expected = {
            "authoritative_branch": work.get("branch"),
            "authoritative_head": work.get("head_commit"),
            "status": work.get("state"),
        }
        for key, value in expected.items():
            if mem_work.get(key) != value:
                return False, f"shared memory is stale/conflicted at current_work.{key}"

        review = authoritative_state.get("independent_review")
        mem_runtime = shared_memory.get("governance_runtime")
        pending = shared_memory.get("pending_reviews")
        if not isinstance(review, Mapping) or not isinstance(mem_runtime, Mapping):
            return False, "review-state grounding is missing"
        if not isinstance(pending, list) or not pending or not isinstance(pending[0], Mapping):
            return False, "shared-memory pending review state is missing"

        active_id = review.get("current_review_request_id")
        active_status = review.get("current_review_status")
        mem_pending = pending[0]
        if mem_runtime.get("current_review_request_id") != active_id:
            return False, "shared memory current review request differs from authority"
        if mem_runtime.get("current_review_status") != active_status:
            return False, "shared memory current review status differs from authority"
        if active_id is None:
            if mem_pending.get("status") != "PENDING_CANDIDATE_FREEZE":
                return False, "shared memory pending review should be candidate-freeze state"
        else:
            if mem_pending.get("review_request_id") != active_id:
                return False, "shared memory pending review request differs from authority"
            if mem_pending.get("status") not in {"PENDING_EXTERNAL_REVIEW", "REVIEW_RECEIVED", "REVIEW_VALIDATED"}:
                return False, "shared memory active review status is invalid"
        return True, "shared memory grounded to authority"
    except (KeyError, TypeError, ValueError):
        return False, "shared-memory grounding is malformed"


def can_promote_material_transition(
    *,
    trigger: str,
    deterministic_gate_passed: bool,
    authoritative_state: Mapping[str, Any],
    shared_memory: Mapping[str, Any],
    review_request: Mapping[str, Any] | None = None,
    review_evidence: Mapping[str, Any] | None = None,
    material_authority_transition: bool = False,
    standard_requires_review: bool = False,
) -> bool:
    """Fail closed unless grounding, deterministic gate, and required review evidence validate."""
    if not deterministic_gate_passed:
        return False
    grounding_ok, _ = validate_shared_memory_grounding(
        authoritative_state=authoritative_state,
        shared_memory=shared_memory,
    )
    if not grounding_ok:
        return False
    if review_required(
        trigger,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
    ):
        if review_request is None or review_evidence is None:
            return False
        valid_review, _ = validate_review_evidence(request=review_request, evidence=review_evidence)
        if not valid_review:
            return False
    return True
