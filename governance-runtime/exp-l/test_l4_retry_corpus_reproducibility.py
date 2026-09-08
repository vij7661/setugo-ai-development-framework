from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/retry_freeze_v2.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("retry_freeze_v2", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def frozen(m, *, base="a"*40, candidate="b"*40, manifest="c"*64, corpus=None):
    return m.freeze_review_input(
        review_request_id="R",
        request_hash="d"*64,
        base_commit=base,
        candidate_commit=candidate,
        evidence_manifest_sha256=manifest,
        corpus=corpus if corpus is not None else {"evidence":[{"id":"x","value":1}]},
    )


class RetryCorpusReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def test_l4_01_main_advance_does_not_change_frozen_base(self):
        first = frozen(self.m, base="a"*40)
        retry = frozen(self.m, base="a"*40)
        moving_main_now = "f"*40
        self.assertNotEqual(moving_main_now, first["base_commit"])
        self.assertEqual(first["base_commit"], retry["base_commit"])
        self.assertTrue(self.m.classify_retry(first, retry)["same_frozen_retry"])

    def test_l4_02_unrelated_main_change_does_not_change_corpus_hash(self):
        corpus = {"candidate":"b"*40,"files":[{"path":"x","sha256":"1"*64}]}
        first = frozen(self.m, corpus=corpus)
        retry = frozen(self.m, corpus=corpus)
        self.assertEqual(first["corpus_sha256"], retry["corpus_sha256"])
        self.assertEqual(first["retry_identity_sha256"], retry["retry_identity_sha256"])

    def test_l4_03_manifest_change_requires_new_governed_input(self):
        first = frozen(self.m, manifest="c"*64)
        changed = frozen(self.m, manifest="e"*64)
        result = self.m.classify_retry(first, changed)
        self.assertFalse(result["same_frozen_retry"])
        self.assertEqual(result["classification"], "NEW_GOVERNED_INPUT_REQUIRED")
        self.assertIn("evidence_manifest_sha256", result["differences"])

    def test_l4_04_candidate_change_requires_new_governed_input(self):
        first = frozen(self.m, candidate="b"*40)
        changed = frozen(self.m, candidate="9"*40)
        result = self.m.classify_retry(first, changed)
        self.assertFalse(result["same_frozen_retry"])
        self.assertIn("candidate_commit", result["differences"])

    def test_l4_05_identical_inputs_have_exact_retry_identity(self):
        first = frozen(self.m)
        retry = frozen(self.m)
        self.assertEqual(first, retry)
        result = self.m.classify_retry(first, retry)
        self.assertTrue(result["same_frozen_retry"])
        self.assertEqual(result["differences"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
