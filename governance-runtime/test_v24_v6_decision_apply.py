from __future__ import annotations

import unittest

from v24_v6_decision_apply import (
    APPLY_READY,
    MIXED_SNAPSHOT_REJECTED,
    REEVALUATION_REQUIRED,
    canonical_snapshot_digest,
    construction_frontier,
    evaluate_decision_apply_latch,
)
from v24_v6_governance_foundation import CURRENT, QUALIFIED

D1="1"*64;D2="2"*64;D3="3"*64;D4="4"*64;D5="5"*64;D6="6"*64;D7="7"*64;D8="8"*64;D9="9"*64;DA="a"*64;DB="b"*64;DC="c"*64


def source():
    return {
        "snapshot_source_id":"SNAPSHOT-SOURCE-1",
        "mechanism_id":"SNAPSHOT-MECH-1",
        "mechanism_content_digest":D1,
        "snapshot_schema_id":"V24-V6-APPLY-SNAPSHOT-1",
        "owner_id":"SNAPSHOT-OWNER",
        "owner_control_domain_id":"SNAPSHOT-DOMAIN",
        "independence_rule_id":"IND-RULE-1",
        "currentness_rule_id":"CUR-RULE-1",
        "qualification_digest":D2,
        "independence_qualification_digest":D3,
        "currentness_binding_digest":D4,
        "qualification_state":QUALIFIED,
        "independence_state":QUALIFIED,
        "currentness_result":CURRENT,
        "read_consistency_semantics":"SINGLE_AUTHORITATIVE_SNAPSHOT",
        "authoritative_head_fields":["material_observation_head_digest","completeness_ledger_head_digest"],
    }


def snapshot(**overrides):
    s={
        "snapshot_source_id":"SNAPSHOT-SOURCE-1",
        "snapshot_sequence":12,
        "snapshot_epoch":"GEN-V24:12",
        "endpoint_table_digest":D1,
        "applicability_digest":D2,
        "evaluator_registry_digest":D3,
        "condition_registry_digest":D4,
        "evidence_registry_digest":D5,
        "predicate_coverage_qualification_digest":D6,
        "material_observation_head_digest":D7,
        "completeness_ledger_head_digest":D8,
        "material_surface_digest":D9,
        "authority_sink_id":"SINK-A",
        "writer_identity":"WRITER-A",
        "guard_mechanism_digest":DA,
        "source_qualification_digest":D2,
        "source_independence_digest":D3,
        "source_currentness_digest":D4,
        "mixed_snapshot_detected":False,
    }
    s.update(overrides)
    s["snapshot_digest"]=canonical_snapshot_digest(s)
    return s


def decision(s=None,**overrides):
    s=s or snapshot()
    d={
        "decision_digest":DB,
        "decision_context_digest":DC,
        "endpoint_projection_digest":D6,
        "decision_qualification_state":QUALIFIED,
        "endpoint_projection_qualification_state":QUALIFIED,
        "predicate_coverage_qualification_state":QUALIFIED,
        "selected_endpoint_state":"ALLOW",
        **{k:s[k] for k in (
            "endpoint_table_digest","applicability_digest","evaluator_registry_digest",
            "condition_registry_digest","evidence_registry_digest","predicate_coverage_qualification_digest",
            "material_observation_head_digest","completeness_ledger_head_digest","material_surface_digest",
            "authority_sink_id","writer_identity","guard_mechanism_digest")}
    }
    d.update(overrides)
    return d


def path(s=None,**overrides):
    s=s or snapshot()
    p={
        "path_id":"PATH-1","source_or_writer_id":"WRITER-A","sink_id":"SINK-A","effect_class_id":"WRITE",
        "writer_admission_digest":D1,"capability_digest":D2,"guard_mechanism_digest":DA,
        "sink_admitted_writer_set_digest":D3,"material_surface_membership_digest":D9,
        "observation_head_digest":D7,"writer_admission_state":QUALIFIED,"capability_state":QUALIFIED,
        "guard_qualification_state":QUALIFIED,"sink_admitted_writer_ids":["WRITER-A"],
        "dependency_edge_digests":[D4],"control_plane_evidence_digests":[D5],"currentness_result":CURRENT,
    }
    p.update(overrides)
    return p


def bundle():
    s=snapshot()
    return {"snapshot_source":source(),"current_snapshot":s,"decision":decision(s),"material_effect_path":path(s)}


