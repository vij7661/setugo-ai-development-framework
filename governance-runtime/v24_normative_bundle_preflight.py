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


def build_candidate_bundle(repo_root: Path, source: dict[str, Any]) -> dict[str, Any]:
    generation = source["governance_generation"]
    build_problems: list[str] = []
    manifest_artifacts: list[dict[str, Any]] = []
    descriptors: list[dict[str, Any]] = []
    expected_control_count = 0
    sequence = 0

    for artifact in source.get("artifacts", []):
        path = artifact["path"]
        expected_blob = artifact["blob_sha"]
        expected_ids = _expand_ids(artifact.get("control_series", []))
        expected_control_count += len(expected_ids)
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
                {
                    "control_id": control_id,
                    "normative_artifact_path": path,
                    "normative_artifact_blob_sha": expected_blob,
                    "clause_locator": {"locator_id": control_id, "heading": heading},
                    "clause_sha256": digest,
                    "inherited_predecessor_control_ids": [],
                    "authority_bearing_predicate_ids": [],
                    "phase_severity_endpoint_mappings": [],
                    "applicability_rules": [],
                    "required_proof_fields": [],
                    "protected_mutation_strength_class": "PENDING_EXPLICIT_MAPPING",
                    "effective_generation": generation,
                    "effective_sequence": sequence,
                    "descriptor_qualification_state": "SEMANTIC_MAPPING_PENDING",
                }
            )

        extras = sorted(set(h2_values) - expected_headings)
        if extras:
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
        "legacy_clause_inventory": source.get("legacy_clause_inventory", []),
        "records": source.get("legacy_qualification_records", []),
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

    problems = sorted(set(problems))
    state = "V24_NORMATIVE_BUNDLE_QUALIFIED" if not problems else "V24_NORMATIVE_BUNDLE_INCOMPLETE"
    return {
        "state": state,
        "qualified": not problems,
        "problems": problems,
        "expected_control_count": expected_control_count,
        "generated_descriptor_count": len(descriptors),
        "manifest_artifact_count": len(manifest_artifacts),
        "legacy_inventory_count": len(legacy["legacy_clause_inventory"]),
        "manifest": manifest,
        "catalog": catalog,
        "legacy_qualification": legacy,
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
        required = {
            "LEGACY_CLAUSE_INVENTORY_REQUIRED",
        }
        prefix_present = any(x.startswith("DESCRIPTOR_SEMANTIC_MAPPING_PENDING:") for x in result["problems"])
        correct_count = result["expected_control_count"] == 110 and result["generated_descriptor_count"] == 110
        return 0 if (not result["qualified"] and required.issubset(result["problems"]) and prefix_present and correct_count) else 1
    return 0 if result["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
