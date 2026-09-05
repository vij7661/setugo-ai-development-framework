"""Task-specific multidimensional reviewer qualification.

A reviewer is not globally "good" or "bad". Eligibility is evaluated against
pre-registered dimension thresholds for the exact role/task/risk scope. High
surface/discourse quality cannot compensate for a weak safety-critical dimension.
"""
from __future__ import annotations

REQUIRED_DIMENSIONS = (
    "factuality_quality",
    "logical_reasoning_quality",
    "requirement_interpretation_quality",
    "omission_detection_quality",
    "authority_scope_safety",
    "provenance_quality",
    "discourse_quality",
)


def _score(value, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError(f"{field} must be a numeric score in [0, 1]")
    return float(value)


def validate_reviewer_profile(profile: dict) -> dict:
    required = ("reviewer_id", "role", "task_class", "risk_tier", "evidence_ref", "performance_epoch", "sample_count")
    for field in required:
        if field not in profile:
            raise ValueError(f"missing reviewer profile field: {field}")
    for field in ("reviewer_id", "role", "task_class", "risk_tier", "evidence_ref"):
        if not isinstance(profile[field], str) or not profile[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    if not profile.get("independently_adjudicated", False):
        raise ValueError("reviewer profile must be independently adjudicated")
    if not isinstance(profile["performance_epoch"], int) or profile["performance_epoch"] < 1:
        raise ValueError("performance_epoch must be a positive integer")
    if not isinstance(profile["sample_count"], int) or profile["sample_count"] < 1:
        raise ValueError("sample_count must be a positive integer")
    dimensions = profile.get("dimensions")
    if not isinstance(dimensions, dict):
        raise ValueError("dimensions must be an object")
    normalized = {}
    for name in REQUIRED_DIMENSIONS:
        if name not in dimensions:
            raise ValueError(f"missing qualification dimension: {name}")
        normalized[name] = _score(dimensions[name], f"dimensions.{name}")
    return {**profile, "dimensions": normalized}


def evaluate_reviewer_eligibility(policy: dict, profile: dict) -> dict:
    """Evaluate exact-scope reviewer eligibility without collapsing to one average."""
    validated = validate_reviewer_profile(profile)
    for field in ("role", "task_class", "risk_tier"):
        expected = policy.get(field)
        if not isinstance(expected, str) or not expected:
            raise ValueError(f"policy {field} must be pre-registered")
        if validated[field] != expected:
            return {"eligible": False, "reason": f"{field} mismatch", "failed_dimensions": []}

    thresholds = policy.get("dimension_thresholds")
    if not isinstance(thresholds, dict) or not thresholds:
        raise ValueError("dimension_thresholds must be a non-empty pre-registered object")
    failed = []
    for dimension, threshold in thresholds.items():
        if dimension not in REQUIRED_DIMENSIONS:
            raise ValueError(f"unsupported qualification dimension: {dimension}")
        threshold_value = _score(threshold, f"dimension_thresholds.{dimension}")
        if validated["dimensions"][dimension] < threshold_value:
            failed.append(dimension)

    min_samples = policy.get("min_samples")
    if not isinstance(min_samples, int) or min_samples < 1:
        raise ValueError("min_samples must be a positive pre-registered integer")
    if validated["sample_count"] < min_samples:
        return {"eligible": False, "reason": "insufficient samples", "failed_dimensions": failed}

    if failed:
        return {"eligible": False, "reason": "dimension threshold failed", "failed_dimensions": sorted(failed)}
    return {
        "eligible": True,
        "reason": "all required task-specific qualification dimensions passed",
        "failed_dimensions": [],
        "reviewer_id": validated["reviewer_id"],
        "performance_epoch": validated["performance_epoch"],
    }
