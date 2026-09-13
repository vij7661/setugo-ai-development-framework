from __future__ import annotations
import unittest
from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_material_surface import (
    AUTHORITY_ADMISSION_REQUIRED,
    MATERIAL,
    construction_frontier,
    derive_material_authority_surface,
    evaluate_material_discovery,
    validate_material_effect_path,
    validate_material_observation_ledger,
)

D1="1"*64; D2="2"*64; D3="3"*64; D4="4"*64; D5="5"*64; D6="6"*64


def observation(seq, prev, oid, entity):
    r={"observation_id":oid,"observation_sequence":seq,"predecessor_record_digest":prev,"observer_identity":"OBS","observer_control_domain_id":"OBS-DOM","source_kind":"RUNTIME","entity_or_path_id":entity,"evidence_class_id":"E-MAT","evidence_digest":D1,"currentness_binding_digest":D2,"record_digest":""}
    x=dict(r); x.pop("record_digest"); r["record_digest"]=digest(x); return r


def ledger_bundle():
    genesis=D3
    r1=observation(1,genesis,"O1","PATH-A"); r2=observation(2,r1["record_digest"],"O2","PATH-B")
    ds=[r1["record_digest"],r2["record_digest"]]; hd=digest(ds)
    return {"genesis_predecessor_digest":genesis,"records":[r1,r2],"head":{"ledger_id":"LEDGER","latest_sequence":2,"latest_record_digest":r2["record_digest"],"cumulative_root_digest":hd,"durable_storage_identity":"STORE","durable_anchor_identity":"ANCHOR","durable_anchor_digest":D4,"anchor_sequence":2,"fork_or_rollback_detected":False,"operator_control_domain_id":"OP-DOM","witness_currentness_records":[{"witness_identity":"W1","witness_control_domain_id":"W-DOM","observed_head_digest":hd,"observed_sequence":2,"currentness_result":CURRENT,"independence_result":QUALIFIED}]}}


