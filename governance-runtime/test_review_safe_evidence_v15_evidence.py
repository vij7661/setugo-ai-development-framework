from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_evidence import (
    evidence_construction_frontier,
    validate_evidence_registry,
    validate_na_challenge,
    validate_not_applicable_proof,
    validate_observation_applicability,
    validate_raw_evidence_record,
)


def seal(r, field):
    r[field] = canonical_hash({k: v for k, v in r.items() if k != field})
    return r


def independence(a="D-PROOF", b="D-VERIFY", result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"IP-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "1" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["ROOT-P", "ROOT-V"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def na_proof(*, proof_id="NA-1", obligation="O2", subject="SUB-2", expires=100,
             contradiction="NONE", result="NOT_APPLICABLE_SUPPORTED"):
    return seal({
        "schema_version": 1,
        "proof_id": proof_id,
        "obligation_id": obligation,
        "subject_id": subject,
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "proof_authority_id": "PA-1",
        "proof_control_domain_id": "D-PROOF",
        "verifier_id": "PV-1",
        "verifier_control_domain_id": "D-VERIFY",
        "challenge_evidence_digests": ["2" * 64],
        "source_digest": "3" * 64,
        "issued_sequence": 10,
        "expires_sequence": expires,
        "currentness_rule": "SEQUENCE_BOUND",
        "result": result,
        "contradiction_state": contradiction,
        "candidate_self_authored": False,
        "proof_digest": "",
    }, "proof_digest")


def evidence(eid, obligation, state, predecessor="GENESIS", proof=None):
    r = {
        "schema_version": 1,
        "evidence_id": eid,
        "obligation_id": obligation,
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "environment_id": "ENV-1",
        "capture_authority_id": "CAP-1",
        "capture_control_domain_id": "D-CAP",
        "source_identity": f"SRC-{obligation}",
        "source_digest": "4" * 64,
        "currentness_state": "CURRENT",
        "state": state,
        "candidate_self_captured": False,
        "predecessor_record_digest": predecessor,
        "payload_digest": None,
        "not_applicable_proof_id": None,
        "not_applicable_proof_digest": None,
        "record_digest": "",
    }
    if state == "CAPTURED":
        r["payload_digest"] = "5" * 64
    elif state == "NOT_APPLICABLE_WITH_GOVERNED_PROOF" and proof is not None:
        r["not_applicable_proof_id"] = proof["proof_id"]
        r["not_applicable_proof_digest"] = proof["proof_digest"]
    return seal(r, "record_digest")


def challenge(proof, state="OPEN", expires=100):
    r = {
        "schema_version": 1,
        "challenge_id": "CH-1",
        "proof_id": proof["proof_id"],
        "obligation_id": proof["obligation_id"],
        "snapshot_id": proof["snapshot_id"],
        "generation_id": proof["generation_id"],
        "challenger_id": "CHALLENGER-1",
        "verifier_id": "CHV-1",
        "verifier_independence_result": "INDEPENDENT",
        "state": state,
        "opened_sequence": 20,
        "expires_sequence": expires,
        "resolution_evidence_digest": None,
        "resolution_verifier_id": None,
        "challenge_digest": "",
    }
    if state in {"RESOLVED_SUPPORTED", "RESOLVED_REJECTED"}:
        r["resolution_evidence_digest"] = "6" * 64
        r["resolution_verifier_id"] = "CHV-2"
    return seal(r, "challenge_digest")


def valid_registry():
    proof = na_proof()
    ip = independence()
    e1 = evidence("E1", "O1", "CAPTURED")
    e2 = evidence("E2", "O2", "NOT_APPLICABLE_WITH_GOVERNED_PROOF",
                  predecessor=e1["record_digest"], proof=proof)
    bundle = {
        "schema_version": 1,
        "registry_id": "REG-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "records": [e1, e2],
        "registry_head_digest": e2["record_digest"],
        "registry_digest": "",
    }
    seal(bundle, "registry_digest")
    return bundle, proof, ip


