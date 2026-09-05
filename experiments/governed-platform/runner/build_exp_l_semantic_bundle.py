#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from math import log
from pathlib import Path

MIN_VALID_SAMPLES_FOR_STABILITY = 3


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalized_entropy(labels: list[str]) -> float | None:
    if len(labels) < MIN_VALID_SAMPLES_FOR_STABILITY:
        return None
    counts = Counter(labels)
    if len(counts) <= 1:
        return 0.0
    total = len(labels)
    probs = [count / total for count in counts.values()]
    entropy = -sum(p * log(p) for p in probs)
    return entropy / log(len(counts))


def _sample_label(result: dict) -> str | None:
    """Return a deterministic task-specific semantic proxy for diagnosis cases.

    This is not a general semantic equivalence model. Prefer the explicit primary
    diagnosis. Otherwise use one unambiguous canonical finding class. A clean
    structured review with no diagnosis/findings is a distinct NO_MATERIAL_DEFECT
    conclusion rather than an uninformative placeholder.
    """
    if result.get("status") != "PASS" or not result.get("evidence_eligible"):
        return None

    diagnosis = result.get("diagnosis") or {}
    primary = diagnosis.get("primary_failure_class")
    if isinstance(primary, str) and primary:
        return primary

    finding_classes = {
        f.get("failure_class")
        for f in (result.get("findings") or [])
        if isinstance(f, dict) and isinstance(f.get("failure_class"), str) and f.get("failure_class")
    }
    if len(finding_classes) == 1:
        return next(iter(finding_classes))
    if len(finding_classes) > 1:
        return "MULTIPLE_MATERIAL_CLASSES"
    return "NO_MATERIAL_DEFECT"


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
        sufficient = len(labels) >= MIN_VALID_SAMPLES_FOR_STABILITY
        observed_single_cluster = bool(labels) and len(counts) == 1
        providers.append({
            "provider": provider,
            "sample_count": len(provider_samples),
            "valid_model_sample_count": len(labels),
            "error_or_ineligible_count": len(provider_samples) - len(labels),
            "minimum_valid_samples_for_stability": MIN_VALID_SAMPLES_FOR_STABILITY,
            "sample_sufficiency": "SUFFICIENT" if sufficient else "INSUFFICIENT",
            "semantic_proxy": "canonical diagnosis/finding class or NO_MATERIAL_DEFECT for diagnosis cases; not a general semantic-equivalence model",
            "cluster_counts": dict(sorted(counts.items())),
            "normalized_semantic_entropy": _normalized_entropy(labels),
            "observed_single_cluster": observed_single_cluster,
            "stable_single_cluster": sufficient and observed_single_cluster,
            "total_input_tokens": sum((s["input_tokens"] or 0) for s in provider_samples),
            "total_output_tokens": sum((s["output_tokens"] or 0) for s in provider_samples),
            "total_latency_ms": sum((s["latency_ms"] or 0) for s in provider_samples),
        })

    bundle = {
        "schema_version": "1.1",
        "experiment": "EXP-L",
        "pilot_stage": "SEMANTIC_CALIBRATION_COLLECTION",
        "case_id": case_id,
        "execution_sha": execution_sha,
        "workflow_run_id": int(workflow_run_id),
        "scientific_status": "COLLECTION_ONLY_NOT_ADJUDICATED",
        "authority": "NONE",
        "threshold_applied": False,
        "note": "This stage measures observed within-model classification stability without applying an invented production threshold. Protected adjudication occurs later. Stability is not reported from fewer than three valid samples.",
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
