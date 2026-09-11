from __future__ import annotations

import re
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]

# RELEASE qualification-contributing candidate workflows. New workflows must be
# added here before they can be cited as RELEASE qualification evidence.
QUALIFICATION_CONTRIBUTING_WORKFLOWS = (
    ".github/workflows/testing-qualification-boundary-ownership.yml",
    ".github/workflows/release-r1-hardening.yml",
    ".github/workflows/release-r3-phase-scoped-authority.yml",
    ".github/workflows/governed-execution-accelerator.yml",
    ".github/workflows/integrated-governed-mvp-slice11-coding-agent-adapter.yml",
)

USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)\s*(?:#.*)?$", re.MULTILINE)
IMMUTABLE_REF_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class ReleaseActionPinningTests(unittest.TestCase):
    def test_all_qualification_contributing_third_party_actions_are_immutable(self):
        checked = 0
        for relpath in QUALIFICATION_CONTRIBUTING_WORKFLOWS:
            path = REPO_ROOT / relpath
            self.assertTrue(path.is_file(), f"missing qualification-contributing workflow: {relpath}")
            text = path.read_text(encoding="utf-8")
            for uses in USES_RE.findall(text):
                # Local actions are candidate-owned and are not third-party action refs.
                if uses.startswith("./"):
                    continue
                checked += 1
                self.assertIn("@", uses, f"third-party action lacks an explicit ref: {relpath}: {uses}")
                action, ref = uses.rsplit("@", 1)
                self.assertTrue(action and IMMUTABLE_REF_RE.fullmatch(ref),
                                f"mutable/non-SHA third-party action ref: {relpath}: {uses}")
        self.assertGreater(checked, 0, "pinning regression did not inspect any third-party actions")

    def test_mutable_action_tag_negative_control_is_rejected(self):
        synthetic = "steps:\n  - uses: actions/checkout@v4\n"
        matches = USES_RE.findall(synthetic)
        self.assertEqual(["actions/checkout@v4"], matches)
        _, ref = matches[0].rsplit("@", 1)
        self.assertIsNone(IMMUTABLE_REF_RE.fullmatch(ref), "negative control unexpectedly accepted mutable tag")


if __name__ == "__main__":
    unittest.main()
