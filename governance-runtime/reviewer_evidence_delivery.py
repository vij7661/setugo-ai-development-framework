"""Reviewer evidence-delivery completeness and finding-remediation helpers."""
from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping, Sequence


ADJUDICATION_STATES = frozenset({
    "ACCEPTED_AS_PROPOSED",
    "ACCEPTED_NARROWED",
    "ACCEPTED_WITH_ALTERNATIVE_SOLUTION",
    "REJECTED_NOT_REPRODUCED",
    "REJECTED_UNSAFE_OR_OUT_OF_SCOPE",
    "DEFERRED_REQUIRES_EVIDENCE",
})

DELIVERY_MODES = frozenset({
    "AUTHENTICATED_GITHUB_MCP_READ_ONLY",
    "PROVIDER_URL_CONTEXT",
    "PLATFORM_MATERIALIZED_CONTENT",
    "URL_ONLY",
})
_SHA1 = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SECRET_KEYS = frozenset({"authorization", "bearer", "token", "access_token", "api_key", "x_api_key", "x_goog_api_key", "password", "secret", "pat", "personal_access_token"})

def _key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_whole_delivery(*, declared_sha256: str, declared_bytes: int, delivered: bytes) -> bool:
    if not isinstance(declared_sha256, str) or len(declared_sha256) != 64:
        return False
    if not isinstance(declared_bytes, int) or declared_bytes < 0:
        return False
    return len(delivered) == declared_bytes and sha256_bytes(delivered) == declared_sha256


def verify_material_delivery(item: Mapping[str, Any], delivered: bytes | None = None, *, chunks: Sequence[Mapping[str, Any]] | None = None) -> bool:
    """Require actual material, never a filename/hash/summary-only placeholder."""
    if not isinstance(item, Mapping) or item.get("delivery_mode") not in {"native_file", "in_request", "chunked"}:
        return False
    if not isinstance(item.get("sha256"), str) or not isinstance(item.get("bytes"), int):
        return False
    if item.get("delivery_mode") == "chunked":
        return chunks is not None and verify_chunked_delivery(declared_sha256=item["sha256"], declared_bytes=item["bytes"], chunks=chunks)
    return delivered is not None and verify_whole_delivery(declared_sha256=item["sha256"], declared_bytes=item["bytes"], delivered=delivered)


