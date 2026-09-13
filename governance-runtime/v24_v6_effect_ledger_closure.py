"""V24 I11 V6 remediation R6: effect-class completeness and durable ledger closure.

Construction-only validators for V6 Sections 11.1 and 12.  These functions
produce evidence about exact supplied records.  They do not grant runtime,
release, deployment, production, or terminal authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    digest,
    validate_registry_completeness_qualification,
)
from v24_v6_material_surface import validate_material_effect_path

LEDGER_KINDS = frozenset({"MATERIAL_OBSERVATION", "COMPLETENESS"})
DURABLE_STORAGE_CLASSES = frozenset(
    {"DURABLE_APPEND_ONLY", "DURABLE_TRANSACTIONAL", "DURABLE_IMMUTABLE_OBJECT"}
)
DURABLE_ANCHOR_CLASSES = frozenset(
    {"INDEPENDENT_DURABLE_ANCHOR", "GENESIS_DURABLE_ANCHOR"}
)
REQUIRED_EFFECT_SOURCE_CLASSES = frozenset(
    {"IMPLEMENTATION_ARTIFACT", "DEPLOYMENT_ARTIFACT", "EFFECT_OBSERVATION"}
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _unique_strings(value: Any) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], ["LIST_REQUIRED"]
    out: list[str] = []
    seen: set[str] = set()
    problems: list[str] = []
    for item in value:
        if not _nonempty(item):
            problems.append("STRING_MEMBER_INVALID")
            continue
        if item in seen:
            problems.append(f"DUPLICATE_MEMBER:{item}")
            continue
        seen.add(item)
        out.append(item)
    return out, problems


def _without(record: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    material = dict(record)
    for field in fields:
        material.pop(field, None)
    return material


def _record_digest(record: Mapping[str, Any], field: str = "record_digest") -> str:
    return digest(_without(record, field))


def _ledger_head_material(head: Mapping[str, Any]) -> dict[str, Any]:
    """Head digest deliberately excludes witnesses to avoid circular witness binding."""
    return _without(head, "head_digest", "witness_currentness_records")


def validate_durable_governance_ledger(
    bundle: Mapping[str, Any], *, ledger_kind: str
) -> dict[str, Any]:
    """Validate a monotonic, anchored, witnessed current governance ledger.

    The exact V6 rule is fail-closed: process-memory/local unanchored state is
    never sufficient to establish a current authority-bearing head.
    """
    problems: list[str] = []
    if ledger_kind not in LEDGER_KINDS:
        problems.append("DURABLE_LEDGER_KIND_INVALID")

    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        problems.append("DURABLE_LEDGER_RECORDS_REQUIRED")

    genesis = bundle.get("genesis_predecessor_digest")
    if not _sha(genesis):
        problems.append("DURABLE_LEDGER_GENESIS_PREDECESSOR_INVALID")

    expected_predecessor = genesis
    record_digests: list[str] = []
    seen_ids: set[str] = set()
    expected_sequence = 1

    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            problems.append(f"DURABLE_LEDGER_RECORD_MALFORMED:{index}")
            continue
        rid = record.get("record_id")
        if not _nonempty(rid):
            problems.append(f"DURABLE_LEDGER_RECORD_ID_REQUIRED:{index}")
            rid = f"INDEX-{index}"
        elif rid in seen_ids:
            problems.append(f"DURABLE_LEDGER_RECORD_ID_DUPLICATE:{rid}")
        seen_ids.add(rid)

        if record.get("ledger_kind") != ledger_kind:
            problems.append(f"DURABLE_LEDGER_RECORD_KIND_MISMATCH:{rid}")
        sequence = record.get("sequence")
        if sequence != expected_sequence:
            problems.append(
                f"DURABLE_LEDGER_SEQUENCE_NOT_MONOTONIC:{rid}:{expected_sequence}:{sequence}"
            )
        expected_sequence += 1
        if record.get("predecessor_record_digest") != expected_predecessor:
            problems.append(f"DURABLE_LEDGER_PREDECESSOR_MISMATCH:{rid}")

        for key in (
            "producer_identity_id",
            "producer_control_domain_id",
            "evidence_class_id",
            "event_or_subject_id",
        ):
            if not _nonempty(record.get(key)):
                problems.append(f"DURABLE_LEDGER_RECORD_FIELD_REQUIRED:{rid}:{key}")
        if not _sha(record.get("event_digest")):
            problems.append(f"DURABLE_LEDGER_EVENT_DIGEST_INVALID:{rid}")

        computed = _record_digest(record)
        if record.get("record_digest") != computed:
            problems.append(f"DURABLE_LEDGER_RECORD_DIGEST_MISMATCH:{rid}")
        record_digests.append(computed)
        expected_predecessor = computed

    head = bundle.get("head")
    if not isinstance(head, Mapping):
        head = {}
        problems.append("DURABLE_LEDGER_HEAD_REQUIRED")

    latest_sequence = len(records)
    latest_record_digest = record_digests[-1] if record_digests else genesis
    cumulative_root = digest(record_digests)

    if head.get("ledger_kind") != ledger_kind:
        problems.append("DURABLE_LEDGER_HEAD_KIND_MISMATCH")
    for key in (
        "ledger_id",
        "operator_identity_id",
        "operator_control_domain_id",
        "durable_storage_identity",
        "durable_anchor_identity",
    ):
        if not _nonempty(head.get(key)):
            problems.append(f"DURABLE_LEDGER_HEAD_FIELD_REQUIRED:{key}")

    storage_class = head.get("durable_storage_class")
    if storage_class not in DURABLE_STORAGE_CLASSES:
        problems.append("DURABLE_LEDGER_STORAGE_NOT_DURABLE")
    anchor_class = head.get("durable_anchor_class")
    if anchor_class not in DURABLE_ANCHOR_CLASSES:
        problems.append("DURABLE_LEDGER_ANCHOR_NOT_DURABLE")

    if head.get("latest_sequence") != latest_sequence:
        problems.append("DURABLE_LEDGER_HEAD_SEQUENCE_MISMATCH")
    if head.get("latest_record_digest") != latest_record_digest:
        problems.append("DURABLE_LEDGER_HEAD_RECORD_DIGEST_MISMATCH")
    if head.get("cumulative_root_digest") != cumulative_root:
        problems.append("DURABLE_LEDGER_CUMULATIVE_ROOT_MISMATCH")
    if head.get("anchor_sequence") != latest_sequence:
        problems.append("DURABLE_LEDGER_ANCHOR_SEQUENCE_MISMATCH")
    if not _sha(head.get("durable_anchor_digest")):
        problems.append("DURABLE_LEDGER_ANCHOR_DIGEST_INVALID")
    if head.get("fork_or_rollback_detected") is not False:
        problems.append("DURABLE_LEDGER_FORK_OR_ROLLBACK_DETECTED")
    if head.get("head_qualification_state") != QUALIFIED:
        problems.append("DURABLE_LEDGER_HEAD_NOT_QUALIFIED")
    if head.get("currentness_result") != CURRENT:
        problems.append("DURABLE_LEDGER_HEAD_NOT_CURRENT")

    computed_head_digest = digest(_ledger_head_material(head))
    if head.get("head_digest") != computed_head_digest:
        problems.append("DURABLE_LEDGER_HEAD_DIGEST_MISMATCH")

    witnesses = head.get("witness_currentness_records")
    if not isinstance(witnesses, list) or not witnesses:
        witnesses = []
        problems.append("DURABLE_LEDGER_INDEPENDENT_WITNESS_REQUIRED")

    operator_domain = head.get("operator_control_domain_id")
    qualified_independent_witnesses = 0
    seen_witness_ids: set[str] = set()
    for index, witness in enumerate(witnesses):
        if not isinstance(witness, Mapping):
            problems.append(f"DURABLE_LEDGER_WITNESS_MALFORMED:{index}")
            continue
        wid = witness.get("witness_identity_id")
        if not _nonempty(wid):
            problems.append(f"DURABLE_LEDGER_WITNESS_ID_REQUIRED:{index}")
            wid = f"INDEX-{index}"
        elif wid in seen_witness_ids:
            problems.append(f"DURABLE_LEDGER_WITNESS_DUPLICATE:{wid}")
        seen_witness_ids.add(wid)

        for key in (
            "witness_control_domain_id",
            "evidence_class_id",
            "currentness_rule_id",
        ):
            if not _nonempty(witness.get(key)):
                problems.append(f"DURABLE_LEDGER_WITNESS_FIELD_REQUIRED:{wid}:{key}")
        if not _sha(witness.get("independence_qualification_digest")):
            problems.append(
                f"DURABLE_LEDGER_WITNESS_INDEPENDENCE_DIGEST_INVALID:{wid}"
            )
        if witness.get("observed_head_digest") != computed_head_digest:
            problems.append(f"DURABLE_LEDGER_WITNESS_HEAD_MISMATCH:{wid}")
        if witness.get("observed_sequence") != latest_sequence:
            problems.append(f"DURABLE_LEDGER_WITNESS_SEQUENCE_MISMATCH:{wid}")
        if witness.get("currentness_result") != CURRENT:
            problems.append(f"DURABLE_LEDGER_WITNESS_NOT_CURRENT:{wid}")
        if witness.get("independence_result") != QUALIFIED:
            problems.append(f"DURABLE_LEDGER_WITNESS_NOT_INDEPENDENT:{wid}")
        if witness.get("witness_control_domain_id") == operator_domain:
            problems.append(f"DURABLE_LEDGER_WITNESS_OPERATOR_DOMAIN_CONFLICT:{wid}")
        if not _sha(witness.get("witness_record_digest")):
            problems.append(f"DURABLE_LEDGER_WITNESS_RECORD_DIGEST_INVALID:{wid}")
        elif witness.get("witness_record_digest") != _record_digest(
            witness, "witness_record_digest"
        ):
            problems.append(f"DURABLE_LEDGER_WITNESS_RECORD_DIGEST_MISMATCH:{wid}")

        if (
            witness.get("currentness_result") == CURRENT
            and witness.get("independence_result") == QUALIFIED
            and _nonempty(witness.get("witness_control_domain_id"))
            and witness.get("witness_control_domain_id") != operator_domain
            and witness.get("observed_head_digest") == computed_head_digest
            and witness.get("observed_sequence") == latest_sequence
        ):
            qualified_independent_witnesses += 1

    if qualified_independent_witnesses < 1:
        problems.append("DURABLE_LEDGER_NO_QUALIFIED_INDEPENDENT_WITNESS")

    problems = sorted(set(problems))
    return {
        "state": "DURABLE_GOVERNANCE_LEDGER_CURRENT" if not problems else "DURABLE_GOVERNANCE_LEDGER_INVALID",
        "qualified": not problems,
        "ledger_kind": ledger_kind,
        "latest_sequence": latest_sequence,
        "latest_record_digest": latest_record_digest,
        "cumulative_root_digest": cumulative_root,
        "head_digest": computed_head_digest,
        "qualified_independent_witness_count": qualified_independent_witnesses,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def derive_effect_class_obligation_set(
    derivations: Any, *, current_observation_head_digest: str
) -> dict[str, Any]:
    """Independently derive the omission-sensitive material effect-class universe.

    Expected membership is the union of current classes observed through the
    required implementation, deployment, and effect-observation source classes.
    No caller-provided registry is used as a source of expected membership.
    """
    problems: list[str] = []
    if not _sha(current_observation_head_digest):
        problems.append("EFFECT_CLASS_OBSERVATION_HEAD_INVALID")

    if not isinstance(derivations, list) or not derivations:
        derivations = []
        problems.append("EFFECT_CLASS_DERIVATIONS_REQUIRED")

    covered_source_classes: set[str] = set()
    expected: set[str] = set()
    seen_ids: set[str] = set()
    control_domains: set[str] = set()
    canonical_inputs: list[dict[str, Any]] = []

    for index, record in enumerate(derivations):
        if not isinstance(record, Mapping):
            problems.append(f"EFFECT_CLASS_DERIVATION_MALFORMED:{index}")
            continue
        did = record.get("derivation_id")
        if not _nonempty(did):
            problems.append(f"EFFECT_CLASS_DERIVATION_ID_REQUIRED:{index}")
            did = f"INDEX-{index}"
        elif did in seen_ids:
            problems.append(f"EFFECT_CLASS_DERIVATION_ID_DUPLICATE:{did}")
        seen_ids.add(did)

        source_class = record.get("source_surface_class")
        if source_class not in REQUIRED_EFFECT_SOURCE_CLASSES:
            problems.append(f"EFFECT_CLASS_SOURCE_CLASS_INVALID:{did}")
        else:
            covered_source_classes.add(source_class)
        if not _sha(record.get("source_surface_digest")):
            problems.append(f"EFFECT_CLASS_SOURCE_DIGEST_INVALID:{did}")
        if not _sha(record.get("derivation_mechanism_qualification_digest")):
            problems.append(f"EFFECT_CLASS_MECHANISM_QUALIFICATION_INVALID:{did}")
        if not _sha(record.get("derivation_authority_independence_digest")):
            problems.append(f"EFFECT_CLASS_AUTHORITY_INDEPENDENCE_INVALID:{did}")
        if record.get("mechanism_qualification_state") != QUALIFIED:
            problems.append(f"EFFECT_CLASS_MECHANISM_NOT_QUALIFIED:{did}")
        if record.get("authority_independence_state") != QUALIFIED:
            problems.append(f"EFFECT_CLASS_AUTHORITY_NOT_INDEPENDENT:{did}")
        if record.get("currentness_result") != CURRENT:
            problems.append(f"EFFECT_CLASS_DERIVATION_NOT_CURRENT:{did}")

        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"EFFECT_CLASS_CONTROL_DOMAIN_REQUIRED:{did}")
        elif domain in control_domains:
            problems.append(f"EFFECT_CLASS_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            control_domains.add(domain)

        if source_class == "EFFECT_OBSERVATION" and record.get(
            "observation_head_digest"
        ) != current_observation_head_digest:
            problems.append(f"EFFECT_CLASS_OBSERVATION_HEAD_STALE:{did}")

        members, member_problems = _unique_strings(record.get("effect_class_ids"))
        problems.extend(
            f"EFFECT_CLASS_MEMBERS:{did}:{problem}" for problem in member_problems
        )
        expected.update(members)
        canonical_inputs.append(
            {
                "derivation_id": did,
                "source_surface_class": source_class,
                "source_surface_digest": record.get("source_surface_digest"),
                "effect_class_ids": sorted(members),
                "control_domain_id": domain,
                "currentness_result": record.get("currentness_result"),
            }
        )

    missing_sources = REQUIRED_EFFECT_SOURCE_CLASSES - covered_source_classes
    for source_class in sorted(missing_sources):
        problems.append(f"EFFECT_CLASS_REQUIRED_SOURCE_MISSING:{source_class}")
    if not expected:
        problems.append("EFFECT_CLASS_EXPECTED_UNIVERSE_EMPTY")

    expected_members = sorted(expected)
    problems = sorted(set(problems))
    return {
        "state": "EFFECT_CLASS_OBLIGATION_SET_QUALIFIED" if not problems else "EFFECT_CLASS_OBLIGATION_SET_INVALID",
        "qualified": not problems,
        "expected_members": expected_members,
        "expected_member_set_digest": digest(expected_members),
        "derivation_inputs_digest": digest(sorted(canonical_inputs, key=lambda x: x["derivation_id"])),
        "covered_source_classes": sorted(covered_source_classes),
        "observation_head_digest": current_observation_head_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _registry_content_digest(registry: Mapping[str, Any]) -> str:
    return digest(_without(registry, "content_digest"))


def validate_effect_class_registry(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate current effect-class registry plus generic completeness proof."""
    problems: list[str] = []
    registry = bundle.get("registry")
    if not isinstance(registry, Mapping):
        registry = {}
        problems.append("EFFECT_CLASS_REGISTRY_REQUIRED")

    registry_id = registry.get("registry_id")
    if not _nonempty(registry_id):
        problems.append("EFFECT_CLASS_REGISTRY_ID_REQUIRED")
    if registry.get("currentness_result") != CURRENT:
        problems.append("EFFECT_CLASS_REGISTRY_NOT_CURRENT")
    if registry.get("qualification_state") != QUALIFIED:
        problems.append("EFFECT_CLASS_REGISTRY_NOT_QUALIFIED")

    computed_registry_digest = _registry_content_digest(registry)
    if registry.get("content_digest") != computed_registry_digest:
        problems.append("EFFECT_CLASS_REGISTRY_CONTENT_DIGEST_MISMATCH")

    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        entries = []
        problems.append("EFFECT_CLASS_REGISTRY_ENTRIES_REQUIRED")

    actual_members: list[str] = []
    entry_by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            problems.append(f"EFFECT_CLASS_ENTRY_MALFORMED:{index}")
            continue
        cid = entry.get("effect_class_id")
        if not _nonempty(cid):
            problems.append(f"EFFECT_CLASS_ENTRY_ID_REQUIRED:{index}")
            continue
        if cid in seen:
            problems.append(f"EFFECT_CLASS_ENTRY_DUPLICATE:{cid}")
            continue
        seen.add(cid)
        actual_members.append(cid)
        for key in ("proof_schema_digest", "verifier_qualification_digest"):
            if not _sha(entry.get(key)):
                problems.append(f"EFFECT_CLASS_ENTRY_DIGEST_INVALID:{cid}:{key}")
        if not _nonempty(entry.get("verifier_mechanism_id")):
            problems.append(f"EFFECT_CLASS_ENTRY_VERIFIER_REQUIRED:{cid}")
        if entry.get("verifier_qualification_state") != QUALIFIED:
            problems.append(f"EFFECT_CLASS_ENTRY_VERIFIER_NOT_QUALIFIED:{cid}")
        if entry.get("currentness_result") != CURRENT:
            problems.append(f"EFFECT_CLASS_ENTRY_NOT_CURRENT:{cid}")
        entry_by_id[cid] = dict(entry)

    obligation = derive_effect_class_obligation_set(
        bundle.get("derivations"),
        current_observation_head_digest=bundle.get("current_observation_head_digest"),
    )
    problems.extend(f"EFFECT_CLASS_OBLIGATION:{x}" for x in obligation["problems"])

    expected_members = obligation["expected_members"]
    actual_members = sorted(actual_members)
    if expected_members != actual_members:
        problems.append("EFFECT_CLASS_REGISTRY_SET_EQUALITY_FAILED")

    completeness = bundle.get("completeness_qualification")
    if not isinstance(completeness, Mapping):
        completeness = {}
        problems.append("EFFECT_CLASS_COMPLETENESS_QUALIFICATION_REQUIRED")
    else:
        generic_problems = validate_registry_completeness_qualification(completeness)
        problems.extend(f"EFFECT_CLASS_COMPLETENESS:{x}" for x in generic_problems)
        if completeness.get("subject_object_id") != registry_id:
            problems.append("EFFECT_CLASS_COMPLETENESS_SUBJECT_ID_MISMATCH")
        if completeness.get("subject_content_digest") != computed_registry_digest:
            problems.append("EFFECT_CLASS_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
        if completeness.get("expected_members") != expected_members:
            problems.append("EFFECT_CLASS_COMPLETENESS_EXPECTED_MEMBERS_MISMATCH")
        if completeness.get("actual_members") != actual_members:
            problems.append("EFFECT_CLASS_COMPLETENESS_ACTUAL_MEMBERS_MISMATCH")
        if completeness.get("expected_member_set_digest") != obligation.get(
            "expected_member_set_digest"
        ):
            problems.append("EFFECT_CLASS_COMPLETENESS_EXPECTED_DIGEST_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("EFFECT_CLASS_COMPLETENESS_NOT_QUALIFIED")

    problems = sorted(set(problems))
    return {
        "state": "EFFECT_CLASS_REGISTRY_QUALIFIED" if not problems else "EFFECT_CLASS_REGISTRY_INVALID",
        "qualified": not problems,
        "registry_id": registry_id,
        "registry_content_digest": computed_registry_digest,
        "expected_members": expected_members,
        "actual_members": actual_members,
        "expected_member_set_digest": obligation["expected_member_set_digest"],
        "entries": entry_by_id,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_effect_path_against_registry(
    record: Mapping[str, Any],
    *,
    current_observation_head_digest: str,
    registry_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Require a valid material effect path to use a current registered effect class."""
    problems = validate_material_effect_path(
        record, current_observation_head=current_observation_head_digest
    )
    if registry_result.get("qualified") is not True:
        problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_REGISTRY_NOT_QUALIFIED")
    effect_class_id = record.get("effect_class_id")
    entries = registry_result.get("entries")
    if not isinstance(entries, Mapping) or effect_class_id not in entries:
        problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_UNKNOWN_OR_UNREGISTERED")
        entry: Mapping[str, Any] = {}
    else:
        entry = entries[effect_class_id]

    proof = record.get("effect_class_proof")
    if not isinstance(proof, Mapping):
        proof = {}
        problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_REQUIRED")
    if entry:
        if proof.get("effect_class_id") != effect_class_id:
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_CLASS_MISMATCH")
        if proof.get("registry_content_digest") != registry_result.get("registry_content_digest"):
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_REGISTRY_MISMATCH")
        if proof.get("proof_schema_digest") != entry.get("proof_schema_digest"):
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_SCHEMA_MISMATCH")
        if proof.get("verifier_mechanism_id") != entry.get("verifier_mechanism_id"):
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_VERIFIER_MISMATCH")
        if proof.get("verifier_qualification_digest") != entry.get("verifier_qualification_digest"):
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_VERIFIER_QUALIFICATION_MISMATCH")
        if entry.get("verifier_qualification_state") != QUALIFIED:
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_VERIFIER_NOT_QUALIFIED")
        if entry.get("currentness_result") != CURRENT:
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_VERIFIER_NOT_CURRENT")
        path_binding_digest = digest(_without(record, "effect_class_proof"))
        if proof.get("path_binding_digest") != path_binding_digest:
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_PATH_BINDING_MISMATCH")
        expected_proof_digest = digest({
            "effect_class_id": effect_class_id,
            "registry_content_digest": registry_result.get("registry_content_digest"),
            "proof_schema_digest": entry.get("proof_schema_digest"),
            "verifier_mechanism_id": entry.get("verifier_mechanism_id"),
            "verifier_qualification_digest": entry.get("verifier_qualification_digest"),
            "path_binding_digest": path_binding_digest,
        })
        if proof.get("proof_material_digest") != expected_proof_digest:
            problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_PROOF_MATERIAL_DIGEST_MISMATCH")
    problems = sorted(set(problems))
    return {
        "state": "MATERIAL_EFFECT_PATH_CLASSIFIED" if not problems else "MATERIAL_EFFECT_PATH_BLOCKED",
        "qualified": not problems,
        "effect_class_id": effect_class_id,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R6_EFFECT_LEDGER_CLOSURE_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R6",
        "authority_effect": AUTHORITY_EFFECT,
    }
