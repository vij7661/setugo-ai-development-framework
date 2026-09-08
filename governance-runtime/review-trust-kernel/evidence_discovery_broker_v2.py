from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(obj):
    return hashlib.sha256(_canon(obj)).hexdigest()


def _valid_path(path: str) -> bool:
    p = PurePosixPath(path)
    return bool(path) and not p.is_absolute() and ".." not in p.parts


def build_discovery_request(*, review_id, decision_target, candidate_sha, base_sha, query_type, path, reason, allowed_prefixes):
    if not decision_target or not str(decision_target).strip():
        raise ValueError("decision_target required")
    if query_type != "READ_FILE":
        raise ValueError("unsupported query_type")
    if not _valid_path(path):
        raise ValueError("invalid path")
    if not any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in allowed_prefixes):
        raise ValueError("path outside allowed prefixes")
    req = {
        "schema_version": 2,
        "review_id": review_id,
        "decision_target": decision_target,
        "candidate_sha": candidate_sha,
        "base_sha": base_sha,
        "query_type": query_type,
        "path": path,
        "reason": reason,
        "allowed_prefixes": sorted(set(allowed_prefixes)),
        "read_only": True,
    }
    req["request_sha256"] = _sha(req)
    return req


def materialize_response(request, *, content=None, source_ref=None, found=True):
    if not request.get("read_only"):
        raise ValueError("request must be read-only")
    for required in ("review_id", "decision_target", "candidate_sha", "base_sha", "path", "request_sha256"):
        if required not in request:
            raise ValueError(f"missing request field: {required}")
    resp = {
        "schema_version": 2,
        "request_sha256": request["request_sha256"],
        "review_id": request["review_id"],
        "decision_target": request["decision_target"],
        "candidate_sha": request["candidate_sha"],
        "base_sha": request["base_sha"],
        "path": request["path"],
        "found": bool(found),
        "source_ref": source_ref,
        "content_sha256": hashlib.sha256((content or "").encode("utf-8")).hexdigest() if found else None,
        "read_only": True,
    }
    resp["response_sha256"] = _sha(resp)
    return resp


def build_continuation_packet(*, review_id, decision_target, candidate_sha, base_sha, requests, responses):
    if not decision_target or not str(decision_target).strip():
        raise ValueError("decision_target required")
    req_by_hash = {r["request_sha256"]: r for r in requests}
    for r in requests:
        if r.get("review_id") != review_id or r.get("decision_target") != decision_target or r.get("candidate_sha") != candidate_sha or r.get("base_sha") != base_sha:
            raise ValueError("request binding mismatch")
    for resp in responses:
        req = req_by_hash.get(resp.get("request_sha256"))
        if req is None:
            raise ValueError("response has no matching request")
        for field in ("review_id", "decision_target", "candidate_sha", "base_sha", "path"):
            if resp.get(field) != req.get(field):
                raise ValueError(f"response binding mismatch: {field}")
    packet = {
        "schema_version": 2,
        "review_id": review_id,
        "decision_target": decision_target,
        "candidate_sha": candidate_sha,
        "base_sha": base_sha,
        "request_hashes": sorted(req_by_hash),
        "response_hashes": sorted(r["response_sha256"] for r in responses),
        "read_only": True,
    }
    packet["continuation_sha256"] = _sha(packet)
    return packet
