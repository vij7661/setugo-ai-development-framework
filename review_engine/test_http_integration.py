from __future__ import annotations

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from review_engine.http_server import ReviewEngineHTTPHandler


class _FakeApp:
    def health(self):
        return {"status": "ok", "assurance_mode": "EXPERIMENTAL_UNQUALIFIED", "reviewers": {}, "action_execution_enabled": False}

    def review(self, payload):
        return {
            "request_id": payload["request_id"],
            "state": "CONVERGED_PASS",
            "reasons": ["test"],
            "final_output": "answer",
            "artifact_hash": "abc",
            "assurance_mode": "EXPERIMENTAL_UNQUALIFIED",
            "action_authorized": False,
            "human_action_approval_required": False,
            "session_chain_valid": True,
        }

    def session_summaries(self, *, limit=100):
        return [{
            "session_id": "s1", "started_at_utc": "2026-09-05 10:00:00", "updated_at_utc": "2026-09-05 10:00:01",
            "event_count": 2, "final_state": "CONVERGED_PASS", "final_reasons": ["test"], "artifact_hash": "abc", "chain_valid": True,
        }][:limit]

    def current_memory(self):
        return []

    def session_events(self, session_id):
        return [{"session_id": session_id, "seq": 1, "event_type": "REQUEST_RECEIVED", "payload": {}, "previous_hash": "GENESIS", "event_hash": "h", "created_at": "2026-09-05 10:00:00"}]


class HTTPVerticalSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ReviewEngineHTTPHandler.app = _FakeApp()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ReviewEngineHTTPHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        ReviewEngineHTTPHandler.app = None

    def _url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def test_dashboard_and_api_are_served_from_same_local_origin(self):
        with urlopen(self._url("/"), timeout=3) as response:
            body = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("Review Engine", body)
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertIn("frame-ancestors 'none'", response.headers.get("Content-Security-Policy"))
        with urlopen(self._url("/health"), timeout=3) as response:
            health = json.loads(response.read())
            self.assertEqual(health["status"], "ok")

    def test_review_post_returns_governed_decision_shape(self):
        body = json.dumps({"request_id": "r-http", "user_input": "hello"}).encode("utf-8")
        request = Request(self._url("/review"), data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=3) as response:
            result = json.loads(response.read())
        self.assertEqual(result["state"], "CONVERGED_PASS")
        self.assertFalse(result["action_authorized"])
        self.assertTrue(result["session_chain_valid"])

    def test_non_json_review_is_rejected(self):
        request = Request(self._url("/review"), data=b"hello", headers={"Content-Type": "text/plain"}, method="POST")
        with self.assertRaises(HTTPError) as raised:
            urlopen(request, timeout=3)
        self.assertEqual(raised.exception.code, 415)

    def test_history_and_event_drilldown_are_queryable(self):
        with urlopen(self._url("/sessions?limit=10"), timeout=3) as response:
            sessions = json.loads(response.read())["sessions"]
        self.assertEqual(sessions[0]["session_id"], "s1")
        with urlopen(self._url("/sessions/s1/events"), timeout=3) as response:
            events = json.loads(response.read())["events"]
        self.assertEqual(events[0]["event_type"], "REQUEST_RECEIVED")


if __name__ == "__main__":
    unittest.main()
