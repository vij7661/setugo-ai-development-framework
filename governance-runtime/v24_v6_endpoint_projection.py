"""V24 I11 V6 remediation R2: predicate coverage and governed endpoint projection."""
from __future__ import annotations

from typing import Any, Mapping

from v24_endpoint_proof_compiler import compile_endpoint_precedence
from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    digest,
    validate_registry_completeness_qualification,
)

TRUE = "TRUE"
FALSE = "FALSE"
NOT_APPLICABLE = "NOT_APPLICABLE"
EVALUATION_STATUSES = frozenset({TRUE, FALSE, NOT_APPLICABLE})


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


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


def compile_qualified_endpoint_table(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Compile I5 precedence and bind qualification to that exact table digest."""
    compiled = compile_endpoint_precedence(bundle)
    problems = list(compiled["problems"])
    expected_table_digest = bundle.get("expected_compiled_table_digest")
    if expected_table_digest is not None and expected_table_digest != compiled["compiled_table_digest"]:
        problems.append("ENDPOINT_TABLE_DIGEST_MISMATCH")
    qualification = bundle.get("endpoint_table_qualification")
    if not isinstance(qualification, Mapping):
        problems.append("ENDPOINT_TABLE_QUALIFICATION_REQUIRED")
    else:
        if qualification.get("result") != QUALIFIED:
            problems.append("ENDPOINT_TABLE_NOT_QUALIFIED")
        if qualification.get("subject_content_digest") != compiled["compiled_table_digest"]:
            problems.append("ENDPOINT_TABLE_QUALIFICATION_DIGEST_MISMATCH")
        if not _sha256(qualification.get("qualification_digest")):
            problems.append("ENDPOINT_TABLE_QUALIFICATION_RECORD_DIGEST_INVALID")
        if qualification.get("currentness_result") != CURRENT:
            problems.append("ENDPOINT_TABLE_NOT_CURRENT")
    problems = sorted(set(problems))
    return {
        "state": "GOVERNED_ENDPOINT_TABLE_READY" if not problems else "GOVERNED_ENDPOINT_TABLE_INVALID",
        "qualified": not problems,
        "problems": problems,
        "compiled_rows": compiled["compiled_rows"],
        "compiled_table_digest": compiled["compiled_table_digest"],
        "endpoint_table_qualification_digest": (
            qualification.get("qualification_digest") if isinstance(qualification, Mapping) else None
        ),
        "authority_effect": AUTHORITY_EFFECT,
    }


def derive_applicable_predicate_universe(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Compile applicability over the complete qualified endpoint predicate universe."""
    problems: list[str] = []
    table_rows = bundle.get("compiled_endpoint_rows")
    if not isinstance(table_rows, list) or not table_rows:
        table_rows = []
        problems.append("ENDPOINT_TABLE_ROWS_REQUIRED")
    table_digest = bundle.get("endpoint_table_digest")
    if not _sha256(table_digest):
        problems.append("ENDPOINT_TABLE_DIGEST_INVALID")
    if bundle.get("endpoint_table_qualification_state") != QUALIFIED:
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

    if bundle.get("applicability_compiler_qualification_state") != QUALIFIED:
        problems.append("APPLICABILITY_COMPILER_NOT_QUALIFIED")
    compiler_digest = bundle.get("applicability_compiler_qualification_digest")
    if not _sha256(compiler_digest):
        problems.append("APPLICABILITY_COMPILER_QUALIFICATION_DIGEST_INVALID")

    applicable = sorted(pid for pid, rule in by_pid.items() if rule.get("applies") is True)
    not_applicable = sorted(pid for pid, rule in by_pid.items() if rule.get("applies") is False)
    context_digest = bundle.get("decision_context_digest")
    if not _sha256(context_digest):
        problems.append("DECISION_CONTEXT_DIGEST_INVALID")

    universe_material = {
        "decision_context_digest": context_digest,
        "endpoint_table_digest": table_digest,
        "applicability_compiler_qualification_digest": compiler_digest,
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

    problems = sorted(set(problems))
    return {
        "state": "APPLICABLE_PREDICATE_UNIVERSE_QUALIFIED" if not problems else "APPLICABLE_PREDICATE_UNIVERSE_INVALID",
        "qualified": not problems,
        "problems": problems,
        "applicable_predicate_ids": applicable,
        "not_applicable_predicate_ids": not_applicable,
        "universe_digest": universe_digest,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_evaluator_condition_universe(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    applicable, pp = _set_of_strings(bundle.get("applicable_predicate_ids"))
    problems.extend(f"APPLICABLE:{x}" for x in pp)
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
        if not _sha256(contract.get("evaluator_mechanism_qualification_digest")):
            problems.append(f"EVALUATOR_MECHANISM_QUALIFICATION_REQUIRED:{pid}")
        ids, ip = _set_of_strings(contract.get("true_condition_ids"))
        problems.extend(f"TRUE_CONDITION_IDS:{pid}:{x}" for x in ip)
        if not ids:
            problems.append(f"TRUE_CONDITION_SCHEMA_REQUIRED:{pid}")
        true_condition_ids.update(ids)
        negative_classes, np = _set_of_strings(contract.get("false_evidence_class_ids"))
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
            problems.append(f"CONDITION_DESCRIPTOR_UNKNOWN_APPLICABLE_PREDICATE:{cid}:{pid}")
        if not _sha256(desc.get("condition_schema_digest")):
            problems.append(f"CONDITION_SCHEMA_DIGEST_INVALID:{cid}")

    for cid in sorted(true_condition_ids - set(desc_by_id)):
        problems.append(f"TRUE_CONDITION_DESCRIPTOR_MISSING:{cid}")
    for cid in sorted(set(desc_by_id) - true_condition_ids):
        problems.append(f"CONDITION_DESCRIPTOR_NOT_REQUIRED_BY_EVALUATOR:{cid}")

    for label, members in (("EVALUATOR", set(contract_by_pid)), ("CONDITION", set(desc_by_id))):
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

    problems = sorted(set(problems))
    return {
        "state": "EVALUATOR_CONDITION_UNIVERSE_QUALIFIED" if not problems else "EVALUATOR_CONDITION_UNIVERSE_INVALID",
        "qualified": not problems,
        "problems": problems,
        "evaluator_contract_digest": digest(contracts),
        "condition_registry_digest": digest(conditions),
        "authority_effect": AUTHORITY_EFFECT,
    }


def qualify_predicate_coverage(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Verify complete one-record-per-applicable-predicate coverage."""
    problems: list[str] = []
    applicable, ap = _set_of_strings(bundle.get("applicable_predicate_ids"))
    not_applicable, nap = _set_of_strings(bundle.get("not_applicable_predicate_ids"))
    problems.extend(f"APPLICABLE:{x}" for x in ap)
    problems.extend(f"NOT_APPLICABLE:{x}" for x in nap)
    if applicable.intersection(not_applicable):
        problems.append("PREDICATE_APPLICABILITY_PARTITION_OVERLAP")

    contracts = bundle.get("evaluator_contracts")
    if not isinstance(contracts, list):
        contracts = []
        problems.append("EVALUATOR_CONTRACTS_REQUIRED")
    contract_by_pid = {
        c.get("predicate_id"): c for c in contracts
        if isinstance(c, Mapping) and _nonempty(c.get("predicate_id"))
    }
    condition_desc = {
        c.get("condition_id"): c for c in bundle.get("condition_descriptors", [])
        if isinstance(c, Mapping) and _nonempty(c.get("condition_id"))
    }

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
        if rec.get("evaluator_mechanism_qualification_digest") != contract.get("evaluator_mechanism_qualification_digest"):
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
            conditions = rec.get("conditions")
            if not isinstance(conditions, list) or not conditions:
                problems.append(f"TRUE_CONDITION_REQUIRED:{pid}")
            else:
                allowed = set(contract.get("true_condition_ids", []))
                seen_condition_ids: set[str] = set()
                for condition in conditions:
                    if not isinstance(condition, Mapping):
                        problems.append(f"TRUE_CONDITION_MALFORMED:{pid}")
                        continue
                    cid = condition.get("condition_id")
                    if cid not in allowed:
                        problems.append(f"TRUE_CONDITION_UNREGISTERED_FOR_PREDICATE:{pid}:{cid}")
                        continue
                    desc = condition_desc.get(cid)
                    if desc is None or desc.get("predicate_id") != pid:
                        problems.append(f"TRUE_CONDITION_DESCRIPTOR_BINDING_INVALID:{pid}:{cid}")
                    if condition.get("predicate_id") != pid:
                        problems.append(f"TRUE_CONDITION_PREDICATE_MISMATCH:{pid}:{cid}")
                    if not _sha256(condition.get("condition_payload_digest")):
                        problems.append(f"TRUE_CONDITION_PAYLOAD_DIGEST_INVALID:{pid}:{cid}")
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

    coverage_material = {
        "decision_context_digest": bundle.get("decision_context_digest"),
        "applicable_predicate_universe_digest": bundle.get("applicable_predicate_universe_digest"),
        "endpoint_table_digest": bundle.get("endpoint_table_digest"),
        "evaluation_record_digests": sorted(digest(r) for r in evals if isinstance(r, Mapping)),
        "true_predicate_ids": sorted(true_ids),
        "false_predicate_ids": sorted(false_ids),
        "not_applicable_predicate_ids": sorted(not_applicable),
    }
    coverage_digest = digest(coverage_material)

    for key in (
        "decision_context_digest", "applicable_predicate_universe_digest", "endpoint_table_digest",
        "evaluator_contract_registry_digest", "condition_registry_digest", "evidence_class_registry_digest",
        "source_snapshot_digest", "observation_ledger_head_digest", "coverage_verifier_qualification_digest",
    ):
        if not _sha256(bundle.get(key)):
            problems.append(f"COVERAGE_BINDING_DIGEST_INVALID:{key}")

    if bundle.get("applicability_qualification_state") != QUALIFIED:
        problems.append("COVERAGE_APPLICABILITY_NOT_QUALIFIED")
    if bundle.get("evaluator_condition_universe_state") != QUALIFIED:
        problems.append("COVERAGE_EVALUATOR_CONDITION_UNIVERSE_NOT_QUALIFIED")
    if bundle.get("coverage_verifier_qualification_state") != QUALIFIED:
        problems.append("COVERAGE_VERIFIER_NOT_QUALIFIED")

    problems = sorted(set(problems))
    return {
        "state": "PREDICATE_EVALUATION_COVERAGE_QUALIFIED" if not problems else "PREDICATE_EVALUATION_COVERAGE_INVALID",
        "qualified": not problems,
        "problems": problems,
        "coverage_digest": coverage_digest,
        "true_predicate_ids": sorted(true_ids),
        "false_predicate_ids": sorted(false_ids),
        "not_applicable_predicate_ids": sorted(not_applicable),
        "evaluation_record_digests": coverage_material["evaluation_record_digests"],
        "authority_effect": AUTHORITY_EFFECT,
    }


def project_governed_endpoint(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Select exact endpoint only from current qualified coverage and table."""
    problems: list[str] = []
    if bundle.get("coverage_qualification_state") != QUALIFIED:
        problems.append("ENDPOINT_PROJECTION_COVERAGE_NOT_QUALIFIED")
    if bundle.get("endpoint_table_qualification_state") != QUALIFIED:
        problems.append("ENDPOINT_PROJECTION_TABLE_NOT_QUALIFIED")
    if bundle.get("projector_mechanism_qualification_state") != QUALIFIED:
        problems.append("ENDPOINT_PROJECTOR_NOT_QUALIFIED")
    for key in (
        "decision_context_digest", "coverage_qualification_digest", "endpoint_table_digest",
        "endpoint_table_qualification_digest", "applicability_digest", "evaluator_registry_digest",
        "condition_registry_digest", "evidence_registry_digest", "source_snapshot_digest",
        "observation_head_digest", "projector_mechanism_qualification_digest",
    ):
        if not _sha256(bundle.get(key)):
            problems.append(f"ENDPOINT_PROJECTION_BINDING_DIGEST_INVALID:{key}")

    rows = bundle.get("compiled_endpoint_rows")
    if not isinstance(rows, list) or not rows:
        rows = []
        problems.append("ENDPOINT_PROJECTION_TABLE_ROWS_REQUIRED")
    normalized_rows = [
        {
            "predicate_id": r.get("predicate_id"), "phase": r.get("phase"),
            "within_phase_rank": r.get("within_phase_rank"), "severity_rank": r.get("severity_rank"),
            "endpoint": r.get("endpoint"), "control_id": r.get("control_id"),
        }
        for r in rows if isinstance(r, Mapping)
    ]
    computed_table_digest = digest(sorted(normalized_rows, key=lambda x: (
        x.get("phase") or 10**9, x.get("within_phase_rank") or 10**9, x.get("predicate_id") or ""
    )))
    if _sha256(bundle.get("endpoint_table_digest")) and computed_table_digest != bundle.get("endpoint_table_digest"):
        problems.append("ENDPOINT_PROJECTION_TABLE_DIGEST_DRIFT")

    row_by_pid = {r.get("predicate_id"): r for r in rows if isinstance(r, Mapping) and _nonempty(r.get("predicate_id"))}
    true_ids, tip = _set_of_strings(bundle.get("true_predicate_ids"))
    problems.extend(f"TRUE_PREDICATES:{x}" for x in tip)
    for pid in sorted(true_ids - set(row_by_pid)):
        problems.append(f"ENDPOINT_PROJECTION_TRUE_PREDICATE_UNMAPPED:{pid}")

    selected = None
    candidates = [row_by_pid[pid] for pid in true_ids if pid in row_by_pid]
    if candidates:
        selected = min(candidates, key=lambda r: (r["phase"], r["within_phase_rank"], r["predicate_id"]))
    if problems:
        selected = None
    projection_material = {
        "decision_context_digest": bundle.get("decision_context_digest"),
        "coverage_qualification_digest": bundle.get("coverage_qualification_digest"),
        "endpoint_table_digest": bundle.get("endpoint_table_digest"),
        "true_predicate_ids": sorted(true_ids),
        "selected_predicate_id": selected.get("predicate_id") if selected else None,
        "selected_endpoint": selected.get("endpoint") if selected else None,
        "selected_phase": selected.get("phase") if selected else None,
        "selected_within_phase_rank": selected.get("within_phase_rank") if selected else None,
        "source_snapshot_digest": bundle.get("source_snapshot_digest"),
        "observation_head_digest": bundle.get("observation_head_digest"),
    }
    problems = sorted(set(problems))
    return {
        "state": "ENDPOINT_PROJECTION_DECISION_READY" if not problems else "ENDPOINT_PROJECTION_BLOCKED",
        "qualified": not problems,
        "problems": problems,
        "selected_predicate_id": projection_material["selected_predicate_id"],
        "selected_endpoint": projection_material["selected_endpoint"],
        "selected_phase": projection_material["selected_phase"],
        "selected_within_phase_rank": projection_material["selected_within_phase_rank"],
        "nonselected_true_predicate_ids": sorted(true_ids - ({selected.get("predicate_id")} if selected else set())),
        "projection_digest": digest(projection_material),
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R2_ENDPOINT_PROJECTION_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R2",
        "authority_effect": AUTHORITY_EFFECT,
    }
