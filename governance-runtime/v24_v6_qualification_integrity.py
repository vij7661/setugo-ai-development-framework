"""V24 I11 V6 remediation R8: anti-false-green and result accounting.

Construction-only implementation of V6 Sections 15 and 16.  The module
validates exact evidence/records and never grants runtime or terminal authority.
"""
from __future__ import annotations

import ast
import hashlib
import re
from typing import Any, Mapping

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    digest,
    validate_registry_completeness_qualification,
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
WDPC_LITERAL = re.compile(r"\bWDPC-[0-9]+\b", re.IGNORECASE)

HARD_FORBIDDEN_INPUT_KINDS = frozenset(
    {
        "WDPC_CASE_ID",
        "FIXTURE_BRANCH_ID",
        "TEST_EXPECTED_ENDPOINT",
        "REVIEWER_FINDING_ID",
        "TEST_ARTIFACT",
        "DIAGNOSTIC_STRING",
        "FIXTURE_REGISTRY",
        "FIXTURE_CLASSIFICATION",
        "FIXTURE_DISPOSITION",
    }
)

NONPASS_TERMINALS = frozenset(
    {
        "BLOCKED",
        "NOT_EXECUTED",
        "NOT_EXECUTABLE",
        "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
        "INSUFFICIENT_EVIDENCE",
        "FAIL",
        "FAIL_CODE_DEFECT",
        "FAIL_FIXTURE_DEFECT",
        "STALE",
        "WRONG_CANDIDATE",
        "UNRESOLVED",
    }
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _git_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX40.fullmatch(value))


def _unique_strings(value: Any) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], ["LIST_REQUIRED"]
    out: list[str] = []
    seen: set[str] = set()
    problems: list[str] = []
    for item in value:
        if not _nonempty(item):
            problems.append("STRING_MEMBER_INVALID")
        elif item in seen:
            problems.append(f"DUPLICATE_MEMBER:{item}")
        else:
            seen.add(item)
            out.append(item)
    return out, problems


