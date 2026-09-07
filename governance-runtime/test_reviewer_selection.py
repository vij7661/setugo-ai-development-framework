from __future__ import annotations

import unittest

from review_protocol import build_review_request, verify_review_request


class ReviewerSelectionTests(unittest.TestCase):
    def test_deepseek_selection_binds_review_request_to_deepseek(self) -> None:
        request = build_review_request(
            review_request_id="REV-SELECT-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="pull_request_candidate",
            artifact_ref="PR-5",
            artifact_commit="1" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            blind_review_required=True,
            review_questions=["Review independently."],
            evidence_refs=[],
            material_authority_transition=True,
        )
        ok, reason = verify_review_request(request)
        self.assertTrue(ok, reason)
        self.assertEqual(request["required_reviewer"]["provider"], "deepseek")
        self.assertEqual(request["required_reviewer"]["model_class"], "deepseek")

    def test_claude_and_deepseek_requests_have_distinct_semantic_bindings(self) -> None:
        common = dict(
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="pull_request_candidate",
            artifact_ref="PR-5",
            artifact_commit="2" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            blind_review_required=True,
            review_questions=["Review independently."],
            evidence_refs=[],
            material_authority_transition=True,
        )
        claude = build_review_request(
            review_request_id="REV-SELECT-C",
            required_reviewer={"provider": "anthropic", "model_class": "claude"},
            **common,
        )
        deepseek = build_review_request(
            review_request_id="REV-SELECT-D",
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            **common,
        )
        self.assertNotEqual(claude["request_hash"], deepseek["request_hash"])
        self.assertEqual(claude["required_reviewer"]["provider"], "anthropic")
        self.assertEqual(deepseek["required_reviewer"]["provider"], "deepseek")


if __name__ == "__main__":
    unittest.main()
