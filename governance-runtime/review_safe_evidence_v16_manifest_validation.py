"""Strict V16 Slice 2 construction-manifest validation.

Reject duplicate JSON keys, unknown schema fields, source-semantic drift, and
predecessor-history substitution. This is construction evidence machinery only; it
never grants implementation, runtime, scientific, promotion, or effect authority.
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

CURRENT_IAR1_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR1-MANDATORY-TESTS-002"
HISTORICAL_IAR1_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR1-MANDATORY-TESTS-001"
HISTORICAL_IAR1_BLOB = "a63d613298ba2514a3d11fb86fd2a67dc70c756b"
CURRENT_IAR2_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR2-MANDATORY-TESTS-002"
HISTORICAL_IAR2_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR2-MANDATORY-TESTS-001"
HISTORICAL_IAR2_BLOB = "d72f7c72b46c680e8d4f94b1d03bbb4e0765dc5c"

IAR3_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR3-MANDATORY-TESTS-001"
CURRENT_IAR4_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR4-MANDATORY-TESTS-002"
HISTORICAL_IAR4_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR4-MANDATORY-TESTS-001"
HISTORICAL_IAR4_BLOB = "beda2c0ca7c8cf54ecccbfe5b765bd3c2e3ef336"
IAR5_ID = "REVIEW-SAFE-EVIDENCE-V16-SLICE2-IAR5-MANDATORY-TESTS-001"

CURRENT_IDS = (
    CURRENT_BASELINE_ID,
    CURRENT_IAR1_ID,
    CURRENT_IAR2_ID,
    IAR3_ID,
    CURRENT_IAR4_ID,
    IAR5_ID,
)
HISTORICAL_IDS = (
    HISTORICAL_BASELINE_ID,
    HISTORICAL_IAR1_ID,
    HISTORICAL_IAR2_ID,
    HISTORICAL_IAR4_ID,
)
HISTORICAL_BLOBS = {
    HISTORICAL_BASELINE_ID: HISTORICAL_BASELINE_BLOB,
    HISTORICAL_IAR1_ID: HISTORICAL_IAR1_BLOB,
    HISTORICAL_IAR2_ID: HISTORICAL_IAR2_BLOB,
    HISTORICAL_IAR4_ID: HISTORICAL_IAR4_BLOB,
}

BASELINE_TEST_BLOB = "8ed790401280862796ea1f79eadb17f18cfe7ff8"
IAR1_TEST_BLOB = "f5f130543641d7675fe4eba9f52dca969d52d74e"
IAR2_TEST_BLOB = "d62eb7cde62805ace95b1dff6d27a08cdf295213"
IAR3_TEST_BLOB = "7537c9517366bbff30c430306975da3b4caf6b96"
IAR4_TEST_BLOB = "f421f46c2ce67feda3c851f3d85f890026d2b813"
HISTORICAL_IAR4_TEST_BLOB = "dcbfde5e548d500cbececed331956965cc10d5ff"
IAR5_TEST_BLOB = "99c560edbba1c1ac8518862e432df8032680cc16"

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
HISTORICAL_IAR_FIELDS = frozenset({
    "authority_effect", "implementation_qualification", "manifest_id",
    "runtime_qualification", "schema_version", "slice_id", "slice1_frozen_commit",
    "predecessor_slice2_candidate", "tests",
})
HISTORICAL_IAR_SOURCE_FIELDS = HISTORICAL_IAR_FIELDS | {"test_source_git_blob_sha"}
REVISIONED_IAR_FIELDS = HISTORICAL_IAR_FIELDS | {
    "semantic_revision", "supersedes_manifest_id", "supersedes_manifest_git_blob_sha",
    "test_source_git_blob_sha", "semantic_change_reason",
}
CURRENT_UNREVISIONED_IAR_FIELDS = HISTORICAL_IAR_SOURCE_FIELDS
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
        "current_iar1": REVISIONED_IAR_FIELDS,
        "current_iar2": REVISIONED_IAR_FIELDS,
        "iar3": CURRENT_UNREVISIONED_IAR_FIELDS,
        "current_iar4": REVISIONED_IAR_FIELDS,
        "iar5": CURRENT_UNREVISIONED_IAR_FIELDS,
        "historical_iar1": HISTORICAL_IAR_FIELDS,
        "historical_iar2": HISTORICAL_IAR_FIELDS,
        "historical_iar4": HISTORICAL_IAR_SOURCE_FIELDS,
        "index": INDEX_FIELDS,
    }
    expected = schemas.get(schema_name)
    if expected is None:
        return [f"UNKNOWN_SCHEMA:{schema_name}"]
    _exact_fields(obj, expected, schema_name, problems)
    if type(obj) is not dict:
        return sorted(set(problems))
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


def validate_historical_manifest_binding(
    current: dict[str, Any], index: dict[str, Any], historical_bytes: bytes, *,
    historical_schema_name: str, historical_id: str, historical_blob: str,
    code_prefix: str,
) -> list[str]:
    problems: list[str] = []
    try:
        historical = loads_strict_json(historical_bytes.decode("utf-8"), historical_schema_name)
    except (UnicodeDecodeError, ManifestValidationError) as exc:
        return [f"{code_prefix}_HISTORICAL_LOAD:{exc}"]
    problems.extend(validate_manifest_schema(historical, historical_schema_name))
    if type(historical) is dict and historical.get("manifest_id") != historical_id:
        problems.append(f"{code_prefix}_HISTORICAL_ID_MISMATCH")
    if git_blob_sha_bytes(historical_bytes) != historical_blob:
        problems.append(f"{code_prefix}_HISTORICAL_BLOB_MISMATCH")
    if current.get("supersedes_manifest_id") != historical_id:
        problems.append(f"{code_prefix}_PREDECESSOR_ID_MISMATCH")
    if current.get("supersedes_manifest_git_blob_sha") != historical_blob:
        problems.append(f"{code_prefix}_PREDECESSOR_BLOB_BINDING_MISMATCH")
    historical_ids = index.get("historical_manifest_ids")
    if type(historical_ids) is not list or historical_id not in historical_ids:
        problems.append(f"{code_prefix}_INDEX_HISTORICAL_ID_MISSING")
    historical_blobs = index.get("historical_manifest_git_blobs")
    if type(historical_blobs) is not dict or historical_blobs.get(historical_id) != historical_blob:
        problems.append(f"{code_prefix}_INDEX_HISTORICAL_BLOB_BINDING_MISMATCH")
    return sorted(set(problems))


def validate_predecessor_binding(
    baseline: dict[str, Any], index: dict[str, Any], historical_bytes: bytes,
) -> list[str]:
    """Compatibility wrapper preserving IAR4's historical baseline error vocabulary."""
    problems = validate_historical_manifest_binding(
        baseline, index, historical_bytes,
        historical_schema_name="historical_baseline",
        historical_id=HISTORICAL_BASELINE_ID,
        historical_blob=HISTORICAL_BASELINE_BLOB,
        code_prefix="BASELINE",
    )
    mapped: list[str] = []
    for problem in problems:
        if problem == "BASELINE_HISTORICAL_BLOB_MISMATCH":
            mapped.append("HISTORICAL_BASELINE_BLOB_MISMATCH")
        elif problem == "BASELINE_HISTORICAL_ID_MISMATCH":
            mapped.append("HISTORICAL_BASELINE_ID_MISMATCH")
        elif problem.startswith("BASELINE_HISTORICAL_LOAD:"):
            mapped.append("HISTORICAL_BASELINE_LOAD:" + problem.split(":", 1)[1])
        else:
            mapped.append(problem)
    return sorted(set(mapped))


