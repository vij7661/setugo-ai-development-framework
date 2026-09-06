import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "experiments/governed-platform/adjudication/EXP-O-PILOT26-MULTI-KMS-ROOT-QUORUM-PREREGISTRATION.md"
AMEND = REPO / "experiments/governed-platform/adjudication/EXP-O-PILOT26-KMS-ROOT-RESOURCE-BINDING-AMENDMENT.md"
RUNNER = REPO / "experiments/governed-platform/runner/run_exp_o_pilot26_multi_kms_quorum.py"
WORKFLOW = REPO / ".github/workflows/governed-platform-exp-o-pilot26-multi-kms-quorum.yml"
TRIGGER = REPO / ".github/exp-o-pilot26-multi-kms-quorum-trigger.json"

A = "arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c"
B = "arn:aws:kms:ap-southeast-2:297165774800:key/aad32262-2396-485e-a6f2-0ae0cd10f52e"
C = "arn:aws:kms:ap-southeast-2:297165774800:key/992638b8-7086-41a6-a3dc-849a998c4f86"


class ExpOPilot26PreExecutionIntegrityTests(unittest.TestCase):
    def test_preregistration_freezes_twenty_endpoints_and_two_of_three_rule(self):
        text = PREREG.read_text()
        ids = re.findall(r"\*\*P26-(\d{2})\*\*", text)
        self.assertEqual(ids, [f"{i:02d}" for i in range(1, 21)])
        self.assertIn("2 distinct registered KMS key ARNs", text)
        self.assertIn("same AWS account and IAM administrative trust domain", text)

    def test_resource_amendment_binds_exact_three_external_roots_before_execution(self):
        text = AMEND.read_text()
        for arn in (A, B, C):
            self.assertEqual(text.count(arn), 1)
        self.assertIn("ECC_NIST_P256", text)
        self.assertIn("SIGN_VERIFY", text)
        self.assertIn("ECDSA_SHA_256", text)
        self.assertIn("does not change the twenty scientific endpoints", text)

    def test_runner_freezes_exact_roots_threshold_and_has_no_destructive_kms_admin(self):
        text = RUNNER.read_text()
        for arn in (A, B, C):
            self.assertIn(arn, text)
        self.assertIn('"threshold": "2-of-3-distinct-registered-kms-key-arns"', text)
        self.assertIn('model_authority_effect": False', text)
        self.assertIn('authoritative_platform_effect_count": 0', text)
        for forbidden in ("DisableKey", "ScheduleKeyDeletion", "CreateKey", "PutKeyPolicy", "CreateAlias", "UpdateAlias", "DeleteAlias"):
            self.assertNotIn(forbidden, text)

    def test_runner_counts_distinct_registered_root_arns_not_signature_count(self):
        text = RUNNER.read_text()
        self.assertIn("REGISTERED = set(ROOTS.values())", text)
        self.assertIn('groups.setdefault(h, {"roots": set()', text)
        self.assertIn('.add(root)', text)
        self.assertIn('len(v["roots"]) >= 2', text)
        self.assertIn('root not in REGISTERED', text)

    def test_runner_keeps_crypto_validity_separate_from_semantic_eligibility(self):
        text = RUNNER.read_text()
        self.assertIn("SIGNATURE_INVALID", text)
        self.assertIn("STATEMENT_SCOPE_INVALID", text)
        self.assertIn("STALE_GENERATION", text)
        self.assertIn("trusted_min_generation", text)
        self.assertIn("administratively_independent_trust_domains", text)

    def test_workflow_is_trigger_only_oidc_exact_role_and_guard_precedes_aws(self):
        text = WORKFLOW.read_text()
        self.assertIn(".github/exp-o-pilot26-multi-kms-quorum-trigger.json", text)
        self.assertIn("id-token: write", text)
        self.assertIn("arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer", text)
        self.assertNotIn("AWS_ACCESS_KEY_ID", text)
        self.assertLess(text.index("Enforce frozen Pilot 26 trigger"), text.index("Configure temporary AWS credentials"))
        for arn in (A, B, C):
            self.assertIn(arn, text)

    def test_trigger_if_present_binds_exact_resources_and_full_design_sha(self):
        if not TRIGGER.exists():
            return
        t = json.loads(TRIGGER.read_text())
        self.assertEqual(t["experiment"], "EXP-O")
        self.assertEqual(t["pilot"], "PILOT26-MULTI-KMS-ROOT-QUORUM")
        self.assertEqual(t["root_a_arn"], A)
        self.assertEqual(t["root_b_arn"], B)
        self.assertEqual(t["root_c_arn"], C)
        self.assertEqual(t["threshold"], "2-of-3-distinct-registered-kms-key-arns")
        self.assertRegex(t["design_commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(t["created_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


if __name__ == "__main__":
    unittest.main()
