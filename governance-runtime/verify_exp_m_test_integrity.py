"""Fail-closed integrity checks for EXP-M falsification mechanisms.

This checker treats attack tests themselves as a governed surface. It rejects
simulated outcome shortcuts and requires each authoritative CA-1..CA-10 case to
invoke the real mechanism it claims to falsify.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from verify_exp_m_prior_evidence import verify_prior_evidence_index
from verify_exp_m_sep_sequence import REVIEWER_SUITE_ANCHORS, verify_reviewer_suite_frozen

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

EXPECTED_REVIEWER_ANCHORS = (
    ("governance-runtime/reviewer_exp_m_r2e_suite.py", "04913502b7ea1dcb11d551b2bec27c5a8d9c4a8a"),
    ("governance-runtime/reviewer_exp_m_r2e_authority_suite.py", "aae96510eb1ac05b45b961b62a5ea2b010ad6b32"),
    ("governance-runtime/reviewer_exp_m_r2e_compound_suite.py", "4c70788b9fc8c8ec93f5ea90bedc762c827f090a"),
    ("governance-runtime/reviewer_exp_m_r2e_mechanism_suite.py", "24415847085e4032a9892aaa8730806bd246225e"),
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

REQUIRED_ASSERTION_CONTRACTS = {
    "test_ca1_real_forged_context_reaches_production_authority_check": {
        "assert_calls": {"assertFalse", "assertIn"},
        "symbols": {"verdict", "admissible", "reasons"},
        "strings": {"expectation_authority_invalid"},
    },
    "test_ca2_real_mismatched_evidence_token_reaches_cas_verifier": {
        "assert_calls": {"assertTrue", "assertIn"},
        "symbols": {"cp", "void", "reasons"},
        "strings": {"evidence_token_mismatch"},
    },
    "test_ca3_real_fabricated_delivery_commit_reaches_authority_check": {
        "assert_calls": {"assertFalse", "assertIn"},
        "symbols": {"ok", "reasons"},
        "strings": {"authority_reviewed_commit_mismatch"},
    },
    "test_ca4_real_forged_retrieval_and_delivery_bytes_reach_validators": {
        "assert_calls": {"assertFalse"},
        "symbols": {"retrieval_ok", "delivery_ok"},
        "strings": set(),
    },
    "test_ca5_real_archive_and_schedule_inputs_reach_production_validators": {
        "assert_calls": {"assertFalse", "assertTrue"},
        "symbols": {"mat", "success", "cap_ok", "cap_reasons"},
        "strings": {"schedule"},
    },
    "test_ca6_real_unauthorized_plan_reaches_authority_validator": {
        "assert_calls": {"assertFalse", "assertIn"},
        "symbols": {"ok", "reasons"},
        "strings": {"qualification_authority_plan_missing"},
    },
    "test_ca7_real_deleted_indexed_artifact_reaches_unmodified_prior_verifier": {
        "assert_calls": {"assertFalse", "assertIn"},
        "symbols": {"ok", "reasons"},
        "strings": {"indexed_prior_artifact_deleted_after_source_freeze"},
    },
    "test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier": {
        "assert_calls": {"assertFalse", "assertTrue"},
        "symbols": {"ok", "reasons"},
        "strings": {"reviewer_suite_hash_drift", "reviewer_suite_preregister_hash_drift"},
    },
    "test_ca9_real_caller_pass_reaches_derived_disposition": {
        "assert_calls": {"assertFalse"},
        "symbols": {"verdict", "admissible", "predicate_results"},
        "strings": set(),
    },
    "test_ca10_real_protocol_unavailable_state_reaches_production_validator": {
        "assert_calls": {"assertFalse", "assertIn"},
        "symbols": {"ok", "reasons"},
        "strings": {"r5_protocol_unavailable"},
    },
}


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_text(commit: str, path: str) -> str:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT, text=True)


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _call_name(node: ast.Call) -> str:
    fn = node.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return ""


def _shortcut_references(source: str) -> list[str]:
    """Return executable references to forbidden shortcut APIs.

    Documentation text remains ignored, but strings used by dynamic attribute
    access (for example getattr(obj, "forbidden_name")) are executable and are
    therefore inspected.
    """
    tree = ast.parse(source, filename=SUITE_PATH)
    findings: set[str] = set()
    dynamic_accessors = {"getattr", "setattr", "hasattr", "delattr"}
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Call):
            call_name = _call_name(node)
            names.append(call_name)
            for keyword in node.keywords:
                if keyword.arg:
                    names.append(keyword.arg)
            if (
                call_name in dynamic_accessors
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
            ):
                names.append(node.args[1].value)
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


def authoritative_case_contracts(source: str) -> dict[str, dict]:
    """Analyze whether each CA method both reaches its mechanism and proves rejection."""
    tree = ast.parse(source, filename=SUITE_PATH)
    found: dict[str, dict] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test_ca"):
            continue
        calls = {
            _call_name(call)
            for call in ast.walk(node)
            if isinstance(call, ast.Call) and _call_name(call)
        }
        assert_calls: set[str] = set()
        assert_symbols: set[str] = set()
        assert_strings: set[str] = set()
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            call_name = _call_name(call)
            if not call_name.startswith("assert"):
                continue
            assert_calls.add(call_name)
            for argument in list(call.args) + [kw.value for kw in call.keywords]:
                for child in ast.walk(argument):
                    if isinstance(child, ast.Name):
                        assert_symbols.add(child.id)
                    elif isinstance(child, ast.Attribute):
                        assert_symbols.add(child.attr)
                    elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                        assert_strings.add(child.value)
        required_calls = REQUIRED_CALLS.get(node.name, set())
        required_assert = REQUIRED_ASSERTION_CONTRACTS.get(node.name, {})
        missing_mechanism_calls = sorted(required_calls - calls)
        missing_assert_calls = sorted(set(required_assert.get("assert_calls", ())) - assert_calls)
        missing_assert_symbols = sorted(set(required_assert.get("symbols", ())) - assert_symbols)
        required_strings = set(required_assert.get("strings", ()))
        if node.name == "test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier":
            missing_assert_strings = [] if required_strings.intersection(assert_strings) else sorted(required_strings)
        else:
            missing_assert_strings = sorted(required_strings - assert_strings)
        valid = not (
            missing_mechanism_calls
            or missing_assert_calls
            or missing_assert_symbols
            or missing_assert_strings
        )
        found[node.name] = {
            "valid": valid,
            "calls": sorted(calls),
            "assert_calls": sorted(assert_calls),
            "assert_symbols": sorted(assert_symbols),
            "assert_strings": sorted(assert_strings),
            "missing_mechanism_calls": missing_mechanism_calls,
            "missing_assert_calls": missing_assert_calls,
            "missing_assert_symbols": missing_assert_symbols,
            "missing_assert_strings": missing_assert_strings,
        }
    return found


def _method_calls(source: str) -> dict[str, set[str]]:
    return {
        name: set(details["calls"])
        for name, details in authoritative_case_contracts(source).items()
    }


def _self_falsification_context_issues(source: str) -> list[str]:
    tree = ast.parse(source, filename=SELF_FALSIFY_PATH)
    issues: list[str] = []
    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    wrapper = functions.get("evaluate_admissibility")
    if wrapper is None:
        issues.append("evaluate_wrapper_missing")
    else:
        production_calls = [
            node for node in ast.walk(wrapper)
            if isinstance(node, ast.Call) and _call_name(node) == "_production_evaluate_admissibility"
        ]
        if len(production_calls) != 1:
            issues.append("evaluate_wrapper_production_call_count")
        else:
            call = production_calls[0]
            if len(call.args) < 2 or not isinstance(call.args[1], ast.Name) or call.args[1].id != "context":
                issues.append("evaluate_wrapper_discards_explicit_context")
    context_helper = functions.get("context_from_state")
    if context_helper is None:
        issues.append("context_helper_missing")
    else:
        calls = [
            node for node in ast.walk(context_helper)
            if isinstance(node, ast.Call) and _call_name(node) == "_unauthorized_context_from_state"
        ]
        if len(calls) != 1:
            issues.append("context_helper_not_adversarial")
    return issues


def run() -> dict:
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    suite_source = _git_text(source_commit, SUITE_PATH)
    runner_source = _git_text(source_commit, RUNNER_PATH)
    self_falsify_source = _git_text(source_commit, SELF_FALSIFY_PATH)
    mutation_source = _git_text(source_commit, MUTATION_PATH)
    sep_source = _git_text(source_commit, "governance-runtime/verify_exp_m_sep_sequence.py")
    prior_source = _git_text(source_commit, "governance-runtime/verify_exp_m_prior_evidence.py")

    findings: list[str] = []

    if tuple(REVIEWER_SUITE_ANCHORS) != EXPECTED_REVIEWER_ANCHORS:
        findings.append("reviewer_suite_anchor_set_mismatch")

    # Differential positive controls: the unmodified verifier must accept the
    # genuine frozen source before the synthetic CA-7/CA-8 attacks are allowed
    # to count as rejection evidence.
    reviewer_source_files = {
        path: hashlib.sha256(_git_bytes(source_commit, path)).hexdigest()
        for path, _ in REVIEWER_SUITE_ANCHORS
    }
    reviewer_control_ok, reviewer_control_reasons = verify_reviewer_suite_frozen(
        source_commit=source_commit,
        source_files=reviewer_source_files,
    )
    if not reviewer_control_ok:
        findings.append("reviewer_freeze_positive_control_failed")

    prior_control_ok, prior_control_reasons = verify_prior_evidence_index(
        index_commit=source_commit,
        source_commit=source_commit,
        packet_commit=source_commit,
    )
    if not prior_control_ok:
        findings.append("prior_evidence_positive_control_failed")

    if "simulate_suite_mutation" in sep_source:
        findings.append("reviewer_freeze_simulation_api_still_present")
    if "simulate_deleted_indexed_artifact" in prior_source:
        findings.append("prior_evidence_simulation_api_still_present")

    sep_tree = ast.parse(sep_source, filename="governance-runtime/verify_exp_m_sep_sequence.py")
    ambient_refs: list[str] = []
    for node in ast.walk(sep_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "verify_reviewer_suite_frozen":
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and child.id == "FREEZE_PATH":
                    ambient_refs.append("FREEZE_PATH")
                if isinstance(child, ast.Attribute) and child.attr in {"read_text", "read_bytes"}:
                    ambient_refs.append(child.attr)
    if ambient_refs:
        findings.append("reviewer_freeze_ambient_state_reference:" + ",".join(sorted(set(ambient_refs))))

    shortcut_refs = _shortcut_references(suite_source)
    for name in shortcut_refs:
        findings.append(f"authoritative_suite_shortcut_reference:{name}")

    contracts = authoritative_case_contracts(suite_source)
    calls = {name: set(details["calls"]) for name, details in contracts.items()}
    if set(calls) != set(REQUIRED_CALLS):
        findings.append("authoritative_ca_method_set_mismatch")
    missing_calls: dict[str, list[str]] = {}
    for method, required in REQUIRED_CALLS.items():
        absent = sorted(required - calls.get(method, set()))
        if absent:
            missing_calls[method] = absent
            findings.append(f"authoritative_case_missing_real_mechanism_call:{method}")
        contract = contracts.get(method)
        if contract is None or contract.get("valid") is not True:
            findings.append(f"authoritative_case_rejection_contract_invalid:{method}")

    assertionless_probe = """
