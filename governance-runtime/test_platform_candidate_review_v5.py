from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import platform_candidate_review_v5 as v5

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


class FakeResponse:
    def __init__(self, body):
        self.body = body
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return json.dumps(self.body).encode("utf-8")


def main():
    passed = 0
    original = v5.urlopen
    try:
        # V5-01 provider error is classified before model mismatch.
        v5.urlopen = lambda *a, **k: FakeResponse({"error": {"code": 429, "type": "rate_limit", "message": "capacity"}})
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "raw.json"
            try:
                v5._invoke_openrouter("dummy", MODEL, "prompt", raw)
                raise AssertionError("provider error accepted")
            except RuntimeError as exc:
                assert "provider error" in str(exc)
                assert "rate_limit" in str(exc)
                assert raw.exists()
                assert json.loads(raw.read_text())["error"]["code"] == 429
        passed += 1

        # V5-02 exact model match succeeds and raw body is persisted.
        review = {"x": 1}
        body = {"model": MODEL, "provider": "Nvidia", "choices": [{"message": {"content": json.dumps(review)}}]}
        v5.urlopen = lambda *a, **k: FakeResponse(body)
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "raw.json"
            got_body, got_review = v5._invoke_openrouter("dummy", MODEL, "prompt", raw)
            assert got_body["model"] == MODEL
            assert got_review == review
            assert json.loads(raw.read_text())["provider"] == "Nvidia"
        passed += 1

        # V5-03 real model substitution still fails closed.
        v5.urlopen = lambda *a, **k: FakeResponse({"model": "different/model", "choices": [{"message": {"content": json.dumps(review)}}]})
        try:
            v5._invoke_openrouter("dummy", MODEL, "prompt")
            raise AssertionError("model substitution accepted")
        except RuntimeError as exc:
            assert "model mismatch" in str(exc)
        passed += 1

        # V5-04 missing model without provider error remains model mismatch.
        v5.urlopen = lambda *a, **k: FakeResponse({"choices": [{"message": {"content": json.dumps(review)}}]})
        try:
            v5._invoke_openrouter("dummy", MODEL, "prompt")
            raise AssertionError("missing model accepted")
        except RuntimeError as exc:
            assert "returned=None" in str(exc)
        passed += 1

        # V5-05 non-OpenRouter providers delegate unchanged.
        assert v5.required_secret_name("gemini") == "GEMINI_API_KEY"
        assert v5.required_secret_name("groq") == "GROQ_API_KEY"
        passed += 1
    finally:
        v5.urlopen = original

    print(f"V5 observability tests: {passed}/5 PASS")


if __name__ == "__main__":
    main()
