from __future__ import annotations

import json
import subprocess
from hashlib import sha256


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def materialize_file(root, candidate_commit, ref):
    path = ref.get("ref")
    if not isinstance(path, str) or not path:
        raise ValueError("file evidence ref requires ref path")
    cp = subprocess.run(
        ["git", "show", f"{candidate_commit}:{path}"], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if cp.returncode:
        raise RuntimeError(f"candidate evidence file unavailable: {path}")
    return {
        "type": "file",
        "ref": path,
        "candidate_commit": candidate_commit,
        "bytes": len(cp.stdout),
        "sha256": digest_bytes(cp.stdout),
        "content": cp.stdout.decode("utf-8"),
    }


def materialize_evidence_refs(root, candidate_commit, evidence_refs, resolvers=None):
    resolvers = dict(resolvers or {})
    if not isinstance(evidence_refs, list):
        raise ValueError("evidence_refs must be list")
    materialized = []
    for index, ref in enumerate(evidence_refs):
        if not isinstance(ref, dict):
            raise ValueError(f"evidence ref {index} must be object")
        kind = ref.get("type")
        if kind == "file":
            item = materialize_file(root, candidate_commit, ref)
        else:
            resolver = resolvers.get(kind)
            if resolver is None:
                raise RuntimeError(f"mandatory evidence unsupported or unresolved: type={kind!r} index={index}")
            payload = resolver(ref)
            if payload is None:
                raise RuntimeError(f"mandatory evidence unavailable: type={kind!r} index={index}")
            raw = canon(payload)
            item = {
                "type": kind,
                "ref": ref.get("ref"),
                "bytes": len(raw),
                "sha256": digest_bytes(raw),
                "content": payload,
            }
        materialized.append(item)

    if len(materialized) != len(evidence_refs):
        raise RuntimeError("evidence materialization count mismatch")
    return {
        "schema_version": 2,
        "candidate_commit": candidate_commit,
        "declared_count": len(evidence_refs),
        "materialized_count": len(materialized),
        "artifacts": materialized,
        "manifest_sha256": sha256(canon(materialized)).hexdigest(),
    }
