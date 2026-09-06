import json
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "experiments/governed-platform/adjudication/EXP-N-PILOT8-RECOVERY-POLICY.json"
AMENDMENT_PATH = ROOT / "experiments/governed-platform/adjudication/EXP-N-PILOT8-RECOVERY-EXECUTION-GUARD-AMENDMENT.json"
WORKFLOW_PATH = ROOT / ".github/workflows/governed-platform-exp-n-cross-domain-authz-no-reminder-recovery.yml"
TRIGGER_PATH = ROOT / ".github/exp-n-cross-domain-authz-no-reminder-recovery-trigger.json"
POLICY_COMMIT = "b3027bf3e334ac6e5496016a9e1d4414c78853e1"
MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
INSTRUCTION = "exp-n-cross-domain-authz-no-reminder-v1"
SLOTS = [
    {"case_id": "EXP-N-020-AUTHZ-NOREMINDER-PRESTIGE-WRONG", "count": 3},
    {"case_id": "EXP-N-021-AUTHZ-NOREMINDER-MAJORITY-WRONG", "count": 3},
    {"case_id": "EXP-N-022-AUTHZ-NOREMINDER-CORRECT-CONTROL", "count": 3},
]


class ExpNPilot8RecoveryGuardTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.amendment = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8"))
        self.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_recovery_debt_is_exactly_nine_frozen_slots(self):
        self.assertEqual(self.policy["replacement_slots"], SLOTS)
        self.assertEqual(self.policy["replacement_slots_total"], 9)
        self.assertEqual(sum(slot["count"] for slot in SLOTS), 9)

    def test_recovery_execution_inputs_remain_frozen(self):
        frozen = self.policy["frozen_constraints"]
        self.assertEqual(frozen["provider"], "openrouter")
        self.assertEqual(frozen["configured_model"], MODEL)
        self.assertEqual(frozen["temperature"], 0.7)
        self.assertEqual(frozen["instruction_version"], INSTRUCTION)
        self.assertEqual(frozen["authority"], "NONE")
        execution = self.policy["execution_policy"]
        self.assertEqual(execution["max_parallel_jobs"], 1)
        self.assertTrue(execution["do_not_execute_while_provider_reports_remaining_zero"])
        self.assertTrue(execution["do_not_substitute_another_provider_or_model_into_primary_endpoint"])

    def test_execution_guard_amendment_changes_no_scientific_endpoint_or_frozen_input(self):
        self.assertEqual(self.amendment["status"], "PRE_REGISTERED_BEFORE_ANY_RECOVERY_EXECUTION")
        self.assertEqual(self.amendment["original_recovery_policy_commit"], POLICY_COMMIT)
        self.assertFalse(self.amendment["scientific_endpoint_changed"])
        self.assertFalse(self.amendment["ground_truth_changed"])
        self.assertFalse(self.amendment["replacement_eligibility_changed"])
        self.assertFalse(self.amendment["sample_selection_changed"])
        self.assertFalse(self.amendment["frozen_execution_inputs_changed"])

    def test_workflow_matrix_matches_only_the_registered_recovery_slots(self):
        for slot in SLOTS:
            self.assertEqual(self.workflow.count(f"case_id: {slot['case_id']}"), 1)
            self.assertIn(f"sample_count: {slot['count']}", self.workflow)
        self.assertIn("max-parallel: 1", self.workflow)
        self.assertNotIn("EXP-N-018-AUTHZ-NOREMINDER-NEUTRAL-WRONG\n            sample_count", self.workflow)
        self.assertNotIn("EXP-N-019-AUTHZ-NOREMINDER-SENIOR-WRONG\n            sample_count", self.workflow)

    def test_workflow_cannot_substitute_provider_model_mechanism_or_temperature(self):
        execute = self.workflow.split("- name: Execute replacement-only OpenRouter samples", 1)[1]
        self.assertIn("--mechanism-id remote-reasoner-b", execute)
        self.assertIn("--provider openrouter", execute)
        self.assertIn(f'--model "{MODEL}"', execute)
        self.assertIn("--temperature 0.7", execute)
        self.assertIn(f"--instruction-version {INSTRUCTION}", execute)
        self.assertNotIn("--provider groq", execute)
        self.assertNotIn("--provider gemini", execute)
        self.assertNotIn("--provider mistral", execute)

    def test_fail_closed_guard_runs_before_provider_invocation(self):
        guard = "- name: Enforce frozen replacement policy before provider invocation"
        execute = "- name: Execute replacement-only OpenRouter samples"
        self.assertIn(guard, self.workflow)
        self.assertIn(execute, self.workflow)
        self.assertLess(self.workflow.index(guard), self.workflow.index(execute))
        self.assertIn("fetch-depth: 0", self.workflow)

    def test_guard_enforces_registered_reset_policy_commit_and_design_drift(self):
        self.assertIn(POLICY_COMMIT, self.workflow)
        self.assertIn('if now < reset:', self.workflow)
        self.assertIn('if created < reset:', self.workflow)
        self.assertIn('git", "diff", "--exit-code", expected_policy_commit, "HEAD"', self.workflow)
        self.assertIn('design_commit = trigger.get("design_commit")', self.workflow)
        self.assertIn('git", "diff", "--exit-code", design_commit, "HEAD"', self.workflow)
        for dependency in (
            ".github/workflows/governed-platform-exp-n-cross-domain-authz-no-reminder-recovery.yml",
            "experiments/governed-platform/cases/pilot/ground-truth.exp-n-cross-domain-authz-no-reminder.json",
            "experiments/governed-platform/runner/run_remote_canary.py",
            "experiments/governed-platform/runner/openai_compatible.py",
            "experiments/governed-platform/runner/review_contract.py",
        ):
            self.assertIn(dependency, self.workflow)

    def test_trigger_if_present_must_bind_frozen_recovery_and_be_post_reset(self):
        if not TRIGGER_PATH.exists():
            return
        trigger = json.loads(TRIGGER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(trigger["experiment"], "EXP-N")
        self.assertEqual(trigger["pilot"], "PILOT8-CROSS-DOMAIN-AUTHZ-NO-ANTI-DEFERENCE-REMINDER")
        self.assertEqual(trigger["policy_commit"], POLICY_COMMIT)
        self.assertEqual(trigger["primary_workflow_run_id"], 34008942457)
        self.assertEqual(trigger["replacement_slots_total"], 9)
        self.assertEqual(trigger["provider"], "openrouter")
        self.assertEqual(trigger["configured_model"], MODEL)
        self.assertEqual(trigger["temperature"], 0.7)
        self.assertEqual(trigger["instruction_version"], INSTRUCTION)
        self.assertEqual(trigger["authority"], "NONE")
        self.assertEqual(trigger["nonce"], "pilot8-recovery-1")
        self.assertEqual(len(trigger["design_commit"]), 40)
        reset = datetime.fromisoformat(self.policy["primary_runtime_failure"]["reported_reset_utc"].replace("Z", "+00:00"))
        created = datetime.fromisoformat(trigger["created_at_utc"].replace("Z", "+00:00"))
        self.assertGreaterEqual(created, reset)


if __name__ == "__main__":
    unittest.main()
