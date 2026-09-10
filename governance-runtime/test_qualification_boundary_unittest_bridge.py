from __future__ import annotations

import inspect
import unittest

import test_manual_authority_verifier as manual_verifier
import test_manual_review_authority_ingress_regression as ingress
import test_manual_review_authority_spoofing_regression as spoofing
import test_qualification_boundary_policy as ownership


def _module_tests(module):
    return sorted(
        (name, obj)
        for name, obj in vars(module).items()
        if name.startswith("test_") and inspect.isfunction(obj) and obj.__module__ == module.__name__
    )


def _execute_sync_test_function(fn):
    """Execute only a synchronous test body; reject unevaluated async/generator shapes."""
    if inspect.iscoroutinefunction(fn):
        raise AssertionError("qualification bridge rejects coroutine test functions")
    if inspect.isgeneratorfunction(fn):
        raise AssertionError("qualification bridge rejects generator test functions")
    if inspect.isasyncgenfunction(fn):
        raise AssertionError("qualification bridge rejects async-generator test functions")

    result = fn()
    if inspect.isawaitable(result):
        if inspect.iscoroutine(result):
            result.close()
        raise AssertionError("qualification bridge rejects unevaluated awaitable test results")
    if inspect.isgenerator(result):
        result.close()
        raise AssertionError("qualification bridge rejects unevaluated generator test results")
    if inspect.isasyncgen(result):
        raise AssertionError("qualification bridge rejects unevaluated async-generator test results")
    return result


class QualificationBoundaryModuleFunctionBridgeTests(unittest.TestCase):
    def test_all_ownership_module_tests_are_executed(self):
        tests = _module_tests(ownership)
        self.assertGreaterEqual(len(tests), 15, "ownership module unexpectedly exposes too few tests")
        for name, fn in tests:
            with self.subTest(module=ownership.__name__, test=name):
                _execute_sync_test_function(fn)

    def test_all_manual_authority_verifier_module_tests_are_executed(self):
        tests = _module_tests(manual_verifier)
        self.assertEqual(2, len(tests), "manual-authority verifier regression count changed")
        for name, fn in tests:
            with self.subTest(module=manual_verifier.__name__, test=name):
                _execute_sync_test_function(fn)

    def test_all_frozen_manual_spoofing_regressions_are_executed(self):
        tests = _module_tests(spoofing)
        self.assertEqual(4, len(tests), "frozen manual spoofing regression count changed")
        for name, fn in tests:
            with self.subTest(module=spoofing.__name__, test=name):
                _execute_sync_test_function(fn)

    def test_all_frozen_authority_ingress_regressions_are_executed(self):
        tests = _module_tests(ingress)
        self.assertEqual(2, len(tests), "frozen authority-ingress regression count changed")
        for name, fn in tests:
            with self.subTest(module=ingress.__name__, test=name):
                _execute_sync_test_function(fn)


if __name__ == "__main__":
    unittest.main()
