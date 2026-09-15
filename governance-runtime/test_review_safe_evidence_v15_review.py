from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_review import (
    review_execution_construction_frontier,
    validate_authenticated_review_response_receipt,
    validate_clean_room_session_attestation,
    validate_reviewer_qualification,
    validate_sealed_review_snapshot,
    validate_snapshot_witness_bundle,
)


def seal(record, field):
    record[field] = canonical_hash({k: v for k, v in record.items() if k != field})
    return record


def independence(a, b, result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"P-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "1" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["ROOT-A", "ROOT-B"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def snapshot():
    return seal({
        "schema_version": 1,
        "snapshot_id": "S1",
        "candidate_id": "C1",
        "candidate_commit": "a" * 40,
        "candidate_tree_digest": "b" * 64,
        "generation_id": "GEN-1",
        "writer_id": "WRITER-1",
        "writer_control_domain_id": "D-WRITER",
        "candidate_control_domain_id": "D-CANDIDATE",
        "content_root_digest": "c" * 64,
        "raw_evidence_root_digest": "d" * 64,
        "obligation_graph_digest": "e" * 64,
        "disclosure_catalog_digest": "f" * 64,
        "monitor_certificate_digest": "1" * 64,
        "currentness_vector_digest": "2" * 64,
        "state": "SEALED",
        "atomic_seal": True,
        "mixed_state_detected": False,
        "rollback_or_fork_detected": False,
        "reconciliation_required": False,
        "currentness_state": "CURRENT",
        "sealed_sequence": 100,
        "predecessor_snapshot_digest": "GENESIS",
        "snapshot_digest": "",
    }, "snapshot_digest")


def witness_bundle(s):
    rows = []
    for wid, domain in (("W1", "D-W1"), ("W2", "D-W2")):
        rows.append(seal({
            "witness_id": wid,
            "control_domain_id": domain,
            "candidate_controlled": False,
            "currentness_state": "CURRENT",
            "snapshot_id": s["snapshot_id"],
            "snapshot_digest": s["snapshot_digest"],
            "anchor_digest": "3" * 64,
            "record_digest": "",
        }, "record_digest"))
    return seal({
        "schema_version": 1,
        "bundle_id": "WB-1",
        "snapshot_id": s["snapshot_id"],
        "snapshot_digest": s["snapshot_digest"],
        "generation_id": s["generation_id"],
        "anchor_id": "ANCHOR-1",
        "anchor_digest": "3" * 64,
        "anchor_currentness_state": "CURRENT",
        "threshold_control_domains": 2,
        "witnesses": rows,
        "bundle_digest": "",
    }, "bundle_digest")


def clean_room(s, *, assurance="INDEPENDENTLY_VERIFIABLE_PROVIDER_ISOLATION",
               transport="PLATFORM_AUTHENTICATED_API"):
    return seal({
        "schema_version": 1,
        "session_id": "SESSION-1",
        "reviewer_id": "R1",
        "provider_id": "anthropic",
        "model_id": "claude-sonnet",
        "transport_id": "TRANSPORT-1",
        "transport_class": transport,
        "context_isolation_method": "fresh-provider-session-with-external-attestation",
        "provider_context_isolation_assurance": assurance,
        "snapshot_id": s["snapshot_id"],
        "snapshot_digest": s["snapshot_digest"],
        "content_root_digest": s["content_root_digest"],
        "package_digest": "4" * 64,
        "fresh_session": True,
        "prior_project_review_findings_absent": True,
        "post_review_finding_artifacts_excluded": True,
        "provider_identity_authenticated": True,
        "currentness_state": "CURRENT",
        "attestation_digest": "",
    }, "attestation_digest")


def qualification(*, expires=200):
    return seal({
        "schema_version": 1,
        "qualification_id": "Q1",
        "reviewer_id": "R1",
        "provider_id": "anthropic",
        "model_id": "claude-sonnet",
        "role": "INDEPENDENT_REVIEWER",
        "authority_id": "AUTH-REVIEW",
        "authority_control_domain_id": "D-AUTH",
        "reviewer_control_domain_id": "D-REVIEWER",
        "generation_id": "GEN-1",
        "candidate_controlled": False,
        "provider_identity_authenticated": True,
        "authority_independence_result": "INDEPENDENT",
        "currentness_state": "CURRENT",
        "issued_sequence": 50,
        "expires_sequence": expires,
        "policy_digest": "5" * 64,
        "qualification_evidence_digest": "6" * 64,
        "qualification_digest": "",
    }, "qualification_digest")


def receipt(s, cr, q, *, dims=None, disposition="PASS"):
    dims = dims or ["AUTHORITY_PATH", "EVIDENCE_COMPLETENESS"]
    rows = [{
        "dimension_id": d,
        "status": "SUPPORTED",
        "assessment_digest": canonical_hash({"dimension": d, "assessment": "supported"}),
    } for d in dims]
    r = {
        "schema_version": 1,
        "review_id": "REV-1",
        "snapshot_id": s["snapshot_id"],
        "snapshot_digest": s["snapshot_digest"],
        "content_root_digest": s["content_root_digest"],
        "reviewer_id": q["reviewer_id"],
        "session_id": cr["session_id"],
        "provider_id": q["provider_id"],
        "model_id": q["model_id"],
        "transport_class": cr["transport_class"],
        "qualification_digest": q["qualification_digest"],
        "clean_room_attestation_digest": cr["attestation_digest"],
        "response_digest": "7" * 64,
        "content_receipt_digest": "8" * 64,
        "authenticated_transport_receipt": True,
        "exact_response_bytes_bound": True,
        "received_sequence": 120,
        "currentness_state": "CURRENT",
        "dimensions": rows,
        "complete": True,
        "disposition": disposition,
        "receipt_digest": "",
    }
    return seal(r, "receipt_digest")


class SnapshotTests(unittest.TestCase):
    def test_valid_sealed_snapshot(self):
        out = validate_sealed_review_snapshot(snapshot())
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["reviewable"])
        self.assertFalse(out["qualified"])

    def test_unsealed_snapshot_rejected(self):
        s = snapshot(); s["state"] = "PREPARING"; seal(s, "snapshot_digest")
        self.assertIn("REVIEW_SNAPSHOT_NOT_SEALED", validate_sealed_review_snapshot(s)["problems"])

    def test_mixed_snapshot_rejected(self):
        s = snapshot(); s["mixed_state_detected"] = True; seal(s, "snapshot_digest")
        self.assertIn("REVIEW_SNAPSHOT_MIXED_STATE_FORBIDDEN", validate_sealed_review_snapshot(s)["problems"])

    def test_rollback_snapshot_rejected(self):
        s = snapshot(); s["rollback_or_fork_detected"] = True; seal(s, "snapshot_digest")
        self.assertIn("REVIEW_SNAPSHOT_ROLLBACK_OR_FORK_FORBIDDEN", validate_sealed_review_snapshot(s)["problems"])

    def test_writer_candidate_domain_collapse_rejected(self):
        s = snapshot(); s["writer_control_domain_id"] = s["candidate_control_domain_id"]; seal(s, "snapshot_digest")
        self.assertIn("REVIEW_SNAPSHOT_WRITER_CANDIDATE_DOMAIN_COLLAPSE", validate_sealed_review_snapshot(s)["problems"])


