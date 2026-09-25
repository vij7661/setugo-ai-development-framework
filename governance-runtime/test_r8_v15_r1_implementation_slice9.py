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
SLICE9_BRANCH="implementation/r8-v15-r1-slice9-evidence-record-local-2026-09-25"

sys.path.insert(0,str(HERE))
try:
    ev=importlib.import_module("r8_v15_r1_evidence_record_validator")
    IMPORT_ERROR=None
except Exception as exc:
    ev=None
    IMPORT_ERROR=exc

def require_ev():
    if ev is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return ev

def evidence(ids=None,digests=None,seq=7):
    return {
        "evidence_id":"evidence:1",
        "evidence_class":"class:1",
        "producer_identity_digest":"producer:1",
        "runtime_identity_digest":"runtime:1",
        "input_digest":"input:1",
        "input_object_ids":list(ids if ids is not None else ["obj:1"]),
        "input_object_digests":list(digests if digests is not None else ["obj-digest:1"]),
        "execution_proof_digest":"execution:1",
        "output_derivation_digest":"derivation:1",
        "event_id":"event:1",
        "output_digest":"output:1",
        "effective_sequence":seq,
        "evidence_digest":"evidence-digest:1",
    }

class Slice9FrozenAcceptance(unittest.TestCase):
    def validate(self,e=None):
        return require_ev().validate_evidence_record(e or evidence())

    def test_i9_01_field_parity(self):
        m=require_ev()
        schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["EvidenceRecord"]["required"]
        self.assertEqual(set(req),set(m.EVIDENCE_RECORD_FIELDS))
        self.assertEqual(len(req),len(m.EVIDENCE_RECORD_FIELDS))

    def test_i9_02_valid_one_input(self):
        self.assertTrue(self.validate()["locally_valid"])

    def test_i9_03_valid_multi_input(self):
        r=self.validate(evidence(ids=["obj:1","obj:2"],digests=["d:1","d:2"]))
        self.assertEqual(r["input_object_id_count"],2)
        self.assertEqual(r["input_object_digest_count"],2)

    def test_i9_04_missing_extra_reject(self):
        m=require_ev()
        e=evidence(); e.pop("output_digest")
        with self.assertRaises(m.EvidenceRecordError) as cm: self.validate(e)
        self.assertEqual(cm.exception.code,"EVIDENCE_FIELD_SET_INVALID")
        e=evidence(); e["extra"]="x"
        with self.assertRaises(m.EvidenceRecordError) as cm2: self.validate(e)
        self.assertEqual(cm2.exception.code,"EVIDENCE_FIELD_SET_INVALID")

    def test_i9_05_input_object_ids_list_nonempty(self):
        m=require_ev()
        for bad in ([],("obj:1",),"obj:1",None):
            e=evidence(); e["input_object_ids"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.EvidenceRecordError) as cm: self.validate(e)
                self.assertEqual(cm.exception.code,"EVIDENCE_INPUT_IDS_INVALID")

    def test_i9_06_input_object_digests_list_nonempty(self):
        m=require_ev()
        for bad in ([],("d:1",),"d:1",None):
            e=evidence(); e["input_object_digests"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.EvidenceRecordError) as cm: self.validate(e)
                self.assertEqual(cm.exception.code,"EVIDENCE_INPUT_DIGESTS_INVALID")

    def test_i9_07_input_array_lengths_not_invented_equal(self):
        r=self.validate(evidence(ids=["obj:1","obj:2"],digests=["d:1"]))
        self.assertTrue(r["locally_valid"])
        self.assertFalse(r["input_arrays_correspondence_proven"])

    def test_i9_08_opaque_non_sha_strings_pass(self):
        e=evidence()
        for k in ("evidence_id","evidence_class","producer_identity_digest","runtime_identity_digest",
                  "input_digest","execution_proof_digest","output_derivation_digest","event_id",
                  "output_digest","evidence_digest"):
            e[k]=f"opaque-{k}:not-sha"
        e["input_object_ids"]=["opaque-object"]
        e["input_object_digests"]=["opaque-digest:not-sha"]
        self.assertTrue(self.validate(e)["locally_valid"])

    def test_i9_09_empty_non_nfc_noncharacter_reject(self):
        m=require_ev()
        cases=[("evidence_id","", "EVIDENCE_STRING_INVALID"),
               ("producer_identity_digest","e\u0301","EVIDENCE_GCP_STRING_INVALID"),
               ("event_id","\ufdd0","EVIDENCE_GCP_STRING_INVALID")]
        for field,bad,code in cases:
            e=evidence(); e[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.EvidenceRecordError) as cm: self.validate(e)
                self.assertEqual(cm.exception.code,code)
        e=evidence(); e["input_object_ids"]=[""]
        with self.assertRaises(m.EvidenceRecordError) as cm4: self.validate(e)
        self.assertEqual(cm4.exception.code,"EVIDENCE_STRING_INVALID")

    def test_i9_10_sequence_min_max(self):
        for good in (0,9223372036854775807):
            self.assertTrue(self.validate(evidence(seq=good))["locally_valid"])

    def test_i9_11_sequence_invalid_values(self):
        m=require_ev()
        for bad in (-1,9223372036854775808,True,"1",1.5):
            e=evidence(); e["effective_sequence"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.EvidenceRecordError) as cm: self.validate(e)
                self.assertEqual(cm.exception.code,"EVIDENCE_SEQUENCE_INVALID")

    def test_i9_12_duplicate_inputs_are_structurally_allowed(self):
        r=self.validate(evidence(ids=["obj:1","obj:1"],digests=["d:1","d:1"]))
        self.assertTrue(r["locally_valid"])
        self.assertFalse(r["input_uniqueness_proven"])

    def test_i9_13_evidence_digest_remains_unverified(self):
        e=evidence(); e["evidence_digest"]="opaque:not-sha256"
        r=self.validate(e)
        self.assertTrue(r["locally_valid"])
        self.assertFalse(r["evidence_digest_verified"])

    def test_i9_14_semantic_invariants_are_not_self_granted(self):
        r=self.validate()
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("evidence_class_upgrade_valid","producer_revocation_temporally_valid",
                  "mandatory_evidence_satisfied","promotion_authorized","execution_proof_verified",
                  "output_derivation_verified","runtime_qualified","release_authorized",
                  "deployment_authorized","production_authorized","policy_authorized","terminal_authority"):
            self.assertFalse(r[k],k)

    def test_i9_15_failure_does_not_poison(self):
        m=require_ev()
        bad=evidence(); bad["effective_sequence"]=-1
        with self.assertRaises(m.EvidenceRecordError): self.validate(bad)
        self.assertEqual(self.validate(),self.validate())

    def test_i9_16_dependency_immutability_and_workflow(self):
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
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice9.yml").read_text()
        for p in (
            SLICE9_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_evidence_record_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice9.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice9.yml",
            "governance-runtime/test_r8_v15_r1_implementation_slice7.py",
        ):
            self.assertIn(p,wf)

if __name__=="__main__":
    unittest.main(verbosity=2)
