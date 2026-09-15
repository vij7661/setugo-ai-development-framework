from __future__ import annotations

import copy
import unittest

from review_safe_evidence_v16_independence import (
    assess_domain_independence,
    assess_registry_key_independence,
    control_domain_graph_digest,
    control_domain_graph_signature_message,
    resolve_registry_key_authority,
    validate_control_domain_graph_chain,
)
from test_review_safe_evidence_v16_independence import base_domains, graph_head, make_graph
from test_review_safe_evidence_v16_trust import (
    ATTACKER,
    ISSUER,
    ROOT1,
    ROOT2,
    ROOT3,
    _pub,
    _sig,
    head_for,
    key_entry,
    make_registry,
    trust,
)


def _resign_graph(record: dict, signers=("root-1", "root-2")) -> None:
    t = trust()
    meta = {
        "root-1": ("root-key-1", "root-domain-1", ROOT1),
        "root-2": ("root-key-2", "root-domain-2", ROOT2),
        "root-3": ("root-key-3", "root-domain-3", ROOT3),
    }
    record["graph_digest"] = control_domain_graph_digest(record)
    rows = []
    for root_id in signers:
        key_id, domain, priv = meta[root_id]
        message = control_domain_graph_signature_message(
            record["graph_digest"], trust_set_digest=t.trust_set_digest,
            root_id=root_id, key_id=key_id, control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(priv, message),
        })
    record["bootstrap_signatures"] = rows


def _validate(graph: dict):
    return validate_control_domain_graph_chain(
        [graph], bootstrap_trust=trust(), expected_current_head=graph_head([graph]),
        expected_candidate_id="candidate-1",
    )


def _registry_two_keys():
    keys = [
        key_entry(
            issuer_id="issuer-a", key_id="key-a", control_domain="review-domain-a",
            public_key_b64=_pub(ISSUER), roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"],
        ),
        key_entry(
            issuer_id="issuer-b", key_id="key-b", control_domain="review-domain-b",
            public_key_b64=_pub(ATTACKER), roles=["RAW_EVIDENCE_CAPTURE_AUTHORITY"],
        ),
    ]
    registry = make_registry(keys=keys, generation_id="gen-1")
    return registry


class Slice2IAR2Tests(unittest.TestCase):
    def test_direct_core_independence_success_remains_globally_blocked(self):
        graph = make_graph(generation_id="gen-1")
        result = assess_domain_independence(
            "review-domain-a", "review-domain-b", graph_chain=[graph],
            bootstrap_trust=trust(), expected_current_head=graph_head([graph]),
            expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["independence_real_world_proven"])

    def test_graph_signer_domain_absent_from_graph_cannot_count_toward_threshold(self):
        domains = [d for d in base_domains() if d["control_domain_id"] != "root-domain-1"]
        graph = make_graph(domains=domains)
        result = _validate(graph)
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNER_DOMAIN_NOT_IN_GRAPH:root-domain-1" in p for p in result["problems"]))
        self.assertTrue(result["promotion_blocked"])

    def test_graph_signers_with_shared_load_bearing_ancestor_cannot_satisfy_threshold(self):
        domains = base_domains()
        domains.append({"control_domain_id": "bootstrap-shared-root", "parent_control_domain_ids": []})
        next(d for d in domains if d["control_domain_id"] == "root-domain-1")["parent_control_domain_ids"] = ["bootstrap-shared-root"]
        next(d for d in domains if d["control_domain_id"] == "root-domain-2")["parent_control_domain_ids"] = ["bootstrap-shared-root"]
        graph = make_graph(domains=domains)
        result = _validate(graph)
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNER_INDEPENDENCE_NOT_MET" in p for p in result["problems"]))
        self.assertTrue(any("INDEPENDENT_NONCANDIDATE_THRESHOLD_NOT_MET" in p for p in result["problems"]))

    def test_candidate_controlled_graph_signer_cannot_count_toward_threshold(self):
        graph = make_graph(candidate_domains=["candidate-domain", "root-domain-1"])
        result = _validate(graph)
        self.assertFalse(result["valid"])
        self.assertTrue(any("SIGNER_CANDIDATE_CONTROLLED:root-domain-1" in p for p in result["problems"]))

    def test_independent_noncandidate_root_quorum_authenticates_graph_structurally(self):
        graph = make_graph(generation_id="gen-1")
        result = _validate(graph)
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["bootstrap_authenticated_control_domains"], ["root-domain-1", "root-domain-2"])
        self.assertTrue(result["construction_graph_valid"])
        self.assertTrue(result["promotion_blocked"])

    def test_registry_bootstrap_quorum_relying_on_graph_candidate_root_is_rejected(self):
        graph = make_graph(
            generation_id="gen-1",
            candidate_domains=["candidate-domain", "root-domain-1"],
        )
        _resign_graph(graph, signers=("root-2", "root-3"))
        graph_result = _validate(graph)
        self.assertTrue(graph_result["valid"], graph_result["problems"])
        registry = _registry_two_keys()
        result = resolve_registry_key_authority(
            "key-a", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            registry_chain=[registry], expected_registry_head=head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])
        self.assertTrue(any("SIGNER_CANDIDATE_CONTROLLED:root-domain-1" in p for p in result["problems"]))

    def test_registry_bootstrap_quorum_with_shared_graph_ancestor_is_rejected(self):
        domains = base_domains()
        domains.append({"control_domain_id": "bootstrap-shared-root", "parent_control_domain_ids": []})
        next(d for d in domains if d["control_domain_id"] == "root-domain-1")["parent_control_domain_ids"] = ["bootstrap-shared-root"]
        next(d for d in domains if d["control_domain_id"] == "root-domain-2")["parent_control_domain_ids"] = ["bootstrap-shared-root"]
        graph = make_graph(generation_id="gen-1", domains=domains)
        _resign_graph(graph, signers=("root-2", "root-3"))
        graph_result = _validate(graph)
        self.assertTrue(graph_result["valid"], graph_result["problems"])
        registry = _registry_two_keys()
        result = resolve_registry_key_authority(
            "key-a", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            registry_chain=[registry], expected_registry_head=head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["authority_structurally_admissible_within_authenticated_graph"])
        self.assertTrue(any("SIGNER_INDEPENDENCE_NOT_MET" in p for p in result["problems"]))
        self.assertTrue(result["promotion_blocked"])

    def test_direct_core_registry_key_independence_is_structural_only_and_globally_blocked(self):
        graph = make_graph(generation_id="gen-1")
        registry = _registry_two_keys()
        result = assess_registry_key_independence(
            "key-a", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            "key-b", "RAW_EVIDENCE_CAPTURE_AUTHORITY",
            registry_chain=[registry], expected_registry_head=head_for([registry]),
            graph_chain=[graph], expected_graph_head=graph_head([graph]),
            bootstrap_trust=trust(), expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["construction_independence_satisfied"])
        self.assertFalse(result["authority_admissible"])
        self.assertTrue(result["promotion_blocked"])
        self.assertFalse(result["independence_real_world_proven"])


if __name__ == "__main__":
    unittest.main()
