from __future__ import annotations

import copy
import hashlib
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_qualification_integrity import (
    compile_qualification_summary,
    scan_production_authority_source,
    validate_anti_false_green_gate,
    validate_qualification_case_universe,
    validate_runtime_authority_trace,
)

Q = "a" * 64
ENV = "b" * 64
COMMIT = "1" * 40
TREE = "2" * 40


def seal(record: dict, field: str) -> dict:
    material = dict(record); material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str) -> dict:
    r = {
        "currentness_rule_id": "CURRENT-RULE",
        "source_object_id": source_id,
        "source_version_or_sequence": "1",
        "source_digest": source_digest,
        "verifier_qualification_digest": Q,
        "result": CURRENT,
        "observed_at_sequence": 1,
        "binding_digest": "",
    }
    return seal(r, "binding_digest")


def completeness(subject_id: str, subject_digest: str, cases: list[str]) -> dict:
    cases = sorted(cases)
    graph = {
        "nodes": [
            {"node_id": subject_id, "omission_sensitive": True},
            {
                "node_id": "ROOT-CASE-CONTRACTS",
                "omission_sensitive": False,
                "root_kind": "NORMATIVE_ARTIFACT_BYTES_STRUCTURE",
                "source_surface_digest": "3" * 64,
            },
        ],
        "edges": [{"from": subject_id, "to": "ROOT-CASE-CONTRACTS"}],
    }
    r = {
        "subject_object_id": subject_id,
        "subject_content_digest": subject_digest,
        "expected_member_set_digest": digest(cases),
        "actual_member_set_digest": digest(cases),
        "set_equality_proof_digest": digest({"expected": cases, "actual": cases}),
        "verifier_qualification_digest": Q,
        "expected_members": cases,
        "actual_members": cases,
        "completeness_derivation_graph": graph,
        "derivation_mechanism_qualification_digests": ["4" * 64],
        "derivation_authority_independence_digests": ["5" * 64],
        "source_surface_digests": ["3" * 64],
        "currentness_bindings": [currentness(subject_id, subject_digest)],
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(r, "qualification_digest")


def universe(round_id: str = "ROUND-1", cases: list[str] | None = None) -> dict:
    cases = sorted(cases or ["CASE-A", "CASE-B"])
    r = {
        "universe_id": f"UNIVERSE-{round_id}",
        "qualification_round_id": round_id,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "case_contract_set_digest": "6" * 64,
        "case_ids": cases,
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
        "content_digest": "",
    }
    material = dict(r); material.pop("content_digest")
    r["content_digest"] = digest(material)
    r["completeness_qualification"] = completeness(r["universe_id"], r["content_digest"], cases)
    return r


def result_record(case_id: str, seq: int, disposition: str, *, round_id: str = "ROUND-1", execution: str = "EXECUTED", prior: str | None = None) -> dict:
    r = {
        "result_id": f"RESULT-{round_id}-{case_id}-{seq}",
        "qualification_round_id": round_id,
        "case_id": case_id,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "case_contract_digest": "7" * 64,
        "execution_state": execution,
        "terminal_disposition": disposition,
        "binding_valid": True,
        "qualification_basis_digests": ["8" * 64],
        "evidence_basis_digests": ["9" * 64],
        "sequence": seq,
        "resolves_prior_result_digest": prior,
        "result_record_digest": "",
    }
    return seal(r, "result_record_digest")


def compiler() -> dict:
    return {
        "compiler_id": "SUMMARY-COMPILER",
        "compiler_digest": "c" * 64,
        "compiler_qualification_digest": "d" * 64,
        "qualification_state": QUALIFIED,
        "independence_state": QUALIFIED,
        "currentness_result": CURRENT,
    }


def clean_source(text: str = "def decide(value):\n    return value\n") -> dict:
    return {
        "artifact_id": "governance/runtime.py",
        "artifact_role": "PRODUCTION_AUTHORITY",
        "source_text": text,
        "content_digest": hashlib.sha256(text.encode()).hexdigest(),
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
    }


def clean_trace() -> dict:
    r = {
        "trace_id": "TRACE-1",
        "candidate_identity_id": "CANDIDATE",
        "decision_subject_id": "SUBJECT",
        "endpoint_derivation_source": "QUALIFIED_ENDPOINT_PROJECTOR",
        "independence_proof_subject_id": "INDEPENDENCE-SUBJECT",
        "independence_proof_producer_id": "INDEPENDENT-VERIFIER",
        "decision_input_kinds": ["NORMALIZED_PREDICATE_EVALUATIONS", "CURRENT_REGISTRY_DIGESTS"],
        "runtime_artifact_refs": ["governance-runtime/runtime.py"],
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
        "trace_digest": "",
    }
    return seal(r, "trace_digest")


def gate_bundle() -> dict:
    return {
        "gate_descriptor": {
            "gate_id": "ANTI-FALSE-GREEN-GATE",
            "gate_implementation_digest": "e" * 64,
            "gate_qualification_digest": "f" * 64,
            "qualification_state": QUALIFIED,
            "independence_state": QUALIFIED,
            "currentness_result": CURRENT,
        },
        "production_sources": [clean_source()],
        "runtime_traces": [clean_trace()],
    }


class AntiFalseGreenTests(unittest.TestCase):
    def test_clean_source_and_trace_pass(self):
        r = validate_anti_false_green_gate(gate_bundle())
        self.assertTrue(r["qualified"], r["problems"])

    def test_wdpc_literal_in_production_rejected(self):
        s = clean_source("def decide():\n    return 'WDPC-999'\n")
        r = scan_production_authority_source(s)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_WDPC_LITERAL_IN_PRODUCTION", r["problems"])

    def test_fixture_branch_identifier_rejected(self):
        s = clean_source("def decide(fixture_branch_id):\n    return fixture_branch_id\n")
        r = scan_production_authority_source(s)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_FIXTURE_BRANCH_IDENTIFIER", r["problems"])

    def test_test_module_import_rejected(self):
        s = clean_source("import testing\ndef decide():\n    return 1\n")
        r = scan_production_authority_source(s)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_RUNTIME_TEST_IMPORT_COUPLING", r["problems"])

    def test_expected_endpoint_runtime_input_rejected(self):
        t = clean_trace(); t["decision_input_kinds"].append("TEST_EXPECTED_ENDPOINT"); seal(t, "trace_digest")
        r = validate_runtime_authority_trace(t)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_FORBIDDEN_RUNTIME_INPUT:TEST_EXPECTED_ENDPOINT", r["problems"])

    def test_diagnostic_string_endpoint_derivation_rejected(self):
        t = clean_trace(); t["endpoint_derivation_source"] = "DIAGNOSTIC_STRING"; seal(t, "trace_digest")
        r = validate_runtime_authority_trace(t)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_DIAGNOSTIC_STRING_ENDPOINT_DERIVATION", r["problems"])

    def test_candidate_self_created_independence_rejected(self):
        t = clean_trace(); t["independence_proof_producer_id"] = "CANDIDATE"; seal(t, "trace_digest")
        r = validate_runtime_authority_trace(t)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_SELF_CREATED_INDEPENDENCE_PROOF", r["problems"])

    def test_runtime_test_artifact_coupling_rejected(self):
        t = clean_trace(); t["runtime_artifact_refs"] = ["testing/fixture.py"]; seal(t, "trace_digest")
        r = validate_runtime_authority_trace(t)
        self.assertFalse(r["qualified"]); self.assertTrue(any("RUNTIME_TEST_ARTIFACT_COUPLING" in p for p in r["problems"]))

    def test_unqualified_gate_rejected(self):
        b = gate_bundle(); b["gate_descriptor"]["qualification_state"] = "INVALID"
        r = validate_anti_false_green_gate(b)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_GATE_NOT_QUALIFIED", r["problems"])

    def test_allowlist_cannot_bypass_hard_prohibition(self):
        b = gate_bundle(); b["allowlist"] = {"entries": [], "permits_hard_prohibition_bypass": True}
        r = validate_anti_false_green_gate(b)
        self.assertFalse(r["qualified"]); self.assertIn("ANTI_FALSE_GREEN_HARD_PROHIBITION_ALLOWLIST_FORBIDDEN", r["problems"])


class ResultAccountingTests(unittest.TestCase):
    def test_case_universe_positive(self):
        r = validate_qualification_case_universe(universe())
        self.assertTrue(r["qualified"], r["problems"])

    def test_case_universe_completeness_mismatch_blocks(self):
        u = universe(); u["completeness_qualification"]["expected_members"] = ["CASE-A"]
        r = validate_qualification_case_universe(u)
        self.assertFalse(r["qualified"])
        self.assertTrue(any("COMPLETENESS" in p for p in r["problems"]))

    def test_only_executed_terminal_pass_counts(self):
        records = [result_record("CASE-A", 1, "PASS"), result_record("CASE-B", 2, "FAIL_CODE_DEFECT")]
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertTrue(r["qualified"], r["problems"]); self.assertEqual(1, r["pass_count"]); self.assertEqual(["CASE-A"], r["pass_cases"])

    def test_blocked_or_not_executed_never_counts_pass(self):
        records = [result_record("CASE-A", 1, "BLOCKED", execution="NOT_EXECUTED"), result_record("CASE-B", 2, "PASS", execution="NOT_EXECUTED")]
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertEqual(0, r["pass_count"])

    def test_wrong_candidate_pass_rejected(self):
        a = result_record("CASE-A", 1, "PASS"); a["candidate_commit"] = "9" * 40; seal(a, "result_record_digest")
        records = [a, result_record("CASE-B", 2, "FAIL_CODE_DEFECT")]
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertEqual(0, r["pass_count"]); self.assertIn("QUALIFICATION_SUMMARY_WRONG_BINDING_PASS_REJECTED:CASE-A", r["problems"])

    def test_invalid_result_record_cannot_count_pass(self):
        a = result_record("CASE-A", 1, "PASS"); a["result_record_digest"] = "0" * 64
        records = [a, result_record("CASE-B", 2, "FAIL_CODE_DEFECT")]
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertEqual(0, r["pass_count"])

    def test_missing_case_result_blocks_summary(self):
        records = [result_record("CASE-A", 1, "PASS")]
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertFalse(r["qualified"]); self.assertIn("QUALIFICATION_SUMMARY_CASE_RESULT_MISSING:CASE-B", r["problems"])

    def test_later_resolution_does_not_rewrite_prior_round_pass_count(self):
        old = result_record("CASE-A", 1, "UNRESOLVED", execution="NOT_EXECUTED")
        old_b = result_record("CASE-B", 2, "FAIL_CODE_DEFECT")
        later = result_record("CASE-A", 3, "PASS", round_id="ROUND-2", prior=old["result_record_digest"])
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe("ROUND-1"), "qualification_round_id": "ROUND-1", "result_records": [old, old_b, later]})
        self.assertEqual(0, r["pass_count"]); self.assertEqual("UNRESOLVED", r["nonpass"]["CASE-A"])

    def test_same_round_resolution_rewrite_forbidden(self):
        old = result_record("CASE-A", 1, "UNRESOLVED", execution="NOT_EXECUTED")
        later = result_record("CASE-A", 2, "PASS", prior=old["result_record_digest"])
        b = result_record("CASE-B", 3, "FAIL_CODE_DEFECT")
        r = compile_qualification_summary({"summary_compiler": compiler(), "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": [old, later, b]})
        self.assertFalse(r["qualified"]); self.assertTrue(any("SAME_ROUND_REWRITE_FORBIDDEN" in p for p in r["problems"]))

    def test_stale_summary_compiler_blocks(self):
        c = compiler(); c["currentness_result"] = "STALE"
        records = [result_record("CASE-A", 1, "PASS"), result_record("CASE-B", 2, "FAIL_CODE_DEFECT")]
        r = compile_qualification_summary({"summary_compiler": c, "case_universe": universe(), "qualification_round_id": "ROUND-1", "result_records": records})
        self.assertFalse(r["qualified"]); self.assertIn("QUALIFICATION_SUMMARY_COMPILER_NOT_CURRENT", r["problems"])


if __name__ == "__main__":
    unittest.main()
