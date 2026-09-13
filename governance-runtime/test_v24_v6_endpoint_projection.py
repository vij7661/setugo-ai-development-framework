from __future__ import annotations

import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_endpoint_projection import (
    compile_qualified_endpoint_table,
    derive_applicable_predicate_universe,
    validate_evaluator_condition_universe,
    qualify_predicate_coverage,
    project_governed_endpoint,
    construction_frontier,
)

D1="1"*64; D2="2"*64; D3="3"*64; D4="4"*64; D5="5"*64; D6="6"*64; D7="7"*64; D8="8"*64; D9="9"*64


def seal(r, field):
    x=dict(r); x.pop(field,None); r[field]=digest(x); return r


def currentness(source):
    r={"currentness_rule_id":"CUR","source_object_id":source,"source_version_or_sequence":"1","source_digest":D1,"observed_at_sequence":2,"verifier_qualification_digest":D2,"result":CURRENT,"binding_digest":""}
    return seal(r,"binding_digest")


def graph(subject):
    return {"nodes":[{"node_id":subject,"omission_sensitive":True},{"node_id":"ROOT","omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":D3}],"edges":[{"from":subject,"to":"ROOT"}]}


def completeness(subject, members):
    m=sorted(members)
    r={"subject_object_id":subject,"subject_content_digest":D1,"expected_members":m,"actual_members":m,"expected_member_set_digest":digest(m),"actual_member_set_digest":digest(m),"set_equality_proof_digest":D2,"completeness_derivation_graph":graph(subject),"derivation_mechanism_qualification_digests":[D3],"derivation_authority_independence_digests":[D4],"source_surface_digests":[D3],"currentness_bindings":[currentness(subject)],"verifier_qualification_digest":D5,"result":QUALIFIED,"qualification_digest":""}
    return seal(r,"qualification_digest")


def endpoint_bundle():
    descriptors=[
      {"predicate_id":"P1","phase":1,"within_phase_rank":1,"severity_rank":1,"endpoint":"EARLY_BLOCK","control_id":"C1"},
      {"predicate_id":"P2","phase":2,"within_phase_rank":1,"severity_rank":2,"endpoint":"LATE_BLOCK","control_id":"C2"},
      {"predicate_id":"P3","phase":3,"within_phase_rank":1,"severity_rank":3,"endpoint":"LAST_BLOCK","control_id":"C3"},
    ]
    from v24_endpoint_proof_compiler import compile_endpoint_precedence
    base={"normative_catalog_qualification_state":"QUALIFIED","predicate_descriptors":descriptors,"active_predicate_ids":["P1","P2","P3"]}
    c=compile_endpoint_precedence(base)
    q={"result":QUALIFIED,"subject_content_digest":c["compiled_table_digest"],"qualification_digest":D6,"currentness_result":CURRENT}
    return {**base,"expected_compiled_table_digest":c["compiled_table_digest"],"endpoint_table_qualification":q}


def applicability_bundle(rows, table_digest, applicable=("P1","P2")):
    rules=[{"predicate_id":"P1","applicability_rule_id":"A1","applies":"P1" in applicable},{"predicate_id":"P2","applicability_rule_id":"A2","applies":"P2" in applicable},{"predicate_id":"P3","applicability_rule_id":"A3","applies":"P3" in applicable}]
    return {"compiled_endpoint_rows":rows,"endpoint_table_digest":table_digest,"endpoint_table_qualification_state":QUALIFIED,"applicability_rules":rules,"applicability_registry_completeness":completeness("APP-R",["P1","P2","P3"]),"applicability_compiler_qualification_state":QUALIFIED,"applicability_compiler_qualification_digest":D6,"decision_context_digest":D7,"applicable_universe_completeness":completeness("APP-U",list(applicable))}


