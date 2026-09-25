import importlib, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice27-scope-replacement-mapping-local-2026-09-25"; INT64_MAX=9223372036854775807
FIELDS=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_scope_replacement_mapping_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def scope(v="scope:1"): return {k:v for k in FIELDS}
def valid(): return {"mapping_id":"map:1","semantic_input_id":"input:1","semantic_lineage_id":"lineage:1","revoked_entry_id":"entry:old","destination_entry_id":"entry:new","old_scope_tuple":scope(),"new_scope_tuple":scope("scope:2"),"old_specificity":1,"new_specificity":1,"old_scope_effect":"BLOCK_OLD_SCOPE","decision_scope_match_rule_id":"rule:1","effective_sequence":0,"constitutional_amendment_evidence_digest":"constitutional:digest","lifecycle_state":"ACTIVE","mapping_digest":"mapping:digest"}
class Slice27FrozenAcceptance(unittest.TestCase):
    def test_i27_01_field_parity(self): self.assertEqual(set(require().FIELDS),set(valid().keys()))
    def test_i27_02_valid_passes(self): self.assertTrue(require().validate_scope_replacement_mapping(valid())["locally_valid"])
    def test_i27_03_top_level_shape(self):
        m=require()
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping([])
        x=valid(); x.pop("mapping_digest")
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_04_string_rules(self):
        m=require()
        for f,b in (("mapping_id",True),("semantic_input_id",""),("mapping_digest","e\u0301"),("constitutional_amendment_evidence_digest","\ufdd0")):
            x=valid(); x[f]=b
            with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_05_scope_tuple_shape(self):
        m=require()
        for f in ("old_scope_tuple","new_scope_tuple"):
            x=valid(); x[f]=[] 
            with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
            x=valid(); x[f]=scope(); x[f].pop("tenant_id")
            with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_06_any_and_stable_components(self):
        m=require(); x=valid(); x["old_scope_tuple"]=scope("ANY"); x["new_scope_tuple"]=scope("stable:x"); self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
    def test_i27_07_leading_line_terminators_reject(self):
        m=require()
        for tf in ("old_scope_tuple","new_scope_tuple"):
            for field in FIELDS:
                for bad in ("\nvalue","\rvalue","\u2028value","\u2029value"):
                    x=valid(); x[tf]=scope(); x[tf][field]=bad
                    with self.subTest(tf=tf,field=field,bad=repr(bad)):
                        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
        x=valid(); x["old_scope_tuple"]["tenant_id"]="x\n"; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
    def test_i27_08_scope_component_invalids(self):
        m=require()
        for bad in ("",True,"e\u0301","\ufdd0"):
            x=valid(); x["old_scope_tuple"]["tenant_id"]=bad
            with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_09_specificity(self):
        m=require()
        for f in ("old_specificity","new_specificity"):
            for g in (0,9):
                x=valid(); x[f]=g; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
            for b in (-1,10,True,1.5,"1"):
                x=valid(); x[f]=b
                with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_10_old_scope_effect(self):
        m=require()
        for g in ("BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"):
            x=valid(); x["old_scope_effect"]=g; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
        x=valid(); x["old_scope_effect"]="BAD"
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_11_sequence(self):
        m=require()
        for g in (0,INT64_MAX):
            x=valid(); x["effective_sequence"]=g; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
        for b in (-1,INT64_MAX+1,True,"1"):
            x=valid(); x["effective_sequence"]=b
            with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_12_lifecycle(self):
        m=require()
        for g in ("ACTIVE","SUSPENDED","RETIRED","REVOKED"):
            x=valid(); x["lifecycle_state"]=g; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
        x=valid(); x["lifecycle_state"]="BAD"
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(x)
    def test_i27_13_opaque_digests(self):
        m=require(); x=valid(); x["mapping_digest"]="opaque"; x["constitutional_amendment_evidence_digest"]="not-a-sha"; self.assertTrue(m.validate_scope_replacement_mapping(x)["locally_valid"])
    def test_i27_14_no_effectiveness_or_authority(self):
        r=require().validate_scope_replacement_mapping(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("objects_exist_verified","specificity_matches_scope","scope_relation_verified","mapping_current","mapping_effective","constitutional_amendment_verified","replacement_authorized","semantic_selected","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i27_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["old_specificity"]=-1
        with self.assertRaises(m.ScopeReplacementMappingError): m.validate_scope_replacement_mapping(bad)
        self.assertTrue(m.validate_scope_replacement_mapping(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_scope_replacement_mapping_validator.py").read_text()
        for name in ("r8_v15_r1_canonical_scope_tuple_validator","r8_v15_r1_scope_component_validator"): self.assertNotIn(name,src)
    def test_i27_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice27.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE27-PREREGISTRATION.md","r8_v15_r1_scope_replacement_mapping_validator.py","test_r8_v15_r1_implementation_slice27.py","R8-V15-R1-IMPLEMENTATION-SLICE27-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
