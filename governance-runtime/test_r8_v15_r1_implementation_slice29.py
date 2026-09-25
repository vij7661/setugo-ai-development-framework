import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice29-review-field-rule-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_review_field_rule_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid():
    return {"field_id":"field:1","classification":"REVIEW_SEMANTIC","conditions":[],"source_rules":["R1"]}
class Slice29FrozenAcceptance(unittest.TestCase):
    def test_i29_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"review-presentation-schema.schema.json").read_text())["$defs"]["FieldRule"]
        self.assertEqual(tuple(d["required"]),m.FIELDS); self.assertEqual(tuple(d["properties"]["classification"]["enum"]),m.CLASSIFICATIONS)
    def test_i29_02_valid_passes(self): self.assertTrue(require().validate_review_field_rule(valid())["locally_valid"])
    def test_i29_03_shape_rejects(self):
        m=require()
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule([])
        x=valid(); x.pop("field_id")
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_04_field_id_rules(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["field_id"]=bad
            with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_05_classification_enum(self):
        m=require()
        for good in ("REVIEW_SEMANTIC","DISPLAY_NON_SEMANTIC"):
            x=valid(); x["classification"]=good; self.assertTrue(m.validate_review_field_rule(x)["locally_valid"])
        x=valid(); x["classification"]="BAD"
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_06_conditions_empty_allowed(self):
        m=require(); x=valid(); x["conditions"]=[]; self.assertTrue(m.validate_review_field_rule(x)["locally_valid"])
    def test_i29_07_conditions_list_and_items(self):
        m=require()
        for bad in (None,{},"x"):
            x=valid(); x["conditions"]=bad
            with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
        for bad in ("",True,"e\u0301","\ufdd0"):
            x=valid(); x["conditions"]=[bad]
            with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_08_source_rules_min1(self):
        m=require()
        for bad in ([],None,{},"R1"):
            x=valid(); x["source_rules"]=bad
            with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_09_source_rule_items(self):
        m=require()
        for bad in ("",True,"e\u0301","\ufdd0"):
            x=valid(); x["source_rules"]=[bad]
            with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_10_source_rules_unique(self):
        m=require(); x=valid(); x["source_rules"]=["R1","R1"]
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(x)
    def test_i29_11_opaque_strings_pass(self):
        m=require(); x=valid(); x["field_id"]="x:y/z"; x["conditions"]=["a b"]; x["source_rules"]=["NORM-001"]; self.assertTrue(m.validate_review_field_rule(x)["locally_valid"])
    def test_i29_12_deterministic(self):
        m=require(); self.assertEqual(m.validate_review_field_rule(valid()),m.validate_review_field_rule(valid()))
    def test_i29_13_nonpoison(self):
        m=require(); bad=valid(); bad["classification"]="BAD"
        with self.assertRaises(m.ReviewFieldRuleError): m.validate_review_field_rule(bad)
        self.assertTrue(m.validate_review_field_rule(valid())["locally_valid"])
    def test_i29_14_non_authority(self):
        r=require().validate_review_field_rule(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("review_materiality_verified","reviewer_influence_verified","packet_semantics_verified","review_authority_granted","runtime_qualified","terminal_authority"): self.assertFalse(r[k],k)
    def test_i29_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_review_field_rule_validator.py").read_text()
        for name in ("r8_v15_r1_review_packet_type_validator","r8_v15_r1_review_presentation_schema_validator"): self.assertNotIn(name,src)
    def test_i29_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice29.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE29-PREREGISTRATION.md","r8_v15_r1_review_field_rule_validator.py","test_r8_v15_r1_implementation_slice29.py","R8-V15-R1-IMPLEMENTATION-SLICE29-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
