import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).with_name('measure_review_latency_exp_p.py')
spec = importlib.util.spec_from_file_location('exp_p_latency', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ExpPPilot1LatencyHarnessTests(unittest.TestCase):
    def test_frozen_paths_have_exact_stage_counts(self):
        self.assertEqual(mod.PATHS['R1-R2-R1'], ['R1', 'R2', 'R1'])
        self.assertEqual(mod.PATHS['R1-R2-R1-R3'], ['R1', 'R2', 'R1', 'R3'])
        self.assertEqual(mod.PATHS['R1-R2-R1-R3-R1'], ['R1', 'R2', 'R1', 'R3', 'R1'])
        self.assertEqual(sum(len(v) for v in mod.PATHS.values()) * 10, 120)

    def test_frozen_role_mapping(self):
        self.assertEqual(mod.ROLE_CONFIG['R1']['provider'], 'groq')
        self.assertEqual(mod.ROLE_CONFIG['R2']['provider'], 'gemini')
        self.assertEqual(mod.ROLE_CONFIG['R3']['provider'], 'mistral')

    def test_nearest_rank_percentiles(self):
        vals = list(range(1, 11))
        self.assertEqual(mod.nearest_rank(vals, 0.50), 5)
        self.assertEqual(mod.nearest_rank(vals, 0.95), 10)

    def test_empty_summary_is_explicit(self):
        s = mod.summarize([])
        self.assertEqual(s['n'], 0)
        self.assertIsNone(s['p50_ms'])
        self.assertIsNone(s['p95_ms'])


if __name__ == '__main__':
    unittest.main()
