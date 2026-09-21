"""Generate fresh EXP-M R2E evidence against exactly frozen source S.

The script is intended to run at clean source commit S. It first emits the
source-freeze evidence, then runs only offline/deterministic commands. With
--commit it commits only generated EXP-M JSON/TXT evidence artifacts, producing
E. It never performs provider/API execution.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "governed-platform"
FREEZE = EXP / "EXP-M-SOURCE-FREEZE.json"
MANIFEST = EXP / "EXP-M-R2E-EVIDENCE-MANIFEST.json"

COMMANDS = (
    ("prior-evidence", [sys.executable, "governance-runtime/verify_exp_m_prior_evidence.py"], "EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt"),
    ("tests", [sys.executable, "governance-runtime/run_exp_m_tests.py"], "EXP-M-R2E-TEST-RUN-STDOUT.txt"),
    ("reviewer-core", [sys.executable, "governance-runtime/reviewer_exp_m_r2e_suite.py"], "EXP-M-R2E-REVIEWER-CORE-STDOUT.txt"),
    ("reviewer-authority", [sys.executable, "governance-runtime/reviewer_exp_m_r2e_authority_suite.py"], "EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt"),
    ("reviewer-compound", [sys.executable, "governance-runtime/run_reviewer_compound_attacks.py"], "EXP-M-R2E-COMPOUND-STDOUT.txt"),
    ("static-review-probes", [sys.executable, "governance-runtime/run_exp_m_static_review_probes.py"], "EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt"),
    ("phases", [sys.executable, "governance-runtime/run_exp_m_deterministic.py"], "EXP-M-R2E-PHASE-STDOUT.txt"),
    ("mutations", [sys.executable, "governance-runtime/run_exp_m_mutations.py"], "EXP-M-R2E-MUTATION-STDOUT.txt"),
    ("self-falsification", [sys.executable, "governance-runtime/self_falsify_exp_m.py"], "EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt"),
)

RESULT_JSONS = (
    "EXP-M-TEST-RESULTS.json",
    "EXP-M-DETERMINISTIC-RESULTS.json",
    "EXP-M-MUTATION-RESULTS.json",
    "EXP-M-SELF-FALSIFICATION-RESULTS.json",
    "EXP-M-R2E-COMPOUND-RESULTS.json",
    "EXP-M-R2E-CLARIFICATION-PROBES.json",
)

RESULT_BY_COMMAND = {
    "tests": "EXP-M-TEST-RESULTS.json",
    "reviewer-compound": "EXP-M-R2E-COMPOUND-RESULTS.json",
    "static-review-probes": "EXP-M-R2E-CLARIFICATION-PROBES.json",
    "phases": "EXP-M-DETERMINISTIC-RESULTS.json",
    "mutations": "EXP-M-MUTATION-RESULTS.json",
    "self-falsification": "EXP-M-SELF-FALSIFICATION-RESULTS.json",
}

EXPECTED_GENERATED_PATHS = frozenset(
    [str(FREEZE.relative_to(ROOT)).replace("\\", "/"),
     str(MANIFEST.relative_to(ROOT)).replace("\\", "/")]
    + [f"experiments/governed-platform/{name}" for name in RESULT_JSONS]
    + [f"experiments/governed-platform/{stdout_name}" for _, _, stdout_name in COMMANDS]
)


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _audit_python_imports(source_files: dict[str, str]) -> dict:
    local_modules = {
        path.stem
        for path in (ROOT / "governance-runtime").glob("*.py")
    }
    imports: set[str] = set()
    for rel in source_files:
        if not rel.endswith(".py"):
            continue
        source_path = ROOT / rel
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    third_party = sorted(name for name in imports if name not in stdlib and name not in local_modules)
    return {
        "import_roots": sorted(imports),
        "local_modules": sorted(name for name in imports if name in local_modules),
        "third_party_imports": third_party,
        "third_party_dependency_count": len(third_party),
    }


def _reproducibility_environment(source_files: dict[str, str]) -> dict:
    audit = _audit_python_imports(source_files)
    if audit["third_party_imports"]:
        raise SystemExit("unexpected_third_party_dependency:" + ",".join(audit["third_party_imports"]))
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_version": subprocess.check_output(("git", "--version"), cwd=ROOT, text=True).strip(),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "github_actions_image_os": os.environ.get("ImageOS"),
        "github_actions_image_version": os.environ.get("ImageVersion"),
        "third_party_python_dependencies": [],
        "dependency_basis": "governed Python source import audit found only Python standard-library and repository-local modules",
        "network_required_for_test_commands": False,
        "checkout_sequence": [
            "git fetch --all --tags --prune",
            "git checkout --detach <S>",
            "git rev-parse HEAD",
            "git rev-parse HEAD^{tree}",
            "verify clean worktree before evidence generation",
        ],
    }


def _status_lines() -> list[str]:
    raw = subprocess.check_output(
        ("git", "status", "--porcelain", "--untracked-files=all"),
        cwd=ROOT, text=True,
    )
    return [line for line in raw.splitlines() if line]


def _path_from_status(line: str) -> str:
    rel = line[3:].strip().replace("\\", "/")
    if " -> " in rel:
        rel = rel.split(" -> ", 1)[1]
    return rel


def _is_transient(path: str) -> bool:
    return "/__pycache__/" in f"/{path}" or path.endswith(".pyc")


def _cleanup_transients() -> None:
    for cache in ROOT.rglob("__pycache__"):
        if cache.is_dir():
            shutil.rmtree(cache, ignore_errors=True)


def _assert_clean_source_head() -> tuple[str, str]:
    _cleanup_transients()
    dirty = [line for line in _status_lines() if not _is_transient(_path_from_status(line))]
    if dirty:
        raise SystemExit("generate_evidence_requires_clean_source_worktree:" + ",".join(_path_from_status(x) for x in dirty))
    return _git("rev-parse", "HEAD"), _git("rev-parse", "HEAD^{tree}")


def _assert_result_identity(path: Path, source_commit: str, source_tree: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    execution = data.get("execution") or {}
    if execution.get("source_commit") != source_commit:
        raise SystemExit(f"stale_result_source_commit:{path.name}")
    if execution.get("source_tree") != source_tree:
        raise SystemExit(f"stale_result_source_tree:{path.name}")


def _merge_compound_into_self_falsification() -> None:
    self_path = EXP / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    compound_path = EXP / "EXP-M-R2E-COMPOUND-RESULTS.json"
    self_data = json.loads(self_path.read_text(encoding="utf-8"))
    compound = json.loads(compound_path.read_text(encoding="utf-8"))
    existing = list(self_data.get("cases") or [])
    existing_ids = {str(row.get("id")) for row in existing}
    for row in compound.get("cases") or []:
        case_id = str(row.get("id"))
        if case_id in existing_ids:
            existing = [x for x in existing if str(x.get("id")) != case_id]
        existing.append({
            "id": case_id,
            "rejected": bool(row.get("rejected")),
            "rejection_reason": str(row.get("rejection_reason", "")),
            "source": str(row.get("source", "reviewer_exp_m_r2e_compound_suite.py")),
        })
    survivors = [row for row in existing if not row.get("rejected")]
    self_data["cases"] = existing
    self_data["total"] = len(existing)
    self_data["surviving_critical"] = len(survivors)
    self_data["surviving_high"] = len(survivors)
    self_data["all_rejected"] = not survivors
    self_data["reviewer_compound_attacks"] = {
        "case_ids": [row.get("id") for row in compound.get("cases") or []],
        "survivor_count": compound.get("survivor_count"),
        "all_rejected": compound.get("all_rejected"),
    }
    self_path.write_text(json.dumps(self_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _allowed_generated(path: str) -> bool:
    return path in EXPECTED_GENERATED_PATHS


def generate() -> dict:
    source_commit, source_tree = _assert_clean_source_head()

    freeze_run = _run([sys.executable, "governance-runtime/freeze_source.py"])
    if freeze_run.returncode != 0:
        raise SystemExit("source_freeze_failed:\n" + freeze_run.stdout)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("source_commit") != source_commit or freeze.get("source_tree") != source_tree:
        raise SystemExit("source_freeze_identity_mismatch")

    command_records = []
    for name, command, stdout_name in COMMANDS:
        completed = _run(list(command))
        stdout_path = EXP / stdout_name
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        record = {
            "name": name,
            "command": " ".join(command),
            "portable_command": "python " + " ".join(command[1:]) if command and command[0] == sys.executable else " ".join(command),
            "exit_code": completed.returncode,
            "stdout_path": str(stdout_path.relative_to(ROOT)).replace("\\", "/"),
            "stdout_sha256": _sha256(stdout_path),
            "stdout_role": "command_console_capture",
        }
        result_name = RESULT_BY_COMMAND.get(name)
        if result_name:
            result_path = EXP / result_name
            if result_path.exists():
                identical = _sha256(stdout_path) == _sha256(result_path) and stdout_path.stat().st_size == result_path.stat().st_size
                record["result_path"] = str(result_path.relative_to(ROOT)).replace("\\", "/")
                record["stdout_identical_to_result"] = identical
                if identical:
                    record["stdout_role"] = "duplicate_serialization_of_result_json; retained as command-console capture, not independent evidence"
        command_records.append(record)
        if completed.returncode != 0:
            raise SystemExit(f"evidence_command_failed:{name}\n{completed.stdout}")

    _merge_compound_into_self_falsification()

    for name in RESULT_JSONS:
        path = EXP / name
        if not path.exists():
            raise SystemExit(f"required_result_missing:{name}")
        _assert_result_identity(path, source_commit, source_tree)

    compound = json.loads((EXP / "EXP-M-R2E-COMPOUND-RESULTS.json").read_text(encoding="utf-8"))
    if not compound.get("all_rejected") or compound.get("survivor_count") != 0:
        raise SystemExit("compound_attack_survivor")

    self_data = json.loads((EXP / "EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text(encoding="utf-8"))
    compound_ids = {f"CA-{n}" for n in range(1, 11)}
    observed = {str(row.get("id")) for row in self_data.get("cases") or []}
    if not compound_ids.issubset(observed):
        raise SystemExit("compound_attacks_not_embedded_in_self_falsification")
    if any(not row.get("rejection_reason") for row in self_data.get("cases") or [] if str(row.get("id")) in compound_ids):
        raise SystemExit("compound_rejection_reason_missing")
    if not self_data.get("all_rejected"):
        raise SystemExit("self_falsification_survivor")

    artifacts = []
    artifact_paths = [FREEZE]
    artifact_paths.extend(EXP / name for name in RESULT_JSONS)
    artifact_paths.extend(EXP / stdout_name for _, _, stdout_name in COMMANDS)
    for path in artifact_paths:
        if not path.exists():
            raise SystemExit(f"evidence_artifact_missing:{path.name}")
        artifacts.append({
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": _sha256(path),
            "size": path.stat().st_size,
        })

    reproducibility = _reproducibility_environment(dict(freeze.get("source_files") or {}))
    payload = {
        "schema": "EXP-M-R2E-EVIDENCE-MANIFEST/v2",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "commands": command_records,
        "reproducibility": reproducibility,
        "manifest_self_attestation": {
            "included_in_artifacts": False,
            "reason": "self-hash recursion is intentionally avoided; P independently attests the complete manifest bytes as stored at E",
        },
        "artifacts": artifacts,
        "compound_attack_survivors": 0,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    _cleanup_transients()
    changed = _status_lines()
    bad = []
    for line in changed:
        rel = _path_from_status(line)
        if _is_transient(rel):
            continue
        if not _allowed_generated(rel):
            bad.append(rel)
    if bad:
        raise SystemExit("non_evidence_worktree_change:" + ",".join(sorted(set(bad))))
    observed = {_path_from_status(line) for line in changed if not _is_transient(_path_from_status(line))}
    required_changed = {str(FREEZE.relative_to(ROOT)).replace("\\", "/"), str(MANIFEST.relative_to(ROOT)).replace("\\", "/")}
    if not required_changed.issubset(observed):
        raise SystemExit("required_evidence_not_materialized:" + ",".join(sorted(required_changed - observed)))
    return payload


def commit_evidence() -> str:
    _cleanup_transients()
    paths: list[str] = []
    unexpected: list[str] = []
    for line in _status_lines():
        rel = _path_from_status(line)
        if _is_transient(rel):
            continue
        if _allowed_generated(rel):
            paths.append(rel)
        else:
            unexpected.append(rel)
    if unexpected:
        raise SystemExit("unexpected_non_evidence_before_commit:" + ",".join(sorted(set(unexpected))))
    if not paths:
        raise SystemExit("no_generated_evidence_to_commit")
    unique_paths = tuple(sorted(set(paths)))
    subprocess.check_call(("git", "add", "--") + unique_paths, cwd=ROOT)
    staged = tuple(_git("diff", "--cached", "--name-only").splitlines())
    if set(staged) != set(unique_paths) or any(not _allowed_generated(path) for path in staged):
        raise SystemExit("staged_evidence_set_mismatch")
    subprocess.check_call(("git", "commit", "-m", "evidence(exp-m): R2E generated evidence [R2E-EVIDENCE]"), cwd=ROOT)
    _cleanup_transients()
    leftover = [line for line in _status_lines() if not _is_transient(_path_from_status(line))]
    if leftover:
        raise SystemExit("post_evidence_commit_worktree_not_clean:" + ",".join(_path_from_status(x) for x in leftover))
    return _git("rev-parse", "HEAD")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    payload = generate()
    if args.commit:
        evidence_commit = commit_evidence()
        print(json.dumps({"source_commit": payload["source_commit"], "evidence_commit": evidence_commit}, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
