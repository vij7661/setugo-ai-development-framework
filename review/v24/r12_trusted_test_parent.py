from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

PREFIX = "R12_WORKER_RESULT="
PARENT_PREFIX = "R12_PARENT_RESULT="


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(obj: object) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def actual_interpreter_contract() -> dict[str, object]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    for key, value in flags.items():
        if value is not True:
            raise SystemExit(f"R12_PARENT_ACTUAL_INTERPRETER_FLAG_NOT_TRUE:{key}")
    executable = pathlib.Path(sys.executable).resolve()
    if not executable.is_file():
        raise SystemExit("R12_PARENT_INTERPRETER_EXECUTABLE_MISSING")
    stdlib_names = sorted(sys.stdlib_module_names)
    contract = {
        "flags": flags,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro, sys.version_info.releaselevel, sys.version_info.serial],
        "hexversion": sys.hexversion,
        "executable_sha256": raw_sha256(executable.read_bytes()),
        "stdlib_module_names_digest": canonical_digest(stdlib_names),
        "trusted_parent_outside_candidate_tree": True,
        "candidate_path_absent_at_interpreter_startup": True,
    }
    contract["contract_digest"] = canonical_digest(contract)
    return contract


def load_pinset(path: pathlib.Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != 2:
        raise SystemExit("R12_PARENT_PINSET_SCHEMA_INVALID")
    if obj.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH":
        raise SystemExit("R12_PARENT_PINSET_AUTHORITY_INVALID")
    if obj.get("candidate_self_grant") is not False:
        raise SystemExit("R12_PARENT_PINSET_SELF_GRANT_FORBIDDEN")
    actual = actual_interpreter_contract()
    if obj.get("interpreter_contract") != actual:
        raise SystemExit("R12_PARENT_INTERPRETER_CONTRACT_MISMATCH")
    return obj


def candidate_modules_loaded(sandbox: pathlib.Path) -> list[str]:
    hits: list[str] = []
    for name, module in sys.modules.items():
        file = getattr(module, "__file__", None)
        if not isinstance(file, str):
            continue
        try:
            pathlib.Path(file).resolve().relative_to(sandbox)
        except (ValueError, OSError):
            continue
        hits.append(name)
    return sorted(hits)


def parse_worker_stdout(stdout: str, module: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].startswith(PREFIX):
        raise SystemExit(f"R12_PARENT_WORKER_STDOUT_PROTOCOL_INVALID:{module}:{lines!r}")
    try:
        obj = json.loads(lines[0][len(PREFIX):])
    except Exception as exc:
        raise SystemExit(f"R12_PARENT_WORKER_JSON_INVALID:{module}:{exc}") from exc
    if obj.get("schema_version") != 1 or obj.get("module") != module:
        raise SystemExit(f"R12_PARENT_WORKER_IDENTITY_INVALID:{module}")
    if obj.get("authority_effect") != "NONE_EVIDENCE_ONLY":
        raise SystemExit(f"R12_PARENT_WORKER_AUTHORITY_EFFECT_INVALID:{module}")
    flags = obj.get("actual_interpreter_flags")
    if not isinstance(flags, dict) or any(flags.get(k) is not True for k in ("isolated", "no_site", "ignore_environment", "safe_path")):
        raise SystemExit(f"R12_PARENT_WORKER_INTERPRETER_FLAGS_INVALID:{module}")
    canaries = obj.get("negative_canaries")
    if not isinstance(canaries, dict) or any(canaries.get(k) != "PASS" for k in ("before_candidate_import", "after_candidate_import", "after_test_execution")):
        raise SystemExit(f"R12_PARENT_WORKER_CANARY_INVALID:{module}")
    if obj.get("framework_integrity") is not True:
        raise SystemExit(f"R12_PARENT_WORKER_FRAMEWORK_INTEGRITY_INVALID:{module}")
    expected = obj.get("expected_tests")
    tests_run = obj.get("tests_run")
    if not isinstance(expected, int) or expected <= 0 or tests_run != expected:
        raise SystemExit(f"R12_PARENT_WORKER_TEST_COUNT_INVALID:{module}:expected={expected}:run={tests_run}")
    for key in ("failures", "errors", "unexpected_successes"):
        if obj.get(key) != 0:
            raise SystemExit(f"R12_PARENT_WORKER_NONPASS:{module}:{key}={obj.get(key)}")
    if obj.get("successful") is not True:
        raise SystemExit(f"R12_PARENT_WORKER_SUCCESS_FALSE:{module}")
    return obj


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--pinset", required=True)
    parser.add_argument("--worker", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    runtime = actual_interpreter_contract()
    sandbox = pathlib.Path(args.sandbox).resolve()
    subject = sandbox / "governance-runtime"
    pinset_path = pathlib.Path(args.pinset).resolve()
    worker = pathlib.Path(args.worker).resolve()
    if worker.is_relative_to(sandbox):
        raise SystemExit("R12_PARENT_WORKER_INSIDE_CANDIDATE_SANDBOX")
    if not worker.is_file():
        raise SystemExit("R12_PARENT_WORKER_MISSING")

    startup_path = list(sys.path)
    if "" in startup_path or str(subject) in startup_path or str(sandbox) in startup_path:
        raise SystemExit(f"R12_PARENT_CANDIDATE_PATH_PRESENT_AT_STARTUP:{startup_path!r}")
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R12_PARENT_CANDIDATE_MODULE_LOADED_BEFORE_EXECUTION")

    pinset = load_pinset(pinset_path)
    tests = pinset.get("executed_tests")
    if not isinstance(tests, list) or not tests:
        raise SystemExit("R12_PARENT_EXECUTED_TESTS_REQUIRED")
    modules: list[str] = []
    seen: set[str] = set()
    for raw in tests:
        if not isinstance(raw, str) or not raw.startswith("governance-runtime/test_") or not raw.endswith(".py"):
            raise SystemExit(f"R12_PARENT_INVALID_TEST_PATH:{raw}")
        p = pathlib.PurePosixPath(raw)
        if len(p.parts) != 2:
            raise SystemExit(f"R12_PARENT_NESTED_TEST_PATH_FORBIDDEN:{raw}")
        module = p.stem
        if module in seen:
            raise SystemExit(f"R12_PARENT_DUPLICATE_TEST_MODULE:{module}")
        seen.add(module)
        modules.append(module)

    python_bin = pathlib.Path(sys.executable).resolve()
    env = {
        "HOME": os.environ.get("HOME", "/tmp"),
        "PATH": f"{python_bin.parent}:/usr/bin:/bin",
    }
    envelopes: list[dict[str, Any]] = []
    for module in modules:
        command = [
            str(python_bin),
            "-I",
            "-S",
            str(worker),
            "--sandbox",
            str(sandbox),
            "--pinset",
            str(pinset_path),
            "--module",
            module,
        ]
        completed = subprocess.run(
            command,
            cwd=str(worker.parent),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
        # A direct os._exit(0), crash, or forged normal process termination cannot
        # count unless the exact trusted envelope protocol is also satisfied.
        if completed.returncode != 0:
            raise SystemExit(
                f"R12_PARENT_WORKER_FAILED:{module}:rc={completed.returncode}:stderr={completed.stderr[-1000:]!r}"
            )
        if completed.stderr.strip():
            raise SystemExit(f"R12_PARENT_WORKER_STDERR_NOT_EMPTY:{module}:{completed.stderr[-1000:]!r}")
        envelopes.append(parse_worker_stdout(completed.stdout, module))
        if candidate_modules_loaded(sandbox):
            raise SystemExit("R12_PARENT_CANDIDATE_MODULE_LEAKED_INTO_PARENT")

    total = sum(int(x["tests_run"]) for x in envelopes)
    transcript = {
        "schema_version": 1,
        "module_results": envelopes,
        "module_count": len(envelopes),
        "test_count": total,
    }
    transcript_digest = canonical_digest(transcript)
    output = {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": pinset.get("candidate_commit"),
        "candidate_tree": pinset.get("candidate_tree"),
        "environment_digest": canonical_digest({
            "interpreter_contract_digest": runtime["contract_digest"],
            "pinset_sha256": raw_sha256(pinset_path.read_bytes()),
            "worker_sha256": raw_sha256(worker.read_bytes()),
        }),
        "interpreter_contract_digest": runtime["contract_digest"],
        "execution_transcript_digest": transcript_digest,
        "actual_interpreter_flags": runtime["flags"],
        "trusted_parent_imported_candidate": False,
        "candidate_shared_trusted_result_state": False,
        "result_accounting_origin": "TRUSTED_PARENT",
        "module_count": len(envelopes),
        "test_count": total,
        "worker_sha256": raw_sha256(worker.read_bytes()),
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    print(PARENT_PREFIX + json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
