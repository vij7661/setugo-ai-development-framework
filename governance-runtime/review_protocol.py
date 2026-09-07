#!/usr/bin/env python3
"""Transport-neutral independent-review protocol for governed authority transitions.

Governance policy determines whether review is required. Review transport only
moves the same ReviewRequest/ReviewEvidence objects. Manual relay and automatic
API delivery MUST NOT change promotion eligibility or evidence requirements.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Callable, Mapping

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
})

ALLOWED_TRANSPORTS = frozenset({"MANUAL_RELAY", "AUTOMATIC_API"})
ALLOWED_REQUEST_STATES = frozenset({
    "REVIEW_REQUIRED",
    "PENDING_EXTERNAL_REVIEW",
    "REVIEW_RECEIVED",
    "REVIEW_VALIDATED",
    "REVIEW_REJECTED",
})


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def review_required(trigger: str) -> bool:
    """Deterministically decide whether an authority transition needs review."""
    return trigger in MANDATORY_REVIEW_TRIGGERS


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
) -> dict[str, Any]:
    if not review_required(trigger):
        raise ValueError(f"trigger does not require independent review: {trigger}")
    if not SHA40.fullmatch(artifact_commit):
        raise ValueError("artifact_commit must be an exact lowercase 40-character Git SHA")
    if not review_request_id or not artifact_type or not artifact_ref:
        raise ValueError("review request identity and artifact identity are required")
    if not proposer.get("model") or not proposer.get("provider"):
        raise ValueError("proposer model/provider identity is required")
    if not required_reviewer.get("provider"):
        raise ValueError("required reviewer provider identity is required")
    if not review_questions:
        raise ValueError("at least one review question is required")

    request = {
        "schema_version": 1,
        "review_request_id": review_request_id,
        "trigger": trigger,
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
        if request.get("schema_version") != 1:
            return False, "unsupported review request schema"
        if request.get("trigger") not in MANDATORY_REVIEW_TRIGGERS:
            return False, "review trigger is not a mandatory-review trigger"
        artifact = request.get("artifact")
        if not isinstance(artifact, Mapping) or not SHA40.fullmatch(str(artifact.get("commit", ""))):
            return False, "review artifact commit is invalid"
        if request.get("state") not in ALLOWED_REQUEST_STATES:
            return False, "review request state is invalid"
        return True, "review request verified"
    except (KeyError, TypeError, ValueError):
        return False, "review request is malformed"


@dataclass(frozen=True)
class DispatchResult:
    transport: str
    state: str
    review_request_id: str
    payload_hash: str
    response: Mapping[str, Any] | None = None


class ManualRelayTransport:
    name = "MANUAL_RELAY"

    def dispatch(self, request: Mapping[str, Any]) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        return DispatchResult(
            transport=self.name,
            state="PENDING_EXTERNAL_REVIEW",
            review_request_id=str(request["review_request_id"]),
            payload_hash=canonical_hash(request),
            response=None,
        )


class AutomaticAPITransport:
    name = "AUTOMATIC_API"

    def __init__(self, provider_call: Callable[[Mapping[str, Any]], Mapping[str, Any]]):
        self.provider_call = provider_call

    def dispatch(self, request: Mapping[str, Any]) -> DispatchResult:
        ok, reason = verify_review_request(request)
        if not ok:
            raise ValueError(reason)
        # The transport receives the exact same immutable logical request used by
        # manual relay. The provider client is injected so governance policy is
        # independent of any specific API/vendor implementation.
        response = deepcopy(dict(self.provider_call(deepcopy(dict(request)))))
        return DispatchResult(
            transport=self.name,
            state="REVIEW_RECEIVED",
            review_request_id=str(request["review_request_id"]),
            payload_hash=canonical_hash(request),
            response=response,
        )


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
        proposer = request.get("proposer", {})
        if (
            reviewer.get("provider") == proposer.get("provider")
            and reviewer.get("model") == proposer.get("model")
        ):
            return False, "review independence is unproven: proposer and reviewer are identical"
        required = request.get("required_reviewer", {})
        if required.get("provider") and reviewer.get("provider") != required.get("provider"):
            return False, "reviewer provider does not satisfy the required reviewer"
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


def can_promote_material_transition(
    *,
    trigger: str,
    deterministic_gate_passed: bool,
    valid_independent_review_present: bool,
) -> bool:
    """Transport never appears here: it cannot alter promotion eligibility."""
    if not deterministic_gate_passed:
        return False
    if review_required(trigger) and not valid_independent_review_present:
        return False
    return True
