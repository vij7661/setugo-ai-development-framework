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
from v24_v6_test_proof_context import build_test_proof_context

D1="1"*64;D2="2"*64;D3="3"*64;D4="4"*64;D5="5"*64;D6="6"*64;D7="7"*64;D8="8"*64;D9="9"*64;DA="a"*64;DB="b"*64;DC="c"*64;DF="f"*64


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
        "predicate_coverage_content_digest":DF,
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
        "decision_id":"DECISION-1",
        "decision_digest":DB,
        "decision_qualification_digest":D1,
        "decision_context_digest":DC,
        "endpoint_projection_id":"ENDPOINT-PROJECTION-1",
        "endpoint_projection_digest":D6,
        "endpoint_projection_qualification_digest":D2,
        "predicate_coverage_id":"PREDICATE-COVERAGE-1",
        "predicate_coverage_content_digest":s["predicate_coverage_content_digest"],
        "decision_qualification_state":QUALIFIED,
        "endpoint_projection_qualification_state":QUALIFIED,
        "predicate_coverage_qualification_state":QUALIFIED,
        "selected_endpoint_state":"ALLOW",
        **{k:s[k] for k in (
            "endpoint_table_digest","applicability_digest","evaluator_registry_digest",
            "condition_registry_digest","evidence_registry_digest","predicate_coverage_content_digest",
            "predicate_coverage_qualification_digest","material_observation_head_digest",
            "completeness_ledger_head_digest","material_surface_digest","authority_sink_id",
            "writer_identity","guard_mechanism_digest")}
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


def attach_proofs(b):
    src=b["snapshot_source"];snap=b["current_snapshot"];dec=b["decision"]
    old_snapshot_digest=snap.get("snapshot_digest")
    specs={
        "source_q":{"kind":"QUALIFICATION","subject_id":src["mechanism_id"],"content_digest":src["mechanism_content_digest"]},
        "source_i":{"kind":"INDEPENDENCE","subject_identity_id":src["mechanism_id"]},
        "source_c":{"kind":"CURRENTNESS","source_id":src["mechanism_id"],"source_digest":src["mechanism_content_digest"]},
        "predicate_q":{"kind":"QUALIFICATION","subject_id":dec["predicate_coverage_id"],"content_digest":dec["predicate_coverage_content_digest"]},
        "decision_q":{"kind":"QUALIFICATION","subject_id":dec["decision_id"],"content_digest":dec["decision_digest"]},
        "endpoint_q":{"kind":"QUALIFICATION","subject_id":dec["endpoint_projection_id"],"content_digest":dec["endpoint_projection_digest"]},
    }
    rd=b.get("reevaluated_decision")
    if isinstance(rd,dict):
        specs["reevaluated_decision_q"]={"kind":"QUALIFICATION","subject_id":rd["decision_id"],"content_digest":rd["decision_digest"]}
        specs["reevaluated_endpoint_q"]={"kind":"QUALIFICATION","subject_id":rd["endpoint_projection_id"],"content_digest":rd["endpoint_projection_digest"]}
    context,boundary,refs=build_test_proof_context(specs)
    src["qualification_digest"]=refs["source_q"]
    src["independence_qualification_digest"]=refs["source_i"]
    src["currentness_binding_digest"]=refs["source_c"]
    snap["source_qualification_digest"]=refs["source_q"]
    snap["source_independence_digest"]=refs["source_i"]
    snap["source_currentness_digest"]=refs["source_c"]
    snap["predicate_coverage_qualification_digest"]=refs["predicate_q"]
    dec["predicate_coverage_qualification_digest"]=refs["predicate_q"]
    dec["decision_qualification_digest"]=refs["decision_q"]
    dec["endpoint_projection_qualification_digest"]=refs["endpoint_q"]
    if isinstance(rd,dict):
        rd["predicate_coverage_qualification_digest"]=refs["predicate_q"]
        rd["decision_qualification_digest"]=refs["reevaluated_decision_q"]
        rd["endpoint_projection_qualification_digest"]=refs["reevaluated_endpoint_q"]
    snap["snapshot_digest"]=canonical_snapshot_digest(snap)
    if isinstance(rd,dict) and rd.get("source_snapshot_digest")==old_snapshot_digest:
        rd["source_snapshot_digest"]=snap["snapshot_digest"]
    return context,boundary


def evaluate(b):
    context,boundary=attach_proofs(b)
    return evaluate_decision_apply_latch(b,proof_context=context,trusted_boundary=boundary)


