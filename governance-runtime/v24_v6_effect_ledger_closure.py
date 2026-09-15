"""V24 I11 V6 remediation R6: effect-class completeness and durable ledger closure.

Construction-only validators for V6 Sections 11.1 and 12. Authority-bearing
head, witness, storage, anchor, derivation, registry and effect-path dependencies
resolve exact R1 proof records through a separately trusted proof context.
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
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
)

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


def _append_proof(prefix: str, result: Mapping[str, Any], problems: list[str]) -> bool:
    if result.get("qualified") is True:
        return True
    child = result.get("problems")
    if isinstance(child, list) and child:
        problems.extend(f"{prefix}:{item}" for item in child)
    else:
        problems.append(f"{prefix}:PROOF_REFERENCE_CLOSURE_FAILED")
    return False


def _close(
    requirements: list[Mapping[str, Any]],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    result = close_governance_dependencies(
        requirements,
        proof_context,
        trusted_boundary,
    )
    return _append_proof(prefix, result, problems)


def _close_completeness_dependencies(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    requirements: list[Mapping[str, Any]] = []
    for ref in record.get("derivation_mechanism_qualification_digests", []):
        requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": ref})
    for ref in record.get("derivation_authority_independence_digests", []):
        requirements.append({"kind": INDEPENDENCE_QUALIFICATION, "reference_digest": ref})
    verifier = record.get("verifier_qualification_digest")
    if verifier is not None:
        requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": verifier})
    currentness = record.get("currentness_bindings")
    if isinstance(currentness, list):
        for binding in currentness:
            if isinstance(binding, Mapping):
                ref = binding.get("verifier_qualification_digest")
                if ref is not None:
                    requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": ref})
    if not requirements:
        problems.append(f"{prefix}:COMPLETENESS_PROOF_REFERENCES_REQUIRED")
        return False
    return _close(
        requirements,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix=prefix,
        problems=problems,
    )


def canonical_storage_content_digest(head: Mapping[str, Any]) -> str:
    return digest(
        {
            "durable_storage_identity": head.get("durable_storage_identity"),
            "durable_storage_class": head.get("durable_storage_class"),
        }
    )


def canonical_anchor_content_digest(head: Mapping[str, Any]) -> str:
    return digest(
        {
            "durable_anchor_identity": head.get("durable_anchor_identity"),
            "durable_anchor_class": head.get("durable_anchor_class"),
            "durable_anchor_digest": head.get("durable_anchor_digest"),
            "anchor_sequence": head.get("anchor_sequence"),
            "cumulative_root_digest": head.get("cumulative_root_digest"),
        }
    )


def _ledger_head_material(head: Mapping[str, Any]) -> dict[str, Any]:
    return _without(
        head,
        "head_digest",
        "witness_currentness_records",
        "head_qualification_digest",
        "head_currentness_binding_digest",
        "storage_qualification_digest",
        "storage_currentness_binding_digest",
        "anchor_qualification_digest",
        "anchor_independence_qualification_digest",
        "anchor_currentness_binding_digest",
    )


def canonical_ledger_head_digest(head: Mapping[str, Any]) -> str:
    return digest(_ledger_head_material(head))


def canonical_witness_content_digest(witness: Mapping[str, Any]) -> str:
    return digest(
        _without(
            witness,
            "witness_content_digest",
            "witness_record_digest",
            "witness_qualification_digest",
            "independence_qualification_digest",
            "currentness_binding_digest",
        )
    )


def validate_durable_governance_ledger(
    bundle: Mapping[str, Any],
    *,
    ledger_kind: str,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a monotonic, durable, exact-proof-closed governance ledger."""
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
        "head_object_id",
        "operator_identity_id",
        "operator_control_domain_id",
        "durable_storage_identity",
        "durable_anchor_identity",
    ):
        if not _nonempty(head.get(key)):
            problems.append(f"DURABLE_LEDGER_HEAD_FIELD_REQUIRED:{key}")
    if head.get("durable_storage_class") not in DURABLE_STORAGE_CLASSES:
        problems.append("DURABLE_LEDGER_STORAGE_NOT_DURABLE")
    if head.get("durable_anchor_class") not in DURABLE_ANCHOR_CLASSES:
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
    if head.get("head_qualification_state") not in (None, QUALIFIED):
        problems.append("DURABLE_LEDGER_HEAD_NOT_QUALIFIED")
    if head.get("currentness_result") not in (None, CURRENT):
        problems.append("DURABLE_LEDGER_HEAD_NOT_CURRENT")

    computed_head_digest = canonical_ledger_head_digest(head)
    if head.get("head_digest") != computed_head_digest:
        problems.append("DURABLE_LEDGER_HEAD_DIGEST_MISMATCH")

    storage_content = canonical_storage_content_digest(head)
    anchor_content = canonical_anchor_content_digest(head)
    for key in (
        "head_qualification_digest",
        "head_currentness_binding_digest",
        "storage_content_digest",
        "storage_qualification_digest",
        "storage_currentness_binding_digest",
        "anchor_content_digest",
        "anchor_qualification_digest",
        "anchor_independence_qualification_digest",
        "anchor_currentness_binding_digest",
    ):
        if not _sha(head.get(key)):
            problems.append(f"DURABLE_LEDGER_HEAD_PROOF_DIGEST_INVALID:{key}")
    if _sha(head.get("storage_content_digest")) and head.get("storage_content_digest") != storage_content:
        problems.append("DURABLE_LEDGER_STORAGE_CONTENT_DIGEST_MISMATCH")
    if _sha(head.get("anchor_content_digest")) and head.get("anchor_content_digest") != anchor_content:
        problems.append("DURABLE_LEDGER_ANCHOR_CONTENT_DIGEST_MISMATCH")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": head.get("head_qualification_digest"),
                "subject_id": head.get("head_object_id"),
                "subject_content_digest": computed_head_digest,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": head.get("head_currentness_binding_digest"),
                "source_id": head.get("head_object_id"),
                "source_digest": computed_head_digest,
            },
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": head.get("storage_qualification_digest"),
                "subject_id": head.get("durable_storage_identity"),
                "subject_content_digest": storage_content,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": head.get("storage_currentness_binding_digest"),
                "source_id": head.get("durable_storage_identity"),
                "source_digest": storage_content,
            },
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": head.get("anchor_qualification_digest"),
                "subject_id": head.get("durable_anchor_identity"),
                "subject_content_digest": anchor_content,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": head.get("anchor_independence_qualification_digest"),
                "subject_identity_id": head.get("durable_anchor_identity"),
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": head.get("anchor_currentness_binding_digest"),
                "source_id": head.get("durable_anchor_identity"),
                "source_digest": anchor_content,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="DURABLE_LEDGER_HEAD_PROOF",
        problems=problems,
    )

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
        wrid = witness.get("witness_record_id")
        if not _nonempty(wid):
            problems.append(f"DURABLE_LEDGER_WITNESS_ID_REQUIRED:{index}")
            wid = f"INDEX-{index}"
        elif wid in seen_witness_ids:
            problems.append(f"DURABLE_LEDGER_WITNESS_DUPLICATE:{wid}")
        seen_witness_ids.add(wid)
        if not _nonempty(wrid):
            problems.append(f"DURABLE_LEDGER_WITNESS_RECORD_ID_REQUIRED:{wid}")
        for key in ("witness_control_domain_id", "evidence_class_id", "currentness_rule_id"):
            if not _nonempty(witness.get(key)):
                problems.append(f"DURABLE_LEDGER_WITNESS_FIELD_REQUIRED:{wid}:{key}")
        if witness.get("observed_head_digest") != computed_head_digest:
            problems.append(f"DURABLE_LEDGER_WITNESS_HEAD_MISMATCH:{wid}")
        if witness.get("observed_sequence") != latest_sequence:
            problems.append(f"DURABLE_LEDGER_WITNESS_SEQUENCE_MISMATCH:{wid}")
        if witness.get("currentness_result") not in (None, CURRENT):
            problems.append(f"DURABLE_LEDGER_WITNESS_NOT_CURRENT:{wid}")
        if witness.get("independence_result") not in (None, QUALIFIED):
            problems.append(f"DURABLE_LEDGER_WITNESS_NOT_INDEPENDENT:{wid}")
        if witness.get("witness_control_domain_id") == operator_domain:
            problems.append(f"DURABLE_LEDGER_WITNESS_OPERATOR_DOMAIN_CONFLICT:{wid}")

        content_digest = canonical_witness_content_digest(witness)
        if witness.get("witness_content_digest") != content_digest:
            problems.append(f"DURABLE_LEDGER_WITNESS_CONTENT_DIGEST_MISMATCH:{wid}")
        if witness.get("witness_record_digest") != content_digest:
            problems.append(f"DURABLE_LEDGER_WITNESS_RECORD_DIGEST_MISMATCH:{wid}")
        for key in (
            "witness_qualification_digest",
            "independence_qualification_digest",
            "currentness_binding_digest",
        ):
            if not _sha(witness.get(key)):
                problems.append(f"DURABLE_LEDGER_WITNESS_PROOF_DIGEST_INVALID:{wid}:{key}")
        witness_ok = _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": witness.get("witness_qualification_digest"),
                    "subject_id": wrid,
                    "subject_content_digest": content_digest,
                },
                {
                    "kind": INDEPENDENCE_QUALIFICATION,
                    "reference_digest": witness.get("independence_qualification_digest"),
                    "subject_identity_id": wid,
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": witness.get("currentness_binding_digest"),
                    "source_id": wrid,
                    "source_digest": content_digest,
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"DURABLE_LEDGER_WITNESS_PROOF:{wid}",
            problems=problems,
        )
        structural_ok = (
            witness.get("currentness_result") in (None, CURRENT)
            and witness.get("independence_result") in (None, QUALIFIED)
            and _nonempty(witness.get("witness_control_domain_id"))
            and witness.get("witness_control_domain_id") != operator_domain
            and witness.get("observed_head_digest") == computed_head_digest
            and witness.get("observed_sequence") == latest_sequence
            and witness.get("witness_content_digest") == content_digest
        )
        if witness_ok and structural_ok:
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


