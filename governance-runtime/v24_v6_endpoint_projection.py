"""V24 I11 V6 remediation R2: predicate coverage and governed endpoint projection.

Construction-only.  Every authority-bearing R2 stage resolves exact R1 proof
records through an externally bound proof context and carries recomputable
binding material to the next stage.  No runtime/release/scientific authority is
granted by this module.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_endpoint_proof_compiler import compile_endpoint_precedence
from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    QUALIFIED,
    digest,
    validate_registry_completeness_qualification,
)
from v24_v6_proof_reference_closure import (
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
)

TRUE = "TRUE"
FALSE = "FALSE"
NOT_APPLICABLE = "NOT_APPLICABLE"
EVALUATION_STATUSES = frozenset({TRUE, FALSE, NOT_APPLICABLE})


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


def _set_of_strings(value: Any) -> tuple[set[str], list[str]]:
    if not isinstance(value, list):
        return set(), ["LIST_REQUIRED"]
    result: set[str] = set()
    problems: list[str] = []
    for item in value:
        if not _nonempty(item):
            problems.append("STRING_MEMBER_INVALID")
        elif item in result:
            problems.append(f"DUPLICATE_MEMBER:{item}")
        else:
            result.add(item)
    return result, problems


def _append_proof(prefix: str, result: Mapping[str, Any], problems: list[str]) -> bool:
    if result.get("qualified") is True:
        return True
    child = result.get("problems")
    if isinstance(child, list) and child:
        problems.extend(f"{prefix}:{item}" for item in child)
    else:
        problems.append(f"{prefix}:PROOF_REFERENCE_CLOSURE_FAILED")
    return False


def _close_single_qualification(
    *,
    reference_digest: Any,
    subject_id: Any,
    subject_content_digest: Any,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    proof = close_governance_dependencies(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": reference_digest,
                "subject_id": subject_id,
                "subject_content_digest": subject_content_digest,
            }
        ],
        proof_context,
        trusted_boundary,
    )
    return _append_proof(prefix, proof, problems)


def _close_registry_completeness_dependencies(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    """Resolve every proof reference carried by an R1 completeness record."""
    requirements: list[Mapping[str, Any]] = []
    for ref in record.get("derivation_mechanism_qualification_digests", []):
        requirements.append(
            {"kind": GOVERNED_QUALIFICATION, "reference_digest": ref}
        )
    for ref in record.get("derivation_authority_independence_digests", []):
        requirements.append(
            {"kind": INDEPENDENCE_QUALIFICATION, "reference_digest": ref}
        )
    verifier_ref = record.get("verifier_qualification_digest")
    if verifier_ref is not None:
        requirements.append(
            {"kind": GOVERNED_QUALIFICATION, "reference_digest": verifier_ref}
        )
    currentness = record.get("currentness_bindings")
    if isinstance(currentness, list):
        for binding in currentness:
            if isinstance(binding, Mapping):
                ref = binding.get("verifier_qualification_digest")
                if ref is not None:
                    requirements.append(
                        {"kind": GOVERNED_QUALIFICATION, "reference_digest": ref}
                    )
    if not requirements:
        problems.append(f"{prefix}:COMPLETENESS_PROOF_REFERENCES_REQUIRED")
        return False
    proof = close_governance_dependencies(
        requirements,
        proof_context,
        trusted_boundary,
    )
    return _append_proof(prefix, proof, problems)


def _validate_bound_material(
    *,
    material: Any,
    expected_digest: Any,
    prefix: str,
    problems: list[str],
) -> Mapping[str, Any] | None:
    if not isinstance(material, Mapping):
        problems.append(f"{prefix}_BINDING_MATERIAL_REQUIRED")
        return None
    if not _sha256(expected_digest):
        problems.append(f"{prefix}_DIGEST_INVALID")
        return material
    if digest(material) != expected_digest:
        problems.append(f"{prefix}_BINDING_MATERIAL_DIGEST_MISMATCH")
    return material


def canonical_normative_catalog_digest(bundle: Mapping[str, Any]) -> str:
    predicates = bundle.get("predicate_descriptors")
    active = bundle.get("active_predicate_ids")
    return digest(
        {
            "predicate_descriptors": predicates if isinstance(predicates, list) else [],
            "active_predicate_ids": sorted(active) if isinstance(active, list) else [],
        }
    )


def canonical_endpoint_table_digest(rows: Any) -> str:
    source = rows if isinstance(rows, list) else []
    normalized = [
        {
            "predicate_id": row.get("predicate_id"),
            "phase": row.get("phase"),
            "within_phase_rank": row.get("within_phase_rank"),
            "severity_rank": row.get("severity_rank"),
            "endpoint": row.get("endpoint"),
            "control_id": row.get("control_id"),
        }
        for row in source
        if isinstance(row, Mapping)
    ]
    return digest(
        sorted(
            normalized,
            key=lambda x: (
                x.get("phase") or 10**9,
                x.get("within_phase_rank") or 10**9,
                x.get("predicate_id") or "",
            ),
        )
    )


def compile_qualified_endpoint_table(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile I5 and require exact catalog + resulting table qualifications."""
    compiled = compile_endpoint_precedence(bundle)
    problems = list(compiled["problems"])

    expected_table_digest = bundle.get("expected_compiled_table_digest")
    if (
        expected_table_digest is not None
        and expected_table_digest != compiled["compiled_table_digest"]
    ):
        problems.append("ENDPOINT_TABLE_DIGEST_MISMATCH")

    catalog_id = bundle.get("normative_catalog_id")
    catalog_q = bundle.get("normative_catalog_qualification_digest")
    catalog_digest = canonical_normative_catalog_digest(bundle)
    if not _nonempty(catalog_id):
        problems.append("NORMATIVE_CATALOG_ID_REQUIRED")
    if not _sha256(catalog_q):
        problems.append("NORMATIVE_CATALOG_QUALIFICATION_DIGEST_INVALID")
    _close_single_qualification(
        reference_digest=catalog_q,
        subject_id=catalog_id,
        subject_content_digest=catalog_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="NORMATIVE_CATALOG_PROOF",
        problems=problems,
    )

    table_id = bundle.get("endpoint_table_id")
    table_q = bundle.get("endpoint_table_qualification_digest")
    legacy_q = bundle.get("endpoint_table_qualification")
    if table_q is None and isinstance(legacy_q, Mapping):
        table_q = legacy_q.get("qualification_digest")
    if not _nonempty(table_id):
        problems.append("ENDPOINT_TABLE_ID_REQUIRED")
    if not _sha256(table_q):
        problems.append("ENDPOINT_TABLE_QUALIFICATION_RECORD_DIGEST_INVALID")
    table_ok = _close_single_qualification(
        reference_digest=table_q,
        subject_id=table_id,
        subject_content_digest=compiled["compiled_table_digest"],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ENDPOINT_TABLE_QUALIFICATION_PROOF",
        problems=problems,
    )
    if not table_ok:
        problems.append("ENDPOINT_TABLE_QUALIFICATION_PROOF_INVALID")

    if isinstance(legacy_q, Mapping):
        if legacy_q.get("result") not in (None, QUALIFIED):
            problems.append("ENDPOINT_TABLE_NOT_QUALIFIED")
        subject_digest = legacy_q.get("subject_content_digest")
        if (
            subject_digest is not None
            and subject_digest != compiled["compiled_table_digest"]
        ):
            problems.append("ENDPOINT_TABLE_QUALIFICATION_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": (
            "GOVERNED_ENDPOINT_TABLE_READY"
            if not problems
            else "GOVERNED_ENDPOINT_TABLE_INVALID"
        ),
        "qualified": not problems,
        "problems": problems,
        "compiled_rows": compiled["compiled_rows"],
        "compiled_table_digest": compiled["compiled_table_digest"],
        "normative_catalog_digest": catalog_digest,
        "endpoint_table_id": table_id,
        "endpoint_table_qualification_digest": table_q,
        "authority_effect": AUTHORITY_EFFECT,
    }


