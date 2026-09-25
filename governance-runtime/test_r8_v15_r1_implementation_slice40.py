import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice40-spg1-binding-family-local-2026-09-25"; D="a"*64
try: mod=importlib.import_module("r8_v15_r1_spg1_binding_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def runtime(): return {"application_artifact_digest":D,"interpreter_compiler_runtime_version_digest":None,"crypto_library_digest":None,"schema_parser_bundle_digest":None,"os_container_image_digest":None,"las_anchor_client_library_digest":None,"runtime_manifest_digest":None}
def valid():
    return {"schema":"r8-v15-r1-spg-1-binding/v1","status":"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","authority_effect":"NONE","generator_id":"g1","generator_artifact_path":"gen.py","generator_artifact_sha256":D,"runtime_manifest":runtime(),"workload_attestation_policy_digest":None,"workload_attestation_proof_digest":None,"allowed_input_design_artifacts":["d1"],"allowed_output_schema_classes":["c1"],"signing_credential_id":None,"revocation_state":"ACTIVE","qualification_status":"UNATTESTED_RUNTIME"}
class Slice40CompositeAcceptance(unittest.TestCase):
    def test_i40_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"schema-provenance-generator.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS); self.assertEqual(tuple(d["$defs"]["RuntimeManifest"]["required"]),m.RUNTIME_FIELDS)
    def test_i40_02_valid_passes(self): self.assertTrue(require().validate_spg1_binding(valid())["locally_valid"])
    def test_i40_03_root_shape_consts_status(self):
        m=require(); x=valid(); x["status"]="QUALIFIED_GENERATOR_BINDING"; self.assertTrue(m.validate_spg1_binding(x)["locally_valid"])
        x=valid(); x["extra"]=1
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_04_required_strings_and_digest(self):
        m=require()
        for f,bad in (("generator_id",""),("generator_artifact_path",True),("generator_artifact_sha256","A"*64)):
            x=valid(); x[f]=bad
            with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_05_runtime_manifest_shape_and_digest(self):
        m=require(); x=valid(); x["runtime_manifest"]["application_artifact_digest"]="a"*63
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
        x=valid(); x["runtime_manifest"]["extra"]=None
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_06_nullable_attestation_digests(self):
        m=require(); x=valid(); x["workload_attestation_policy_digest"]=D; x["workload_attestation_proof_digest"]=D; self.assertTrue(m.validate_spg1_binding(x)["locally_valid"])
        x=valid(); x["workload_attestation_policy_digest"]="A"*64
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_07_allowed_arrays_min1_unique(self):
        m=require()
        for f in ("allowed_input_design_artifacts","allowed_output_schema_classes"):
            x=valid(); x[f]=[]
            with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
            x=valid(); x[f]=["x","x"]
            with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_08_signing_credential_nullable(self):
        m=require(); x=valid(); x["signing_credential_id"]="cred"; self.assertTrue(m.validate_spg1_binding(x)["locally_valid"])
        x=valid(); x["signing_credential_id"]=""
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_09_revocation_enum(self):
        m=require()
        for st in ("ACTIVE","SUSPENDED","REVOKED","RETIRED","UNKNOWN"):
            x=valid(); x["revocation_state"]=st; self.assertTrue(m.validate_spg1_binding(x)["locally_valid"])
        x=valid(); x["revocation_state"]="BAD"
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_10_qualification_enum(self):
        m=require()
        for st in ("QUALIFIED","UNATTESTED_RUNTIME","REVOKED","DRIFTED","UNREGISTERED"):
            x=valid(); x["qualification_status"]=st; self.assertTrue(m.validate_spg1_binding(x)["locally_valid"])
        x=valid(); x["qualification_status"]="BAD"
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_11_qualified_declarations_do_not_prove_qualification(self):
        m=require(); x=valid(); x["status"]="QUALIFIED_GENERATOR_BINDING"; x["qualification_status"]="QUALIFIED"; r=m.validate_spg1_binding(x)
        self.assertFalse(r["generator_qualification_verified"]); self.assertFalse(r["workload_attestation_verified"])
    def test_i40_12_digest_strict_lowercase_hex(self):
        m=require()
        for bad in ("g"*64,"A"*64,"a"*65):
            x=valid(); x["generator_artifact_sha256"]=bad
            with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(x)
    def test_i40_13_runtime_nulls_structurally_allowed(self):
        self.assertTrue(require().validate_spg1_binding(valid())["locally_valid"])
    def test_i40_14_no_currentness_or_final_freeze_authority(self):
        r=require().validate_spg1_binding(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("artifact_authenticity_verified","runtime_manifest_verified","revocation_current","final_freeze_eligibility_verified","signing_authority_verified","runtime_qualified","terminal_authority"): self.assertFalse(r[k],k)
    def test_i40_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["generator_artifact_sha256"]="bad"
        with self.assertRaises(m.SPG1BindingError): m.validate_spg1_binding(bad)
        self.assertTrue(m.validate_spg1_binding(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_spg1_binding_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_spm1_provenance",src)
    def test_i40_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice40.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE40-PREREGISTRATION.md","r8_v15_r1_spg1_binding_family_validator.py","test_r8_v15_r1_implementation_slice40.py","R8-V15-R1-IMPLEMENTATION-SLICE40-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
