from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import platform_candidate_review as legacy

DIGITS = re.compile(r"^[0-9]+$")


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _repo_name() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repo or "/" not in repo:
        raise RuntimeError("GITHUB_REPOSITORY required for ci_run evidence materialization")
    return repo


def _fetch_ci_run(run_id: str) -> dict:
    if not isinstance(run_id, str) or not DIGITS.fullmatch(run_id):
        raise ValueError("ci_run ref must be numeric string")
    repo = _repo_name()
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "setugo-governance-evidence-materializer/2.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"ci_run evidence fetch failed HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"ci_run evidence fetch failed: {exc.reason}") from exc
    if str(data.get("id")) != run_id:
        raise RuntimeError("ci_run response id mismatch")
    return data


def _materialize_file(root: Path, candidate: str, ref_value: str) -> dict:
    if not isinstance(ref_value, str) or not ref_value.strip():
        raise ValueError("file evidence ref required")
    path = ref_value.strip()
    cp = subprocess.run(
        ["git", "show", f"{candidate}:{path}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if cp.returncode:
        raise RuntimeError(f"candidate evidence file unavailable: {path}")
    text = cp.stdout.decode("utf-8")
    return {
        "type": "file",
        "ref": path,
        "candidate_sha": candidate,
        "bytes_utf8": len(cp.stdout),
        "sha256": _sha_bytes(cp.stdout),
        "content": text,
    }


def _materialize_history(ref_value: str) -> dict:
    if not isinstance(ref_value, str) or not ref_value.strip():
        raise ValueError("history evidence ref required")
    text = ref_value.strip()
    raw = text.encode("utf-8")
    return {
        "type": "history",
        "ref": text,
        "authority_class": "FROZEN_REQUEST_TEXT_NON_AUTHORITATIVE",
        "bytes_utf8": len(raw),
        "sha256": _sha_bytes(raw),
        "content": text,
    }


def _materialize_ci_run(candidate: str, ref_value: str) -> dict:
    data = _fetch_ci_run(ref_value)
    if data.get("head_sha") != candidate:
        raise RuntimeError("ci_run head_sha does not match reviewed candidate")
    materialized = {
        "id": data.get("id"),
        "name": data.get("name"),
        "workflow_id": data.get("workflow_id"),
        "event": data.get("event"),
        "status": data.get("status"),
        "conclusion": data.get("conclusion"),
        "head_branch": data.get("head_branch"),
        "head_sha": data.get("head_sha"),
        "run_attempt": data.get("run_attempt"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }
    raw = _canon(materialized)
    return {
        "type": "ci_run",
        "ref": ref_value,
        "candidate_sha": candidate,
        "authority_class": "EXECUTION_EVIDENCE_NOT_SEMANTIC_AUTHORITY",
        "sha256": _sha_bytes(raw),
        "content": materialized,
    }


def materialize_evidence_ref(root: Path, candidate: str, ref: dict) -> dict:
    if not isinstance(ref, dict):
        raise ValueError("evidence ref must be object")
    ref_type = ref.get("type")
    ref_value = ref.get("ref")
    if ref_type == "file":
        return _materialize_file(root, candidate, ref_value)
    if ref_type == "history":
        return _materialize_history(ref_value)
    if ref_type == "ci_run":
        return _materialize_ci_run(candidate, ref_value)
    raise ValueError(f"unsupported evidence ref type: {ref_type!r}")


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
        "schema_version": 2,
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "review_request": request,
        "base_commit": base,
        "candidate_commit": candidate,
        "candidate_diff": diff,
        "evidence_artifacts": evidence,
        "evidence_ref_count": len(refs),
        "materialized_evidence_count": len(evidence),
        "posture": "Assume false-green. Treat green CI, memory, prior PASS labels, consensus, and history text as non-semantic authority unless independently supported by governed evidence.",
    }
    corpus["corpus_sha256"] = sha256(_canon(corpus)).hexdigest()
    return corpus


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--model", required=True)
    args = ap.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    legacy.verify_request_integrity(request)
    root = Path(".")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Materialization is completed before any provider secret is required or provider call can occur.
    corpus = build_corpus(root, request)
    prompt = legacy.build_prompt(request, corpus, args.model)
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY repository secret required")
    provider, review = legacy.invoke(key, args.model, prompt)
    validation = legacy.validate(review, request, args.model)
    envelope = {
        "schema_version": 2,
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "review_class": "PLATFORM_AUTO_API_REVIEW",
        "transport": "AUTOMATIC_API",
        "provider": "gemini",
        "model": args.model,
        "provider_api_authenticated": True,
        "remote_model_identity_cryptographically_proven": False,
        "request_hash": request.get("request_hash"),
        "corpus_sha256": corpus["corpus_sha256"],
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "evidence_ref_count": corpus["evidence_ref_count"],
        "materialized_evidence_count": corpus["materialized_evidence_count"],
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
    }
    for name, obj in [
        ("corpus.json", corpus),
        ("provider-response.json", provider),
        ("review.json", review),
        ("validation.json", validation),
        ("execution-envelope.json", envelope),
    ]:
        (out / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not validation["valid"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
