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
SLICE4_CANDIDATE = "3b60d8f14851b755f09a35431c620d6ae594a894"
SLICE5_BRANCH = "implementation/r8-v15-r1-slice5-timeproof-local-validation-2026-09-25"

sys.path.insert(0, str(HERE))
slice4 = importlib.import_module("r8_v15_r1_preseal_validator")

try:
    timemod = importlib.import_module("r8_v15_r1_timeproof_validator")
    IMPORT_ERROR = None
except Exception as exc:
    timemod = None
    IMPORT_ERROR = exc


def require_time():
    if timemod is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return timemod


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


def ars_entry(i=1):
    return {
        "input_id": f"input:{i}",
        "source_id": f"source:{i}",
        "head_digest": f"head:{i}",
        "value_digest": f"value:{i}",
        "schema_semantic_entry_digest": f"schema-entry:{i}",
    }


def authority_read_set(digest="ars:digest:1"):
    return {
        "entries": [ars_entry(1)],
        "authority_read_set_digest": digest,
    }


def decision_preseal(digest="dps:digest:1"):
    return {
        "candidate_id": "candidate:1",
        "action_id": "action:1",
        "decision_scope_digest": "scope:1",
        "governance_snapshot_digest": "governance-snapshot:1",
        "authority_read_set_digest": "ars:digest:1",
        "semantic_state_sequence": 42,
        "semantic_heads": semantic_heads(),
        "rir_record_id": "rir-record:1",
        "rir_head_digest": "rir-head:1",
        "resolver_identity": resolver_identity(),
        "revocation_state_digest": "rev-state:1",
        "runtime_state_digest": "runtime-state:1",
        "workload_state_digest": "workload-state:1",
        "effect_class": None,
        "decision_preseal_digest": digest,
    }


def source_attestation(i=1, source_id=None):
    return {
        "time_source_id": source_id or f"time-source:{i}",
        "source_status_digest": f"source-status:{i}",
        "attestation_digest": f"attestation:{i}",
    }


def qualified_time_proof(
    dps_digest="dps:digest:1",
    attestations=None,
    nonce="0" * 64,
    effective_sequence=42,
    proof_digest="time-proof:digest:1",
):
    return {
        "nonce_256bit_hex": nonce,
        "decision_preseal_digest": dps_digest,
        "effective_sequence": effective_sequence,
        "source_attestations": list(attestations if attestations is not None else [source_attestation(1), source_attestation(2)]),
        "time_proof_digest": proof_digest,
    }