def _require_manifest_identity(
    obj: dict[str, Any], expected_id: str, label: str, problems: list[str],
) -> None:
    if obj.get("manifest_id") != expected_id:
        problems.append(f"{label}:MANIFEST_ID_MISMATCH")


def _unique(values: Iterable[str]) -> bool:
    rows = list(values)
    return len(rows) == len(set(rows))


def _validate_revisioned_manifest(
    obj: dict[str, Any], *, label: str, expected_id: str, historical_id: str,
    historical_blob: str, test_blob: str, problems: list[str],
) -> None:
    _require_manifest_identity(obj, expected_id, label, problems)
    if type(obj.get("semantic_revision")) is not int or obj.get("semantic_revision") != 2:
        problems.append(f"{label.upper()}_SEMANTIC_REVISION_INVALID")
    if obj.get("supersedes_manifest_id") != historical_id:
        problems.append(f"{label.upper()}_PREDECESSOR_ID_MISMATCH")
    if obj.get("supersedes_manifest_git_blob_sha") != historical_blob:
        problems.append(f"{label.upper()}_PREDECESSOR_BLOB_BINDING_MISMATCH")
    if obj.get("test_source_git_blob_sha") != test_blob:
        problems.append(f"{label.upper()}_TEST_SOURCE_BINDING_INVALID")
    if not isinstance(obj.get("semantic_change_reason"), str) or not obj["semantic_change_reason"].strip():
        problems.append(f"{label.upper()}_SEMANTIC_CHANGE_REASON_REQUIRED")


