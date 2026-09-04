"""Machine-validated corrective-authority diagnosis contract.

This module turns an evidence-backed structured diagnosis into the maximum
artifact scope that may be changed. A requirement conflict always collapses
automatic mutation authority to zero, even when another defect class is also
present.
"""
from __future__ import annotations

CLASSIFICATIONS = {
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
}

ARTIFACTS_BY_CLASS = {
    "CODE DEFECT": {"production_code"},
    "FIXTURE-DATA DEFECT": {"fixtures", "seed_data", "test_data"},
    "TEST DEFECT": {"tests", "test_harness"},
    "ENVIRONMENT-TOOLING DEFECT": {"ci", "tooling", "environment_config", "build_config"},
    "REQUIREMENT UNRESOLVED": set(),
}


def validate_diagnosis(diagnosis: dict) -> dict:
    required = {
        "primary_failure_class",
        "contributing_failure_classes",
        "authorized_artifact_classes",
        "requirement_resolution_required",
        "evidence_refs",
    }
    missing = sorted(required - diagnosis.keys())
    if missing:
        raise ValueError("missing diagnosis fields: " + ",".join(missing))

    primary = diagnosis["primary_failure_class"]
    contributors = diagnosis["contributing_failure_classes"]
    requested = diagnosis["authorized_artifact_classes"]
    evidence = diagnosis["evidence_refs"]

    if primary not in CLASSIFICATIONS:
        raise ValueError("invalid primary failure class")
    if not isinstance(contributors, list) or any(c not in CLASSIFICATIONS for c in contributors):
        raise ValueError("invalid contributing failure class")
    if primary in contributors:
        raise ValueError("primary failure class must not be duplicated as a contributor")
    if not isinstance(requested, list) or len(requested) != len(set(requested)):
        raise ValueError("authorized artifact classes must be a unique list")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(ref, str) or not ref for ref in evidence):
        raise ValueError("at least one evidence ref is required")

    all_classes = {primary, *contributors}
    unresolved = "REQUIREMENT UNRESOLVED" in all_classes
    if bool(diagnosis["requirement_resolution_required"]) != unresolved:
        raise ValueError("requirement_resolution_required must reflect REQUIREMENT UNRESOLVED")

    allowed = set()
    for failure_class in all_classes:
        allowed.update(ARTIFACTS_BY_CLASS[failure_class])

    if unresolved:
        allowed.clear()

    requested_set = set(requested)
    if not requested_set.issubset(allowed):
        raise ValueError("diagnosis requests artifact authority outside classified scope")

    return {
        "decision": "REQUEST_HUMAN" if unresolved else "REPAIR",
        "authority": "NONE" if unresolved else "CLASSIFICATION_SCOPED",
        "primary_failure_class": primary,
        "contributing_failure_classes": contributors,
        "allowed_artifacts": sorted(allowed),
        "authorized_artifacts": sorted(requested_set),
        "requirement_resolution_required": unresolved,
        "evidence_refs": evidence,
        "human_required": unresolved,
    }
