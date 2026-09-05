from __future__ import annotations

import unittest

from review_engine.cli import build_request


class CLITests(unittest.TestCase):
    def test_simple_chat_remains_low_risk(self):
        request = build_request({"request_id": "r1", "user_input": "brainstorm names", "operation_class": "CHAT"})
        self.assertEqual(request.risk, "LOW")
        self.assertFalse(request.external_action)
        self.assertFalse(request.platform_facts["human_approval_required"])

    def test_simple_language_cannot_hide_production_target(self):
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

    def test_connected_send_capability_raises_risk_floor(self):
        request = build_request({
            "request_id": "r3",
            "user_input": "handle this",
            "operation_class": "CHAT",
            "connected_tool_capabilities": ["SEND"],
        })
        self.assertEqual(request.risk, "HIGH")
        self.assertTrue(request.external_action)

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


if __name__ == "__main__":
    unittest.main()
