import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice30-review-packet-type-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_review_packet_type_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def field(fid="f1",conditions=None,sources=None):
    return {"field_id":fid,"classification":"REVIEW_SEMANTIC","conditions":[] if conditions is None else conditions,"source_rules":["R1"] if sources is None else sources}
def valid(): return {"packet_type_id":"packet:1","fields":[field()],"ordering_semantic":True,"evidence_association_semantic":True}
class Slice30FrozenAcceptance(unittest.TestCase):
    def test_i30_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"review-presentation-schema.schema.json").read_text())["$defs"]["PacketType"]
        self.assertEqual(tuple(d["required"]),m.FIELDS); self.assertEqual(d["properties"]["fields"]["minItems"],1)
    def test_i30_02_valid_passes(self): self.assertTrue(require().validate_review_packet_type(valid())["locally_valid"])
    def test_i30_03_shape(self):
        m=require()
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type([])
        x=valid(); x.pop("fields")
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_04_packet_type_id(self):
        m=require()
        for bad in (True,"","e\u0301","\ufdd0"):
            x=valid(); x["packet_type_id"]=bad
            with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_05_fields_min1_list(self):
        m=require()
        for bad in ([],None,{},"x"):
            x=valid(); x["fields"]=bad
            with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_06_nested_field_exact_shape(self):
        m=require(); x=valid(); x["fields"]=[{"field_id":"f","classification":"REVIEW_SEMANTIC","conditions":[]}]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
        x=valid(); y=field(); y["extra"]=1; x["fields"]=[y]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_07_nested_string_and_classification_rules(self):
        m=require()
        for bad in ("",True,"e\u0301","\ufdd0"):
            x=valid(); y=field(); y["field_id"]=bad; x["fields"]=[y]
            with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
        x=valid(); y=field(); y["classification"]="BAD"; x["fields"]=[y]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_08_nested_conditions(self):
        m=require(); x=valid(); y=field(conditions=[]); x["fields"]=[y]; self.assertTrue(m.validate_review_packet_type(x)["locally_valid"])
        x=valid(); y=field(conditions=[""]); x["fields"]=[y]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_09_nested_source_rules(self):
        m=require(); x=valid(); y=field(sources=[]); x["fields"]=[y]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
        x=valid(); y=field(sources=["R1","R1"]); x["fields"]=[y]
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_10_fields_unique_items(self):
        m=require(); f=field(); x=valid(); x["fields"]=[f,dict(f)]
        with self.assertRaises(m.ReviewPacketTypeError) as cm: m.validate_review_packet_type(x)
        self.assertEqual(cm.exception.code,"REVIEW_PACKET_FIELDS_NOT_UNIQUE")
    def test_i30_11_same_field_id_different_object_allowed(self):
        m=require(); x=valid(); x["fields"]=[field("same"),field("same",conditions=["c2"])]
        self.assertTrue(m.validate_review_packet_type(x)["locally_valid"])
    def test_i30_12_ordering_semantic_strict_true(self):
        m=require()
        for bad in (False,1,"true",None):
            x=valid(); x["ordering_semantic"]=bad
            with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_13_evidence_semantic_strict_true(self):
        m=require()
        for bad in (False,1,"true",None):
            x=valid(); x["evidence_association_semantic"]=bad
            with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(x)
    def test_i30_14_no_semantic_execution(self):
        r=require().validate_review_packet_type(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("ordering_semantics_executed","evidence_association_verified","review_materiality_verified","review_authority_granted","runtime_qualified","terminal_authority"): self.assertFalse(r[k],k)
    def test_i30_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["ordering_semantic"]=False
        with self.assertRaises(m.ReviewPacketTypeError): m.validate_review_packet_type(bad)
        self.assertTrue(m.validate_review_packet_type(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_review_packet_type_validator.py").read_text()
        for name in ("r8_v15_r1_review_field_rule_validator","r8_v15_r1_review_presentation_schema_validator"): self.assertNotIn(name,src)
    def test_i30_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice30.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE30-PREREGISTRATION.md","r8_v15_r1_review_packet_type_validator.py","test_r8_v15_r1_implementation_slice30.py","R8-V15-R1-IMPLEMENTATION-SLICE30-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