def canonical_derivation_content_digest(record: Mapping[str, Any]) -> str:
    members = record.get("effect_class_ids")
    return digest(
        {
            "derivation_id": record.get("derivation_id"),
            "source_surface_class": record.get("source_surface_class"),
            "source_surface_digest": record.get("source_surface_digest"),
            "effect_class_ids": sorted(members) if isinstance(members, list) else [],
            "control_domain_id": record.get("control_domain_id"),
            "observation_head_digest": record.get("observation_head_digest"),
        }
    )


def derive_effect_class_obligation_set(
    derivations: Any,
    *,
    current_observation_head_digest: str,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the omission-sensitive effect universe from exact proof-closed sources."""
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
        for key in (
            "derivation_content_digest",
            "derivation_mechanism_content_digest",
            "derivation_mechanism_qualification_digest",
            "derivation_authority_independence_digest",
            "currentness_binding_digest",
        ):
            if not _sha(record.get(key)):
                problems.append(f"EFFECT_CLASS_PROOF_DIGEST_INVALID:{did}:{key}")
        for key in ("derivation_mechanism_id", "derivation_authority_id"):
            if not _nonempty(record.get(key)):
                problems.append(f"EFFECT_CLASS_PROOF_FIELD_REQUIRED:{did}:{key}")
        expected_content = canonical_derivation_content_digest(record)
        if _sha(record.get("derivation_content_digest")) and record.get("derivation_content_digest") != expected_content:
            problems.append(f"EFFECT_CLASS_DERIVATION_CONTENT_DIGEST_MISMATCH:{did}")
        if record.get("mechanism_qualification_state") not in (None, QUALIFIED):
            problems.append(f"EFFECT_CLASS_MECHANISM_NOT_QUALIFIED:{did}")
        if record.get("authority_independence_state") not in (None, QUALIFIED):
            problems.append(f"EFFECT_CLASS_AUTHORITY_NOT_INDEPENDENT:{did}")
        if record.get("currentness_result") not in (None, CURRENT):
            problems.append(f"EFFECT_CLASS_DERIVATION_NOT_CURRENT:{did}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": record.get("derivation_mechanism_qualification_digest"),
                    "subject_id": record.get("derivation_mechanism_id"),
                    "subject_content_digest": record.get("derivation_mechanism_content_digest"),
                },
                {
                    "kind": INDEPENDENCE_QUALIFICATION,
                    "reference_digest": record.get("derivation_authority_independence_digest"),
                    "subject_identity_id": record.get("derivation_authority_id"),
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": record.get("currentness_binding_digest"),
                    "source_id": did,
                    "source_digest": record.get("derivation_content_digest"),
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"EFFECT_CLASS_DERIVATION_PROOF:{did}",
            problems=problems,
        )
        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"EFFECT_CLASS_CONTROL_DOMAIN_REQUIRED:{did}")
        elif domain in control_domains:
            problems.append(f"EFFECT_CLASS_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            control_domains.add(domain)
        if source_class == "EFFECT_OBSERVATION" and record.get("observation_head_digest") != current_observation_head_digest:
            problems.append(f"EFFECT_CLASS_OBSERVATION_HEAD_STALE:{did}")
        members, member_problems = _unique_strings(record.get("effect_class_ids"))
        problems.extend(f"EFFECT_CLASS_MEMBERS:{did}:{problem}" for problem in member_problems)
        expected.update(members)
        canonical_inputs.append(
            {
                "derivation_id": did,
                "derivation_content_digest": record.get("derivation_content_digest"),
                "source_surface_class": source_class,
                "source_surface_digest": record.get("source_surface_digest"),
                "effect_class_ids": sorted(members),
                "control_domain_id": domain,
            }
        )

    for source_class in sorted(REQUIRED_EFFECT_SOURCE_CLASSES - covered_source_classes):
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


def canonical_effect_registry_content_digest(registry: Mapping[str, Any]) -> str:
    entries = registry.get("entries")
    return digest(
        {
            "registry_id": registry.get("registry_id"),
            "entries": entries if isinstance(entries, list) else [],
        }
    )


def validate_effect_class_registry(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate exact current effect registry and proof-closed completeness chain."""
    problems: list[str] = []
    registry = bundle.get("registry")
    if not isinstance(registry, Mapping):
        registry = {}
        problems.append("EFFECT_CLASS_REGISTRY_REQUIRED")
    registry_id = registry.get("registry_id")
    if not _nonempty(registry_id):
        problems.append("EFFECT_CLASS_REGISTRY_ID_REQUIRED")
    if registry.get("currentness_result") not in (None, CURRENT):
        problems.append("EFFECT_CLASS_REGISTRY_NOT_CURRENT")
    if registry.get("qualification_state") not in (None, QUALIFIED):
        problems.append("EFFECT_CLASS_REGISTRY_NOT_QUALIFIED")

    computed_registry_digest = canonical_effect_registry_content_digest(registry)
    if registry.get("content_digest") != computed_registry_digest:
        problems.append("EFFECT_CLASS_REGISTRY_CONTENT_DIGEST_MISMATCH")
    for key in ("qualification_digest", "currentness_binding_digest"):
        if not _sha(registry.get(key)):
            problems.append(f"EFFECT_CLASS_REGISTRY_PROOF_DIGEST_INVALID:{key}")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": registry.get("qualification_digest"),
                "subject_id": registry_id,
                "subject_content_digest": computed_registry_digest,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": registry.get("currentness_binding_digest"),
                "source_id": registry_id,
                "source_digest": computed_registry_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="EFFECT_CLASS_REGISTRY_PROOF",
        problems=problems,
    )

    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        entries = []
        problems.append("EFFECT_CLASS_REGISTRY_ENTRIES_REQUIRED")
    actual_members: list[str] = []
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
        for key in (
            "proof_schema_digest",
            "verifier_mechanism_content_digest",
            "verifier_qualification_digest",
            "verifier_currentness_binding_digest",
        ):
            if not _sha(entry.get(key)):
                problems.append(f"EFFECT_CLASS_ENTRY_DIGEST_INVALID:{cid}:{key}")
        if not _nonempty(entry.get("verifier_mechanism_id")):
            problems.append(f"EFFECT_CLASS_ENTRY_VERIFIER_REQUIRED:{cid}")
        if entry.get("verifier_qualification_state") not in (None, QUALIFIED):
            problems.append(f"EFFECT_CLASS_ENTRY_VERIFIER_NOT_QUALIFIED:{cid}")
        if entry.get("currentness_result") not in (None, CURRENT):
            problems.append(f"EFFECT_CLASS_ENTRY_NOT_CURRENT:{cid}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": entry.get("verifier_qualification_digest"),
                    "subject_id": entry.get("verifier_mechanism_id"),
                    "subject_content_digest": entry.get("verifier_mechanism_content_digest"),
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": entry.get("verifier_currentness_binding_digest"),
                    "source_id": entry.get("verifier_mechanism_id"),
                    "source_digest": entry.get("verifier_mechanism_content_digest"),
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"EFFECT_CLASS_ENTRY_PROOF:{cid}",
            problems=problems,
        )

    obligation = derive_effect_class_obligation_set(
        bundle.get("derivations"),
        current_observation_head_digest=bundle.get("current_observation_head_digest"),
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
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
        if completeness.get("expected_member_set_digest") != obligation.get("expected_member_set_digest"):
            problems.append("EFFECT_CLASS_COMPLETENESS_EXPECTED_DIGEST_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("EFFECT_CLASS_COMPLETENESS_NOT_QUALIFIED")
        _close_completeness_dependencies(
            completeness,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="EFFECT_CLASS_COMPLETENESS_PROOF",
            problems=problems,
        )

    completeness_digest = completeness.get("qualification_digest") if isinstance(completeness, Mapping) else None
    binding_material = {
        "registry": {
            "registry_id": registry_id,
            "entries": entries,
        },
        "registry_content_digest": computed_registry_digest,
        "registry_qualification_digest": registry.get("qualification_digest"),
        "registry_currentness_binding_digest": registry.get("currentness_binding_digest"),
        "expected_members": expected_members,
        "actual_members": actual_members,
        "expected_member_set_digest": obligation["expected_member_set_digest"],
        "derivation_inputs_digest": obligation["derivation_inputs_digest"],
        "completeness_qualification_digest": completeness_digest,
        "observation_head_digest": bundle.get("current_observation_head_digest"),
    }
    result_digest = digest(binding_material)
    problems = sorted(set(problems))
    return {
        "state": "EFFECT_CLASS_REGISTRY_QUALIFIED" if not problems else "EFFECT_CLASS_REGISTRY_INVALID",
        "qualified": not problems,
        "registry_id": registry_id,
        "registry_content_digest": computed_registry_digest,
        "registry_qualification_digest": registry.get("qualification_digest"),
        "registry_currentness_binding_digest": registry.get("currentness_binding_digest"),
        "expected_members": expected_members,
        "actual_members": actual_members,
        "expected_member_set_digest": obligation["expected_member_set_digest"],
        "registry_result_digest": result_digest,
        "registry_binding_material": binding_material,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def canonical_effect_path_content_digest(record: Mapping[str, Any]) -> str:
    """Digest the exact effect-path semantics whose currentness is asserted.

    Proof-reference fields and caller result labels are excluded; the underlying
    authority/evidence digests and the effect class itself are included.  Any
    material mutation therefore requires a new currentness binding.
    """
    writers = record.get("sink_admitted_writer_ids")
    edges = record.get("dependency_edge_digests")
    control = record.get("control_plane_evidence_digests")
    return digest(
        {
            "path_id": record.get("path_id"),
            "source_or_writer_id": record.get("source_or_writer_id"),
            "sink_id": record.get("sink_id"),
            "effect_class_id": record.get("effect_class_id"),
            "writer_admission_id": record.get("writer_admission_id"),
            "writer_admission_digest": record.get("writer_admission_digest"),
            "capability_id": record.get("capability_id"),
            "capability_digest": record.get("capability_digest"),
            "guard_mechanism_id": record.get("guard_mechanism_id"),
            "guard_mechanism_digest": record.get("guard_mechanism_digest"),
            "sink_admitted_writer_set_digest": record.get("sink_admitted_writer_set_digest"),
            "material_surface_membership_digest": record.get("material_surface_membership_digest"),
            "observation_head_digest": record.get("observation_head_digest"),
            "sink_admitted_writer_ids": sorted(writers) if isinstance(writers, list) else [],
            "dependency_edge_digests": sorted(edges) if isinstance(edges, list) else [],
            "control_plane_evidence_digests": sorted(control) if isinstance(control, list) else [],
        }
    )


def validate_effect_path_against_registry(
    record: Mapping[str, Any],
    *,
    current_observation_head_digest: str,
    registry_result: Mapping[str, Any],
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require exact-current path proof plus an independently qualified registry result."""
    problems = validate_material_effect_path(
        record,
        current_observation_head=current_observation_head_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    )
    computed_path_digest = canonical_effect_path_content_digest(record)
    if record.get("path_content_digest") != computed_path_digest:
        problems.append("MATERIAL_EFFECT_PATH_CONTENT_DIGEST_MISMATCH")
    # Close currentness a second time against the recomputed path content.  This
    # makes R6 fail closed even if an upstream validator were to trust an opaque
    # caller-supplied path_content_digest.
    _close(
        [
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": record.get("currentness_binding_digest"),
                "source_id": record.get("path_id"),
                "source_digest": computed_path_digest,
            }
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="MATERIAL_EFFECT_PATH_CURRENTNESS_PROOF",
        problems=problems,
    )

    material = registry_result.get("registry_binding_material")
    result_digest = registry_result.get("registry_result_digest")
    if not isinstance(material, Mapping):
        problems.append("MATERIAL_EFFECT_PATH_REGISTRY_BINDING_MATERIAL_REQUIRED")
        material = {}
    elif digest(material) != result_digest:
        problems.append("MATERIAL_EFFECT_PATH_REGISTRY_RESULT_DIGEST_MISMATCH")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": registry_result.get("registry_result_qualification_digest"),
                "subject_id": registry_result.get("registry_result_id"),
                "subject_content_digest": result_digest,
            }
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="MATERIAL_EFFECT_PATH_REGISTRY_RESULT_PROOF",
        problems=problems,
    )

    bound_registry = material.get("registry")
    bound_entries: list[Any] = []
    if not isinstance(bound_registry, Mapping):
        problems.append("MATERIAL_EFFECT_PATH_BOUND_REGISTRY_REQUIRED")
    else:
        bound_entries = bound_registry.get("entries") if isinstance(bound_registry.get("entries"), list) else []
        if canonical_effect_registry_content_digest(bound_registry) != material.get("registry_content_digest"):
            problems.append("MATERIAL_EFFECT_PATH_BOUND_REGISTRY_CONTENT_DIGEST_MISMATCH")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": material.get("registry_qualification_digest"),
                    "subject_id": bound_registry.get("registry_id"),
                    "subject_content_digest": material.get("registry_content_digest"),
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": material.get("registry_currentness_binding_digest"),
                    "source_id": bound_registry.get("registry_id"),
                    "source_digest": material.get("registry_content_digest"),
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="MATERIAL_EFFECT_PATH_REGISTRY_OBJECT_PROOF",
            problems=problems,
        )
    actual_members = sorted(
        entry.get("effect_class_id")
        for entry in bound_entries
        if isinstance(entry, Mapping) and _nonempty(entry.get("effect_class_id"))
    )
    if actual_members != material.get("actual_members"):
        problems.append("MATERIAL_EFFECT_PATH_REGISTRY_MEMBER_BINDING_MISMATCH")
    if registry_result.get("actual_members") != actual_members:
        problems.append("MATERIAL_EFFECT_PATH_CALLER_REGISTRY_MEMBERS_MISMATCH")
    if registry_result.get("qualified") is not True:
        problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_REGISTRY_NOT_QUALIFIED")
    effect_class_id = record.get("effect_class_id")
    if effect_class_id not in set(actual_members):
        problems.append("MATERIAL_EFFECT_PATH_EFFECT_CLASS_UNKNOWN_OR_UNREGISTERED")
    problems = sorted(set(problems))
    return {
        "state": "MATERIAL_EFFECT_PATH_CLASSIFIED" if not problems else "MATERIAL_EFFECT_PATH_BLOCKED",
        "qualified": not problems,
        "effect_class_id": effect_class_id,
        "path_content_digest": computed_path_digest,
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
