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
import re
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
    ("source-freeze", [sys.executable, "governance-runtime/freeze_source.py"], "EXP-M-R2E-SOURCE-FREEZE-STDOUT.txt"),
    ("prior-evidence", [sys.executable, "governance-runtime/verify_exp_m_prior_evidence.py"], "EXP-M-R2E-PRIOR-EVIDENCE-VERIFY-STDOUT.txt"),
    ("tests", [sys.executable, "governance-runtime/run_exp_m_tests.py"], "EXP-M-R2E-TEST-RUN-STDOUT.txt"),
    ("reviewer-core", [sys.executable, "governance-runtime/reviewer_exp_m_r2e_suite.py"], "EXP-M-R2E-REVIEWER-CORE-STDOUT.txt"),
    ("reviewer-authority", [sys.executable, "governance-runtime/reviewer_exp_m_r2e_authority_suite.py"], "EXP-M-R2E-REVIEWER-AUTHORITY-STDOUT.txt"),
    ("reviewer-compound", [sys.executable, "governance-runtime/run_reviewer_compound_attacks.py"], "EXP-M-R2E-COMPOUND-STDOUT.txt"),
    ("static-review-probes", [sys.executable, "governance-runtime/run_exp_m_static_review_probes.py"], "EXP-M-R2E-STATIC-REVIEW-PROBES-STDOUT.txt"),
    ("phases", [sys.executable, "governance-runtime/run_exp_m_deterministic.py"], "EXP-M-R2E-PHASE-STDOUT.txt"),
    ("mutations", [sys.executable, "governance-runtime/run_exp_m_mutations.py"], "EXP-M-R2E-MUTATION-STDOUT.txt"),
    ("self-falsification", [sys.executable, "governance-runtime/self_falsify_exp_m.py"], "EXP-M-R2E-SELF-FALSIFICATION-STDOUT.txt"),
    ("self-adjudication", [sys.executable, "governance-runtime/self_adjudicate_r2d.py"], "EXP-M-R2E-SELF-ADJUDICATION-STDOUT.txt"),
)

RESULT_JSONS = (
    "EXP-M-TEST-RESULTS.json",
    "EXP-M-DETERMINISTIC-RESULTS.json",
    "EXP-M-MUTATION-RESULTS.json",
    "EXP-M-SELF-FALSIFICATION-RESULTS.json",
    "EXP-M-R2E-COMPOUND-RESULTS.json",
    "EXP-M-R2E-CLARIFICATION-PROBES.json",
    "EXP-M-R2D-SELF-ADJUDICATION.json",
)

