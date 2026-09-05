from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from review_engine.configuration import build_provider_registry, build_qualification_registry, load_configuration


class ConfigurationTests(unittest.TestCase):
    def _write(self, data):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with tmp: json.dump(data, tmp)
        return Path(tmp.name)

    def test_user_can_choose_distinct_models_and_secret_env_names(self):
        path = self._write({
            "providers": {
                "p1": {"adapter": "openai_compatible", "base_url": "https://p1.example/v1"},
                "p2": {"adapter": "openai_compatible", "base_url": "https://p2.example/v1"},
            },
            "reviewers": {
                "R1": {"provider": "p1", "model": "model-a", "api_key_env": "KEY_A", "foundation_lineage": "a"},
                "R2": {"provider": "p2", "model": "model-b", "api_key_env": "KEY_B", "foundation_lineage": "b"},
            },
        })
        config = load_configuration(path)
        self.assertEqual(config.reviewer("R1").model, "model-a")
        self.assertEqual(config.reviewer("R2").api_key_env, "KEY_B")
        self.assertIsNone(config.reviewer("R3"))
        self.assertEqual(config.assurance_mode, "EXPERIMENTAL_UNQUALIFIED")

    def test_native_anthropic_and_gemini_adapters_can_be_registered(self):
        path = self._write({
            "providers": {
                "a": {"adapter": "anthropic"},
                "g": {"adapter": "gemini"},
            },
            "reviewers": {
                "R1": {"provider": "a", "model": "claude-model", "api_key_env": "A_KEY", "foundation_lineage": "anthropic"},
                "R2": {"provider": "g", "model": "gemini-model", "api_key_env": "G_KEY", "foundation_lineage": "gemini"},
            },
        })
        config = load_configuration(path)
        registry = build_provider_registry(config)
        self.assertIsNotNone(registry)

    def test_retained_qualification_switches_assurance_to_governed(self):
        path = self._write({
            "providers": {"p": {"adapter": "openai_compatible", "base_url": "https://p.example/v1"}},
            "reviewers": {
                "R1": {"provider": "p", "model": "m", "api_key_env": "KEY", "foundation_lineage": "l", "qualification_ref": "q1"}
            },
            "qualifications": [{
                "qualification_ref": "q1", "provider": "p", "model": "m", "role": "R1",
                "foundation_lineage": "l", "status": "QUALIFIED", "qualification_epoch": 1,
                "max_risk": "LOW", "task_types": ["GENERAL"]
            }],
        })
        config = load_configuration(path)
        self.assertEqual(config.assurance_mode, "GOVERNED")
        self.assertIsNotNone(build_qualification_registry(config))

    def test_raw_api_key_field_is_rejected(self):
        path = self._write({
            "providers": {"p": {"adapter": "openai_compatible", "base_url": "https://p.example/v1", "api_key": "secret"}},
            "reviewers": {"R1": {"provider": "p", "model": "m", "api_key_env": "KEY", "foundation_lineage": "l"}},
        })
        with self.assertRaises(ValueError): load_configuration(path)

    def test_unknown_provider_is_rejected(self):
        path = self._write({"providers": {}, "reviewers": {"R1": {"provider": "missing", "model": "m", "api_key_env": "KEY", "foundation_lineage": "l"}}})
        with self.assertRaises(ValueError): load_configuration(path)

    def test_r1_is_required(self):
        path = self._write({"providers": {}, "reviewers": {}})
        with self.assertRaises(ValueError): load_configuration(path)


if __name__ == "__main__": unittest.main()
