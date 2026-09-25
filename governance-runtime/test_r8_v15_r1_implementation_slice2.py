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

sys.path.insert(0, str(HERE))

try:
    roots = importlib.import_module("r8_v15_r1_state_roots")
    IMPORT_ERROR = None
except Exception as exc:
    roots = None
    IMPORT_ERROR = exc

slice1 = importlib.import_module("r8_v15_r1_frozen_schema_runtime")

LAS_CANONICAL = (
    b'{"aim4_descriptor_head":"aim:1","aim_scope_policy_head":"aimscope:1",'
    b'"any_scope_permission_head":"any:1","authority_state_machine_root":"asm:1",'
    b'"committed_log_prefix_digest":"log:1","configuration_generation":7,'
    b'"csm5_registry_head":"csm:1","effect_stream_head":"effect:1",'
    b'"guard_registry_head":"guards:1","idempotency_ledger_root":"idem:1",'
    b'"nonce_ledger_head":"nonce:1","prior_certificate_chain_digest":"certs:1",'
    b'"resolver_implementation_registry_head":"rir:1","resolver_policy_head":"resolver:1",'
    b'"revocation_stream_head":"rev:1","semantic_state_sequence":42,'
    b'"stream_head_map_root":"stream:1"}'
)
LAS_SHA = "0cf25eac0681f3f27ae97f15e7172c0f509c29cec34a9abc2c08edaa59155c71"

GGS_CANONICAL = (
    b'{"barrier_index":11,"bootstrap_authorization_root":"auth:g1",'
    b'"committed_log_prefix_digest":"log:g1","configuration_generation":3,'
    b'"constitution_namespace_root":"ns:g1","idempotency_ledger_root":"idem:g1",'
    b'"prior_certificate_chain_digest":"certs:g1"}'
)
GGS_SHA = "bd1a6eca718d0433faeabba571fc5d0e337eaeecd5bb67de8a8457087640d84f"


def require_roots():
    if roots is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return roots


def las_vector():
    return {
        "semantic_state_sequence": 42,
        "committed_log_prefix_digest": "log:1",
        "stream_head_map_root": "stream:1",
        "idempotency_ledger_root": "idem:1",
        "authority_state_machine_root": "asm:1",
        "revocation_stream_head": "rev:1",
        "nonce_ledger_head": "nonce:1",
        "effect_stream_head": "effect:1",
        "csm5_registry_head": "csm:1",
        "aim4_descriptor_head": "aim:1",
        "any_scope_permission_head": "any:1",
        "aim_scope_policy_head": "aimscope:1",
        "resolver_policy_head": "resolver:1",
        "resolver_implementation_registry_head": "rir:1",
        "guard_registry_head": "guards:1",
        "configuration_generation": 7,
        "prior_certificate_chain_digest": "certs:1",
    }


def ggs_vector():
    return {
        "barrier_index": 11,
        "committed_log_prefix_digest": "log:g1",
        "constitution_namespace_root": "ns:g1",
        "bootstrap_authorization_root": "auth:g1",
        "idempotency_ledger_root": "idem:g1",
        "configuration_generation": 3,
        "prior_certificate_chain_digest": "certs:g1",
    }


