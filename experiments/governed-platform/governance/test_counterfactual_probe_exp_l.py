import unittest

from counterfactual_probe import CounterfactualProbeResult, assess_counterfactuals


def row(cid, **overrides):
    data = dict(
        counterfactual_id=cid,
        complete=True,
        conclusion_changed=False,
        falsifier_identified=True,
        unsupported_premise_found=False,
        evidence_gap_found=False,
    )
    data.update(overrides)
    return CounterfactualProbeResult(**data)


class ExpLCounterfactualProbeTests(unittest.TestCase):
    def test_stable_under_two_complete_probes(self):
        a = assess_counterfactuals([row("cf1"), row("cf2")])
        self.assertEqual("STABLE_UNDER_PROBES", a.status)
        self.assertFalse(a.instability_signal)

    def test_changed_conclusion_is_instability_signal(self):
        a = assess_counterfactuals([row("cf1", conclusion_changed=True), row("cf2")])
        self.assertEqual("INSTABILITY_SIGNAL", a.status)
        self.assertTrue(a.instability_signal)

    def test_unsupported_premise_is_instability_signal(self):
        a = assess_counterfactuals([row("cf1", unsupported_premise_found=True), row("cf2")])
        self.assertTrue(a.instability_signal)

    def test_evidence_gap_is_instability_signal(self):
        a = assess_counterfactuals([row("cf1", evidence_gap_found=True), row("cf2")])
        self.assertTrue(a.instability_signal)

    def test_identifying_a_falsifier_is_not_itself_instability(self):
        a = assess_counterfactuals([row("cf1", falsifier_identified=True), row("cf2", falsifier_identified=True)])
        self.assertFalse(a.instability_signal)

    def test_incomplete_probe_set_fails_toward_review(self):
        a = assess_counterfactuals([row("cf1"), row("cf2", complete=False)])
        self.assertEqual("INSUFFICIENT", a.status)
        self.assertTrue(a.instability_signal)

    def test_duplicate_probe_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            assess_counterfactuals([row("cf1"), row("cf1")])

    def test_empty_probe_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "required"):
            assess_counterfactuals([row(""), row("cf2")])

    def test_invalid_minimum_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            assess_counterfactuals([row("cf1")], minimum_complete_probes=0)


if __name__ == "__main__":
    unittest.main()
