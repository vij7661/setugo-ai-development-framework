import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice19-aiep-runtime-profile-local-2026-09-25"
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_aiep_runtime_profile_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def valid(attestation_state="ATTESTED"):
    return {
      "runtime_manifest_digest":"runtime:manifest",
      "attestation_state":attestation_state,
      "read_only_root_filesystem":True,
      "arbitrary_mutable_environment_allowed":False,
      "direct_db_cloud_provider_credentials_allowed":False,
      "general_external_network_dns_allowed":False,
      "approved_channel_ids":["channel:1","channel:2"],
      "dynamic_code_loading_outside_runtime_manifest_allowed":False,
      "profile_digest":"profile:digest"
    }

class Slice19FrozenAcceptance(unittest.TestCase):
    def test_i19_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["AIEPRuntimeProfile"]["required"]
        self.assertEqual(set(req),set(m.AIEP_RUNTIME_PROFILE_FIELDS)); self.assertEqual(len(req),len(m.AIEP_RUNTIME_PROFILE_FIELDS))
    def test_i19_02_valid_declared_attested_passes(self):
        r=require().validate_aiep_runtime_profile(valid("ATTESTED"))
        self.assertTrue(r["locally_valid"]); self.assertEqual(r["declared_attestation_state"],"ATTESTED"); self.assertFalse(r["attestation_verified"])
    def test_i19_03_unattested_runtime_passes_without_authority(self):
        r=require().validate_aiep_runtime_profile(valid("UNATTESTED_RUNTIME"))
        self.assertTrue(r["locally_valid"]); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("strong_evidence_producer_qualified","root_authority_evaluator","terminal_authority_evaluator","runtime_qualified"): self.assertFalse(r[k],k)
    def test_i19_04_top_level_mapping_and_field_closure(self):
        m=require()
        with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile([])
        self.assertEqual(cm.exception.code,"AIEP_PROFILE_FIELD_SET_INVALID")
        x=valid(); x.pop("profile_digest")
        with self.assertRaises(m.AIEPRuntimeProfileError) as cm2:m.validate_aiep_runtime_profile(x)
        self.assertEqual(cm2.exception.code,"AIEP_PROFILE_FIELD_SET_INVALID")
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.AIEPRuntimeProfileError) as cm3:m.validate_aiep_runtime_profile(x)
        self.assertEqual(cm3.exception.code,"AIEP_PROFILE_FIELD_SET_INVALID")
    def test_i19_05_digest_string_rules(self):
        m=require()
        for field,bad,code in (("runtime_manifest_digest",1,"AIEP_PROFILE_STRING_INVALID"),("profile_digest","","AIEP_PROFILE_STRING_INVALID"),("runtime_manifest_digest","e\u0301","AIEP_PROFILE_GCP_STRING_INVALID"),("profile_digest","\ufdd0","AIEP_PROFILE_GCP_STRING_INVALID")):
            x=valid(); x[field]=bad
            with self.subTest(field=field,bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,code)
    def test_i19_06_attestation_enum_closure(self):
        m=require()
        for good in ("ATTESTED","UNATTESTED_RUNTIME"):
            self.assertTrue(m.validate_aiep_runtime_profile(valid(good))["locally_valid"])
        for bad in ("UNKNOWN","",None,1,True):
            x=valid(); x["attestation_state"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_ATTESTATION_STATE_INVALID")
    def test_i19_07_read_only_root_exact_true(self):
        m=require()
        for bad in (False,1,"true",None):
            x=valid(); x["read_only_root_filesystem"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_READ_ONLY_ROOT_INVALID")
    def test_i19_08_arbitrary_mutable_environment_exact_false(self):
        m=require()
        for bad in (True,0,"false",None):
            x=valid(); x["arbitrary_mutable_environment_allowed"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_MUTABLE_ENV_INVALID")
    def test_i19_09_direct_db_credentials_exact_false(self):
        m=require()
        for bad in (True,0,"false",None):
            x=valid(); x["direct_db_cloud_provider_credentials_allowed"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_DIRECT_CREDENTIALS_INVALID")
    def test_i19_10_external_network_dns_exact_false(self):
        m=require()
        for bad in (True,0,"false",None):
            x=valid(); x["general_external_network_dns_allowed"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_EXTERNAL_NETWORK_INVALID")
    def test_i19_11_dynamic_code_loading_exact_false(self):
        m=require()
        for bad in (True,0,"false",None):
            x=valid(); x["dynamic_code_loading_outside_runtime_manifest_allowed"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_DYNAMIC_CODE_INVALID")
    def test_i19_12_approved_channels_nonempty_list(self):
        m=require()
        for bad in ([],("channel:1",),"channel:1",None):
            x=valid(); x["approved_channel_ids"]=bad
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm.exception.code,"AIEP_PROFILE_CHANNELS_INVALID")
    def test_i19_13_approved_channel_elements_unique_and_gcp_valid(self):
        m=require()
        x=valid(); x["approved_channel_ids"]=["channel:1","channel:1"]
        with self.assertRaises(m.AIEPRuntimeProfileError) as cm:m.validate_aiep_runtime_profile(x)
        self.assertEqual(cm.exception.code,"AIEP_PROFILE_CHANNELS_NOT_UNIQUE")
        for bad,code in ((1,"AIEP_PROFILE_CHANNEL_STRING_INVALID"),("","AIEP_PROFILE_CHANNEL_STRING_INVALID"),("e\u0301","AIEP_PROFILE_CHANNEL_GCP_INVALID"),("\ufdd0","AIEP_PROFILE_CHANNEL_GCP_INVALID")):
            x=valid(); x["approved_channel_ids"]=[bad]
            with self.subTest(bad=bad):
                with self.assertRaises(m.AIEPRuntimeProfileError) as cm2:m.validate_aiep_runtime_profile(x)
                self.assertEqual(cm2.exception.code,code)
    def test_i19_14_opaque_digests_and_no_positive_authority(self):
        m=require(); x=valid("ATTESTED"); x["runtime_manifest_digest"]="not-a-sha"; x["profile_digest"]="opaque"
        r=m.validate_aiep_runtime_profile(x); self.assertTrue(r["locally_valid"]); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("runtime_manifest_verified","profile_digest_verified","attestation_verified","approved_channels_authorized","runtime_profile_current","strong_evidence_producer_qualified","root_authority_evaluator","terminal_authority_evaluator","runtime_qualified","evidence_promotion_authorized","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i19_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["read_only_root_filesystem"]=False
        with self.assertRaises(m.AIEPRuntimeProfileError):m.validate_aiep_runtime_profile(bad)
        self.assertEqual(m.validate_aiep_runtime_profile(valid()),m.validate_aiep_runtime_profile(valid()))
    def test_i19_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice19.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-PREREGISTRATION.md","governance-runtime/r8_v15_r1_aiep_runtime_profile_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice19.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice19.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH14-16-CLOSURE.json"): self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
