#!/usr/bin/env python3
"""Deterministic validator for live conversation governance runtime state."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from review_protocol import (
    ALLOWED_TRANSPORTS,
    PLATFORM_MODES,
    PROMOTABLE_REVIEW_DISPOSITIONS,
    REVIEW_DIMENSION_STATUSES,
    REVIEW_LEVELS,
    SEMANTIC_REVIEW_SCHEMA_VERSION,
    canonical_hash,
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
    "NOT_YET_PRESENT",
    "PENDING_INDEPENDENT_REVIEW",
    "PENDING_EXTERNAL_REVIEW",
    "REVIEW_RECEIVED",
    "REVIEW_VALIDATED",
    "VALID_INDEPENDENT_REVIEW_PRESENT",
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

    if state.get("schema_version") != 3:
        fail("unsupported session-state schema")
    if state.get("checkpoint_state") not in ALLOWED_CHECKPOINT_STATES:
        fail("invalid checkpoint_state")
    authority = state.get("authority", {})
    if authority.get("repository") != "vij7661/setugo-ai-development-framework":
        fail("authoritative repository changed unexpectedly")
    if authority.get("source_precedence") != EXPECTED_PRECEDENCE:
        fail("authority precedence changed or weakened")

    runtime = state.get("runtime", {})
    if runtime.get("branch") != "governance/live-conversation-runtime":
        fail("runtime branch identity changed unexpectedly")
    if runtime.get("normative_contract_path") != "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md":
        fail("normative contract path changed unexpectedly")
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
        fail("shared-memory write ordering weakened")
    if shared.get("on_write_failure_after_authoritative_persist") != "AUTHORITY_REMAINS_VALID_MEMORY_STALE":
        fail("memory failure semantics weakened")
    if shared.get("on_authoritative_persist_failure") != "BLOCK_AUTHORITATIVE_COMPLETION":
        fail("authoritative persistence failure must block completion")

    if memory.get("schema_version") != 2 or memory.get("state") != "ACTIVE":
        fail("shared-memory artifact malformed/inactive")
    if memory.get("independent_authority") is not False:
        fail("shared-memory artifact claims authority")
    if memory.get("read_policy") != "READ_AT_SESSION_START_THEN_VERIFY_MATERIAL_POINTERS_AGAINST_AUTHORITY":
        fail("shared-memory read policy invalid")
    if memory.get("write_policy") != "AUTHORITATIVE_PERSIST_FIRST_THEN_SYNCHRONIZE_MEMORY":
        fail("shared-memory write policy invalid")

    work = state.get("active_workstream", {})
    for key in ("branch", "head_commit", "state", "next_action", "forbidden_shortcut"):
        if not work.get(key):
            fail(f"active_workstream.{key} is required")
    for key in (
        "head_commit",
        "preregistration_commit",
        "frozen_acceptance_harness_commit",
        "first_mechanism_commit",
        "preserved_failure_record_commit",
    ):
        require_sha(work.get(key), f"active_workstream.{key}")
    latest = work.get("latest_result", {})
    passed, total, failures = latest.get("passed"), latest.get("total"), latest.get("failures")
    if not isinstance(passed, int) or not isinstance(total, int) or not isinstance(failures, list):
        fail("latest_result malformed")
    if passed < 0 or total <= 0 or passed > total or len(failures) != total - passed:
        fail("latest_result counts inconsistent")

    mem_work = memory.get("current_work", {})
    if mem_work.get("authoritative_branch") != work.get("branch"):
        fail("shared memory workstream branch differs from authority")
    if mem_work.get("authoritative_head") != work.get("head_commit"):
        fail("shared memory workstream head differs from authority")
    if mem_work.get("status") != work.get("state"):
        fail("shared memory workstream state differs from authority")

    review = state.get("independent_review", {})
    if review.get("policy_state") != "MANDATORY_FOR_MATERIAL_AUTHORITY_TRANSITIONS":
        fail("mandatory review policy weakened")
    if review.get("semantic_review_schema_minimum_for_promotion") != SEMANTIC_REVIEW_SCHEMA_VERSION:
        fail("semantic review schema floor changed or missing")
    if set(review.get("positive_promotable_dispositions", [])) != set(PROMOTABLE_REVIEW_DISPOSITIONS):
        fail("positive promotable review dispositions changed")
    if set(review.get("platform_modes", [])) != set(PLATFORM_MODES):
        fail("platform modes invalid")
    if set(review.get("review_levels", [])) != set(REVIEW_LEVELS):
        fail("review levels invalid")
    if set(review.get("supported_transports", [])) != set(ALLOWED_TRANSPORTS):
        fail("review transports invalid")
    if review.get("current_collaboration_mode") != "MANUAL_MODE":
        fail("this collaboration must emulate MANUAL_MODE")
    if review.get("current_collaboration_transport") != "MANUAL_RELAY":
        fail("this collaboration must use MANUAL_RELAY")
    if review.get("production_auto_mode_transport") != "AUTOMATIC_API":
        fail("AUTO_MODE transport changed")
    if review.get("production_manual_mode_transport") != "USER_INITIATED_API":
        fail("MANUAL_MODE production transport changed")
    if review.get("transport_may_change_policy") is not False or review.get("platform_mode_may_change_authority") is not False:
        fail("mode/transport may not change authority")
    if review.get("current_review_status") not in ALLOWED_REVIEW_STATUS:
        fail("invalid current review status")
    if review.get("consensus_is_evidence") is not False:
        fail("consensus must not be evidence")
    if review.get("fallback_if_unavailable") != "PENDING_INDEPENDENT_REVIEW":
        fail("review-unavailable fallback weakened")

    mem_runtime = memory.get("governance_runtime", {})
    if mem_runtime.get("current_review_request_id") != review.get("current_review_request_id"):
        fail("shared memory current review request differs from authority")
    if mem_runtime.get("current_review_status") != review.get("current_review_status"):
        fail("shared memory current review status differs from authority")
    if mem_runtime.get("production_auto_mode_transport") != "AUTOMATIC_API":
        fail("shared memory lost AUTO_MODE transport")
    if mem_runtime.get("production_manual_mode_transport") != "USER_INITIATED_API":
        fail("shared memory lost MANUAL_MODE transport")
    if mem_runtime.get("semantic_review_schema_minimum_for_promotion") != SEMANTIC_REVIEW_SCHEMA_VERSION:
        fail("shared memory lost semantic review schema floor")
    if set(mem_runtime.get("positive_promotable_dispositions", [])) != set(PROMOTABLE_REVIEW_DISPOSITIONS):
        fail("shared memory lost promotable disposition floor")

    pending = memory.get("pending_reviews")
    if not isinstance(pending, list) or not pending or not isinstance(pending[0], dict):
        fail("shared memory pending review coordination missing")
    mem_review = pending[0]
    if mem_review.get("transport") not in ALLOWED_TRANSPORTS or mem_review.get("platform_mode") not in PLATFORM_MODES:
        fail("shared memory pending review mode/transport invalid")

    promotion = runtime.get("promotion", {})
    active_id = review.get("current_review_request_id")
    if active_id is None:
        if promotion.get("state") != "PENDING_CANDIDATE_FREEZE":
            fail("no active review requires PENDING_CANDIDATE_FREEZE")
        if mem_review.get("status") != "PENDING_CANDIDATE_FREEZE":
            fail("shared memory disagrees with candidate-freeze state")
        if review.get("current_review_status") != "NOT_YET_PRESENT":
            fail("candidate-freeze state pretends review exists")
    else:
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
            fail("active material review must use semantic ReviewRequest schema 4")
        dimensions = request.get("required_review_dimensions")
        if not isinstance(dimensions, list) or not dimensions:
            fail("active semantic review lacks required dimensions")
        if set(request.get("review_dimension_status_vocabulary", [])) != set(REVIEW_DIMENSION_STATUSES):
            fail("active semantic review status vocabulary invalid")
        if request.get("review_request_id") != active_id:
            fail("active request ID differs from authority")
        reviewed_commit = review.get("current_reviewed_artifact_commit")
        require_sha(reviewed_commit, "independent_review.current_reviewed_artifact_commit")
        if request.get("artifact", {}).get("commit") != reviewed_commit:
            fail("active review request targets wrong candidate")
        if promotion.get("reviewed_candidate_commit") != reviewed_commit:
            fail("promotion candidate differs from active request")
        if mem_review.get("review_request_id") != active_id or mem_review.get("reviewed_artifact_commit") != reviewed_commit:
            fail("shared memory active review binding differs from authority")
        if mem_review.get("status") not in {"PENDING_EXTERNAL_REVIEW", "REVIEW_RECEIVED", "REVIEW_VALIDATED"}:
            fail("shared memory active review state invalid")

        if review.get("current_collaboration_transport") == "MANUAL_RELAY":
            manifest_path_value = promotion.get("portable_bundle_manifest_path")
            if not isinstance(manifest_path_value, str) or not manifest_path_value.startswith("governance-runtime/review-bundles/"):
                fail("manual relay requires governed packet manifest")
            manifest_path = ROOT.parent / manifest_path_value
            if not manifest_path.is_file():
                fail("packet manifest missing")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            schema = manifest.get("schema_version")
            if schema != 4:
                fail("active semantic review packet manifest must use schema 4")
            if manifest.get("review_request_id") != active_id or manifest.get("reviewed_candidate_commit") != reviewed_commit:
                fail("packet manifest review binding invalid")
            if canonical_hash(manifest.get("required_review_dimensions", [])) != canonical_hash(dimensions):
                fail("packet manifest semantic dimensions differ from ReviewRequest")
            if manifest.get("repository_access_required") is not False:
                fail("manual packet must not require repository access")
            if manifest.get("bundle_storage") not in {"EXTERNAL_USER_PORTABLE_FILE", "GITHUB_ACTIONS_ARTIFACT_EXPORT"}:
                fail("packet storage mode invalid")
            require_sha256(manifest.get("bundle_file_sha256"), "packet.bundle_file_sha256")
            if manifest.get("bundle_body_sha256") is not None:
                require_sha256(manifest.get("bundle_body_sha256"), "packet.bundle_body_sha256")
            if manifest.get("logical_bundle_sha256") is not None:
                require_sha256(manifest.get("logical_bundle_sha256"), "packet.logical_bundle_sha256")
            embedded = manifest.get("embedded_artifacts")
            if not isinstance(embedded, list) or not embedded:
                fail("packet manifest lacks embedded artifacts")
            for idx, item in enumerate(embedded):
                if not isinstance(item, dict) or not item.get("path"):
                    fail(f"packet artifact {idx} malformed")
                require_sha256(item.get("content_sha256"), f"packet.artifact[{idx}].content_sha256")
                if not isinstance(item.get("bytes_utf8"), int) or item["bytes_utf8"] <= 0:
                    fail(f"packet artifact {idx} byte length invalid")
                if item.get("hash_basis") != "RAW_GIT_BLOB_UTF8_BYTES":
                    fail(f"packet artifact {idx} raw hash basis missing")
                if not isinstance(item.get("raw_export_path"), str) or not item.get("raw_export_path", "").startswith("raw-artifacts/"):
                    fail(f"packet artifact {idx} raw export path missing")
            if manifest.get("raw_artifacts_are_byte_authoritative") is not True:
                fail("semantic packet must declare raw artifacts byte-authoritative")
            if manifest.get("bundle_storage") == "GITHUB_ACTIONS_ARTIFACT_EXPORT":
                if not isinstance(manifest.get("actions_artifact_id"), int) or manifest["actions_artifact_id"] <= 0:
                    fail("packet manifest missing Actions artifact ID")
                if not isinstance(manifest.get("actions_run_id"), int) or manifest["actions_run_id"] <= 0:
                    fail("packet manifest missing Actions run ID")
                digest = manifest.get("actions_artifact_digest")
                if not isinstance(digest, str) or not ARTIFACT_DIGEST.fullmatch(digest):
                    fail("packet manifest missing Actions digest")
            if mem_review.get("portable_bundle_manifest_path") != manifest_path_value:
                fail("shared memory packet manifest differs from authority")
            if mem_review.get("portable_bundle_sha256") != manifest.get("bundle_file_sha256"):
                fail("shared memory packet hash differs from manifest")

    superseded = set(review.get("superseded_review_requests", [])) | set(promotion.get("superseded_review_requests", []))
    for request_id in superseded:
        if not isinstance(request_id, str) or not request_id:
            fail("superseded request ID malformed")
        if not (ROOT / "review-requests" / f"{request_id}.json").is_file():
            fail(f"superseded review request file missing: {request_id}")

    rules = memory.get("memory_rules", {})
    required_rules = {
        "repetition_upgrades_status": False,
        "consensus_is_evidence": False,
        "material_claim_requires_authority_resolution_before_promotion": True,
        "stale_memory_must_be_marked_and_repaired": True,
        "memory_write_failure_changes_authority": False,
        "memory_write_failure_must_be_surfaced": True,
        "platform_mode_changes_authority": False,
        "manual_mode_user_skip_of_required_review_promotes_authority": False,
        "review_disposition_may_override_missing_required_review_evidence": False,
        "legacy_review_schema_may_promote_material_authority": False,
        "negative_review_disposition_may_promote_material_authority": False,
    }
    for key, expected in required_rules.items():
        if rules.get(key) is not expected:
            fail(f"shared-memory rule invalid: {key}")
    if rules.get("manual_relay_self_declared_reviewer_identity_is_authenticated", False) is not False:
        fail("manual relay self-declared identity must not authenticate reviewer")

    continuity = state.get("continuity", {})
    if continuity.get("project_chat_is_authoritative") is not False:
        fail("project chat must remain non-authoritative")
    if continuity.get("shared_memory_is_active") is not True or continuity.get("shared_memory_is_independent_authority") is not False:
        fail("continuity shared-memory semantics invalid")
    if continuity.get("model_memory_is_authoritative") is not False:
        fail("model memory must remain non-authoritative")
    if continuity.get("new_chat_bootstrap_required") is not True or continuity.get("bootstrap_sequence") != "SHARED_MEMORY_THEN_GIT_VERIFICATION":
        fail("new-chat bootstrap weakened")
    if continuity.get("on_git_unavailable") != "GROUNDING_REQUIRED":
        fail("Git-unavailable state must fail closed")

    event_ids = set()
    for line_no, raw in enumerate(LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        event = json.loads(raw)
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            fail(f"decision-log line {line_no} missing event_id")
        if event_id in event_ids:
            fail(f"duplicate decision-log event_id: {event_id}")
        event_ids.add(event_id)
        if not isinstance(event.get("event_type"), str) or not isinstance(event.get("state"), str):
            fail(f"decision-log line {line_no} malformed")
    if not event_ids:
        fail("decision log empty")

    print(
        "LIVE_CONVERSATION_GOVERNANCE_VALID "
        f"checkpoint={state['checkpoint_id']} workstream={work['state']} result={passed}/{total} "
        f"review={review['current_review_status']} mode={review['current_collaboration_mode']} "
        f"transport={review['current_collaboration_transport']} shared_memory={memory['state']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as exc:
        print(f"LIVE_CONVERSATION_GOVERNANCE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
