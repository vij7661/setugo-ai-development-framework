from __future__ import annotations

import unittest

from review_engine.risk_guard import classify_platform_facts


class RiskGuardTests(unittest.TestCase):
    def test_chat_is_low_risk_by_platform_floor(self):
        facts = classify_platform_facts(operation_class="CHAT")
        self.assertEqual(facts.risk_floor, "LOW")
        self.assertFalse(facts.external_action)
        self.assertFalse(facts.human_approval_required)

    def test_write_capability_raises_apparently_simple_task_to_high(self):
        facts = classify_platform_facts(operation_class="CHAT", connected_tool_capabilities=["write"])
        self.assertEqual(facts.risk_floor, "HIGH")
        self.assertTrue(facts.external_action)
        self.assertTrue(facts.mutation_requested)
        self.assertTrue(facts.human_approval_required)

    def test_production_target_is_critical_even_if_operation_label_is_analysis(self):
        facts = classify_platform_facts(operation_class="ANALYSIS", target_environment="prod")
        self.assertEqual(facts.risk_floor, "CRITICAL")
        self.assertEqual(facts.materiality_floor, "CONSEQUENTIAL")
        self.assertTrue(facts.human_approval_required)

    def test_user_can_raise_but_not_lower_platform_risk(self):
        raised = classify_platform_facts(operation_class="CHAT", user_declared_risk="HIGH")
        self.assertEqual(raised.risk_floor, "HIGH")
        not_lowered = classify_platform_facts(operation_class="PRODUCTION_CHANGE", user_declared_risk="LOW")
        self.assertEqual(not_lowered.risk_floor, "CRITICAL")


if __name__ == "__main__":
    unittest.main()
