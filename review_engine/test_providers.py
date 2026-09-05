from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from review_engine.models import ReviewerConfig
from review_engine.providers import ProviderRegistry, _parse_response


class DummyAdapter:
    def invoke(self, config, context):
        return _parse_response(config.role, context, json.dumps({"output": "ok", "findings": []}))


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

    def test_missing_finding_summary_is_rejected(self):
        raw = json.dumps({"output": "review", "findings": [{"severity": "HIGH", "material": True}]})
        with self.assertRaises(ValueError):
            _parse_response("R2", {"artifact": {"artifact_hash": "h"}}, raw)

    def test_registry_requires_explicit_provider_registration(self):
        registry = ProviderRegistry()
        with self.assertRaises(RuntimeError):
            registry.invoke(cfg(), {})
        registry.register("dummy", DummyAdapter())
        response = registry.invoke(cfg(), {"artifact": {"artifact_hash": "h"}})
        self.assertEqual(response.output, "ok")
        self.assertEqual(response.artifact_hash, "h")

    def test_reviewer_config_uses_environment_name_not_raw_key_shape(self):
        bad = ReviewerConfig(
            role="R1", provider="p", model="m", sku="s", deployment_path="d",
            api_key_env="sk-live-secret-value!", foundation_lineage="l",
        )
        with self.assertRaises(ValueError):
            bad.validate()


if __name__ == "__main__":
    unittest.main()
