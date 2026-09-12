import unittest

from api_call_gate import (
    build_policy_hash,
    build_request_hash,
    validate_preflight,
    validate_receipt,
    validate_dispatch_history,
)

H64 = "b"*64

def base_policy():
    p = {
        "schema_version": 1,
        "policy_id": "API-GOV-V1",
        "phase_rules": {
            "DESIGN_REVIEW": {
                "allowed_call_classes": ["REVIEW_API", "RESEARCH_API", "READ_ONLY_API"],
                "allowed_transports": ["AUTOMATIC_API", "USER_INITIATED_API"],
                "manual_review_only": False,
            },
            "TESTING_FALSIFICATION": {
                "allowed_call_classes": ["READ_ONLY_API"],
                "allowed_transports": ["USER_INITIATED_API"],
                "manual_review_only": True,
            },
        },
    }
    p["policy_hash"] = build_policy_hash(p)
    return p

def base_envelope(policy=None):
    policy = policy or base_policy()
    env = {
        "schema_version": 1,
        "call_id": "call-1",
        "intent_id": "intent-1",
        "attempt_no": 1,
        "transport": "AUTOMATIC_API",
        "call_class": "REVIEW_API",
        "authority_effect": "EVIDENCE_ONLY",
        "phase": "DESIGN_REVIEW",
        "governance_policy_id": policy["policy_id"],
        "governance_policy_hash": policy["policy_hash"],
        "provider": "provider-a",
        "model": "model-x",
        "endpoint_origin": "https://api.example.test",
        "credential_ref": "secret://reviewer/provider-a",
        "request_payload_sha256": H64,
        "context_bundle_sha256": "c"*64,
        "secrets_in_payload": False,
        "request_metadata": {"purpose": "review"},
        "retry_policy": {
            "max_attempts": 3,
            "reuse_intent_id": True,
            "blind_retry_after_outcome_unknown": False,
            "retryable_http_statuses": [429, 500, 502, 503, 504],
        },
        "fallback_policy": {
            "allowed_targets": [
                {"provider": "provider-a", "model": "model-x"},
                {"provider": "provider-b", "model": "model-y"},
            ],
            "silent_provider_or_model_substitution": False,
            "stop_on_first_qualified_success": True,
        },
        "candidate_commit": "a"*40,
        "review_request_id": "REV-1",
        "expected_response_contract": {
            "required_fields": ["disposition", "findings"],
        },
    }
    env["envelope_hash"] = build_request_hash(env)
    return env

def base_receipt(env):
    return {
        "schema_version": 1,
        "call_id": env["call_id"],
        "intent_id": env["intent_id"],
        "attempt_no": env["attempt_no"],
        "request_envelope_hash": env["envelope_hash"],
        "adapter_identity_assurance": "PROVIDER_ADAPTER_AUTHENTICATED",
        "actual_provider": env["provider"],
        "actual_model": env["model"],
        "dispatch_state": "SUCCEEDED",
        "http_status": 200,
        "response_payload_sha256": "d"*64,
        "response_schema_valid": True,
        "assistant_content_present": True,
        "observed_response_fields": ["disposition", "findings"],
        "review_request_id": env["review_request_id"],
        "candidate_commit": env["candidate_commit"],
        "secrets_redacted": True,
        "provider_request_id": "provider-request-123",
        "latency_ms": 1200,
    }

