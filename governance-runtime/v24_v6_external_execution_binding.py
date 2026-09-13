"""R11 construction support for externally governed qualification execution.

This module validates an external execution pinset against exact local bytes. It
is not itself an authority source: authoritative pinsets and trusted runners
must originate outside the candidate tree/branch. The module is construction
evidence only and cannot grant qualification or open scientific execution.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
SCIENTIFIC_EXECUTION_STATE = "CLOSED_PENDING_SUCCESSOR_REVIEW"
EXTERNAL_AUTHORITY_ORIGIN = "EXTERNAL_REVIEW_BRANCH"
ALLOWED_ROLES = frozenset({"production", "test", "dependency", "support"})
PYTHON_ROLES = frozenset({"production", "test", "dependency"})
FORBIDDEN_BOOTSTRAP_NAMES = frozenset({
    "unittest.py",
    "sitecustomize.py",
    "usercustomize.py",
})


def _git_sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _safe_path(v: Any) -> str | None:
    if not isinstance(v, str) or not v:
        return None
    p = PurePosixPath(v)
    if p.is_absolute() or ".." in p.parts or any(x in {"", "."} for x in p.parts):
        return None
    return p.as_posix()


def _valid_role_path(path: str, role: Any) -> bool:
    if role in PYTHON_ROLES:
        return path.startswith("governance-runtime/") and path.endswith(".py")
    if role == "support":
        return path.startswith("implementation/v24/") and not path.endswith(".py")
    return False


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bound_file(root: Path, repo_path: str) -> tuple[bytes | None, str | None]:
    try:
        base = root.resolve()
        unresolved = base / repo_path
        if unresolved.is_symlink():
            return None, "EXTERNAL_PINSET_SYMLINK_REJECTED"
        target = unresolved.resolve(strict=True)
        target.relative_to(base)
        if not target.is_file():
            return None, "EXTERNAL_PINSET_BOUND_PATH_NOT_FILE"
        return target.read_bytes(), None
    except Exception:
        return None, "EXTERNAL_PINSET_BOUND_FILE_MISSING_OR_ESCAPE"


def _shadow_problem(path: str) -> str | None:
    p = PurePosixPath(path)
    if p.suffix != ".py":
        return None
    name = p.name
    stem = p.stem
    if name in FORBIDDEN_BOOTSTRAP_NAMES:
        return f"EXTERNAL_PINSET_BOOTSTRAP_SHADOW_REJECTED:{path}"
    if stem in sys.stdlib_module_names:
        return f"EXTERNAL_PINSET_STDLIB_SHADOW_REJECTED:{path}"
    return None


def validate_external_execution_pinset(
    *,
    repo_root: str | Path,
    pinset: Mapping[str, Any],
    expected_candidate_commit: str | None = None,
    expected_candidate_tree: str | None = None,
) -> dict[str, Any]:
    """Validate externally supplied pinset against exact candidate bytes.

    This function never treats the pinset as self-authenticating. Callers must
    separately establish that the pinset came from an external authority path.
    """
    problems: list[str] = []
    root = Path(repo_root)

    if pinset.get("schema_version") != 1:
        problems.append("EXTERNAL_PINSET_SCHEMA_INVALID")
    if pinset.get("authority_origin") != EXTERNAL_AUTHORITY_ORIGIN:
        problems.append("EXTERNAL_PINSET_AUTHORITY_ORIGIN_INVALID")
    if pinset.get("candidate_self_grant") is not False:
        problems.append("EXTERNAL_PINSET_CANDIDATE_SELF_GRANT_FORBIDDEN")

    commit = pinset.get("candidate_commit")
    tree = pinset.get("candidate_tree")
    if not _git_sha(commit):
        problems.append("EXTERNAL_PINSET_CANDIDATE_COMMIT_INVALID")
    if not _git_sha(tree):
        problems.append("EXTERNAL_PINSET_CANDIDATE_TREE_INVALID")
    if expected_candidate_commit is not None and commit != expected_candidate_commit:
        problems.append("EXTERNAL_PINSET_CANDIDATE_COMMIT_MISMATCH")
    if expected_candidate_tree is not None and tree != expected_candidate_tree:
        problems.append("EXTERNAL_PINSET_CANDIDATE_TREE_MISMATCH")

    interpreter = pinset.get("interpreter_contract")
    if not isinstance(interpreter, Mapping):
        interpreter = {}
        problems.append("EXTERNAL_PINSET_INTERPRETER_CONTRACT_REQUIRED")
    for key in (
        "isolated_mode",
        "safe_path",
        "ignore_environment",
        "no_site",
        "trusted_runner_outside_candidate_tree",
        "candidate_path_absent_at_interpreter_startup",
    ):
        if interpreter.get(key) is not True:
            problems.append(f"EXTERNAL_PINSET_INTERPRETER_REQUIREMENT_MISSING:{key}")

    rows = pinset.get("admitted_files")
    if not isinstance(rows, list) or not rows:
        rows = []
        problems.append("EXTERNAL_PINSET_ADMITTED_FILES_REQUIRED")

    by_path: dict[str, Mapping[str, Any]] = {}
    bound: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            problems.append(f"EXTERNAL_PINSET_ROW_MALFORMED:{i}")
            continue
        path = _safe_path(row.get("path"))
        role = row.get("role")
        if path is None or not _valid_role_path(path, role):
            problems.append(f"EXTERNAL_PINSET_PATH_ROLE_INVALID:{i}")
            continue
        if path in by_path:
            problems.append(f"EXTERNAL_PINSET_DUPLICATE_PATH:{path}")
            continue
        by_path[path] = row
        if role not in ALLOWED_ROLES:
            problems.append(f"EXTERNAL_PINSET_ROLE_INVALID:{path}")
        shadow = _shadow_problem(path)
        if shadow:
            problems.append(shadow)
        if not _git_sha(row.get("git_blob_sha1")):
            problems.append(f"EXTERNAL_PINSET_GIT_BLOB_INVALID:{path}")
        if not _sha256(row.get("raw_sha256")):
            problems.append(f"EXTERNAL_PINSET_RAW_SHA256_INVALID:{path}")
        data, read_problem = _read_bound_file(root, path)
        if read_problem:
            problems.append(f"{read_problem}:{path}")
            continue
        assert data is not None
        actual_blob = git_blob_sha(data)
        actual_sha = raw_sha256(data)
        if row.get("git_blob_sha1") != actual_blob:
            problems.append(f"EXTERNAL_PINSET_GIT_BLOB_MISMATCH:{path}")
        if row.get("raw_sha256") != actual_sha:
            problems.append(f"EXTERNAL_PINSET_RAW_SHA256_MISMATCH:{path}")
        bound.append({
            "path": path,
            "role": role,
            "git_blob_sha1": actual_blob,
            "raw_sha256": actual_sha,
        })

    tests = pinset.get("executed_tests")
    if not isinstance(tests, list) or not tests:
        tests = []
        problems.append("EXTERNAL_PINSET_EXECUTED_TESTS_REQUIRED")
    seen_tests: set[str] = set()
    for raw in tests:
        path = _safe_path(raw)
        if path is None or not path.startswith("governance-runtime/") or not path.endswith(".py"):
            problems.append(f"EXTERNAL_PINSET_EXECUTED_TEST_PATH_INVALID:{raw}")
            continue
        if path in seen_tests:
            problems.append(f"EXTERNAL_PINSET_EXECUTED_TEST_DUPLICATE:{path}")
            continue
        seen_tests.add(path)
        row = by_path.get(path)
        if row is None:
            problems.append(f"EXTERNAL_PINSET_EXECUTED_TEST_UNPINNED:{path}")
        elif row.get("role") != "test":
            problems.append(f"EXTERNAL_PINSET_EXECUTED_TEST_ROLE_INVALID:{path}")

    required_support = pinset.get("required_support_files")
    if not isinstance(required_support, list) or not required_support:
        required_support = []
        problems.append("EXTERNAL_PINSET_REQUIRED_SUPPORT_FILES_REQUIRED")
    seen_support: set[str] = set()
    for raw in required_support:
        path = _safe_path(raw)
        if path is None:
            problems.append(f"EXTERNAL_PINSET_REQUIRED_SUPPORT_PATH_INVALID:{raw}")
            continue
        if path in seen_support:
            problems.append(f"EXTERNAL_PINSET_REQUIRED_SUPPORT_DUPLICATE:{path}")
            continue
        seen_support.add(path)
        row = by_path.get(path)
        if row is None:
            problems.append(f"EXTERNAL_PINSET_REQUIRED_SUPPORT_UNPINNED:{path}")
        elif row.get("role") != "support":
            problems.append(f"EXTERNAL_PINSET_REQUIRED_SUPPORT_ROLE_INVALID:{path}")

    problems = sorted(set(problems))
    return {
        "state": "EXTERNAL_EXECUTION_PINSET_VALID" if not problems else "EXTERNAL_EXECUTION_PINSET_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "bound_file_count": len(bound),
        "executed_test_count": len(seen_tests),
        "required_support_count": len(seen_support),
        "bound_files": sorted(bound, key=lambda x: x["path"]),
        "scientific_execution_state": SCIENTIFIC_EXECUTION_STATE,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_staged_execution_sandbox(*, sandbox_root: str | Path, pinset: Mapping[str, Any]) -> dict[str, Any]:
    """Require every staged file to equal the externally pinned admitted set."""
    root = Path(sandbox_root).resolve()
    admitted = pinset.get("admitted_files")
    expected: set[str] = set()
    if isinstance(admitted, list):
        for row in admitted:
            if isinstance(row, Mapping):
                path = _safe_path(row.get("path"))
                if path:
                    expected.add(path)

    actual: set[str] = set()
    symlinks: list[str] = []
    if root.exists():
        for path in root.rglob("*"):
            if path.is_symlink():
                symlinks.append(path.relative_to(root).as_posix())
            elif path.is_file():
                actual.add(path.relative_to(root).as_posix())

    problems: list[str] = []
    for path in sorted(expected - actual):
        problems.append(f"EXTERNAL_SANDBOX_PINNED_FILE_MISSING:{path}")
    for path in sorted(actual - expected):
        problems.append(f"EXTERNAL_SANDBOX_UNPINNED_FILE_PRESENT:{path}")
    for path in sorted(symlinks):
        problems.append(f"EXTERNAL_SANDBOX_SYMLINK_REJECTED:{path}")
    for path in sorted(actual):
        shadow = _shadow_problem(path)
        if shadow:
            problems.append(shadow)

    problems = sorted(set(problems))
    return {
        "state": "EXTERNAL_EXECUTION_SANDBOX_VALID" if not problems else "EXTERNAL_EXECUTION_SANDBOX_INVALID",
        "valid": not problems,
        "problems": problems,
        "expected_file_count": len(expected),
        "actual_file_count": len(actual),
        "scientific_execution_state": SCIENTIFIC_EXECUTION_STATE,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R11_EXTERNAL_EXECUTION_BINDING_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R11",
        "external_authority_required": True,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_STATE,
        "authority_effect": AUTHORITY_EFFECT,
    }
