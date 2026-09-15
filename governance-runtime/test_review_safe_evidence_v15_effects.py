from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_effects import (
    effects_construction_frontier,
    validate_effect_issuance_record,
    validate_external_effect_gateway,
    validate_implementation_stopping_rule,
    validate_taint_provenance_graph,
)


def seal(record, field):
    record[field] = canonical_hash({k: v for k, v in record.items() if k != field})
    return record


def token(*, expires=200):
    return seal({
        "schema_version": 1,
        "token_id": "TOK-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "nonce": "N-1",
        "ledger_head_digest": "1" * 64,
        "currentness_vector_digest": "2" * 64,
        "content_receipt_digest": "3" * 64,
        "single_use": True,
        "expires_sequence": expires,
        "token_digest": "",
    }, "token_digest")


def expected_context():
    return {
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "ledger_head_digest": "1" * 64,
        "currentness_vector_digest": "2" * 64,
        "content_receipt_digest": "3" * 64,
        "gateway_version_digest": "4" * 64,
    }


def positive_result(*, promotion_blocked=False, positive_completion_ready=True, valid=True, current=True):
    return {
        "promotion_blocked": promotion_blocked,
        "positive_completion_ready": positive_completion_ready,
        "valid": valid,
        "current": current,
    }


def issuance(*, fenceable=True, tok=None):
    tok = tok or token()
    return seal({
        "schema_version": 1,
        "issuance_id": "ISS-1",
        "effect_id": "EFF-1",
        "gateway_id": "GW-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "token_id": tok["token_id"],
        "token": tok,
        "gateway_version_digest": "4" * 64,
        "effect_fenceable": fenceable,
        "decision_time_revalidation_complete": True,
        "candidate_controlled": False,
        "issuance_digest": "",
    }, "issuance_digest")


def gateway_record(*, outcome="EFFECT_AUTHORIZED_ONCE", immediate=True, atomic=True, version=None):
    return seal({
        "schema_version": 1,
        "gateway_decision_id": "GD-1",
        "gateway_id": "GW-1",
        "effect_id": "EFF-1",
        "token_id": "TOK-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "current_gateway_version_digest": version or "4" * 64,
        "effect_fenceable": True,
        "immediate_pre_effect_revalidation": immediate,
        "atomic_token_consumption": atomic,
        "candidate_controlled": False,
        "outcome": outcome,
        "decision_digest": "",
    }, "decision_digest")


def provenance_graph():
    nodes = [
        {"artifact_id": "SRC-1", "provenance_class": "SOURCE_EVIDENCE", "content_digest": "a" * 64, "candidate_controlled_provenance_label": False, "source_allowlisted": True},
        {"artifact_id": "TPL-1", "provenance_class": "CANONICAL_NEUTRAL_TEMPLATE", "content_digest": "b" * 64, "candidate_controlled_provenance_label": False, "source_allowlisted": True},
        {"artifact_id": "VIEW-1", "provenance_class": "DETERMINISTIC_STRUCTURED_VIEW", "content_digest": "c" * 64, "candidate_controlled_provenance_label": False, "source_allowlisted": True},
        {"artifact_id": "POST-1", "provenance_class": "POST_REVIEW_FINDING", "content_digest": "d" * 64, "candidate_controlled_provenance_label": False, "source_allowlisted": False},
        {"artifact_id": "POST-SUMMARY", "provenance_class": "EXTERNAL_NARRATIVE", "content_digest": "e" * 64, "candidate_controlled_provenance_label": False, "source_allowlisted": False},
    ]
    return seal({
        "schema_version": 1,
        "graph_id": "PG-1",
        "generation_id": "GEN-1",
        "snapshot_id": "S1",
        "nodes": nodes,
        "edges": [{"from_artifact_id": "POST-1", "to_artifact_id": "POST-SUMMARY", "relation": "SUMMARIZES"}],
        "graph_digest": "",
    }, "graph_digest")


