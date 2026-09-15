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
from v24_v6_test_proof_context import build_test_proof_context

D1="1"*64; D2="2"*64; D3="3"*64; D4="4"*64; D5="5"*64; D6="6"*64
WCONTENT="a"*64; M1CONTENT="b"*64; M2CONTENT="c"*64; C1CONTENT="d"*64; C2CONTENT="e"*64; PATHCONTENT="f"*64


def observation(seq, prev, oid, entity, currentness_ref=D2):
    r={"observation_id":oid,"observation_sequence":seq,"predecessor_record_digest":prev,"observer_identity":"OBS","observer_control_domain_id":"OBS-DOM","source_kind":"RUNTIME","entity_or_path_id":entity,"evidence_class_id":"E-MAT","evidence_digest":D1,"currentness_binding_digest":currentness_ref,"record_digest":""}
    x=dict(r); x.pop("record_digest"); r["record_digest"]=digest(x); return r


def _ledger(refs=None):
    genesis=D3
    r1=observation(1,genesis,"O1","PATH-A",refs["obs1_c"] if refs else D2)
    r2=observation(2,r1["record_digest"],"O2","PATH-B",refs["obs2_c"] if refs else D2)
    ds=[r1["record_digest"],r2["record_digest"]]; hd=digest(ds)
    witness={"witness_identity":"W1","witness_control_domain_id":"W-DOM","observed_head_digest":hd,"observed_sequence":2,"currentness_result":CURRENT,"independence_result":QUALIFIED}
    if refs:
        witness.update({"witness_content_digest":WCONTENT,"witness_qualification_digest":refs["witness_q"],"witness_independence_qualification_digest":refs["witness_i"],"witness_currentness_binding_digest":refs["witness_c"]})
    return {"genesis_predecessor_digest":genesis,"records":[r1,r2],"head":{"ledger_id":"LEDGER","latest_sequence":2,"latest_record_digest":r2["record_digest"],"cumulative_root_digest":hd,"durable_storage_identity":"STORE","durable_anchor_identity":"ANCHOR","durable_anchor_digest":D4,"anchor_sequence":2,"fork_or_rollback_detected":False,"operator_control_domain_id":"OP-DOM","witness_currentness_records":[witness]}}


def ledger_bundle():
    """Legacy opaque-label fixture retained for the permanent false-green regression."""
    return _ledger()


def proof_closed_ledger_bundle():
    context,boundary,refs=build_test_proof_context({
        "obs1_c":{"kind":"CURRENTNESS","source_id":"PATH-A","source_digest":D1},
        "obs2_c":{"kind":"CURRENTNESS","source_id":"PATH-B","source_digest":D1},
        "witness_q":{"kind":"QUALIFICATION","subject_id":"W1","content_digest":WCONTENT},
        "witness_i":{"kind":"INDEPENDENCE","subject_identity_id":"W1"},
        "witness_c":{"kind":"CURRENTNESS","source_id":"W1","source_digest":WCONTENT},
    })
    return _ledger(refs),context,boundary


