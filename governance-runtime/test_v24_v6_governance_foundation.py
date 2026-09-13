from __future__ import annotations

import unittest

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    COMPLETENESS_DERIVATION_REJECTION,
    GENESIS_TRUST_SCOPE_REJECTION,
    CURRENT,
    QUALIFIED,
    construction_frontier,
    digest,
    genesis_scope_match,
    validate_completeness_derivation_graph,
    validate_currentness_binding,
    validate_genesis_trusted_scope,
    validate_governed_qualification,
    validate_independence_qualification,
    validate_registry_completeness_qualification,
)

D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64
D5 = "5" * 64
D6 = "6" * 64


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str = "SRC-1") -> dict:
    r = {
        "currentness_rule_id": "CUR-1",
        "source_object_id": source_id,
        "source_version_or_sequence": "7",
        "source_digest": D1,
        "observed_at_sequence": 8,
        "verifier_qualification_digest": D2,
        "result": CURRENT,
        "binding_digest": "",
    }
    return seal(r, "binding_digest")


def allowed_graph() -> dict:
    return {
        "nodes": [
            {"node_id": "REG-A", "omission_sensitive": True},
            {
                "node_id": "ROOT-DEPLOY",
                "omission_sensitive": False,
                "root_kind": "IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY",
                "source_surface_digest": D3,
            },
        ],
        "edges": [{"from": "REG-A", "to": "ROOT-DEPLOY"}],
    }


