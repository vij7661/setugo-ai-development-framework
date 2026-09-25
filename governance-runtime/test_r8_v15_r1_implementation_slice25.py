import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice25-aim-scope-policy-class-rule-local-2026-09-25"
NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_aim_scope_policy_class_rule_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid(): return {"semantic_class":"class:1","allowed_any_tuple_components":["tenant_id"]}
class Slice25FrozenAcceptance(unittest.TestCase):
    def test_i25_01_field_parity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["AIMScopePolicyClassRule"]
        self.assertEqual(set(d["required"]),set(m.AIM_SCOPE_POLICY_CLASS_RULE_FIELDS)); self.assertEqual(len(d["required"]),len(m.AIM_SCOPE_POLICY_CLASS_RULE_FIELDS))
    def test_i25_02_valid_rule_passes(self): self.assertTrue(require().validate_aim_scope_policy_class_rule(valid())["locally_valid"])
    def test_i25_03_mapping_missing_extra_reject(self):
        m=require()
        with self.assertRaises(m.AIMScopePolicyClassRuleError):m.validate_aim_scope_policy_class_rule([])
        x=valid(); x.pop("semantic_class")
        with self.assertRaises(m.AIMScopePolicyClassRuleError):m.validate_aim_scope_policy_class_rule(x)
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.AIMScopePolicyClassRuleError):m.validate_aim_scope_policy_class_rule(x)
    def test_i25_04_semantic_class_string_rules(self):
        m=require()
        for bad,code in ((True,"AIM_SCOPE_CLASS_STRING_INVALID"),("","AIM_SCOPE_CLASS_STRING_INVALID"),("e\u0301","AIM_SCOPE_CLASS_GCP_INVALID"),("\ufdd0","AIM_SCOPE_CLASS_GCP_INVALID")):
            x=valid(); x["semantic_class"]=bad
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.AIMScopePolicyClassRuleError) as cm:m.validate_aim_scope_policy_class_rule(x)
                self.assertEqual(cm.exception.code,code)
    def test_i25_05_components_list_and_empty_allowed(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=[]; self.assertTrue(m.validate_aim_scope_policy_class_rule(x)["locally_valid"])
        for bad in (None,"tenant_id",("tenant_id",),{}):
            x=valid(); x["allowed_any_tuple_components"]=bad
            with self.assertRaises(m.AIMScopePolicyClassRuleError) as cm:m.validate_aim_scope_policy_class_rule(x)
            self.assertEqual(cm.exception.code,"AIM_SCOPE_CLASS_COMPONENTS_INVALID")
    def test_i25_06_exact_component_name_elements(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=list(NAMES); self.assertTrue(m.validate_aim_scope_policy_class_rule(x)["locally_valid"])
    def test_i25_07_duplicates_reject(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=["tenant_id","tenant_id"]
        with self.assertRaises(m.AIMScopePolicyClassRuleError) as cm:m.validate_aim_scope_policy_class_rule(x)
        self.assertEqual(cm.exception.code,"AIM_SCOPE_CLASS_COMPONENTS_NOT_UNIQUE")
    def test_i25_08_all_nine_can_coexist(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=list(NAMES); self.assertEqual(m.validate_aim_scope_policy_class_rule(x)["component_count"],9)
    def test_i25_09_unknown_case_spaced_reject(self):
        m=require()
        for bad in ("unknown","Tenant_Id","tenant_id "):
            x=valid(); x["allowed_any_tuple_components"]=[bad]
            with self.assertRaises(m.AIMScopePolicyClassRuleError) as cm:m.validate_aim_scope_policy_class_rule(x)
            self.assertEqual(cm.exception.code,"AIM_SCOPE_CLASS_COMPONENT_NAME_INVALID")
    def test_i25_10_boolean_numeric_elements_reject(self):
        m=require()
        for bad in (True,False,1,1.5):
            x=valid(); x["allowed_any_tuple_components"]=[bad]
            with self.assertRaises(m.AIMScopePolicyClassRuleError) as cm:m.validate_aim_scope_policy_class_rule(x)
            self.assertEqual(cm.exception.code,"AIM_SCOPE_CLASS_COMPONENT_NAME_INVALID")
    def test_i25_11_no_policy_currentness_inferred(self):
        r=require().validate_aim_scope_policy_class_rule(valid()); self.assertFalse(r["aim_policy_current"]); self.assertFalse(r["any_permission_authorized"])
    def test_i25_12_deterministic(self):
        m=require(); self.assertEqual(m.validate_aim_scope_policy_class_rule(valid()),m.validate_aim_scope_policy_class_rule(valid()))
    def test_i25_13_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["allowed_any_tuple_components"]=["bad"]
        with self.assertRaises(m.AIMScopePolicyClassRuleError):m.validate_aim_scope_policy_class_rule(bad)
        self.assertTrue(m.validate_aim_scope_policy_class_rule(valid())["locally_valid"])
    def test_i25_14_non_authority_metadata(self):
        r=require().validate_aim_scope_policy_class_rule(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("semantic_selected","scope_authorized","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i25_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_aim_scope_policy_class_rule_validator.py").read_text()
        for name in ("r8_v15_r1_scope_component_name_validator","r8_v15_r1_any_scope_permission_validator"): self.assertNotIn(name,src)
    def test_i25_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice25.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE25-PREREGISTRATION.md","r8_v15_r1_aim_scope_policy_class_rule_validator.py","test_r8_v15_r1_implementation_slice25.py","R8-V15-R1-IMPLEMENTATION-SLICE25-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
