"""Fail-closed integrity checks for EXP-M falsification mechanisms.

This checker treats attack tests themselves as a governed surface. It rejects
simulated outcome shortcuts and requires each authoritative CA-1..CA-10 case to
invoke the real mechanism it claims to falsify.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = "governance-runtime/reviewer_exp_m_r2e_mechanism_suite.py"
RUNNER_PATH = "governance-runtime/run_reviewer_compound_attacks.py"
SELF_FALSIFY_PATH = "governance-runtime/self_falsify_exp_m.py"
MUTATION_PATH = "governance-runtime/run_exp_m_mutations.py"
OUT = ROOT / "experiments/governed-platform/EXP-M-R2E-TEST-INTEGRITY-RESULTS.json"

FORBIDDEN_SHORTCUT_TOKENS = (
    "simulate_",
    "force_",
    "mock_",
    "with_missing_r5_protocol_for_test",
)

REQUIRED_CALLS = {
    "test_ca1_real_forged_context_reaches_production_authority_check": {"evaluate_admissibility"},
    "test_ca2_real_mismatched_evidence_token_reaches_cas_verifier": {"commit_with_verdict"},
    "test_ca3_real_fabricated_delivery_commit_reaches_authority_check": {"validate_wire_delivery"},
    "test_ca4_real_forged_retrieval_and_delivery_bytes_reach_validators": {"validate_retrieval", "validate_wire_delivery"},
    "test_ca5_real_archive_and_schedule_inputs_reach_production_validators": {"materialize_entries", "validate_capability"},
    "test_ca6_real_unauthorized_plan_reaches_authority_validator": {"validate_capability"},
    "test_ca7_real_deleted_indexed_artifact_reaches_unmodified_prior_verifier": {"_synthetic_commit", "verify_prior_evidence_index"},
    "test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier": {"_synthetic_commit", "verify_reviewer_suite_frozen"},
    "test_ca9_real_caller_pass_reaches_derived_disposition": {"evaluate_admissibility"},
    "test_ca10_real_protocol_unavailable_state_reaches_production_validator": {"validate_capability"},
}


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_text(commit: str, path: str) -> str:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT, text=True)


def _call_name(node: ast.Call) -> str:
    fn = node.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return ""


def _shortcut_references(source: str) -> list[str]:
    """Return executable identifier/call references to forbidden shortcut APIs.

    String literals and documentation text do not count as executable use.
    """
    tree = ast.parse(source, filename=SUITE_PATH)
    findings: set[str] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Call):
            names.append(_call_name(node))
            for keyword in node.keywords:
                if keyword.arg:
                    names.append(keyword.arg)
        elif isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        for name in names:
            if not name:
                continue
            if (
                name.startswith("simulate_")
                or name.startswith("force_")
                or name.startswith("mock_")
                or name == "with_missing_r5_protocol_for_test"
            ):
                findings.add(name)
    return sorted(findings)


def _hardcoded_self_falsification_outcomes(source: str) -> list[str]:
    tree = ast.parse(source, filename=SELF_FALSIFY_PATH)
    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _call_name(node) != "case":
            continue
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, bool):
            case_id = "unknown"
            if node.args and isinstance(node.args[0], ast.Constant):
                case_id = str(node.args[0].value)
            findings.append(case_id)
    return sorted(findings)


def _hardcoded_mutation_outcomes(source: str) -> list[str]:
    tree = ast.parse(source, filename=MUTATION_PATH)
    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        pairs = {
            key.value: value
            for key, value in zip(node.keys, node.values)
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        mutation_id = pairs.get("id")
        label = mutation_id.value if isinstance(mutation_id, ast.Constant) else "unknown"
        killed = pairs.get("killed")
        if isinstance(killed, ast.Constant) and isinstance(killed.value, bool):
            findings.append(f"{label}:killed={killed.value}")
        actual = pairs.get("actual")
        if isinstance(actual, ast.Constant) and actual.value in {"REJECT", "PASS"}:
            findings.append(f"{label}:actual={actual.value}")
    return sorted(findings)


def _method_calls(source: str) -> dict[str, set[str]]:
    tree = ast.parse(source, filename=SUITE_PATH)
    found: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_ca"):
            found[node.name] = {
                _call_name(call)
                for call in ast.walk(node)
                if isinstance(call, ast.Call) and _call_name(call)
            }
    return found


def run() -> dict:
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    suite_source = _git_text(source_commit, SUITE_PATH)
    runner_source = _git_text(source_commit, RUNNER_PATH)
    self_falsify_source = _git_text(source_commit, SELF_FALSIFY_PATH)
    mutation_source = _git_text(source_commit, MUTATION_PATH)

    findings: list[str] = []

    shortcut_refs = _shortcut_references(suite_source)
    for name in shortcut_refs:
        findings.append(f"authoritative_suite_shortcut_reference:{name}")

    calls = _method_calls(suite_source)
    if set(calls) != set(REQUIRED_CALLS):
        findings.append("authoritative_ca_method_set_mismatch")
    missing_calls: dict[str, list[str]] = {}
    for method, required in REQUIRED_CALLS.items():
        absent = sorted(required - calls.get(method, set()))
        if absent:
            missing_calls[method] = absent
            findings.append(f"authoritative_case_missing_real_mechanism_call:{method}")

    if "reviewer_exp_m_r2e_mechanism_suite" not in runner_source:
        findings.append("compound_runner_not_using_mechanism_suite")
    if "reviewer_exp_m_r2e_compound_suite import CompoundAttackSuite" in runner_source:
        findings.append("legacy_simulated_suite_still_authoritative")
    if '"schema": "EXP-M-R2E-COMPOUND/v3"' not in runner_source:
        findings.append("compound_schema_v3_missing")

    for token in ("simulate_", "force_", "mock_"):
        if token in self_falsify_source:
            findings.append(f"self_falsification_shortcut_token:{token}")
        if token in mutation_source:
            findings.append(f"mutation_harness_shortcut_token:{token}")

    hardcoded_self = _hardcoded_self_falsification_outcomes(self_falsify_source)
    for case_id in hardcoded_self:
        findings.append(f"self_falsification_hardcoded_outcome:{case_id}")

    hardcoded_mutations = _hardcoded_mutation_outcomes(mutation_source)
    for mutation_id in hardcoded_mutations:
        findings.append(f"mutation_harness_hardcoded_outcome:{mutation_id}")

    self_requirements = (
        'EXP-M-R2E-COMPOUND-RESULTS.json',
        'compound_execution.get("source_commit")',
        'compound_execution.get("source_tree")',
        'compound.get("survivor_count") != 0',
        'compound.get("all_rejected") is not True',
    )
    for marker in self_requirements:
        if marker not in self_falsify_source:
            findings.append("self_falsification_compound_binding_missing:" + marker)

    mutation_requirements = (
        "isolated_mutant_result",
        "_mutated_evaluate",
        "production._predicate_validators",
        "subprocess.run",
        "target_flipped",
        "normal_result",
    )
    for marker in mutation_requirements:
        if marker not in mutation_source:
            findings.append("mutation_harness_real_path_marker_missing:" + marker)

    payload = {
        "schema": "EXP-M-R2E-TEST-INTEGRITY/v1",
        "execution": {
            "source_commit": source_commit,
            "source_tree": source_tree,
            "utc": datetime.now(timezone.utc).isoformat(),
            "command": "python governance-runtime/verify_exp_m_test_integrity.py",
            "interpreter": sys.executable,
        },
        "authoritative_suite": SUITE_PATH,
        "case_count": len(calls),
        "required_case_count": len(REQUIRED_CALLS),
        "case_calls": {name: sorted(values) for name, values in sorted(calls.items())},
        "missing_required_calls": missing_calls,
        "hardcoded_self_falsification_outcomes": hardcoded_self,
        "hardcoded_mutation_outcomes": hardcoded_mutations,
        "forbidden_shortcut_tokens": list(FORBIDDEN_SHORTCUT_TOKENS),
        "executable_shortcut_references": shortcut_refs,
        "findings": findings,
        "all_passed": not findings,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }
    return payload


def main() -> int:
    payload = run()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    OUT.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
