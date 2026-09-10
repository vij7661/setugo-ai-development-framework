from __future__ import annotations

import inspect
import unittest

import test_manual_review_authority_spoofing_regression as spoofing
import test_qualification_boundary_policy as ownership


def _module_tests(module):
    return sorted(
        (name, obj)
        for name, obj in vars(module).items()
        if name.startswith("test_") and inspect.isfunction(obj) and obj.__module__ == module.__name__
    )


class QualificationBoundaryModuleFunctionBridgeTests(unittest.TestCase):
    def test_all_ownership_module_tests_are_executed(self):
        tests = _module_tests(ownership)
        self.assertGreaterEqual(len(tests), 15, "ownership module unexpectedly exposes too few tests")
        for name, fn in tests:
            with self.subTest(module=ownership.__name__, test=name):
                fn()

    def test_all_frozen_manual_spoofing_regressions_are_executed(self):
        tests = _module_tests(spoofing)
        self.assertEqual(4, len(tests), "frozen manual spoofing regression count changed")
        for name, fn in tests:
            with self.subTest(module=spoofing.__name__, test=name):
                fn()


if __name__ == "__main__":
    unittest.main()
