#!/usr/bin/env python3
"""Governed independent-review protocol for material authority transitions."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Callable, Mapping, Protocol, Sequence

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
GOVERNANCE_RELEVANT_PATH_PREFIXES = (
    "governance-runtime/",
    "standards/",
    "experiments/governed-platform/",
    ".github/workflows/",
)
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
TRUSTED_IDENTITY_ASSURANCE = frozenset({"PROVIDER_ADAPTER_AUTHENTICATED"})
PROMOTABLE_REVIEW_STATES = frozenset({"REVIEW_RECEIVED", "REVIEW_VALIDATED", "VALID_INDEPENDENT_REVIEW_PRESENT"})
PROMOTABLE_REVIEW_DISPOSITIONS = frozenset({"PASS", "BOUNDED_PASS"})
SEMANTIC_REVIEW_SCHEMA_VERSION = 4
REVIEW_DIMENSION_STATUSES = frozenset({
    "TESTED_SUPPORTED",
    "TESTED_DEFECT_FOUND",
    "CONTRADICTED",
    "NOT_TESTED",
    "UNAVAILABLE",
    "INACCESSIBLE",
    "INSUFFICIENT",
})
INCOMPLETE_DIMENSION_STATUSES = frozenset({"NOT_TESTED", "UNAVAILABLE", "INACCESSIBLE", "INSUFFICIENT"})
DEFECT_DIMENSION_STATUSES = frozenset({"TESTED_DEFECT_FOUND", "CONTRADICTED"})
EVIDENCE_REQUIRED_STATUSES = frozenset({"TESTED_SUPPORTED", "TESTED_DEFECT_FOUND", "CONTRADICTED"})
PASS_CONTRADICTION_PATTERNS = (
    re.compile(r"\b(?:raw\s+files?|artifacts?)\s+(?:were|was)\s+not\s+(?:directly\s+)?accessible\b", re.IGNORECASE),
    re.compile(r"\b(?:could\s+not|couldn't|unable\s+to)\s+(?:directly\s+)?(?:access|inspect|verify|test|exercise)\b", re.IGNORECASE),
    re.compile(r"\b(?:was|were)\s+not\s+(?:directly\s+|independently\s+)?(?:tested|verified|exercised|inspected)\b", re.IGNORECASE),
)


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
    changed_paths: Sequence[str] | None = None,
) -> bool:
    """Classifier for interaction/orchestration, not the final authority gate."""
    protected_path_changed = any(
        isinstance(path, str) and path.startswith(GOVERNANCE_RELEVANT_PATH_PREFIXES)
        for path in tuple(changed_paths or ())
    )
    return (
        trigger in MANDATORY_REVIEW_TRIGGERS
        or bool(material_authority_transition)
        or bool(standard_requires_review)
        or protected_path_changed
    )


def evaluate_review_level(
    *,
    trigger: str,
    r1_recommends_review: bool,
    material_authority_transition: bool = False,
    standard_requires_review: bool = False,
    changed_paths: Sequence[str] | None = None,
) -> str:
    if review_required(
        trigger,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
        changed_paths=changed_paths,
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


def _normalize_required_review_dimensions(dimensions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not dimensions:
        raise ValueError("semantic review contract requires at least one review dimension")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in dimensions:
        if not isinstance(item, Mapping):
            raise ValueError("review dimension must be a mapping")
        dimension_id = item.get("id")
        mandatory = item.get("mandatory")
        description = item.get("description")
        if not isinstance(dimension_id, str) or not dimension_id:
            raise ValueError("review dimension id is required")
        if dimension_id in seen:
            raise ValueError(f"duplicate review dimension id: {dimension_id}")
        if not isinstance(mandatory, bool):
            raise ValueError(f"review dimension mandatory flag is required: {dimension_id}")
        if not isinstance(description, str) or not description:
            raise ValueError(f"review dimension description is required: {dimension_id}")
        seen.add(dimension_id)
        normalized.append({"id": dimension_id, "mandatory": mandatory, "description": description})
    return normalized


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
    material_authority_transition: bool = True,
    standard_requires_review: bool = False,
    changed_paths: Sequence[str] | None = None,
    required_review_dimensions: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if not review_required(
        trigger,
        material_authority_transition=material_authority_transition,
        standard_requires_review=standard_requires_review,
        changed_paths=changed_paths,
    ):
        raise ValueError("review request is not bound to a mandatory-review condition")
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
    if not (
        isinstance(required_reviewer.get("model"), str) and required_reviewer.get("model")
        or isinstance(required_reviewer.get("model_class"), str) and required_reviewer.get("model_class")
    ):
        raise ValueError("required reviewer model or model_class is required")
    if not review_questions:
        raise ValueError("at least one review question is required")

    semantic_dimensions = None
    schema_version = 3
    if required_review_dimensions is not None:
        semantic_dimensions = _normalize_required_review_dimensions(required_review_dimensions)
        schema_version = SEMANTIC_REVIEW_SCHEMA_VERSION

    required_fields = [
        "review_request_id",
        "reviewed_artifact_commit",
        "reviewer",
        "disposition",
        "findings",
        "evidence_assessment",
        "independence_attestation",
    ]
    if semantic_dimensions is not None:
        required_fields.append("review_coverage")

    request = {
        "schema_version": schema_version,
        "review_request_id": review_request_id,
        "trigger": trigger,
        "material_authority_transition": bool(material_authority_transition),
        "standard_requires_review": bool(standard_requires_review),
        "changed_paths": list(changed_paths or ()),
        "artifact": {"type": artifact_type, "ref": artifact_ref, "commit": artifact_commit},
        "proposer": deepcopy(dict(proposer)),
        "required_reviewer": deepcopy(dict(required_reviewer)),
        "blind_review_required": bool(blind_review_required),
        "review_questions": deepcopy(review_questions),
        "evidence_refs": [deepcopy(dict(item)) for item in evidence_refs],
        "expected_output": {
            "required_fields": required_fields,
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
    if semantic_dimensions is not None:
        request["required_review_dimensions"] = semantic_dimensions
        request["review_dimension_status_vocabulary"] = sorted(REVIEW_DIMENSION_STATUSES)
    request["request_hash"] = canonical_hash(request)
    return request


def verify_review_request(request: Mapping[str, Any]) -> tuple[bool, str]:
    try:
        material = deepcopy(dict(request))
        supplied_hash = material.pop("request_hash")
        if not isinstance(supplied_hash, str) or canonical_hash(material) != supplied_hash:
            return False, "review request hash is invalid"
        schema = request.get("schema_version")
        if schema not in {1, 2, 3, 4}:
            return False, "unsupported review request schema"
        if not review_required(
            str(request.get("trigger", "")),
            material_authority_transition=bool(request.get("material_authority_transition", False)),
            standard_requires_review=bool(request.get("standard_requires_review", False)),
            changed_paths=request.get("changed_paths", []),
        ):
            return False, "review request is not bound to a mandatory-review condition"
        artifact = request.get("artifact")
        if not isinstance(artifact, Mapping) or not SHA40.fullmatch(str(artifact.get("commit", ""))):
            return False, "review artifact commit is invalid"
        proposer = request.get("proposer")
        if not isinstance(proposer, Mapping) or not proposer.get("provider") or not proposer.get("model"):
            return False, "review proposer identity is missing"
        required = request.get("required_reviewer")
        if not isinstance(required, Mapping) or not isinstance(required.get("provider"), str) or not required.get("provider"):
            return False, "required reviewer provider is missing"
        if not (
            isinstance(required.get("model"), str) and required.get("model")
            or isinstance(required.get("model_class"), str) and required.get("model_class")
        ):
            return False, "required reviewer model constraint is missing"
        if request.get("state") not in ALLOWED_REQUEST_STATES:
            return False, "review request state is invalid"
        if schema == SEMANTIC_REVIEW_SCHEMA_VERSION:
            dimensions = request.get("required_review_dimensions")
            if not isinstance(dimensions, list):
                return False, "semantic review request lacks required review dimensions"
            try:
                normalized = _normalize_required_review_dimensions(dimensions)
            except ValueError as exc:
                return False, str(exc)
            if canonical_hash(normalized) != canonical_hash(dimensions):
                return False, "semantic review dimensions are not normalized"
            if set(request.get("review_dimension_status_vocabulary", [])) != set(REVIEW_DIMENSION_STATUSES):
                return False, "semantic review status vocabulary is invalid"
            required_fields = request.get("expected_output", {}).get("required_fields", [])
            if "review_coverage" not in required_fields:
                return False, "semantic review output contract lacks review_coverage"
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
    ok, reason = verify_review_request(request)
    if not ok:
        raise ValueError(reason)
    if not artifacts:
        raise ValueError("portable review bundle requires at least one embedded artifact")
    embedded: list[dict[str, Any]] = []
    artifact_paths: set[str] = set()
    for item in artifacts:
        path, content = item.get("path"), item.get("content")
        if not isinstance(path, str) or not path or not isinstance(content, str):
            raise ValueError("portable artifact requires path and UTF-8 content")
        artifact_paths.add(path)
        embedded.append({"path": path, "content": content, "content_sha256": content_hash(content)})
    reference_summaries = evidence_summary.get("reference_summaries", {})
    if not isinstance(reference_summaries, Mapping):
        raise ValueError("evidence_summary.reference_summaries must be a mapping")
    for ref in request.get("evidence_refs", []):
        if not isinstance(ref, Mapping):
            raise ValueError("review request evidence ref is malformed")
        ref_type, ref_value = ref.get("type"), ref.get("ref")
        if not isinstance(ref_type, str) or not isinstance(ref_value, str):
            raise ValueError("review request evidence ref requires type/ref")
        if ref_type in {"file", "artifact"} and ref_value not in artifact_paths:
            raise ValueError(f"portable bundle missing referenced artifact: {ref_value}")
        if ref_type not in {"file", "artifact", "portable_bundle"} and _evidence_key(ref) not in reference_summaries:
            raise ValueError(f"portable bundle missing evidence summary for: {_evidence_key(ref)}")
    bundle = {
        "schema_version": 3,
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
        if bundle.get("schema_version") not in {1, 2, 3} or bundle.get("bundle_type") != "SELF_CONTAINED_INDEPENDENT_REVIEW":
            return False, "portable review bundle schema/type is invalid"
        if bundle.get("repository_access_required") is not False:
            return False, "manual review bundle must not require repository access"
        embedded_request = bundle.get("review_request")
        if not isinstance(embedded_request, Mapping) or canonical_hash(embedded_request) != canonical_hash(request):
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
            path, content = item.get("path"), item.get("content")
            if not isinstance(path, str) or not path:
                return False, "portable review artifact path is invalid"
            if not isinstance(content, str) or item.get("content_sha256") != content_hash(content):
                return False, "portable review artifact content hash is invalid"
            artifact_paths.add(path)
        if canonical_hash(bundle.get("covered_evidence_refs")) != canonical_hash(request.get("evidence_refs", [])):
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
            ref_type, ref_value = ref.get("type"), ref.get("ref")
            if ref_type in {"file", "artifact"} and ref_value not in artifact_paths:
                return False, f"portable review bundle missing referenced artifact: {ref_value}"
            if ref_type not in {"file", "artifact", "portable_bundle"} and _evidence_key(ref) not in reference_summaries:
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
    reviewer_provider: str | None = None
    reviewer_model: str | None = None
    identity_assurance: str = "UNVERIFIED"


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
            portable_bundle_hash=str(self.portable_bundle["bundle_hash"]),
            identity_assurance="UNVERIFIED_MANUAL_RELAY",
        )


def ingest_manual_relay_response(
    *,
    request: Mapping[str, Any],
    evidence: Mapping[str, Any],
    portable_bundle_hash: str | None = None,
) -> DispatchResult:
    ok, reason = verify_review_request(request)
    if not ok:
        raise ValueError(reason)
    return DispatchResult(
        transport="MANUAL_RELAY",
        state="REVIEW_RECEIVED",
        review_request_id=str(request["review_request_id"]),
        payload_hash=canonical_hash(request),
        response=deepcopy(dict(evidence)),
        portable_bundle_hash=portable_bundle_hash,
        identity_assurance="UNVERIFIED_MANUAL_RELAY",
    )


class _APITransportBase:
    def __init__(
        self,
        provider_call: Callable[[Mapping[str, Any]], Mapping[str, Any]],
        *,
        provider: str,
        model: str,
    ):
        if not provider or not model:
            raise ValueError("trusted API adapter requires configured provider/model identity")
        self.provider_call = provider_call
        self.provider = provider
        self.model = model

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
            reviewer_provider=self.provider,
            reviewer_model=self.model,
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
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
                error_class=type(exc).__name__,
                identity_assurance="UNVERIFIED",
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
    return bool(class_tokens) and all(token in model_tokens for token in class_tokens)


def _coverage_map(evidence: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]] | None, str | None]:
    coverage = evidence.get("review_coverage")
    if not isinstance(coverage, list):
        return None, "semantic review evidence lacks review_coverage"
    by_id: dict[str, Mapping[str, Any]] = {}
    for row in coverage:
        if not isinstance(row, Mapping):
            return None, "review coverage row is malformed"
        dimension_id = row.get("dimension_id")
        if not isinstance(dimension_id, str) or not dimension_id:
            return None, "review coverage dimension_id is missing"
        if dimension_id in by_id:
            return None, f"duplicate review coverage dimension: {dimension_id}"
        status = row.get("status")
        if status not in REVIEW_DIMENSION_STATUSES:
            return None, f"review coverage status is invalid for dimension: {dimension_id}"
        assessment = row.get("assessment")
        if not isinstance(assessment, str) or not assessment.strip():
            return None, f"review coverage assessment is missing for dimension: {dimension_id}"
        refs = row.get("evidence")
        if not isinstance(refs, list):
            return None, f"review coverage evidence must be a list for dimension: {dimension_id}"
        if status in EVIDENCE_REQUIRED_STATUSES:
            if not refs or not all(isinstance(ref, str) and ref.strip() for ref in refs):
                return None, f"review dimension {dimension_id} with status {status} requires non-empty evidence"
        by_id[dimension_id] = row
    return by_id, None


def validate_review_semantics(
    *,
    request: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[bool, str]:
    """Validate disposition against machine-readable review coverage.

    Schema <4 remains readable for historical evidence, but it is not sufficient for
    material promotion. `can_promote_material_transition` enforces that floor.
    """
    try:
        if request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
            return True, "legacy review has no semantic coverage contract; historical content only"
        dimensions = request.get("required_review_dimensions")
        if not isinstance(dimensions, list) or not dimensions:
            return False, "semantic review request lacks required review dimensions"
        by_id, coverage_error = _coverage_map(evidence)
        if by_id is None:
            return False, str(coverage_error)
        expected_ids = [str(item.get("id")) for item in dimensions if isinstance(item, Mapping)]
        if len(expected_ids) != len(dimensions) or set(by_id) != set(expected_ids):
            return False, "review coverage dimensions differ from ReviewRequest"

        disposition = evidence.get("disposition")
        mandatory_ids = {
            str(item["id"])
            for item in dimensions
            if isinstance(item, Mapping) and item.get("mandatory") is True
        }
        statuses = {dimension_id: str(row.get("status")) for dimension_id, row in by_id.items()}

        if disposition == "PASS":
            if any(status != "TESTED_SUPPORTED" for status in statuses.values()):
                return False, "PASS requires every review dimension to be TESTED_SUPPORTED"
            assessment = evidence.get("evidence_assessment")
            if not isinstance(assessment, str):
                return False, "review evidence_assessment must be text"
            if any(pattern.search(assessment) for pattern in PASS_CONTRADICTION_PATTERNS):
                return False, "free-text evidence assessment contradicts PASS coverage"
            return True, "PASS semantic coverage validated"

        if disposition == "BOUNDED_PASS":
            if any(statuses.get(dimension_id) != "TESTED_SUPPORTED" for dimension_id in mandatory_ids):
                return False, "BOUNDED_PASS requires every mandatory review dimension to be TESTED_SUPPORTED"
            return True, "BOUNDED_PASS semantic coverage validated"

        mandatory_incomplete = any(statuses.get(dimension_id) in INCOMPLETE_DIMENSION_STATUSES for dimension_id in mandatory_ids)
        if disposition in {"NOT_TESTED", "INSUFFICIENT_EVIDENCE"}:
            if not mandatory_incomplete:
                return False, f"{disposition} requires at least one incomplete mandatory review dimension"
            return True, f"{disposition} semantic coverage validated as non-promotable"

        if disposition in {"FAIL", "CHANGES_REQUIRED"}:
            findings = evidence.get("findings")
            if not isinstance(findings, list) or not findings:
                return False, f"{disposition} requires at least one finding"
            if not any(status in DEFECT_DIMENSION_STATUSES or status == "INSUFFICIENT" for status in statuses.values()):
                return False, f"{disposition} requires a contradicted, defective, or insufficient review dimension"
            return True, f"{disposition} semantic coverage validated as non-promotable"

        return False, "review disposition is not semantically handled"
    except (KeyError, TypeError, ValueError):
        return False, "review semantic coverage is malformed"


def validate_review_evidence(
    *,
    request: Mapping[str, Any],
    evidence: Mapping[str, Any],
    execution: DispatchResult,
) -> tuple[bool, str]:
    ok, reason = verify_review_request(request)
    if not ok:
        return False, reason
    try:
        if execution.state != "REVIEW_RECEIVED":
            return False, "review execution has not produced received evidence"
        if execution.review_request_id != request.get("review_request_id"):
            return False, "review execution is bound to a different request"
        if execution.payload_hash != canonical_hash(request):
            return False, "review execution changed request semantics"
        if execution.response is None or canonical_hash(execution.response) != canonical_hash(evidence):
            return False, "review evidence differs from transport execution response"
        if evidence.get("review_request_id") != request.get("review_request_id"):
            return False, "review evidence is bound to a different request"
        if evidence.get("reviewed_artifact_commit") != request["artifact"]["commit"]:
            return False, "review evidence is bound to a different artifact commit"
        required = request.get("required_reviewer")
        if not isinstance(required, Mapping):
            return False, "required reviewer identity is missing"
        required_provider = required.get("provider")
        if not isinstance(required_provider, str) or not required_provider:
            return False, "required reviewer provider is missing"
        required_model = required.get("model")
        required_model_class = required.get("model_class")
        if not (
            isinstance(required_model, str) and required_model
            or isinstance(required_model_class, str) and required_model_class
        ):
            return False, "required reviewer model constraint is missing"
        if execution.identity_assurance not in TRUSTED_IDENTITY_ASSURANCE:
            return False, "reviewer identity is not provider-authenticated"
        reviewer_provider = execution.reviewer_provider
        reviewer_model = execution.reviewer_model
        if not isinstance(reviewer_provider, str) or not reviewer_provider:
            return False, "trusted reviewer provider identity is missing"
        if not isinstance(reviewer_model, str) or not reviewer_model:
            return False, "trusted reviewer model identity is missing"
        if reviewer_provider != required_provider:
            return False, "trusted reviewer provider does not satisfy required reviewer"
        if required_model and reviewer_model != required_model:
            return False, "trusted reviewer model does not satisfy required exact model"
        if required_model_class and not _model_matches_class(reviewer_model, str(required_model_class)):
            return False, "trusted reviewer model does not satisfy required model class"
        reviewer_claim = evidence.get("reviewer")
        if not isinstance(reviewer_claim, Mapping):
            return False, "reviewer claim is missing from review content"
        if reviewer_claim.get("provider") != reviewer_provider or reviewer_claim.get("model") != reviewer_model:
            return False, "review content reviewer claim conflicts with trusted execution identity"
        proposer = request.get("proposer", {})
        if reviewer_provider == proposer.get("provider") and reviewer_model == proposer.get("model"):
            return False, "review independence is unproven: proposer and reviewer are identical"
        if request.get("blind_review_required") and evidence.get("independence_attestation") != "BLIND_TO_PROPOSER_CONCLUSION":
            return False, "blind-review attestation is missing"
        if evidence.get("disposition") not in request.get("expected_output", {}).get("allowed_dispositions", []):
            return False, "review disposition is not allowed"
        for field in ("findings", "evidence_assessment"):
            if field not in evidence:
                return False, f"review evidence missing required field: {field}"
        semantic_ok, semantic_reason = validate_review_semantics(request=request, evidence=evidence)
        if not semantic_ok:
            return False, semantic_reason
        return True, "review evidence, semantics, and provenance validated"
    except (KeyError, TypeError, ValueError):
        return False, "review evidence is malformed"


def validate_shared_memory_grounding(
    *,
    authoritative_state: Mapping[str, Any],
    shared_memory: Mapping[str, Any],
) -> tuple[bool, str]:
    try:
        if shared_memory.get("independent_authority") is not False:
            return False, "shared memory claims independent authority"
        work = authoritative_state.get("active_workstream")
        mem_work = shared_memory.get("current_work")
        if not isinstance(work, Mapping) or not isinstance(mem_work, Mapping):
            return False, "authoritative/shared workstream grounding is missing"
        for key, value in {
            "authoritative_branch": work.get("branch"),
            "authoritative_head": work.get("head_commit"),
            "status": work.get("state"),
        }.items():
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
    deterministic_gate_passed: bool,
    authoritative_state: Mapping[str, Any],
    shared_memory: Mapping[str, Any],
    review_request: Mapping[str, Any] | None,
    review_evidence: Mapping[str, Any] | None,
    review_execution: DispatchResult | None,
    trigger: str | None = None,
) -> bool:
    """Material promotion requires current authenticated semantically valid positive review."""
    if not deterministic_gate_passed:
        return False
    grounding_ok, _ = validate_shared_memory_grounding(
        authoritative_state=authoritative_state,
        shared_memory=shared_memory,
    )
    if not grounding_ok:
        return False
    if review_request is None or review_evidence is None or review_execution is None:
        return False
    if review_request.get("schema_version", 0) < SEMANTIC_REVIEW_SCHEMA_VERSION:
        return False
    if review_evidence.get("disposition") not in PROMOTABLE_REVIEW_DISPOSITIONS:
        return False
    active = authoritative_state.get("independent_review")
    if not isinstance(active, Mapping):
        return False
    if active.get("current_review_request_id") != review_request.get("review_request_id"):
        return False
    if active.get("current_review_status") not in PROMOTABLE_REVIEW_STATES:
        return False
    current_commit = active.get("current_reviewed_artifact_commit")
    if current_commit is not None and current_commit != review_request.get("artifact", {}).get("commit"):
        return False
    valid_review, _ = validate_review_evidence(
        request=review_request,
        evidence=review_evidence,
        execution=review_execution,
    )
    return bool(valid_review)
