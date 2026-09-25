import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice26-aim-scope-policy-local-2026-09-25"; INT64_MAX=9223372036854775807
NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_aim_scope_policy_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def rule(sc="class:1", comps=None): return {"semantic_class":sc,"allowed_any_tuple_components":["tenant_id"] if comps is None else comps}
def valid(): return {"aim_scope_policy_id":"policy:1","class_rules":[rule()],"effective_sequence":0,"lifecycle_state":"ACTIVE","constitutional_authority_evidence_digest":"constitutional:digest","policy_digest":"policy:digest"}
class Slice26FrozenAcceptance(unittest.TestCase):
    def test_i26_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["AIMScopePolicy"]
        self.assertEqual(set(d["required"]),set(m.FIELDS)); self.assertEqual(d["properties"]["class_rules"]["minItems"],1)
    def test_i26_02_valid_passes(self): self.assertTrue(require().validate_aim_scope_policy(valid())["locally_valid"])
    def test_i26_03_top_level_shape(self):
        m=require()
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy([])
        x=valid(); x.pop("policy_digest")
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_04_string_rules(self):
        m=require()
        for f,b in (("aim_scope_policy_id",True),("policy_digest",""),("constitutional_authority_evidence_digest","e\u0301"),("policy_digest","\ufdd0")):
            x=valid(); x[f]=b
            with self.subTest(f=f,b=repr(b)):
                with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_05_class_rules_list_min1(self):
        m=require()
        for b in (None,{},(), "x", []):
            x=valid(); x["class_rules"]=b
            with self.subTest(b=repr(b)):
                with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_06_rule_exact_fields(self):
        m=require(); x=valid(); x["class_rules"]=[{"semantic_class":"x"}]
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
        x=valid(); x["class_rules"]=[{"semantic_class":"x","allowed_any_tuple_components":[],"extra":1}]
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_07_nested_semantic_class(self):
        m=require()
        for b in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["class_rules"]=[rule(b)]
            with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_08_nested_components(self):
        m=require(); x=valid(); x["class_rules"]=[rule("c",list(NAMES))]; self.assertTrue(m.validate_aim_scope_policy(x)["locally_valid"])
        for b in ("bad","Tenant_Id",True,1):
            x=valid(); x["class_rules"]=[rule("c",[b])]
            with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_09_nested_component_duplicates(self):
        m=require(); x=valid(); x["class_rules"]=[rule("c",["tenant_id","tenant_id"])]
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_10_semantic_class_unique(self):
        m=require(); x=valid(); x["class_rules"]=[rule("same"),rule("same",["project_id"])]
        with self.assertRaises(m.AIMScopePolicyError) as cm: m.validate_aim_scope_policy(x)
        self.assertEqual(cm.exception.code,"AIM_SCOPE_POLICY_CLASS_NOT_UNIQUE")
    def test_i26_11_sequence(self):
        m=require()
        for g in (0,INT64_MAX):
            x=valid(); x["effective_sequence"]=g; self.assertTrue(m.validate_aim_scope_policy(x)["locally_valid"])
        for b in (-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["effective_sequence"]=b
            with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_12_lifecycle(self):
        m=require()
        for g in ("ACTIVE","SUSPENDED","RETIRED","REVOKED"):
            x=valid(); x["lifecycle_state"]=g; self.assertTrue(m.validate_aim_scope_policy(x)["locally_valid"])
        x=valid(); x["lifecycle_state"]="BAD"
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(x)
    def test_i26_13_opaque_digests(self):
        m=require(); x=valid(); x["policy_digest"]="not-a-sha"; x["constitutional_authority_evidence_digest"]="opaque"; self.assertTrue(m.validate_aim_scope_policy(x)["locally_valid"])
    def test_i26_14_no_currentness_or_authority(self):
        r=require().validate_aim_scope_policy(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("policy_current","policy_effective","constitutional_evidence_verified","anti_broadening_enforced","any_permission_authorized","semantic_selected","scope_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i26_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["effective_sequence"]=-1
        with self.assertRaises(m.AIMScopePolicyError): m.validate_aim_scope_policy(bad)
        self.assertTrue(m.validate_aim_scope_policy(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_aim_scope_policy_validator.py").read_text()
        for name in ("r8_v15_r1_aim_scope_policy_class_rule_validator","r8_v15_r1_any_scope_permission_validator"): self.assertNotIn(name,src)
    def test_i26_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice26.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE26-PREREGISTRATION.md","r8_v15_r1_aim_scope_policy_validator.py","test_r8_v15_r1_implementation_slice26.py","R8-V15-R1-IMPLEMENTATION-SLICE26-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
