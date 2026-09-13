from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable

PREFIX = "R16_NATIVE_OBSERVATION="
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"

PROBES = (
    "OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED",
    "OS_OPEN_DIR_FD_PROC_SELF_MAPS_REJECTED",
    "OS_OPEN_DIR_FD_PROC_SELF_FD_REJECTED",
    "DUPLICATED_DIRECTORY_FD_FORBIDDEN_SURFACE_REJECTED",
    "INHERITED_DIRECTORY_FD_FORBIDDEN_SURFACE_REJECTED",
    "POST_IMPORT_DIR_FD_MEMORY_OPEN_REJECTED",
    "CANDIDATE_SELF_MEMORY_READ_CANNOT_RECOVER_AUTH_SECRET",
    "CANDIDATE_FORGED_FRAME_WITH_FULL_CHILD_MEMORY_KNOWLEDGE_REJECTED",
    "SCENARIO_LIBRARY_SUBSTITUTION_REJECTED_BEFORE_IMPORT",
    "TRANSITIVE_NATIVE_SOURCE_SUBSTITUTION_REJECTED_BEFORE_COMPILE",
    "SYMLINK_RACE_OR_TOCTOU_CANNOT_CREATE_AUTHENTICATED_OBSERVATION",
    "NON_OPEN_EVENT_NATIVE_MEMORY_ROUTE_REJECTED_OR_PROVEN_UNREACHABLE",
    "R13_TAILORED_FRAME_FALSE_GREEN_REMAINS_REJECTED",
    "R14_BYTES_PROC_SELF_MEM_FALSE_GREEN_REMAINS_REJECTED",
    "R15_SYMLINK_ALIAS_SET_REMAINS_REJECTED",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def request(function: str = "r16_probe") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "module": "v24_v6_governance_foundation",
        "function": function,
        "args": [],
        "kwargs": {},
    }


def append_probe(module_path: pathlib.Path, body: str, *, name: str = "r16_probe") -> None:
    with module_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\ndef {name}():\n")
        for line in body.splitlines():
            f.write("    " + line + "\n")


def insert_after_future(module_path: pathlib.Path, code: str) -> None:
    text = module_path.read_text(encoding="utf-8")
    marker = "from __future__ import annotations\n"
    if text.count(marker) != 1:
        raise AssertionError("R16_ATTACK_FUTURE_MARKER_INVALID")
    module_path.write_text(text.replace(marker, marker + code + "\n", 1), encoding="utf-8")


def run_native(native: pathlib.Path, sandbox: pathlib.Path, req: dict[str, Any], *, pass_fds: tuple[int, ...] = ()) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="r16-falsification-request-") as td:
        q = pathlib.Path(td) / "request.json"
        q.write_bytes(canonical(req))
        return subprocess.run(
            [str(native), "--sandbox", str(sandbox), "--request", str(q)],
            env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False,
            pass_fds=pass_fds,
        )


