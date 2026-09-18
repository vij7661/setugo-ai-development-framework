"""V24 I11 V6 R9 integrated-successor construction/freeze preflight.

The committed manifest binds the exact approved V6 design identity, R1-R8
workstream artifacts, their construction evidence, and every audited local
load-bearing production dependency by exact Git object identity. This verifier
recomputes raw SHA-256 for the same bytes. It is construction-only and cannot
open scientific execution or grant runtime, qualification, release, deployment,
or terminal authority.
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
# Audited local leaves outside the eight headline workstream modules whose bytes
# can change R1-R8 semantics. R4/R6 also depend on R3, which is already bound as
# a workstream module; the resolver depends only on already-bound R1.
EXPECTED_SHARED_PRODUCTION_DEPENDENCIES = {
    "PROOF_REFERENCE_CLOSURE": "governance-runtime/v24_v6_proof_reference_closure.py",
    "CONSTRUCTION_ROOT_ATTESTATION_VERIFIER": "governance-runtime/v24_v6_root_attestation.py",
    "CONSTRUCTION_ROOT_PUBLIC_ARTIFACT": "governance-runtime/fixtures/v24-v6-construction-root-attestation-v3.json",
    "ENDPOINT_PROOF_COMPILER": "governance-runtime/v24_endpoint_proof_compiler.py",
    "NORMATIVE_CONTROL_CATALOG": "governance-runtime/normative_control_catalog.py",
    "INTEGRATED_SUCCESSOR_VALIDATOR": "governance-runtime/v24_v6_integrated_successor.py",
    "EXTERNAL_AUTHORITY_GATE_SOURCE": "governance-runtime/native/v24_v6_external_authority_gate.c",
    "EXTERNAL_AUTHORITY_GATE_BUILD_SCRIPT": "governance-runtime/build_v24_v6_external_authority_gate.sh",
    "EXTERNAL_AUTHORITY_GATE_WORKER": "governance-runtime/v24_v6_external_gate_worker.py",
    "TRUSTED_AUTHORITY_SERVICE_SOURCE": "governance-runtime/native/v24_v6_trusted_authority_service.c",
    "TRUSTED_AUTHORITY_SERVICE_BUILD_SCRIPT": "governance-runtime/build_v24_v6_trusted_authority_service.sh",
    "TRUSTED_SERVICE_CLIENT": "governance-runtime/v24_v6_trusted_service_client.py",
}
REQUIRED_ADVERSARIAL_CHECKS = frozenset(
    {
        "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
        "EVERY_REACHABLE_TERMINAL_ALLOWED",
        "GENESIS_CROSS_PAIR_REJECTED",
        "APPLICABLE_PREDICATE_OMISSION_REJECTED",
        "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
        "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
        "SHARED_PRODUCTION_DEPENDENCY_MUTATION_REJECTED",
        "CLAUSE_CONTROL_REASSIGNMENT_REJECTED",
        "DECISION_EFFECT_PATH_TARGET_MISMATCH_REJECTED",
        "SAME_PROCESS_ANCHOR_REWRITE_REJECTED",
        "UNSIGNED_CONTEXT_REJECTED",
        "WRONG_CONTEXT_SIGNATURE_REJECTED",
        "CALLER_SELECTED_PUBLIC_KEY_REJECTED",
        "ATTESTATION_SCOPE_SUBSTITUTION_REJECTED",
        "SIGNED_CONTEXT_POSITIVE",
        "SAME_PROCESS_IMPORTED_VERIFIER_SUBSTITUTION_REJECTED",
        "SAME_PROCESS_ROOT_KEY_SUBSTITUTION_REJECTED",
        "SAME_PROCESS_RSA_HELPER_SUBSTITUTION_REJECTED",
        "DIRECT_PYTHON_QUALIFIED_IS_NONAUTHORITATIVE",
        "FORGED_EXTERNAL_VERDICT_REJECTED",
        "VERDICT_CONTEXT_REBIND_REJECTED",
        "VERDICT_SCOPE_OR_GENERATION_REBIND_REJECTED",
        "VERIFIER_IDENTITY_VERSION_REBIND_REJECTED",
        "EXTERNAL_GATE_FAILURE_FAILS_CLOSED",
        "EXTERNALLY_VERIFIED_SIGNED_CONTEXT_POSITIVE",
        "DA1_FRESH_EFFECT_PATH_SELF_GRANT_REJECTED",
        "NCP1_FRESH_CLAUSE_CONTROL_SELF_GRANT_REJECTED",
        "SAME_USER_GATE_EXECUTABLE_REPLACEMENT_REJECTED",
        "GATE_PARENT_DIRECTORY_RENAME_UNLINK_REPLACEMENT_REJECTED",
        "PINNED_SOURCE_POST_MEASUREMENT_SUBSTITUTION_REJECTED",
        "CALLER_SELECTED_GATE_PATH_REJECTED",
        "LIVE_GATE_DIGEST_MISMATCH_REJECTED",
        "TRUSTED_GATE_POSITIVE",
        "CANDIDATE_LD_PRELOAD_GATE_INJECTION_REJECTED",
        "CANDIDATE_LD_LIBRARY_PATH_REBIND_REJECTED",
        "SAME_UID_GATE_PROCESS_TRACE_OR_INJECTION_REJECTED",
        "CANDIDATE_TEMP_RESULT_SUBSTITUTION_REJECTED",
        "TRUSTED_SERVICE_PEER_IDENTITY_ENFORCED",
        "CALLER_CANNOT_SELECT_SERVICE_EXECUTABLE_OR_WORKER",
        "COHERENT_GATE_AND_BUILD_MANIFEST_SUBSTITUTION_REJECTED",
        "CANDIDATE_SELECTED_TRUSTED_ROOT_REJECTED",
        "TRUSTED_SERVICE_POSITIVE",
        "CANDIDATE_LOCAL_SOCKET_PEER_FORGERY_REJECTED",
        "CANDIDATE_REQUEST_SERVICE_REPLACEMENT_NONAUTHORITATIVE",
        "NAMESPACE_LOCAL_FAKE_SERVICE_NONAUTHORITATIVE",
        "AUTHORITY_RECORD_REQUEST_BINDING_ENFORCED",
        "AUTHORITY_RECORD_REPLAY_REJECTED",
        "AUTHORITY_RECORD_SERVICE_BUILD_BINDING_ENFORCED",
        "AUTHORITY_RECORD_GATE_RESULT_BINDING_ENFORCED",
        "TRUSTED_AUTHORITY_RECORD_POSITIVE",
    }
)
SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"

# Exact identity approved by V6 Follow-Up Review 002 and its exact-byte
# reconstruction/verification evidence. These are candidate-freeze bindings,
# not runtime decision rules.
APPROVED_DESIGN_PACKET_SHA256 = "96ec464fbf602ac6b8c89fca5af16aa71a8d53f9f042605e46a07b4cd628ca62"
APPROVED_DESIGN_BODY_SHA256 = "286217399947144630c29e991c3529dfee64d382be08a6ccd3f87e9fc5173ad5"
APPROVED_DESIGN_GIT_BLOB_SHA = "4a15d50a0488464816d235b273d1dbf808fdce94"
APPROVED_DESIGN_PACKET_BYTES = 19297
APPROVED_DESIGN_SOURCE_GIT_BLOB_SHA = "8682df137aa12d57927e7891c16048e90b04caac"
APPROVED_DESIGN_SOURCE_PACKET_SHA256 = "5164747405b2de4d97228318a200e97c6b9c0e2afe58e4daddf09fe804bbc9d9"
APPROVED_DESIGN_SOURCE_PACKET_BYTES = 19296
APPROVED_DESIGN_RECONSTRUCTION_MANIFEST_GIT_BLOB_SHA = "fe97833ea39f796e1616a3eee6f04ccb7968f47a"
APPROVED_DESIGN_REVIEW_RECORD_GIT_BLOB_SHA = "59b96d37b22e3a8b789d33caf65ab3e8b8c6070f"
APPROVED_DESIGN_RECONSTRUCTION_OFFSET = 17321
APPROVED_DESIGN_RECONSTRUCTION_INSERT_HEX = "0a"
APPROVED_DESIGN_VERIFICATION_RUN_ID = "34752761361"


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _git_sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def _safe_path(v: Any) -> str | None:
    if not isinstance(v, str) or not v:
        return None
    p = PurePosixPath(v)
    if p.is_absolute() or ".." in p.parts or any(x in {"", "."} for x in p.parts):
        return None
    return p.as_posix()


def _read(root: Path, repo_path: str) -> bytes:
    base = root.resolve()
    target = (base / repo_path).resolve()
    target.relative_to(base)
    return target.read_bytes()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_approved_design_binding(manifest: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    exact = {
        "approved_design_packet_sha256": APPROVED_DESIGN_PACKET_SHA256,
        "approved_design_body_sha256": APPROVED_DESIGN_BODY_SHA256,
        "approved_design_git_blob_sha": APPROVED_DESIGN_GIT_BLOB_SHA,
        "approved_design_packet_bytes": APPROVED_DESIGN_PACKET_BYTES,
        "approved_design_source_git_blob_sha": APPROVED_DESIGN_SOURCE_GIT_BLOB_SHA,
        "approved_design_source_packet_sha256": APPROVED_DESIGN_SOURCE_PACKET_SHA256,
        "approved_design_source_packet_bytes": APPROVED_DESIGN_SOURCE_PACKET_BYTES,
        "approved_design_reconstruction_manifest_git_blob_sha": APPROVED_DESIGN_RECONSTRUCTION_MANIFEST_GIT_BLOB_SHA,
        "approved_design_review_record_git_blob_sha": APPROVED_DESIGN_REVIEW_RECORD_GIT_BLOB_SHA,
        "approved_design_reconstruction_offset": APPROVED_DESIGN_RECONSTRUCTION_OFFSET,
        "approved_design_reconstruction_insert_hex": APPROVED_DESIGN_RECONSTRUCTION_INSERT_HEX,
        "approved_design_verification_run_id": APPROVED_DESIGN_VERIFICATION_RUN_ID,
    }
    for key, expected in exact.items():
        if manifest.get(key) != expected:
            problems.append(f"INTEGRATED_SUCCESSOR_APPROVED_DESIGN_BINDING_MISMATCH:{key}")
    return problems


def validate_integrated_successor_manifest(
    *, repo_root: str | Path, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    problems: list[str] = []
    root = Path(repo_root)
    if manifest.get("schema_version") != 1:
        problems.append("INTEGRATED_SUCCESSOR_SCHEMA_INVALID")
    for key in (
        "candidate_family_id",
        "approved_design_packet_sha256",
        "approved_design_body_sha256",
        "approved_design_git_blob_sha",
        "approved_design_source_git_blob_sha",
        "approved_design_source_packet_sha256",
        "approved_design_reconstruction_manifest_git_blob_sha",
        "approved_design_review_record_git_blob_sha",
        "approved_design_verification_run_id",
        "frozen_i10_commit",
        "frozen_i10_tree",
        "implementation_lineage_root_commit",
    ):
        if not _nonempty(manifest.get(key)):
            problems.append(f"INTEGRATED_SUCCESSOR_FIELD_REQUIRED:{key}")
    for key in (
        "approved_design_packet_sha256",
        "approved_design_body_sha256",
        "approved_design_source_packet_sha256",
    ):
        if not _sha256(manifest.get(key)):
            problems.append(f"INTEGRATED_SUCCESSOR_SHA256_INVALID:{key}")
    for key in (
        "approved_design_git_blob_sha",
        "approved_design_source_git_blob_sha",
        "approved_design_reconstruction_manifest_git_blob_sha",
        "approved_design_review_record_git_blob_sha",
        "frozen_i10_commit",
        "frozen_i10_tree",
        "implementation_lineage_root_commit",
    ):
        if not _git_sha(manifest.get(key)):
            problems.append(f"INTEGRATED_SUCCESSOR_GIT_ID_INVALID:{key}")
    problems.extend(_validate_approved_design_binding(manifest))
    if manifest.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("INTEGRATED_SUCCESSOR_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if manifest.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("INTEGRATED_SUCCESSOR_AUTHORITY_EFFECT_INVALID")

    rows = manifest.get("workstreams")
    if not isinstance(rows, list):
        rows = []
        problems.append("INTEGRATED_SUCCESSOR_WORKSTREAMS_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            problems.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_MALFORMED:{index}")
            continue
        wid = row.get("workstream_id")
        if wid not in EXPECTED_WORKSTREAMS:
            problems.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_ID_INVALID:{wid}")
            continue
        if wid in by_id:
            problems.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_DUPLICATE:{wid}")
            continue
        by_id[wid] = row
    for missing in sorted(set(EXPECTED_WORKSTREAMS) - set(by_id)):
        problems.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_MISSING:{missing}")

    bound: list[dict[str, Any]] = []
    for wid in EXPECTED_WORKSTREAMS:
        row = by_id.get(wid)
        if row is None:
            continue
        module = EXPECTED_PRODUCTION_MODULES[wid]
        evidence = EXPECTED_EVIDENCE_FILES[wid]
        if row.get("production_module_path") != module:
            problems.append(f"INTEGRATED_SUCCESSOR_PRODUCTION_PATH_MISMATCH:{wid}")
        if row.get("construction_evidence_path") != evidence:
            problems.append(f"INTEGRATED_SUCCESSOR_EVIDENCE_PATH_MISMATCH:{wid}")
        if row.get("construction_state") != "PASS":
            problems.append(f"INTEGRATED_SUCCESSOR_WORKSTREAM_NOT_PASS:{wid}")
        if row.get("runtime_qualification_state") != "NOT_CLAIMED":
            problems.append(f"INTEGRATED_SUCCESSOR_RUNTIME_QUALIFICATION_CLAIMED:{wid}")
        for role, path, blob_key in (
            ("production", module, "production_git_blob_sha"),
            ("evidence", evidence, "evidence_git_blob_sha"),
        ):
            if _safe_path(path) != path:
                problems.append(f"INTEGRATED_SUCCESSOR_PATH_INVALID:{wid}:{role}")
                continue
            try:
                data = _read(root, path)
            except Exception:
                problems.append(f"INTEGRATED_SUCCESSOR_BOUND_FILE_MISSING:{wid}:{role}")
                continue
            actual_blob = git_blob_sha(data)
            if row.get(blob_key) != actual_blob:
                problems.append(f"INTEGRATED_SUCCESSOR_BLOB_MISMATCH:{wid}:{role}")
            bound.append(
                {
                    "workstream_id": wid,
                    "role": role,
                    "path": path,
                    "git_blob_sha": actual_blob,
                    "raw_sha256": raw_sha256(data),
                }
            )

    dependencies = manifest.get("shared_dependencies")
    if not isinstance(dependencies, list):
        dependencies = []
        problems.append("INTEGRATED_SUCCESSOR_SHARED_DEPENDENCIES_REQUIRED")
    dependency_by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(dependencies):
        if not isinstance(row, Mapping):
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_MALFORMED:{index}")
            continue
        dep_id = row.get("dependency_id")
        if dep_id not in EXPECTED_SHARED_PRODUCTION_DEPENDENCIES:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_ID_INVALID:{dep_id}")
            continue
        if dep_id in dependency_by_id:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_DUPLICATE:{dep_id}")
            continue
        dependency_by_id[dep_id] = row
    for missing in sorted(set(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES) - set(dependency_by_id)):
        problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_MISSING:{missing}")
    for dep_id, path in EXPECTED_SHARED_PRODUCTION_DEPENDENCIES.items():
        row = dependency_by_id.get(dep_id)
        if row is None:
            continue
        if row.get("path") != path:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_PATH_MISMATCH:{dep_id}")
        if _safe_path(path) != path:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_PATH_INVALID:{dep_id}")
            continue
        try:
            data = _read(root, path)
        except Exception:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_FILE_MISSING:{dep_id}")
            continue
        actual_blob = git_blob_sha(data)
        if row.get("git_blob_sha") != actual_blob:
            problems.append(f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_BLOB_MISMATCH:{dep_id}")
        bound.append(
            {
                "workstream_id": f"SHARED:{dep_id}",
                "role": "dependency",
                "path": path,
                "git_blob_sha": actual_blob,
                "raw_sha256": raw_sha256(data),
            }
        )

    checks = manifest.get("mandatory_v6_adversarial_checks")
    if not isinstance(checks, list):
        checks = []
        problems.append("INTEGRATED_SUCCESSOR_MANDATORY_CHECKS_REQUIRED")
    for missing in sorted(REQUIRED_ADVERSARIAL_CHECKS - set(checks)):
        problems.append(f"INTEGRATED_SUCCESSOR_MANDATORY_CHECK_MISSING:{missing}")
    for extra in sorted(set(checks) - REQUIRED_ADVERSARIAL_CHECKS):
        problems.append(f"INTEGRATED_SUCCESSOR_MANDATORY_CHECK_UNKNOWN:{extra}")

    problems = sorted(set(problems))
    bound_sorted = sorted(bound, key=lambda x: (x["workstream_id"], x["role"], x["path"]))
    material = {
        "candidate_family_id": manifest.get("candidate_family_id"),
        "approved_design_packet_sha256": manifest.get("approved_design_packet_sha256"),
        "approved_design_body_sha256": manifest.get("approved_design_body_sha256"),
        "approved_design_git_blob_sha": manifest.get("approved_design_git_blob_sha"),
        "approved_design_packet_bytes": manifest.get("approved_design_packet_bytes"),
        "approved_design_source_git_blob_sha": manifest.get("approved_design_source_git_blob_sha"),
        "approved_design_source_packet_sha256": manifest.get("approved_design_source_packet_sha256"),
        "approved_design_source_packet_bytes": manifest.get("approved_design_source_packet_bytes"),
        "approved_design_reconstruction_manifest_git_blob_sha": manifest.get("approved_design_reconstruction_manifest_git_blob_sha"),
        "approved_design_review_record_git_blob_sha": manifest.get("approved_design_review_record_git_blob_sha"),
        "approved_design_reconstruction_offset": manifest.get("approved_design_reconstruction_offset"),
        "approved_design_reconstruction_insert_hex": manifest.get("approved_design_reconstruction_insert_hex"),
        "approved_design_verification_run_id": manifest.get("approved_design_verification_run_id"),
        "frozen_i10_commit": manifest.get("frozen_i10_commit"),
        "frozen_i10_tree": manifest.get("frozen_i10_tree"),
        "scientific_execution_state": manifest.get("scientific_execution_state"),
        "bound_files": bound_sorted,
        "mandatory_v6_adversarial_checks": sorted(REQUIRED_ADVERSARIAL_CHECKS),
    }
    return {
        "state": "V24_V6_INTEGRATED_SUCCESSOR_BOUND" if not problems else "V24_V6_INTEGRATED_SUCCESSOR_INVALID",
        "qualified": False,
        "integration_valid": not problems,
        "problems": problems,
        "binding_digest": digest(material),
        "bound_file_count": len(bound_sorted),
        "bound_files": bound_sorted,
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
