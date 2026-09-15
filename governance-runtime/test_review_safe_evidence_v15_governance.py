from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_governance import (
    governance_construction_frontier,
    validate_adjudication_firewall,
    validate_blocker_ledger,
    validate_currentness_vector,
    validate_governance_generation,
    validate_residual_trust_state,
    validate_review_response_ledger,
)


def seal(record, field):
    record[field] = canonical_hash({k: v for k, v in record.items() if k != field})
    return record


def review_record(seq, prev, rid, state="VALIDATED"):
    return seal({
        "ledger_record_id": f"LR-{seq}",
        "ledger_sequence": seq,
        "predecessor_record_digest": prev,
        "review_id": rid,
        "reviewer_id": f"RV-{seq}",
        "session_id": f"S-{seq}",
        "snapshot_id": "SNAP-1",
        "response_receipt_digest": str(seq) * 64,
        "content_root_digest": "a" * 64,
        "state": state,
        "candidate_controlled": False,
        "record_digest": "",
    }, "record_digest")


def review_ledger():
    r1 = review_record(1, "GENESIS", "REV-1")
    r2 = review_record(2, r1["record_digest"], "REV-2")
    return seal({
        "schema_version": 1,
        "ledger_id": "RL-1",
        "generation_id": "GEN-1",
        "witness_id": "W-REVIEW",
        "witness_control_domain_id": "D-W-REVIEW",
        "witness_currentness_state": "CURRENT",
        "witness_independence_result": "INDEPENDENT",
        "candidate_controlled": False,
        "records": [r1, r2],
        "current_head_digest": r2["record_digest"],
        "witnessed_head_digest": r2["record_digest"],
        "ledger_digest": "",
    }, "ledger_digest")


def blocker_record(seq, prev, bid, state="OPEN_BLOCKER"):
    r = {
        "schema_version": 1,
        "blocker_id": bid,
        "review_id": "REV-1",
        "snapshot_id": "SNAP-1",
        "generation_id": "GEN-1",
        "severity": "HIGH",
        "state": state,
        "evidence_digests": ["b" * 64],
        "opened_sequence": 10 + seq,
        "ledger_sequence": seq,
        "predecessor_record_digest": prev,
        "record_digest": "",
    }
    if state == "RESOLVED_IN_REOPENED_REVIEW":
        r["resolution_review_id"] = "REV-REOPEN-2"
        r["resolution_evidence_digest"] = "c" * 64
    return seal(r, "record_digest")


def blocker_ledger(open_one=True):
    state = "OPEN_BLOCKER" if open_one else "RESOLVED_IN_REOPENED_REVIEW"
    r1 = blocker_record(1, "GENESIS", "B-1", state=state)
    return seal({
        "schema_version": 1,
        "ledger_id": "BL-1",
        "generation_id": "GEN-1",
        "witness_id": "W-BLOCK",
        "witness_control_domain_id": "D-W-BLOCK",
        "witness_currentness_state": "CURRENT",
        "witness_independence_result": "INDEPENDENT",
        "candidate_controlled": False,
        "records": [r1],
        "current_head_digest": r1["record_digest"],
        "witnessed_head_digest": r1["record_digest"],
        "ledger_digest": "",
    }, "ledger_digest")


def currentness_binding(subject, state="CURRENT"):
    return seal({
        "schema_version": 1,
        "subject_id": subject,
        "source_version": "v1",
        "source_digest": "d" * 64,
        "observed_sequence": 50,
        "verifier_id": "CV-1",
        "generation_id": "GEN-1",
        "state": state,
        "verifier_independence_result": "INDEPENDENT",
        "binding_digest": "",
    }, "binding_digest")


def currentness_vector():
    rows = [currentness_binding("SNAPSHOT"), currentness_binding("REVIEWER"), currentness_binding("LEDGERS")]
    return seal({
        "schema_version": 1,
        "vector_id": "CVEC-1",
        "generation_id": "GEN-1",
        "snapshot_id": "SNAP-1",
        "bindings": rows,
        "vector_digest": "",
    }, "vector_digest")


def generation(*, change_class="REVIEW_GOVERNANCE_ROOT", impact="MATERIAL_GOVERNANCE_CHANGE", blocked=False):
    return seal({
        "schema_version": 1,
        "generation_id": "GEN-2",
        "predecessor_generation_id": "GEN-1",
        "transition_id": "GT-1",
        "authority_id": "GA-1",
        "change_classes": [change_class],
        "impact_state": impact,
        "independent_nonimpact_proof_valid": impact == "PROVEN_NON_IMPACTING",
        "promotion_blocked": blocked,
        "change_set_digest": "e" * 64,
        "cumulative_generation_digest": "f" * 64,
        "transition_evidence_digest": "1" * 64,
        "witness_anchor_digest": "2" * 64,
        "witness_currentness_state": "CURRENT",
        "witness_independence_result": "INDEPENDENT",
        "candidate_controlled": False,
        "generation_record_digest": "",
    }, "generation_record_digest")


def residual_root(rid):
    return seal({
        "schema_version": 1,
        "root_id": rid,
        "control_domain_id": f"D-{rid}",
        "generation_id": "GEN-1",
        "scope": ["REVIEW_GOVERNANCE"],
        "accepted_limitations": ["ROOT_COLLUSION_RESIDUAL"],
        "currentness_state": "CURRENT",
        "record_digest": "",
    }, "record_digest")


def residual_state(*, common_control=False):
    return seal({
        "schema_version": 1,
        "state_id": "RTS-1",
        "generation_id": "GEN-1",
        "snapshot_id": "SNAP-1",
        "risk_owner_id": "RISK-OWNER-1",
        "declared_root_ids": ["ROOT-A", "ROOT-B"],
        "unresolved_limitations": ["ROOT_COLLUSION_RESIDUAL", "PROVIDER_COMPROMISE_RESIDUAL"],
        "cannot_override_blockers": True,
        "cannot_override_insufficiency": True,
        "cannot_override_unproven_independence": True,
        "risk_owner_acceptance_digest": "3" * 64,
        "currentness_state": "CURRENT",
        "unresolved_common_control_risk": common_control,
        "promotion_blocked": common_control,
        "state_digest": "",
    }, "state_digest")


def adjudication(expected):
    return seal({
        "schema_version": 1,
        "adjudication_id": "ADJ-1",
        "adjudicator_id": "A-1",
        "adjudicator_control_domain_id": "D-ADJ",
        "candidate_id": "C1",
        "snapshot_id": "SNAP-1",
        "generation_id": "GEN-1",
        "raw_hidden_evidence_read_capability": False,
        "candidate_controlled": False,
        "adjudicator_independence_result": "INDEPENDENT",
        "allowed_input_classes": [
            "REVIEWER_VISIBLE_EVIDENCE",
            "AUTHENTICATED_REVIEW_RESPONSES",
            "REVIEW_RESPONSE_LEDGER",
            "BLOCKER_LEDGER",
            "HIDDEN_MONITOR_CERTIFICATE",
            "GOVERNED_POLICY",
            "CURRENTNESS_VECTOR",
            "RESIDUAL_TRUST_STATE",
        ],
        "reviewer_visible_evidence_root_digest": expected["reviewer_visible_evidence_root_digest"],
        "review_ledger_head_digest": expected["review_ledger_head_digest"],
        "blocker_ledger_head_digest": expected["blocker_ledger_head_digest"],
        "monitor_certificate_digest": expected["monitor_certificate_digest"],
        "policy_digest": expected["policy_digest"],
        "currentness_vector_digest": expected["currentness_vector_digest"],
        "residual_trust_state_digest": expected["residual_trust_state_digest"],
        "monitor_reopen_required": False,
        "review_response_valid": True,
        "clean_room_promotable": True,
        "decision_time_revalidation_complete": True,
        "adjudication_digest": "",
    }, "adjudication_digest")


class ReviewLedgerTests(unittest.TestCase):
    def test_valid_review_ledger(self):
        out = validate_review_response_ledger(review_ledger(), expected_snapshot_id="SNAP-1")
        self.assertTrue(out["valid"], out["problems"])
        self.assertEqual(out["record_count"], 2)

    def test_review_ledger_predecessor_tamper_blocks(self):
        b = review_ledger()
        b["records"][1]["predecessor_record_digest"] = "0" * 64
        seal(b["records"][1], "record_digest")
        b["current_head_digest"] = b["records"][1]["record_digest"]
        b["witnessed_head_digest"] = b["records"][1]["record_digest"]
        seal(b, "ledger_digest")
        out = validate_review_response_ledger(b, expected_snapshot_id="SNAP-1")
        self.assertTrue(any("REVIEW_LEDGER_PREDECESSOR_MISMATCH" in x for x in out["problems"]))

    def test_review_ledger_witnessed_head_replay_blocks(self):
        b = review_ledger(); b["witnessed_head_digest"] = b["records"][0]["record_digest"]; seal(b, "ledger_digest")
        self.assertIn("REVIEW_LEDGER_WITNESSED_HEAD_MISMATCH", validate_review_response_ledger(b, expected_snapshot_id="SNAP-1")["problems"])

    def test_review_ledger_snapshot_rebinding_blocks(self):
        b = review_ledger(); b["records"][0]["snapshot_id"] = "OTHER"; seal(b["records"][0], "record_digest"); seal(b, "ledger_digest")
        out = validate_review_response_ledger(b, expected_snapshot_id="SNAP-1")
        self.assertTrue(any("REVIEW_LEDGER_SNAPSHOT_MISMATCH" in x for x in out["problems"]))


