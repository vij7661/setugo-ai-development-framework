"""Strict V16 Slice 2 construction-manifest validation.

This module rejects duplicate JSON keys, unknown schema fields, and predecessor
history substitution. It is construction evidence machinery only and never grants
implementation/runtime/scientific/effect authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
SLICE_ID = "V16-S2-CONTROL-DOMAIN-INDEPENDENCE"
SLICE1_FROZEN_COMMIT = "36f22a35ff57b6994d55c705c08686609276ddb3"
CURRENT_BASELINE_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-002"
HISTORICAL_BASELINE_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001"
HISTORICAL_BASELINE_BLOB = "27983a245408589ec39681aa69da3a003294ddd8"
IAR1_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR1-MANDATORY-TESTS-001"
IAR2_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR2-MANDATORY-TESTS-001"
IAR3_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR3-MANDATORY-TESTS-001"
CURRENT_IDS = (CURRENT_BASELINE_ID, IAR1_ID, IAR2_ID, IAR3_ID)
BASELINE_TEST_BLOB = "8ed790401280862796ea1f79eadb17f18cfe7ff8"
IAR3_TEST_BLOB = "7537c9517366bbff30c430306975da3b4caf6b96"

TEST_FIELDS = frozenset({"mandatory", "python_test_id", "requirement_test_id"})
BASELINE_V2_FIELDS = frozenset({
    "schema_version", "manifest_id", "slice_id", "semantic_revision",
    "supersedes_manifest_id", "supersedes_manifest_git_blob_sha",
    "test_source_git_blob_sha", "semantic_change_reason", "slice1_frozen_commit",
    "authority_effect", "implementation_qualification", "runtime_qualification", "tests",
})
HISTORICAL_BASELINE_FIELDS = frozenset({
    "authority_effect", "implementation_qualification", "manifest_id",
    "runtime_qualification", "schema_version", "slice_id", "slice1_frozen_commit", "tests",
})
IAR12_FIELDS = frozenset({
    "authority_effect", "implementation_qualification", "manifest_id",
    "runtime_qualification", "schema_version", "slice_id", "slice1_frozen_commit",
    "predecessor_slice2_candidate", "tests",
})
IAR3_FIELDS = IAR12_FIELDS | {"test_source_git_blob_sha"}
INDEX_FIELDS = frozenset({
    "schema_version", "slice_id", "current_baseline_manifest_id", "current_manifest_ids",
    "historical_manifest_ids", "historical_manifest_git_blobs",
    "implementation_qualification", "runtime_qualification", "authority_effect",
})


class ManifestValidationError(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ManifestValidationError(f"DUPLICATE_JSON_KEY:{key}")
        out[key] = value
    return out


def loads_strict_json(text: str, label: str = "json") -> Any:
    if not isinstance(text, str):
        raise ManifestValidationError(f"{label}:TEXT_REQUIRED")
    try:
        return json.loads(text, object_pairs_hook=_pairs_no_duplicates)
    except ManifestValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ManifestValidationError(f"{label}:JSON_INVALID:{exc.msg}") from exc


def load_strict_json(path: Path) -> Any:
    return loads_strict_json(path.read_text(encoding="utf-8"), str(path))


def git_blob_sha_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha_path(path: Path) -> str:
    return git_blob_sha_bytes(path.read_bytes())


def _exact_fields(obj: Any, expected: frozenset[str], label: str, problems: list[str]) -> None:
    if type(obj) is not dict:
        problems.append(f"{label}:OBJECT_REQUIRED")
        return
    actual = set(obj.keys())
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            problems.append(f"{label}:FIELDS_MISSING:{','.join(missing)}")
        if extra:
            problems.append(f"{label}:FIELDS_UNKNOWN:{','.join(extra)}")


def _required_string(obj: dict[str, Any], field: str, label: str, problems: list[str]) -> None:
    if not isinstance(obj.get(field), str) or not obj[field]:
        problems.append(f"{label}:{field}:NONEMPTY_STRING_REQUIRED")


def _validate_tests(obj: dict[str, Any], label: str, problems: list[str]) -> None:
    tests = obj.get("tests")
    if type(tests) is not list or not tests:
        problems.append(f"{label}:TESTS_REQUIRED")
        return
    for i, row in enumerate(tests):
        row_label = f"{label}:TEST[{i}]"
        _exact_fields(row, TEST_FIELDS, row_label, problems)
        if type(row) is not dict:
            continue
        if row.get("mandatory") is not True:
            problems.append(f"{row_label}:MANDATORY_TRUE_REQUIRED")
        _required_string(row, "python_test_id", row_label, problems)
        _required_string(row, "requirement_test_id", row_label, problems)


def validate_manifest_schema(obj: Any, schema_name: str) -> list[str]:
    problems: list[str] = []
    schemas = {
        "baseline_v2": BASELINE_V2_FIELDS,
        "historical_baseline": HISTORICAL_BASELINE_FIELDS,
        "iar1": IAR12_FIELDS,
        "iar2": IAR12_FIELDS,
        "iar3": IAR3_FIELDS,
        "index": INDEX_FIELDS,
    }
    expected = schemas.get(schema_name)
    if expected is None:
        return [f"UNKNOWN_SCHEMA:{schema_name}"]
    _exact_fields(obj, expected, schema_name, problems)
    if type(obj) is not dict:
        return problems
    if type(obj.get("schema_version")) is not int or obj.get("schema_version") != 1:
        problems.append(f"{schema_name}:SCHEMA_VERSION_INVALID")
    if obj.get("slice_id") != SLICE_ID:
        problems.append(f"{schema_name}:SLICE_ID_MISMATCH")
    if schema_name != "index":
        if obj.get("slice1_frozen_commit") != SLICE1_FROZEN_COMMIT:
            problems.append(f"{schema_name}:SLICE1_FROZEN_COMMIT_MISMATCH")
        _validate_tests(obj, schema_name, problems)
    if obj.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append(f"{schema_name}:AUTHORITY_EFFECT_INVALID")
    if obj.get("implementation_qualification") != "NOT_CLAIMED":
        problems.append(f"{schema_name}:IMPLEMENTATION_QUALIFICATION_INVALID")
    if obj.get("runtime_qualification") != "NOT_CLAIMED":
        problems.append(f"{schema_name}:RUNTIME_QUALIFICATION_INVALID")
    return sorted(set(problems))


def validate_predecessor_binding(
    baseline: dict[str, Any], index: dict[str, Any], historical_bytes: bytes,
) -> list[str]:
    problems: list[str] = []
    try:
        historical = loads_strict_json(historical_bytes.decode("utf-8"), "historical_baseline")
    except (UnicodeDecodeError, ManifestValidationError) as exc:
        return [f"HISTORICAL_BASELINE_LOAD:{exc}"]
    problems.extend(validate_manifest_schema(historical, "historical_baseline"))
    if type(historical) is dict and historical.get("manifest_id") != HISTORICAL_BASELINE_ID:
        problems.append("HISTORICAL_BASELINE_ID_MISMATCH")
    actual_blob = git_blob_sha_bytes(historical_bytes)
    if actual_blob != HISTORICAL_BASELINE_BLOB:
        problems.append("HISTORICAL_BASELINE_BLOB_MISMATCH")
    if baseline.get("supersedes_manifest_id") != HISTORICAL_BASELINE_ID:
        problems.append("BASELINE_PREDECESSOR_ID_MISMATCH")
    if baseline.get("supersedes_manifest_git_blob_sha") != HISTORICAL_BASELINE_BLOB:
        problems.append("BASELINE_PREDECESSOR_BLOB_BINDING_MISMATCH")
    historical_ids = index.get("historical_manifest_ids")
    if historical_ids != [HISTORICAL_BASELINE_ID]:
        problems.append("INDEX_HISTORICAL_IDS_MISMATCH")
    historical_blobs = index.get("historical_manifest_git_blobs")
    if type(historical_blobs) is not dict or historical_blobs != {HISTORICAL_BASELINE_ID: HISTORICAL_BASELINE_BLOB}:
        problems.append("INDEX_HISTORICAL_BLOB_BINDING_MISMATCH")
    return sorted(set(problems))


def _require_manifest_identity(obj: dict[str, Any], expected_id: str, label: str, problems: list[str]) -> None:
    if obj.get("manifest_id") != expected_id:
        problems.append(f"{label}:MANIFEST_ID_MISMATCH")


def _unique(values: Iterable[str]) -> bool:
    rows = list(values)
    return len(rows) == len(set(rows))


def validate_current_manifest_set(root: Path) -> dict[str, Any]:
    problems: list[str] = []
    paths = {
        "baseline_v2": root / "review-safe-evidence-v16-slice2-test-manifest-v2.json",
        "iar1": root / "review-safe-evidence-v16-slice2-test-manifest-iar1.json",
        "iar2": root / "review-safe-evidence-v16-slice2-test-manifest-iar2.json",
        "iar3": root / "review-safe-evidence-v16-slice2-test-manifest-iar3.json",
        "index": root / "review-safe-evidence-v16-slice2-current-manifests.json",
    }
    loaded: dict[str, dict[str, Any]] = {}
    for label, path in paths.items():
        try:
            obj = load_strict_json(path)
        except (OSError, ManifestValidationError) as exc:
            problems.append(f"{label}:LOAD_FAILED:{exc}")
            continue
        if type(obj) is not dict:
            problems.append(f"{label}:OBJECT_REQUIRED")
            continue
        loaded[label] = obj
        problems.extend(validate_manifest_schema(obj, label))
    if set(loaded) != set(paths):
        return {"valid": False, "problems": sorted(set(problems)), "authority_effect": AUTHORITY_EFFECT}

    baseline = loaded["baseline_v2"]
    iar1 = loaded["iar1"]
    iar2 = loaded["iar2"]
    iar3 = loaded["iar3"]
    index = loaded["index"]
    for obj, expected, label in (
        (baseline, CURRENT_BASELINE_ID, "baseline_v2"),
        (iar1, IAR1_ID, "iar1"),
        (iar2, IAR2_ID, "iar2"),
        (iar3, IAR3_ID, "iar3"),
    ):
        _require_manifest_identity(obj, expected, label, problems)

    if baseline.get("semantic_revision") != 2 or type(baseline.get("semantic_revision")) is not int:
        problems.append("BASELINE_SEMANTIC_REVISION_INVALID")
    if baseline.get("test_source_git_blob_sha") != BASELINE_TEST_BLOB:
        problems.append("BASELINE_TEST_SOURCE_BINDING_INVALID")
    if iar3.get("test_source_git_blob_sha") != IAR3_TEST_BLOB:
        problems.append("IAR3_TEST_SOURCE_BINDING_INVALID")
    if git_blob_sha_path(root / "test_review_safe_evidence_v16_independence.py") != BASELINE_TEST_BLOB:
        problems.append("BASELINE_TEST_SOURCE_BLOB_MISMATCH")
    if git_blob_sha_path(root / "test_review_safe_evidence_v16_independence_iar3.py") != IAR3_TEST_BLOB:
        problems.append("IAR3_TEST_SOURCE_BLOB_MISMATCH")

    historical_path = root / "review-safe-evidence-v16-slice2-test-manifest.json"
    try:
        historical_bytes = historical_path.read_bytes()
    except OSError as exc:
        problems.append(f"HISTORICAL_BASELINE_READ_FAILED:{exc}")
    else:
        problems.extend(validate_predecessor_binding(baseline, index, historical_bytes))

    if index.get("current_baseline_manifest_id") != CURRENT_BASELINE_ID:
        problems.append("INDEX_CURRENT_BASELINE_ID_MISMATCH")
    if index.get("current_manifest_ids") != list(CURRENT_IDS):
        problems.append("INDEX_CURRENT_MANIFEST_IDS_MISMATCH")
    if HISTORICAL_BASELINE_ID in index.get("current_manifest_ids", []):
        problems.append("HISTORICAL_BASELINE_MARKED_CURRENT")

    manifests = [baseline, iar1, iar2, iar3]
    rows = [row for manifest in manifests for row in manifest.get("tests", []) if type(row) is dict]
    requirement_ids = [row.get("requirement_test_id") for row in rows]
    python_ids = [row.get("python_test_id") for row in rows]
    if len(rows) != 61:
        problems.append(f"CURRENT_TEST_COUNT_MISMATCH:{len(rows)}")
    if not _unique([x for x in requirement_ids if isinstance(x, str)]) or len(requirement_ids) != len([x for x in requirement_ids if isinstance(x, str)]):
        problems.append("CURRENT_REQUIREMENT_IDS_NOT_UNIQUE_STRINGS")
    if not _unique([x for x in python_ids if isinstance(x, str)]) or len(python_ids) != len([x for x in python_ids if isinstance(x, str)]):
        problems.append("CURRENT_PYTHON_TEST_IDS_NOT_UNIQUE_STRINGS")

    valid = not problems
    return {
        "valid": valid,
        "problems": sorted(set(problems)),
        "current_manifest_ids": list(CURRENT_IDS),
        "historical_manifest_id": HISTORICAL_BASELINE_ID,
        "historical_manifest_git_blob_sha": HISTORICAL_BASELINE_BLOB,
        "test_count": len(rows),
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
