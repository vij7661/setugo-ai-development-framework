"""Scientific construction tests for the post-P19 bounded state-space analysis."""
from __future__ import annotations

import json
import unittest

from exp_i_issuance_anchor_state_space import (
    LIVENESS_MAX_STEPS,
    MAX_DEPTH,
    MAX_GENERATION,
    State,
    can_authorize,
    explore,
    find_mutant_counterexample,
    pair_status,
    reconciliation_targets,
    scientific_summary,
    successors,
)


class ExpIStateSpaceIssuanceAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = explore()
        cls.summary = scientific_summary()
        print("EXP_I_STATE_SPACE_SUMMARY=" + json.dumps(cls.summary, sort_keys=True), flush=True)

    def test_sa_00_frozen_bounds_are_exact(self):
        self.assertEqual(MAX_GENERATION, 3)
        self.assertEqual(MAX_DEPTH, 12)
        self.assertEqual(LIVENESS_MAX_STEPS, 8)
        self.assertEqual(self.summary["bounds"]["sa09_local_liveness_steps"], 8)
        self.assertEqual(self.result.max_depth_reached, MAX_DEPTH)
        self.assertGreater(self.result.visited_states, 0)
        self.assertGreater(self.result.transitions_checked, self.result.visited_states)

    def test_sa_01_no_authority_from_ambiguity(self):
        self.assertNotIn("SA-01", {v.invariant for v in self.result.violations})

    def test_sa_02_no_ledger_only_authority(self):
        self.assertNotIn("SA-02", {v.invariant for v in self.result.violations})
        ledger_ahead = State(ledger=(("A", "T1"),), anchor=(), receipt=())
        self.assertEqual(pair_status(ledger_ahead), "LEDGER_AHEAD_EXACT")
        self.assertFalse(can_authorize(ledger_ahead))

    def test_sa_03_no_anchor_only_authority(self):
        self.assertNotIn("SA-03", {v.invariant for v in self.result.violations})
        anchor_ahead = State(ledger=(), anchor=(("A", "T1"),), receipt=())
        self.assertEqual(pair_status(anchor_ahead), "FAIL_CLOSED")
        self.assertFalse(can_authorize(anchor_ahead))

    def test_sa_04_monotonic_trust(self):
        self.assertNotIn("SA-04", {v.invariant for v in self.result.violations})

    def test_sa_05_no_semantic_rebinding(self):
        self.assertNotIn("SA-05", {v.invariant for v in self.result.violations})

    def test_sa_06_at_most_once_consequential_advancement(self):
        self.assertNotIn("SA-06", {v.invariant for v in self.result.violations})

    def test_sa_07_reconciliation_is_actor_independent(self):
        self.assertNotIn("SA-07", {v.invariant for v in self.result.violations})
        state = State(ledger=(("A", "T1"),), anchor=(), receipt=())
        targets = reconciliation_targets(state)
        self.assertEqual(targets["R1"], targets["R2"])

    def test_sa_08_conflicts_fail_closed(self):
        self.assertNotIn("SA-08", {v.invariant for v in self.result.violations})
        conflict = State(
            ledger=(("A", "T1"),),
            anchor=(("A", "T2"),),
            receipt=(("A", "T1"),),
        )
        self.assertEqual(pair_status(conflict), "FAIL_CLOSED")
        self.assertFalse(can_authorize(conflict))

    def test_sa_09_bounded_liveness_from_recoverable_states(self):
        self.assertNotIn("SA-09", {v.invariant for v in self.result.violations})

    def test_sa_10_external_authority(self):
        self.assertNotIn("SA-10", {v.invariant for v in self.result.violations})

    def test_production_model_has_zero_frozen_invariant_counterexamples(self):
        self.assertEqual(self.result.violations, ())
        self.assertEqual(self.summary["production_violations"], [])

    def test_mut_01_explorer_detects_ledger_only_authority(self):
        v = find_mutant_counterexample("ledger_only")
        self.assertIsNotNone(v)
        assert v is not None
        self.assertEqual(v.invariant, "SA-02")
        self.assertGreater(len(v.trace), 0)

    def test_mut_02_explorer_detects_caller_selected_conflict(self):
        v = find_mutant_counterexample("caller_selects_conflict")
        self.assertIsNotNone(v)
        assert v is not None
        self.assertEqual(v.invariant, "SA-10")
        self.assertIn("same-generation-anchor-conflict", " ".join(v.trace))

    def test_mut_03_explorer_detects_anchor_only_authority(self):
        v = find_mutant_counterexample("anchor_only")
        self.assertIsNotNone(v)
        assert v is not None
        self.assertEqual(v.invariant, "SA-03")
        self.assertIn("stale-ledger", " ".join(v.trace))

    def test_mut_04_explorer_detects_semantic_rebind(self):
        v = find_mutant_counterexample("semantic_rebind")
        self.assertIsNotNone(v)
        assert v is not None
        self.assertEqual(v.invariant, "SA-05")
        self.assertIn("issue-rebind", " ".join(v.trace))

    def test_restart_cannot_promote_untrusted_temp_material(self):
        state = State(ledger=(("A", "T1"),), anchor=(), receipt=(), temp_anchor=(("A", "T1"),))
        restart = [x for x in successors(state, include_attacks=False) if x.action == "crash-restart-discard-untrusted-temp"]
        self.assertEqual(len(restart), 1)
        self.assertEqual(restart[0].state.anchor, ())
        self.assertEqual(restart[0].state.receipt, ())
        self.assertFalse(can_authorize(restart[0].state))


if __name__ == "__main__":
    unittest.main(verbosity=2)
