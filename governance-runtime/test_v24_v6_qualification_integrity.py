from __future__ import annotations

import copy
import hashlib
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_qualification_integrity import (
    canonical_case_universe_content_digest,
    canonical_gate_content_digest,
    canonical_result_record_digest,
    canonical_summary_compiler_content_digest,
    canonical_trace_content_digest,
    compile_qualification_summary,
    scan_production_authority_source,
    validate_anti_false_green_gate,
    validate_qualification_case_universe,
    validate_runtime_authority_trace,
)
from v24_v6_test_proof_context import build_test_proof_context

ENV = "b" * 64
COMMIT = "1" * 40
TREE = "2" * 40


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str, verifier_ref: str) -> dict:
    return seal(
        {
            "currentness_rule_id": "CURRENT-RULE",
            "source_object_id": source_id,
            "source_version_or_sequence": "1",
            "source_digest": source_digest,
            "verifier_qualification_digest": verifier_ref,
            "result": CURRENT,
            "observed_at_sequence": 1,
            "binding_digest": "",
        },
        "binding_digest",
    )


def completeness(subject_id: str, subject_digest: str, members: list[str], refs: dict) -> dict:
    members = sorted(members)
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
    record = {
        "subject_object_id": subject_id,
        "subject_content_digest": subject_digest,
        "expected_member_set_digest": digest(members),
        "actual_member_set_digest": digest(members),
        "set_equality_proof_digest": digest({"expected": members, "actual": members}),
        "verifier_qualification_digest": refs["completeness_q"],
        "expected_members": members,
        "actual_members": members,
        "completeness_derivation_graph": graph,
        "derivation_mechanism_qualification_digests": [refs["completeness_q"]],
        "derivation_authority_independence_digests": [refs["completeness_i"]],
        "source_surface_digests": ["3" * 64],
        "currentness_bindings": [currentness(subject_id, subject_digest, refs["completeness_q"])],
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(record, "qualification_digest")


def clean_source(text: str = "def decide(value):\n    return value\n") -> dict:
    return {
        "artifact_id": "governance/runtime.py",
        "artifact_role": "PRODUCTION_AUTHORITY",
        "source_text": text,
        "content_digest": hashlib.sha256(text.encode()).hexdigest(),
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
    }


def clean_trace(**overrides) -> dict:
    record = {
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
    }
    record.update(overrides)
    record["trace_digest"] = canonical_trace_content_digest(record)
    return record


# Legacy label-only fixture retained for the permanent R8 RED regression.
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


def proof_closed_gate_bundle(*, source_text: str | None = None, trace_overrides: dict | None = None):
    source = clean_source(source_text or "def decide(value):\n    return value\n")
    trace = clean_trace(**(trace_overrides or {}))
    gate = {
        "gate_id": "ANTI-FALSE-GREEN-GATE",
        "gate_authority_identity_id": "ANTI-FALSE-GREEN-AUTHORITY",
        "gate_implementation_digest": "e" * 64,
        "qualification_state": QUALIFIED,
        "independence_state": QUALIFIED,
        "currentness_result": CURRENT,
    }
    gate["gate_content_digest"] = canonical_gate_content_digest(gate)
    specs = {
        "gate_q": {"kind": "QUALIFICATION", "subject_id": gate["gate_id"], "content_digest": gate["gate_content_digest"]},
        "gate_i": {"kind": "INDEPENDENCE", "subject_identity_id": gate["gate_authority_identity_id"]},
        "gate_c": {"kind": "CURRENTNESS", "source_id": gate["gate_id"], "source_digest": gate["gate_content_digest"]},
        "source_q": {"kind": "QUALIFICATION", "subject_id": source["artifact_id"], "content_digest": source["content_digest"]},
        "source_c": {"kind": "CURRENTNESS", "source_id": source["artifact_id"], "source_digest": source["content_digest"]},
        "trace_q": {"kind": "QUALIFICATION", "subject_id": trace["trace_id"], "content_digest": trace["trace_digest"]},
        "trace_i": {"kind": "INDEPENDENCE", "subject_identity_id": trace["independence_proof_producer_id"]},
        "trace_c": {"kind": "CURRENTNESS", "source_id": trace["trace_id"], "source_digest": trace["trace_digest"]},
    }
    context, boundary, refs = build_test_proof_context(specs)
    gate.update(
        {
            "gate_qualification_digest": refs["gate_q"],
            "gate_independence_qualification_digest": refs["gate_i"],
            "gate_currentness_binding_digest": refs["gate_c"],
        }
    )
    source.update(
        {
            "source_qualification_digest": refs["source_q"],
            "source_currentness_binding_digest": refs["source_c"],
        }
    )
    trace.update(
        {
            "trace_qualification_digest": refs["trace_q"],
            "trace_independence_qualification_digest": refs["trace_i"],
            "trace_currentness_binding_digest": refs["trace_c"],
        }
    )
    return {"gate_descriptor": gate, "production_sources": [source], "runtime_traces": [trace]}, context, boundary


def universe_draft(round_id: str = "ROUND-1", cases: list[str] | None = None) -> dict:
    record = {
        "universe_id": f"UNIVERSE-{round_id}",
        "qualification_round_id": round_id,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "case_contract_set_digest": "6" * 64,
        "case_ids": sorted(cases or ["CASE-A", "CASE-B"]),
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
    }
    record["content_digest"] = canonical_case_universe_content_digest(record)
    return record


def proof_closed_universe(round_id: str = "ROUND-1", cases: list[str] | None = None):
    record = universe_draft(round_id, cases)
    specs = {
        "universe_q": {"kind": "QUALIFICATION", "subject_id": record["universe_id"], "content_digest": record["content_digest"]},
        "universe_c": {"kind": "CURRENTNESS", "source_id": record["universe_id"], "source_digest": record["content_digest"]},
        "completeness_q": {"kind": "QUALIFICATION", "subject_id": "CASE-COMPLETENESS-VERIFIER", "content_digest": "4" * 64},
        "completeness_i": {"kind": "INDEPENDENCE", "subject_identity_id": "CASE-COMPLETENESS-AUTHORITY"},
    }
    context, boundary, refs = build_test_proof_context(specs)
    record["universe_qualification_digest"] = refs["universe_q"]
    record["universe_currentness_binding_digest"] = refs["universe_c"]
    record["completeness_qualification"] = completeness(record["universe_id"], record["content_digest"], record["case_ids"], refs)
    return record, context, boundary


def compiler_draft() -> dict:
    compiler = {
        "compiler_id": "SUMMARY-COMPILER",
        "compiler_authority_identity_id": "SUMMARY-COMPILER-AUTHORITY",
        "compiler_digest": "c" * 64,
        "qualification_state": QUALIFIED,
        "independence_state": QUALIFIED,
        "currentness_result": CURRENT,
    }
    compiler["compiler_content_digest"] = canonical_summary_compiler_content_digest(compiler)
    return compiler


def result_draft(
    case_id: str,
    seq: int,
    disposition: str,
    *,
    basis_ref: str,
    round_id: str = "ROUND-1",
    execution: str = "EXECUTED",
    prior: str | None = None,
) -> dict:
    record = {
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
        "qualification_basis_digests": [basis_ref],
        "evidence_basis_digests": ["9" * 64],
        "sequence": seq,
        "resolves_prior_result_digest": prior,
    }
    record["result_record_digest"] = canonical_result_record_digest(record)
    return record


def summary_fixture(
    record_specs: list[dict] | None = None,
    *,
    round_id: str = "ROUND-1",
    universe_cases: list[str] | None = None,
):
    universe = universe_draft(round_id, universe_cases)
    compiler = compiler_draft()
    base_specs = {
        "universe_q": {"kind": "QUALIFICATION", "subject_id": universe["universe_id"], "content_digest": universe["content_digest"]},
        "universe_c": {"kind": "CURRENTNESS", "source_id": universe["universe_id"], "source_digest": universe["content_digest"]},
        "completeness_q": {"kind": "QUALIFICATION", "subject_id": "CASE-COMPLETENESS-VERIFIER", "content_digest": "4" * 64},
        "completeness_i": {"kind": "INDEPENDENCE", "subject_identity_id": "CASE-COMPLETENESS-AUTHORITY"},
        "compiler_q": {"kind": "QUALIFICATION", "subject_id": compiler["compiler_id"], "content_digest": compiler["compiler_content_digest"]},
        "compiler_i": {"kind": "INDEPENDENCE", "subject_identity_id": compiler["compiler_authority_identity_id"]},
        "compiler_c": {"kind": "CURRENTNESS", "source_id": compiler["compiler_id"], "source_digest": compiler["compiler_content_digest"]},
        "basis_q": {"kind": "QUALIFICATION", "subject_id": "RESULT-BASIS", "content_digest": "8" * 64},
    }
    _, _, refs1 = build_test_proof_context(base_specs)
    specs_in = record_specs or [
        {"case_id": "CASE-A", "seq": 1, "disposition": "PASS"},
        {"case_id": "CASE-B", "seq": 2, "disposition": "FAIL_CODE_DEFECT"},
    ]
    records: list[dict] = []
    by_name: dict[str, dict] = {}
    for item in specs_in:
        prior = None
        prior_name = item.get("prior_name")
        if prior_name:
            prior = by_name[prior_name]["result_record_digest"]
        record = result_draft(
            item["case_id"],
            item["seq"],
            item["disposition"],
            basis_ref=refs1["basis_q"],
            round_id=item.get("round_id", round_id),
            execution=item.get("execution", "EXECUTED"),
            prior=prior,
        )
        records.append(record)
        by_name[item.get("name", f"R{len(records)}")] = record
    specs = dict(base_specs)
    for index, record in enumerate(records, 1):
        specs[f"result_{index}_q"] = {"kind": "QUALIFICATION", "subject_id": record["result_id"], "content_digest": record["result_record_digest"]}
        specs[f"result_{index}_c"] = {"kind": "CURRENTNESS", "source_id": record["result_id"], "source_digest": record["result_record_digest"]}
    context, boundary, refs = build_test_proof_context(specs)
    universe["universe_qualification_digest"] = refs["universe_q"]
    universe["universe_currentness_binding_digest"] = refs["universe_c"]
    universe["completeness_qualification"] = completeness(universe["universe_id"], universe["content_digest"], universe["case_ids"], refs)
    compiler.update(
        {
            "compiler_qualification_digest": refs["compiler_q"],
            "compiler_independence_qualification_digest": refs["compiler_i"],
            "compiler_currentness_binding_digest": refs["compiler_c"],
        }
    )
    for index, record in enumerate(records, 1):
        record["result_qualification_digest"] = refs[f"result_{index}_q"]
        record["result_currentness_binding_digest"] = refs[f"result_{index}_c"]
    bundle = {
        "summary_compiler": compiler,
        "case_universe": universe,
        "qualification_round_id": round_id,
        "result_records": records,
    }
    return bundle, context, boundary


class AntiFalseGreenTests(unittest.TestCase):
    def test_clean_gate_source_and_trace_pass(self):
        bundle, context, boundary = proof_closed_gate_bundle()
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(result["qualified"], result["problems"])

    def test_legacy_label_only_gate_fails(self):
        result = validate_anti_false_green_gate(gate_bundle())
        self.assertFalse(result["qualified"])
        self.assertTrue(any("GATE_PROOF" in item or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in item for item in result["problems"]))

    def test_wdpc_literal_in_production_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(source_text="def decide():\n    return 'WDPC-999'\n")
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("WDPC_LITERAL_IN_PRODUCTION" in item for item in result["problems"]))

    def test_fixture_branch_identifier_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(source_text="def decide(fixture_branch_id):\n    return fixture_branch_id\n")
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("FIXTURE_BRANCH_IDENTIFIER" in item for item in result["problems"]))

    def test_test_module_import_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(source_text="import testing\ndef decide():\n    return 1\n")
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("RUNTIME_TEST_IMPORT_COUPLING" in item for item in result["problems"]))

    def test_expected_endpoint_runtime_input_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(trace_overrides={"decision_input_kinds": ["NORMALIZED_PREDICATE_EVALUATIONS", "TEST_EXPECTED_ENDPOINT"]})
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("FORBIDDEN_RUNTIME_INPUT:TEST_EXPECTED_ENDPOINT" in item for item in result["problems"]))

    def test_candidate_self_created_independence_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(trace_overrides={"independence_proof_producer_id": "CANDIDATE"})
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("SELF_CREATED_INDEPENDENCE_PROOF" in item for item in result["problems"]))

    def test_runtime_test_artifact_coupling_rejected(self):
        bundle, context, boundary = proof_closed_gate_bundle(trace_overrides={"runtime_artifact_refs": ["testing/fixture.py"]})
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("RUNTIME_TEST_ARTIFACT_COUPLING" in item for item in result["problems"]))

    def test_unqualified_gate_rejected_even_with_valid_proofs(self):
        bundle, context, boundary = proof_closed_gate_bundle()
        bundle["gate_descriptor"]["qualification_state"] = "INVALID"
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertIn("ANTI_FALSE_GREEN_GATE_NOT_QUALIFIED", result["problems"])

    def test_source_content_substitution_reusing_old_proof_blocks(self):
        bundle, context, boundary = proof_closed_gate_bundle()
        bundle["production_sources"][0]["source_text"] = "def decide():\n    return 999\n"
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("SOURCE_DIGEST_MISMATCH" in item or "SOURCE_PROOF" in item and "SUBJECT_DIGEST_MISMATCH" in item for item in result["problems"]))

    def test_allowlist_cannot_bypass_hard_prohibition(self):
        bundle, context, boundary = proof_closed_gate_bundle()
        bundle["allowlist"] = {"entries": [], "permits_hard_prohibition_bypass": True}
        result = validate_anti_false_green_gate(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertIn("ANTI_FALSE_GREEN_HARD_PROHIBITION_ALLOWLIST_FORBIDDEN", result["problems"])


class ResultAccountingTests(unittest.TestCase):
    def test_case_universe_positive(self):
        record, context, boundary = proof_closed_universe()
        result = validate_qualification_case_universe(record, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(result["qualified"], result["problems"])

    def test_case_universe_without_proof_context_blocks(self):
        record, _, _ = proof_closed_universe()
        result = validate_qualification_case_universe(record)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("TRUSTED_PROOF_BOUNDARY_REQUIRED" in item for item in result["problems"]))

    def test_case_universe_completeness_reference_mismatch_blocks(self):
        record, context, boundary = proof_closed_universe()
        record["completeness_qualification"]["verifier_qualification_digest"] = "0" * 64
        result = validate_qualification_case_universe(record, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("COMPLETENESS_PROOF" in item and "UNRESOLVED" in item for item in result["problems"]))

    def test_only_executed_terminal_pass_counts(self):
        bundle, context, boundary = summary_fixture()
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(1, result["pass_count"])
        self.assertEqual(["CASE-A"], result["pass_cases"])

    def test_blocked_or_not_executed_never_counts_pass(self):
        specs = [
            {"case_id": "CASE-A", "seq": 1, "disposition": "BLOCKED", "execution": "NOT_EXECUTED"},
            {"case_id": "CASE-B", "seq": 2, "disposition": "PASS", "execution": "NOT_EXECUTED"},
        ]
        bundle, context, boundary = summary_fixture(specs)
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(0, result["pass_count"])

    def test_wrong_candidate_pass_rejected(self):
        bundle, context, boundary = summary_fixture()
        bundle["result_records"][0]["candidate_commit"] = "9" * 40
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertEqual(0, result["pass_count"])
        self.assertIn("QUALIFICATION_SUMMARY_WRONG_BINDING_PASS_REJECTED:CASE-A", result["problems"])

    def test_invalid_result_record_cannot_count_pass(self):
        bundle, context, boundary = summary_fixture()
        bundle["result_records"][0]["result_record_digest"] = "0" * 64
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertEqual(0, result["pass_count"])
        self.assertIn("QUALIFICATION_SUMMARY_INVALID_RECORD_PASS_REJECTED:CASE-A", result["problems"])

    def test_missing_result_qualification_cannot_count_pass(self):
        bundle, context, boundary = summary_fixture()
        bundle["result_records"][0].pop("result_qualification_digest")
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertEqual(0, result["pass_count"])
        self.assertTrue(any("QUALIFICATION_RESULT_PROOF" in item or "RESULT_PROOF_DIGEST_INVALID" in item for item in result["problems"]))

    def test_opaque_qualification_basis_cannot_count_pass(self):
        bundle, context, boundary = summary_fixture()
        bundle["result_records"][0]["qualification_basis_digests"] = ["0" * 64]
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertEqual(0, result["pass_count"])
        self.assertTrue(any("QUALIFICATION_RESULT_PROOF" in item and "UNRESOLVED" in item for item in result["problems"]))

    def test_missing_case_result_blocks_summary(self):
        bundle, context, boundary = summary_fixture(
            [{"case_id": "CASE-A", "seq": 1, "disposition": "PASS"}]
        )
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertFalse(result["qualified"])
        self.assertIn("QUALIFICATION_SUMMARY_CASE_RESULT_MISSING:CASE-B", result["problems"])

    def test_later_resolution_does_not_rewrite_prior_round_pass_count(self):
        specs = [
            {"name": "OLD-A", "case_id": "CASE-A", "seq": 1, "disposition": "UNRESOLVED", "execution": "NOT_EXECUTED", "round_id": "ROUND-1"},
            {"case_id": "CASE-B", "seq": 2, "disposition": "FAIL_CODE_DEFECT", "round_id": "ROUND-1"},
            {"case_id": "CASE-A", "seq": 3, "disposition": "PASS", "round_id": "ROUND-2", "prior_name": "OLD-A"},
        ]
        bundle, context, boundary = summary_fixture(specs, round_id="ROUND-1")
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(0, result["pass_count"])
        self.assertEqual("UNRESOLVED", result["nonpass"]["CASE-A"])

    def test_same_round_resolution_rewrite_forbidden(self):
        specs = [
            {"name": "OLD-A", "case_id": "CASE-A", "seq": 1, "disposition": "UNRESOLVED", "execution": "NOT_EXECUTED"},
            {"case_id": "CASE-A", "seq": 2, "disposition": "PASS", "prior_name": "OLD-A"},
            {"case_id": "CASE-B", "seq": 3, "disposition": "FAIL_CODE_DEFECT"},
        ]
        bundle, context, boundary = summary_fixture(specs)
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SAME_ROUND_REWRITE_FORBIDDEN" in item for item in result["problems"]))

    def test_stale_summary_compiler_blocks(self):
        bundle, context, boundary = summary_fixture()
        bundle["summary_compiler"]["currentness_result"] = "STALE"
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertIn("QUALIFICATION_SUMMARY_COMPILER_NOT_CURRENT", result["problems"])

    def test_summary_compiler_reference_substitution_blocks(self):
        bundle, context, boundary = summary_fixture()
        bundle["summary_compiler"]["compiler_qualification_digest"] = "0" * 64
        result = compile_qualification_summary(bundle, proof_context=context, trusted_boundary=boundary)
        self.assertTrue(any("QUALIFICATION_SUMMARY_COMPILER_PROOF" in item and "UNRESOLVED" in item for item in result["problems"]))


if __name__ == "__main__":
    unittest.main()
