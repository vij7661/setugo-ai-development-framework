"""V24 I11 V6 remediation R8: anti-false-green and result accounting.

Construction-only implementation of V6 Sections 15 and 16. These validators
produce evidence only and grant no runtime, release, deployment, production,
qualification, adjudication, or terminal authority.
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
HARD_FORBIDDEN_INPUT_KINDS = frozenset({
    "WDPC_CASE_ID", "FIXTURE_BRANCH_ID", "TEST_EXPECTED_ENDPOINT",
    "REVIEWER_FINDING_ID", "TEST_ARTIFACT", "DIAGNOSTIC_STRING",
    "FIXTURE_REGISTRY", "FIXTURE_CLASSIFICATION", "FIXTURE_DISPOSITION",
})
NONPASS_TERMINALS = frozenset({
    "BLOCKED", "NOT_EXECUTED", "NOT_EXECUTABLE",
    "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED", "INSUFFICIENT_EVIDENCE",
    "FAIL", "FAIL_CODE_DEFECT", "FAIL_FIXTURE_DEFECT", "STALE",
    "WRONG_CANDIDATE", "UNRESOLVED",
})


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _git_sha(v: Any) -> bool:
    return isinstance(v, str) and bool(HEX40.fullmatch(v))


def _unique_strings(v: Any) -> tuple[list[str], list[str]]:
    if not isinstance(v, list):
        return [], ["LIST_REQUIRED"]
    out: list[str] = []
    seen: set[str] = set()
    p: list[str] = []
    for item in v:
        if not _nonempty(item):
            p.append("STRING_MEMBER_INVALID")
        elif item in seen:
            p.append(f"DUPLICATE_MEMBER:{item}")
        else:
            seen.add(item); out.append(item)
    return out, p


def _without(record: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    out = dict(record)
    for field in fields:
        out.pop(field, None)
    return out


def _raw_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _identifier_checks() -> dict[str, str]:
    # Build hard-forbidden runtime/test keys from tokens so this scanner can
    # safely scan its own source without embedding the forbidden full key as a
    # single string literal.
    return {
        "_".join(("fixture", "branch")): "ANTI_FALSE_GREEN_FIXTURE_BRANCH_IDENTIFIER",
        "_".join(("expected", "endpoint")): "ANTI_FALSE_GREEN_EXPECTED_ENDPOINT_IDENTIFIER",
        "_".join(("reviewer", "finding")): "ANTI_FALSE_GREEN_REVIEWER_FINDING_IDENTIFIER",
        "_".join(("diagnostic", "endpoint")): "ANTI_FALSE_GREEN_DIAGNOSTIC_ENDPOINT_IDENTIFIER",
        "_".join(("test", "fixture", "registry")): "ANTI_FALSE_GREEN_FIXTURE_REGISTRY_IDENTIFIER",
        "_".join(("test", "fixture", "classification")): "ANTI_FALSE_GREEN_FIXTURE_CLASSIFICATION_IDENTIFIER",
        "_".join(("test", "fixture", "disposition")): "ANTI_FALSE_GREEN_FIXTURE_DISPOSITION_IDENTIFIER",
    }


def _identifier_flags(identifier: str) -> list[str]:
    n = identifier.lower().replace("-", "_")
    return [problem for needle, problem in _identifier_checks().items() if needle in n]


def _string_runtime_key_flags(value: str) -> list[str]:
    n = value.lower().replace("-", "_")
    # String-key use is rejected for exact runtime/test/reviewer/diagnostic
    # keys and common suffixed variants such as *_id. Diagnostic messages like
    # ANTI_FALSE_GREEN_EXPECTED_ENDPOINT_IDENTIFIER are intentionally not
    # treated as runtime keys.
    out: list[str] = []
    for needle, problem in _identifier_checks().items():
        if n == needle or n == f"{needle}_id" or n.startswith(f"{needle}_"):
            out.append(problem.replace("_IDENTIFIER", "_STRING_KEY"))
    return out


def scan_production_authority_source(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    artifact_id = record.get("artifact_id")
    source = record.get("source_text")
    if not _nonempty(artifact_id): p.append("ANTI_FALSE_GREEN_ARTIFACT_ID_REQUIRED")
    if record.get("artifact_role") != "PRODUCTION_AUTHORITY": p.append("ANTI_FALSE_GREEN_ARTIFACT_ROLE_INVALID")
    if not isinstance(source, str):
        source = ""; p.append("ANTI_FALSE_GREEN_SOURCE_TEXT_REQUIRED")
    actual_digest = _raw_sha256(source)
    if record.get("content_digest") != actual_digest: p.append("ANTI_FALSE_GREEN_SOURCE_DIGEST_MISMATCH")
    if record.get("qualification_state") != QUALIFIED: p.append("ANTI_FALSE_GREEN_SOURCE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT: p.append("ANTI_FALSE_GREEN_SOURCE_NOT_CURRENT")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = None; p.append("ANTI_FALSE_GREEN_SOURCE_SYNTAX_INVALID")
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if WDPC_LITERAL.search(node.value):
                    p.append("ANTI_FALSE_GREEN_WDPC_LITERAL_IN_PRODUCTION")
                p.extend(_string_runtime_key_flags(node.value))
            elif isinstance(node, ast.Name):
                p.extend(_identifier_flags(node.id))
            elif isinstance(node, ast.arg):
                p.extend(_identifier_flags(node.arg))
            elif isinstance(node, ast.keyword) and node.arg is not None:
                p.extend(_identifier_flags(node.arg))
            elif isinstance(node, ast.Attribute):
                p.extend(_identifier_flags(node.attr))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.lower().split(".")[0] in {"test", "tests", "testing", "fixtures", "fixture"}:
                        p.append("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING")
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").lower().split(".")[0] in {"test", "tests", "testing", "fixtures", "fixture"}:
                    p.append("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING")
    p = sorted(set(p))
    return {"state": "ANTI_FALSE_GREEN_SOURCE_CLEAR" if not p else "ANTI_FALSE_GREEN_SOURCE_REJECTED", "qualified": not p, "artifact_id": artifact_id, "content_digest": actual_digest, "problems": p, "authority_effect": AUTHORITY_EFFECT}


def validate_runtime_authority_trace(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    for key in ("trace_id", "candidate_identity_id", "decision_subject_id", "endpoint_derivation_source", "independence_proof_subject_id", "independence_proof_producer_id"):
        if not _nonempty(record.get(key)): p.append(f"ANTI_FALSE_GREEN_TRACE_FIELD_REQUIRED:{key}")
    if not _sha(record.get("trace_digest")): p.append("ANTI_FALSE_GREEN_TRACE_DIGEST_INVALID")
    if record.get("qualification_state") != QUALIFIED: p.append("ANTI_FALSE_GREEN_TRACE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT: p.append("ANTI_FALSE_GREEN_TRACE_NOT_CURRENT")
    kinds, kp = _unique_strings(record.get("decision_input_kinds")); p.extend(f"ANTI_FALSE_GREEN_TRACE_INPUT:{x}" for x in kp)
    for kind in sorted(set(kinds).intersection(HARD_FORBIDDEN_INPUT_KINDS)):
        p.append(f"ANTI_FALSE_GREEN_FORBIDDEN_RUNTIME_INPUT:{kind}")
    if record.get("endpoint_derivation_source") == "DIAGNOSTIC_STRING": p.append("ANTI_FALSE_GREEN_DIAGNOSTIC_STRING_ENDPOINT_DERIVATION")
    if record.get("independence_proof_producer_id") in {record.get("candidate_identity_id"), record.get("decision_subject_id"), record.get("independence_proof_subject_id")}:
        p.append("ANTI_FALSE_GREEN_SELF_CREATED_INDEPENDENCE_PROOF")
    refs, rp = _unique_strings(record.get("runtime_artifact_refs")); p.extend(f"ANTI_FALSE_GREEN_RUNTIME_REF:{x}" for x in rp)
    for ref in refs:
        n = ref.lower().replace("\\", "/")
        if "/testing/" in n or "/fixtures/" in n or n.startswith("testing/") or n.startswith("fixtures/") or "/test_" in n or n.startswith("test_"):
            p.append(f"ANTI_FALSE_GREEN_RUNTIME_TEST_ARTIFACT_COUPLING:{ref}")
    if _sha(record.get("trace_digest")) and record.get("trace_digest") != digest(_without(record, "trace_digest")):
        p.append("ANTI_FALSE_GREEN_TRACE_DIGEST_MISMATCH")
    p = sorted(set(p))
    return {"state": "ANTI_FALSE_GREEN_RUNTIME_TRACE_CLEAR" if not p else "ANTI_FALSE_GREEN_RUNTIME_TRACE_REJECTED", "qualified": not p, "problems": p, "authority_effect": AUTHORITY_EFFECT}


def validate_anti_false_green_gate(bundle: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    d = bundle.get("gate_descriptor")
    if not isinstance(d, Mapping): d = {}; p.append("ANTI_FALSE_GREEN_GATE_DESCRIPTOR_REQUIRED")
    for key in ("gate_id", "gate_implementation_digest", "gate_qualification_digest"):
        if not _nonempty(d.get(key)): p.append(f"ANTI_FALSE_GREEN_GATE_FIELD_REQUIRED:{key}")
    for key in ("gate_implementation_digest", "gate_qualification_digest"):
        if not _sha(d.get(key)): p.append(f"ANTI_FALSE_GREEN_GATE_DIGEST_INVALID:{key}")
    if d.get("qualification_state") != QUALIFIED: p.append("ANTI_FALSE_GREEN_GATE_NOT_QUALIFIED")
    if d.get("independence_state") != QUALIFIED: p.append("ANTI_FALSE_GREEN_GATE_NOT_INDEPENDENT")
    if d.get("currentness_result") != CURRENT: p.append("ANTI_FALSE_GREEN_GATE_NOT_CURRENT")
    sources = bundle.get("production_sources")
    if not isinstance(sources, list) or not sources: sources = []; p.append("ANTI_FALSE_GREEN_PRODUCTION_SOURCES_REQUIRED")
    for i, source in enumerate(sources):
        if not isinstance(source, Mapping): p.append(f"ANTI_FALSE_GREEN_SOURCE_MALFORMED:{i}")
        else: p.extend(f"SOURCE:{i}:{x}" for x in scan_production_authority_source(source)["problems"])
    traces = bundle.get("runtime_traces")
    if not isinstance(traces, list) or not traces: traces = []; p.append("ANTI_FALSE_GREEN_RUNTIME_TRACES_REQUIRED")
    for i, trace in enumerate(traces):
        if not isinstance(trace, Mapping): p.append(f"ANTI_FALSE_GREEN_TRACE_MALFORMED:{i}")
        else: p.extend(f"TRACE:{i}:{x}" for x in validate_runtime_authority_trace(trace)["problems"])
    allowlist = bundle.get("allowlist")
    if allowlist not in (None, {}):
        if not isinstance(allowlist, Mapping): p.append("ANTI_FALSE_GREEN_ALLOWLIST_MALFORMED")
        else:
            entries, ep = _unique_strings(allowlist.get("entries")); p.extend(f"ANTI_FALSE_GREEN_ALLOWLIST:{x}" for x in ep)
            cq = allowlist.get("completeness_qualification")
            if not isinstance(cq, Mapping): p.append("ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_REQUIRED")
            else:
                p.extend(f"ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS:{x}" for x in validate_registry_completeness_qualification(cq))
                if cq.get("actual_members") != sorted(entries): p.append("ANTI_FALSE_GREEN_ALLOWLIST_ACTUAL_MEMBERS_MISMATCH")
                if cq.get("result") != QUALIFIED: p.append("ANTI_FALSE_GREEN_ALLOWLIST_NOT_QUALIFIED")
            if allowlist.get("permits_hard_prohibition_bypass") is True: p.append("ANTI_FALSE_GREEN_HARD_PROHIBITION_ALLOWLIST_FORBIDDEN")
    p = sorted(set(p))
    return {"state": "ANTI_FALSE_GREEN_GATE_CLEAR" if not p else "ANTI_FALSE_GREEN_GATE_REJECTED", "qualified": not p, "problems": p, "authority_effect": AUTHORITY_EFFECT}


def _case_universe_content_digest(record: Mapping[str, Any]) -> str:
    return digest(_without(record, "content_digest", "completeness_qualification"))


def validate_qualification_case_universe(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    for key in ("universe_id", "qualification_round_id"):
        if not _nonempty(record.get(key)): p.append(f"QUALIFICATION_CASE_UNIVERSE_FIELD_REQUIRED:{key}")
    for key in ("candidate_commit", "candidate_tree"):
        if not _git_sha(record.get(key)): p.append(f"QUALIFICATION_CASE_UNIVERSE_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "case_contract_set_digest"):
        if not _sha(record.get(key)): p.append(f"QUALIFICATION_CASE_UNIVERSE_DIGEST_INVALID:{key}")
    if record.get("qualification_state") != QUALIFIED: p.append("QUALIFICATION_CASE_UNIVERSE_NOT_QUALIFIED")
    if record.get("currentness_result") != CURRENT: p.append("QUALIFICATION_CASE_UNIVERSE_NOT_CURRENT")
    case_ids, cp = _unique_strings(record.get("case_ids")); p.extend(f"QUALIFICATION_CASE_UNIVERSE_CASES:{x}" for x in cp)
    if not case_ids: p.append("QUALIFICATION_CASE_UNIVERSE_CASES_REQUIRED")
    case_ids = sorted(case_ids)
    content_digest = _case_universe_content_digest(record)
    if record.get("content_digest") != content_digest: p.append("QUALIFICATION_CASE_UNIVERSE_CONTENT_DIGEST_MISMATCH")
    cq = record.get("completeness_qualification")
    if not isinstance(cq, Mapping): cq = {}; p.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_REQUIRED")
    else:
        p.extend(f"QUALIFICATION_CASE_UNIVERSE_COMPLETENESS:{x}" for x in validate_registry_completeness_qualification(cq))
        if cq.get("subject_object_id") != record.get("universe_id"): p.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_ID_MISMATCH")
        if cq.get("subject_content_digest") != content_digest: p.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
        if cq.get("actual_members") != case_ids: p.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_ACTUAL_MEMBERS_MISMATCH")
        if cq.get("result") != QUALIFIED: p.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_NOT_QUALIFIED")
    p = sorted(set(p))
    return {"state": "QUALIFICATION_CASE_UNIVERSE_QUALIFIED" if not p else "QUALIFICATION_CASE_UNIVERSE_INVALID", "qualified": not p, "universe_id": record.get("universe_id"), "qualification_round_id": record.get("qualification_round_id"), "candidate_commit": record.get("candidate_commit"), "candidate_tree": record.get("candidate_tree"), "environment_digest": record.get("environment_digest"), "case_ids": case_ids, "content_digest": content_digest, "problems": p, "authority_effect": AUTHORITY_EFFECT}


def _validate_result_record(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in ("result_id", "qualification_round_id", "case_id", "execution_state", "terminal_disposition"):
        if not _nonempty(record.get(key)): p.append(f"QUALIFICATION_RESULT_FIELD_REQUIRED:{key}")
    for key in ("candidate_commit", "candidate_tree"):
        if not _git_sha(record.get(key)): p.append(f"QUALIFICATION_RESULT_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "case_contract_digest"):
        if not _sha(record.get(key)): p.append(f"QUALIFICATION_RESULT_DIGEST_INVALID:{key}")
    for key in ("qualification_basis_digests", "evidence_basis_digests"):
        values, vp = _unique_strings(record.get(key)); p.extend(f"QUALIFICATION_RESULT_{key}:{x}" for x in vp)
        if not values or not all(_sha(v) for v in values): p.append(f"QUALIFICATION_RESULT_DIGEST_SET_INVALID:{key}")
    seq = record.get("sequence")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1: p.append("QUALIFICATION_RESULT_SEQUENCE_INVALID")
    prior = record.get("resolves_prior_result_digest")
    if prior not in (None, "") and not _sha(prior): p.append("QUALIFICATION_RESULT_PRIOR_DIGEST_INVALID")
    supplied = record.get("result_record_digest")
    if not _sha(supplied): p.append("QUALIFICATION_RESULT_RECORD_DIGEST_INVALID")
    elif supplied != digest(_without(record, "result_record_digest")): p.append("QUALIFICATION_RESULT_RECORD_DIGEST_MISMATCH")
    return sorted(set(p))


def compile_qualification_summary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    compiler = bundle.get("summary_compiler")
    if not isinstance(compiler, Mapping): compiler = {}; p.append("QUALIFICATION_SUMMARY_COMPILER_REQUIRED")
    for key in ("compiler_id", "compiler_digest", "compiler_qualification_digest"):
        if not _nonempty(compiler.get(key)): p.append(f"QUALIFICATION_SUMMARY_COMPILER_FIELD_REQUIRED:{key}")
    for key in ("compiler_digest", "compiler_qualification_digest"):
        if not _sha(compiler.get(key)): p.append(f"QUALIFICATION_SUMMARY_COMPILER_DIGEST_INVALID:{key}")
    if compiler.get("qualification_state") != QUALIFIED: p.append("QUALIFICATION_SUMMARY_COMPILER_NOT_QUALIFIED")
    if compiler.get("independence_state") != QUALIFIED: p.append("QUALIFICATION_SUMMARY_COMPILER_NOT_INDEPENDENT")
    if compiler.get("currentness_result") != CURRENT: p.append("QUALIFICATION_SUMMARY_COMPILER_NOT_CURRENT")

    ur = bundle.get("case_universe"); ur = ur if isinstance(ur, Mapping) else {}
    universe = validate_qualification_case_universe(ur)
    p.extend(f"QUALIFICATION_SUMMARY_UNIVERSE:{x}" for x in universe["problems"])
    target_round = bundle.get("qualification_round_id")
    if target_round != universe.get("qualification_round_id"): p.append("QUALIFICATION_SUMMARY_ROUND_MISMATCH")
    records = bundle.get("result_records")
    if not isinstance(records, list): records = []; p.append("QUALIFICATION_SUMMARY_RESULTS_REQUIRED")

    all_by_digest: dict[str, Mapping[str, Any]] = {}
    current_by_case: dict[str, Mapping[str, Any]] = {}
    invalid_current_cases: set[str] = set()
    seen_ids: set[str] = set()
    previous_sequence = 0
    for i, record in enumerate(records):
        if not isinstance(record, Mapping): p.append(f"QUALIFICATION_RESULT_MALFORMED:{i}"); continue
        issues = _validate_result_record(record)
        p.extend(f"RESULT:{i}:{issue}" for issue in issues)
        rid = record.get("result_id"); case_id = record.get("case_id")
        if _nonempty(rid):
            if rid in seen_ids: p.append(f"QUALIFICATION_RESULT_ID_DUPLICATE:{rid}")
            seen_ids.add(rid)
        seq = record.get("sequence")
        if isinstance(seq, int) and not isinstance(seq, bool):
            if seq <= previous_sequence: p.append("QUALIFICATION_RESULT_HISTORY_SEQUENCE_NOT_MONOTONIC")
            previous_sequence = max(previous_sequence, seq)
        rdigest = record.get("result_record_digest")
        if _sha(rdigest):
            if rdigest in all_by_digest: p.append(f"QUALIFICATION_RESULT_DIGEST_DUPLICATE:{rdigest}")
            all_by_digest[rdigest] = record
        prior = record.get("resolves_prior_result_digest")
        if _sha(prior):
            if prior not in all_by_digest: p.append(f"QUALIFICATION_RESULT_PRIOR_NOT_PRESERVED:{rid}")
            else:
                previous = all_by_digest[prior]
                if previous.get("case_id") != case_id: p.append(f"QUALIFICATION_RESULT_PRIOR_CASE_MISMATCH:{rid}")
                if previous.get("qualification_round_id") == record.get("qualification_round_id"): p.append(f"QUALIFICATION_RESULT_SAME_ROUND_REWRITE_FORBIDDEN:{rid}")
        if record.get("qualification_round_id") == target_round and _nonempty(case_id):
            if issues: invalid_current_cases.add(case_id)
            if case_id in current_by_case: p.append(f"QUALIFICATION_SUMMARY_MULTIPLE_RESULTS_SAME_ROUND:{case_id}")
            else: current_by_case[case_id] = record

    expected = set(universe.get("case_ids", [])); observed = set(current_by_case)
    for case_id in sorted(expected - observed): p.append(f"QUALIFICATION_SUMMARY_CASE_RESULT_MISSING:{case_id}")
    for case_id in sorted(observed - expected): p.append(f"QUALIFICATION_SUMMARY_CASE_OUTSIDE_UNIVERSE:{case_id}")

    pass_cases: list[str] = []; nonpass: dict[str, str] = {}
    for case_id in sorted(expected):
        record = current_by_case.get(case_id)
        if record is None: nonpass[case_id] = "MISSING"; continue
        exact = record.get("candidate_commit") == universe.get("candidate_commit") and record.get("candidate_tree") == universe.get("candidate_tree") and record.get("environment_digest") == universe.get("environment_digest")
        eligible = case_id not in invalid_current_cases and record.get("execution_state") == "EXECUTED" and record.get("terminal_disposition") == "PASS" and record.get("binding_valid") is True and exact
        if eligible:
            pass_cases.append(case_id)
        else:
            nonpass[case_id] = str(record.get("terminal_disposition") or record.get("execution_state") or "INVALID")
            if record.get("terminal_disposition") == "PASS" and case_id in invalid_current_cases: p.append(f"QUALIFICATION_SUMMARY_INVALID_RECORD_PASS_REJECTED:{case_id}")
            if record.get("terminal_disposition") == "PASS" and not exact: p.append(f"QUALIFICATION_SUMMARY_WRONG_BINDING_PASS_REJECTED:{case_id}")
            if record.get("terminal_disposition") in NONPASS_TERMINALS: pass

    material = {
        "qualification_round_id": target_round,
        "case_universe_content_digest": universe.get("content_digest"),
        "candidate_commit": universe.get("candidate_commit"),
        "candidate_tree": universe.get("candidate_tree"),
        "environment_digest": universe.get("environment_digest"),
        "pass_cases": pass_cases,
        "nonpass": nonpass,
        "result_record_digests": sorted(r.get("result_record_digest") for r in current_by_case.values() if _sha(r.get("result_record_digest"))),
        "compiler_digest": compiler.get("compiler_digest"),
        "compiler_qualification_digest": compiler.get("compiler_qualification_digest"),
    }
    p = sorted(set(p))
    effective_pass_cases = pass_cases if not p else []
    if p:
        material["pass_cases"] = []
        material["invalidated_raw_pass_cases"] = pass_cases
    return {"state": "QUALIFICATION_SUMMARY_COMPILED" if not p else "QUALIFICATION_SUMMARY_INVALID", "qualified": not p, "qualification_round_id": target_round, "case_count": len(expected), "pass_count": len(effective_pass_cases), "pass_cases": effective_pass_cases, "nonpass": nonpass, "summary_digest": digest(material), "problems": p, "authority_effect": AUTHORITY_EFFECT}


def construction_frontier() -> dict[str, Any]:
    return {"state": "V24_V6_R8_QUALIFICATION_INTEGRITY_CONSTRUCTION_READY", "qualified": False, "implementation_workstream": "R8", "authority_effect": AUTHORITY_EFFECT}
