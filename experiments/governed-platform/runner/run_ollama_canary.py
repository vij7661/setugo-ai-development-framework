#!/usr/bin/env python3
"""Execute one prepared blinded envelope through a local Ollama mechanism.

This runner never reads protected ground truth. It writes raw/normalized evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapters import OllamaAdapter, normalize_adapter_result


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    configured_model = envelope.get("mechanism", {}).get("model")
    if configured_model and configured_model != args.model:
        raise ValueError(
            f"runtime model {args.model!r} does not match prepared envelope model {configured_model!r}"
        )

    adapter = OllamaAdapter(
        model=args.model,
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
    )
    result = adapter.invoke(envelope)
    normalized = normalize_adapter_result(envelope, result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0 if result.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
