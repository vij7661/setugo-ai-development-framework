"""Regression tests for provider API request contract preservation."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from provider_api_request_contract import (  # noqa: E402
    assert_governance_change_preserves_provider_request,
    canonical_provider_request,
    provider_request_fingerprint,
)


def sample_request() -> dict:
    return {
        "provider": "deepseek",
        "endpoint": "/chat/completions",
        "method": "POST",
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Return only the requested answer."},
            {"role": "user", "content": "What is 7 multiplied by 8? Reply exactly with 56."},
        ],
        "provider_parameters": {
            "temperature": 0,
            "stream": False,
        },
        "timeout_ms": 60000,
        "retry_policy": {
            "max_attempts": 1,
            "retry_on": [],
        },
    }


class ProviderAPIRequestContractTests(unittest.TestCase):
    def test_governance_only_change_preserves_fingerprint(self):
        before = sample_request()
        after = copy.deepcopy(before)
        fp = assert_governance_change_preserves_provider_request(
            before,
            after,
            change_classes={"CONTROL_PLANE_ONLY", "EVIDENCE_ONLY"},
        )
        self.assertEqual(fp, provider_request_fingerprint(before))

    def test_governance_envelope_is_not_part_of_provider_request(self):
        req = sample_request()
        req["candidate_sha"] = "1" * 40
        with self.assertRaisesRegex(ValueError, "governance metadata leaked"):
            canonical_provider_request(req)

    def test_model_change_is_detected(self):
        before = sample_request()
        after = copy.deepcopy(before)
        after["model"] = "other-model"
        with self.assertRaisesRegex(ValueError, "changed provider request semantics"):
            assert_governance_change_preserves_provider_request(
                before,
                after,
                change_classes={"CONTROL_PLANE_ONLY"},
            )

    def test_message_change_is_detected(self):
        before = sample_request()
        after = copy.deepcopy(before)
        after["messages"][1]["content"] = "What is 9 multiplied by 9?"
        with self.assertRaisesRegex(ValueError, "changed provider request semantics"):
            assert_governance_change_preserves_provider_request(
                before,
                after,
                change_classes={"EVIDENCE_ONLY"},
            )

    def test_timeout_or_retry_change_is_execution_behavior_change(self):
        before = sample_request()
        after = copy.deepcopy(before)
        after["timeout_ms"] = 120000
        # Explicit execution-behavior changes are allowed by this preservation
        # helper only because the caller declared the correct change class.
        assert_governance_change_preserves_provider_request(
            before,
            after,
            change_classes={"API_EXECUTION_BEHAVIOR_CHANGE"},
        )


if __name__ == "__main__":
    unittest.main()
