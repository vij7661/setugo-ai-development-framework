#!/usr/bin/env python3
"""Build a self-contained Remediation-7 package from supplied run-35 evidence.

The command is intentionally fail-closed: it refuses to build a package when
the immutable RQ-13/14/15 raw evidence directory is absent or incomplete.
It performs no runtime operation.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

CASES = ("RQ-13", "RQ-14", "RQ-15")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--replay-output", type=Path, required=True)
    ap.add_argument("--mutation-output", type=Path, required=True)
    ap.add_argument("--test-output", type=Path, required=True)
    ap.add_argument("--validator-output", type=Path, required=True)
    args = ap.parse_args()
    required = [f"{case}.result.json" for case in CASES]
    required += [f"{case}.boundary.json" for case in CASES]
    required += [f"{case}.tracer-ready.json" for case in CASES]
    missing = [name for name in required if not (args.evidence / name).is_file()]
    if missing:
        raise SystemExit("INSUFFICIENT_EVIDENCE: missing immutable raw files: " + ", ".join(missing))
    args.output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(args.evidence, args.output / "raw-evidence")
    source = args.output / "source"; source.mkdir()
    for name in ("v24_v6_rq1_crash_predicates.py", "v24_v6_rq1_remediation2_harness.py", "v24_v6_rq1_observer.py", "replay_rq1_crash_evidence.py", "run_rq1_remediation7_mutations.py", "test_v24_v6_rq1_crash_observation.py", "validate_rq1_oracle_contract.py"):
        shutil.copy2(args.repo_root / "governance-runtime" / name, source / name)
    design = args.output / "design"; design.mkdir()
    for name in ("V24-I11-V6-RQ1-REMEDIATION-2-ORACLE-CONTRACT.json", "V24-I11-V6-RQ1-REMEDIATION-2-ORACLE-CONTRACT.md", "V24-I11-V6-RUNTIME-QUALIFICATION-1-PLAN.md"):
        shutil.copy2(args.repo_root / "implementation" / "v24" / name, design / name)
    shutil.copy2(args.repo_root / "implementation" / "v24" / "V24-I11-V6-RQ1-REMEDIATION-6-BOUNDED-PASS-CLOSURE.md", args.output)
    shutil.copy2(args.repo_root / "implementation" / "v24" / "V24-I11-V6-RQ1-REMEDIATION-7-BACKLOG.md", args.output)
    shutil.copy2(args.replay_output, args.output / "offline-replay.json")
    shutil.copy2(args.mutation_output, args.output / "mutation-results.json")
    shutil.copy2(args.test_output, args.output / "regression-tests.txt")
    shutil.copy2(args.validator_output, args.output / "oracle-validator.txt")
    diff = subprocess.check_output(["git", "-C", str(args.repo_root), "diff", "d79db50568cccaffe67ed1de5a6ee63bf5027284", "HEAD"], text=True)
    (args.output / "exact-diff-remediation6-to-remediation7.patch").write_text(diff, encoding="utf-8")
    manifest = {
        "operation": "OFFLINE_REVIEW_PACKAGE_NO_SCIENTIFIC_REEXECUTION",
        "scientific_commit": "d79db50568cccaffe67ed1de5a6ee63bf5027284",
        "scientific_run": "35433799081",
        "raw_input_sha256": {str(p.relative_to(args.evidence)): sha(p) for p in sorted(args.evidence.rglob("*")) if p.is_file()},
        "predicate_sha256": sha(args.repo_root / "governance-runtime" / "v24_v6_rq1_crash_predicates.py"),
        "governance": ["NOT_QUALIFIED", "CLOSED_PENDING_SUCCESSOR_REVIEW", "NONE_EVIDENCE_ONLY"],
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    excluded = {"package-file-hashes.sha256", "package.tar", "package.tar.sha256"}
    (args.output / "package-file-hashes.sha256").write_text("\n".join(f"{sha(p)}  {p.relative_to(args.output).as_posix()}" for p in sorted(args.output.rglob("*")) if p.is_file() and p.name not in excluded) + "\n", encoding="utf-8")
    tar = args.output.with_suffix(".tar")
    subprocess.run(["tar", "-cf", str(tar), "-C", str(args.output.parent), args.output.name], check=True)
    # The archive is adjacent to the package directory, so its manifest uses
    # an explicit parent-relative path and cannot accidentally hash itself.
    (args.output / "package.tar.sha256").write_text(f"{sha(tar)}  ../{tar.name}\n", encoding="utf-8")
    print(json.dumps({"package": str(args.output), "package_tar": str(tar), "files": len(list(args.output.rglob("*"))), "package_sha256": sha(tar)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
