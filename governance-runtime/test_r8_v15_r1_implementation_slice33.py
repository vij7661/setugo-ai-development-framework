import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice33-ncg-structured-closure-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_ncg_structured_closure_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def nodes(prefix,n): return [f"{prefix}{i}" for i in range(n)]
def valid():
    return {
      "schema":"ncg:1","status":"candidate","authority_effect":"NONE",
      "dependency_nodes":nodes("n",18),
      "dependency_edges":[[f"n{i%18}",f"n{(i+1)%18}"] for i in range(18)] + [[f"n{i%18}",f"n{(i+2)%18}"] for i in range(11)],
      "evaluation_order":nodes("e",21),
      "ownership":[[f"class{i}",f"owner{i}"] for i in range(18)],
      "verification":{"node_count":18,"edge_count":29,"dependency_acyclic":True,"topological_order":nodes("n",18),"evaluation_stage_count":21,"ownership_class_count":18,"duplicate_ownership_classes":[],"edge_semantics_declared":True},
      "edge_semantics":{"kind":"DIRECT_AUTHORITY_RELEVANT_CONSUMPTION_OR_PRECONDITION","transitive_closure_edges_omitted":True,"source_matrix":"governance-r8/R8-V15-NCG-1-MATRICES.md","hand_added_untraceable_edges_forbidden":True},
      "reviewer_suggested_edge_disposition":[],
      "v15_closure_assertions":{}
    }
class Slice33FrozenAcceptance(unittest.TestCase):
    def test_i33_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"ncg-structured-closure.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.FIELDS)
    def test_i33_02_valid_passes(self): self.assertTrue(require().validate_ncg_structured_closure(valid())["locally_valid"])
    def test_i33_03_top_shape(self):
        m=require()
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure([])
        x=valid(); x.pop("ownership")
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_04_nodes_exact18_unique(self):
        m=require(); x=valid(); x["dependency_nodes"]=nodes("n",17)
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["dependency_nodes"][17]=x["dependency_nodes"][0]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_05_edges_exact29_unique_pairs(self):
        m=require(); x=valid(); x["dependency_edges"]=x["dependency_edges"][:-1]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["dependency_edges"][28]=list(x["dependency_edges"][0])
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_06_edge_pair_shape_and_strings(self):
        m=require()
        for bad in (["a"],["a","b","c"],["", "b"],[True,"b"]):
            x=valid(); x["dependency_edges"][0]=bad
            with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_07_evaluation_order_exact21_unique(self):
        m=require(); x=valid(); x["evaluation_order"]=nodes("e",20)
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["evaluation_order"][20]=x["evaluation_order"][0]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_08_ownership_exact18_pairs_duplicates_allowed(self):
        m=require(); x=valid(); x["ownership"]=x["ownership"][:-1]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["ownership"][17]=list(x["ownership"][0]); self.assertTrue(m.validate_ncg_structured_closure(x)["locally_valid"])
    def test_i33_09_verification_exact_fields_consts(self):
        m=require(); x=valid(); x["verification"]["node_count"]=17
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["verification"]["extra"]=1
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_10_topological_order_shape_only(self):
        m=require(); x=valid(); x["verification"]["topological_order"]=list(reversed(x["verification"]["topological_order"]))
        self.assertTrue(m.validate_ncg_structured_closure(x)["locally_valid"])
    def test_i33_11_duplicate_ownership_classes_must_empty(self):
        m=require(); x=valid(); x["verification"]["duplicate_ownership_classes"]=["x"]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_12_edge_semantics_consts_strict(self):
        m=require(); x=valid(); x["edge_semantics"]["transitive_closure_edges_omitted"]=1
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
        x=valid(); x["edge_semantics"]["source_matrix"]="other"
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(x)
    def test_i33_13_open_object_fields(self):
        m=require(); x=valid(); x["reviewer_suggested_edge_disposition"]=[{"anything":1}]; x["v15_closure_assertions"]={"opaque":True}
        self.assertTrue(m.validate_ncg_structured_closure(x)["locally_valid"])
    def test_i33_14_no_graph_recomputation_or_authority(self):
        r=require().validate_ncg_structured_closure(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("acyclicity_recomputed","topology_verified","edge_semantics_verified","ownership_semantics_verified","authority_graph_enforced","terminal_authority"): self.assertFalse(r[k],k)
    def test_i33_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["dependency_nodes"]=[]
        with self.assertRaises(m.NCGStructuredClosureError): m.validate_ncg_structured_closure(bad)
        self.assertTrue(m.validate_ncg_structured_closure(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_ncg_structured_closure_validator.py").read_text(); self.assertNotIn("r8_v15_r1_review_",src)
    def test_i33_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice33.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE33-PREREGISTRATION.md","r8_v15_r1_ncg_structured_closure_validator.py","test_r8_v15_r1_implementation_slice33.py","R8-V15-R1-IMPLEMENTATION-SLICE33-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
