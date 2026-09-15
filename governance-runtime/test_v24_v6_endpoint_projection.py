from __future__ import annotations

import copy
import unittest

from v24_endpoint_proof_compiler import compile_endpoint_precedence
from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_endpoint_projection import (
    canonical_normative_catalog_digest,
    compile_qualified_endpoint_table,
    construction_frontier,
    derive_applicable_predicate_universe,
    project_governed_endpoint,
    qualify_predicate_coverage,
    validate_evaluator_condition_universe,
)
from v24_v6_test_proof_context import build_test_proof_context

D1="1"*64; D2="2"*64; D3="3"*64; D4="4"*64; D5="5"*64
D6="6"*64; D7="7"*64; D8="8"*64; D9="9"*64
CATALOG_ID="NORMATIVE-CATALOG-1"; TABLE_ID="ENDPOINT-TABLE-1"
APP_COMPILER_ID="APPLICABILITY-COMPILER-1"; APP_COMPILER_CONTENT="a"*64
COMP_VERIFIER_ID="COMPLETENESS-VERIFIER-1"; COMP_VERIFIER_CONTENT="b"*64
COMP_AUTHORITY_ID="COMPLETENESS-AUTHORITY-1"
APP_UNIVERSE_ID="APPLICABILITY-UNIVERSE-1"; EVAL_UNIVERSE_ID="EVALUATOR-UNIVERSE-1"
COVERAGE_VERIFIER_ID="COVERAGE-VERIFIER-1"; COVERAGE_VERIFIER_CONTENT="c"*64
COVERAGE_ID="PREDICATE-COVERAGE-1"
PROJECTOR_ID="ENDPOINT-PROJECTOR-1"; PROJECTOR_CONTENT="d"*64
EVAL_CONTENT={"P1":"e"*64,"P2":"f"*64,"P3":"0"*64}


def seal(record, field):
    material=dict(record);material.pop(field,None);record[field]=digest(material);return record


def currentness(source, verifier_ref):
    return seal({
        "currentness_rule_id":"CUR",
        "source_object_id":source,
        "source_version_or_sequence":"1",
        "source_digest":D1,
        "observed_at_sequence":2,
        "verifier_qualification_digest":verifier_ref,
        "result":CURRENT,
        "binding_digest":"",
    },"binding_digest")


def graph(subject):
    return {
        "nodes":[
            {"node_id":subject,"omission_sensitive":True},
            {"node_id":"ROOT","omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":D3},
        ],
        "edges":[{"from":subject,"to":"ROOT"}],
    }


def completeness(subject,members,q_ref,i_ref):
    m=sorted(members)
    return seal({
        "subject_object_id":subject,
        "subject_content_digest":D1,
        "expected_members":m,
        "actual_members":m,
        "expected_member_set_digest":digest(m),
        "actual_member_set_digest":digest(m),
        "set_equality_proof_digest":D2,
        "completeness_derivation_graph":graph(subject),
        "derivation_mechanism_qualification_digests":[q_ref],
        "derivation_authority_independence_digests":[i_ref],
        "source_surface_digests":[D3],
        "currentness_bindings":[currentness(subject,q_ref)],
        "verifier_qualification_digest":q_ref,
        "result":QUALIFIED,
        "qualification_digest":"",
    },"qualification_digest")


def descriptors():
    return [
        {"predicate_id":"P1","phase":1,"within_phase_rank":1,"severity_rank":1,"endpoint":"EARLY_BLOCK","control_id":"C1"},
        {"predicate_id":"P2","phase":2,"within_phase_rank":1,"severity_rank":2,"endpoint":"LATE_BLOCK","control_id":"C2"},
        {"predicate_id":"P3","phase":3,"within_phase_rank":1,"severity_rank":3,"endpoint":"LAST_BLOCK","control_id":"C3"},
    ]


def base_catalog():
    return {
        "normative_catalog_qualification_state":QUALIFIED,
        "predicate_descriptors":descriptors(),
        "active_predicate_ids":["P1","P2","P3"],
    }


