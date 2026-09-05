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
        qualifications = root / "q.json"
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
        return case, registry, qualifications, out, evidence

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
                    "sku": provider + "-sku",
                    "deployment_path": "api/" + provider + "/prod",
                    "role": "JUDGE",
                    "task_class": "GOVERNANCE_REVIEW",
                    "privacy_class": "external-approved",
                    "policy_hash": "policy-v1",
                    "qualification_id": "qual-" + provider,
                    "qualification_epoch": 1,
                    "api_key_env": provider.upper() + "_API_KEY",
                }
            )
        return {"mechanisms": mechanisms}

    @staticmethod
    def _qualifications(mechanisms, *, unqualified=()):
        rows = []
        for m in mechanisms["mechanisms"]:
            rows.append(
                {
                    "mechanism_id": m["mechanism_id"],
                    "provider": m["provider"],
                    "model": m["model"],
                    "sku": m["sku"],
                    "deployment_path": m["deployment_path"],
                    "role": m["role"],
                    "task_class": m["task_class"],
                    "privacy_class": m["privacy_class"],
                    "policy_hash": m["policy_hash"],
                    "qualification_id": m["qualification_id"],
                    "qualification_epoch": m["qualification_epoch"],
                    "status": "UNQUALIFIED" if m["mechanism_id"] in unqualified else "QUALIFIED",
                }
            )
        return {"qualifications": rows}

    def _argv(self, case, registry, qualifications, out, evidence, version, order="m1,m2,m3"):
        return [
            "provider_router.py",
            "--case",
            str(case),
            "--mechanisms",
            str(registry),
            "--qualifications",
            str(qualifications),
            "--order",
            order,
            "--instruction-version",
            version,
            "--out",
            str(out),
            "--evidence-out",
            str(evidence),
        ]

    def test_first_qualified_success_stops_later_calls_and_publishes_trail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, qualifications, out, evidence = self._files(root)
            mechanisms = self._mechanisms([("m1", "mistral"), ("m2", "groq"), ("m3", "gemini")])
            registry.write_text(json.dumps(mechanisms))
            qualifications.write_text(json.dumps(self._qualifications(mechanisms)))
            FakeAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", FakeAdapter), patch(
                "sys.argv", self._argv(case, registry, qualifications, out, evidence, "router-test-v1")
            ):
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

    def test_unstructured_completion_is_failed_and_router_uses_next_qualified_provider(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, qualifications, out, evidence = self._files(root)
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq"), ("m3", "gemini")])
            registry.write_text(json.dumps(mechanisms))
            qualifications.write_text(json.dumps(self._qualifications(mechanisms)))
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch(
                "sys.argv", self._argv(case, registry, qualifications, out, evidence, "router-test-v2")
            ):
                self.assertEqual(provider_router.main(), 0)

            ev = json.loads(evidence.read_text())
            result = json.loads(out.read_text())
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["openrouter", "groq"])
            self.assertEqual([x["status"] for x in ev["attempts"]], ["FAILED", "SUCCESS", "NOT_CALLED"])
            self.assertIn("normalized evidence validation", ev["attempts"][0]["reason"])
            self.assertEqual(ev["selected_mechanism"], "m2")
            self.assertEqual(result["provider"], "groq")
            self.assertTrue(result["evidence_eligible"])

    def test_unqualified_provider_is_denied_before_network_and_next_qualified_provider_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, qualifications, out, evidence = self._files(root)
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq"), ("m3", "gemini")])
            registry.write_text(json.dumps(mechanisms))
            qualifications.write_text(json.dumps(self._qualifications(mechanisms, unqualified={"m1"})))
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch(
                "sys.argv", self._argv(case, registry, qualifications, out, evidence, "router-test-v3")
            ):
                self.assertEqual(provider_router.main(), 0)

            ev = json.loads(evidence.read_text())
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["groq"])
            self.assertEqual([x["status"] for x in ev["attempts"]], ["NOT_CALLED", "SUCCESS", "NOT_CALLED"])
            self.assertIn("qualification-denied", ev["attempts"][0]["reason"])
            self.assertEqual(ev["selected_mechanism"], "m2")

    def test_qualification_scope_mismatch_is_denied_before_network(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case, registry, qualifications, out, evidence = self._files(root)
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq")])
            registry.write_text(json.dumps(mechanisms))
            quals = self._qualifications(mechanisms)
            quals["qualifications"][0]["deployment_path"] = "api/openrouter/other"
            qualifications.write_text(json.dumps(quals))
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch(
                "sys.argv", self._argv(case, registry, qualifications, out, evidence, "router-test-v4", "m1,m2")
            ):
                self.assertEqual(provider_router.main(), 0)

            ev = json.loads(evidence.read_text())
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["groq"])
            self.assertIn("qualification-deployment_path-mismatch", ev["attempts"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
