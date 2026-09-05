import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import provider_router
from adapters import AdapterResult


def structured_output(summary="fallback ok"):
    return json.dumps({"summary": summary, "findings": [], "diagnosis": None, "authorized_scope": [], "changed_artifacts": [], "evidence_refs": []})


class FakeAdapter:
    calls = []
    def __init__(self, config): self.config = config
    def invoke(self, envelope):
        self.calls.append(self.config.provider_id)
        if self.config.provider_id == "mistral": raise RuntimeError("provider HTTP 429 exhausted (attempt 3/3)")
        return AdapterResult("PASS", structured_output(), self.config.provider_id, self.config.model, 1, 2, 0.0, 3, True, {"provider_attempts": 1})


class UnstructuredThenSuccessAdapter:
    calls = []
    def __init__(self, config): self.config = config
    def invoke(self, envelope):
        self.calls.append(self.config.provider_id)
        raw = "plain prose completion" if self.config.provider_id == "openrouter" else structured_output("qualified fallback")
        return AdapterResult("PASS", raw, self.config.provider_id, self.config.model, 1, 2, 0.0, 3, True, {"provider_attempts": 1})


class RevokingAdapter:
    qualification_path = None
    def __init__(self, config): self.config = config
    def invoke(self, envelope):
        data = json.loads(Path(self.qualification_path).read_text())
        data["qualifications"][0]["status"] = "REVOKED"
        Path(self.qualification_path).write_text(json.dumps(data))
        return AdapterResult("PASS", structured_output(), self.config.provider_id, self.config.model, 1, 2, 0.0, 3, True, {"provider_attempts": 1})


