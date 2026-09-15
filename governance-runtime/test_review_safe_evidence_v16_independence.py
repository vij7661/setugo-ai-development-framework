from __future__ import annotations

import copy
from dataclasses import replace
import unittest

from review_safe_evidence_v16_independence import (
    PinnedControlDomainGraphHead,
    assess_candidate_control,
    assess_domain_independence,
    assess_registry_key_independence,
    control_domain_graph_digest,
    control_domain_graph_signature_message,
    resolve_registry_key_authority,
    validate_control_domain_graph_chain,
)
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


def base_domains() -> list[dict]:
    return [
        {"control_domain_id": "root-domain-1", "parent_control_domain_ids": []},
        {"control_domain_id": "root-domain-2", "parent_control_domain_ids": []},
        {"control_domain_id": "root-domain-3", "parent_control_domain_ids": []},
        {"control_domain_id": "candidate-root", "parent_control_domain_ids": []},
        {"control_domain_id": "candidate-domain", "parent_control_domain_ids": ["candidate-root"]},
        {"control_domain_id": "candidate-service", "parent_control_domain_ids": ["candidate-domain"]},
        {"control_domain_id": "review-root-a", "parent_control_domain_ids": []},
        {"control_domain_id": "review-domain-a", "parent_control_domain_ids": ["review-root-a"]},
        {"control_domain_id": "review-root-b", "parent_control_domain_ids": []},
        {"control_domain_id": "review-domain-b", "parent_control_domain_ids": ["review-root-b"]},
        {"control_domain_id": "shared-root", "parent_control_domain_ids": []},
        {"control_domain_id": "shared-mid-a", "parent_control_domain_ids": ["shared-root"]},
        {"control_domain_id": "shared-domain-a", "parent_control_domain_ids": ["shared-mid-a"]},
        {"control_domain_id": "shared-mid-b", "parent_control_domain_ids": ["shared-root"]},
        {"control_domain_id": "shared-domain-b", "parent_control_domain_ids": ["shared-mid-b"]},
    ]


def _sign_graph(record: dict, signers=("root-1", "root-2")) -> None:
    t = trust()
    meta = {
        "root-1": ("root-key-1", "root-domain-1", ROOT1),
        "root-2": ("root-key-2", "root-domain-2", ROOT2),
    }
    rows = []
    for root_id in signers:
        key_id, domain, priv = meta[root_id]
        msg = control_domain_graph_signature_message(
            record["graph_digest"], trust_set_digest=t.trust_set_digest,
            root_id=root_id, key_id=key_id, control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(priv, msg),
        })
    record["bootstrap_signatures"] = rows


def make_graph(
    *, sequence=1, generation_id="graph-gen-1", predecessor="GENESIS",
    domains=None, candidate_domains=None, signers=("root-1", "root-2"),
) -> dict:
    t = trust()
    record = {
        "schema_version": 1,
        "object_type": "CONTROL_DOMAIN_GRAPH",
        "graph_id": "control-graph-1",
        "candidate_id": "candidate-1",
        "generation_id": generation_id,
        "trust_set_id": t.trust_set_id,
        "trust_set_digest": t.trust_set_digest,
        "sequence": sequence,
        "predecessor_graph_digest": predecessor,
        "candidate_domain_ids": list(candidate_domains or ["candidate-domain"]),
        "domains": copy.deepcopy(domains if domains is not None else base_domains()),
        "graph_digest": "",
        "bootstrap_signatures": [],
    }
    record["graph_digest"] = control_domain_graph_digest(record)
    _sign_graph(record, signers)
    return record


def resign_graph(record: dict) -> None:
    record["graph_digest"] = control_domain_graph_digest(record)
    _sign_graph(record)


def graph_head(chain: list[dict]) -> PinnedControlDomainGraphHead:
    current = chain[-1]
    return PinnedControlDomainGraphHead(
        anchor_id=f"graph-head-{current['sequence']}",
        trust_set_id=current["trust_set_id"],
        trust_set_digest=current["trust_set_digest"],
        graph_id=current["graph_id"],
        candidate_id=current["candidate_id"],
        sequence=current["sequence"],
        generation_id=current["generation_id"],
        graph_digest=current["graph_digest"],
    )


