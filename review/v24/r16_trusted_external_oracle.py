from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import secrets
import subprocess
import sys
import tempfile
from typing import Any, Callable

PREFIX = "R16_NATIVE_OBSERVATION="
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def actual_interpreter_contract() -> dict[str, Any]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    if any(v is not True for v in flags.values()):
        raise SystemExit("R16_ORACLE_INTERPRETER_NOT_ISOLATED")
    if sys.flags.optimize != 0:
        raise SystemExit("R16_ORACLE_OPTIMIZATION_FORBIDDEN")
    executable = pathlib.Path(sys.executable).resolve()
    contract = {
        "flags": flags,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "version": list(sys.version_info),
        "hexversion": sys.hexversion,
        "executable_sha256": raw_sha256(executable.read_bytes()),
        "stdlib_module_names_digest": digest(sorted(sys.stdlib_module_names)),
        "candidate_path_absent": True,
        "trusted_oracle_imports_candidate": False,
    }
    contract["contract_digest"] = digest(contract)
    return contract


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


def load_bound_scenarios(path: pathlib.Path, expected_sha256: str, expected_git_blob_sha1: str):
    raw = path.read_bytes()
    if raw_sha256(raw) != expected_sha256:
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_SHA256_MISMATCH")
    if git_blob_sha1(raw) != expected_git_blob_sha1:
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_GIT_BLOB_MISMATCH")
    spec = importlib.util.spec_from_file_location("r16_bound_scenarios", path)
    if spec is None or spec.loader is None:
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not isinstance(getattr(module, "CHECKS", None), tuple) or len(module.CHECKS) != 6:
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_CHECK_SET_INVALID")
    required = (
        "scenario_mixed_terminal",
        "scenario_allowed_terminal",
        "scenario_genesis_cross_pair",
        "scenario_applicability_omission",
        "scenario_atomic_omission",
        "scenario_historical_pass",
    )
    if any(not callable(getattr(module, name, None)) for name in required):
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_FUNCTION_SET_INVALID")
    return module


