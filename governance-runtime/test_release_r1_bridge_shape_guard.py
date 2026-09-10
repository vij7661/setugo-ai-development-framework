from __future__ import annotations

import asyncio
import inspect
import types
import unittest

import test_qualification_boundary_unittest_bridge as bridge


class ReleaseR1BridgeShapeGuardTests(unittest.TestCase):
    def _executor(self):
        executor = getattr(bridge, "_execute_sync_test_function", None)
        self.assertTrue(callable(executor), "REL-R1-01 bridge shape guard is not implemented")
        return executor

    def test_sync_zero_argument_function_executes(self):
        called = []
        def test_sync():
            called.append(True)
        self._executor()(test_sync)
        self.assertEqual([True], called)

    def test_async_function_is_rejected_before_false_green(self):
        async def test_async():
            return None
        with self.assertRaises(AssertionError):
            self._executor()(test_async)

    def test_generator_function_is_rejected_before_false_green(self):
        def test_generator():
            yield "not executed by a plain call"
        with self.assertRaises(AssertionError):
            self._executor()(test_generator)

    def test_async_generator_function_is_rejected_before_false_green(self):
        async def test_async_generator():
            yield "not executed by a plain call"
        with self.assertRaises(AssertionError):
            self._executor()(test_async_generator)

    def test_plain_function_returning_awaitable_is_rejected(self):
        def test_returns_awaitable():
            async def inner():
                return None
            return inner()
        with self.assertRaises(AssertionError):
            self._executor()(test_returns_awaitable)

    def test_plain_function_returning_generator_is_rejected(self):
        def test_returns_generator():
            return (item for item in (1,))
        with self.assertRaises(AssertionError):
            self._executor()(test_returns_generator)


if __name__ == "__main__":
    unittest.main()
