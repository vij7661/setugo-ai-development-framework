import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"; BRANCH="implementation/r8-v15-r1-slice24-any-scope-permission-local-2026-09-25"; INT64_MAX=9223372036854775807
NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
sys.path.insert(0,str(HERE))
try: mod=importlib.import_module("r8_v15_r1_any_scope_permission_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def valid():
    return {"permission_id":"perm:1","semantic_class":"class:1","allowed_any_tuple_components":["tenant_id"],"effective_sequence":0,"lifecycle_state":"ACTIVE","constitutional_authority_evidence_digest":"constitutional:digest","permission_digest":"permission:digest"}
class Slice24FrozenAcceptance(unittest.TestCase):
    def test_i24_01_field_parity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())["$defs"]["ANYScopePermission"]
        self.assertEqual(set(d["required"]),set(m.ANY_SCOPE_PERMISSION_FIELDS)); self.assertEqual(len(d["required"]),len(m.ANY_SCOPE_PERMISSION_FIELDS))
    def test_i24_02_valid_permission_passes(self): self.assertTrue(require().validate_any_scope_permission(valid())["locally_valid"])
    def test_i24_03_mapping_missing_extra_reject(self):
        m=require()
        for bad in ([],):
            with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(bad)
            self.assertEqual(cm.exception.code,"ANY_PERMISSION_FIELD_SET_INVALID")
        x=valid(); x.pop("permission_id")
        with self.assertRaises(m.ANYScopePermissionError):m.validate_any_scope_permission(x)
        x=valid(); x["extra"]="x"
        with self.assertRaises(m.ANYScopePermissionError):m.validate_any_scope_permission(x)
    def test_i24_04_string_rules(self):
        m=require()
        for field,bad,code in (("permission_id",True,"ANY_PERMISSION_STRING_INVALID"),("semantic_class","","ANY_PERMISSION_STRING_INVALID"),("constitutional_authority_evidence_digest","e\u0301","ANY_PERMISSION_GCP_STRING_INVALID"),("permission_digest","\ufdd0","ANY_PERMISSION_GCP_STRING_INVALID")):
            x=valid(); x[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
                self.assertEqual(cm.exception.code,code)
    def test_i24_05_components_list_and_empty_allowed(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=[]; self.assertTrue(m.validate_any_scope_permission(x)["locally_valid"])
        for bad in (None,"tenant_id",("tenant_id",),{}):
            x=valid(); x["allowed_any_tuple_components"]=bad
            with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
            self.assertEqual(cm.exception.code,"ANY_PERMISSION_COMPONENTS_INVALID")
    def test_i24_06_exact_component_name_elements(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=list(NAMES); self.assertTrue(m.validate_any_scope_permission(x)["locally_valid"])
        for bad in ("unknown","Tenant_Id","tenant_id ",True,1):
            x=valid(); x["allowed_any_tuple_components"]=[bad]
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
                self.assertEqual(cm.exception.code,"ANY_PERMISSION_COMPONENT_NAME_INVALID")
    def test_i24_07_duplicates_reject(self):
        m=require(); x=valid(); x["allowed_any_tuple_components"]=["tenant_id","tenant_id"]
        with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
        self.assertEqual(cm.exception.code,"ANY_PERMISSION_COMPONENTS_NOT_UNIQUE")
    def test_i24_08_sequence_closure(self):
        m=require()
        for good in (0,INT64_MAX):
            x=valid(); x["effective_sequence"]=good; self.assertTrue(m.validate_any_scope_permission(x)["locally_valid"])
        for bad in (-1,INT64_MAX+1,True,"1",1.5):
            x=valid(); x["effective_sequence"]=bad
            with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
            self.assertEqual(cm.exception.code,"ANY_PERMISSION_SEQUENCE_INVALID")
    def test_i24_09_lifecycle_enum(self):
        m=require()
        for good in ("ACTIVE","SUSPENDED","RETIRED","REVOKED"):
            x=valid(); x["lifecycle_state"]=good; self.assertTrue(m.validate_any_scope_permission(x)["locally_valid"])
        x=valid(); x["lifecycle_state"]="UNKNOWN"
        with self.assertRaises(m.ANYScopePermissionError) as cm:m.validate_any_scope_permission(x)
        self.assertEqual(cm.exception.code,"ANY_PERMISSION_LIFECYCLE_INVALID")
    def test_i24_10_opaque_digests_pass(self):
        m=require(); x=valid(); x["constitutional_authority_evidence_digest"]="not-a-sha"; x["permission_digest"]="opaque"; self.assertTrue(m.validate_any_scope_permission(x)["locally_valid"])
    def test_i24_11_active_not_current(self): self.assertFalse(require().validate_any_scope_permission(valid())["permission_current"])
    def test_i24_12_any_coverage_unverified(self): self.assertFalse(require().validate_any_scope_permission(valid())["semantic_entry_any_coverage_verified"])
    def test_i24_13_constitutional_and_broadening_unverified(self):
        r=require().validate_any_scope_permission(valid()); self.assertFalse(r["constitutional_evidence_verified"]); self.assertFalse(r["broadening_authorized"])
    def test_i24_14_non_authority_metadata(self):
        r=require().validate_any_scope_permission(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("permission_effective","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"): self.assertFalse(r[k],k)
    def test_i24_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["effective_sequence"]=-1
        with self.assertRaises(m.ANYScopePermissionError):m.validate_any_scope_permission(bad)
        self.assertTrue(m.validate_any_scope_permission(valid())["locally_valid"])
    def test_i24_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice24.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE24-PREREGISTRATION.md","r8_v15_r1_any_scope_permission_validator.py","test_r8_v15_r1_implementation_slice24.py","R8-V15-R1-IMPLEMENTATION-SLICE24-MARKER.json","R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"): self.assertIn(p,wf)
if __name__=="__main__":unittest.main(verbosity=2)
