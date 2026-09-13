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
from typing import Any

OBS_PREFIX = "R14_NATIVE_OBSERVATION="
CHECKS = (
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_scenarios(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("r14_trusted_scenario_library", path)
    if spec is None or spec.loader is None:
        raise SystemExit("R14_ORACLE_SCENARIO_LIBRARY_SPEC_INVALID")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate_modules_loaded(sandbox: pathlib.Path) -> list[str]:
    hits=[]
    for name,module in sys.modules.items():
        f=getattr(module,"__file__",None)
        if not isinstance(f,str):
            continue
        try:
            pathlib.Path(f).resolve().relative_to(sandbox)
        except (ValueError,OSError):
            continue
        hits.append(name)
    return sorted(hits)


def run_native(*, sandbox: pathlib.Path, native_observer: pathlib.Path, request: dict[str, Any]) -> dict[str, Any]:
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R14_ORACLE_CANDIDATE_MODULE_PRESENT_IN_TRUSTED_PROCESS")
    with tempfile.TemporaryDirectory(prefix="r14-native-request-") as td:
        req=pathlib.Path(td)/"request.json"
        req.write_bytes(canonical(request))
        env={"HOME":os.environ.get("HOME","/tmp"),"PATH":"/usr/bin:/bin"}
        cp=subprocess.run(
            [str(native_observer),"--sandbox",str(sandbox),"--request",str(req)],
            cwd=str(native_observer.parent),env=env,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60,check=False,
        )
    if cp.returncode != 0:
        raise SystemExit(f"R14_ORACLE_NATIVE_OBSERVER_FAILED:rc={cp.returncode}:stderr={cp.stderr[-1200:]!r}")
    if cp.stderr.strip():
        raise SystemExit(f"R14_ORACLE_NATIVE_OBSERVER_STDERR:{cp.stderr[-1200:]!r}")
    lines=[x for x in cp.stdout.splitlines() if x.strip()]
    if len(lines)!=1 or not lines[0].startswith(OBS_PREFIX):
        raise SystemExit(f"R14_ORACLE_NATIVE_PROTOCOL_INVALID:{lines!r}")
    try:
        obs=json.loads(lines[0][len(OBS_PREFIX):])
    except Exception as exc:
        raise SystemExit(f"R14_ORACLE_NATIVE_JSON_INVALID:{exc}") from exc
    if obs.get("schema_version")!=1:
        raise SystemExit("R14_ORACLE_NATIVE_SCHEMA_INVALID")
    if obs.get("request_digest")!=digest(request):
        raise SystemExit("R14_ORACLE_NATIVE_REQUEST_BINDING_INVALID")
    if obs.get("module")!=request.get("module") or obs.get("function")!=request.get("function"):
        raise SystemExit("R14_ORACLE_NATIVE_CALL_IDENTITY_INVALID")
    if obs.get("candidate_process_role")!="UNTRUSTED_EXECUTION_ONLY":
        raise SystemExit("R14_ORACLE_NATIVE_CANDIDATE_ROLE_INVALID")
    if obs.get("observation_transport")!="NATIVE_PARENT_AUTHENTICATED_FRAME":
        raise SystemExit("R14_ORACLE_NATIVE_TRANSPORT_INVALID")
    if obs.get("native_parent_initializes_python") is not False:
        raise SystemExit("R14_ORACLE_NATIVE_PARENT_PYTHON_INVALID")
    if obs.get("authority_effect")!="NONE_EVIDENCE_ONLY":
        raise SystemExit("R14_ORACLE_NATIVE_AUTHORITY_EFFECT_INVALID")
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R14_ORACLE_CANDIDATE_MODULE_LEAKED_TO_TRUSTED_PROCESS")
    return obs


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sandbox",required=True)
    ap.add_argument("--native-observer",required=True)
    ap.add_argument("--scenario-library",required=True)
    ap.add_argument("--candidate-commit",required=True)
    ap.add_argument("--candidate-tree",required=True)
    ap.add_argument("--environment-digest",required=True)
    ap.add_argument("--interpreter-contract-digest",required=True)
    ap.add_argument("--native-observer-source-git-blob-sha1",required=True)
    ap.add_argument("--native-observer-binary-sha256",required=True)
    ap.add_argument("--native-observer-compiler-digest",required=True)
    ap.add_argument("--oracle-git-blob-sha1",required=True)
    ap.add_argument("--run-id",required=True)
    ap.add_argument("--round-id",required=True)
    ap.add_argument("--r13-regression-evidence-digest",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    sandbox=pathlib.Path(args.sandbox).resolve()
    native=pathlib.Path(args.native_observer).resolve()
    scenario_path=pathlib.Path(args.scenario_library).resolve()
    if native.is_relative_to(sandbox) or scenario_path.is_relative_to(sandbox):
        raise SystemExit("R14_ORACLE_TRUSTED_OBJECT_INSIDE_CANDIDATE")
    if not native.is_file() or not scenario_path.is_file():
        raise SystemExit("R14_ORACLE_TRUSTED_OBJECT_MISSING")
    if not (len(args.r13_regression_evidence_digest)==64 and all(c in "0123456789abcdef" for c in args.r13_regression_evidence_digest)):
        raise SystemExit("R14_ORACLE_R13_REGRESSION_DIGEST_INVALID")

    lib=load_scenarios(scenario_path)
    scenarios=(
        (CHECKS[0],lib.scenario_mixed_terminal),
        (CHECKS[1],lib.scenario_allowed_terminal),
        (CHECKS[2],lib.scenario_genesis_cross_pair),
        (CHECKS[3],lib.scenario_applicability_omission),
        (CHECKS[4],lib.scenario_atomic_omission),
        (CHECKS[5],lib.scenario_historical_pass),
    )
    records=[]
    for check_id,scenario in scenarios:
        nonce=secrets.token_hex(16)
        observed=[]
        def run(req):
            obs=run_native(sandbox=sandbox,native_observer=native,request=req)
            observed.append(obs)
            return obs
        if check_id=="LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT":
            requests,material=scenario(nonce,run,args.candidate_commit,args.candidate_tree,args.environment_digest)
        else:
            requests,material=scenario(nonce,run)
        if material.get("observations")!=observed:
            raise SystemExit(f"R14_ORACLE_SCENARIO_OBSERVATION_BINDING_MISMATCH:{check_id}")
        row={
            "check_id":check_id,
            "challenge_digest":digest({"nonce":nonce,"check_id":check_id}),
            "request_digest":digest(requests),
            "observation_digest":digest(observed),
            "assertion_digest":digest(material.get("assertion")),
            "candidate_commit":args.candidate_commit,
            "candidate_tree":args.candidate_tree,
            "environment_digest":args.environment_digest,
            "interpreter_contract_digest":args.interpreter_contract_digest,
            "native_observer_source_git_blob_sha1":args.native_observer_source_git_blob_sha1,
            "native_observer_binary_sha256":args.native_observer_binary_sha256,
            "native_observer_compiler_digest":args.native_observer_compiler_digest,
            "oracle_git_blob_sha1":args.oracle_git_blob_sha1,
            "run_id":args.run_id,
            "round_id":args.round_id,
            "candidate_process_role":"UNTRUSTED_EXECUTION_ONLY",
            "observation_transport":"NATIVE_PARENT_AUTHENTICATED_FRAME",
            "observation_authentication":"HMAC_SHA256_EPHEMERAL_NATIVE_PARENT",
            "native_parent_initializes_python":False,
            "trusted_parent_imports_candidate_python":False,
            "oracle_decision_origin":"TRUSTED_EXTERNAL_ORACLE",
            "oracle_control_domain":"R14-EXTERNAL-ORACLE",
            "candidate_control_domain":"R14-CANDIDATE",
            "oracle_terminal_result":"PASS",
            "r13_tailored_frame_regression":"REJECTED",
            "r13_tailored_frame_regression_evidence_digest":args.r13_regression_evidence_digest,
        }
        material_for_digest={k:v for k,v in row.items() if k!="r13_tailored_frame_regression_evidence_digest"}
        material_for_digest["r13_tailored_frame_regression_evidence_digest"]=row["r13_tailored_frame_regression_evidence_digest"]
        row["record_digest"]=digest(material_for_digest)
        records.append(row)

    bundle={
        "schema_version":1,
        "authority_origin":"EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant":False,
        "candidate_side_unittest_role":"NON_AUTHORITATIVE_DIAGNOSTIC_ONLY",
        "native_parent_process_initializes_python":False,
        "candidate_python_executes_only_in_forked_child":True,
        "candidate_commit":args.candidate_commit,
        "candidate_tree":args.candidate_tree,
        "environment_digest":args.environment_digest,
        "interpreter_contract_digest":args.interpreter_contract_digest,
        "native_observer_source_git_blob_sha1":args.native_observer_source_git_blob_sha1,
        "native_observer_binary_sha256":args.native_observer_binary_sha256,
        "native_observer_compiler_digest":args.native_observer_compiler_digest,
        "oracle_git_blob_sha1":args.oracle_git_blob_sha1,
        "r13_tailored_frame_regression_evidence_digest":args.r13_regression_evidence_digest,
        "records":records,
        "evidence_set_digest":digest({"record_digests":sorted(x["record_digest"] for x in records)}),
        "scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect":"NONE_EVIDENCE_ONLY",
    }
    pathlib.Path(args.output).write_text(json.dumps(bundle,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"R14_EXTERNAL_ORACLE_RECORDS={len(records)}")
    print(f"R14_EXTERNAL_ORACLE_EVIDENCE_SET_DIGEST={bundle['evidence_set_digest']}")


if __name__=="__main__":
    main()