def derivation(i, members, domain, refs=None):
    content=M1CONTENT if i==1 else M2CONTENT
    d={"derivation_id":f"D{i}","derivation_mechanism_id":f"M{i}","derivation_authority_id":f"A{i}","control_domain_id":domain,"derivation_mechanism_content_digest":content,"mechanism_qualification_digest":D1,"authority_independence_qualification_digest":D2,"currentness_binding_digest":D3,"mechanism_qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"member_ids":list(members),"source_kinds":["DEPLOYMENT","RUNTIME_OBSERVATION"],"derivation_digest":D5}
    if refs:
        d["mechanism_qualification_digest"]=refs[f"d{i}_q"];d["authority_independence_qualification_digest"]=refs[f"d{i}_i"];d["currentness_binding_digest"]=refs[f"d{i}_c"]
    return d


def classifications(ids, refs=None):
    out=[]
    for n,sid in enumerate(sorted(ids),1):
        cid=f"CLASSIFIER-{sid}"; content=C1CONTENT if n==1 else C2CONTENT
        c={"subject_id":sid,"classification":MATERIAL,"classifier_id":cid,"classifier_content_digest":content,"classifier_qualification_digest":D1,"classifier_independence_qualification_digest":D2,"currentness_binding_digest":D3,"classifier_qualification_state":QUALIFIED,"classifier_independence_state":QUALIFIED,"currentness_result":CURRENT}
        if refs:
            key=sid.replace("-","_").lower();c["classifier_qualification_digest"]=refs[f"{key}_q"];c["classifier_independence_qualification_digest"]=refs[f"{key}_i"];c["currentness_binding_digest"]=refs[f"{key}_c"]
        out.append(c)
    return out


def surface_fixture(l):
    ids={"PATH-A","PATH-B"}
    specs={
        "ledger_q":{"kind":"QUALIFICATION","subject_id":"LEDGER","content_digest":l["head_digest"]},
        "d1_q":{"kind":"QUALIFICATION","subject_id":"M1","content_digest":M1CONTENT},
        "d1_i":{"kind":"INDEPENDENCE","subject_identity_id":"A1"},
        "d1_c":{"kind":"CURRENTNESS","source_id":"M1","source_digest":M1CONTENT},
        "d2_q":{"kind":"QUALIFICATION","subject_id":"M2","content_digest":M2CONTENT},
        "d2_i":{"kind":"INDEPENDENCE","subject_identity_id":"A2"},
        "d2_c":{"kind":"CURRENTNESS","source_id":"M2","source_digest":M2CONTENT},
        "path_a_q":{"kind":"QUALIFICATION","subject_id":"CLASSIFIER-PATH-A","content_digest":C1CONTENT},
        "path_a_i":{"kind":"INDEPENDENCE","subject_identity_id":"CLASSIFIER-PATH-A"},
        "path_a_c":{"kind":"CURRENTNESS","source_id":"CLASSIFIER-PATH-A","source_digest":C1CONTENT},
        "path_b_q":{"kind":"QUALIFICATION","subject_id":"CLASSIFIER-PATH-B","content_digest":C2CONTENT},
        "path_b_i":{"kind":"INDEPENDENCE","subject_identity_id":"CLASSIFIER-PATH-B"},
        "path_b_c":{"kind":"CURRENTNESS","source_id":"CLASSIFIER-PATH-B","source_digest":C2CONTENT},
    }
    context,boundary,refs=build_test_proof_context(specs)
    b={"observation_ledger_state":QUALIFIED,"observation_ledger_id":"LEDGER","observation_ledger_qualification_digest":refs["ledger_q"],"observation_head_digest":l["head_digest"],"observed_entity_or_path_ids":l["observed_entity_or_path_ids"],"material_surface_id":"SURFACE-1","derivations":[derivation(1,ids,"D-A",refs),derivation(2,ids,"D-B",refs)],"materiality_classifications":classifications(ids,refs)}
    return b,context,boundary


def effect_path(head, refs=None):
    p={"path_id":"EP-1","path_content_digest":PATHCONTENT,"source_or_writer_id":"WRITER","sink_id":"SINK","effect_class_id":"WRITE","writer_admission_id":"WRITER-ADMISSION-1","writer_admission_digest":D1,"writer_admission_qualification_digest":D1,"capability_id":"CAPABILITY-1","capability_digest":D2,"capability_qualification_digest":D2,"guard_mechanism_id":"GUARD-1","guard_mechanism_digest":D3,"guard_qualification_digest":D3,"currentness_binding_digest":D4,"sink_admitted_writer_set_digest":D4,"material_surface_membership_digest":D5,"observation_head_digest":head,"writer_admission_state":QUALIFIED,"capability_state":QUALIFIED,"guard_qualification_state":QUALIFIED,"sink_admitted_writer_ids":["WRITER"],"dependency_edge_digests":[D1],"control_plane_evidence_digests":[D2],"currentness_result":CURRENT}
    if refs:
        p["writer_admission_qualification_digest"]=refs["writer_q"];p["capability_qualification_digest"]=refs["cap_q"];p["guard_qualification_digest"]=refs["guard_q"];p["currentness_binding_digest"]=refs["path_c"]
    return p


def effect_fixture(head):
    context,boundary,refs=build_test_proof_context({
        "writer_q":{"kind":"QUALIFICATION","subject_id":"WRITER-ADMISSION-1","content_digest":D1},
        "cap_q":{"kind":"QUALIFICATION","subject_id":"CAPABILITY-1","content_digest":D2},
        "guard_q":{"kind":"QUALIFICATION","subject_id":"GUARD-1","content_digest":D3},
        "path_c":{"kind":"CURRENTNESS","source_id":"EP-1","source_digest":PATHCONTENT},
    })
    return effect_path(head,refs),context,boundary


def discovery_fixture(l,s,admitted):
    context,boundary,refs=build_test_proof_context({
        "ledger_q":{"kind":"QUALIFICATION","subject_id":"LEDGER","content_digest":l["head_digest"]},
        "surface_q":{"kind":"QUALIFICATION","subject_id":s["material_surface_id"],"content_digest":s["surface_digest"]},
    })
    b={"observation_ledger_state":QUALIFIED,"material_surface_state":QUALIFIED,"observation_ledger_id":"LEDGER","observation_ledger_qualification_digest":refs["ledger_q"],"material_surface_id":s["material_surface_id"],"material_surface_qualification_digest":refs["surface_q"],"observed_material_ids":["PATH-A","PATH-B"],"admitted_material_ids":admitted,"observation_head_digest":l["head_digest"],"material_surface_digest":s["surface_digest"]}
    return b,context,boundary


class R3MaterialSurfaceTests(unittest.TestCase):
    def test_construction_frontier_non_authoritative(self):
        r=construction_frontier(); self.assertFalse(r["qualified"])

    def test_observation_ledger_valid(self):
        b,c,t=proof_closed_ledger_bundle();r=validate_material_observation_ledger(b,proof_context=c,trusted_boundary=t); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["observed_entity_or_path_ids"],["PATH-A","PATH-B"])

    def test_fabricated_witness_labels_without_proofs_fail(self):
        r=validate_material_observation_ledger(ledger_bundle());self.assertFalse(r["qualified"]);self.assertTrue(any("WITNESS_PROOF" in x or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in x for x in r["problems"]))

    def test_observation_ledger_predecessor_tamper_fails(self):
        b,c,t=proof_closed_ledger_bundle(); b["records"][1]["predecessor_record_digest"]=D6
        r=validate_material_observation_ledger(b,proof_context=c,trusted_boundary=t); self.assertTrue(any("PREDECESSOR_MISMATCH" in x for x in r["problems"]))

    def test_observation_ledger_unanchored_fails(self):
        b,c,t=proof_closed_ledger_bundle(); b["head"]["durable_anchor_digest"]=""
        r=validate_material_observation_ledger(b,proof_context=c,trusted_boundary=t); self.assertIn("MATERIAL_OBSERVATION_ANCHOR_DIGEST_INVALID",r["problems"])

    def test_observation_ledger_operator_only_witness_fails(self):
        b,c,t=proof_closed_ledger_bundle(); b["head"]["witness_currentness_records"][0]["witness_control_domain_id"]="OP-DOM"
        r=validate_material_observation_ledger(b,proof_context=c,trusted_boundary=t); self.assertIn("MATERIAL_OBSERVATION_NO_QUALIFIED_INDEPENDENT_WITNESS",r["problems"])

    def good_surface(self):
        lb,lc,lt=proof_closed_ledger_bundle();l=validate_material_observation_ledger(lb,proof_context=lc,trusted_boundary=lt); self.assertTrue(l["qualified"],l["problems"])
        b,c,t=surface_fixture(l);return b,l,c,t

    def test_two_independent_consistent_derivations_qualify(self):
        b,l,c,t=self.good_surface(); r=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["material_member_ids"],["PATH-A","PATH-B"])

    def test_derivation_divergence_blocks(self):
        b,l,c,t=self.good_surface(); b["derivations"][1]["member_ids"]=["PATH-A"]
        r=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertIn("MATERIAL_SURFACE_DERIVATION_DIVERGENCE:1",r["problems"]); self.assertFalse(r["qualified"])

    def test_same_control_domain_not_independent(self):
        b,l,c,t=self.good_surface(); b["derivations"][1]["control_domain_id"]="D-A"
        r=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertIn("MATERIAL_SURFACE_DERIVATION_CONTROL_DOMAIN_DUPLICATE:D-A",r["problems"])

    def test_candidate_only_derivation_forbidden(self):
        b,l,c,t=self.good_surface(); b["derivations"][0]["source_kinds"]=["CANDIDATE_SELF_REPORT"]
        r=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertIn("MATERIAL_SURFACE_CANDIDATE_ONLY_DERIVATION_FORBIDDEN:0",r["problems"])

    def test_missing_materiality_classification_blocks(self):
        b,l,c,t=self.good_surface(); b["materiality_classifications"].pop()
        r=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertTrue(any("MATERIALITY_CLASSIFICATION_MISSING" in x for x in r["problems"]))

    def test_effect_path_closure_passes(self):
        lb,lc,lt=proof_closed_ledger_bundle();l=validate_material_observation_ledger(lb,proof_context=lc,trusted_boundary=lt);p,c,t=effect_fixture(l["head_digest"]);self.assertEqual(validate_material_effect_path(p,current_observation_head=l["head_digest"],proof_context=c,trusted_boundary=t),[])

    def test_direct_writer_missing_from_sink_blocks(self):
        lb,lc,lt=proof_closed_ledger_bundle();l=validate_material_observation_ledger(lb,proof_context=lc,trusted_boundary=lt);p,c,t=effect_fixture(l["head_digest"]);p["sink_admitted_writer_ids"]=["OTHER"]
        self.assertIn("MATERIAL_EFFECT_PATH_WRITER_NOT_ADMITTED_AT_SINK",validate_material_effect_path(p,current_observation_head=l["head_digest"],proof_context=c,trusted_boundary=t))

    def test_stale_observation_head_blocks_effect_path(self):
        lb,lc,lt=proof_closed_ledger_bundle();l=validate_material_observation_ledger(lb,proof_context=lc,trusted_boundary=lt);p,c,t=effect_fixture(D6)
        self.assertIn("MATERIAL_EFFECT_PATH_OBSERVATION_HEAD_STALE",validate_material_effect_path(p,current_observation_head=l["head_digest"],proof_context=c,trusted_boundary=t))

    def test_real_observed_unadmitted_path_drives_condition(self):
        b,l,c,t=self.good_surface(); s=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t); self.assertTrue(s["qualified"],s["problems"])
        d,dc,dt=discovery_fixture(l,s,["PATH-A"]);r=evaluate_material_discovery(d,proof_context=dc,trusted_boundary=dt)
        self.assertFalse(r["qualified"]); self.assertIn(AUTHORITY_ADMISSION_REQUIRED,r["problems"]); self.assertEqual(r["unadmitted_material_ids"],["PATH-B"]); self.assertEqual(r["conditions"][0]["subject_id"],"PATH-B")

    def test_all_observed_admitted_clears_discovery(self):
        b,l,c,t=self.good_surface(); s=derive_material_authority_surface(b,proof_context=c,trusted_boundary=t)
        d,dc,dt=discovery_fixture(l,s,["PATH-A","PATH-B"]);r=evaluate_material_discovery(d,proof_context=dc,trusted_boundary=dt)
        self.assertTrue(r["qualified"],r["problems"])

if __name__=="__main__": unittest.main()
