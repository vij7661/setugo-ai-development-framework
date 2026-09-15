from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import unittest

from review_safe_evidence_v16_independence import (
    control_domain_graph_digest,
    control_domain_graph_signature_message,
)
from review_safe_evidence_v16_independence_v2 import (
    PinnedSlice2BindingHead,
    graph_validator_binding_digest,
    graph_validator_binding_signature_message,
    slice2_validation_profile_digest,
    slice2_validator_bundle_digest,
    validate_graph_validator_binding_certificate,
)
from test_review_safe_evidence_v16_independence import base_domains, graph_head, make_graph
from test_review_safe_evidence_v16_trust import ROOT1, ROOT2, ROOT3, _sig, trust

ROOT_META = {
    "root-1": ("root-key-1", "root-domain-1", ROOT1),
    "root-2": ("root-key-2", "root-domain-2", ROOT2),
    "root-3": ("root-key-3", "root-domain-3", ROOT3),
}


def _resign_graph(record: dict, signers=("root-1", "root-2")) -> None:
    t = trust()
    record["graph_digest"] = control_domain_graph_digest(record)
    rows = []
    for root_id in signers:
        key_id, domain, private = ROOT_META[root_id]
        message = control_domain_graph_signature_message(
            record["graph_digest"], trust_set_digest=t.trust_set_digest,
            root_id=root_id, key_id=key_id, control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(private, message),
        })
    record["bootstrap_signatures"] = rows


def _binding_signatures(binding_digest: str, signers=("root-1", "root-2")) -> list[dict]:
    t = trust()
    rows = []
    for root_id in signers:
        key_id, domain, private = ROOT_META[root_id]
        message = graph_validator_binding_signature_message(
            binding_digest, trust_set_digest=t.trust_set_digest,
            root_id=root_id, key_id=key_id, control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(private, message),
        })
    return rows


def _make_binding(graph: dict, signers=("root-1", "root-2")) -> tuple[dict, PinnedSlice2BindingHead]:
    t = trust()
    head = graph_head([graph])
    cert = {
        "schema_version": 1,
        "object_type": "SLICE2_GRAPH_VALIDATOR_BINDING",
        "candidate_id": "candidate-1",
        "graph_id": head.graph_id,
        "graph_sequence": head.sequence,
        "graph_generation_id": head.generation_id,
        "graph_digest": head.graph_digest,
        "trust_set_id": t.trust_set_id,
        "trust_set_digest": t.trust_set_digest,
        "validation_profile_digest": slice2_validation_profile_digest(),
        "validator_bundle_digest": slice2_validator_bundle_digest(),
        "binding_digest": "",
        "bootstrap_signatures": [],
    }
    cert["binding_digest"] = graph_validator_binding_digest(cert)
    cert["bootstrap_signatures"] = _binding_signatures(cert["binding_digest"], signers)
    pinned = PinnedSlice2BindingHead(
        anchor_id="slice2-binding-head-iar3",
        graph_head=head,
        binding_digest=cert["binding_digest"],
        validation_profile_digest=cert["validation_profile_digest"],
        validator_bundle_digest=cert["validator_bundle_digest"],
    )
    return cert, pinned


def _validate(graph: dict, binding_signers=("root-1", "root-2")) -> dict:
    cert, pinned = _make_binding(graph, binding_signers)
    return validate_graph_validator_binding_certificate(
        cert, graph_chain=[graph], bootstrap_trust=trust(),
        expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
        expected_candidate_id="candidate-1",
    )