def stopping_rule():
    return seal({
        "schema_version": 1,
        "all_mandatory_schemas_exist": True,
        "construction_tests_green": True,
        "all_adversarial_tests_executed": True,
        "no_unresolved_critical_high": True,
        "historical_reds_preserved": True,
        "exact_candidate_frozen": True,
        "evidence_package_bound_to_candidate_environment": True,
        "reviewer_safe_projection_built": True,
        "fresh_independent_evidence_review_required_next": True,
        "runtime_qualification_state": "NOT_CLAIMED",
        "scientific_execution_state": "CLOSED_PENDING_INDEPENDENT_EVIDENCE_REVIEW",
        "candidate_commit": "f" * 40,
        "candidate_tree_digest": "1" * 64,
        "environment_digest": "2" * 64,
        "evidence_package_digest": "3" * 64,
        "projection_digest": "4" * 64,
        "historical_red_count": 1,
        "record_digest": "",
    }, "record_digest")


class EffectIssuanceTests(unittest.TestCase):
    def call(self, record=None, *, consumed=frozenset(), blocker=False, monitor=False, residual=False, adjudication=True, current=True):
        return validate_effect_issuance_record(
            record or issuance(),
            current_sequence=120,
            consumed_token_ids=consumed,
            expected_context=expected_context(),
            adjudication_result=positive_result(positive_completion_ready=adjudication),
            currentness_vector_result=positive_result(valid=current, current=current),
            blocker_ledger_result=positive_result(promotion_blocked=blocker),
            monitor_certificate_result=positive_result(promotion_blocked=monitor),
            residual_trust_result=positive_result(promotion_blocked=residual),
        )

    def test_valid_effect_issuance(self):
        out = self.call()
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["effect_ready"]); self.assertFalse(out["qualified"])

    def test_unfenceable_effect_is_nonpromotable(self):
        out = self.call(issuance(fenceable=False))
        self.assertIn("EFFECT_ISSUANCE_UNFENCEABLE_EFFECT_NONPROMOTABLE", out["problems"])

    def test_open_blocker_stops_issuance(self):
        self.assertIn("EFFECT_ISSUANCE_BLOCKER_LEDGER_BLOCKING", self.call(blocker=True)["problems"])

    def test_monitor_reopen_stops_issuance(self):
        self.assertIn("EFFECT_ISSUANCE_MONITOR_CERTIFICATE_BLOCKING", self.call(monitor=True)["problems"])

    def test_residual_trust_block_stops_issuance(self):
        self.assertIn("EFFECT_ISSUANCE_RESIDUAL_TRUST_BLOCKING", self.call(residual=True)["problems"])

    def test_consumed_token_cannot_be_reissued(self):
        out = self.call(consumed={"TOK-1"})
        self.assertTrue(any("FENCED_TOKEN_REPLAYED" in x for x in out["problems"]))


class EffectGatewayTests(unittest.TestCase):
    def call(self, rec=None, tok=None, consumed=frozenset(), current=120):
        return validate_external_effect_gateway(
            rec or gateway_record(), token=tok or token(), current_sequence=current,
            consumed_token_ids=consumed, expected_context=expected_context(),
        )

    def test_exact_context_authorizes_once(self):
        out = self.call()
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["effect_authorized"])

    def test_gateway_version_drift_rejected(self):
        out = self.call(gateway_record(version="9" * 64))
        self.assertIn("EFFECT_GATEWAY_VERSION_DRIFT", out["problems"])

    def test_immediate_pre_effect_revalidation_required(self):
        self.assertIn("EFFECT_GATEWAY_IMMEDIATE_REVALIDATION_REQUIRED", self.call(gateway_record(immediate=False))["problems"])

    def test_atomic_token_consumption_required(self):
        self.assertIn("EFFECT_GATEWAY_ATOMIC_TOKEN_CONSUMPTION_REQUIRED", self.call(gateway_record(atomic=False))["problems"])

    def test_expired_token_rejected(self):
        out = self.call(tok=token(expires=100), current=120)
        self.assertTrue(any("FENCED_TOKEN_EXPIRED" in x for x in out["problems"]))

    def test_invalid_context_cannot_false_green_authorization(self):
        out = self.call(gateway_record(version="9" * 64, outcome="EFFECT_AUTHORIZED_ONCE"))
        self.assertIn("EFFECT_GATEWAY_FALSE_GREEN_AUTHORIZATION", out["problems"])

    def test_replayed_token_rejected(self):
        out = self.call(consumed={"TOK-1"})
        self.assertTrue(any("FENCED_TOKEN_REPLAYED" in x for x in out["problems"]))


