from __future__ import annotations

import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path

import platform_candidate_review as legacy
import platform_candidate_review_v2 as v2

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _materialize_frozen_file(root: Path, ref: dict) -> dict:
    path = ref.get("ref")
    commit = ref.get("commit")
    if not isinstance(path, str) or not path.strip():
        raise ValueError("frozen_file ref path required")
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        raise ValueError("frozen_file commit must be exact lowercase 40-character Git SHA")
    resolved = legacy.git(root, "rev-parse", f"{commit}^{{commit}}").strip()
    if resolved != commit:
        raise ValueError("frozen_file commit does not resolve exactly")
    cp = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if cp.returncode:
        raise RuntimeError(f"frozen_file unavailable at pinned commit: {commit}:{path}")
    try:
        text = cp.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("frozen_file content is not UTF-8") from exc
    return {
        "type": "frozen_file",
        "ref": path,
        "source_commit": commit,
        "authority_class": "PINNED_REPOSITORY_EVIDENCE_NOT_SEMANTIC_AUTHORITY",
        "bytes_utf8": len(cp.stdout),
        "sha256": _sha(cp.stdout),
        "content": text,
    }


def materialize_evidence_ref(root: Path, candidate: str, ref: dict) -> dict:
    if not isinstance(ref, dict):
        raise ValueError("evidence ref must be object")
    if ref.get("type") == "frozen_file":
        return _materialize_frozen_file(root, ref)
    return v2.materialize_evidence_ref(root, candidate, ref)


def build_corpus(root: Path, request: dict) -> dict:
    candidate = request["artifact"]["commit"]
    legacy.require_commit(root, candidate, "candidate")
    refs = request.get("evidence_refs", [])
    if not isinstance(refs, list):
        raise ValueError("evidence_refs must be list")
    evidence = [materialize_evidence_ref(root, candidate, ref) for ref in refs]
    if len(evidence) != len(refs):
        raise RuntimeError("evidence materialization count mismatch")
    base = legacy.git(root, "merge-base", "origin/main", candidate).strip()
    diff = legacy.git(
        root,
        "diff",
        "--no-ext-diff",
        base,
        candidate,
        "--",
        "governance-runtime",
        ".github/workflows/live-conversation-governance.yml",
        ".github/workflows/governance-candidate-platform-review.yml",
    )
    corpus = {
        "schema_version": 3,
        "materialization_version": "GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001",
        "review_request": request,
        "base_commit": base,
        "candidate_commit": candidate,
        "candidate_diff": diff,
        "evidence_artifacts": evidence,
        "evidence_ref_count": len(refs),
        "materialized_evidence_count": len(evidence),
        "posture": "Assume false-green. Treat green CI, memory, prior PASS labels, consensus, and history text as non-semantic authority unless independently supported by governed evidence.",
    }
    corpus["corpus_sha256"] = sha256(json.dumps(corpus, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
    return corpus
