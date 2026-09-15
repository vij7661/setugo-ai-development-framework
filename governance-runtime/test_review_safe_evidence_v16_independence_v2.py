from __future__ import annotations

import copy
from dataclasses import replace
import unittest

import review_safe_evidence_v16_independence_v2 as v2
from review_safe_evidence_v16_independence_v2 import (
    PinnedSlice2BindingHead,
    assess_bound_candidate_control,
    assess_bound_domain_independence,
    assess_bound_registry_key_independence,
    graph_validator_binding_digest,
    graph_validator_binding_signature_message,
    resolve_bound_registry_key_authority,
    slice2_validation_profile_digest,
    slice2_validator_bundle_digest,
    validate_bound_control_domain_graph_chain,
    validate_graph_validator_binding_certificate,
)
from test_review_safe_evidence_v16_independence import graph_head, make_graph
from test_review_safe_evidence_v16_trust import (
    ATTACKER,
    ISSUER,
    ROOT1,
    ROOT2,
    _pub,
    _sig,
    head_for,
    key_entry,
    make_registry,
    trust,
)


def _binding_signatures(binding_digest: str, signers=("root-1", "root-2")) -> list[dict]:
    t = trust()
    meta = {
        "root-1": ("root-key-1", "root-domain-1", ROOT1),
        "root-2": ("root-key-2", "root-domain-2", ROOT2),
    }
    rows: list[dict] = []
    for root_id in signers:
        key_id, domain, priv = meta[root_id]
        message = graph_validator_binding_signature_message(
            binding_digest,
            trust_set_digest=t.trust_set_digest,
            root_id=root_id,
            key_id=key_id,
            control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(priv, message),
        })
    return rows


def make_binding(graph: dict, signers=("root-1", "root-2")) -> tuple[dict, PinnedSlice2BindingHead]:
    t = trust()
    gh = graph_head([graph])
    cert = {
        "schema_version": 1,
        "object_type": "SLICE2_GRAPH_VALIDATOR_BINDING",
        "candidate_id": "candidate-1",
        "graph_id": gh.graph_id,
        "graph_sequence": gh.sequence,
        "graph_generation_id": gh.generation_id,
        "graph_digest": gh.graph_digest,
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
        anchor_id="slice2-binding-head-1",
        graph_head=gh,
        binding_digest=cert["binding_digest"],
        validation_profile_digest=cert["validation_profile_digest"],
        validator_bundle_digest=cert["validator_bundle_digest"],
    )
    return cert, pinned


def make_registry_context(*, generation_id="gen-1", roles_a=None, roles_b=None):
    roles_a = roles_a or ["RAW_EVIDENCE_CAPTURE_AUTHORITY"]
    roles_b = roles_b or ["RAW_EVIDENCE_CAPTURE_AUTHORITY"]
    keys = [
        key_entry(
            issuer_id="issuer-a", key_id="key-a", control_domain="review-domain-a",
            public_key_b64=_pub(ISSUER), roles=roles_a,
        ),
        key_entry(
            issuer_id="issuer-b", key_id="key-b", control_domain="review-domain-b",
            public_key_b64=_pub(ATTACKER), roles=roles_b,
        ),
    ]
    registry = make_registry(keys=keys, generation_id=generation_id)
    return registry, head_for([registry])