def derivation(i, members, domain):
    return {"derivation_id":f"D{i}","derivation_mechanism_id":f"M{i}","derivation_authority_id":f"A{i}","control_domain_id":domain,"mechanism_qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"member_ids":list(members),"source_kinds":["DEPLOYMENT","RUNTIME_OBSERVATION"],"derivation_digest":D5}


def classifications(ids):
    return [{"subject_id":sid,"classification":MATERIAL,"classifier_qualification_state":QUALIFIED,"classifier_independence_state":QUALIFIED,"currentness_result":CURRENT} for sid in ids]


class R3MaterialSurfaceTests(unittest.TestCase):
    def test_construction_frontier_non_authoritative(self):
        r=construction_frontier(); self.assertFalse(r["qualified"])

    def test_observation_ledger_valid(self):
        r=validate_material_observation_ledger(ledger_bundle()); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["observed_entity_or_path_ids"],["PATH-A","PATH-B"])

    def test_observation_ledger_predecessor_tamper_fails(self):
        b=ledger_bundle(); b["records"][1]["predecessor_record_digest"]=D6
        r=validate_material_observation_ledger(b); self.assertTrue(any("PREDECESSOR_MISMATCH" in x for x in r["problems"]))

    def test_observation_ledger_unanchored_fails(self):
        b=ledger_bundle(); b["head"]["durable_anchor_digest"]=""
        r=validate_material_observation_ledger(b); self.assertIn("MATERIAL_OBSERVATION_ANCHOR_DIGEST_INVALID",r["problems"])

    def test_observation_ledger_operator_only_witness_fails(self):
        b=ledger_bundle(); b["head"]["witness_currentness_records"][0]["witness_control_domain_id"]="OP-DOM"
        r=validate_material_observation_ledger(b); self.assertIn("MATERIAL_OBSERVATION_NO_QUALIFIED_INDEPENDENT_WITNESS",r["problems"])

    def good_surface(self):
        l=validate_material_observation_ledger(ledger_bundle()); self.assertTrue(l["qualified"])
        ids={"PATH-A","PATH-B"}
        b={"observation_ledger_state":QUALIFIED,"observation_head_digest":l["head_digest"],"observed_entity_or_path_ids":l["observed_entity_or_path_ids"],"derivations":[derivation(1,ids,"D-A"),derivation(2,ids,"D-B")],"materiality_classifications":classifications(ids)}
        return b,l

    def test_two_independent_consistent_derivations_qualify(self):
        b,l=self.good_surface(); r=derive_material_authority_surface(b); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["material_member_ids"],["PATH-A","PATH-B"])

    def test_derivation_divergence_blocks(self):
        b,l=self.good_surface(); b["derivations"][1]["member_ids"]=["PATH-A"]
        r=derive_material_authority_surface(b); self.assertIn("MATERIAL_SURFACE_DERIVATION_DIVERGENCE:1",r["problems"]); self.assertFalse(r["qualified"])

    def test_same_control_domain_not_independent(self):
        b,l=self.good_surface(); b["derivations"][1]["control_domain_id"]="D-A"
        r=derive_material_authority_surface(b); self.assertIn("MATERIAL_SURFACE_DERIVATION_CONTROL_DOMAIN_DUPLICATE:D-A",r["problems"])

    def test_candidate_only_derivation_forbidden(self):
        b,l=self.good_surface(); b["derivations"][0]["source_kinds"]=["CANDIDATE_SELF_REPORT"]
        r=derive_material_authority_surface(b); self.assertIn("MATERIAL_SURFACE_CANDIDATE_SELF_REPORT_SOURCE_FORBIDDEN:0",r["problems"])


    def test_candidate_self_report_mixed_with_other_sources_is_forbidden(self):
        b,_=self.good_surface(); b["derivations"][0]["source_kinds"]=["IMPLEMENTATION_ARTIFACT","CANDIDATE_SELF_REPORT"]
        r=derive_material_authority_surface(b)
        self.assertFalse(r["qualified"]); self.assertTrue(any("CANDIDATE_SELF_REPORT_SOURCE_FORBIDDEN" in x for x in r["problems"]))

    def test_missing_materiality_classification_blocks(self):
        b,l=self.good_surface(); b["materiality_classifications"].pop()
        r=derive_material_authority_surface(b); self.assertTrue(any("MATERIALITY_CLASSIFICATION_MISSING" in x for x in r["problems"]))

    def effect_path(self,head):
        return {"path_id":"EP-1","source_or_writer_id":"WRITER","sink_id":"SINK","effect_class_id":"WRITE","writer_admission_digest":D1,"capability_digest":D2,"guard_mechanism_digest":D3,"sink_admitted_writer_set_digest":D4,"material_surface_membership_digest":D5,"observation_head_digest":head,"writer_admission_state":QUALIFIED,"capability_state":QUALIFIED,"guard_qualification_state":QUALIFIED,"sink_admitted_writer_ids":["WRITER"],"dependency_edge_digests":[D1],"control_plane_evidence_digests":[D2],"currentness_result":CURRENT}

    def test_effect_path_closure_passes(self):
        l=validate_material_observation_ledger(ledger_bundle()); self.assertEqual(validate_material_effect_path(self.effect_path(l["head_digest"]),current_observation_head=l["head_digest"]),[])

    def test_direct_writer_missing_from_sink_blocks(self):
        l=validate_material_observation_ledger(ledger_bundle()); p=self.effect_path(l["head_digest"]); p["sink_admitted_writer_ids"]=["OTHER"]
        self.assertIn("MATERIAL_EFFECT_PATH_WRITER_NOT_ADMITTED_AT_SINK",validate_material_effect_path(p,current_observation_head=l["head_digest"]))

    def test_stale_observation_head_blocks_effect_path(self):
        l=validate_material_observation_ledger(ledger_bundle()); p=self.effect_path(D6)
        self.assertIn("MATERIAL_EFFECT_PATH_OBSERVATION_HEAD_STALE",validate_material_effect_path(p,current_observation_head=l["head_digest"]))

    def test_real_observed_unadmitted_path_drives_condition(self):
        b,l=self.good_surface(); s=derive_material_authority_surface(b); self.assertTrue(s["qualified"])
        r=evaluate_material_discovery({"observation_ledger_state":QUALIFIED,"material_surface_state":QUALIFIED,"observed_material_ids":["PATH-A","PATH-B"],"admitted_material_ids":["PATH-A"],"observation_head_digest":l["head_digest"],"material_surface_digest":s["surface_digest"]})
        self.assertFalse(r["qualified"]); self.assertIn(AUTHORITY_ADMISSION_REQUIRED,r["problems"]); self.assertEqual(r["unadmitted_material_ids"],["PATH-B"]); self.assertEqual(r["conditions"][0]["subject_id"],"PATH-B")

    def test_all_observed_admitted_clears_discovery(self):
        b,l=self.good_surface(); s=derive_material_authority_surface(b)
        r=evaluate_material_discovery({"observation_ledger_state":QUALIFIED,"material_surface_state":QUALIFIED,"observed_material_ids":["PATH-A","PATH-B"],"admitted_material_ids":["PATH-A","PATH-B"],"observation_head_digest":l["head_digest"],"material_surface_digest":s["surface_digest"]})
        self.assertTrue(r["qualified"],r["problems"])

if __name__=="__main__": unittest.main()
