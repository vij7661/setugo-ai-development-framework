from __future__ import annotations

import json
from hashlib import sha256


SINGLE_FILE_SCHEMA_VERSION = 1
SINGLE_FILE_HASH_BASIS = "UTF8_REENCODED_CONTENT_BYTES"


def _canonical_json(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def build_single_file_review_container(
    *,
    review_id: str,
    candidate_sha: str,
    intended_reviewer: str,
    prompt: str,
    artifacts: tuple[dict, ...],
) -> str:
    """Build one ordinary UTF-8 text file containing every review artifact.

    Each artifact record carries exact content, UTF-8 byte length and SHA-256.
    Re-encoding `content` as UTF-8 reconstructs the reviewed bytes. This is an
    external-evidence convenience container; it does not authenticate whichever
    model receives or returns it.
    """
    if not review_id or not prompt.strip():
        raise ValueError("review_id and prompt required")
    if len(candidate_sha) != 40 or any(ch not in "0123456789abcdef" for ch in candidate_sha):
        raise ValueError("candidate_sha must be lowercase 40-character git sha")
    if not artifacts:
        raise ValueError("single-file review container requires artifacts")

    normalized = []
    seen: set[str] = set()
    for item in artifacts:
        path = str(item.get("path", ""))
        content = item.get("content")
        if not path or path in seen:
            raise ValueError("artifact paths must be non-empty and unique")
        if not isinstance(content, str):
            raise ValueError("artifact content must be UTF-8 text")
        seen.add(path)
        raw = content.encode("utf-8")
        normalized.append({
            "path": path,
            "bytes_utf8": len(raw),
            "content_sha256": sha256(raw).hexdigest(),
            "hash_basis": SINGLE_FILE_HASH_BASIS,
            "content": content,
        })
    normalized.sort(key=lambda item: item["path"])

    payload = {
        "schema_version": SINGLE_FILE_SCHEMA_VERSION,
        "review_id": review_id,
        "candidate_sha": candidate_sha,
        "intended_external_reviewer": intended_reviewer,
        "content_classification": "USER_PROVIDED_EXTERNAL_CONTENT",
        "delivery_channel": "EXTERNAL_EVIDENCE_RELAY",
        "provider_api_authenticated": False,
        "can_satisfy_platform_review": False,
        "review_instruction": prompt.rstrip(),
        "reconstruction_rule": "For each artifact, UTF-8 encode content exactly and verify bytes_utf8 and content_sha256.",
        "artifacts": normalized,
    }
    container = {
        "container_format": "SETUGO_REVIEW_ENGINE_SINGLE_FILE_EXTERNAL_EVIDENCE_V1",
        "payload": payload,
        "payload_sha256": sha256(_canonical_json(payload)).hexdigest(),
    }
    return json.dumps(container, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def verify_single_file_review_container(text: str) -> dict:
    try:
        container = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("single-file review container is not valid JSON") from exc
    if not isinstance(container, dict) or container.get("container_format") != "SETUGO_REVIEW_ENGINE_SINGLE_FILE_EXTERNAL_EVIDENCE_V1":
        raise ValueError("invalid single-file review container format")
    payload = container.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("single-file review payload missing")
    expected_payload_hash = sha256(_canonical_json(payload)).hexdigest()
    if container.get("payload_sha256") != expected_payload_hash:
        raise ValueError("single-file review payload hash mismatch")
    if payload.get("provider_api_authenticated") is not False or payload.get("can_satisfy_platform_review") is not False:
        raise ValueError("external review container cannot claim platform API-review authority")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("single-file review artifacts missing")
    seen: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict):
            raise ValueError("single-file review artifact record invalid")
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not path or path in seen:
            raise ValueError("single-file review artifact path invalid or duplicated")
        if not isinstance(content, str):
            raise ValueError("single-file review artifact content invalid")
        seen.add(path)
        raw = content.encode("utf-8")
        if item.get("hash_basis") != SINGLE_FILE_HASH_BASIS:
            raise ValueError("single-file review artifact hash basis mismatch")
        if item.get("bytes_utf8") != len(raw):
            raise ValueError("single-file review artifact byte length mismatch")
        if item.get("content_sha256") != sha256(raw).hexdigest():
            raise ValueError("single-file review artifact content hash mismatch")
    return payload
