import importlib, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice28-scope-replacement-outside-table-input-local-2026-09-25"
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_scope_replacement_outside_table_input_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid(): return {"source_entry_state":"ACTIVE","old_scope_match":"NO_MATCH","destination_scope_match":"NO_MATCH","old_scope_effect":"BLOCK_OLD_SCOPE","scope_relation":"SAME","any_permission_valid":False,"mapping_effective":False,"lineage_mapping_valid":False,"scope_expansion_authorized":False,"decision_inside_authorized_expansion_domain":False}
class Slice28FrozenAcceptance(unittest.TestCase):
    def test_i28_01_field_parity(self): self.assertEqual(set(require().FIELDS),set(valid().keys()))
    def test_i28_02_valid_passes(self): self.assertTrue(require().validate_scope_replacement_outside_table_input(valid())["locally_valid"])
    def test_i28_03_top_level_shape(self):
        m=require()
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input([])
        x=valid(); x.pop("scope_relation")
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_04_source_state_enum(self):
        m=require()
        for g in ("ACTIVE","SUSPENDED","SUPERSEDED","RETIRED","SCOPE_PERMISSION_REEVALUATION_REQUIRED"):
            x=valid(); x["source_entry_state"]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
        x=valid(); x["source_entry_state"]="REVOKED"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_05_old_scope_match_enum(self):
        m=require()
        for g in ("NO_MATCH","EXACT_MATCH"):
            x=valid(); x["old_scope_match"]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
        x=valid(); x["old_scope_match"]="MAPPED_MATCH"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_06_destination_match_enum(self):
        m=require()
        for g in ("NO_MATCH","EXACT_MATCH","MAPPED_MATCH"):
            x=valid(); x["destination_scope_match"]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
        x=valid(); x["destination_scope_match"]="BAD"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_07_effect_enum(self):
        m=require()
        for g in ("BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"):
            x=valid(); x["old_scope_effect"]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
        x=valid(); x["old_scope_effect"]="BAD"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_08_relation_enum(self):
        m=require()
        for g in ("SAME","NARROWER","BROADER","DISJOINT"):
            x=valid(); x["scope_relation"]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
        x=valid(); x["scope_relation"]="BAD"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_09_strict_booleans(self):
        m=require(); fields=("any_permission_valid","mapping_effective","lineage_mapping_valid","scope_expansion_authorized","decision_inside_authorized_expansion_domain")
        for f in fields:
            for g in (True,False):
                x=valid(); x[f]=g; self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
            for b in (0,1,"true",None):
                x=valid(); x[f]=b
                with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(x)
    def test_i28_10_enum_cross_products_structural_only(self):
        m=require()
        for src in ("ACTIVE","SUPERSEDED"):
            for rel in ("SAME","BROADER"):
                x=valid(); x["source_entry_state"]=src; x["scope_relation"]=rel; x["scope_expansion_authorized"]=True
                self.assertTrue(m.validate_scope_replacement_outside_table_input(x)["locally_valid"])
    def test_i28_11_no_effectiveness_or_permission_inference(self):
        r=require().validate_scope_replacement_outside_table_input(valid()); self.assertFalse(r["mapping_effectiveness_verified"]); self.assertFalse(r["any_permission_verified"]); self.assertFalse(r["lineage_mapping_verified"])
    def test_i28_12_no_table_lookup_or_branch_result(self):
        r=require().validate_scope_replacement_outside_table_input(valid()); self.assertFalse(r["srtt_table_lookup_performed"]); self.assertFalse(r["not_a_replacement_branch_verified"])
    def test_i28_13_deterministic(self):
        m=require(); self.assertEqual(m.validate_scope_replacement_outside_table_input(valid()),m.validate_scope_replacement_outside_table_input(valid()))
    def test_i28_14_non_authority_metadata(self):
        r=require().validate_scope_replacement_outside_table_input(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("replacement_eligible","scope_expansion_verified","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i28_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["scope_relation"]="BAD"
        with self.assertRaises(m.ScopeReplacementOutsideTableInputError): m.validate_scope_replacement_outside_table_input(bad)
        self.assertTrue(m.validate_scope_replacement_outside_table_input(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_scope_replacement_outside_table_input_validator.py").read_text()
        for name in ("r8_v15_r1_scope_replacement_mapping_validator","r8_v15_r1_canonical_scope_tuple_validator"): self.assertNotIn(name,src)
    def test_i28_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice28.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE28-PREREGISTRATION.md","r8_v15_r1_scope_replacement_outside_table_input_validator.py","test_r8_v15_r1_implementation_slice28.py","R8-V15-R1-IMPLEMENTATION-SLICE28-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
