import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice35-spm1-provenance-family-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_spm1_provenance_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
D="a"*64; B="b"*40
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def source_ref(): return {"design_id":"design:1","path":"p","commit":"opaque-c","blob":"opaque-b"}
def generator(status="UNATTESTED_RUNTIME"): return {"generator_id":"g1","generator_artifact_path":"gen.py","generator_artifact_sha256":D,"runtime_manifest_digest":None,"workload_attestation_proof_digest":None,"qualification_status":status}
def artifact(aid="a1"): return {"artifact_id":aid,"path":"schema.json","git_blob_sha1":B,"sha256":D}
def entry(aid="a1",ref="src1"): return {"artifact_id":aid,"artifact_sha256":D,"json_pointer":"/x","semantic_purpose":"purpose","source_design_ids":["design:1"],"generator_id":"g1","generator_runtime_manifest_digest":None,"reviewer_status":"NOT_YET_REVIEWED","source_ref_ids":[ref]}
def valid():
    return {"schema":"r8-v15-r1-spm-1/v1","status":"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","authority_effect":"NONE","semantic_candidate_commit":"c721b38cf8b00294797300b526596ce723a47ff8","generator":generator(),"artifact_count":1,"entry_count":1,"artifacts":[artifact()],"entries":[entry()],"coverage":{"uncovered_semantic_elements":[],"non_authoritative_only_sources":[],"conflicting_entries":[]},"source_ref_catalog":{"src1":source_ref()}}
class Slice35CompositeAcceptance(unittest.TestCase):
    def test_i35_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"schema-provenance-manifest.schema.json").read_text())
        self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS); self.assertEqual(tuple(d["$defs"]["GeneratorBinding"]["required"]),m.GENERATOR_FIELDS)
    def test_i35_02_valid_family_passes(self): self.assertTrue(require().validate_spm1_manifest(valid())["locally_valid"])
    def test_i35_03_root_shape_and_consts(self):
        m=require()
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest([])
        x=valid(); x.pop("entries")
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["schema"]="bad"
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_04_status_and_counts(self):
        m=require()
        for st in ("SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","FINAL_FREEZE_ELIGIBLE"):
            x=valid(); x["status"]=st; self.assertTrue(m.validate_spm1_manifest(x)["locally_valid"])
        for f in ("artifact_count","entry_count"):
            for bad in (0,-1,True,"1"):
                x=valid(); x[f]=bad
                with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_05_generator_binding(self):
        m=require(); x=valid(); x["generator"]=generator("QUALIFIED"); self.assertTrue(m.validate_spm1_manifest(x)["locally_valid"])
        for bad in ("A"*64,"a"*63,True):
            x=valid(); x["generator"]["generator_artifact_sha256"]=bad
            with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["generator"]["qualification_status"]="BAD"
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_06_artifact_binding_and_uniqueitems(self):
        m=require(); x=valid(); x["artifacts"]=[artifact("a1"),artifact("a2")]; self.assertTrue(m.validate_spm1_manifest(x)["locally_valid"])
        x=valid(); x["artifacts"]=[artifact(),artifact()]
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["artifacts"][0]["git_blob_sha1"]="A"*40
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_07_source_ref_catalog(self):
        m=require(); x=valid(); x["source_ref_catalog"]={}
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["source_ref_catalog"]={"":source_ref()}; self.assertTrue(m.validate_spm1_manifest(x)["locally_valid"])
        x=valid(); x["source_ref_catalog"]["src1"]["design_id"]=""
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_08_provenance_entry(self):
        m=require(); x=valid(); x["entries"][0]["json_pointer"]="x"
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["entries"][0]["source_design_ids"]=[]
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["entries"][0]["source_ref_ids"]=["src1","src1"]
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_09_entries_duplicates_allowed(self):
        m=require(); e=entry(); x=valid(); x["entries"]=[e,dict(e)]; self.assertTrue(m.validate_spm1_manifest(x)["locally_valid"])
    def test_i35_10_coverage_must_be_exact_empty_arrays(self):
        m=require(); x=valid(); x["coverage"]["conflicting_entries"]=["x"]
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
        x=valid(); x["coverage"]["extra"]=[]
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(x)
    def test_i35_11_source_ref_binding_not_inferred(self):
        m=require(); x=valid(); x["entries"][0]["source_ref_ids"]=["missing"]; r=m.validate_spm1_manifest(x); self.assertFalse(r["source_ref_binding_verified"])
    def test_i35_12_count_equality_not_inferred(self):
        m=require(); x=valid(); x["artifact_count"]=2; x["entry_count"]=2; r=m.validate_spm1_manifest(x); self.assertFalse(r["count_correspondence_verified"])
    def test_i35_13_declared_final_or_qualified_not_proof(self):
        m=require(); x=valid(); x["status"]="FINAL_FREEZE_ELIGIBLE"; x["generator"]=generator("QUALIFIED"); r=m.validate_spm1_manifest(x)
        self.assertFalse(r["final_freeze_eligibility_verified"]); self.assertFalse(r["generator_qualification_verified"])
    def test_i35_14_non_authority(self):
        r=require().validate_spm1_manifest(valid()); self.assertEqual(r["authority_effect"],"NONE")
        for k in ("artifact_digests_verified","source_authority_verified","provenance_semantics_verified","evidence_promotion_authorized","runtime_qualified","terminal_authority"): self.assertFalse(r[k],k)
    def test_i35_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["artifact_count"]=0
        with self.assertRaises(m.SPM1Error): m.validate_spm1_manifest(bad)
        self.assertTrue(m.validate_spm1_manifest(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_spm1_provenance_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_spm_source_ref_validator",src)
    def test_i35_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice35.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE35-PREREGISTRATION.md","r8_v15_r1_spm1_provenance_family_validator.py","test_r8_v15_r1_implementation_slice35.py","R8-V15-R1-IMPLEMENTATION-SLICE35-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
