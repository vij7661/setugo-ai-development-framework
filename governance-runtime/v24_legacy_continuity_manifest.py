from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from v24_legacy_inventory_candidate import derive_candidate_inventory
from v24_legacy_v7_classifier import classify_v5_v7

BASE_COMMIT = "a0c780b516b83ff8a1d0cdfd3724545d7dd6668b"
V24_MANUAL_ADDENDUM_PATH = "standards/external-manual-review-completeness-qualification-v24-addendum.md"
V24_MANUAL_ADDENDUM_BLOB = "d169181b9f444f40be717daefb819594b6961928"

# Exact inherited normative lineage derived from V24 -> V23 -> ... -> V5 bindings.
# Adjacent standards remain separate governance domains and are not silently folded
# into the WDPC continuity manifest.
INHERITED_ARTIFACT_PATHS = (
    "standards/external-manual-review-packet-control.md",
    "standards/conversation-drift-parent-child-impact-control.md",
    "standards/conversation-drift-parent-child-impact-control-v6-hardening.md",
    "standards/conversation-drift-parent-child-impact-control-v7-hardening.md",
    "standards/conversation-drift-parent-child-v7-active-clause-map.md",
    "standards/conversation-drift-parent-child-impact-control-v8-hardening.md",
    "standards/conversation-drift-parent-child-v8-precedence-and-evidence-map.md",
    "standards/conversation-drift-parent-child-impact-control-v9-hardening.md",
    "standards/conversation-drift-parent-child-v9-precedence-and-coverage-map.md",
    "standards/conversation-drift-parent-child-impact-control-v10-hardening.md",
    "standards/conversation-drift-parent-child-v10-precedence-and-review-map.md",
    "standards/conversation-drift-parent-child-impact-control-v11-hardening.md",
    "standards/conversation-drift-parent-child-v11-precedence-and-review-map.md",
    "standards/conversation-drift-parent-child-impact-control-v12-review-isolation.md",
    "standards/conversation-drift-parent-child-v12-independent-review-map.md",
    "standards/conversation-drift-parent-child-impact-control-v13-projection-assurance.md",
    "standards/conversation-drift-parent-child-v13-independent-review-assurance-map.md",
    "standards/conversation-drift-parent-child-impact-control-v14-review-proof.md",
    "standards/conversation-drift-parent-child-v14-review-proof-map.md",
    "standards/conversation-drift-parent-child-impact-control-v15-qualification-surface.md",
    "standards/conversation-drift-parent-child-v15-qualification-map.md",
    "standards/conversation-drift-parent-child-impact-control-v16-threshold-atomicity.md",
    "standards/conversation-drift-parent-child-v16-threshold-atomicity-map.md",
    "standards/conversation-drift-parent-child-impact-control-v17-threshold-ledger.md",
    "standards/conversation-drift-parent-child-v17-threshold-ledger-map.md",
    "standards/conversation-drift-parent-child-impact-control-v18-atomicity-lineage-hardening.md",
    "standards/conversation-drift-parent-child-v18-coverage-map.md",
    "standards/conversation-drift-parent-child-impact-control-v19-deterministic-reconciliation-enforcement-attestation.md",
    "standards/conversation-drift-parent-child-impact-control-v20-deterministic-authority-proof.md",
    "standards/conversation-drift-parent-child-impact-control-v21-authority-object-integrity.md",
    "standards/conversation-drift-parent-child-impact-control-v22-governance-root-closure.md",
    "standards/conversation-drift-parent-child-impact-control-v22-runtime-enforcement-addendum.md",
    "standards/conversation-drift-parent-child-impact-control-v22-self-activation-addendum.md",
    "standards/conversation-drift-parent-child-impact-control-v22-sink-fencing-addendum.md",
    "standards/conversation-drift-parent-child-impact-control-v23-completeness-hardening.md",
    "standards/conversation-drift-parent-child-impact-control-v23-endpoint-precedence-addendum.md",
    "standards/platform-root-meta-governance-closure.md",
    "standards/platform-root-meta-governance-runtime-enforcement-addendum.md",
    "standards/platform-root-meta-governance-self-activation-clarification.md",
    "standards/platform-root-meta-governance-sink-fencing-addendum.md",
    "standards/platform-governance-completeness-hardening-v23.md",
    "standards/platform-authority-endpoint-precedence-v23.md",
)