def evaluator_bundle(applicable=("P1","P2")):
    contracts=[{"predicate_id":pid,"evaluator_contract_id":f"E-{pid}","evaluator_mechanism_qualification_digest":D6,"true_condition_ids":[f"COND-{pid}"],"false_evidence_class_ids":[f"NEG-{pid}"]} for pid in applicable]
    conditions=[{"condition_id":f"COND-{pid}","predicate_id":pid,"condition_schema_digest":D7} for pid in applicable]
    return {"applicable_predicate_ids":list(applicable),"evaluator_contracts":contracts,"condition_descriptors":conditions,"evaluator_registry_completeness":completeness("EVAL-R",list(applicable)),"condition_registry_completeness":completeness("COND-R",[f"COND-{x}" for x in applicable])}


def evaluation(pid,status):
    ec=[f"NEG-{pid}"] if status=="FALSE" else [f"POS-{pid}"]
    conditions=[] if status=="FALSE" else [{"condition_id":f"COND-{pid}","predicate_id":pid,"condition_payload_digest":D8}]
    return {"predicate_id":pid,"evaluator_contract_id":f"E-{pid}","evaluator_mechanism_qualification_digest":D6,"status":status,"source_snapshot_digest":D7,"observation_ledger_head_digest":D8,"evidence_class_ids":ec,"evidence_record_digests":[D9],"condition_observation_binding_digest":D5,"conditions":conditions}


def coverage_bundle(app_universe_digest, table_digest, contracts, conditions, evals):
    return {"applicable_predicate_ids":["P1","P2"],"not_applicable_predicate_ids":["P3"],"evaluator_contracts":contracts,"condition_descriptors":conditions,"evaluation_records":evals,"decision_context_digest":D7,"applicable_predicate_universe_digest":app_universe_digest,"endpoint_table_digest":table_digest,"evaluator_contract_registry_digest":D1,"condition_registry_digest":D2,"evidence_class_registry_digest":D3,"source_snapshot_digest":D7,"observation_ledger_head_digest":D8,"coverage_verifier_qualification_digest":D4,"applicability_qualification_state":QUALIFIED,"evaluator_condition_universe_state":QUALIFIED,"coverage_verifier_qualification_state":QUALIFIED}


