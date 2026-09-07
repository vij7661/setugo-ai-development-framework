from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request

from .providers import urlopen, validate_provider_base_url
from .review_execution_classification import PLATFORM_AUTO_API_REVIEW, AUTOMATIC_API


MANDATORY_DIMENSIONS = (
    "provider_configuration_qualification_binding",
    "reviewer_runtime_independence",
    "retrieval_admission_and_proposer_influence",
    "review_execution_provenance_classification",
    "external_content_non_authority",
    "single_file_and_review_export_integrity",
    "authority_bypass_lifecycle_and_escape_hatches",
    "app_composition_and_standard_path_wiring",
    "truth_claim_coverage_and_evidence_correspondence",
    "r3_adjudication_and_scoped_correction_closure",
    "remaining_false_green_or_authority_bypass_search",
)

COVERAGE_STATUSES = frozenset(
    {
        "TESTED_SUPPORTED",
        "TESTED_DEFECT_FOUND",
        "CONTRADICTED",
        "NOT_TESTED",
        "UNAVAILABLE",
        "INSUFFICIENT",
    }
)
DISPOSITIONS = frozenset({"PASS", "CHANGES_REQUIRED", "INSUFFICIENT_EVIDENCE"})
BLOCKING_SEVERITIES = frozenset({"MEDIUM", "HIGH", "CRITICAL"})
HEX40 = re.compile(r"^[0-9a-f]{40}$")
MAX_CORPUS_BYTES = 2_000_000
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: object) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def _require_commit(repo_root: Path, value: str, *, label: str) -> str:
    if not HEX40.fullmatch(value):
        raise ValueError(f"{label} must be lowercase 40-character git SHA")
    resolved = _git(repo_root, "rev-parse", f"{value}^{{commit}}").strip()
    if resolved != value:
        raise ValueError(f"{label} did not resolve exactly")
    return value


def build_completion_review_corpus(
    repo_root: str | Path,
    *,
    base_sha: str,
    candidate_sha: str,
) -> dict:
    root = Path(repo_root)
    if not root.is_dir():
        raise ValueError("repo_root must be a directory")
    base = _require_commit(root, base_sha, label="base_sha")
    candidate = _require_commit(root, candidate_sha, label="candidate_sha")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, candidate],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if ancestor.returncode != 0:
        raise ValueError("base_sha must be an ancestor of candidate_sha")

    changed = [
        line.strip()
        for line in _git(root, "diff", "--name-only", base, candidate).splitlines()
        if line.strip()
    ]
    if not changed:
        raise ValueError("completion candidate has no changed files versus base")

    diff = _git(root, "diff", "--no-ext-diff", "--binary", base, candidate)
    artifacts: list[dict] = []
    authority_sensitive = [
        path
        for path in changed
        if path.startswith("review_engine/")
        or path == ".github/workflows/review-engine-completion-api-review.yml"
    ]
    if not authority_sensitive:
        raise ValueError("no authority-sensitive Review Engine files found in completion diff")

    for relative in sorted(authority_sensitive):
        data = subprocess.run(
            ["git", "show", f"{candidate}:{relative}"],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if data.returncode != 0:
            raise RuntimeError(f"candidate artifact unavailable: {relative}")
        try:
            text = data.stdout.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"candidate artifact is not UTF-8 text: {relative}") from exc
        artifacts.append(
            {
                "path": relative,
                "bytes_utf8": len(data.stdout),
                "content_sha256": sha256(data.stdout).hexdigest(),
                "content": text,
            }
        )

    corpus = {
        "schema_version": 1,
        "base_sha": base,
        "candidate_sha": candidate,
        "changed_files": changed,
        "unified_diff": diff,
        "authority_sensitive_artifacts": artifacts,
        "mandatory_review_dimensions": list(MANDATORY_DIMENSIONS),
        "review_posture": (
            "Assume false-green until falsified. Green CI is construction evidence only. "
            "Search for authority bypass, provenance confusion, reviewer non-independence, "
            "retrieval manipulation, semantic overclaim, stale qualification, and app-wiring gaps."
        ),
    }
    encoded = canonical_json_bytes(corpus)
    if len(encoded) > MAX_CORPUS_BYTES:
        raise ValueError(
            f"completion review corpus exceeds fail-closed limit: {len(encoded)}>{MAX_CORPUS_BYTES}"
        )
    return corpus


