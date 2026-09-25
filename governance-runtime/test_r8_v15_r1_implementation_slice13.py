import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice13-rcs-suite-local-2026-09-25"
sys.path.insert(0,str(HERE))
slice1=importlib.import_module("r8_v15_r1_frozen_schema_runtime")
try:
    rcs=importlib.import_module("r8_v15_r1_rcs_suite_validator"); IMPORT_ERROR=None
except Exception as exc:
    rcs=None; IMPORT_ERROR=exc

def require():
    if rcs is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return rcs

def valid():
    return {
      "suite_id":"suite:1",
      "suite_version":"suite-v1",
      "vector_manifest_digest":"vector-manifest:1",
      "vector_generator_implementation_digest":"vector-generator:1",
      "generator_runtime_manifest_digest":"generator-runtime:1",
      "input_corpus_digest":"input-corpus:1",
      "expected_result_manifest_digest":"expected-results:1",
      "execution_harness_digest":"harness:1",
      "required_resolver_runtime_identity_digest":"resolver-runtime-id:1",
      "required_resolver_workload_identity_digest":"resolver-workload-id:1",
      "result_schema_digest":"result-schema:1",
      "suite_digest":"suite-digest:1"
    }

class Slice13FrozenAcceptance(unittest.TestCase):
    def test_i13_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverConformanceSuite1"]["required"]
        self.assertEqual(set(req),set(m.RCS_SUITE_FIELDS)); self.assertEqual(len(req),len(m.RCS_SUITE_FIELDS))
    def test_i13_02_missing_rejects(self):
        m=require(); x=valid(); x.pop("suite_id")
        with self.assertRaises(m.RCSSuiteError) as cm:m.validate_rcs_suite(x)
        self.assertEqual(cm.exception.code,"RCS_SUITE_FIELD_SET_INVALID")
    def test_i13_03_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.RCSSuiteError) as cm:m.validate_rcs_suite(x)
        self.assertEqual(cm.exception.code,"RCS_SUITE_FIELD_SET_INVALID")
    def test_i13_04_nonempty_strings(self):
        m=require()
        for field,bad in (("suite_id",""),("suite_version",1)):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RCSSuiteError) as cm:m.validate_rcs_suite(x)
                self.assertEqual(cm.exception.code,"RCS_SUITE_STRING_INVALID")
    def test_i13_05_non_nfc_rejects(self):
        m=require(); x=valid(); x["suite_version"]="e\u0301"
        with self.assertRaises(m.RCSSuiteError) as cm:m.validate_rcs_suite(x)
        self.assertEqual(cm.exception.code,"RCS_SUITE_GCP_STRING_INVALID")
    def test_i13_06_noncharacter_rejects(self):
        m=require(); x=valid(); x["result_schema_digest"]="\ufdd0"
        with self.assertRaises(m.RCSSuiteError) as cm:m.validate_rcs_suite(x)
        self.assertEqual(cm.exception.code,"RCS_SUITE_GCP_STRING_INVALID")
    def test_i13_07_opaque_non_sha_digests_pass(self):
        m=require(); x=valid(); x["suite_digest"]="not-a-sha"; self.assertTrue(m.validate_rcs_suite(x)["locally_valid"])
    def test_i13_08_suite_id_opaque(self):
        m=require(); x=valid(); x["suite_id"]="opaque suite id"; self.assertTrue(m.validate_rcs_suite(x)["locally_valid"])
    def test_i13_09_suite_version_opaque(self):
        m=require(); x=valid(); x["suite_version"]="opaque suite version"; self.assertTrue(m.validate_rcs_suite(x)["locally_valid"])
    def test_i13_10_runtime_identity_unverified(self):
        r=require().validate_rcs_suite(valid()); self.assertFalse(r["required_runtime_identity_verified"])
    def test_i13_11_workload_identity_unverified(self):
        r=require().validate_rcs_suite(valid()); self.assertFalse(r["required_workload_identity_verified"])
    def test_i13_12_suite_digest_unverified(self):
        r=require().validate_rcs_suite(valid()); self.assertFalse(r["suite_digest_verified"])
    def test_i13_13_generator_harness_unverified(self):
        r=require().validate_rcs_suite(valid()); self.assertFalse(r["vector_generator_identity_verified"]); self.assertFalse(r["execution_harness_verified"])
    def test_i13_14_non_authority_metadata(self):
        r=require().validate_rcs_suite(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("suite_current","suite_executed","resolver_qualified","conformance_fresh","runtime_qualified","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i13_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["suite_digest"]=""
        with self.assertRaises(m.RCSSuiteError):m.validate_rcs_suite(bad)
        self.assertEqual(m.validate_rcs_suite(valid()),m.validate_rcs_suite(valid()))
    def test_i13_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice13.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE13-PREREGISTRATION.md","governance-runtime/r8_v15_r1_rcs_suite_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice13.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE13-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice13.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py"): self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