def derive_applicable_predicate_universe(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive applicability from the exact qualified table rows."""
    problems: list[str] = []
    table_rows = bundle.get("compiled_endpoint_rows")
    if not isinstance(table_rows, list) or not table_rows:
        table_rows = []
        problems.append("ENDPOINT_TABLE_ROWS_REQUIRED")
    table_digest = bundle.get("endpoint_table_digest")
    if not _sha256(table_digest):
        problems.append("ENDPOINT_TABLE_DIGEST_INVALID")
    if _sha256(table_digest) and canonical_endpoint_table_digest(table_rows) != table_digest:
        problems.append("APPLICABILITY_ENDPOINT_TABLE_DIGEST_DRIFT")

    table_id = bundle.get("endpoint_table_id")
    table_q = bundle.get("endpoint_table_qualification_digest")
    _close_single_qualification(
        reference_digest=table_q,
        subject_id=table_id,
        subject_content_digest=table_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="APPLICABILITY_ENDPOINT_TABLE_PROOF",
        problems=problems,
    )
    state = bundle.get("endpoint_table_qualification_state")
    if state is not None and state != QUALIFIED:
        problems.append("ENDPOINT_TABLE_QUALIFICATION_REQUIRED")

    table_ids: set[str] = set()
    for row in table_rows:
        if not isinstance(row, Mapping) or not _nonempty(row.get("predicate_id")):
            problems.append("ENDPOINT_TABLE_ROW_INVALID")
            continue
        pid = row["predicate_id"]
        if pid in table_ids:
            problems.append(f"ENDPOINT_TABLE_PREDICATE_DUPLICATE:{pid}")
        table_ids.add(pid)

    rules = bundle.get("applicability_rules")
    if not isinstance(rules, list) or not rules:
        rules = []
        problems.append("APPLICABILITY_RULES_REQUIRED")
    by_pid: dict[str, Mapping[str, Any]] = {}
    for rule in rules:
        if not isinstance(rule, Mapping):
            problems.append("APPLICABILITY_RULE_MALFORMED")
            continue
        pid = rule.get("predicate_id")
        if not _nonempty(pid):
            problems.append("APPLICABILITY_RULE_PREDICATE_ID_REQUIRED")
            continue
        if pid in by_pid:
            problems.append(f"APPLICABILITY_RULE_DUPLICATE:{pid}")
            continue
        by_pid[pid] = rule
        if not _nonempty(rule.get("applicability_rule_id")):
            problems.append(f"APPLICABILITY_RULE_ID_REQUIRED:{pid}")
        if type(rule.get("applies")) is not bool:
            problems.append(f"APPLICABILITY_RULE_RESULT_INVALID:{pid}")

    for pid in sorted(table_ids - set(by_pid)):
        problems.append(f"APPLICABILITY_RULE_MISSING:{pid}")
    for pid in sorted(set(by_pid) - table_ids):
        problems.append(f"APPLICABILITY_RULE_UNKNOWN_PREDICATE:{pid}")

    registry_q = bundle.get("applicability_registry_completeness")
    if not isinstance(registry_q, Mapping):
        problems.append("APPLICABILITY_REGISTRY_COMPLETENESS_REQUIRED")
    else:
        q_problems = validate_registry_completeness_qualification(registry_q)
        problems.extend(f"APPLICABILITY_REGISTRY:{x}" for x in q_problems)
        if registry_q.get("result") != QUALIFIED:
            problems.append("APPLICABILITY_REGISTRY_NOT_QUALIFIED")
        if set(registry_q.get("actual_members", [])) != table_ids:
            problems.append("APPLICABILITY_REGISTRY_MEMBER_SET_MISMATCH")
        _close_registry_completeness_dependencies(
            registry_q,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="APPLICABILITY_REGISTRY_PROOF",
            problems=problems,
        )

    compiler_id = bundle.get("applicability_compiler_id")
    compiler_content = bundle.get("applicability_compiler_content_digest")
    compiler_q = bundle.get("applicability_compiler_qualification_digest")
    if not _nonempty(compiler_id):
        problems.append("APPLICABILITY_COMPILER_ID_REQUIRED")
    if not _sha256(compiler_content):
        problems.append("APPLICABILITY_COMPILER_CONTENT_DIGEST_INVALID")
    if not _sha256(compiler_q):
        problems.append("APPLICABILITY_COMPILER_QUALIFICATION_DIGEST_INVALID")
    _close_single_qualification(
        reference_digest=compiler_q,
        subject_id=compiler_id,
        subject_content_digest=compiler_content,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="APPLICABILITY_COMPILER_PROOF",
        problems=problems,
    )
    compiler_state = bundle.get("applicability_compiler_qualification_state")
    if compiler_state is not None and compiler_state != QUALIFIED:
        problems.append("APPLICABILITY_COMPILER_NOT_QUALIFIED")

    applicable = sorted(pid for pid, rule in by_pid.items() if rule.get("applies") is True)
    not_applicable = sorted(
        pid for pid, rule in by_pid.items() if rule.get("applies") is False
    )
    context_digest = bundle.get("decision_context_digest")
    if not _sha256(context_digest):
        problems.append("DECISION_CONTEXT_DIGEST_INVALID")

    universe_material = {
        "decision_context_digest": context_digest,
        "endpoint_table_id": table_id,
        "endpoint_table_digest": table_digest,
        "endpoint_table_qualification_digest": table_q,
        "applicability_compiler_id": compiler_id,
        "applicability_compiler_content_digest": compiler_content,
        "applicability_compiler_qualification_digest": compiler_q,
        "applicable_predicate_ids": applicable,
        "not_applicable_predicate_ids": not_applicable,
    }
    universe_digest = digest(universe_material)

    universe_q = bundle.get("applicable_universe_completeness")
    if not isinstance(universe_q, Mapping):
        problems.append("APPLICABLE_UNIVERSE_COMPLETENESS_REQUIRED")
    else:
        q_problems = validate_registry_completeness_qualification(universe_q)
        problems.extend(f"APPLICABLE_UNIVERSE:{x}" for x in q_problems)
        if universe_q.get("result") != QUALIFIED:
            problems.append("APPLICABLE_UNIVERSE_NOT_QUALIFIED")
        if set(universe_q.get("actual_members", [])) != set(applicable):
            problems.append("APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH")
        _close_registry_completeness_dependencies(
            universe_q,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="APPLICABLE_UNIVERSE_COMPLETENESS_PROOF",
            problems=problems,
        )

    problems = sorted(set(problems))
    return {
        "state": (
            "APPLICABLE_PREDICATE_UNIVERSE_QUALIFIED"
            if not problems
            else "APPLICABLE_PREDICATE_UNIVERSE_INVALID"
        ),
        "qualified": not problems,
        "problems": problems,
        "applicable_predicate_ids": applicable,
        "not_applicable_predicate_ids": not_applicable,
        "universe_digest": universe_digest,
        "universe_binding_material": universe_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_evaluator_condition_universe(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    problems: list[str] = []
    applicable, pp = _set_of_strings(bundle.get("applicable_predicate_ids"))
    problems.extend(f"APPLICABLE:{x}" for x in pp)

    app_digest = bundle.get("applicability_universe_digest")
    app_material = _validate_bound_material(
        material=bundle.get("applicability_binding_material"),
        expected_digest=app_digest,
        prefix="EVALUATOR_APPLICABILITY",
        problems=problems,
    )
    if app_material is not None:
        bound_applicable = set(app_material.get("applicable_predicate_ids", []))
        if bound_applicable != applicable:
            problems.append("EVALUATOR_APPLICABILITY_MEMBER_SET_MISMATCH")
    _close_single_qualification(
        reference_digest=bundle.get("applicability_qualification_digest"),
        subject_id=bundle.get("applicability_universe_id"),
        subject_content_digest=app_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="EVALUATOR_APPLICABILITY_PROOF",
        problems=problems,
    )

    contracts = bundle.get("evaluator_contracts")
    if not isinstance(contracts, list):
        contracts = []
        problems.append("EVALUATOR_CONTRACTS_REQUIRED")
    conditions = bundle.get("condition_descriptors")
    if not isinstance(conditions, list):
        conditions = []
        problems.append("CONDITION_DESCRIPTORS_REQUIRED")

    contract_by_pid: dict[str, Mapping[str, Any]] = {}
    true_condition_ids: set[str] = set()
    for contract in contracts:
        if not isinstance(contract, Mapping):
            problems.append("EVALUATOR_CONTRACT_MALFORMED")
            continue
        pid = contract.get("predicate_id")
        if not _nonempty(pid):
            problems.append("EVALUATOR_CONTRACT_PREDICATE_REQUIRED")
            continue
        if pid in contract_by_pid:
            problems.append(f"EVALUATOR_CONTRACT_DUPLICATE:{pid}")
            continue
        contract_by_pid[pid] = contract
        if not _nonempty(contract.get("evaluator_contract_id")):
            problems.append(f"EVALUATOR_CONTRACT_ID_REQUIRED:{pid}")
        mechanism_id = contract.get("evaluator_mechanism_id")
        mechanism_content = contract.get("evaluator_mechanism_content_digest")
        mechanism_q = contract.get("evaluator_mechanism_qualification_digest")
        if not _nonempty(mechanism_id):
            problems.append(f"EVALUATOR_MECHANISM_ID_REQUIRED:{pid}")
        if not _sha256(mechanism_content):
            problems.append(f"EVALUATOR_MECHANISM_CONTENT_DIGEST_INVALID:{pid}")
        if not _sha256(mechanism_q):
            problems.append(f"EVALUATOR_MECHANISM_QUALIFICATION_REQUIRED:{pid}")
        _close_single_qualification(
            reference_digest=mechanism_q,
            subject_id=mechanism_id,
            subject_content_digest=mechanism_content,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"EVALUATOR_MECHANISM_PROOF:{pid}",
            problems=problems,
        )
        ids, ip = _set_of_strings(contract.get("true_condition_ids"))
        problems.extend(f"TRUE_CONDITION_IDS:{pid}:{x}" for x in ip)
        if not ids:
            problems.append(f"TRUE_CONDITION_SCHEMA_REQUIRED:{pid}")
        true_condition_ids.update(ids)
        negative_classes, np = _set_of_strings(
            contract.get("false_evidence_class_ids")
        )
        problems.extend(f"FALSE_EVIDENCE_CLASSES:{pid}:{x}" for x in np)
        if not negative_classes:
            problems.append(f"FALSE_EVIDENCE_CLASS_REQUIRED:{pid}")

    for pid in sorted(applicable - set(contract_by_pid)):
        problems.append(f"EVALUATOR_CONTRACT_MISSING:{pid}")
    for pid in sorted(set(contract_by_pid) - applicable):
        problems.append(f"EVALUATOR_CONTRACT_OUTSIDE_APPLICABLE_UNIVERSE:{pid}")

    desc_by_id: dict[str, Mapping[str, Any]] = {}
    for desc in conditions:
        if not isinstance(desc, Mapping):
            problems.append("CONDITION_DESCRIPTOR_MALFORMED")
            continue
        cid, pid = desc.get("condition_id"), desc.get("predicate_id")
        if not _nonempty(cid) or not _nonempty(pid):
            problems.append("CONDITION_DESCRIPTOR_IDENTITY_INVALID")
            continue
        if cid in desc_by_id:
            problems.append(f"CONDITION_DESCRIPTOR_DUPLICATE:{cid}")
            continue
        desc_by_id[cid] = desc
        if pid not in applicable:
            problems.append(
                f"CONDITION_DESCRIPTOR_UNKNOWN_APPLICABLE_PREDICATE:{cid}:{pid}"
            )
        if not _sha256(desc.get("condition_schema_digest")):
            problems.append(f"CONDITION_SCHEMA_DIGEST_INVALID:{cid}")

    for cid in sorted(true_condition_ids - set(desc_by_id)):
        problems.append(f"TRUE_CONDITION_DESCRIPTOR_MISSING:{cid}")
    for cid in sorted(set(desc_by_id) - true_condition_ids):
        problems.append(f"CONDITION_DESCRIPTOR_NOT_REQUIRED_BY_EVALUATOR:{cid}")

    for label, members in (
        ("EVALUATOR", set(contract_by_pid)),
        ("CONDITION", set(desc_by_id)),
    ):
        q = bundle.get(f"{label.lower()}_registry_completeness")
        if not isinstance(q, Mapping):
            problems.append(f"{label}_REGISTRY_COMPLETENESS_REQUIRED")
        else:
            qp = validate_registry_completeness_qualification(q)
            problems.extend(f"{label}_REGISTRY:{x}" for x in qp)
            if q.get("result") != QUALIFIED:
                problems.append(f"{label}_REGISTRY_NOT_QUALIFIED")
            if set(q.get("actual_members", [])) != members:
                problems.append(f"{label}_REGISTRY_MEMBER_SET_MISMATCH")
            _close_registry_completeness_dependencies(
                q,
                proof_context=proof_context,
                trusted_boundary=trusted_boundary,
                prefix=f"{label}_REGISTRY_PROOF",
                problems=problems,
            )

    evaluator_contract_digest = digest(contracts)
    condition_registry_digest = digest(conditions)
    universe_material = {
        "applicability_universe_digest": app_digest,
        "applicable_predicate_ids": sorted(applicable),
        "evaluator_contract_digest": evaluator_contract_digest,
        "condition_registry_digest": condition_registry_digest,
    }
    universe_digest = digest(universe_material)
    problems = sorted(set(problems))
    return {
        "state": (
            "EVALUATOR_CONDITION_UNIVERSE_QUALIFIED"
            if not problems
            else "EVALUATOR_CONDITION_UNIVERSE_INVALID"
        ),
        "qualified": not problems,
        "problems": problems,
        "evaluator_contract_digest": evaluator_contract_digest,
        "condition_registry_digest": condition_registry_digest,
        "universe_digest": universe_digest,
        "universe_binding_material": universe_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def qualify_predicate_coverage(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify complete predicate evaluation over exact qualified upstream artifacts."""
    problems: list[str] = []
    applicable, ap = _set_of_strings(bundle.get("applicable_predicate_ids"))
    not_applicable, nap = _set_of_strings(bundle.get("not_applicable_predicate_ids"))
    problems.extend(f"APPLICABLE:{x}" for x in ap)
    problems.extend(f"NOT_APPLICABLE:{x}" for x in nap)
    if applicable.intersection(not_applicable):
        problems.append("PREDICATE_APPLICABILITY_PARTITION_OVERLAP")

    app_digest = bundle.get("applicable_predicate_universe_digest")
    app_material = _validate_bound_material(
        material=bundle.get("applicability_binding_material"),
        expected_digest=app_digest,
        prefix="COVERAGE_APPLICABILITY",
        problems=problems,
    )
    if app_material is not None:
        if set(app_material.get("applicable_predicate_ids", [])) != applicable:
            problems.append("COVERAGE_APPLICABILITY_MEMBER_SET_MISMATCH")
        if set(app_material.get("not_applicable_predicate_ids", [])) != not_applicable:
            problems.append("COVERAGE_NOT_APPLICABLE_MEMBER_SET_MISMATCH")
        if app_material.get("endpoint_table_digest") != bundle.get("endpoint_table_digest"):
            problems.append("COVERAGE_APPLICABILITY_TABLE_BINDING_MISMATCH")
    _close_single_qualification(
        reference_digest=bundle.get("applicability_qualification_digest"),
        subject_id=bundle.get("applicability_universe_id"),
        subject_content_digest=app_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="COVERAGE_APPLICABILITY_RESULT_PROOF",
        problems=problems,
    )

    eval_universe_digest = bundle.get("evaluator_condition_universe_digest")
    eval_material = _validate_bound_material(
        material=bundle.get("evaluator_condition_binding_material"),
        expected_digest=eval_universe_digest,
        prefix="COVERAGE_EVALUATOR_UNIVERSE",
        problems=problems,
    )
    if eval_material is not None:
        if set(eval_material.get("applicable_predicate_ids", [])) != applicable:
            problems.append("COVERAGE_EVALUATOR_MEMBER_SET_MISMATCH")
        if eval_material.get("applicability_universe_digest") != app_digest:
            problems.append("COVERAGE_EVALUATOR_APPLICABILITY_BINDING_MISMATCH")
    _close_single_qualification(
        reference_digest=bundle.get("evaluator_condition_universe_qualification_digest"),
        subject_id=bundle.get("evaluator_condition_universe_id"),
        subject_content_digest=eval_universe_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="COVERAGE_EVALUATOR_UNIVERSE_PROOF",
        problems=problems,
    )

    _close_single_qualification(
        reference_digest=bundle.get("endpoint_table_qualification_digest"),
        subject_id=bundle.get("endpoint_table_id"),
        subject_content_digest=bundle.get("endpoint_table_digest"),
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="COVERAGE_ENDPOINT_TABLE_PROOF",
        problems=problems,
    )

    if app_material is not None:
        _close_single_qualification(
            reference_digest=app_material.get(
                "applicability_compiler_qualification_digest"
            ),
            subject_id=app_material.get("applicability_compiler_id"),
            subject_content_digest=app_material.get(
                "applicability_compiler_content_digest"
            ),
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="COVERAGE_APPLICABILITY_COMPILER_PROOF",
            problems=problems,
        )

    contracts = bundle.get("evaluator_contracts")
    if not isinstance(contracts, list):
        contracts = []
        problems.append("EVALUATOR_CONTRACTS_REQUIRED")
    contract_by_pid = {
        c.get("predicate_id"): c
        for c in contracts
        if isinstance(c, Mapping) and _nonempty(c.get("predicate_id"))
    }
    conditions = bundle.get("condition_descriptors")
    condition_list = conditions if isinstance(conditions, list) else []
    condition_desc = {
        c.get("condition_id"): c
        for c in condition_list
        if isinstance(c, Mapping) and _nonempty(c.get("condition_id"))
    }

    if eval_material is not None:
        if digest(contracts) != eval_material.get("evaluator_contract_digest"):
            problems.append("COVERAGE_EVALUATOR_CONTRACT_DIGEST_MISMATCH")
        if digest(condition_list) != eval_material.get("condition_registry_digest"):
            problems.append("COVERAGE_CONDITION_REGISTRY_DIGEST_MISMATCH")

    for pid, contract in contract_by_pid.items():
        _close_single_qualification(
            reference_digest=contract.get("evaluator_mechanism_qualification_digest"),
            subject_id=contract.get("evaluator_mechanism_id"),
            subject_content_digest=contract.get("evaluator_mechanism_content_digest"),
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"COVERAGE_EVALUATOR_MECHANISM_PROOF:{pid}",
            problems=problems,
        )

    evals = bundle.get("evaluation_records")
    if not isinstance(evals, list):
        evals = []
        problems.append("PREDICATE_EVALUATION_RECORDS_REQUIRED")
    by_pid: dict[str, Mapping[str, Any]] = {}
    true_ids: set[str] = set()
    false_ids: set[str] = set()
    for rec in evals:
        if not isinstance(rec, Mapping):
            problems.append("PREDICATE_EVALUATION_RECORD_MALFORMED")
            continue
        pid = rec.get("predicate_id")
        if not _nonempty(pid):
            problems.append("PREDICATE_EVALUATION_PREDICATE_REQUIRED")
            continue
        if pid in by_pid:
            problems.append(f"PREDICATE_EVALUATION_DUPLICATE:{pid}")
            continue
        by_pid[pid] = rec
        if pid not in applicable:
            problems.append(f"PREDICATE_EVALUATION_OUTSIDE_APPLICABLE_UNIVERSE:{pid}")
        status = rec.get("status")
        if status not in EVALUATION_STATUSES:
            problems.append(f"PREDICATE_EVALUATION_STATUS_INVALID:{pid}")
            continue
        if status == NOT_APPLICABLE:
            problems.append(f"PRODUCER_SELECTED_NOT_APPLICABLE_FORBIDDEN:{pid}")
            continue
        contract = contract_by_pid.get(pid)
        if contract is None:
            problems.append(f"EVALUATOR_CONTRACT_MISSING:{pid}")
            continue
        if rec.get("evaluator_contract_id") != contract.get("evaluator_contract_id"):
            problems.append(f"EVALUATOR_CONTRACT_BINDING_MISMATCH:{pid}")
        if (
            rec.get("evaluator_mechanism_qualification_digest")
            != contract.get("evaluator_mechanism_qualification_digest")
        ):
            problems.append(f"EVALUATOR_MECHANISM_BINDING_MISMATCH:{pid}")
        if not _sha256(rec.get("source_snapshot_digest")):
            problems.append(f"EVALUATION_SOURCE_SNAPSHOT_DIGEST_INVALID:{pid}")
        if not _sha256(rec.get("observation_ledger_head_digest")):
            problems.append(f"EVALUATION_OBSERVATION_HEAD_DIGEST_INVALID:{pid}")
        if not _sha256(rec.get("condition_observation_binding_digest")):
            problems.append(f"EVALUATION_ATOMIC_BINDING_DIGEST_INVALID:{pid}")

        evidence_classes, ep = _set_of_strings(rec.get("evidence_class_ids"))
        problems.extend(f"EVALUATION_EVIDENCE_CLASSES:{pid}:{x}" for x in ep)
        evidence_records, erp = _set_of_strings(rec.get("evidence_record_digests"))
        problems.extend(f"EVALUATION_EVIDENCE_RECORDS:{pid}:{x}" for x in erp)
        if not evidence_records or not all(_sha256(x) for x in evidence_records):
            problems.append(f"EVALUATION_EVIDENCE_REQUIRED:{pid}")

        if status == TRUE:
            true_ids.add(pid)
            record_conditions = rec.get("conditions")
            if not isinstance(record_conditions, list) or not record_conditions:
                problems.append(f"TRUE_CONDITION_REQUIRED:{pid}")
            else:
                allowed = set(contract.get("true_condition_ids", []))
                seen_condition_ids: set[str] = set()
                for condition in record_conditions:
                    if not isinstance(condition, Mapping):
                        problems.append(f"TRUE_CONDITION_MALFORMED:{pid}")
                        continue
                    cid = condition.get("condition_id")
                    if cid not in allowed:
                        problems.append(
                            f"TRUE_CONDITION_UNREGISTERED_FOR_PREDICATE:{pid}:{cid}"
                        )
                        continue
                    desc = condition_desc.get(cid)
                    if desc is None or desc.get("predicate_id") != pid:
                        problems.append(
                            f"TRUE_CONDITION_DESCRIPTOR_BINDING_INVALID:{pid}:{cid}"
                        )
                    if condition.get("predicate_id") != pid:
                        problems.append(
                            f"TRUE_CONDITION_PREDICATE_MISMATCH:{pid}:{cid}"
                        )
                    if not _sha256(condition.get("condition_payload_digest")):
                        problems.append(
                            f"TRUE_CONDITION_PAYLOAD_DIGEST_INVALID:{pid}:{cid}"
                        )
                    seen_condition_ids.add(cid)
                if not seen_condition_ids:
                    problems.append(f"TRUE_CONDITION_REQUIRED:{pid}")
        else:
            false_ids.add(pid)
            required_negative = set(contract.get("false_evidence_class_ids", []))
            if not required_negative.issubset(evidence_classes):
                problems.append(f"FALSE_GOVERNED_NEGATIVE_EVIDENCE_MISSING:{pid}")

    for pid in sorted(applicable - set(by_pid)):
        problems.append(f"PREDICATE_EVALUATION_MISSING:{pid}")
    for pid in sorted(set(by_pid) - applicable):
        problems.append(f"PREDICATE_EVALUATION_EXTRA:{pid}")

    for key in (
        "decision_context_digest",
        "applicable_predicate_universe_digest",
        "endpoint_table_digest",
        "evaluator_contract_registry_digest",
        "condition_registry_digest",
        "evidence_class_registry_digest",
        "source_snapshot_digest",
        "observation_ledger_head_digest",
        "coverage_verifier_content_digest",
        "coverage_verifier_qualification_digest",
        "evaluator_condition_universe_digest",
        "evaluator_condition_universe_qualification_digest",
        "applicability_qualification_digest",
        "endpoint_table_qualification_digest",
    ):
        if not _sha256(bundle.get(key)):
            problems.append(f"COVERAGE_BINDING_DIGEST_INVALID:{key}")

    if app_material is not None:
        if app_material.get("decision_context_digest") != bundle.get(
            "decision_context_digest"
        ):
            problems.append("COVERAGE_DECISION_CONTEXT_BINDING_MISMATCH")
    if bundle.get("evaluator_contract_registry_digest") != digest(contracts):
        problems.append("COVERAGE_EVALUATOR_REGISTRY_DIGEST_MISMATCH")
    if bundle.get("condition_registry_digest") != digest(condition_list):
        problems.append("COVERAGE_CONDITION_REGISTRY_BINDING_MISMATCH")

    _close_single_qualification(
        reference_digest=bundle.get("coverage_verifier_qualification_digest"),
        subject_id=bundle.get("coverage_verifier_id"),
        subject_content_digest=bundle.get("coverage_verifier_content_digest"),
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="COVERAGE_VERIFIER_PROOF",
        problems=problems,
    )

    for key, error in (
        ("applicability_qualification_state", "COVERAGE_APPLICABILITY_NOT_QUALIFIED"),
        (
            "evaluator_condition_universe_state",
            "COVERAGE_EVALUATOR_CONDITION_UNIVERSE_NOT_QUALIFIED",
        ),
        ("coverage_verifier_qualification_state", "COVERAGE_VERIFIER_NOT_QUALIFIED"),
    ):
        state = bundle.get(key)
        if state is not None and state != QUALIFIED:
            problems.append(error)

    coverage_material = {
        "decision_context_digest": bundle.get("decision_context_digest"),
        "applicable_predicate_universe_digest": app_digest,
        "evaluator_condition_universe_digest": eval_universe_digest,
        "endpoint_table_digest": bundle.get("endpoint_table_digest"),
        "evaluator_contract_registry_digest": bundle.get(
            "evaluator_contract_registry_digest"
        ),
        "condition_registry_digest": bundle.get("condition_registry_digest"),
        "evidence_class_registry_digest": bundle.get("evidence_class_registry_digest"),
        "source_snapshot_digest": bundle.get("source_snapshot_digest"),
        "observation_ledger_head_digest": bundle.get("observation_ledger_head_digest"),
        "evaluation_record_digests": sorted(
            digest(r) for r in evals if isinstance(r, Mapping)
        ),
        "true_predicate_ids": sorted(true_ids),
        "false_predicate_ids": sorted(false_ids),
        "not_applicable_predicate_ids": sorted(not_applicable),
    }
    coverage_digest = digest(coverage_material)

    problems = sorted(set(problems))
    return {
        "state": (
            "PREDICATE_EVALUATION_COVERAGE_QUALIFIED"
            if not problems
            else "PREDICATE_EVALUATION_COVERAGE_INVALID"
        ),
        "qualified": not problems,
        "problems": problems,
        "coverage_digest": coverage_digest,
        "true_predicate_ids": sorted(true_ids),
        "false_predicate_ids": sorted(false_ids),
        "not_applicable_predicate_ids": sorted(not_applicable),
        "evaluation_record_digests": coverage_material["evaluation_record_digests"],
        "coverage_binding_material": coverage_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def project_governed_endpoint(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project solely from exact qualified coverage and table binding material."""
    problems: list[str] = []
    coverage_content = bundle.get("coverage_content_digest")
    coverage_material = _validate_bound_material(
        material=bundle.get("coverage_binding_material"),
        expected_digest=coverage_content,
        prefix="ENDPOINT_PROJECTION_COVERAGE",
        problems=problems,
    )
    _close_single_qualification(
        reference_digest=bundle.get("coverage_qualification_digest"),
        subject_id=bundle.get("coverage_id"),
        subject_content_digest=coverage_content,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ENDPOINT_PROJECTION_COVERAGE_PROOF",
        problems=problems,
    )

    endpoint_table_digest = bundle.get("endpoint_table_digest")
    _close_single_qualification(
        reference_digest=bundle.get("endpoint_table_qualification_digest"),
        subject_id=bundle.get("endpoint_table_id"),
        subject_content_digest=endpoint_table_digest,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ENDPOINT_PROJECTION_TABLE_PROOF",
        problems=problems,
    )
    _close_single_qualification(
        reference_digest=bundle.get("projector_mechanism_qualification_digest"),
        subject_id=bundle.get("projector_mechanism_id"),
        subject_content_digest=bundle.get("projector_mechanism_content_digest"),
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ENDPOINT_PROJECTOR_PROOF",
        problems=problems,
    )

    for key, error in (
        ("coverage_qualification_state", "ENDPOINT_PROJECTION_COVERAGE_NOT_QUALIFIED"),
        ("endpoint_table_qualification_state", "ENDPOINT_PROJECTION_TABLE_NOT_QUALIFIED"),
        (
            "projector_mechanism_qualification_state",
            "ENDPOINT_PROJECTOR_NOT_QUALIFIED",
        ),
    ):
        state = bundle.get(key)
        if state is not None and state != QUALIFIED:
            problems.append(error)

    for key in (
        "decision_context_digest",
        "coverage_content_digest",
        "coverage_qualification_digest",
        "endpoint_table_digest",
        "endpoint_table_qualification_digest",
        "applicability_digest",
        "evaluator_registry_digest",
        "condition_registry_digest",
        "evidence_registry_digest",
        "source_snapshot_digest",
        "observation_head_digest",
        "projector_mechanism_content_digest",
        "projector_mechanism_qualification_digest",
    ):
        if not _sha256(bundle.get(key)):
            problems.append(f"ENDPOINT_PROJECTION_BINDING_DIGEST_INVALID:{key}")

    if coverage_material is not None:
        comparisons = (
            ("decision_context_digest", "decision_context_digest"),
            ("endpoint_table_digest", "endpoint_table_digest"),
            ("applicable_predicate_universe_digest", "applicability_digest"),
            ("evaluator_contract_registry_digest", "evaluator_registry_digest"),
            ("condition_registry_digest", "condition_registry_digest"),
            ("evidence_class_registry_digest", "evidence_registry_digest"),
            ("source_snapshot_digest", "source_snapshot_digest"),
            ("observation_ledger_head_digest", "observation_head_digest"),
        )
        for coverage_key, bundle_key in comparisons:
            if coverage_material.get(coverage_key) != bundle.get(bundle_key):
                problems.append(
                    f"ENDPOINT_PROJECTION_COVERAGE_BINDING_MISMATCH:{coverage_key}"
                )

    rows = bundle.get("compiled_endpoint_rows")
    if not isinstance(rows, list) or not rows:
        rows = []
        problems.append("ENDPOINT_PROJECTION_TABLE_ROWS_REQUIRED")
    if (
        _sha256(endpoint_table_digest)
        and canonical_endpoint_table_digest(rows) != endpoint_table_digest
    ):
        problems.append("ENDPOINT_PROJECTION_TABLE_DIGEST_DRIFT")

    row_by_pid = {
        r.get("predicate_id"): r
        for r in rows
        if isinstance(r, Mapping) and _nonempty(r.get("predicate_id"))
    }
    if coverage_material is None:
        true_ids: set[str] = set()
    else:
        true_ids, tip = _set_of_strings(coverage_material.get("true_predicate_ids"))
        problems.extend(f"TRUE_PREDICATES:{x}" for x in tip)
    caller_true = bundle.get("true_predicate_ids")
    if caller_true is not None:
        caller_set, cp = _set_of_strings(caller_true)
        problems.extend(f"CALLER_TRUE_PREDICATES:{x}" for x in cp)
        if caller_set != true_ids:
            problems.append("ENDPOINT_PROJECTION_CALLER_TRUE_SET_MISMATCH")
    for pid in sorted(true_ids - set(row_by_pid)):
        problems.append(f"ENDPOINT_PROJECTION_TRUE_PREDICATE_UNMAPPED:{pid}")

    selected = None
    candidates = [row_by_pid[pid] for pid in true_ids if pid in row_by_pid]
    if candidates:
        selected = min(
            candidates,
            key=lambda r: (
                r["phase"],
                r["within_phase_rank"],
                r["predicate_id"],
            ),
        )
    if problems:
        selected = None

    projection_material = {
        "decision_context_digest": bundle.get("decision_context_digest"),
        "coverage_content_digest": coverage_content,
        "coverage_qualification_digest": bundle.get("coverage_qualification_digest"),
        "endpoint_table_digest": endpoint_table_digest,
        "endpoint_table_qualification_digest": bundle.get(
            "endpoint_table_qualification_digest"
        ),
        "applicability_digest": bundle.get("applicability_digest"),
        "evaluator_registry_digest": bundle.get("evaluator_registry_digest"),
        "condition_registry_digest": bundle.get("condition_registry_digest"),
        "evidence_registry_digest": bundle.get("evidence_registry_digest"),
        "true_predicate_ids": sorted(true_ids),
        "selected_predicate_id": selected.get("predicate_id") if selected else None,
        "selected_endpoint": selected.get("endpoint") if selected else None,
        "selected_phase": selected.get("phase") if selected else None,
        "selected_within_phase_rank": (
            selected.get("within_phase_rank") if selected else None
        ),
        "source_snapshot_digest": bundle.get("source_snapshot_digest"),
        "observation_head_digest": bundle.get("observation_head_digest"),
        "projector_mechanism_qualification_digest": bundle.get(
            "projector_mechanism_qualification_digest"
        ),
    }
    problems = sorted(set(problems))
    return {
        "state": (
            "ENDPOINT_PROJECTION_DECISION_READY"
            if not problems
            else "ENDPOINT_PROJECTION_BLOCKED"
        ),
        "qualified": not problems,
        "problems": problems,
        "selected_predicate_id": projection_material["selected_predicate_id"],
        "selected_endpoint": projection_material["selected_endpoint"],
        "selected_phase": projection_material["selected_phase"],
        "selected_within_phase_rank": projection_material[
            "selected_within_phase_rank"
        ],
        "nonselected_true_predicate_ids": sorted(
            true_ids - ({selected.get("predicate_id")} if selected else set())
        ),
        "projection_digest": digest(projection_material),
        "projection_binding_material": projection_material,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R2_ENDPOINT_PROJECTION_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R2",
        "authority_effect": AUTHORITY_EFFECT,
    }
