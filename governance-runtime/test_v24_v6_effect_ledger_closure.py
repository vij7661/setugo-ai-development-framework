from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_effect_ledger_closure import (
    canonical_anchor_content_digest,
    canonical_derivation_content_digest,
    canonical_effect_path_content_digest,
    canonical_effect_registry_content_digest,
    canonical_ledger_head_digest,
    canonical_storage_content_digest,
    canonical_witness_content_digest,
    derive_effect_class_obligation_set,
    validate_durable_governance_ledger,
    validate_effect_class_registry,
    validate_effect_path_against_registry,
)
from v24_v6_test_proof_context import build_test_proof_context

H="a"*64;Q="b"*64;E="c"*64
REGISTRY_ID="EFFECT-CLASS-REGISTRY";REGISTRY_RESULT_ID="EFFECT-CLASS-REGISTRY-RESULT"


def seal(record: dict, field: str) -> dict:
    material=dict(record);material.pop(field,None);record[field]=digest(material);return record


def currentness(source_id: str, source_digest: str, verifier_ref: str=Q) -> dict:
    return seal({
        "currentness_rule_id":"CURRENT-RULE-1",
        "source_object_id":source_id,
        "source_version_or_sequence":"1",
        "source_digest":source_digest,
        "verifier_qualification_digest":verifier_ref,
        "result":CURRENT,
        "observed_at_sequence":1,
        "binding_digest":"",
    },"binding_digest")


# Legacy label-only fixture retained for the permanent R6 RED.
def durable_ledger(kind: str="MATERIAL_OBSERVATION") -> dict:
    genesis="0"*64
    r1={"record_id":"R-1","ledger_kind":kind,"sequence":1,"predecessor_record_digest":genesis,"producer_identity_id":"PRODUCER-1","producer_control_domain_id":"DOMAIN-P","evidence_class_id":"EVIDENCE-1","event_or_subject_id":"SUBJECT-1","event_digest":E,"record_digest":""}
    seal(r1,"record_digest");record_digests=[r1["record_digest"]]
    head={"ledger_id":f"LEDGER-{kind}","ledger_kind":kind,"operator_identity_id":"OPERATOR-1","operator_control_domain_id":"DOMAIN-OP","durable_storage_identity":"STORE-1","durable_storage_class":"DURABLE_APPEND_ONLY","durable_anchor_identity":"ANCHOR-1","durable_anchor_class":"INDEPENDENT_DURABLE_ANCHOR","durable_anchor_digest":H,"anchor_sequence":1,"latest_sequence":1,"latest_record_digest":r1["record_digest"],"cumulative_root_digest":digest(record_digests),"fork_or_rollback_detected":False,"head_qualification_state":QUALIFIED,"currentness_result":CURRENT,"head_digest":"","witness_currentness_records":[]}
    material=dict(head);material.pop("head_digest");material.pop("witness_currentness_records");head["head_digest"]=digest(material)
    witness={"witness_identity_id":"WITNESS-1","witness_control_domain_id":"DOMAIN-W","evidence_class_id":"WITNESS-EVIDENCE","currentness_rule_id":"WITNESS-CURRENT-RULE","independence_qualification_digest":Q,"observed_head_digest":head["head_digest"],"observed_sequence":1,"currentness_result":CURRENT,"independence_result":QUALIFIED,"witness_record_digest":""}
    seal(witness,"witness_record_digest");head["witness_currentness_records"]=[witness]
    return {"genesis_predecessor_digest":genesis,"records":[r1],"head":head}


