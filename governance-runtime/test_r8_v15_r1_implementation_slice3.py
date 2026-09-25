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
FROZEN_SCHEMA_CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1_CANDIDATE = "fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE2_CANDIDATE = "6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
SLICE3_BRANCH = "implementation/r8-v15-r1-slice3-stc-local-validation-2026-09-25"

sys.path.insert(0, str(HERE))
slice1 = importlib.import_module("r8_v15_r1_frozen_schema_runtime")
slice2 = importlib.import_module("r8_v15_r1_state_roots")

try:
    stcmod = importlib.import_module("r8_v15_r1_stc_validator")
    IMPORT_ERROR = None
except Exception as exc:
    stcmod = None
    IMPORT_ERROR = exc


def require_stc():
    if stcmod is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return stcmod


def semantic_heads():
    return {
        "csm_head": "csm:1",
        "aim_head": "aim:1",
        "semantic_any_permission_head": "any:1",
        "aim_scope_policy_head": "aimscope:1",
        "resolver_policy_head": "resolver:1",
        "resolver_implementation_registry_head": "rir:1",
        "guard_registry_head": "guards:1",
        "revocation_head": "rev:1",
        "nonce_ledger_head": "nonce:1",
        "effect_stream_head": "effect:1",
        "configuration_head": "config:1",
    }


def las_root():
    preimage = {
        "semantic_state_sequence": 42,
        "committed_log_prefix_digest": "log:las",
        "stream_head_map_root": "stream:las",
        "idempotency_ledger_root": "idem:las",
        "authority_state_machine_root": "asm:las",
        "revocation_stream_head": "rev:las",
        "nonce_ledger_head": "nonce:las",
        "effect_stream_head": "effect:las",
        "csm5_registry_head": "csm:las",
        "aim4_descriptor_head": "aim:las",
        "any_scope_permission_head": "any:las",
        "aim_scope_policy_head": "aimscope:las",
        "resolver_policy_head": "resolver:las",
        "resolver_implementation_registry_head": "rir:las",
        "guard_registry_head": "guards:las",
        "configuration_generation": 7,
        "prior_certificate_chain_digest": "certs:las",
    }
    return slice2.compute_las_authority_state_root(preimage)["root"]


def ggs_preimage():
    return {
        "barrier_index": 11,
        "committed_log_prefix_digest": "log:ggs",
        "constitution_namespace_root": "ns:ggs",
        "bootstrap_authorization_root": "auth:ggs",
        "idempotency_ledger_root": "idem:ggs",
        "configuration_generation": 3,
        "prior_certificate_chain_digest": "certs:ggs",
    }


def ggs_root(preimage=None):
    return slice2.compute_ggs_genesis_state_root(preimage or ggs_preimage())["root"]


def valid_las_stc():
    root = las_root()
    return {
        "system_id": "LAS-3",
        "rotation_id": "rotation:las:1",
        "transition_id": "transition:las:1",
        "rotation_prepare_certificate_digest": "rpcert:las:1",
        "old_configuration_generation": 7,
        "old_configuration_digest": "oldcfg:las:1",
        "proposed_new_configuration_digest": "newcfg:las:1",
        "barrier_snapshot_index": 42,
        "committed_log_prefix_digest": "log:las",
        "highest_seen_term": 8,
        "highest_committed_index": 42,
        "highest_applied_index": 42,
        "last_committed_entry_digest": "entry:las:42",
        "state_root_digest": root["state_root_digest"],
        "stream_head_map_root_digest": "stream:las",
        "idempotency_dedup_ledger_root_digest": "idem:las",
        "prior_certificate_chain_digest": "certs:las",
        "ggs_namespace_root_digest": None,
        "ggs_authorization_root_digest": None,
        "semantic_state_binding_required": True,
        "semantic_heads": semantic_heads(),
        "ggs_genesis_state_root": None,
        "stc_digest": "opaque-stc-digest:las:1",
    }