class APICallGateTests(unittest.TestCase):
    def test_valid_preflight(self):
        policy = base_policy()
        env = base_envelope(policy)
        ok, errors = validate_preflight(env, policy)
        self.assertTrue(ok, errors)

    def test_testing_phase_review_api_is_blocked(self):
        policy = base_policy()
        env = base_envelope(policy)
        env["phase"] = "TESTING_FALSIFICATION"
        env["transport"] = "USER_INITIATED_API"
        env["envelope_hash"] = build_request_hash(env)
        ok, errors = validate_preflight(env, policy)
        self.assertFalse(ok)
        self.assertIn("API_PHASE_POLICY_PROHIBITS_CALL", errors)
        self.assertIn("API_PHASE_POLICY_MANUAL_REVIEW_ONLY", errors)

    def test_silent_provider_substitution_blocked(self):
        policy = base_policy()
        env = base_envelope(policy)
        receipt = base_receipt(env)
        receipt["actual_provider"] = "provider-b"
        ok, errors = validate_receipt(env, receipt, policy)
        self.assertFalse(ok)
        self.assertIn("API_PROVIDER_IDENTITY_MISMATCH", errors)

    def test_missing_assistant_content_rejected(self):
        policy = base_policy()
        env = base_envelope(policy)
        receipt = base_receipt(env)
        receipt["assistant_content_present"] = False
        ok, errors = validate_receipt(env, receipt, policy)
        self.assertFalse(ok)
        self.assertIn("API_RESPONSE_CONTENT_MISSING", errors)

    def test_outcome_unknown_cannot_qualify(self):
        policy = base_policy()
        env = base_envelope(policy)
        receipt = base_receipt(env)
        receipt["dispatch_state"] = "OUTCOME_UNKNOWN"
        ok, errors = validate_receipt(env, receipt, policy)
        self.assertFalse(ok)
        self.assertIn("API_OUTCOME_UNKNOWN_CANNOT_QUALIFY", errors)

    def test_secret_literal_rejected(self):
        policy = base_policy()
        env = base_envelope(policy)
        env["request_metadata"] = {"api_key": "actual-secret"}
        env["envelope_hash"] = build_request_hash(env)
        ok, errors = validate_preflight(env, policy)
        self.assertFalse(ok)
        self.assertTrue(any(x.startswith("API_SECRET_LITERAL_PRESENT") for x in errors))

    def test_review_candidate_binding_rejected(self):
        policy = base_policy()
        env = base_envelope(policy)
        receipt = base_receipt(env)
        receipt["candidate_commit"] = "f"*40
        ok, errors = validate_receipt(env, receipt, policy)
        self.assertFalse(ok)
        self.assertIn("API_REVIEW_CANDIDATE_BINDING_MISMATCH", errors)

    def test_mutating_call_requires_idempotency_key(self):
        policy = base_policy()
        policy["phase_rules"]["DESIGN_REVIEW"]["allowed_call_classes"].append("MUTATING_API")
        policy["policy_hash"] = build_policy_hash(policy)
        env = base_envelope(policy)
        env["call_class"] = "MUTATING_API"
        env["authority_effect"] = "AUTHORITY_AFFECTING"
        env.pop("candidate_commit")
        env.pop("review_request_id")
        env["envelope_hash"] = build_request_hash(env)
        ok, errors = validate_preflight(env, policy)
        self.assertFalse(ok)
        self.assertIn("API_IDEMPOTENCY_KEY_REQUIRED", errors)

    def test_stop_after_first_qualified_success(self):
        policy = base_policy()
        env = base_envelope(policy)
        env["attempt_no"] = 2
        env["provider"] = "provider-b"
        env["model"] = "model-y"
        env["call_id"] = "call-2"
        env["envelope_hash"] = build_request_hash(env)
        history = [{
            "intent_id": "intent-1",
            "attempt_no": 1,
            "dispatch_state": "SUCCEEDED",
            "gate_result": "API_RESULT_QUALIFIED",
        }]
        ok, errors = validate_dispatch_history(env, history)
        self.assertFalse(ok)
        self.assertIn("API_FALLBACK_AFTER_QUALIFIED_SUCCESS", errors)

    def test_mutating_retry_after_unknown_requires_reconciliation(self):
        policy = base_policy()
        policy["phase_rules"]["DESIGN_REVIEW"]["allowed_call_classes"].append("MUTATING_API")
        policy["policy_hash"] = build_policy_hash(policy)
        env = base_envelope(policy)
        env["call_class"] = "MUTATING_API"
        env["authority_effect"] = "AUTHORITY_AFFECTING"
        env["idempotency_key"] = "idem-1"
        env.pop("candidate_commit")
        env.pop("review_request_id")
        env["attempt_no"] = 2
        env["call_id"] = "call-2"
        env["envelope_hash"] = build_request_hash(env)
        history = [{
            "intent_id": "intent-1",
            "attempt_no": 1,
            "dispatch_state": "OUTCOME_UNKNOWN",
        }]
        ok, errors = validate_dispatch_history(env, history)
        self.assertFalse(ok)
        self.assertIn("API_OUTCOME_UNKNOWN_REQUIRES_RECONCILIATION", errors)

if __name__ == "__main__":
    unittest.main()
