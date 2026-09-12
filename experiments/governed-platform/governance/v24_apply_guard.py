"""Central V24 apply-time guard for authority-capable execution paths.

The guard is fail-closed and evidence-only.  A positive receipt means the
supplied V24 prerequisite state is internally current for this exact attempted
apply; it does not itself grant production authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

REQUIRED_QUALIFIED_STATES = (
    "normative_catalog_state",
    "authority_universe_state",
    "effective_control_state",
    "completeness_state",
    "endpoint_precedence_state",
    "admission_state",
    "witness_state",
    "aggregate_budget_state",
    "generation_migration_state",
)


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate_v24_apply(context: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    generation = context.get("governance_generation_id")
    if not isinstance(generation, str) or not generation:
        problems.append("V24_GENERATION_REQUIRED")

    for field in REQUIRED_QUALIFIED_STATES:
        if context.get(field) != "QUALIFIED":
            problems.append(f"V24_PREREQUISITE_NOT_QUALIFIED:{field}")

    decision_generation = context.get("decision_generation_id")
    if decision_generation != generation:
        problems.append("V24_DECISION_GENERATION_STALE")

    current_admission = context.get("current_admission_ledger_digest")
    bound_admission = context.get("decision_admission_ledger_digest")
    if not isinstance(current_admission, str) or not current_admission or current_admission != bound_admission:
        problems.append("V24_ADMISSION_LEDGER_STALE_OR_MISSING")

    current_completeness = context.get("current_completeness_ledger_digest")
    bound_completeness = context.get("decision_completeness_ledger_digest")
    if not isinstance(current_completeness, str) or not current_completeness or current_completeness != bound_completeness:
        problems.append("V24_COMPLETENESS_LEDGER_STALE_OR_MISSING")

    if context.get("material_discovery_pending") is True:
        problems.append("V24_MATERIAL_DISCOVERY_UNRESOLVED")

    perimeter = context.get("admission_perimeter_record")
    sink_id = context.get("sink_id")
    guarded_writer_id = context.get("guarded_writer_id")
    if not isinstance(perimeter, Mapping):
        problems.append("V24_ADMISSION_PERIMETER_RECORD_REQUIRED")
    else:
        if perimeter.get("state") != "CURRENT":
            problems.append("V24_ADMISSION_PERIMETER_STALE")
        if perimeter.get("generation_id") != generation:
            problems.append("V24_ADMISSION_PERIMETER_GENERATION_MISMATCH")
        if perimeter.get("sink_id") != sink_id:
            problems.append("V24_ADMISSION_PERIMETER_SINK_MISMATCH")
        writers = perimeter.get("admitted_writer_ids")
        if not isinstance(writers, list) or guarded_writer_id not in writers:
            problems.append("V24_GUARDED_WRITER_NOT_ADMITTED")
        if not perimeter.get("enforcement_configuration_digest"):
            problems.append("V24_PERIMETER_ENFORCEMENT_DIGEST_REQUIRED")
        if perimeter.get("independent_observation_state") != "QUALIFIED":
            problems.append("V24_PERIMETER_ENFORCEMENT_NOT_INDEPENDENTLY_QUALIFIED")

    decision_digest = context.get("decision_digest")
    transition_digest = context.get("transition_digest")
    sink_set_digest = context.get("sink_set_digest")
    for name, value in (
        ("decision_digest", decision_digest),
        ("transition_digest", transition_digest),
        ("sink_set_digest", sink_set_digest),
    ):
        if not isinstance(value, str) or not value:
            problems.append(f"V24_BINDING_REQUIRED:{name}")

    problems = sorted(set(problems))
    receipt_material = {
        "governance_generation_id": generation,
        "decision_digest": decision_digest,
        "transition_digest": transition_digest,
        "sink_set_digest": sink_set_digest,
        "sink_id": sink_id,
        "guarded_writer_id": guarded_writer_id,
        "admission_ledger_digest": current_admission,
        "completeness_ledger_digest": current_completeness,
        "perimeter_digest": canonical_hash(dict(perimeter)) if isinstance(perimeter, Mapping) else None,
        "problems": problems,
    }
    return {
        "state": "V24_APPLY_READY" if not problems else "V24_APPLY_BLOCKED",
        "allowed": not problems,
        "problems": problems,
        "receipt": receipt_material,
        "guard_receipt_digest": canonical_hash(receipt_material),
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
