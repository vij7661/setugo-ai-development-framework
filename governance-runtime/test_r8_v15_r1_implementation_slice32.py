import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice32-bsp5-grammar-freeze-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_bsp5_grammar_freeze_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def frozen(): return json.loads((SCHEMA_DIR/"bsp-5-grammar.schema.json").read_text())["const"]
class Slice32FrozenAcceptance(unittest.TestCase):
    def test_i32_01_frozen_const_identity(self):
        m=require(); self.assertEqual(m.FROZEN_GRAMMAR,frozen())
    def test_i32_02_exact_passes(self): self.assertTrue(require().validate_bsp5_grammar_freeze(frozen())["locally_valid"])
    def test_i32_03_non_mapping_rejects(self):
        m=require()
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze([])
    def test_i32_04_missing_top_field_rejects(self):
        m=require(); x=frozen(); x.pop("patterns")
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_05_extra_top_field_rejects(self):
        m=require(); x=frozen(); x["extra"]=1
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_06_nested_mutation_rejects(self):
        m=require(); x=frozen(); x["current_status_binding"]["exact_block_count"]=2
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_07_list_reorder_rejects(self):
        m=require(); x=frozen(); x["parser_states"]=list(reversed(x["parser_states"]))
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_08_version_mutation_rejects(self):
        m=require(); x=frozen(); x["current_candidate_version"]=14
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_09_status_authority_mutation_rejects(self):
        m=require()
        for f,b in (("status","OTHER"),("authority_effect","SOME")):
            x=frozen(); x[f]=b
            with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_10_pattern_mutation_rejects(self):
        m=require(); x=frozen(); x["patterns"]["status_header"]="bad"
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_11_json_type_fidelity(self):
        m=require(); x=frozen(); x["current_status_binding"]["exact_block_count"]=True
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(x)
    def test_i32_12_object_key_order_irrelevant(self):
        m=require(); x=frozen(); y={k:x[k] for k in reversed(list(x.keys()))}
        self.assertTrue(m.validate_bsp5_grammar_freeze(y)["locally_valid"])
    def test_i32_13_no_parser_execution(self):
        r=require().validate_bsp5_grammar_freeze(frozen())
        for k in ("parser_executed","classification_verified","residual_rule_verified","review_projection_verified"): self.assertFalse(r[k],k)
    def test_i32_14_non_authority(self):
        r=require().validate_bsp5_grammar_freeze(frozen()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["review_authority_granted"]); self.assertFalse(r["terminal_authority"])
    def test_i32_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=frozen(); bad["status"]="bad"
        with self.assertRaises(m.BSP5GrammarFreezeError): m.validate_bsp5_grammar_freeze(bad)
        self.assertTrue(m.validate_bsp5_grammar_freeze(frozen())["locally_valid"])
        src=(HERE/"r8_v15_r1_bsp5_grammar_freeze_validator.py").read_text()
        self.assertNotIn("r8_v15_r1_review_",src)
    def test_i32_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice32.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE32-PREREGISTRATION.md","r8_v15_r1_bsp5_grammar_freeze_validator.py","test_r8_v15_r1_implementation_slice32.py","R8-V15-R1-IMPLEMENTATION-SLICE32-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
