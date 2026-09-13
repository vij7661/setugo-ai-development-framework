from __future__ import annotations

import copy
import unittest

from v24_v6_r16_successor import (
    REQUIRED_R16_PROBES,
    construction_frontier,
    digest,
    validate_r16_external_evidence,
)

COMMIT = "1" * 40
TREE = "2" * 40
ENV = "3" * 64


def source_rows():
    return [
        {
            "path": "review/v24/r16_native_observer.c",
            "git_blob_sha1": "4" * 40,
            "raw_sha256": "5" * 64,
            "role": "NATIVE_AUTHORITY_SOURCE",
        },
        {
            "path": "review/v24/r16_kernel_confinement.c",
            "git_blob_sha1": "6" * 40,
            "raw_sha256": "7" * 64,
            "role": "NATIVE_BUILD_SUPPORT",
        },
        {
            "path": "review/v24/r16_trusted_external_oracle.py",
            "git_blob_sha1": "8" * 40,
            "raw_sha256": "9" * 64,
            "role": "TRUSTED_ORACLE_SOURCE",
        },
    ]


def source_set_digest(rows):
    normalized = [
        {
            "path": row["path"],
            "git_blob_sha1": row["git_blob_sha1"],
            "raw_sha256": row["raw_sha256"],
            "role": row["role"],
        }
        for row in rows
    ]
    normalized.sort(key=lambda x: x["path"])
    return digest(normalized)


def record(probe_id: str):
    row = {
        "probe_id": probe_id,
        "execution_state": "EXECUTED",
        "terminal_result": "PASS",
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "evidence_digest": "a" * 64,
        "run_id": "run-1",
        "round_id": "round-1",
        "witness_id": "r16-external-witness",
        "witness_control_domain": "R16-EXTERNAL-AUTHORITY",
        "witness_authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_authored": False,
    }
    row["record_digest"] = digest(row)
    return row


def bundle():
    rows = source_rows()
    records = [record(x) for x in sorted(REQUIRED_R16_PROBES)]
    return {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "environment_digest": ENV,
        "native_confinement": {
            "kernel_or_fd_aware_enforcement": True,
            "cwd_realpath_authoritative": False,
            "dir_fd_openat_covered": True,
            "inherited_and_duplicated_fd_covered": True,
            "post_import_semantic_probe_passed": True,
            "policy_digest": "b" * 64,
            "kernel_evidence_digest": "c" * 64,
            "surface_inventory_digest": "d" * 64,
        },
        "secret_separation": {
            "authority_secret_in_candidate_address_space": False,
            "candidate_can_compute_authority_mac": False,
            "candidate_observation_role": "UNTRUSTED_OBSERVATION_ONLY",
            "parent_authentication_material_origin": "PARENT_ONLY_POST_FORK",
            "full_child_memory_knowledge_forgery_rejected": True,
            "separation_evidence_digest": "e" * 64,
        },
        "trusted_scenario_library": {
            "path": "review/v24/r16_trusted_scenario_library.py",
            "git_blob_sha1": "f" * 40,
            "raw_sha256": "0" * 64,
            "verified_before_import": True,
        },
        "trusted_native_sources": rows,
        "trusted_native_source_set_digest": source_set_digest(rows),
        "probe_records": records,
        "probe_set_digest": digest({"record_digests": sorted(x["record_digest"] for x in records)}),
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "runtime_qualification_state": "NOT_CLAIMED",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def reseal_probe_set(b):
    b["probe_set_digest"] = digest({"record_digests": sorted(x["record_digest"] for x in b["probe_records"])})


class R16SuccessorEvidenceTests(unittest.TestCase):
    def test_complete_evidence_binds_but_never_qualifies(self):
        result = validate_r16_external_evidence(bundle())
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["required_probe_count"], len(REQUIRED_R16_PROBES))
        self.assertEqual(result["bound_probe_count"], len(REQUIRED_R16_PROBES))
        self.assertEqual(result["trusted_native_source_count"], 3)

    def test_dir_fd_openat_must_be_covered(self):
        b = bundle()
        b["native_confinement"]["dir_fd_openat_covered"] = False
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_DIR_FD_OPENAT_COVERAGE_REQUIRED", result["problems"])

    def test_cwd_realpath_cannot_be_authority_root(self):
        b = bundle()
        b["native_confinement"]["cwd_realpath_authoritative"] = True
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_CWD_REALPATH_MUST_NOT_BE_AUTHORITY", result["problems"])

    def test_inherited_or_duplicated_fd_gap_blocks(self):
        b = bundle()
        b["native_confinement"]["inherited_and_duplicated_fd_covered"] = False
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_FD_ALIAS_COVERAGE_REQUIRED", result["problems"])

    def test_authority_secret_may_not_exist_in_candidate_memory(self):
        b = bundle()
        b["secret_separation"]["authority_secret_in_candidate_address_space"] = True
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_AUTHORITY_SECRET_IN_CANDIDATE_FORBIDDEN", result["problems"])

    def test_candidate_may_not_compute_authority_mac(self):
        b = bundle()
        b["secret_separation"]["candidate_can_compute_authority_mac"] = True
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_CANDIDATE_AUTHORITY_MAC_FORBIDDEN", result["problems"])

    def test_full_child_memory_forgery_regression_is_mandatory(self):
        b = bundle()
        b["secret_separation"]["full_child_memory_knowledge_forgery_rejected"] = False
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_FULL_CHILD_MEMORY_FORGERY_REGRESSION_REQUIRED", result["problems"])

    def test_scenario_library_must_be_verified_before_import(self):
        b = bundle()
        b["trusted_scenario_library"]["verified_before_import"] = False
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_SCENARIO_LIBRARY_PREIMPORT_VERIFICATION_REQUIRED", result["problems"])

    def test_transitive_native_source_set_digest_is_load_bearing(self):
        b = bundle()
        b["trusted_native_sources"].pop()
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_TRUSTED_NATIVE_SOURCE_SET_DIGEST_MISMATCH", result["problems"])

    def test_missing_probe_fails_closed(self):
        b = bundle()
        removed = b["probe_records"].pop()["probe_id"]
        reseal_probe_set(b)
        result = validate_r16_external_evidence(b)
        self.assertIn(f"R16_PROBE_MISSING:{removed}", result["problems"])

    def test_name_only_probe_record_cannot_satisfy_execution(self):
        b = bundle()
        target = sorted(REQUIRED_R16_PROBES)[0]
        b["probe_records"][0] = {"probe_id": target}
        b["probe_set_digest"] = digest({"record_digests": sorted(
            x["record_digest"] for x in b["probe_records"] if "record_digest" in x
        )})
        result = validate_r16_external_evidence(b)
        self.assertTrue(any(x.startswith("R16_PROBE_NOT_EXECUTED:") for x in result["problems"]))
        self.assertTrue(any(x.startswith("R16_PROBE_RECORD_DIGEST_MISMATCH:") for x in result["problems"]))

    def test_scientific_execution_cannot_be_opened(self):
        b = bundle()
        b["scientific_execution_state"] = "OPEN"
        result = validate_r16_external_evidence(b)
        self.assertIn("R16_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED", result["problems"])

    def test_frontier_remains_non_authoritative(self):
        result = construction_frontier()
        self.assertFalse(result["qualified"])
        self.assertEqual(result["runtime_qualification_state"], "NOT_CLAIMED")
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
