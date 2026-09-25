import copy
import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SCHEMA_DIR = REPO_ROOT / "schemas" / "governance-r8" / "v15-r1"
SLICE5_CANDIDATE = "403e40502e9d51740e89ef352b5611711439661e"
SLICE6_BRANCH = "implementation/r8-v15-r1-slice6-seal-local-binding-2026-09-25"

sys.path.insert(0, str(HERE))
slice1 = importlib.import_module("r8_v15_r1_frozen_schema_runtime")
slice4 = importlib.import_module("r8_v15_r1_preseal_validator")
slice5 = importlib.import_module("r8_v15_r1_timeproof_validator")

try:
    sealmod = importlib.import_module("r8_v15_r1_seal_validator")
    IMPORT_ERROR = None
except Exception as exc:
    sealmod = None
    IMPORT_ERROR = exc


def require_seal():
    if sealmod is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return sealmod


def semantic_heads():
    return {
        "csm_head": "csm:1",
        "aim_head": "aim:1",
        "semantic_any_permission_head": "any:1",
        "aim_scope_policy_head": "aimscope:1",
        "resolver_policy_head": "resolver-policy:1",
        "resolver_implementation_registry_head": "rir-head:1",
        "guard_registry_head": "guard-head:1",
        "revocation_head": "rev-head:1",
        "nonce_ledger_head": "nonce-head:1",
        "effect_stream_head": "effect-head:1",
        "configuration_head": "config-head:1",
    }


def resolver_identity():
    return {
        "resolver_policy_digest": "resolver-policy-digest:1",
        "implementation_id": "resolver-impl:1",
        "runtime_identity_digest": "runtime-id:1",
        "workload_identity_digest": "workload-id:1",
        "conformance_suite_digest": "suite:1",
        "conformance_evidence_digest": "conformance-evidence:1",
    }


def ars_entry():
    return {
        "input_id": "input:1",
        "source_id": "source:1",
        "head_digest": "head:1",
        "value_digest": "value:1",
        "schema_semantic_entry_digest": "schema-entry:1",
    }


def authority_read_set(digest="ars:digest:1"):
    return {"entries": [ars_entry()], "authority_read_set_digest": digest}


def dps(
    dps_digest="dps:digest:1",
    ars_digest="ars:digest:1",
    seq=42,
    heads=None,
):
    return {
        "candidate_id": "candidate:1",
        "action_id": "action:1",
        "decision_scope_digest": "scope:1",
        "governance_snapshot_digest": "gov:1",
        "authority_read_set_digest": ars_digest,
        "semantic_state_sequence": seq,
        "semantic_heads": copy.deepcopy(heads or semantic_heads()),
        "rir_record_id": "rir:1",
        "rir_head_digest": "rir-head:1",
        "resolver_identity": resolver_identity(),
        "revocation_state_digest": "rev-state:1",
        "runtime_state_digest": "runtime-state:1",
        "workload_state_digest": "workload-state:1",
        "effect_class": None,
        "decision_preseal_digest": dps_digest,
    }


def att(i):
    return {
        "time_source_id": f"time-source:{i}",
        "source_status_digest": f"source-status:{i}",
        "attestation_digest": f"attestation:{i}",
    }


def qtp(
    dps_digest="dps:digest:1",
    proof_digest="time-proof:digest:1",
    effective_sequence=42,
):
    return {
        "nonce_256bit_hex": "0" * 64,
        "decision_preseal_digest": dps_digest,
        "effective_sequence": effective_sequence,
        "source_attestations": [att(1), att(2)],
        "time_proof_digest": proof_digest,
    }


def seal(
    dps_digest="dps:digest:1",
    time_digest="time-proof:digest:1",
    ars_digest="ars:digest:1",
    seq=42,
    heads=None,
    revocation_head="rev-head:1",
    seal_digest="opaque-seal:digest:1",
):
    return {
        "decision_preseal_digest": dps_digest,
        "time_proof_digest": time_digest,
        "authority_read_set_digest": ars_digest,
        "semantic_state_sequence": seq,
        "semantic_heads": copy.deepcopy(heads or semantic_heads()),
        "revocation_head": revocation_head,
        "seal_digest": seal_digest,
    }


