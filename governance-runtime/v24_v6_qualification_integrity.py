"""V24 I11 V6 remediation R8: anti-false-green and result accounting.

Construction-only implementation of V6 Sections 15 and 16. Authority-bearing
gate, source, trace, case-universe, result, completeness, and compiler claims
resolve exact R1 proof records through a separately trusted proof context.
These validators grant no runtime, release, deployment, production, scientific,
adjudication, or terminal authority.
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
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
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
    material = dict(record)
    for field in fields:
        material.pop(field, None)
    return material


def _raw_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def _identifier_flags(identifier: str) -> list[str]:
    normalized = identifier.lower().replace("-", "_")
    checks = {
        "fixture_branch": "ANTI_FALSE_GREEN_FIXTURE_BRANCH_IDENTIFIER",
        "expected_endpoint": "ANTI_FALSE_GREEN_EXPECTED_ENDPOINT_IDENTIFIER",
        "reviewer_finding": "ANTI_FALSE_GREEN_REVIEWER_FINDING_IDENTIFIER",
        "diagnostic_endpoint": "ANTI_FALSE_GREEN_DIAGNOSTIC_ENDPOINT_IDENTIFIER",
        "test_fixture_registry": "ANTI_FALSE_GREEN_FIXTURE_REGISTRY_IDENTIFIER",
        "test_fixture_classification": "ANTI_FALSE_GREEN_FIXTURE_CLASSIFICATION_IDENTIFIER",
        "test_fixture_disposition": "ANTI_FALSE_GREEN_FIXTURE_DISPOSITION_IDENTIFIER",
    }
    return [problem for needle, problem in checks.items() if needle in normalized]


def scan_production_authority_source(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan exact source bytes and require exact qualification/currentness of them."""
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
    if record.get("qualification_state") not in (None, QUALIFIED):
        problems.append("ANTI_FALSE_GREEN_SOURCE_NOT_QUALIFIED")
    if record.get("currentness_result") not in (None, CURRENT):
        problems.append("ANTI_FALSE_GREEN_SOURCE_NOT_CURRENT")
    for key in ("source_qualification_digest", "source_currentness_binding_digest"):
        if not _sha(record.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_SOURCE_PROOF_DIGEST_INVALID:{key}")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": record.get("source_qualification_digest"),
                "subject_id": artifact_id,
                "subject_content_digest": actual_digest,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": record.get("source_currentness_binding_digest"),
                "source_id": artifact_id,
                "source_digest": actual_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix=f"ANTI_FALSE_GREEN_SOURCE_PROOF:{artifact_id}",
        problems=problems,
    )

    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = None
        problems.append("ANTI_FALSE_GREEN_SOURCE_SYNTAX_INVALID")
    if tree is not None:
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and WDPC_LITERAL.search(node.value)
            ):
                problems.append("ANTI_FALSE_GREEN_WDPC_LITERAL_IN_PRODUCTION")
            elif isinstance(node, ast.Name):
                problems.extend(_identifier_flags(node.id))
            elif isinstance(node, ast.Attribute):
                problems.extend(_identifier_flags(node.attr))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.lower().split(".")[0] in {
                        "test",
                        "tests",
                        "testing",
                        "fixtures",
                        "fixture",
                    }:
                        problems.append("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING")
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").lower().split(".")[0] in {
                    "test",
                    "tests",
                    "testing",
                    "fixtures",
                    "fixture",
                }:
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


def canonical_trace_content_digest(record: Mapping[str, Any]) -> str:
    return digest(
        _without(
            record,
            "trace_digest",
            "trace_qualification_digest",
            "trace_independence_qualification_digest",
            "trace_currentness_binding_digest",
        )
    )


