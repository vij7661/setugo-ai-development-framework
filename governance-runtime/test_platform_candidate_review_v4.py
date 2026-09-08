from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import platform_candidate_review_v4 as v4

OPENROUTER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


def req(provider="openrouter", model=OPENROUTER_MODEL, blind=True):
    return {
        "review_request_id": "REV-TEST-ORR",
        "artifact": {"commit": "a" * 40},
        "required_reviewer": {"provider": provider, "model": model},
        "blind_review_required": blind,
        "required_review_dimensions": [{"id": "d1", "mandatory": True}],
    }


def review_for(r, provider="openrouter", model=OPENROUTER_MODEL):
    return {
        "review_request_id": r["review_request_id"],
        "reviewed_artifact_commit": r["artifact"]["commit"],
        "reviewer": {"provider": provider, "model": model},
        "disposition": "PASS",
        "findings": [],
        "evidence_assessment": "supported",
        "independence_attestation": v4.legacy.expected_attestation(r),
        "review_coverage": [{"dimension_id": "d1", "status": "TESTED_SUPPORTED", "evidence": ["e1"], "assessment": "ok"}],
    }


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

    # ORR-01
    assert "openrouter" in v4.SUPPORTED_PROVIDERS
    passed += 1

    # ORR-02
    assert v4.required_secret_name("openrouter") == "OPENROUTER_API_KEY"
    passed += 1

    # ORR-03
    v4.verify_provider_binding(req(), "openrouter", OPENROUTER_MODEL)
    passed += 1

    # ORR-04
    try:
        v4.verify_provider_binding(req(provider="gemini", model="gemini-3.6-flash"), "openrouter", OPENROUTER_MODEL)
        raise AssertionError("provider substitution accepted")
    except ValueError:
        pass
    passed += 1

    # ORR-05
    try:
        v4.verify_provider_binding(req(), "openrouter", "openrouter/free")
        raise AssertionError("wrong exact model accepted")
    except ValueError:
        pass
    passed += 1

    # ORR-06: returned OpenRouter model mismatch fails closed.
    original = v4.urlopen
    try:
        v4.urlopen = lambda *a, **k: FakeResponse({
            "model": "different/model",
            "provider": "SomeProvider",
            "choices": [{"message": {"content": json.dumps(review_for(req()))}}],
        })
        try:
            v4._invoke_openrouter("dummy", OPENROUTER_MODEL, "prompt")
            raise AssertionError("returned model mismatch accepted")
        except RuntimeError as exc:
            assert "returned model mismatch" in str(exc)
    finally:
        v4.urlopen = original
    passed += 1

    # ORR-07: upstream provider metadata is captured in deterministic envelope.
    corpus = {"corpus_sha256": "sha256:" + "b" * 64, "evidence_ref_count": 2, "materialized_evidence_count": 2}
    env = v4.execution_envelope(req(), corpus, "openrouter", OPENROUTER_MODEL, {
        "model": OPENROUTER_MODEL, "provider": "Nvidia", "usage": {"prompt_tokens": 123}
    })
    assert env["remote_returned_model"] == OPENROUTER_MODEL
    assert env["openrouter_upstream_provider"] == "Nvidia"
    assert env["provider_usage"]["prompt_tokens"] == 123
    passed += 1

    # ORR-08: R2 attestation remains blind.
    r2 = req(blind=True)
    p2 = v4.build_prompt(r2, {"x": 1}, "openrouter", OPENROUTER_MODEL)
    assert "independent adversarial R2 reviewer" in p2
    assert "BLIND_TO_PROPOSER_CONCLUSION" in p2
    passed += 1

    # ORR-09: R3 attestation remains explicit review-of-review.
    r3 = req(blind=False)
    p3 = v4.build_prompt(r3, {"x": 1}, "openrouter", OPENROUTER_MODEL)
    assert "R3 adversarial review-of-review critic" in p3
    assert "REVIEW_OF_REVIEW_EXPOSED_TO_PRIOR_REVIEW" in p3
    passed += 1

    # ORR-10: semantic validator remains strict and provider-independent.
    assert v4.validate(review_for(req()), req(), "openrouter", OPENROUTER_MODEL)["valid"] is True
    bad = review_for(req())
    bad["reviewer"]["model"] = "wrong/model"
    assert v4.validate(bad, req(), "openrouter", OPENROUTER_MODEL)["valid"] is False
    passed += 1

    print(f"ORR deterministic tests: {passed}/10 PASS")


if __name__ == "__main__":
    main()