def proof_closed_durable_ledger(kind: str="MATERIAL_OBSERVATION"):
    genesis="0"*64
    r1={"record_id":"R-1","ledger_kind":kind,"sequence":1,"predecessor_record_digest":genesis,"producer_identity_id":"PRODUCER-1","producer_control_domain_id":"DOMAIN-P","evidence_class_id":"EVIDENCE-1","event_or_subject_id":"SUBJECT-1","event_digest":E,"record_digest":""}
    seal(r1,"record_digest")
    head={
        "ledger_id":f"LEDGER-{kind}","head_object_id":f"LEDGER-HEAD-{kind}","ledger_kind":kind,
        "operator_identity_id":"OPERATOR-1","operator_control_domain_id":"DOMAIN-OP",
        "durable_storage_identity":"STORE-1","durable_storage_class":"DURABLE_APPEND_ONLY",
        "durable_anchor_identity":"ANCHOR-1","durable_anchor_class":"INDEPENDENT_DURABLE_ANCHOR",
        "durable_anchor_digest":H,"anchor_sequence":1,"latest_sequence":1,"latest_record_digest":r1["record_digest"],
        "cumulative_root_digest":digest([r1["record_digest"]]),"fork_or_rollback_detected":False,
        "head_qualification_state":QUALIFIED,"currentness_result":CURRENT,
    }
    head["storage_content_digest"]=canonical_storage_content_digest(head)
    head["anchor_content_digest"]=canonical_anchor_content_digest(head)
    head["head_digest"]=canonical_ledger_head_digest(head)
    witness={
        "witness_record_id":"WITNESS-RECORD-1","witness_identity_id":"WITNESS-1","witness_control_domain_id":"DOMAIN-W",
        "evidence_class_id":"WITNESS-EVIDENCE","currentness_rule_id":"WITNESS-CURRENT-RULE",
        "observed_head_digest":head["head_digest"],"observed_sequence":1,"currentness_result":CURRENT,"independence_result":QUALIFIED,
    }
    witness["witness_content_digest"]=canonical_witness_content_digest(witness)
    witness["witness_record_digest"]=witness["witness_content_digest"]
    specs={
        "head_q":{"kind":"QUALIFICATION","subject_id":head["head_object_id"],"content_digest":head["head_digest"]},
        "head_c":{"kind":"CURRENTNESS","source_id":head["head_object_id"],"source_digest":head["head_digest"]},
        "storage_q":{"kind":"QUALIFICATION","subject_id":"STORE-1","content_digest":head["storage_content_digest"]},
        "storage_c":{"kind":"CURRENTNESS","source_id":"STORE-1","source_digest":head["storage_content_digest"]},
        "anchor_q":{"kind":"QUALIFICATION","subject_id":"ANCHOR-1","content_digest":head["anchor_content_digest"]},
        "anchor_i":{"kind":"INDEPENDENCE","subject_identity_id":"ANCHOR-1"},
        "anchor_c":{"kind":"CURRENTNESS","source_id":"ANCHOR-1","source_digest":head["anchor_content_digest"]},
        "witness_q":{"kind":"QUALIFICATION","subject_id":"WITNESS-RECORD-1","content_digest":witness["witness_content_digest"]},
        "witness_i":{"kind":"INDEPENDENCE","subject_identity_id":"WITNESS-1"},
        "witness_c":{"kind":"CURRENTNESS","source_id":"WITNESS-RECORD-1","source_digest":witness["witness_content_digest"]},
    }
    context,boundary,refs=build_test_proof_context(specs)
    head.update({
        "head_qualification_digest":refs["head_q"],"head_currentness_binding_digest":refs["head_c"],
        "storage_qualification_digest":refs["storage_q"],"storage_currentness_binding_digest":refs["storage_c"],
        "anchor_qualification_digest":refs["anchor_q"],"anchor_independence_qualification_digest":refs["anchor_i"],"anchor_currentness_binding_digest":refs["anchor_c"],
    })
    witness.update({"witness_qualification_digest":refs["witness_q"],"independence_qualification_digest":refs["witness_i"],"currentness_binding_digest":refs["witness_c"]})
    head["witness_currentness_records"]=[witness]
    return {"genesis_predecessor_digest":genesis,"records":[r1],"head":head},context,boundary


