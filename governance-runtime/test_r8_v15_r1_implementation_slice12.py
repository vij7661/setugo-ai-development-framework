import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice12-rir-record-local-2026-09-25"
sys.path.insert(0,str(HERE))
slice1=importlib.import_module("r8_v15_r1_frozen_schema_runtime")
try:
    rir=importlib.import_module("r8_v15_r1_rir_record_validator"); IMPORT_ERROR=None
except Exception as exc:
    rir=None; IMPORT_ERROR=exc

def require():
    if rir is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return rir

def valid():
    return {
      "resolver_implementation_record_id":"resolver-record:1",
      "rir_record_id":"rir:1",
      "resolver_policy_digest":"policy:digest",
      "implementation_id":"impl:1",
      "resolver_implementation_digest":"impl:digest",
      "resolver_runtime_manifest_digest":"runtime:manifest",
      "workload_attestation_policy_digest":"workload:policy",
      "runtime_identity_digest":"runtime:identity",
      "workload_identity_digest":"workload:identity",
      "conformance_suite_digest":"suite:digest",
      "predecessor_record_id":None,
      "constitutional_source_evidence_digest":"constitutional:evidence",
      "activation_sequence":0,
      "retirement_or_revocation_sequence":None,
      "lifecycle_state":"ACTIVE",
      "freshness_profile_id":"freshness:1",
      "record_digest":"record:digest"
    }

class Slice12FrozenAcceptance(unittest.TestCase):
    def test_i12_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverImplementationRegistryRecord"]["required"]
        self.assertEqual(set(req),set(m.RIR_RECORD_FIELDS)); self.assertEqual(len(req),len(m.RIR_RECORD_FIELDS))
    def test_i12_02_missing_rejects(self):
        m=require(); x=valid(); x.pop("rir_record_id")
        with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
        self.assertEqual(cm.exception.code,"RIR_FIELD_SET_INVALID")
    def test_i12_03_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
        self.assertEqual(cm.exception.code,"RIR_FIELD_SET_INVALID")
    def test_i12_04_required_strings_nonempty(self):
        m=require()
        for field,bad in (("implementation_id",""),("resolver_policy_digest",1)):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
                self.assertEqual(cm.exception.code,"RIR_STRING_INVALID")
    def test_i12_05_gcp_string_rejection(self):
        m=require()
        for field,bad in (("rir_record_id","e\u0301"),("record_digest","\ufdd0")):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
                self.assertEqual(cm.exception.code,"RIR_GCP_STRING_INVALID")
    def test_i12_06_predecessor_nullable_or_nonempty(self):
        m=require(); self.assertTrue(m.validate_rir_record(valid())["locally_valid"])
        x=valid(); x["predecessor_record_id"]="prev:1"; self.assertTrue(m.validate_rir_record(x)["locally_valid"])
        for bad in ("",1):
            x=valid(); x["predecessor_record_id"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
                self.assertEqual(cm.exception.code,"RIR_PREDECESSOR_INVALID")
    def test_i12_07_activation_sequence(self):
        m=require()
        for good in (0,9223372036854775807):
            x=valid(); x["activation_sequence"]=good; self.assertTrue(m.validate_rir_record(x)["locally_valid"])
        for bad in (-1,9223372036854775808,True,"1",1.5):
            x=valid(); x["activation_sequence"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
                self.assertEqual(cm.exception.code,"RIR_SEQUENCE_INVALID")
    def test_i12_08_retirement_sequence_nullable_and_bounded(self):
        m=require()
        for good in (None,0,9223372036854775807):
            x=valid(); x["retirement_or_revocation_sequence"]=good; self.assertTrue(m.validate_rir_record(x)["locally_valid"])
        for bad in (-1,9223372036854775808,True,"1",1.5):
            x=valid(); x["retirement_or_revocation_sequence"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
                self.assertEqual(cm.exception.code,"RIR_SEQUENCE_INVALID")
    def test_i12_09_lifecycle_enum(self):
        m=require()
        for good in ("ACTIVE","SUSPENDED","RETIRED","REVOKED"):
            x=valid(); x["lifecycle_state"]=good; self.assertTrue(m.validate_rir_record(x)["locally_valid"])
        x=valid(); x["lifecycle_state"]="UNKNOWN"
        with self.assertRaises(m.RIRRecordError) as cm:m.validate_rir_record(x)
        self.assertEqual(cm.exception.code,"RIR_LIFECYCLE_INVALID")
    def test_i12_10_opaque_digests_pass(self):
        m=require(); x=valid(); x["resolver_implementation_digest"]="not-a-sha"; self.assertTrue(m.validate_rir_record(x)["locally_valid"])
    def test_i12_11_no_local_temporal_order_rule(self):
        m=require(); x=valid(); x["activation_sequence"]=100; x["retirement_or_revocation_sequence"]=50
        r=m.validate_rir_record(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["temporal_ordering_verified"])
    def test_i12_12_temporal_eligibility_unproven(self):
        r=require().validate_rir_record(valid()); self.assertFalse(r["temporal_eligibility_proven"])
    def test_i12_13_record_digest_unverified(self):
        r=require().validate_rir_record(valid()); self.assertFalse(r["record_digest_verified"])
    def test_i12_14_non_authority_metadata(self):
        r=require().validate_rir_record(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("record_current","registry_head_current","resolver_authorized","conformance_qualified","runtime_qualified","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i12_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["lifecycle_state"]="BAD"
        with self.assertRaises(m.RIRRecordError):m.validate_rir_record(bad)
        self.assertEqual(m.validate_rir_record(valid()),m.validate_rir_record(valid()))
    def test_i12_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice12.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE12-PREREGISTRATION.md","governance-runtime/r8_v15_r1_rir_record_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice12.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE12-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice12.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py"): self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
