import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice20-stable-scope-value-local-2026-09-25"
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_stable_scope_value_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
class Slice20FrozenAcceptance(unittest.TestCase):
    def test_i20_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["StableScopeValue"]
        self.assertEqual((d["type"],d["minLength"],d["pattern"]),(m.SCHEMA_TYPE,m.MIN_LENGTH,m.PATTERN))
    def test_i20_02_ordinary_value_passes(self): self.assertTrue(require().validate_stable_scope_value("tenant:1")["locally_valid"])
    def test_i20_03_exact_any_rejects(self):
        m=require()
        with self.assertRaises(m.StableScopeValueError) as cm:m.validate_stable_scope_value("ANY")
        self.assertEqual(cm.exception.code,"STABLE_SCOPE_ANY_FORBIDDEN")
    def test_i20_04_empty_rejects(self):
        m=require()
        with self.assertRaises(m.StableScopeValueError) as cm:m.validate_stable_scope_value("")
        self.assertEqual(cm.exception.code,"STABLE_SCOPE_VALUE_INVALID")
    def test_i20_05_non_strings_reject(self):
        m=require()
        for bad in (None,True,False,1,1.5,[],{}):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.StableScopeValueError) as cm:m.validate_stable_scope_value(bad)
                self.assertEqual(cm.exception.code,"STABLE_SCOPE_VALUE_INVALID")
    def test_i20_06_non_nfc_rejects(self):
        m=require()
        with self.assertRaises(m.StableScopeValueError) as cm:m.validate_stable_scope_value("e\u0301")
        self.assertEqual(cm.exception.code,"STABLE_SCOPE_GCP_INVALID")
    def test_i20_07_noncharacter_rejects(self):
        m=require()
        with self.assertRaises(m.StableScopeValueError) as cm:m.validate_stable_scope_value("\ufdd0")
        self.assertEqual(cm.exception.code,"STABLE_SCOPE_GCP_INVALID")
    def test_i20_08_opaque_punctuation_passes(self): self.assertTrue(require().validate_stable_scope_value("tenant:alpha/beta-1")["locally_valid"])
    def test_i20_09_whitespace_value_passes(self): self.assertTrue(require().validate_stable_scope_value("tenant alpha")["locally_valid"])
    def test_i20_10_any_like_non_exact_passes(self): self.assertTrue(require().validate_stable_scope_value("ANYTHING")["locally_valid"])
    def test_i20_11_deterministic(self):
        m=require(); self.assertEqual(m.validate_stable_scope_value("x"),m.validate_stable_scope_value("x"))
    def test_i20_12_failure_does_not_poison(self):
        m=require()
        with self.assertRaises(m.StableScopeValueError):m.validate_stable_scope_value("ANY")
        self.assertTrue(m.validate_stable_scope_value("x")["locally_valid"])
    def test_i20_13_non_authority_metadata(self):
        r=require().validate_stable_scope_value("x"); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["terminal_authority"])
    def test_i20_14_currentness_permission_selection_false(self):
        r=require().validate_stable_scope_value("x")
        for k in ("scope_permission_verified","scope_current","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted"): self.assertFalse(r[k],k)
    def test_i20_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_stable_scope_value_validator.py").read_text()
        for name in ("r8_v15_r1_scope_component_validator","r8_v15_r1_canonical_scope_tuple_validator","r8_v15_r1_any_scope_permission_validator"): self.assertNotIn(name,src)
    def test_i20_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice20.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE20-PREREGISTRATION.md","r8_v15_r1_stable_scope_value_validator.py","test_r8_v15_r1_implementation_slice20.py","R8-V15-R1-IMPLEMENTATION-SLICE20-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
