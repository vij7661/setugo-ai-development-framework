import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v24_v6_rq1_remediation2_harness import observed_entries

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

if __name__ == "__main__":
    unittest.main()
