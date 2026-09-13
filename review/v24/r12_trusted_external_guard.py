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
EXPECTED_ADMITTED_FILES = 72


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


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
            raise SystemExit(f"R12_GUARD_ACTUAL_INTERPRETER_FLAG_NOT_TRUE:{key}")
    executable = Path(sys.executable).resolve()
    if not executable.is_file():
        raise SystemExit("R12_GUARD_INTERPRETER_EXECUTABLE_MISSING")
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


def safe_rel(path: str) -> str:
    p = PurePosixPath(path)
    if p.is_absolute() or not path or ".." in p.parts or any(x in {"", "."} for x in p.parts):
        raise SystemExit(f"R12_GUARD_UNSAFE_PATH:{path}")
    return p.as_posix()


def checked_file(root: Path, rel: str, role: str) -> dict[str, str]:
    rel = safe_rel(rel)
    p = root / rel
    if p.is_symlink():
        raise SystemExit(f"R12_GUARD_SYMLINK_REJECTED:{rel}")
    if not p.is_file():
        raise SystemExit(f"R12_GUARD_REQUIRED_FILE_MISSING:{rel}")
    if p.suffix == ".py":
        if p.name in FORBIDDEN:
            raise SystemExit(f"R12_GUARD_BOOTSTRAP_SHADOW_REJECTED:{rel}")
        if p.stem in sys.stdlib_module_names:
            raise SystemExit(f"R12_GUARD_STDLIB_SHADOW_REJECTED:{rel}")
    data = p.read_bytes()
    return {
        "path": rel,
        "git_blob_sha1": git_blob_sha(data),
        "raw_sha256": raw_sha256(data),
        "role": role,
    }