class RawEvidenceTests(unittest.TestCase):
    def test_captured_evidence_valid(self):
        self.assertTrue(validate_raw_evidence_record(evidence("E1", "O1", "CAPTURED"))["valid"])

    def test_candidate_self_capture_rejected(self):
        r = evidence("E1", "O1", "CAPTURED")
        r["candidate_self_captured"] = True
        seal(r, "record_digest")
        self.assertIn("RAW_EVIDENCE_CANDIDATE_SELF_CAPTURE_FORBIDDEN",
                      validate_raw_evidence_record(r)["problems"])

    def test_name_only_na_without_proof_rejected(self):
        r = evidence("E1", "O1", "NOT_APPLICABLE_WITH_GOVERNED_PROOF")
        out = validate_raw_evidence_record(r)
        self.assertIn("RAW_EVIDENCE_NA_PROOF_ID_REQUIRED", out["problems"])
        self.assertIn("RAW_EVIDENCE_NA_PROOF_DIGEST_REQUIRED", out["problems"])

    def test_missing_evidence_may_be_recorded_without_fake_payload(self):
        r = evidence("E1", "O1", "EVIDENCE_MISSING")
        self.assertTrue(validate_raw_evidence_record(r)["valid"])

    def test_missing_evidence_with_payload_rejected(self):
        r = evidence("E1", "O1", "EVIDENCE_MISSING")
        r["payload_digest"] = "7" * 64
        seal(r, "record_digest")
        self.assertIn("RAW_EVIDENCE_MISSING_MUST_NOT_CARRY_PAYLOAD",
                      validate_raw_evidence_record(r)["problems"])


