import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice14-rcs-vector-result-local-2026-09-25"
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_rcs_vector_result_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def valid(result="PASS"):
    return {
      "vector_id":"vector:1",
      "input_digest":"input:digest",
      "output_digest":"output:digest",
      "result":result,
      "result_digest":"result:digest"
    }

class Slice14FrozenAcceptance(unittest.TestCase):
    def test_i14_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverConformanceVectorResult"]["required"]
        self.assertEqual(set(req),set(m.RCS_VECTOR_RESULT_FIELDS)); self.assertEqual(len(req),len(m.RCS_VECTOR_RESULT_FIELDS))
    def test_i14_02_valid_pass(self):
        self.assertTrue(require().validate_rcs_vector_result(valid("PASS"))["locally_valid"])
    def test_i14_03_valid_fail(self):
        self.assertTrue(require().validate_rcs_vector_result(valid("FAIL"))["locally_valid"])
    def test_i14_04_missing_rejects(self):
        m=require(); x=valid(); x.pop("vector_id")
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_FIELD_SET_INVALID")
    def test_i14_05_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_FIELD_SET_INVALID")
    def test_i14_06_non_string_rejects(self):
        m=require(); x=valid(); x["input_digest"]=1
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_STRING_INVALID")
    def test_i14_07_empty_rejects(self):
        m=require(); x=valid(); x["result_digest"]=""
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_STRING_INVALID")
    def test_i14_08_non_nfc_rejects(self):
        m=require(); x=valid(); x["vector_id"]="e\u0301"
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_GCP_STRING_INVALID")
    def test_i14_09_noncharacter_rejects(self):
        m=require(); x=valid(); x["output_digest"]="\ufdd0"
        with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
        self.assertEqual(cm.exception.code,"RCS_VECTOR_GCP_STRING_INVALID")
    def test_i14_10_result_enum_closure(self):
        m=require()
        for bad in ("UNKNOWN","",None,1,True):
            x=valid(); x["result"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RCSVectorResultError) as cm:m.validate_rcs_vector_result(x)
                self.assertEqual(cm.exception.code,"RCS_VECTOR_RESULT_INVALID")
    def test_i14_11_opaque_non_sha_digests_pass(self):
        m=require(); x=valid(); x["input_digest"]="not-a-sha"; x["output_digest"]="opaque"; x["result_digest"]="also-not-sha"
        self.assertTrue(m.validate_rcs_vector_result(x)["locally_valid"])
    def test_i14_12_result_digest_unverified(self):
        self.assertFalse(require().validate_rcs_vector_result(valid())["result_digest_verified"])
    def test_i14_13_input_output_digests_unverified(self):
        r=require().validate_rcs_vector_result(valid())
        self.assertFalse(r["input_digest_verified"]); self.assertFalse(r["output_digest_verified"])
    def test_i14_14_non_authority_metadata(self):
        r=require().validate_rcs_vector_result(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("vector_executed","conformance_qualified","resolver_authorized","runtime_qualified","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)
    def test_i14_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["result"]="BAD"
        with self.assertRaises(m.RCSVectorResultError):m.validate_rcs_vector_result(bad)
        self.assertEqual(m.validate_rcs_vector_result(valid()),m.validate_rcs_vector_result(valid()))
    def test_i14_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice14.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-PREREGISTRATION.md","governance-runtime/r8_v15_r1_rcs_vector_result_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice14.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice14.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH11-13-CLOSURE.json"):
            self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
