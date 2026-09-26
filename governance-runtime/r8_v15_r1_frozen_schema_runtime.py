"""R8 v15-r1 implementation Slice 1: frozen schema loader + GCP helpers.

This module is deliberately non-authoritative.  It verifies the exact frozen schema
bundle and implements only the bounded canonicalization behavior preregistered in
R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Tuple

FROZEN_CANDIDATE_SHA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
FROZEN_SPM_SHA256 = "84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797"
FROZEN_SEMANTIC_SHA = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"
FROZEN_SOURCE_MAP_SHA256 = "6d35964bfaa0cccfdd09bb46128a5efe3197d146e90144d1ac61ebe08c0aeec5"
FROZEN_GCP_JSON_SHA256 = "0466789e013d6f4e0080262effc674a57277588353c1dba19431be5be4f25ab9"

GENERATOR_ID = "R8V15R1-SPG-V2"
GENERATOR_ARTIFACT_SHA256 = "388fb8a61f31cbf99b001a2313d554c8a4aac36e61188eb95230b93c6b0077e6"
GENERATOR_RUNTIME_MANIFEST_DIGEST = "5d284ca4039368e3f74cbc9127cac07930f7852621d22c7e3a169fd51dd0147a"
GENERATOR_WORKLOAD_PROOF_DIGEST = "9cca9f7e996e9e956f6c1dc93451a9a9e53794071275e9074f5a25b31478c51c"

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

FROZEN_ARTIFACT_COUNT = 16
FROZEN_ENTRY_COUNT = 3058
FROZEN_SCHEMA_PREFIX = "schemas/governance-r8/v15-r1"


class FrozenSchemaError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


class GCPError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


class _PairObject(list):
    """Marker type preserving JSON object pairs before duplicate/NFC checks."""


class _LexicalInteger:
    """Preserves the exact JSON integer token until governance lexical validation."""

    __slots__ = ("raw",)

    def __init__(self, raw: str):
        self.raw = raw


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(_read_verified_file(path))


def _read_verified_file(path: Path) -> bytes:
    """Read one regular object through one descriptor, never by pathname twice.

    The governed runtime requires kernel no-follow support for its adversarial
    namespace model. Platforms without O_NOFOLLOW fail closed rather than
    silently weakening the guarantee.
    """
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise FrozenSchemaError("NOFOLLOW_UNSUPPORTED", str(path))
    flags = os.O_RDONLY | nofollow
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise FrozenSchemaError("ARTIFACT_OPEN_FAILED", f"{path}: {exc}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise FrozenSchemaError("ARTIFACT_NOT_REGULAR", str(path))
        chunks = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    except OSError as exc:
        raise FrozenSchemaError("ARTIFACT_READ_FAILED", f"{path}: {exc}") from exc
    finally:
        os.close(fd)


def _required_file(path: Path) -> None:
    if not path.is_file():
        raise FrozenSchemaError("REQUIRED_ARTIFACT_MISSING", str(path))


def _assert_frozen_file_path(repo_root: Path, schema_dir: Path, path: Path) -> None:
    """Reject symlink substitution and require direct confinement to the frozen schema dir."""
    try:
        relative = path.relative_to(repo_root)
    except ValueError as exc:
        raise FrozenSchemaError("ARTIFACT_PATH_INVALID", str(path)) from exc

    current = repo_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise FrozenSchemaError("ARTIFACT_PATH_SYMLINK", str(current))

    _required_file(path)

    try:
        resolved = path.resolve(strict=True)
        schema_resolved = schema_dir.resolve(strict=True)
    except FileNotFoundError as exc:
        raise FrozenSchemaError("REQUIRED_ARTIFACT_MISSING", str(path)) from exc

    if resolved.parent != schema_resolved:
        raise FrozenSchemaError(
            "ARTIFACT_PATH_INVALID",
            f"{path} resolves outside frozen schema directory: {resolved}",
        )
    if not resolved.is_file():
        raise FrozenSchemaError("REQUIRED_ARTIFACT_MISSING", str(path))


def validate_source_map_artifact_paths(spm: Dict[str, Any], source_map: Dict[str, Any]) -> None:
    artifacts = spm.get("artifacts")
    artifact_sources = source_map.get("artifact_sources")
    if not isinstance(artifacts, list) or not isinstance(artifact_sources, dict):
        raise FrozenSchemaError("SOURCE_MAP_ARTIFACT_SET_MISMATCH", "missing artifact sets")

    spm_paths = {a.get("path") for a in artifacts}
    source_paths = {
        f"{FROZEN_SCHEMA_PREFIX}/{name}"
        for name in artifact_sources
        if isinstance(name, str)
    }
    if spm_paths != source_paths:
        raise FrozenSchemaError(
            "SOURCE_MAP_ARTIFACT_SET_MISMATCH",
            f"spm-only={sorted(spm_paths-source_paths)} source-only={sorted(source_paths-spm_paths)}",
        )


def _load_json_bytes(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FrozenSchemaError("ARTIFACT_PARSE_ERROR", f"{label}: {exc}") from exc


def validate_spm_document(spm: Dict[str, Any]) -> None:
    if spm.get("semantic_candidate_commit") != FROZEN_SEMANTIC_SHA:
        raise FrozenSchemaError(
            "SEMANTIC_IDENTITY_MISMATCH",
            f"expected {FROZEN_SEMANTIC_SHA}, got {spm.get('semantic_candidate_commit')}",
        )

    coverage = spm.get("coverage")
    expected_coverage = {
        "uncovered_semantic_elements": [],
        "non_authoritative_only_sources": [],
        "conflicting_entries": [],
    }
    if coverage != expected_coverage:
        raise FrozenSchemaError("SPM_COVERAGE_INCOMPLETE", repr(coverage))

    generator = spm.get("generator") or {}
    expected = {
        "generator_id": GENERATOR_ID,
        "generator_artifact_sha256": GENERATOR_ARTIFACT_SHA256,
        "runtime_manifest_digest": GENERATOR_RUNTIME_MANIFEST_DIGEST,
        "workload_attestation_proof_digest": GENERATOR_WORKLOAD_PROOF_DIGEST,
        "qualification_status": "QUALIFIED",
    }
    for key, value in expected.items():
        if generator.get(key) != value:
            raise FrozenSchemaError(
                "GENERATOR_BINDING_MISMATCH",
                f"{key}: expected {value!r}, got {generator.get(key)!r}",
            )

    artifacts = spm.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != spm.get("artifact_count"):
        raise FrozenSchemaError("SPM_ARTIFACT_SET_INVALID", "artifact_count/list mismatch")
    if len(artifacts) != FROZEN_ARTIFACT_COUNT:
        raise FrozenSchemaError(
            "SPM_ARTIFACT_COUNT_MISMATCH",
            f"expected {FROZEN_ARTIFACT_COUNT} artifacts, got {len(artifacts)}",
        )

    for artifact in artifacts:
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise FrozenSchemaError("SPM_ARTIFACT_ID_INVALID", repr(artifact_id))
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise FrozenSchemaError("SPM_ARTIFACT_SHA256_INVALID", repr(digest))

        raw_path = artifact.get("path")
        if not isinstance(raw_path, str):
            raise FrozenSchemaError("SPM_ARTIFACT_PATH_INVALID", repr(raw_path))
        pure = PurePosixPath(raw_path)
        if (
            pure.is_absolute()
            or ".." in pure.parts
            or "." in pure.parts
            or pure.parent.as_posix() != FROZEN_SCHEMA_PREFIX
            or pure.as_posix() != raw_path
        ):
            raise FrozenSchemaError("SPM_ARTIFACT_PATH_INVALID", raw_path)

    entries = spm.get("entries")
    if not isinstance(entries, list) or len(entries) != spm.get("entry_count"):
        raise FrozenSchemaError("SPM_ENTRY_SET_INVALID", "entry_count/list mismatch")
    if len(entries) != FROZEN_ENTRY_COUNT:
        raise FrozenSchemaError(
            "SPM_ENTRY_COUNT_MISMATCH",
            f"expected {FROZEN_ENTRY_COUNT} entries, got {len(entries)}",
        )

    known_refs = set((spm.get("source_ref_catalog") or {}).keys())
    if not known_refs:
        raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", "empty source_ref_catalog")

    artifact_hashes_by_path = {a.get("path"): a.get("sha256") for a in artifacts}
    artifact_hashes_by_id = {a.get("artifact_id"): a.get("sha256") for a in artifacts}
    if (
        len(artifact_hashes_by_path) != len(artifacts)
        or len(artifact_hashes_by_id) != len(artifacts)
        or None in artifact_hashes_by_path
        or None in artifact_hashes_by_id
    ):
        raise FrozenSchemaError("SPM_ARTIFACT_SET_INVALID", "duplicate/missing artifact path or artifact_id")

    for entry in entries:
        artifact_id = entry.get("artifact_id")
        if artifact_id not in artifact_hashes_by_id:
            raise FrozenSchemaError("SPM_ENTRY_ARTIFACT_UNKNOWN", repr(artifact_id))
        if entry.get("artifact_sha256") != artifact_hashes_by_id[artifact_id]:
            raise FrozenSchemaError("SPM_ENTRY_ARTIFACT_DIGEST_MISMATCH", repr(artifact_id))
        refs = entry.get("source_ref_ids")
        if not isinstance(refs, list) or not refs:
            raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", f"empty refs for {artifact_id}")
        if not set(refs).issubset(known_refs):
            raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", f"unknown refs for {artifact_id}")
        if entry.get("generator_id") != GENERATOR_ID:
            raise FrozenSchemaError("GENERATOR_BINDING_MISMATCH", f"entry generator mismatch for {artifact_id}")
        if entry.get("generator_runtime_manifest_digest") != GENERATOR_RUNTIME_MANIFEST_DIGEST:
            raise FrozenSchemaError("GENERATOR_BINDING_MISMATCH", f"entry runtime mismatch for {artifact_id}")


class FrozenSchemaRuntime:
    def __init__(self, repo_root: Path | str, *, candidate_sha: str):
        self.repo_root = Path(repo_root)
        self.candidate_sha = candidate_sha
        self.schema_dir = self.repo_root / "schemas" / "governance-r8" / "v15-r1"

    def load(self) -> Dict[str, Any]:
        if self.candidate_sha != FROZEN_CANDIDATE_SHA:
            raise FrozenSchemaError(
                "CANDIDATE_IDENTITY_MISMATCH",
                f"expected {FROZEN_CANDIDATE_SHA}, got {self.candidate_sha}",
            )

        required = {
            "spm": self.schema_dir / "schema-provenance-manifest-candidate.json",
            "source_map": self.schema_dir / "schema-provenance-source-map.json",
            "traceability": self.schema_dir / "schema-freeze-traceability.json",
            "runtime_schema": self.schema_dir / "runtime-contracts.schema.json",
            "gcp": self.schema_dir / "gcp-rvm-2.json",
            "validator": self.schema_dir / "schema-freeze-validator-contract.json",
        }
        for path in required.values():
            _assert_frozen_file_path(self.repo_root, self.schema_dir, path)

        byte_cache: Dict[Path, bytes] = {}

        def read_once(path: Path) -> bytes:
            key = path.resolve()
            if key not in byte_cache:
                byte_cache[key] = _read_verified_file(path)
            return byte_cache[key]

        spm_path = required["spm"]
        spm_bytes = read_once(spm_path)
        actual_spm_sha = _sha256_bytes(spm_bytes)
        if actual_spm_sha != FROZEN_SPM_SHA256:
            raise FrozenSchemaError(
                "SPM_DIGEST_MISMATCH",
                f"expected {FROZEN_SPM_SHA256}, got {actual_spm_sha}",
            )
        spm = _load_json_bytes(spm_bytes, str(spm_path))
        validate_spm_document(spm)

        artifact_bytes_by_rel: Dict[str, bytes] = {}
        for artifact in spm["artifacts"]:
            rel = artifact["path"]
            path = self.repo_root / rel
            _assert_frozen_file_path(self.repo_root, self.schema_dir, path)
            data = read_once(path)
            actual = _sha256_bytes(data)
            if actual != artifact["sha256"]:
                raise FrozenSchemaError(
                    "ARTIFACT_DIGEST_MISMATCH",
                    f"{rel}: expected {artifact['sha256']}, got {actual}",
                )
            artifact_bytes_by_rel[rel] = data

        source_map_bytes = read_once(required["source_map"])
        source_map_sha = _sha256_bytes(source_map_bytes)
        if source_map_sha != FROZEN_SOURCE_MAP_SHA256:
            raise FrozenSchemaError(
                "SOURCE_MAP_DIGEST_MISMATCH",
                f"expected {FROZEN_SOURCE_MAP_SHA256}, got {source_map_sha}",
            )
        source_map = _load_json_bytes(source_map_bytes, str(required["source_map"]))
        if source_map.get("semantic_candidate_commit") != FROZEN_SEMANTIC_SHA:
            raise FrozenSchemaError(
                "SEMANTIC_IDENTITY_MISMATCH",
                "source map semantic candidate mismatch",
            )

        gcp_bytes = read_once(required["gcp"])
        gcp_sha = _sha256_bytes(gcp_bytes)
        if gcp_sha != FROZEN_GCP_JSON_SHA256:
            raise FrozenSchemaError(
                "GCP_VECTOR_DIGEST_MISMATCH",
                f"expected {FROZEN_GCP_JSON_SHA256}, got {gcp_sha}",
            )
        gcp = _load_json_bytes(gcp_bytes, str(required["gcp"]))

        validate_source_map_artifact_paths(spm, source_map)

        recompute_positive_vectors(gcp)
        validate_rejection_vectors(gcp)

        trace_rel = "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
        runtime_rel = "schemas/governance-r8/v15-r1/runtime-contracts.schema.json"
        validator_rel = "schemas/governance-r8/v15-r1/schema-freeze-validator-contract.json"

        traceability = _load_json_bytes(
            artifact_bytes_by_rel[trace_rel],
            trace_rel,
        )
        runtime_schema = _load_json_bytes(
            artifact_bytes_by_rel[runtime_rel],
            runtime_rel,
        )
        validator = _load_json_bytes(
            artifact_bytes_by_rel[validator_rel],
            validator_rel,
        )

        return {
            "candidate_sha": FROZEN_CANDIDATE_SHA,
            "spm_sha256": FROZEN_SPM_SHA256,
            "semantic_candidate_sha": FROZEN_SEMANTIC_SHA,
            "source_map_sha256": FROZEN_SOURCE_MAP_SHA256,
            "artifact_count": len(spm["artifacts"]),
            "entry_count": len(spm["entries"]),
            "runtime_schema_id": runtime_schema.get("$id"),
            "validator_rule_count": validator.get("rule_count"),
            "traceability_status": traceability.get("status"),
            "authority_effect": "NONE",
            "runtime_qualified": False,
            "release_authorized": False,
            "deployment_authorized": False,
            "production_authorized": False,
            "terminal_authority": False,
        }


_INTEGER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
_LEADING_ZERO_RE = re.compile(r"-?0[0-9]+\Z")


def _reject_top_level_integer_lexical(text: str) -> None:
    if text.startswith("+"):
        raise GCPError("GCP_REJECT_LEADING_PLUS", "leading plus is forbidden")
    if text == "-0":
        raise GCPError("GCP_REJECT_NEGATIVE_ZERO", "negative zero is forbidden")
    if "e" in text.lower():
        raise GCPError("GCP_REJECT_EXPONENT_FORM", "exponent form is forbidden")
    if "." in text:
        raise GCPError("GCP_REJECT_DECIMAL_FORM", "decimal form is forbidden")
    if _LEADING_ZERO_RE.fullmatch(text):
        raise GCPError("GCP_REJECT_LEADING_ZERO_INTEGER", "leading zero integer is forbidden")
    if not _INTEGER_RE.fullmatch(text):
        raise GCPError("GCP_REJECT_INTEGER_LEXICAL", f"invalid integer lexical form: {text}")


def _unicode_rejection_code(s: str) -> str | None:
    for ch in s:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            return "GCP_REJECT_UNPAIRED_SURROGATE"
        if 0xFDD0 <= cp <= 0xFDEF:
            return "GCP_REJECT_UNICODE_NONCHARACTER_FDD0"
        if cp & 0xFFFF == 0xFFFE:
            return "GCP_REJECT_UNICODE_NONCHARACTER_FFFE"
        if cp & 0xFFFF == 0xFFFF:
            return "GCP_REJECT_UNICODE_NONCHARACTER_FFFF"
    return None


def _validate_authority_string(s: str) -> str:
    code = _unicode_rejection_code(s)
    if code:
        raise GCPError(code, "forbidden Unicode scalar")
    if unicodedata.normalize("NFC", s) != s:
        raise GCPError("GCP_REJECT_NON_NFC_STRING", "authority string/key must already be NFC")
    return s


def _object_from_pairs(pairs: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
    seen_raw = set()
    seen_nfc: Dict[str, str] = {}
    materialized: List[Tuple[str, Any]] = []

    for raw_key, raw_value in pairs:
        if raw_key in seen_raw:
            raise GCPError("GCP_REJECT_DUPLICATE_KEY", f"duplicate key: {raw_key!r}")
        seen_raw.add(raw_key)

        code = _unicode_rejection_code(raw_key)
        if code:
            raise GCPError(code, "forbidden Unicode scalar in key")

        nfc = unicodedata.normalize("NFC", raw_key)
        prior = seen_nfc.get(nfc)
        if prior is not None and prior != raw_key:
            raise GCPError(
                "GCP_REJECT_NFC_KEY_COLLISION",
                f"keys {prior!r} and {raw_key!r} collide after NFC",
            )
        seen_nfc[nfc] = raw_key

        if nfc != raw_key:
            raise GCPError("GCP_REJECT_NON_NFC_STRING", f"key {raw_key!r} is not NFC")

        materialized.append((nfc, _normalize_value(raw_value)))

    materialized.sort(key=lambda kv: tuple(ord(ch) for ch in kv[0]))
    return {key: value for key, value in materialized}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, _PairObject):
        return _object_from_pairs(value)
    if isinstance(value, _LexicalInteger):
        _reject_top_level_integer_lexical(value.raw)
        parsed = int(value.raw)
        if parsed < INT64_MIN or parsed > INT64_MAX:
            raise GCPError("GCP_REJECT_OUT_OF_INT64", f"{parsed} outside signed int64")
        return parsed
    if isinstance(value, list):
        return [_normalize_value(v) for v in value]
    if isinstance(value, str):
        return _validate_authority_string(value)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value < INT64_MIN or value > INT64_MAX:
            raise GCPError("GCP_REJECT_OUT_OF_INT64", f"{value} outside signed int64")
        return value
    if isinstance(value, float):
        raise GCPError("GCP_REJECT_DECIMAL_FORM", "floating point numbers are not governance integers")
    raise GCPError("GCP_REJECT_UNSUPPORTED_TYPE", type(value).__name__)


def _parse_json_preserving_pairs(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=lambda pairs: _PairObject(pairs),
            parse_int=_LexicalInteger,
            parse_constant=lambda value: (_ for _ in ()).throw(
                GCPError("GCP_REJECT_UNSUPPORTED_NUMBER", value)
            ),
        )
    except GCPError:
        raise
    except json.JSONDecodeError as exc:
        raise GCPError("GCP_REJECT_MALFORMED_JSON", str(exc)) from exc


def _validate_extension_map(obj: Dict[str, Any]) -> None:
    if "extensions" not in obj:
        return
    ext = obj["extensions"]
    if not isinstance(ext, dict):
        raise GCPError("GCP_REJECT_EXTENSION_MAP_INVALID", "extensions must be an object")
    standard = set(obj) - {"extensions"}
    for key in ext:
        if key.startswith("sys:"):
            raise GCPError("GCP_REJECT_RESERVED_SYS_EXTENSION", key)
        if key in standard:
            raise GCPError("GCP_REJECT_EXTENSION_SHADOWS_STANDARD_FIELD", key)


def canonicalize_json_text(text: str, *, schema_context: str = "object") -> bytes:
    stripped = text.strip()

    if schema_context in {"integer_lexical", "integer_range"}:
        _reject_top_level_integer_lexical(stripped)
        value = int(stripped)
        if value < INT64_MIN or value > INT64_MAX:
            raise GCPError("GCP_REJECT_OUT_OF_INT64", f"{value} outside signed int64")
        return str(value).encode("ascii")

    value = _parse_json_preserving_pairs(stripped)
    normalized = _normalize_value(value)

    if schema_context == "extension_map":
        if not isinstance(normalized, dict):
            raise GCPError("GCP_REJECT_EXTENSION_MAP_INVALID", "expected object")
        _validate_extension_map(normalized)

    try:
        rendered = json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=False,
        )
        return rendered.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise GCPError("GCP_REJECT_UNPAIRED_SURROGATE", str(exc)) from exc


def recompute_positive_vectors(gcp_document: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    vectors = gcp_document.get("canonical_vectors")
    if not isinstance(vectors, list):
        raise FrozenSchemaError("GCP_VECTOR_SET_INVALID", "canonical_vectors missing")

    observed: Dict[str, Dict[str, str]] = {}
    for vector in vectors:
        vector_id = vector["vector_id"]
        canonical = canonicalize_json_text(
            vector["input_representation"],
            schema_context=vector["schema_context"],
        )
        canonical_text = canonical.decode("utf-8")
        digest = _sha256_bytes(canonical)
        if canonical_text != vector["expected_canonical_utf8"] or digest != vector["expected_sha256"]:
            raise FrozenSchemaError(
                "GCP_POSITIVE_VECTOR_MISMATCH",
                f"{vector_id}: canonical={canonical_text!r} sha256={digest}",
            )
        observed[vector_id] = {
            "canonical_utf8": canonical_text,
            "sha256": digest,
        }
    return observed


def validate_rejection_vectors(gcp_document: Dict[str, Any]) -> Dict[str, str]:
    vectors = gcp_document.get("rejection_vectors")
    if not isinstance(vectors, list):
        raise FrozenSchemaError("GCP_VECTOR_SET_INVALID", "rejection_vectors missing")

    observed: Dict[str, str] = {}
    for vector in vectors:
        vector_id = vector["vector_id"]
        expected_code = vector["expected_rejection_code"]
        try:
            canonicalize_json_text(
                vector["input_representation"],
                schema_context=vector["schema_context"],
            )
        except GCPError as exc:
            if exc.code != expected_code:
                raise FrozenSchemaError(
                    "GCP_REJECTION_VECTOR_CODE_MISMATCH",
                    f"{vector_id}: expected {expected_code}, got {exc.code}",
                ) from exc
            observed[vector_id] = exc.code
        else:
            raise FrozenSchemaError(
                "GCP_REJECTION_VECTOR_FALSE_ACCEPT",
                f"{vector_id}: expected {expected_code}",
            )
    return observed
