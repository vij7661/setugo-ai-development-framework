import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import provider_router
from adapters import AdapterResult


def structured_output(summary="fallback ok"):
    return json.dumps(
        {
            "summary": summary,
            "findings": [],
            "diagnosis": None,
            "authorized_scope": [],
            "changed_artifacts": [],
            "evidence_refs": [],
        }
    )


class FakeAdapter:
    calls = []

    def __init__(self, config):
        self.config = config

    def invoke(self, envelope):
        self.calls.append((self.config.provider_id, envelope["mechanism"]["mechanism_id"], envelope["run_id"]))
        if self.config.provider_id == "mistral":
            raise RuntimeError("provider HTTP 429 exhausted (attempt 3/3)")
        return AdapterResult(
            status="PASS",
            raw_output=structured_output(),
            provider=self.config.provider_id,
            mechanism_version=self.config.model,
            input_tokens=1,
            output_tokens=2,
            estimated_cost_usd=0.0,
            latency_ms=3,
            evidence_eligible=True,
            runtime_metadata={"provider_attempts": 1},
        )


class UnstructuredThenSuccessAdapter:
    calls = []

    def __init__(self, config):
        self.config = config

    def invoke(self, envelope):
        self.calls.append(self.config.provider_id)
        raw = "plain prose completion" if self.config.provider_id == "openrouter" else structured_output("qualified fallback")
        return AdapterResult(
            status="PASS",
            raw_output=raw,
            provider=self.config.provider_id,
            mechanism_version=self.config.model,
            input_tokens=1,
            output_tokens=2,
            estimated_cost_usd=0.0,
            latency_ms=3,
            evidence_eligible=True,
            runtime_metadata={"provider_attempts": 1},
        )


class RouterTest(unittest.TestCase):
    def _files(self, root):
        case = root / "EXP-C-001.json"
        registry = root / "m.json"
        out = root / "o.json"
        evidence = root / "ev.json"
        case.write_text(
            json.dumps(
                {
                    "case_id": "EXP-C-001",
                    "experiment_id": "EXP-C",
                    "version": 1,
                    "risk": "HIGH",
                    "artifact_ref": "fixture",
                    "model_visible": {"task": "x"},
                }
            )
        )
        return case, registry, out, evidence

    @staticmethod
    def _mechanisms(items):
        mechanisms = []
        for mid, provider in items:
            mechanisms.append(
                {
                    "mechanism_id": mid,
                    "enabled": True,
                    "kind": "reasoning-model",
                    "adapter": "openai-compatible",
                    "provider": provider,
                    "base_url": "x",
                    "model": provider + "-model",
                    "api_key_env": provider.upper() + "_API_KEY",
                }
            )
        return {"mechanisms": mechanisms}

    def test_first_success_stops_later_calls_and_publishes_trail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, out, evidence = self._files(root)
            registry.write_text(json.dumps(self._mechanisms([("m1", "mistral"), ("m2", "groq"), ("m3", "gemini")])))
            FakeAdapter.calls = []
            argv = [
                "provider_router.py",
                "--case",
                str(case),
                "--mechanisms",
                str(registry),
                "--order",
                "m1,m2,m3",
                "--instruction-version",
                "router-test-v1",
                "--out",
                str(out),
                "--evidence-out",
                str(evidence),
            ]
            with patch("provider_router.OpenAICompatibleAdapter", FakeAdapter), patch("sys.argv", argv):
                self.assertEqual(provider_router.main(), 0)

            ev = json.loads(evidence.read_text())
            result = json.loads(out.read_text())
            self.assertEqual([c[0] for c in FakeAdapter.calls], ["mistral", "groq"])
            self.assertEqual(ev["selected_mechanism"], "m2")
            self.assertEqual([x["status"] for x in ev["attempts"]], ["FAILED", "SUCCESS", "NOT_CALLED"])
            self.assertEqual(ev["attempts"][0]["attempts"], 3)
            self.assertEqual(ev["attempts"][1]["attempts"], 1)
            self.assertEqual(ev["attempts"][2]["attempts"], 0)
            self.assertEqual(ev["routing_rule"], "QUALIFIED_FIRST_SUCCESS")
            self.assertEqual(ev["case_id"], "EXP-C-001")
            self.assertEqual(result["mechanism_id"], "m2")
            self.assertFalse(ev["portfolio_exhausted"])

    def test_unstructured_completion_is_failed_and_router_uses_next_provider(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, out, evidence = self._files(root)
            registry.write_text(json.dumps(self._mechanisms([("m1", "openrouter"), ("m2", "groq"), ("m3", "gemini")])))
            UnstructuredThenSuccessAdapter.calls = []
            argv = [
                "provider_router.py",
                "--case",
                str(case),
                "--mechanisms",
                str(registry),
                "--order",
                "m1,m2,m3",
                "--instruction-version",
                "router-test-v2",
                "--out",
                str(out),
                "--evidence-out",
                str(evidence),
            ]
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch("sys.argv", argv):
                self.assertEqual(provider_router.main(), 0)

            ev = json.loads(evidence.read_text())
            result = json.loads(out.read_text())
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["openrouter", "groq"])
            self.assertEqual([x["status"] for x in ev["attempts"]], ["FAILED", "SUCCESS", "NOT_CALLED"])
            self.assertIn("normalized evidence validation", ev["attempts"][0]["reason"])
            self.assertEqual(ev["selected_mechanism"], "m2")
            self.assertEqual(result["provider"], "groq")
            self.assertTrue(result["evidence_eligible"])


if __name__ == "__main__":
    unittest.main()
