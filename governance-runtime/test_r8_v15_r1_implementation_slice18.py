import importlib, json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice18-semantic-lineage-mapping-local-2026-09-25"
INT64_MAX=9223372036854775807
sys.path.insert(0,str(HERE))
try:
    mod=importlib.import_module("r8_v15_r1_semantic_lineage_mapping_validator"); IMPORT_ERROR=None
except Exception as exc:
    mod=None; IMPORT_ERROR=exc

def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod

def scope(prefix):
    return {
      "trust_domain_id":f"{prefix}:trust","constitution_id":f"{prefix}:constitution",
      "root_namespace":f"{prefix}:root","tenant_id":f"{prefix}:tenant",
      "organization_id":f"{prefix}:org","project_id":f"{prefix}:project",
      "experiment_or_release_id":f"{prefix}:release","object_class":f"{prefix}:object",
      "action_class":f"{prefix}:action"
    }

def valid():
    return {
      "mapping_id":"mapping:1","semantic_input_id":"input:1","source_lineage_id":"lineage:source",
      "destination_lineage_id":"lineage:destination","source_entry_id":"entry:source",
      "destination_entry_id":"entry:destination","source_scope_tuple":scope("source"),
      "destination_scope_tuple":scope("destination"),"transition_semantics_digest":"transition:digest",
      "constitutional_evidence_digest":"constitutional:digest","effective_sequence":0,
      "lifecycle_state":"ACTIVE","mapping_digest":"mapping:digest"
    }