class Slice2FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def test_i2_01_las_member_list_matches_frozen_schema(self):
        m = require_roots()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            tuple(schema["$defs"]["LASAuthorityStateRoot"]["x-gcp1-preimage-members"]),
            m.LAS_PREIMAGE_MEMBERS,
        )

    def test_i2_02_ggs_member_list_matches_frozen_schema(self):
        m = require_roots()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            tuple(schema["$defs"]["GGSGenesisStateRoot"]["x-gcp1-preimage-members"]),
            m.GGS_PREIMAGE_MEMBERS,
        )

    def test_i2_03_las_known_vector_exact_bytes_and_digest(self):
        m = require_roots()
        result = m.compute_las_authority_state_root(las_vector())
        self.assertEqual(result["canonical_preimage_utf8"], LAS_CANONICAL)
        self.assertEqual(result["state_root_digest"], LAS_SHA)
        self.assertEqual(result["root"]["state_root_digest"], LAS_SHA)

    def test_i2_04_las_mapping_order_does_not_change_root(self):
        m = require_roots()
        original = las_vector()
        reversed_mapping = dict(reversed(list(original.items())))
        a = m.compute_las_authority_state_root(original)
        b = m.compute_las_authority_state_root(reversed_mapping)
        self.assertEqual(a["canonical_preimage_utf8"], b["canonical_preimage_utf8"])
        self.assertEqual(a["state_root_digest"], b["state_root_digest"])

    def test_i2_05_las_missing_extra_and_self_included_member_reject(self):
        m = require_roots()
        for mutation in ("missing", "extra", "self"):
            data = las_vector()
            if mutation == "missing":
                data.pop("guard_registry_head")
            elif mutation == "extra":
                data["unexpected"] = "x"
            else:
                data["state_root_digest"] = "0" * 64
            with self.subTest(mutation=mutation):
                with self.assertRaises(m.StateRootError) as cm:
                    m.compute_las_authority_state_root(data)
                self.assertEqual(cm.exception.code, "ROOT_MEMBER_SET_INVALID")

    def test_i2_06_las_sequence_boundaries_and_types(self):
        m = require_roots()
        for field in ("semantic_state_sequence", "configuration_generation"):
            for good in (0, 9223372036854775807):
                data = las_vector()
                data[field] = good
                m.compute_las_authority_state_root(data)
            for bad in (-1, 9223372036854775808, True, "1", 1.5):
                data = las_vector()
                data[field] = bad
                with self.subTest(field=field, bad=bad):
                    with self.assertRaises(m.StateRootError) as cm:
                        m.compute_las_authority_state_root(data)
                    self.assertEqual(cm.exception.code, "ROOT_SEQUENCE_INVALID")

    def test_i2_07_las_member_mutation_changes_root_and_old_root_fails(self):
        m = require_roots()
        base = m.compute_las_authority_state_root(las_vector())
        mutated = las_vector()
        mutated["guard_registry_head"] = "guards:2"
        changed = m.compute_las_authority_state_root(mutated)
        self.assertNotEqual(base["state_root_digest"], changed["state_root_digest"])

        stale = copy.deepcopy(changed["root"])
        stale["state_root_digest"] = base["state_root_digest"]
        with self.assertRaises(m.StateRootError) as cm:
            m.verify_las_authority_state_root(stale)
        self.assertEqual(cm.exception.code, "STATE_ROOT_DIGEST_MISMATCH")

    def test_i2_08_las_verification_exact_and_malformed_digest(self):
        m = require_roots()
        computed = m.compute_las_authority_state_root(las_vector())
        verified = m.verify_las_authority_state_root(computed["root"])
        self.assertTrue(verified["verified_digest"])
        self.assertEqual(verified["state_root_digest"], LAS_SHA)

        for bad in ("ABC", "g" * 64, "0" * 63, ""):
            root = copy.deepcopy(computed["root"])
            root["state_root_digest"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.StateRootError) as cm:
                    m.verify_las_authority_state_root(root)
                self.assertEqual(cm.exception.code, "ROOT_DIGEST_ENCODING_INVALID")

    def test_i2_09_ggs_known_vector_exact_bytes_and_digest(self):
        m = require_roots()
        result = m.compute_ggs_genesis_state_root(ggs_vector())
        self.assertEqual(result["canonical_preimage_utf8"], GGS_CANONICAL)
        self.assertEqual(result["state_root_digest"], GGS_SHA)
        self.assertEqual(result["root"]["state_root_digest"], GGS_SHA)

    def test_i2_10_ggs_missing_extra_and_self_included_member_reject(self):
        m = require_roots()
        for mutation in ("missing", "extra", "self"):
            data = ggs_vector()
            if mutation == "missing":
                data.pop("constitution_namespace_root")
            elif mutation == "extra":
                data["unexpected"] = "x"
            else:
                data["state_root_digest"] = "0" * 64
            with self.subTest(mutation=mutation):
                with self.assertRaises(m.StateRootError) as cm:
                    m.compute_ggs_genesis_state_root(data)
                self.assertEqual(cm.exception.code, "ROOT_MEMBER_SET_INVALID")

    def test_i2_11_ggs_sequence_boundaries_and_types(self):
        m = require_roots()
        for field in ("barrier_index", "configuration_generation"):
            for good in (0, 9223372036854775807):
                data = ggs_vector()
                data[field] = good
                m.compute_ggs_genesis_state_root(data)
            for bad in (-1, 9223372036854775808, True, "1", 1.5):
                data = ggs_vector()
                data[field] = bad
                with self.subTest(field=field, bad=bad):
                    with self.assertRaises(m.StateRootError) as cm:
                        m.compute_ggs_genesis_state_root(data)
                    self.assertEqual(cm.exception.code, "ROOT_SEQUENCE_INVALID")

    def test_i2_12_opaque_non_sha_component_digests_are_allowed(self):
        m = require_roots()
        data = las_vector()
        data["guard_registry_head"] = "opaque-digest-profile:v1:not-global-sha256"
        result = m.compute_las_authority_state_root(data)
        self.assertRegex(result["state_root_digest"], r"^[0-9a-f]{64}$")

    def test_i2_13_empty_non_nfc_and_noncharacter_component_strings_reject(self):
        m = require_roots()

        empty = las_vector()
        empty["guard_registry_head"] = ""
        with self.assertRaises(m.StateRootError) as cm:
            m.compute_las_authority_state_root(empty)
        self.assertEqual(cm.exception.code, "ROOT_COMPONENT_DIGEST_INVALID")

        non_nfc = las_vector()
        non_nfc["guard_registry_head"] = "e\u0301"
        with self.assertRaises(slice1.GCPError) as cm2:
            m.compute_las_authority_state_root(non_nfc)
        self.assertEqual(cm2.exception.code, "GCP_REJECT_NON_NFC_STRING")

        nonchar = las_vector()
        nonchar["guard_registry_head"] = "\ufdd0"
        with self.assertRaises(slice1.GCPError) as cm3:
            m.compute_las_authority_state_root(nonchar)
        self.assertEqual(cm3.exception.code, "GCP_REJECT_UNICODE_NONCHARACTER_FDD0")

    def test_i2_14_success_metadata_never_self_grants_currentness_or_authority(self):
        m = require_roots()
        for result in (
            m.compute_las_authority_state_root(las_vector()),
            m.compute_ggs_genesis_state_root(ggs_vector()),
        ):
            self.assertEqual(result["authority_effect"], "NONE")
            self.assertFalse(result["runtime_qualified"])
            self.assertFalse(result["release_authorized"])
            self.assertFalse(result["deployment_authorized"])
            self.assertFalse(result["production_authorized"])
            self.assertFalse(result["terminal_authority"])
            forbidden = {"current", "certified", "authority", "authoritative"}
            self.assertTrue(forbidden.isdisjoint(result.keys()))

    def test_i2_15_failure_does_not_poison_subsequent_construction(self):
        m = require_roots()
        bad = las_vector()
        bad["semantic_state_sequence"] = -1
        with self.assertRaises(m.StateRootError):
            m.compute_las_authority_state_root(bad)

        first = m.compute_las_authority_state_root(las_vector())
        second = m.compute_las_authority_state_root(las_vector())
        self.assertEqual(first["canonical_preimage_utf8"], second["canonical_preimage_utf8"])
        self.assertEqual(first["state_root_digest"], second["state_root_digest"])

    def test_i2_16_slice1_and_frozen_schema_bytes_remain_unchanged(self):
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                SLICE1_CANDIDATE,
                "HEAD",
                "--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
