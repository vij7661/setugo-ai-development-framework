import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice23-scope-component-name-local-2026-09-25"
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_scope_component_name_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
class Slice23FrozenAcceptance(unittest.TestCase):
    def test_i23_01_enum_parity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["ScopeComponentName"]
        self.assertEqual(tuple(d["enum"]),m.SCOPE_COMPONENT_NAMES)
    def test_i23_02_all_nine_pass(self):
        m=require()
        for v in m.SCOPE_COMPONENT_NAMES:self.assertEqual(m.validate_scope_component_name(v)["value"],v)
    def test_i23_03_unknown_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError) as cm:m.validate_scope_component_name("unknown")
        self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_NAME_INVALID")
    def test_i23_04_empty_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name("")
    def test_i23_05_non_strings_reject(self):
        m=require()
        for bad in (None,True,False,1,1.5,[],{}):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name(bad)
    def test_i23_06_case_changed_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name("Tenant_Id")
    def test_i23_07_whitespace_changed_rejects(self):
        m=require()
        for bad in (" tenant_id","tenant_id "):
            with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name(bad)
    def test_i23_08_non_nfc_unrelated_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name("e\u0301")
    def test_i23_09_noncharacter_unrelated_rejects(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name("\ufdd0")
    def test_i23_10_echo_only_accepted_value(self): self.assertEqual(require().validate_scope_component_name("tenant_id")["value"],"tenant_id")
    def test_i23_11_no_permission_inferred(self): self.assertFalse(require().validate_scope_component_name("tenant_id")["any_permission_verified"])
    def test_i23_12_deterministic(self):
        m=require(); self.assertEqual(m.validate_scope_component_name("tenant_id"),m.validate_scope_component_name("tenant_id"))
    def test_i23_13_failure_does_not_poison(self):
        m=require()
        with self.assertRaises(m.ScopeComponentNameError):m.validate_scope_component_name("bad")
        self.assertTrue(m.validate_scope_component_name("tenant_id")["locally_valid"])
    def test_i23_14_non_authority_metadata(self):
        r=require().validate_scope_component_name("tenant_id"); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("scope_current","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i23_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_scope_component_name_validator.py").read_text()
        for name in ("r8_v15_r1_any_scope_permission_validator","r8_v15_r1_aim_scope_policy_class_rule_validator"): self.assertNotIn(name,src)
    def test_i23_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice23.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE23-PREREGISTRATION.md","r8_v15_r1_scope_component_name_validator.py","test_r8_v15_r1_implementation_slice23.py","R8-V15-R1-IMPLEMENTATION-SLICE23-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
