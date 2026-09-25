import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice15-rcs-aggregate-result-local-2026-09-25"
INT64_MAX=9223372036854775807
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_rcs_aggregate_result_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def valid(status="PASS",vector_count=2,passed_vector_count=2):
    return {
      "status":status,
      "vector_count":vector_count,
      "passed_vector_count":passed_vector_count,
      "aggregate_digest":"aggregate:digest"
    }

class Slice15FrozenAcceptance(unittest.TestCase):
    def test_i15_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverConformanceAggregateResult"]["required"]
        self.assertEqual(set(req),set(m.RCS_AGGREGATE_RESULT_FIELDS)); self.assertEqual(len(req),len(m.RCS_AGGREGATE_RESULT_FIELDS))
    def test_i15_02_valid_pass(self):
        self.assertTrue(require().validate_rcs_aggregate_result(valid("PASS"))["locally_valid"])
    def test_i15_03_valid_fail(self):
        self.assertTrue(require().validate_rcs_aggregate_result(valid("FAIL",2,1))["locally_valid"])
    def test_i15_04_missing_rejects(self):
        m=require(); x=valid(); x.pop("aggregate_digest")
        with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
        self.assertEqual(cm.exception.code,"RCS_AGGREGATE_FIELD_SET_INVALID")
    def test_i15_05_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
        self.assertEqual(cm.exception.code,"RCS_AGGREGATE_FIELD_SET_INVALID")
    def test_i15_06_status_enum_closure(self):
        m=require()
        for bad in ("UNKNOWN","",None,1,True):
            x=valid(); x["status"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
                self.assertEqual(cm.exception.code,"RCS_AGGREGATE_STATUS_INVALID")
    def test_i15_07_vector_count_bounds_accept(self):
        m=require()
        for good in (1,INT64_MAX):
            self.assertTrue(m.validate_rcs_aggregate_result(valid(vector_count=good))["locally_valid"])
    def test_i15_08_vector_count_invalid(self):
        m=require()
        for bad in (0,-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["vector_count"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
                self.assertEqual(cm.exception.code,"RCS_AGGREGATE_VECTOR_COUNT_INVALID")
    def test_i15_09_passed_count_bounds_accept(self):
        m=require()
        for good in (0,INT64_MAX):
            self.assertTrue(m.validate_rcs_aggregate_result(valid(passed_vector_count=good))["locally_valid"])
    def test_i15_10_passed_count_invalid(self):
        m=require()
        for bad in (-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["passed_vector_count"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
                self.assertEqual(cm.exception.code,"RCS_AGGREGATE_PASSED_COUNT_INVALID")
    def test_i15_11_digest_string_rules(self):
        m=require()
        for bad,code in ((None,"RCS_AGGREGATE_STRING_INVALID"),("","RCS_AGGREGATE_STRING_INVALID"),("e\u0301","RCS_AGGREGATE_GCP_STRING_INVALID"),("\ufdd0","RCS_AGGREGATE_GCP_STRING_INVALID")):
            x=valid(); x["aggregate_digest"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RCSAggregateResultError) as cm:m.validate_rcs_aggregate_result(x)
                self.assertEqual(cm.exception.code,code)
    def test_i15_12_opaque_non_sha_digest_passes(self):
        m=require(); x=valid(); x["aggregate_digest"]="not-a-sha"
        self.assertTrue(m.validate_rcs_aggregate_result(x)["locally_valid"])
    def test_i15_13_no_relational_rule_invented(self):
        r=require().validate_rcs_aggregate_result(valid(status="PASS",vector_count=1,passed_vector_count=2))
        self.assertTrue(r["locally_valid"]); self.assertFalse(r["count_relation_verified"]); self.assertFalse(r["aggregate_semantics_verified"])
    def test_i15_14_non_authority_metadata(self):
        r=require().validate_rcs_aggregate_result(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("aggregate_digest_verified","aggregate_semantics_verified","conformance_qualified","resolver_authorized","runtime_qualified","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)
    def test_i15_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["vector_count"]=0
        with self.assertRaises(m.RCSAggregateResultError):m.validate_rcs_aggregate_result(bad)
        self.assertEqual(m.validate_rcs_aggregate_result(valid()),m.validate_rcs_aggregate_result(valid()))
    def test_i15_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice15.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-PREREGISTRATION.md","governance-runtime/r8_v15_r1_rcs_aggregate_result_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice15.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice15.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH11-13-CLOSURE.json"):
            self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
