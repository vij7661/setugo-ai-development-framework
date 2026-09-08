from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
TOKEN_CLASS = 60000
MARKER = "OPENROUTER_CAPACITY_PROBE_OK"
URL = "https://openrouter.ai/api/v1/chat/completions"


def main() -> int:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY repository secret required")

    # Intentionally repetitive but deterministic. The scientific endpoint is whether
    # one large request is accepted; it must never be reduced to manufacture a pass.
    payload_text = " ".join(f"evidence{i % 97}" for i in range(TOKEN_CLASS))
    prompt = (
        "Capacity probe only. Read the entire following evidence payload. "
        f"Reply with exactly {MARKER} and nothing else if the request is accepted.\n"
        "BEGIN_EVIDENCE\n" + payload_text + "\nEND_EVIDENCE"
    )
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 32,
    }
    req = Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vij7661/setugo-ai-development-framework",
            "X-Title": "Setugo Governed Review Capacity Probe",
            "User-Agent": "setugo-openrouter-capacity-probe/1.0",
        },
        method="POST",
    )

    out = Path("openrouter-capacity-probe")
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    result = {
        "schema_version": 1,
        "probe_id": "GOV-OPENROUTER-CAPACITY-PROBE-001",
        "provider": "openrouter",
        "requested_model": MODEL,
        "synthetic_whitespace_token_class": TOKEN_CLASS,
        "marker": MARKER,
        "authority_effect": "NONE_PROVIDER_CAPACITY_EVIDENCE_ONLY",
    }

    try:
        with urlopen(req, timeout=300) as response:
            raw = response.read().decode("utf-8")
            http_status = response.status
        parsed = json.loads(raw)
        choices = parsed.get("choices") or []
        content = (((choices[0] if choices else {}).get("message") or {}).get("content"))
        success = isinstance(content, str) and MARKER in content
        result.update({
            "status": "PASS" if success else "FAIL",
            "http_status": http_status,
            "returned_model": parsed.get("model"),
            "provider_field": parsed.get("provider"),
            "usage": parsed.get("usage"),
            "latency_seconds": round(time.time() - started, 3),
            "response_content": content,
            "response_id": parsed.get("id"),
        })
        Path(out / "provider-response.json").write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        result.update({
            "status": "FAIL",
            "http_status": exc.code,
            "latency_seconds": round(time.time() - started, 3),
            "failure_detail": detail[:8000],
        })
    except URLError as exc:
        result.update({
            "status": "FAIL",
            "http_status": None,
            "latency_seconds": round(time.time() - started, 3),
            "failure_detail": str(exc.reason),
        })
    except Exception as exc:
        result.update({
            "status": "FAIL",
            "http_status": None,
            "latency_seconds": round(time.time() - started, 3),
            "failure_detail": f"{type(exc).__name__}: {exc}",
        })

    Path(out / "capacity-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
