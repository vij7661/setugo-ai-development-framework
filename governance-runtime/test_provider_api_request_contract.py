"""Regression tests for provider API request contract preservation."""
from __future__ import annotations

import copy
import os
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from provider_api_request_contract import (  # noqa: E402
    assert_governance_change_preserves_provider_request,
    canonical_provider_request,
    provider_request_fingerprint,
    gemini_adapter_semantic_request,
    gemini_wire_request_from_semantic,
    assert_gemini_wire_matches_semantic,
    sanitize_semantic_headers,
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

    def test_secret_headers_never_enter_semantic_material(self):
        headers = sanitize_semantic_headers({"Authorization": "Bearer secret", "X-Trace": "stable"})
        self.assertNotIn("Authorization", headers)
        self.assertEqual(headers["x_trace"], "stable")

    def test_nested_structured_governance_metadata_is_rejected(self):
        for key in ("governance_review_blob", "candidate_sha", "authority_effect"):
            req = sample_request()
            req["provider_parameters"]["adapter"] = {"tools": [{key: "leak"}]}
            with self.assertRaisesRegex(ValueError, "forbidden structured metadata"):
                canonical_provider_request(req)

    def test_normalized_governance_and_secret_keys_are_rejected(self):
        for key in (" Candidate_SHA ", "Authority_Effect ", "Authorization", "API-KEY", "x-goog-api-key", " token ", "access_token", "PAT", "password"):
            req = sample_request(); req["provider_parameters"]["nested"] = {key: "secret"}
            with self.assertRaisesRegex(ValueError, "forbidden structured metadata"):
                canonical_provider_request(req)

    def test_retry_policy_is_recursively_governed(self):
        for key in ("candidate_sha", "authority_effect", "authorization", "api_key", "x-api-key", "x-goog-api-key", "token", "access_token", "secret", "password", "PAT"):
            req = sample_request(); req["retry_policy"]["nested"] = {key: "blocked"}
            with self.assertRaisesRegex(ValueError, "forbidden structured metadata"):
                canonical_provider_request(req)

    def test_natural_language_may_discuss_governance_keys(self):
        req = sample_request()
        req["messages"][1]["content"] = "Explain candidate_sha and governance_review_blob in prose."
        canonical_provider_request(req)

    def test_real_gemini_projection_excludes_auth_and_is_secret_invariant(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "first-secret"}):
            first = gemini_adapter_semantic_request(model="gemini-test", prompt="hello")
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "different-secret"}):
            second = gemini_adapter_semantic_request(model="gemini-test", prompt="hello")
        self.assertEqual(provider_request_fingerprint(first), provider_request_fingerprint(second))
        serialized = str(first).lower()
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("authorization", serialized)
        self.assertEqual(first["provider_parameters"]["temperature"], 0.0)
        self.assertEqual(first["timeout_ms"], 180000)

    def test_real_gemini_wire_is_derived_and_drift_fails(self):
        semantic = gemini_adapter_semantic_request(model="gemini-test", prompt="hello")
        wire = gemini_wire_request_from_semantic(semantic)
        assert_gemini_wire_matches_semantic(semantic, wire)
        for mutate in (
            lambda w: w.update(url=w["url"] + "-drift"),
            lambda w: w["payload"]["generationConfig"].update(temperature=1.0),
            lambda w: w.update(timeout_seconds=1),
            lambda w: w["retry_policy"].update(max_attempts=2),
        ):
            bad = copy.deepcopy(wire); mutate(bad)
            with self.assertRaisesRegex(ValueError, "wire request drifted"):
                assert_gemini_wire_matches_semantic(semantic, bad)


if __name__ == "__main__":
    unittest.main()
