#!/usr/bin/env python3
"""Require reviewer change recommendations and claimed impacts to be independently reconciled."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

CHANGE_REQUIRED_VALUES = {"YES", "NO", "INSUFFICIENT_EVIDENCE"}
REMEDIATION_DECISIONS = {
    "ADOPT",
    "ADOPT_WITH_MODIFICATION",
    "REJECT_FIX_ACCEPT_FINDING",
    "REJECT_FINDING",
    "DEFER_INSUFFICIENT_EVIDENCE",
}
CLAIM_DISPOSITIONS = {
    "DIRECT_CHANGE",
    "TRANSITIVE_CHANGE",
    "TEST_OR_EVIDENCE_CHANGE",
    "NO_CHANGE_REQUIRED",
    "REVIEWER_CLAIM_REJECTED",
    "UNRESOLVED",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _str_list(value: Any) -> list[str]:
    return [x for x in value if isinstance(x, str) and x] if isinstance(value, list) else []


def validate_reviewer_change_reconciliation(manifest: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    findings = manifest.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("REVIEWER_RECONCILIATION_FINDINGS_REQUIRED")
        findings = []

    impact = manifest.get("impact_manifest")
    if not isinstance(impact, Mapping):
        errors.append("REVIEWER_RECONCILIATION_IMPACT_MANIFEST_REQUIRED")
        impact = {}

    direct = set(_str_list(impact.get("direct_paths")))
    transitive = set(_str_list(impact.get("transitive_paths")))
    no_change = set(_str_list(impact.get("no_change_required_paths")))
    claim_recon = impact.get("reviewer_claim_reconciliation")
    if claim_recon is None:
        claim_recon = {}
    if not isinstance(claim_recon, Mapping):
        errors.append("REVIEWER_CLAIM_RECONCILIATION_MAP_INVALID")
        claim_recon = {}

    seen: set[str] = set()
    for idx, finding in enumerate(findings):
        if not isinstance(finding, Mapping):
            errors.append(f"REVIEWER_FINDING_MALFORMED:{idx}")
            continue
        fid = finding.get("id")
        if not _nonempty(fid) or fid in seen:
            errors.append(f"REVIEWER_FINDING_ID_INVALID:{idx}")
            continue
        fid = str(fid)
        seen.add(fid)
        if finding.get("disposition") == "PACKET_PROCESS_DEFECT":
            continue

        review = finding.get("reviewer_change_assessment")
        if not isinstance(review, Mapping):
            errors.append(f"REVIEWER_CHANGE_ASSESSMENT_REQUIRED:{fid}")
            continue
        changes_required = review.get("changes_required")
        if changes_required not in CHANGE_REQUIRED_VALUES:
            errors.append(f"REVIEWER_CHANGES_REQUIRED_VALUE_INVALID:{fid}")
        if changes_required == "YES":
            for field in (
                "minimum_required_change",
                "why_required",
                "regression_risks",
                "evidence_to_verify_fix",
            ):
                value = review.get(field)
                if field == "regression_risks":
                    if not isinstance(value, list):
                        errors.append(f"REVIEWER_CHANGE_FIELD_REQUIRED:{fid}:{field}")
                elif not _nonempty(value):
                    errors.append(f"REVIEWER_CHANGE_FIELD_REQUIRED:{fid}:{field}")
            if not isinstance(review.get("affected_existing_surfaces"), list):
                errors.append(f"REVIEWER_AFFECTED_SURFACES_REQUIRED:{fid}")
        if changes_required == "INSUFFICIENT_EVIDENCE" and not _str_list(review.get("missing_evidence")):
            errors.append(f"REVIEWER_MISSING_EVIDENCE_REQUIRED:{fid}")

        independent = finding.get("independent_change_assessment")
        if not isinstance(independent, Mapping):
            errors.append(f"INDEPENDENT_CHANGE_ASSESSMENT_REQUIRED:{fid}")
            continue
        decision = independent.get("reviewer_proposal_decision")
        if decision not in REMEDIATION_DECISIONS:
            errors.append(f"INDEPENDENT_REMEDIATION_DECISION_INVALID:{fid}")
        if not _nonempty(independent.get("rationale")):
            errors.append(f"INDEPENDENT_REMEDIATION_RATIONALE_REQUIRED:{fid}")
        if not _nonempty(independent.get("evidence")):
            errors.append(f"INDEPENDENT_REMEDIATION_EVIDENCE_REQUIRED:{fid}")
        if independent.get("reviewer_change_considered") is not True:
            errors.append(f"REVIEWER_CHANGE_NOT_CONSIDERED:{fid}")

        claimed = _str_list(review.get("affected_existing_surfaces"))
        for surface in claimed:
            if surface in direct or surface in transitive or surface in no_change:
                continue
            item = claim_recon.get(surface)
            if not isinstance(item, Mapping):
                errors.append(f"REVIEWER_IMPACT_CLAIM_UNRESOLVED:{fid}:{surface}")
                continue
            disp = item.get("disposition")
            if disp not in CLAIM_DISPOSITIONS:
                errors.append(f"REVIEWER_IMPACT_CLAIM_DISPOSITION_INVALID:{fid}:{surface}")
                continue
            if disp == "UNRESOLVED":
                errors.append(f"REVIEWER_IMPACT_CLAIM_UNRESOLVED:{fid}:{surface}")
            if disp in {"NO_CHANGE_REQUIRED", "REVIEWER_CLAIM_REJECTED"}:
                if not _nonempty(item.get("rationale")) or not _nonempty(item.get("evidence")):
                    errors.append(f"REVIEWER_IMPACT_CLAIM_EVIDENCE_REQUIRED:{fid}:{surface}")

    return {
        "schema_version": 1,
        "result": "REVIEWER_CHANGE_RECONCILED" if not errors else "REVIEWER_CHANGE_NOT_RECONCILED",
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report = validate_reviewer_change_reconciliation(manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "REVIEWER_CHANGE_RECONCILED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
