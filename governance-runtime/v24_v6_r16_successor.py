"""R16 evidence contract for dir_fd/openat confinement and authority-secret separation.

This module validates externally produced construction/falsification evidence only.
It never grants runtime, release, deployment, terminal, or scientific authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"
EXTERNAL_AUTHORITY_ORIGIN = "EXTERNAL_REVIEW_BRANCH"

REQUIRED_R16_PROBES = frozenset({
    "OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED",
    "OS_OPEN_DIR_FD_PROC_SELF_MAPS_REJECTED",
    "OS_OPEN_DIR_FD_PROC_SELF_FD_REJECTED",
    "DUPLICATED_DIRECTORY_FD_FORBIDDEN_SURFACE_REJECTED",
    "INHERITED_DIRECTORY_FD_FORBIDDEN_SURFACE_REJECTED",
    "POST_IMPORT_DIR_FD_MEMORY_OPEN_REJECTED",
    "CANDIDATE_SELF_MEMORY_READ_CANNOT_RECOVER_AUTH_SECRET",
    "CANDIDATE_FORGED_FRAME_WITH_FULL_CHILD_MEMORY_KNOWLEDGE_REJECTED",
    "SCENARIO_LIBRARY_SUBSTITUTION_REJECTED_BEFORE_IMPORT",
    "TRANSITIVE_NATIVE_SOURCE_SUBSTITUTION_REJECTED_BEFORE_COMPILE",
    "SYMLINK_RACE_OR_TOCTOU_CANNOT_CREATE_AUTHENTICATED_OBSERVATION",
    "NON_OPEN_EVENT_NATIVE_MEMORY_ROUTE_REJECTED_OR_PROVEN_UNREACHABLE",
    "R13_TAILORED_FRAME_FALSE_GREEN_REMAINS_REJECTED",
    "R14_BYTES_PROC_SELF_MEM_FALSE_GREEN_REMAINS_REJECTED",
    "R15_SYMLINK_ALIAS_SET_REMAINS_REJECTED",
})


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hex(value: Any, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_set_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    normalized = [
        {
            "path": row.get("path"),
            "git_blob_sha1": row.get("git_blob_sha1"),
            "raw_sha256": row.get("raw_sha256"),
            "role": row.get("role"),
        }
        for row in rows
    ]
    normalized.sort(key=lambda x: str(x.get("path")))
    return digest(normalized)


def _record_digest(row: Mapping[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "record_digest"}
    return digest(material)


def validate_r16_external_evidence(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []

    if bundle.get("schema_version") != 1:
        problems.append("R16_EVIDENCE_SCHEMA_INVALID")
    if bundle.get("authority_origin") != EXTERNAL_AUTHORITY_ORIGIN:
        problems.append("R16_EVIDENCE_AUTHORITY_ORIGIN_INVALID")
    if bundle.get("candidate_self_grant") is not False:
        problems.append("R16_EVIDENCE_SELF_GRANT_FORBIDDEN")
    if bundle.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("R16_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if bundle.get("runtime_qualification_state") != "NOT_CLAIMED":
        problems.append("R16_RUNTIME_QUALIFICATION_MUST_REMAIN_UNCLAIMED")
    if bundle.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("R16_AUTHORITY_EFFECT_INVALID")

    commit = bundle.get("candidate_commit")
    tree = bundle.get("candidate_tree")
    environment = bundle.get("environment_digest")
    if not _hex(commit, 40):
        problems.append("R16_CANDIDATE_COMMIT_INVALID")
    if not _hex(tree, 40):
        problems.append("R16_CANDIDATE_TREE_INVALID")
    if not _hex(environment, 64):
        problems.append("R16_ENVIRONMENT_DIGEST_INVALID")

    confinement = bundle.get("native_confinement")
    if not isinstance(confinement, Mapping):
        confinement = {}
        problems.append("R16_NATIVE_CONFINEMENT_REQUIRED")
    if confinement.get("kernel_or_fd_aware_enforcement") is not True:
        problems.append("R16_KERNEL_OR_FD_AWARE_CONFINEMENT_REQUIRED")
    if confinement.get("cwd_realpath_authoritative") is not False:
        problems.append("R16_CWD_REALPATH_MUST_NOT_BE_AUTHORITY")
    if confinement.get("dir_fd_openat_covered") is not True:
        problems.append("R16_DIR_FD_OPENAT_COVERAGE_REQUIRED")
    if confinement.get("inherited_and_duplicated_fd_covered") is not True:
        problems.append("R16_FD_ALIAS_COVERAGE_REQUIRED")
    if confinement.get("post_import_semantic_probe_passed") is not True:
        problems.append("R16_POST_IMPORT_SEMANTIC_PROBE_REQUIRED")
    for key in ("policy_digest", "kernel_evidence_digest", "surface_inventory_digest"):
        if not _hex(confinement.get(key), 64):
            problems.append(f"R16_CONFINEMENT_DIGEST_INVALID:{key}")

    secret = bundle.get("secret_separation")
    if not isinstance(secret, Mapping):
        secret = {}
        problems.append("R16_SECRET_SEPARATION_REQUIRED")
    if secret.get("authority_secret_in_candidate_address_space") is not False:
        problems.append("R16_AUTHORITY_SECRET_IN_CANDIDATE_FORBIDDEN")
    if secret.get("candidate_can_compute_authority_mac") is not False:
        problems.append("R16_CANDIDATE_AUTHORITY_MAC_FORBIDDEN")
    if secret.get("candidate_observation_role") != "UNTRUSTED_OBSERVATION_ONLY":
        problems.append("R16_CANDIDATE_OBSERVATION_ROLE_INVALID")
    if secret.get("parent_authentication_material_origin") not in {
        "PARENT_ONLY_POST_FORK",
        "SEPARATE_TRUSTED_PROCESS_ONLY",
    }:
        problems.append("R16_PARENT_AUTH_MATERIAL_ORIGIN_INVALID")
    if secret.get("full_child_memory_knowledge_forgery_rejected") is not True:
        problems.append("R16_FULL_CHILD_MEMORY_FORGERY_REGRESSION_REQUIRED")
    if not _hex(secret.get("separation_evidence_digest"), 64):
        problems.append("R16_SECRET_SEPARATION_EVIDENCE_DIGEST_INVALID")

    scenario = bundle.get("trusted_scenario_library")
    if not isinstance(scenario, Mapping):
        scenario = {}
        problems.append("R16_SCENARIO_LIBRARY_BINDING_REQUIRED")
    if scenario.get("verified_before_import") is not True:
        problems.append("R16_SCENARIO_LIBRARY_PREIMPORT_VERIFICATION_REQUIRED")
    if not _hex(scenario.get("git_blob_sha1"), 40):
        problems.append("R16_SCENARIO_LIBRARY_GIT_BLOB_INVALID")
    if not _hex(scenario.get("raw_sha256"), 64):
        problems.append("R16_SCENARIO_LIBRARY_SHA256_INVALID")
    if not _nonempty(scenario.get("path")):
        problems.append("R16_SCENARIO_LIBRARY_PATH_REQUIRED")

    sources = bundle.get("trusted_native_sources")
    if not isinstance(sources, list) or not sources:
        sources = []
        problems.append("R16_TRUSTED_NATIVE_SOURCE_SET_REQUIRED")
    paths: set[str] = set()
    for i, row in enumerate(sources):
        if not isinstance(row, Mapping):
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_MALFORMED:{i}")
            continue
        path = row.get("path")
        if not _nonempty(path):
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_PATH_REQUIRED:{i}")
            continue
        if path in paths:
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_DUPLICATE:{path}")
        paths.add(path)
        if not _hex(row.get("git_blob_sha1"), 40):
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_GIT_BLOB_INVALID:{path}")
        if not _hex(row.get("raw_sha256"), 64):
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_SHA256_INVALID:{path}")
        if row.get("role") not in {"NATIVE_AUTHORITY_SOURCE", "NATIVE_BUILD_SUPPORT", "TRUSTED_ORACLE_SOURCE"}:
            problems.append(f"R16_TRUSTED_NATIVE_SOURCE_ROLE_INVALID:{path}")
    if sources and bundle.get("trusted_native_source_set_digest") != _source_set_digest(
        [x for x in sources if isinstance(x, Mapping)]
    ):
        problems.append("R16_TRUSTED_NATIVE_SOURCE_SET_DIGEST_MISMATCH")

    records = bundle.get("probe_records")
    if not isinstance(records, list):
        records = []
        problems.append("R16_PROBE_RECORDS_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    valid_record_digests: list[str] = []
    for i, row in enumerate(records):
        if not isinstance(row, Mapping):
            problems.append(f"R16_PROBE_RECORD_MALFORMED:{i}")
            continue
        probe_id = row.get("probe_id")
        if probe_id not in REQUIRED_R16_PROBES:
            problems.append(f"R16_PROBE_UNKNOWN:{probe_id}")
            continue
        if probe_id in by_id:
            problems.append(f"R16_PROBE_DUPLICATE:{probe_id}")
            continue
        by_id[probe_id] = row
        if row.get("execution_state") != "EXECUTED":
            problems.append(f"R16_PROBE_NOT_EXECUTED:{probe_id}")
        if row.get("terminal_result") != "PASS":
            problems.append(f"R16_PROBE_NOT_PASS:{probe_id}")
        if row.get("candidate_commit") != commit:
            problems.append(f"R16_PROBE_COMMIT_MISMATCH:{probe_id}")
        if row.get("candidate_tree") != tree:
            problems.append(f"R16_PROBE_TREE_MISMATCH:{probe_id}")
        if row.get("environment_digest") != environment:
            problems.append(f"R16_PROBE_ENVIRONMENT_MISMATCH:{probe_id}")
        if row.get("witness_authority_origin") != EXTERNAL_AUTHORITY_ORIGIN:
            problems.append(f"R16_PROBE_WITNESS_ORIGIN_INVALID:{probe_id}")
        if row.get("candidate_self_authored") is not False:
            problems.append(f"R16_PROBE_SELF_AUTHORED_FORBIDDEN:{probe_id}")
        for key in ("run_id", "round_id", "witness_id", "witness_control_domain"):
            if not _nonempty(row.get(key)):
                problems.append(f"R16_PROBE_FIELD_REQUIRED:{probe_id}:{key}")
        if not _hex(row.get("evidence_digest"), 64):
            problems.append(f"R16_PROBE_EVIDENCE_DIGEST_INVALID:{probe_id}")
        expected = _record_digest(row)
        if row.get("record_digest") != expected:
            problems.append(f"R16_PROBE_RECORD_DIGEST_MISMATCH:{probe_id}")
        else:
            valid_record_digests.append(expected)

    for missing in sorted(REQUIRED_R16_PROBES - set(by_id)):
        problems.append(f"R16_PROBE_MISSING:{missing}")
    expected_probe_set_digest = digest({"record_digests": sorted(valid_record_digests)})
    if bundle.get("probe_set_digest") != expected_probe_set_digest:
        problems.append("R16_PROBE_SET_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "V24_V6_R16_EXTERNAL_EVIDENCE_BOUND" if not problems else "V24_V6_R16_EXTERNAL_EVIDENCE_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "required_probe_count": len(REQUIRED_R16_PROBES),
        "bound_probe_count": len(by_id),
        "trusted_native_source_count": len(paths),
        "probe_set_digest": expected_probe_set_digest,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "runtime_qualification_state": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R16_EVIDENCE_CONTRACT_CONSTRUCTION_READY",
        "qualified": False,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "runtime_qualification_state": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
