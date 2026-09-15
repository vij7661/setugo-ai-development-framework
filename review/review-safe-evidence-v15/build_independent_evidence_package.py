#!/usr/bin/env python3
"""Build the frozen V15 manual independent implementation-evidence package.

Review/evidence-side tooling only. This script never changes the frozen candidate
and has no authority effect.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

REPO = "vij7661/setugo-ai-development-framework"
CANDIDATE = "380e1d9db083a6477691bf187d5cba7c61eee280"
TREE = "6bdd7bf8ec214e406383e084bd7c28b8c9738ee9"
BASE = "87f6e3df73c0c70c5d8ff4da38365ff92721aff7"
RUNS = {
    "34945260098": "success",
    "34945569703": "success",
    "34945856539": "success",
    "34946188255": "success",
    "34946457176": "success",
    "34946677355": "failure",
    "34946873858": "success",
    "34947546487": "success",
    "34948097857": "success",
    "34948589255": "success",
}
RAW_LOG_RUNS = ("34946677355", "34948589255")
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def run(*args: str, text: bool = False) -> bytes | str:
    cp = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if cp.returncode != 0:
        raise RuntimeError(f"command failed rc={cp.returncode}: {args!r}\n{cp.stderr.decode('utf-8','replace')[-2000:]}")
    return cp.stdout.decode("utf-8") if text else cp.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def gh_json(endpoint: str) -> dict:
    raw = run("gh", "api", endpoint)
    assert isinstance(raw, bytes)
    return json.loads(raw.decode("utf-8"))


def gh_log(endpoint: str) -> bytes:
    raw = run("gh", "api", "--allow-escape-sequences", endpoint)
    assert isinstance(raw, bytes)
    return raw


def copy_current(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def deterministic_zip(stage: Path, dst: Path) -> None:
    key = lambda p: p.relative_to(stage).as_posix()
    files = sorted((p for p in stage.rglob("*") if p.is_file()), key=key)
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_STORED) as z:
        for p in files:
            info = zipfile.ZipInfo(key(p), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            z.writestr(info, p.read_bytes())


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (root / "dist-v15-evidence")
    work = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "v15-independent-evidence-stage-v2"
    if work.exists():
        shutil.rmtree(work)
    if out.exists():
        shutil.rmtree(out)
    work.mkdir(parents=True)
    out.mkdir(parents=True)
    for name in ("candidate", "evidence", "review"):
        (work / name).mkdir()

    run("git", "fetch", "--no-tags", "origin", CANDIDATE, BASE)
    actual_tree = str(run("git", "rev-parse", f"{CANDIDATE}^{{tree}}", text=True)).strip()
    if actual_tree != TREE:
        raise SystemExit(f"candidate tree mismatch: {actual_tree}")
    changed_raw = str(run("git", "diff", "--name-only", BASE, CANDIDATE, text=True))
    changed = sorted(x for x in changed_raw.splitlines() if x.strip())
    if len(changed) != 30 or len(set(changed)) != 30:
        raise SystemExit(f"expected exactly 30 changed files, got {len(changed)}")

    instructions = root / "review/review-safe-evidence-v15/V15-INDEPENDENT-EVIDENCE-REVIEW-INSTRUCTIONS.md"
    freeze = root / "review/review-safe-evidence-v15/V15-IMPLEMENTATION-FREEZE.json"
    red1 = root / "review/review-safe-evidence-v15/V15-EVIDENCE-PACKAGE-RED-001.md"
    builder = Path(__file__).resolve()
    workflow = root / ".github/workflows/review-safe-evidence-v15-independent-evidence-package-v2.yml"
    copy_current(instructions, work / "00-REVIEW-INSTRUCTIONS.md")
    copy_current(freeze, work / "review/V15-IMPLEMENTATION-FREEZE.json")
    copy_current(red1, work / "review/V15-EVIDENCE-PACKAGE-RED-001.md")
    copy_current(builder, work / "review/PACKAGE-BUILDER-SOURCE.py")
    copy_current(workflow, work / "review/PACKAGE-BUILDER-WORKFLOW.yml")

    candidate_rows = []
    for path in changed:
        data = run("git", "show", f"{CANDIDATE}:{path}")
        assert isinstance(data, bytes)
        target = work / "candidate" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        candidate_rows.append({
            "path": path,
            "bytes": len(data),
            "sha256": sha256(data),
            "git_blob_sha1": git_blob_sha(data),
        })

    projection = f"""# V15 Implementation Evidence — Neutral Reviewer Projection

This projection is navigation evidence only and is not a PASS claim.

- frozen candidate commit: `{CANDIDATE}`
- frozen candidate tree: `{TREE}`
- baseline commit: `{BASE}`
- changed candidate files staged: `30`
- claimed implementation surfaces: `33/33 construction-only`
- final accumulated construction run: `34948589255`
- final accumulated construction tests: `199/199 PASS`
- preserved candidate-construction RED: `34946677355` followed by corrected run `34946873858`
- preserved package-builder RED: `34948998139`
- implementation qualification: `NOT_CLAIMED`
- runtime qualification: `NOT_CLAIMED`
- scientific execution: `CLOSED_PENDING_INDEPENDENT_EVIDENCE_REVIEW`
- authority effect: `NONE_EVIDENCE_ONLY`

