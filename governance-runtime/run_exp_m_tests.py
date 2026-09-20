"""Run the offline EXP-M unit/phase suites and bind their result to source."""
from __future__ import annotations
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (("core", "governance-runtime/test_exp_m_deterministic.py"), ("phases", "governance-runtime/test_exp_m_phases.py"))


def _summary_counts(output: str, total: int, returncode: int) -> dict[str, int]:
    def count(label: str) -> int:
        match = re.search(rf"{re.escape(label)}=(\d+)", output)
        return int(match.group(1)) if match else 0

    failures = count("failures")
    errors = count("errors")
    skipped = count("skipped")
    expected_failures = count("expected failures")
    unexpected_successes = count("unexpected successes")
    nonpasses = failures + errors + skipped + expected_failures + unexpected_successes
    if returncode != 0 and nonpasses == 0:
        # Fail closed if unittest aborted without a standard summary.
        nonpasses = total
        errors = total
    passed = max(0, total - nonpasses)
    return {
        "tests_passed": passed,
        "tests_failed": failures,
        "tests_errors": errors,
        "tests_skipped": skipped,
        "tests_expected_failures": expected_failures,
        "tests_unexpected_successes": unexpected_successes,
        "tests_nonpassing": nonpasses,
    }


def main() -> int:
    results = []
    for name, script in COMMANDS:
        completed = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        output = completed.stdout + completed.stderr
        match = re.search(r"Ran (\d+) tests", output)
        total = int(match.group(1)) if match else 0
        counts = _summary_counts(output, total, completed.returncode)
        suite_all_passed = (
            completed.returncode == 0
            and total > 0
            and counts["tests_nonpassing"] == 0
            and counts["tests_passed"] == total
        )
        results.append({
            "suite": name,
            "command": f"python {script}",
            "exit_code": completed.returncode,
            "tests_total": total,
            **counts,
            "all_passed": suite_all_passed,
            "stdout_stderr": output,
        })

    total = sum(r["tests_total"] for r in results)
    passed = sum(r["tests_passed"] for r in results)
    nonpassing = sum(r["tests_nonpassing"] for r in results)
    result = {
        "tests_total": total,
        "tests_passed": passed,
        "tests_nonpassing": nonpassing,
        "tests_failed": sum(r["tests_failed"] for r in results),
        "tests_errors": sum(r["tests_errors"] for r in results),
        "tests_skipped": sum(r["tests_skipped"] for r in results),
        "tests_expected_failures": sum(r["tests_expected_failures"] for r in results),
        "tests_unexpected_successes": sum(r["tests_unexpected_successes"] for r in results),
        "all_passed": total > 0 and passed == total and nonpassing == 0 and all(r["all_passed"] for r in results),
        "suites": results,
        "execution": {
            "source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(),
            "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(),
            "utc": datetime.now(timezone.utc).isoformat(),
            "command": "python governance-runtime/run_exp_m_tests.py",
            "interpreter": sys.executable,
        },
    }
    out = ROOT / "experiments/governed-platform/EXP-M-TEST-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
