from __future__ import annotations

import json

import platform_candidate_review_v7 as v7


MODEL = "nvidia/nemotron-3-ultra-550b-a55b"


def request(slot="R3", serving="deepinfra", fallbacks=False):
    return {
        "required_reviewer": {"provider": "openrouter", "model": MODEL},
        "reviewer_slot": slot,
        "review_execution_policy": {
            "serving_provider": serving,
            "allow_fallbacks": fallbacks,
            "reasoning_max_tokens": 4096,
            "max_output_tokens": 16384,
            "response_format": "json_object",
        },
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


def assert_raises(exc_type, fn, contains):
    try:
        fn()
    except exc_type as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError(f"expected {exc_type.__name__}: {contains}")


def test_all_slots_use_same_route_contract():
    for slot in ("R1", "R2", "R3"):
        policy = v7.verify_route_binding(request(slot=slot), "openrouter", MODEL)
        assert policy["serving_provider"] == "deepinfra"
        assert policy["allow_fallbacks"] is False


def test_fallbacks_fail_closed():
    assert_raises(
        ValueError,
        lambda: v7.verify_route_binding(request(fallbacks=True), "openrouter", MODEL),
        "allow_fallbacks=false",
    )


def test_openrouter_payload_is_pinned_and_bounded():
    captured = {}
    original = v7.urlopen

    def fake_urlopen(req, timeout=0):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse({
            "model": MODEL,
            "provider": "DeepInfra",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps({"ok": True})},
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
        })

    v7.urlopen = fake_urlopen
    try:
        body, review = v7._invoke_openrouter_pinned("secret", MODEL, "prompt", request()["review_execution_policy"])
    finally:
        v7.urlopen = original

    payload = captured["payload"]
    assert payload["provider"] == {
        "order": ["deepinfra"],
        "only": ["deepinfra"],
        "allow_fallbacks": False,
        "require_parameters": True,
    }
    assert payload["reasoning"] == {"max_tokens": 4096}
    assert payload["max_tokens"] == 16384
    assert payload["response_format"] == {"type": "json_object"}
    assert body["provider"] == "DeepInfra"
    assert review == {"ok": True}


def test_returned_provider_mismatch_fails_closed():
    original = v7.urlopen

    def fake_urlopen(req, timeout=0):
        return FakeResponse({
            "model": MODEL,
            "provider": "Baseten",
            "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"ok": True})}}],
        })

    v7.urlopen = fake_urlopen
    try:
        assert_raises(
            RuntimeError,
            lambda: v7._invoke_openrouter_pinned("secret", MODEL, "prompt", request()["review_execution_policy"]),
            "serving provider mismatch",
        )
    finally:
        v7.urlopen = original


def test_length_without_final_answer_fails_closed():
    original = v7.urlopen

    def fake_urlopen(req, timeout=0):
        return FakeResponse({
            "model": MODEL,
            "provider": "DeepInfra",
            "choices": [{"finish_reason": "length", "message": {"content": None, "reasoning": "exhausted"}}],
        })

    v7.urlopen = fake_urlopen
    try:
        assert_raises(
            RuntimeError,
            lambda: v7._invoke_openrouter_pinned("secret", MODEL, "prompt", request()["review_execution_policy"]),
            "exhausted token budget",
        )
    finally:
        v7.urlopen = original


def main():
    tests = [
        test_all_slots_use_same_route_contract,
        test_fallbacks_fail_closed,
        test_openrouter_payload_is_pinned_and_bounded,
        test_returned_provider_mismatch_fails_closed,
        test_length_without_final_answer_fails_closed,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)}/{len(tests)} serving-provider pinning tests")


if __name__ == "__main__":
    main()
