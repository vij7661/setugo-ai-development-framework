from __future__ import annotations

import copy
from pathlib import Path
from unittest import mock
import unittest

import review_safe_evidence_v16_independence_v2 as wrapper
from review_safe_evidence_v16_manifest_validation import (
    HISTORICAL_BASELINE_BLOB,
    ManifestValidationError,
    load_strict_json,
    loads_strict_json,
    validate_current_manifest_set,
    validate_manifest_schema,
    validate_predecessor_binding,
)
from test_review_safe_evidence_v16_independence import make_graph
from test_review_safe_evidence_v16_independence_iar3 import _make_binding
from test_review_safe_evidence_v16_trust import trust


class Slice2IAR4Tests(unittest.TestCase):
    def test_public_binding_uses_owned_graph_snapshot_when_caller_mutates_after_snapshot(self):
        graph = make_graph(generation_id="gen-1")
        caller_chain = [graph]
        cert, pinned = _make_binding(graph)
        original_qualifier = wrapper._qualify_binding_signers

        def mutate_caller_then_qualify(signer_domains, received_chain, threshold):
            caller_chain[0]["candidate_domain_ids"].append("root-domain-1")
            return original_qualifier(signer_domains, received_chain, threshold)

        with mock.patch.object(wrapper, "_qualify_binding_signers", side_effect=mutate_caller_then_qualify):
            result = wrapper.validate_graph_validator_binding_certificate(
                cert,
                graph_chain=caller_chain,
                bootstrap_trust=trust(),
                expected_graph_head=pinned.graph_head,
                pinned_binding_head=pinned,
                expected_candidate_id="candidate-1",
            )
        self.assertIn("root-domain-1", caller_chain[0]["candidate_domain_ids"])
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_binding_valid"])
        self.assertEqual(
            result["bootstrap_authenticated_control_domains"],
            ["root-domain-1", "root-domain-2"],
        )
        self.assertTrue(result["promotion_blocked"])

    def test_historical_predecessor_exact_blob_binding_passes(self):
        root = Path(__file__).resolve().parent
        baseline = load_strict_json(root / "review-safe-evidence-v16-slice2-test-manifest-v2.json")
        index = load_strict_json(root / "review-safe-evidence-v16-slice2-current-manifests.json")
        historical = (root / "review-safe-evidence-v16-slice2-test-manifest.json").read_bytes()
        self.assertEqual(baseline["supersedes_manifest_git_blob_sha"], HISTORICAL_BASELINE_BLOB)
        self.assertEqual(validate_predecessor_binding(baseline, index, historical), [])

    def test_same_predecessor_id_with_different_content_is_rejected(self):
        root = Path(__file__).resolve().parent
        baseline = load_strict_json(root / "review-safe-evidence-v16-slice2-test-manifest-v2.json")
        index = load_strict_json(root / "review-safe-evidence-v16-slice2-current-manifests.json")
        historical = (root / "review-safe-evidence-v16-slice2-test-manifest.json").read_bytes()
        mutated = historical + b"\n"
        problems = validate_predecessor_binding(baseline, index, mutated)
        self.assertIn("HISTORICAL_BASELINE_BLOB_MISMATCH", problems)

    def test_duplicate_top_level_manifest_key_is_rejected(self):
        with self.assertRaises(ManifestValidationError):
            loads_strict_json('{"schema_version":1,"schema_version":1}', "duplicate-top")

    def test_duplicate_per_test_key_is_rejected(self):
        text = '{"tests":[{"mandatory":true,"mandatory":true,"python_test_id":"x","requirement_test_id":"y"}]}'
        with self.assertRaises(ManifestValidationError):
            loads_strict_json(text, "duplicate-test")

    def test_unknown_top_level_manifest_field_is_rejected(self):
        root = Path(__file__).resolve().parent
        baseline = copy.deepcopy(load_strict_json(root / "review-safe-evidence-v16-slice2-test-manifest-v2.json"))
        baseline["unreviewed_authority_override"] = True
        problems = validate_manifest_schema(baseline, "baseline_v2")
        self.assertTrue(any("FIELDS_UNKNOWN:unreviewed_authority_override" in p for p in problems))

    def test_unknown_per_test_field_is_rejected(self):
        root = Path(__file__).resolve().parent
        baseline = copy.deepcopy(load_strict_json(root / "review-safe-evidence-v16-slice2-test-manifest-v2.json"))
        baseline["tests"][0]["silent_override"] = "PASS"
        problems = validate_manifest_schema(baseline, "baseline_v2")
        self.assertTrue(any("FIELDS_UNKNOWN:silent_override" in p for p in problems))

    def test_valid_current_manifest_set_passes_strictly_but_remains_nonauthoritative(self):
        root = Path(__file__).resolve().parent
        result = validate_current_manifest_set(root)
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["test_count"], 69)
        self.assertEqual(result["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(result["runtime_qualification"], "NOT_CLAIMED")
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
