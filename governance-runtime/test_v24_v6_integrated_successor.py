from __future__ import annotations

import json
import unittest
from pathlib import Path

from v24_v6_governance_foundation import (
    COMPLETENESS_DERIVATION_REJECTION,
    GENESIS_TRUST_SCOPE_REJECTION,
    digest,
    genesis_scope_match,
    validate_completeness_derivation_graph,
)
from v24_v6_endpoint_projection import (
    compile_qualified_endpoint_table,
    derive_applicable_predicate_universe,
)
from v24_v6_atomic_binding_modes import validate_atomic_binding_mode_registry
from v24_v6_qualification_integrity import compile_qualification_summary
from v24_v6_integrated_successor import (
    APPROVED_DESIGN_GIT_BLOB_SHA,
    APPROVED_DESIGN_RECONSTRUCTION_MANIFEST_GIT_BLOB_SHA,
    SCIENTIFIC_EXECUTION_CLOSED,
    construction_frontier,
    validate_integrated_successor_manifest,
)

from test_v24_v6_adversarial_evidence_binding import (
    COMMIT as EVIDENCE_COMMIT,
    TREE as EVIDENCE_TREE,
    ENV as EVIDENCE_ENV,
    RUN as EVIDENCE_RUN,
    ROUND as EVIDENCE_ROUND,
    valid_records,
)
from test_v24_v6_governance_foundation import allowed_graph, valid_genesis_scope, D2
from test_v24_v6_endpoint_projection import endpoint_bundle, applicability_bundle, completeness
from test_v24_v6_atomic_binding_modes import registry_bundle as atomic_registry_bundle
from test_v24_v6_qualification_integrity import (
    compiler as summary_compiler,
    result_record,
    universe,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json"


class IntegratedSuccessorBindingTests(unittest.TestCase):
    def manifest(self):
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def validate(self, manifest=None, evidence=None):
        return validate_integrated_successor_manifest(
            repo_root=ROOT,
            manifest=self.manifest() if manifest is None else manifest,
            adversarial_evidence=valid_records() if evidence is None else evidence,
            expected_candidate_commit=EVIDENCE_COMMIT,
            expected_candidate_tree=EVIDENCE_TREE,
            expected_environment_contract_digest=EVIDENCE_ENV,
            expected_run_id=EVIDENCE_RUN,
            expected_round_id=EVIDENCE_ROUND,
            forbidden_evidence_producers=("CANDIDATE",),
        )

    def test_exact_r1_r8_manifest_and_executed_adversarial_evidence_bind(self):
        result = self.validate()
        self.assertTrue(result["integration_valid"], result["problems"])
        self.assertTrue(result["adversarial_evidence_valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["bound_file_count"], 16)
        self.assertEqual(result["scientific_execution_state"], SCIENTIFIC_EXECUTION_CLOSED)
        self.assertEqual(len({x["raw_sha256"] for x in result["bound_files"]}), 16)
        self.assertEqual(len(result["adversarial_evidence_records"]), 6)

    def test_name_only_mandatory_checks_are_not_sufficient(self):
        result = self.validate(evidence=[])
        self.assertFalse(result["integration_valid"])
        self.assertFalse(result["adversarial_evidence_valid"])
        self.assertTrue(
            any("ADVERSARIAL_EVIDENCE_REQUIRED_CHECK_MISSING" in x for x in result["problems"]),
            result["problems"],
        )

    def test_missing_external_evidence_context_fails_closed(self):
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=self.manifest())
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            "INTEGRATED_SUCCESSOR_ADVERSARIAL_EVIDENCE_CONTEXT_REQUIRED:expected_candidate_commit",
            result["problems"],
        )

    def test_manifest_blob_tamper_blocks(self):
        m = self.manifest()
        m["workstreams"][0]["production_git_blob_sha"] = "0" * 40
        result = self.validate(manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn("INTEGRATED_SUCCESSOR_BLOB_MISMATCH:R1:production", result["problems"])

    def test_approved_design_object_must_be_exact_reviewed_blob(self):
        m = self.manifest()
        self.assertEqual(m["approved_design_git_blob_sha"], APPROVED_DESIGN_GIT_BLOB_SHA)
        m["approved_design_git_blob_sha"] = m["approved_design_source_git_blob_sha"]
        result = self.validate(manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            "INTEGRATED_SUCCESSOR_APPROVED_DESIGN_BINDING_MISMATCH:approved_design_git_blob_sha",
            result["problems"],
        )

    def test_reconstruction_manifest_identity_is_load_bearing(self):
        m = self.manifest()
        self.assertEqual(
            m["approved_design_reconstruction_manifest_git_blob_sha"],
            APPROVED_DESIGN_RECONSTRUCTION_MANIFEST_GIT_BLOB_SHA,
        )
        m["approved_design_reconstruction_manifest_git_blob_sha"] = "0" * 40
        result = self.validate(manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            "INTEGRATED_SUCCESSOR_APPROVED_DESIGN_BINDING_MISMATCH:approved_design_reconstruction_manifest_git_blob_sha",
            result["problems"],
        )

    def test_manifest_cannot_open_scientific_execution(self):
        m = self.manifest()
        m["scientific_execution_state"] = "OPEN"
        result = self.validate(manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn("INTEGRATED_SUCCESSOR_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED", result["problems"])

    def test_frontier_is_non_authoritative_and_execution_closed(self):
        result = construction_frontier()
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")
        self.assertEqual(result["scientific_execution_state"], SCIENTIFIC_EXECUTION_CLOSED)


class MandatoryV6AdversarialIntegrationTests(unittest.TestCase):
    def test_mixed_allowed_and_disallowed_terminal_is_rejected(self):
        graph = allowed_graph()
        graph["nodes"].append({
            "node_id": "DISALLOWED-TERMINAL",
            "omission_sensitive": True,
            "root_kind": "CANDIDATE_REGISTRY",
            "source_surface_digest": "4" * 64,
        })
        graph["edges"].append({"from": "REG-A", "to": "DISALLOWED-TERMINAL"})
        result = validate_completeness_derivation_graph(graph)
        self.assertIn(COMPLETENESS_DERIVATION_REJECTION, result["problems"])
        self.assertIn("COMPLETENESS_GRAPH_DISALLOWED_TERMINAL:DISALLOWED-TERMINAL", result["problems"])

    def test_every_reachable_terminal_allowed_positive(self):
        result = validate_completeness_derivation_graph(allowed_graph())
        self.assertEqual(result["problems"], [])
        self.assertEqual(result["allowed_roots"], ["ROOT-DEPLOY"])

    def test_genesis_cross_pair_is_rejected(self):
        scope = valid_genesis_scope()
        result = genesis_scope_match(scope, object_id="BOOTSTRAP-VERIFIER", content_digest=D2)
        self.assertFalse(result["matched"])
        self.assertEqual(result["endpoint"], GENESIS_TRUST_SCOPE_REJECTION)

    def test_applicable_predicate_omission_is_rejected(self):
        table = compile_qualified_endpoint_table(endpoint_bundle())
        self.assertTrue(table["qualified"], table["problems"])
        bundle = applicability_bundle(table["compiled_rows"], table["compiled_table_digest"])
        bundle["applicable_universe_completeness"] = completeness("APP-U", ["P1"])
        result = derive_applicable_predicate_universe(bundle)
        self.assertFalse(result["qualified"])
        self.assertIn("APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH", result["problems"])

    def test_atomic_binding_mode_omission_is_rejected(self):
        bundle = atomic_registry_bundle()
        bundle["registry"]["entries"].pop()
        material = dict(bundle["registry"])
        material.pop("content_digest")
        bundle["registry"]["content_digest"] = digest(material)
        result = validate_atomic_binding_mode_registry(bundle)
        self.assertFalse(result["qualified"])
        self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", result["problems"])

    def test_later_resolution_preserves_historical_pass_count(self):
        old = result_record("CASE-A", 1, "UNRESOLVED", execution="NOT_EXECUTED")
        old_b = result_record("CASE-B", 2, "FAIL_CODE_DEFECT")
        later = result_record(
            "CASE-A",
            3,
            "PASS",
            round_id="ROUND-2",
            prior=old["result_record_digest"],
        )
        result = compile_qualification_summary({
            "summary_compiler": summary_compiler(),
            "case_universe": universe("ROUND-1"),
            "qualification_round_id": "ROUND-1",
            "result_records": [old, old_b, later],
        })
        self.assertEqual(result["pass_count"], 0)
        self.assertEqual(result["nonpass"]["CASE-A"], "UNRESOLVED")


if __name__ == "__main__":
    unittest.main()
