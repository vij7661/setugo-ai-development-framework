import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice16-rcs-evidence-local-2026-09-25"
INT64_MAX=9223372036854775807
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_rcs_evidence_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def suite():
    return {
      "suite_id":"suite:1","suite_version":"suite-v1","vector_manifest_digest":"vector-manifest:1",
      "vector_generator_implementation_digest":"vector-generator:1","generator_runtime_manifest_digest":"generator-runtime:1",
      "input_corpus_digest":"input-corpus:1","expected_result_manifest_digest":"expected-results:1",
      "execution_harness_digest":"harness:1","required_resolver_runtime_identity_digest":"resolver-runtime-id:1",
      "required_resolver_workload_identity_digest":"resolver-workload-id:1","result_schema_digest":"result-schema:1",
      "suite_digest":"suite-digest:1"
    }

def vector(i=1,result="PASS"):
    return {
      "vector_id":f"vector:{i}","input_digest":f"input:{i}","output_digest":f"output:{i}",
      "result":result,"result_digest":f"result:{i}"
    }

def aggregate(status="PASS",vector_count=1,passed_vector_count=1):
    return {"status":status,"vector_count":vector_count,"passed_vector_count":passed_vector_count,"aggregate_digest":"aggregate:1"}

def valid(status="PASS"):
    return {
      "rir_record_digest":"rir-record:digest","rir_record_id":"rir:1","resolver_policy_digest":"policy:digest",
      "implementation_id":"impl:1","resolver_implementation_digest":"impl:digest",
      "resolver_runtime_manifest_digest":"runtime:manifest","runtime_identity_digest":"runtime:identity",
      "workload_identity_digest":"workload:identity","conformance_suite_digest":"suite:digest",
      "rcs_suite":suite(),"rcs_suite_digest":"suite:digest","rcs_vector_digests":["vector:digest:1"],
      "raw_per_vector_results":[vector()],"deterministic_aggregate_result":aggregate(),
      "registry_head_digest":"registry:head","freshness_profile_id":"freshness:1","status":status,
      "evidence_digest":"evidence:digest"
    }

