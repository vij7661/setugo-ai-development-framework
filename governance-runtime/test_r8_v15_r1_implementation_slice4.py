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
SLICE3_CANDIDATE = "9b8b519c1f32b675d102b1267511a6a141f39c4a"
SLICE4_BRANCH = "implementation/r8-v15-r1-slice4-preseal-local-validation-2026-09-25"

sys.path.insert(0, str(HERE))
slice1 = importlib.import_module("r8_v15_r1_frozen_schema_runtime")

try:
    preseal = importlib.import_module("r8_v15_r1_preseal_validator")
    IMPORT_ERROR = None
except Exception as exc:
    preseal = None
    IMPORT_ERROR = exc


def require_preseal():
    if preseal is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return preseal


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


def authority_read_set(entries=None, digest="ars:digest:1"):
    return {
        "entries": list(entries if entries is not None else [ars_entry(1)]),
        "authority_read_set_digest": digest,
    }


def decision_preseal(read_set_digest="ars:digest:1", effect_class=None):
    return {
        "candidate_id": "candidate:1",
        "action_id": "action:1",
        "decision_scope_digest": "scope:1",
        "governance_snapshot_digest": "governance-snapshot:1",
        "authority_read_set_digest": read_set_digest,
        "semantic_state_sequence": 42,
        "semantic_heads": semantic_heads(),
        "rir_record_id": "rir-record:1",
        "rir_head_digest": "rir-head:1",
        "resolver_identity": resolver_identity(),
        "revocation_state_digest": "rev-state:1",
        "runtime_state_digest": "runtime-state:1",
        "workload_state_digest": "workload-state:1",
        "effect_class": effect_class,
        "decision_preseal_digest": "opaque-decision-preseal-digest:1",
    }


