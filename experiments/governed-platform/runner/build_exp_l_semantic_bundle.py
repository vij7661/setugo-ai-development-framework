#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from math import log
from pathlib import Path


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalized_entropy(labels: list[str]) -> float:
    if len(labels) <= 1:
        return 0.0
    counts = Counter(labels)
    if len(counts) <= 1:
        return 0.0
    total = len(labels)
    probs = [count / total for count in counts.values()]
    entropy = -sum(p * log(p) for p in probs)
    return entropy / log(len(counts))


def _sample_label(result: dict) -> str | None:
    if result.get("status") != "PASS" or not result.get("evidence_eligible"):
        return None
    diagnosis = result.get("diagnosis") or {}
    primary = diagnosis.get("primary_failure_class")
    return primary if isinstance(primary, str) and primary else "NO_PRIMARY_CLASS"


def build_bundle(case_id: str, result_paths: list[Path], execution_sha: str, workflow_run_id: int) -> dict:
    samples = []
    by_provider: dict[str, list[dict]] = {}
    for path in sorted(result_paths):
        result = _read(path)
        provider = result.get("provider") or "unknown"
        label = _sample_label(result)
        sample = {
            "source_file": path.name,
            "provider": provider,
            "model": result.get("mechanism_version"),
            "status": result.get("status"),
            "evidence_eligible": bool(result.get("evidence_eligible")),
            "semantic_proxy_label": label,
            "input_tokens": result.get("input_tokens"),
            "output_tokens": result.get("output_tokens"),
            "latency_ms": result.get("latency_ms"),
            "sampling_temperature": (result.get("runtime_metadata") or {}).get("sampling_temperature"),
            "result_sha256": _sha256(result),
        }
        samples.append(sample)
        by_provider.setdefault(provider, []).append(sample)

    providers = []
    for provider, provider_samples in sorted(by_provider.items()):
        labels = [s["semantic_proxy_label"] for s in provider_samples if s["semantic_proxy_label"] is not None]
        counts = Counter(labels)
        providers.append({
            "provider": provider,
            "sample_count": len(provider_samples),
            "valid_model_sample_count": len(labels),
            "error_or_ineligible_count": len(provider_samples) - len(labels),
            "semantic_proxy": "canonical primary_failure_class for diagnosis cases; not a general semantic-equivalence model",
            "cluster_counts": dict(sorted(counts.items())),
            "normalized_semantic_entropy": _normalized_entropy(labels),
            "stable_single_cluster": len(labels) > 0 and len(counts) == 1,
            "total_input_tokens": sum((s["input_tokens"] or 0) for s in provider_samples),
            "total_output_tokens": sum((s["output_tokens"] or 0) for s in provider_samples),
            "total_latency_ms": sum((s["latency_ms"] or 0) for s in provider_samples),
        })

    bundle = {
        "schema_version": "1.0",
        "experiment": "EXP-L",
        "pilot_stage": "SEMANTIC_CALIBRATION_COLLECTION",
        "case_id": case_id,
        "execution_sha": execution_sha,
        "workflow_run_id": int(workflow_run_id),
        "scientific_status": "COLLECTION_ONLY_NOT_ADJUDICATED",
        "authority": "NONE",
        "threshold_applied": False,
        "note": "This stage measures observed within-model classification stability without applying an invented production threshold. Protected adjudication occurs later.",
        "providers": providers,
        "samples": samples,
    }
    bundle["bundle_sha256"] = _sha256({k: v for k, v in bundle.items() if k != "bundle_sha256"})
    return bundle


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--case-id", required=True)
    p.add_argument("--result", action="append", default=[])
    p.add_argument("--execution-sha", required=True)
    p.add_argument("--workflow-run-id", required=True, type=int)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    if not args.result:
        raise SystemExit("at least one --result is required")
    bundle = build_bundle(args.case_id, [Path(x) for x in args.result], args.execution_sha, args.workflow_run_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
