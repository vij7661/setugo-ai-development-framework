import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice17-semantic-entry-local-2026-09-25"
INT64_MAX=9223372036854775807
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_semantic_entry_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def scope():
    return {
      "trust_domain_id":"trust:1",
      "constitution_id":"constitution:1",
      "root_namespace":"root",
      "tenant_id":"tenant:1",
      "organization_id":"org:1",
      "project_id":"project:1",
      "experiment_or_release_id":"release:1",
      "object_class":"object:1",
      "action_class":"action:1"
    }

def valid():
    return {
      "semantic_entry_id":"entry:1",
      "semantic_input_id":"input:1",
      "semantic_lineage_id":"lineage:1",
      "semantic_version":"v1",
      "scope_tuple":scope(),
      "specificity_score":9,
      "lifecycle_state":"ACTIVE",
      "predecessor_entry_id":None,
      "successor_of_entry_id":None,
      "scope_replacement_mapping_id":None,
      "lineage_mapping_id":None,
      "any_scope_permission_id":None,
      "semantic_class":"class:1",
      "artifact_or_rule_digest":"artifact:digest",
      "schema_version":"schema:v1",
      "source_authority_digest":"source:digest",
      "effective_sequence":0,
      "constitutional_binding_digest":None,
      "semantic_entry_key":"entry:key"
    }

