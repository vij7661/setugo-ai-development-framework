from __future__ import annotations

import json
import unittest

from exp_i_systematic_state_space import (
    ANCHOR_REPLACED_RECEIPT_PENDING,
    FAIL_CLOSED,
    LEDGER_AHEAD_EXACT,
    MAX_CONFLICT_ANCHOR,
    MAX_CRASHES,
    MAX_DEPTH,
    MAX_GENERATION,
    MAX_STALE_ANCHOR,
    MAX_STALE_LEDGER,
    RECONCILED,
    RECOVERY_IDS,
    TARGETS,
    WORKERS,
    State,
    authority_allowed,
    classifier,
    explore,
    successors,
)


class ExpISystematicStateSpaceTests(unittest.TestCase):
    def test_frozen_bounds_match_preregistration(self):
        self.assertEqual(MAX_GENERATION, 2)
        self.assertEqual(MAX_DEPTH, 14)
        self.assertEqual(MAX_CRASHES, 2)
        self.assertEqual(MAX_STALE_LEDGER, 1)
        self.assertEqual(MAX_STALE_ANCHOR, 1)
        self.assertEqual(MAX_CONFLICT_ANCHOR, 1)
        self.assertEqual(RECOVERY_IDS, ("REC-A", "REC-B"))
        self.assertEqual(TARGETS, ("TARGET-X", "TARGET-Y"))
        self.assertEqual(WORKERS, ("W1", "W2"))

    def test_frozen_pair_classifier_matches_pilot19_recovery_classes(self):
        b = (("REC-A", "TARGET-X"),)
        self.assertEqual(classifier(State()), RECONCILED)
        self.assertEqual(classifier(State(ledger=b)), LEDGER_AHEAD_EXACT)
        self.assertEqual(classifier(State(ledger=b, anchor=b)), ANCHOR_REPLACED_RECEIPT_PENDING)
        self.assertEqual(classifier(State(ledger=b, anchor=(("REC-A", "TARGET-Y"),))), FAIL_CLOSED)

    def test_authority_requires_exact_ledger_anchor_receipt_correspondence(self):
        b = (("REC-A", "TARGET-X"),)
        self.assertTrue(authority_allowed(State(ledger=b, anchor=b, receipt=b)))
        self.assertFalse(authority_allowed(State(ledger=b)))
        self.assertFalse(authority_allowed(State(ledger=b, anchor=b)))
        self.assertFalse(authority_allowed(State(ledger=b, anchor=(("REC-A", "TARGET-Y"),), receipt=b)))

    def test_crash_discards_uncommitted_issue_but_not_durable_authority(self):
        s = State(issue=("REC-A", "TARGET-X", "INSERTED"), crashes=0)
        crash = next(e for e in successors(s) if e.label == "CRASH_RESTART")
        self.assertIsNone(crash.state.issue)
        self.assertEqual(crash.state.ledger, s.ledger)
        self.assertEqual(crash.state.anchor, s.anchor)
        self.assertEqual(crash.state.receipt, s.receipt)
        self.assertEqual(crash.state.accepted_generation, s.accepted_generation)

    def test_systematic_frozen_analysis_gate(self):
        result = explore()
        # Preserve a stable machine-readable line in the exact CI job log.  If a
        # counterexample exists the assertion fails with the complete shortest trace.
        print("EXP_I_SYSTEMATIC_RESULT " + json.dumps({
            "status": result.status,
            "states": result.states,
            "transitions": result.transitions,
            "max_depth_reached": result.max_depth_reached,
            "classifications": result.classifications,
            "invariant_checks": result.invariant_checks,
            "liveness_states_checked": result.liveness_states_checked,
            "counterexample": result.counterexample,
        }, sort_keys=True))
        self.assertNotEqual(result.status, "HARNESS_FAILURE", result.to_json())
        self.assertEqual(result.status, "BOUNDED_SYSTEMATIC_PASS", result.to_json())
        self.assertIsNone(result.counterexample)
        self.assertGreater(result.states, 1)
        self.assertGreater(result.transitions, 1)
        self.assertEqual(result.max_depth_reached, MAX_DEPTH)
        self.assertGreater(result.invariant_checks, 1)
        self.assertGreater(result.liveness_states_checked, 0)


if __name__ == "__main__":
    unittest.main()
