"""V24 I11 V6 remediation R4: qualified revalidation snapshot and decision/apply latch."""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, CURRENT, QUALIFIED, digest
from v24_v6_material_surface import validate_material_effect_path
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
)

APPLY_READY = "DECISION_APPLY_LATCH_READY"
APPLY_BLOCKED = "DECISION_APPLY_LATCH_BLOCKED"
REEVALUATION_REQUIRED = "DECISION_APPLY_REEVALUATION_REQUIRED"
SNAPSHOT_SOURCE_INVALID = "REVALIDATION_SNAPSHOT_SOURCE_INVALID"
MIXED_SNAPSHOT_REJECTED = "DECISION_APPLY_MIXED_SNAPSHOT_REJECTED"

LOAD_BEARING_BINDINGS = (
    "endpoint_table_digest",
    "applicability_digest",
    "evaluator_registry_digest",
    "condition_registry_digest",
    "evidence_registry_digest",
    "predicate_coverage_content_digest",
    "predicate_coverage_qualification_digest",
    "material_observation_head_digest",
    "completeness_ledger_head_digest",
    "material_surface_digest",
    "authority_sink_id",
    "writer_identity",
    "guard_mechanism_digest",
)


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _append_proof_problems(prefix: str, result: Mapping[str, Any], problems: list[str]) -> None:
    if result.get("qualified") is True:
        return
    child = result.get("problems")
    if isinstance(child, list) and child:
        problems.extend(f"{prefix}:{item}" for item in child)
    else:
        problems.append(f"{prefix}:PROOF_REFERENCE_CLOSURE_FAILED")


def validate_revalidation_snapshot_source(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> list[str]:
    p: list[str] = []
    for key in (
        "snapshot_source_id",
        "mechanism_id",
        "mechanism_content_digest",
        "snapshot_schema_id",
        "owner_id",
        "owner_control_domain_id",
        "independence_rule_id",
        "currentness_rule_id",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"SNAPSHOT_SOURCE_FIELD_REQUIRED:{key}")
    for key in (
        "mechanism_content_digest",
        "qualification_digest",
        "independence_qualification_digest",
        "currentness_binding_digest",
    ):
        if not _sha(record.get(key)):
            p.append(f"SNAPSHOT_SOURCE_DIGEST_INVALID:{key}")
    if record.get("qualification_state") != QUALIFIED:
        p.append("SNAPSHOT_SOURCE_NOT_QUALIFIED")
    if record.get("independence_state") != QUALIFIED:
        p.append("SNAPSHOT_SOURCE_NOT_INDEPENDENT")
    if record.get("currentness_result") != CURRENT:
        p.append("SNAPSHOT_SOURCE_NOT_CURRENT")
    read_semantics = record.get("read_consistency_semantics")
    if read_semantics not in {"SINGLE_AUTHORITATIVE_SNAPSHOT", "SERIALIZABLE_SNAPSHOT"}:
        p.append("SNAPSHOT_SOURCE_READ_CONSISTENCY_UNADMITTED")
    heads = record.get("authoritative_head_fields")
    if not isinstance(heads, list) or not heads:
        p.append("SNAPSHOT_SOURCE_AUTHORITATIVE_HEAD_FIELDS_REQUIRED")

    proof_result = close_governance_dependencies(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": record.get("qualification_digest"),
                "subject_id": record.get("mechanism_id"),
                "subject_content_digest": record.get("mechanism_content_digest"),
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": record.get("independence_qualification_digest"),
                "subject_identity_id": record.get("mechanism_id"),
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": record.get("currentness_binding_digest"),
                "source_id": record.get("mechanism_id"),
                "source_digest": record.get("mechanism_content_digest"),
            },
        ],
        proof_context,
        trusted_boundary,
    )
    _append_proof_problems("SNAPSHOT_SOURCE_PROOF_CLOSURE", proof_result, p)
    return sorted(set(p))