class Slice4FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def test_i4_01_authority_read_set_entry_fields_match_schema(self):
        m = require_preseal()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["AuthorityReadSetEntry"]["required"]),
            set(m.AUTHORITY_READ_SET_ENTRY_FIELDS),
        )
        self.assertEqual(
            len(schema["$defs"]["AuthorityReadSetEntry"]["required"]),
            len(m.AUTHORITY_READ_SET_ENTRY_FIELDS),
        )

    def test_i4_02_authority_read_set_fields_match_schema(self):
        m = require_preseal()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["AuthorityReadSet"]["required"]),
            set(m.AUTHORITY_READ_SET_FIELDS),
        )
        self.assertEqual(
            len(schema["$defs"]["AuthorityReadSet"]["required"]),
            len(m.AUTHORITY_READ_SET_FIELDS),
        )

    def test_i4_03_decision_preseal_fields_match_schema(self):
        m = require_preseal()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["DecisionPresealContext"]["required"]),
            set(m.DECISION_PRESEAL_FIELDS),
        )
        self.assertEqual(
            len(schema["$defs"]["DecisionPresealContext"]["required"]),
            len(m.DECISION_PRESEAL_FIELDS),
        )

    def test_i4_04_nested_field_sets_match_schema(self):
        m = require_preseal()
        schema = json.loads((SCHEMA_DIR / "runtime-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["$defs"]["SemanticHeads"]["required"]), set(m.SEMANTIC_HEAD_FIELDS))
        self.assertEqual(set(schema["$defs"]["ResolverIdentity"]["required"]), set(m.RESOLVER_IDENTITY_FIELDS))
        self.assertEqual(len(schema["$defs"]["SemanticHeads"]["required"]), len(m.SEMANTIC_HEAD_FIELDS))
        self.assertEqual(len(schema["$defs"]["ResolverIdentity"]["required"]), len(m.RESOLVER_IDENTITY_FIELDS))

    def test_i4_05_valid_one_and_multi_entry_read_sets_pass_empty_rejects(self):
        m = require_preseal()
        one = m.validate_authority_read_set(authority_read_set())
        self.assertTrue(one["locally_valid"])
        multi = m.validate_authority_read_set(authority_read_set([ars_entry(1), ars_entry(2)]))
        self.assertTrue(multi["locally_valid"])

        with self.assertRaises(m.PresealError) as cm:
            m.validate_authority_read_set(authority_read_set([]))
        self.assertEqual(cm.exception.code, "ARS_ENTRIES_INVALID")

    def test_i4_06_read_set_and_entry_missing_extra_fields_reject(self):
        m = require_preseal()

        rs = authority_read_set()
        rs.pop("authority_read_set_digest")
        with self.assertRaises(m.PresealError) as cm1:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm1.exception.code, "ARS_FIELD_SET_INVALID")

        rs = authority_read_set()
        rs["extra"] = "x"
        with self.assertRaises(m.PresealError) as cm2:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm2.exception.code, "ARS_FIELD_SET_INVALID")

        rs = authority_read_set()
        rs["entries"][0] = dict(rs["entries"][0])
        rs["entries"][0].pop("value_digest")
        with self.assertRaises(m.PresealError) as cm3:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm3.exception.code, "ARS_ENTRY_FIELD_SET_INVALID")

        rs = authority_read_set()
        rs["entries"][0] = dict(rs["entries"][0])
        rs["entries"][0]["extra"] = "x"
        with self.assertRaises(m.PresealError) as cm4:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm4.exception.code, "ARS_ENTRY_FIELD_SET_INVALID")

    def test_i4_07_generic_strings_opaque_nonempty_and_gcp_valid(self):
        m = require_preseal()

        rs = authority_read_set()
        rs["authority_read_set_digest"] = "opaque:not-global-sha256"
        self.assertTrue(m.validate_authority_read_set(rs)["locally_valid"])

        rs = authority_read_set()
        rs["entries"][0] = dict(rs["entries"][0])
        rs["entries"][0]["input_id"] = ""
        with self.assertRaises(m.PresealError) as cm1:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm1.exception.code, "PRESEAL_STRING_INVALID")

        rs = authority_read_set()
        rs["entries"][0] = dict(rs["entries"][0])
        rs["entries"][0]["input_id"] = "e\u0301"
        with self.assertRaises(slice1.GCPError) as cm2:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm2.exception.code, "GCP_REJECT_NON_NFC_STRING")

        rs = authority_read_set()
        rs["entries"][0] = dict(rs["entries"][0])
        rs["entries"][0]["head_digest"] = "\ufdd0"
        with self.assertRaises(slice1.GCPError) as cm3:
            m.validate_authority_read_set(rs)
        self.assertEqual(cm3.exception.code, "GCP_REJECT_UNICODE_NONCHARACTER_FDD0")

    def test_i4_08_semantic_state_sequence_boundaries_and_types(self):
        m = require_preseal()
        rs = authority_read_set()

        for good in (0, 9223372036854775807):
            dps = decision_preseal()
            dps["semantic_state_sequence"] = good
            m.validate_decision_preseal_context(
                dps,
                authority_read_set=rs,
                external_effect_involved=False,
            )

        for bad in (-1, 9223372036854775808, True, "1", 1.5):
            dps = decision_preseal()
            dps["semantic_state_sequence"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(m.PresealError) as cm:
                    m.validate_decision_preseal_context(
                        dps,
                        authority_read_set=rs,
                        external_effect_involved=False,
                    )
                self.assertEqual(cm.exception.code, "PRESEAL_SEQUENCE_INVALID")

    def test_i4_09_no_effect_sentinel_rules(self):
        m = require_preseal()
        rs = authority_read_set()

        result = m.validate_decision_preseal_context(
            decision_preseal(effect_class=None),
            authority_read_set=rs,
            external_effect_involved=False,
        )
        self.assertTrue(result["locally_valid"])

        with self.assertRaises(m.PresealError) as cm:
            m.validate_decision_preseal_context(
                decision_preseal(effect_class="PAYMENT"),
                authority_read_set=rs,
                external_effect_involved=False,
            )
        self.assertEqual(cm.exception.code, "PRESEAL_EFFECT_CLASS_INVALID")

    def test_i4_10_effect_sentinel_rules_and_context_type(self):
        m = require_preseal()
        rs = authority_read_set()

        result = m.validate_decision_preseal_context(
            decision_preseal(effect_class="PAYMENT"),
            authority_read_set=rs,
            external_effect_involved=True,
        )
        self.assertTrue(result["locally_valid"])

        for bad_effect in (None, ""):
            with self.subTest(bad_effect=bad_effect):
                with self.assertRaises(m.PresealError) as cm:
                    m.validate_decision_preseal_context(
                        decision_preseal(effect_class=bad_effect),
                        authority_read_set=rs,
                        external_effect_involved=True,
                    )
                self.assertEqual(cm.exception.code, "PRESEAL_EFFECT_CLASS_INVALID")

        with self.assertRaises(m.PresealError) as cm2:
            m.validate_decision_preseal_context(
                decision_preseal(effect_class="PAYMENT"),
                authority_read_set=rs,
                external_effect_involved=1,
            )
        self.assertEqual(cm2.exception.code, "PRESEAL_EFFECT_CONTEXT_INVALID")

    def test_i4_11_read_set_digest_must_match_preseal(self):
        m = require_preseal()

        rs = authority_read_set(digest="ars:digest:1")
        m.validate_decision_preseal_context(
            decision_preseal(read_set_digest="ars:digest:1"),
            authority_read_set=rs,
            external_effect_involved=False,
        )

        with self.assertRaises(m.PresealError) as cm:
            m.validate_decision_preseal_context(
                decision_preseal(read_set_digest="ars:digest:other"),
                authority_read_set=rs,
                external_effect_involved=False,
            )
        self.assertEqual(cm.exception.code, "PRESEAL_AUTHORITY_READ_SET_DIGEST_MISMATCH")

    def test_i4_12_semantic_heads_shape_and_string_rules(self):
        m = require_preseal()
        rs = authority_read_set()

        for mutation in ("missing", "extra", "empty", "non_nfc"):
            dps = decision_preseal()
            heads = copy.deepcopy(dps["semantic_heads"])
            if mutation == "missing":
                heads.pop("guard_registry_head")
            elif mutation == "extra":
                heads["extra"] = "x"
            elif mutation == "empty":
                heads["guard_registry_head"] = ""
            else:
                heads["guard_registry_head"] = "e\u0301"
            dps["semantic_heads"] = heads
            with self.subTest(mutation=mutation):
                if mutation == "non_nfc":
                    with self.assertRaises(slice1.GCPError) as cm:
                        m.validate_decision_preseal_context(
                            dps, authority_read_set=rs, external_effect_involved=False
                        )
                    self.assertEqual(cm.exception.code, "GCP_REJECT_NON_NFC_STRING")
                else:
                    with self.assertRaises(m.PresealError) as cm:
                        m.validate_decision_preseal_context(
                            dps, authority_read_set=rs, external_effect_involved=False
                        )
                    self.assertEqual(
                        cm.exception.code,
                        "PRESEAL_SEMANTIC_HEADS_INVALID" if mutation in ("missing", "extra") else "PRESEAL_STRING_INVALID",
                    )

    def test_i4_13_resolver_identity_shape_and_string_rules(self):
        m = require_preseal()
        rs = authority_read_set()

        dps = decision_preseal()
        dps["resolver_identity"] = dict(dps["resolver_identity"])
        dps["resolver_identity"].pop("conformance_evidence_digest")
        with self.assertRaises(m.PresealError) as cm1:
            m.validate_decision_preseal_context(dps, authority_read_set=rs, external_effect_involved=False)
        self.assertEqual(cm1.exception.code, "PRESEAL_RESOLVER_IDENTITY_INVALID")

        dps = decision_preseal()
        dps["resolver_identity"] = dict(dps["resolver_identity"])
        dps["resolver_identity"]["extra"] = "x"
        with self.assertRaises(m.PresealError) as cm2:
            m.validate_decision_preseal_context(dps, authority_read_set=rs, external_effect_involved=False)
        self.assertEqual(cm2.exception.code, "PRESEAL_RESOLVER_IDENTITY_INVALID")

        dps = decision_preseal()
        dps["resolver_identity"] = dict(dps["resolver_identity"])
        dps["resolver_identity"]["runtime_identity_digest"] = ""
        with self.assertRaises(m.PresealError) as cm3:
            m.validate_decision_preseal_context(dps, authority_read_set=rs, external_effect_involved=False)
        self.assertEqual(cm3.exception.code, "PRESEAL_STRING_INVALID")

        dps = decision_preseal()
        dps["resolver_identity"] = dict(dps["resolver_identity"])
        dps["resolver_identity"]["workload_identity_digest"] = "\ufdd0"
        with self.assertRaises(slice1.GCPError) as cm4:
            m.validate_decision_preseal_context(dps, authority_read_set=rs, external_effect_involved=False)
        self.assertEqual(cm4.exception.code, "GCP_REJECT_UNICODE_NONCHARACTER_FDD0")

    def test_i4_14_preseal_digest_opaque_and_result_non_authoritative(self):
        m = require_preseal()
        rs = authority_read_set()
        dps = decision_preseal()
        dps["decision_preseal_digest"] = "opaque:not-global-sha256"

        result = m.validate_decision_preseal_context(
            dps,
            authority_read_set=rs,
            external_effect_involved=False,
        )
        self.assertTrue(result["locally_valid"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertFalse(result["runtime_qualified"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["deployment_authorized"])
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["policy_authorized"])
        self.assertFalse(result["terminal_authority"])
        self.assertFalse(result["read_set_completeness_proven"])
        self.assertFalse(result["decision_preseal_digest_verified"])
        forbidden = {"current", "certified", "authority", "authoritative"}
        self.assertTrue(forbidden.isdisjoint(result.keys()))

    def test_i4_15_failure_does_not_poison_subsequent_validation(self):
        m = require_preseal()
        rs = authority_read_set()

        bad = decision_preseal(effect_class="PAYMENT")
        with self.assertRaises(m.PresealError):
            m.validate_decision_preseal_context(
                bad, authority_read_set=rs, external_effect_involved=False
            )

        first = m.validate_decision_preseal_context(
            decision_preseal(), authority_read_set=rs, external_effect_involved=False
        )
        second = m.validate_decision_preseal_context(
            decision_preseal(), authority_read_set=rs, external_effect_involved=False
        )
        self.assertEqual(first, second)

    def test_i4_16_dependency_immutability_inherited_tests_and_workflow_coverage(self):
        result = subprocess.run(
            [
                "git", "diff", "--name-only", SLICE3_CANDIDATE, "HEAD", "--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
                "governance-runtime/r8_v15_r1_stc_validator.py",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

        workflow = (
            REPO_ROOT / ".github" / "workflows" / "r8-v15-r1-implementation-slice4.yml"
        ).read_text(encoding="utf-8")
        for required in (
            SLICE4_BRANCH,
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-PREREGISTRATION.md",
            "governance-runtime/r8_v15_r1_preseal_validator.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice4.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice4.yml",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        ):
            with self.subTest(required=required):
                self.assertIn(required, workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
