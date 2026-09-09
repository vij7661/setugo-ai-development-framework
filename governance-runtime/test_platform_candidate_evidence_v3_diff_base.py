from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

import platform_candidate_evidence_v3 as evidence


CANDIDATE = "f" * 40
BASE = "b" * 40


class CandidateDiffBaseTests(unittest.TestCase):
    def _request(self, base=BASE):
        return {
            "artifact": {"commit": CANDIDATE},
            "candidate_diff_base_commit": base,
            "evidence_refs": [],
        }

    def test_pinned_candidate_diff_base_is_used_instead_of_origin_main(self):
        calls = []

        def fake_git(root, *args):
            calls.append(args)
            if args[:2] == ("rev-parse", f"{BASE}^{{commit}}"):
                return BASE + "\n"
            if args[:2] == ("merge-base", "--is-ancestor"):
                return ""
            if args and args[0] == "diff":
                self.assertEqual(BASE, args[2])
                self.assertEqual(CANDIDATE, args[3])
                return "bounded-diff"
            raise AssertionError(f"unexpected git call: {args}")

        with patch.object(evidence.legacy, "require_commit"), patch.object(evidence.legacy, "git", side_effect=fake_git):
            corpus = evidence.build_corpus(Path("."), self._request())

        self.assertEqual(BASE, corpus["base_commit"])
        self.assertEqual("bounded-diff", corpus["candidate_diff"])
        self.assertNotIn(("merge-base", "origin/main", CANDIDATE), calls)

    def test_non_exact_diff_base_fails_closed(self):
        with patch.object(evidence.legacy, "require_commit"):
            with self.assertRaises(ValueError):
                evidence.build_corpus(Path("."), self._request("main"))

    def test_non_ancestor_diff_base_fails_closed(self):
        def fake_git(root, *args):
            if args[:2] == ("rev-parse", f"{BASE}^{{commit}}"):
                return BASE + "\n"
            if args[:2] == ("merge-base", "--is-ancestor"):
                raise RuntimeError("not ancestor")
            raise AssertionError(f"unexpected git call: {args}")

        with patch.object(evidence.legacy, "require_commit"), patch.object(evidence.legacy, "git", side_effect=fake_git):
            with self.assertRaises(ValueError):
                evidence.build_corpus(Path("."), self._request())


if __name__ == "__main__":
    unittest.main()