def canonical_snapshot_digest(snapshot: Mapping[str, Any]) -> str:
    material = {key: snapshot.get(key) for key in LOAD_BEARING_BINDINGS}
    material.update(
        {
            "snapshot_source_id": snapshot.get("snapshot_source_id"),
            "snapshot_sequence": snapshot.get("snapshot_sequence"),
            "snapshot_epoch": snapshot.get("snapshot_epoch"),
        }
    )
    return digest(material)


def validate_revalidation_snapshot(
    snapshot: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> list[str]:
    p = validate_revalidation_snapshot_source(
        source,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    )
    if snapshot.get("snapshot_source_id") != source.get("snapshot_source_id"):
        p.append("SNAPSHOT_SOURCE_ID_MISMATCH")
    sequence = snapshot.get("snapshot_sequence")
    if not isinstance(sequence, int) or sequence < 0:
        p.append("SNAPSHOT_SEQUENCE_INVALID")
    if not _nonempty(snapshot.get("snapshot_epoch")):
        p.append("SNAPSHOT_EPOCH_REQUIRED")
    for key in LOAD_BEARING_BINDINGS:
        value = snapshot.get(key)
        if key in {"authority_sink_id", "writer_identity"}:
            if not _nonempty(value):
                p.append(f"SNAPSHOT_BINDING_REQUIRED:{key}")
        elif not _sha(value):
            p.append(f"SNAPSHOT_DIGEST_INVALID:{key}")
    supplied = snapshot.get("snapshot_digest")
    computed = canonical_snapshot_digest(snapshot)
    if supplied != computed:
        p.append("SNAPSHOT_DIGEST_MISMATCH")
    if snapshot.get("mixed_snapshot_detected") is True:
        p.append(MIXED_SNAPSHOT_REJECTED)
    if snapshot.get("source_qualification_digest") != source.get("qualification_digest"):
        p.append("SNAPSHOT_SOURCE_QUALIFICATION_BINDING_MISMATCH")
    if snapshot.get("source_independence_digest") != source.get("independence_qualification_digest"):
        p.append("SNAPSHOT_SOURCE_INDEPENDENCE_BINDING_MISMATCH")
    if snapshot.get("source_currentness_digest") != source.get("currentness_binding_digest"):
        p.append("SNAPSHOT_SOURCE_CURRENTNESS_BINDING_MISMATCH")
    return sorted(set(p))


def decision_binding_material(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {key: decision.get(key) for key in LOAD_BEARING_BINDINGS}


def _binding_drift(decision: Mapping[str, Any], snapshot: Mapping[str, Any]) -> list[str]:
    return sorted(
        key for key in LOAD_BEARING_BINDINGS if decision.get(key) != snapshot.get(key)
    )


def _validate_decision_proof_fields(decision: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "decision_id",
        "endpoint_projection_id",
        "predicate_coverage_id",
    ):
        if not _nonempty(decision.get(key)):
            p.append(f"DECISION_PROOF_FIELD_REQUIRED:{key}")
    for key in (
        "decision_digest",
        "decision_qualification_digest",
        "endpoint_projection_digest",
        "endpoint_projection_qualification_digest",
        "predicate_coverage_content_digest",
        "predicate_coverage_qualification_digest",
    ):
        if not _sha(decision.get(key)):
            p.append(f"DECISION_PROOF_DIGEST_INVALID:{key}")
    return sorted(set(p))


def _close_decision_proofs(
    decision: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
) -> list[str]:
    p = _validate_decision_proof_fields(decision)
    result = close_governance_dependencies(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": decision.get("decision_qualification_digest"),
                "subject_id": decision.get("decision_id"),
                "subject_content_digest": decision.get("decision_digest"),
            },
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": decision.get("endpoint_projection_qualification_digest"),
                "subject_id": decision.get("endpoint_projection_id"),
                "subject_content_digest": decision.get("endpoint_projection_digest"),
            },
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": decision.get("predicate_coverage_qualification_digest"),
                "subject_id": decision.get("predicate_coverage_id"),
                "subject_content_digest": decision.get("predicate_coverage_content_digest"),
            },
        ],
        proof_context,
        trusted_boundary,
    )
    _append_proof_problems("DECISION_PROOF_CLOSURE", result, p)
    return sorted(set(p))


