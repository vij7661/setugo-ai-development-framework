from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "codex" / "validate_codex_agent.py"

spec = importlib.util.spec_from_file_location("validate_codex_agent", VALIDATOR_PATH)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CodexGovernanceValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        cls.skill = (ROOT / "skills" / "codex-execution" / "SKILL.md").read_text(encoding="utf-8")

    def test_current_repository_contract_passes(self) -> None:
        self.assertEqual([], validator.validate_texts(self.agents, self.skill))

    def test_missing_exact_head_clause_fails(self) -> None:
        bad = self.agents.replace("exact current HEAD SHA", "current revision", 1)
        errors = validator.validate_texts(bad, self.skill)
        self.assertTrue(any("exact current HEAD SHA" in error for error in errors))

    def test_missing_failure_triage_reference_fails(self) -> None:
        bad = self.skill.replace("skills/failure-triage/SKILL.md", "triage guidance", 1)
        errors = validator.validate_texts(self.agents, bad)
        self.assertTrue(any("failure-triage" in error for error in errors))

    def test_missing_abrupt_stop_recovery_fails(self) -> None:
        bad = self.agents.replace("repository/activity timestamps", "recent history", 1)
        errors = validator.validate_texts(bad, self.skill)
        self.assertTrue(any("repository/activity timestamps" in error for error in errors))

    def test_terminal_merge_authority_grant_fails(self) -> None:
        bad = self.agents + "\nCodex may merge after tests pass.\n"
        errors = validator.validate_texts(bad, self.skill)
        self.assertTrue(any("terminal authority grant detected" in error for error in errors))

    def test_terminal_deploy_authority_grant_fails(self) -> None:
        bad = self.skill + "\nCodex is authorized to deploy after CI passes.\n"
        errors = validator.validate_texts(self.agents, bad)
        self.assertTrue(any("terminal authority grant detected" in error for error in errors))

    def test_missing_requirement_unresolved_gate_fails(self) -> None:
        bad = self.skill.replace("REQUIREMENT UNRESOLVED", "UNKNOWN")
        errors = validator.validate_texts(self.agents, bad)
        self.assertTrue(any("REQUIREMENT UNRESOLVED" in error for error in errors))

    def test_missing_manual_qa_gate_fails(self) -> None:
        bad = self.agents.replace("PASS — MANUAL QA REQUIRED", "PASS", 1)
        errors = validator.validate_texts(bad, self.skill)
        self.assertTrue(any("PASS — MANUAL QA REQUIRED" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