def _derivation_base(idx,source,effect_ids,obs_head):
    d={
        "derivation_id":f"DERIVE-{idx}","source_surface_class":source,"source_surface_digest":str(idx)*64,
        "derivation_mechanism_id":f"DERIVE-MECH-{idx}","derivation_mechanism_content_digest":str(idx+3)*64,
        "derivation_authority_id":f"DERIVE-AUTH-{idx}","mechanism_qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,
        "currentness_result":CURRENT,"control_domain_id":f"DOMAIN-D{idx}",
        "observation_head_digest":obs_head if source=="EFFECT_OBSERVATION" else None,"effect_class_ids":list(effect_ids),
    }
    d["derivation_content_digest"]=canonical_derivation_content_digest(d);return d


def _completeness(registry_digest,expected,actual,refs):
    roots=[
        {"node_id":"ROOT-I","omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":"1"*64},
        {"node_id":"ROOT-D","omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":"2"*64},
        {"node_id":"ROOT-E","omission_sensitive":False,"root_kind":"EFFECT_PATH_OBSERVATION","source_surface_digest":"3"*64},
    ]
    graph={"nodes":[{"node_id":REGISTRY_ID,"omission_sensitive":True},*roots],"edges":[{"from":REGISTRY_ID,"to":"ROOT-I"},{"from":REGISTRY_ID,"to":"ROOT-D"},{"from":REGISTRY_ID,"to":"ROOT-E"}]}
    rec={
        "subject_object_id":REGISTRY_ID,"subject_content_digest":registry_digest,
        "expected_member_set_digest":digest(sorted(expected)),"actual_member_set_digest":digest(sorted(actual)),
        "set_equality_proof_digest":digest({"expected":sorted(expected),"actual":sorted(actual)}),
        "verifier_qualification_digest":refs["comp_q"],"expected_members":sorted(expected),"actual_members":sorted(actual),
        "completeness_derivation_graph":graph,"derivation_mechanism_qualification_digests":[refs["comp_q"]],
        "derivation_authority_independence_digests":[refs["comp_i"]],"source_surface_digests":["1"*64,"2"*64,"3"*64],
        "currentness_bindings":[currentness(REGISTRY_ID,registry_digest,refs["comp_q"])],"result":QUALIFIED,"qualification_digest":"",
    }
    return seal(rec,"qualification_digest")


def proof_closed_registry_fixture(extra_observed: str|None=None):
    obs_head="9"*64;members=["STATE_WRITE","REMOTE_EFFECT"]
    derivations=[]
    for idx,source in enumerate(("IMPLEMENTATION_ARTIFACT","DEPLOYMENT_ARTIFACT","EFFECT_OBSERVATION"),1):
        effects=list(members)
        if extra_observed and source=="EFFECT_OBSERVATION":effects.append(extra_observed)
        derivations.append(_derivation_base(idx,source,effects,obs_head))
    verifier_contents={"REMOTE_EFFECT":"7"*64,"STATE_WRITE":"8"*64}
    specs={"comp_q":{"kind":"QUALIFICATION","subject_id":"COMP-MECH","content_digest":"6"*64},"comp_i":{"kind":"INDEPENDENCE","subject_identity_id":"COMP-AUTH"}}
    for idx,d in enumerate(derivations,1):
        specs[f"d{idx}_q"]={"kind":"QUALIFICATION","subject_id":d["derivation_mechanism_id"],"content_digest":d["derivation_mechanism_content_digest"]}
        specs[f"d{idx}_i"]={"kind":"INDEPENDENCE","subject_identity_id":d["derivation_authority_id"]}
        specs[f"d{idx}_c"]={"kind":"CURRENTNESS","source_id":d["derivation_id"],"source_digest":d["derivation_content_digest"]}
    for cid,content in verifier_contents.items():
        key=cid.lower();specs[f"{key}_q"]={"kind":"QUALIFICATION","subject_id":f"VERIFY-{cid}","content_digest":content};specs[f"{key}_c"]={"kind":"CURRENTNESS","source_id":f"VERIFY-{cid}","source_digest":content}
    _,_,refs1=build_test_proof_context(specs)
    for idx,d in enumerate(derivations,1):
        d.update({"derivation_mechanism_qualification_digest":refs1[f"d{idx}_q"],"derivation_authority_independence_digest":refs1[f"d{idx}_i"],"currentness_binding_digest":refs1[f"d{idx}_c"]})
    entries=[]
    for cid in sorted(verifier_contents):
        key=cid.lower();entries.append({"effect_class_id":cid,"proof_schema_digest":H,"verifier_mechanism_id":f"VERIFY-{cid}","verifier_mechanism_content_digest":verifier_contents[cid],"verifier_qualification_digest":refs1[f"{key}_q"],"verifier_currentness_binding_digest":refs1[f"{key}_c"],"verifier_qualification_state":QUALIFIED,"currentness_result":CURRENT})
    registry={"registry_id":REGISTRY_ID,"entries":entries,"currentness_result":CURRENT,"qualification_state":QUALIFIED}
    registry["content_digest"]=canonical_effect_registry_content_digest(registry)
    specs2=dict(specs);specs2["registry_q"]={"kind":"QUALIFICATION","subject_id":REGISTRY_ID,"content_digest":registry["content_digest"]};specs2["registry_c"]={"kind":"CURRENTNESS","source_id":REGISTRY_ID,"source_digest":registry["content_digest"]}
    context,boundary,refs=build_test_proof_context(specs2)
    registry.update({"qualification_digest":refs["registry_q"],"currentness_binding_digest":refs["registry_c"]})
    expected=sorted(set(x for d in derivations for x in d["effect_class_ids"]));actual=["REMOTE_EFFECT","STATE_WRITE"]
    completeness=_completeness(registry["content_digest"],expected,actual,refs)
    return {"registry":registry,"derivations":derivations,"current_observation_head_digest":obs_head,"completeness_qualification":completeness},context,boundary,specs2


