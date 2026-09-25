import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice36-case-guard-registry-family-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_case_guard_registry_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def case(i): return {"case_id":f"V1-{i:03d}","text":f"case {i}","source_version":"v1","source_commit":"c","source_blob":"b"}
def case_registry():
    return {"schema":"case-registry/v1","status":"candidate","authority_effect":"NONE","source_versions":[],"case_count":467,"guard_referenced_case_count":0,"missing_guard_referenced_cases":[],"duplicate_conflicts":[],"cases":[case(i) for i in range(1,468)]}
def guard(i):
    return {"guard_id":f"G{i:03d}","mechanism_id":f"m{i}","positive_case_ids":["V1-001"],"negative_cases":[{"case_id":"V1-002","fault_proof_class":"FP0"}],"canonical_source":{"path":"p"},"activation_sequence":"1","lifecycle_state":"ACTIVE"}
def guard_registry():
    return {"schema":"guard-registry/v1","status":"candidate","authority_effect":"NONE","registry_range":"G001-G156","records":[guard(i) for i in range(1,157)]}
class Slice36CompositeAcceptance(unittest.TestCase):
    def test_i36_01_schema_identity(self):
        m=require(); c=json.loads((SCHEMA_DIR/"case-registry.schema.json").read_text()); g=json.loads((SCHEMA_DIR/"guard-registry.schema.json").read_text())
        self.assertEqual(tuple(c["required"]),m.CASE_ROOT_FIELDS); self.assertEqual(tuple(g["required"]),m.GUARD_ROOT_FIELDS)
    def test_i36_02_valid_both_pass(self):
        m=require(); self.assertTrue(m.validate_case_registry(case_registry())["locally_valid"]); self.assertTrue(m.validate_guard_registry(guard_registry())["locally_valid"])
    def test_i36_03_case_root_shape(self):
        m=require()
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry([])
        x=case_registry(); x.pop("cases")
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
        x=case_registry(); x["authority_effect"]="X"
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
    def test_i36_04_case_source_versions_ascii_pattern(self):
        m=require(); x=case_registry(); x["source_versions"]=[{"version":"v12","commit":"c","blob":"b"}]; self.assertTrue(m.validate_case_registry(x)["locally_valid"])
        x=case_registry(); x["source_versions"]=[{"version":"v١","commit":"c","blob":"b"}]
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
    def test_i36_05_case_records_cardinality_and_pattern(self):
        m=require(); x=case_registry(); x["cases"]=x["cases"][:-1]
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
        x=case_registry(); x["cases"][0]["case_id"]="V١-001"
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
    def test_i36_06_case_duplicates_structurally_allowed(self):
        m=require(); x=case_registry(); x["cases"][-1]=dict(x["cases"][0]); r=m.validate_case_registry(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["case_identity_uniqueness_verified"])
    def test_i36_07_case_counts_and_empty_conflicts(self):
        m=require(); x=case_registry(); x["guard_referenced_case_count"]=True
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
        x=case_registry(); x["duplicate_conflicts"]=["x"]
        with self.assertRaises(m.RegistryFamilyError): m.validate_case_registry(x)
    def test_i36_08_guard_root_and_optional_fields(self):
        m=require(); x=guard_registry(); x.update({"seed_catalog":"opaque","v13_design":None,"v14_design":{},"v15_design":None}); self.assertTrue(m.validate_guard_registry(x)["locally_valid"])
        x=guard_registry(); x["registry_range"]="G001-G155"
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
    def test_i36_09_guard_records_and_id_range(self):
        m=require(); x=guard_registry(); x["records"]=x["records"][:-1]
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
        for bad in ("G000","G157","G١01"):
            x=guard_registry(); x["records"][0]["guard_id"]=bad
            with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
    def test_i36_10_positive_case_ids(self):
        m=require(); x=guard_registry(); x["records"][0]["positive_case_ids"]=[]
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
        x=guard_registry(); x["records"][0]["positive_case_ids"]=["V1-001","V1-001"]
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
    def test_i36_11_negative_cases(self):
        m=require(); x=guard_registry(); x["records"][0]["negative_cases"]=[]
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
        x=guard_registry(); x["records"][0]["negative_cases"][0]["fault_proof_class"]="FP7"
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
    def test_i36_12_guard_source_activation_lifecycle(self):
        m=require(); x=guard_registry(); x["records"][0]["canonical_source"]={}
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
        x=guard_registry(); x["records"][0]["lifecycle_state"]="REVOKED"
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(x)
    def test_i36_13_guard_record_duplicates_allowed(self):
        m=require(); x=guard_registry(); x["records"][-1]=dict(x["records"][0]); r=m.validate_guard_registry(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["guard_identity_uniqueness_verified"])
    def test_i36_14_no_cross_registry_or_authority(self):
        m=require(); r1=m.validate_case_registry(case_registry()); r2=m.validate_guard_registry(guard_registry())
        for r in (r1,r2):
            self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["cross_registry_references_verified"]); self.assertFalse(r["registry_authority_granted"]); self.assertFalse(r["terminal_authority"])
    def test_i36_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=guard_registry(); bad["records"]=[]
        with self.assertRaises(m.RegistryFamilyError): m.validate_guard_registry(bad)
        self.assertTrue(m.validate_case_registry(case_registry())["locally_valid"])
        src=(HERE/"r8_v15_r1_case_guard_registry_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_guard_omission",src)
    def test_i36_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice36.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE36-PREREGISTRATION.md","r8_v15_r1_case_guard_registry_family_validator.py","test_r8_v15_r1_implementation_slice36.py","R8-V15-R1-IMPLEMENTATION-SLICE36-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
