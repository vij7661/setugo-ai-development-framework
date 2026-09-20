"""Run the offline EXP-M unit/phase suites and bind their result to source."""
from __future__ import annotations
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (("core", "governance-runtime/test_exp_m_deterministic.py"), ("phases", "governance-runtime/test_exp_m_phases.py"))

def main() -> int:
    results = []
    for name, script in COMMANDS:
        completed = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        output = completed.stdout + completed.stderr
        match = re.search(r"Ran (\d+) tests", output)
        total = int(match.group(1)) if match else 0
        passed = total if completed.returncode == 0 and "OK" in output else 0
        results.append({"suite": name, "command": f"python {script}", "exit_code": completed.returncode, "tests_total": total, "tests_passed": passed, "tests_failed": total - passed, "stdout_stderr": output})
    total = sum(r["tests_total"] for r in results); passed = sum(r["tests_passed"] for r in results)
    result = {"tests_total": total, "tests_passed": passed, "tests_failed": total - passed, "all_passed": total == passed and total > 0, "suites": results,
              "execution": {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_tests.py", "interpreter": sys.executable}}
    out = ROOT / "experiments/governed-platform/EXP-M-TEST-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
