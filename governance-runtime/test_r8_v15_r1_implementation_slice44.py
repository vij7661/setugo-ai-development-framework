import copy, importlib, itertools, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice44-srtt4-total-table-structural-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_srtt4_total_table_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
OLD=["NO_MATCH","EXACT_MATCH"]; DEST=["NO_MATCH","EXACT_MATCH","MAPPED_MATCH"]; EFFECT=["BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"]; REL=["SAME","NARROWER","BROADER","DISJOINT"]; BOOL=[False,True]
RESULTS=["SEMANTIC_SCOPE_REVOKED","SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED","MAPPING_NOT_APPLICABLE","REPLACEMENT_ELIGIBLE","SEMANTIC_SCOPE_REPLACEMENT_INVALID"]
DIST={"SEMANTIC_SCOPE_REVOKED":1808,"SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED":288,"MAPPING_NOT_APPLICABLE":144,"REPLACEMENT_ELIGIBLE":22,"SEMANTIC_SCOPE_REPLACEMENT_INVALID":42}
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def tuples():
    return itertools.product(OLD,DEST,EFFECT,REL,BOOL,BOOL,BOOL,BOOL,BOOL)
def make_rows():
    quotas=[]
    for r,c in DIST.items(): quotas += [r]*c
    out=[]
    for idx,t in enumerate(tuples(),1):
        old,dest,effect,rel,a,m,l,s,d=t
        out.append({"row_id":idx,"input":{"source_entry_state":"REVOKED","old_scope_match":old,"destination_scope_match":dest,"old_scope_effect":effect,"scope_relation":rel,"any_permission_valid":a,"mapping_effective":m,"lineage_mapping_valid":l,"scope_expansion_authorized":s,"decision_inside_authorized_expansion_domain":d},"result":quotas[idx-1],"decisive_rule_id":f"SRTT15-R{((idx-1)%11)+1:02d}"})
    return out
ROWS=make_rows()
def valid():
    return {"schema":"r8-v15-srtt-4-total-table/v1","status":"candidate","authority_effect":"NONE","generator_contract":"R8V15-I001..I007","rule_registry_path":"governance-r8/R8-V15-SRTT-4-RULE-REGISTRY.json","domain_fixed":{"source_entry_state":"REVOKED"},"enum_order":{"old_scope_match":OLD,"destination_scope_match":DEST,"old_scope_effect":EFFECT,"scope_relation":REL,"any_permission_valid":BOOL,"mapping_effective":BOOL,"lineage_mapping_valid":BOOL,"scope_expansion_authorized":BOOL,"decision_inside_authorized_expansion_domain":BOOL},"row_count":2304,"distribution":dict(DIST),"verification":{"expected_row_count":2304,"generated_row_count":2304,"every_row_has_declared_rule":True,"generation_conflicts":0},"rows":copy.deepcopy(ROWS)}
class Slice44FrozenAcceptance(unittest.TestCase):
    def test_i44_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"srtt-4-total-table.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS)
    def test_i44_02_valid_passes(self): self.assertTrue(require().validate_srtt4_total_table(valid())["locally_valid"])
    def test_i44_03_root_consts_shape(self):
        m=require(); x=valid(); x["generator_contract"]="bad"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_04_enum_order_exact(self):
        m=require(); x=valid(); x["enum_order"]["old_scope_match"]=list(reversed(OLD))
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_05_row_count_exact2304(self):
        m=require(); x=valid(); x["rows"]=x["rows"][:-1]
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_06_row_shape_id_range(self):
        m=require(); x=valid(); x["rows"][0]["extra"]=1
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
        x=valid(); x["rows"][0]["row_id"]=True
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_07_row_ids_unique_contiguous(self):
        m=require(); x=valid(); x["rows"][-1]["row_id"]=1
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_08_input_shape_enum_bool(self):
        m=require(); x=valid(); x["rows"][0]["input"]["old_scope_match"]="BAD"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
        x=valid(); x["rows"][0]["input"]["any_permission_valid"]=1
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_09_cartesian_domain_unique_complete(self):
        m=require(); x=valid(); x["rows"][-1]["input"]=copy.deepcopy(x["rows"][0]["input"])
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_10_result_enum_and_distribution(self):
        m=require(); x=valid(); x["rows"][0]["result"]="BAD"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
        x=valid(); x["rows"][0]["result"]="REPLACEMENT_ELIGIBLE"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_11_decisive_rule_pattern(self):
        m=require(); x=valid(); x["rows"][0]["decisive_rule_id"]="SRTT15-R00"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
        x=valid(); x["rows"][0]["decisive_rule_id"]="SRTT15-R٠1"
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_12_verification_consts(self):
        m=require(); x=valid(); x["verification"]["every_row_has_declared_rule"]=1
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(x)
    def test_i44_13_no_rule_membership_or_semantic_recompute(self):
        r=require().validate_srtt4_total_table(valid()); self.assertFalse(r["decisive_rule_registry_membership_verified"]); self.assertFalse(r["decision_semantics_recomputed"])
    def test_i44_14_non_authority(self):
        r=require().validate_srtt4_total_table(valid()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["replacement_authority_granted"]); self.assertFalse(r["terminal_authority"])
    def test_i44_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["rows"]=[]
        with self.assertRaises(m.SRTT4TotalTableError): m.validate_srtt4_total_table(bad)
        self.assertTrue(m.validate_srtt4_total_table(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_srtt4_total_table_validator.py").read_text(); self.assertNotIn("r8_v15_r1_srtt4_rule_registry_validator",src)
    def test_i44_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice44.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE44-PREREGISTRATION.md","r8_v15_r1_srtt4_total_table_validator.py","test_r8_v15_r1_implementation_slice44.py","R8-V15-R1-IMPLEMENTATION-SLICE44-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
