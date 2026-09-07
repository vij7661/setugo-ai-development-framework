#!/usr/bin/env python3
"""Deterministic validator for the live conversation governance checkpoint."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "session-state.json"
LOG_PATH = ROOT / "decision-log.jsonl"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

EXPECTED_PRECEDENCE = [
    "governed_git_state",
    "governed_registries_and_evidence",
    "project_chat_and_files_advisory",
    "continuity_summaries_and_memory_advisory",
    "model_recollection_non_authoritative",
]

ALLOWED_CHECKPOINT_STATES = {"ACTIVE", "GROUNDING_REQUIRED", "SUSPENDED", "SUPERSEDED"}
ALLOWED_REVIEW_STATUS = {
    "NOT_YET_PRESENT",
    "PENDING_INDEPENDENT_REVIEW",
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

    for field in (
        "schema_version",
        "checkpoint_id",
        "checkpoint_state",
        "authority",
        "runtime",
        "applicable_standards",
        "active_workstream",
        "independent_review",
        "continuity",
    ):
        if field not in state:
            fail(f"missing required top-level field: {field}")

    if state["schema_version"] != 1:
        fail("unsupported schema_version")
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
        if failure.get("unauthorized_mutation_observed") is True:
            # This does not erase such a result; it forces the checkpoint to stop
            # pretending normal construction may continue.
            if state["checkpoint_state"] != "GROUNDING_REQUIRED":
                fail("unauthorized mutation requires GROUNDING_REQUIRED checkpoint state")

    review = state["independent_review"]
    if review.get("policy_state") != "MANDATORY_FOR_MATERIAL_AUTHORITY_TRANSITIONS":
        fail("mandatory independent-review policy was weakened")
    if review.get("current_review_status") not in ALLOWED_REVIEW_STATUS:
        fail("invalid independent-review status")
    if review.get("consensus_is_evidence") is not False:
        fail("consensus must not be treated as evidence")
    if review.get("fallback_if_unavailable") != "PENDING_INDEPENDENT_REVIEW":
        fail("review-unavailable fallback must remain PENDING_INDEPENDENT_REVIEW")

    continuity = state["continuity"]
    if continuity.get("project_chat_is_authoritative") is not False:
        fail("Project chat must remain non-authoritative")
    if continuity.get("memory_is_authoritative") is not False:
        fail("memory must remain non-authoritative")
    if continuity.get("new_chat_bootstrap_required") is not True:
        fail("new-chat Git bootstrap must remain required")
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
        f"review={review['current_review_status']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as exc:
        print(f"LIVE_CONVERSATION_GOVERNANCE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
