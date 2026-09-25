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
SLICE6_CANDIDATE = "a972ddcee333aff063858727739986fe2fd8088d"
SLICE7_BRANCH = "implementation/r8-v15-r1-slice7-effect-intent-local-binding-2026-09-25"

sys.path.insert(0, str(HERE))
slice1 = importlib.import_module("r8_v15_r1_frozen_schema_runtime")

try:
    effectmod = importlib.import_module("r8_v15_r1_effect_intent_validator")
    IMPORT_ERROR = None
except Exception as exc:
    effectmod = None
    IMPORT_ERROR = exc


def require_effect():
    if effectmod is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return effectmod


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


def ars():
    return {
        "entries": [{
            "input_id": "input:1",
            "source_id": "source:1",
            "head_digest": "head:1",
            "value_digest": "value:1",
            "schema_semantic_entry_digest": "schema-entry:1",
        }],
        "authority_read_set_digest": "ars:digest:1",
    }


def dps(effect_class="PAYMENT", dps_digest="dps:digest:1", seq=42, heads=None):
    return {
        "candidate_id": "candidate:1",
        "action_id": "action:1",
        "decision_scope_digest": "scope:1",
        "governance_snapshot_digest": "gov:1",
        "authority_read_set_digest": "ars:digest:1",
        "semantic_state_sequence": seq,
        "semantic_heads": copy.deepcopy(heads or semantic_heads()),
        "rir_record_id": "rir:1",
        "rir_head_digest": "rir-head:1",
        "resolver_identity": resolver_identity(),
        "revocation_state_digest": "rev-state:1",
        "runtime_state_digest": "runtime-state:1",
        "workload_state_digest": "workload-state:1",
        "effect_class": effect_class,
        "decision_preseal_digest": dps_digest,
    }


def att(i):
    return {
        "time_source_id": f"time-source:{i}",
        "source_status_digest": f"source-status:{i}",
        "attestation_digest": f"attestation:{i}",
    }


def qtp(dps_digest="dps:digest:1", time_digest="time-proof:digest:1", seq=42):
    return {
        "nonce_256bit_hex": "0" * 64,
        "decision_preseal_digest": dps_digest,
        "effective_sequence": seq,
        "source_attestations": [att(1), att(2)],
        "time_proof_digest": time_digest,
    }


def seal_obj(
    dps_digest="dps:digest:1",
    time_digest="time-proof:digest:1",
    ars_digest="ars:digest:1",
    seq=42,
    heads=None,
    seal_digest="seal:digest:1",
):
    h = copy.deepcopy(heads or semantic_heads())
    return {
        "decision_preseal_digest": dps_digest,
        "time_proof_digest": time_digest,
        "authority_read_set_digest": ars_digest,
        "semantic_state_sequence": seq,
        "semantic_heads": h,
        "revocation_head": h["revocation_head"],
        "seal_digest": seal_digest,
    }


def intent(
    seal_digest="seal:digest:1",
    dps_digest="dps:digest:1",
    effect_class="PAYMENT",
    state="INTENT_COMMITTED",
):
    return {
        "effect_intent_id": "effect:1",
        "idempotency_key": "idem:1",
        "verified_state_seal_digest": seal_digest,
        "decision_preseal_digest": dps_digest,
        "effect_class": effect_class,
        "payload_digest": "payload:digest:1",
        "provider_id": "provider:1",
        "action": "charge",
        "candidate_scope_digest": "candidate-scope:1",
        "action_scope_digest": "action-scope:1",
        "tenant_scope_digest": "tenant-scope:1",
        "state": state,
    }