class WitnessTests(unittest.TestCase):
    def test_valid_independent_witness_bundle(self):
        s = snapshot(); b = witness_bundle(s)
        out = validate_snapshot_witness_bundle(b, snapshot=s, independence_proofs=[independence("D-W1", "D-W2")], forbidden_control_domains=["D-ROOT", "D-ADJUDICATOR"])
        self.assertTrue(out["valid"], out["problems"]); self.assertEqual(out["control_domain_count"], 2)

    def test_candidate_domain_witness_rejected(self):
        s = snapshot(); b = witness_bundle(s); b["witnesses"][0]["control_domain_id"] = "D-CANDIDATE"; seal(b["witnesses"][0], "record_digest"); seal(b, "bundle_digest")
        out = validate_snapshot_witness_bundle(b, snapshot=s, independence_proofs=[independence("D-CANDIDATE", "D-W2")])
        self.assertTrue(any("SNAPSHOT_WITNESS_FORBIDDEN_CONTROL_DOMAIN" in x for x in out["problems"]))

    def test_witness_digest_mismatch_rejected(self):
        s = snapshot(); b = witness_bundle(s); b["witnesses"][0]["snapshot_digest"] = "9" * 64; seal(b["witnesses"][0], "record_digest"); seal(b, "bundle_digest")
        out = validate_snapshot_witness_bundle(b, snapshot=s, independence_proofs=[independence("D-W1", "D-W2")])
        self.assertTrue(any("SNAPSHOT_WITNESS_DIGEST_MISMATCH" in x for x in out["problems"]))

    def test_missing_witness_independence_proof_blocks(self):
        s = snapshot(); out = validate_snapshot_witness_bundle(witness_bundle(s), snapshot=s, independence_proofs=[])
        self.assertIn("SNAPSHOT_WITNESS_INDEPENDENCE_PROOF_MISSING:D-W1:D-W2", out["problems"])

    def test_witness_quorum_fail_closed(self):
        s = snapshot(); b = witness_bundle(s); b["threshold_control_domains"] = 3; seal(b, "bundle_digest")
        out = validate_snapshot_witness_bundle(b, snapshot=s, independence_proofs=[independence("D-W1", "D-W2")])
        self.assertIn("SNAPSHOT_WITNESS_DOMAIN_QUORUM_INSUFFICIENT:2:3", out["problems"])