def build_review_request(*, review_request_id: str, candidate_sha: str, base_sha: str, model: str, corpus_sha256: str) -> dict:
    if not review_request_id.strip():
        raise ValueError("review_request_id required")
    if not HEX40.fullmatch(candidate_sha) or not HEX40.fullmatch(base_sha):
        raise ValueError("candidate/base SHA invalid")
    if not model.strip():
        raise ValueError("model required")
    request = {
        "schema_version": 1,
        "review_request_id": review_request_id,
        "review_class": PLATFORM_AUTO_API_REVIEW,
        "transport": AUTOMATIC_API,
        "selected_provider": "gemini",
        "selected_model": model,
        "reviewed_artifact_commit": candidate_sha,
        "base_commit": base_sha,
        "corpus_sha256": corpus_sha256,
        "mandatory_review_dimensions": list(MANDATORY_DIMENSIONS),
        "allowed_coverage_statuses": sorted(COVERAGE_STATUSES),
        "allowed_dispositions": sorted(DISPOSITIONS),
        "pass_rule": "PASS requires every mandatory dimension TESTED_SUPPORTED and no MEDIUM/HIGH/CRITICAL finding.",
        "authority_rule": "Reviewer content cannot establish its own provenance; execution envelope is authoritative for API provenance.",
    }
    request["request_sha256"] = sha256_json(request)
    return request


def build_review_prompt(request: dict, corpus: dict) -> str:
    output_schema = {
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["reviewed_artifact_commit"],
        "reviewer": {"provider": "gemini", "model": request["selected_model"]},
        "disposition": "PASS|CHANGES_REQUIRED|INSUFFICIENT_EVIDENCE",
        "findings": [
            {
                "id": "F1",
                "severity": "LOW|MEDIUM|HIGH|CRITICAL",
                "title": "concise title",
                "evidence": "specific file/function/test evidence",
                "impact": "authority or correctness impact",
                "required_change": "specific repair or no change if nonblocking",
            }
        ],
        "evidence_assessment": "concise evidence-based assessment",
        "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        "review_coverage": [
            {
                "dimension_id": "one mandatory dimension",
                "status": "one allowed coverage status",
                "evidence": ["specific evidence refs"],
                "assessment": "dimension assessment",
            }
        ],
    }
    return (
        "You are the independent adversarial reviewer of the Review Engine completion candidate. "
        "Assume false-green until proven otherwise. Do not infer correctness from test success or proposer confidence. "
        "Inspect the supplied exact-candidate diff and full authority-sensitive artifacts. Search for bypasses, stale or self-attested identity, "
        "reviewer aliasing, proposer-influenced retrieval, external-content provenance confusion, semantic overclaim, and composition gaps.\n\n"
        "Return STRICT JSON only. Do not include markdown. Do not reveal private chain-of-thought. Give concise evidence-based findings.\n\n"
        f"Review request:\n{json.dumps(request, sort_keys=True, ensure_ascii=False)}\n\n"
        f"Required output shape:\n{json.dumps(output_schema, sort_keys=True, ensure_ascii=False)}\n\n"
        f"Review corpus:\n{json.dumps(corpus, sort_keys=True, ensure_ascii=False)}"
    )