def proof_effect_path(effect_class_id,refs,currentness_ref=""):
    p={
        "path_id":"EP-1","source_or_writer_id":"WRITER-1","sink_id":"SINK-1","effect_class_id":effect_class_id,
        "writer_admission_id":"WRITER-ADMISSION-1","writer_admission_digest":H,"writer_admission_qualification_digest":refs["writer_q"],
        "capability_id":"CAPABILITY-1","capability_digest":Q,"capability_qualification_digest":refs["cap_q"],
        "guard_mechanism_id":"GUARD-1","guard_mechanism_digest":E,"guard_qualification_digest":refs["guard_q"],
        "currentness_binding_digest":currentness_ref,"sink_admitted_writer_set_digest":"d"*64,"material_surface_membership_digest":"e"*64,
        "observation_head_digest":"9"*64,"writer_admission_state":QUALIFIED,"capability_state":QUALIFIED,"guard_qualification_state":QUALIFIED,
        "sink_admitted_writer_ids":["WRITER-1"],"dependency_edge_digests":["f"*64],"control_plane_evidence_digests":["8"*64],"currentness_result":CURRENT,
    }
    p["path_content_digest"]=canonical_effect_path_content_digest(p)
    return p


def registry_and_path_fixture(effect_class_id="STATE_WRITE"):
    bundle,context,boundary,specs=proof_closed_registry_fixture();rr=validate_effect_class_registry(bundle,proof_context=context,trusted_boundary=boundary);assert rr["qualified"],rr["problems"]
    extended=dict(specs)
    extended.update({
        "result_q":{"kind":"QUALIFICATION","subject_id":REGISTRY_RESULT_ID,"content_digest":rr["registry_result_digest"]},
        "writer_q":{"kind":"QUALIFICATION","subject_id":"WRITER-ADMISSION-1","content_digest":H},
        "cap_q":{"kind":"QUALIFICATION","subject_id":"CAPABILITY-1","content_digest":Q},
        "guard_q":{"kind":"QUALIFICATION","subject_id":"GUARD-1","content_digest":E},
    })
    _,_,pre_refs=build_test_proof_context(extended)
    draft=proof_effect_path(effect_class_id,pre_refs)
    extended["path_c"]={"kind":"CURRENTNESS","source_id":draft["path_id"],"source_digest":draft["path_content_digest"]}
    context,boundary,refs=build_test_proof_context(extended)
    path=proof_effect_path(effect_class_id,refs,refs["path_c"])
    rr=validate_effect_class_registry(bundle,proof_context=context,trusted_boundary=boundary);assert rr["qualified"],rr["problems"]
    rr=dict(rr);rr["registry_result_id"]=REGISTRY_RESULT_ID;rr["registry_result_qualification_digest"]=refs["result_q"]
    return path,rr,context,boundary


