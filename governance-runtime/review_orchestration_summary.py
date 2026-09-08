from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _dimension_summary(review: dict[str, Any] | None) -> dict[str, Any]:
    if not review:
        return {"total": 0, "supported": 0, "unsupported": 0, "ids": []}
    rows = review.get("mandatory_dimensions") or review.get("dimension_assessments") or []
    if not isinstance(rows, list):
        rows = []
    ids: list[str] = []
    supported = 0
    unsupported = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        dim_id = row.get("dimension_id") or row.get("id") or row.get("dimension")
        if isinstance(dim_id, str):
            ids.append(dim_id)
        status = str(row.get("status") or row.get("assessment") or "").upper()
        if status in {"SUPPORTED", "TESTED_SUPPORTED", "PASS"}:
            supported += 1
        else:
            unsupported += 1
    return {"total": supported + unsupported, "supported": supported, "unsupported": unsupported, "ids": ids}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--job-status", required=True)
    args = ap.parse_args()

    request = _read_json(Path(args.request)) or {}
    evidence_dir = Path(args.evidence_dir)
    envelope = _read_json(evidence_dir / "execution-envelope.json") or {}
    review = _read_json(evidence_dir / "review.json")
    validation = _read_json(evidence_dir / "validation.json")
    workflow_status = _read_json(evidence_dir / "workflow-status.json") or {}
    corpus = _read_json(evidence_dir / "corpus.json") or {}
    error_path = evidence_dir / "provider-error.log"
    error_text = error_path.read_text(encoding="utf-8", errors="replace")[-2000:] if error_path.exists() else None

    findings = review.get("findings", []) if review else []
    if not isinstance(findings, list):
        findings = []

    summary = {
        "schema_version": 1,
        "summary_type": "GOVERNED_REVIEW_ORCHESTRATION_SUMMARY",
        "review_request_id": request.get("review_request_id"),
        "review_request_path": args.request,
        "reviewed_candidate_commit": (request.get("artifact") or {}).get("commit") if isinstance(request.get("artifact"), dict) else None,
        "request_hash": request.get("request_hash"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "trigger_sha": os.environ.get("GITHUB_SHA"),
        "job_status": args.job_status.lower(),
        "provider": envelope.get("provider") or workflow_status.get("provider"),
        "model": envelope.get("model") or workflow_status.get("model"),
        "provider_api_authenticated": envelope.get("provider_api_authenticated", False),
        "materialization_version": envelope.get("materialization_version") or workflow_status.get("materialization_version"),
        "evidence_ref_count": envelope.get("evidence_ref_count", corpus.get("evidence_ref_count")),
        "materialized_evidence_count": envelope.get("materialized_evidence_count", corpus.get("materialized_evidence_count")),
        "corpus_sha256": envelope.get("corpus_sha256", corpus.get("corpus_sha256")),
        "validation_valid": validation.get("valid") if validation else None,
        "disposition": review.get("disposition") if review else None,
        "dimensions": _dimension_summary(review),
        "findings_count": len(findings),
        "uncertainties_count": len(review.get("uncertainties", [])) if review and isinstance(review.get("uncertainties", []), list) else 0,
        "failure_detail": error_text or workflow_status.get("failure_detail"),
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
        "semantic_authority_note": "This summary is deterministic orchestration evidence only. It does not itself grant promotion authority.",
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
