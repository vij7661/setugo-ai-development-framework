import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice34-spm-source-ref-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_spm_source_ref_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid(): return {"design_id":"design:1","path":"path/to/file","commit":"commit:opaque","blob":"blob:opaque"}
class Slice34FrozenAcceptance(unittest.TestCase):
    def test_i34_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"schema-provenance-manifest.schema.json").read_text())["$defs"]["SourceRef"]; self.assertEqual(tuple(d["required"]),m.FIELDS)
    def test_i34_02_valid_passes(self): self.assertTrue(require().validate_spm_source_ref(valid())["locally_valid"])
    def test_i34_03_shape(self):
        m=require()
        with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref([])
        x=valid(); x.pop("blob")
        with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
    def test_i34_04_design_id_string(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["design_id"]=bad
            with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
    def test_i34_05_path_string(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["path"]=bad
            with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
    def test_i34_06_commit_string(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["commit"]=bad
            with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
    def test_i34_07_blob_string(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["blob"]=bad
            with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(x)
    def test_i34_08_opaque_commit_blob_accepted(self):
        m=require(); x=valid(); x["commit"]="not-a-sha"; x["blob"]="not-a-sha"; self.assertTrue(m.validate_spm_source_ref(x)["locally_valid"])
    def test_i34_09_opaque_path_accepted(self):
        m=require(); x=valid(); x["path"]="weird path/with spaces"; self.assertTrue(m.validate_spm_source_ref(x)["locally_valid"])
    def test_i34_10_unicode_nfc_accepted(self):
        m=require(); x=valid(); x["design_id"]="dé"; self.assertTrue(m.validate_spm_source_ref(x)["locally_valid"])
    def test_i34_11_no_source_existence_inference(self):
        r=require().validate_spm_source_ref(valid()); self.assertFalse(r["source_exists_verified"]); self.assertFalse(r["commit_blob_verified"])
    def test_i34_12_no_source_authority_inference(self):
        r=require().validate_spm_source_ref(valid()); self.assertFalse(r["source_authority_verified"]); self.assertFalse(r["provenance_referential_integrity_verified"])
    def test_i34_13_deterministic(self):
        m=require(); self.assertEqual(m.validate_spm_source_ref(valid()),m.validate_spm_source_ref(valid()))
    def test_i34_14_non_authority(self):
        r=require().validate_spm_source_ref(valid()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["evidence_promotion_authorized"]); self.assertFalse(r["terminal_authority"])
    def test_i34_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["path"]=""
        with self.assertRaises(m.SPMSourceRefError): m.validate_spm_source_ref(bad)
        self.assertTrue(m.validate_spm_source_ref(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_spm_source_ref_validator.py").read_text(); self.assertNotIn("r8_v15_r1_review_",src)
    def test_i34_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice34.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE34-PREREGISTRATION.md","r8_v15_r1_spm_source_ref_validator.py","test_r8_v15_r1_implementation_slice34.py","R8-V15-R1-IMPLEMENTATION-SLICE34-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