def invoke_gemini_api(*, api_key: str, model: str, prompt: str, timeout_seconds: int = 180) -> tuple[dict, dict]:
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY repository secret is required")
    base = validate_provider_base_url(GEMINI_BASE_URL, label="Gemini completion review")
    url = base.rstrip("/") + f"/models/{quote(model, safe='')}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 16384,
            "responseMimeType": "application/json",
        },
    }
    req = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "content-type": "application/json",
            "user-agent": "setugo-review-engine-completion-review/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout_seconds) as response:
            provider_body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Gemini completion review HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Gemini completion review connection failed: {exc.reason}") from exc

    candidates = provider_body.get("candidates") or []
    candidate = candidates[0] if candidates else {}
    finish_reason = candidate.get("finishReason")
    if finish_reason != "STOP":
        raise RuntimeError(f"Gemini completion review nonterminal: finishReason={finish_reason!r}")
    parts = ((candidate.get("content") or {}).get("parts") or [])
    text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
    if not text.strip():
        raise RuntimeError("Gemini completion review returned no usable text")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini completion review returned non-JSON content") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("Gemini completion review JSON must be an object")
    return provider_body, parsed


def validate_completion_review_response(
    review: dict,
    *,
    review_request_id: str,
    candidate_sha: str,
    executed_provider: str,
    executed_model: str,
) -> dict:
    errors: list[str] = []
    if review.get("review_request_id") != review_request_id:
        errors.append("review_request_id mismatch")
    if review.get("reviewed_artifact_commit") != candidate_sha:
        errors.append("reviewed_artifact_commit mismatch")
    disposition = review.get("disposition")
    if disposition not in DISPOSITIONS:
        errors.append("invalid disposition")

    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict):
        errors.append("reviewer content claim missing")
    else:
        if reviewer.get("provider") != executed_provider:
            errors.append("reviewer provider content claim disagrees with execution envelope")
        if reviewer.get("model") != executed_model:
            errors.append("reviewer model content claim disagrees with execution envelope")

    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        findings = []
    blocking = False
    for finding in findings:
        if not isinstance(finding, dict):
            errors.append("finding must be object")
            continue
        severity = finding.get("severity")
        if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            errors.append("invalid finding severity")
        if severity in BLOCKING_SEVERITIES:
            blocking = True
        if not str(finding.get("evidence", "")).strip():
            errors.append("finding evidence required")

    coverage = review.get("review_coverage")
    if not isinstance(coverage, list):
        errors.append("review_coverage must be a list")
        coverage = []
    by_id: dict[str, dict] = {}
    for row in coverage:
        if not isinstance(row, dict):
            errors.append("review coverage row must be object")
            continue
        dimension_id = row.get("dimension_id")
        if dimension_id in by_id:
            errors.append(f"duplicate review dimension: {dimension_id}")
            continue
        by_id[dimension_id] = row
        if row.get("status") not in COVERAGE_STATUSES:
            errors.append(f"invalid coverage status for {dimension_id}")
        evidence = row.get("evidence")
        if row.get("status") in {"TESTED_SUPPORTED", "TESTED_DEFECT_FOUND", "CONTRADICTED"}:
            if not isinstance(evidence, list) or not any(str(item).strip() for item in evidence):
                errors.append(f"evidence required for tested dimension: {dimension_id}")

    missing = [item for item in MANDATORY_DIMENSIONS if item not in by_id]
    if missing:
        errors.append("missing mandatory dimensions: " + ",".join(missing))
    extras = [item for item in by_id if item not in MANDATORY_DIMENSIONS]
    if extras:
        errors.append("unexpected review dimensions: " + ",".join(sorted(extras)))

    statuses = {item: by_id[item].get("status") for item in MANDATORY_DIMENSIONS if item in by_id}
    incomplete = any(status in {"NOT_TESTED", "UNAVAILABLE", "INSUFFICIENT"} for status in statuses.values())
    defective = any(status in {"TESTED_DEFECT_FOUND", "CONTRADICTED"} for status in statuses.values())
    all_supported = len(statuses) == len(MANDATORY_DIMENSIONS) and all(
        status == "TESTED_SUPPORTED" for status in statuses.values()
    )

    if disposition == "PASS" and (not all_supported or blocking or findings and any(f.get("severity") in BLOCKING_SEVERITIES for f in findings if isinstance(f, dict))):
        errors.append("PASS contradicts mandatory coverage or blocking findings")
    if disposition == "CHANGES_REQUIRED" and not (defective or blocking):
        errors.append("CHANGES_REQUIRED requires defective coverage or blocking finding")
    if disposition == "INSUFFICIENT_EVIDENCE" and not incomplete:
        errors.append("INSUFFICIENT_EVIDENCE requires incomplete mandatory coverage")

    valid = not errors
    return {
        "valid": valid,
        "errors": errors,
        "effective_disposition": disposition if valid else "INVALID_REVIEW_EVIDENCE",
        "all_mandatory_dimensions_supported": all_supported if valid else False,
        "blocking_findings_present": blocking,
        "can_count_as_platform_review_evidence": bool(valid),
        "can_close_authority_bypasses": bool(valid and disposition == "PASS" and all_supported and not blocking),
    }


