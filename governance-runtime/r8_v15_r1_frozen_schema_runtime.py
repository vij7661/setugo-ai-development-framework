"""R8 v15-r1 implementation Slice 1: frozen schema loader + GCP helpers.

This module is deliberately non-authoritative.  It verifies the exact frozen schema
bundle and implements only the bounded canonicalization behavior preregistered in
R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

FROZEN_CANDIDATE_SHA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
FROZEN_SPM_SHA256 = "84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797"
FROZEN_SEMANTIC_SHA = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"
FROZEN_SOURCE_MAP_SHA256 = "6d35964bfaa0cccfdd09bb46128a5efe3197d146e90144d1ac61ebe08c0aeec5"
FROZEN_GCP_JSON_SHA256 = "c6c07133e6d1254afaf703e04fd4b5509298b9c7b71fc30572870207907d5b1e"

GENERATOR_ID = "R8V15R1-SPG-V2"
GENERATOR_ARTIFACT_SHA256 = "388fb8a61f31cbf99b001a2313d554c8a4aac36e61188eb95230b93c6b0077e6"
GENERATOR_RUNTIME_MANIFEST_DIGEST = "5d284ca4039368e3f74cbc9127cac07930f7852621d22c7e3a169fd51dd0147a"
GENERATOR_WORKLOAD_PROOF_DIGEST = "9cca9f7e996e9e956f6c1dc93451a9a9e53794071275e9074f5a25b31478c51c"

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


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


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _required_file(path: Path) -> None:
    if not path.is_file():
        raise FrozenSchemaError("REQUIRED_ARTIFACT_MISSING", str(path))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FrozenSchemaError("ARTIFACT_PARSE_ERROR", f"{path}: {exc}") from exc


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
    if len(artifacts) != 16:
        raise FrozenSchemaError("SPM_ARTIFACT_SET_INVALID", f"expected 16 artifacts, got {len(artifacts)}")

    entries = spm.get("entries")
    if not isinstance(entries, list) or len(entries) != spm.get("entry_count"):
        raise FrozenSchemaError("SPM_ENTRY_SET_INVALID", "entry_count/list mismatch")

    known_refs = set((spm.get("source_ref_catalog") or {}).keys())
    if not known_refs:
        raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", "empty source_ref_catalog")

    artifact_hashes = {a.get("path"): a.get("sha256") for a in artifacts}
    if len(artifact_hashes) != len(artifacts) or None in artifact_hashes:
        raise FrozenSchemaError("SPM_ARTIFACT_SET_INVALID", "duplicate/missing artifact path")

    for entry in entries:
        path = entry.get("artifact_path")
        if path not in artifact_hashes:
            raise FrozenSchemaError("SPM_ENTRY_ARTIFACT_UNKNOWN", repr(path))
        if entry.get("artifact_sha256") != artifact_hashes[path]:
            raise FrozenSchemaError("SPM_ENTRY_ARTIFACT_DIGEST_MISMATCH", repr(path))
        refs = entry.get("source_ref_ids")
        if not isinstance(refs, list) or not refs:
            raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", f"empty refs for {path}")
        if not set(refs).issubset(known_refs):
            raise FrozenSchemaError("SPM_SOURCE_REF_INVALID", f"unknown refs for {path}")
        if entry.get("generator_id") != GENERATOR_ID:
            raise FrozenSchemaError("GENERATOR_BINDING_MISMATCH", f"entry generator mismatch for {path}")
        if entry.get("generator_runtime_manifest_digest") != GENERATOR_RUNTIME_MANIFEST_DIGEST:
            raise FrozenSchemaError("GENERATOR_BINDING_MISMATCH", f"entry runtime mismatch for {path}")


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
            _required_file(path)

        spm_path = required["spm"]
        actual_spm_sha = _sha256_file(spm_path)
        if actual_spm_sha != FROZEN_SPM_SHA256:
            raise FrozenSchemaError(
                "SPM_DIGEST_MISMATCH",
                f"expected {FROZEN_SPM_SHA256}, got {actual_spm_sha}",
            )

        source_map_sha = _sha256_file(required["source_map"])
        if source_map_sha != FROZEN_SOURCE_MAP_SHA256:
            raise FrozenSchemaError(
                "SOURCE_MAP_DIGEST_MISMATCH",
                f"expected {FROZEN_SOURCE_MAP_SHA256}, got {source_map_sha}",
            )

        gcp_sha = _sha256_file(required["gcp"])
        if gcp_sha != FROZEN_GCP_JSON_SHA256:
            raise FrozenSchemaError(
                "GCP_VECTOR_DIGEST_MISMATCH",
                f"expected {FROZEN_GCP_JSON_SHA256}, got {gcp_sha}",
            )

        spm = _load_json(spm_path)
        validate_spm_document(spm)

        for artifact in spm["artifacts"]:
            rel = artifact["path"]
            path = self.repo_root / rel
            _required_file(path)
            actual = _sha256_file(path)
            if actual != artifact["sha256"]:
                raise FrozenSchemaError(
                    "ARTIFACT_DIGEST_MISMATCH",
                    f"{rel}: expected {artifact['sha256']}, got {actual}",
                )

        source_map = _load_json(required["source_map"])
        if source_map.get("semantic_candidate_commit") != FROZEN_SEMANTIC_SHA:
            raise FrozenSchemaError(
                "SEMANTIC_IDENTITY_MISMATCH",
                "source map semantic candidate mismatch",
            )

        spm_names = {Path(a["path"]).name for a in spm["artifacts"]}
        source_names = set((source_map.get("artifact_sources") or {}).keys())
        if spm_names != source_names:
            raise FrozenSchemaError(
                "SOURCE_MAP_ARTIFACT_SET_MISMATCH",
                f"spm-only={sorted(spm_names-source_names)} source-only={sorted(source_names-spm_names)}",
            )

        gcp = _load_json(required["gcp"])
        recompute_positive_vectors(gcp)

        # Parse the remaining required core artifacts after digest verification.
        traceability = _load_json(required["traceability"])
        runtime_schema = _load_json(required["runtime_schema"])
        validator = _load_json(required["validator"])

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
