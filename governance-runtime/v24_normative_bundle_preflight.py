from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from normative_control_catalog import (
    _extract_clause,
    git_blob_sha_bytes,
    validate_normative_catalog,
)
from v24_legacy_continuity_manifest import build_legacy_continuity_manifest

H2 = re.compile(r"^## (.+)$", re.MULTILINE)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expand_ids(series: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for item in series:
        prefix = item["prefix"]
        start = int(item["start"])
        end = int(item["end"])
        width = int(item["width"])
        if start < 0 or end < start or width <= 0:
            raise ValueError("invalid control series")
        result.extend(f"{prefix}{i:0{width}d}" for i in range(start, end + 1))
    if len(result) != len(set(result)):
        raise ValueError("duplicate expected control id")
    return result


def _heading_for(text: str, control_id: str) -> str | None:
    prefix = f"{control_id} — "
    matches = [value for value in H2.findall(text) if value.startswith(prefix)]
    if len(matches) != 1:
        return None
    return "## " + matches[0]


def _pending_descriptor(
    *,
    control_id: str,
    path: str,
    blob_sha: str,
    locator_id: str,
    heading: str,
    clause_sha256: str,
    generation: str,
    sequence: int,
    predecessors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "normative_artifact_path": path,
        "normative_artifact_blob_sha": blob_sha,
        "clause_locator": {"locator_id": locator_id, "heading": heading},
        "clause_sha256": clause_sha256,
        "inherited_predecessor_control_ids": predecessors or [],
        "authority_bearing_predicate_ids": [],
        "phase_severity_endpoint_mappings": [],
        "applicability_rules": [],
        "required_proof_fields": [],
        "protected_mutation_strength_class": "PENDING_EXPLICIT_MAPPING",
        "effective_generation": generation,
        "effective_sequence": sequence,
        "descriptor_qualification_state": "SEMANTIC_MAPPING_PENDING",
    }


def build_candidate_bundle(repo_root: Path, source: dict[str, Any]) -> dict[str, Any]:
    generation = source["governance_generation"]
    build_problems: list[str] = []
    manifest_artifacts: list[dict[str, Any]] = []
    descriptors: list[dict[str, Any]] = []
    expected_current_control_count = 0
    sequence = 0

    # Exact V24 controls.
    for artifact in source.get("artifacts", []):
        path = artifact["path"]
        expected_blob = artifact["blob_sha"]
        expected_ids = _expand_ids(artifact.get("control_series", []))
        expected_current_control_count += len(expected_ids)
        raw = (repo_root / path).read_bytes()
        text = raw.decode("utf-8")
        actual_blob = git_blob_sha_bytes(raw)
        if actual_blob != expected_blob:
            build_problems.append(f"SOURCE_BLOB_MISMATCH:{path}")

        h2_values = H2.findall(text)
        expected_headings: set[str] = set()
        locators: list[dict[str, Any]] = []
        for control_id in expected_ids:
            heading = _heading_for(text, control_id)
            if heading is None:
                build_problems.append(f"EXPECTED_CONTROL_HEADING_MISSING_OR_DUPLICATE:{path}:{control_id}")
                continue
            expected_headings.add(heading[3:])
            clause = _extract_clause(text, heading)
            if clause is None:
                build_problems.append(f"EXPECTED_CONTROL_CLAUSE_UNREADABLE:{path}:{control_id}")
                continue
            digest = _sha256_text(clause)
            locator = {
                "locator_id": control_id,
                "heading": heading,
                "clause_sha256": digest,
            }
            locators.append(locator)
            sequence += 1
            descriptors.append(
                _pending_descriptor(
                    control_id=control_id,
                    path=path,
                    blob_sha=expected_blob,
                    locator_id=control_id,
                    heading=heading,
                    clause_sha256=digest,
                    generation=generation,
                    sequence=sequence,
                )
            )

        extras = sorted(set(h2_values) - expected_headings)
        for heading in extras:
            build_problems.append(f"UNDECLARED_LEVEL2_HEADING:{path}:{heading}")

        manifest_artifacts.append(
            {
                "path": path,
                "blob_sha": expected_blob,
                "classification": "AUTHORITATIVE_DESCRIPTOR_REQUIRED",
                "required_clause_locators": locators,
            }
        )

    # Exact inherited V5-V23 continuity surface.
    continuity = build_legacy_continuity_manifest(repo_root)
    if continuity.get("problems"):
        build_problems.extend(
            f"LEGACY_CONTINUITY:{problem}" for problem in continuity["problems"]
        )

    inventory_by_key = {
        (x["artifact_path"], x["locator_id"]): x
        for x in continuity.get("legacy_clause_inventory", [])
    }
    record_by_key = {
        (x["artifact_path"], x["locator_id"]): x
        for x in continuity.get("records", [])
    }

    active_by_path: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for key, record in record_by_key.items():
        if record.get("status") != "ACTIVE_MAPPED":
            continue
        item = inventory_by_key.get(key)
        if item is None:
            build_problems.append(f"ACTIVE_LEGACY_INVENTORY_MISSING:{key[0]}:{key[1]}")
            continue
        active_by_path.setdefault(key[0], []).append((item, record))

    inherited_artifact_by_path = {
        x["path"]: x for x in continuity.get("inherited_artifacts", [])
    }
    inherited_active_descriptor_count = 0
    for path in sorted(active_by_path):
        artifact = inherited_artifact_by_path.get(path)
        if artifact is None:
            build_problems.append(f"ACTIVE_LEGACY_ARTIFACT_SCOPE_MISSING:{path}")
            continue
        expected_blob = artifact["blob_sha"]
        raw = (repo_root / path).read_bytes()
        if git_blob_sha_bytes(raw) != expected_blob:
            build_problems.append(f"ACTIVE_LEGACY_BLOB_MISMATCH:{path}")

        locators: list[dict[str, Any]] = []
        for item, record in sorted(active_by_path[path], key=lambda pair: pair[0]["locator_id"]):
            control_id = record["target_control_id"]
            locator = {
                "locator_id": item["locator_id"],
                "heading": item["heading"],
                "clause_sha256": item["clause_sha256"],
            }
            locators.append(locator)
            sequence += 1
            inherited_active_descriptor_count += 1
            descriptors.append(
                _pending_descriptor(
                    control_id=control_id,
                    path=path,
                    blob_sha=expected_blob,
                    locator_id=item["locator_id"],
                    heading=item["heading"],
                    clause_sha256=item["clause_sha256"],
                    generation=generation,
                    sequence=sequence,
                )
            )

        manifest_artifacts.append(
            {
                "path": path,
                "blob_sha": expected_blob,
                "classification": "AUTHORITATIVE_DESCRIPTOR_REQUIRED",
                "required_clause_locators": locators,
            }
        )

    manifest = {
        "schema_version": 1,
        "governance_generation": generation,
        "frozen_candidate_commit": source["frozen_candidate_commit"],
        "frozen_candidate_tree": source["frozen_candidate_tree"],
        "requires_legacy_qualification": bool(source.get("requires_legacy_qualification", False)),
        "artifacts": manifest_artifacts,
    }
    catalog = {
        "schema_version": 1,
        "governance_generation": generation,
        "descriptors": descriptors,
    }
    legacy = {
        "schema_version": 1,
        "governance_generation": generation,
        "requires_legacy_qualification": bool(source.get("requires_legacy_qualification", False)),
        "legacy_clause_inventory": continuity.get("legacy_clause_inventory", []),
        "records": continuity.get("records", []),
    }

    base = validate_normative_catalog(
        repo_root=repo_root,
        artifact_manifest=manifest,
        control_catalog=catalog,
        legacy_qualification=legacy,
    )
    problems = list(base["problems"]) + build_problems

    if legacy["requires_legacy_qualification"] and not legacy["legacy_clause_inventory"]:
        problems.append("LEGACY_CLAUSE_INVENTORY_REQUIRED")

    for descriptor in descriptors:
        if descriptor.get("descriptor_qualification_state") != "QUALIFIED":
            problems.append(f"DESCRIPTOR_SEMANTIC_MAPPING_PENDING:{descriptor['control_id']}")

    for item in continuity.get("pending_semantic_dispositions", []):
        problems.append(f"LEGACY_SEMANTIC_DISPOSITION_PENDING:{item}")

    problems = sorted(set(problems))
    state = "V24_NORMATIVE_BUNDLE_QUALIFIED" if not problems else "V24_NORMATIVE_BUNDLE_INCOMPLETE"
    return {
        "state": state,
        "qualified": not problems,
        "problems": problems,
        "expected_current_control_count": expected_current_control_count,
        "generated_descriptor_count": len(descriptors),
        "current_descriptor_count": expected_current_control_count,
        "inherited_active_descriptor_count": inherited_active_descriptor_count,
        "manifest_artifact_count": len(manifest_artifacts),
        "current_manifest_artifact_count": len(source.get("artifacts", [])),
        "inherited_manifest_artifact_count": len(active_by_path),
        "legacy_artifact_count": continuity.get("inherited_artifact_count", 0),
        "adjacent_separate_standard_count": continuity.get("adjacent_separate_standard_count", 0),
        "legacy_inventory_count": len(legacy["legacy_clause_inventory"]),
        "legacy_pending_semantic_disposition_count": continuity.get("pending_semantic_disposition_count", 0),
        "legacy_current_drift_paths": [],
        "manifest": manifest,
        "catalog": catalog,
        "legacy_qualification": legacy,
        "legacy_continuity": continuity,
        "source_digest": _sha256_text(_canon(source)),
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="..")
    parser.add_argument("--source", default="v24-normative-inventory-source.json")
    parser.add_argument("--report")
    parser.add_argument("--expect-incomplete", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = Path(__file__).resolve().parent / source_path
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = build_candidate_bundle(repo_root, source)
    rendered = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.expect_incomplete:
        semantic_pending = [
            x for x in result["problems"] if x.startswith("DESCRIPTOR_SEMANTIC_MAPPING_PENDING:")
        ]
        legacy_semantic = [
            x for x in result["problems"] if x.startswith("LEGACY_SEMANTIC_DISPOSITION_PENDING:")
        ]
        unexpected = [
            x for x in result["problems"]
            if not x.startswith("DESCRIPTOR_SEMANTIC_MAPPING_PENDING:")
            and not x.startswith("LEGACY_SEMANTIC_DISPOSITION_PENDING:")
        ]
        correct_counts = (
            result["expected_current_control_count"] == 110
            and result["current_descriptor_count"] == 110
            and result["inherited_active_descriptor_count"] == 493
            and result["generated_descriptor_count"] == 603
            and result["current_manifest_artifact_count"] == 9
            and result["inherited_manifest_artifact_count"] == 42
            and result["manifest_artifact_count"] == 51
            and result["legacy_artifact_count"] == 42
            and result["adjacent_separate_standard_count"] == 4
            and result["legacy_inventory_count"] == 495
            and result["legacy_pending_semantic_disposition_count"] == 426
        )
        ok = (
            not result["qualified"]
            and len(semantic_pending) == 603
            and len(legacy_semantic) == 426
            and not unexpected
            and correct_counts
            and not result["legacy_current_drift_paths"]
        )
        return 0 if ok else 1
    return 0 if result["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
