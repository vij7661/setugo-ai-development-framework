#!/usr/bin/env python3
"""R8 v15-r1 Stage2 SG-1 dependency-semantic conformance harness.

Qualification-only. Executes against an exact closed Stage1 candidate worktree.
It does not modify candidate bytes, grant authority, contact external systems,
or perform currentness/qualification/evidence-promotion decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import pathlib
import sys
from typing import Any

PROPOSAL_ROOT=pathlib.Path(__file__).resolve().parent.parent
SURFACE=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-SURFACE.json"
ALLOW=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
CANDIDATE="4984f06a4420b76ad1ad475751aebda04a2d2c5c"
TREE="5a34e0d7db3e750dd5b0f722ccecc8014be189ef"
FROZEN_RUNTIME_PATH="governance-runtime/r8_v15_r1_frozen_schema_runtime.py"
FROZEN_RUNTIME_BLOB="e5a06f43b98131f0730852757a83bb7fe5882001"
EFFECT_INTENT_PATH="governance-runtime/r8_v15_r1_effect_intent_validator.py"
EFFECT_INTENT_BLOB="50c5f3edd905ec23ae8e97d3cc2d441489935786"
EFFECT_STATE_PATH="governance-runtime/r8_v15_r1_effect_state_validator.py"
EFFECT_STATE_BLOB="d89b5929b607a1a39c9e412dffded49586ce3b91"
SLICE7_TEST_PATH="governance-runtime/test_r8_v15_r1_implementation_slice7.py"
SLICE7_TEST_BLOB="c11a7ce8eb04a23016abaed5456b3a6ae169cd7f"
SLICE8_TEST_PATH="governance-runtime/test_r8_v15_r1_implementation_slice8.py"
SLICE8_TEST_BLOB="62a15e44ee17d08becb14bc955e1368f88a6b0c7"

BLOCKED_AUDIT_PREFIXES=(
    "subprocess.Popen","socket.connect","socket.bind","socket.listen",
    "os.system","os.exec","os.spawn","os.fork","os.remove","os.unlink",
    "os.rename","os.replace","os.mkdir","os.rmdir"
)

def audit(event: str, args: tuple[Any,...]) -> None:
    if event.startswith(BLOCKED_AUDIT_PREFIXES):
        raise RuntimeError(f"SG1_EXTERNAL_OR_MUTATING_EFFECT_BLOCKED: {event}")
    if event=="open":
        mode=""
        if len(args)>=2 and isinstance(args[1],str):
            mode=args[1]
        if any(ch in mode for ch in "wax+"):
            raise RuntimeError(f"SG1_FILE_WRITE_BLOCKED: mode={mode}")

def git_blob_sha1(data: bytes) -> str:
    header=f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header+data).hexdigest()

def exact_file(target: pathlib.Path, rel: str, expected_blob: str) -> pathlib.Path:
    p=(target/rel).resolve()
    root=target.resolve()
    try:
        p.relative_to(root)
    except ValueError as exc:
        raise AssertionError(f"SG1_PATH_ESCAPE: {rel} -> {p}") from exc
    if not p.is_file():
        raise AssertionError(f"SG1_FILE_MISSING: {rel}")
    actual=git_blob_sha1(p.read_bytes())
    if actual!=expected_blob:
        raise AssertionError(f"SG1_BLOB_MISMATCH: {rel} {actual} != {expected_blob}")
    return p

def module_name(path: str) -> str:
    return pathlib.PurePosixPath(path).stem

def code_hash(fn: Any) -> str:
    return hashlib.sha256(fn.__code__.co_code).hexdigest()

def expect_error(fn, error_type, code: str, contains: str|None=None):
    try:
        fn()
    except error_type as exc:
        if getattr(exc,"code",None)!=code:
            raise AssertionError(f"expected {code}, got {getattr(exc,'code',None)}: {exc}") from exc
        if contains is not None and contains not in str(exc):
            raise AssertionError(f"expected nested marker {contains!r} in {exc!s}") from exc
        return
    raise AssertionError(f"expected {error_type.__name__} code {code}")

def authority_false(result: dict[str,Any]) -> None:
    if result.get("authority_effect")!="NONE":
        raise AssertionError("authority_effect must be NONE")
    for key in (
        "effect_state_committed","executor_qualified","reconciliation_verified",
        "external_effect_succeeded","compensation_authorized","runtime_qualified",
        "release_authorized","deployment_authorized","production_authorized",
        "policy_authorized","terminal_authority",
    ):
        if result.get(key) is not False:
            raise AssertionError(f"{key} must remain false")

def main() -> None:
    sys.addaudithook(audit)
    ap=argparse.ArgumentParser()
    ap.add_argument("--target",required=True)
    ap.add_argument("--order",choices=("forward","reverse"),required=True)
    args=ap.parse_args()
    target=pathlib.Path(args.target).resolve()
    runtime_dir=(target/"governance-runtime").resolve()
    sys.path.insert(0,str(runtime_dir))

    surface=json.loads(SURFACE.read_text())
    allow=json.loads(ALLOW.read_text())
    assert surface["candidate"]==CANDIDATE
    assert surface["candidate_tree"]==TREE
    assert surface["direct_r8_dependency_edges"]==32
    assert surface["unique_dependency_targets"]==2
    cases={}

    # Case 01: exact dependency targets and reviewed fixture/source identities.
    exact_file(target,FROZEN_RUNTIME_PATH,FROZEN_RUNTIME_BLOB)
    exact_file(target,EFFECT_INTENT_PATH,EFFECT_INTENT_BLOB)
    exact_file(target,EFFECT_STATE_PATH,EFFECT_STATE_BLOB)
    exact_file(target,SLICE7_TEST_PATH,SLICE7_TEST_BLOB)
    exact_file(target,SLICE8_TEST_PATH,SLICE8_TEST_BLOB)
    cases["SG1-01-exact-target-and-fixture-identities"]=True

    # Expected source blobs are inherited from the exact reviewed Stage1 allowlist.
    allow_by_path={
      e["path"]:e["blob"]
      for rec in allow["per_candidate"].values()
      for e in rec["selected_entries"]
    }
    source_paths=sorted({e["from_path"] for e in surface["edges"]})
    for path in source_paths:
        exact_file(target,path,allow_by_path[path])
    cases["SG1-02-exact-consumer-identities"]=True

    frozen=importlib.import_module("r8_v15_r1_frozen_schema_runtime")
    effect_intent=importlib.import_module("r8_v15_r1_effect_intent_validator")
    if pathlib.Path(frozen.__file__).resolve()!=exact_file(target,FROZEN_RUNTIME_PATH,FROZEN_RUNTIME_BLOB):
        raise AssertionError("frozen runtime resolved to wrong file")
    if pathlib.Path(effect_intent.__file__).resolve()!=exact_file(target,EFFECT_INTENT_PATH,EFFECT_INTENT_BLOB):
        raise AssertionError("effect intent resolved to wrong file")
    cases["SG1-03-runtime-resolution-exact"]=True

    ordered=source_paths if args.order=="forward" else list(reversed(source_paths))
    modules={}
    for path in ordered:
        mod=importlib.import_module(module_name(path))
        if pathlib.Path(mod.__file__).resolve()!=exact_file(target,path,allow_by_path[path]):
            raise AssertionError(f"consumer resolved to wrong file: {path}")
        modules[path]=mod
    cases["SG1-04-all-consumers-import-in-selected-order"]=True

    frozen_edges=[e for e in surface["edges"] if e["target_path"]==FROZEN_RUNTIME_PATH]
    if len(frozen_edges)!=31:
        raise AssertionError(f"expected 31 frozen-runtime edges, got {len(frozen_edges)}")
    for e in frozen_edges:
        mod=modules[e["from_path"]]
        alias_obj=getattr(mod,e["alias"])
        if alias_obj is not frozen:
            raise AssertionError(f"module object mismatch: {e['from_path']} alias {e['alias']}")
    cases["SG1-05-shared-frozen-runtime-module-object"]=True

    for e in frozen_edges:
        mod=modules[e["from_path"]]
        alias_obj=getattr(mod,e["alias"])
        for attr in e["used_attributes"]:
            actual=getattr(alias_obj,attr)
            expected=getattr(frozen,attr)
            if attr=="INT64_MAX":
                if actual!=expected or actual!=(2**63-1):
                    raise AssertionError(f"INT64_MAX mismatch in {e['from_path']}")
            elif actual is not expected:
                raise AssertionError(f"{attr} object identity mismatch in {e['from_path']}")
    cases["SG1-06-used-frozen-surface-object-identity"]=True

    if frozen.canonicalize_json_text('{"value":"abc"}',schema_context="object")!=b'{"value":"abc"}':
        raise AssertionError("canonicalization valid case mismatch")
    cases["SG1-07-gcp-valid-canonicalization"]=True

    expect_error(
      lambda:frozen.canonicalize_json_text('{"value":"e\\u0301"}',schema_context="object"),
      frozen.GCPError,"GCP_REJECT_NON_NFC_STRING"
    )
    cases["SG1-08-gcp-non-nfc-rejection"]=True

    expect_error(
      lambda:frozen.canonicalize_json_text('{"value":"\\ufdd0"}',schema_context="object"),
      frozen.GCPError,"GCP_REJECT_UNICODE_NONCHARACTER_FDD0"
    )
    cases["SG1-09-gcp-noncharacter-rejection"]=True

    maxv=str(2**63-1)
    if frozen.canonicalize_json_text(maxv,schema_context="integer_range")!=maxv.encode("ascii"):
        raise AssertionError("INT64_MAX canonicalization mismatch")
    expect_error(
      lambda:frozen.canonicalize_json_text(str(2**63),schema_context="integer_range"),
      frozen.GCPError,"GCP_REJECT_OUT_OF_INT64"
    )
    cases["SG1-10-int64-boundary"]=True

    state=modules[EFFECT_STATE_PATH]
    if getattr(state,"slice7") is not effect_intent:
        raise AssertionError("effect-state slice7 alias does not resolve to exact effect-intent module")
    if state.slice7.validate_effect_intent is not effect_intent.validate_effect_intent:
        raise AssertionError("effect-intent function identity mismatch")
    if state.slice7.EffectIntentError is not effect_intent.EffectIntentError:
        raise AssertionError("effect-intent error class identity mismatch")
    cases["SG1-11-effect-state-dependency-object-identity"]=True

    s7=importlib.import_module("test_r8_v15_r1_implementation_slice7")
    s8=importlib.import_module("test_r8_v15_r1_implementation_slice8")
    if pathlib.Path(s7.__file__).resolve()!=exact_file(target,SLICE7_TEST_PATH,SLICE7_TEST_BLOB):
        raise AssertionError("slice7 fixture module mismatch")
    if pathlib.Path(s8.__file__).resolve()!=exact_file(target,SLICE8_TEST_PATH,SLICE8_TEST_BLOB):
        raise AssertionError("slice8 fixture module mismatch")

    def validate(record=None,intent=None,qtp=None):
        return state.validate_effect_state_record(
          record or s8.record(),
          effect_intent=intent or s7.intent(),
          decision_preseal=s7.dps(),
          authority_read_set=s7.ars(),
          qualified_time_proof=qtp or s7.qtp(),
          verified_state_seal=s7.seal_obj(),
          external_effect_involved=True,
        )

    valid=validate()
    if valid["locally_valid"] is not True or valid["effect_intent_locally_valid"] is not True:
        raise AssertionError("valid delegated state did not pass")
    authority_false(valid)
    cases["SG1-12-valid-effect-state-delegation-nonauthority"]=True

    bad_intent=s7.intent(); bad_intent["state"]="DISPATCHING"
    expect_error(
      lambda:validate(intent=bad_intent),
      state.EffectStateError,"EFFECT_STATE_INTENT_INVALID","EFFECT_INTENT_STATE_INVALID"
    )
    cases["SG1-13-invalid-intent-error-translation"]=True

    bad_qtp=s7.qtp(); bad_qtp["nonce_256bit_hex"]="g"*64
    expect_error(
      lambda:validate(qtp=bad_qtp),
      state.EffectStateError,"EFFECT_STATE_INTENT_INVALID","EFFECT_INTENT_TIME_PROOF_INVALID"
    )
    cases["SG1-14-nested-timeproof-error-translation"]=True

    bad_record=s8.record(); bad_record["effect_intent_id"]="effect:other"
    expect_error(lambda:validate(record=bad_record),state.EffectStateError,"EFFECT_STATE_INTENT_ID_MISMATCH")
    cases["SG1-15-effect-intent-id-binding"]=True

    bad_record=s8.record(); bad_record["idempotency_key"]="idem:other"
    expect_error(lambda:validate(record=bad_record),state.EffectStateError,"EFFECT_STATE_IDEMPOTENCY_MISMATCH")
    cases["SG1-16-idempotency-binding"]=True

    succeeded=validate(record=s8.record("SUCCEEDED_RECONCILED"))
    authority_false(succeeded)
    if succeeded["state"]!="SUCCEEDED_RECONCILED":
        raise AssertionError("state label mismatch")
    cases["SG1-17-success-label-does-not-grant-authority"]=True

    bad=s8.record(); bad["state"]="BAD"
    expect_error(lambda:validate(record=bad),state.EffectStateError,"EFFECT_STATE_STATE_INVALID")
    first=validate(); second=validate()
    if first!=second:
        raise AssertionError("failure poisoned subsequent validation")
    authority_false(first)
    cases["SG1-18-failure-nonpoison-determinism"]=True

    fingerprint={
      "frozen_runtime":{
        "blob":FROZEN_RUNTIME_BLOB,
        "GCPError_module":frozen.GCPError.__module__,
        "GCPError_qualname":frozen.GCPError.__qualname__,
        "canonicalize_code_sha256":code_hash(frozen.canonicalize_json_text),
        "INT64_MAX":frozen.INT64_MAX,
      },
      "effect_intent":{
        "blob":EFFECT_INTENT_BLOB,
        "error_module":effect_intent.EffectIntentError.__module__,
        "error_qualname":effect_intent.EffectIntentError.__qualname__,
        "validate_code_sha256":code_hash(effect_intent.validate_effect_intent),
      },
      "dependency_edges":[
        {
          "from_path":e["from_path"],"target_path":e["target_path"],
          "alias":e["alias"],"used_attributes":e["used_attributes"]
        } for e in surface["edges"]
      ],
      "valid_effect_state_result":valid,
      "succeeded_effect_state_result":succeeded,
    }
    out={
      "schema":"r8-v15-r1-stage2-sg1-harness-result/v1",
      "status":"PASS",
      "order":args.order,
      "candidate":CANDIDATE,
      "candidate_tree":TREE,
      "case_count":len(cases),
      "cases":cases,
      "semantic_fingerprint":fingerprint,
      "external_effects_performed":False,
      "candidate_modified":False,
      "authority_effect":"NONE",
      "stage2_scope":"DEPENDENCY_SEMANTIC_CONFORMANCE_SG1_ONLY",
      "stage2_broader_authority":False,
    }
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
