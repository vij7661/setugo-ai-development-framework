import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice38-gcp-rvm2-family-local-2026-09-25"; D="a"*64
try: mod=importlib.import_module("r8_v15_r1_gcp_rvm2_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def pos(i): return {"vector_id":f"GCP-RVM2-P{i:02d}","input_representation":"","schema_context":"object","expected_canonical_utf8":"","expected_sha256":D,"source_rules":["R1"]}
def rej(i): return {"vector_id":f"GCP-RVM2-R{i:02d}","input_representation":"","schema_context":"object","expected_outcome":"REJECT","expected_rejection_code":"GCP_REJECT_TEST","source_case_id":None,"source_rules":["R1"]}
def valid(): return {"schema":"gcp-rvm-2/v1","status":"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","authority_effect":"NONE","canonical_vectors":[pos(i) for i in range(1,6)],"rejection_vectors":[rej(i) for i in range(1,15)],"canonicalization_rules":["R1"]}
class Slice38CompositeAcceptance(unittest.TestCase):
    def test_i38_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"gcp-rvm-2.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS)
    def test_i38_02_valid_passes(self): self.assertTrue(require().validate_gcp_rvm2_manifest(valid())["locally_valid"])
    def test_i38_03_root_shape_consts(self):
        m=require(); x=valid(); x["schema"]="bad"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_04_positive_min_and_uniqueitems(self):
        m=require(); x=valid(); x["canonical_vectors"]=x["canonical_vectors"][:4]
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["canonical_vectors"].append(dict(x["canonical_vectors"][0]))
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_05_positive_vector_shape_ascii_id(self):
        m=require(); x=valid(); x["canonical_vectors"][0]["vector_id"]="GCP-RVM2-P٠1"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["canonical_vectors"][0].pop("source_rules")
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_06_positive_empty_payload_strings_allowed(self):
        self.assertTrue(require().validate_gcp_rvm2_manifest(valid())["locally_valid"])
    def test_i38_07_digest_strict(self):
        m=require()
        for bad in ("A"*64,"a"*63,True):
            x=valid(); x["canonical_vectors"][0]["expected_sha256"]=bad
            with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_08_rejection_min_and_uniqueitems(self):
        m=require(); x=valid(); x["rejection_vectors"]=x["rejection_vectors"][:13]
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["rejection_vectors"].append(dict(x["rejection_vectors"][0]))
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_09_rejection_id_and_const(self):
        m=require(); x=valid(); x["rejection_vectors"][0]["vector_id"]="GCP-RVM2-R١1"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["rejection_vectors"][0]["expected_outcome"]="PASS"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_10_rejection_code_and_source_case(self):
        m=require(); x=valid(); x["rejection_vectors"][0]["expected_rejection_code"]="bad"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["rejection_vectors"][0]["source_case_id"]="V١-001"
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["rejection_vectors"][0]["source_case_id"]="V2-003"; self.assertTrue(m.validate_gcp_rvm2_manifest(x)["locally_valid"])
    def test_i38_11_source_rules_and_root_rules_unique(self):
        m=require(); x=valid(); x["canonical_vectors"][0]["source_rules"]=["R","R"]
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
        x=valid(); x["canonicalization_rules"]=["R1","R1"]
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(x)
    def test_i38_12_more_than_minimum_allowed(self):
        m=require(); x=valid(); x["canonical_vectors"].append(pos(6)); x["rejection_vectors"].append(rej(15)); self.assertTrue(m.validate_gcp_rvm2_manifest(x)["locally_valid"])
    def test_i38_13_no_execution_or_recompute(self):
        r=require().validate_gcp_rvm2_manifest(valid()); self.assertFalse(r["canonicalization_executed"]); self.assertFalse(r["digest_recomputed"]); self.assertFalse(r["rejection_vectors_executed"])
    def test_i38_14_non_authority(self):
        r=require().validate_gcp_rvm2_manifest(valid()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["diagnostic_semantics_verified"]); self.assertFalse(r["terminal_authority"])
    def test_i38_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["canonical_vectors"]=[]
        with self.assertRaises(m.GCPRVM2Error): m.validate_gcp_rvm2_manifest(bad)
        self.assertTrue(m.validate_gcp_rvm2_manifest(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_gcp_rvm2_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_case_proof",src)
    def test_i38_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice38.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE38-PREREGISTRATION.md","r8_v15_r1_gcp_rvm2_family_validator.py","test_r8_v15_r1_implementation_slice38.py","R8-V15-R1-IMPLEMENTATION-SLICE38-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