class Slice16FrozenAcceptance(unittest.TestCase):
    def test_i16_01_top_level_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverConformanceEvidence"]["required"]
        self.assertEqual(set(req),set(m.RCS_EVIDENCE_FIELDS)); self.assertEqual(len(req),len(m.RCS_EVIDENCE_FIELDS))
    def test_i16_02_valid_pass(self):
        self.assertTrue(require().validate_rcs_evidence(valid("PASS"))["locally_valid"])
    def test_i16_03_all_statuses_structurally_accept(self):
        m=require()
        for status in ("PASS","FAIL","EXPIRED","UNAVAILABLE"):
            with self.subTest(status=status):
                self.assertTrue(m.validate_rcs_evidence(valid(status))["locally_valid"])
    def test_i16_04_missing_extra_top_level_reject(self):
        m=require(); x=valid(); x.pop("evidence_digest")
        with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
        self.assertEqual(cm.exception.code,"RCS_EVIDENCE_FIELD_SET_INVALID")
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_FIELD_SET_INVALID")
    def test_i16_05_scalar_nonempty_string_rules(self):
        m=require()
        for field,bad in (("rir_record_id",1),("resolver_policy_digest","")):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
                self.assertEqual(cm.exception.code,"RCS_EVIDENCE_STRING_INVALID")
    def test_i16_06_scalar_gcp_rules(self):
        m=require()
        for field,bad in (("implementation_id","e\u0301"),("evidence_digest","\ufdd0")):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
                self.assertEqual(cm.exception.code,"RCS_EVIDENCE_GCP_STRING_INVALID")
    def test_i16_07_rcs_suite_exact_shape_and_strings(self):
        m=require(); x=valid(); x["rcs_suite"].pop("suite_digest")
        with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
        self.assertEqual(cm.exception.code,"RCS_EVIDENCE_SUITE_FIELD_SET_INVALID")
        x=valid(); x["rcs_suite"]["suite_version"]=""
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_STRING_INVALID")
    def test_i16_08_vector_digest_list_rules(self):
        m=require()
        for bad in ([],("d:1",),"d:1",None):
            x=valid(); x["rcs_vector_digests"]=bad
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
                self.assertEqual(cm.exception.code,"RCS_EVIDENCE_VECTOR_DIGESTS_INVALID")
        x=valid(); x["rcs_vector_digests"]=[""]
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_STRING_INVALID")
    def test_i16_09_raw_vector_result_list_and_shape(self):
        m=require()
        for bad in ([],(vector(),),vector(),None):
            x=valid(); x["raw_per_vector_results"]=bad
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
                self.assertEqual(cm.exception.code,"RCS_EVIDENCE_VECTOR_RESULTS_INVALID")
        x=valid(); x["raw_per_vector_results"][0].pop("result_digest")
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_VECTOR_FIELD_SET_INVALID")
    def test_i16_10_nested_vector_result_rules(self):
        m=require(); x=valid(); x["raw_per_vector_results"][0]["result"]="UNKNOWN"
        with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
        self.assertEqual(cm.exception.code,"RCS_EVIDENCE_VECTOR_RESULT_INVALID")
        x=valid(); x["raw_per_vector_results"][0]["output_digest"]="e\u0301"
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_GCP_STRING_INVALID")
    def test_i16_11_nested_aggregate_rules(self):
        m=require(); x=valid(); x["deterministic_aggregate_result"].pop("aggregate_digest")
        with self.assertRaises(m.RCSEvidenceError) as cm:m.validate_rcs_evidence(x)
        self.assertEqual(cm.exception.code,"RCS_EVIDENCE_AGGREGATE_FIELD_SET_INVALID")
        x=valid(); x["deterministic_aggregate_result"]["status"]="UNKNOWN"
        with self.assertRaises(m.RCSEvidenceError) as cm2:m.validate_rcs_evidence(x)
        self.assertEqual(cm2.exception.code,"RCS_EVIDENCE_AGGREGATE_STATUS_INVALID")
        for field,bad,code in (("vector_count",0,"RCS_EVIDENCE_AGGREGATE_VECTOR_COUNT_INVALID"),("passed_vector_count",-1,"RCS_EVIDENCE_AGGREGATE_PASSED_COUNT_INVALID")):
            x=valid(); x["deterministic_aggregate_result"][field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RCSEvidenceError) as cm3:m.validate_rcs_evidence(x)
                self.assertEqual(cm3.exception.code,code)
    def test_i16_12_opaque_non_sha_digests_pass(self):
        m=require(); x=valid()
        x["resolver_policy_digest"]="not-a-sha"; x["rcs_suite"]["suite_digest"]="opaque"; x["rcs_vector_digests"]=["opaque:d"]
        x["raw_per_vector_results"][0]["result_digest"]="opaque:r"; x["deterministic_aggregate_result"]["aggregate_digest"]="opaque:a"
        self.assertTrue(m.validate_rcs_evidence(x)["locally_valid"])
    def test_i16_13_binding_invariants_remain_unproven(self):
        m=require(); x=valid()
        x["conformance_suite_digest"]="top:one"; x["rcs_suite_digest"]="top:two"; x["rcs_suite"]["suite_digest"]="nested:three"
        x["runtime_identity_digest"]="runtime:top"; x["rcs_suite"]["required_resolver_runtime_identity_digest"]="runtime:nested"
        x["workload_identity_digest"]="workload:top"; x["rcs_suite"]["required_resolver_workload_identity_digest"]="workload:nested"
        r=m.validate_rcs_evidence(x); self.assertTrue(r["locally_valid"])
        for k in ("suite_digest_binding_verified","resolver_identity_binding_verified","workload_identity_binding_verified"):
            self.assertFalse(r[k],k)
    def test_i16_14_semantic_and_authority_claims_remain_false(self):
        m=require(); x=valid()
        x["rcs_vector_digests"]=["d:1"]; x["raw_per_vector_results"]=[vector(1),vector(2,"FAIL")]
        x["deterministic_aggregate_result"]=aggregate("FAIL",9,7); x["status"]="PASS"
        r=m.validate_rcs_evidence(x); self.assertTrue(r["locally_valid"])
        for k in ("vector_manifest_binding_verified","array_count_relation_verified","current_pass_exact_tuple_verified","freshness_verified","cached_pass_substitution_prevented","evidence_digest_verified","resolver_qualified","resolver_authorized","runtime_qualified","evidence_promotion_authorized","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)
    def test_i16_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["status"]="BAD"
        with self.assertRaises(m.RCSEvidenceError):m.validate_rcs_evidence(bad)
        self.assertEqual(m.validate_rcs_evidence(valid()),m.validate_rcs_evidence(valid()))
    def test_i16_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice16.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-PREREGISTRATION.md","governance-runtime/r8_v15_r1_rcs_evidence_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice16.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice16.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH11-13-CLOSURE.json"):
            self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
