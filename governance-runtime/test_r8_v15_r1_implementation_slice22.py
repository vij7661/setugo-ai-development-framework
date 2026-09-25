import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice22-canonical-scope-tuple-local-2026-09-25"
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_canonical_scope_tuple_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid(v="scope:1"):
    return {k:v for k in ("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")}
class Slice22FrozenAcceptance(unittest.TestCase):
    def test_i22_01_fields_and_order_match_schema(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["CanonicalScopeTuple"]
        self.assertEqual(tuple(d["required"]),m.SCOPE_FIELDS); self.assertEqual(tuple(d["x-canonical-order"]),m.SCOPE_FIELDS)
    def test_i22_02_valid_tuple_passes(self): self.assertTrue(require().validate_canonical_scope_tuple(valid())["locally_valid"])
    def test_i22_03_non_mapping_rejects(self):
        m=require()
        with self.assertRaises(m.CanonicalScopeTupleError) as cm:m.validate_canonical_scope_tuple([])
        self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_FIELD_SET_INVALID")
    def test_i22_04_missing_rejects(self):
        m=require(); x=valid(); x.pop("tenant_id")
        with self.assertRaises(m.CanonicalScopeTupleError) as cm:m.validate_canonical_scope_tuple(x)
        self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_FIELD_SET_INVALID")
    def test_i22_05_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.CanonicalScopeTupleError) as cm:m.validate_canonical_scope_tuple(x)
        self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_FIELD_SET_INVALID")
    def test_i22_06_all_components_accept_any(self): self.assertTrue(require().validate_canonical_scope_tuple(valid("ANY"))["locally_valid"])
    def test_i22_07_all_components_accept_stable(self): self.assertTrue(require().validate_canonical_scope_tuple(valid("tenant:alpha"))["locally_valid"])
    def test_i22_08_empty_and_non_string_reject(self):
        m=require()
        for bad in ("",True,1,None):
            x=valid(); x["tenant_id"]=bad
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.CanonicalScopeTupleError) as cm:m.validate_canonical_scope_tuple(x)
                self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_COMPONENT_INVALID")
    def test_i22_09_non_nfc_noncharacter_reject(self):
        m=require()
        for bad in ("e\u0301","\ufdd0"):
            x=valid(); x["tenant_id"]=bad
            with self.assertRaises(m.CanonicalScopeTupleError) as cm:m.validate_canonical_scope_tuple(x)
            self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_COMPONENT_GCP_INVALID")
    def test_i22_10_canonical_order_metadata(self): self.assertEqual(require().validate_canonical_scope_tuple(valid())["canonical_order"],list(require().SCOPE_FIELDS))
    def test_i22_11_no_any_permission_inferred(self): self.assertFalse(require().validate_canonical_scope_tuple(valid("ANY"))["any_permission_verified"])
    def test_i22_12_deterministic(self):
        m=require(); self.assertEqual(m.validate_canonical_scope_tuple(valid()),m.validate_canonical_scope_tuple(valid()))
    def test_i22_13_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["tenant_id"]=""
        with self.assertRaises(m.CanonicalScopeTupleError):m.validate_canonical_scope_tuple(bad)
        self.assertTrue(m.validate_canonical_scope_tuple(valid())["locally_valid"])
    def test_i22_14_non_authority_metadata(self):
        r=require().validate_canonical_scope_tuple(valid("ANY")); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("scope_current","scope_match_verified","scope_relation_verified","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i22_15_no_sibling_dependency(self):
        src=(HERE/"r8_v15_r1_canonical_scope_tuple_validator.py").read_text()
        for name in ("r8_v15_r1_scope_component_validator","r8_v15_r1_stable_scope_value_validator","r8_v15_r1_any_scope_permission_validator"): self.assertNotIn(name,src)
    def test_i22_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice22.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE22-PREREGISTRATION.md","r8_v15_r1_canonical_scope_tuple_validator.py","test_r8_v15_r1_implementation_slice22.py","R8-V15-R1-IMPLEMENTATION-SLICE22-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