class RouterTest(unittest.TestCase):
    def _files(self, root):
        case = root / "EXP-C-001.json"; registry = root / "m.json"; qualifications = root / "q.json"; attestations = root / "a.json"; out = root / "o.json"; evidence = root / "ev.json"
        case.write_text(json.dumps({"case_id": "EXP-C-001", "experiment_id": "EXP-C", "version": 1, "risk": "HIGH", "artifact_ref": "fixture", "model_visible": {"task": "x"}}))
        return case, registry, qualifications, attestations, out, evidence

    @staticmethod
    def _mechanisms(items):
        return {"mechanisms": [{
            "mechanism_id": mid, "enabled": True, "kind": "reasoning-model", "adapter": "openai-compatible", "provider": provider,
            "base_url": "https://" + provider + ".example/v1", "model": provider + "-model", "sku": provider + "-sku",
            "deployment_path": "api/" + provider + "/prod", "role": "JUDGE", "task_class": "GOVERNANCE_REVIEW",
            "privacy_class": "external-approved", "policy_hash": "policy-v1", "qualification_id": "qual-" + provider,
            "qualification_epoch": 1, "api_key_env": provider.upper() + "_API_KEY",
        } for mid, provider in items]}

    @staticmethod
    def _qualifications(mechanisms, *, unqualified=()):
        rows = []
        for m in mechanisms["mechanisms"]:
            rows.append({
                "mechanism_id": m["mechanism_id"], "provider": m["provider"], "model": m["model"], "sku": m["sku"],
                "deployment_path": m["deployment_path"], "role": m["role"], "task_class": m["task_class"],
                "privacy_class": m["privacy_class"], "policy_hash": m["policy_hash"], "qualification_id": m["qualification_id"],
                "qualification_epoch": m["qualification_epoch"], "status": "UNQUALIFIED" if m["mechanism_id"] in unqualified else "QUALIFIED",
            })
        return {"qualifications": rows}

    @staticmethod
    def _attestations(mechanisms, *, omit=(), self_attest=()):
        rows = []
        for m in mechanisms["mechanisms"]:
            if m["mechanism_id"] in omit: continue
            rows.append({
                "mechanism_id": m["mechanism_id"], "provider": m["provider"], "model": m["model"], "sku": m["sku"],
                "deployment_path": m["deployment_path"], "qualification_id": m["qualification_id"], "qualification_epoch": m["qualification_epoch"],
                "attestation_ref": "attest-" + m["mechanism_id"], "verified_by": m["provider"] if m["mechanism_id"] in self_attest else "control-plane-verifier",
                "status": "VERIFIED",
            })
        return {"identity_attestations": rows}

    def _argv(self, case, registry, qualifications, attestations, out, evidence, version, order="m1,m2,m3"):
        return ["provider_router.py", "--case", str(case), "--mechanisms", str(registry), "--qualifications", str(qualifications), "--identity-attestations", str(attestations), "--order", order, "--instruction-version", version, "--out", str(out), "--evidence-out", str(evidence)]

    def _write(self, registry, qualifications, attestations, mechanisms, *, unqualified=(), omit_attestation=(), self_attest=()):
        registry.write_text(json.dumps(mechanisms)); qualifications.write_text(json.dumps(self._qualifications(mechanisms, unqualified=unqualified))); attestations.write_text(json.dumps(self._attestations(mechanisms, omit=omit_attestation, self_attest=self_attest)))

    def test_first_qualified_attested_success_stops_later_calls(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "mistral"), ("m2", "groq"), ("m3", "gemini")]); self._write(registry, qualifications, attestations, mechanisms)
            FakeAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", FakeAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v1")):
                self.assertEqual(provider_router.main(), 0)
            ev = json.loads(evidence.read_text())
            self.assertEqual(FakeAdapter.calls, ["mistral", "groq"])
            self.assertEqual(ev["selected_mechanism"], "m2")
            self.assertEqual(ev["routing_rule"], "QUALIFIED_ATTESTED_FIRST_SUCCESS")

    def test_unqualified_provider_is_denied_before_network(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq")]); self._write(registry, qualifications, attestations, mechanisms, unqualified={"m1"})
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v2", "m1,m2")):
                self.assertEqual(provider_router.main(), 0)
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["groq"])

    def test_missing_out_of_band_attestation_is_denied_before_network(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq")]); self._write(registry, qualifications, attestations, mechanisms, omit_attestation={"m1"})
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v3", "m1,m2")):
                self.assertEqual(provider_router.main(), 0)
            ev = json.loads(evidence.read_text())
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["groq"])
            self.assertIn("identity-denied", ev["attempts"][0]["reason"])

    def test_provider_self_attestation_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq")]); self._write(registry, qualifications, attestations, mechanisms, self_attest={"m1"})
            FakeAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", FakeAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v4", "m1,m2")):
                self.assertEqual(provider_router.main(), 0)
            self.assertEqual(FakeAdapter.calls, ["groq"])

    def test_response_model_label_is_not_identity_authority(self):
        class ForgedLabelAdapter(FakeAdapter):
            def invoke(self, envelope):
                self.calls.append(self.config.provider_id)
                return AdapterResult("PASS", structured_output(), self.config.provider_id, "forged-response-model-label", 1, 2, 0.0, 3, True, {"provider_attempts": 1})
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "groq")]); self._write(registry, qualifications, attestations, mechanisms)
            ForgedLabelAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", ForgedLabelAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v5", "m1")):
                self.assertEqual(provider_router.main(), 0)
            self.assertEqual(json.loads(evidence.read_text())["selected_mechanism"], "m1")

    def test_midflight_qualification_revocation_discards_result(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "groq")]); self._write(registry, qualifications, attestations, mechanisms)
            RevokingAdapter.qualification_path = qualifications
            with patch("provider_router.OpenAICompatibleAdapter", RevokingAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v6", "m1")):
                with self.assertRaisesRegex(RuntimeError, "portfolio exhausted"):
                    provider_router.main()
            ev = json.loads(evidence.read_text())
            self.assertIn("post-call qualification revalidation failed", ev["attempts"][0]["reason"])

    def test_unstructured_completion_fails_and_next_attested_provider_runs(self):
        with tempfile.TemporaryDirectory() as td:
            case, registry, qualifications, attestations, out, evidence = self._files(Path(td))
            mechanisms = self._mechanisms([("m1", "openrouter"), ("m2", "groq")]); self._write(registry, qualifications, attestations, mechanisms)
            UnstructuredThenSuccessAdapter.calls = []
            with patch("provider_router.OpenAICompatibleAdapter", UnstructuredThenSuccessAdapter), patch("sys.argv", self._argv(case, registry, qualifications, attestations, out, evidence, "v7", "m1,m2")):
                self.assertEqual(provider_router.main(), 0)
            self.assertEqual(UnstructuredThenSuccessAdapter.calls, ["openrouter", "groq"])


if __name__ == "__main__": unittest.main()