def validate(chain: list[dict], *, head=None):
    return validate_control_domain_graph_chain(
        chain, bootstrap_trust=trust(), expected_current_head=head or graph_head(chain),
        expected_candidate_id="candidate-1",
    )


class GraphValidationTests(unittest.TestCase):
    def test_valid_graph_is_threshold_authenticated_current_but_nonqualified(self):
        graph = make_graph()
        result = validate([graph])
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_graph_valid"])
        self.assertTrue(result["current_head_matched"])
        self.assertEqual(len(result["bootstrap_authenticated_control_domains"]), 2)
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["qualified"])
        self.assertFalse(result["graph_completeness_real_world_proven"])

    def test_single_bootstrap_signature_cannot_authenticate_graph(self):
        graph = make_graph(signers=("root-1",))
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("THRESHOLD_NOT_MET" in p for p in result["problems"]))

    def test_graph_tamper_and_digest_recompute_without_new_signatures_fails(self):
        graph = make_graph()
        forged = copy.deepcopy(graph)
        forged["domains"].append({"control_domain_id": "evil-domain", "parent_control_domain_ids": []})
        forged["graph_digest"] = control_domain_graph_digest(forged)
        result = validate([forged], head=graph_head([forged]))
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNATURE_INVALID" in p for p in result["problems"]))

    def test_stale_graph_prefix_cannot_override_newer_pinned_head(self):
        g1 = make_graph()
        g2 = make_graph(sequence=2, generation_id="graph-gen-2", predecessor=g1["graph_digest"])
        result = validate([g1], head=graph_head([g1, g2]))
        self.assertFalse(result["valid"])
        self.assertFalse(result["current_head_matched"])

    def test_unknown_parent_fails_closed(self):
        domains = base_domains()
        next(d for d in domains if d["control_domain_id"] == "review-domain-a")["parent_control_domain_ids"] = ["missing-parent"]
        graph = make_graph(domains=domains)
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("UNKNOWN_PARENT" in p for p in result["problems"]))

    def test_self_edge_fails_closed(self):
        domains = base_domains()
        next(d for d in domains if d["control_domain_id"] == "review-domain-a")["parent_control_domain_ids"] = ["review-domain-a"]
        graph = make_graph(domains=domains)
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("SELF_EDGE" in p for p in result["problems"]))

    def test_cycle_fails_closed(self):
        domains = base_domains()
        next(d for d in domains if d["control_domain_id"] == "review-root-a")["parent_control_domain_ids"] = ["review-domain-a"]
        graph = make_graph(domains=domains)
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("GRAPH_CYCLE" in p for p in result["problems"]))

    def test_non_nfc_domain_identifier_fails_closed(self):
        domains = base_domains()
        domains.append({"control_domain_id": "e\u0301-domain", "parent_control_domain_ids": []})
        graph = make_graph(domains=domains)
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("NOT_CANONICAL_NFC" in p for p in result["problems"]))

    def test_pinned_candidate_domain_cannot_be_omitted(self):
        graph = make_graph(candidate_domains=["candidate-root"])
        result = validate([graph])
        self.assertFalse(result["valid"])
        self.assertTrue(any("PINNED_CANDIDATE_DOMAIN_MISSING" in p for p in result["problems"]))

    def test_parent_edge_removal_is_forbidden_across_graph_updates(self):
        g1 = make_graph()
        domains = base_domains()
        next(d for d in domains if d["control_domain_id"] == "review-domain-a")["parent_control_domain_ids"] = []
        g2 = make_graph(sequence=2, generation_id="graph-gen-2", predecessor=g1["graph_digest"], domains=domains)
        result = validate([g1, g2])
        self.assertFalse(result["valid"])
        self.assertTrue(any("PARENT_REMOVAL_FORBIDDEN" in p for p in result["problems"]))

    def test_candidate_domain_removal_is_forbidden_across_updates(self):
        g1 = make_graph(candidate_domains=["candidate-domain", "candidate-root"])
        g2 = make_graph(
            sequence=2, generation_id="graph-gen-2", predecessor=g1["graph_digest"],
            candidate_domains=["candidate-domain"],
        )
        result = validate([g1, g2])
        self.assertFalse(result["valid"])
        self.assertTrue(any("CANDIDATE_DOMAIN_REMOVAL_FORBIDDEN" in p for p in result["problems"]))

    def test_domain_removal_is_forbidden_across_updates(self):
        g1 = make_graph()
        domains = [d for d in base_domains() if d["control_domain_id"] != "review-domain-b"]
        g2 = make_graph(sequence=2, generation_id="graph-gen-2", predecessor=g1["graph_digest"], domains=domains)
        result = validate([g1, g2])
        self.assertFalse(result["valid"])
        self.assertTrue(any("DOMAIN_REMOVAL_FORBIDDEN" in p for p in result["problems"]))

    def test_generation_reuse_is_forbidden(self):
        g1 = make_graph()
        g2 = make_graph(sequence=2, generation_id="graph-gen-1", predecessor=g1["graph_digest"])
        result = validate([g1, g2])
        self.assertFalse(result["valid"])
        self.assertTrue(any("GENERATION_REUSE" in p for p in result["problems"]))

    def test_predecessor_digest_mismatch_is_rejected(self):
        g1 = make_graph()
        g2 = make_graph(sequence=2, generation_id="graph-gen-2", predecessor="f" * 64)
        result = validate([g1, g2])
        self.assertFalse(result["valid"])
        self.assertTrue(any("PREDECESSOR_MISMATCH" in p for p in result["problems"]))


