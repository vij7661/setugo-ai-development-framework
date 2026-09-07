#!/usr/bin/env python3
"""Deterministic validator for the live conversation governance runtime."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from review_protocol import ALLOWED_TRANSPORTS, MANDATORY_REVIEW_TRIGGERS

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "session-state.json"
MEMORY_PATH = ROOT / "shared-memory.json"
LOG_PATH = ROOT / "decision-log.jsonl"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

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
    "VALID_INDEPENDENT_REVIEW_PRESENT",
    "REVIEW_INDEPENDENCE_UNPROVEN",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def require_sha(value: object, field: str) -> None:
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        fail(f"{field} must be a lowercase 40-character Git SHA")


def main() -> int:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

    for field in (
        "schema_version",
        "checkpoint_id",
        "checkpoint_state",
        "authority",
        "runtime",
        "shared_memory",
        "applicable_standards",
        "active_workstream",
        "independent_review",
        "continuity",
    ):
        if field not in state:
            fail(f"missing required top-level field: {field}")

    if state["schema_version"] != 2:
        fail("unsupported session-state schema_version")
    if state["checkpoint_state"] not in ALLOWED_CHECKPOINT_STATES:
        fail("invalid checkpoint_state")
    if state["authority"].get("repository") != "vij7661/setugo-ai-development-framework":
        fail("authoritative repository changed unexpectedly")
    if state["authority"].get("source_precedence") != EXPECTED_PRECEDENCE:
        fail("source precedence is missing, reordered, or weakened")

    runtime = state["runtime"]
    if runtime.get("branch") != "governance/live-conversation-runtime":
        fail("runtime branch identity changed unexpectedly")
    if runtime.get("normative_contract_path") != "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md":
        fail("normative contract path changed unexpectedly")
    require_sha(runtime.get("normative_contract_commit"), "runtime.normative_contract_commit")

    shared = state["shared_memory"]
    if shared.get("path") != "governance-runtime/shared-memory.json":
        fail("shared-memory path changed unexpectedly")
    if shared.get("active") is not True:
        fail("shared project memory must be active")
    if shared.get("independent_authority") is not False:
        fail("shared project memory must not become independent authority")
    if shared.get("bootstrap_order") != "READ_THEN_VERIFY_AGAINST_GIT":
        fail("shared-memory bootstrap must read memory then verify against Git")
    if shared.get("on_conflict") != "AUTHORITATIVE_STATE_WINS_AND_MEMORY_REASSESSMENT_REQUIRED":
        fail("shared-memory conflict policy was weakened")
    if shared.get("write_order") != "AUTHORITATIVE_PERSIST_FIRST_THEN_MEMORY_SYNC":
        fail("shared-memory write ordering was weakened")
    if shared.get("on_write_failure_after_authoritative_persist") != "AUTHORITY_REMAINS_VALID_MEMORY_STALE":
        fail("memory write failure must not change already durable authority")
    if shared.get("on_authoritative_persist_failure") != "BLOCK_AUTHORITATIVE_COMPLETION":
        fail("authoritative persistence failure must block completion")

    if memory.get("schema_version") != 1 or memory.get("state") != "ACTIVE":
        fail("shared-memory artifact is malformed or inactive")
    if memory.get("independent_authority") is not False:
        fail("shared-memory artifact claims independent authority")
    if memory.get("read_policy") != "READ_AT_SESSION_START_THEN_VERIFY_MATERIAL_POINTERS_AGAINST_AUTHORITY":
        fail("shared-memory read policy is invalid")
    if memory.get("write_policy") != "AUTHORITATIVE_PERSIST_FIRST_THEN_SYNCHRONIZE_MEMORY":
        fail("shared-memory write policy is invalid")

    standards = state["applicable_standards"]
    if not isinstance(standards, list) or not standards:
        fail("at least one applicable standard is required")
    for index, item in enumerate(standards):
        if not isinstance(item, dict) or not item.get("path") or not item.get("branch"):
            fail(f"applicable_standards[{index}] is malformed")
        require_sha(item.get("blob_sha"), f"applicable_standards[{index}].blob_sha")

    work = state["active_workstream"]
    for field in ("name", "branch", "state", "next_action", "forbidden_shortcut"):
        if not isinstance(work.get(field), str) or not work[field]:
            fail(f"active_workstream.{field} is required")
    for field in (
        "head_commit",
        "preregistration_commit",
        "frozen_acceptance_harness_commit",
        "first_mechanism_commit",
        "preserved_failure_record_commit",
    ):
        require_sha(work.get(field), f"active_workstream.{field}")

    mem_work = memory.get("current_work", {})
    if mem_work.get("authoritative_branch") != work.get("branch"):
        fail("shared memory points to a different active workstream branch")
    if mem_work.get("authoritative_head") != work.get("head_commit"):
        fail("shared memory is stale: active workstream head differs from session state")
    if mem_work.get("status") != work.get("state"):
        fail("shared memory is stale: active workstream state differs from session state")

    latest = work.get("latest_result")
    if not isinstance(latest, dict):
        fail("active_workstream.latest_result is required")
    passed = latest.get("passed")
    total = latest.get("total")
    if not isinstance(passed, int) or not isinstance(total, int) or passed < 0 or total <= 0 or passed > total:
        fail("latest_result passed/total is invalid")
    failures = latest.get("failures", [])
    if not isinstance(failures, list) or len(failures) != total - passed:
        fail("latest_result failure count does not correspond to passed/total")
    for failure in failures:
        if not isinstance(failure, dict):
            fail("latest_result failure entry is malformed")
        if failure.get("unauthorized_mutation_observed") is True and state["checkpoint_state"] != "GROUNDING_REQUIRED":
            fail("unauthorized mutation requires GROUNDING_REQUIRED checkpoint state")

    review = state["independent_review"]
    if review.get("policy_state") != "MANDATORY_FOR_MATERIAL_AUTHORITY_TRANSITIONS":
        fail("mandatory independent-review policy was weakened")
    if set(review.get("supported_transports", [])) != set(ALLOWED_TRANSPORTS):
        fail("review transports must include exactly MANUAL_RELAY and AUTOMATIC_API")
    if review.get("current_collaboration_transport") != "MANUAL_RELAY":
        fail("this collaboration must use MANUAL_RELAY until a valid API reviewer is connected")
    if review.get("production_default_intent") != "AUTOMATIC_API_WHEN_CONFIGURED":
        fail("production automatic API intent was removed")
    if review.get("transport_may_change_policy") is not False:
        fail("review transport must not be allowed to change governance policy")
    if review.get("current_review_status") not in ALLOWED_REVIEW_STATUS:
        fail("invalid independent-review status")
    if review.get("consensus_is_evidence") is not False:
        fail("consensus must not be treated as evidence")
    if review.get("fallback_if_unavailable") != "PENDING_INDEPENDENT_REVIEW":
        fail("review-unavailable fallback must remain PENDING_INDEPENDENT_REVIEW")
    if not MANDATORY_REVIEW_TRIGGERS:
        fail("mandatory review trigger set must not be empty")

    pending_reviews = memory.get("pending_reviews")
    if not isinstance(pending_reviews, list) or not pending_reviews:
        fail("shared memory must retain pending review coordination")
    for item in pending_reviews:
        if item.get("transport") not in ALLOWED_TRANSPORTS:
            fail("shared-memory pending review uses unsupported transport")
        if item.get("status") not in {"PENDING_CANDIDATE_FREEZE", "PENDING_EXTERNAL_REVIEW", "REVIEW_RECEIVED", "REVIEW_VALIDATED"}:
            fail("shared-memory pending review has invalid status")

    memory_rules = memory.get("memory_rules", {})
    if memory_rules.get("repetition_upgrades_status") is not False:
        fail("memory repetition must not upgrade status")
    if memory_rules.get("consensus_is_evidence") is not False:
        fail("memory consensus must not become evidence")
    if memory_rules.get("material_claim_requires_authority_resolution_before_promotion") is not True:
        fail("material memory claims must resolve against authority before promotion")
    if memory_rules.get("memory_write_failure_changes_authority") is not False:
        fail("memory write failure must not change authority")
    if memory_rules.get("memory_write_failure_must_be_surfaced") is not True:
        fail("memory write failure must be surfaced")

    continuity = state["continuity"]
    if continuity.get("project_chat_is_authoritative") is not False:
        fail("Project chat must remain non-authoritative")
    if continuity.get("shared_memory_is_active") is not True:
        fail("shared memory must remain active")
    if continuity.get("shared_memory_is_independent_authority") is not False:
        fail("shared memory must not become independent authority")
    if continuity.get("model_memory_is_authoritative") is not False:
        fail("model memory must remain non-authoritative")
    if continuity.get("new_chat_bootstrap_required") is not True:
        fail("new-chat governed bootstrap must remain required")
    if continuity.get("bootstrap_sequence") != "SHARED_MEMORY_THEN_GIT_VERIFICATION":
        fail("new-chat bootstrap must use shared memory then Git verification")
    if continuity.get("on_git_unavailable") != "GROUNDING_REQUIRED":
        fail("Git-unavailable state must be GROUNDING_REQUIRED")
    if continuity.get("user_repetition_required_when_governed_state_exists") is not False:
        fail("user repetition must not be required when governed state exists")

    event_ids: set[str] = set()
    for line_no, raw in enumerate(LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        event = json.loads(raw)
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            fail(f"decision-log line {line_no} has no event_id")
        if event_id in event_ids:
            fail(f"duplicate decision-log event_id: {event_id}")
        event_ids.add(event_id)
        if not isinstance(event.get("event_type"), str) or not isinstance(event.get("state"), str):
            fail(f"decision-log line {line_no} is malformed")

    if not event_ids:
        fail("decision log must contain at least one event")

    print(
        "LIVE_CONVERSATION_GOVERNANCE_VALID "
        f"checkpoint={state['checkpoint_id']} "
        f"workstream={work['state']} "
        f"result={passed}/{total} "
        f"review={review['current_review_status']} "
        f"transport={review['current_collaboration_transport']} "
        f"shared_memory={memory['state']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as exc:
        print(f"LIVE_CONVERSATION_GOVERNANCE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