class R2EndpointProjectionTests(unittest.TestCase):
    def setUp(self):
        table=compile_qualified_endpoint_table(endpoint_bundle())
        self.assertTrue(table["qualified"],table["problems"]); self.table=table
        app=derive_applicable_predicate_universe(applicability_bundle(table["compiled_rows"],table["compiled_table_digest"]))
        self.assertTrue(app["qualified"],app["problems"]); self.app=app
        ev=evaluator_bundle(); ec=validate_evaluator_condition_universe(ev)
        self.assertTrue(ec["qualified"],ec["problems"]); self.ev=ev; self.ec=ec

    def test_construction_frontier_is_non_authoritative(self):
        r=construction_frontier(); self.assertFalse(r["qualified"]); self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_endpoint_table_is_qualified_only_for_exact_compiled_digest(self):
        b=endpoint_bundle(); b["endpoint_table_qualification"]["subject_content_digest"]=D1
        r=compile_qualified_endpoint_table(b); self.assertIn("ENDPOINT_TABLE_QUALIFICATION_DIGEST_MISMATCH",r["problems"])

    def test_applicability_requires_rule_for_every_endpoint_predicate(self):
        b=applicability_bundle(self.table["compiled_rows"],self.table["compiled_table_digest"]); b["applicability_rules"].pop()
        r=derive_applicable_predicate_universe(b); self.assertIn("APPLICABILITY_RULE_MISSING:P3",r["problems"])

    def test_applicable_universe_omission_fails_completeness(self):
        b=applicability_bundle(self.table["compiled_rows"],self.table["compiled_table_digest"]); b["applicable_universe_completeness"]=completeness("APP-U",["P1"])
        r=derive_applicable_predicate_universe(b); self.assertIn("APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH",r["problems"])

    def test_evaluator_contract_required_for_every_applicable_predicate(self):
        b=evaluator_bundle(); b["evaluator_contracts"].pop()
        r=validate_evaluator_condition_universe(b); self.assertIn("EVALUATOR_CONTRACT_MISSING:P2",r["problems"])

    def test_true_condition_schema_cannot_be_omitted(self):
        b=evaluator_bundle(); b["evaluator_contracts"][0]["true_condition_ids"]=[]
        r=validate_evaluator_condition_universe(b); self.assertIn("TRUE_CONDITION_SCHEMA_REQUIRED:P1",r["problems"])

    def good_coverage(self, evals=None):
        if evals is None: evals=[evaluation("P1","TRUE"),evaluation("P2","FALSE")]
        return qualify_predicate_coverage(coverage_bundle(self.app["universe_digest"],self.table["compiled_table_digest"],self.ev["evaluator_contracts"],self.ev["condition_descriptors"],evals))

    def test_complete_coverage_qualifies(self):
        r=self.good_coverage(); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["true_predicate_ids"],["P1"])

    def test_missing_predicate_evaluation_blocks(self):
        r=self.good_coverage([evaluation("P1","TRUE")]); self.assertIn("PREDICATE_EVALUATION_MISSING:P2",r["problems"])

    def test_true_without_condition_blocks(self):
        e=evaluation("P1","TRUE"); e["conditions"]=[]
        r=self.good_coverage([e,evaluation("P2","FALSE")]); self.assertIn("TRUE_CONDITION_REQUIRED:P1",r["problems"])

    def test_false_without_governed_negative_evidence_blocks(self):
        e=evaluation("P2","FALSE"); e["evidence_class_ids"]=["OTHER"]
        r=self.good_coverage([evaluation("P1","TRUE"),e]); self.assertIn("FALSE_GOVERNED_NEGATIVE_EVIDENCE_MISSING:P2",r["problems"])

    def test_producer_selected_not_applicable_blocks(self):
        e=evaluation("P2","FALSE"); e["status"]="NOT_APPLICABLE"
        r=self.good_coverage([evaluation("P1","TRUE"),e]); self.assertIn("PRODUCER_SELECTED_NOT_APPLICABLE_FORBIDDEN:P2",r["problems"])

    def projection_bundle(self,true_ids):
        coverage=self.good_coverage([evaluation("P1","TRUE" if "P1" in true_ids else "FALSE"),evaluation("P2","TRUE" if "P2" in true_ids else "FALSE")])
        self.assertTrue(coverage["qualified"],coverage["problems"])
        return {"coverage_qualification_state":QUALIFIED,"endpoint_table_qualification_state":QUALIFIED,"projector_mechanism_qualification_state":QUALIFIED,"decision_context_digest":D7,"coverage_qualification_digest":coverage["coverage_digest"],"endpoint_table_digest":self.table["compiled_table_digest"],"endpoint_table_qualification_digest":D6,"applicability_digest":self.app["universe_digest"],"evaluator_registry_digest":D1,"condition_registry_digest":D2,"evidence_registry_digest":D3,"source_snapshot_digest":D7,"observation_head_digest":D8,"projector_mechanism_qualification_digest":D4,"compiled_endpoint_rows":self.table["compiled_rows"],"true_predicate_ids":true_ids}

    def test_projector_selects_earliest_phase_not_caller_choice(self):
        r=project_governed_endpoint(self.projection_bundle(["P1","P2"])); self.assertTrue(r["qualified"],r["problems"]); self.assertEqual(r["selected_predicate_id"],"P1"); self.assertEqual(r["selected_endpoint"],"EARLY_BLOCK"); self.assertEqual(r["nonselected_true_predicate_ids"],["P2"])

    def test_projector_blocks_stale_table_digest(self):
        b=self.projection_bundle(["P1"]); b["endpoint_table_digest"]=D9
        r=project_governed_endpoint(b); self.assertIn("ENDPOINT_PROJECTION_TABLE_DIGEST_DRIFT",r["problems"])

    def test_projector_blocks_unknown_true_predicate(self):
        b=self.projection_bundle(["P1"]); b["true_predicate_ids"]=["P1","UNKNOWN"]
        r=project_governed_endpoint(b); self.assertIn("ENDPOINT_PROJECTION_TRUE_PREDICATE_UNMAPPED:UNKNOWN",r["problems"])

    def test_no_true_predicate_is_valid_no_selected_failure_endpoint(self):
        r=project_governed_endpoint(self.projection_bundle([])); self.assertTrue(r["qualified"],r["problems"]); self.assertIsNone(r["selected_endpoint"])


if __name__=="__main__": unittest.main()