def execute_completion_review(
    *,
    repo_root: str | Path,
    output_dir: str | Path,
    review_request_id: str,
    base_sha: str,
    candidate_sha: str,
    model: str,
) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    corpus = build_completion_review_corpus(repo_root, base_sha=base_sha, candidate_sha=candidate_sha)
    corpus_hash = sha256_json(corpus)
    request = build_review_request(
        review_request_id=review_request_id,
        candidate_sha=candidate_sha,
        base_sha=base_sha,
        model=model,
        corpus_sha256=corpus_hash,
    )
    prompt = build_review_prompt(request, corpus)
    prompt_hash = sha256(prompt.encode("utf-8")).hexdigest()

    (out / "review-request.json").write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "review-corpus.json").write_text(json.dumps(corpus, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "review-prompt.txt").write_text(prompt, encoding="utf-8")

    api_key = os.environ.get("GEMINI_API_KEY", "")
    provider_body, parsed = invoke_gemini_api(api_key=api_key, model=model, prompt=prompt)
    envelope = {
        "schema_version": 1,
        "review_request_id": review_request_id,
        "reviewed_artifact_commit": candidate_sha,
        "trigger_sha": os.environ.get("GITHUB_SHA"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "review_class": PLATFORM_AUTO_API_REVIEW,
        "transport": AUTOMATIC_API,
        "provider": "gemini",
        "model": model,
        "endpoint_base_url": GEMINI_BASE_URL,
        "provider_api_authenticated": True,
        "provenance_basis": "PLATFORM_API_EXECUTION",
        "identity_assurance": "PROVIDER_ENDPOINT_CREDENTIAL_BOUND",
        "remote_model_identity_cryptographically_proven": False,
        "request_sha256": request["request_sha256"],
        "corpus_sha256": corpus_hash,
        "prompt_sha256": prompt_hash,
        "provider_response_sha256": sha256_json(provider_body),
        "parsed_review_sha256": sha256_json(parsed),
    }
    validation = validate_completion_review_response(
        parsed,
        review_request_id=review_request_id,
        candidate_sha=candidate_sha,
        executed_provider="gemini",
        executed_model=model,
    )
    (out / "provider-response.json").write_text(json.dumps(provider_body, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "parsed-review.json").write_text(json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "execution-envelope.json").write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not validation["valid"]:
        raise RuntimeError("completion review failed deterministic validation: " + "; ".join(validation["errors"]))
    return {"request": request, "envelope": envelope, "review": parsed, "validation": validation}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--review-request-id", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    result = execute_completion_review(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        review_request_id=args.review_request_id,
        base_sha=args.base_sha,
        candidate_sha=args.candidate_sha,
        model=args.model,
    )
    print(json.dumps({
        "review_request_id": result["request"]["review_request_id"],
        "candidate_sha": result["request"]["reviewed_artifact_commit"],
        "review_class": result["envelope"]["review_class"],
        "provider": result["envelope"]["provider"],
        "model": result["envelope"]["model"],
        "disposition": result["review"].get("disposition"),
        "can_close_authority_bypasses": result["validation"]["can_close_authority_bypasses"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