class TaintProvenanceTests(unittest.TestCase):
    def test_clean_allowlisted_sources_views_templates_pass(self):
        out = validate_taint_provenance_graph(provenance_graph(), clean_package_artifact_ids=["SRC-1", "TPL-1", "VIEW-1"])
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["clean_package_ready"])

    def test_post_review_finding_cannot_enter_clean_package(self):
        out = validate_taint_provenance_graph(provenance_graph(), clean_package_artifact_ids=["POST-1"])
        self.assertTrue(any("POST_REVIEW_TAINT_IN_CLEAN_PACKAGE:POST-1" in x for x in out["problems"]))

    def test_taint_propagates_through_summary(self):
        out = validate_taint_provenance_graph(provenance_graph(), clean_package_artifact_ids=["POST-SUMMARY"])
        self.assertIn("POST-SUMMARY", out["tainted_artifact_ids"])
        self.assertTrue(any("POST_REVIEW_TAINT_IN_CLEAN_PACKAGE:POST-SUMMARY" in x for x in out["problems"]))

    def test_unknown_provenance_blocks_clean_package(self):
        g = provenance_graph(); g["nodes"][0]["provenance_class"] = "UNKNOWN_PROVENANCE"; seal(g, "graph_digest")
        out = validate_taint_provenance_graph(g, clean_package_artifact_ids=["SRC-1"])
        self.assertTrue(any("CLEAN_PACKAGE_PROVENANCE_FORBIDDEN:SRC-1:UNKNOWN_PROVENANCE" in x for x in out["problems"]))

    def test_candidate_cannot_self_label_provenance(self):
        g = provenance_graph(); g["nodes"][0]["candidate_controlled_provenance_label"] = True; seal(g, "graph_digest")
        out = validate_taint_provenance_graph(g, clean_package_artifact_ids=["SRC-1"])
        self.assertTrue(any("TAINT_GRAPH_CANDIDATE_PROVENANCE_LABEL_FORBIDDEN:SRC-1" in x for x in out["problems"]))


class StoppingRuleTests(unittest.TestCase):
    def test_complete_stopping_rule_ready_for_independent_review(self):
        out = validate_implementation_stopping_rule(stopping_rule())
        self.assertTrue(out["valid"], out["problems"]); self.assertTrue(out["ready_for_independent_evidence_review"]); self.assertFalse(out["qualified"])

    def test_all_adversarial_tests_must_execute(self):
        r = stopping_rule(); r["all_adversarial_tests_executed"] = False; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_REQUIRED_TRUE:all_adversarial_tests_executed", validate_implementation_stopping_rule(r)["problems"])

    def test_unresolved_critical_high_blocks(self):
        r = stopping_rule(); r["no_unresolved_critical_high"] = False; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_REQUIRED_TRUE:no_unresolved_critical_high", validate_implementation_stopping_rule(r)["problems"])

    def test_runtime_qualification_must_remain_unclaimed(self):
        r = stopping_rule(); r["runtime_qualification_state"] = "QUALIFIED"; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_RUNTIME_AUTHORITY_CLAIMED", validate_implementation_stopping_rule(r)["problems"])

    def test_scientific_execution_must_remain_closed(self):
        r = stopping_rule(); r["scientific_execution_state"] = "OPEN"; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_SCIENTIFIC_EXECUTION_NOT_CLOSED", validate_implementation_stopping_rule(r)["problems"])

    def test_historical_reds_must_be_preserved(self):
        r = stopping_rule(); r["historical_reds_preserved"] = False; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_REQUIRED_TRUE:historical_reds_preserved", validate_implementation_stopping_rule(r)["problems"])

    def test_exact_candidate_must_be_frozen(self):
        r = stopping_rule(); r["exact_candidate_frozen"] = False; seal(r, "record_digest")
        self.assertIn("IMPLEMENTATION_STOPPING_RULE_REQUIRED_TRUE:exact_candidate_frozen", validate_implementation_stopping_rule(r)["problems"])

    def test_frontier_non_authoritative(self):
        f = effects_construction_frontier()
        self.assertEqual(f["implemented_surfaces"], [30, 31, 32, 33]); self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