class Slice17FrozenAcceptance(unittest.TestCase):
    def test_i17_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["SemanticEntry"]["required"]
        self.assertEqual(set(req),set(m.SEMANTIC_ENTRY_FIELDS)); self.assertEqual(len(req),len(m.SEMANTIC_ENTRY_FIELDS))
    def test_i17_02_valid_structural_entry_passes(self):
        self.assertTrue(require().validate_semantic_entry(valid())["locally_valid"])
    def test_i17_03_top_level_mapping_and_field_closure(self):
        m=require()
        with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry([])
        self.assertEqual(cm.exception.code,"SEMANTIC_ENTRY_FIELD_SET_INVALID")
        x=valid(); x.pop("semantic_entry_id")
        with self.assertRaises(m.SemanticEntryError) as cm2:m.validate_semantic_entry(x)
        self.assertEqual(cm2.exception.code,"SEMANTIC_ENTRY_FIELD_SET_INVALID")
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.SemanticEntryError) as cm3:m.validate_semantic_entry(x)
        self.assertEqual(cm3.exception.code,"SEMANTIC_ENTRY_FIELD_SET_INVALID")
    def test_i17_04_required_scalar_string_rules(self):
        m=require()
        cases=(("semantic_entry_id",1,"SEMANTIC_ENTRY_STRING_INVALID"),("semantic_class","","SEMANTIC_ENTRY_STRING_INVALID"),("schema_version","e\u0301","SEMANTIC_ENTRY_GCP_STRING_INVALID"),("source_authority_digest","\ufdd0","SEMANTIC_ENTRY_GCP_STRING_INVALID"))
        for field,bad,code in cases:
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                self.assertEqual(cm.exception.code,code)
    def test_i17_05_scope_tuple_exact_shape_and_mapping(self):
        m=require(); x=valid(); x["scope_tuple"]=[]
        with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
        self.assertEqual(cm.exception.code,"SEMANTIC_ENTRY_SCOPE_FIELD_SET_INVALID")
        x=valid(); x["scope_tuple"].pop("action_class")
        with self.assertRaises(m.SemanticEntryError) as cm2:m.validate_semantic_entry(x)
        self.assertEqual(cm2.exception.code,"SEMANTIC_ENTRY_SCOPE_FIELD_SET_INVALID")
        x=valid(); x["scope_tuple"]["extra"]="x"
        with self.assertRaises(m.SemanticEntryError) as cm3:m.validate_semantic_entry(x)
        self.assertEqual(cm3.exception.code,"SEMANTIC_ENTRY_SCOPE_FIELD_SET_INVALID")
    def test_i17_06_scope_components_any_or_stable_value(self):
        m=require(); x=valid(); x["scope_tuple"]["tenant_id"]="ANY"
        self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
        x=valid(); x["scope_tuple"]["tenant_id"]="stable tenant value"
        self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
    def test_i17_07_invalid_scope_components_reject(self):
        m=require()
        for bad,code in ((1,"SEMANTIC_ENTRY_SCOPE_COMPONENT_INVALID"),("","SEMANTIC_ENTRY_SCOPE_COMPONENT_INVALID"),("e\u0301","SEMANTIC_ENTRY_SCOPE_COMPONENT_GCP_INVALID"),("\ufdd0","SEMANTIC_ENTRY_SCOPE_COMPONENT_GCP_INVALID")):
            x=valid(); x["scope_tuple"]["tenant_id"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                self.assertEqual(cm.exception.code,code)
    def test_i17_08_specificity_score_closure(self):
        m=require()
        for good in (0,9):
            x=valid(); x["specificity_score"]=good; self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
        for bad in (-1,10,True,"9",1.5):
            x=valid(); x["specificity_score"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                self.assertEqual(cm.exception.code,"SEMANTIC_ENTRY_SPECIFICITY_INVALID")
    def test_i17_09_lifecycle_enum_closure(self):
        m=require()
        for good in ("ACTIVE","SUSPENDED","REVOKED","SUPERSEDED","RETIRED","SCOPE_PERMISSION_REEVALUATION_REQUIRED"):
            x=valid(); x["lifecycle_state"]=good; self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
        for bad in ("UNKNOWN","",None,1):
            x=valid(); x["lifecycle_state"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                self.assertEqual(cm.exception.code,"SEMANTIC_ENTRY_LIFECYCLE_INVALID")
    def test_i17_10_nullable_string_fields(self):
        m=require(); fields=("predecessor_entry_id","successor_of_entry_id","scope_replacement_mapping_id","lineage_mapping_id","any_scope_permission_id","constitutional_binding_digest")
        for field in fields:
            x=valid(); x[field]=None; self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
            x=valid(); x[field]="opaque:value"; self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
            for bad,code in (("","SEMANTIC_ENTRY_NULLABLE_STRING_INVALID"),(1,"SEMANTIC_ENTRY_NULLABLE_STRING_INVALID"),("e\u0301","SEMANTIC_ENTRY_GCP_STRING_INVALID"),("\ufdd0","SEMANTIC_ENTRY_GCP_STRING_INVALID")):
                x=valid(); x[field]=bad
                with self.subTest(field=field,bad=bad):
                    with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                    self.assertEqual(cm.exception.code,code)
    def test_i17_11_effective_sequence_closure(self):
        m=require()
        for good in (0,INT64_MAX):
            x=valid(); x["effective_sequence"]=good; self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
        for bad in (-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["effective_sequence"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SemanticEntryError) as cm:m.validate_semantic_entry(x)
                self.assertEqual(cm.exception.code,"SEMANTIC_ENTRY_SEQUENCE_INVALID")
    def test_i17_12_opaque_non_sha_digests_and_key_pass(self):
        m=require(); x=valid(); x["artifact_or_rule_digest"]="not-a-sha"; x["source_authority_digest"]="opaque"; x["semantic_entry_key"]="also-not-sha"
        self.assertTrue(m.validate_semantic_entry(x)["locally_valid"])
    def test_i17_13_specificity_mismatch_structurally_accepts(self):
        m=require(); x=valid(); x["scope_tuple"]["tenant_id"]="ANY"; x["specificity_score"]=9
        r=m.validate_semantic_entry(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["specificity_verified"])
    def test_i17_14_semantic_invariants_and_authority_false(self):
        m=require(); x=valid(); x["scope_tuple"]["tenant_id"]="ANY"; x["any_scope_permission_id"]=None
        r=m.validate_semantic_entry(x); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("semantic_entry_key_verified","any_scope_permission_verified","entry_current","semantic_selected","lineage_transition_authorized","scope_transition_authorized","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)
    def test_i17_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["specificity_score"]=10
        with self.assertRaises(m.SemanticEntryError):m.validate_semantic_entry(bad)
        self.assertEqual(m.validate_semantic_entry(valid()),m.validate_semantic_entry(valid()))
    def test_i17_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice17.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-PREREGISTRATION.md","governance-runtime/r8_v15_r1_semantic_entry_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice17.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice17.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH14-16-CLOSURE.json"):
            self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