def validate_current_manifest_set(root: Path) -> dict[str, Any]:
    problems: list[str] = []
    paths = {
        "baseline_v2": root / "review-safe-evidence-v16-slice2-test-manifest-v2.json",
        "current_iar1": root / "review-safe-evidence-v16-slice2-test-manifest-iar1-v2.json",
        "current_iar2": root / "review-safe-evidence-v16-slice2-test-manifest-iar2-v2.json",
        "iar3": root / "review-safe-evidence-v16-slice2-test-manifest-iar3.json",
        "current_iar4": root / "review-safe-evidence-v16-slice2-test-manifest-iar4-v2.json",
        "iar5": root / "review-safe-evidence-v16-slice2-test-manifest-iar5.json",
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
        return {
            "valid": False,
            "problems": sorted(set(problems)),
            "implementation_qualification": "NOT_CLAIMED",
            "runtime_qualification": "NOT_CLAIMED",
            "authority_effect": AUTHORITY_EFFECT,
        }

    baseline = loaded["baseline_v2"]
    iar1 = loaded["current_iar1"]
    iar2 = loaded["current_iar2"]
    iar3 = loaded["iar3"]
    iar4 = loaded["current_iar4"]
    iar5 = loaded["iar5"]
    index = loaded["index"]

    _require_manifest_identity(baseline, CURRENT_BASELINE_ID, "baseline_v2", problems)
    _validate_revisioned_manifest(
        iar1, label="iar1", expected_id=CURRENT_IAR1_ID,
        historical_id=HISTORICAL_IAR1_ID, historical_blob=HISTORICAL_IAR1_BLOB,
        test_blob=IAR1_TEST_BLOB, problems=problems,
    )
    _validate_revisioned_manifest(
        iar2, label="iar2", expected_id=CURRENT_IAR2_ID,
        historical_id=HISTORICAL_IAR2_ID, historical_blob=HISTORICAL_IAR2_BLOB,
        test_blob=IAR2_TEST_BLOB, problems=problems,
    )
    _require_manifest_identity(iar3, IAR3_ID, "iar3", problems)
    _validate_revisioned_manifest(
        iar4, label="iar4", expected_id=CURRENT_IAR4_ID,
        historical_id=HISTORICAL_IAR4_ID, historical_blob=HISTORICAL_IAR4_BLOB,
        test_blob=IAR4_TEST_BLOB, problems=problems,
    )
    _require_manifest_identity(iar5, IAR5_ID, "iar5", problems)

    if type(baseline.get("semantic_revision")) is not int or baseline.get("semantic_revision") != 2:
        problems.append("BASELINE_SEMANTIC_REVISION_INVALID")
    if baseline.get("test_source_git_blob_sha") != BASELINE_TEST_BLOB:
        problems.append("BASELINE_TEST_SOURCE_BINDING_INVALID")
    if iar3.get("test_source_git_blob_sha") != IAR3_TEST_BLOB:
        problems.append("IAR3_TEST_SOURCE_BINDING_INVALID")
    if iar5.get("test_source_git_blob_sha") != IAR5_TEST_BLOB:
        problems.append("IAR5_TEST_SOURCE_BINDING_INVALID")

    source_bindings = (
        ("BASELINE", root / "test_review_safe_evidence_v16_independence.py", BASELINE_TEST_BLOB),
        ("IAR1", root / "test_review_safe_evidence_v16_independence_v2.py", IAR1_TEST_BLOB),
        ("IAR2", root / "test_review_safe_evidence_v16_independence_iar2.py", IAR2_TEST_BLOB),
        ("IAR3", root / "test_review_safe_evidence_v16_independence_iar3.py", IAR3_TEST_BLOB),
        ("IAR4", root / "test_review_safe_evidence_v16_independence_iar4_v2.py", IAR4_TEST_BLOB),
        ("IAR5", root / "test_review_safe_evidence_v16_independence_iar5.py", IAR5_TEST_BLOB),
        ("HISTORICAL_IAR4", root / "test_review_safe_evidence_v16_independence_iar4.py", HISTORICAL_IAR4_TEST_BLOB),
    )
    for label, path, expected_blob in source_bindings:
        try:
            actual = git_blob_sha_path(path)
        except OSError as exc:
            problems.append(f"{label}_TEST_SOURCE_READ_FAILED:{exc}")
            continue
        if actual != expected_blob:
            problems.append(f"{label}_TEST_SOURCE_BLOB_MISMATCH")

    historical_specs = (
        (
            baseline, root / "review-safe-evidence-v16-slice2-test-manifest.json",
            "historical_baseline", HISTORICAL_BASELINE_ID, HISTORICAL_BASELINE_BLOB, "BASELINE",
        ),
        (
            iar1, root / "review-safe-evidence-v16-slice2-test-manifest-iar1.json",
            "historical_iar1", HISTORICAL_IAR1_ID, HISTORICAL_IAR1_BLOB, "IAR1",
        ),
        (
            iar2, root / "review-safe-evidence-v16-slice2-test-manifest-iar2.json",
            "historical_iar2", HISTORICAL_IAR2_ID, HISTORICAL_IAR2_BLOB, "IAR2",
        ),
        (
            iar4, root / "review-safe-evidence-v16-slice2-test-manifest-iar4.json",
            "historical_iar4", HISTORICAL_IAR4_ID, HISTORICAL_IAR4_BLOB, "IAR4",
        ),
    )
    for current, historical_path, schema_name, historical_id, historical_blob, prefix in historical_specs:
        try:
            historical_bytes = historical_path.read_bytes()
        except OSError as exc:
            problems.append(f"{prefix}_HISTORICAL_READ_FAILED:{exc}")
            continue
        problems.extend(validate_historical_manifest_binding(
            current, index, historical_bytes,
            historical_schema_name=schema_name,
            historical_id=historical_id,
            historical_blob=historical_blob,
            code_prefix=prefix,
        ))

    if index.get("current_baseline_manifest_id") != CURRENT_BASELINE_ID:
        problems.append("INDEX_CURRENT_BASELINE_ID_MISMATCH")
    if index.get("current_manifest_ids") != list(CURRENT_IDS):
        problems.append("INDEX_CURRENT_MANIFEST_IDS_MISMATCH")
    if index.get("historical_manifest_ids") != list(HISTORICAL_IDS):
        problems.append("INDEX_HISTORICAL_IDS_MISMATCH")
    if index.get("historical_manifest_git_blobs") != HISTORICAL_BLOBS:
        problems.append("INDEX_HISTORICAL_BLOB_BINDINGS_MISMATCH")
    if set(HISTORICAL_IDS) & set(index.get("current_manifest_ids", [])):
        problems.append("HISTORICAL_MANIFEST_MARKED_CURRENT")

    manifests = [baseline, iar1, iar2, iar3, iar4, iar5]
    rows = [row for manifest in manifests for row in manifest.get("tests", []) if type(row) is dict]
    requirement_ids = [row.get("requirement_test_id") for row in rows]
    python_ids = [row.get("python_test_id") for row in rows]
    if len(rows) != 77:
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
        "historical_manifest_ids": list(HISTORICAL_IDS),
        "historical_manifest_git_blobs": dict(HISTORICAL_BLOBS),
        "test_count": len(rows),
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
