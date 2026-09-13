from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

FORBIDDEN = frozenset({"unittest.py", "sitecustomize.py", "usercustomize.py"})
PY_SCOPE = PurePosixPath("governance-runtime")
SUPPORT = (
    "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json",
    "implementation/v24/V24-I11-V6-R1-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R2-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R3-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R4-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R5-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R6-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R7-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R8-CONSTRUCTION-EVIDENCE.md",
    "implementation/v24/V24-I11-V6-R11-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R12-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R13-EXECUTION-CONTRACT.json",
)
EXECUTED_TESTS = (
    "governance-runtime/test_v24_v6_external_execution_binding.py",
    "governance-runtime/test_v24_v6_governance_foundation.py",
    "governance-runtime/test_v24_v6_endpoint_projection.py",
    "governance-runtime/test_v24_v6_material_surface.py",
    "governance-runtime/test_v24_v6_decision_apply.py",
    "governance-runtime/test_v24_v6_normative_clause_projection.py",
    "governance-runtime/test_v24_v6_effect_ledger_closure.py",
    "governance-runtime/test_v24_v6_atomic_binding_modes.py",
    "governance-runtime/test_v24_v6_qualification_integrity.py",
    "governance-runtime/test_v24_v6_integrated_successor.py",
    "governance-runtime/test_v24_v6_r12_successor.py",
    "governance-runtime/test_v24_v6_r13_successor.py",
    "governance-runtime/test_normative_control_catalog.py",
    "governance-runtime/test_v24_authority_universe.py",
    "governance-runtime/test_v24_effective_control.py",
    "governance-runtime/test_v24_completeness_bootstrap.py",
    "governance-runtime/test_v24_endpoint_proof_compiler.py",
    "governance-runtime/test_v24_admission_application_witness.py",
    "governance-runtime/test_v24_aggregate_budget.py",
    "governance-runtime/test_v24_generation_migration.py",
    "governance-runtime/test_v24_review_proof_audit.py",
)
EXPECTED_ADMITTED_FILES = 75


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def actual_interpreter_contract() -> dict[str, object]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
        "optimize": int(sys.flags.optimize),
    }
    for key in ("isolated", "no_site", "ignore_environment", "safe_path"):
        if flags[key] is not True:
            raise SystemExit(f"R13_GUARD_FLAG_NOT_TRUE:{key}")
    if flags["optimize"] != 0:
        raise SystemExit(f"R13_GUARD_OPTIMIZATION_FORBIDDEN:{flags['optimize']}")
    executable = Path(sys.executable).resolve()
    if not executable.is_file():
        raise SystemExit("R13_GUARD_INTERPRETER_MISSING")
    contract = {
        "flags": flags,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro, sys.version_info.releaselevel, sys.version_info.serial],
        "hexversion": sys.hexversion,
        "executable_sha256": raw_sha256(executable.read_bytes()),
        "stdlib_module_names_digest": canonical_digest(sorted(sys.stdlib_module_names)),
        "candidate_path_absent_at_interpreter_startup": True,
        "trusted_guard_outside_candidate_tree": True,
    }
    contract["contract_digest"] = canonical_digest(contract)
    return contract


def safe_rel(path: str) -> str:
    p = PurePosixPath(path)
    if p.is_absolute() or not path or ".." in p.parts or any(x in {"", "."} for x in p.parts):
        raise SystemExit(f"R13_GUARD_UNSAFE_PATH:{path}")
    return p.as_posix()


def checked_file(root: Path, rel: str, role: str) -> dict[str, str]:
    rel = safe_rel(rel)
    p = root / rel
    if p.is_symlink():
        raise SystemExit(f"R13_GUARD_SYMLINK_REJECTED:{rel}")
    if not p.is_file():
        raise SystemExit(f"R13_GUARD_REQUIRED_FILE_MISSING:{rel}")
    if p.suffix == ".py":
        if p.name in FORBIDDEN:
            raise SystemExit(f"R13_GUARD_BOOTSTRAP_SHADOW_REJECTED:{rel}")
        if p.stem in sys.stdlib_module_names:
            raise SystemExit(f"R13_GUARD_STDLIB_SHADOW_REJECTED:{rel}")
    data = p.read_bytes()
    return {"path": rel, "git_blob_sha1": git_blob_sha(data), "raw_sha256": raw_sha256(data), "role": role}