def validate_reevaluated_decision(
    reevaluated: Mapping[str, Any],
    *,
    snapshot: Mapping[str, Any],
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> list[str]:
    p: list[str] = []
    if reevaluated.get("decision_qualification_state") != QUALIFIED:
        p.append("REEVALUATED_DECISION_NOT_QUALIFIED")
    if reevaluated.get("endpoint_projection_qualification_state") != QUALIFIED:
        p.append("REEVALUATED_ENDPOINT_PROJECTION_NOT_QUALIFIED")
    if reevaluated.get("predicate_coverage_qualification_state") != QUALIFIED:
        p.append("REEVALUATED_PREDICATE_COVERAGE_NOT_QUALIFIED")
    if reevaluated.get("source_snapshot_digest") != snapshot.get("snapshot_digest"):
        p.append("REEVALUATED_DECISION_SNAPSHOT_BINDING_MISMATCH")
    for key in LOAD_BEARING_BINDINGS:
        if reevaluated.get(key) != snapshot.get(key):
            p.append(f"REEVALUATED_DECISION_CURRENT_BINDING_MISMATCH:{key}")
    for key in ("decision_digest", "endpoint_projection_digest"):
        if not _sha(reevaluated.get(key)):
            p.append(f"REEVALUATED_DECISION_DIGEST_INVALID:{key}")
    if reevaluated.get("selected_endpoint_state") not in {"ALLOW", "DENY"}:
        p.append("REEVALUATED_DECISION_ENDPOINT_STATE_INVALID")
    for problem in _close_decision_proofs(
        reevaluated,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    ):
        p.append(f"REEVALUATED:{problem}")
    return sorted(set(p))


def evaluate_decision_apply_latch(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail closed unless one current proof-closed snapshot supports apply.

    Candidate decision data cannot supply the trusted proof boundary.  Qualification,
    independence, and currentness labels remain descriptive claims until their exact
    references close through the separately supplied proof context.
    """
    p: list[str] = []
    source = bundle.get("snapshot_source")
    snapshot = bundle.get("current_snapshot")
    decision = bundle.get("decision")
    if not isinstance(source, Mapping):
        source = {}
        p.append("SNAPSHOT_SOURCE_REQUIRED")
    if not isinstance(snapshot, Mapping):
        snapshot = {}
        p.append("CURRENT_SNAPSHOT_REQUIRED")
    if not isinstance(decision, Mapping):
        decision = {}
        p.append("DECISION_RECORD_REQUIRED")

    for problem in validate_revalidation_snapshot(
        snapshot,
        source,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    ):
        p.append(f"SNAPSHOT:{problem}")

    if decision.get("decision_qualification_state") != QUALIFIED:
        p.append("DECISION_NOT_QUALIFIED")
    if decision.get("endpoint_projection_qualification_state") != QUALIFIED:
        p.append("DECISION_ENDPOINT_PROJECTION_NOT_QUALIFIED")
    if decision.get("predicate_coverage_qualification_state") != QUALIFIED:
        p.append("DECISION_PREDICATE_COVERAGE_NOT_QUALIFIED")
    if not _sha(decision.get("decision_digest")):
        p.append("DECISION_DIGEST_INVALID")
    if not _sha(decision.get("endpoint_projection_digest")):
        p.append("DECISION_ENDPOINT_PROJECTION_DIGEST_INVALID")
    p.extend(
        _close_decision_proofs(
            decision,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
        )
    )

    drift = _binding_drift(decision, snapshot)
    active_decision = decision
    re_evaluated = False
    if drift:
        reevaluated = bundle.get("reevaluated_decision")
        if not isinstance(reevaluated, Mapping):
            p.append(REEVALUATION_REQUIRED)
            p.extend(f"DECISION_BINDING_DRIFT:{key}" for key in drift)
        else:
            rp = validate_reevaluated_decision(
                reevaluated,
                snapshot=snapshot,
                proof_context=proof_context,
                trusted_boundary=trusted_boundary,
            )
            if rp:
                p.extend(f"REEVALUATION:{x}" for x in rp)
                p.extend(f"DECISION_BINDING_DRIFT:{key}" for key in drift)
            else:
                active_decision = reevaluated
                re_evaluated = True

    effect_path = bundle.get("material_effect_path")
    if not isinstance(effect_path, Mapping):
        p.append("MATERIAL_EFFECT_PATH_REQUIRED")
    else:
        for problem in validate_material_effect_path(
            effect_path,
            current_observation_head=snapshot.get("material_observation_head_digest"),
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
        ):
            p.append(f"MATERIAL_EFFECT_PATH:{problem}")
        if effect_path.get("sink_id") != snapshot.get("authority_sink_id"):
            p.append("MATERIAL_EFFECT_PATH_SINK_BINDING_MISMATCH")
        if effect_path.get("source_or_writer_id") != snapshot.get("writer_identity"):
            p.append("MATERIAL_EFFECT_PATH_WRITER_BINDING_MISMATCH")
        if effect_path.get("guard_mechanism_digest") != snapshot.get("guard_mechanism_digest"):
            p.append("MATERIAL_EFFECT_PATH_GUARD_BINDING_MISMATCH")
        if effect_path.get("material_surface_membership_digest") != snapshot.get("material_surface_digest"):
            p.append("MATERIAL_EFFECT_PATH_SURFACE_BINDING_MISMATCH")

    if active_decision.get("selected_endpoint_state") != "ALLOW":
        p.append("APPLY_SELECTED_ENDPOINT_NOT_ALLOW")

    p = sorted(set(p))
    latch_material = {
        "decision_record_digest": active_decision.get("decision_digest"),
        "decision_qualification_digest": active_decision.get("decision_qualification_digest"),
        "decision_context_digest": active_decision.get("decision_context_digest"),
        "endpoint_projection_digest": active_decision.get("endpoint_projection_digest"),
        "endpoint_projection_qualification_digest": active_decision.get(
            "endpoint_projection_qualification_digest"
        ),
        "endpoint_table_digest": snapshot.get("endpoint_table_digest"),
        "applicability_digest": snapshot.get("applicability_digest"),
        "evaluator_registry_digest": snapshot.get("evaluator_registry_digest"),
        "condition_registry_digest": snapshot.get("condition_registry_digest"),
        "evidence_registry_digest": snapshot.get("evidence_registry_digest"),
        "predicate_coverage_content_digest": snapshot.get("predicate_coverage_content_digest"),
        "predicate_coverage_qualification_digest": snapshot.get(
            "predicate_coverage_qualification_digest"
        ),
        "material_observation_head_digest": snapshot.get("material_observation_head_digest"),
        "completeness_ledger_head_digest": snapshot.get("completeness_ledger_head_digest"),
        "material_surface_digest": snapshot.get("material_surface_digest"),
        "authority_sink_id": snapshot.get("authority_sink_id"),
        "writer_identity": snapshot.get("writer_identity"),
        "guard_mechanism_digest": snapshot.get("guard_mechanism_digest"),
        "revalidation_snapshot_source_id": source.get("snapshot_source_id"),
        "revalidation_snapshot_source_qualification_digest": source.get("qualification_digest"),
        "revalidation_snapshot_source_independence_digest": source.get(
            "independence_qualification_digest"
        ),
        "revalidation_snapshot_source_currentness_digest": source.get(
            "currentness_binding_digest"
        ),
        "current_revalidation_snapshot_digest": snapshot.get("snapshot_digest"),
        "re_evaluated": re_evaluated,
        "revalidation_result": "PASS" if not p else "BLOCK",
    }
    return {
        "state": APPLY_READY if not p else APPLY_BLOCKED,
        "allowed": not p,
        "problems": p,
        "drifted_binding_fields": drift,
        "re_evaluated": re_evaluated,
        "active_decision_digest": active_decision.get("decision_digest"),
        "latch_record": latch_material,
        "latch_digest": digest(latch_material),
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R4_DECISION_APPLY_LATCH_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R4",
        "authority_effect": AUTHORITY_EFFECT,
    }
