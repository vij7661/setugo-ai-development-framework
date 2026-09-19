import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v24_v6_rq1_remediation2_harness import observed_entries, target_lifecycle, set_delta

class CrashObservationTests(unittest.TestCase):
    def test_error_never_counts_metadata_keys_as_entries(self):
        with self.assertRaises(RuntimeError):
            observed_entries({"entries": [], "error": "PermissionError"}, "consumed")

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

if __name__ == "__main__":
    unittest.main()
