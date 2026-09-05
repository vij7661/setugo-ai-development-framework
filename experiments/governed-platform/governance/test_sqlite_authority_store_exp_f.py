import tempfile
import threading
import unittest
from pathlib import Path

from sqlite_authority_store import commit_intent, initialize_store, snapshot


class ExpFSQLiteAuthorityStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "authority.db"
        initialize_store(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def req(self, event_id="evt-1", key="key-1", intent="intent-a", expected=0, actor="actor-a"):
        return {
            "actor_id": actor,
            "idempotency_key": key,
            "intent_hash": intent,
            "event_id": event_id,
            "expected_state_version": expected,
        }

    def test_first_append_updates_intent_event_and_state_atomically(self):
        result = commit_intent(self.path, self.req())
        self.assertEqual("APPEND", result["decision"])
        state = snapshot(self.path)
        self.assertEqual(1, state["state_version"])
        self.assertEqual(1, len(state["intents"]))
        self.assertEqual(1, len(state["events"]))

    def test_same_intent_retry_returns_original_event_without_second_append(self):
        first = commit_intent(self.path, self.req())
        retry = commit_intent(self.path, self.req(event_id="evt-2", expected=1))
        self.assertEqual("DUPLICATE", retry["decision"])
        self.assertEqual(first["authoritative_event_id"], retry["authoritative_event_id"])
        state = snapshot(self.path)
        self.assertEqual(1, len(state["events"]))

    def test_same_key_different_intent_is_blocked(self):
        commit_intent(self.path, self.req())
        result = commit_intent(self.path, self.req(event_id="evt-2", intent="intent-b", expected=1))
        self.assertEqual("BLOCK", result["decision"])
        self.assertEqual(1, len(snapshot(self.path)["events"]))

    def test_distinct_new_intent_with_stale_version_loses(self):
        commit_intent(self.path, self.req())
        result = commit_intent(self.path, self.req(event_id="evt-2", key="key-2", intent="intent-b", expected=0))
        self.assertEqual("STALE", result["decision"])
        self.assertEqual(1, len(snapshot(self.path)["events"]))

    def test_refreshed_distinct_intent_can_append(self):
        commit_intent(self.path, self.req())
        result = commit_intent(self.path, self.req(event_id="evt-2", key="key-2", intent="intent-b", expected=1))
        self.assertEqual("APPEND", result["decision"])
        state = snapshot(self.path)
        self.assertEqual(2, state["state_version"])
        self.assertEqual(2, len(state["events"]))

    def test_concurrent_distinct_writers_from_same_version_only_one_appends(self):
        barrier = threading.Barrier(3)
        results = []
        lock = threading.Lock()

        def worker(req):
            barrier.wait()
            value = commit_intent(self.path, req)
            with lock:
                results.append(value)

        t1 = threading.Thread(target=worker, args=(self.req(event_id="evt-a", key="key-a", intent="intent-a"),))
        t2 = threading.Thread(target=worker, args=(self.req(event_id="evt-b", key="key-b", intent="intent-b"),))
        t1.start(); t2.start(); barrier.wait(); t1.join(); t2.join()

        decisions = sorted(r["decision"] for r in results)
        self.assertEqual(["APPEND", "STALE"], decisions)
        state = snapshot(self.path)
        self.assertEqual(1, state["state_version"])
        self.assertEqual(1, len(state["events"]))

    def test_concurrent_duplicate_retry_produces_single_authoritative_event(self):
        barrier = threading.Barrier(3)
        results = []
        lock = threading.Lock()

        def worker(event_id):
            barrier.wait()
            value = commit_intent(self.path, self.req(event_id=event_id))
            with lock:
                results.append(value)

        t1 = threading.Thread(target=worker, args=("evt-a",))
        t2 = threading.Thread(target=worker, args=("evt-b",))
        t1.start(); t2.start(); barrier.wait(); t1.join(); t2.join()

        decisions = sorted(r["decision"] for r in results)
        self.assertEqual(["APPEND", "DUPLICATE"], decisions)
        self.assertEqual(1, len(snapshot(self.path)["events"]))

    def test_same_key_is_scoped_by_actor(self):
        first = commit_intent(self.path, self.req(actor="actor-a"))
        second = commit_intent(self.path, self.req(event_id="evt-2", actor="actor-b", expected=1))
        self.assertEqual("APPEND", first["decision"])
        self.assertEqual("APPEND", second["decision"])
        self.assertEqual(2, len(snapshot(self.path)["events"]))

    def test_missing_fields_fail_closed_without_database_mutation(self):
        result = commit_intent(self.path, {"actor_id": "actor-a"})
        self.assertEqual("BLOCK", result["decision"])
        self.assertEqual(0, len(snapshot(self.path)["events"]))


if __name__ == "__main__":
    unittest.main()
