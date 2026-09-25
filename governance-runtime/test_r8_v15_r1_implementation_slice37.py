import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice37-guard-omission-family-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_guard_omission_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
D="a"*64
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def evidence_record(i=0):
    return {"source_version":"v1","source_path":"p","source_commit":"c","source_blob":"b","line_start":2,"line_end":1,"digest_basis":"raw","raw_section_sha256":D,"raw_section_bytes":1,"parsed_guard_ids":["G001"],"parsed_case_ids":["V1-001"],"manifest_guard_ids":["G001"],"manifest_case_ids":["V1-001"],"verification":{"guard_set_equal":True,"case_set_equal":True,"missing_guard_ids":[],"extra_guard_ids":[],"missing_case_ids":[],"extra_case_ids":[]},"excerpt":"x"}
def evidence():
    return {"schema":"r8-v15-r1-guard-omission-source-evidence/v1","status":"REVIEW_EVIDENCE_NON_AUTHORITATIVE","authority_effect":"NONE","semantic_candidate_commit":"c721b38cf8b00294797300b526596ce723a47ff8","purpose":"p","digest_contract":{"algorithm":"SHA-256","text_encoding":"UTF-8","line_separator":"LF","trailing_line_separator_added":False,"digest_field":"raw_section_sha256","verification_instruction":"verify"},"record_count":11,"all_guard_sets_equal":True,"all_case_sets_equal":True,"records":[evidence_record(i) for i in range(11)]}
def manifest_record(i=0):
    return {"source_version":"v1","source_path":"p","source_commit":"c","source_blob":"b","line_start":2,"line_end":1,"raw_section_sha256":D,"raw_section_bytes":1,"guard_ids":["G001"],"referenced_case_ids":["V1-001"],"parsed_source_guard_set_equals_manifest_set":True,"parsed_source_case_set_equals_manifest_set":True,"all_guard_ids_in_current_registry":True,"all_referenced_case_ids_in_current_case_registry":True,"missing_guard_ids":[],"extra_guard_ids":[],"missing_case_ids":[],"extra_case_ids":[],"evidence_record_index":i}
def manifest():
    return {"schema":"guard-omission-manifest-1/v3","status":"REVIEW_EVIDENCE_NON_AUTHORITATIVE","authority_effect":"NONE","current_guard_registry":{},"current_case_registry":{},"omitted_table_count":11,"invalid_omission_count":0,"validation_contract":{},"omitted_tables":[manifest_record(i) for i in range(11)],"reverification":{},"legacy_note":"legacy"}
class Slice37CompositeAcceptance(unittest.TestCase):
    def test_i37_01_schema_identity(self):
        m=require(); e=json.loads((SCHEMA_DIR/"guard-omission-source-evidence.schema.json").read_text()); g=json.loads((SCHEMA_DIR/"guard-omission-manifest.schema.json").read_text())
        self.assertEqual(tuple(e["required"]),m.EVIDENCE_ROOT_FIELDS); self.assertEqual(tuple(g["required"]),m.MANIFEST_ROOT_FIELDS)
    def test_i37_02_valid_both_pass(self):
        m=require(); self.assertTrue(m.validate_guard_omission_source_evidence(evidence())["locally_valid"]); self.assertTrue(m.validate_guard_omission_manifest(manifest())["locally_valid"])
    def test_i37_03_evidence_root_consts_shape(self):
        m=require(); x=evidence(); x["record_count"]=10
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["extra"]=1
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
    def test_i37_04_digest_contract_exact(self):
        m=require(); x=evidence(); x["digest_contract"]["trailing_line_separator_added"]=0
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["digest_contract"]["algorithm"]="SHA256"
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
    def test_i37_05_evidence_records_cardinality_patterns_numbers(self):
        m=require(); x=evidence(); x["records"]=x["records"][:-1]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["records"][0]["source_version"]="v١"
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["records"][0]["raw_section_bytes"]=True
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
    def test_i37_06_evidence_ids_and_verification(self):
        m=require(); x=evidence(); x["records"][0]["parsed_guard_ids"]=["G001","G001"]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["records"][0]["verification"]["guard_set_equal"]=1
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
        x=evidence(); x["records"][0]["verification"]["missing_case_ids"]=["V1-001"]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_source_evidence(x)
    def test_i37_07_evidence_claims_not_recomputed(self):
        r=require().validate_guard_omission_source_evidence(evidence()); self.assertFalse(r["digest_recomputed"]); self.assertFalse(r["guard_case_sets_recomputed"])
    def test_i37_08_manifest_root_and_open_objects(self):
        m=require(); x=manifest(); x["current_guard_registry"]={"opaque":1}; x["validation_contract"]={"opaque":2}; x["reverification"]={"opaque":3}; self.assertTrue(m.validate_guard_omission_manifest(x)["locally_valid"])
        x=manifest(); x["invalid_omission_count"]=1
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
    def test_i37_09_manifest_tables_cardinality_and_patterns(self):
        m=require(); x=manifest(); x["omitted_tables"]=x["omitted_tables"][:-1]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
        x=manifest(); x["omitted_tables"][0]["guard_ids"]=["G١01"]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
    def test_i37_10_manifest_ids_and_true_consts(self):
        m=require(); x=manifest(); x["omitted_tables"][0]["guard_ids"]=["G001","G001"]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
        x=manifest(); x["omitted_tables"][0]["all_guard_ids_in_current_registry"]=1
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
    def test_i37_11_empty_arrays_and_evidence_index(self):
        m=require(); x=manifest(); x["omitted_tables"][0]["missing_guard_ids"]=["G001"]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
        for bad in (-1,11,True):
            x=manifest(); x["omitted_tables"][0]["evidence_record_index"]=bad
            with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(x)
    def test_i37_12_no_line_range_relation_inferred(self):
        m=require(); self.assertTrue(m.validate_guard_omission_source_evidence(evidence())["locally_valid"]); self.assertTrue(m.validate_guard_omission_manifest(manifest())["locally_valid"])
    def test_i37_13_no_source_or_membership_verification(self):
        m=require()
        for r in (m.validate_guard_omission_source_evidence(evidence()),m.validate_guard_omission_manifest(manifest())):
            self.assertFalse(r["source_exists_verified"]); self.assertFalse(r["registry_membership_verified"]); self.assertFalse(r["reverification_executed"])
    def test_i37_14_non_authority(self):
        m=require()
        for r in (m.validate_guard_omission_source_evidence(evidence()),m.validate_guard_omission_manifest(manifest())):
            self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["evidence_promotion_authorized"]); self.assertFalse(r["terminal_authority"])
    def test_i37_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=manifest(); bad["omitted_tables"]=[]
        with self.assertRaises(m.GuardOmissionFamilyError): m.validate_guard_omission_manifest(bad)
        self.assertTrue(m.validate_guard_omission_source_evidence(evidence())["locally_valid"])
        src=(HERE/"r8_v15_r1_guard_omission_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_case_guard_registry",src)
    def test_i37_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice37.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE37-PREREGISTRATION.md","r8_v15_r1_guard_omission_family_validator.py","test_r8_v15_r1_implementation_slice37.py","R8-V15-R1-IMPLEMENTATION-SLICE37-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
