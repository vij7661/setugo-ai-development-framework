from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from review_engine.configuration import build_provider_registry, build_qualification_registry, load_configuration


class ConfigurationTests(unittest.TestCase):
    def _write(self, data):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with tmp:
            json.dump(data, tmp)
        return Path(tmp.name)

    @staticmethod
    def _minimal(provider_extra=None, reviewer_extra=None, root_extra=None):
        provider = {"adapter": "openai_compatible", "base_url": "https://p.example/v1"}
        if provider_extra:
            provider.update(provider_extra)
        reviewer = {"provider": "p", "model": "m", "api_key_env": "KEY", "foundation_lineage": "l"}
        if reviewer_extra:
            reviewer.update(reviewer_extra)
        data = {"providers": {"p": provider}, "reviewers": {"R1": reviewer}}
        if root_extra:
            data.update(root_extra)
        return data

    @staticmethod
    def _qualified_config_data():
        return {
            "providers": {"p": {"adapter": "openai_compatible", "base_url": "https://p.example/v1"}},
            "reviewers": {
                "R1": {
                    "provider": "p",
                    "model": "m",
                    "api_key_env": "KEY",
                    "foundation_lineage": "l",
                    "qualification_ref": "q1",
                }
            },
            "qualifications": [{
                "qualification_ref": "q1",
                "provider": "p",
                "model": "m",
                "role": "R1",
                "foundation_lineage": "l",
                "status": "QUALIFIED",
                "qualification_epoch": 1,
                "max_risk": "LOW",
                "task_types": ["GENERAL"],
            }],
        }

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
        path = self._write(self._qualified_config_data())
        config = load_configuration(path)
        self.assertEqual(config.assurance_mode, "GOVERNED")
        self.assertIsNotNone(build_qualification_registry(config))

    def test_provider_endpoint_substitution_cannot_reuse_old_qualification(self):
        approved = self._qualified_config_data()
        approved_config = load_configuration(self._write(approved))
        self.assertEqual(approved_config.assurance_mode, "GOVERNED")

        substituted = copy.deepcopy(approved)
        substituted["providers"]["p"]["base_url"] = "https://different-provider.example/v1"
        substituted_config = load_configuration(self._write(substituted))

        with self.assertRaisesRegex(ValueError, "deployment|provider.*binding|fingerprint|qualification"):
            build_qualification_registry(substituted_config)

    def test_raw_api_key_field_is_rejected(self):
        path = self._write(self._minimal(provider_extra={"api_key": "secret"}))
        with self.assertRaises(ValueError):
            load_configuration(path)

    def test_common_credential_field_aliases_are_rejected_after_normalization(self):
        aliases = (
            "apiKey",
            "api-key",
            "access_token",
            "bearerToken",
            "client_secret",
            "authorization",
            "password",
            "credentials",
        )
        for alias in aliases:
            with self.subTest(alias=alias):
                path = self._write(self._minimal(provider_extra={alias: "raw-secret"}))
                with self.assertRaisesRegex(ValueError, "raw credential field forbidden"):
                    load_configuration(path)

    def test_custom_headers_cannot_smuggle_authorization_secret(self):
        path = self._write(self._minimal(provider_extra={"headers": {"Authorization": "Bearer raw-secret"}}))
        with self.assertRaisesRegex(ValueError, "raw credential field forbidden"):
            load_configuration(path)

    def test_unknown_provider_field_is_rejected_instead_of_silently_persisted(self):
        path = self._write(self._minimal(provider_extra={"metadata": "should-not-be-retained"}))
        with self.assertRaisesRegex(ValueError, "unsupported configuration field"):
            load_configuration(path)

    def test_unknown_reviewer_field_is_rejected_instead_of_silently_persisted(self):
        path = self._write(self._minimal(reviewer_extra={"metadata": "should-not-be-retained"}))
        with self.assertRaisesRegex(ValueError, "unsupported configuration field"):
            load_configuration(path)

    def test_unknown_root_field_is_rejected_instead_of_becoming_a_secret_bag(self):
        path = self._write(self._minimal(root_extra={"metadata": {"owner": "test"}}))
        with self.assertRaisesRegex(ValueError, "unsupported configuration field"):
            load_configuration(path)

    def test_unknown_qualification_field_is_rejected(self):
        data = self._minimal()
        data["qualifications"] = [{
            "qualification_ref": "q1",
            "provider": "p",
            "model": "m",
            "role": "R1",
            "foundation_lineage": "l",
            "status": "QUALIFIED",
            "qualification_epoch": 1,
            "max_risk": "LOW",
            "task_types": ["GENERAL"],
            "metadata": "ignored-before-hardening",
        }]
        path = self._write(data)
        with self.assertRaisesRegex(ValueError, "unsupported configuration field"):
            load_configuration(path)

    def test_api_key_env_reference_remains_allowed(self):
        path = self._write(self._minimal())
        config = load_configuration(path)
        self.assertEqual(config.reviewer("R1").api_key_env, "KEY")

    def test_unknown_provider_is_rejected(self):
        path = self._write({
            "providers": {},
            "reviewers": {"R1": {"provider": "missing", "model": "m", "api_key_env": "KEY", "foundation_lineage": "l"}},
        })
        with self.assertRaises(ValueError):
            load_configuration(path)

    def test_r1_is_required(self):
        path = self._write({"providers": {}, "reviewers": {}})
        with self.assertRaises(ValueError):
            load_configuration(path)


if __name__ == "__main__":
    unittest.main()