class Probe:
    def test_ca1_real_forged_context_reaches_production_authority_check(self):
        evaluate_admissibility(None, None)
"""
    assertionless = authoritative_case_contracts(assertionless_probe).get(
        "test_ca1_real_forged_context_reaches_production_authority_check", {}
    )
    assertionless_probe_rejected = assertionless.get("valid") is False
    if not assertionless_probe_rejected:
        findings.append("assertionless_ca_probe_false_green")

    dynamic_shortcut_probe = """
def probe(authority):
    return getattr(authority, "with_missing_r5_protocol_for_test")()
"""
    dynamic_shortcut_probe_rejected = (
        "with_missing_r5_protocol_for_test" in _shortcut_references(dynamic_shortcut_probe)
    )
    if not dynamic_shortcut_probe_rejected:
        findings.append("dynamic_shortcut_probe_false_green")

    for issue in _self_falsification_context_issues(self_falsify_source):
        findings.append("self_falsification_context_integrity:" + issue)

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
        "expected_reviewer_anchors": [list(row) for row in EXPECTED_REVIEWER_ANCHORS],
        "observed_reviewer_anchors": [list(row) for row in REVIEWER_SUITE_ANCHORS],
        "case_count": len(calls),
        "required_case_count": len(REQUIRED_CALLS),
        "case_calls": {name: sorted(values) for name, values in sorted(calls.items())},
        "case_rejection_contracts": contracts,
        "integrity_regression_probes": {
            "assertionless_required_call_rejected": assertionless_probe_rejected,
            "dynamic_getattr_shortcut_rejected": dynamic_shortcut_probe_rejected,
            "self_falsification_context_issues": _self_falsification_context_issues(self_falsify_source),
        },
        "positive_controls": {
            "reviewer_suite_frozen": {"ok": reviewer_control_ok, "reasons": list(reviewer_control_reasons)},
            "prior_evidence_index": {"ok": prior_control_ok, "reasons": list(prior_control_reasons)},
        },
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
