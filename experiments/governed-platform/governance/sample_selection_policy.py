"""Pre-registered sample-selection rules for experimental LLM evidence.

Repeated model calls are evidence only if the selection/aggregation policy was
frozen before execution. Post-hoc "pick the best/longest/most confident" rules
are intentionally rejected.
"""
from __future__ import annotations

ALLOWED_STRATEGIES = {"FIRST_VALID", "ALL_VALID_SCORED", "PRE_REGISTERED_INDEX"}
FORBIDDEN_POST_HOC_FIELDS = {
    "pick_best",
    "prefer_longest",
    "prefer_most_confident",
    "prefer_most_polished",
    "post_hoc_selection",
}


def validate_sampling_policy(policy: dict) -> dict:
    if not isinstance(policy.get("policy_version"), str) or not policy["policy_version"].strip():
        raise ValueError("policy_version must be pre-registered")
    strategy = policy.get("strategy")
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError("sampling strategy is not permitted")
    count = policy.get("sample_count")
    if not isinstance(count, int) or count < 1:
        raise ValueError("sample_count must be a positive pre-registered integer")
    forbidden = sorted(name for name in FORBIDDEN_POST_HOC_FIELDS if policy.get(name))
    if forbidden:
        raise ValueError("post-hoc sample selection is forbidden: " + ",".join(forbidden))
    if strategy == "PRE_REGISTERED_INDEX":
        index = policy.get("selected_index")
        if not isinstance(index, int) or index < 0 or index >= count:
            raise ValueError("selected_index must be pre-registered within sample_count")
    elif "selected_index" in policy:
        raise ValueError("selected_index is only valid for PRE_REGISTERED_INDEX")
    return dict(policy)


def select_evidence(policy: dict, samples: list[dict]) -> list[dict]:
    validated = validate_sampling_policy(policy)
    if len(samples) != validated["sample_count"]:
        raise ValueError("observed sample count must equal pre-registered sample_count")
    strategy = validated["strategy"]

    def eligible(sample: dict) -> bool:
        return sample.get("evidence_eligible") is True and sample.get("status") == "PASS"

    if strategy == "FIRST_VALID":
        for sample in samples:
            if eligible(sample):
                return [sample]
        return []
    if strategy == "ALL_VALID_SCORED":
        return [sample for sample in samples if eligible(sample)]

    selected = samples[validated["selected_index"]]
    return [selected] if eligible(selected) else []
