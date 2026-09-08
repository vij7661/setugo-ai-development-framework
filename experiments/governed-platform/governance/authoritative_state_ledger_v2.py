from __future__ import annotations

import json
from typing import Any

import authoritative_state_ledger as v1

LedgerError = v1.LedgerError
IdempotencyConflict = v1.IdempotencyConflict
VersionConflict = v1.VersionConflict
AuthorityClaimRejected = v1.AuthorityClaimRejected
CompletionConflict = v1.CompletionConflict
InjectedFailure = v1.InjectedFailure
SimulatedCrashAfterCommit = v1.SimulatedCrashAfterCommit
TransitionResult = v1.TransitionResult


class AuthoritativeStateLedger(v1.AuthoritativeStateLedger):
    """Slice 5 narrow audit-integrity repair.

    Transaction, replay, concurrency and outbox behavior remain inherited from
    v1. Only audit reconstruction is strengthened so persisted digests are
    recomputed from persisted semantics and current state is reconciled with
    replayed event lineage.
    """

    def audit(self, project_id: str) -> dict[str, Any]:
        problems: list[str] = []
        with self._connect() as con:
            events = con.execute(
                "SELECT * FROM accepted_events WHERE project_id=? ORDER BY result_version,event_id",
                (project_id,),
            ).fetchall()
            state = con.execute(
                "SELECT * FROM project_state WHERE project_id=?",
                (project_id,),
            ).fetchone()
            outbox_rows = con.execute(
                "SELECT * FROM outbox WHERE project_id=? ORDER BY outbox_id",
                (project_id,),
            ).fetchall()
            outbox_by_event = {row["event_id"]: row for row in outbox_rows}

            expected_prior = 0
            replayed_state: dict[str, Any] = {}
            event_ids = {event["event_id"] for event in events}

            for event in events:
                if event["prior_version"] != expected_prior or event["result_version"] != expected_prior + 1:
                    problems.append(f"version_lineage:{event['event_id']}")

                try:
                    payload = json.loads(event["payload_json"])
                except Exception:
                    problems.append(f"payload_json:{event['event_id']}")
                    payload = {}

                outbox = outbox_by_event.get(event["event_id"])
                effect_type = outbox["effect_type"] if outbox is not None else None
                try:
                    effect_payload = json.loads(outbox["effect_payload_json"]) if outbox is not None else None
                except Exception:
                    problems.append(f"effect_payload_json:{event['event_id']}")
                    effect_payload = {}

                reconstructed_command = {
                    "project_id": event["project_id"],
                    "idempotency_key": event["idempotency_key"],
                    "command_type": event["command_type"],
                    "payload": payload,
                    "expected_version": event["expected_version"],
                    "effect_type": effect_type,
                    "effect_payload": effect_payload,
                }
                reconstructed_command_digest = v1._digest(reconstructed_command)
                if reconstructed_command_digest != event["command_digest"]:
                    problems.append(f"command_digest:{event['event_id']}")

                try:
                    calculated_state = self._apply_transition(replayed_state, event["command_type"], payload)
                    stored_result_state = json.loads(event["result_state_json"])
                    if v1._canon(calculated_state) != v1._canon(stored_result_state):
                        problems.append(f"result_state_replay:{event['event_id']}")
                except Exception:
                    problems.append(f"result_state_replay:{event['event_id']}")
                    calculated_state = replayed_state
                    try:
                        stored_result_state = json.loads(event["result_state_json"])
                    except Exception:
                        stored_result_state = {}

                result_state_digest = v1._digest(
                    {
                        "project_id": project_id,
                        "version": event["result_version"],
                        "state": stored_result_state,
                    }
                )
                recomputed_result = v1._digest(
                    {
                        "event_id": event["event_id"],
                        "command_digest": reconstructed_command_digest,
                        "prior_version": event["prior_version"],
                        "result_version": event["result_version"],
                        "state_digest": result_state_digest,
                    }
                )
                if recomputed_result != event["result_digest"]:
                    problems.append(f"result_digest:{event['event_id']}")

                replayed_state = calculated_state
                expected_prior = event["result_version"]

            if events:
                if state is None or state["version"] != expected_prior:
                    problems.append("state_version_mismatch")
            elif state is not None and state["version"] != 0:
                problems.append("state_without_events")

            if state is not None:
                try:
                    current_state = json.loads(state["state_json"])
                    expected_state_digest = v1._digest(
                        {
                            "project_id": project_id,
                            "version": state["version"],
                            "state": current_state,
                        }
                    )
                    if expected_state_digest != state["state_digest"]:
                        problems.append("current_state_digest")
                    if events and v1._canon(current_state) != v1._canon(replayed_state):
                        problems.append("current_state_lineage")
                except Exception:
                    problems.append("current_state_json")

            for row in outbox_rows:
                if row["event_id"] not in event_ids:
                    problems.append(f"orphan_outbox:{row['outbox_id']}")
                try:
                    expected_effect = v1._digest(
                        {
                            "effect_type": row["effect_type"],
                            "effect_payload": json.loads(row["effect_payload_json"]),
                        }
                    )
                    if expected_effect != row["effect_digest"]:
                        problems.append(f"effect_digest:{row['outbox_id']}")
                except Exception:
                    problems.append(f"effect_digest:{row['outbox_id']}")

        return {
            "valid": not problems,
            "problems": sorted(set(problems)),
            "event_count": len(events),
            "final_version": expected_prior,
        }