def _without(record: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    out = dict(record)
    for field in fields:
        out.pop(field, None)
    return out


def _raw_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _identifier_flags(identifier: str) -> list[str]:
    normalized = identifier.lower().replace("-", "_")
    flags: list[str] = []
    checks = {
        "fixture_branch": "ANTI_FALSE_GREEN_FIXTURE_BRANCH_IDENTIFIER",
        "expected_endpoint": "ANTI_FALSE_GREEN_EXPECTED_ENDPOINT_IDENTIFIER",
        "reviewer_finding": "ANTI_FALSE_GREEN_REVIEWER_FINDING_IDENTIFIER",
        "diagnostic_endpoint": "ANTI_FALSE_GREEN_DIAGNOSTIC_ENDPOINT_IDENTIFIER",
        "test_fixture_registry": "ANTI_FALSE_GREEN_FIXTURE_REGISTRY_IDENTIFIER",
        "test_fixture_classification": "ANTI_FALSE_GREEN_FIXTURE_CLASSIFICATION_IDENTIFIER",
        "test_fixture_disposition": "ANTI_FALSE_GREEN_FIXTURE_DISPOSITION_IDENTIFIER",
    }
    for needle, problem in checks.items():
        if needle in normalized:
            flags.append(problem)
    return flags


def scan_production_authority_source(record: Mapping[str, Any]) -> dict[str, Any]:
    """AST-based static gate for production authority source.

    It intentionally scans code structure/identifiers and exact prohibited case
    namespace references, not fixture policy prose or expected outcomes.
    """
    problems: list[str] = []
    artifact_id = record.get("artifact_id")
    source = record.get("source_text")
    if not _nonempty(artifact_id):
        problems.append("ANTI_FALSE_GREEN_ARTIFACT_ID_REQUIRED")
    if record.get("artifact_role") != "PRODUCTION_AUTHORITY":
        problems.append("ANTI_FALSE_GREEN_ARTIFACT_ROLE_INVALID")
    if not isinstance(source, str):
        source = ""
        problems.append("ANTI_FALSE_GREEN_SOURCE_TEXT_REQUIRED")
    actual_digest = _raw_sha256(source)
    if record.get("content_digest") != actual_digest:
        problems.append("ANTI_FALSE_GREEN_SOURCE_DIGEST_MISMATCH")
    if record.get("qualification_state") != QUALIFIED:
        problems.append("ANTI_FALSE_GREEN_SOURCE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT:
        problems.append("ANTI_FALSE_GREEN_SOURCE_NOT_CURRENT")

    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = None
        problems.append("ANTI_FALSE_GREEN_SOURCE_SYNTAX_INVALID")

    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if WDPC_LITERAL.search(node.value):
                    problems.append("ANTI_FALSE_GREEN_WDPC_LITERAL_IN_PRODUCTION")
            elif isinstance(node, ast.Name):
                problems.extend(_identifier_flags(node.id))
            elif isinstance(node, ast.Attribute):
                problems.extend(_identifier_flags(node.attr))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.lower().split(".")[0]
                    if root in {"test", "tests", "testing", "fixtures", "fixture"}:
                        problems.append("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING")
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").lower()
                root = module.split(".")[0]
                if root in {"test", "tests", "testing", "fixtures", "fixture"}:
                    problems.append("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING")

    problems = sorted(set(problems))
    return {
        "state": "ANTI_FALSE_GREEN_SOURCE_CLEAR" if not problems else "ANTI_FALSE_GREEN_SOURCE_REJECTED",
        "qualified": not problems,
        "artifact_id": artifact_id,
        "content_digest": actual_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_runtime_authority_trace(record: Mapping[str, Any]) -> dict[str, Any]:
    """Reject test/reviewer/diagnostic sources from runtime authority derivation."""
    problems: list[str] = []
    for key in (
        "trace_id",
        "candidate_identity_id",
        "decision_subject_id",
        "endpoint_derivation_source",
        "independence_proof_subject_id",
        "independence_proof_producer_id",
    ):
        if not _nonempty(record.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_TRACE_FIELD_REQUIRED:{key}")
    if not _sha(record.get("trace_digest")):
        problems.append("ANTI_FALSE_GREEN_TRACE_DIGEST_INVALID")
    if record.get("qualification_state") != QUALIFIED:
        problems.append("ANTI_FALSE_GREEN_TRACE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT:
        problems.append("ANTI_FALSE_GREEN_TRACE_NOT_CURRENT")

    input_kinds, input_problems = _unique_strings(record.get("decision_input_kinds"))
    problems.extend(f"ANTI_FALSE_GREEN_TRACE_INPUT:{x}" for x in input_problems)
    for input_kind in sorted(set(input_kinds).intersection(HARD_FORBIDDEN_INPUT_KINDS)):
        problems.append(f"ANTI_FALSE_GREEN_FORBIDDEN_RUNTIME_INPUT:{input_kind}")
    if record.get("endpoint_derivation_source") == "DIAGNOSTIC_STRING":
        problems.append("ANTI_FALSE_GREEN_DIAGNOSTIC_STRING_ENDPOINT_DERIVATION")
    if record.get("independence_proof_producer_id") in {
        record.get("candidate_identity_id"),
        record.get("decision_subject_id"),
        record.get("independence_proof_subject_id"),
    }:
        problems.append("ANTI_FALSE_GREEN_SELF_CREATED_INDEPENDENCE_PROOF")

    runtime_refs, ref_problems = _unique_strings(record.get("runtime_artifact_refs"))
    problems.extend(f"ANTI_FALSE_GREEN_RUNTIME_REF:{x}" for x in ref_problems)
    for ref in runtime_refs:
        normalized = ref.lower().replace("\\", "/")
        if (
            "/testing/" in normalized
            or "/fixtures/" in normalized
            or normalized.startswith("testing/")
            or normalized.startswith("fixtures/")
            or "/test_" in normalized
            or normalized.startswith("test_")
        ):
            problems.append(f"ANTI_FALSE_GREEN_RUNTIME_TEST_ARTIFACT_COUPLING:{ref}")

    supplied = record.get("trace_digest")
    expected = digest(_without(record, "trace_digest"))
    if _sha(supplied) and supplied != expected:
        problems.append("ANTI_FALSE_GREEN_TRACE_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "ANTI_FALSE_GREEN_RUNTIME_TRACE_CLEAR" if not problems else "ANTI_FALSE_GREEN_RUNTIME_TRACE_REJECTED",
        "qualified": not problems,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_anti_false_green_gate(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    descriptor = bundle.get("gate_descriptor")
    if not isinstance(descriptor, Mapping):
        descriptor = {}
        problems.append("ANTI_FALSE_GREEN_GATE_DESCRIPTOR_REQUIRED")
    for key in ("gate_id", "gate_implementation_digest", "gate_qualification_digest"):
        if not _nonempty(descriptor.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_GATE_FIELD_REQUIRED:{key}")
    for key in ("gate_implementation_digest", "gate_qualification_digest"):
        if not _sha(descriptor.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_GATE_DIGEST_INVALID:{key}")
    if descriptor.get("qualification_state") != QUALIFIED:
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_QUALIFIED")
    if descriptor.get("independence_state") != QUALIFIED:
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_INDEPENDENT")
    if descriptor.get("currentness_result") != CURRENT:
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_CURRENT")

    sources = bundle.get("production_sources")
    if not isinstance(sources, list) or not sources:
        sources = []
        problems.append("ANTI_FALSE_GREEN_PRODUCTION_SOURCES_REQUIRED")
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            problems.append(f"ANTI_FALSE_GREEN_SOURCE_MALFORMED:{index}")
            continue
        result = scan_production_authority_source(source)
        problems.extend(f"SOURCE:{index}:{x}" for x in result["problems"])

    traces = bundle.get("runtime_traces")
    if not isinstance(traces, list) or not traces:
        traces = []
        problems.append("ANTI_FALSE_GREEN_RUNTIME_TRACES_REQUIRED")
    for index, trace in enumerate(traces):
        if not isinstance(trace, Mapping):
            problems.append(f"ANTI_FALSE_GREEN_TRACE_MALFORMED:{index}")
            continue
        result = validate_runtime_authority_trace(trace)
        problems.extend(f"TRACE:{index}:{x}" for x in result["problems"])

    allowlist = bundle.get("allowlist")
    if allowlist not in (None, {}):
        if not isinstance(allowlist, Mapping):
            problems.append("ANTI_FALSE_GREEN_ALLOWLIST_MALFORMED")
        else:
            entries, entry_problems = _unique_strings(allowlist.get("entries"))
            problems.extend(f"ANTI_FALSE_GREEN_ALLOWLIST:{x}" for x in entry_problems)
            completeness = allowlist.get("completeness_qualification")
            if not isinstance(completeness, Mapping):
                problems.append("ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_REQUIRED")
            else:
                generic = validate_registry_completeness_qualification(completeness)
                problems.extend(f"ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS:{x}" for x in generic)
                if completeness.get("actual_members") != sorted(entries):
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_ACTUAL_MEMBERS_MISMATCH")
                if completeness.get("result") != QUALIFIED:
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_NOT_QUALIFIED")
            # Hard V6 prohibitions are never bypassed by an allow-list.  A list
            # may document benign non-authority references only.
            if allowlist.get("permits_hard_prohibition_bypass") is True:
                problems.append("ANTI_FALSE_GREEN_HARD_PROHIBITION_ALLOWLIST_FORBIDDEN")

    problems = sorted(set(problems))
    return {
        "state": "ANTI_FALSE_GREEN_GATE_CLEAR" if not problems else "ANTI_FALSE_GREEN_GATE_REJECTED",
        "qualified": not problems,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _case_universe_content_digest(record: Mapping[str, Any]) -> str:
    return digest(_without(record, "content_digest", "completeness_qualification"))


def validate_qualification_case_universe(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the omission-sensitive universe used for one qualification round."""
    problems: list[str] = []
    for key in ("universe_id", "qualification_round_id"):
        if not _nonempty(record.get(key)):
            problems.append(f"QUALIFICATION_CASE_UNIVERSE_FIELD_REQUIRED:{key}")
    for key in ("candidate_commit", "candidate_tree"):
        if not _git_sha(record.get(key)):
            problems.append(f"QUALIFICATION_CASE_UNIVERSE_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "case_contract_set_digest"):
        if not _sha(record.get(key)):
            problems.append(f"QUALIFICATION_CASE_UNIVERSE_DIGEST_INVALID:{key}")
    if record.get("qualification_state") != QUALIFIED:
        problems.append("QUALIFICATION_CASE_UNIVERSE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT:
        problems.append("QUALIFICATION_CASE_UNIVERSE_NOT_CURRENT")

    case_ids, case_problems = _unique_strings(record.get("case_ids"))
    problems.extend(f"QUALIFICATION_CASE_UNIVERSE_CASES:{x}" for x in case_problems)
    if not case_ids:
        problems.append("QUALIFICATION_CASE_UNIVERSE_CASES_REQUIRED")
    case_ids = sorted(case_ids)
    computed_content_digest = _case_universe_content_digest(record)
    if record.get("content_digest") != computed_content_digest:
        problems.append("QUALIFICATION_CASE_UNIVERSE_CONTENT_DIGEST_MISMATCH")

    completeness = record.get("completeness_qualification")
    if not isinstance(completeness, Mapping):
        completeness = {}
        problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_REQUIRED")
    else:
        generic = validate_registry_completeness_qualification(completeness)
        problems.extend(f"QUALIFICATION_CASE_UNIVERSE_COMPLETENESS:{x}" for x in generic)
        if completeness.get("subject_object_id") != record.get("universe_id"):
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_ID_MISMATCH")
        if completeness.get("subject_content_digest") != computed_content_digest:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
        if completeness.get("actual_members") != case_ids:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_ACTUAL_MEMBERS_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_NOT_QUALIFIED")

    problems = sorted(set(problems))
    return {
        "state": "QUALIFICATION_CASE_UNIVERSE_QUALIFIED" if not problems else "QUALIFICATION_CASE_UNIVERSE_INVALID",
        "qualified": not problems,
        "universe_id": record.get("universe_id"),
        "qualification_round_id": record.get("qualification_round_id"),
        "candidate_commit": record.get("candidate_commit"),
        "candidate_tree": record.get("candidate_tree"),
        "environment_digest": record.get("environment_digest"),
        "case_ids": case_ids,
        "content_digest": computed_content_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _validate_result_record(record: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    for key in ("result_id", "qualification_round_id", "case_id", "execution_state", "terminal_disposition"):
        if not _nonempty(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_FIELD_REQUIRED:{key}")
    for key in ("candidate_commit", "candidate_tree"):
        if not _git_sha(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "case_contract_digest"):
        if not _sha(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_DIGEST_INVALID:{key}")
    for key in ("qualification_basis_digests", "evidence_basis_digests"):
        values, value_problems = _unique_strings(record.get(key))
        problems.extend(f"QUALIFICATION_RESULT_{key}:{x}" for x in value_problems)
        if not values or not all(_sha(value) for value in values):
            problems.append(f"QUALIFICATION_RESULT_DIGEST_SET_INVALID:{key}")
    sequence = record.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        problems.append("QUALIFICATION_RESULT_SEQUENCE_INVALID")
    prior = record.get("resolves_prior_result_digest")
    if prior not in (None, "") and not _sha(prior):
        problems.append("QUALIFICATION_RESULT_PRIOR_DIGEST_INVALID")
    supplied = record.get("result_record_digest")
    if not _sha(supplied):
        problems.append("QUALIFICATION_RESULT_RECORD_DIGEST_INVALID")
    elif supplied != digest(_without(record, "result_record_digest")):
        problems.append("QUALIFICATION_RESULT_RECORD_DIGEST_MISMATCH")
    return sorted(set(problems))


def compile_qualification_summary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Compile one exact qualification round without rewriting prior rounds."""
    problems: list[str] = []
    compiler = bundle.get("summary_compiler")
    if not isinstance(compiler, Mapping):
        compiler = {}
        problems.append("QUALIFICATION_SUMMARY_COMPILER_REQUIRED")
    for key in ("compiler_id", "compiler_digest", "compiler_qualification_digest"):
        if not _nonempty(compiler.get(key)):
            problems.append(f"QUALIFICATION_SUMMARY_COMPILER_FIELD_REQUIRED:{key}")
    for key in ("compiler_digest", "compiler_qualification_digest"):
        if not _sha(compiler.get(key)):
            problems.append(f"QUALIFICATION_SUMMARY_COMPILER_DIGEST_INVALID:{key}")
    if compiler.get("qualification_state") != QUALIFIED:
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_QUALIFIED")
    if compiler.get("independence_state") != QUALIFIED:
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_INDEPENDENT")
    if compiler.get("currentness_result") != CURRENT:
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_CURRENT")

    universe_record = bundle.get("case_universe")
    if not isinstance(universe_record, Mapping):
        universe_record = {}
    universe = validate_qualification_case_universe(universe_record)
    problems.extend(f"QUALIFICATION_SUMMARY_UNIVERSE:{x}" for x in universe["problems"])

    target_round = bundle.get("qualification_round_id")
    if target_round != universe.get("qualification_round_id"):
        problems.append("QUALIFICATION_SUMMARY_ROUND_MISMATCH")

    records = bundle.get("result_records")
    if not isinstance(records, list):
        records = []
        problems.append("QUALIFICATION_SUMMARY_RESULTS_REQUIRED")

    all_by_digest: dict[str, Mapping[str, Any]] = {}
    current_round_by_case: dict[str, Mapping[str, Any]] = {}
    seen_result_ids: set[str] = set()
    previous_sequence = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            problems.append(f"QUALIFICATION_RESULT_MALFORMED:{index}")
            continue
        for issue in _validate_result_record(record):
            problems.append(f"RESULT:{index}:{issue}")
        rid = record.get("result_id")
        if _nonempty(rid):
            if rid in seen_result_ids:
                problems.append(f"QUALIFICATION_RESULT_ID_DUPLICATE:{rid}")
            seen_result_ids.add(rid)
        seq = record.get("sequence")
        if isinstance(seq, int) and not isinstance(seq, bool):
            if seq <= previous_sequence:
                problems.append("QUALIFICATION_RESULT_HISTORY_SEQUENCE_NOT_MONOTONIC")
            previous_sequence = max(previous_sequence, seq)
        rdigest = record.get("result_record_digest")
        if _sha(rdigest):
            if rdigest in all_by_digest:
                problems.append(f"QUALIFICATION_RESULT_DIGEST_DUPLICATE:{rdigest}")
            all_by_digest[rdigest] = record
        prior = record.get("resolves_prior_result_digest")
        if _sha(prior):
            if prior not in all_by_digest:
                problems.append(f"QUALIFICATION_RESULT_PRIOR_NOT_PRESERVED:{rid}")
            else:
                prior_record = all_by_digest[prior]
                if prior_record.get("case_id") != record.get("case_id"):
                    problems.append(f"QUALIFICATION_RESULT_PRIOR_CASE_MISMATCH:{rid}")
                if prior_record.get("qualification_round_id") == record.get("qualification_round_id"):
                    problems.append(f"QUALIFICATION_RESULT_SAME_ROUND_REWRITE_FORBIDDEN:{rid}")
        if record.get("qualification_round_id") == target_round:
            case_id = record.get("case_id")
            if case_id in current_round_by_case:
                problems.append(f"QUALIFICATION_SUMMARY_MULTIPLE_RESULTS_SAME_ROUND:{case_id}")
            elif _nonempty(case_id):
                current_round_by_case[case_id] = record

    expected_cases = set(universe.get("case_ids", []))
    observed_cases = set(current_round_by_case)
    for missing in sorted(expected_cases - observed_cases):
        problems.append(f"QUALIFICATION_SUMMARY_CASE_RESULT_MISSING:{missing}")
    for extra in sorted(observed_cases - expected_cases):
        problems.append(f"QUALIFICATION_SUMMARY_CASE_OUTSIDE_UNIVERSE:{extra}")

    pass_cases: list[str] = []
    nonpass: dict[str, str] = {}
    for case_id in sorted(expected_cases):
        record = current_round_by_case.get(case_id)
        if record is None:
            nonpass[case_id] = "MISSING"
            continue
        exact_binding = (
            record.get("candidate_commit") == universe.get("candidate_commit")
            and record.get("candidate_tree") == universe.get("candidate_tree")
            and record.get("environment_digest") == universe.get("environment_digest")
        )
        is_pass = (
            record.get("execution_state") == "EXECUTED"
            and record.get("terminal_disposition") == "PASS"
            and record.get("binding_valid") is True
            and exact_binding
            and not any(
                issue.startswith("RESULT:") and f":{case_id}:" in issue
                for issue in problems
            )
        )
        if is_pass:
            pass_cases.append(case_id)
        else:
            disposition = record.get("terminal_disposition") or record.get("execution_state") or "INVALID"
            nonpass[case_id] = str(disposition)
            if record.get("terminal_disposition") == "PASS" and not exact_binding:
                problems.append(f"QUALIFICATION_SUMMARY_WRONG_BINDING_PASS_REJECTED:{case_id}")
            if record.get("terminal_disposition") in NONPASS_TERMINALS:
                # Explicitly retained as non-PASS; no error is necessary merely
                # because the case failed/blocked/unresolved.
                pass

    summary_material = {
        "qualification_round_id": target_round,
        "case_universe_content_digest": universe.get("content_digest"),
        "candidate_commit": universe.get("candidate_commit"),
        "candidate_tree": universe.get("candidate_tree"),
        "environment_digest": universe.get("environment_digest"),
        "pass_cases": pass_cases,
        "nonpass": nonpass,
        "result_record_digests": sorted(
            record.get("result_record_digest")
            for record in current_round_by_case.values()
            if _sha(record.get("result_record_digest"))
        ),
        "compiler_digest": compiler.get("compiler_digest"),
        "compiler_qualification_digest": compiler.get("compiler_qualification_digest"),
    }
    problems = sorted(set(problems))
    return {
        "state": "QUALIFICATION_SUMMARY_COMPILED" if not problems else "QUALIFICATION_SUMMARY_INVALID",
        "qualified": not problems,
        "qualification_round_id": target_round,
        "case_count": len(expected_cases),
        "pass_count": len(pass_cases),
        "pass_cases": pass_cases,
        "nonpass": nonpass,
        "summary_digest": digest(summary_material),
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R8_QUALIFICATION_INTEGRITY_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R8",
        "authority_effect": AUTHORITY_EFFECT,
    }
