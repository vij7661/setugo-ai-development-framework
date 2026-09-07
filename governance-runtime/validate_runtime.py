#!/usr/bin/env python3
"""Deterministic validator for live conversation governance runtime state."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from review_protocol import (
    EXTERNAL_EVIDENCE_CLASSES,
    PLATFORM_MODES,
    PLATFORM_REVIEW_TRANSPORTS,
    PROMOTABLE_REVIEW_DISPOSITIONS,
    REVIEW_LEVELS,
    SEMANTIC_REVIEW_SCHEMA_VERSION,
    verify_review_request,
)

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "session-state.json"
MEMORY_PATH = ROOT / "shared-memory.json"
LOG_PATH = ROOT / "decision-log.jsonl"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_PRECEDENCE = [
    "governed_git_state",
    "governed_registries_and_evidence",
    "governed_shared_project_memory",
    "project_chat_and_files_working_context",
    "ungoverned_summaries_and_caches_advisory",
    "model_recollection_non_authoritative",
]
ALLOWED_CHECKPOINT_STATES = {"ACTIVE", "GROUNDING_REQUIRED", "SUSPENDED", "SUPERSEDED"}
ALLOWED_REVIEW_STATUS = {
    "NOT_YET_PRESENT", "PENDING_INDEPENDENT_REVIEW", "PENDING_EXTERNAL_REVIEW",
    "REVIEW_RECEIVED", "REVIEW_VALIDATED", "VALID_INDEPENDENT_REVIEW_PRESENT",
    "REVIEW_INDEPENDENCE_UNPROVEN",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def require_sha(value: object, field: str) -> None:
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        fail(f"{field} must be a lowercase 40-character Git SHA")


def require_sha256(value: object, field: str) -> None:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        fail(f"{field} must be a lowercase 64-character SHA-256")


def main() -> int:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

    if state.get("schema_version") != 3 or state.get("checkpoint_state") not in ALLOWED_CHECKPOINT_STATES:
        fail("session-state schema/checkpoint invalid")
    authority = state.get("authority", {})
    if authority.get("repository") != "vij7661/setugo-ai-development-framework":
        fail("authoritative repository changed")
    if authority.get("source_precedence") != EXPECTED_PRECEDENCE:
        fail("authority precedence changed or weakened")

    runtime = state.get("runtime", {})
    if runtime.get("branch") != "governance/live-conversation-runtime":
        fail("runtime branch changed")
    if runtime.get("normative_contract_path") != "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md":
        fail("normative contract path changed")
    require_sha(runtime.get("normative_contract_commit"), "runtime.normative_contract_commit")

    shared = state.get("shared_memory", {})
    if shared.get("path") != "governance-runtime/shared-memory.json" or shared.get("active") is not True:
        fail("shared memory path/state invalid")
    if shared.get("independent_authority") is not False:
        fail("shared memory must not be independent authority")
    if shared.get("bootstrap_order") != "READ_THEN_VERIFY_AGAINST_GIT":
        fail("shared-memory bootstrap order weakened")
    if shared.get("on_conflict") != "AUTHORITATIVE_STATE_WINS_AND_MEMORY_REASSESSMENT_REQUIRED":
        fail("shared-memory conflict policy weakened")
    if shared.get("write_order") != "AUTHORITATIVE_PERSIST_FIRST_THEN_MEMORY_SYNC":
        fail("shared-memory write order weakened")
    if shared.get("on_write_failure_after_authoritative_persist") != "AUTHORITY_REMAINS_VALID_MEMORY_STALE":
        fail("memory failure semantics weakened")
    if shared.get("on_authoritative_persist_failure") != "BLOCK_AUTHORITATIVE_COMPLETION":
        fail("authority persistence failure must block completion")

    if memory.get("schema_version") != 2 or memory.get("state") != "ACTIVE":
        fail("shared-memory artifact malformed/inactive")
    if memory.get("independent_authority") is not False:
        fail("shared-memory artifact claims independent authority")
    if memory.get("read_policy") != "READ_AT_SESSION_START_THEN_VERIFY_MATERIAL_POINTERS_AGAINST_AUTHORITY":
        fail("shared-memory read policy invalid")
    if memory.get("write_policy") != "AUTHORITATIVE_PERSIST_FIRST_THEN_SYNCHRONIZE_MEMORY":
        fail("shared-memory write policy invalid")

    work = state.get("active_workstream", {})
    for key in ("branch", "head_commit", "state", "next_action", "forbidden_shortcut"):
        if not work.get(key):
            fail(f"active_workstream.{key} required")
    for key in ("head_commit", "preregistration_commit", "frozen_acceptance_harness_commit",
                "first_mechanism_commit", "preserved_failure_record_commit"):
        require_sha(work.get(key), f"active_workstream.{key}")
    latest = work.get("latest_result", {})
    passed, total, failures = latest.get("passed"), latest.get("total"), latest.get("failures")
    if not isinstance(passed, int) or not isinstance(total, int) or not isinstance(failures, list):
        fail("latest_result malformed")
    if passed < 0 or total <= 0 or passed > total or len(failures) != total - passed:
        fail("latest_result counts inconsistent")

    mem_work = memory.get("current_work", {})
    if mem_work.get("authoritative_branch") != work.get("branch") or mem_work.get("authoritative_head") != work.get("head_commit") or mem_work.get("status") != work.get("state"):
        fail("shared memory workstream differs from authority")

    review = state.get("independent_review", {})
    if review.get("policy_state") != "MANDATORY_FOR_MATERIAL_AUTHORITY_TRANSITIONS":
        fail("mandatory review policy weakened")
    if review.get("semantic_review_schema_minimum_for_promotion") != SEMANTIC_REVIEW_SCHEMA_VERSION:
        fail("semantic schema floor changed")
    if set(review.get("positive_promotable_dispositions", [])) != set(PROMOTABLE_REVIEW_DISPOSITIONS):
        fail("promotable dispositions changed")
    if set(review.get("platform_modes", [])) != set(PLATFORM_MODES):
        fail("platform modes invalid")
    if set(review.get("review_levels", [])) != set(REVIEW_LEVELS):
        fail("review levels invalid")
    if set(review.get("supported_review_transports", [])) != set(PLATFORM_REVIEW_TRANSPORTS):
        fail("platform review transports invalid")
    if set(review.get("external_evidence_classes", [])) != set(EXTERNAL_EVIDENCE_CLASSES):
        fail("external evidence classes invalid")
    if review.get("production_auto_mode_transport") != "AUTOMATIC_API":
        fail("AUTO_MODE transport changed")
    if review.get("production_manual_mode_transport") != "USER_INITIATED_API":
        fail("MANUAL_MODE transport changed")
    if review.get("current_collaboration_mode") != "MANUAL_MODE":
        fail("current collaboration mode must be MANUAL_MODE")
    if review.get("current_collaboration_review_transport") is not None:
        fail("copy/paste collaboration must not claim a platform review transport")
    if review.get("current_external_evidence_channel") != "USER_PASTE":
        fail("current external evidence channel must be USER_PASTE")
    if review.get("content_may_establish_own_provenance") is not False:
        fail("content must not establish its own provenance")
    if review.get("user_attestation_is_provider_authentication") is not False:
        fail("user attestation must not become provider authentication")
    if review.get("transport_may_change_policy") is not False or review.get("platform_mode_may_change_authority") is not False:
        fail("mode/transport may not change authority")
    if review.get("current_review_status") not in ALLOWED_REVIEW_STATUS:
        fail("invalid current review status")
    if review.get("consensus_is_evidence") is not False:
        fail("consensus must not be evidence")
    if review.get("fallback_if_unavailable") != "PENDING_INDEPENDENT_REVIEW":
        fail("review-unavailable fallback weakened")

    mem_runtime = memory.get("governance_runtime", {})
    if set(mem_runtime.get("supported_review_transports", [])) != set(PLATFORM_REVIEW_TRANSPORTS):
        fail("shared memory review transports invalid")
    if set(mem_runtime.get("external_evidence_classes", [])) != set(EXTERNAL_EVIDENCE_CLASSES):
        fail("shared memory external evidence classes invalid")
    if mem_runtime.get("current_review_request_id") != review.get("current_review_request_id"):
        fail("shared memory current review request differs from authority")
    if mem_runtime.get("current_review_status") != review.get("current_review_status"):
        fail("shared memory current review status differs from authority")
    if mem_runtime.get("production_auto_mode_transport") != "AUTOMATIC_API" or mem_runtime.get("production_manual_mode_transport") != "USER_INITIATED_API":
        fail("shared memory lost API review transport policy")
    if mem_runtime.get("current_collaboration_review_transport") is not None or mem_runtime.get("current_external_evidence_channel") != "USER_PASTE":
        fail("shared memory conflates paste channel with review transport")
    if mem_runtime.get("semantic_review_schema_minimum_for_promotion") != SEMANTIC_REVIEW_SCHEMA_VERSION:
        fail("shared memory lost semantic schema floor")

    promotion = runtime.get("promotion", {})
    active_id = review.get("current_review_request_id")
    pending = memory.get("pending_reviews")
    if not isinstance(pending, list) or not pending or not isinstance(pending[0], dict):
        fail("pending review coordination missing")
    mem_review = pending[0]

    if active_id is None:
        if promotion.get("state") != "PENDING_CANDIDATE_FREEZE":
            fail("no active review requires PENDING_CANDIDATE_FREEZE")
        if review.get("current_review_status") != "NOT_YET_PRESENT":
            fail("candidate-freeze state pretends review exists")
        if mem_review.get("status") != "PENDING_CANDIDATE_FREEZE":
            fail("memory disagrees with candidate-freeze state")
        if mem_review.get("review_request_id") is not None or mem_review.get("review_transport") is not None:
            fail("candidate-freeze memory must not claim active review execution")
    else:
        if promotion.get("state") != "PENDING_EXTERNAL_REVIEW":
            fail("active review must be pending external/API review")
        request_path_value = promotion.get("review_request_path")
        if not isinstance(request_path_value, str) or not request_path_value.startswith("governance-runtime/review-requests/"):
            fail("active review request path invalid")
        request_path = ROOT.parent / request_path_value
        if not request_path.is_file():
            fail("active review request file missing")
        request = json.loads(request_path.read_text(encoding="utf-8"))
        ok, reason = verify_review_request(request)
        if not ok:
            fail(f"active review request invalid: {reason}")
        if request.get("schema_version") != SEMANTIC_REVIEW_SCHEMA_VERSION:
            fail("active material review must use schema 4")
        reviewed_commit = review.get("current_reviewed_artifact_commit")
        require_sha(reviewed_commit, "independent_review.current_reviewed_artifact_commit")
        if request.get("review_request_id") != active_id or request.get("artifact", {}).get("commit") != reviewed_commit:
            fail("active request binding invalid")
        review_transport = review.get("current_review_transport")
        if review_transport not in PLATFORM_REVIEW_TRANSPORTS:
            fail("active authority review must use platform API transport")
        if mem_review.get("review_request_id") != active_id or mem_review.get("review_transport") != review_transport:
            fail("memory active review binding differs from authority")

    superseded = set(review.get("superseded_review_requests", [])) | set(promotion.get("superseded_review_requests", []))
    for request_id in superseded:
        if not isinstance(request_id, str) or not request_id:
            fail("superseded request ID malformed")
        if not (ROOT / "review-requests" / f"{request_id}.json").is_file():
            fail(f"superseded review request file missing: {request_id}")

    for item in state.get("external_evidence", []):
        if not isinstance(item, dict) or item.get("evidence_class") not in EXTERNAL_EVIDENCE_CLASSES:
            fail("external evidence record class invalid")
        if item.get("provider_api_authenticated") is not False or item.get("counts_for_promotion") is not False:
            fail("external evidence improperly claims platform review authority")
        path = item.get("path")
        if not isinstance(path, str) or not (ROOT.parent / path).is_file():
            fail("external evidence record file missing")

    rules = memory.get("memory_rules", {})
    required_false = [
        "repetition_upgrades_status", "consensus_is_evidence", "memory_write_failure_changes_authority",
        "platform_mode_changes_authority", "manual_mode_user_skip_of_required_review_promotes_authority",
        "external_content_self_declared_reviewer_is_authenticated",
        "user_attested_external_review_is_provider_api_authenticated",
        "external_evidence_may_satisfy_platform_review_gate",
        "review_disposition_may_override_missing_required_review_evidence",
        "legacy_review_schema_may_promote_material_authority",
        "negative_review_disposition_may_promote_material_authority",
    ]
    for key in required_false:
        if rules.get(key) is not False:
            fail(f"shared-memory rule weakened/missing: {key}")

    if not LOG_PATH.is_file() or not LOG_PATH.read_text(encoding="utf-8").strip():
        fail("decision log missing/empty")

    print(
        "LIVE_CONVERSATION_GOVERNANCE_VALID "
        f"checkpoint={state.get('checkpoint_id')} workstream={work.get('state')} "
        f"result={passed}/{total} review={review.get('current_review_status')} "
        f"mode={review.get('current_collaboration_mode')} review_transport={review.get('current_collaboration_review_transport')} "
        f"external_channel={review.get('current_external_evidence_channel')} shared_memory=ACTIVE"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"LIVE_CONVERSATION_GOVERNANCE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