class CleanRoomTests(unittest.TestCase):
    def test_independently_verifiable_clean_room_is_promotable_evidence(self):
        s = snapshot(); out = validate_clean_room_session_attestation(clean_room(s), snapshot=s)
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["promotable"])

    def test_manual_paste_is_valid_external_evidence_but_nonpromotable(self):
        s = snapshot(); cr = clean_room(s, assurance="UNAVAILABLE", transport="MANUAL_PASTE_EXTERNAL_EVIDENCE_ONLY")
        out = validate_clean_room_session_attestation(cr, snapshot=s)
        self.assertTrue(out["valid"], out["problems"]); self.assertFalse(out["promotable"])
        self.assertEqual(out["nonpromotable_reason"], "CONTEXT_ISOLATION_NOT_INDEPENDENTLY_VERIFIABLE")

    def test_provider_isolation_unavailable_blocks_promotion(self):
        s = snapshot(); out = validate_clean_room_session_attestation(clean_room(s, assurance="UNAVAILABLE"), snapshot=s)
        self.assertTrue(out["valid"], out["problems"]); self.assertFalse(out["promotable"])

    def test_nonfresh_session_rejected(self):
        s = snapshot(); cr = clean_room(s); cr["fresh_session"] = False; seal(cr, "attestation_digest")
        self.assertIn("CLEAN_ROOM_FRESH_SESSION_REQUIRED", validate_clean_room_session_attestation(cr, snapshot=s)["problems"])

    def test_prior_findings_contamination_rejected(self):
        s = snapshot(); cr = clean_room(s); cr["prior_project_review_findings_absent"] = False; seal(cr, "attestation_digest")
        self.assertIn("CLEAN_ROOM_PRIOR_FINDINGS_ABSENCE_REQUIRED", validate_clean_room_session_attestation(cr, snapshot=s)["problems"])


