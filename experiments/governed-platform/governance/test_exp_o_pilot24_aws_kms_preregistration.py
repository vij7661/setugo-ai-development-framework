import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "adjudication" / "EXP-O-PILOT24-AWS-KMS-ASYMMETRIC-CHECKPOINT-PREREGISTRATION.md"
AMEND = ROOT / "adjudication" / "EXP-O-PILOT24-PREEXECUTION-SAFETY-AMENDMENT.md"
RUNNER = ROOT / "runner" / "run_exp_o_pilot24_aws_kms.py"
WORKFLOW = ROOT.parents[1] / ".github" / "workflows" / "governed-platform-exp-o-pilot24-aws-kms.yml"
TRIGGER = ROOT.parents[1] / ".github" / "exp-o-pilot24-aws-kms-trigger.json"

ROLE = "arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer"
KEY = "arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c"
BRANCH = "experiment/governed-platform-falsification-harness"


class ExpOPilot24PreExecutionIntegrityTests(unittest.TestCase):
    def test_preregistration_freezes_external_asymmetric_path_and_twenty_cases(self):
        text = PREREG.read_text(encoding="utf-8")
        self.assertIn(ROLE, text)
        self.assertIn(KEY, text)
        self.assertIn("ECC_NIST_P256", text)
        self.assertIn("ECDSA_SHA_256", text)
        for i in range(1, 21):
            self.assertIn(f"P24-{i:02d}", text)

    def test_safety_amendment_precedes_execution_and_forbids_destructive_runtime_probes(self):
        text = AMEND.read_text(encoding="utf-8")
        self.assertIn("BEFORE ANY PILOT 24 AWS/KMS EXECUTION", text)
        self.assertIn("CONFIGURATION-BOUND / NOT DESTRUCTIVE-RUNTIME-PROBED", text)
        self.assertIn("DisableKey", text)
        self.assertIn("ScheduleKeyDeletion", text)
        self.assertIn("CreateKey", text)

    def test_workflow_is_trigger_only_exact_branch_and_oidc_enabled(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("exp-o-pilot24-aws-kms-trigger.json", text)
        self.assertIn(BRANCH, text)
        self.assertIn("id-token: write", text)
        self.assertIn("contents: read", text)
        self.assertIn("aws-actions/configure-aws-credentials@v4", text)

    def test_workflow_has_exact_role_region_key_and_no_static_aws_secret(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(ROLE, text)
        self.assertIn(KEY, text)
        self.assertIn("ap-southeast-2", text)
        self.assertNotRegex(text, r"secrets\.[A-Za-z0-9_]*AWS[A-Za-z0-9_]*")
        self.assertNotIn("aws-access-key-id", text.lower())
        self.assertNotIn("aws-secret-access-key", text.lower())

    def test_workflow_guard_precedes_oidc_and_kms_execution(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index("Enforce frozen Pilot 24 trigger")
        oidc = text.index("Configure temporary AWS credentials")
        execute = text.index("Execute frozen Pilot 24 AWS KMS")
        self.assertLess(guard, oidc)
        self.assertLess(oidc, execute)
        self.assertIn("git','diff','--exit-code',design,'HEAD'", text)

    def test_runner_freezes_exact_key_spec_algorithm_and_has_no_destructive_aws_command(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn(ROLE, text)
        self.assertIn(KEY, text)
        self.assertIn("ECC_NIST_P256", text)
        self.assertIn("ECDSA_SHA_256", text)
        for command in ["disable-key", "schedule-key-deletion", "create-key"]:
            self.assertNotRegex(text, rf'\[\s*"aws"[^\]]*"{re.escape(command)}"')

    def test_runner_uses_public_key_local_openssl_verification(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('"kms", "get-public-key"', text)
        self.assertIn('"openssl", "dgst", "-sha256", "-verify"', text)
        self.assertIn("credentialless=True", text)
        self.assertNotIn("kms\", \"verify", text)

    def test_runner_keeps_valid_signature_separate_from_semantic_generation_authority(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("trusted_min_generation = 2", text)
        self.assertIn("semantic_eligible", text)
        self.assertIn('"model_authority_effect": False', text)
        self.assertIn('"authoritative_platform_effect_count": 0', text)

    def test_configuration_bound_cases_are_not_reported_as_runtime_admin_denials(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertEqual(text.count('classification="CONFIGURATION_BOUND_NOT_RUNTIME_PROBED"'), 3)
        self.assertIn('"destructive_runtime_probe_performed": False', text)

    def test_trigger_if_present_must_bind_exact_frozen_design(self):
        if not TRIGGER.exists():
            return
        t = json.loads(TRIGGER.read_text(encoding="utf-8"))
        self.assertEqual(t["experiment"], "EXP-O")
        self.assertEqual(t["pilot"], "PILOT24-AWS-KMS-ASYMMETRIC-CHECKPOINT")
        self.assertEqual(t["aws_role_arn"], ROLE)
        self.assertEqual(t["kms_key_arn"], KEY)
        self.assertEqual(t["aws_region"], "ap-southeast-2")
        self.assertEqual(t["key_spec"], "ECC_NIST_P256")
        self.assertEqual(t["signing_algorithm"], "ECDSA_SHA_256")
        self.assertEqual(t["nonce"], "pilot24-aws-kms-1")
        self.assertRegex(t["design_commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(t["created_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


if __name__ == "__main__":
    unittest.main()