def endpoint_bundle():
    """Legacy opaque-label fixture retained by the permanent R2 RED regression."""
    base=base_catalog();compiled=compile_endpoint_precedence(base)
    q={
        "result":QUALIFIED,
        "subject_content_digest":compiled["compiled_table_digest"],
        "qualification_digest":D6,
        "currentness_result":CURRENT,
    }
    return {**base,"expected_compiled_table_digest":compiled["compiled_table_digest"],"endpoint_table_qualification":q}


def _rules(applicable):
    selected=set(applicable)
    return [
        {"predicate_id":"P1","applicability_rule_id":"A1","applies":"P1" in selected},
        {"predicate_id":"P2","applicability_rule_id":"A2","applies":"P2" in selected},
        {"predicate_id":"P3","applicability_rule_id":"A3","applies":"P3" in selected},
    ]


def _contracts(applicable,refs):
    out=[]
    for pid in applicable:
        out.append({
            "predicate_id":pid,
            "evaluator_contract_id":f"E-{pid}",
            "evaluator_mechanism_id":f"EVAL-MECH-{pid}",
            "evaluator_mechanism_content_digest":EVAL_CONTENT[pid],
            "evaluator_mechanism_qualification_digest":refs[f"eval_{pid.lower()}_q"],
            "true_condition_ids":[f"COND-{pid}"],
            "false_evidence_class_ids":[f"NEG-{pid}"],
        })
    return out


def _conditions(applicable):
    return [
        {"condition_id":f"COND-{pid}","predicate_id":pid,"condition_schema_digest":D7}
        for pid in applicable
    ]


def _evaluation(pid,status,contracts):
    contract=next(x for x in contracts if x["predicate_id"]==pid)
    evidence=[f"NEG-{pid}"] if status=="FALSE" else [f"POS-{pid}"]
    conditions=[] if status!="TRUE" else [{"condition_id":f"COND-{pid}","predicate_id":pid,"condition_payload_digest":D8}]
    return {
        "predicate_id":pid,
        "evaluator_contract_id":contract["evaluator_contract_id"],
        "evaluator_mechanism_qualification_digest":contract["evaluator_mechanism_qualification_digest"],
        "status":status,
        "source_snapshot_digest":D7,
        "observation_ledger_head_digest":D8,
        "evidence_class_ids":evidence,
        "evidence_record_digests":[D9],
        "condition_observation_binding_digest":D5,
        "conditions":conditions,
    }


