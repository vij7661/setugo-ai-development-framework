from __future__ import annotations

import unittest

from review_engine.judge_health import JudgeHealthMonitor, JudgeIdentityBinding, JudgeObservation


def identity(name: str, *, lineage: str | None = None, deployment_path: str | None = None, qualification_ref: str | None = None) -> JudgeIdentityBinding:
    return JudgeIdentityBinding(
        provider=f"provider-{name}",
        model=f"model-{name}",
        sku="default",
        deployment_path=deployment_path or f"api/{name}",
        role="R2",
        foundation_lineage=lineage or f"lineage-{name}",
        qualification_ref=qualification_ref or f"q-{name}",
        qualification_epoch=1,
    )


class JudgeHealthMonitorTests(unittest.TestCase):
    def _pair(self, disagreements: int, total: int = 10):
        a = identity("a")
        b = identity("b")
        observations = []
        for i in range(total):
            observations.append(JudgeObservation.bound(f"t{i}", a, "A"))
            label_b = "B" if i < disagreements else "A"
            observations.append(JudgeObservation.bound(f"t{i}", b, label_b))
        return observations

    def test_pairwise_logical_alarm_fires_when_both_cannot_meet_accuracy_target(self):
        report = JudgeHealthMonitor(minimum_accuracy_target=0.9, minimum_shared_tasks=10).evaluate(
            self._pair(disagreements=3)
        )
        self.assertEqual(report.status, "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET")
        self.assertEqual(report.pair_assessments[0].max_disagreements_if_both_meet_target, 2)
        self.assertTrue(report.pair_assessments[0].alarm)
        self.assertEqual(report.pair_assessments[0].identity_correlation, "DISTINCT_DECLARED_LINEAGE")
        self.assertFalse(report.can_identify_faulty_judge)
        self.assertFalse(report.no_alarm_establishes_correctness)

    def test_no_alarm_does_not_claim_alignment_or_correctness(self):
        report = JudgeHealthMonitor(minimum_accuracy_target=0.9, minimum_shared_tasks=10).evaluate(
            self._pair(disagreements=2)
        )
        self.assertEqual(report.status, "NO_LOGICAL_ALARM")
        self.assertFalse(report.no_alarm_establishes_correctness)
        self.assertFalse(report.can_identify_faulty_judge)

    def test_insufficient_overlap_does_not_emit_health_claim(self):
        report = JudgeHealthMonitor(minimum_accuracy_target=0.8, minimum_shared_tasks=5).evaluate(
            self._pair(disagreements=1, total=4)
        )
        self.assertEqual(report.status, "INSUFFICIENT_DATA")
        self.assertEqual(report.pair_assessments, ())

    def test_unbound_self_reported_judge_id_is_rejected_by_default(self):
        observations = [JudgeObservation("t1", "claimed-model-name", "PASS")]
        with self.assertRaisesRegex(ValueError, "platform-bound identity"):
            JudgeHealthMonitor(minimum_accuracy_target=0.8, minimum_shared_tasks=1).evaluate(observations)

    def test_forged_judge_id_cannot_disagree_with_bound_identity(self):
        a = identity("a")
        forged = JudgeObservation("t1", "judge:forged", "PASS", identity=a)
        with self.assertRaisesRegex(ValueError, "does not match"):
            JudgeHealthMonitor(minimum_accuracy_target=0.8, minimum_shared_tasks=1).evaluate([forged])

    def test_conflicting_retained_observation_is_rejected(self):
        a = identity("a")
        observations = [
            JudgeObservation.bound("t1", a, "A"),
            JudgeObservation.bound("t1", a, "B"),
        ]
        with self.assertRaisesRegex(ValueError, "conflicting retained judge observations"):
            JudgeHealthMonitor(minimum_accuracy_target=0.8, minimum_shared_tasks=1).evaluate(observations)

    def test_same_runtime_path_aliases_do_not_create_two_judges(self):
        a = JudgeIdentityBinding(
            provider="provider-x", model="model-x", sku="default", deployment_path="api/shared",
            role="R2", foundation_lineage="lineage-x", qualification_ref="q-a", qualification_epoch=1,
        )
        b = JudgeIdentityBinding(
            provider="provider-x", model="model-x", sku="default", deployment_path="api/shared",
            role="R3", foundation_lineage="lineage-x", qualification_ref="q-b", qualification_epoch=1,
        )
        observations = [
            JudgeObservation.bound("t1", a, "PASS"),
            JudgeObservation.bound("t1", b, "FAIL"),
        ]
        report = JudgeHealthMonitor(minimum_accuracy_target=1.0, minimum_shared_tasks=1).evaluate(observations)
        self.assertEqual(report.status, "INSUFFICIENT_DATA")
        self.assertEqual(report.pair_assessments, ())
        self.assertTrue(any("same deployment path" in warning[2] for warning in report.identity_warnings))

    def test_same_foundation_lineage_is_analyzed_but_warned(self):
        a = identity("a", lineage="shared-lineage")
        b = identity("b", lineage="shared-lineage")
        observations = [
            JudgeObservation.bound("t1", a, "PASS"),
            JudgeObservation.bound("t1", b, "FAIL"),
        ]
        report = JudgeHealthMonitor(minimum_accuracy_target=1.0, minimum_shared_tasks=1).evaluate(observations)
        self.assertEqual(report.status, "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET")
        self.assertEqual(report.pair_assessments[0].identity_correlation, "SAME_FOUNDATION_LINEAGE")
        self.assertTrue(report.identity_warnings)

    def test_dimensions_are_not_mixed(self):
        a, b = identity("a"), identity("b")
        observations = [
            JudgeObservation.bound("t1", a, "PASS", "SECURITY"),
            JudgeObservation.bound("t1", b, "FAIL", "SECURITY"),
            JudgeObservation.bound("t1", a, "PASS", "REQUIREMENTS"),
            JudgeObservation.bound("t1", b, "PASS", "REQUIREMENTS"),
        ]
        report = JudgeHealthMonitor(minimum_accuracy_target=1.0, minimum_shared_tasks=1).evaluate(observations)
        self.assertEqual(len(report.pair_assessments), 2)
        alarms = {(a.dimension, a.alarm) for a in report.pair_assessments}
        self.assertIn(("SECURITY", True), alarms)
        self.assertIn(("REQUIREMENTS", False), alarms)


if __name__ == "__main__":
    unittest.main()