class Slice18FrozenAcceptance(unittest.TestCase):
    def test_i18_01_fields_match_schema(self):
        m=require(); schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["SemanticLineageMapping"]["required"]
        self.assertEqual(set(req),set(m.SEMANTIC_LINEAGE_MAPPING_FIELDS)); self.assertEqual(len(req),len(m.SEMANTIC_LINEAGE_MAPPING_FIELDS))
    def test_i18_02_valid_structural_mapping_passes(self):
        self.assertTrue(require().validate_semantic_lineage_mapping(valid())["locally_valid"])
    def test_i18_03_top_level_mapping_and_field_closure(self):
        m=require()
        with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping([])
        self.assertEqual(cm.exception.code,"SEMANTIC_LINEAGE_FIELD_SET_INVALID")
        x=valid(); x.pop("mapping_id")
        with self.assertRaises(m.SemanticLineageMappingError) as cm2:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm2.exception.code,"SEMANTIC_LINEAGE_FIELD_SET_INVALID")
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.SemanticLineageMappingError) as cm3:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm3.exception.code,"SEMANTIC_LINEAGE_FIELD_SET_INVALID")
    def test_i18_04_scalar_string_rules(self):
        m=require()
        for field,bad,code in (("mapping_id",1,"SEMANTIC_LINEAGE_STRING_INVALID"),("semantic_input_id","","SEMANTIC_LINEAGE_STRING_INVALID"),("transition_semantics_digest","e\u0301","SEMANTIC_LINEAGE_GCP_STRING_INVALID"),("mapping_digest","\ufdd0","SEMANTIC_LINEAGE_GCP_STRING_INVALID")):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
                self.assertEqual(cm.exception.code,code)
    def test_i18_05_source_scope_exact_shape(self):
        m=require(); x=valid(); x["source_scope_tuple"]=[]
        with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm.exception.code,"SEMANTIC_LINEAGE_SOURCE_SCOPE_FIELD_SET_INVALID")
        x=valid(); x["source_scope_tuple"].pop("action_class")
        with self.assertRaises(m.SemanticLineageMappingError) as cm2:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm2.exception.code,"SEMANTIC_LINEAGE_SOURCE_SCOPE_FIELD_SET_INVALID")
    def test_i18_06_destination_scope_exact_shape(self):
        m=require(); x=valid(); x["destination_scope_tuple"]=[]
        with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm.exception.code,"SEMANTIC_LINEAGE_DEST_SCOPE_FIELD_SET_INVALID")
        x=valid(); x["destination_scope_tuple"]["extra"]="x"
        with self.assertRaises(m.SemanticLineageMappingError) as cm2:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm2.exception.code,"SEMANTIC_LINEAGE_DEST_SCOPE_FIELD_SET_INVALID")
    def test_i18_07_scope_component_rules(self):
        m=require()
        for key in ("source_scope_tuple","destination_scope_tuple"):
            x=valid(); x[key]["tenant_id"]="ANY"; self.assertTrue(m.validate_semantic_lineage_mapping(x)["locally_valid"])
            for bad,code in ((1,"SEMANTIC_LINEAGE_SCOPE_COMPONENT_INVALID"),("","SEMANTIC_LINEAGE_SCOPE_COMPONENT_INVALID"),("e\u0301","SEMANTIC_LINEAGE_SCOPE_COMPONENT_GCP_INVALID"),("\ufdd0","SEMANTIC_LINEAGE_SCOPE_COMPONENT_GCP_INVALID")):
                x=valid(); x[key]["tenant_id"]=bad
                with self.subTest(key=key,bad=bad):
                    with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
                    self.assertEqual(cm.exception.code,code)
    def test_i18_08_effective_sequence_closure(self):
        m=require()
        for good in (0,INT64_MAX):
            x=valid(); x["effective_sequence"]=good; self.assertTrue(m.validate_semantic_lineage_mapping(x)["locally_valid"])
        for bad in (-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["effective_sequence"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
                self.assertEqual(cm.exception.code,"SEMANTIC_LINEAGE_SEQUENCE_INVALID")
    def test_i18_09_lifecycle_enum_closure(self):
        m=require()
        for good in ("ACTIVE","SUSPENDED","RETIRED","REVOKED"):
            x=valid(); x["lifecycle_state"]=good; self.assertTrue(m.validate_semantic_lineage_mapping(x)["locally_valid"])
        x=valid(); x["lifecycle_state"]="UNKNOWN"
        with self.assertRaises(m.SemanticLineageMappingError) as cm:m.validate_semantic_lineage_mapping(x)
        self.assertEqual(cm.exception.code,"SEMANTIC_LINEAGE_LIFECYCLE_INVALID")
    def test_i18_10_opaque_non_sha_digests_pass(self):
        m=require(); x=valid(); x["transition_semantics_digest"]="not-a-sha"; x["constitutional_evidence_digest"]="opaque"; x["mapping_digest"]="also-not-sha"
        self.assertTrue(m.validate_semantic_lineage_mapping(x)["locally_valid"])
    def test_i18_11_no_source_destination_relation_invented(self):
        m=require(); x=valid()
        x["source_lineage_id"]=x["destination_lineage_id"]; x["source_entry_id"]=x["destination_entry_id"]; x["source_scope_tuple"]=x["destination_scope_tuple"].copy()
        r=m.validate_semantic_lineage_mapping(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["source_destination_relation_verified"])
    def test_i18_12_digests_remain_unverified(self):
        r=require().validate_semantic_lineage_mapping(valid())
        for k in ("transition_semantics_digest_verified","constitutional_evidence_digest_verified","mapping_digest_verified"): self.assertFalse(r[k],k)
    def test_i18_13_currentness_and_existence_unproven(self):
        r=require().validate_semantic_lineage_mapping(valid())
        for k in ("mapping_current","mapping_effective","source_entry_exists","destination_entry_exists","source_lineage_exists","destination_lineage_exists"): self.assertFalse(r[k],k)
    def test_i18_14_non_authority_metadata(self):
        r=require().validate_semantic_lineage_mapping(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("lineage_transition_authorized","scope_transition_authorized","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i18_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["lifecycle_state"]="BAD"
        with self.assertRaises(m.SemanticLineageMappingError):m.validate_semantic_lineage_mapping(bad)
        self.assertEqual(m.validate_semantic_lineage_mapping(valid()),m.validate_semantic_lineage_mapping(valid()))
    def test_i18_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice18.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-PREREGISTRATION.md","governance-runtime/r8_v15_r1_semantic_lineage_mapping_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice18.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice18.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py","governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH14-16-CLOSURE.json"): self.assertIn(p,wf)

if __name__=="__main__":unittest.main(verbosity=2)
