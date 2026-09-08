from __future__ import annotations

import json
from hashlib import sha256


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return sha256(canon(value)).hexdigest()


def freeze_review_input(*, review_request_id, request_hash, base_commit, candidate_commit, evidence_manifest_sha256, corpus):
    frozen = {
        "schema_version": 2,
        "review_request_id": review_request_id,
        "request_hash": request_hash,
        "base_commit": base_commit,
        "candidate_commit": candidate_commit,
        "evidence_manifest_sha256": evidence_manifest_sha256,
        "corpus": corpus,
    }
    frozen["corpus_sha256"] = digest(corpus)
    frozen["retry_identity_sha256"] = digest({
        "review_request_id": review_request_id,
        "request_hash": request_hash,
        "base_commit": base_commit,
        "candidate_commit": candidate_commit,
        "evidence_manifest_sha256": evidence_manifest_sha256,
        "corpus_sha256": frozen["corpus_sha256"],
    })
    return frozen


def classify_retry(previous, current):
    keys = [
        "review_request_id", "request_hash", "base_commit", "candidate_commit",
        "evidence_manifest_sha256", "corpus_sha256", "retry_identity_sha256",
    ]
    differences = [k for k in keys if previous.get(k) != current.get(k)]
    if differences:
        return {
            "same_frozen_retry": False,
            "classification": "NEW_GOVERNED_INPUT_REQUIRED",
            "differences": differences,
            "authority_effect": "NONE",
        }
    return {
        "same_frozen_retry": True,
        "classification": "SAME_FROZEN_RETRY",
        "differences": [],
        "authority_effect": "NONE_PENDING_REVIEW",
    }
