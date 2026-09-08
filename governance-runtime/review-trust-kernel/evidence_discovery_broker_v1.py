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


def build_discovery_request(*, review_id, candidate_sha, base_sha, query_type, path, reason, allowed_prefixes):
    if query_type != "READ_FILE":
        raise ValueError("unsupported query_type")
    if not _valid_path(path):
        raise ValueError("invalid path")
    if not any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in allowed_prefixes):
        raise ValueError("path outside allowed prefixes")
    req = {
        "schema_version": 1,
        "review_id": review_id,
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
    resp = {
        "schema_version": 1,
        "request_sha256": request["request_sha256"],
        "review_id": request["review_id"],
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


def adjudicate_discovery(*, mandatory_request_hashes, responses, reviewer_disposition):
    by_req = {r["request_sha256"]: r for r in responses}
    unresolved = []
    for req_hash in sorted(set(mandatory_request_hashes)):
        r = by_req.get(req_hash)
        if r is None or not r.get("found"):
            unresolved.append(req_hash)
    promotable = reviewer_disposition == "PASS" and not unresolved
    result = {
        "reviewer_disposition": reviewer_disposition,
        "mandatory_request_hashes": sorted(set(mandatory_request_hashes)),
        "resolved_response_hashes": sorted(r["response_sha256"] for r in responses if r.get("found")),
        "unresolved_request_hashes": unresolved,
        "promotable": promotable,
    }
    result["decision_sha256"] = _sha(result)
    return result
