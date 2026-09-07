from __future__ import annotations

import unittest
from pathlib import Path


FORBIDDEN_PRODUCTION_ESCAPE_HATCH_IDENTIFIERS = (
    "allow_governance_bypass",
    "governance_bypass_enabled",
    "skip_governance_validation",
    "disable_governance_checks",
    "allow_legacy_bypass",
    "ignore_governance_failure",
)


class NoAuthorityBypassEscapeHatchTests(unittest.TestCase):
    def test_production_modules_do_not_define_explicit_governance_bypass_switches(self):
        """Prevent obvious debug/test/legacy authority exceptions from shipping.

        This is defense in depth, not a complete malicious-code detector. The
        primary protection remains the invariant/regression/full-suite/review
        lifecycle. This check blocks the most dangerous accidental pattern: a
        production switch whose purpose is to continue despite governance failure.
        """
        root = Path(__file__).resolve().parent
        violations: list[str] = []
        for path in sorted(root.glob("*.py")):
            if path.name.startswith("test_"):
                continue
            text = path.read_text(encoding="utf-8").lower()
            for identifier in FORBIDDEN_PRODUCTION_ESCAPE_HATCH_IDENTIFIERS:
                if identifier in text:
                    violations.append(f"{path.name}:{identifier}")
        self.assertEqual(violations, [], f"production governance bypass escape hatch detected: {violations}")


if __name__ == "__main__":
    unittest.main()
