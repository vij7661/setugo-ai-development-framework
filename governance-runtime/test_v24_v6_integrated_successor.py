from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from v24_v6_governance_foundation import (
    COMPLETENESS_DERIVATION_REJECTION,
    GENESIS_TRUST_SCOPE_REJECTION,
    genesis_scope_match,
    validate_completeness_derivation_graph,
)
from v24_v6_endpoint_projection import derive_applicable_predicate_universe
from v24_v6_atomic_binding_modes import validate_atomic_binding_mode_registry
from v24_v6_qualification_integrity import compile_qualification_summary
from v24_v6_integrated_successor import (
    APPROVED_DESIGN_GIT_BLOB_SHA,
    APPROVED_DESIGN_RECONSTRUCTION_MANIFEST_GIT_BLOB_SHA,
    EXPECTED_SHARED_PRODUCTION_DEPENDENCIES,
    SCIENTIFIC_EXECUTION_CLOSED,
    construction_frontier,
    validate_integrated_successor_manifest,
)

from test_v24_v6_governance_foundation import allowed_graph, valid_genesis_scope, D2
from test_v24_v6_endpoint_projection import build_chain
from test_v24_v6_atomic_binding_modes import proof_closed_registry_fixture
from test_v24_v6_qualification_integrity import summary_fixture

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json"


class IntegratedSuccessorBindingTests(unittest.TestCase):
    def manifest(self):
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_exact_r1_r8_plus_shared_dependency_manifest_binds(self):
        result = validate_integrated_successor_manifest(
            repo_root=ROOT,
            manifest=self.manifest(),
        )
        self.assertTrue(result["integration_valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["bound_file_count"], 21)
        self.assertEqual(result["scientific_execution_state"], SCIENTIFIC_EXECUTION_CLOSED)
        self.assertEqual(len({x["raw_sha256"] for x in result["bound_files"]}), 21)
        dependency_paths = {
            row["path"]
            for row in result["bound_files"]
            if row["role"] == "dependency"
        }
        self.assertEqual(
            dependency_paths,
            set(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES.values()),
        )

    def test_manifest_blob_tamper_blocks(self):
        m = self.manifest()
        m["workstreams"][0]["production_git_blob_sha"] = "0" * 40
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn("INTEGRATED_SUCCESSOR_BLOB_MISMATCH:R1:production", result["problems"])

    def test_shared_dependency_blob_tamper_blocks(self):
        m = self.manifest()
        m["shared_dependencies"][0]["git_blob_sha"] = "0" * 40
        dep_id = m["shared_dependencies"][0]["dependency_id"]
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_BLOB_MISMATCH:{dep_id}",
            result["problems"],
        )

    def test_shared_dependency_omission_blocks(self):
        m = self.manifest()
        removed = m["shared_dependencies"].pop()
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_MISSING:{removed['dependency_id']}",
            result["problems"],
        )

    def test_approved_design_object_must_be_exact_reviewed_blob(self):
        m = self.manifest()
        self.assertEqual(m["approved_design_git_blob_sha"], APPROVED_DESIGN_GIT_BLOB_SHA)
        m["approved_design_git_blob_sha"] = m["approved_design_source_git_blob_sha"]
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
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
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            "INTEGRATED_SUCCESSOR_APPROVED_DESIGN_BINDING_MISMATCH:approved_design_reconstruction_manifest_git_blob_sha",
            result["problems"],
        )

    def test_manifest_cannot_open_scientific_execution(self):
        m = self.manifest()
        m["scientific_execution_state"] = "OPEN"
        result = validate_integrated_successor_manifest(repo_root=ROOT, manifest=m)
        self.assertFalse(result["integration_valid"])
        self.assertIn(
            "INTEGRATED_SUCCESSOR_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED",
            result["problems"],
        )

    def test_frontier_is_non_authoritative_and_execution_closed(self):
        result = construction_frontier()
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")
        self.assertEqual(result["scientific_execution_state"], SCIENTIFIC_EXECUTION_CLOSED)


class MandatoryV6AdversarialIntegrationTests(unittest.TestCase):
    def test_mixed_allowed_and_disallowed_terminal_is_rejected(self):
        graph = allowed_graph()
        graph["nodes"].append(
            {
                "node_id": "DISALLOWED-TERMINAL",
                "omission_sensitive": True,
                "root_kind": "CANDIDATE_REGISTRY",
                "source_surface_digest": "4" * 64,
            }
        )
        graph["edges"].append({"from": "REG-A", "to": "DISALLOWED-TERMINAL"})
        result = validate_completeness_derivation_graph(graph)
        self.assertIn(COMPLETENESS_DERIVATION_REJECTION, result["problems"])
        self.assertIn(
            "COMPLETENESS_GRAPH_DISALLOWED_TERMINAL:DISALLOWED-TERMINAL",
            result["problems"],
        )

    def test_every_reachable_terminal_allowed_positive(self):
        result = validate_completeness_derivation_graph(allowed_graph())
        self.assertEqual(result["problems"], [])
        self.assertEqual(result["allowed_roots"], ["ROOT-DEPLOY"])

    def test_genesis_cross_pair_is_rejected(self):
        scope = valid_genesis_scope()
        result = genesis_scope_match(
            scope,
            object_id="BOOTSTRAP-VERIFIER",
            content_digest=D2,
        )
        self.assertFalse(result["matched"])
        self.assertEqual(result["endpoint"], GENESIS_TRUST_SCOPE_REJECTION)

    def test_applicable_predicate_omission_is_rejected(self):
        chain = build_chain()
        bundle = copy.deepcopy(chain["app"])
        bundle["applicable_universe_completeness"]["actual_members"] = ["P1"]
        result = derive_applicable_predicate_universe(
            bundle,
            proof_context=chain["context"],
            trusted_boundary=chain["boundary"],
        )
        self.assertFalse(result["qualified"])
        self.assertIn("APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH", result["problems"])

    def test_atomic_binding_mode_omission_is_rejected(self):
        bundle, context, boundary, _ = proof_closed_registry_fixture()
        bundle = copy.deepcopy(bundle)
        bundle["registry"]["entries"].pop()
        result = validate_atomic_binding_mode_registry(
            bundle,
            proof_context=context,
            trusted_boundary=boundary,
        )
        self.assertFalse(result["qualified"])
        self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", result["problems"])

    def test_later_resolution_preserves_historical_pass_count(self):
        specs = [
            {
                "name": "OLD-A",
                "case_id": "CASE-A",
                "seq": 1,
                "disposition": "UNRESOLVED",
                "execution": "NOT_EXECUTED",
                "round_id": "ROUND-1",
            },
            {
                "case_id": "CASE-B",
                "seq": 2,
                "disposition": "FAIL_CODE_DEFECT",
                "round_id": "ROUND-1",
            },
            {
                "case_id": "CASE-A",
                "seq": 3,
                "disposition": "PASS",
                "round_id": "ROUND-2",
                "prior_name": "OLD-A",
            },
        ]
        bundle, context, boundary = summary_fixture(specs, round_id="ROUND-1")
        result = compile_qualification_summary(
            bundle,
            proof_context=context,
            trusted_boundary=boundary,
        )
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(result["pass_count"], 0)
        self.assertEqual(result["nonpass"]["CASE-A"], "UNRESOLVED")


if __name__ == "__main__":
    unittest.main()
