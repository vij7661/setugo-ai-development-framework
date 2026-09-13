"""V24 I11 V6 remediation R3: material authority surface and observation closure."""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    INSUFFICIENT_EVIDENCE,
    digest,
)

MATERIAL = "MATERIAL"
PROVEN_NON_MATERIAL = "PROVEN_NON_MATERIAL"
MATERIALITY_RESULTS = frozenset({MATERIAL, PROVEN_NON_MATERIAL, INSUFFICIENT_EVIDENCE})
MATERIAL_SURFACE_UNRESOLVED = "MATERIAL_AUTHORITY_SURFACE_UNRESOLVED"
AUTHORITY_ADMISSION_REQUIRED = "AUTHORITY_ADMISSION_REQUIRED"


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _strings(v: Any) -> tuple[set[str], list[str]]:
    if not isinstance(v, list):
        return set(), ["LIST_REQUIRED"]
    out: set[str] = set()
    p: list[str] = []
    for x in v:
        if not _nonempty(x):
            p.append("STRING_MEMBER_INVALID")
        elif x in out:
            p.append(f"DUPLICATE_MEMBER:{x}")
        else:
            out.add(x)
    return out, p


def _record_digest(rec: Mapping[str, Any]) -> str:
    x = dict(rec)
    x.pop("record_digest", None)
    return digest(x)