class NotApplicableTests(unittest.TestCase):
    def test_valid_na_proof(self):
        out = validate_not_applicable_proof(
            na_proof(), independence_proof=independence(), current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])

    def test_expired_na_proof_blocks(self):
        out = validate_not_applicable_proof(
            na_proof(expires=40), independence_proof=independence(), current_sequence=50)
        self.assertIn("N_A_PROOF_EXPIRED", out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_unproven_verifier_independence_blocks(self):
        out = validate_not_applicable_proof(
            na_proof(), independence_proof=independence(result="INDEPENDENCE_UNPROVEN"),
            current_sequence=50)
        self.assertIn("N_A_PROOF_VERIFIER_INDEPENDENCE_REQUIRED", out["problems"])

    def test_shared_control_domain_na_proof_blocks(self):
        proof = na_proof()
        proof["verifier_control_domain_id"] = "D-PROOF"
        seal(proof, "proof_digest")
        ip = independence("D-PROOF", "D-PROOF", result="NOT_INDEPENDENT", shared=["ROOT-X"])
        out = validate_not_applicable_proof(proof, independence_proof=ip, current_sequence=50)
        self.assertIn("N_A_PROOF_CONTROL_DOMAIN_COLLAPSE", out["problems"])

    def test_contradicted_na_proof_blocks(self):
        out = validate_not_applicable_proof(
            na_proof(contradiction="CONTRADICTED_BY_OBSERVATION"),
            independence_proof=independence(), current_sequence=50)
        self.assertIn("N_A_PROOF_CONTRADICTED", out["problems"])

    def test_open_challenge_blocks_promotion(self):
        proof = na_proof()
        out = validate_na_challenge(challenge(proof, "OPEN"), proof=proof, current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_rejected_challenge_blocks_promotion(self):
        proof = na_proof()
        out = validate_na_challenge(challenge(proof, "RESOLVED_REJECTED"), proof=proof, current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_expired_unresolved_challenge_rejected(self):
        proof = na_proof()
        out = validate_na_challenge(challenge(proof, "OPEN", expires=30), proof=proof, current_sequence=50)
        self.assertIn("N_A_CHALLENGE_EXPIRED_UNRESOLVED", out["problems"])


class ObservationApplicabilityTests(unittest.TestCase):
    def observation(self, applicable):
        return seal({
            "schema_version": 1,
            "observation_source_id": "OBS-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "applicable": applicable,
            "record_digest": "",
        }, "record_digest")

    def test_applicable_observation_needs_no_waiver(self):
        out = validate_observation_applicability(
            self.observation(True), na_proof=None, independence_proof=None, current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])

    def test_omitted_observation_without_na_proof_blocks(self):
        out = validate_observation_applicability(
            self.observation(False), na_proof=None, independence_proof=None, current_sequence=50)
        self.assertIn("OBSERVATION_APPLICABILITY_N_A_PROOF_REQUIRED", out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_omitted_observation_with_wrong_subject_proof_blocks(self):
        proof = na_proof(subject="OTHER")
        out = validate_observation_applicability(
            self.observation(False), na_proof=proof, independence_proof=independence(), current_sequence=50)
        self.assertIn("OBSERVATION_APPLICABILITY_N_A_SUBJECT_MISMATCH", out["problems"])

    def test_omitted_observation_with_governed_proof_passes_structure(self):
        proof = na_proof(subject="OBS-1")
        out = validate_observation_applicability(
            self.observation(False), na_proof=proof, independence_proof=independence(), current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])


class EvidenceRegistryTests(unittest.TestCase):
    def test_valid_registry_with_capture_and_current_na_is_not_blocked(self):
        bundle, proof, ip = valid_registry()
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2"],
            na_proofs={proof["proof_id"]: (proof, ip)}, challenges={}, current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])
        self.assertFalse(out["promotion_blocked"], out["blocking_reasons"])

    def test_missing_expected_obligation_blocks(self):
        bundle, proof, ip = valid_registry()
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2", "O3"],
            na_proofs={proof["proof_id"]: (proof, ip)}, challenges={}, current_sequence=50)
        self.assertIn("EVIDENCE_REGISTRY_OBLIGATION_RECORD_MISSING:O3", out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_explicit_missing_evidence_blocks_without_being_fake_capture(self):
        e1 = evidence("E1", "O1", "EVIDENCE_MISSING")
        bundle = {
            "schema_version": 1, "registry_id": "REG-M", "candidate_id": "C1",
            "snapshot_id": "S1", "generation_id": "GEN-1", "records": [e1],
            "registry_head_digest": e1["record_digest"], "registry_digest": "",
        }
        seal(bundle, "registry_digest")
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1"], na_proofs={}, challenges={}, current_sequence=50)
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["promotion_blocked"])
        self.assertIn("EVIDENCE_MISSING:O1", out["blocking_reasons"])

    def test_open_na_challenge_blocks_registry(self):
        bundle, proof, ip = valid_registry()
        ch = challenge(proof, "OPEN")
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2"],
            na_proofs={proof["proof_id"]: (proof, ip)},
            challenges={proof["proof_id"]: [ch]}, current_sequence=50)
        self.assertTrue(out["promotion_blocked"])
        self.assertTrue(any(x.startswith("N_A_CHALLENGE_BLOCKING:O2") for x in out["blocking_reasons"]))

    def test_predecessor_tamper_blocks(self):
        bundle, proof, ip = valid_registry()
        bundle["records"][1]["predecessor_record_digest"] = "9" * 64
        seal(bundle["records"][1], "record_digest")
        bundle["registry_head_digest"] = bundle["records"][1]["record_digest"]
        seal(bundle, "registry_digest")
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2"],
            na_proofs={proof["proof_id"]: (proof, ip)}, challenges={}, current_sequence=50)
        self.assertTrue(any("EVIDENCE_REGISTRY_PREDECESSOR_MISMATCH:E2" in x for x in out["problems"]))

    def test_registry_head_replay_blocks(self):
        bundle, proof, ip = valid_registry()
        bundle["registry_head_digest"] = bundle["records"][0]["record_digest"]
        seal(bundle, "registry_digest")
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2"],
            na_proofs={proof["proof_id"]: (proof, ip)}, challenges={}, current_sequence=50)
        self.assertIn("EVIDENCE_REGISTRY_HEAD_DIGEST_MISMATCH", out["problems"])

    def test_underived_obligation_record_blocks(self):
        bundle, proof, ip = valid_registry()
        extra = evidence("E3", "O3", "CAPTURED", predecessor=bundle["records"][-1]["record_digest"])
        bundle["records"].append(extra)
        bundle["registry_head_digest"] = extra["record_digest"]
        seal(bundle, "registry_digest")
        out = validate_evidence_registry(
            bundle, expected_obligations=["O1", "O2"],
            na_proofs={proof["proof_id"]: (proof, ip)}, challenges={}, current_sequence=50)
        self.assertIn("EVIDENCE_REGISTRY_UNDERIVED_OBLIGATION:O3", out["problems"])

    def test_frontier_non_authoritative(self):
        f = evidence_construction_frontier()
        self.assertFalse(f["qualified"])
        self.assertEqual(f["implementation_qualification"], "NOT_CLAIMED")
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
