import copy, importlib, itertools, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice46-frozen-instance-family-exact-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_frozen_instance_family_exact_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
FILES=["review-presentation-schema.json","gcp-rvm-2.json","case-proof-contracts.json","schema-provenance-generator-binding.json","schema-provenance-manifest-candidate.json"]
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def load(name): return json.loads((SCHEMA_DIR/name).read_text())
class Slice46FrozenAcceptance(unittest.TestCase):
    def test_i46_01_family_identity(self):
        self.assertEqual(FILES,require().ARTIFACTS)
    def test_i46_02_review_presentation_exact(self): self.assertTrue(require().validate_frozen_instance("review-presentation-schema.json",load("review-presentation-schema.json"))["locally_valid"])
    def test_i46_03_gcp_rvm_exact(self): self.assertTrue(require().validate_frozen_instance("gcp-rvm-2.json",load("gcp-rvm-2.json"))["locally_valid"])
    def test_i46_04_case_proof_exact(self): self.assertTrue(require().validate_frozen_instance("case-proof-contracts.json",load("case-proof-contracts.json"))["locally_valid"])
    def test_i46_05_spg_binding_exact(self): self.assertTrue(require().validate_frozen_instance("schema-provenance-generator-binding.json",load("schema-provenance-generator-binding.json"))["locally_valid"])
    def test_i46_06_spm_candidate_exact(self): self.assertTrue(require().validate_frozen_instance("schema-provenance-manifest-candidate.json",load("schema-provenance-manifest-candidate.json"))["locally_valid"])
    def test_i46_07_review_mutation_rejects(self):
        m=require(); x=load(FILES[0]); x["schema"]="bad"
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance(FILES[0],x)
    def test_i46_08_gcp_mutation_rejects(self):
        m=require(); x=load(FILES[1]); x["schema"]="bad"
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance(FILES[1],x)
    def test_i46_09_caseproof_mutation_rejects(self):
        m=require(); x=load(FILES[2]); x["guard_range"]="bad"
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance(FILES[2],x)
    def test_i46_10_spg_mutation_rejects(self):
        m=require(); x=load(FILES[3]); x["qualification_status"]="UNREGISTERED"
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance(FILES[3],x)
    def test_i46_11_spm_mutation_rejects(self):
        m=require(); x=load(FILES[4]); x["status"]="__mutated__"
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance(FILES[4],x)
    def test_i46_12_unknown_artifact_rejects(self):
        m=require()
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance("unknown.json",{})
    def test_i46_13_deterministic(self):
        m=require(); x=load(FILES[0]); self.assertEqual(m.validate_frozen_instance(FILES[0],x),m.validate_frozen_instance(FILES[0],x))
    def test_i46_14_non_authority_no_semantic_execution(self):
        r=require().validate_frozen_instance(FILES[3],load(FILES[3])); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["semantic_correctness_verified"]); self.assertFalse(r["qualification_verified"]); self.assertFalse(r["terminal_authority"])
    def test_i46_15_nonpoison_and_no_sibling_dependency(self):
        m=require()
        with self.assertRaises(m.FrozenInstanceFamilyExactError): m.validate_frozen_instance("unknown.json",{})
        self.assertTrue(m.validate_frozen_instance(FILES[0],load(FILES[0]))["locally_valid"])
        src=(HERE/"r8_v15_r1_frozen_instance_family_exact_validator.py").read_text(); self.assertNotIn("r8_v15_r1_spg1_binding_family_validator",src)
    def test_i46_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice46.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE46-PREREGISTRATION.md","r8_v15_r1_frozen_instance_family_exact_validator.py","test_r8_v15_r1_implementation_slice46.py","R8-V15-R1-IMPLEMENTATION-SLICE46-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
