#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DECISIONS = frozenset({"ACCEPT", "REJECT", "SPLIT"})
REPRODUCTION_STATES = frozenset({"REPRODUCED", "NOT_REPRODUCED", "NOT_APPLICABLE", "IMPRACTICAL"})
ROOT_CAUSE_CLASSES = frozenset({
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "GOVERNANCE-PROCESS DEFECT",
    "REQUIREMENT UNRESOLVED",
    "REVIEWER EVIDENCE ERROR",
})


class AdjudicationPolicyError(ValueError):
    pass


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _nonempty_strings(values: Sequence[str] | None, *, field: str) -> list[str]:
    if values is None:
        return []
    out = list(values)
    if any(not isinstance(x, str) or not x.strip() for x in out):
        raise AdjudicationPolicyError(f"{field} must contain non-empty strings")
    return out


def build_adjudication_record(
    *,
    finding_id: str,
    candidate_sha: str,
    original_review_evidence_hash: str,
    decision: str,
    root_cause_classification: str,
    reproduction_status: str,
    reproduction_evidence_refs: Sequence[str],
    regression_test_sha: str | None,
    governance_change_sha: str | None,
    adjudicator_identity_claim: str,
    alternative_evidence_refs: Sequence[str] | None = None,
    reproduction_impractical_reason: str | None = None,
) -> dict[str, Any]:
    if not isinstance(finding_id, str) or not finding_id.strip():
        raise AdjudicationPolicyError("finding_id is required")
    if not SHA40.fullmatch(str(candidate_sha)):
        raise AdjudicationPolicyError("candidate_sha must be exact lowercase SHA40")
    if not SHA256.fullmatch(str(original_review_evidence_hash)):
        raise AdjudicationPolicyError("original_review_evidence_hash must be SHA-256 hex")
    d = str(decision).upper()
    if d not in DECISIONS:
        raise AdjudicationPolicyError(f"invalid decision: {decision}")
    if root_cause_classification not in ROOT_CAUSE_CLASSES:
        raise AdjudicationPolicyError(f"invalid root cause: {root_cause_classification}")
    rs = str(reproduction_status).upper()
    if rs not in REPRODUCTION_STATES:
        raise AdjudicationPolicyError(f"invalid reproduction_status: {reproduction_status}")
    repro = _nonempty_strings(reproduction_evidence_refs, field="reproduction_evidence_refs")
    alt = _nonempty_strings(alternative_evidence_refs, field="alternative_evidence_refs")
    if regression_test_sha is not None and not SHA40.fullmatch(str(regression_test_sha)):
        raise AdjudicationPolicyError("regression_test_sha must be SHA40 when present")
    if governance_change_sha is not None and not SHA40.fullmatch(str(governance_change_sha)):
        raise AdjudicationPolicyError("governance_change_sha must be SHA40 when present")
    if not isinstance(adjudicator_identity_claim, str) or not adjudicator_identity_claim.strip():
        raise AdjudicationPolicyError("adjudicator_identity_claim is required")

    if rs == "REPRODUCED" and not repro:
        raise AdjudicationPolicyError("REPRODUCED requires reproduction evidence")
    if rs == "IMPRACTICAL":
        if not isinstance(reproduction_impractical_reason, str) or not reproduction_impractical_reason.strip():
            raise AdjudicationPolicyError("IMPRACTICAL requires a reason")
        if not alt:
            raise AdjudicationPolicyError("IMPRACTICAL requires alternative deterministic evidence")
    if d == "ACCEPT":
        if rs == "NOT_REPRODUCED":
            raise AdjudicationPolicyError("cannot ACCEPT a finding that was not reproduced")
        if rs == "NOT_APPLICABLE":
            raise AdjudicationPolicyError("cannot ACCEPT a finding marked NOT_APPLICABLE")
        if rs not in {"REPRODUCED", "IMPRACTICAL"}:
            raise AdjudicationPolicyError("ACCEPT requires reproduced or justified alternative evidence")
    if d == "REJECT" and root_cause_classification == "REVIEWER EVIDENCE ERROR" and not (repro or alt):
        raise AdjudicationPolicyError("reviewer-evidence rejection must cite disconfirming evidence")

    material = {
        "schema_version": 1,
        "finding_id": finding_id,
        "candidate_sha": candidate_sha,
        "original_review_evidence_hash": original_review_evidence_hash,
        "decision": d,
        "root_cause_classification": root_cause_classification,
        "reproduction_status": rs,
        "reproduction_evidence_refs": repro,
        "alternative_evidence_refs": alt,
        "reproduction_impractical_reason": reproduction_impractical_reason,
        "regression_test_sha": regression_test_sha,
        "governance_change_sha": governance_change_sha,
        "adjudicator_identity_claim": adjudicator_identity_claim,
        "adjudicator_identity_authenticated": False,
        "preserve_original_finding": True,
        "authority_effect": "NONE",
    }
    material["record_hash"] = _hash(material)
    return material


def classify_memory_only_rule(*, present_in_shared_memory: bool, present_in_authoritative_git: bool) -> str:
    if present_in_authoritative_git:
        return "AUTHORITATIVE_RULE"
    if present_in_shared_memory:
        return "UNVERIFIED_RULE"
    return "RULE_NOT_PRESENT"


def validate_adjudication_chain(record: Mapping[str, Any], *, candidate_sha: str, original_review_evidence_hash: str) -> bool:
    if not isinstance(record, Mapping):
        raise AdjudicationPolicyError("record must be a mapping")
    if record.get("candidate_sha") != candidate_sha:
        raise AdjudicationPolicyError("adjudication candidate does not match current candidate")
    if record.get("original_review_evidence_hash") != original_review_evidence_hash:
        raise AdjudicationPolicyError("adjudication does not bind the original review evidence")
    if record.get("preserve_original_finding") is not True:
        raise AdjudicationPolicyError("original finding preservation is mandatory")
    if record.get("authority_effect") != "NONE":
        raise AdjudicationPolicyError("adjudication record cannot grant authority")
    material = dict(record)
    supplied = material.pop("record_hash", None)
    if supplied != _hash(material):
        raise AdjudicationPolicyError("adjudication record hash mismatch")
    return True