class ReviewerQualificationTests(unittest.TestCase):
    def test_current_reviewer_qualification_valid(self):
        out = validate_reviewer_qualification(qualification(), current_sequence=120)
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["current"])

    def test_expired_reviewer_qualification_rejected(self):
        out = validate_reviewer_qualification(qualification(expires=100), current_sequence=120)
        self.assertIn("REVIEWER_QUALIFICATION_EXPIRED", out["problems"])

    def test_reviewer_authority_domain_collapse_rejected(self):
        q = qualification(); q["reviewer_control_domain_id"] = q["authority_control_domain_id"]; seal(q, "qualification_digest")
        self.assertIn("REVIEWER_QUALIFICATION_AUTHORITY_DOMAIN_COLLAPSE", validate_reviewer_qualification(q, current_sequence=120)["problems"])

    def test_candidate_controlled_qualification_rejected(self):
        q = qualification(); q["candidate_controlled"] = True; seal(q, "qualification_digest")
        self.assertIn("REVIEWER_QUALIFICATION_CANDIDATE_CONTROL_FORBIDDEN", validate_reviewer_qualification(q, current_sequence=120)["problems"])


class ReceiptTests(unittest.TestCase):
    mandatory = ["AUTHORITY_PATH", "EVIDENCE_COMPLETENESS"]

    def valid_parts(self):
        s = snapshot(); cr = clean_room(s); q = qualification(); r = receipt(s, cr, q)
        return s, cr, q, r

    def test_authenticated_exact_receipt_valid(self):
        s, cr, q, r = self.valid_parts()
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["review_evidence_ready"]); self.assertFalse(out["qualified"])

    def test_missing_mandatory_dimension_rejected(self):
        s, cr, q, _ = self.valid_parts(); r = receipt(s, cr, q, dims=["AUTHORITY_PATH"])
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertTrue(any("REVIEW_RESPONSE_MANDATORY_DIMENSION_MISSING:EVIDENCE_COMPLETENESS" in x for x in out["problems"]))

    def test_snapshot_rebinding_rejected(self):
        s, cr, q, r = self.valid_parts(); r["snapshot_digest"] = "9" * 64; seal(r, "receipt_digest")
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertIn("REVIEW_RECEIPT_SNAPSHOT_DIGEST_MISMATCH", out["problems"])

    def test_manual_paste_cannot_become_authoritative_receipt(self):
        s = snapshot(); cr = clean_room(s, assurance="UNAVAILABLE", transport="MANUAL_PASTE_EXTERNAL_EVIDENCE_ONLY"); q = qualification(); r = receipt(s, cr, q)
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertIn("REVIEW_RECEIPT_CLEAN_ROOM_NONPROMOTABLE", out["problems"])

    def test_expired_qualification_blocks_receipt_at_decision_time(self):
        s = snapshot(); cr = clean_room(s); q = qualification(expires=125); r = receipt(s, cr, q)
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertTrue(any("REVIEWER_QUALIFICATION_EXPIRED" in x for x in out["problems"]))

    def test_provider_mismatch_rejected(self):
        s, cr, q, r = self.valid_parts(); r["provider_id"] = "other-provider"; seal(r, "receipt_digest")
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertIn("REVIEW_RECEIPT_PROVIDER_MISMATCH", out["problems"])

    def test_response_bytes_must_be_exactly_bound(self):
        s, cr, q, r = self.valid_parts(); r["exact_response_bytes_bound"] = False; seal(r, "receipt_digest")
        out = validate_authenticated_review_response_receipt(r, snapshot=s, clean_room_attestation=cr, reviewer_qualification=q, mandatory_dimensions=self.mandatory, current_sequence=130)
        self.assertIn("REVIEW_RECEIPT_EXACT_RESPONSE_BINDING_REQUIRED", out["problems"])

    def test_frontier_non_authoritative(self):
        f = review_execution_construction_frontier()
        self.assertEqual(f["implemented_surfaces"], [20, 21, 22, 23, 24]); self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