def validate_material_observation_ledger(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate append-only material observation records and durable current head."""
    p: list[str] = []
    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        p.append("MATERIAL_OBSERVATION_RECORDS_REQUIRED")

    expected_prev = bundle.get("genesis_predecessor_digest")
    if expected_prev is not None and not _sha(expected_prev):
        p.append("MATERIAL_OBSERVATION_GENESIS_PREDECESSOR_INVALID")

    record_digests: list[str] = []
    seen_ids: set[str] = set()
    seen_seq: set[int] = set()
    expected_seq = 1
    observation_entities: set[str] = set()
    for rec in records:
        if not isinstance(rec, Mapping):
            p.append("MATERIAL_OBSERVATION_RECORD_MALFORMED")
            continue
        oid = rec.get("observation_id")
        seq = rec.get("observation_sequence")
        if not _nonempty(oid):
            p.append("MATERIAL_OBSERVATION_ID_REQUIRED")
        elif oid in seen_ids:
            p.append(f"MATERIAL_OBSERVATION_ID_DUPLICATE:{oid}")
        else:
            seen_ids.add(oid)
        if not isinstance(seq, int) or seq < 1:
            p.append(f"MATERIAL_OBSERVATION_SEQUENCE_INVALID:{oid}")
        else:
            if seq in seen_seq:
                p.append(f"MATERIAL_OBSERVATION_SEQUENCE_DUPLICATE:{seq}")
            seen_seq.add(seq)
            if seq != expected_seq:
                p.append(f"MATERIAL_OBSERVATION_SEQUENCE_GAP:{expected_seq}:{seq}")
            expected_seq = seq + 1
        if rec.get("predecessor_record_digest") != expected_prev:
            p.append(f"MATERIAL_OBSERVATION_PREDECESSOR_MISMATCH:{oid}")
        for key in (
            "observer_identity", "observer_control_domain_id", "source_kind",
            "entity_or_path_id", "evidence_class_id", "currentness_binding_digest",
        ):
            if not _nonempty(rec.get(key)):
                p.append(f"MATERIAL_OBSERVATION_FIELD_REQUIRED:{oid}:{key}")
        if _nonempty(rec.get("entity_or_path_id")):
            observation_entities.add(rec["entity_or_path_id"])
        for key in ("evidence_digest", "currentness_binding_digest"):
            if not _sha(rec.get(key)):
                p.append(f"MATERIAL_OBSERVATION_DIGEST_INVALID:{oid}:{key}")
        supplied = rec.get("record_digest")
        computed = _record_digest(rec)
        if supplied != computed:
            p.append(f"MATERIAL_OBSERVATION_RECORD_DIGEST_MISMATCH:{oid}")
        record_digests.append(computed)
        expected_prev = computed

    head = bundle.get("head")
    if not isinstance(head, Mapping):
        head = {}
        p.append("MATERIAL_OBSERVATION_HEAD_REQUIRED")
    expected_latest_seq = len(records)
    expected_latest_digest = record_digests[-1] if record_digests else bundle.get("genesis_predecessor_digest")
    expected_cumulative = digest(record_digests)
    if head.get("latest_sequence") != expected_latest_seq:
        p.append("MATERIAL_OBSERVATION_HEAD_SEQUENCE_MISMATCH")
    if head.get("latest_record_digest") != expected_latest_digest:
        p.append("MATERIAL_OBSERVATION_HEAD_RECORD_DIGEST_MISMATCH")
    if head.get("cumulative_root_digest") != expected_cumulative:
        p.append("MATERIAL_OBSERVATION_CUMULATIVE_ROOT_MISMATCH")
    for key in ("ledger_id", "durable_storage_identity", "durable_anchor_identity"):
        if not _nonempty(head.get(key)):
            p.append(f"MATERIAL_OBSERVATION_HEAD_FIELD_REQUIRED:{key}")
    if not _sha(head.get("durable_anchor_digest")):
        p.append("MATERIAL_OBSERVATION_ANCHOR_DIGEST_INVALID")
    if head.get("anchor_sequence") != expected_latest_seq:
        p.append("MATERIAL_OBSERVATION_ANCHOR_SEQUENCE_MISMATCH")
    if head.get("fork_or_rollback_detected") is not False:
        p.append("MATERIAL_OBSERVATION_FORK_OR_ROLLBACK_DETECTED")

    witnesses = head.get("witness_currentness_records")
    if not isinstance(witnesses, list) or not witnesses:
        p.append("MATERIAL_OBSERVATION_INDEPENDENT_WITNESS_REQUIRED")
        witnesses = []
    independent_current = 0
    operator_domain = head.get("operator_control_domain_id")
    for idx, w in enumerate(witnesses):
        if not isinstance(w, Mapping):
            p.append(f"MATERIAL_OBSERVATION_WITNESS_MALFORMED:{idx}")
            continue
        if w.get("observed_head_digest") != expected_cumulative:
            p.append(f"MATERIAL_OBSERVATION_WITNESS_HEAD_MISMATCH:{idx}")
        if w.get("observed_sequence") != expected_latest_seq:
            p.append(f"MATERIAL_OBSERVATION_WITNESS_SEQUENCE_MISMATCH:{idx}")
        if w.get("currentness_result") != CURRENT:
            p.append(f"MATERIAL_OBSERVATION_WITNESS_NOT_CURRENT:{idx}")
        if w.get("independence_result") != QUALIFIED:
            p.append(f"MATERIAL_OBSERVATION_WITNESS_NOT_INDEPENDENT:{idx}")
        if w.get("witness_control_domain_id") == operator_domain:
            p.append(f"MATERIAL_OBSERVATION_WITNESS_OPERATOR_DOMAIN_CONFLICT:{idx}")
        elif w.get("currentness_result") == CURRENT and w.get("independence_result") == QUALIFIED:
            independent_current += 1
    if independent_current < 1:
        p.append("MATERIAL_OBSERVATION_NO_QUALIFIED_INDEPENDENT_WITNESS")

    p = sorted(set(p))
    return {
        "state": "MATERIAL_OBSERVATION_LEDGER_CURRENT" if not p else "MATERIAL_OBSERVATION_LEDGER_INVALID",
        "qualified": not p,
        "problems": p,
        "head_digest": expected_cumulative,
        "latest_sequence": expected_latest_seq,
        "observed_entity_or_path_ids": sorted(observation_entities),
        "authority_effect": AUTHORITY_EFFECT,
    }


def derive_material_authority_surface(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Require independently controlled material-surface derivations and exact consensus."""
    p: list[str] = []
    if bundle.get("observation_ledger_state") != QUALIFIED:
        p.append("MATERIAL_SURFACE_OBSERVATION_LEDGER_NOT_QUALIFIED")
    observation_head = bundle.get("observation_head_digest")
    if not _sha(observation_head):
        p.append("MATERIAL_SURFACE_OBSERVATION_HEAD_INVALID")
    observed, op = _strings(bundle.get("observed_entity_or_path_ids"))
    p.extend(f"OBSERVED:{x}" for x in op)

    derivations = bundle.get("derivations")
    if not isinstance(derivations, list) or len(derivations) < 2:
        derivations = derivations if isinstance(derivations, list) else []
        p.append("MATERIAL_SURFACE_TWO_INDEPENDENT_DERIVATIONS_REQUIRED")
    member_sets: list[set[str]] = []
    control_domains: set[str] = set()
    for idx, d in enumerate(derivations):
        if not isinstance(d, Mapping):
            p.append(f"MATERIAL_SURFACE_DERIVATION_MALFORMED:{idx}")
            continue
        for key in ("derivation_id", "derivation_mechanism_id", "derivation_authority_id", "control_domain_id"):
            if not _nonempty(d.get(key)):
                p.append(f"MATERIAL_SURFACE_DERIVATION_FIELD_REQUIRED:{idx}:{key}")
        if d.get("mechanism_qualification_state") != QUALIFIED:
            p.append(f"MATERIAL_SURFACE_DERIVATION_MECHANISM_NOT_QUALIFIED:{idx}")
        if d.get("authority_independence_state") != QUALIFIED:
            p.append(f"MATERIAL_SURFACE_DERIVATION_AUTHORITY_NOT_INDEPENDENT:{idx}")
        if d.get("currentness_result") != CURRENT:
            p.append(f"MATERIAL_SURFACE_DERIVATION_NOT_CURRENT:{idx}")
        domain = d.get("control_domain_id")
        if _nonempty(domain):
            if domain in control_domains:
                p.append(f"MATERIAL_SURFACE_DERIVATION_CONTROL_DOMAIN_DUPLICATE:{domain}")
            control_domains.add(domain)
        members, mp = _strings(d.get("member_ids"))
        p.extend(f"MATERIAL_SURFACE_DERIVATION_MEMBERS:{idx}:{x}" for x in mp)
        if not members:
            p.append(f"MATERIAL_SURFACE_DERIVATION_EMPTY:{idx}")
        member_sets.append(members)
        source_kinds, sp = _strings(d.get("source_kinds"))
        p.extend(f"MATERIAL_SURFACE_DERIVATION_SOURCES:{idx}:{x}" for x in sp)
        if "CANDIDATE_SELF_REPORT" in source_kinds:
            p.append(f"MATERIAL_SURFACE_CANDIDATE_SELF_REPORT_SOURCE_FORBIDDEN:{idx}")
        if not _sha(d.get("derivation_digest")):
            p.append(f"MATERIAL_SURFACE_DERIVATION_DIGEST_INVALID:{idx}")

    consensus: set[str] = set()
    if member_sets:
        consensus = set(member_sets[0])
        for i, members in enumerate(member_sets[1:], 1):
            if members != consensus:
                p.append(f"MATERIAL_SURFACE_DERIVATION_DIVERGENCE:{i}")
    if not observed.issubset(consensus):
        for missing in sorted(observed - consensus):
            p.append(f"MATERIAL_SURFACE_OBSERVED_MEMBER_OMITTED:{missing}")

    classifications = bundle.get("materiality_classifications")
    if not isinstance(classifications, list):
        classifications = []
        p.append("MATERIALITY_CLASSIFICATIONS_REQUIRED")
    class_by_subject: dict[str, Mapping[str, Any]] = {}
    for idx, c in enumerate(classifications):
        if not isinstance(c, Mapping):
            p.append(f"MATERIALITY_CLASSIFICATION_MALFORMED:{idx}")
            continue
        sid = c.get("subject_id")
        if not _nonempty(sid):
            p.append(f"MATERIALITY_SUBJECT_ID_REQUIRED:{idx}")
            continue
        if sid in class_by_subject:
            p.append(f"MATERIALITY_CLASSIFICATION_DUPLICATE:{sid}")
            continue
        class_by_subject[sid] = c
        if c.get("classification") not in MATERIALITY_RESULTS:
            p.append(f"MATERIALITY_CLASSIFICATION_RESULT_INVALID:{sid}")
        if c.get("classifier_qualification_state") != QUALIFIED:
            p.append(f"MATERIALITY_CLASSIFIER_NOT_QUALIFIED:{sid}")
        if c.get("classifier_independence_state") != QUALIFIED:
            p.append(f"MATERIALITY_CLASSIFIER_NOT_INDEPENDENT:{sid}")
        if c.get("currentness_result") != CURRENT:
            p.append(f"MATERIALITY_CLASSIFICATION_NOT_CURRENT:{sid}")
        if c.get("classification") == INSUFFICIENT_EVIDENCE:
            p.append(f"MATERIALITY_CLASSIFICATION_INSUFFICIENT:{sid}")

    for sid in sorted(consensus - set(class_by_subject)):
        p.append(f"MATERIALITY_CLASSIFICATION_MISSING:{sid}")
    for sid in sorted(set(class_by_subject) - consensus):
        p.append(f"MATERIALITY_CLASSIFICATION_OUTSIDE_DERIVED_SURFACE:{sid}")

    material_ids = sorted(sid for sid, c in class_by_subject.items() if c.get("classification") == MATERIAL)
    p = sorted(set(p))
    return {
        "state": "MATERIAL_AUTHORITY_SURFACE_QUALIFIED" if not p else MATERIAL_SURFACE_UNRESOLVED,
        "qualified": not p,
        "problems": p,
        "material_member_ids": material_ids,
        "derived_member_ids": sorted(consensus),
        "surface_digest": digest({"observation_head_digest": observation_head, "derived_member_ids": sorted(consensus), "material_member_ids": material_ids}),
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_material_effect_path(record: Mapping[str, Any], *, current_observation_head: str) -> list[str]:
    p: list[str] = []
    for key in ("path_id", "source_or_writer_id", "sink_id", "effect_class_id", "writer_admission_digest", "capability_digest", "guard_mechanism_digest", "sink_admitted_writer_set_digest", "material_surface_membership_digest", "observation_head_digest"):
        if not _nonempty(record.get(key)):
            p.append(f"MATERIAL_EFFECT_PATH_FIELD_REQUIRED:{key}")
    for key in ("writer_admission_digest", "capability_digest", "guard_mechanism_digest", "sink_admitted_writer_set_digest", "material_surface_membership_digest", "observation_head_digest"):
        if not _sha(record.get(key)):
            p.append(f"MATERIAL_EFFECT_PATH_DIGEST_INVALID:{key}")
    if record.get("writer_admission_state") != QUALIFIED:
        p.append("MATERIAL_EFFECT_PATH_WRITER_NOT_ADMITTED")
    if record.get("capability_state") != QUALIFIED:
        p.append("MATERIAL_EFFECT_PATH_CAPABILITY_NOT_QUALIFIED")
    if record.get("guard_qualification_state") != QUALIFIED:
        p.append("MATERIAL_EFFECT_PATH_GUARD_NOT_QUALIFIED")
    admitted_writers, wp = _strings(record.get("sink_admitted_writer_ids"))
    p.extend(f"MATERIAL_EFFECT_PATH_WRITERS:{x}" for x in wp)
    if record.get("source_or_writer_id") not in admitted_writers:
        p.append("MATERIAL_EFFECT_PATH_WRITER_NOT_ADMITTED_AT_SINK")
    edges, ep = _strings(record.get("dependency_edge_digests"))
    p.extend(f"MATERIAL_EFFECT_PATH_EDGES:{x}" for x in ep)
    if not edges or not all(_sha(x) for x in edges):
        p.append("MATERIAL_EFFECT_PATH_DEPENDENCY_EDGES_REQUIRED")
    control, cp = _strings(record.get("control_plane_evidence_digests"))
    p.extend(f"MATERIAL_EFFECT_PATH_CONTROL:{x}" for x in cp)
    if not control or not all(_sha(x) for x in control):
        p.append("MATERIAL_EFFECT_PATH_CONTROL_EVIDENCE_REQUIRED")
    if record.get("currentness_result") != CURRENT:
        p.append("MATERIAL_EFFECT_PATH_NOT_CURRENT")
    if record.get("observation_head_digest") != current_observation_head:
        p.append("MATERIAL_EFFECT_PATH_OBSERVATION_HEAD_STALE")
    return sorted(set(p))


def evaluate_material_discovery(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Latch real observations into authority evaluation; no caller discovery boolean exists."""
    p: list[str] = []
    if bundle.get("observation_ledger_state") != QUALIFIED:
        p.append("MATERIAL_DISCOVERY_OBSERVATION_LEDGER_NOT_QUALIFIED")
    if bundle.get("material_surface_state") != QUALIFIED:
        p.append("MATERIAL_DISCOVERY_SURFACE_NOT_QUALIFIED")
    observed, op = _strings(bundle.get("observed_material_ids"))
    admitted, ap = _strings(bundle.get("admitted_material_ids"))
    p.extend(f"OBSERVED:{x}" for x in op)
    p.extend(f"ADMITTED:{x}" for x in ap)
    observation_head = bundle.get("observation_head_digest")
    surface_digest = bundle.get("material_surface_digest")
    if not _sha(observation_head):
        p.append("MATERIAL_DISCOVERY_OBSERVATION_HEAD_INVALID")
    if not _sha(surface_digest):
        p.append("MATERIAL_DISCOVERY_SURFACE_DIGEST_INVALID")

    unadmitted = sorted(observed - admitted)
    conditions = []
    for subject_id in unadmitted:
        conditions.append({
            "condition_id": "UNADMITTED_MATERIAL_AUTHORITY_PATH",
            "predicate_id": AUTHORITY_ADMISSION_REQUIRED,
            "subject_id": subject_id,
            "observation_head_digest": observation_head,
            "material_surface_digest": surface_digest,
            "condition_payload_digest": digest({"subject_id": subject_id, "observation_head_digest": observation_head, "material_surface_digest": surface_digest}),
        })
    if unadmitted:
        p.append(AUTHORITY_ADMISSION_REQUIRED)

    p = sorted(set(p))
    return {
        "state": "MATERIAL_DISCOVERY_CLEAR" if not p else "MATERIAL_DISCOVERY_BLOCKED",
        "qualified": not p,
        "problems": p,
        "unadmitted_material_ids": unadmitted,
        "conditions": conditions,
        "observation_head_digest": observation_head,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {"state": "V24_V6_R3_MATERIAL_SURFACE_CONSTRUCTION_READY", "qualified": False, "implementation_workstream": "R3", "authority_effect": AUTHORITY_EFFECT}
