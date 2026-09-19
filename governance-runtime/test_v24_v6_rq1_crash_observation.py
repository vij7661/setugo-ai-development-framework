import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v24_v6_rq1_remediation2_harness import observed_entries, target_lifecycle, set_delta, exact_delta, exact_boundary_target

class CrashObservationTests(unittest.TestCase):
    def test_error_never_counts_metadata_keys_as_entries(self):
        with self.assertRaises(RuntimeError):
            observed_entries({"entries": [], "error": "PermissionError"}, "consumed")
        with self.assertRaises(RuntimeError):
            observed_entries({"consumed": {"entries": [], "error": "PermissionError"}}, "consumed")

    def test_empty_entries_are_distinct_from_observed_entry(self):
        self.assertEqual(observed_entries({"consumed": {"entries": []}}, "consumed"), [])
        self.assertEqual(observed_entries({"consumed": {"entries": [{"name": "x.record"}]}}, "consumed"), [{"name": "x.record"}])

    def test_missing_or_malformed_shape_fails_closed(self):
        for value in ({}, {"records": {"entries": None}}, {"records": {"error": "inaccessible"}}):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    observed_entries(value, "records")

    def test_historical_consumed_entries_cannot_satisfy_target(self):
        historical=[{"name":f"old-{i}.record"} for i in range(100)]
        obs={"records":{"entries":[{"name":"target.record"}]},"consumed":{"entries":historical}}
        life=target_lifecycle(obs,"target.record")
        self.assertTrue(life["records"])
        self.assertFalse(life["consumed"])

    def test_target_transition_is_identity_bound(self):
        before={"records":{"entries":[{"name":"target.record"}]},"consumed":{"entries":[{"name":"old.record"}]}}
        after={"records":{"entries":[]},"consumed":{"entries":[{"name":"old.record"},{"name":"target.record"}]}}
        self.assertEqual(set_delta(before,after,"consumed"),{"added":["target.record"],"removed":[]})
        self.assertEqual(set_delta(before,after,"records"),{"added":[],"removed":["target.record"]})

    def test_wrong_boundary_record_is_not_target(self):
        obs={"records":{"entries":[{"name":"other.record"}]},"consumed":{"entries":[]}}
        life=target_lifecycle(obs,"target.record")
        self.assertFalse(life["records"])
        self.assertFalse(life["consumed"])

    def test_unrelated_new_consumed_does_not_satisfy_target(self):
        recovery={"records":{"entries":[{"name":"target.record"}]},"consumed":{"entries":[{"name":"old.record"},{"name":"new-unrelated.record"}]}}
        life=target_lifecycle(recovery,"target.record")
        self.assertTrue(life["records"]); self.assertFalse(life["consumed"])

    def test_target_transition_only_after_retry_is_distinguished(self):
        prepared={"records":{"entries":[{"name":"target.record"}]},"consumed":{"entries":[]}}
        recovery=prepared
        post_retry={"records":{"entries":[]},"consumed":{"entries":[{"name":"target.record"}]}}
        self.assertEqual(set_delta(prepared,recovery,"records"),{"added":[],"removed":[]})
        self.assertEqual(set_delta(prepared,recovery,"consumed"),{"added":[],"removed":[]})
        self.assertEqual(set_delta(recovery,post_retry,"records"),{"added":[],"removed":["target.record"]})

    def test_target_already_consumed_before_retry_is_distinguished(self):
        recovery={"records":{"entries":[]},"consumed":{"entries":[{"name":"target.record"}]}}
        life=target_lifecycle(recovery,"target.record")
        self.assertFalse(life["records"]); self.assertTrue(life["consumed"])

    def test_exact_delta_rejects_unrelated_transition(self):
        delta={"added":["target.record","unrelated.record"],"removed":["target.record","unrelated.record"]}
        self.assertFalse(exact_delta(delta,added=["target.record"],removed=["target.record"]))

    def test_replay_deny_with_state_mutation_is_not_pass(self):
        before={"records":{"entries":[]},"consumed":{"entries":[{"name":"target.record"}]}}
        after={"records":{"entries":[{"name":"other.record"}]},"consumed":{"entries":[{"name":"target.record"}]}}
        self.assertNotEqual(set_delta(before,after,"records"),{"added":[],"removed":[]})

    def test_exact_boundary_rejects_wrong_destination_and_collision(self):
        trace={"paths":["/run/v24-v6-authority/private/records/target.record","/run/v24-v6-authority/private/consumed/other.record"]}
        self.assertFalse(exact_boundary_target("RQ-15","target.record",trace))
        collision={"paths":["/run/v24-v6-authority/private/records/target.record.extra"]}
        self.assertFalse(exact_boundary_target("RQ-13","target.record",collision))

if __name__ == "__main__":
    unittest.main()
