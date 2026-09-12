from __future__ import annotations
import unittest
from v24_endpoint_proof_compiler import compile_endpoint_precedence, compile_proof_view

def endpoint_bundle():
    return {
      "normative_catalog_qualification_state":"QUALIFIED",
      "active_predicate_ids":["P-ROOT","P-SINK","P-EVID"],
      "predicate_descriptors":[
        {"predicate_id":"P-ROOT","control_id":"C1","phase":1,"within_phase_rank":1,"severity_rank":1,"endpoint":"ROOT_FAIL"},
        {"predicate_id":"P-SINK","control_id":"C2","phase":2,"within_phase_rank":1,"severity_rank":2,"endpoint":"SINK_FAIL"},
        {"predicate_id":"P-EVID","control_id":"C3","phase":2,"within_phase_rank":2,"severity_rank":3,"endpoint":"INSUFFICIENT_EVIDENCE"}
      ]}

def proof_bundle():
    return {
      "normative_catalog_qualification_state":"QUALIFIED",
      "endpoint_precedence_state":"ENDPOINT_PRECEDENCE_CORRECTNESS_QUALIFIED",
      "exact_decision_path_predicate_ids":["P-ROOT"],
      "admitted_applicability_predicate_ids":["P-EVID"],
      "producer_requested_field_ids":["F-ROOT","F-EVID"],
      "kernel_bound_redaction_classes":["VISIBLE","SECRET_SAFE_IDENTITY_ONLY"],
      "proof_field_descriptors":[
        {"field_id":"F-ROOT","predicate_id":"P-ROOT","control_id":"C1","source_binding":"SRC-ROOT","redaction_class":"VISIBLE","qualification_or_failure_field":True},
        {"field_id":"F-EVID","predicate_id":"P-EVID","control_id":"C3","source_binding":"SRC-EVID","redaction_class":"SECRET_SAFE_IDENTITY_ONLY","qualification_or_failure_field":True}
      ]}
    }

class EndpointProofTests(unittest.TestCase):
    def test_endpoint_positive_construction(self):
        r=compile_endpoint_precedence(endpoint_bundle()); self.assertEqual(r["state"],"ENDPOINT_PRECEDENCE_COMPILED"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])
    def test_real_unqualified_catalog_must_block(self):
        b=endpoint_bundle(); b["normative_catalog_qualification_state"]="CONSTRUCTION_COMPLETE_QUALIFICATION_PENDING"
        self.assertIn("NORMATIVE_CONTROL_CATALOG_INCOMPLETE",compile_endpoint_precedence(b)["problems"])
    def test_duplicate_primary_mapping_blocks(self):
        b=endpoint_bundle(); b["predicate_descriptors"].append(dict(b["predicate_descriptors"][0]))
        self.assertIn("PREDICATE_PRIMARY_MAPPING_DUPLICATE:P-ROOT",compile_endpoint_precedence(b)["problems"])
    def test_within_phase_total_order_required(self):
        b=endpoint_bundle(); b["predicate_descriptors"][2]["within_phase_rank"]=3
        self.assertIn("WITHIN_PHASE_ORDER_NOT_TOTAL:2",compile_endpoint_precedence(b)["problems"])
    def test_unmapped_active_predicate_blocks(self):
        b=endpoint_bundle(); b["active_predicate_ids"].append("P-MISSING")
        self.assertIn("ACTIVE_PREDICATE_UNMAPPED:P-MISSING",compile_endpoint_precedence(b)["problems"])
    def test_weaker_subsystem_override_blocks(self):
        b=endpoint_bundle(); b["active_predicate_ids"].append("P-SUB"); b["predicate_descriptors"].append({"predicate_id":"P-SUB","control_id":"C4","phase":2,"within_phase_rank":3,"severity_rank":4,"endpoint":"SUB","overrides_predicate_id":"P-SINK"})
        self.assertIn("OVERRIDE_WEAKER_THAN_GENERIC:P-SUB:P-SINK",compile_endpoint_precedence(b)["problems"])
    def test_proof_positive_construction(self):
        r=compile_proof_view(proof_bundle()); self.assertEqual(r["state"],"PROOF_VIEW_APPLICABILITY_COMPILED"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])
    def test_producer_cannot_omit_mandatory_field(self):
        b=proof_bundle(); b["producer_requested_field_ids"]=["F-ROOT"]
        self.assertIn("PRODUCER_SELECTION_ATTEMPTS_TO_OMIT_MANDATORY_FIELD",compile_proof_view(b)["problems"])
    def test_applicable_predicate_requires_field(self):
        b=proof_bundle(); b["proof_field_descriptors"].pop()
        self.assertIn("APPLICABLE_PREDICATE_PROOF_FIELD_MISSING:P-EVID",compile_proof_view(b)["problems"])
    def test_unadmitted_redaction_blocks(self):
        b=proof_bundle(); b["proof_field_descriptors"][0]["redaction_class"]="LOCAL_HIDE"
        self.assertIn("PROOF_REDACTION_CLASS_UNADMITTED:F-ROOT:LOCAL_HIDE",compile_proof_view(b)["problems"])
    def test_proof_compile_requires_qualified_endpoint_correctness(self):
        b=proof_bundle(); b["endpoint_precedence_state"]="ENDPOINT_PRECEDENCE_COMPILED"
        self.assertIn("ENDPOINT_PRECEDENCE_CORRECTNESS_NOT_QUALIFIED",compile_proof_view(b)["problems"])

if __name__=="__main__": unittest.main()
