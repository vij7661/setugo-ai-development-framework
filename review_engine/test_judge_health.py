from __future__ import annotations

import unittest

from review_engine.judge_health import JudgeHealthMonitor, JudgeObservation


class JudgeHealthMonitorTests(unittest.TestCase):
    def _pair(self, disagreements: int, total: int = 10):
        observations = []
        for i in range(total):
            observations.append(JudgeObservation(f"t{i}", "judge-a", "A"))
            label_b = "B" if i < disagreements else "A"
            observations.append(JudgeObservation(f"t{i}", "judge-b", label_b))
        return observations

    def test_pairwise_logical_alarm_fires_when_both_cannot_meet_accuracy_target(self):
        # At 90% minimum accuracy over 10 tasks, two judges that both satisfy
        # the target can disagree on at most two tasks. Three disagreements are
        # therefore logically incompatible with both meeting the target.
        report = JudgeHealthMonitor(minimum_accuracy_target=0.9, minimum_shared_tasks=10).evaluate(
            self._pair(disagreements=3)
        )
        self.assertEqual(report.status, "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET")
        self.assertEqual(report.pair_assessments[0].max_disagreements_if_both_meet_target, 2)
        self.assertTrue(report.pair_assessments[0].alarm)
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

    def test_conflicting_retained_observation_is_rejected(self):
        observations = [
            JudgeObservation("t1", "judge-a", "A"),
            JudgeObservation("t1", "judge-a", "B"),
        ]
        with self.assertRaisesRegex(ValueError, "conflicting retained judge observations"):
            JudgeHealthMonitor(minimum_accuracy_target=0.8, minimum_shared_tasks=1).evaluate(observations)

    def test_dimensions_are_not_mixed(self):
        observations = [
            JudgeObservation("t1", "judge-a", "PASS", "SECURITY"),
            JudgeObservation("t1", "judge-b", "FAIL", "SECURITY"),
            JudgeObservation("t1", "judge-a", "PASS", "REQUIREMENTS"),
            JudgeObservation("t1", "judge-b", "PASS", "REQUIREMENTS"),
        ]
        report = JudgeHealthMonitor(minimum_accuracy_target=1.0, minimum_shared_tasks=1).evaluate(observations)
        self.assertEqual(len(report.pair_assessments), 2)
        alarms = {(a.dimension, a.alarm) for a in report.pair_assessments}
        self.assertIn(("SECURITY", True), alarms)
        self.assertIn(("REQUIREMENTS", False), alarms)


if __name__ == "__main__":
    unittest.main()
