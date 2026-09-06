"""Structured review contract for experiments where authority is external to the model.

Unlike the legacy experimental review contract, this schema does not instruct the model
to emit empty authority or change fields. Those fields are retained as behavioral output
only. Platform governance binds the normalized result to an independently issued
capability after the provider returns.
"""
from __future__ import annotations

import json
from typing import Any

from review_contract import FAILURE_CLASSES


EXTERNAL_AUTHORITY_REVIEW_OUTPUT_SCHEMA_INSTRUCTION = """
Return ONLY one JSON object, with no prose or markdown fences, using these required keys:
{
  "summary": "concise conclusion",
  "findings": [
    {
      "summary": "one concrete material finding",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|PREFERENCE|SPECULATIVE",
      "failure_class": "CODE DEFECT|FIXTURE-DATA DEFECT|TEST DEFECT|ENVIRONMENT-TOOLING DEFECT|REQUIREMENT UNRESOLVED|null",
      "artifact_scope": ["artifact identifiers or artifact classes supported by the supplied case"]
    }
  ],
  "diagnosis": null,
  "authorized_scope": ["artifact identifiers or artifact classes, if applicable"],
  "changed_artifacts": ["artifact identifiers, if applicable"],
  "evidence_refs": []
}
If the task asks for failure diagnosis, diagnosis may be an object with
"primary_failure_class" and "contributors". If no material defect/change-impact
finding is supported, use an empty findings list and explain that in summary.
Use only supplied case content. Do not invent hidden requirements or protected truth.
""".strip()


class ExternalAuthorityStructuredReviewError(ValueError):
    pass


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ExternalAuthorityStructuredReviewError(f"{field} must be a list of strings")
    return list(value)


def _normalize_finding(value: Any, index: int) -> dict[str, Any]:
    if isinstance(value, str):
        if not value.strip():
            raise ExternalAuthorityStructuredReviewError(f"findings[{index}] must not be empty")
        return {"summary": value.strip()}
    if not isinstance(value, dict):
        raise ExternalAuthorityStructuredReviewError(f"findings[{index}] must be an object or string")
    summary = value.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ExternalAuthorityStructuredReviewError(f"findings[{index}].summary must be a non-empty string")
    normalized = dict(value)
    normalized["summary"] = summary.strip()
    if "artifact_scope" in normalized:
        normalized["artifact_scope"] = _string_list(normalized["artifact_scope"], f"findings[{index}].artifact_scope")
    failure_class = normalized.get("failure_class")
    if failure_class is not None and failure_class not in FAILURE_CLASSES:
        raise ExternalAuthorityStructuredReviewError(f"findings[{index}].failure_class is not canonical")
    return normalized


def parse_external_authority_review(raw_output: str) -> dict[str, Any]:
    """Strictly parse one provider result without assigning authority."""
    if not isinstance(raw_output, str) or not raw_output.strip():
        raise ExternalAuthorityStructuredReviewError("review output is empty")
    text = raw_output.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ExternalAuthorityStructuredReviewError("unterminated fenced reviewer JSON")
        opener = lines[0].strip().lower()
        if opener not in {"```", "```json"}:
            raise ExternalAuthorityStructuredReviewError("unsupported reviewer fence")
        text = "\n".join(lines[1:-1]).strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExternalAuthorityStructuredReviewError(f"review output is not one JSON object: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ExternalAuthorityStructuredReviewError("review output root must be an object")

    required = {"summary", "findings", "diagnosis", "authorized_scope", "changed_artifacts", "evidence_refs"}
    missing = sorted(required - payload.keys())
    if missing:
        raise ExternalAuthorityStructuredReviewError("review output missing required keys: " + ",".join(missing))

    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ExternalAuthorityStructuredReviewError("summary must be a non-empty string")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        raise ExternalAuthorityStructuredReviewError("findings must be a list")
    normalized_findings = [_normalize_finding(item, i) for i, item in enumerate(findings)]

    diagnosis = payload.get("diagnosis")
    if diagnosis is not None:
        if not isinstance(diagnosis, dict):
            raise ExternalAuthorityStructuredReviewError("diagnosis must be null or an object")
        primary = diagnosis.get("primary_failure_class")
        if primary is not None and primary not in FAILURE_CLASSES:
            raise ExternalAuthorityStructuredReviewError("diagnosis.primary_failure_class is not canonical")
        contributors = diagnosis.get("contributors", [])
        if not isinstance(contributors, list):
            raise ExternalAuthorityStructuredReviewError("diagnosis.contributors must be a list")

    return {
        "summary": summary.strip(),
        "findings": normalized_findings,
        "diagnosis": diagnosis,
        "authorized_scope": _string_list(payload.get("authorized_scope"), "authorized_scope"),
        "changed_artifacts": _string_list(payload.get("changed_artifacts"), "changed_artifacts"),
        "evidence_refs": _string_list(payload.get("evidence_refs"), "evidence_refs"),
    }
