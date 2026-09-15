from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_authority import (
    MANDATORY_SEPARATION_PAIRS,
    REQUIRED_ROLE_CLASSES,
    authority_construction_frontier,
    validate_review_governance_root,
    validate_role_authority_registry,
    validate_role_record,
)


def seal(record, field):
    record[field] = canonical_hash({k: v for k, v in record.items() if k != field})
    return record


def proof(a, b, result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"P-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "a" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["ROOT-1", "ROOT-2"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def role(role_class, domain):
    return seal({
        "schema_version": 1,
        "role_id": f"ROLE-{role_class}-{domain}",
        "role_class": role_class,
        "control_domain_id": domain,
        "generation_id": "GEN-1",
        "currentness_state": "CURRENT",
        "authority_origin": "REVIEW_GOVERNANCE_ROOT",
        "candidate_controlled": False,
        "appointment_record_digest": "b" * 64,
        "record_digest": "",
    }, "record_digest")


def valid_registry():
    roles = []
    domains = {}
    for i, role_class in enumerate(sorted(REQUIRED_ROLE_CLASSES), 1):
        domain = f"D{i}"
        domains[role_class] = domain
        roles.append(role(role_class, domain))
    proofs = []
    needed = set()
    for a, b in MANDATORY_SEPARATION_PAIRS:
        needed.add(tuple(sorted((domains[a], domains[b]))))
    for a, b in sorted(needed):
        proofs.append(proof(a, b))
    bundle = {
        "schema_version": 1,
        "generation_id": "GEN-1",
        "root_id": "ROOT-GOV",
        "roles": roles,
        "authority_effect": "NONE_EVIDENCE_ONLY",
        "registry_digest": "",
    }
    seal(bundle, "registry_digest")
    return bundle, proofs, domains


def valid_root():
    root = {
        "schema_version": 1,
        "root_id": "ROOT-GOV",
        "generation_id": "GEN-1",
        "genesis_record_digest": "c" * 64,
        "terminal_residual_trust_declared": True,
        "self_qualified_by_descendant_machinery": False,
        "candidate_controlled": False,
        "threshold": 2,
        "threshold_members": [
            {"authority_id": "A1", "control_domain_id": "DROOT1", "currentness_state": "CURRENT"},
            {"authority_id": "A2", "control_domain_id": "DROOT2", "currentness_state": "CURRENT"},
        ],
        "authority_effect": "NONE_EVIDENCE_ONLY",
        "record_digest": "",
    }
    seal(root, "record_digest")
    return root, [proof("DROOT1", "DROOT2")]


class RootTests(unittest.TestCase):
    def test_valid_root_requires_pairwise_independence(self):
        root, proofs = valid_root()
        self.assertTrue(validate_review_governance_root(root, proofs)["valid"])

    def test_root_missing_independence_proof_blocks(self):
        root, _ = valid_root()
        out = validate_review_governance_root(root, [])
        self.assertTrue(any("THRESHOLD_INDEPENDENCE_PROOF_MISSING" in x for x in out["problems"]))

    def test_root_unproven_independence_blocks(self):
        root, _ = valid_root()
        out = validate_review_governance_root(root, [proof("DROOT1", "DROOT2", "INDEPENDENCE_UNPROVEN")])
        self.assertTrue(any("THRESHOLD_INDEPENDENCE_UNPROVEN" in x for x in out["problems"]))

    def test_root_candidate_control_forbidden(self):
        root, proofs = valid_root()
        root["candidate_controlled"] = True
        seal(root, "record_digest")
        self.assertIn("REVIEW_ROOT_CANDIDATE_CONTROL_FORBIDDEN",
                      validate_review_governance_root(root, proofs)["problems"])

    def test_root_descendant_self_qualification_forbidden(self):
        root, proofs = valid_root()
        root["self_qualified_by_descendant_machinery"] = True
        seal(root, "record_digest")
        self.assertIn("REVIEW_ROOT_DESCENDANT_SELF_QUALIFICATION_FORBIDDEN",
                      validate_review_governance_root(root, proofs)["problems"])


class RegistryTests(unittest.TestCase):
    def test_role_record_candidate_control_rejected(self):
        r = role("PROJECTION_COMPILER", "D1")
        r["candidate_controlled"] = True
        seal(r, "record_digest")
        self.assertIn("ROLE_AUTHORITY_CANDIDATE_CONTROL_FORBIDDEN", validate_role_record(r)["problems"])

    def test_complete_registry_passes(self):
        bundle, proofs, _ = valid_registry()
        out = validate_role_authority_registry(bundle, proofs)
        self.assertTrue(out["valid"], out["problems"])
        self.assertEqual(out["present_role_class_count"], len(REQUIRED_ROLE_CLASSES))

    def test_missing_required_role_class_blocks(self):
        bundle, proofs, _ = valid_registry()
        bundle["roles"] = [r for r in bundle["roles"] if r["role_class"] != "ADJUDICATION_AUTHORITY"]
        seal(bundle, "registry_digest")
        out = validate_role_authority_registry(bundle, proofs)
        self.assertIn("ROLE_REGISTRY_REQUIRED_CLASS_MISSING:ADJUDICATION_AUTHORITY", out["problems"])

    def test_projection_compiler_verifier_same_domain_blocks(self):
        bundle, proofs, domains = valid_registry()
        compiler_domain = domains["PROJECTION_COMPILER"]
        for r in bundle["roles"]:
            if r["role_class"] == "PROJECTION_VERIFIER":
                r["control_domain_id"] = compiler_domain
                seal(r, "record_digest")
        seal(bundle, "registry_digest")
        out = validate_role_authority_registry(bundle, proofs)
        self.assertTrue(any("ROLE_REGISTRY_CONTROL_DOMAIN_COLLAPSE:PROJECTION_COMPILER:PROJECTION_VERIFIER" in x
                            for x in out["problems"]))

    def test_missing_separation_proof_blocks(self):
        bundle, proofs, domains = valid_registry()
        target = frozenset((domains["PROJECTION_COMPILER"], domains["PROJECTION_VERIFIER"]))
        reduced = [p for p in proofs if frozenset((p["subject_a"], p["subject_b"])) != target]
        out = validate_role_authority_registry(bundle, reduced)
        self.assertTrue(any("ROLE_REGISTRY_SEPARATION_PROOF_MISSING:PROJECTION_COMPILER:PROJECTION_VERIFIER" in x
                            for x in out["problems"]))

    def test_unproven_separation_blocks(self):
        bundle, proofs, domains = valid_registry()
        target = frozenset((domains["REVIEW_SET_AUTHORITY"], domains["ADJUDICATION_AUTHORITY"]))
        changed = []
        for p in proofs:
            if frozenset((p["subject_a"], p["subject_b"])) == target:
                changed.append(proof(p["subject_a"], p["subject_b"], "INDEPENDENCE_UNPROVEN"))
            else:
                changed.append(p)
        out = validate_role_authority_registry(bundle, changed)
        self.assertTrue(any("ROLE_REGISTRY_INDEPENDENCE_UNPROVEN:REVIEW_SET_AUTHORITY:ADJUDICATION_AUTHORITY" in x
                            for x in out["problems"]))

    def test_role_generation_mismatch_blocks(self):
        bundle, proofs, _ = valid_registry()
        bundle["roles"][0]["generation_id"] = "GEN-2"
        seal(bundle["roles"][0], "record_digest")
        seal(bundle, "registry_digest")
        self.assertTrue(any("ROLE_REGISTRY_GENERATION_MISMATCH" in x
                            for x in validate_role_authority_registry(bundle, proofs)["problems"]))

    def test_registry_digest_tamper_rejected(self):
        bundle, proofs, _ = valid_registry()
        bundle["root_id"] = "ROOT-OTHER"
        self.assertIn("ROLE_REGISTRY_DIGEST_MISMATCH",
                      validate_role_authority_registry(bundle, proofs)["problems"])

    def test_frontier_non_authoritative(self):
        f = authority_construction_frontier()
        self.assertFalse(f["qualified"])
        self.assertEqual(f["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
