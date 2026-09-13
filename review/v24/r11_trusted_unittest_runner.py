from __future__ import annotations

import argparse
import pathlib
import sys
import unittest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("modules", nargs="+")
    args = ap.parse_args()

    sandbox = pathlib.Path(args.sandbox).resolve()
    subject = sandbox / "governance-runtime"
    startup_path = list(sys.path)

    if "" in startup_path or str(subject) in startup_path or str(sandbox) in startup_path:
        raise SystemExit(f"TRUSTED_RUNNER_CANDIDATE_PATH_PRESENT_AT_STARTUP:{startup_path!r}")

    unittest_path = pathlib.Path(unittest.__file__).resolve()
    if unittest_path.is_relative_to(sandbox):
        raise SystemExit("TRUSTED_RUNNER_UNITTEST_RESOLVED_FROM_CANDIDATE")

    sys.path.insert(0, str(subject))
    suite = unittest.defaultTestLoader.loadTestsFromNames(args.modules)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