def source_rows(root: Path) -> list[dict[str, str]]:
    scope = root / PY_SCOPE.as_posix()
    if not scope.is_dir():
        raise SystemExit("R13_GUARD_SCOPE_MISSING")
    rows: list[dict[str, str]] = []
    for p in sorted(scope.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        rows.append(checked_file(root, rel, "test" if p.name.startswith("test_") else "dependency"))
    for rel in SUPPORT:
        rows.append(checked_file(root, rel, "support"))
    rows.sort(key=lambda x: x["path"])
    if len(rows) != EXPECTED_ADMITTED_FILES:
        raise SystemExit(f"R13_GUARD_ADMITTED_FILE_COUNT:expected={EXPECTED_ADMITTED_FILES}:actual={len(rows)}")
    return rows


def load_pinset(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != 3:
        raise SystemExit("R13_GUARD_PINSET_SCHEMA_INVALID")
    if obj.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH" or obj.get("candidate_self_grant") is not False:
        raise SystemExit("R13_GUARD_AUTHORITY_INVALID")
    if obj.get("interpreter_contract") != actual_interpreter_contract():
        raise SystemExit("R13_GUARD_INTERPRETER_CONTRACT_MISMATCH")
    return obj


def assert_identity(obj: dict, commit: str, tree: str) -> None:
    if obj.get("candidate_commit") != commit or obj.get("candidate_tree") != tree:
        raise SystemExit("R13_GUARD_CANDIDATE_IDENTITY_MISMATCH")
    if tuple(obj.get("executed_tests", ())) != EXECUTED_TESTS:
        raise SystemExit("R13_GUARD_EXECUTED_TEST_SET_MISMATCH")
    if tuple(obj.get("required_support_files", ())) != SUPPORT:
        raise SystemExit("R13_GUARD_SUPPORT_SET_MISMATCH")


def build_pinset(args: argparse.Namespace) -> None:
    runtime = actual_interpreter_contract()
    rows = source_rows(Path(args.root).resolve())
    by_path = {x["path"]: x for x in rows}
    for path in EXECUTED_TESTS:
        if by_path.get(path, {}).get("role") != "test":
            raise SystemExit(f"R13_GUARD_TEST_NOT_PINNED:{path}")
    for path in SUPPORT:
        if by_path.get(path, {}).get("role") != "support":
            raise SystemExit(f"R13_GUARD_SUPPORT_NOT_PINNED:{path}")
    obj = {
        "schema_version": 3,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": args.commit,
        "candidate_tree": args.tree,
        "review_branch_commit": args.review_commit,
        "interpreter_contract": runtime,
        "admitted_files": rows,
        "executed_tests": list(EXECUTED_TESTS),
        "required_support_files": list(SUPPORT),
        "candidate_side_unittest_role": "NON_AUTHORITATIVE_DIAGNOSTIC_ONLY",
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    out = Path(args.output)
    out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"R13_PINSET_FILES={len(rows)}")
    print(f"R13_PINSET_SHA256={raw_sha256(out.read_bytes())}")
    print(f"R13_INTERPRETER_CONTRACT_DIGEST={runtime['contract_digest']}")


def verify_source(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve(); obj = load_pinset(Path(args.pinset)); assert_identity(obj, args.commit, args.tree)
    actual = source_rows(root); expected = obj.get("admitted_files")
    if actual != expected:
        amap = {x["path"]: x for x in actual}; emap = {x["path"]: x for x in expected or []}
        if set(amap) != set(emap):
            raise SystemExit(f"R13_GUARD_SOURCE_FILESET_MISMATCH:missing={sorted(set(emap)-set(amap))}:extra={sorted(set(amap)-set(emap))}")
        for path in sorted(amap):
            if amap[path] != emap[path]:
                raise SystemExit(f"R13_GUARD_SOURCE_BINDING_MISMATCH:{path}")
        raise SystemExit("R13_GUARD_SOURCE_MISMATCH")
    print(f"R13_SOURCE_BINDING_PASS files={len(actual)}")


def stage(args: argparse.Namespace) -> None:
    source = Path(args.root).resolve(); target = Path(args.target).resolve(); obj = load_pinset(Path(args.pinset)); assert_identity(obj, args.commit, args.tree)
    if target.exists():
        raise SystemExit("R13_GUARD_STAGE_TARGET_EXISTS")
    target.mkdir(parents=True, exist_ok=False)
    for row in obj["admitted_files"]:
        rel = row["path"]
        if checked_file(source, rel, row["role"]) != row:
            raise SystemExit(f"R13_GUARD_SOURCE_CHANGED_BEFORE_STAGE:{rel}")
        dst = target / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source / rel, dst)
    print("R13_STAGE_PASS")


def sandbox_rows(root: Path) -> list[dict[str, str]]:
    rows=[]
    for p in root.rglob("*"):
        if p.is_symlink():
            raise SystemExit(f"R13_GUARD_SANDBOX_SYMLINK_REJECTED:{p.relative_to(root).as_posix()}")
        if not p.is_file():
            continue
        rel=p.relative_to(root).as_posix()
        if p.suffix==".py":
            if p.name in FORBIDDEN: raise SystemExit(f"R13_GUARD_BOOTSTRAP_SHADOW_REJECTED:{rel}")
            if p.stem in sys.stdlib_module_names: raise SystemExit(f"R13_GUARD_STDLIB_SHADOW_REJECTED:{rel}")
        data=p.read_bytes(); rows.append({"path":rel,"git_blob_sha1":git_blob_sha(data),"raw_sha256":raw_sha256(data)})
    return sorted(rows,key=lambda x:x["path"])


def verify_sandbox(args: argparse.Namespace) -> None:
    root=Path(args.root).resolve(); obj=load_pinset(Path(args.pinset)); assert_identity(obj,args.commit,args.tree)
    expected={x["path"]:{"path":x["path"],"git_blob_sha1":x["git_blob_sha1"],"raw_sha256":x["raw_sha256"]} for x in obj["admitted_files"]}
    actual={x["path"]:x for x in sandbox_rows(root)}
    if set(actual)!=set(expected):
        raise SystemExit(f"R13_GUARD_SANDBOX_FILESET_MISMATCH:missing={sorted(set(expected)-set(actual))}:extra={sorted(set(actual)-set(expected))}")
    for path in sorted(expected):
        if actual[path]!=expected[path]: raise SystemExit(f"R13_GUARD_SANDBOX_BINDING_MISMATCH:{path}")
    print(f"R13_SANDBOX_BINDING_PASS files={len(actual)}")


def main() -> None:
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="command",required=True)
    p=sp.add_parser("build-pinset"); p.add_argument("--root",required=True); p.add_argument("--commit",required=True); p.add_argument("--tree",required=True); p.add_argument("--review-commit",required=True); p.add_argument("--output",required=True); p.set_defaults(fn=build_pinset)
    for cmd,fn in (("verify-source",verify_source),("stage",stage),("verify-sandbox",verify_sandbox)):
        p=sp.add_parser(cmd); p.add_argument("--root",required=True); p.add_argument("--pinset",required=True); p.add_argument("--commit",required=True); p.add_argument("--tree",required=True)
        if cmd=="stage": p.add_argument("--target",required=True)
        p.set_defaults(fn=fn)
    args=ap.parse_args(); args.fn(args)


if __name__=="__main__": main()
