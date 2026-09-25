import copy, importlib, itertools, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice43-srtt4-rule-registry-structural-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_srtt4_rule_registry_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
RESULTS=["SEMANTIC_SCOPE_REVOKED","SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED","MAPPING_NOT_APPLICABLE","REPLACEMENT_ELIGIBLE","SEMANTIC_SCOPE_REPLACEMENT_INVALID"]
def rule(i): return {"rule_id":f"SRTT15-R{i:02d}","precedence":i,"predicate":f"p{i}","result":RESULTS[(i-1)%len(RESULTS)],"source_trace":["NORM-027"]}
def valid():
    return {"schema":"r8-v15-srtt-4-rule-registry/v1","status":"candidate","authority_effect":"NONE","domain_fixed":{"source_entry_state":"REVOKED"},"outside_table_rule":{"rule_id":"SRTT15-R00","predicate":"outside","result":"NOT_A_REPLACEMENT_BRANCH","source_trace":["NORM-027"]},"rules":[rule(i) for i in range(1,12)]}
class Slice43FrozenAcceptance(unittest.TestCase):
    def test_i43_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"srtt-4-rule-registry.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS)
    def test_i43_02_valid_passes(self): self.assertTrue(require().validate_srtt4_rule_registry(valid())["locally_valid"])
    def test_i43_03_root_shape(self):
        m=require()
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry([])
        x=valid(); x["extra"]=1
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_04_domain_fixed(self):
        m=require(); x=valid(); x["domain_fixed"]["source_entry_state"]="ACTIVE"
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_05_outside_rule_exact(self):
        m=require()
        for f,bad in (("rule_id","SRTT15-R01"),("result","REPLACEMENT_ELIGIBLE")):
            x=valid(); x["outside_table_rule"][f]=bad
            with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_06_rule_count_exact11(self):
        m=require(); x=valid(); x["rules"]=x["rules"][:-1]
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_07_rule_id_ascii_pattern(self):
        m=require()
        for bad in ("SRTT15-R00","SRTT15-R12","SRTT15-R٠1"):
            x=valid(); x["rules"][0]["rule_id"]=bad
            with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_08_rule_id_closure_unique(self):
        m=require(); x=valid(); x["rules"][10]["rule_id"]="SRTT15-R01"
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_09_precedence_integer_range(self):
        m=require()
        for bad in (True,0,12,"1"):
            x=valid(); x["rules"][0]["precedence"]=bad
            with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_10_precedence_closure_unique(self):
        m=require(); x=valid(); x["rules"][10]["precedence"]=1
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_11_predicate_and_source_trace(self):
        m=require(); x=valid(); x["rules"][0]["predicate"]=""
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
        x=valid(); x["rules"][0]["source_trace"]=[]
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_12_result_enum(self):
        m=require(); x=valid(); x["rules"][0]["result"]="BAD"
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(x)
    def test_i43_13_predicates_not_executed(self):
        r=require().validate_srtt4_rule_registry(valid()); self.assertFalse(r["predicate_semantics_verified"]); self.assertFalse(r["decision_recomputation_performed"])
    def test_i43_14_non_authority(self):
        r=require().validate_srtt4_rule_registry(valid()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["replacement_authority_granted"]); self.assertFalse(r["terminal_authority"])
    def test_i43_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["rules"]=[]
        with self.assertRaises(m.SRTT4RuleRegistryError): m.validate_srtt4_rule_registry(bad)
        self.assertTrue(m.validate_srtt4_rule_registry(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_srtt4_rule_registry_validator.py").read_text(); self.assertNotIn("r8_v15_r1_srtt4_total_table_validator",src)
    def test_i43_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice43.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE43-PREREGISTRATION.md","r8_v15_r1_srtt4_rule_registry_validator.py","test_r8_v15_r1_implementation_slice43.py","R8-V15-R1-IMPLEMENTATION-SLICE43-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