RESULT_BY_COMMAND = {
    "source-freeze": "EXP-M-SOURCE-FREEZE.json",
    "tests": "EXP-M-TEST-RESULTS.json",
    "reviewer-compound": "EXP-M-R2E-COMPOUND-RESULTS.json",
    "static-review-probes": "EXP-M-R2E-CLARIFICATION-PROBES.json",
    "phases": "EXP-M-DETERMINISTIC-RESULTS.json",
    "mutations": "EXP-M-MUTATION-RESULTS.json",
    "self-falsification": "EXP-M-SELF-FALSIFICATION-RESULTS.json",
    "self-adjudication": "EXP-M-R2D-SELF-ADJUDICATION.json",
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
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _execute_evidence_command(
    name: str,
    command: list[str],
    stdout_name: str,
    source_commit: str,
    source_tree: str,
) -> dict:
    completed = _run(list(command))
    stdout_path = EXP / stdout_name
    portable_command = "python " + " ".join(command[1:]) if command and command[0] == sys.executable else " ".join(command)
    raw_stdout = completed.stdout or ""
    raw_stderr = completed.stderr or ""
    raw_stdout_bytes = raw_stdout.encode("utf-8")
    raw_stderr_bytes = raw_stderr.encode("utf-8")

    command_source_path = None
    command_source_sha256 = None
    if len(command) >= 2:
        candidate = ROOT / command[1]
        if candidate.is_file():
            command_source_path = str(candidate.relative_to(ROOT)).replace("\\", "/")
            command_source_sha256 = _sha256(candidate)

    result_name = RESULT_BY_COMMAND.get(name)
    result_path = EXP / result_name if result_name else None
    result_sha256 = None
    result_size = None
    identical_payload = None
    if result_path is not None:
        if not result_path.exists():
            raise SystemExit(f"evidence_command_result_missing:{name}:{result_name}")
        result_raw = result_path.read_bytes()
        result_sha256 = hashlib.sha256(result_raw).hexdigest()
        result_size = len(result_raw)
        identical_payload = raw_stdout_bytes == result_raw
        if not identical_payload:
            raise SystemExit(f"evidence_command_result_not_stdout_identical:{name}")

    capture = {
        "schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "command_name": name,
        "command": " ".join(command),
        "portable_command": portable_command,
        "command_source_path": command_source_path,
        "command_source_sha256": command_source_sha256,
        "exit_code": completed.returncode,
        "raw_stdout_sha256": hashlib.sha256(raw_stdout_bytes).hexdigest(),
        "raw_stdout_size": len(raw_stdout_bytes),
        "raw_stdout": raw_stdout,
        "raw_stderr_sha256": hashlib.sha256(raw_stderr_bytes).hexdigest(),
        "raw_stderr_size": len(raw_stderr_bytes),
        "raw_stderr": raw_stderr,
        "result_path": str(result_path.relative_to(ROOT)).replace("\\", "/") if result_path else None,
        "result_sha256_at_command_exit": result_sha256,
        "result_size_at_command_exit": result_size,
        "stdout_payload_identical_to_result": identical_payload,
    }
    stdout_path.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    record = {
        "name": name,
        "command": " ".join(command),
        "portable_command": portable_command,
        "command_source_path": command_source_path,
        "command_source_sha256": command_source_sha256,
        "exit_code": completed.returncode,
        "stdout_path": str(stdout_path.relative_to(ROOT)).replace("\\", "/"),
        "stdout_sha256": _sha256(stdout_path),
        "stdout_capture_schema": "EXP-M-R2E-COMMAND-CAPTURE/v2",
        "stdout_payload_sha256": capture["raw_stdout_sha256"],
        "stdout_payload_size": capture["raw_stdout_size"],
        "stderr_payload_sha256": capture["raw_stderr_sha256"],
        "stderr_payload_size": capture["raw_stderr_size"],
        "stdout_role": "source-bound exact result serialization" if result_path else "source-bound command-console capture",
    }
    if result_path is not None:
        record["result_path"] = str(result_path.relative_to(ROOT)).replace("\\", "/")
        record["result_sha256_at_command_exit"] = result_sha256
        record["result_size_at_command_exit"] = result_size
        record["stdout_payload_identical_to_result"] = True
    if completed.returncode != 0:
        raise SystemExit(
            f"evidence_command_failed:{name}\nSTDOUT:\n{raw_stdout}\nSTDERR:\n{raw_stderr}"
        )
    return record

def _audit_python_imports(source_files: dict[str, str]) -> dict:
    local_module_paths = {
        path.stem: str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "governance-runtime").glob("*.py")
    }
    local_modules = set(local_module_paths)
    imports: set[str] = set()
    dynamic_import_sites: list[str] = []
    dynamic_code_sites: list[str] = []
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
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    imports.add(node.args[0].value.split(".", 1)[0])
                else:
                    dynamic_import_sites.append(f"{rel}:{getattr(node, 'lineno', 0)}")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                dynamic_code_sites.append(f"{rel}:{getattr(node, 'lineno', 0)}")
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "importlib"
                and node.func.attr == "import_module"
            ):
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    imports.add(node.args[0].value.split(".", 1)[0])
                else:
                    dynamic_import_sites.append(f"{rel}:{getattr(node, 'lineno', 0)}")
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    third_party = sorted(name for name in imports if name not in stdlib and name not in local_modules)
    local_imports = sorted(name for name in imports if name in local_modules)
    unfrozen_local_imports = sorted(
        local_module_paths[name]
        for name in local_imports
        if local_module_paths[name] not in source_files
    )
    network_capable_roots = {
        "socket", "http", "urllib", "ftplib", "smtplib", "telnetlib",
        "requests", "aiohttp", "httpx", "websockets",
    }
    observed_network_imports = sorted(imports & network_capable_roots)
    return {
        "import_roots": sorted(imports),
        "local_modules": local_imports,
        "local_module_paths": {name: local_module_paths[name] for name in local_imports},
        "unfrozen_local_imports": unfrozen_local_imports,
        "dynamic_import_sites": sorted(dynamic_import_sites),
        "dynamic_code_sites": sorted(dynamic_code_sites),
        "third_party_imports": third_party,
        "third_party_dependency_count": len(third_party),
        "network_capable_imports": observed_network_imports,
    }