class DurableLedgerTests(unittest.TestCase):
    def test_material_observation_ledger_positive(self):
        b,c,t=proof_closed_durable_ledger();r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertTrue(r["qualified"],r["problems"])

    def test_completeness_ledger_positive(self):
        b,c,t=proof_closed_durable_ledger("COMPLETENESS");r=validate_durable_governance_ledger(b,ledger_kind="COMPLETENESS",proof_context=c,trusted_boundary=t);self.assertTrue(r["qualified"],r["problems"])

    def test_opaque_head_and_witness_labels_fail(self):
        r=validate_durable_governance_ledger(durable_ledger(),ledger_kind="MATERIAL_OBSERVATION");self.assertFalse(r["qualified"]);self.assertTrue(any("DURABLE_LEDGER_HEAD_PROOF" in x or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in x for x in r["problems"]))

    def test_process_memory_head_cannot_be_authoritative(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["durable_storage_class"]="PROCESS_MEMORY";r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertIn("DURABLE_LEDGER_STORAGE_NOT_DURABLE",r["problems"])

    def test_unanchored_local_head_blocks(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["durable_anchor_class"]="UNANCHORED_LOCAL";r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertIn("DURABLE_LEDGER_ANCHOR_NOT_DURABLE",r["problems"])

    def test_rollback_or_fork_blocks(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["fork_or_rollback_detected"]=True;r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertIn("DURABLE_LEDGER_FORK_OR_ROLLBACK_DETECTED",r["problems"])

    def test_same_control_domain_witness_blocks(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["witness_currentness_records"][0]["witness_control_domain_id"]="DOMAIN-OP";r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertIn("DURABLE_LEDGER_NO_QUALIFIED_INDEPENDENT_WITNESS",r["problems"])

    def test_stale_witness_blocks(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["witness_currentness_records"][0]["currentness_result"]="STALE";r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertIn("DURABLE_LEDGER_NO_QUALIFIED_INDEPENDENT_WITNESS",r["problems"])

    def test_anchor_identity_without_independence_proof_blocks(self):
        b,c,t=proof_closed_durable_ledger();b["head"]["anchor_independence_qualification_digest"]="0"*64;r=validate_durable_governance_ledger(b,ledger_kind="MATERIAL_OBSERVATION",proof_context=c,trusted_boundary=t);self.assertTrue(any("DURABLE_LEDGER_HEAD_PROOF" in x and "UNRESOLVED" in x for x in r["problems"]))


class EffectClassTests(unittest.TestCase):
    def test_effect_class_registry_positive(self):
        b,c,t,_=proof_closed_registry_fixture();r=validate_effect_class_registry(b,proof_context=c,trusted_boundary=t);self.assertTrue(r["qualified"],r["problems"]);self.assertEqual(["REMOTE_EFFECT","STATE_WRITE"],r["actual_members"])

    def test_missing_required_source_surface_blocks(self):
        b,c,t,_=proof_closed_registry_fixture();b["derivations"]=b["derivations"][:-1];r=validate_effect_class_registry(b,proof_context=c,trusted_boundary=t);self.assertTrue(any("EFFECT_CLASS_REQUIRED_SOURCE_MISSING:EFFECT_OBSERVATION" in p for p in r["problems"]))

    def test_new_observed_effect_class_missing_from_registry_blocks(self):
        b,c,t,_=proof_closed_registry_fixture("UNREGISTERED_NEW_EFFECT");r=validate_effect_class_registry(b,proof_context=c,trusted_boundary=t);self.assertIn("EFFECT_CLASS_REGISTRY_SET_EQUALITY_FAILED",r["problems"])

    def test_registry_extra_caller_class_not_independently_observed_blocks(self):
        b,c,t,_=proof_closed_registry_fixture();extra=copy.deepcopy(b["registry"]["entries"][0]);extra["effect_class_id"]="CALLER_ONLY";b["registry"]["entries"].append(extra);b["registry"]["content_digest"]=canonical_effect_registry_content_digest(b["registry"]);r=validate_effect_class_registry(b,proof_context=c,trusted_boundary=t);self.assertIn("EFFECT_CLASS_REGISTRY_SET_EQUALITY_FAILED",r["problems"])

    def test_stale_effect_class_verifier_blocks(self):
        b,c,t,_=proof_closed_registry_fixture();b["registry"]["entries"][0]["currentness_result"]="STALE";r=validate_effect_class_registry(b,proof_context=c,trusted_boundary=t);self.assertTrue(any("EFFECT_CLASS_ENTRY_NOT_CURRENT" in p for p in r["problems"]))

    def test_opaque_derivation_labels_without_proofs_block(self):
        legacy=[{"derivation_id":"D1","source_surface_class":"IMPLEMENTATION_ARTIFACT","source_surface_digest":"1"*64,"derivation_mechanism_qualification_digest":Q,"derivation_authority_independence_digest":E,"mechanism_qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"control_domain_id":"D","effect_class_ids":["WRITE"]}]
        r=derive_effect_class_obligation_set(legacy,current_observation_head_digest="9"*64);self.assertFalse(r["qualified"]);self.assertTrue(any("EFFECT_CLASS_DERIVATION_PROOF" in x or "PROOF_DIGEST_INVALID" in x for x in r["problems"]))

    def test_registered_effect_path_classifies(self):
        path,rr,c,t=registry_and_path_fixture();r=validate_effect_path_against_registry(path,current_observation_head_digest="9"*64,registry_result=rr,proof_context=c,trusted_boundary=t);self.assertTrue(r["qualified"],r["problems"])

    def test_registered_to_registered_effect_class_substitution_blocks(self):
        path,rr,c,t=registry_and_path_fixture("STATE_WRITE");path["effect_class_id"]="REMOTE_EFFECT";r=validate_effect_path_against_registry(path,current_observation_head_digest="9"*64,registry_result=rr,proof_context=c,trusted_boundary=t);self.assertFalse(r["qualified"]);self.assertIn("MATERIAL_EFFECT_PATH_CONTENT_DIGEST_MISMATCH",r["problems"])

    def test_unregistered_effect_class_blocks_effect_path(self):
        path,rr,c,t=registry_and_path_fixture("UNKNOWN_EFFECT");r=validate_effect_path_against_registry(path,current_observation_head_digest="9"*64,registry_result=rr,proof_context=c,trusted_boundary=t);self.assertIn("MATERIAL_EFFECT_PATH_EFFECT_CLASS_UNKNOWN_OR_UNREGISTERED",r["problems"])

    def test_registry_result_requires_independent_qualification(self):
        path,rr,c,t=registry_and_path_fixture();rr.pop("registry_result_qualification_digest");r=validate_effect_path_against_registry(path,current_observation_head_digest="9"*64,registry_result=rr,proof_context=c,trusted_boundary=t);self.assertTrue(any("MATERIAL_EFFECT_PATH_REGISTRY_RESULT_PROOF" in x for x in r["problems"]))

    def test_caller_cannot_override_bound_registry_members(self):
        path,rr,c,t=registry_and_path_fixture();rr["actual_members"]=["STATE_WRITE","CALLER_ONLY"];r=validate_effect_path_against_registry(path,current_observation_head_digest="9"*64,registry_result=rr,proof_context=c,trusted_boundary=t);self.assertIn("MATERIAL_EFFECT_PATH_CALLER_REGISTRY_MEMBERS_MISMATCH",r["problems"])


if __name__=="__main__":unittest.main()
