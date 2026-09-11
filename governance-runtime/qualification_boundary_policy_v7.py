#!/usr/bin/env python3
"""Qualification-boundary policy v7: phase-scoped manual authority roots.

v7 preserves the v6 qualification floor and adds a distinct RELEASE trust root.
The TESTING root cannot satisfy RELEASE authority; RELEASE authority cannot
satisfy TESTING or PRODUCTION authority.
"""
from __future__ import annotations

from typing import Any, Mapping
import hashlib
import json

import qualification_boundary_policy_v4 as legacy
from qualification_boundary_policy_v4 import *  # noqa: F401,F403
from manual_authority_verifier import TRUST_ROOT_ID, verify_manual_authority_attestation
from release_manual_authority_verifier import verify_release_authority_attestation
from release_external_governance_root import (
    RELEASE_TRUST_ROOT_ID,
    RELEASE_EXTERNAL_REPOSITORY,
    RELEASE_EXTERNAL_REPOSITORY_ID,
    RELEASE_EXTERNAL_ROOT_COMMIT,
    RELEASE_EXPECTED_PUBLIC_KEY_DER_SHA256,
)

POLICY_ID = legacy.POLICY_ID
POLICY_VERSION = 7
TERMINAL_AUTHORITY_POLICY = legacy.TERMINAL_AUTHORITY_POLICY
REVIEW_ADJUDICATION_AUTHORITY = legacy.REVIEW_ADJUDICATION_AUTHORITY
ROOT_CAUSE_CLASSES = legacy.ROOT_CAUSE_CLASSES
ROOT_CAUSE_AUTHORITY = legacy.ROOT_CAUSE_AUTHORITY


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _policy_material() -> dict[str, Any]:
    material = dict(legacy._policy_material())
    material["policy_version"] = POLICY_VERSION
    material.update({
        "release_authority_trust_root_id": RELEASE_TRUST_ROOT_ID,
        "release_authority_public_key_der_sha256": RELEASE_EXPECTED_PUBLIC_KEY_DER_SHA256,
        "release_authority_external_repository": RELEASE_EXTERNAL_REPOSITORY,
        "release_authority_external_repository_id": RELEASE_EXTERNAL_REPOSITORY_ID,
        "release_authority_external_root_commit": RELEASE_EXTERNAL_ROOT_COMMIT,
        "release_authority_external_root_must_be_public": True,
        "release_authority_external_root_must_be_archived": True,
        "release_authority_class": "HUMAN_RELEASE_AUTHORITY",
        "release_authority_scopes": [
            "TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
            "TERMINAL_ACTION:RELEASE:BEGIN_PRODUCTION_QUALIFICATION",
        ],
        "cross_phase_root_reuse_forbidden": True,
    })
    return material


def qualification_policy_hash() -> str:
    return hashlib.sha256(_canonical(_policy_material()).encode("utf-8")).hexdigest()


def policy_binding() -> dict[str, Any]:
    return {
        "qualification_policy_id": POLICY_ID,
        "qualification_policy_version": POLICY_VERSION,
        "qualification_policy_hash": qualification_policy_hash(),
    }


def build_unsigned_manual_attestation(*, candidate_sha: str, authority_class: str,
                                      decision_scope: str, evidence_ref: str) -> dict[str, Any]:
    if authority_class == "HUMAN_RELEASE_AUTHORITY":
        trust_root_id = RELEASE_TRUST_ROOT_ID
    elif authority_class == "HUMAN_PRODUCTION_AUTHORITY":
        raise ValueError("PRODUCTION authority trust root is not configured")
    else:
        trust_root_id = TRUST_ROOT_ID
    return {
        "schema_version": 1,
        "candidate_sha": candidate_sha,
        "authority_class": authority_class,
        "decision_scope": decision_scope,
        "evidence_ref": evidence_ref,
        "source_kind": "MANUAL_GOVERNANCE_ATTESTATION",
        **policy_binding(),
        "trust_root_id": trust_root_id,
    }


def verify_authority_binding(binding: Any, *, candidate_sha: str,
                             required_authority_class: str,
                             required_scope: str) -> tuple[bool, str]:
    if not isinstance(binding, Mapping):
        return False, "privileged authority requires a signed manual governance attestation"
    common = dict(
        candidate_sha=candidate_sha,
        required_authority_class=required_authority_class,
        required_scope=required_scope,
        qualification_policy_binding=policy_binding(),
    )
    if required_authority_class == "HUMAN_RELEASE_AUTHORITY":
        return verify_release_authority_attestation(
            binding.get("attestation"), binding.get("signature_b64"), **common
        )
    if required_authority_class == "HUMAN_PRODUCTION_AUTHORITY":
        return False, "PRODUCTION authority trust root is not configured"
    return verify_manual_authority_attestation(
        binding.get("attestation"), binding.get("signature_b64"), **common
    )