class IndependenceTests(unittest.TestCase):
    def assess(self, a, b, graph=None):
        graph = graph or make_graph()
        return assess_domain_independence(
            a, b, graph_chain=[graph], bootstrap_trust=trust(),
            expected_current_head=graph_head([graph]), expected_candidate_id="candidate-1",
        )

    def test_multihop_shared_ancestor_is_derived_not_inferred_from_labels(self):
        result = self.assess("shared-domain-a", "shared-domain-b")
        self.assertEqual(result["independence_result"], "NOT_INDEPENDENT")
        self.assertIn("shared-root", result["shared_load_bearing_ancestors"])
        self.assertTrue(result["promotion_blocked"])

    def test_disconnected_domains_are_independent_within_authenticated_graph(self):
        result = self.assess("review-domain-a", "review-domain-b")
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["independence_result"], "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH")
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["independence_real_world_proven"])

    def test_same_domain_is_not_independent(self):
        result = self.assess("review-domain-a", "review-domain-a")
        self.assertEqual(result["independence_result"], "NOT_INDEPENDENT")
        self.assertIn("review-domain-a", result["shared_load_bearing_ancestors"])

    def test_unknown_domain_is_independence_unproven(self):
        result = self.assess("review-domain-a", "not-in-graph")
        self.assertEqual(result["independence_result"], "INDEPENDENCE_UNPROVEN")
        self.assertTrue(result["promotion_blocked"])

    def test_invalid_graph_makes_independence_unproven(self):
        graph = make_graph(signers=("root-1",))
        result = self.assess("review-domain-a", "review-domain-b", graph=graph)
        self.assertEqual(result["independence_result"], "INDEPENDENCE_UNPROVEN")
        self.assertTrue(result["promotion_blocked"])


