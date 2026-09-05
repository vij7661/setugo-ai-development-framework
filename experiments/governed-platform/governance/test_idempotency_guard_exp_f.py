import unittest

from idempotency_guard import authorize_intent_append


def state(**overrides):
    value = {"state_version": 10, "intent_ledger": {}}
    value.update(overrides)
    return value


def command(**overrides):
    value = {
        "actor_id": "buyer-7",
        "idempotency_key": "tap-abc",
        "intent_hash": "intent-hash-1",
        "expected_state_version": 10,
        "proposed_event_id": "evt-1",
    }
    value.update(overrides)
    return value


class ExpFIdempotencyGuardTests(unittest.TestCase):
    def test_first_intent_append_is_authorized(self):
        result = authorize_intent_append(state(), command())
        self.assertTrue(result["authorized"])
        self.assertEqual(11, result["state"]["state_version"])

    def test_same_logical_intent_retry_cannot_append_twice(self):
        first = authorize_intent_append(state(), command())
        retry = authorize_intent_append(
            first["state"],
            command(expected_state_version=11, proposed_event_id="evt-2"),
        )
        self.assertFalse(retry["authorized"])
        self.assertTrue(retry["duplicate"])
        self.assertEqual("evt-1", retry["authoritative_event_id"])

    def test_same_idempotency_key_different_intent_is_rejected(self):
        first = authorize_intent_append(state(), command())
        replay = authorize_intent_append(
            first["state"],
            command(expected_state_version=11, intent_hash="intent-hash-2", proposed_event_id="evt-2"),
        )
        self.assertFalse(replay["authorized"])
        self.assertIn("different intent", replay["reason"])

    def test_concurrent_duplicate_loser_cannot_linearize(self):
        base = state()
        winner = authorize_intent_append(base, command(proposed_event_id="evt-a"))
        loser = authorize_intent_append(winner["state"], command(proposed_event_id="evt-b"))
        self.assertFalse(loser["authorized"])
        self.assertIn("state-version race", loser["reason"])

    def test_concurrent_different_intent_loser_with_stale_version_is_rejected(self):
        base = state()
        winner = authorize_intent_append(base, command(proposed_event_id="evt-a"))
        loser = authorize_intent_append(
            winner["state"],
            command(idempotency_key="tap-def", intent_hash="intent-hash-2", proposed_event_id="evt-b"),
        )
        self.assertFalse(loser["authorized"])
        self.assertIn("state-version race", loser["reason"])

    def test_retry_after_refresh_of_distinct_intent_can_linearize(self):
        first = authorize_intent_append(state(), command(proposed_event_id="evt-a"))
        second = authorize_intent_append(
            first["state"],
            command(
                idempotency_key="tap-def",
                intent_hash="intent-hash-2",
                expected_state_version=11,
                proposed_event_id="evt-b",
            ),
        )
        self.assertTrue(second["authorized"])
        self.assertEqual(12, second["state"]["state_version"])

    def test_same_idempotency_key_different_actor_is_distinct_scope(self):
        first = authorize_intent_append(state(), command(proposed_event_id="evt-a"))
        second = authorize_intent_append(
            first["state"],
            command(actor_id="buyer-8", expected_state_version=11, proposed_event_id="evt-b"),
        )
        self.assertTrue(second["authorized"])

    def test_missing_idempotency_key_fails_closed(self):
        result = authorize_intent_append(state(), command(idempotency_key=""))
        self.assertFalse(result["authorized"])

    def test_malformed_intent_ledger_fails_closed(self):
        result = authorize_intent_append(state(intent_ledger=[]), command())
        self.assertFalse(result["authorized"])

    def test_missing_event_identity_fails_closed(self):
        result = authorize_intent_append(state(), command(proposed_event_id=""))
        self.assertFalse(result["authorized"])


if __name__ == "__main__":
    unittest.main()