def acceptance_boundary_record(*, artifact_type: str, artifact_sha: str,
                               boundary_hash: str, authority_binding: Any = None,
                               approved_by: str | None = None,
                               exposed: bool = False) -> dict[str, Any]:
    if not legacy.preregistration_required(artifact_type=artifact_type):
        raise ValueError("artifact type does not require platform preregistration")
    if approved_by is not None:
        raise ValueError("naked approved_by role strings are not authority")
    ok, reason = verify_authority_binding(
        authority_binding,
        candidate_sha=artifact_sha,
        required_authority_class="HUMAN_GOVERNANCE_OWNER",
        required_scope="ACCEPTANCE_BOUNDARY_APPROVAL",
    )
    if not ok:
        raise ValueError(reason)
    attestation = dict(authority_binding["attestation"])
    if not isinstance(boundary_hash, str) or not boundary_hash:
        raise ValueError("boundary_hash is required")
    return {
        "artifact_type": artifact_type,
        "artifact_sha": artifact_sha,
        "boundary_hash": boundary_hash,
        "approved_by": attestation["authority_class"],
        "authority_evidence_ref": attestation["evidence_ref"],
        "exposed": bool(exposed),
        **policy_binding(),
    }


def root_cause_classification_allowed(*, classification: str, material: bool,
                                      candidate_sha: str | None = None,
                                      authority_binding: Any = None,
                                      classifier_role: str | None = None,
                                      independent_evidence_bound: bool = False) -> tuple[bool, str]:
    if classification not in ROOT_CAUSE_CLASSES:
        return False, "unknown root-cause class"
    expected = ROOT_CAUSE_AUTHORITY["material" if material else "non_material"]
    if material:
        if classifier_role is not None:
            return False, "naked classifier role strings are not authority"
        if not independent_evidence_bound:
            return False, "material root-cause classification lacks bound independent evidence"
        if not isinstance(candidate_sha, str) or not candidate_sha:
            return False, "material root-cause classification requires exact candidate SHA"
        return verify_authority_binding(
            authority_binding,
            candidate_sha=candidate_sha,
            required_authority_class=expected,
            required_scope="MATERIAL_ROOT_CAUSE_CLASSIFICATION",
        )
    if classifier_role not in {None, expected}:
        return False, "classifier role is not authorized for this failure materiality"
    return True, "non-material root cause may use platform deterministic classifier"


def reviewer_finding_adjudication_allowed(*, candidate_sha: str | None = None,
                                           authority_binding: Any = None,
                                           adjudicator_role: str | None = None,
                                           candidate_role: str,
                                           reviewer_role: str,
                                           exact_sha_bound: bool,
                                           raw_finding_preserved: bool) -> tuple[bool, str]:
    if adjudicator_role is not None:
        return False, "naked adjudicator role strings are not authority"
    if not exact_sha_bound:
        return False, "adjudication is not bound to exact candidate SHA"
    if not raw_finding_preserved:
        return False, "raw reviewer finding must be preserved before adjudication"
    if not isinstance(candidate_sha, str) or not candidate_sha:
        return False, "review adjudication requires exact candidate SHA"
    return verify_authority_binding(
        authority_binding,
        candidate_sha=candidate_sha,
        required_authority_class=REVIEW_ADJUDICATION_AUTHORITY,
        required_scope="REVIEW_FINDING_ADJUDICATION",
    )


def terminal_authority_allowed(*, phase: str, action: str,
           candidate_sha: str | None = None,
           authority_binding: Any = None,
           issuer_class: str | None = None,
           provenance_verified: bool = False,
           current: bool = False) -> tuple[bool, str]:
    phase_policy = TERMINAL_AUTHORITY_POLICY.get(phase)
    if not isinstance(phase_policy, Mapping):
        return False, "unknown phase has no terminal-authority policy"
    if action not in phase_policy["permitted_actions"]:
        return False, "terminal action is outside the authority scope for this phase"
    if not isinstance(candidate_sha, str) or not candidate_sha:
        return False, "terminal authority requires exact candidate SHA"
    if not isinstance(authority_binding, Mapping):
        return False, "terminal authority requires signed manual governance attestation"
    permitted = tuple(phase_policy["permitted_issuer_classes"])
    if len(permitted) != 1:
        return False, "terminal-authority policy has ambiguous issuer ownership"
    required_authority_class = permitted[0]
    required_scope = f"TERMINAL_ACTION:{phase}:{action}"
    ok, reason = verify_authority_binding(
        authority_binding,
        candidate_sha=candidate_sha,
        required_authority_class=required_authority_class,
        required_scope=required_scope,
    )
    if not ok:
        return False, reason
    return True, "terminal authority is permitted by signed exact-candidate phase-scoped governance attestation"


__all__ = [name for name in globals() if not name.startswith("_")]