class R4DecisionApplyTests(unittest.TestCase):
    def test_construction_frontier_non_authoritative(self):
        r=construction_frontier();self.assertFalse(r["qualified"]);self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_exact_current_latch_allows(self):
        r=evaluate_decision_apply_latch(bundle());self.assertTrue(r["allowed"],r["problems"]);self.assertEqual(r["state"],APPLY_READY);self.assertFalse(r["re_evaluated"])

    def test_unqualified_snapshot_source_blocks(self):
        b=bundle();b["snapshot_source"]["qualification_state"]="INVALID"
        r=evaluate_decision_apply_latch(b);self.assertFalse(r["allowed"]);self.assertTrue(any("SNAPSHOT_SOURCE_NOT_QUALIFIED" in x for x in r["problems"]))

    def test_non_independent_snapshot_source_blocks(self):
        b=bundle();b["snapshot_source"]["independence_state"]="CONFLICT"
        r=evaluate_decision_apply_latch(b);self.assertTrue(any("SNAPSHOT_SOURCE_NOT_INDEPENDENT" in x for x in r["problems"]))

    def test_mixed_snapshot_blocks(self):
        b=bundle();b["current_snapshot"]["mixed_snapshot_detected"]=True
        r=evaluate_decision_apply_latch(b);self.assertTrue(any(MIXED_SNAPSHOT_REJECTED in x for x in r["problems"]))

    def test_digest_drift_without_reevaluation_blocks(self):
        b=bundle();b["current_snapshot"]["completeness_ledger_head_digest"]="f"*64;b["current_snapshot"]["snapshot_digest"]=canonical_snapshot_digest(b["current_snapshot"])
        r=evaluate_decision_apply_latch(b);self.assertIn(REEVALUATION_REQUIRED,r["problems"]);self.assertIn("completeness_ledger_head_digest",r["drifted_binding_fields"]);self.assertFalse(r["allowed"])

    def test_drift_with_exact_current_reevaluation_allows_new_decision(self):
        b=bundle();s=b["current_snapshot"];s["material_observation_head_digest"]="e"*64;s["snapshot_digest"]=canonical_snapshot_digest(s)
        p=b["material_effect_path"];p["observation_head_digest"]="e"*64
        rd=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=s["snapshot_digest"])
        b["reevaluated_decision"]=rd
        r=evaluate_decision_apply_latch(b);self.assertTrue(r["allowed"],r["problems"]);self.assertTrue(r["re_evaluated"]);self.assertEqual(r["active_decision_digest"],"d"*64)

    def test_reevaluation_not_bound_to_current_snapshot_blocks(self):
        b=bundle();s=b["current_snapshot"];s["condition_registry_digest"]="e"*64;s["snapshot_digest"]=canonical_snapshot_digest(s)
        b["reevaluated_decision"]=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=D1)
        r=evaluate_decision_apply_latch(b);self.assertTrue(any("REEVALUATED_DECISION_SNAPSHOT_BINDING_MISMATCH" in x for x in r["problems"]))

    def test_deny_endpoint_blocks_effect(self):
        b=bundle();b["decision"]["selected_endpoint_state"]="DENY"
        r=evaluate_decision_apply_latch(b);self.assertIn("APPLY_SELECTED_ENDPOINT_NOT_ALLOW",r["problems"])

    def test_writer_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["source_or_writer_id"]="OTHER"
        r=evaluate_decision_apply_latch(b);self.assertIn("MATERIAL_EFFECT_PATH_WRITER_BINDING_MISMATCH",r["problems"])

    def test_stale_observation_head_blocks(self):
        b=bundle();b["material_effect_path"]["observation_head_digest"]="e"*64
        r=evaluate_decision_apply_latch(b);self.assertTrue(any("MATERIAL_EFFECT_PATH_OBSERVATION_HEAD_STALE" in x for x in r["problems"]))

    def test_surface_binding_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["material_surface_membership_digest"]="e"*64
        r=evaluate_decision_apply_latch(b);self.assertIn("MATERIAL_EFFECT_PATH_SURFACE_BINDING_MISMATCH",r["problems"])

    def test_guard_binding_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["guard_mechanism_digest"]="e"*64
        r=evaluate_decision_apply_latch(b);self.assertIn("MATERIAL_EFFECT_PATH_GUARD_BINDING_MISMATCH",r["problems"])


    def test_snapshot_digest_binds_source_trust_material(self):
        s=snapshot(); original=s["snapshot_digest"]
        s["source_qualification_digest"]="f"*64
        self.assertNotEqual(original, canonical_snapshot_digest(s))
        b=bundle(); b["current_snapshot"]["source_qualification_digest"]="f"*64
        r=evaluate_decision_apply_latch(b)
        self.assertTrue(any("SNAPSHOT_DIGEST_MISMATCH" in x or "SOURCE_QUALIFICATION_BINDING_MISMATCH" in x for x in r["problems"]))

    def test_no_caller_material_discovery_boolean_is_needed(self):
        b=bundle();self.assertNotIn("material_discovery_pending",b);r=evaluate_decision_apply_latch(b);self.assertTrue(r["allowed"],r["problems"])

if __name__=="__main__":unittest.main()