class CandidateControlTests(unittest.TestCase):
    def assess(self, domain):
        graph = make_graph()
        return assess_candidate_control(
            domain, graph_chain=[graph], bootstrap_trust=trust(),
            expected_current_head=graph_head([graph]), expected_candidate_id="candidate-1",
        )

    def test_candidate_domain_is_derived_candidate_controlled(self):
        result = self.assess("candidate-domain")
        self.assertTrue(result["candidate_controlled"])
        self.assertTrue(result["promotion_blocked"])

    def test_descendant_of_candidate_domain_is_candidate_controlled(self):
        result = self.assess("candidate-service")
        self.assertTrue(result["candidate_controlled"])
        self.assertIn("candidate-domain", result["shared_candidate_ancestors"])

    def test_disconnected_review_domain_is_not_candidate_controlled_within_graph(self):
        result = self.assess("review-domain-a")
        self.assertFalse(result["candidate_controlled"])
        self.assertTrue(result["construction_candidate_control_clear"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["control_real_world_completeness_proven"])


class RegistryAuthorityResolutionTests(unittest.TestCase):
    def setup_context(self, domain_a="review-domain-a", domain_b="review-domain-b"):
        graph = make_graph(generation_id="gen-1")
        keys = [
            key_entry(
                issuer_id="issuer-a", key_id="key-a", control_domain=domain_a,
                public_key_b64=_pub(ISSUER), roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"],
            ),
            key_entry(
                issuer_id="issuer-b", key_id="key-b", control_domain=domain_b,
                public_key_b64=_pub(ATTACKER), roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"],
            ),
        ]
        registry = make_registry(keys=keys, generation_id="gen-1")
        return graph, registry

    def resolve(self, key_id, role="RAW_EVIDENCE_CAPTURE_AUTHORITY", *, graph=None, registry=None, registry_head=None):
        if graph is None or registry is None:
            graph, registry = self.setup_context()
        return resolve_registry_key_authority(
            key_id, role, registry_chain=[registry],
            expected_registry_head=registry_head or head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )

    def test_valid_registry_key_role_and_domain_resolve_admissible(self):
        graph, registry = self.setup_context()
        result = self.resolve("key-a", graph=graph, registry=registry)
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])
        self.assertEqual(result["control_domain_id"], "review-domain-a")
        self.assertFalse(result["candidate_controlled"])

    def test_role_not_granted_cannot_be_asserted_by_caller(self):
        graph, registry = self.setup_context()
        result = self.resolve("key-a", "ADJUDICATION_AUTHORITY", graph=graph, registry=registry)
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertFalse(result["authority_admissible"])
        self.assertIn("REGISTRY_AUTHORITY_ROLE_NOT_GRANTED", result["problems"])

    def test_registry_domain_absent_from_authenticated_graph_fails_closed(self):
        graph, registry = self.setup_context(domain_a="unregistered-domain")
        result = self.resolve("key-a", graph=graph, registry=registry)
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertIn("REGISTRY_AUTHORITY_CONTROL_DOMAIN_NOT_IN_AUTHENTICATED_GRAPH", result["problems"])

    def test_candidate_controlled_registry_key_is_not_admissible(self):
        graph, registry = self.setup_context(domain_a="candidate-service")
        result = self.resolve("key-a", graph=graph, registry=registry)
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["candidate_controlled"])
        self.assertIn("REGISTRY_AUTHORITY_CANDIDATE_CONTROLLED", result["problems"])

    def test_stale_registry_head_fails_closed(self):
        graph, registry = self.setup_context()
        bad_head = replace(head_for([registry]), registry_digest="f" * 64)
        result = self.resolve("key-a", graph=graph, registry=registry, registry_head=bad_head)
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertIn("REGISTRY_AUTHORITY_CURRENT_HEAD_MISMATCH", result["problems"])

    def test_registry_candidate_control_boolean_injection_is_rejected_upstream(self):
        graph, registry = self.setup_context()
        registry["keys"][0]["candidate_controlled"] = False
        from test_review_safe_evidence_v16_trust import resign_registry
        resign_registry(registry)
        result = self.resolve("key-a", graph=graph, registry=registry)
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertTrue(any("KEY_FIELDS_NOT_EXACT" in p for p in result["problems"]))

    def test_two_registry_keys_in_disconnected_domains_are_independent(self):
        graph, registry = self.setup_context()
        result = assess_registry_key_independence(
            "key-a", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            "key-b", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            registry_chain=[registry], expected_registry_head=head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["independence_result"], "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH")
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])

    def test_two_registry_keys_with_shared_ancestor_are_not_independent(self):
        graph, registry = self.setup_context("shared-domain-a", "shared-domain-b")
        result = assess_registry_key_independence(
            "key-a", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            "key-b", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            registry_chain=[registry], expected_registry_head=head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertEqual(result["independence_result"], "NOT_INDEPENDENT")
        self.assertTrue(result["promotion_blocked"])
        self.assertIn("shared-root", result["shared_load_bearing_ancestors"])


if __name__ == "__main__":
    unittest.main()