def build_chain(statuses=None,applicable=("P1","P2")):
    statuses=statuses or {"P1":"TRUE","P2":"FALSE"}
    applicable=tuple(applicable)
    base=base_catalog();raw=compile_endpoint_precedence(base);table_digest=raw["compiled_table_digest"]
    catalog_digest=canonical_normative_catalog_digest(base)

    primitive={
        "catalog_q":{"kind":"QUALIFICATION","subject_id":CATALOG_ID,"content_digest":catalog_digest},
        "table_q":{"kind":"QUALIFICATION","subject_id":TABLE_ID,"content_digest":table_digest},
        "app_compiler_q":{"kind":"QUALIFICATION","subject_id":APP_COMPILER_ID,"content_digest":APP_COMPILER_CONTENT},
        "completeness_q":{"kind":"QUALIFICATION","subject_id":COMP_VERIFIER_ID,"content_digest":COMP_VERIFIER_CONTENT},
        "completeness_i":{"kind":"INDEPENDENCE","subject_identity_id":COMP_AUTHORITY_ID},
        "eval_p1_q":{"kind":"QUALIFICATION","subject_id":"EVAL-MECH-P1","content_digest":EVAL_CONTENT["P1"]},
        "eval_p2_q":{"kind":"QUALIFICATION","subject_id":"EVAL-MECH-P2","content_digest":EVAL_CONTENT["P2"]},
        "eval_p3_q":{"kind":"QUALIFICATION","subject_id":"EVAL-MECH-P3","content_digest":EVAL_CONTENT["P3"]},
        "coverage_verifier_q":{"kind":"QUALIFICATION","subject_id":COVERAGE_VERIFIER_ID,"content_digest":COVERAGE_VERIFIER_CONTENT},
        "projector_q":{"kind":"QUALIFICATION","subject_id":PROJECTOR_ID,"content_digest":PROJECTOR_CONTENT},
    }
    _,_,refs1=build_test_proof_context(primitive)

    app_material={
        "decision_context_digest":D7,
        "endpoint_table_id":TABLE_ID,
        "endpoint_table_digest":table_digest,
        "endpoint_table_qualification_digest":refs1["table_q"],
        "applicability_compiler_id":APP_COMPILER_ID,
        "applicability_compiler_content_digest":APP_COMPILER_CONTENT,
        "applicability_compiler_qualification_digest":refs1["app_compiler_q"],
        "applicable_predicate_ids":sorted(applicable),
        "not_applicable_predicate_ids":sorted(set(("P1","P2","P3"))-set(applicable)),
    }
    app_digest=digest(app_material)
    specs2=dict(primitive);specs2["app_result_q"]={"kind":"QUALIFICATION","subject_id":APP_UNIVERSE_ID,"content_digest":app_digest}
    _,_,refs2=build_test_proof_context(specs2)

    contracts=_contracts(applicable,refs2);conditions=_conditions(applicable)
    eval_material={
        "applicability_universe_digest":app_digest,
        "applicable_predicate_ids":sorted(applicable),
        "evaluator_contract_digest":digest(contracts),
        "condition_registry_digest":digest(conditions),
    }
    eval_digest=digest(eval_material)
    specs3=dict(specs2);specs3["eval_result_q"]={"kind":"QUALIFICATION","subject_id":EVAL_UNIVERSE_ID,"content_digest":eval_digest}
    _,_,refs3=build_test_proof_context(specs3)
    contracts=_contracts(applicable,refs3)

    evals=[_evaluation(pid,statuses[pid],contracts) for pid in applicable]
    true_ids=sorted(pid for pid,status in statuses.items() if pid in applicable and status=="TRUE")
    false_ids=sorted(pid for pid,status in statuses.items() if pid in applicable and status=="FALSE")
    coverage_material={
        "decision_context_digest":D7,
        "applicable_predicate_universe_digest":app_digest,
        "evaluator_condition_universe_digest":eval_digest,
        "endpoint_table_digest":table_digest,
        "evaluator_contract_registry_digest":digest(contracts),
        "condition_registry_digest":digest(conditions),
        "evidence_class_registry_digest":D3,
        "source_snapshot_digest":D7,
        "observation_ledger_head_digest":D8,
        "evaluation_record_digests":sorted(digest(r) for r in evals),
        "true_predicate_ids":true_ids,
        "false_predicate_ids":false_ids,
        "not_applicable_predicate_ids":sorted(set(("P1","P2","P3"))-set(applicable)),
    }
    coverage_digest=digest(coverage_material)
    specs4=dict(specs3);specs4["coverage_result_q"]={"kind":"QUALIFICATION","subject_id":COVERAGE_ID,"content_digest":coverage_digest}
    context,boundary,refs=build_test_proof_context(specs4)
    contracts=_contracts(applicable,refs);conditions=_conditions(applicable)
    evals=[_evaluation(pid,statuses[pid],contracts) for pid in applicable]

    endpoint={
        **base,
        "expected_compiled_table_digest":table_digest,
        "normative_catalog_id":CATALOG_ID,
        "normative_catalog_qualification_digest":refs["catalog_q"],
        "endpoint_table_id":TABLE_ID,
        "endpoint_table_qualification_digest":refs["table_q"],
    }
    app={
        "compiled_endpoint_rows":raw["compiled_rows"],
        "endpoint_table_id":TABLE_ID,
        "endpoint_table_digest":table_digest,
        "endpoint_table_qualification_digest":refs["table_q"],
        "endpoint_table_qualification_state":QUALIFIED,
        "applicability_rules":_rules(applicable),
        "applicability_registry_completeness":completeness("APP-R",["P1","P2","P3"],refs["completeness_q"],refs["completeness_i"]),
        "applicability_compiler_id":APP_COMPILER_ID,
        "applicability_compiler_content_digest":APP_COMPILER_CONTENT,
        "applicability_compiler_qualification_digest":refs["app_compiler_q"],
        "applicability_compiler_qualification_state":QUALIFIED,
        "decision_context_digest":D7,
        "applicable_universe_completeness":completeness("APP-U",list(applicable),refs["completeness_q"],refs["completeness_i"]),
    }
    evaluator={
        "applicable_predicate_ids":list(applicable),
        "applicability_universe_id":APP_UNIVERSE_ID,
        "applicability_universe_digest":app_digest,
        "applicability_qualification_digest":refs["app_result_q"],
        "applicability_binding_material":app_material,
        "evaluator_contracts":contracts,
        "condition_descriptors":conditions,
        "evaluator_registry_completeness":completeness("EVAL-R",list(applicable),refs["completeness_q"],refs["completeness_i"]),
        "condition_registry_completeness":completeness("COND-R",[f"COND-{x}" for x in applicable],refs["completeness_q"],refs["completeness_i"]),
    }
    coverage={
        "applicable_predicate_ids":list(applicable),
        "not_applicable_predicate_ids":sorted(set(("P1","P2","P3"))-set(applicable)),
        "applicability_universe_id":APP_UNIVERSE_ID,
        "applicable_predicate_universe_digest":app_digest,
        "applicability_qualification_digest":refs["app_result_q"],
        "applicability_binding_material":app_material,
        "evaluator_condition_universe_id":EVAL_UNIVERSE_ID,
        "evaluator_condition_universe_digest":eval_digest,
        "evaluator_condition_universe_qualification_digest":refs["eval_result_q"],
        "evaluator_condition_binding_material":eval_material,
        "endpoint_table_id":TABLE_ID,
        "endpoint_table_digest":table_digest,
        "endpoint_table_qualification_digest":refs["table_q"],
        "evaluator_contracts":contracts,
        "condition_descriptors":conditions,
        "evaluation_records":evals,
        "decision_context_digest":D7,
        "evaluator_contract_registry_digest":digest(contracts),
        "condition_registry_digest":digest(conditions),
        "evidence_class_registry_digest":D3,
        "source_snapshot_digest":D7,
        "observation_ledger_head_digest":D8,
        "coverage_verifier_id":COVERAGE_VERIFIER_ID,
        "coverage_verifier_content_digest":COVERAGE_VERIFIER_CONTENT,
        "coverage_verifier_qualification_digest":refs["coverage_verifier_q"],
        "applicability_qualification_state":QUALIFIED,
        "evaluator_condition_universe_state":QUALIFIED,
        "coverage_verifier_qualification_state":QUALIFIED,
    }
    projection={
        "coverage_id":COVERAGE_ID,
        "coverage_content_digest":coverage_digest,
        "coverage_qualification_digest":refs["coverage_result_q"],
        "coverage_binding_material":coverage_material,
        "coverage_qualification_state":QUALIFIED,
        "endpoint_table_id":TABLE_ID,
        "endpoint_table_digest":table_digest,
        "endpoint_table_qualification_digest":refs["table_q"],
        "endpoint_table_qualification_state":QUALIFIED,
        "projector_mechanism_id":PROJECTOR_ID,
        "projector_mechanism_content_digest":PROJECTOR_CONTENT,
        "projector_mechanism_qualification_digest":refs["projector_q"],
        "projector_mechanism_qualification_state":QUALIFIED,
        "decision_context_digest":D7,
        "applicability_digest":app_digest,
        "evaluator_registry_digest":digest(contracts),
        "condition_registry_digest":digest(conditions),
        "evidence_registry_digest":D3,
        "source_snapshot_digest":D7,
        "observation_head_digest":D8,
        "compiled_endpoint_rows":raw["compiled_rows"],
        "true_predicate_ids":true_ids,
    }
    return {
        "context":context,"boundary":boundary,"refs":refs,
        "endpoint":endpoint,"app":app,"evaluator":evaluator,"coverage":coverage,"projection":projection,
        "expected_app_digest":app_digest,"expected_eval_digest":eval_digest,"expected_coverage_digest":coverage_digest,
    }