def valid_registry_record() -> dict:
    members = ["A", "B"]
    r = {
        "subject_object_id": "REG-A",
        "subject_content_digest": D1,
        "expected_members": members,
        "actual_members": list(reversed(members)),
        "expected_member_set_digest": digest(sorted(members)),
        "actual_member_set_digest": digest(sorted(members)),
        "set_equality_proof_digest": D2,
        "completeness_derivation_graph": allowed_graph(),
        "derivation_mechanism_qualification_digests": [D3, D4],
        "derivation_authority_independence_digests": [D5, D6],
        "source_surface_digests": [D3],
        "currentness_bindings": [currentness("REG-A")],
        "verifier_qualification_digest": D4,
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(r, "qualification_digest")


def valid_genesis_scope() -> dict:
    trusted = [
        {"object_id": "BOOTSTRAP-VERIFIER", "content_digest": D1},
        {"object_id": "ANCHOR-VERIFIER", "content_digest": D2},
    ]
    r = {
        "governance_generation_id": "GEN-V24",
        "genesis_record_digest": D3,
        "root_kernel_digest": D4,
        "trusted_objects": trusted,
        "trusted_object_pair_set_digest": digest(
            sorted(trusted, key=lambda x: (x["object_id"], x["content_digest"]))
        ),
        "permitted_bootstrap_roles": ["BOOTSTRAP_VERIFIER", "ANCHOR_VERIFIER"],
        "residual_trust_reason_ids": ["GENESIS_ROOT"],
        "creation_ceremony_digest": D5,
        "durable_anchor_digest": D6,
        "scope_digest": "",
    }
    return seal(r, "scope_digest")


def valid_independence() -> dict:
    r = {
        "independence_qualification_id": "IND-1",
        "independence_rule_id": "RULE-1",
        "subject_identity_id": "SUBJECT",
        "subject_control_closure": ["ORG:SUBJECT", "KMS:SUBJECT"],
        "counterparties": [
            {
                "identity_id": "CP-1",
                "control_closure": ["ORG:EXTERNAL", "KMS:EXTERNAL"],
            }
        ],
        "shared_control_intersections": [],
        "evidence_record_digests": [D1],
        "currentness_bindings": [currentness("IND-EVIDENCE")],
        "result": QUALIFIED,
        "verifier_qualification_digest": D2,
        "qualification_digest": "",
    }
    return seal(r, "qualification_digest")


def valid_qualification() -> dict:
    r = {
        "qualification_id": "Q-1",
        "subject_object_id": "MECH-1",
        "subject_content_digest": D1,
        "subject_kind": "VERIFIER",
        "subject_owner_id": "OWNER-1",
        "qualification_authority_id": "AUTH-1",
        "authority_member_ids": ["MEMBER-1"],
        "authority_control_domain_ids": ["DOMAIN-EXT"],
        "independence_qualification_digests": [D2],
        "evidence_record_digests": [D3],
        "evidence_class_ids": ["EVIDENCE-CLASS-1"],
        "verifier_mechanism_id": "VERIFIER-2",
        "verifier_mechanism_qualification_digest": D4,
        "currentness_bindings": [currentness("MECH-1")],
        "result": QUALIFIED,
        "proof_digest": D5,
        "qualification_digest": "",
    }
    return seal(r, "qualification_digest")


class V24V6GovernanceFoundationTests(unittest.TestCase):
    def test_frontier_is_construction_only(self):
        r = construction_frontier()
        self.assertEqual(r["state"], "V24_V6_R1_GOVERNANCE_FOUNDATION_CONSTRUCTION_READY")
        self.assertFalse(r["qualified"])
        self.assertEqual(r["authority_effect"], AUTHORITY_EFFECT)

    def test_allowed_root_graph_passes(self):
        r = validate_completeness_derivation_graph(allowed_graph())
        self.assertEqual(r["problems"], [])
        self.assertEqual(r["allowed_roots"], ["ROOT-DEPLOY"])

    def test_allowed_plus_disallowed_terminal_fails_universal_root_closure(self):
        g = allowed_graph()
        g["nodes"].append(
            {
                "node_id": "BAD-REGISTRY-ROOT",
                "omission_sensitive": True,
                "root_kind": "CANDIDATE_REGISTRY",
                "source_surface_digest": D4,
            }
        )
        g["edges"].append({"from": "REG-A", "to": "BAD-REGISTRY-ROOT"})
        r = validate_completeness_derivation_graph(g)
        self.assertIn(COMPLETENESS_DERIVATION_REJECTION, r["problems"])
        self.assertIn(
            "COMPLETENESS_GRAPH_DISALLOWED_TERMINAL:BAD-REGISTRY-ROOT",
            r["problems"],
        )

    def test_cycle_fails(self):
        g = allowed_graph()
        g["nodes"].append({"node_id": "REG-B", "omission_sensitive": True})
        g["edges"] = [
            {"from": "REG-A", "to": "REG-B"},
            {"from": "REG-B", "to": "REG-A"},
        ]
        r = validate_completeness_derivation_graph(g)
        self.assertIn(COMPLETENESS_DERIVATION_REJECTION, r["problems"])

    def test_transitive_mutual_omission_cycle_fails_even_with_allowed_root(self):
        g = allowed_graph()
        g["nodes"].append({"node_id": "REG-B", "omission_sensitive": True})
        g["edges"] = [
            {"from": "REG-A", "to": "REG-B"},
            {"from": "REG-B", "to": "REG-A"},
            {"from": "REG-B", "to": "ROOT-DEPLOY"},
        ]
        r = validate_completeness_derivation_graph(g)
        self.assertIn(COMPLETENESS_DERIVATION_REJECTION, r["problems"])

    def test_registry_completeness_exact_set_equality_passes(self):
        self.assertEqual(validate_registry_completeness_qualification(valid_registry_record()), [])

    def test_registry_omission_fails(self):
        r = valid_registry_record()
        r["actual_members"] = ["A"]
        r["actual_member_set_digest"] = digest(["A"])
        seal(r, "qualification_digest")
        problems = validate_registry_completeness_qualification(r)
        self.assertIn("REGISTRY_COMPLETENESS_SET_EQUALITY_FAILED", problems)
        self.assertIn("REGISTRY_COMPLETENESS_FALSE_QUALIFIED_RESULT", problems)

    def test_registry_with_disallowed_dependency_fails(self):
        r = valid_registry_record()
        g = r["completeness_derivation_graph"]
        g["nodes"].append(
            {
                "node_id": "BAD",
                "omission_sensitive": False,
                "root_kind": "UNQUALIFIED_REGISTRY",
                "source_surface_digest": D6,
            }
        )
        g["edges"].append({"from": "REG-A", "to": "BAD"})
        seal(r, "qualification_digest")
        problems = validate_registry_completeness_qualification(r)
        self.assertTrue(any(COMPLETENESS_DERIVATION_REJECTION in x for x in problems))

    def test_currentness_digest_is_verified(self):
        r = currentness()
        self.assertEqual(validate_currentness_binding(r), [])
        r["source_digest"] = D2
        self.assertIn(
            "CURRENTNESS_BINDING_DIGEST_MISMATCH",
            validate_currentness_binding(r),
        )

    def test_independence_shared_control_cannot_be_qualified(self):
        r = valid_independence()
        r["counterparties"][0]["control_closure"] = ["ORG:SUBJECT", "KMS:EXTERNAL"]
        r["shared_control_intersections"] = ["ORG:SUBJECT"]
        seal(r, "qualification_digest")
        problems = validate_independence_qualification(r)
        self.assertIn("INDEPENDENCE_QUALIFIED_WITH_SHARED_CONTROL", problems)

    def test_independence_intersection_proof_must_match_actual(self):
        r = valid_independence()
        r["shared_control_intersections"] = ["ORG:FAKE"]
        seal(r, "qualification_digest")
        self.assertIn(
            "INDEPENDENCE_INTERSECTION_PROOF_MISMATCH",
            validate_independence_qualification(r),
        )

    def test_governed_qualification_prohibits_self_authority(self):
        r = valid_qualification()
        r["qualification_authority_id"] = "OWNER-1"
        seal(r, "qualification_digest")
        self.assertIn(
            "QUALIFICATION_SELF_AUTHORITY_FORBIDDEN",
            validate_governed_qualification(r),
        )

    def test_governed_qualification_prohibits_self_verifier(self):
        r = valid_qualification()
        r["verifier_mechanism_id"] = "MECH-1"
        seal(r, "qualification_digest")
        self.assertIn(
            "QUALIFICATION_SELF_VERIFIER_FORBIDDEN",
            validate_governed_qualification(r),
        )

    def test_genesis_scope_exact_pair_match_passes(self):
        scope = valid_genesis_scope()
        self.assertEqual(validate_genesis_trusted_scope(scope), [])
        result = genesis_scope_match(
            scope, object_id="BOOTSTRAP-VERIFIER", content_digest=D1
        )
        self.assertTrue(result["matched"])
        self.assertIsNone(result["endpoint"])

    def test_genesis_scope_cross_matching_is_rejected(self):
        scope = valid_genesis_scope()
        result = genesis_scope_match(
            scope, object_id="BOOTSTRAP-VERIFIER", content_digest=D2
        )
        self.assertFalse(result["matched"])
        self.assertEqual(result["endpoint"], GENESIS_TRUST_SCOPE_REJECTION)

    def test_genesis_scope_duplicate_object_id_is_rejected(self):
        scope = valid_genesis_scope()
        scope["trusted_objects"].append(
            {"object_id": "BOOTSTRAP-VERIFIER", "content_digest": D3}
        )
        scope["trusted_object_pair_set_digest"] = digest(
            sorted(
                scope["trusted_objects"],
                key=lambda x: (x["object_id"], x["content_digest"]),
            )
        )
        seal(scope, "scope_digest")
        self.assertIn(
            "GENESIS_SCOPE_OBJECT_ID_AMBIGUOUS:BOOTSTRAP-VERIFIER",
            validate_genesis_trusted_scope(scope),
        )


if __name__ == "__main__":
    unittest.main()