class BlockerLedgerTests(unittest.TestCase):
    def test_open_blocker_valid_but_promotion_blocked(self):
        out = validate_blocker_ledger(blocker_ledger(open_one=True), expected_snapshot_id="SNAP-1")
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["promotion_blocked"]); self.assertEqual(out["open_blockers"], ["B-1"])

    def test_resolved_blocker_requires_reopened_evidence_and_unblocks(self):
        out = validate_blocker_ledger(blocker_ledger(open_one=False), expected_snapshot_id="SNAP-1")
        self.assertTrue(out["valid"], out["problems"]); self.assertFalse(out["promotion_blocked"])

    def test_blocker_ledger_head_tamper_blocks(self):
        b = blocker_ledger(); b["current_head_digest"] = "0" * 64; seal(b, "ledger_digest")
        self.assertIn("BLOCKER_LEDGER_CURRENT_HEAD_MISMATCH", validate_blocker_ledger(b, expected_snapshot_id="SNAP-1")["problems"])


class CurrentnessVectorTests(unittest.TestCase):
    required = ["SNAPSHOT", "REVIEWER", "LEDGERS"]

    def test_complete_currentness_vector(self):
        out = validate_currentness_vector(currentness_vector(), required_subject_ids=self.required)
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["current"])

    def test_stale_binding_blocks_vector(self):
        b = currentness_vector(); b["bindings"][1]["state"] = "STALE"; seal(b["bindings"][1], "binding_digest"); seal(b, "vector_digest")
        out = validate_currentness_vector(b, required_subject_ids=self.required)
        self.assertTrue(any("CURRENTNESS_VECTOR_NONCURRENT:REVIEWER" in x for x in out["problems"]))

    def test_missing_required_subject_blocks(self):
        b = currentness_vector(); b["bindings"].pop(); seal(b, "vector_digest")
        self.assertIn("CURRENTNESS_VECTOR_SUBJECT_SET_MISMATCH", validate_currentness_vector(b, required_subject_ids=self.required)["problems"])


class GenerationTests(unittest.TestCase):
    def test_load_bearing_change_creates_material_generation(self):
        out = validate_governance_generation(generation())
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["load_bearing_change"]); self.assertFalse(out["promotion_blocked"])

    def test_load_bearing_change_cannot_be_nonimpacting(self):
        out = validate_governance_generation(generation(change_class="ADJUDICATION_POLICY", impact="PROVEN_NON_IMPACTING"))
        self.assertIn("GOVERNANCE_GENERATION_LOAD_BEARING_CHANGE_MUST_BE_MATERIAL", out["problems"])

    def test_unknown_governance_impact_must_block(self):
        out = validate_governance_generation(generation(change_class="OTHER_CHANGE", impact="GOVERNANCE_IMPACT_UNKNOWN", blocked=True))
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["promotion_blocked"])

    def test_unknown_impact_without_block_is_rejected(self):
        out = validate_governance_generation(generation(change_class="OTHER_CHANGE", impact="GOVERNANCE_IMPACT_UNKNOWN", blocked=False))
        self.assertIn("GOVERNANCE_GENERATION_UNKNOWN_IMPACT_MUST_BLOCK", out["problems"])


class ResidualTrustTests(unittest.TestCase):
    roots = [residual_root("ROOT-A"), residual_root("ROOT-B")]

    def test_current_residual_trust_state_valid(self):
        out = validate_residual_trust_state(residual_state(), root_records=self.roots, required_root_ids=["ROOT-A", "ROOT-B"])
        self.assertTrue(out["valid"], out["problems"]); self.assertFalse(out["promotion_blocked"])

    def test_common_control_risk_blocks_even_when_accepted(self):
        out = validate_residual_trust_state(residual_state(common_control=True), root_records=self.roots, required_root_ids=["ROOT-A", "ROOT-B"])
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["promotion_blocked"])

    def test_residual_trust_cannot_override_blockers(self):
        s = residual_state(); s["cannot_override_blockers"] = False; seal(s, "state_digest")
        out = validate_residual_trust_state(s, root_records=self.roots, required_root_ids=["ROOT-A", "ROOT-B"])
        self.assertIn("RESIDUAL_TRUST_STATE_CANNOT_OVERRIDE_BLOCKERS_REQUIRED", out["problems"])

    def test_stale_root_blocks(self):
        roots = [residual_root("ROOT-A"), residual_root("ROOT-B")]; roots[0]["currentness_state"] = "STALE"; seal(roots[0], "record_digest")
        out = validate_residual_trust_state(residual_state(), root_records=roots, required_root_ids=["ROOT-A", "ROOT-B"])
        self.assertTrue(any("RESIDUAL_TRUST_STATE_ROOT_NOT_CURRENT:ROOT-A" in x for x in out["problems"]))