class R2EndpointProjectionTests(unittest.TestCase):
    def setUp(self):
        self.chain=build_chain()
        c=self.chain["context"];t=self.chain["boundary"]
        self.table=compile_qualified_endpoint_table(self.chain["endpoint"],proof_context=c,trusted_boundary=t)
        self.assertTrue(self.table["qualified"],self.table["problems"])
        self.app=derive_applicable_predicate_universe(self.chain["app"],proof_context=c,trusted_boundary=t)
        self.assertTrue(self.app["qualified"],self.app["problems"])
        self.ec=validate_evaluator_condition_universe(self.chain["evaluator"],proof_context=c,trusted_boundary=t)
        self.assertTrue(self.ec["qualified"],self.ec["problems"])

    def test_construction_frontier_is_non_authoritative(self):
        r=construction_frontier();self.assertFalse(r["qualified"]);self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_endpoint_table_requires_exact_qualified_compiled_digest(self):
        ch=build_chain();b=copy.deepcopy(ch["endpoint"]);b["predicate_descriptors"][0]["endpoint"]="CHANGED"
        r=compile_qualified_endpoint_table(b,proof_context=ch["context"],trusted_boundary=ch["boundary"])
        self.assertFalse(r["qualified"]);self.assertIn("ENDPOINT_TABLE_DIGEST_MISMATCH",r["problems"]);self.assertIn("ENDPOINT_TABLE_QUALIFICATION_PROOF_INVALID",r["problems"])

    def test_applicability_rejects_table_row_substitution(self):
        b=copy.deepcopy(self.chain["app"]);b["compiled_endpoint_rows"][0]["endpoint"]="SUBSTITUTED"
        r=derive_applicable_predicate_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("APPLICABILITY_ENDPOINT_TABLE_DIGEST_DRIFT",r["problems"])

    def test_applicability_requires_rule_for_every_endpoint_predicate(self):
        b=copy.deepcopy(self.chain["app"]);b["applicability_rules"].pop()
        r=derive_applicable_predicate_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("APPLICABILITY_RULE_MISSING:P3",r["problems"])

    def test_applicable_universe_omission_fails_completeness(self):
        b=copy.deepcopy(self.chain["app"]);q=b["applicable_universe_completeness"];q["actual_members"]=["P1"];q["actual_member_set_digest"]=digest(["P1"]);seal(q,"qualification_digest")
        r=derive_applicable_predicate_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH",r["problems"])

    def test_evaluator_rejects_applicability_binding_substitution(self):
        b=copy.deepcopy(self.chain["evaluator"]);b["applicable_predicate_ids"]=["P1"]
        r=validate_evaluator_condition_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("EVALUATOR_APPLICABILITY_MEMBER_SET_MISMATCH",r["problems"])

    def test_evaluator_contract_required_for_every_applicable_predicate(self):
        b=copy.deepcopy(self.chain["evaluator"]);b["evaluator_contracts"].pop()
        r=validate_evaluator_condition_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("EVALUATOR_CONTRACT_MISSING:P2",r["problems"])

    def test_true_condition_schema_cannot_be_omitted(self):
        b=copy.deepcopy(self.chain["evaluator"]);b["evaluator_contracts"][0]["true_condition_ids"]=[]
        r=validate_evaluator_condition_universe(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("TRUE_CONDITION_SCHEMA_REQUIRED:P1",r["problems"])

    def good_coverage(self,chain=None):
        ch=chain or self.chain
        return qualify_predicate_coverage(ch["coverage"],proof_context=ch["context"],trusted_boundary=ch["boundary"])

    def test_complete_coverage_qualifies(self):
        r=self.good_coverage();self.assertTrue(r["qualified"],r["problems"]);self.assertEqual(r["true_predicate_ids"],["P1"]);self.assertEqual(r["coverage_digest"],self.chain["expected_coverage_digest"])

    def test_coverage_rejects_upstream_binding_material_tamper(self):
        b=copy.deepcopy(self.chain["coverage"]);b["applicability_binding_material"]["decision_context_digest"]=D9
        r=qualify_predicate_coverage(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("COVERAGE_APPLICABILITY_BINDING_MATERIAL_DIGEST_MISMATCH",r["problems"])

    def test_missing_predicate_evaluation_blocks(self):
        b=copy.deepcopy(self.chain["coverage"]);b["evaluation_records"].pop()
        r=qualify_predicate_coverage(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("PREDICATE_EVALUATION_MISSING:P2",r["problems"])

    def test_true_without_condition_blocks(self):
        b=copy.deepcopy(self.chain["coverage"]);b["evaluation_records"][0]["conditions"]=[]
        r=qualify_predicate_coverage(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("TRUE_CONDITION_REQUIRED:P1",r["problems"])

    def test_false_without_governed_negative_evidence_blocks(self):
        b=copy.deepcopy(self.chain["coverage"]);b["evaluation_records"][1]["evidence_class_ids"]=["OTHER"]
        r=qualify_predicate_coverage(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("FALSE_GOVERNED_NEGATIVE_EVIDENCE_MISSING:P2",r["problems"])

    def test_producer_selected_not_applicable_blocks(self):
        b=copy.deepcopy(self.chain["coverage"]);b["evaluation_records"][1]["status"]="NOT_APPLICABLE"
        r=qualify_predicate_coverage(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("PRODUCER_SELECTED_NOT_APPLICABLE_FORBIDDEN:P2",r["problems"])

    def test_projector_selects_earliest_phase_not_caller_choice(self):
        ch=build_chain({"P1":"TRUE","P2":"TRUE"});r=project_governed_endpoint(ch["projection"],proof_context=ch["context"],trusted_boundary=ch["boundary"])
        self.assertTrue(r["qualified"],r["problems"]);self.assertEqual(r["selected_predicate_id"],"P1");self.assertEqual(r["selected_endpoint"],"EARLY_BLOCK");self.assertEqual(r["nonselected_true_predicate_ids"],["P2"])

    def test_projector_blocks_caller_true_set_override(self):
        b=copy.deepcopy(self.chain["projection"]);b["true_predicate_ids"]=[]
        r=project_governed_endpoint(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("ENDPOINT_PROJECTION_CALLER_TRUE_SET_MISMATCH",r["problems"]);self.assertFalse(r["qualified"])

    def test_projector_blocks_stale_table_digest(self):
        b=copy.deepcopy(self.chain["projection"]);b["endpoint_table_digest"]=D9
        r=project_governed_endpoint(b,proof_context=self.chain["context"],trusted_boundary=self.chain["boundary"])
        self.assertIn("ENDPOINT_PROJECTION_TABLE_DIGEST_DRIFT",r["problems"])

    def test_projector_blocks_unknown_true_predicate_even_when_coverage_is_qualified(self):
        b=copy.deepcopy(self.chain["projection"]);material=dict(b["coverage_binding_material"]);material["true_predicate_ids"]=["P1","UNKNOWN"];new_digest=digest(material)
        context,boundary,refs=build_test_proof_context({
            "coverage_q":{"kind":"QUALIFICATION","subject_id":COVERAGE_ID,"content_digest":new_digest},
            "table_q":{"kind":"QUALIFICATION","subject_id":TABLE_ID,"content_digest":b["endpoint_table_digest"]},
            "projector_q":{"kind":"QUALIFICATION","subject_id":PROJECTOR_ID,"content_digest":PROJECTOR_CONTENT},
        })
        b["coverage_binding_material"]=material;b["coverage_content_digest"]=new_digest;b["coverage_qualification_digest"]=refs["coverage_q"];b["endpoint_table_qualification_digest"]=refs["table_q"];b["projector_mechanism_qualification_digest"]=refs["projector_q"];b["true_predicate_ids"]=["P1","UNKNOWN"]
        r=project_governed_endpoint(b,proof_context=context,trusted_boundary=boundary)
        self.assertIn("ENDPOINT_PROJECTION_TRUE_PREDICATE_UNMAPPED:UNKNOWN",r["problems"])

    def test_no_true_predicate_is_valid_no_selected_failure_endpoint(self):
        ch=build_chain({"P1":"FALSE","P2":"FALSE"});r=project_governed_endpoint(ch["projection"],proof_context=ch["context"],trusted_boundary=ch["boundary"])
        self.assertTrue(r["qualified"],r["problems"]);self.assertIsNone(r["selected_endpoint"])


if __name__=="__main__":unittest.main()
