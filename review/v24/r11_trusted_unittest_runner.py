from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import unittest


def modules_from_pinset(pinset_path: pathlib.Path) -> list[str]:
    obj = json.loads(pinset_path.read_text(encoding="utf-8"))
    if obj.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH":
        raise SystemExit("TRUSTED_RUNNER_PINSET_AUTHORITY_INVALID")
    if obj.get("candidate_self_grant") is not False:
        raise SystemExit("TRUSTED_RUNNER_PINSET_SELF_GRANT_FORBIDDEN")
    tests = obj.get("executed_tests")
    if not isinstance(tests, list) or not tests:
        raise SystemExit("TRUSTED_RUNNER_EXECUTED_TESTS_REQUIRED")
    modules: list[str] = []
    seen: set[str] = set()
    for raw in tests:
        if not isinstance(raw, str) or not raw.startswith("governance-runtime/test_") or not raw.endswith(".py"):
            raise SystemExit(f"TRUSTED_RUNNER_INVALID_TEST_PATH:{raw}")
        path = pathlib.PurePosixPath(raw)
        if len(path.parts) != 2:
            raise SystemExit(f"TRUSTED_RUNNER_NESTED_TEST_PATH_FORBIDDEN:{raw}")
        module = path.stem
        if module in seen:
            raise SystemExit(f"TRUSTED_RUNNER_DUPLICATE_TEST_MODULE:{module}")
        seen.add(module)
        modules.append(module)
    return modules


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--pinset", required=True)
    args = ap.parse_args()

    sandbox = pathlib.Path(args.sandbox).resolve()
    subject = sandbox / "governance-runtime"
    pinset = pathlib.Path(args.pinset).resolve()
    startup_path = list(sys.path)

    if "" in startup_path or str(subject) in startup_path or str(sandbox) in startup_path:
        raise SystemExit(f"TRUSTED_RUNNER_CANDIDATE_PATH_PRESENT_AT_STARTUP:{startup_path!r}")

    unittest_path = pathlib.Path(unittest.__file__).resolve()
    if unittest_path.is_relative_to(sandbox):
        raise SystemExit("TRUSTED_RUNNER_UNITTEST_RESOLVED_FROM_CANDIDATE")

    modules = modules_from_pinset(pinset)

    # Only after stdlib unittest and the external pinset have been loaded do we
    # move into the candidate sandbox and make its Python bytes importable.
    os.chdir(sandbox)
    sys.path.insert(0, str(subject))

    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    print(f"TRUSTED_RUNNER_TEST_CASES={suite.countTestCases()}")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
