"""Authoritative intent idempotency and linearization guard.

The platform, not the model or transport, owns the decision that one logical intent
may produce at most one authoritative append/state mutation.
"""
from __future__ import annotations

from copy import deepcopy


def authorize_intent_append(state: dict, command: dict) -> dict:
    """Atomically decide whether a logical intent may be appended.

    The caller must persist returned state together with the authoritative event in
    one transaction guarded by the expected_state_version compare-and-swap and a
    unique constraint over (actor_id, idempotency_key).
    """
    required = ["actor_id", "idempotency_key", "intent_hash", "expected_state_version"]
    missing = [key for key in required if command.get(key) in (None, "")]
    if missing:
        return {"authorized": False, "reason": "missing required intent fields", "missing": missing, "state": deepcopy(state)}

    try:
        expected = int(command["expected_state_version"])
        current_version = int(state.get("state_version", 0))
    except (TypeError, ValueError):
        return {"authorized": False, "reason": "state version malformed", "state": deepcopy(state)}
    if expected != current_version:
        return {"authorized": False, "reason": "lost authoritative state-version race", "state": deepcopy(state)}

    ledger = state.get("intent_ledger", {})
    if not isinstance(ledger, dict):
        return {"authorized": False, "reason": "intent ledger malformed", "state": deepcopy(state)}

    key = f"{command['actor_id']}::{command['idempotency_key']}"
    existing = ledger.get(key)
    if existing is not None:
        if not isinstance(existing, dict):
            return {"authorized": False, "reason": "intent ledger entry malformed", "state": deepcopy(state)}
        if existing.get("intent_hash") != command["intent_hash"]:
            return {"authorized": False, "reason": "idempotency key reused for a different intent", "state": deepcopy(state)}
        return {
            "authorized": False,
            "duplicate": True,
            "reason": "logical intent already has an authoritative append",
            "authoritative_event_id": existing.get("authoritative_event_id"),
            "state": deepcopy(state),
        }

    event_id = command.get("proposed_event_id")
    if not isinstance(event_id, str) or not event_id:
        return {"authorized": False, "reason": "proposed_event_id is required", "state": deepcopy(state)}

    updated = deepcopy(state)
    updated_ledger = deepcopy(ledger)
    updated_ledger[key] = {
        "intent_hash": command["intent_hash"],
        "authoritative_event_id": event_id,
        "accepted_state_version": current_version,
    }
    updated["intent_ledger"] = updated_ledger
    updated["state_version"] = current_version + 1
    updated["last_authoritative_event_id"] = event_id
    return {
        "authorized": True,
        "duplicate": False,
        "reason": "intent linearized as the single authoritative append",
        "authoritative_event_id": event_id,
        "state": updated,
    }
