"""Deterministic protocol checks for EXP-G cross-model adversarial review."""
from __future__ import annotations

_REQUIRED_IDENTITY = (
    "provider",
    "model",
    "sku",
    "deployment_path",
    "qualification_ref",
    "qualification_epoch",
    "foundation_lineage",
)


def _complete_identity(actor: dict) -> bool:
    return all(actor.get(k) not in (None, "") for k in _REQUIRED_IDENTITY)


def validate_cross_model_run(run: dict) -> dict:
    """Fail closed unless a sequential cross-model run preserves experimental boundaries."""
    required = [
        "case_id",
        "case_version",
        "requirements_hash",
        "builder",
        "builder_artifact_hash",
        "reviewer",
        "reviewer_output_hash",
        "reviewer_input",
        "ground_truth_ref",
        "ground_truth_hash",
        "role_assignment_id",
    ]
    missing = [k for k in required if run.get(k) in (None, "")]
    if missing:
        return {"valid": False, "reason": "EXP-G run metadata incomplete", "missing": missing}

    builder = run["builder"]
    reviewer = run["reviewer"]
    if not isinstance(builder, dict) or not isinstance(reviewer, dict):
        return {"valid": False, "reason": "builder/reviewer identity malformed"}
    if not _complete_identity(builder) or not _complete_identity(reviewer):
        return {"valid": False, "reason": "builder/reviewer qualification identity incomplete"}
    if builder.get("qualification_status") != "QUALIFIED" or reviewer.get("qualification_status") != "QUALIFIED":
        return {"valid": False, "reason": "builder/reviewer must be currently qualified"}

    if run.get("reviewer_complete") is not True:
        return {"valid": False, "reason": "reviewer output incomplete or truncated"}

    reviewer_input = run.get("reviewer_input")
    if not isinstance(reviewer_input, dict):
        return {"valid": False, "reason": "reviewer input malformed"}
    forbidden = {"builder_private_reasoning", "builder_chain_of_thought", "protected_ground_truth"}
    leaked = sorted(k for k in forbidden if k in reviewer_input)
    if leaked:
        return {"valid": False, "reason": "reviewer blinding boundary violated", "leaked_fields": leaked}

    if reviewer_input.get("builder_artifact_hash") != run.get("builder_artifact_hash"):
        return {"valid": False, "reason": "reviewer did not receive the frozen builder artifact"}
    if reviewer_input.get("requirements_hash") != run.get("requirements_hash"):
        return {"valid": False, "reason": "reviewer requirements binding drifted"}

    if run.get("risk_tier") == "HIGH" and builder.get("foundation_lineage") == reviewer.get("foundation_lineage"):
        return {"valid": False, "reason": "high-risk builder/reviewer foundation lineage is correlated"}

    if run.get("reviewer_claims_release_authority") is True:
        return {"valid": False, "reason": "reviewer cannot grant release authority"}

    adjudicator = run.get("adjudicator")
    if adjudicator is not None:
        if not isinstance(adjudicator, dict) or not _complete_identity(adjudicator):
            return {"valid": False, "reason": "adjudicator identity incomplete"}
        if adjudicator.get("qualification_status") != "QUALIFIED":
            return {"valid": False, "reason": "adjudicator must be currently qualified"}
        if run.get("adjudicator_claims_release_authority") is True:
            return {"valid": False, "reason": "adjudicator cannot grant release authority"}

    return {"valid": True, "reason": "EXP-G cross-model review protocol bindings satisfied"}


def validate_role_reversal(pair: list[dict]) -> dict:
    """Require a matched A→B / B→A pair for role-order analysis."""
    if not isinstance(pair, list) or len(pair) != 2:
        return {"valid": False, "reason": "role reversal requires exactly two matched runs"}
    first, second = pair
    for run in pair:
        check = validate_cross_model_run(run)
        if not check["valid"]:
            return {"valid": False, "reason": "role-reversal member invalid", "detail": check}
    if first.get("role_reversal_pair_id") in (None, "") or first.get("role_reversal_pair_id") != second.get("role_reversal_pair_id"):
        return {"valid": False, "reason": "role-reversal pair identity mismatch"}

    f_builder = first["builder"]
    f_reviewer = first["reviewer"]
    s_builder = second["builder"]
    s_reviewer = second["reviewer"]
    identity = lambda x: (x.get("provider"), x.get("model"), x.get("sku"), x.get("deployment_path"))
    if identity(f_builder) != identity(s_reviewer) or identity(f_reviewer) != identity(s_builder):
        return {"valid": False, "reason": "models were not actually role-reversed"}
    if first.get("case_version") != second.get("case_version") or first.get("requirements_hash") != second.get("requirements_hash"):
        return {"valid": False, "reason": "role-reversal cases are not matched"}
    return {"valid": True, "reason": "matched cross-model role reversal verified"}