class Slice7FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def validate(self, i=None, p=None, a=None, t=None, s=None, ctx=True):
        m = require_effect()
        return m.validate_effect_intent(
            i or intent(),
            decision_preseal=p or dps(),
            authority_read_set=a or ars(),
            qualified_time_proof=t or qtp(),
            verified_state_seal=s or seal_obj(),
            external_effect_involved=ctx,
        )

    def test_i7_01_effect_intent_fields_match_schema(self):
        m = require_effect()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        required = schema["$defs"]["EffectIntent"]["required"]
        self.assertEqual(set(required), set(m.EFFECT_INTENT_FIELDS))
        self.assertEqual(len(required), len(m.EFFECT_INTENT_FIELDS))

    def test_i7_02_valid_locally_bound_intent_passes(self):
        result = self.validate()
        self.assertTrue(result["locally_valid"])
        self.assertTrue(result["seal_locally_valid"])
        self.assertTrue(result["preseal_locally_valid"])
        self.assertTrue(result["time_proof_locally_valid"])

    def test_i7_03_missing_extra_fields_reject(self):
        m = require_effect()
        i = intent()
        i.pop("payload_digest")
        with self.assertRaises(m.EffectIntentError) as cm1:
            self.validate(i=i)
        self.assertEqual(cm1.exception.code, "EFFECT_INTENT_FIELD_SET_INVALID")

        i = intent()
        i["extra"] = "x"
        with self.assertRaises(m.EffectIntentError) as cm2:
            self.validate(i=i)
        self.assertEqual(cm2.exception.code, "EFFECT_INTENT_FIELD_SET_INVALID")

    def test_i7_04_generic_strings_gcp_valid_and_opaque(self):
        m = require_effect()

        i = intent()
        i["payload_digest"] = "opaque:not-sha"
        self.assertTrue(self.validate(i=i)["locally_valid"])

        for field,bad,code in (
            ("provider_id","", "EFFECT_INTENT_STRING_INVALID"),
            ("action","e\u0301","EFFECT_INTENT_GCP_STRING_INVALID"),
            ("tenant_scope_digest","\ufdd0","EFFECT_INTENT_GCP_STRING_INVALID"),
        ):
            i = intent()
            i[field] = bad
            with self.subTest(field=field):
                with self.assertRaises(m.EffectIntentError) as cm:
                    self.validate(i=i)
                self.assertEqual(cm.exception.code, code)

    def test_i7_05_state_must_be_intent_committed(self):
        m = require_effect()
        for bad in ("DISPATCHING", "SUCCEEDED_RECONCILED", "", None):
            i = intent()
            i["state"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.EffectIntentError) as cm:
                    self.validate(i=i)
                self.assertEqual(cm.exception.code, "EFFECT_INTENT_STATE_INVALID")

    def test_i7_06_invalid_preseal_or_read_set_rejects_first(self):
        m = require_effect()
        p = dps(seq=-1)
        with self.assertRaises(m.EffectIntentError) as cm1:
            self.validate(p=p)
        self.assertEqual(cm1.exception.code, "EFFECT_INTENT_PRESEAL_INVALID")

        a = ars()
        a["authority_read_set_digest"] = "ars:other"
        with self.assertRaises(m.EffectIntentError) as cm2:
            self.validate(a=a)
        self.assertEqual(cm2.exception.code, "EFFECT_INTENT_PRESEAL_INVALID")

    def test_i7_07_invalid_time_proof_rejects_first(self):
        m = require_effect()
        t = qtp()
        t["nonce_256bit_hex"] = "g" * 64
        with self.assertRaises(m.EffectIntentError) as cm:
            self.validate(t=t)
        self.assertEqual(cm.exception.code, "EFFECT_INTENT_TIME_PROOF_INVALID")

    def test_i7_08_invalid_verified_state_seal_rejects_first(self):
        m = require_effect()
        s = seal_obj()
        s["semantic_state_sequence"] = 43
        with self.assertRaises(m.EffectIntentError) as cm:
            self.validate(s=s)
        self.assertEqual(cm.exception.code, "EFFECT_INTENT_SEAL_INVALID")

    def test_i7_09_external_effect_context_required_and_boolean(self):
        m = require_effect()
        with self.assertRaises(m.EffectIntentError) as cm1:
            self.validate(ctx=False)
        self.assertEqual(cm1.exception.code, "EFFECT_INTENT_EXTERNAL_EFFECT_REQUIRED")

        with self.assertRaises(m.EffectIntentError) as cm2:
            self.validate(ctx=1)
        self.assertEqual(cm2.exception.code, "EFFECT_INTENT_EFFECT_CONTEXT_INVALID")

    def test_i7_10_verified_state_seal_digest_binding(self):
        m = require_effect()
        i = intent(seal_digest="seal:other")
        with self.assertRaises(m.EffectIntentError) as cm:
            self.validate(i=i)
        self.assertEqual(cm.exception.code, "EFFECT_INTENT_SEAL_DIGEST_MISMATCH")

    def test_i7_11_decision_preseal_digest_binding(self):
        m = require_effect()
        i = intent(dps_digest="dps:other")
        with self.assertRaises(m.EffectIntentError) as cm:
            self.validate(i=i)
        self.assertEqual(cm.exception.code, "EFFECT_INTENT_PRESEAL_DIGEST_MISMATCH")

    def test_i7_12_effect_class_binding_and_nonnull_preseal(self):
        m = require_effect()
        i = intent(effect_class="EMAIL")
        with self.assertRaises(m.EffectIntentError) as cm1:
            self.validate(i=i)
        self.assertEqual(cm1.exception.code, "EFFECT_INTENT_EFFECT_CLASS_MISMATCH")

        p = dps(effect_class=None)
        with self.assertRaises(m.EffectIntentError) as cm2:
            self.validate(p=p)
        self.assertEqual(cm2.exception.code, "EFFECT_INTENT_PRESEAL_INVALID")

    def test_i7_13_opaque_fields_remain_unverified(self):
        i = intent()
        i["idempotency_key"] = "opaque-idem"
        i["payload_digest"] = "opaque-payload"
        i["provider_id"] = "opaque-provider"
        i["action"] = "opaque-action"
        i["candidate_scope_digest"] = "opaque-candidate-scope"
        i["action_scope_digest"] = "opaque-action-scope"
        i["tenant_scope_digest"] = "opaque-tenant-scope"
        result = self.validate(i=i)
        self.assertTrue(result["locally_valid"])
        self.assertFalse(result["idempotency_key_derivation_verified"])
        self.assertFalse(result["payload_digest_verified"])
        self.assertFalse(result["provider_action_authorized"])
        self.assertFalse(result["scope_digests_verified"])

    def test_i7_14_result_is_explicitly_non_authoritative_and_not_completion(self):
        result = self.validate()
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertFalse(result["effect_intent_committed"])
        self.assertFalse(result["commit_with_seal_authorized"])
        self.assertFalse(result["current_heads_rechecked"])
        self.assertFalse(result["state_unchanged_at_commit"])
        self.assertFalse(result["executor_qualified"])
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["external_effect_succeeded"])
        self.assertFalse(result["reconciliation_complete"])
        self.assertFalse(result["runtime_qualified"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["deployment_authorized"])
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["policy_authorized"])
        self.assertFalse(result["terminal_authority"])

    def test_i7_15_failure_does_not_poison_subsequent_validation(self):
        m = require_effect()
        bad = intent(state="SUCCEEDED_RECONCILED")
        with self.assertRaises(m.EffectIntentError):
            self.validate(i=bad)
        first = self.validate()
        second = self.validate()
        self.assertEqual(first, second)

    def test_i7_16_dependency_immutability_inherited_tests_and_workflow_coverage(self):
        result = subprocess.run(
            [
                "git","diff","--name-only",SLICE6_CANDIDATE,"HEAD","--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
                "governance-runtime/r8_v15_r1_stc_validator.py",
                "governance-runtime/r8_v15_r1_preseal_validator.py",
                "governance-runtime/r8_v15_r1_timeproof_validator.py",
                "governance-runtime/r8_v15_r1_seal_validator.py",
            ],
            cwd=REPO_ROOT,check=True,text=True,capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

        workflow=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice7.yml").read_text(encoding="utf-8")
        required=(
            SLICE7_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE7-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_effect_intent_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice7.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE7-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice7.yml",
            "governance-runtime/r8_v15_r1_seal_validator.py",
            "governance-runtime/r8_v15_r1_timeproof_validator.py",
            "governance-runtime/r8_v15_r1_preseal_validator.py",
            "governance-runtime/r8_v15_r1_stc_validator.py",
            "governance-runtime/r8_v15_r1_state_roots.py",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice6.py",
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