def validate_runtime_authority_trace(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Reject test-coupled traces and require exact Q/I/currentness proof closure."""
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
    computed_trace_digest = canonical_trace_content_digest(record)
    if not _sha(record.get("trace_digest")):
        problems.append("ANTI_FALSE_GREEN_TRACE_DIGEST_INVALID")
    elif record.get("trace_digest") != computed_trace_digest:
        problems.append("ANTI_FALSE_GREEN_TRACE_DIGEST_MISMATCH")
    if record.get("qualification_state") not in (None, QUALIFIED):
        problems.append("ANTI_FALSE_GREEN_TRACE_NOT_QUALIFIED")
    if record.get("currentness_result") not in (None, CURRENT):
        problems.append("ANTI_FALSE_GREEN_TRACE_NOT_CURRENT")
    for key in (
        "trace_qualification_digest",
        "trace_independence_qualification_digest",
        "trace_currentness_binding_digest",
    ):
        if not _sha(record.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_TRACE_PROOF_DIGEST_INVALID:{key}")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": record.get("trace_qualification_digest"),
                "subject_id": record.get("trace_id"),
                "subject_content_digest": computed_trace_digest,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": record.get("trace_independence_qualification_digest"),
                "subject_identity_id": record.get("independence_proof_producer_id"),
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": record.get("trace_currentness_binding_digest"),
                "source_id": record.get("trace_id"),
                "source_digest": computed_trace_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix=f"ANTI_FALSE_GREEN_TRACE_PROOF:{record.get('trace_id')}",
        problems=problems,
    )

    kinds, kind_problems = _unique_strings(record.get("decision_input_kinds"))
    problems.extend(f"ANTI_FALSE_GREEN_TRACE_INPUT:{item}" for item in kind_problems)
    for kind in sorted(set(kinds).intersection(HARD_FORBIDDEN_INPUT_KINDS)):
        problems.append(f"ANTI_FALSE_GREEN_FORBIDDEN_RUNTIME_INPUT:{kind}")
    if record.get("endpoint_derivation_source") == "DIAGNOSTIC_STRING":
        problems.append("ANTI_FALSE_GREEN_DIAGNOSTIC_STRING_ENDPOINT_DERIVATION")
    if record.get("independence_proof_producer_id") in {
        record.get("candidate_identity_id"),
        record.get("decision_subject_id"),
        record.get("independence_proof_subject_id"),
    }:
        problems.append("ANTI_FALSE_GREEN_SELF_CREATED_INDEPENDENCE_PROOF")
    refs, ref_problems = _unique_strings(record.get("runtime_artifact_refs"))
    problems.extend(f"ANTI_FALSE_GREEN_RUNTIME_REF:{item}" for item in ref_problems)
    for ref in refs:
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
    problems = sorted(set(problems))
    return {
        "state": "ANTI_FALSE_GREEN_RUNTIME_TRACE_CLEAR" if not problems else "ANTI_FALSE_GREEN_RUNTIME_TRACE_REJECTED",
        "qualified": not problems,
        "trace_digest": computed_trace_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def canonical_gate_content_digest(descriptor: Mapping[str, Any]) -> str:
    return digest(
        {
            "gate_id": descriptor.get("gate_id"),
            "gate_implementation_digest": descriptor.get("gate_implementation_digest"),
            "gate_authority_identity_id": descriptor.get("gate_authority_identity_id"),
        }
    )


def canonical_allowlist_content_digest(allowlist: Mapping[str, Any]) -> str:
    entries = allowlist.get("entries")
    return digest(
        {
            "allowlist_id": allowlist.get("allowlist_id"),
            "entries": sorted(entries) if isinstance(entries, list) else [],
            "permits_hard_prohibition_bypass": allowlist.get("permits_hard_prohibition_bypass") is True,
        }
    )


def validate_anti_false_green_gate(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    problems: list[str] = []
    descriptor = bundle.get("gate_descriptor")
    if not isinstance(descriptor, Mapping):
        descriptor = {}
        problems.append("ANTI_FALSE_GREEN_GATE_DESCRIPTOR_REQUIRED")
    gate_content_digest = canonical_gate_content_digest(descriptor)
    for key in (
        "gate_id",
        "gate_authority_identity_id",
        "gate_implementation_digest",
        "gate_content_digest",
        "gate_qualification_digest",
        "gate_independence_qualification_digest",
        "gate_currentness_binding_digest",
    ):
        if not _nonempty(descriptor.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_GATE_FIELD_REQUIRED:{key}")
    for key in (
        "gate_implementation_digest",
        "gate_content_digest",
        "gate_qualification_digest",
        "gate_independence_qualification_digest",
        "gate_currentness_binding_digest",
    ):
        if not _sha(descriptor.get(key)):
            problems.append(f"ANTI_FALSE_GREEN_GATE_DIGEST_INVALID:{key}")
    if _sha(descriptor.get("gate_content_digest")) and descriptor.get("gate_content_digest") != gate_content_digest:
        problems.append("ANTI_FALSE_GREEN_GATE_CONTENT_DIGEST_MISMATCH")
    if descriptor.get("qualification_state") not in (None, QUALIFIED):
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_QUALIFIED")
    if descriptor.get("independence_state") not in (None, QUALIFIED):
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_INDEPENDENT")
    if descriptor.get("currentness_result") not in (None, CURRENT):
        problems.append("ANTI_FALSE_GREEN_GATE_NOT_CURRENT")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": descriptor.get("gate_qualification_digest"),
                "subject_id": descriptor.get("gate_id"),
                "subject_content_digest": gate_content_digest,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": descriptor.get("gate_independence_qualification_digest"),
                "subject_identity_id": descriptor.get("gate_authority_identity_id"),
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": descriptor.get("gate_currentness_binding_digest"),
                "source_id": descriptor.get("gate_id"),
                "source_digest": gate_content_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ANTI_FALSE_GREEN_GATE_PROOF",
        problems=problems,
    )

    sources = bundle.get("production_sources")
    if not isinstance(sources, list) or not sources:
        sources = []
        problems.append("ANTI_FALSE_GREEN_PRODUCTION_SOURCES_REQUIRED")
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            problems.append(f"ANTI_FALSE_GREEN_SOURCE_MALFORMED:{index}")
        else:
            result = scan_production_authority_source(
                source,
                proof_context=proof_context,
                trusted_boundary=trusted_boundary,
            )
            problems.extend(f"SOURCE:{index}:{item}" for item in result["problems"])

    traces = bundle.get("runtime_traces")
    if not isinstance(traces, list) or not traces:
        traces = []
        problems.append("ANTI_FALSE_GREEN_RUNTIME_TRACES_REQUIRED")
    for index, trace in enumerate(traces):
        if not isinstance(trace, Mapping):
            problems.append(f"ANTI_FALSE_GREEN_TRACE_MALFORMED:{index}")
        else:
            result = validate_runtime_authority_trace(
                trace,
                proof_context=proof_context,
                trusted_boundary=trusted_boundary,
            )
            problems.extend(f"TRACE:{index}:{item}" for item in result["problems"])

    allowlist = bundle.get("allowlist")
    if allowlist not in (None, {}):
        if not isinstance(allowlist, Mapping):
            problems.append("ANTI_FALSE_GREEN_ALLOWLIST_MALFORMED")
        else:
            entries, entry_problems = _unique_strings(allowlist.get("entries"))
            problems.extend(f"ANTI_FALSE_GREEN_ALLOWLIST:{item}" for item in entry_problems)
            allowlist_digest = canonical_allowlist_content_digest(allowlist)
            for key in (
                "allowlist_id",
                "allowlist_content_digest",
                "allowlist_qualification_digest",
                "allowlist_currentness_binding_digest",
            ):
                if not _nonempty(allowlist.get(key)):
                    problems.append(f"ANTI_FALSE_GREEN_ALLOWLIST_FIELD_REQUIRED:{key}")
            for key in (
                "allowlist_content_digest",
                "allowlist_qualification_digest",
                "allowlist_currentness_binding_digest",
            ):
                if not _sha(allowlist.get(key)):
                    problems.append(f"ANTI_FALSE_GREEN_ALLOWLIST_DIGEST_INVALID:{key}")
            if _sha(allowlist.get("allowlist_content_digest")) and allowlist.get("allowlist_content_digest") != allowlist_digest:
                problems.append("ANTI_FALSE_GREEN_ALLOWLIST_CONTENT_DIGEST_MISMATCH")
            _close(
                [
                    {
                        "kind": GOVERNED_QUALIFICATION,
                        "reference_digest": allowlist.get("allowlist_qualification_digest"),
                        "subject_id": allowlist.get("allowlist_id"),
                        "subject_content_digest": allowlist_digest,
                    },
                    {
                        "kind": CURRENTNESS_BINDING,
                        "reference_digest": allowlist.get("allowlist_currentness_binding_digest"),
                        "source_id": allowlist.get("allowlist_id"),
                        "source_digest": allowlist_digest,
                    },
                ],
                proof_context=proof_context,
                trusted_boundary=trusted_boundary,
                prefix="ANTI_FALSE_GREEN_ALLOWLIST_PROOF",
                problems=problems,
            )
            completeness = allowlist.get("completeness_qualification")
            if not isinstance(completeness, Mapping):
                problems.append("ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_REQUIRED")
            else:
                problems.extend(
                    f"ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS:{item}"
                    for item in validate_registry_completeness_qualification(completeness)
                )
                if completeness.get("subject_object_id") != allowlist.get("allowlist_id"):
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_SUBJECT_ID_MISMATCH")
                if completeness.get("subject_content_digest") != allowlist_digest:
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
                if completeness.get("actual_members") != sorted(entries):
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_ACTUAL_MEMBERS_MISMATCH")
                if completeness.get("result") != QUALIFIED:
                    problems.append("ANTI_FALSE_GREEN_ALLOWLIST_NOT_QUALIFIED")
                _close_completeness_dependencies(
                    completeness,
                    proof_context=proof_context,
                    trusted_boundary=trusted_boundary,
                    prefix="ANTI_FALSE_GREEN_ALLOWLIST_COMPLETENESS_PROOF",
                    problems=problems,
                )
            if allowlist.get("permits_hard_prohibition_bypass") is True:
                problems.append("ANTI_FALSE_GREEN_HARD_PROHIBITION_ALLOWLIST_FORBIDDEN")

    problems = sorted(set(problems))
    return {
        "state": "ANTI_FALSE_GREEN_GATE_CLEAR" if not problems else "ANTI_FALSE_GREEN_GATE_REJECTED",
        "qualified": not problems,
        "gate_content_digest": gate_content_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def canonical_case_universe_content_digest(record: Mapping[str, Any]) -> str:
    case_ids = record.get("case_ids")
    return digest(
        {
            "universe_id": record.get("universe_id"),
            "qualification_round_id": record.get("qualification_round_id"),
            "candidate_commit": record.get("candidate_commit"),
            "candidate_tree": record.get("candidate_tree"),
            "environment_digest": record.get("environment_digest"),
            "case_contract_set_digest": record.get("case_contract_set_digest"),
            "case_ids": sorted(case_ids) if isinstance(case_ids, list) else [],
        }
    )


def validate_qualification_case_universe(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
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
    if record.get("qualification_state") not in (None, QUALIFIED):
        problems.append("QUALIFICATION_CASE_UNIVERSE_NOT_QUALIFIED")
    if record.get("currentness_result") not in (None, CURRENT):
        problems.append("QUALIFICATION_CASE_UNIVERSE_NOT_CURRENT")
    case_ids, case_problems = _unique_strings(record.get("case_ids"))
    problems.extend(f"QUALIFICATION_CASE_UNIVERSE_CASES:{item}" for item in case_problems)
    if not case_ids:
        problems.append("QUALIFICATION_CASE_UNIVERSE_CASES_REQUIRED")
    case_ids = sorted(case_ids)
    content_digest = canonical_case_universe_content_digest(record)
    if record.get("content_digest") != content_digest:
        problems.append("QUALIFICATION_CASE_UNIVERSE_CONTENT_DIGEST_MISMATCH")
    for key in ("universe_qualification_digest", "universe_currentness_binding_digest"):
        if not _sha(record.get(key)):
            problems.append(f"QUALIFICATION_CASE_UNIVERSE_PROOF_DIGEST_INVALID:{key}")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": record.get("universe_qualification_digest"),
                "subject_id": record.get("universe_id"),
                "subject_content_digest": content_digest,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": record.get("universe_currentness_binding_digest"),
                "source_id": record.get("universe_id"),
                "source_digest": content_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="QUALIFICATION_CASE_UNIVERSE_PROOF",
        problems=problems,
    )
    completeness = record.get("completeness_qualification")
    if not isinstance(completeness, Mapping):
        completeness = {}
        problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_REQUIRED")
    else:
        problems.extend(
            f"QUALIFICATION_CASE_UNIVERSE_COMPLETENESS:{item}"
            for item in validate_registry_completeness_qualification(completeness)
        )
        if completeness.get("subject_object_id") != record.get("universe_id"):
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_ID_MISMATCH")
        if completeness.get("subject_content_digest") != content_digest:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
        if completeness.get("actual_members") != case_ids:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_ACTUAL_MEMBERS_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_NOT_QUALIFIED")
        _close_completeness_dependencies(
            completeness,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="QUALIFICATION_CASE_UNIVERSE_COMPLETENESS_PROOF",
            problems=problems,
        )
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
        "content_digest": content_digest,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def canonical_result_record_digest(record: Mapping[str, Any]) -> str:
    return digest(
        _without(
            record,
            "result_record_digest",
            "result_qualification_digest",
            "result_currentness_binding_digest",
        )
    )


def _validate_result_record(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
) -> list[str]:
    problems: list[str] = []
    for key in (
        "result_id",
        "qualification_round_id",
        "case_id",
        "execution_state",
        "terminal_disposition",
    ):
        if not _nonempty(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_FIELD_REQUIRED:{key}")
    for key in ("candidate_commit", "candidate_tree"):
        if not _git_sha(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "case_contract_digest"):
        if not _sha(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_DIGEST_INVALID:{key}")
    qualification_basis, basis_problems = _unique_strings(record.get("qualification_basis_digests"))
    problems.extend(f"QUALIFICATION_RESULT_qualification_basis_digests:{item}" for item in basis_problems)
    if not qualification_basis or not all(_sha(value) for value in qualification_basis):
        problems.append("QUALIFICATION_RESULT_DIGEST_SET_INVALID:qualification_basis_digests")
    evidence_basis, evidence_problems = _unique_strings(record.get("evidence_basis_digests"))
    problems.extend(f"QUALIFICATION_RESULT_evidence_basis_digests:{item}" for item in evidence_problems)
    if not evidence_basis or not all(_sha(value) for value in evidence_basis):
        problems.append("QUALIFICATION_RESULT_DIGEST_SET_INVALID:evidence_basis_digests")
    sequence = record.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        problems.append("QUALIFICATION_RESULT_SEQUENCE_INVALID")
    prior = record.get("resolves_prior_result_digest")
    if prior not in (None, "") and not _sha(prior):
        problems.append("QUALIFICATION_RESULT_PRIOR_DIGEST_INVALID")
    computed_digest = canonical_result_record_digest(record)
    supplied_digest = record.get("result_record_digest")
    if not _sha(supplied_digest):
        problems.append("QUALIFICATION_RESULT_RECORD_DIGEST_INVALID")
    elif supplied_digest != computed_digest:
        problems.append("QUALIFICATION_RESULT_RECORD_DIGEST_MISMATCH")
    for key in ("result_qualification_digest", "result_currentness_binding_digest"):
        if not _sha(record.get(key)):
            problems.append(f"QUALIFICATION_RESULT_PROOF_DIGEST_INVALID:{key}")
    requirements: list[Mapping[str, Any]] = [
        {
            "kind": GOVERNED_QUALIFICATION,
            "reference_digest": record.get("result_qualification_digest"),
            "subject_id": record.get("result_id"),
            "subject_content_digest": computed_digest,
        },
        {
            "kind": CURRENTNESS_BINDING,
            "reference_digest": record.get("result_currentness_binding_digest"),
            "source_id": record.get("result_id"),
            "source_digest": computed_digest,
        },
    ]
    requirements.extend(
        {"kind": GOVERNED_QUALIFICATION, "reference_digest": ref}
        for ref in qualification_basis
        if _sha(ref)
    )
    _close(
        requirements,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix=f"QUALIFICATION_RESULT_PROOF:{record.get('result_id')}",
        problems=problems,
    )
    return sorted(set(problems))


def canonical_summary_compiler_content_digest(compiler: Mapping[str, Any]) -> str:
    return digest(
        {
            "compiler_id": compiler.get("compiler_id"),
            "compiler_digest": compiler.get("compiler_digest"),
            "compiler_authority_identity_id": compiler.get("compiler_authority_identity_id"),
        }
    )


def compile_qualification_summary(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    problems: list[str] = []
    compiler = bundle.get("summary_compiler")
    if not isinstance(compiler, Mapping):
        compiler = {}
        problems.append("QUALIFICATION_SUMMARY_COMPILER_REQUIRED")
    compiler_content = canonical_summary_compiler_content_digest(compiler)
    for key in (
        "compiler_id",
        "compiler_authority_identity_id",
        "compiler_digest",
        "compiler_content_digest",
        "compiler_qualification_digest",
        "compiler_independence_qualification_digest",
        "compiler_currentness_binding_digest",
    ):
        if not _nonempty(compiler.get(key)):
            problems.append(f"QUALIFICATION_SUMMARY_COMPILER_FIELD_REQUIRED:{key}")
    for key in (
        "compiler_digest",
        "compiler_content_digest",
        "compiler_qualification_digest",
        "compiler_independence_qualification_digest",
        "compiler_currentness_binding_digest",
    ):
        if not _sha(compiler.get(key)):
            problems.append(f"QUALIFICATION_SUMMARY_COMPILER_DIGEST_INVALID:{key}")
    if _sha(compiler.get("compiler_content_digest")) and compiler.get("compiler_content_digest") != compiler_content:
        problems.append("QUALIFICATION_SUMMARY_COMPILER_CONTENT_DIGEST_MISMATCH")
    if compiler.get("qualification_state") not in (None, QUALIFIED):
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_QUALIFIED")
    if compiler.get("independence_state") not in (None, QUALIFIED):
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_INDEPENDENT")
    if compiler.get("currentness_result") not in (None, CURRENT):
        problems.append("QUALIFICATION_SUMMARY_COMPILER_NOT_CURRENT")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": compiler.get("compiler_qualification_digest"),
                "subject_id": compiler.get("compiler_id"),
                "subject_content_digest": compiler_content,
            },
            {
                "kind": INDEPENDENCE_QUALIFICATION,
                "reference_digest": compiler.get("compiler_independence_qualification_digest"),
                "subject_identity_id": compiler.get("compiler_authority_identity_id"),
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": compiler.get("compiler_currentness_binding_digest"),
                "source_id": compiler.get("compiler_id"),
                "source_digest": compiler_content,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="QUALIFICATION_SUMMARY_COMPILER_PROOF",
        problems=problems,
    )

    universe_record = bundle.get("case_universe")
    universe_record = universe_record if isinstance(universe_record, Mapping) else {}
    universe = validate_qualification_case_universe(
        universe_record,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    )
    problems.extend(f"QUALIFICATION_SUMMARY_UNIVERSE:{item}" for item in universe["problems"])
    target_round = bundle.get("qualification_round_id")
    if target_round != universe.get("qualification_round_id"):
        problems.append("QUALIFICATION_SUMMARY_ROUND_MISMATCH")
    records = bundle.get("result_records")
    if not isinstance(records, list):
        records = []
        problems.append("QUALIFICATION_SUMMARY_RESULTS_REQUIRED")

    all_by_digest: dict[str, Mapping[str, Any]] = {}
    current_by_case: dict[str, Mapping[str, Any]] = {}
    invalid_current_cases: set[str] = set()
    seen_ids: set[str] = set()
    previous_sequence = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            problems.append(f"QUALIFICATION_RESULT_MALFORMED:{index}")
            continue
        issues = _validate_result_record(
            record,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
        )
        problems.extend(f"RESULT:{index}:{issue}" for issue in issues)
        result_id = record.get("result_id")
        case_id = record.get("case_id")
        if _nonempty(result_id):
            if result_id in seen_ids:
                problems.append(f"QUALIFICATION_RESULT_ID_DUPLICATE:{result_id}")
            seen_ids.add(result_id)
        sequence = record.get("sequence")
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            if sequence <= previous_sequence:
                problems.append("QUALIFICATION_RESULT_HISTORY_SEQUENCE_NOT_MONOTONIC")
            previous_sequence = max(previous_sequence, sequence)
        record_digest = record.get("result_record_digest")
        if _sha(record_digest):
            if record_digest in all_by_digest:
                problems.append(f"QUALIFICATION_RESULT_DIGEST_DUPLICATE:{record_digest}")
            all_by_digest[record_digest] = record
        prior = record.get("resolves_prior_result_digest")
        if _sha(prior):
            if prior not in all_by_digest:
                problems.append(f"QUALIFICATION_RESULT_PRIOR_NOT_PRESERVED:{result_id}")
            else:
                previous = all_by_digest[prior]
                if previous.get("case_id") != case_id:
                    problems.append(f"QUALIFICATION_RESULT_PRIOR_CASE_MISMATCH:{result_id}")
                if previous.get("qualification_round_id") == record.get("qualification_round_id"):
                    problems.append(f"QUALIFICATION_RESULT_SAME_ROUND_REWRITE_FORBIDDEN:{result_id}")
        if record.get("qualification_round_id") == target_round and _nonempty(case_id):
            if issues:
                invalid_current_cases.add(case_id)
            if case_id in current_by_case:
                problems.append(f"QUALIFICATION_SUMMARY_MULTIPLE_RESULTS_SAME_ROUND:{case_id}")
            else:
                current_by_case[case_id] = record

    expected = set(universe.get("case_ids", []))
    observed = set(current_by_case)
    for case_id in sorted(expected - observed):
        problems.append(f"QUALIFICATION_SUMMARY_CASE_RESULT_MISSING:{case_id}")
    for case_id in sorted(observed - expected):
        problems.append(f"QUALIFICATION_SUMMARY_CASE_OUTSIDE_UNIVERSE:{case_id}")

    pass_cases: list[str] = []
    nonpass: dict[str, str] = {}
    for case_id in sorted(expected):
        record = current_by_case.get(case_id)
        if record is None:
            nonpass[case_id] = "MISSING"
            continue
        exact = (
            record.get("candidate_commit") == universe.get("candidate_commit")
            and record.get("candidate_tree") == universe.get("candidate_tree")
            and record.get("environment_digest") == universe.get("environment_digest")
        )
        eligible = (
            case_id not in invalid_current_cases
            and record.get("execution_state") == "EXECUTED"
            and record.get("terminal_disposition") == "PASS"
            and record.get("binding_valid") is True
            and exact
        )
        if eligible:
            pass_cases.append(case_id)
        else:
            nonpass[case_id] = str(
                record.get("terminal_disposition")
                or record.get("execution_state")
                or "INVALID"
            )
            if record.get("terminal_disposition") == "PASS" and case_id in invalid_current_cases:
                problems.append(f"QUALIFICATION_SUMMARY_INVALID_RECORD_PASS_REJECTED:{case_id}")
            if record.get("terminal_disposition") == "PASS" and not exact:
                problems.append(f"QUALIFICATION_SUMMARY_WRONG_BINDING_PASS_REJECTED:{case_id}")

    material = {
        "qualification_round_id": target_round,
        "case_universe_content_digest": universe.get("content_digest"),
        "candidate_commit": universe.get("candidate_commit"),
        "candidate_tree": universe.get("candidate_tree"),
        "environment_digest": universe.get("environment_digest"),
        "pass_cases": pass_cases,
        "nonpass": nonpass,
        "result_record_digests": sorted(
            record.get("result_record_digest")
            for record in current_by_case.values()
            if _sha(record.get("result_record_digest"))
        ),
        "compiler_content_digest": compiler_content,
        "compiler_qualification_digest": compiler.get("compiler_qualification_digest"),
    }
    problems = sorted(set(problems))
    return {
        "state": "QUALIFICATION_SUMMARY_COMPILED" if not problems else "QUALIFICATION_SUMMARY_INVALID",
        "qualified": not problems,
        "qualification_round_id": target_round,
        "case_count": len(expected),
        "pass_count": len(pass_cases),
        "pass_cases": pass_cases,
        "nonpass": nonpass,
        "summary_digest": digest(material),
        "summary_binding_material": material,
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