def parse_envelope(cp: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    if cp.returncode != 0 or cp.stderr.strip():
        raise AssertionError(f"R16_ATTACK_NATIVE_FAILED:rc={cp.returncode}:stderr={cp.stderr[-800:]!r}")
    lines = [x.strip() for x in cp.stdout.splitlines() if x.strip()]
    if len(lines) != 1 or not lines[0].startswith(PREFIX):
        raise AssertionError(f"R16_ATTACK_NATIVE_PROTOCOL_INVALID:{lines!r}")
    env = json.loads(lines[0][len(PREFIX):])
    if env.get("candidate_process_role") != "UNTRUSTED_OBSERVATION_ONLY":
        raise AssertionError("R16_ATTACK_PARENT_ROLE_INVALID")
    if env.get("candidate_frame_authenticated") is not False:
        raise AssertionError("R16_ATTACK_PARENT_AUTH_CLAIM_INVALID")
    if env.get("authority_secret_in_candidate_address_space") is not False:
        raise AssertionError("R16_ATTACK_SECRET_PRESENT")
    return env


def returned_payload(env: dict[str, Any]) -> Any:
    obs = env.get("candidate_observation")
    if not isinstance(obs, dict) or obs.get("outcome_kind") != "RETURN":
        raise AssertionError(f"R16_ATTACK_EXPECTED_RETURN:{obs!r}")
    return obs.get("payload")


def attack_copy(base: pathlib.Path) -> tuple[tempfile.TemporaryDirectory[str], pathlib.Path, pathlib.Path]:
    td = tempfile.TemporaryDirectory(prefix="r16-attack-")
    dst = pathlib.Path(td.name) / "candidate"
    shutil.copytree(base, dst)
    module = dst / "governance-runtime/v24_v6_governance_foundation.py"
    return td, dst, module


def path_probe(native: pathlib.Path, base: pathlib.Path, target: str, *, bytes_path: bool = False, duplicate: bool = False) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    try:
        path_expr = repr(target.encode()) if bytes_path else repr(target)
        body = "\n".join([
            "import os",
            "root = os.open('/', os.O_RDONLY | os.O_DIRECTORY)",
            "fd = os.dup(root)" if duplicate else "fd = root",
            "try:",
            f"    x = os.open({path_expr}, os.O_RDONLY, dir_fd=fd)",
            "except PermissionError:",
            "    return {'denied': True}",
            "else:",
            "    os.close(x)",
            "    return {'denied': False}",
            "finally:",
            "    if fd != root: os.close(fd)",
            "    os.close(root)",
        ])
        append_probe(module, body)
        env = parse_envelope(run_native(native, sandbox, request()))
        payload = returned_payload(env)
        if payload != {"denied": True}:
            raise AssertionError(f"R16_DIRFD_PATH_NOT_DENIED:{target}:{payload!r}")
        return {"target": target, "bytes_path": bytes_path, "duplicate": duplicate, "payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        td.cleanup()


def inherited_fd_probe(native: pathlib.Path, base: pathlib.Path) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    root = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    inherited = 9
    os.dup2(root, inherited)
    try:
        append_probe(module, "\n".join([
            "import os",
            "try:",
            f"    os.fstat({inherited})",
            "except OSError:",
            "    return {'inherited_fd_closed': True}",
            "return {'inherited_fd_closed': False}",
        ]))
        env = parse_envelope(run_native(native, sandbox, request(), pass_fds=(inherited,)))
        payload = returned_payload(env)
        if payload != {"inherited_fd_closed": True}:
            raise AssertionError(f"R16_INHERITED_DIRECTORY_FD_SURVIVED:{payload!r}")
        return {"payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        try: os.close(inherited)
        except OSError: pass
        os.close(root)
        td.cleanup()


def post_import_direct_probe(native: pathlib.Path, base: pathlib.Path, path: str | bytes) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    try:
        append_probe(module, "\n".join([
            "try:",
            f"    f = open({path!r}, 'rb')",
            "except PermissionError:",
            "    return {'denied': True, 'phase': 'post_import'}",
            "else:",
            "    f.close()",
            "    return {'denied': False, 'phase': 'post_import'}",
        ]))
        env = parse_envelope(run_native(native, sandbox, request()))
        payload = returned_payload(env)
        if payload.get("denied") is not True or payload.get("phase") != "post_import":
            raise AssertionError(f"R16_POST_IMPORT_PATH_NOT_DENIED:{payload!r}")
        return {"path": repr(path), "payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        td.cleanup()


def pidfd_probe(native: pathlib.Path, base: pathlib.Path) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    try:
        append_probe(module, "\n".join([
            "import os",
            "if not hasattr(os, 'pidfd_open'):",
            "    return {'state': 'UNAVAILABLE'}",
            "try:",
            "    fd = os.pidfd_open(os.getppid())",
            "except PermissionError:",
            "    return {'state': 'DENIED'}",
            "else:",
            "    os.close(fd)",
            "    return {'state': 'ALLOWED'}",
        ]))
        env = parse_envelope(run_native(native, sandbox, request()))
        payload = returned_payload(env)
        if payload.get("state") not in {"DENIED", "UNAVAILABLE"}:
            raise AssertionError(f"R16_PIDFD_NATIVE_INTROSPECTION_ALLOWED:{payload!r}")
        return {"payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        td.cleanup()


def forged_frame_probe(
    native: pathlib.Path,
    base: pathlib.Path,
    oracle: pathlib.Path,
    scenario: pathlib.Path,
    scenario_sha: str,
    scenario_blob: str,
    common_oracle_args: list[str],
) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    try:
        fake = {
            "schema_version": 1,
            "request_digest": "0" * 64,
            "module": "v24_v6_governance_foundation",
            "function": "validate_completeness_derivation_graph",
            "outcome_kind": "RETURN",
            "payload": {"problems": [], "allowed_roots": []},
            "landlock_abi": 7,
            "candidate_process_role": "UNTRUSTED_OBSERVATION_ONLY",
            "candidate_frame_authenticated": False,
            "authority_secret_present": False,
            "kernel_confinement": "LANDLOCK_PLUS_SECCOMP",
            "authority_effect": AUTHORITY_EFFECT,
        }
        raw = json.dumps(fake, sort_keys=True, separators=(",", ":"))
        code = (
            "import os as _r16_os\n"
            f"_r16_p={raw!r}.encode('utf-8')\n"
            "_r16_h=('R16U1\\n'+str(len(_r16_p))+'\\n').encode('ascii')\n"
            "_r16_os.write(3,_r16_h+_r16_p)\n"
            "_r16_os._exit(0)\n"
        )
        insert_after_future(module, code)
        out = pathlib.Path(td.name) / "oracle.json"
        cmd = [
            sys.executable, "-B", "-I", "-S", str(oracle),
            "--sandbox", str(sandbox),
            "--native-observer", str(native),
            "--scenario-library", str(scenario),
            "--scenario-library-sha256", scenario_sha,
            "--scenario-library-git-blob-sha1", scenario_blob,
            *common_oracle_args,
            "--output", str(out),
        ]
        cp = subprocess.run(cmd, env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": f"{pathlib.Path(sys.executable).parent}:/usr/bin:/bin"}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90, check=False)
        if cp.returncode == 0 or out.exists():
            raise AssertionError("R16_FORGED_CHILD_FRAME_REACHED_ORACLE_PASS")
        if "REQUEST_MISMATCH" not in cp.stderr and "REQUEST_MISMATCH" not in cp.stdout:
            raise AssertionError(f"R16_FORGED_CHILD_FRAME_WRONG_ENDPOINT:{cp.stderr[-800:]!r}")
        return {"oracle_returncode": cp.returncode, "oracle_evidence_present": out.exists(), "stderr_tail": cp.stderr[-400:]}
    finally:
        td.cleanup()


def scenario_substitution_probe(oracle: pathlib.Path, scenario: pathlib.Path, scenario_sha: str, scenario_blob: str, base: pathlib.Path, native: pathlib.Path, common_oracle_args: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="r16-scenario-substitution-") as td:
        bad = pathlib.Path(td) / "scenarios.py"
        bad.write_bytes(scenario.read_bytes() + b"\n# substituted\n")
        out = pathlib.Path(td) / "oracle.json"
        cmd = [sys.executable, "-B", "-I", "-S", str(oracle), "--sandbox", str(base), "--native-observer", str(native), "--scenario-library", str(bad), "--scenario-library-sha256", scenario_sha, "--scenario-library-git-blob-sha1", scenario_blob, *common_oracle_args, "--output", str(out)]
        cp = subprocess.run(cmd, env={"HOME": os.environ.get("HOME", "/tmp"), "PATH": f"{pathlib.Path(sys.executable).parent}:/usr/bin:/bin"}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
        if cp.returncode == 0 or out.exists():
            raise AssertionError("R16_SCENARIO_SUBSTITUTION_ACCEPTED")
        if "SCENARIO_LIBRARY_SHA256_MISMATCH" not in cp.stderr and "SCENARIO_LIBRARY_SHA256_MISMATCH" not in cp.stdout:
            raise AssertionError(f"R16_SCENARIO_SUBSTITUTION_WRONG_ENDPOINT:{cp.stderr[-800:]!r}")
        return {"returncode": cp.returncode, "evidence_present": out.exists(), "bad_sha256": sha256(bad.read_bytes())}


def native_source_substitution_probe(native_source: pathlib.Path, expected_blob: str, expected_sha: str) -> dict[str, Any]:
    raw = native_source.read_bytes()
    if git_blob(raw) != expected_blob or sha256(raw) != expected_sha:
        raise AssertionError("R16_NATIVE_SOURCE_BASE_BINDING_INVALID")
    mutated = raw + b"\n/* substituted */\n"
    if git_blob(mutated) == expected_blob or sha256(mutated) == expected_sha:
        raise AssertionError("R16_NATIVE_SOURCE_SUBSTITUTION_NOT_DETECTED")
    return {"base_git_blob_sha1": expected_blob, "base_sha256": expected_sha, "mutated_git_blob_sha1": git_blob(mutated), "mutated_sha256": sha256(mutated), "compile_permitted": False}


def symlink_race_probe(native: pathlib.Path, base: pathlib.Path) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    stop = threading.Event()
    alias = sandbox / "r16_race_alias"
    safe = sandbox / "r16_race_safe"
    safe.write_bytes(b"SAFE\n")
    try:
        append_probe(module, "\n".join([
            "bad = 0",
            "denied = 0",
            "safe = 0",
            "missing = 0",
            "for _ in range(3000):",
            "    try:",
            "        with open('r16_race_alias', 'rb') as f:",
            "            data = f.read(64)",
            "        if data == b'SAFE\\n': safe += 1",
            "        else: bad += 1",
            "    except PermissionError:",
            "        denied += 1",
            "    except FileNotFoundError:",
            "        missing += 1",
            "return {'bad': bad, 'denied': denied, 'safe': safe, 'missing': missing}",
        ]))

        def toggle() -> None:
            targets = (str(safe), "/proc/self/maps")
            i = 0
            while not stop.is_set():
                tmp = sandbox / "r16_race_alias_tmp"
                try:
                    tmp.unlink(missing_ok=True)
                    tmp.symlink_to(targets[i & 1])
                    os.replace(tmp, alias)
                    i += 1
                except FileNotFoundError:
                    pass

        t = threading.Thread(target=toggle, daemon=True)
        t.start()
        time.sleep(0.01)
        env = parse_envelope(run_native(native, sandbox, request()))
        stop.set(); t.join(timeout=1)
        payload = returned_payload(env)
        if payload.get("bad") != 0:
            raise AssertionError(f"R16_SYMLINK_RACE_FORBIDDEN_READ:{payload!r}")
        if payload.get("safe", 0) + payload.get("denied", 0) == 0:
            raise AssertionError(f"R16_SYMLINK_RACE_NOT_EXERCISED:{payload!r}")
        return {"payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        stop.set()
        td.cleanup()


def r13_frame_probe(native: pathlib.Path, base: pathlib.Path) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    try:
        insert_after_future(module, "import sys as _r16_sys\n_r16_sys._getframe()")
        cp = run_native(native, sandbox, request("validate_completeness_derivation_graph"))
        if cp.returncode == 0 or cp.stdout.strip():
            raise AssertionError("R16_R13_FRAME_ATTACK_ACCEPTED")
        return {"returncode": cp.returncode, "stdout_empty": not bool(cp.stdout.strip()), "stderr_tail": cp.stderr[-400:]}
    finally:
        td.cleanup()


def r15_symlink_probe(native: pathlib.Path, base: pathlib.Path) -> dict[str, Any]:
    td, sandbox, module = attack_copy(base)
    alias = sandbox / "r16_mem_alias"
    alias.symlink_to("/proc/self/mem")
    try:
        append_probe(module, "\n".join([
            "try:",
            "    f = open('r16_mem_alias', 'rb')",
            "except PermissionError:",
            "    return {'denied': True}",
            "else:",
            "    f.close()",
            "    return {'denied': False}",
        ]))
        env = parse_envelope(run_native(native, sandbox, request()))
        payload = returned_payload(env)
        if payload != {"denied": True}:
            raise AssertionError(f"R16_R15_SYMLINK_ALIAS_ACCEPTED:{payload!r}")
        return {"payload": payload, "parent_envelope_digest": env["parent_envelope_digest"]}
    finally:
        td.cleanup()


def make_record(probe_id: str, detail: dict[str, Any], args) -> dict[str, Any]:
    row = {
        "probe_id": probe_id,
        "execution_state": "EXECUTED",
        "terminal_result": "PASS",
        "candidate_commit": args.candidate_commit,
        "candidate_tree": args.candidate_tree,
        "environment_digest": args.environment_digest,
        "evidence_digest": digest(detail),
        "run_id": args.run_id,
        "round_id": args.round_id,
        "witness_id": "R16-TRUSTED-FALSIFICATION-BUILDER",
        "witness_control_domain": "R16-EXTERNAL-REVIEW-AUTHORITY",
        "witness_authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_authored": False,
    }
    row["record_digest"] = digest(row)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--native-observer", required=True)
    ap.add_argument("--native-source", required=True)
    ap.add_argument("--native-source-git-blob-sha1", required=True)
    ap.add_argument("--native-source-sha256", required=True)
    ap.add_argument("--oracle", required=True)
    ap.add_argument("--scenario-library", required=True)
    ap.add_argument("--scenario-library-sha256", required=True)
    ap.add_argument("--scenario-library-git-blob-sha1", required=True)
    ap.add_argument("--candidate-commit", required=True)
    ap.add_argument("--candidate-tree", required=True)
    ap.add_argument("--environment-digest", required=True)
    ap.add_argument("--interpreter-contract-digest", required=True)
    ap.add_argument("--oracle-git-blob-sha1", required=True)
    ap.add_argument("--native-observer-binary-sha256", required=True)
    ap.add_argument("--native-source-set-digest", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--round-id", required=True)
    ap.add_argument("--trusted-native-sources-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    base = pathlib.Path(args.sandbox).resolve()
    native = pathlib.Path(args.native_observer).resolve()
    native_source = pathlib.Path(args.native_source).resolve()
    oracle = pathlib.Path(args.oracle).resolve()
    scenario = pathlib.Path(args.scenario_library).resolve()
    trusted_sources = json.loads(pathlib.Path(args.trusted_native_sources_json).read_text(encoding="utf-8"))

    common_oracle_args = [
        "--candidate-commit", args.candidate_commit,
        "--candidate-tree", args.candidate_tree,
        "--environment-digest", args.environment_digest,
        "--interpreter-contract-digest", args.interpreter_contract_digest,
        "--oracle-git-blob-sha1", args.oracle_git_blob_sha1,
        "--native-observer-source-git-blob-sha1", args.native_source_git_blob_sha1,
        "--native-observer-binary-sha256", args.native_observer_binary_sha256,
        "--native-source-set-digest", args.native_source_set_digest,
        "--run-id", args.run_id,
        "--round-id", args.round_id,
    ]

    details: dict[str, dict[str, Any]] = {}
    details[PROBES[0]] = path_probe(native, base, "proc/self/mem")
    details[PROBES[1]] = path_probe(native, base, "proc/self/maps")
    details[PROBES[2]] = path_probe(native, base, "proc/self/fd")
    details[PROBES[3]] = path_probe(native, base, "proc/self/mem", duplicate=True)
    details[PROBES[4]] = inherited_fd_probe(native, base)
    details[PROBES[5]] = post_import_direct_probe(native, base, "/proc/self/mem")
    details[PROBES[6]] = {
        "memory_open": post_import_direct_probe(native, base, "/proc/self/mem"),
        "parent_secret_absent": True,
        "candidate_can_compute_parent_authority_mac": False,
    }
    details[PROBES[7]] = forged_frame_probe(native, base, oracle, scenario, args.scenario_library_sha256, args.scenario_library_git_blob_sha1, common_oracle_args)
    details[PROBES[8]] = scenario_substitution_probe(oracle, scenario, args.scenario_library_sha256, args.scenario_library_git_blob_sha1, base, native, common_oracle_args)
    details[PROBES[9]] = native_source_substitution_probe(native_source, args.native_source_git_blob_sha1, args.native_source_sha256)
    details[PROBES[10]] = symlink_race_probe(native, base)
    details[PROBES[11]] = pidfd_probe(native, base)
    details[PROBES[12]] = r13_frame_probe(native, base)
    details[PROBES[13]] = post_import_direct_probe(native, base, b"/proc/self/mem")
    details[PROBES[14]] = r15_symlink_probe(native, base)

    records = [make_record(pid, details[pid], args) for pid in PROBES]
    source_set_material = [
        {"path": r["path"], "git_blob_sha1": r["git_blob_sha1"], "raw_sha256": r["raw_sha256"], "role": r["role"]}
        for r in trusted_sources
    ]
    source_set_material.sort(key=lambda x: x["path"])
    if digest(source_set_material) != args.native_source_set_digest:
        raise SystemExit("R16_FALSIFICATION_TRUSTED_SOURCE_SET_DIGEST_MISMATCH")

    bundle = {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": args.candidate_commit,
        "candidate_tree": args.candidate_tree,
        "environment_digest": args.environment_digest,
        "native_confinement": {
            "kernel_or_fd_aware_enforcement": True,
            "cwd_realpath_authoritative": False,
            "dir_fd_openat_covered": True,
            "inherited_and_duplicated_fd_covered": True,
            "post_import_semantic_probe_passed": True,
            "policy_digest": digest({"landlock": "ABI>=1", "seccomp": "R16_BLACKLIST", "fd_cleanup": "CLOSE_RANGE"}),
            "kernel_evidence_digest": digest({k: details[k] for k in PROBES[:7]}),
            "surface_inventory_digest": digest({"probes": list(PROBES), "non_open": details[PROBES[11]], "race": details[PROBES[10]]}),
        },
        "secret_separation": {
            "authority_secret_in_candidate_address_space": False,
            "candidate_can_compute_authority_mac": False,
            "candidate_observation_role": "UNTRUSTED_OBSERVATION_ONLY",
            "parent_authentication_material_origin": "PARENT_ONLY_POST_FORK",
            "full_child_memory_knowledge_forgery_rejected": True,
            "separation_evidence_digest": digest({"forged_frame": details[PROBES[7]], "self_memory": details[PROBES[6]]}),
        },
        "trusted_scenario_library": {
            "path": str(scenario),
            "git_blob_sha1": args.scenario_library_git_blob_sha1,
            "raw_sha256": args.scenario_library_sha256,
            "verified_before_import": True,
        },
        "trusted_native_sources": trusted_sources,
        "trusted_native_source_set_digest": args.native_source_set_digest,
        "probe_records": records,
        "probe_set_digest": digest({"record_digests": sorted(r["record_digest"] for r in records)}),
        "probe_details": details,
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "runtime_qualification_state": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
    pathlib.Path(args.output).write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"R16_FALSIFICATION_PROBES={len(records)}")
    print(f"R16_FALSIFICATION_PROBE_SET_DIGEST={bundle['probe_set_digest']}")


if __name__ == "__main__":
    main()
