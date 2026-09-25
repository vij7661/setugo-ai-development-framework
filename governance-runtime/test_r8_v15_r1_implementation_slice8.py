import copy
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
SLICE8_BRANCH="implementation/r8-v15-r1-slice8-effect-state-local-2026-09-25"

sys.path.insert(0,str(HERE))
fixtures=importlib.import_module("test_r8_v15_r1_implementation_slice7")
slice1=importlib.import_module("r8_v15_r1_frozen_schema_runtime")

try:
    state=importlib.import_module("r8_v15_r1_effect_state_validator")
    IMPORT_ERROR=None
except Exception as exc:
    state=None
    IMPORT_ERROR=exc

STATES=(
    "INTENT_COMMITTED","DISPATCHING","ACKNOWLEDGED_UNVERIFIED","SUCCEEDED_RECONCILED",
    "FAILED_FINAL","UNCERTAIN","COMPENSATION_REQUIRED","COMPENSATED",
)

def require_state():
    if state is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return state

def record(st="INTENT_COMMITTED",executor=None,reconciliation=None):
    if st=="SUCCEEDED_RECONCILED":
        executor="executor:1" if executor is None else executor
        reconciliation="recon:1" if reconciliation is None else reconciliation
    return {
        "effect_intent_id":"effect:1",
        "idempotency_key":"idem:1",
        "state":st,
        "executor_identity_digest":executor,
        "reconciliation_evidence_digest":reconciliation,
        "state_record_digest":"state-record:1",
    }

class Slice8FrozenAcceptance(unittest.TestCase):
    maxDiff=None

    def validate(self,r=None,i=None):
        m=require_state()
        return m.validate_effect_state_record(
            r or record(),
            effect_intent=i or fixtures.intent(),
            decision_preseal=fixtures.dps(),
            authority_read_set=fixtures.ars(),
            qualified_time_proof=fixtures.qtp(),
            verified_state_seal=fixtures.seal_obj(),
            external_effect_involved=True,
        )

    def test_i8_01_field_parity(self):
        m=require_state()
        schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["EffectStateRecord"]["required"]
        self.assertEqual(set(req),set(m.EFFECT_STATE_RECORD_FIELDS))
        self.assertEqual(len(req),len(m.EFFECT_STATE_RECORD_FIELDS))

    def test_i8_02_valid_intent_committed(self):
        self.assertTrue(self.validate()["locally_valid"])

    def test_i8_03_all_frozen_states_accept_when_shape_valid(self):
        for st in STATES:
            with self.subTest(st=st):
                self.assertTrue(self.validate(r=record(st))["locally_valid"])

    def test_i8_04_missing_extra_reject(self):
        m=require_state()
        r=record(); r.pop("state_record_digest")
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_FIELD_SET_INVALID")
        r=record(); r["extra"]="x"
        with self.assertRaises(m.EffectStateError) as cm2: self.validate(r=r)
        self.assertEqual(cm2.exception.code,"EFFECT_STATE_FIELD_SET_INVALID")

    def test_i8_05_invalid_state_rejects(self):
        m=require_state()
        for bad in ("SUCCEEDED","",None,1,True):
            r=record(); r["state"]=bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
                self.assertEqual(cm.exception.code,"EFFECT_STATE_STATE_INVALID")

    def test_i8_06_opaque_strings_and_gcp_rules(self):
        m=require_state()
        r=record(); r["state_record_digest"]="opaque:not-sha"
        self.assertTrue(self.validate(r=r)["locally_valid"])
        for field,bad,code in (
            ("effect_intent_id","", "EFFECT_STATE_STRING_INVALID"),
            ("idempotency_key","e\u0301","EFFECT_STATE_GCP_STRING_INVALID"),
            ("state_record_digest","\ufdd0","EFFECT_STATE_GCP_STRING_INVALID"),
        ):
            r=record(); r[field]=bad
            with self.subTest(field=field):
                with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
                self.assertEqual(cm.exception.code,code)

    def test_i8_07_nullable_execution_fields_on_non_success(self):
        for st in ("INTENT_COMMITTED","DISPATCHING","ACKNOWLEDGED_UNVERIFIED","FAILED_FINAL","UNCERTAIN","COMPENSATION_REQUIRED","COMPENSATED"):
            r=record(st,executor=None,reconciliation=None)
            r["executor_identity_digest"]=None
            r["reconciliation_evidence_digest"]=None
            with self.subTest(st=st):
                self.assertTrue(self.validate(r=r)["locally_valid"])

    def test_i8_08_nonnull_execution_fields_must_be_gcp_strings(self):
        m=require_state()
        r=record("DISPATCHING",executor="",reconciliation=None)
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_STRING_INVALID")
        r=record("DISPATCHING",executor=None,reconciliation="e\u0301")
        with self.assertRaises(m.EffectStateError) as cm2: self.validate(r=r)
        self.assertEqual(cm2.exception.code,"EFFECT_STATE_GCP_STRING_INVALID")

    def test_i8_09_success_requires_executor_identity(self):
        m=require_state()
        r=record("SUCCEEDED_RECONCILED"); r["executor_identity_digest"]=None
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_SUCCESS_EVIDENCE_REQUIRED")

    def test_i8_10_success_requires_reconciliation_evidence(self):
        m=require_state()
        r=record("SUCCEEDED_RECONCILED"); r["reconciliation_evidence_digest"]=None
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_SUCCESS_EVIDENCE_REQUIRED")

    def test_i8_11_supplied_effect_intent_revalidated_first(self):
        m=require_state()
        i=fixtures.intent(); i["state"]="DISPATCHING"
        with self.assertRaises(m.EffectStateError) as cm: self.validate(i=i)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_INTENT_INVALID")

    def test_i8_12_effect_intent_id_binding(self):
        m=require_state()
        r=record(); r["effect_intent_id"]="effect:other"
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_INTENT_ID_MISMATCH")

    def test_i8_13_idempotency_key_binding(self):
        m=require_state()
        r=record(); r["idempotency_key"]="idem:other"
        with self.assertRaises(m.EffectStateError) as cm: self.validate(r=r)
        self.assertEqual(cm.exception.code,"EFFECT_STATE_IDEMPOTENCY_MISMATCH")

    def test_i8_14_state_label_is_not_authority_or_external_success(self):
        result=self.validate(r=record("SUCCEEDED_RECONCILED"))
        self.assertEqual(result["authority_effect"],"NONE")
        for k in ("effect_state_committed","executor_qualified","reconciliation_verified",
                  "external_effect_succeeded","compensation_authorized","runtime_qualified",
                  "release_authorized","deployment_authorized","production_authorized",
                  "policy_authorized","terminal_authority"):
            self.assertFalse(result[k],k)

    def test_i8_15_failure_does_not_poison(self):
        m=require_state()
        bad=record(); bad["state"]="BAD"
        with self.assertRaises(m.EffectStateError): self.validate(r=bad)
        self.assertEqual(self.validate(),self.validate())

    def test_i8_16_dependency_immutability_and_workflow_coverage(self):
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
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice8.yml").read_text()
        for p in (
            SLICE8_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_effect_state_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice8.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice8.yml",
            "governance-runtime/r8_v15_r1_effect_intent_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice7.py",
        ):
            self.assertIn(p,wf)

if __name__=="__main__":
    unittest.main(verbosity=2)