class Slice2IAR3Tests(unittest.TestCase):
    def test_binding_signer_domain_absent_from_exact_bound_graph_is_rejected(self):
        domains = [d for d in base_domains() if d["control_domain_id"] != "root-domain-1"]
        graph = make_graph(generation_id="gen-1", domains=domains)
        _resign_graph(graph, signers=("root-2", "root-3"))
        result = _validate(graph, binding_signers=("root-1", "root-2"))
        self.assertFalse(result["valid"])
        self.assertFalse(result["construction_binding_valid"])
        self.assertEqual(result["bootstrap_authenticated_control_domains"], [])
        self.assertTrue(any("SIGNER_DOMAIN_NOT_IN_GRAPH:root-domain-1" in p for p in result["problems"]))

    def test_candidate_controlled_binding_signer_is_rejected(self):
        graph = make_graph(
            generation_id="gen-1",
            candidate_domains=["candidate-domain", "root-domain-1"],
        )
        _resign_graph(graph, signers=("root-2", "root-3"))
        result = _validate(graph, binding_signers=("root-1", "root-2"))
        self.assertFalse(result["valid"])
        self.assertFalse(result["construction_binding_valid"])
        self.assertTrue(any("SIGNER_CANDIDATE_CONTROLLED:root-domain-1" in p for p in result["problems"]))

    def test_binding_signers_with_shared_ancestor_cannot_satisfy_quorum(self):
        domains = copy.deepcopy(base_domains())
        domains.append({"control_domain_id": "binding-shared-root", "parent_control_domain_ids": []})
        next(d for d in domains if d["control_domain_id"] == "root-domain-1")["parent_control_domain_ids"] = ["binding-shared-root"]
        next(d for d in domains if d["control_domain_id"] == "root-domain-2")["parent_control_domain_ids"] = ["binding-shared-root"]
        graph = make_graph(generation_id="gen-1", domains=domains)
        _resign_graph(graph, signers=("root-2", "root-3"))
        result = _validate(graph, binding_signers=("root-1", "root-2"))
        self.assertFalse(result["valid"])
        self.assertFalse(result["construction_binding_valid"])
        self.assertTrue(any("SIGNER_INDEPENDENCE_NOT_MET" in p for p in result["problems"]))
        self.assertTrue(any("INDEPENDENT_NONCANDIDATE_THRESHOLD_NOT_MET" in p for p in result["problems"]))

    def test_graph_represented_noncandidate_pairwise_independent_binding_quorum_validates_structurally(self):
        graph = make_graph(generation_id="gen-1")
        result = _validate(graph)
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_binding_valid"])
        self.assertTrue(result["binding_quorum_graph_qualified"])
        self.assertEqual(result["bootstrap_authenticated_control_domains"], ["root-domain-1", "root-domain-2"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")

    def test_failed_outer_binding_quorum_never_reports_construction_binding_valid(self):
        graph = make_graph(generation_id="gen-1")
        result = _validate(graph, binding_signers=("root-1",))
        self.assertFalse(result["construction_binding_valid"])
        self.assertFalse(result["binding_quorum_graph_qualified"])
        self.assertTrue(result["promotion_blocked"])

    def test_current_baseline_manifest_is_semantic_revision_two_and_blob_bound(self):
        root = Path(__file__).resolve().parent
        current = json.loads((root / "review-safe-evidence-v16-slice2-test-manifest-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(current["manifest_id"], "REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-002")
        self.assertEqual(current["semantic_revision"], 2)
        self.assertEqual(current["supersedes_manifest_id"], "REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001")
        self.assertEqual(len(current["tests"]), 30)
        self.assertTrue(all(row["requirement_test_id"].startswith("V16-S2-B2-") for row in current["tests"]))
        source = root / "test_review_safe_evidence_v16_independence.py"
        blob = subprocess.check_output(["git", "hash-object", str(source)], text=True).strip()
        self.assertEqual(current["test_source_git_blob_sha"], blob)

    def test_historical_baseline_manifest_is_not_in_current_manifest_index(self):
        root = Path(__file__).resolve().parent
        index = json.loads((root / "review-safe-evidence-v16-slice2-current-manifests.json").read_text(encoding="utf-8"))
        self.assertEqual(index["current_baseline_manifest_id"], "REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-002")
        self.assertNotIn("REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001", index["current_manifest_ids"])
        self.assertIn("REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001", index["historical_manifest_ids"])

    def test_valid_binding_still_cannot_claim_qualification_or_effect_authority(self):
        graph = make_graph(generation_id="gen-1")
        result = _validate(graph)
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(result["runtime_qualification"], "NOT_CLAIMED")
        self.assertFalse(result["source_measurement_independently_proven"])
        self.assertFalse(result["graph_completeness_real_world_proven"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
