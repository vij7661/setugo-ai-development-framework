from __future__ import annotations

import unittest

from review_engine.cli import build_request
from review_engine.request_boundary import PlatformExecutionEnvelope


class CLITests(unittest.TestCase):
    def test_simple_chat_remains_low_risk_under_review_only_platform_envelope(self):
        request = build_request({"request_id": "r1", "user_input": "brainstorm names", "operation_class": "CHAT"})
        self.assertEqual(request.risk, "LOW")
        self.assertFalse(request.external_action)
        self.assertFalse(request.platform_facts["human_approval_required"])
        self.assertEqual(request.platform_facts["platform_operation_class"], "ANALYSIS")
        self.assertEqual(request.platform_facts["declared_operation_class"], "CHAT")

    def test_simple_language_cannot_hide_declared_production_target(self):
        request = build_request({
            "request_id": "r2",
            "user_input": "just finish the last step",
            "operation_class": "ANALYSIS",
            "target_environment": "production",
        })
        self.assertEqual(request.risk, "CRITICAL")
        self.assertEqual(request.materiality, "CONSEQUENTIAL")
        self.assertTrue(request.external_action)
        self.assertTrue(request.platform_facts["human_approval_required"])
        self.assertIsNone(request.platform_facts["platform_target_environment"])
        self.assertEqual(request.platform_facts["declared_target_environment"], "production")

    def test_connected_send_capability_is_caller_declaration_that_can_only_raise(self):
        request = build_request({
            "request_id": "r3",
            "user_input": "handle this",
            "operation_class": "CHAT",
            "connected_tool_capabilities": ["SEND"],
        })
        self.assertEqual(request.risk, "HIGH")
        self.assertTrue(request.external_action)
        self.assertEqual(request.platform_facts["platform_connected_tool_capabilities"], [])
        self.assertEqual(request.platform_facts["declared_connected_tool_capabilities"], ["SEND"])

    def test_user_materiality_can_raise_but_not_lower_floor(self):
        request = build_request({
            "request_id": "r4",
            "user_input": "modify artifact",
            "operation_class": "ARTIFACT_MODIFY",
            "materiality": "NONE",
        })
        self.assertEqual(request.materiality, "MATERIAL")
        raised = build_request({
            "request_id": "r5",
            "user_input": "analysis",
            "operation_class": "ANALYSIS",
            "materiality": "CONSEQUENTIAL",
        })
        self.assertEqual(raised.materiality, "CONSEQUENTIAL")

    def test_obvious_production_intent_in_text_raises_floor_even_if_caller_claims_chat(self):
        request = build_request({
            "request_id": "r6",
            "user_input": "deploy this fix to production now",
            "operation_class": "CHAT",
            "connected_tool_capabilities": [],
        })
        self.assertEqual(request.risk, "CRITICAL")
        self.assertEqual(request.materiality, "CONSEQUENTIAL")
        self.assertTrue(request.mutation_requested)
        self.assertTrue(any("production/live" in reason for reason in request.platform_facts["risk_reasons"]))

    def test_caller_cannot_choose_task_type_used_for_qualification(self):
        request = build_request(
            {"request_id": "r7", "user_input": "review", "task_type": "SECURITY"},
            platform_envelope=PlatformExecutionEnvelope(task_type="GENERAL"),
        )
        self.assertEqual(request.platform_facts["task_type"], "GENERAL")
        self.assertEqual(request.platform_facts["declared_task_type"], "SECURITY")

    def test_trusted_platform_envelope_cannot_be_lowered_by_caller(self):
        request = build_request(
            {
                "request_id": "r8",
                "user_input": "do the thing",
                "operation_class": "CHAT",
                "connected_tool_capabilities": [],
                "target_environment": None,
            },
            platform_envelope=PlatformExecutionEnvelope(
                operation_class="PRODUCTION_CHANGE",
                connected_tool_capabilities=("DEPLOY",),
                target_environment="production",
                task_type="DEPLOYMENT",
            ),
        )
        self.assertEqual(request.risk, "CRITICAL")
        self.assertEqual(request.materiality, "CONSEQUENTIAL")
        self.assertTrue(request.external_action)
        self.assertTrue(request.mutation_requested)
        self.assertEqual(request.platform_facts["task_type"], "DEPLOYMENT")


if __name__ == "__main__":
    unittest.main()