class Slice6FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def validate(self, s=None, p=None, t=None, ars=None):
        m = require_seal()
        return m.validate_verified_state_seal(
            s or seal(),
            decision_preseal=p or dps(),
            authority_read_set=ars or authority_read_set(),
            qualified_time_proof=t or qtp(),
            external_effect_involved=False,
        )

    def test_i6_01_seal_fields_match_schema(self):
        m = require_seal()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        required = schema["$defs"]["VerifiedStateSeal"]["required"]
        self.assertEqual(set(required), set(m.VERIFIED_STATE_SEAL_FIELDS))
        self.assertEqual(len(required), len(m.VERIFIED_STATE_SEAL_FIELDS))

    def test_i6_02_valid_locally_bound_seal_passes(self):
        result = self.validate()
        self.assertTrue(result["locally_valid"])
        self.assertTrue(result["preseal_locally_valid"])
        self.assertTrue(result["time_proof_locally_valid"])

    def test_i6_03_missing_extra_seal_fields_reject(self):
        m = require_seal()
        s = seal()
        s.pop("seal_digest")
        with self.assertRaises(m.SealError) as cm1:
            self.validate(s=s)
        self.assertEqual(cm1.exception.code, "SEAL_FIELD_SET_INVALID")

        s = seal()
        s["extra"] = "x"
        with self.assertRaises(m.SealError) as cm2:
            self.validate(s=s)
        self.assertEqual(cm2.exception.code, "SEAL_FIELD_SET_INVALID")

    def test_i6_04_opaque_digest_strings_gcp_valid(self):
        m = require_seal()
        s = seal(seal_digest="opaque:not-sha")
        self.assertTrue(self.validate(s=s)["locally_valid"])

        for field,bad in (
            ("seal_digest",""),
            ("time_proof_digest","e\u0301"),
            ("revocation_head","\ufdd0"),
        ):
            s = seal()
            s[field] = bad
            with self.subTest(field=field):
                with self.assertRaises(m.SealError) as cm:
                    self.validate(s=s)
                self.assertIn(cm.exception.code, {"SEAL_STRING_INVALID","SEAL_GCP_STRING_INVALID"})

    def test_i6_05_sequence_boundaries_and_types(self):
        m = require_seal()
        for good in (0, 9223372036854775807):
            p = dps(seq=good)
            t = qtp(effective_sequence=good)
            s = seal(seq=good)
            self.assertTrue(self.validate(s=s,p=p,t=t)["locally_valid"])

        for bad in (-1, 9223372036854775808, True, "1", 1.5):
            s = seal()
            s["semantic_state_sequence"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.SealError) as cm:
                    self.validate(s=s)
                self.assertEqual(cm.exception.code, "SEAL_SEQUENCE_INVALID")

    def test_i6_06_semantic_heads_shape_and_values(self):
        m = require_seal()
        for mutation in ("missing","extra","empty","non_nfc"):
            h = semantic_heads()
            if mutation == "missing":
                h.pop("guard_registry_head")
            elif mutation == "extra":
                h["extra"] = "x"
            elif mutation == "empty":
                h["guard_registry_head"] = ""
            else:
                h["guard_registry_head"] = "e\u0301"
            s = seal(heads=h)
            with self.subTest(mutation=mutation):
                with self.assertRaises(m.SealError) as cm:
                    self.validate(s=s)
                self.assertEqual(cm.exception.code, "SEAL_SEMANTIC_HEADS_INVALID")

    def test_i6_07_invalid_preseal_or_read_set_rejects_first(self):
        m = require_seal()
        p = dps(seq=-1)
        with self.assertRaises(m.SealError) as cm1:
            self.validate(p=p)
        self.assertEqual(cm1.exception.code, "SEAL_PRESEAL_INVALID")

        ars = authority_read_set("ars:other")
        with self.assertRaises(m.SealError) as cm2:
            self.validate(ars=ars)
        self.assertEqual(cm2.exception.code, "SEAL_PRESEAL_INVALID")

    def test_i6_08_invalid_time_proof_rejects_first(self):
        m = require_seal()
        t = qtp()
        t["nonce_256bit_hex"] = "g" * 64
        with self.assertRaises(m.SealError) as cm:
            self.validate(t=t)
        self.assertEqual(cm.exception.code, "SEAL_TIME_PROOF_INVALID")

    def test_i6_09_decision_preseal_digest_binding(self):
        m = require_seal()
        s = seal(dps_digest="dps:other")
        with self.assertRaises(m.SealError) as cm:
            self.validate(s=s)
        self.assertEqual(cm.exception.code, "SEAL_PRESEAL_DIGEST_MISMATCH")

    def test_i6_10_time_proof_digest_binding(self):
        m = require_seal()
        s = seal(time_digest="time-proof:other")
        with self.assertRaises(m.SealError) as cm:
            self.validate(s=s)
        self.assertEqual(cm.exception.code, "SEAL_TIME_PROOF_DIGEST_MISMATCH")

    def test_i6_11_authority_read_set_digest_binding(self):
        m = require_seal()
        s = seal(ars_digest="ars:other")
        with self.assertRaises(m.SealError) as cm:
            self.validate(s=s)
        self.assertEqual(cm.exception.code, "SEAL_AUTHORITY_READ_SET_DIGEST_MISMATCH")

    def test_i6_12_semantic_sequence_binding_across_seal_preseal_time(self):
        m = require_seal()

        s = seal(seq=43)
        with self.assertRaises(m.SealError) as cm1:
            self.validate(s=s)
        self.assertEqual(cm1.exception.code, "SEAL_SEMANTIC_SEQUENCE_MISMATCH")

        t = qtp(effective_sequence=43)
        with self.assertRaises(m.SealError) as cm2:
            self.validate(t=t)
        self.assertEqual(cm2.exception.code, "SEAL_TIME_SEQUENCE_MISMATCH")

    def test_i6_13_semantic_heads_and_revocation_binding(self):
        m = require_seal()
        h = semantic_heads()
        h["guard_registry_head"] = "guard-head:other"
        s = seal(heads=h)
        with self.assertRaises(m.SealError) as cm1:
            self.validate(s=s)
        self.assertEqual(cm1.exception.code, "SEAL_SEMANTIC_HEADS_MISMATCH")

        s = seal(revocation_head="rev-head:other")
        with self.assertRaises(m.SealError) as cm2:
            self.validate(s=s)
        self.assertEqual(cm2.exception.code, "SEAL_REVOCATION_HEAD_MISMATCH")

    def test_i6_14_seal_digest_opaque_and_result_non_authoritative(self):
        s = seal(seal_digest="opaque:not-sha256")
        result = self.validate(s=s)
        self.assertTrue(result["locally_valid"])
        self.assertFalse(result["seal_digest_verified"])
        self.assertFalse(result["qualified_time_proven"])
        self.assertFalse(result["nonce_consumed"])
        self.assertFalse(result["current_heads_rechecked"])
        self.assertFalse(result["state_unchanged_at_commit"])
        self.assertFalse(result["current_revocation_proven"])
        self.assertFalse(result["current_runtime_workload_proven"])
        self.assertFalse(result["commit_with_seal_authorized"])
        self.assertFalse(result["effect_intent_committed"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertFalse(result["runtime_qualified"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["deployment_authorized"])
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["policy_authorized"])
        self.assertFalse(result["terminal_authority"])

    def test_i6_15_failure_does_not_poison_subsequent_validation(self):
        m = require_seal()
        bad = seal(revocation_head="wrong")
        with self.assertRaises(m.SealError):
            self.validate(s=bad)
        first = self.validate()
        second = self.validate()
        self.assertEqual(first, second)

    def test_i6_16_dependency_immutability_inherited_tests_and_workflow_coverage(self):
        result = subprocess.run(
            [
                "git","diff","--name-only",SLICE5_CANDIDATE,"HEAD","--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
                "governance-runtime/r8_v15_r1_stc_validator.py",
                "governance-runtime/r8_v15_r1_preseal_validator.py",
                "governance-runtime/r8_v15_r1_timeproof_validator.py",
            ],
            cwd=REPO_ROOT,check=True,text=True,capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

        workflow=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice6.yml").read_text(encoding="utf-8")
        required=(
            SLICE6_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_seal_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice6.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice6.yml",
            "governance-runtime/r8_v15_r1_timeproof_validator.py",
            "governance-runtime/r8_v15_r1_preseal_validator.py",
            "governance-runtime/r8_v15_r1_stc_validator.py",
            "governance-runtime/r8_v15_r1_state_roots.py",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice5.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice4.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice3.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice2.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py",
            "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
            "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
        )
        for item in required:
            with self.subTest(item=item):
                self.assertIn(item,workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
