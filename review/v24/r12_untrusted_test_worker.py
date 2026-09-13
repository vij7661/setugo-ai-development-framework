from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import pathlib
import sys
import tempfile
import types
import unittest

PREFIX = "R12_WORKER_RESULT="


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _callable_fingerprint(obj: object) -> dict[str, object]:
    code = getattr(obj, "__code__", None)
    return {
        "id": id(obj),
        "module": getattr(obj, "__module__", None),
        "qualname": getattr(obj, "__qualname__", None),
        "code_sha256": _sha(code.co_code) if code is not None else None,
        "const_sha256": _sha(repr(code.co_consts).encode("utf-8")) if code is not None else None,
    }


def framework_fingerprint() -> dict[str, object]:
    return {
        "unittest_module_file": str(pathlib.Path(unittest.__file__).resolve()),
        "TextTestRunner": _callable_fingerprint(unittest.TextTestRunner),
        "TextTestRunner.run": _callable_fingerprint(unittest.TextTestRunner.run),
        "TestResult.wasSuccessful": _callable_fingerprint(unittest.TestResult.wasSuccessful),
        "TestCase.run": _callable_fingerprint(unittest.TestCase.run),
        "TestCase.fail": _callable_fingerprint(unittest.TestCase.fail),
        "TestLoader.loadTestsFromName": _callable_fingerprint(unittest.TestLoader.loadTestsFromName),
        "default_loader_id": id(unittest.defaultTestLoader),
    }


def require_actual_isolation() -> dict[str, bool]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    for key, value in flags.items():
        if value is not True:
            raise SystemExit(f"R12_WORKER_ACTUAL_INTERPRETER_FLAG_NOT_TRUE:{key}")
    return flags


def _internal_negative_canary(runner_cls: type[unittest.TextTestRunner]) -> bool:
    class _Canary(unittest.TestCase):
        def runTest(self):
            raise AssertionError("R12_TRUSTED_NEGATIVE_CANARY")

    stream = io.StringIO()
    result = runner_cls(stream=stream, verbosity=0).run(unittest.TestSuite([_Canary()]))
    # Use raw result fields, not result.wasSuccessful(), so a monkeypatch of
    # wasSuccessful alone cannot turn the negative canary green.
    return result.testsRun == 1 and len(result.failures) + len(result.errors) == 1


def load_allowed_module(pinset: dict, module: str) -> None:
    expected = {
        pathlib.PurePosixPath(x).stem
        for x in pinset.get("executed_tests", [])
        if isinstance(x, str)
    }
    if module not in expected:
        raise SystemExit(f"R12_WORKER_MODULE_NOT_PINNED:{module}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--pinset", required=True)
    parser.add_argument("--module", required=True)
    args = parser.parse_args()

    flags = require_actual_isolation()
    sandbox = pathlib.Path(args.sandbox).resolve()
    subject = sandbox / "governance-runtime"
    pinset_path = pathlib.Path(args.pinset).resolve()
    startup_path = list(sys.path)
    if "" in startup_path or str(subject) in startup_path or str(sandbox) in startup_path:
        raise SystemExit(f"R12_WORKER_CANDIDATE_PATH_PRESENT_AT_STARTUP:{startup_path!r}")
    unittest_path = pathlib.Path(unittest.__file__).resolve()
    if unittest_path.is_relative_to(sandbox):
        raise SystemExit("R12_WORKER_UNITTEST_RESOLVED_FROM_CANDIDATE")

    pinset = json.loads(pinset_path.read_text(encoding="utf-8"))
    if pinset.get("schema_version") != 2:
        raise SystemExit("R12_WORKER_PINSET_SCHEMA_INVALID")
    if pinset.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH" or pinset.get("candidate_self_grant") is not False:
        raise SystemExit("R12_WORKER_PINSET_AUTHORITY_INVALID")
    load_allowed_module(pinset, args.module)

    baseline = framework_fingerprint()
    trusted_runner_cls = unittest.TextTestRunner
    trusted_loader = unittest.TestLoader()
    if not _internal_negative_canary(trusted_runner_cls):
        raise SystemExit("R12_WORKER_PREIMPORT_NEGATIVE_CANARY_FAILED")

    sys.dont_write_bytecode = True
    os.chdir(sandbox)
    sys.path.insert(0, str(subject))

    # Candidate stdout/stderr is suppressed at the Python layer during module
    # load and test execution. The trusted envelope is emitted only after the
    # candidate phase completes and framework/canary checks have passed.
    candidate_stdout = io.StringIO()
    candidate_stderr = io.StringIO()
    with contextlib.redirect_stdout(candidate_stdout), contextlib.redirect_stderr(candidate_stderr):
        suite = trusted_loader.loadTestsFromName(args.module)
        post_import = framework_fingerprint()
        if post_import != baseline:
            raise SystemExit("R12_WORKER_UNITTEST_MUTATED_DURING_IMPORT")
        if not _internal_negative_canary(trusted_runner_cls):
            raise SystemExit("R12_WORKER_POSTIMPORT_NEGATIVE_CANARY_FAILED")
        expected = suite.countTestCases()
        stream = io.StringIO()
        result = trusted_runner_cls(stream=stream, verbosity=2).run(suite)
        post_run = framework_fingerprint()
        if post_run != baseline:
            raise SystemExit("R12_WORKER_UNITTEST_MUTATED_DURING_TEST_EXECUTION")
        if not _internal_negative_canary(trusted_runner_cls):
            raise SystemExit("R12_WORKER_POSTRUN_NEGATIVE_CANARY_FAILED")

    failures = len(getattr(result, "failures", ()))
    errors = len(getattr(result, "errors", ()))
    unexpected = len(getattr(result, "unexpectedSuccesses", ()))
    tests_run = int(getattr(result, "testsRun", -1))
    successful = tests_run == expected and failures == 0 and errors == 0 and unexpected == 0
    envelope = {
        "schema_version": 1,
        "module": args.module,
        "expected_tests": expected,
        "tests_run": tests_run,
        "failures": failures,
        "errors": errors,
        "unexpected_successes": unexpected,
        "successful": successful,
        "framework_integrity": True,
        "negative_canaries": {
            "before_candidate_import": "PASS",
            "after_candidate_import": "PASS",
            "after_test_execution": "PASS",
        },
        "actual_interpreter_flags": flags,
        "candidate_stdout_sha256": _sha(candidate_stdout.getvalue().encode("utf-8")),
        "candidate_stderr_sha256": _sha(candidate_stderr.getvalue().encode("utf-8")),
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    # os.write bypasses candidate replacement of sys.stdout objects.
    os.write(1, (PREFIX + json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    raise SystemExit(0 if successful else 1)


if __name__ == "__main__":
    main()
