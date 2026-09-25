import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice31-review-presentation-schema-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_review_presentation_schema_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def field(fid="f1"): return {"field_id":fid,"classification":"REVIEW_SEMANTIC","conditions":[],"source_rules":["R1"]}
def packet(pid="p1",fid="f1"): return {"packet_type_id":pid,"fields":[field(fid)],"ordering_semantic":True,"evidence_association_semantic":True}
def valid(): return {"schema":"r8-v15-r1-rps-1/v1","status":"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","authority_effect":"NONE","unknown_display_field_default":"REVIEW_SEMANTIC","packet_types":[packet()]}
class Slice31FrozenAcceptance(unittest.TestCase):
    def test_i31_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"review-presentation-schema.schema.json").read_text())
        self.assertEqual(tuple(d["required"]),m.FIELDS); self.assertEqual(d["properties"]["schema"]["const"],m.SCHEMA_CONST)
    def test_i31_02_valid_passes(self): self.assertTrue(require().validate_review_presentation_schema(valid())["locally_valid"])
    def test_i31_03_top_level_shape(self):
        m=require()
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema([])
        x=valid(); x.pop("packet_types")
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_04_root_consts(self):
        m=require()
        for f,b in (("schema","bad"),("status","bad"),("authority_effect","OTHER"),("unknown_display_field_default","DISPLAY_NON_SEMANTIC")):
            x=valid(); x[f]=b
            with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_05_packet_types_min1_list(self):
        m=require()
        for bad in ([],None,{},"x"):
            x=valid(); x["packet_types"]=bad
            with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_06_packet_shape(self):
        m=require(); x=valid(); x["packet_types"]=[{"packet_type_id":"p","fields":[]}]
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_07_packet_id_string(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); p=packet(); p["packet_type_id"]=bad; x["packet_types"]=[p]
            with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_08_fields_nested_rules(self):
        m=require(); x=valid(); p=packet(); p["fields"]=[]; x["packet_types"]=[p]
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
        x=valid(); p=packet(); p["fields"]=[{"field_id":"f","classification":"BAD","conditions":[],"source_rules":["R1"]}]; x["packet_types"]=[p]
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_09_nested_fields_unique(self):
        m=require(); x=valid(); p=packet(); f=field(); p["fields"]=[f,dict(f)]; x["packet_types"]=[p]
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_10_packet_types_duplicates_allowed(self):
        m=require(); p=packet(); x=valid(); x["packet_types"]=[p,dict(p)]
        self.assertTrue(m.validate_review_presentation_schema(x)["locally_valid"])
    def test_i31_11_nested_true_consts_strict(self):
        m=require()
        for f in ("ordering_semantic","evidence_association_semantic"):
            for bad in (False,1,"true"):
                x=valid(); p=packet(); p[f]=bad; x["packet_types"]=[p]
                with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(x)
    def test_i31_12_unknown_default_is_declaration_only(self):
        r=require().validate_review_presentation_schema(valid()); self.assertFalse(r["unknown_field_materiality_enforced"])
    def test_i31_13_deterministic(self):
        m=require(); self.assertEqual(m.validate_review_presentation_schema(valid()),m.validate_review_presentation_schema(valid()))
    def test_i31_14_non_authority(self):
        r=require().validate_review_presentation_schema(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("presentation_enforced","reviewer_independence_verified","review_authority_granted","runtime_qualified","terminal_authority"): self.assertFalse(r[k],k)
    def test_i31_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["schema"]="bad"
        with self.assertRaises(m.ReviewPresentationSchemaError): m.validate_review_presentation_schema(bad)
        self.assertTrue(m.validate_review_presentation_schema(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_review_presentation_schema_validator.py").read_text()
        for name in ("r8_v15_r1_review_field_rule_validator","r8_v15_r1_review_packet_type_validator"): self.assertNotIn(name,src)
    def test_i31_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice31.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE31-PREREGISTRATION.md","r8_v15_r1_review_presentation_schema_validator.py","test_r8_v15_r1_implementation_slice31.py","R8-V15-R1-IMPLEMENTATION-SLICE31-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
