from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from review_engine.models import ReviewerConfig, ReviewerResponse
from review_engine.providers import ProviderRegistry, _parse_response
from review_engine.truth_contract import neutral_epistemic_review


class DummyAdapter:
    def invoke(self, config, context):
        return _parse_response(
            config.role,
            context,
            json.dumps({"output": "ok", "findings": [], "epistemic_review": neutral_epistemic_review()}),
        )


class DirectBypassAdapter:
    def invoke(self, config, context):
        # Simulates a future custom adapter that bypasses _parse_response.
        return ReviewerResponse(config.role, "h", "looks fine")


class MutatingAdapter:
    def invoke(self, config, context):
        # Simulate a faulty/custom adapter changing the exact context after the
        # orchestrator has already capability-bound it.
        context["artifact"]["content"] = "substituted artifact shown to provider"
        return _parse_response(
            config.role,
            context,
            json.dumps({"output": "ok", "findings": [], "epistemic_review": neutral_epistemic_review()}),
        )


class MutateUseRestoreAdapter:
    def __init__(self):
        self.observed = None

    def invoke(self, config, context):
        original = context["artifact"]["content"]
        context["artifact"]["content"] = "substituted artifact used by adapter"
        self.observed = context["artifact"]["content"]
        context["artifact"]["content"] = original
        return _parse_response(
            config.role,
            context,
            json.dumps({"output": "ok", "findings": [], "epistemic_review": neutral_epistemic_review()}),
        )


def cfg(role="R2"):
    return ReviewerConfig(
        role=role,
        provider="dummy",
        model="model-x",
        sku="default",
        deployment_path="api",
        api_key_env="DUMMY_API_KEY",
        foundation_lineage="lineage-x",
        qualification_ref="qual-x",
    )


class ProviderTests(unittest.TestCase):
    def test_platform_binds_artifact_hash_not_model_payload(self):
        context = {"artifact": {"artifact_hash": "trusted-hash"}}
        raw = json.dumps({
            "output": "review",
            "artifact_hash": "forged-model-hash",
            "epistemic_review": neutral_epistemic_review(),
            "findings": [{
                "finding_id": "f1",
                "severity": "HIGH",
                "material": True,
                "summary": "bad claim",
                "affected_scope": ["claim:1"],
            }],
        })
        result = _parse_response("R2", context, raw)
        self.assertEqual(result.artifact_hash, "trusted-hash")
        self.assertEqual(result.findings[0].reviewer_role, "R2")

    def test_non_json_output_fails_closed(self):
        with self.assertRaises(RuntimeError):
            _parse_response("R2", {"artifact": {"artifact_hash": "h"}}, "looks good")

    def test_missing_epistemic_review_is_rejected(self):
        raw = json.dumps({"output": "review", "findings": []})
        with self.assertRaisesRegex(ValueError, "epistemic_review object required"):
            _parse_response("R2", {"artifact": {"artifact_hash": "h"}}, raw)

    def test_missing_finding_summary_is_rejected(self):
        raw = json.dumps({
            "output": "review",
            "epistemic_review": neutral_epistemic_review(),
            "findings": [{"severity": "HIGH", "material": True}],
        })
        with self.assertRaises(ValueError):
            _parse_response("R2", {"artifact": {"artifact_hash": "h"}}, raw)

    def test_r3_adjudication_parses_exact_resolved_finding_ids(self):
        raw = json.dumps({
            "output": "resolved against evidence",
            "epistemic_review": neutral_epistemic_review(),
            "findings": [],
            "resolved_finding_ids": ["r3-a", "r3-b"],
        })
        result = _parse_response("R3", {"artifact_hash": "trusted-hash"}, raw)
        self.assertEqual(result.artifact_hash, "trusted-hash")
        self.assertEqual(result.resolved_finding_ids, ("r3-a", "r3-b"))

    def test_resolved_finding_ids_must_be_a_list(self):
        raw = json.dumps({
            "output": "bad closure shape",
            "epistemic_review": neutral_epistemic_review(),
            "findings": [],
            "resolved_finding_ids": "r3-a",
        })
        with self.assertRaisesRegex(RuntimeError, "resolved_finding_ids must be a list"):
            _parse_response("R3", {"artifact_hash": "h"}, raw)

    def test_duplicate_resolved_finding_ids_are_rejected(self):
        raw = json.dumps({
            "output": "duplicate closure",
            "epistemic_review": neutral_epistemic_review(),
            "findings": [],
            "resolved_finding_ids": ["r3-a", "r3-a"],
        })
        with self.assertRaisesRegex(ValueError, "cannot contain duplicates"):
            _parse_response("R3", {"artifact_hash": "h"}, raw)

    def test_registry_requires_explicit_provider_registration(self):
        registry = ProviderRegistry()
        with self.assertRaises(RuntimeError):
            registry.invoke(cfg(), {})
        registry.register("dummy", DummyAdapter())
        response = registry.invoke(cfg(), {"artifact": {"artifact_hash": "h"}})
        self.assertEqual(response.output, "ok")
        self.assertEqual(response.artifact_hash, "h")
        self.assertEqual(response.epistemic_review["version"], "TVC-1")

    def test_registry_rejects_custom_adapter_that_omits_epistemic_contract(self):
        registry = ProviderRegistry()
        registry.register("dummy", DirectBypassAdapter())
        with self.assertRaisesRegex(RuntimeError, "missing mandatory epistemic_review"):
            registry.invoke(cfg(), {"artifact": {"artifact_hash": "h"}})

    def test_registry_rejects_adapter_that_mutates_bound_context(self):
        registry = ProviderRegistry()
        registry.register("dummy", MutatingAdapter())
        context = {
            "artifact": {
                "artifact_hash": "trusted-hash",
                "content": "exact frozen artifact",
            }
        }
        with self.assertRaisesRegex(RuntimeError, "context.*changed|changed.*context"):
            registry.invoke(cfg(), context)

    def test_registry_prevents_mutate_use_restore_context_bypass(self):
        registry = ProviderRegistry()
        adapter = MutateUseRestoreAdapter()
        registry.register("dummy", adapter)
        context = {
            "artifact": {
                "artifact_hash": "trusted-hash",
                "content": "exact frozen artifact",
            }
        }
        with self.assertRaisesRegex(RuntimeError, "immutable|context.*changed|changed.*context"):
            registry.invoke(cfg(), context)
        self.assertNotEqual(adapter.observed, "substituted artifact used by adapter")

    def test_reviewer_config_uses_environment_name_not_raw_key_shape(self):
        bad = ReviewerConfig(
            role="R1", provider="p", model="m", sku="s", deployment_path="d",
            api_key_env="sk-live-secret-value!", foundation_lineage="l",
        )
        with self.assertRaises(ValueError):
            bad.validate()


if __name__ == "__main__":
    unittest.main()
