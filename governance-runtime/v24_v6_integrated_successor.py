"""V24 I11 V6 R9: integrated successor construction/freeze preflight.

This module binds the repaired R1-R8 surface and verifies integration metadata.
It is construction-only.  It cannot open scientific execution, qualify the
candidate, or grant release/deployment/production/terminal authority.
"""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, digest

EXPECTED_WORKSTREAMS = tuple(f"R{i}" for i in range(1, 9))
EXPECTED_PRODUCTION_MODULES = {
    "R1": "governance-runtime/v24_v6_governance_foundation.py",
    "R2": "governance-runtime/v24_v6_endpoint_projection.py",
    "R3": "governance-runtime/v24_v6_material_surface.py",
    "R4": "governance-runtime/v24_v6_decision_apply.py",
    "R5": "governance-runtime/v24_v6_normative_clause_projection.py",
    "R6": "governance-runtime/v24_v6_effect_ledger_closure.py",
    "R7": "governance-runtime/v24_v6_atomic_binding_modes.py",
    "R8": "governance-runtime/v24_v6_qualification_integrity.py",
}
EXPECTED_EVIDENCE_FILES = {
    f"R{i}": f"implementation/v24/V24-I11-V6-R{i}-CONSTRUCTION-EVIDENCE.md"
    for i in range(1, 9)
}
SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _git_sha1(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def _safe_path(v: Any) -> str | None:
    if not isinstance(v, str) or not v:
        return None
    p = PurePosixPath(v)
    if p.is_absolute() or ".." in p.parts or any(part in {"", "."} for part in p.parts):
        return None
    return p.as_posix()


def _read(repo_root: Path, repo_path: str) -> bytes:
    root = repo_root.resolve()
    target = (root / repo_path).resolve()
    target.relative_to(root)
    return target.read_bytes()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_integrated_successor_manifest(
    *, repo_root: str | Path, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate exact R1-R8 successor-surface binding and closed execution gate."""
    p: list[str] = []
    root = Path(repo_root)
    if manifest.get("schema_version") != 1:
        p.append("INTEGRATED_SUCCESSOR_SCHEMA_INVALID")
    for key in (
        "candidate_family_id",
        "approved_design_packet_sha256",
        "approved_design_body_sha256",
        "frozen_i10_commit",
        "frozen_i10_tree",
        "implementation_lineage_root_commit",
    ):
        if not _nonempty(manifest.get(key)):
            p.append(f"INTEGRATED_SUCCESSOR_FIELD_REQUIRED:{key}")
    for key in ("approved_design_packet_sha256", "approved_design_body_sha256"):
        if not _sha256(manifest.get(key)):
            p.append(f"INTEGRATED_SUCCESSOR_SHA256_INVALID:{key}")
    for key in ("frozen_i10_commit", "frozen_i10_tree", "implementation_lineage_root_commit"):
        if not _git_sha1(manifest.get(key)):
            p.append(f"INTEGRATED_SUCCESSOR_GIT_ID_INVALID:{key}")

    if manifest.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        p.append("INTEGRATED_SUCCESSOR_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if manifest.get("authority_effect") != AUTHORITY_EFFECT:
        p.append("INTEGRATED_SUCCESSOR_AUTHORITY_EFFECT_INVALID")

    workstreams = manifest.get("workstreams")
    if not isinstance(workstreams, list):
        workstreams = []
        p.append("INTEGRATED_SUCCESSOR_WORKSTREAMS_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    for idx, item in enumerate(workstreams):
        if not isinstance(item, Mapping):
            p.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_MALFORMED:{idx}")
            continue
        wid = item.get("workstream_id")
        if wid not in EXPECTED_WORKSTREAMS:
            p.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_ID_INVALID:{wid}")
            continue
        if wid in by_id:
            p.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_DUPLICATE:{wid}")
            continue
        by_id[wid] = item

    if set(by_id) != set(EXPECTED_WORKSTREAMS):
        for missing in sorted(set(EXPECTED_WORKSTREAMS) - set(by_id)):
            p.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_MISSING:{missing}")

    bound_files: list[dict[str, Any]] = []
    for wid in EXPECTED_WORKSTREAMS:
        item = by_id.get(wid)
        if item is None:
            continue
        expected_module = EXPECTED_PRODUCTION_MODULES[wid]
        expected_evidence = EXPECTED_EVIDENCE_FILES[wid]
        if item.get("production_module_path") != expected_module:
            p.append(f"INTEGRATED_SUCCESSOR_PRODUCTION_PATH_MISMATCH:{wid}")
        if item.get("construction_evidence_path") != expected_evidence:
            p.append(f"INTEGRATED_SUCCESSOR_EVIDENCE_PATH_MISMATCH:{wid}")
        if item.get("construction_state") != "PASS":
            p.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_NOT_PASS:{wid}")
        if item.get("runtime_qualification_state") != "NOT_CLAIMED":
            p.append(f"INTEGRATED_SUCCESSOR_RUNTIME_QUALIFICATION_CLAIMED:{wid}")
        for role, expected_path in (
            ("production", expected_module),
            ("evidence", expected_evidence),
        ):
            supplied_path = item.get(f"{role}_path") if role == "evidence" else item.get("production_module_path")
            if role == "evidence":
                supplied_path = item.get("construction_evidence_path")
            safe = _safe_path(supplied_path)
            if safe != expected_path:
                continue
            try:
                data = _read(root, safe)
            except Exception:
                p.append(f"INTEGRATED_SUCCESSOR_BOUND_FILE_MISSING:{wid}:{role}")
                continue
            actual_blob = git_blob_sha(data)
            actual_sha256 = sha256_bytes(data)
            if item.get(f"{role}_git_blob_sha") != actual_blob:
                p.append(f"INTEGRATED_SUCCESSOR_BLOB_MISMATCH:{wid}:{role}")
            if item.get(f"{role}_sha256") != actual_sha256:
                p.append(f"INTEGRATED_SUCCESSOR_CONTENT_SHA256_MISMATCH:{wid}:{role}")
            bound_files.append({
                "workstream_id": wid,
                "role": role,
                "path": safe,
                "git_blob_sha": actual_blob,
                "sha256": actual_sha256,
            })

    mandatory_checks = manifest.get("mandatory_v6_adversarial_checks")
    required_checks = {
        "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
        "EVERY_REACHABLE_TERMINAL_ALLOWED",
        "GENESIS_CROSS_PAIR_REJECTED",
        "APPLICABLE_PREDICATE_OMISSION_REJECTED",
        "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
        "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
    }
    if not isinstance(mandatory_checks, list):
        mandatory_checks = []
        p.append("INTEGRATED_SUCCESSOR_MANDATORY_CHECKS_REQUIRED")
    if set(mandatory_checks) != required_checks:
        for missing in sorted(required_checks - set(mandatory_checks)):
            p.append(f"INTEGRATED_SUCCESSOR_MANDATORY_CHECK_MISSING:{missing}")
        for extra in sorted(set(mandatory_checks) - required_checks):
            p.append(f"INTEGRATED_SUCCESSOR_MANDATORY_CHECK_UNKNOWN:{extra}")

    p = sorted(set(p))
    material = {
        "candidate_family_id": manifest.get("candidate_family_id"),
        "approved_design_packet_sha256": manifest.get("approved_design_packet_sha256"),
        "approved_design_body_sha256": manifest.get("approved_design_body_sha256"),
        "frozen_i10_commit": manifest.get("frozen_i10_commit"),
        "frozen_i10_tree": manifest.get("frozen_i10_tree"),
        "scientific_execution_state": manifest.get("scientific_execution_state"),
        "bound_files": sorted(bound_files, key=lambda x: (x["workstream_id"], x["role"])),
        "mandatory_v6_adversarial_checks": sorted(required_checks),
    }
    return {
        "state": "V24_V6_INTEGRATED_SUCCESSOR_BOUND" if not p else "V24_V6_INTEGRATED_SUCCESSOR_INVALID",
        "qualified": False,
        "integration_valid": not p,
        "problems": p,
        "binding_digest": digest(material),
        "bound_file_count": len(bound_files),
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R9_INTEGRATED_SUCCESSOR_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R9",
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }
