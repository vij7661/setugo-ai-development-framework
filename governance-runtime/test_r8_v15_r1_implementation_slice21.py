import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice21-scope-component-local-2026-09-25"
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_scope_component_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
class Slice21FrozenAcceptance(unittest.TestCase):
    def test_i21_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["ScopeComponent"]
        self.assertEqual(d["oneOf"][0]["const"],m.ANY_SENTINEL); self.assertEqual(d["oneOf"][1]["$ref"],m.STABLE_SCOPE_REF)
    def test_i21_02_any_passes(self): self.assertEqual(require().validate_scope_component("ANY")["component_kind"],"ANY")
    def test_i21_03_stable_passes(self): self.assertEqual(require().validate_scope_component("tenant:1")["component_kind"],"STABLE")
    def test_i21_04_empty_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentError) as cm:m.validate_scope_component("")
        self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_INVALID")
    def test_i21_05_non_strings_reject(self):
        m=require()
        for bad in (None,True,False,1,1.5,[],{}):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.ScopeComponentError) as cm:m.validate_scope_component(bad)
                self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_INVALID")
    def test_i21_06_non_nfc_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentError) as cm:m.validate_scope_component("e\u0301")
        self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_GCP_INVALID")
    def test_i21_07_noncharacter_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentError) as cm:m.validate_scope_component("\ufdd0")
        self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_GCP_INVALID")
    def test_i21_08_any_like_passes_as_stable(self): self.assertEqual(require().validate_scope_component("ANYTHING")["component_kind"],"STABLE")
    def test_i21_09_punctuation_passes(self): self.assertTrue(require().validate_scope_component("scope:a/b")["locally_valid"])
    def test_i21_10_kind_is_structural_only(self):
        m=require(); self.assertEqual(m.validate_scope_component("ANY")["component_kind"],"ANY"); self.assertEqual(m.validate_scope_component("x")["component_kind"],"STABLE")
    def test_i21_11_no_any_permission_inferred(self): self.assertFalse(require().validate_scope_component("ANY")["any_permission_verified"])
    def test_i21_12_deterministic(self):
        m=require(); self.assertEqual(m.validate_scope_component("x"),m.validate_scope_component("x"))
    def test_i21_13_failure_does_not_poison(self):
        m=require()
        with self.assertRaises(m.ScopeComponentError):m.validate_scope_component("")
        self.assertTrue(m.validate_scope_component("x")["locally_valid"])
    def test_i21_14_non_authority_metadata(self):
        r=require().validate_scope_component("ANY"); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("scope_current","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i21_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_scope_component_validator.py").read_text()
        for name in ("r8_v15_r1_stable_scope_value_validator","r8_v15_r1_canonical_scope_tuple_validator","r8_v15_r1_any_scope_permission_validator"): self.assertNotIn(name,src)
    def test_i21_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice21.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE21-PREREGISTRATION.md","r8_v15_r1_scope_component_validator.py","test_r8_v15_r1_implementation_slice21.py","R8-V15-R1-IMPLEMENTATION-SLICE21-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