def valid_ggs_stc(binding=False):
    root = ggs_root()
    return {
        "system_id": "GGS-3",
        "rotation_id": "rotation:ggs:1",
        "transition_id": "transition:ggs:1",
        "rotation_prepare_certificate_digest": "rpcert:ggs:1",
        "old_configuration_generation": root["configuration_generation"],
        "old_configuration_digest": "oldcfg:ggs:1",
        "proposed_new_configuration_digest": "newcfg:ggs:1",
        "barrier_snapshot_index": root["barrier_index"],
        "committed_log_prefix_digest": root["committed_log_prefix_digest"],
        "highest_seen_term": 4,
        "highest_committed_index": root["barrier_index"],
        "highest_applied_index": None,
        "last_committed_entry_digest": "entry:ggs:11",
        "state_root_digest": root["state_root_digest"],
        "stream_head_map_root_digest": None,
        "idempotency_dedup_ledger_root_digest": root["idempotency_ledger_root"],
        "prior_certificate_chain_digest": root["prior_certificate_chain_digest"],
        "ggs_namespace_root_digest": root["constitution_namespace_root"],
        "ggs_authorization_root_digest": root["bootstrap_authorization_root"],
        "semantic_state_binding_required": binding,
        "semantic_heads": semantic_heads() if binding else None,
        "ggs_genesis_state_root": root,
        "stc_digest": "opaque-stc-digest:ggs:1",
    }


