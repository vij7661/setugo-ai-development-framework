#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PATHS = {
    "R1-R2-R1": ["R1", "R2", "R1"],
    "R1-R2-R1-R3": ["R1", "R2", "R1", "R3"],
    "R1-R2-R1-R3-R1": ["R1", "R2", "R1", "R3", "R1"],
}

ROLE_CONFIG = {
    "R1": {
        "provider": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "openai/gpt-oss-20b",
        "api_key_env": "GROQ_API_KEY",
    },
    "R2": {
        "provider": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-3.8-flash",
        "api_key_env": "GEMINI_API_KEY",
    },
    "R3": {
        "provider": "mistral",
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-small-latest",
        "api_key_env": "MISTRAL_API_KEY",
    },
}

RETRYABLE_HTTP = {429, 500, 502, 503, 504}


def nearest_rank(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def summarize(values: list[float]) -> dict[str, float | int | None]:
    return {
        "n": len(values),
        "p50_ms": nearest_rank(values, 0.50),
        "p95_ms": nearest_rank(values, 0.95),
        "max_ms": max(values) if values else None,
        "min_ms": min(values) if values else None,
    }


def invoke(role: str, case_payload: dict[str, Any], prior_output: str | None, timeout: int, max_tokens: int) -> dict[str, Any]:
    cfg = ROLE_CONFIG[role]
    api_key = os.environ.get(cfg["api_key_env"])
    if not api_key:
        raise RuntimeError(f"missing credential {cfg['api_key_env']}")
    user_payload = {
        "case": case_payload,
        "review_stage": role,
        "prior_stage_output": prior_output,
    }
    body = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": "Act as the assigned governed software-review stage. Review the supplied case and prior-stage output if present. Return a concise JSON object with keys: conclusion, material_findings, recommended_next_step. Do not claim release, deployment, or mutation authority."},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    endpoint = cfg["base_url"].rstrip("/") + "/chat/completions"
    started_ns = time.perf_counter_ns()
    attempts = 0
    last_error = None
    for attempt in range(1, 4):
        attempts = attempt
        req = Request(endpoint, data=json.dumps(body).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "setugo-exp-p-latency/1.0"}, method="POST")
        try:
            with urlopen(req, timeout=timeout) as response:
                parsed = json.loads(response.read().decode("utf-8"))
            choices = parsed.get("choices") or []
            first = choices[0] if choices else {}
            message = first.get("message") or {}
            text = message.get("content")
            finish_reason = first.get("finish_reason")
            if not isinstance(text, str) or not text.strip():
                raise RuntimeError("provider returned no usable completion")
            if finish_reason != "stop":
                raise RuntimeError(f"nonterminal finish_reason={finish_reason!r}")
            ended_ns = time.perf_counter_ns()
            usage = parsed.get("usage") or {}
            return {
                "role": role,
                "provider": cfg["provider"],
                "model": cfg["model"],
                "attempts": attempts,
                "duration_ms": (ended_ns - started_ns) / 1_000_000,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "output": text,
            }
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {detail[:500]}"
            if exc.code in RETRYABLE_HTTP and attempt < 3:
                time.sleep(min(2 ** attempt, 5))
                continue
            break
        except (URLError, TimeoutError) as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(min(2 ** attempt, 5))
                continue
            break
        except Exception as exc:
            last_error = str(exc)
            break
    ended_ns = time.perf_counter_ns()
    return {
        "role": role,
        "provider": cfg["provider"],
        "model": cfg["model"],
        "attempts": attempts,
        "duration_ms": (ended_ns - started_ns) / 1_000_000,
        "error": last_error or "unknown provider failure",
    }


def run_path(path_name: str, case_payload: dict[str, Any], timeout: int, max_tokens: int) -> dict[str, Any]:
    stages = PATHS[path_name]
    path_started = time.perf_counter_ns()
    prior = None
    records = []
    for position, role in enumerate(stages, start=1):
        result = invoke(role, case_payload, prior, timeout, max_tokens)
        result["position"] = position
        records.append(result)
        if "error" in result:
            break
        prior = result["output"]
    path_ended = time.perf_counter_ns()
    complete = len(records) == len(stages) and all("error" not in r for r in records)
    recovered_retry = complete and any(r["attempts"] > 1 for r in records)
    classification = "failed_path" if not complete else ("recovered_retry" if recovered_retry else "healthy_first_attempt")
    return {
        "path": path_name,
        "classification": classification,
        "complete": complete,
        "duration_ms": (path_ended - path_started) / 1_000_000,
        "stages": records,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=Path, required=True)
    ap.add_argument("--iterations", type=int, default=10)
    ap.add_argument("--timeout-seconds", type=int, default=120)
    ap.add_argument("--max-tokens", type=int, default=600)
    ap.add_argument("--execution-sha", required=True)
    ap.add_argument("--workflow-run-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.iterations != 10:
        raise SystemExit("EXP-P Pilot 1 first scientific run is frozen at exactly 10 iterations per path")
    case_payload = json.loads(args.case.read_text(encoding="utf-8"))
    observations = []
    for path_name in PATHS:
        for iteration in range(1, args.iterations + 1):
            row = run_path(path_name, case_payload, args.timeout_seconds, args.max_tokens)
            row["iteration"] = iteration
            observations.append(row)
            print(json.dumps({"path": path_name, "iteration": iteration, "classification": row["classification"], "duration_ms": round(row["duration_ms"], 1)}, sort_keys=True), flush=True)

    summary = {}
    for path_name in PATHS:
        subset = [x for x in observations if x["path"] == path_name]
        healthy = [x["duration_ms"] for x in subset if x["classification"] == "healthy_first_attempt"]
        retry = [x["duration_ms"] for x in subset if x["classification"] == "recovered_retry"]
        failed = [x["duration_ms"] for x in subset if x["classification"] == "failed_path"]
        stage_stats = {}
        for pos, role in enumerate(PATHS[path_name], start=1):
            vals = [s["duration_ms"] for x in subset if x["classification"] == "healthy_first_attempt" for s in x["stages"] if s["position"] == pos]
            stage_stats[f"{pos}:{role}"] = summarize(vals)
        summary[path_name] = {
            "attempted": len(subset),
            "healthy_first_attempt": len(healthy),
            "recovered_retry": len(retry),
            "failed_path": len(failed),
            "healthy_latency": summarize(healthy),
            "recovered_retry_latency": summarize(retry),
            "failed_path_elapsed": summarize(failed),
            "healthy_stage_latency": stage_stats,
        }

    payload = {
        "experiment": "EXP-P",
        "pilot": 1,
        "title": "Governed sequential review latency",
        "execution_sha": args.execution_sha,
        "workflow_run_id": args.workflow_run_id,
        "case": args.case.stem,
        "iterations_per_path": args.iterations,
        "max_tokens": args.max_tokens,
        "temperature": 0.0,
        "role_mapping": ROLE_CONFIG,
        "percentile_method": "nearest-rank",
        "summary": summary,
        "observations": observations,
        "bounded_claim": "Latency measurement only for this mapping/workload/window; no SLA or production authorization.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
