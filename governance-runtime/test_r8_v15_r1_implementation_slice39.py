import importlib, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO_ROOT=HERE.parent; SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice39-case-proof-contracts-family-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_case_proof_contracts_family_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
LEGEND={"FP0":"NOT_APPLICABLE_DETERMINISTIC_INPUT: malformed/mismatched deterministic input is itself the proof.","FP1":"REQUIRED_SIGNED_STATE: independent signed/anchored registry, attestation, certificate, revocation, time, or witness state.","FP2":"REQUIRED_CONCURRENCY_TRACE: independent trace of concurrent attempts plus commit outcomes.","FP3":"REQUIRED_STORAGE_FAULT: independently captured rollback/corruption/outage/store mutation evidence.","FP4":"REQUIRED_RUNTIME_ATTESTATION: workload/runtime/sandbox identity or violation evidence independent of target guard result.","FP5":"REQUIRED_PROVENANCE_DIFF: exact source/artifact/schema/packet/provenance comparison evidence.","FP6":"REQUIRED_EXTERNAL_EFFECT: provider attempt/receipt/observation/reconciliation evidence independent of effect success guard."}
def control(cid="V1-001",blob=None): return {"case_id":cid,"case_text":"text","source_version":"v1","source_commit":"c","source_blob":blob}
def neg(cid="V1-002",fp="FP0"): return {"case_id":cid,"case_text":"text","source_version":"v1","source_commit":"c","source_blob":None,"fault_proof_class":fp}
def contract(i): return {"guard_id":f"G{i:03d}","mechanism_id":f"m{i}","positive_controls":[control()],"negative_controls":[neg()],"canonical_source":{"path":"p"}}
def valid(): return {"schema":"r8-v15-r1-case-proof-contracts/v1","status":"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","authority_effect":"NONE","guard_range":"G001-G156","fault_proof_legend":dict(LEGEND),"contracts":[contract(i) for i in range(1,157)]}
class Slice39CompositeAcceptance(unittest.TestCase):
    def test_i39_01_schema_identity(self):
        m=require(); d=json.loads((SCHEMA_DIR/"case-proof-contracts.schema.json").read_text()); self.assertEqual(tuple(d["required"]),m.ROOT_FIELDS); self.assertEqual(d["properties"]["guard_range"]["const"],m.GUARD_RANGE)
    def test_i39_02_valid_passes(self): self.assertTrue(require().validate_case_proof_contracts(valid())["locally_valid"])
    def test_i39_03_root_shape_consts(self):
        m=require(); x=valid(); x["schema"]="bad"
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
        x=valid(); x["extra"]=1
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_04_legend_exact(self):
        m=require(); x=valid(); x["fault_proof_legend"]["FP0"]="changed"
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
        x=valid(); x["fault_proof_legend"]["FP7"]="x"
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_05_contract_count(self):
        m=require(); x=valid(); x["contracts"]=x["contracts"][:-1]
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_06_guard_id_range_ascii(self):
        m=require()
        for bad in ("G000","G157","G١01"):
            x=valid(); x["contracts"][0]["guard_id"]=bad
            with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_07_contract_shape_mechanism_source(self):
        m=require(); x=valid(); x["contracts"][0]["mechanism_id"]=""
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
        x=valid(); x["contracts"][0]["canonical_source"]={}
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_08_positive_controls(self):
        m=require(); x=valid(); x["contracts"][0]["positive_controls"]=[]
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
        x=valid(); x["contracts"][0]["positive_controls"][0]["case_id"]="V١-001"
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_09_negative_controls_fp_enum(self):
        m=require(); x=valid(); x["contracts"][0]["negative_controls"]=[]
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
        x=valid(); x["contracts"][0]["negative_controls"][0]["fault_proof_class"]="FP7"
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_10_source_blob_null_or_nonempty(self):
        m=require(); x=valid(); x["contracts"][0]["positive_controls"][0]["source_blob"]="blob"; self.assertTrue(m.validate_case_proof_contracts(x)["locally_valid"])
        x=valid(); x["contracts"][0]["positive_controls"][0]["source_blob"]=""
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(x)
    def test_i39_11_duplicate_contracts_allowed(self):
        m=require(); x=valid(); x["contracts"][-1]=dict(x["contracts"][0]); r=m.validate_case_proof_contracts(x); self.assertTrue(r["locally_valid"]); self.assertFalse(r["guard_identity_closure_verified"])
    def test_i39_12_duplicate_controls_allowed(self):
        m=require(); x=valid(); c=x["contracts"][0]["positive_controls"][0]; x["contracts"][0]["positive_controls"]=[c,dict(c)]; self.assertTrue(m.validate_case_proof_contracts(x)["locally_valid"])
    def test_i39_13_no_registry_or_evidence_semantics(self):
        r=require().validate_case_proof_contracts(valid()); self.assertFalse(r["registry_cross_match_verified"]); self.assertFalse(r["fault_proof_evidence_verified"]); self.assertFalse(r["negative_controls_executed"])
    def test_i39_14_non_authority(self):
        r=require().validate_case_proof_contracts(valid()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["freeze_readiness_verified"]); self.assertFalse(r["terminal_authority"])
    def test_i39_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=valid(); bad["contracts"]=[]
        with self.assertRaises(m.CaseProofContractsError): m.validate_case_proof_contracts(bad)
        self.assertTrue(m.validate_case_proof_contracts(valid())["locally_valid"])
        src=(HERE/"r8_v15_r1_case_proof_contracts_family_validator.py").read_text(); self.assertNotIn("r8_v15_r1_case_guard_registry",src)
    def test_i39_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice39.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE39-PREREGISTRATION.md","r8_v15_r1_case_proof_contracts_family_validator.py","test_r8_v15_r1_implementation_slice39.py","R8-V15-R1-IMPLEMENTATION-SLICE39-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