The reviewer must independently inspect and falsify the raw candidate and evidence.
"""
    (work / "01-REVIEWER-SAFE-PROJECTION.md").write_text(projection, encoding="utf-8")

    evidence_run_rows = []
    for run_id, expected in RUNS.items():
        run_obj = gh_json(f"/repos/{REPO}/actions/runs/{run_id}")
        jobs_obj = gh_json(f"/repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100")
        if run_obj.get("conclusion") != expected:
            raise SystemExit(f"run conclusion mismatch {run_id}: {run_obj.get('conclusion')} != {expected}")
        (work / "evidence" / f"run-{run_id}.json").write_text(json.dumps(run_obj, indent=2, sort_keys=True) + "\n")
        (work / "evidence" / f"run-{run_id}-jobs.json").write_text(json.dumps(jobs_obj, indent=2, sort_keys=True) + "\n")
        jobs = jobs_obj.get("jobs", [])
        if not jobs:
            raise SystemExit(f"run {run_id} has no jobs")
        evidence_run_rows.append({"run_id": run_id, "conclusion": expected, "head_sha": run_obj.get("head_sha"), "job_ids": [str(j.get("id")) for j in jobs]})
        if run_id in RAW_LOG_RUNS:
            job_id = str(jobs[0]["id"])
            log = gh_log(f"/repos/{REPO}/actions/jobs/{job_id}/logs")
            (work / "evidence" / f"run-{run_id}-job-{job_id}.log").write_bytes(log)

    red_logs = list((work / "evidence").glob("run-34946677355-job-*.log"))
    final_logs = list((work / "evidence").glob("run-34948589255-job-*.log"))
    if len(red_logs) != 1 or b"FAILED (failures=1)" not in red_logs[0].read_bytes():
        raise SystemExit("historical RED raw log binding failed")
    if len(final_logs) != 1:
        raise SystemExit("final raw log missing")
    final_log = final_logs[0].read_bytes()
    for marker in (b"Ran 199 tests", b"V15_MANDATORY_IMPLEMENTATION_SURFACES=33/33_IMPLEMENTED", b"AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY"):
        if marker not in final_log:
            raise SystemExit(f"final log marker missing: {marker!r}")

    payload = []
    key = lambda p: p.relative_to(work).as_posix()
    for p in sorted((x for x in work.rglob("*") if x.is_file()), key=key):
        data = p.read_bytes()
        payload.append({"path": key(p), "bytes": len(data), "sha256": sha256(data)})
    manifest = {
        "schema_version": 1,
        "candidate_commit": CANDIDATE,
        "candidate_tree": TREE,
        "baseline_commit": BASE,
        "candidate_file_count": len(candidate_rows),
        "candidate_files": candidate_rows,
        "payload_file_count": len(payload),
        "payload_files": payload,
        "construction_runs": evidence_run_rows,
        "final_construction_run": "34948589255",
        "final_construction_tests": "199/199_PASS",
        "candidate_construction_red_preserved": "34946677355",
        "package_builder_red_preserved": "34948998139",
        "independent_manual_review_required": True,
        "automated_external_reviewer_api_calls": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "scientific_execution": "CLOSED_PENDING_INDEPENDENT_EVIDENCE_REVIEW",
        "authority_effect": AUTHORITY_EFFECT,
    }
    manifest_path = work / "PACKAGE-MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    a = out / "V15-INDEPENDENT-IMPLEMENTATION-EVIDENCE-REVIEW.zip"
    b = out / "repeat.zip"
    deterministic_zip(work, a)
    deterministic_zip(work, b)
    if a.read_bytes() != b.read_bytes():
        raise SystemExit("deterministic double build mismatch")
    b.unlink()
    with zipfile.ZipFile(a) as z:
        names = z.namelist()
        if names != sorted(names) or len(names) != len(set(names)):
            raise SystemExit("zip ordering/uniqueness failure")
        for p in sorted((x for x in work.rglob("*") if x.is_file()), key=key):
            if z.read(key(p)) != p.read_bytes():
                raise SystemExit(f"zip byte mismatch: {key(p)}")

    zip_sha = sha256(a.read_bytes())
    (out / "V15-INDEPENDENT-IMPLEMENTATION-EVIDENCE-REVIEW.sha256").write_text(f"{zip_sha}  {a.name}\n")
    build = {
        "schema_version": 1,
        "candidate_commit": CANDIDATE,
        "candidate_tree": TREE,
        "zip_sha256": zip_sha,
        "zip_bytes": a.stat().st_size,
        "zip_entry_count": len(zipfile.ZipFile(a).namelist()),
        "manifest_sha256": sha256(manifest_path.read_bytes()),
        "candidate_file_count": 30,
        "deterministic_double_build": "PASS",
        "content_reverification": "PASS",
        "raw_final_log_binding": "PASS",
        "raw_red_log_binding": "PASS",
        "historical_reds_preserved": True,
        "independent_manual_review_required": True,
        "automated_external_reviewer_api_calls": False,
        "authority_effect": AUTHORITY_EFFECT,
    }
    (out / "V15-INDEPENDENT-IMPLEMENTATION-EVIDENCE-REVIEW.BUILD-RECORD.json").write_text(json.dumps(build, indent=2, sort_keys=True) + "\n")
    print(json.dumps(build, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
