from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import pathlib
import sys
from typing import Any

PREFIX = "R13_OBSERVATION="

ALLOWED_CALLS = frozenset({
    ("v24_v6_governance_foundation", "validate_completeness_derivation_graph"),
    ("v24_v6_governance_foundation", "genesis_scope_match"),
    ("v24_v6_endpoint_projection", "compile_qualified_endpoint_table"),
    ("v24_v6_endpoint_projection", "derive_applicable_predicate_universe"),
    ("v24_v6_atomic_binding_modes", "validate_atomic_binding_mode_registry"),
    ("v24_v6_qualification_integrity", "compile_qualification_summary"),
})


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--request", required=True)
    args = ap.parse_args()

    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    if any(v is not True for v in flags.values()):
        raise SystemExit("R13_OBSERVER_INTERPRETER_NOT_ISOLATED")

    sandbox = pathlib.Path(args.sandbox).resolve()
    subject = sandbox / "governance-runtime"
    startup_path = list(sys.path)
    if "" in startup_path or str(subject) in startup_path or str(sandbox) in startup_path:
        raise SystemExit("R13_OBSERVER_CANDIDATE_PATH_PRESENT_AT_STARTUP")

    request_path = pathlib.Path(args.request).resolve()
    if request_path.is_relative_to(sandbox):
        raise SystemExit("R13_OBSERVER_REQUEST_INSIDE_CANDIDATE_SANDBOX")
    request = json.loads(request_path.read_text(encoding="utf-8"))
    module_name = request.get("module")
    function_name = request.get("function")
    if (module_name, function_name) not in ALLOWED_CALLS:
        raise SystemExit(f"R13_OBSERVER_CALL_NOT_ALLOWED:{module_name}:{function_name}")
    call_args = request.get("args", [])
    call_kwargs = request.get("kwargs", {})
    if not isinstance(call_args, list) or not isinstance(call_kwargs, dict):
        raise SystemExit("R13_OBSERVER_ARGUMENT_SHAPE_INVALID")

    sys.dont_write_bytecode = True
    os.chdir(sandbox)
    sys.path.insert(0, str(subject))

    outcome_kind = "RETURN"
    payload: Any
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, function_name)
        payload = fn(*call_args, **call_kwargs)
        # The observer only transports candidate behavior. It does not interpret
        # a returned field named qualified/pass/success as authority.
        canonical(payload)
    except BaseException as exc:
        outcome_kind = "EXCEPTION"
        payload = {
            "exception_module": type(exc).__module__,
            "exception_type": type(exc).__qualname__,
            "message": str(exc),
        }

    observation = {
        "schema_version": 1,
        "request_digest": digest(request),
        "module": module_name,
        "function": function_name,
        "outcome_kind": outcome_kind,
        "payload": payload,
        "candidate_process_role": "UNTRUSTED_OBSERVATION_ONLY",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    # This output is explicitly untrusted. The external oracle recomputes the
    # request digest and applies all PASS/FAIL assertions outside this process.
    os.write(1, (PREFIX + json.dumps(observation, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