def source_rows(root: Path) -> list[dict[str, str]]:
    scope = root / PY_SCOPE.as_posix()
    if not scope.is_dir():
        raise SystemExit("R12_GUARD_SCOPE_MISSING:governance-runtime")
    rows: list[dict[str, str]] = []
    for p in sorted(scope.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        role = "test" if p.name.startswith("test_") else "dependency"
        rows.append(checked_file(root, rel, role))
    for rel in SUPPORT:
        rows.append(checked_file(root, rel, "support"))
    rows.sort(key=lambda r: r["path"])
    if len(rows) != EXPECTED_ADMITTED_FILES:
        raise SystemExit(f"R12_GUARD_EXPECTED_{EXPECTED_ADMITTED_FILES}_ADMITTED_FILES:actual={len(rows)}")
    return rows


def load_pinset(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != 2:
        raise SystemExit("R12_GUARD_PINSET_SCHEMA_INVALID")
    if obj.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH":
        raise SystemExit("R12_GUARD_PINSET_AUTHORITY_INVALID")
    if obj.get("candidate_self_grant") is not False:
        raise SystemExit("R12_GUARD_PINSET_SELF_GRANT_FORBIDDEN")
    actual = actual_interpreter_contract()
    if obj.get("interpreter_contract") != actual:
        raise SystemExit("R12_GUARD_ACTUAL_INTERPRETER_CONTRACT_MISMATCH")
    return obj


def assert_pinset_identity(pinset: dict, commit: str, tree: str) -> None:
    if pinset.get("candidate_commit") != commit:
        raise SystemExit("R12_GUARD_CANDIDATE_COMMIT_MISMATCH")
    if pinset.get("candidate_tree") != tree:
        raise SystemExit("R12_GUARD_CANDIDATE_TREE_MISMATCH")
    if tuple(pinset.get("executed_tests", ())) != EXECUTED_TESTS:
        raise SystemExit("R12_GUARD_EXECUTED_TEST_SET_MISMATCH")
    if tuple(pinset.get("required_support_files", ())) != SUPPORT:
        raise SystemExit("R12_GUARD_SUPPORT_SET_MISMATCH")


def build_pinset(args: argparse.Namespace) -> None:
    runtime = actual_interpreter_contract()
    root = Path(args.root).resolve()
    rows = source_rows(root)
    by_path = {r["path"]: r for r in rows}
    for path in EXECUTED_TESTS:
        row = by_path.get(path)
        if row is None or row["role"] != "test":
            raise SystemExit(f"R12_GUARD_EXECUTED_TEST_NOT_PINNED_AS_TEST:{path}")
    for path in SUPPORT:
        row = by_path.get(path)
        if row is None or row["role"] != "support":
            raise SystemExit(f"R12_GUARD_SUPPORT_NOT_PINNED_AS_SUPPORT:{path}")
    obj = {
        "schema_version": 2,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": args.commit,
        "candidate_tree": args.tree,
        "review_branch_commit": args.review_commit,
        "interpreter_contract": runtime,
        "admitted_files": rows,
        "executed_tests": list(EXECUTED_TESTS),
        "required_support_files": list(SUPPORT),
        "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }
    out = Path(args.output)
    out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"R12_EXTERNAL_PINSET_FILES={len(rows)}")
    print(f"R12_INTERPRETER_CONTRACT_DIGEST={runtime['contract_digest']}")
    print(f"R12_EXTERNAL_PINSET_SHA256={raw_sha256(out.read_bytes())}")


def verify_source(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    pinset = load_pinset(Path(args.pinset))
    assert_pinset_identity(pinset, args.commit, args.tree)
    actual = source_rows(root)
    expected = pinset.get("admitted_files")
    if actual != expected:
        a = {r["path"]: r for r in actual}
        e = {r["path"]: r for r in expected or []}
        if set(a) != set(e):
            raise SystemExit(f"R12_GUARD_SOURCE_FILESET_MISMATCH:missing={sorted(set(e)-set(a))}:extra={sorted(set(a)-set(e))}")
        for path in sorted(a):
            if a[path] != e[path]:
                raise SystemExit(f"R12_GUARD_SOURCE_BINDING_MISMATCH:{path}")
        raise SystemExit("R12_GUARD_SOURCE_PINSET_MISMATCH")
    print(f"R12_EXTERNAL_SOURCE_BINDING_PASS files={len(actual)}")


def stage(args: argparse.Namespace) -> None:
    source = Path(args.root).resolve()
    target = Path(args.target).resolve()
    pinset = load_pinset(Path(args.pinset))
    assert_pinset_identity(pinset, args.commit, args.tree)
    if target.exists():
        raise SystemExit("R12_GUARD_STAGE_TARGET_MUST_NOT_EXIST")
    target.mkdir(parents=True, exist_ok=False)
    for row in pinset["admitted_files"]:
        rel = row["path"]
        now = checked_file(source, rel, row["role"])
        if now != row:
            raise SystemExit(f"R12_GUARD_SOURCE_CHANGED_BEFORE_STAGE:{rel}")
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / rel, dst)
    print("R12_EXTERNAL_STAGE_PASS")


def sandbox_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in root.rglob("*"):
        if p.is_symlink():
            raise SystemExit(f"R12_GUARD_SANDBOX_SYMLINK_REJECTED:{p.relative_to(root).as_posix()}")
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if p.suffix == ".py":
                if p.name in FORBIDDEN:
                    raise SystemExit(f"R12_GUARD_BOOTSTRAP_SHADOW_REJECTED:{rel}")
                if p.stem in sys.stdlib_module_names:
                    raise SystemExit(f"R12_GUARD_STDLIB_SHADOW_REJECTED:{rel}")
            data = p.read_bytes()
            rows.append({"path": rel, "git_blob_sha1": git_blob_sha(data), "raw_sha256": raw_sha256(data)})
    rows.sort(key=lambda r: r["path"])
    return rows


def verify_sandbox(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    pinset = load_pinset(Path(args.pinset))
    assert_pinset_identity(pinset, args.commit, args.tree)
    expected = {
        row["path"]: {"path": row["path"], "git_blob_sha1": row["git_blob_sha1"], "raw_sha256": row["raw_sha256"]}
        for row in pinset["admitted_files"]
    }
    actual = {r["path"]: r for r in sandbox_rows(root)}
    if set(actual) != set(expected):
        raise SystemExit(f"R12_GUARD_SANDBOX_FILESET_MISMATCH:missing={sorted(set(expected)-set(actual))}:extra={sorted(set(actual)-set(expected))}")
    for path in sorted(expected):
        if actual[path] != expected[path]:
            raise SystemExit(f"R12_GUARD_SANDBOX_BINDING_MISMATCH:{path}")
    print(f"R12_EXTERNAL_SANDBOX_BINDING_PASS files={len(actual)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="command", required=True)
    p = sp.add_parser("build-pinset")
    p.add_argument("--root", required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--tree", required=True)
    p.add_argument("--review-commit", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(fn=build_pinset)
    for cmd, fn in (("verify-source", verify_source), ("stage", stage), ("verify-sandbox", verify_sandbox)):
        p = sp.add_parser(cmd)
        p.add_argument("--root", required=True)
        p.add_argument("--pinset", required=True)
        p.add_argument("--commit", required=True)
        p.add_argument("--tree", required=True)
        if cmd == "stage":
            p.add_argument("--target", required=True)
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