class Slice5FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def validate(self, proof=None, dps=None, ars=None):
        m = require_time()
        return m.validate_qualified_time_proof(
            proof or qualified_time_proof(),
            decision_preseal=dps or decision_preseal(),
            authority_read_set=ars or authority_read_set(),
            external_effect_involved=False,
        )

    def test_i5_01_time_source_attestation_fields_match_schema(self):
        m = require_time()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        required = schema["$defs"]["TimeSourceAttestation"]["required"]
        self.assertEqual(set(required), set(m.TIME_SOURCE_ATTESTATION_FIELDS))
        self.assertEqual(len(required), len(m.TIME_SOURCE_ATTESTATION_FIELDS))

    def test_i5_02_qualified_time_proof_fields_match_schema(self):
        m = require_time()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        required = schema["$defs"]["QualifiedTimeProof"]["required"]
        self.assertEqual(set(required), set(m.QUALIFIED_TIME_PROOF_FIELDS))
        self.assertEqual(len(required), len(m.QUALIFIED_TIME_PROOF_FIELDS))

    def test_i5_03_two_source_attestations_pass(self):
        result = self.validate()
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["source_attestation_count"], 2)

    def test_i5_04_three_source_attestations_pass(self):
        proof = qualified_time_proof(
            attestations=[source_attestation(1), source_attestation(2), source_attestation(3)]
        )
        result = self.validate(proof=proof)
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["source_attestation_count"], 3)

    def test_i5_05_source_attestation_array_cardinality_and_type(self):
        m = require_time()
        for bad in (
            [],
            [source_attestation(1)],
            [source_attestation(1), source_attestation(2), source_attestation(3), source_attestation(4)],
            (source_attestation(1), source_attestation(2)),
        ):
            proof = qualified_time_proof()
            proof["source_attestations"] = bad
            with self.subTest(kind=type(bad).__name__, length=len(bad)):
                with self.assertRaises(m.TimeProofError) as cm:
                    self.validate(proof=proof)
                self.assertEqual(cm.exception.code, "TIME_PROOF_ATTESTATIONS_INVALID")

    def test_i5_06_source_attestation_missing_extra_fields_reject(self):
        m = require_time()

        proof = qualified_time_proof()
        proof["source_attestations"][0] = dict(proof["source_attestations"][0])
        proof["source_attestations"][0].pop("attestation_digest")
        with self.assertRaises(m.TimeProofError) as cm1:
            self.validate(proof=proof)
        self.assertEqual(cm1.exception.code, "TIME_SOURCE_ATTESTATION_FIELD_SET_INVALID")

        proof = qualified_time_proof()
        proof["source_attestations"][0] = dict(proof["source_attestations"][0])
        proof["source_attestations"][0]["extra"] = "x"
        with self.assertRaises(m.TimeProofError) as cm2:
            self.validate(proof=proof)
        self.assertEqual(cm2.exception.code, "TIME_SOURCE_ATTESTATION_FIELD_SET_INVALID")

    def test_i5_07_source_strings_gcp_valid_and_opaque(self):
        m = require_time()

        proof = qualified_time_proof()
        proof["source_attestations"][0]["attestation_digest"] = "opaque:not-global-sha256"
        self.assertTrue(self.validate(proof=proof)["locally_valid"])

        proof = qualified_time_proof()
        proof["source_attestations"][0]["time_source_id"] = ""
        with self.assertRaises(m.TimeProofError) as cm1:
            self.validate(proof=proof)
        self.assertEqual(cm1.exception.code, "TIME_PROOF_STRING_INVALID")

        proof = qualified_time_proof()
        proof["source_attestations"][0]["time_source_id"] = "e\u0301"
        with self.assertRaises(m.TimeProofError) as cm2:
            self.validate(proof=proof)
        self.assertEqual(cm2.exception.code, "TIME_PROOF_GCP_STRING_INVALID")

        proof = qualified_time_proof()
        proof["source_attestations"][0]["source_status_digest"] = "\ufdd0"
        with self.assertRaises(m.TimeProofError) as cm3:
            self.validate(proof=proof)
        self.assertEqual(cm3.exception.code, "TIME_PROOF_GCP_STRING_INVALID")

    def test_i5_08_nonce_exact_64_hex(self):
        m = require_time()
        for good in ("0" * 64, "A" * 64, "aA09" * 16):
            proof = qualified_time_proof(nonce=good)
            self.assertTrue(self.validate(proof=proof)["locally_valid"])

        for bad in ("0" * 63, "0" * 65, "g" * 64, "", None, 123):
            proof = qualified_time_proof()
            proof["nonce_256bit_hex"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.TimeProofError) as cm:
                    self.validate(proof=proof)
                self.assertEqual(cm.exception.code, "TIME_PROOF_NONCE_INVALID")

    def test_i5_09_effective_sequence_boundaries_and_types(self):
        m = require_time()
        for good in (0, 9223372036854775807):
            proof = qualified_time_proof(effective_sequence=good)
            self.assertTrue(self.validate(proof=proof)["locally_valid"])

        for bad in (-1, 9223372036854775808, True, "1", 1.5):
            proof = qualified_time_proof(effective_sequence=42)
            proof["effective_sequence"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.TimeProofError) as cm:
                    self.validate(proof=proof)
                self.assertEqual(cm.exception.code, "TIME_PROOF_SEQUENCE_INVALID")

    def test_i5_10_supplied_preseal_is_revalidated_first(self):
        m = require_time()
        dps = decision_preseal()
        dps["semantic_state_sequence"] = -1
        with self.assertRaises(m.TimeProofError) as cm:
            self.validate(dps=dps)
        self.assertEqual(cm.exception.code, "TIME_PROOF_PRESEAL_INVALID")

        dps = decision_preseal()
        ars = authority_read_set(digest="ars:other")
        with self.assertRaises(m.TimeProofError) as cm2:
            self.validate(dps=dps, ars=ars)
        self.assertEqual(cm2.exception.code, "TIME_PROOF_PRESEAL_INVALID")

    def test_i5_11_decision_preseal_digest_binding(self):
        m = require_time()
        self.assertTrue(self.validate()["locally_valid"])

        proof = qualified_time_proof(dps_digest="dps:other")
        with self.assertRaises(m.TimeProofError) as cm:
            self.validate(proof=proof)
        self.assertEqual(cm.exception.code, "TIME_PROOF_PRESEAL_DIGEST_MISMATCH")

    def test_i5_12_proof_and_preseal_digests_remain_opaque(self):
        proof = qualified_time_proof(
            dps_digest="opaque-dps:not-sha",
            proof_digest="opaque-time-proof:not-sha",
        )
        dps = decision_preseal(digest="opaque-dps:not-sha")
        result = self.validate(proof=proof, dps=dps)
        self.assertTrue(result["locally_valid"])
        self.assertFalse(result["time_proof_digest_verified"])

    def test_i5_13_duplicate_source_ids_are_structurally_allowed_but_not_independence_proof(self):
        proof = qualified_time_proof(
            attestations=[
                source_attestation(1, source_id="same-source"),
                source_attestation(2, source_id="same-source"),
            ]
        )
        result = self.validate(proof=proof)
        self.assertTrue(result["locally_valid"])
        self.assertFalse(result["source_independence_proven"])

    def test_i5_14_result_metadata_is_explicitly_non_authoritative(self):
        result = self.validate()
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertFalse(result["runtime_qualified"])
        self.assertFalse(result["nonce_consumed"])
        self.assertFalse(result["source_status_valid"])
        self.assertFalse(result["source_independence_proven"])
        self.assertFalse(result["freshness_proven"])
        self.assertFalse(result["signature_verified"])
        self.assertFalse(result["time_proof_digest_verified"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["deployment_authorized"])
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["policy_authorized"])
        self.assertFalse(result["terminal_authority"])

    def test_i5_15_failure_does_not_poison_subsequent_validation(self):
        m = require_time()
        bad = qualified_time_proof(nonce="g" * 64)
        with self.assertRaises(m.TimeProofError):
            self.validate(proof=bad)

        first = self.validate()
        second = self.validate()
        self.assertEqual(first, second)

    def test_i5_16_dependency_immutability_inherited_tests_and_workflow_coverage(self):
        result = subprocess.run(
            [
                "git", "diff", "--name-only", SLICE4_CANDIDATE, "HEAD", "--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
                "governance-runtime/r8_v15_r1_stc_validator.py",
                "governance-runtime/r8_v15_r1_preseal_validator.py",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

        workflow = (
            REPO_ROOT / ".github" / "workflows" / "r8-v15-r1-implementation-slice5.yml"
        ).read_text(encoding="utf-8")

        required_paths = (
            SLICE5_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_timeproof_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice5.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice5.yml",
            "governance-runtime/r8_v15_r1_preseal_validator.py",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/r8_v15_r1_state_roots.py",
            "governance-runtime/r8_v15_r1_stc_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice4.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice3.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice2.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py",
            "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
            "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
        )
        for required in required_paths:
            with self.subTest(required=required):
                self.assertIn(required, workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