def _reproducibility_environment(source_files: dict[str, str]) -> dict:
    audit = _audit_python_imports(source_files)
    if audit["third_party_imports"]:
        raise SystemExit("unexpected_third_party_dependency:" + ",".join(audit["third_party_imports"]))
    if audit["unfrozen_local_imports"]:
        raise SystemExit("unfrozen_local_import:" + ",".join(audit["unfrozen_local_imports"]))
    if audit["dynamic_import_sites"]:
        raise SystemExit("dynamic_import_not_statically_bound:" + ",".join(audit["dynamic_import_sites"]))
    if audit["dynamic_code_sites"]:
        raise SystemExit("dynamic_code_execution_not_allowed:" + ",".join(audit["dynamic_code_sites"]))
    if audit["network_capable_imports"]:
        raise SystemExit("network_capable_import_in_governed_surface:" + ",".join(audit["network_capable_imports"]))
    action_pins: dict[str, list[str]] = {}
    for rel in sorted(path for path in source_files if path.startswith(".github/workflows/") and path.endswith(".yml")):
        uses = []
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("uses:"):
                uses.append(stripped.split(":", 1)[1].strip())
        action_pins[rel] = uses
    unpinned = [
        f"{workflow}:{use}"
        for workflow, uses in action_pins.items()
        for use in uses
        if "@" in use and not re.fullmatch(r"[^@]+@[0-9a-f]{40}", use)
    ]
    if unpinned:
        raise SystemExit("unpinned_github_action:" + ",".join(unpinned))
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
        "github_actions_dependencies": action_pins,
        "github_actions_all_pinned_by_commit_sha": True,
        "dependency_basis": "governed Python source import audit found only Python standard-library and repository-local modules",
        "network_required_for_test_commands": False,
        "network_capable_imports": audit["network_capable_imports"],
        "unfrozen_local_imports": audit["unfrozen_local_imports"],
        "dynamic_import_sites": audit["dynamic_import_sites"],
        "dynamic_code_sites": audit["dynamic_code_sites"],
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


def _allowed_generated(path: str) -> bool:
    return path in EXPECTED_GENERATED_PATHS


def generate() -> dict:
    source_commit, source_tree = _assert_clean_source_head()

    command_records = []
    for name, command, stdout_name in COMMANDS:
        command_records.append(
            _execute_evidence_command(name, list(command), stdout_name, source_commit, source_tree)
        )
        if name == "source-freeze":
            freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
            if freeze.get("source_commit") != source_commit or freeze.get("source_tree") != source_tree:
                raise SystemExit("source_freeze_identity_mismatch")

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))

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
    if any(not row.get("blocking_guard") for row in self_data.get("cases") or [] if str(row.get("id")) in compound_ids):
        raise SystemExit("compound_blocking_guard_missing")
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
        "schema": "EXP-M-R2E-EVIDENCE-MANIFEST/v4",
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