ADJACENT_SEPARATE_STANDARD_PATHS = (
    "standards/conversation-continuity-and-resumption-control.md",
    "standards/conversational-drift-contamination-control.md",
    "standards/external-evidence-semantic-validation.md",
    "standards/test-data-lifecycle-dependency.md",
)

EXPLICIT_V7_PATHS = {
    "standards/conversation-drift-parent-child-impact-control.md",
    "standards/conversation-drift-parent-child-impact-control-v6-hardening.md",
    "standards/conversation-drift-parent-child-impact-control-v7-hardening.md",
    "standards/conversation-drift-parent-child-v7-active-clause-map.md",
}


def _target(locator_id: str) -> str:
    return "INHERITED-" + locator_id


def build_legacy_continuity_manifest(repo_root: Path) -> dict[str, Any]:
    inventory = derive_candidate_inventory(repo_root)
    v7 = classify_v5_v7(repo_root)
    problems = list(inventory.get("problems", [])) + list(v7.get("problems", []))

    all_paths = {x["path"] for x in inventory.get("artifacts", [])}
    inherited_paths = set(INHERITED_ARTIFACT_PATHS)
    adjacent_paths = set(ADJACENT_SEPARATE_STANDARD_PATHS)

    missing_inherited = sorted(inherited_paths - all_paths)
    missing_adjacent = sorted(adjacent_paths - all_paths)
    unaccounted = sorted(all_paths - inherited_paths - adjacent_paths)
    overlap = sorted(inherited_paths & adjacent_paths)
    if missing_inherited:
        problems.extend(f"INHERITED_ARTIFACT_MISSING:{p}" for p in missing_inherited)
    if missing_adjacent:
        problems.extend(f"ADJACENT_STANDARD_MISSING:{p}" for p in missing_adjacent)
    if unaccounted:
        problems.extend(f"STANDARD_ARTIFACT_UNACCOUNTED:{p}" for p in unaccounted)
    if overlap:
        problems.extend(f"ARTIFACT_SCOPE_OVERLAP:{p}" for p in overlap)

    v7_by_key = {
        (r["artifact_path"], r["locator_id"]): r
        for r in v7.get("records", [])
    }

    inherited_inventory: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    pending_semantic: list[str] = []
    explicit_count = 0

    for item in inventory.get("legacy_clause_inventory", []):
        path = item["artifact_path"]
        if path not in inherited_paths:
            continue
        inherited_inventory.append(dict(item))
        key = (path, item["locator_id"])
        explicit = v7_by_key.get(key)
        if explicit is not None:
            records.append(dict(explicit))
            explicit_count += 1
            continue

        evidence: dict[str, Any]
        if path == "standards/external-manual-review-packet-control.md":
            evidence = {
                "evidence_class": "EXPLICIT_V24_SUPPLEMENT_BINDING",
                "artifact_path": V24_MANUAL_ADDENDUM_PATH,
                "blob_sha": V24_MANUAL_ADDENDUM_BLOB,
                "statement": "V24 completeness addendum supplements the existing external/manual review packet control",
            }
        else:
            evidence = {
                "evidence_class": "ADDITIVE_LINEAGE_CONSERVATIVE_ACTIVE",
                "v23_base_commit": BASE_COMMIT,
                "reason": "Included in exact additive WDPC/platform lineage and not explicitly dispositioned as superseded/reference-only by available predecessor map evidence",
            }

        records.append(
            {
                "artifact_path": path,
                "locator_id": item["locator_id"],
                "status": "ACTIVE_MAPPED",
                "target_control_id": _target(item["locator_id"]),
                "source_status": "ACTIVE_PENDING_EXPLICIT_CLAUSE_SEMANTICS",
                "classification_evidence": evidence,
                "semantic_disposition_state": "PENDING_EXPLICIT_CLAUSE_CLASSIFICATION",
            }
        )
        pending_semantic.append(f"{path}:{item['locator_id']}")

    inherited_artifacts = [
        dict(x) for x in inventory.get("artifacts", []) if x["path"] in inherited_paths
    ]
    adjacent_artifacts = [
        dict(x) for x in inventory.get("artifacts", []) if x["path"] in adjacent_paths
    ]

    active = [r for r in records if r["status"] == "ACTIVE_MAPPED"]
    superseded = [r for r in records if r["status"] == "SUPERSEDED"]
    reference = [r for r in records if r["status"] == "REFERENCE_ONLY"]

    # Exact construction invariants for the frozen V23 source tree.
    if len(inherited_artifacts) != 42:
        problems.append(f"INHERITED_ARTIFACT_COUNT_MISMATCH:{len(inherited_artifacts)}:42")
    if len(adjacent_artifacts) != 4:
        problems.append(f"ADJACENT_ARTIFACT_COUNT_MISMATCH:{len(adjacent_artifacts)}:4")
    if len(inherited_inventory) != 495:
        problems.append(f"INHERITED_CLAUSE_COUNT_MISMATCH:{len(inherited_inventory)}:495")
    if len(records) != len(inherited_inventory):
        problems.append("LEGACY_RECORD_SET_MISMATCH")
    if explicit_count != 69:
        problems.append(f"EXPLICIT_V5_V7_DISPOSITION_COUNT_MISMATCH:{explicit_count}:69")
    if len(active) != 493:
        problems.append(f"ACTIVE_INHERITED_COUNT_MISMATCH:{len(active)}:493")
    if len(superseded) != 1:
        problems.append(f"SUPERSEDED_INHERITED_COUNT_MISMATCH:{len(superseded)}:1")
    if len(reference) != 1:
        problems.append(f"REFERENCE_INHERITED_COUNT_MISMATCH:{len(reference)}:1")
    if len(pending_semantic) != 426:
        problems.append(f"PENDING_SEMANTIC_DISPOSITION_COUNT_MISMATCH:{len(pending_semantic)}:426")

    problems = sorted(set(problems))
    state = "LEGACY_CONTINUITY_CONSTRUCTION_COMPLETE" if not problems else "LEGACY_CONTINUITY_CONSTRUCTION_INVALID"
    return {
        "schema_version": 1,
        "artifact": "V24_LEGACY_CONTROL_CONTINUITY_MANIFEST",
        "state": state,
        "qualified": False,
        "v23_base_commit": BASE_COMMIT,
        "inherited_artifact_count": len(inherited_artifacts),
        "adjacent_separate_standard_count": len(adjacent_artifacts),
        "inherited_clause_count": len(inherited_inventory),
        "explicit_disposition_count": explicit_count,
        "active_mapped_count": len(active),
        "superseded_count": len(superseded),
        "reference_only_count": len(reference),
        "pending_semantic_disposition_count": len(pending_semantic),
        "inherited_artifacts": inherited_artifacts,
        "adjacent_separate_standards": adjacent_artifacts,
        "legacy_clause_inventory": inherited_inventory,
        "records": records,
        "pending_semantic_dispositions": pending_semantic,
        "problems": problems,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="..")
    parser.add_argument("--report")
    parser.add_argument("--expect-construction-complete", action="store_true")
    args = parser.parse_args()

    result = build_legacy_continuity_manifest(Path(args.repo_root).resolve())
    rendered = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.expect_construction_complete:
        ok = (
            result["state"] == "LEGACY_CONTINUITY_CONSTRUCTION_COMPLETE"
            and result["qualified"] is False
            and result["inherited_artifact_count"] == 42
            and result["adjacent_separate_standard_count"] == 4
            and result["inherited_clause_count"] == 495
            and result["active_mapped_count"] == 493
            and result["superseded_count"] == 1
            and result["reference_only_count"] == 1
            and result["pending_semantic_disposition_count"] == 426
            and not result["problems"]
        )
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
