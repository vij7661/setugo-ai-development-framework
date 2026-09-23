#!/usr/bin/env python3
"""R8 SPG-1 candidate provenance coverage validator.

NONAUTHORITATIVE. This tool cannot qualify itself or mint schema-freeze authority.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

FROZEN_CANDIDATE = "c721b38cf8b00294797300b526596ce723a47ff8"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "semantic_candidate_commit",
    "generator_binding",
    "allowed_output_schema_classes",
    "frozen_sources",
    "artifact",
    "provenance",
}
ALLOWED_TOP_LEVEL = set(REQUIRED_TOP_LEVEL)

GENERATOR_FIELDS = {
    "generator_id",
    "executable_digest",
    "runtime_manifest_digest",
    "workload_attestation_digest",
    "signing_credential_id",
    "generation_event_id",
}

PROVENANCE_FIELDS = {
    "json_pointer",
    "semantic_purpose",
    "source_design_ids",
    "sources",
    "reviewer_status",
}

class ValidationFailure(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def enumerate_nodes(value: Any, pointer: str = "") -> list[str]:
    """Return every JSON node pointer, including root, container and scalar nodes."""
    out = [pointer]
    if isinstance(value, dict):
        for key in sorted(value):
            out.extend(enumerate_nodes(value[key], pointer + "/" + _escape(str(key))))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            out.extend(enumerate_nodes(item, pointer + f"/{idx}"))
    return out


def canonical_json_bytes(value: Any) -> bytes:
    """Transport-only deterministic encoding. NOT a GCP-1 authority digest."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "plan must be an object")

    keys = set(plan)
    unknown = keys - ALLOWED_TOP_LEVEL
    missing = REQUIRED_TOP_LEVEL - keys
    if unknown or missing:
        raise ValidationFailure(
            "PLAN_SCHEMA_INVALID",
            f"unknown={sorted(unknown)} missing={sorted(missing)}",
        )

    if plan["schema_version"] != 1:
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "schema_version must be 1")

    if plan["semantic_candidate_commit"] != FROZEN_CANDIDATE:
        raise ValidationFailure(
            "FROZEN_CANDIDATE_MISMATCH",
            "semantic candidate does not equal frozen v15-r1 candidate",
        )

    binding = plan["generator_binding"]
    if not isinstance(binding, dict):
        raise ValidationFailure("GENERATOR_BINDING_INCOMPLETE", "binding must be object")
    missing_binding = GENERATOR_FIELDS - set(binding)
    if missing_binding or any(not binding.get(k) for k in GENERATOR_FIELDS):
        raise ValidationFailure(
            "GENERATOR_BINDING_INCOMPLETE",
            f"missing/empty={sorted(k for k in GENERATOR_FIELDS if not binding.get(k))}",
        )

    artifact = plan["artifact"]
    if not isinstance(artifact, dict) or set(artifact) != {"artifact_id", "schema_class", "schema_body"}:
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "artifact shape invalid")
    if not artifact["artifact_id"] or not artifact["schema_class"]:
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "artifact identity/class required")

    allowed_classes = plan["allowed_output_schema_classes"]
    if (
        not isinstance(allowed_classes, list)
        or len(allowed_classes) != len(set(allowed_classes))
        or artifact["schema_class"] not in allowed_classes
    ):
        raise ValidationFailure(
            "OUTPUT_SCHEMA_CLASS_UNAUTHORIZED",
            "schema class is not exactly allowed",
        )

    frozen_sources = plan["frozen_sources"]
    if not isinstance(frozen_sources, list) or not frozen_sources:
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "frozen_sources required")

    frozen_map: dict[tuple[str, str], bool] = {}
    for src in frozen_sources:
        if (
            not isinstance(src, dict)
            or set(src) != {"path", "blob", "authoritative"}
            or not src["path"]
            or not src["blob"]
            or not isinstance(src["authoritative"], bool)
        ):
            raise ValidationFailure("PLAN_SCHEMA_INVALID", "invalid frozen source")
        key = (src["path"], src["blob"])
        if key in frozen_map:
            raise ValidationFailure("PLAN_SCHEMA_INVALID", "duplicate frozen source")
        frozen_map[key] = src["authoritative"]

    provenance = plan["provenance"]
    if not isinstance(provenance, list):
        raise ValidationFailure("PLAN_SCHEMA_INVALID", "provenance must be list")

    provenance_by_pointer: dict[str, dict[str, Any]] = {}
    for entry in provenance:
        if not isinstance(entry, dict) or set(entry) != PROVENANCE_FIELDS:
            raise ValidationFailure("PLAN_SCHEMA_INVALID", "provenance entry shape invalid")
        ptr = entry["json_pointer"]
        if not isinstance(ptr, str):
            raise ValidationFailure("PLAN_SCHEMA_INVALID", "json_pointer must be string")
        if ptr in provenance_by_pointer:
            raise ValidationFailure("PROVENANCE_POINTER_DUPLICATE", ptr)
        if not entry["semantic_purpose"] or not entry["source_design_ids"]:
            raise ValidationFailure("PLAN_SCHEMA_INVALID", f"incomplete provenance at {ptr}")
        if not isinstance(entry["source_design_ids"], list):
            raise ValidationFailure("PLAN_SCHEMA_INVALID", f"source_design_ids at {ptr}")
        if not isinstance(entry["sources"], list) or not entry["sources"]:
            raise ValidationFailure("UNAUTHORIZED_SEMANTIC_SOURCE", f"no sources at {ptr}")

        has_authoritative = False
        for src in entry["sources"]:
            if not isinstance(src, dict) or set(src) != {"path", "blob"}:
                raise ValidationFailure("PLAN_SCHEMA_INVALID", f"invalid source at {ptr}")
            key = (src["path"], src["blob"])
            if key not in frozen_map:
                raise ValidationFailure("UNAUTHORIZED_SEMANTIC_SOURCE", f"{ptr}: {key}")
            has_authoritative = has_authoritative or frozen_map[key]
        if not has_authoritative:
            raise ValidationFailure("UNAUTHORIZED_SEMANTIC_SOURCE", f"no authoritative source at {ptr}")
        provenance_by_pointer[ptr] = entry

    nodes = enumerate_nodes(artifact["schema_body"])
    node_set = set(nodes)
    prov_set = set(provenance_by_pointer)

    missing_nodes = sorted(node_set - prov_set)
    if missing_nodes:
        raise ValidationFailure("PROVENANCE_COVERAGE_MISSING", repr(missing_nodes[:20]))

    unknown_ptrs = sorted(prov_set - node_set)
    if unknown_ptrs:
        raise ValidationFailure("PROVENANCE_POINTER_UNKNOWN", repr(unknown_ptrs[:20]))

    report_core = {
        "schema": "r8-spg1-candidate-validation-report/v1",
        "status": "VALID_CANDIDATE_PLAN",
        "authority_effect": "NONE",
        "qualified_schema_provenance_generator": False,
        "semantic_candidate_commit": FROZEN_CANDIDATE,
        "artifact_id": artifact["artifact_id"],
        "schema_class": artifact["schema_class"],
        "covered_node_count": len(nodes),
        "provenance_entry_count": len(provenance),
        "generator_id": binding["generator_id"],
        "runtime_manifest_digest": binding["runtime_manifest_digest"],
        "workload_attestation_digest": binding["workload_attestation_digest"],
        "signing_credential_id": binding["signing_credential_id"],
        "generation_event_id": binding["generation_event_id"],
        "note": "Candidate structural validation only; not GCP-1 schema digest or SPG-1 qualification.",
    }
    report = dict(report_core)
    report["candidate_transport_sha256"] = hashlib.sha256(
        canonical_json_bytes(report_core)
    ).hexdigest()
    return report


def evaluate(plan: dict[str, Any]) -> dict[str, Any]:
    try:
        return validate_plan(plan)
    except ValidationFailure as exc:
        return {
            "schema": "r8-spg1-candidate-validation-report/v1",
            "status": exc.code,
            "authority_effect": "NONE",
            "qualified_schema_provenance_generator": False,
            "detail": exc.detail,
        }