class Slice2BindingRepairTests(unittest.TestCase):
    def test_valid_binding_is_threshold_authenticated_but_global_promotion_remains_blocked(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        result = validate_bound_control_domain_graph_chain(
            [graph], binding_certificate=cert, bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_graph_accepted"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["graph_completeness_real_world_proven"])

    def test_single_root_binding_signature_fails(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph, signers=("root-1",))
        result = validate_graph_validator_binding_certificate(
            cert, graph_chain=[graph], bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["promotion_blocked"])
        self.assertTrue(any("BOOTSTRAP_THRESHOLD_NOT_MET" in p for p in result["problems"]))

    def test_profile_semantic_drift_invalidates_existing_binding(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        original = v2.INDEPENDENCE_RULE_ID
        try:
            v2.INDEPENDENCE_RULE_ID = original + "-DRIFT"
            result = validate_graph_validator_binding_certificate(
                cert, graph_chain=[graph], bootstrap_trust=trust(),
                expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
                expected_candidate_id="candidate-1",
            )
        finally:
            v2.INDEPENDENCE_RULE_ID = original
        self.assertFalse(result["valid"])
        self.assertTrue(any("VALIDATION_PROFILE_DIGEST_MISMATCH" in p or "PROFILE_MISMATCH" in p for p in result["problems"]))

    def test_freshly_resigned_wrong_validator_bundle_still_fails_local_bundle_match(self):
        graph = make_graph(generation_id="gen-1")
        cert, _ = make_binding(graph)
        forged = copy.deepcopy(cert)
        forged["validator_bundle_digest"] = "f" * 64
        forged["binding_digest"] = graph_validator_binding_digest(forged)
        forged["bootstrap_signatures"] = _binding_signatures(forged["binding_digest"])
        pinned = PinnedSlice2BindingHead(
            anchor_id="forged-binding-head",
            graph_head=graph_head([graph]),
            binding_digest=forged["binding_digest"],
            validation_profile_digest=forged["validation_profile_digest"],
            validator_bundle_digest=forged["validator_bundle_digest"],
        )
        result = validate_graph_validator_binding_certificate(
            forged, graph_chain=[graph], bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("VALIDATOR_BUNDLE_DIGEST_MISMATCH" in p or "BUNDLE_MISMATCH" in p for p in result["problems"]))

    def test_binding_cannot_be_reused_for_different_graph_digest(self):
        graph1 = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph1)
        domains = copy.deepcopy(graph1["domains"])
        domains.append({"control_domain_id": "review-domain-c", "parent_control_domain_ids": []})
        graph2 = make_graph(generation_id="gen-1", domains=domains)
        result = validate_graph_validator_binding_certificate(
            cert, graph_chain=[graph2], bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph2]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["promotion_blocked"])

    def test_pinned_binding_digest_mismatch_fails(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        bad_pin = replace(pinned, binding_digest="f" * 64)
        result = validate_graph_validator_binding_certificate(
            cert, graph_chain=[graph], bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=bad_pin,
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertIn("SLICE2_PINNED_BINDING_HEAD_DIGEST_MISMATCH", result["problems"])

    def test_disconnected_bound_domains_are_structurally_independent_but_promotion_blocked(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        result = assess_bound_domain_independence(
            "review-domain-a", "review-domain-b", graph_chain=[graph],
            binding_certificate=cert, bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["independence_result"], "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH")
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["independence_real_world_proven"])

    def test_not_candidate_controlled_is_structurally_clear_but_promotion_blocked(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        result = assess_bound_candidate_control(
            "review-domain-a", graph_chain=[graph], binding_certificate=cert,
            bootstrap_trust=trust(), expected_graph_head=graph_head([graph]),
            pinned_binding_head=pinned, expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_candidate_control_clear"])
        self.assertFalse(result["candidate_controlled"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["control_real_world_completeness_proven"])

    def test_registry_authority_structurally_admissible_but_globally_nonadmissible(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        registry, registry_head = make_registry_context()
        result = resolve_bound_registry_key_authority(
            "key-a", "RAW_EVIDENCE_CAPTURE",
            expected_governance_generation_id="gen-1",
            registry_chain=[registry], expected_registry_head=registry_head,
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            binding_certificate=cert, pinned_binding_head=pinned,
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])
        self.assertEqual(result["required_role"], "RAW_EVIDENCE_CAPTURE_AUTHORITY")

    def test_mixed_registry_graph_generation_fails_closed(self):
        graph = make_graph(generation_id="graph-gen-2")
        cert, pinned = make_binding(graph)
        registry, registry_head = make_registry_context(generation_id="gen-1")
        result = resolve_bound_registry_key_authority(
            "key-a", "RAW_EVIDENCE_CAPTURE",
            expected_governance_generation_id="gen-1",
            registry_chain=[registry], expected_registry_head=registry_head,
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            binding_certificate=cert, pinned_binding_head=pinned,
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertIn("SLICE2_GRAPH_HEAD_GENERATION_MISMATCH", result["problems"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])

    def test_unknown_record_type_fails_closed(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        registry, registry_head = make_registry_context()
        result = resolve_bound_registry_key_authority(
            "key-a", "NOT_A_GOVERNED_RECORD_TYPE",
            expected_governance_generation_id="gen-1",
            registry_chain=[registry], expected_registry_head=registry_head,
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            binding_certificate=cert, pinned_binding_head=pinned,
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertIn("SLICE2_EXPECTED_RECORD_TYPE_UNKNOWN", result["problems"])
        self.assertIsNone(result["required_role"])
        self.assertTrue(result["promotion_blocked"])

    def test_record_type_derives_role_and_missing_grant_fails(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        registry, registry_head = make_registry_context(
            roles_a=["REVIEWER_QUALIFICATION_AUTHORITY"],
        )
        result = resolve_bound_registry_key_authority(
            "key-a", "RAW_EVIDENCE_CAPTURE",
            expected_governance_generation_id="gen-1",
            registry_chain=[registry], expected_registry_head=registry_head,
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            binding_certificate=cert, pinned_binding_head=pinned,
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertEqual(result["required_role"], "RAW_EVIDENCE_CAPTURE_AUTHORITY")
        self.assertFalse(result["valid"])
        self.assertTrue(any("ROLE_NOT_GRANTED" in p for p in result["problems"]))
        self.assertTrue(result["promotion_blocked"])

    def test_two_bound_registry_keys_structurally_independent_but_globally_blocked(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        registry, registry_head = make_registry_context()
        result = assess_bound_registry_key_independence(
            "key-a", "RAW_EVIDENCE_CAPTURE", "key-b", "RAW_EVIDENCE_CAPTURE",
            expected_governance_generation_id="gen-1",
            registry_chain=[registry], expected_registry_head=registry_head,
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            binding_certificate=cert, pinned_binding_head=pinned,
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["independence_result"], "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH")
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["independence_real_world_proven"])

    def test_stale_graph_binding_head_or_graph_substitution_fails(self):
        graph1 = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph1)
        graph2 = make_graph(generation_id="gen-2")
        result = assess_bound_domain_independence(
            "review-domain-a", "review-domain-b", graph_chain=[graph2],
            binding_certificate=cert, bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph2]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertFalse(result["construction_independence_satisfied"])
        self.assertTrue(result["promotion_blocked"])

    def test_valid_results_never_claim_qualification_or_independent_source_measurement(self):
        graph = make_graph(generation_id="gen-1")
        cert, pinned = make_binding(graph)
        result = validate_graph_validator_binding_certificate(
            cert, graph_chain=[graph], bootstrap_trust=trust(),
            expected_graph_head=graph_head([graph]), pinned_binding_head=pinned,
            expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(result["runtime_qualification"], "NOT_CLAIMED")
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")
        self.assertFalse(result["source_measurement_independently_proven"])
        self.assertTrue(result["promotion_blocked"])


if __name__ == "__main__":
    unittest.main()
