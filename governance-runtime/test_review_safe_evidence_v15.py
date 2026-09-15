from __future__ import annotations

import unittest

from review_safe_evidence_v15 import (
    assess_independence,
    canonical_hash,
    construction_frontier,
    promotion_independence_gate,
    validate_blocker_record,
    validate_challenge_certificate,
    validate_control_ancestry_edge,
    validate_control_domain,
    validate_control_domain_graph,
    validate_currentness_binding,
    validate_fenced_effect_token,
    validate_governed_proof,
    validate_independently_rooted_proof,
    validate_residual_trust_root,
    validate_reviewer_response_coverage,
)


def seal(record, field):
    record[field] = canonical_hash({k: v for k, v in record.items() if k != field})
    return record


def domain(did, roots):
    return seal({
        "schema_version": 1,
        "domain_id": did,
        "generation_id": "GEN-1",
        "authority_roots": list(roots),
        "currentness_state": "CURRENT",
        "record_digest": "",
    }, "record_digest")


def edge(child, parent):
    return seal({
        "schema_version": 1,
        "child_domain_id": child,
        "parent_root_id": parent,
        "influence_class": "ADMIN",
        "evidence_digest": "a" * 64,
        "record_digest": "",
    }, "record_digest")


def independence(a="A", b="B", result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"IP-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "b" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["ROOT-A", "ROOT-B"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


class CanonicalPrimitiveTests(unittest.TestCase):
    def test_control_domain_valid(self):
        self.assertTrue(validate_control_domain(domain("A", ["ROOT-A"]))["valid"])

    def test_control_domain_duplicate_root_rejected(self):
        r = domain("A", ["ROOT-A", "ROOT-A"])
        seal(r, "record_digest")
        self.assertIn("CONTROL_DOMAIN_AUTHORITY_ROOT_DUPLICATE", validate_control_domain(r)["problems"])

    def test_control_domain_digest_tamper_rejected(self):
        r = domain("A", ["ROOT-A"])
        r["generation_id"] = "GEN-2"
        self.assertIn("CONTROL_DOMAIN_RECORD_DIGEST_MISMATCH", validate_control_domain(r)["problems"])

    def test_ancestry_self_edge_rejected(self):
        r = edge("A", "A")
        self.assertIn("CONTROL_ANCESTRY_SELF_EDGE_FORBIDDEN", validate_control_ancestry_edge(r)["problems"])

    def test_graph_declared_roots_must_match_edges(self):
        result = validate_control_domain_graph([domain("A", ["ROOT-A"])], [])
        self.assertFalse(result["valid"])
        self.assertIn("CONTROL_DOMAIN_ROOT_SET_MISMATCH:A", result["problems"])

    def test_independence_disjoint_roots(self):
        ds = [domain("A", ["ROOT-A"]), domain("B", ["ROOT-B"])]
        es = [edge("A", "ROOT-A"), edge("B", "ROOT-B")]
        r = assess_independence(subject_a="A", subject_b="B", domains=ds, edges=es)
        self.assertEqual(r["result"], "INDEPENDENT")
        self.assertFalse(r["promotion_blocked"])

    def test_independence_shared_root_blocks(self):
        ds = [domain("A", ["ROOT-X"]), domain("B", ["ROOT-X"])]
        es = [edge("A", "ROOT-X"), edge("B", "ROOT-X")]
        r = assess_independence(subject_a="A", subject_b="B", domains=ds, edges=es)
        self.assertEqual(r["result"], "NOT_INDEPENDENT")
        self.assertTrue(r["promotion_blocked"])

    def test_independence_unknown_subject_blocks(self):
        ds = [domain("A", ["ROOT-A"])]
        es = [edge("A", "ROOT-A")]
        r = assess_independence(subject_a="A", subject_b="B", domains=ds, edges=es)
        self.assertEqual(r["result"], "INDEPENDENCE_UNPROVEN")
        self.assertTrue(r["promotion_blocked"])

    def test_independence_proof_cannot_claim_shared_root(self):
        r = independence(result="INDEPENDENT", shared=["ROOT-X"])
        self.assertIn("INDEPENDENCE_PROOF_INDEPENDENT_WITH_SHARED_ANCESTOR",
                      validate_independently_rooted_proof(r)["problems"])

    def test_global_independence_gate_missing_proof_blocks(self):
        r = promotion_independence_gate([("A", "B")], [])
        self.assertFalse(r["promotion_allowed"])

    def test_global_independence_gate_unproven_blocks(self):
        pr = independence(result="INDEPENDENCE_UNPROVEN")
        r = promotion_independence_gate([("A", "B")], [pr])
        self.assertFalse(r["promotion_allowed"])
        self.assertTrue(any("PROMOTION_BLOCKED_INDEPENDENCE_UNPROVEN" in x for x in r["problems"]))

    def test_global_independence_gate_exact_proof_passes(self):
        pr = independence()
        self.assertTrue(promotion_independence_gate([("A", "B")], [pr])["promotion_allowed"])


class ProofAndCurrentnessTests(unittest.TestCase):
    def test_residual_trust_root_valid(self):
        r = seal({
            "schema_version": 1,
            "root_id": "ROOT-1",
            "control_domain_id": "D-ROOT",
            "generation_id": "GEN-1",
            "scope": ["REVIEW_GOVERNANCE"],
            "accepted_limitations": ["ROOT_COLLUSION_RESIDUAL"],
            "currentness_state": "CURRENT",
            "record_digest": "",
        }, "record_digest")
        self.assertTrue(validate_residual_trust_root(r)["valid"])

    def test_governed_proof_requires_independent_verifier(self):
        r = {
            "schema_version": 1,
            "proof_id": "GP-1",
            "subject_id": "OBJ-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "proof_mechanism_id": "MECH-1",
            "evidence_digests": ["c" * 64],
            "verifier_id": "V1",
            "verifier_independence_result": "INDEPENDENCE_UNPROVEN",
            "currentness": "CURRENT",
            "result": "SUPPORTED",
            "candidate_self_authored": False,
            "proof_digest": "",
        }
        seal(r, "proof_digest")
        self.assertIn("GOVERNED_PROOF_VERIFIER_INDEPENDENCE_REQUIRED",
                      validate_governed_proof(r)["problems"])

    def test_challenge_certificate_expiry_blocks(self):
        r = {
            "schema_version": 1,
            "certificate_id": "CC-1",
            "challenge_type": "UNIVERSE_NEGATIVE_SPACE",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "mechanism_identity": "M1",
            "verifier_id": "V1",
            "source_root_digest": "d" * 64,
            "issued_sequence": 10,
            "expires_sequence": 20,
            "currentness_rule": "SEQ_LE_20",
            "result": "NO_NEW_OBLIGATION_FOUND",
            "verifier_independence_result": "INDEPENDENT",
            "candidate_self_authored": False,
            "certificate_digest": "",
        }
        seal(r, "certificate_digest")
        self.assertIn("CHALLENGE_CERTIFICATE_EXPIRED",
                      validate_challenge_certificate(r, current_sequence=21)["problems"])

    def test_currentness_requires_independent_verifier(self):
        r = {
            "schema_version": 1,
            "subject_id": "OBJ",
            "source_version": "1",
            "source_digest": "e" * 64,
            "observed_sequence": 1,
            "verifier_id": "V",
            "generation_id": "GEN",
            "verifier_independence_result": "NOT_INDEPENDENT",
            "state": "CURRENT",
            "binding_digest": "",
        }
        seal(r, "binding_digest")
        self.assertIn("CURRENTNESS_BINDING_VERIFIER_INDEPENDENCE_REQUIRED",
                      validate_currentness_binding(r)["problems"])


class ReviewAndEffectTests(unittest.TestCase):
    def response(self):
        r = {
            "schema_version": 1,
            "review_id": "REV-1",
            "snapshot_id": "S1",
            "reviewer_id": "R1",
            "session_id": "SESSION-1",
            "response_digest": "1" * 64,
            "content_receipt_digest": "2" * 64,
            "dimensions": [
                {"dimension_id": "A", "status": "SUPPORTED", "assessment_digest": "3" * 64},
                {"dimension_id": "B", "status": "SUPPORTED", "assessment_digest": "4" * 64},
            ],
            "complete": True,
            "disposition": "PASS",
            "receipt_digest": "",
        }
        seal(r, "receipt_digest")
        return r

    def test_positive_review_requires_every_mandatory_dimension(self):
        r = self.response()
        r["dimensions"].pop()
        seal(r, "receipt_digest")
        out = validate_reviewer_response_coverage(r, mandatory_dimensions=["A", "B"])
        self.assertFalse(out["valid"])
        self.assertIn("REVIEW_RESPONSE_MANDATORY_DIMENSION_MISSING:B", out["problems"])

    def test_positive_review_cannot_use_insufficient_dimension(self):
        r = self.response()
        r["dimensions"][1]["status"] = "INSUFFICIENT"
        seal(r, "receipt_digest")
        out = validate_reviewer_response_coverage(r, mandatory_dimensions=["A", "B"])
        self.assertIn("REVIEW_RESPONSE_POSITIVE_WITH_UNSUPPORTED_DIMENSION:B", out["problems"])

    def test_complete_positive_review_passes(self):
        self.assertTrue(validate_reviewer_response_coverage(
            self.response(), mandatory_dimensions=["A", "B"])["valid"])

    def test_blocker_resolution_requires_reopened_review_evidence(self):
        r = {
            "schema_version": 1,
            "blocker_id": "BL-1",
            "severity": "HIGH",
            "state": "RESOLVED_IN_REOPENED_REVIEW",
            "review_id": "REV-1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "evidence_digests": ["5" * 64],
            "opened_sequence": 1,
            "record_digest": "",
        }
        seal(r, "record_digest")
        out = validate_blocker_record(r)
        self.assertIn("BLOCKER_RECORD_RESOLUTION_REVIEW_REQUIRED", out["problems"])
        self.assertIn("BLOCKER_RECORD_RESOLUTION_EVIDENCE_REQUIRED", out["problems"])

    def token(self):
        r = {
            "schema_version": 1,
            "token_id": "TOK-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "ledger_head_digest": "6" * 64,
            "currentness_vector_digest": "7" * 64,
            "content_receipt_digest": "8" * 64,
            "nonce": "N-1",
            "expires_sequence": 100,
            "single_use": True,
            "token_digest": "",
        }
        seal(r, "token_digest")
        return r

    def expected(self):
        t = self.token()
        return {k: t[k] for k in (
            "candidate_id", "snapshot_id", "generation_id", "ledger_head_digest",
            "currentness_vector_digest", "content_receipt_digest"
        )}

    def test_fenced_token_replay_rejected(self):
        t = self.token()
        out = validate_fenced_effect_token(t, current_sequence=50,
                                           consumed_token_ids={"TOK-1"},
                                           expected=self.expected())
        self.assertIn("FENCED_TOKEN_REPLAYED", out["problems"])

    def test_fenced_token_expiry_rejected(self):
        t = self.token()
        out = validate_fenced_effect_token(t, current_sequence=101,
                                           consumed_token_ids=set(),
                                           expected=self.expected())
        self.assertIn("FENCED_TOKEN_EXPIRED", out["problems"])

    def test_fenced_token_context_drift_rejected(self):
        t = self.token()
        exp = self.expected()
        exp["generation_id"] = "GEN-2"
        out = validate_fenced_effect_token(t, current_sequence=50,
                                           consumed_token_ids=set(), expected=exp)
        self.assertIn("FENCED_TOKEN_CONTEXT_MISMATCH:generation_id", out["problems"])

    def test_fenced_token_valid_exact_context(self):
        t = self.token()
        out = validate_fenced_effect_token(t, current_sequence=50,
                                           consumed_token_ids=set(),
                                           expected=self.expected())
        self.assertTrue(out["valid"], out["problems"])

    def test_construction_frontier_non_authoritative(self):
        r = construction_frontier()
        self.assertFalse(r["qualified"])
        self.assertEqual(r["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(r["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
