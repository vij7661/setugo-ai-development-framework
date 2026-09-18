from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from v24_v6_runtime_qualification_preflight import validate_runtime_qualification_entry

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "implementation/v24/V24-I11-V6-RUNTIME-QUALIFICATION-1-SUBJECT.json"


def runtime_fixture() -> dict:
    return {
        "status": "NOMINATED",
        "host_or_image_id": "ubuntu-24.04-image-20260918.1",
        "image_digest": "a" * 64,
        "os_release": "Ubuntu 24.04",
        "kernel_release": "6.11.0-qualified",
        "architecture": "x86_64",
        "service_manager": "systemd-255",
        "filesystem_type": "ext4",
        "mount_options_digest": "b" * 64,
        "runtime_owner": "runtime-owner-1",
        "evidence_custodian": "evidence-custodian-1",
        "independent_reviewer": "independent-reviewer-1",
        "candidate_uid": 997,
        "trusted_uid": 0,
        "record_fs_device": "8:1",
        "consumed_fs_device": "8:1",
        "trusted_path_owner_uid": 0,
        "socket_parent_owner_uid": 0,
        "unprivileged_userns_blocked": True,
        "ptrace_candidate_to_service_denied": True,
        "synthetic_sinks_only": True,
    }


class RuntimeQualificationPreflightTests(unittest.TestCase):
    def subject(self) -> dict:
        return json.loads(SUBJECT.read_text(encoding="utf-8"))

    def test_committed_unbound_subject_is_not_entry_ready(self):
        result = validate_runtime_qualification_entry(self.subject())
        self.assertFalse(result["entry_ready"])
        self.assertFalse(result["qualified"])
        self.assertIn("RUNTIME_NOT_NOMINATED", result["problems"])

    def test_scientific_execution_cannot_open(self):
        subject = self.subject()
        subject["scientific_execution_state"] = "OPEN"
        result = validate_runtime_qualification_entry(subject, runtime_fixture())
        self.assertIn("SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED", result["problems"])

    def test_authority_effect_cannot_change(self):
        subject = self.subject()
        subject["authority_effect"] = "AUTHORITY_ENABLED"
        result = validate_runtime_qualification_entry(subject, runtime_fixture())
        self.assertIn("AUTHORITY_EFFECT_MUST_REMAIN_NONE_EVIDENCE_ONLY", result["problems"])

    def test_preflight_cannot_claim_qualification(self):
        subject = self.subject()
        subject["phase_state"] = "QUALIFIED"
        subject["current_disposition"] = "QUALIFIED_FOR_BOUND_RUNTIME"
        result = validate_runtime_qualification_entry(subject, runtime_fixture())
        self.assertIn("PREFLIGHT_SUBJECT_MUST_REMAIN_NOT_QUALIFIED", result["problems"])

    def test_missing_runtime_custody_blocks_entry(self):
        runtime = runtime_fixture()
        runtime["evidence_custodian"] = None
        result = validate_runtime_qualification_entry(self.subject(), runtime)
        self.assertIn("RUNTIME_FIELD_MISSING:evidence_custodian", result["problems"])

    def test_cross_filesystem_consume_transition_blocks_entry(self):
        runtime = runtime_fixture()
        runtime["consumed_fs_device"] = "8:2"
        result = validate_runtime_qualification_entry(self.subject(), runtime)
        self.assertIn("RECORD_AND_CONSUMED_FILESYSTEM_DIFFER", result["problems"])

    def test_root_candidate_identity_blocks_entry(self):
        runtime = runtime_fixture()
        runtime["candidate_uid"] = 0
        result = validate_runtime_qualification_entry(self.subject(), runtime)
        self.assertIn("CANDIDATE_IDENTITY_IS_ROOT", result["problems"])

    def test_uncontrolled_runtime_security_boundaries_block_entry(self):
        runtime = runtime_fixture()
        runtime["unprivileged_userns_blocked"] = False
        runtime["ptrace_candidate_to_service_denied"] = False
        runtime["synthetic_sinks_only"] = False
        result = validate_runtime_qualification_entry(self.subject(), runtime)
        self.assertIn("UNPRIVILEGED_USER_NAMESPACE_NOT_BLOCKED", result["problems"])
        self.assertIn("CANDIDATE_PTRACE_DENIAL_NOT_EVIDENCED", result["problems"])
        self.assertIn("SYNTHETIC_EVIDENCE_ONLY_SINKS_NOT_ENFORCED", result["problems"])

    def test_exact_nominated_runtime_can_enter_but_is_not_qualified(self):
        subject = self.subject()
        subject["runtime_binding"] = copy.deepcopy(runtime_fixture())
        result = validate_runtime_qualification_entry(subject)
        self.assertTrue(result["entry_ready"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["problems"], [])
        self.assertEqual(result["current_disposition"], "NOT_QUALIFIED")


if __name__ == "__main__":
    unittest.main()