def verify_parent_envelope(envelope: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if envelope.get("schema_version") != 1:
        raise AssertionError("R16_ORACLE_PARENT_ENVELOPE_SCHEMA_INVALID")
    if envelope.get("candidate_process_role") != "UNTRUSTED_OBSERVATION_ONLY":
        raise AssertionError("R16_ORACLE_PARENT_CANDIDATE_ROLE_INVALID")
    if envelope.get("candidate_frame_authenticated") is not False:
        raise AssertionError("R16_ORACLE_CANDIDATE_FRAME_MUST_REMAIN_UNAUTHENTICATED")
    if envelope.get("authority_secret_in_candidate_address_space") is not False:
        raise AssertionError("R16_ORACLE_AUTHORITY_SECRET_IN_CANDIDATE")
    if envelope.get("parent_authentication_material_origin") != "PARENT_ONLY_POST_FORK":
        raise AssertionError("R16_ORACLE_PARENT_MATERIAL_ORIGIN_INVALID")
    if envelope.get("native_parent_initializes_python") is not False:
        raise AssertionError("R16_ORACLE_NATIVE_PARENT_INITIALIZED_PYTHON")
    if envelope.get("authority_effect") != AUTHORITY_EFFECT:
        raise AssertionError("R16_ORACLE_PARENT_AUTHORITY_EFFECT_INVALID")

    nonce = envelope.get("parent_nonce")
    obs_sha = envelope.get("candidate_observation_sha256")
    env_digest = envelope.get("parent_envelope_digest")
    if not all(isinstance(x, str) and len(x) == 64 for x in (nonce, obs_sha, env_digest)):
        raise AssertionError("R16_ORACLE_PARENT_DIGEST_FIELDS_INVALID")
    expected = hashlib.sha256(bytes.fromhex(nonce) + bytes.fromhex(obs_sha)).hexdigest()
    if env_digest != expected:
        raise AssertionError("R16_ORACLE_PARENT_ENVELOPE_DIGEST_MISMATCH")

    obs = envelope.get("candidate_observation")
    if not isinstance(obs, dict):
        raise AssertionError("R16_ORACLE_CANDIDATE_OBSERVATION_INVALID")
    if obs.get("schema_version") != 1:
        raise AssertionError("R16_ORACLE_CANDIDATE_OBSERVATION_SCHEMA_INVALID")
    if obs.get("request_digest") != digest(request):
        raise AssertionError("R16_ORACLE_CANDIDATE_OBSERVATION_REQUEST_MISMATCH")
    if obs.get("module") != request.get("module") or obs.get("function") != request.get("function"):
        raise AssertionError("R16_ORACLE_CANDIDATE_OBSERVATION_CALL_MISMATCH")
    if obs.get("candidate_process_role") != "UNTRUSTED_OBSERVATION_ONLY":
        raise AssertionError("R16_ORACLE_CHILD_ROLE_INVALID")
    if obs.get("candidate_frame_authenticated") is not False:
        raise AssertionError("R16_ORACLE_CHILD_FRAME_AUTHENTICATION_CLAIM_FORBIDDEN")
    if obs.get("authority_secret_present") is not False:
        raise AssertionError("R16_ORACLE_CHILD_SECRET_PRESENT")
    if obs.get("kernel_confinement") != "LANDLOCK_PLUS_SECCOMP":
        raise AssertionError("R16_ORACLE_KERNEL_CONFINEMENT_MISSING")
    if not isinstance(obs.get("landlock_abi"), int) or obs["landlock_abi"] < 1:
        raise AssertionError("R16_ORACLE_LANDLOCK_ABI_INVALID")
    if obs.get("authority_effect") != AUTHORITY_EFFECT:
        raise AssertionError("R16_ORACLE_CHILD_AUTHORITY_EFFECT_INVALID")
    return obs


def run_native_observer(*, sandbox: pathlib.Path, native_observer: pathlib.Path, request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R16_ORACLE_CANDIDATE_MODULE_PRESENT_IN_TRUSTED_PROCESS")
    if native_observer.is_relative_to(sandbox):
        raise SystemExit("R16_ORACLE_NATIVE_OBSERVER_INSIDE_CANDIDATE")
    with tempfile.TemporaryDirectory(prefix="r16-request-") as td:
        request_path = pathlib.Path(td) / "request.json"
        request_path.write_bytes(canonical(request))
        cp = subprocess.run(
            [str(native_observer), "--sandbox", str(sandbox), "--request", str(request_path)],
            cwd=str(native_observer.parent),
            env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=90,
            check=False,
        )
    if cp.returncode != 0:
        raise AssertionError(f"R16_ORACLE_NATIVE_OBSERVER_FAILED:rc={cp.returncode}:stderr={cp.stderr[-1000:]!r}")
    if cp.stderr.strip():
        raise AssertionError(f"R16_ORACLE_NATIVE_OBSERVER_STDERR:{cp.stderr[-1000:]!r}")
    lines = [x.strip() for x in cp.stdout.splitlines() if x.strip()]
    if len(lines) != 1 or not lines[0].startswith(PREFIX):
        raise AssertionError(f"R16_ORACLE_NATIVE_OBSERVER_PROTOCOL_INVALID:{lines!r}")
    envelope = json.loads(lines[0][len(PREFIX):])
    observation = verify_parent_envelope(envelope, request)
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R16_ORACLE_CANDIDATE_MODULE_LEAKED_TO_TRUSTED_PROCESS")
    return observation, envelope


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--native-observer", required=True)
    ap.add_argument("--scenario-library", required=True)
    ap.add_argument("--scenario-library-sha256", required=True)
    ap.add_argument("--scenario-library-git-blob-sha1", required=True)
    ap.add_argument("--candidate-commit", required=True)
    ap.add_argument("--candidate-tree", required=True)
    ap.add_argument("--environment-digest", required=True)
    ap.add_argument("--interpreter-contract-digest", required=True)
    ap.add_argument("--oracle-git-blob-sha1", required=True)
    ap.add_argument("--native-observer-source-git-blob-sha1", required=True)
    ap.add_argument("--native-observer-binary-sha256", required=True)
    ap.add_argument("--native-source-set-digest", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--round-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    runtime = actual_interpreter_contract()
    if runtime["contract_digest"] != args.interpreter_contract_digest:
        raise SystemExit("R16_ORACLE_INTERPRETER_CONTRACT_MISMATCH")
    sandbox = pathlib.Path(args.sandbox).resolve()
    native = pathlib.Path(args.native_observer).resolve()
    scenario_path = pathlib.Path(args.scenario_library).resolve()
    if scenario_path.is_relative_to(sandbox):
        raise SystemExit("R16_ORACLE_SCENARIO_LIBRARY_INSIDE_CANDIDATE")
    if "" in sys.path or str(sandbox) in sys.path or str(sandbox / "governance-runtime") in sys.path:
        raise SystemExit("R16_ORACLE_CANDIDATE_PATH_PRESENT")
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R16_ORACLE_CANDIDATE_MODULE_ALREADY_LOADED")

    scenarios = load_bound_scenarios(
        scenario_path,
        args.scenario_library_sha256,
        args.scenario_library_git_blob_sha1,
    )
    scenario_map: dict[str, Callable[..., tuple[list[dict], dict]]] = {
        scenarios.CHECKS[0]: scenarios.scenario_mixed_terminal,
        scenarios.CHECKS[1]: scenarios.scenario_allowed_terminal,
        scenarios.CHECKS[2]: scenarios.scenario_genesis_cross_pair,
        scenarios.CHECKS[3]: scenarios.scenario_applicability_omission,
        scenarios.CHECKS[4]: scenarios.scenario_atomic_omission,
    }

    records: list[dict[str, Any]] = []
    for check_id in scenarios.CHECKS:
        nonce = secrets.token_hex(16)
        envelopes: list[dict[str, Any]] = []

        def run(request: dict[str, Any]):
            observation, parent_envelope = run_native_observer(
                sandbox=sandbox,
                native_observer=native,
                request=request,
            )
            envelopes.append(parent_envelope)
            return observation

        if check_id == scenarios.CHECKS[5]:
            requests, detail = scenarios.scenario_historical_pass(
                nonce,
                run,
                args.candidate_commit,
                args.candidate_tree,
                args.environment_digest,
            )
        else:
            requests, detail = scenario_map[check_id](nonce, run)

        observations = detail["observations"]
        assertion_material = {
            "check_id": check_id,
            "assertion": detail["assertion"],
            "observation_digest": digest(observations),
            "parent_envelope_digest": digest(envelopes),
        }
        record = {
            "check_id": check_id,
            "challenge_digest": digest({"check_id": check_id, "nonce": nonce}),
            "request_digest": digest(requests),
            "observation_digest": digest(observations),
            "parent_envelope_set_digest": digest(envelopes),
            "assertion_digest": digest(assertion_material),
            "candidate_commit": args.candidate_commit,
            "candidate_tree": args.candidate_tree,
            "environment_digest": args.environment_digest,
            "interpreter_contract_digest": args.interpreter_contract_digest,
            "oracle_git_blob_sha1": args.oracle_git_blob_sha1,
            "native_observer_source_git_blob_sha1": args.native_observer_source_git_blob_sha1,
            "native_observer_binary_sha256": args.native_observer_binary_sha256,
            "native_source_set_digest": args.native_source_set_digest,
            "scenario_library_git_blob_sha1": args.scenario_library_git_blob_sha1,
            "scenario_library_sha256": args.scenario_library_sha256,
            "scenario_library_verified_before_import": True,
            "run_id": args.run_id,
            "round_id": args.round_id,
            "candidate_process_role": "UNTRUSTED_OBSERVATION_ONLY",
            "candidate_frame_authenticated": False,
            "authority_secret_in_candidate_address_space": False,
            "parent_authentication_material_origin": "PARENT_ONLY_POST_FORK",
            "oracle_decision_origin": "TRUSTED_EXTERNAL_ORACLE",
            "oracle_control_domain": "R16-EXTERNAL-TRUSTED-ORACLE",
            "candidate_control_domain": "R16-CANDIDATE-EXECUTION",
            "oracle_terminal_result": "PASS",
        }
        record["record_digest"] = digest(record)
        records.append(record)

    bundle = {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": args.candidate_commit,
        "candidate_tree": args.candidate_tree,
        "environment_digest": args.environment_digest,
        "interpreter_contract_digest": args.interpreter_contract_digest,
        "oracle_git_blob_sha1": args.oracle_git_blob_sha1,
        "native_observer_source_git_blob_sha1": args.native_observer_source_git_blob_sha1,
        "native_observer_binary_sha256": args.native_observer_binary_sha256,
        "native_source_set_digest": args.native_source_set_digest,
        "scenario_library_path": str(scenario_path),
        "scenario_library_git_blob_sha1": args.scenario_library_git_blob_sha1,
        "scenario_library_sha256": args.scenario_library_sha256,
        "scenario_library_verified_before_import": True,
        "candidate_process_role": "UNTRUSTED_OBSERVATION_ONLY",
        "candidate_frame_authenticated": False,
        "authority_secret_in_candidate_address_space": False,
        "parent_authentication_material_origin": "PARENT_ONLY_POST_FORK",
        "records": records,
        "evidence_set_digest": digest({"record_digests": sorted(r["record_digest"] for r in records)}),
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "runtime_qualification_state": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
    pathlib.Path(args.output).write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"R16_TRUSTED_ORACLE_CHECKS={len(records)}")
    print(f"R16_TRUSTED_ORACLE_EVIDENCE_SET_DIGEST={bundle['evidence_set_digest']}")


if __name__ == "__main__":
    main()