class AdjudicationTests(unittest.TestCase):
    def parts(self, open_blocker=False, common_control=False):
        rl = validate_review_response_ledger(review_ledger(), expected_snapshot_id="SNAP-1")
        bl = validate_blocker_ledger(blocker_ledger(open_one=open_blocker), expected_snapshot_id="SNAP-1")
        cv_obj = currentness_vector(); cv = validate_currentness_vector(cv_obj, required_subject_ids=["SNAPSHOT", "REVIEWER", "LEDGERS"])
        rs_obj = residual_state(common_control=common_control)
        rs = validate_residual_trust_state(rs_obj, root_records=[residual_root("ROOT-A"), residual_root("ROOT-B")], required_root_ids=["ROOT-A", "ROOT-B"])
        expected = {
            "reviewer_visible_evidence_root_digest": "4" * 64,
            "review_ledger_head_digest": rl["current_head_digest"],
            "blocker_ledger_head_digest": bl["current_head_digest"],
            "monitor_certificate_digest": "5" * 64,
            "policy_digest": "6" * 64,
            "currentness_vector_digest": cv_obj["vector_digest"],
            "residual_trust_state_digest": rs_obj["state_digest"],
        }
        return expected, bl, cv, rs

    def test_positive_adjudication_firewall_ready(self):
        expected, bl, cv, rs = self.parts(open_blocker=False)
        out = validate_adjudication_firewall(adjudication(expected), expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["positive_completion_ready"])

    def test_hidden_raw_evidence_access_forbidden(self):
        expected, bl, cv, rs = self.parts(open_blocker=False); a = adjudication(expected); a["raw_hidden_evidence_read_capability"] = True; seal(a, "adjudication_digest")
        out = validate_adjudication_firewall(a, expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_HIDDEN_RAW_READ_CAPABILITY_FORBIDDEN", out["problems"])

    def test_open_blocker_stops_adjudication(self):
        expected, bl, cv, rs = self.parts(open_blocker=True)
        out = validate_adjudication_firewall(adjudication(expected), expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_OPEN_BLOCKER_PRESENT", out["problems"])

    def test_residual_common_control_stops_adjudication(self):
        expected, bl, cv, rs = self.parts(open_blocker=False, common_control=True)
        out = validate_adjudication_firewall(adjudication(expected), expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_RESIDUAL_TRUST_BLOCKING", out["problems"])

    def test_monitor_reopen_stops_adjudication(self):
        expected, bl, cv, rs = self.parts(open_blocker=False); a = adjudication(expected); a["monitor_reopen_required"] = True; seal(a, "adjudication_digest")
        out = validate_adjudication_firewall(a, expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_MONITOR_REOPEN_REQUIRED", out["problems"])

    def test_decision_time_revalidation_is_mandatory(self):
        expected, bl, cv, rs = self.parts(open_blocker=False); a = adjudication(expected); a["decision_time_revalidation_complete"] = False; seal(a, "adjudication_digest")
        out = validate_adjudication_firewall(a, expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_DECISION_TIME_REVALIDATION_REQUIRED", out["problems"])

    def test_binding_drift_rejected(self):
        expected, bl, cv, rs = self.parts(open_blocker=False); a = adjudication(expected); a["review_ledger_head_digest"] = "0" * 64; seal(a, "adjudication_digest")
        out = validate_adjudication_firewall(a, expected=expected, blocker_ledger_result=bl, currentness_vector_result=cv, residual_trust_result=rs)
        self.assertIn("ADJUDICATION_BINDING_MISMATCH:review_ledger_head_digest", out["problems"])

    def test_frontier_non_authoritative(self):
        f = governance_construction_frontier()
        self.assertEqual(f["implemented_surfaces"], [25, 26, 27, 28, 29]); self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
