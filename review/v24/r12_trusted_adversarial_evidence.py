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

CHECK_TARGETS = {
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_mixed_allowed_and_disallowed_terminal_is_rejected"
    ),
    "EVERY_REACHABLE_TERMINAL_ALLOWED": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_every_reachable_terminal_allowed_positive"
    ),
    "GENESIS_CROSS_PAIR_REJECTED": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_genesis_cross_pair_is_rejected"
    ),
    "APPLICABLE_PREDICATE_OMISSION_REJECTED": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_applicable_predicate_omission_is_rejected"
    ),
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_atomic_binding_mode_omission_is_rejected"
    ),
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT": (
        "test_v24_v6_integrated_successor.MandatoryV6AdversarialIntegrationTests."
        "test_later_resolution_preserves_historical_pass_count"
    ),
}


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def actual_interpreter_contract() -> dict[str, object]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    for key, value in flags.items():
        if value is not True:
            raise SystemExit(f"R12_EVIDENCE_ACTUAL_INTERPRETER_FLAG_NOT_TRUE:{key}")
    executable = pathlib.Path(sys.executable).resolve()
    stdlib_names = sorted(sys.stdlib_module_names)
    contract = {
        "flags": flags,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro, sys.version_info.releaselevel, sys.version_info.serial],
        "hexversion": sys.hexversion,
        "executable_sha256": raw_sha256(executable.read_bytes()),
        "stdlib_module_names_digest": digest(stdlib_names),
        "trusted_parent_outside_candidate_tree": True,
        "candidate_path_absent_at_interpreter_startup": True,
    }
    contract["contract_digest"] = digest(contract)
    return contract


def parse_worker(stdout: str, target: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].startswith(PREFIX):
        raise SystemExit(f"R12_EVIDENCE_WORKER_PROTOCOL_INVALID:{target}:{lines!r}")
    obj = json.loads(lines[0][len(PREFIX):])
    if obj.get("target") != target:
        raise SystemExit(f"R12_EVIDENCE_TARGET_MISMATCH:{target}")
    if obj.get("expected_tests") != 1 or obj.get("tests_run") != 1:
        raise SystemExit(f"R12_EVIDENCE_TARGET_TEST_COUNT_INVALID:{target}")
    if obj.get("successful") is not True:
        raise SystemExit(f"R12_EVIDENCE_TARGET_NOT_SUCCESSFUL:{target}")
    if any(obj.get(k) != 0 for k in ("failures", "errors", "unexpected_successes")):
        raise SystemExit(f"R12_EVIDENCE_TARGET_NONPASS:{target}")
    if obj.get("framework_integrity") is not True:
        raise SystemExit(f"R12_EVIDENCE_FRAMEWORK_INTEGRITY_INVALID:{target}")
    canaries = obj.get("negative_canaries")
    if not isinstance(canaries, dict) or any(canaries.get(k) != "PASS" for k in ("before_candidate_import", "after_candidate_import", "after_test_execution")):
        raise SystemExit(f"R12_EVIDENCE_CANARY_INVALID:{target}")
    return obj


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--pinset", required=True)
    parser.add_argument("--worker", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--round-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    runtime = actual_interpreter_contract()
    sandbox = pathlib.Path(args.sandbox).resolve()
    pinset_path = pathlib.Path(args.pinset).resolve()
    worker = pathlib.Path(args.worker).resolve()
    if worker.is_relative_to(sandbox):
        raise SystemExit("R12_EVIDENCE_WORKER_INSIDE_CANDIDATE_SANDBOX")
    pinset = json.loads(pinset_path.read_text(encoding="utf-8"))
    if pinset.get("schema_version") != 2:
        raise SystemExit("R12_EVIDENCE_PINSET_SCHEMA_INVALID")
    if pinset.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH" or pinset.get("candidate_self_grant") is not False:
        raise SystemExit("R12_EVIDENCE_PINSET_AUTHORITY_INVALID")
    if pinset.get("interpreter_contract") != runtime:
        raise SystemExit("R12_EVIDENCE_INTERPRETER_CONTRACT_MISMATCH")

    pinset_sha = raw_sha256(pinset_path.read_bytes())
    worker_sha = raw_sha256(worker.read_bytes())
    environment_digest = digest({
        "pinset_sha256": pinset_sha,
        "worker_sha256": worker_sha,
        "interpreter_contract_digest": runtime["contract_digest"],
    })
    python_bin = pathlib.Path(sys.executable).resolve()
    env = {
        "HOME": os.environ.get("HOME", "/tmp"),
        "PATH": f"{python_bin.parent}:/usr/bin:/bin",
    }

    records: list[dict[str, Any]] = []
    for check_id, target in sorted(CHECK_TARGETS.items()):
        completed = subprocess.run(
            [
                str(python_bin), "-I", "-S", str(worker),
                "--sandbox", str(sandbox),
                "--pinset", str(pinset_path),
                "--target", target,
            ],
            cwd=str(worker.parent),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(
                f"R12_EVIDENCE_WORKER_FAILED:{check_id}:rc={completed.returncode}:stderr={completed.stderr[-1000:]!r}"
            )
        if completed.stderr.strip():
            raise SystemExit(f"R12_EVIDENCE_WORKER_STDERR_NOT_EMPTY:{check_id}:{completed.stderr[-1000:]!r}")
        envelope = parse_worker(completed.stdout, target)
        record = {
            "check_id": check_id,
            "execution_state": "EXECUTED",
            "terminal_result": "PASS",
            "candidate_commit": pinset.get("candidate_commit"),
            "candidate_tree": pinset.get("candidate_tree"),
            "environment_digest": environment_digest,
            "interpreter_contract_digest": runtime["contract_digest"],
            "evidence_digest": digest(envelope),
            "run_id": args.run_id,
            "round_id": args.round_id,
            "producer_control_domain": "R12-CANDIDATE-EXECUTION-DOMAIN",
            "witness_id": "R12-TRUSTED-ADVERSARIAL-EVIDENCE-BUILDER",
            "witness_control_domain": "R12-EXTERNAL-REVIEW-AUTHORITY",
            "witness_authority_origin": "EXTERNAL_REVIEW_BRANCH",
        }
        record["record_digest"] = digest(record)
        records.append(record)

    bundle = {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": pinset.get("candidate_commit"),
        "candidate_tree": pinset.get("candidate_tree"),
        "environment_digest": environment_digest,
        "interpreter_contract_digest": runtime["contract_digest"],
        "records": records,
        "evidence_set_digest": digest({"record_digests": sorted(r["record_digest"] for r in records)}),
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    pathlib.Path(args.output).write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"R12_ADVERSARIAL_EVIDENCE_RECORDS={len(records)}")
    print(f"R12_ADVERSARIAL_EVIDENCE_SET_DIGEST={bundle['evidence_set_digest']}")
    print(f"R12_ADVERSARIAL_EVIDENCE_SHA256={raw_sha256(pathlib.Path(args.output).read_bytes())}")


if __name__ == "__main__":
    main()