class R4DecisionApplyTests(unittest.TestCase):
    def test_construction_frontier_non_authoritative(self):
        r=construction_frontier();self.assertFalse(r["qualified"]);self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_exact_current_latch_allows(self):
        r=evaluate(bundle());self.assertTrue(r["allowed"],r["problems"]);self.assertEqual(r["state"],APPLY_READY);self.assertFalse(r["re_evaluated"])

    def test_opaque_labels_without_proof_context_block(self):
        r=evaluate_decision_apply_latch(bundle());self.assertFalse(r["allowed"]);self.assertTrue(any("PROOF" in x for x in r["problems"]))

    def test_candidate_embedded_context_cannot_substitute_for_trusted_arguments(self):
        b=bundle();context,boundary=attach_proofs(b);b["governance_proof_context"]=context;b["trusted_boundary"]=boundary
        r=evaluate_decision_apply_latch(b);self.assertFalse(r["allowed"]);self.assertTrue(any("TRUSTED_PROOF_BOUNDARY_REQUIRED" in x for x in r["problems"]))

    def test_wrong_subject_reference_blocks_after_proof_context_is_frozen(self):
        b=bundle();context,boundary=attach_proofs(b);b["snapshot_source"]["mechanism_id"]="OTHER-MECHANISM"
        r=evaluate_decision_apply_latch(b,proof_context=context,trusted_boundary=boundary);self.assertFalse(r["allowed"]);self.assertTrue(any("SUBJECT_ID_MISMATCH" in x for x in r["problems"]))

    def test_unqualified_snapshot_source_blocks(self):
        b=bundle();b["snapshot_source"]["qualification_state"]="INVALID"
        r=evaluate(b);self.assertFalse(r["allowed"]);self.assertTrue(any("SNAPSHOT_SOURCE_NOT_QUALIFIED" in x for x in r["problems"]))

    def test_non_independent_snapshot_source_blocks(self):
        b=bundle();b["snapshot_source"]["independence_state"]="CONFLICT"
        r=evaluate(b);self.assertTrue(any("SNAPSHOT_SOURCE_NOT_INDEPENDENT" in x for x in r["problems"]))

    def test_mixed_snapshot_blocks(self):
        b=bundle();b["current_snapshot"]["mixed_snapshot_detected"]=True
        r=evaluate(b);self.assertTrue(any(MIXED_SNAPSHOT_REJECTED in x for x in r["problems"]))

    def test_digest_drift_without_reevaluation_blocks(self):
        b=bundle();b["current_snapshot"]["completeness_ledger_head_digest"]="f"*64;b["current_snapshot"]["snapshot_digest"]=canonical_snapshot_digest(b["current_snapshot"])
        r=evaluate(b);self.assertIn(REEVALUATION_REQUIRED,r["problems"]);self.assertIn("completeness_ledger_head_digest",r["drifted_binding_fields"]);self.assertFalse(r["allowed"])

    def test_drift_with_exact_current_reevaluation_allows_new_decision(self):
        b=bundle();s=b["current_snapshot"];s["material_observation_head_digest"]="e"*64;s["snapshot_digest"]=canonical_snapshot_digest(s)
        p=b["material_effect_path"];p["observation_head_digest"]="e"*64
        rd=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=s["snapshot_digest"])
        b["reevaluated_decision"]=rd
        r=evaluate(b);self.assertTrue(r["allowed"],r["problems"]);self.assertTrue(r["re_evaluated"]);self.assertEqual(r["active_decision_digest"],"d"*64)

    def test_reevaluation_not_bound_to_current_snapshot_blocks(self):
        b=bundle();s=b["current_snapshot"];s["condition_registry_digest"]="e"*64;s["snapshot_digest"]=canonical_snapshot_digest(s)
        b["reevaluated_decision"]=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=D1)
        r=evaluate(b);self.assertTrue(any("REEVALUATED_DECISION_SNAPSHOT_BINDING_MISMATCH" in x for x in r["problems"]))

    def test_deny_endpoint_blocks_effect(self):
        b=bundle();b["decision"]["selected_endpoint_state"]="DENY"
        r=evaluate(b);self.assertIn("APPLY_SELECTED_ENDPOINT_NOT_ALLOW",r["problems"])

    def test_writer_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["source_or_writer_id"]="OTHER"
        r=evaluate(b);self.assertIn("MATERIAL_EFFECT_PATH_WRITER_BINDING_MISMATCH",r["problems"])

    def test_stale_observation_head_blocks(self):
        b=bundle();b["material_effect_path"]["observation_head_digest"]="e"*64
        r=evaluate(b);self.assertTrue(any("MATERIAL_EFFECT_PATH_OBSERVATION_HEAD_STALE" in x for x in r["problems"]))

    def test_surface_binding_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["material_surface_membership_digest"]="e"*64
        r=evaluate(b);self.assertIn("MATERIAL_EFFECT_PATH_SURFACE_BINDING_MISMATCH",r["problems"])

    def test_guard_binding_mismatch_blocks(self):
        b=bundle();b["material_effect_path"]["guard_mechanism_digest"]="e"*64
        r=evaluate(b);self.assertIn("MATERIAL_EFFECT_PATH_GUARD_BINDING_MISMATCH",r["problems"])

    def test_no_caller_material_discovery_boolean_is_needed(self):
        b=bundle();self.assertNotIn("material_discovery_pending",b);r=evaluate(b);self.assertTrue(r["allowed"],r["problems"])

if __name__=="__main__":unittest.main()
