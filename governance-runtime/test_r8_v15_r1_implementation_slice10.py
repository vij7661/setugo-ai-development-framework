import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
SLICE7_CANDIDATE="751162ee42c603cb6c84ee12021d16bab6fa626b"
SLICE10_BRANCH="implementation/r8-v15-r1-slice10-review-attestation-local-2026-09-25"

sys.path.insert(0,str(HERE))
try:
    reviewmod=importlib.import_module("r8_v15_r1_review_attestation_validator")
    IMPORT_ERROR=None
except Exception as exc:
    reviewmod=None
    IMPORT_ERROR=exc

def require_review():
    if reviewmod is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return reviewmod

def dim(i=1,result="PASS"):
    return {"dimension_id":f"dimension:{i}","result":result,"result_digest":f"result-digest:{i}"}

def attestation(results=None):
    return {
        "reviewer_canonical_subject_id":"reviewer:1",
        "reviewer_admin_domain_id":"domain:1",
        "candidate_digest":"candidate:digest:1",
        "governance_snapshot_digest":"gov:digest:1",
        "packet_digest":"packet:digest:1",
        "attestation_digest":"attestation:digest:1",
        "review_dimension_results":list(results if results is not None else [dim(1)]),
    }

class Slice10FrozenAcceptance(unittest.TestCase):
    def validate(self,a=None):
        return require_review().validate_review_attestation(a or attestation())

    def test_i10_01_top_level_field_parity(self):
        m=require_review()
        schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ReviewAttestation"]["required"]
        self.assertEqual(set(req),set(m.REVIEW_ATTESTATION_FIELDS))
        self.assertEqual(len(req),len(m.REVIEW_ATTESTATION_FIELDS))

    def test_i10_02_valid_one_dimension(self):
        self.assertTrue(self.validate()["locally_valid"])

    def test_i10_03_valid_multi_dimension(self):
        r=self.validate(attestation([dim(1),dim(2,"FAIL"),dim(3,"UNAVAILABLE")]))
        self.assertEqual(r["review_dimension_count"],3)

    def test_i10_04_missing_extra_top_level_reject(self):
        m=require_review()
        a=attestation(); a.pop("packet_digest")
        with self.assertRaises(m.ReviewAttestationError) as cm: self.validate(a)
        self.assertEqual(cm.exception.code,"REVIEW_ATTESTATION_FIELD_SET_INVALID")
        a=attestation(); a["extra"]="x"
        with self.assertRaises(m.ReviewAttestationError) as cm2: self.validate(a)
        self.assertEqual(cm2.exception.code,"REVIEW_ATTESTATION_FIELD_SET_INVALID")

    def test_i10_05_dimensions_list_nonempty(self):
        m=require_review()
        for bad in ([],(dim(1),),dim(1),None):
            a=attestation(); a["review_dimension_results"]=bad
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(m.ReviewAttestationError) as cm: self.validate(a)
                self.assertEqual(cm.exception.code,"REVIEW_DIMENSIONS_INVALID")

    def test_i10_06_nested_exact_fields(self):
        m=require_review()
        a=attestation(); a["review_dimension_results"][0].pop("result_digest")
        with self.assertRaises(m.ReviewAttestationError) as cm: self.validate(a)
        self.assertEqual(cm.exception.code,"REVIEW_DIMENSION_FIELD_SET_INVALID")
        a=attestation(); a["review_dimension_results"][0]["extra"]="x"
        with self.assertRaises(m.ReviewAttestationError) as cm2: self.validate(a)
        self.assertEqual(cm2.exception.code,"REVIEW_DIMENSION_FIELD_SET_INVALID")

    def test_i10_07_invalid_result_enum_rejects(self):
        m=require_review()
        for bad in ("SKIP","",None,1,True):
            a=attestation(); a["review_dimension_results"][0]["result"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.ReviewAttestationError) as cm: self.validate(a)
                self.assertEqual(cm.exception.code,"REVIEW_DIMENSION_RESULT_INVALID")

    def test_i10_08_all_frozen_results_structurally_accept(self):
        for result in ("PASS","FAIL","UNAVAILABLE"):
            with self.subTest(result=result):
                self.assertTrue(self.validate(attestation([dim(1,result)]))["locally_valid"])

    def test_i10_09_opaque_non_sha_strings_pass(self):
        a=attestation()
        for k in ("reviewer_canonical_subject_id","reviewer_admin_domain_id","candidate_digest",
                  "governance_snapshot_digest","packet_digest","attestation_digest"):
            a[k]=f"opaque-{k}:not-sha"
        a["review_dimension_results"][0]["dimension_id"]="opaque-dimension"
        a["review_dimension_results"][0]["result_digest"]="opaque-result:not-sha"
        self.assertTrue(self.validate(a)["locally_valid"])

    def test_i10_10_empty_non_nfc_noncharacter_reject(self):
        m=require_review()
        cases=[
            ("reviewer_canonical_subject_id","", "REVIEW_STRING_INVALID"),
            ("reviewer_admin_domain_id","e\u0301","REVIEW_GCP_STRING_INVALID"),
            ("packet_digest","\ufdd0","REVIEW_GCP_STRING_INVALID"),
        ]
        for field,bad,code in cases:
            a=attestation(); a[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.ReviewAttestationError) as cm: self.validate(a)
                self.assertEqual(cm.exception.code,code)
        a=attestation(); a["review_dimension_results"][0]["dimension_id"]=""
        with self.assertRaises(m.ReviewAttestationError) as cm4: self.validate(a)
        self.assertEqual(cm4.exception.code,"REVIEW_STRING_INVALID")

    def test_i10_11_duplicate_dimension_ids_are_structurally_allowed(self):
        r=self.validate(attestation([dim(1),dim(1,"FAIL")]))
        self.assertTrue(r["locally_valid"])
        self.assertFalse(r["dimension_uniqueness_proven"])

    def test_i10_12_all_pass_does_not_close_gate(self):
        r=self.validate(attestation([dim(1,"PASS"),dim(2,"PASS")]))
        self.assertFalse(r["review_gate_closed"])
        self.assertFalse(r["promotion_authorized"])

    def test_i10_13_attestation_digest_unverified(self):
        a=attestation(); a["attestation_digest"]="opaque:not-sha"
        r=self.validate(a)
        self.assertTrue(r["locally_valid"])
        self.assertFalse(r["attestation_digest_verified"])

    def test_i10_14_independence_and_authority_not_self_granted(self):
        r=self.validate()
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("reviewer_independence_proven","signature_verified","review_gate_closed",
                  "promotion_authorized","runtime_qualified","release_authorized",
                  "deployment_authorized","production_authorized","policy_authorized","terminal_authority"):
            self.assertFalse(r[k],k)

    def test_i10_15_failure_does_not_poison(self):
        m=require_review()
        bad=attestation(); bad["review_dimension_results"][0]["result"]="BAD"
        with self.assertRaises(m.ReviewAttestationError): self.validate(bad)
        self.assertEqual(self.validate(),self.validate())

    def test_i10_16_dependency_immutability_and_workflow(self):
        result=subprocess.run([
            "git","diff","--name-only",SLICE7_CANDIDATE,"HEAD","--",
            "schemas/governance-r8/v15-r1",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/r8_v15_r1_state_roots.py",
            "governance-runtime/r8_v15_r1_stc_validator.py",
            "governance-runtime/r8_v15_r1_preseal_validator.py",
            "governance-runtime/r8_v15_r1_timeproof_validator.py",
            "governance-runtime/r8_v15_r1_seal_validator.py",
            "governance-runtime/r8_v15_r1_effect_intent_validator.py",
        ],cwd=REPO_ROOT,check=True,text=True,capture_output=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice10.yml").read_text()
        for p in (
            SLICE10_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_review_attestation_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice10.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice10.yml",
            "governance-runtime/test_r8_v15_r1_implementation_slice7.py",
        ):
            self.assertIn(p,wf)

if __name__=="__main__":
    unittest.main(verbosity=2)