def _contains_secret_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_key(key) in _SECRET_KEYS or _contains_secret_key(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return any(_contains_secret_key(child) for child in value)
    return False


def validate_reviewer_access_manifest(manifest: Mapping[str, Any]) -> bool:
    """Validate governed reviewer access without treating a locator as evidence."""
    if not isinstance(manifest, Mapping) or _contains_secret_key(manifest):
        return False
    required = {"provider_identity", "delivery_mode", "repository", "commit_sha", "review_request_id", "request_hash", "corpus_sha256", "accessed_objects", "read_only", "mandatory_subjects_covered", "result_status"}
    if set(manifest) != required or manifest.get("delivery_mode") not in DELIVERY_MODES:
        return False
    if not isinstance(manifest.get("provider_identity"), str) or not manifest["provider_identity"].strip():
        return False
    if not isinstance(manifest.get("repository"), str) or manifest["repository"].count("/") != 1:
        return False
    if not isinstance(manifest.get("commit_sha"), str) or not _SHA1.fullmatch(manifest["commit_sha"]):
        return False
    if not isinstance(manifest.get("review_request_id"), str) or not manifest["review_request_id"].strip():
        return False
    if not isinstance(manifest.get("request_hash"), str) or not _SHA256.fullmatch(manifest["request_hash"]):
        return False
    if not isinstance(manifest.get("corpus_sha256"), str) or not _SHA256.fullmatch(manifest["corpus_sha256"]):
        return False
    objects = manifest.get("accessed_objects")
    if not isinstance(objects, list) or not objects:
        return False
    if not isinstance(manifest.get("read_only"), bool) or not isinstance(manifest.get("mandatory_subjects_covered"), bool):
        return False
    if not isinstance(manifest.get("result_status"), str) or not manifest["result_status"].strip():
        return False
    mode = manifest["delivery_mode"]
    if mode == "URL_ONLY":
        if manifest["mandatory_subjects_covered"] or manifest["read_only"]:
            return False
    elif not manifest["read_only"]:
        return False
    for obj in objects:
        common = {"subject_id", "source_path", "commit_sha", "content_sha256", "bytes"}
        if not isinstance(obj, Mapping) or not all(isinstance(obj.get(k), str) and obj[k].strip() for k in ("subject_id", "source_path")):
            return False
        if obj.get("commit_sha") != manifest["commit_sha"]:
            return False
        if not isinstance(obj.get("content_sha256"), str) or not _SHA256.fullmatch(obj["content_sha256"]): return False
        if not isinstance(obj.get("bytes"), int) or obj["bytes"] < 0: return False
        if mode == "AUTHENTICATED_GITHUB_MCP_READ_ONLY":
            if set(obj) != common | {"repository", "tool_access", "object_id"} or obj.get("repository") != manifest["repository"] or obj.get("tool_access") != "read_only" or not isinstance(obj.get("object_id"), str) or not obj["object_id"].strip():
                return False
        elif mode == "PROVIDER_URL_CONTEXT":
            if set(obj) != common | {"url"}: return False
            url = obj.get("url")
            if not isinstance(url, str) or not (f"/blob/{manifest['commit_sha']}/" in url or f"/commit/{manifest['commit_sha']}/" in url):
                return False
        elif mode == "PLATFORM_MATERIALIZED_CONTENT":
            if set(obj) != common: return False
    return True


def validate_review_delivery_request(subjects: Sequence[Mapping[str, Any]], access_manifest: Mapping[str, Any], *, review_request: Mapping[str, Any] | None = None, required_manifest_mode: str | None = None) -> bool:
    """Bind mandatory material delivery to the declared reviewer access mode."""
    if not validate_reviewer_access_manifest(access_manifest) or not isinstance(subjects, Sequence) or not subjects:
        return False
    if access_manifest["delivery_mode"] == "URL_ONLY" or (required_manifest_mode and access_manifest["delivery_mode"] != required_manifest_mode):
        return False
    if review_request is not None:
        if access_manifest["commit_sha"] != review_request.get("artifact", {}).get("commit"):
            return False
        if access_manifest["review_request_id"] != review_request.get("review_request_id"):
            return False
        if access_manifest["request_hash"] != review_request.get("request_hash"):
            return False
    if not all(isinstance(item, Mapping) and verify_material_delivery(item, item.get("delivered"), chunks=item.get("chunks")) for item in subjects):
        return False
    expected = {(item.get("subject_id"), item.get("source_path"), item.get("commit_sha"), item.get("sha256"), item.get("bytes")) for item in subjects}
    observed = {(item.get("subject_id"), item.get("source_path"), item.get("commit_sha"), item.get("content_sha256"), item.get("bytes")) for item in access_manifest["accessed_objects"]}
    return expected == observed


def verify_chunked_delivery(
    *,
    declared_sha256: str,
    declared_bytes: int,
    chunks: Sequence[Mapping[str, Any]],
) -> bool:
    if not isinstance(chunks, Sequence) or isinstance(chunks, (str, bytes, bytearray)):
        return False
    if not chunks:
        return False

    normalized: list[tuple[int, bytes, str]] = []
    declared_count = None
    for row in chunks:
        if not isinstance(row, Mapping):
            return False
        index = row.get("index")
        count = row.get("count")
        data = row.get("bytes")
        digest = row.get("sha256")
        if not isinstance(index, int) or index < 0:
            return False
        if not isinstance(count, int) or count <= 0:
            return False
        if declared_count is None:
            declared_count = count
        if count != declared_count:
            return False
        if not isinstance(data, (bytes, bytearray)):
            return False
        raw = bytes(data)
        if not isinstance(digest, str) or sha256_bytes(raw) != digest:
            return False
        normalized.append((index, raw, digest))

    assert declared_count is not None
    if len(normalized) != declared_count:
        return False
    indexes = [index for index, _, _ in normalized]
    if sorted(indexes) != list(range(declared_count)):
        return False
    if len(set(indexes)) != len(indexes):
        return False

    whole = b"".join(raw for _, raw, _ in sorted(normalized, key=lambda row: row[0]))
    return verify_whole_delivery(
        declared_sha256=declared_sha256,
        declared_bytes=declared_bytes,
        delivered=whole,
    )


def validate_finding_solution_contract(finding: Mapping[str, Any]) -> bool:
    if not isinstance(finding, Mapping):
        return False
    required_text = (
        "finding_id",
        "severity",
        "location",
        "failure_path",
        "evidence",
        "impact",
        "proposed_remediation",
    )
    for field in required_text:
        if not isinstance(finding.get(field), str) or not finding[field].strip():
            return False
    tests = finding.get("regression_tests")
    if not isinstance(tests, list) or not tests or not all(isinstance(x, str) and x.strip() for x in tests):
        return False
    if finding.get("candidate_invalidated") not in {True, False}:
        return False
    if finding.get("blocking") not in {True, False}:
        return False
    return True


def validate_solution_adjudication(record: Mapping[str, Any]) -> bool:
    if not isinstance(record, Mapping):
        return False
    if record.get("state") not in ADJUDICATION_STATES:
        return False
    if not isinstance(record.get("finding_id"), str) or not record["finding_id"].strip():
        return False
    if not isinstance(record.get("reason"), str) or not record["reason"].strip():
        return False
    return True