class Slice3FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def test_i3_01_stc_required_fields_match_frozen_schema(self):
        m = require_stc()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["StateTransferCertificate"]["required"]),
            set(m.STC_REQUIRED_FIELDS),
        )
        self.assertEqual(
            len(schema["$defs"]["StateTransferCertificate"]["required"]),
            len(m.STC_REQUIRED_FIELDS),
        )

    def test_i3_02_semantic_heads_fields_match_frozen_schema(self):
        m = require_stc()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["SemanticHeads"]["required"]),
            set(m.SEMANTIC_HEAD_FIELDS),
        )
        self.assertEqual(
            len(schema["$defs"]["SemanticHeads"]["required"]),
            len(m.SEMANTIC_HEAD_FIELDS),
        )

    def test_i3_03_valid_las_local_stc_passes(self):
        m = require_stc()
        result = m.validate_state_transfer_certificate(valid_las_stc())
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["system_id"], "LAS-3")

    def test_i3_04_las_conditional_failures_reject(self):
        m = require_stc()
        mutations = []

        x = valid_las_stc()
        x["semantic_state_binding_required"] = False
        x["semantic_heads"] = None
        mutations.append(("false_binding", x))

        x = valid_las_stc()
        x["semantic_heads"] = None
        mutations.append(("null_heads", x))

        x = valid_las_stc()
        x["ggs_namespace_root_digest"] = "ns:should-not-exist"
        mutations.append(("ggs_namespace_present", x))

        x = valid_las_stc()
        x["ggs_authorization_root_digest"] = "auth:should-not-exist"
        mutations.append(("ggs_auth_present", x))

        x = valid_las_stc()
        x["ggs_genesis_state_root"] = ggs_root()
        mutations.append(("ggs_root_present", x))

        x = valid_las_stc()
        x["stream_head_map_root_digest"] = None
        mutations.append(("stream_head_missing", x))

        for name, stc in mutations:
            with self.subTest(name=name):
                with self.assertRaises(m.STCError) as cm:
                    m.validate_state_transfer_certificate(stc)
                self.assertEqual(cm.exception.code, "STC_CONDITIONAL_INVALID")

    def test_i3_05_valid_ggs_without_semantic_binding_passes(self):
        m = require_stc()
        result = m.validate_state_transfer_certificate(valid_ggs_stc(binding=False))
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["system_id"], "GGS-3")

    def test_i3_06_valid_ggs_with_semantic_binding_passes(self):
        m = require_stc()
        result = m.validate_state_transfer_certificate(valid_ggs_stc(binding=True))
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["system_id"], "GGS-3")

    def test_i3_07_ggs_nested_field_mismatch_rejects(self):
        m = require_stc()
        cases = [
            ("barrier_index", "barrier_snapshot_index", 12),
            ("committed_log_prefix_digest", "committed_log_prefix_digest", "log:other"),
            ("constitution_namespace_root", "ggs_namespace_root_digest", "ns:other"),
            ("bootstrap_authorization_root", "ggs_authorization_root_digest", "auth:other"),
            ("idempotency_ledger_root", "idempotency_dedup_ledger_root_digest", "idem:other"),
            ("configuration_generation", "old_configuration_generation", 4),
            ("prior_certificate_chain_digest", "prior_certificate_chain_digest", "certs:other"),
        ]
        for nested_field, stc_field, changed in cases:
            pre = ggs_preimage()
            pre[nested_field] = changed
            changed_root = ggs_root(pre)
            stc = valid_ggs_stc()
            stc["ggs_genesis_state_root"] = changed_root
            stc["state_root_digest"] = changed_root["state_root_digest"]
            with self.subTest(field=nested_field):
                with self.assertRaises(m.STCError) as cm:
                    m.validate_state_transfer_certificate(stc)
                self.assertEqual(cm.exception.code, "STC_GGS_ROOT_MISMATCH")

        stc = valid_ggs_stc()
        stc["state_root_digest"] = "0" * 64
        with self.assertRaises(m.STCError) as cm:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm.exception.code, "STC_GGS_ROOT_MISMATCH")

    def test_i3_08_ggs_nested_root_digest_invalid_rejects(self):
        m = require_stc()

        stc = valid_ggs_stc()
        stc["ggs_genesis_state_root"] = copy.deepcopy(stc["ggs_genesis_state_root"])
        stc["ggs_genesis_state_root"]["state_root_digest"] = "0" * 64
        stc["state_root_digest"] = "0" * 64
        with self.assertRaises(m.STCError) as cm:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm.exception.code, "STC_GGS_ROOT_INVALID")

        stc = valid_ggs_stc()
        stc["ggs_genesis_state_root"] = copy.deepcopy(stc["ggs_genesis_state_root"])
        stc["ggs_genesis_state_root"]["state_root_digest"] = "ABC"
        stc["state_root_digest"] = "ABC"
        with self.assertRaises(m.STCError) as cm2:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm2.exception.code, "STC_ROOT_DIGEST_ENCODING_INVALID")

    def test_i3_09_sequence_boundaries_and_types(self):
        m = require_stc()
        fields = (
            "old_configuration_generation",
            "barrier_snapshot_index",
            "highest_seen_term",
            "highest_committed_index",
        )
        for field in fields:
            for good in (0, 9223372036854775807):
                stc = valid_las_stc()
                stc[field] = good
                m.validate_state_transfer_certificate(stc)
            for bad in (-1, 9223372036854775808, True, "1", 1.5):
                stc = valid_las_stc()
                stc[field] = bad
                with self.subTest(field=field, bad=bad):
                    with self.assertRaises(m.STCError) as cm:
                        m.validate_state_transfer_certificate(stc)
                    self.assertEqual(cm.exception.code, "STC_SEQUENCE_INVALID")

    def test_i3_10_highest_applied_index_nullable_or_sequence_only(self):
        m = require_stc()
        for good in (None, 0, 9223372036854775807):
            stc = valid_las_stc()
            stc["highest_applied_index"] = good
            m.validate_state_transfer_certificate(stc)

        for bad in (-1, 9223372036854775808, True, "1", 1.5):
            stc = valid_las_stc()
            stc["highest_applied_index"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.STCError) as cm:
                    m.validate_state_transfer_certificate(stc)
                self.assertEqual(cm.exception.code, "STC_SEQUENCE_INVALID")

    def test_i3_11_generic_ids_and_digests_are_nonempty_gcp_valid_but_opaque(self):
        m = require_stc()

        stc = valid_las_stc()
        stc["rotation_prepare_certificate_digest"] = "opaque:not-global-sha256"
        m.validate_state_transfer_certificate(stc)

        for field in ("rotation_id", "rotation_prepare_certificate_digest"):
            stc = valid_las_stc()
            stc[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(m.STCError) as cm:
                    m.validate_state_transfer_certificate(stc)
                self.assertEqual(cm.exception.code, "STC_STRING_INVALID")

        stc = valid_las_stc()
        stc["rotation_id"] = "e\u0301"
        with self.assertRaises(slice1.GCPError) as cm2:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm2.exception.code, "GCP_REJECT_NON_NFC_STRING")

        stc = valid_las_stc()
        stc["old_configuration_digest"] = "\ufdd0"
        with self.assertRaises(slice1.GCPError) as cm3:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm3.exception.code, "GCP_REJECT_UNICODE_NONCHARACTER_FDD0")

    def test_i3_12_root_digest_encoding_strict_stc_digest_opaque(self):
        m = require_stc()

        stc = valid_las_stc()
        stc["stc_digest"] = "opaque-stc-identity-not-global-sha"
        m.validate_state_transfer_certificate(stc)

        for bad in ("ABC", "g" * 64, "0" * 63, ""):
            stc = valid_las_stc()
            stc["state_root_digest"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.STCError) as cm:
                    m.validate_state_transfer_certificate(stc)
                self.assertEqual(cm.exception.code, "STC_ROOT_DIGEST_ENCODING_INVALID")

    def test_i3_13_semantic_heads_exact_shape_and_values(self):
        m = require_stc()

        stc = valid_las_stc()
        stc["semantic_heads"] = copy.deepcopy(stc["semantic_heads"])
        stc["semantic_heads"].pop("guard_registry_head")
        with self.assertRaises(m.STCError) as cm1:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm1.exception.code, "SEMANTIC_HEADS_INVALID")

        stc = valid_las_stc()
        stc["semantic_heads"] = copy.deepcopy(stc["semantic_heads"])
        stc["semantic_heads"]["extra"] = "x"
        with self.assertRaises(m.STCError) as cm2:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm2.exception.code, "SEMANTIC_HEADS_INVALID")

        stc = valid_las_stc()
        stc["semantic_heads"] = copy.deepcopy(stc["semantic_heads"])
        stc["semantic_heads"]["guard_registry_head"] = ""
        with self.assertRaises(m.STCError) as cm3:
            m.validate_state_transfer_certificate(stc)
        self.assertEqual(cm3.exception.code, "STC_STRING_INVALID")

    def test_i3_14_validation_metadata_is_non_authoritative(self):
        m = require_stc()
        for result in (
            m.validate_state_transfer_certificate(valid_las_stc()),
            m.validate_state_transfer_certificate(valid_ggs_stc(binding=True)),
        ):
            self.assertEqual(result["authority_effect"], "NONE")
            self.assertFalse(result["runtime_qualified"])
            self.assertFalse(result["release_authorized"])
            self.assertFalse(result["deployment_authorized"])
            self.assertFalse(result["production_authorized"])
            self.assertFalse(result["policy_authorized"])
            self.assertFalse(result["terminal_authority"])
            forbidden = {"current", "certified", "authority", "authoritative"}
            self.assertTrue(forbidden.isdisjoint(result.keys()))

    def test_i3_15_failure_does_not_poison_subsequent_validation(self):
        m = require_stc()
        bad = valid_las_stc()
        bad["semantic_state_binding_required"] = False
        bad["semantic_heads"] = None
        with self.assertRaises(m.STCError):
            m.validate_state_transfer_certificate(bad)

        self.assertTrue(m.validate_state_transfer_certificate(valid_las_stc())["locally_valid"])
        self.assertTrue(m.validate_state_transfer_certificate(valid_ggs_stc())["locally_valid"])

    def test_i3_16_dependency_regressions_immutability_and_workflow_coverage(self):
        # Directly close the two Slice 2 review test-depth gaps before Slice 3 relies on GGS verify.
        computed = slice2.compute_ggs_genesis_state_root(ggs_preimage())
        verified = slice2.verify_ggs_genesis_state_root(computed["root"])
        self.assertTrue(verified["verified_digest"])
        self.assertEqual(verified["authority_effect"], "NONE")
        self.assertFalse(verified["runtime_qualified"])
        self.assertFalse(verified["release_authorized"])
        self.assertFalse(verified["deployment_authorized"])
        self.assertFalse(verified["production_authorized"])
        self.assertFalse(verified["policy_authorized"])
        self.assertFalse(verified["terminal_authority"])

        mismatch = copy.deepcopy(computed["root"])
        mismatch["state_root_digest"] = "0" * 64
        with self.assertRaises(slice2.StateRootError) as cm1:
            slice2.verify_ggs_genesis_state_root(mismatch)
        self.assertEqual(cm1.exception.code, "STATE_ROOT_DIGEST_MISMATCH")

        malformed = copy.deepcopy(computed["root"])
        malformed["state_root_digest"] = "ABC"
        with self.assertRaises(slice2.StateRootError) as cm2:
            slice2.verify_ggs_genesis_state_root(malformed)
        self.assertEqual(cm2.exception.code, "ROOT_DIGEST_ENCODING_INVALID")

        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                SLICE2_CANDIDATE,
                "HEAD",
                "--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

        workflow = (
            REPO_ROOT / ".github" / "workflows" / "r8-v15-r1-implementation-slice3.yml"
        ).read_text(encoding="utf-8")
        for required in (
            SLICE3_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_stc_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice3.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice3.yml",
            "governance-runtime/r8_v15_r1_state_roots.py",
        ):
            with self.subTest(required=required):
                self.assertIn(required, workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
