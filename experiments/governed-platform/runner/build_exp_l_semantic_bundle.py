#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from math import log
from pathlib import Path

MIN_VALID_SAMPLES_FOR_STABILITY = 3
CANONICAL_FAILURE_CLASSES = (
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
)
FAILURE_TO_ARTIFACT_CLASS = {
    "CODE DEFECT": "CODE",
    "FIXTURE-DATA DEFECT": "FIXTURE-DATA",
    "TEST DEFECT": "TEST",
    "ENVIRONMENT-TOOLING DEFECT": "ENVIRONMENT-TOOLING",
    "REQUIREMENT UNRESOLVED": None,
}
CANONICAL_ARTIFACT_CLASSES = {
    "CODE",
    "FIXTURE-DATA",
    "TEST",
    "ENVIRONMENT-TOOLING",
}


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


def _norm_text(value: str) -> str:
    return " ".join(value.strip().split())


def _canonical_failure_class(value) -> str | None:
    if not isinstance(value, str):
        return None
    text = _norm_text(value).upper()
    for failure_class in CANONICAL_FAILURE_CLASSES:
        if text == failure_class or text.startswith(failure_class + ":") or text.startswith(failure_class + " -"):
            return failure_class
    return None


def _canonical_contributors(values, *, primary: str | None) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    result = set()
    for value in values:
        failure_class = _canonical_failure_class(value)
        if failure_class and failure_class != primary:
            result.add(failure_class)
    return tuple(sorted(result))


def _scope_semantics(result: dict) -> tuple[tuple[str, ...], int]:
    """Map free-text authorized scope to semantic artifact classes within one result.

    The model may describe physical paths/components with different wording across
    samples. We therefore do not compare those strings across samples. Instead,
    each authorized scope item is mapped to the canonical failure/artifact class
    of the finding that owns that scope. Unmapped scope remains explicit because
    silently dropping it could hide an unsafe authority expansion.
    """
    raw_scope = result.get("authorized_scope")
    if not isinstance(raw_scope, list):
        raw_scope = []
    authorized = {
        _norm_text(item)
        for item in raw_scope
        if isinstance(item, str) and _norm_text(item)
    }
    if not authorized:
        return (), 0

    classes: set[str] = set()
    matched: set[str] = set()

    for item in authorized:
        direct = item.upper()
        if direct in CANONICAL_ARTIFACT_CLASSES:
            classes.add(direct)
            matched.add(item)

    for finding in result.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        failure_class = _canonical_failure_class(finding.get("failure_class"))
        artifact_class = FAILURE_TO_ARTIFACT_CLASS.get(failure_class) if failure_class else None
        finding_scope = {
            _norm_text(item)
            for item in (finding.get("artifact_scope") or [])
            if isinstance(item, str) and _norm_text(item)
        }
        overlap = authorized & finding_scope
        if overlap:
            matched.update(overlap)
            if artifact_class:
                classes.add(artifact_class)

    return tuple(sorted(classes)), len(authorized - matched)


def _sample_label(result: dict) -> str | None:
    """Return a deterministic task-specific semantic signature for diagnosis cases.

    Material semantics are primary class, contributing classes and semantic
    artifact classes authorized to change. Physical scope wording is deliberately
    excluded so lexical variants do not manufacture disagreement. Unmapped scope
    is preserved as a material marker rather than silently discarded.
    """
    if result.get("status") != "PASS" or not result.get("evidence_eligible"):
        return None

    scope_classes, unmapped_scope_count = _scope_semantics(result)
    scope_parts = list(scope_classes)
    if unmapped_scope_count:
        scope_parts.append("UNMAPPED_SCOPE")
    scope_text = ",".join(scope_parts) if scope_parts else "NONE"

    diagnosis = result.get("diagnosis") or {}
    primary_raw = diagnosis.get("primary_failure_class")
    primary = _canonical_failure_class(primary_raw)
    if isinstance(primary_raw, str) and primary_raw.strip():
        primary_text = primary or "NONCANONICAL"
        contributors = _canonical_contributors(diagnosis.get("contributors", []), primary=primary)
        contributor_text = ",".join(contributors) if contributors else "NONE"
        return f"PRIMARY={primary_text}|CONTRIB={contributor_text}|SCOPE_CLASSES={scope_text}"

    finding_classes = {
        failure_class
        for finding in (result.get("findings") or [])
        if isinstance(finding, dict)
        for failure_class in [_canonical_failure_class(finding.get("failure_class"))]
        if failure_class
    }
    if len(finding_classes) == 1:
        return f"FINDING={next(iter(finding_classes))}|SCOPE_CLASSES={scope_text}"
    if len(finding_classes) > 1:
        return f"FINDINGS={','.join(sorted(finding_classes))}|SCOPE_CLASSES={scope_text}"
    return f"NO_MATERIAL_DEFECT|SCOPE_CLASSES={scope_text}"


def build_bundle(case_id: str, result_paths: list[Path], execution_sha: str, workflow_run_id: int) -> dict:
    samples = []
    by_provider: dict[str, list[dict]] = {}
    for path in sorted(result_paths):
        result = _read(path)
        provider = result.get("provider") or "unknown"
        label = _sample_label(result)
        scope_classes, unmapped_scope_count = _scope_semantics(result)
        sample = {
            "source_file": path.name,
            "provider": provider,
            "model": result.get("mechanism_version"),
            "status": result.get("status"),
            "evidence_eligible": bool(result.get("evidence_eligible")),
            "semantic_proxy_label": label,
            "semantic_scope_classes": list(scope_classes),
            "unmapped_authorized_scope_count": unmapped_scope_count,
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
            "semantic_proxy_version": "diagnosis-material-signature-v3",
            "semantic_proxy": "primary diagnosis + canonical contributors + semantic authorized artifact classes; unmapped authority retained; not a general semantic-equivalence model",
            "cluster_counts": dict(sorted(counts.items())),
            "normalized_semantic_entropy": _normalized_entropy(labels),
            "observed_single_cluster": observed_single_cluster,
            "stable_single_cluster": sufficient and observed_single_cluster,
            "samples_with_unmapped_authorized_scope": sum(1 for s in provider_samples if s["unmapped_authorized_scope_count"]),
            "total_input_tokens": sum((s["input_tokens"] or 0) for s in provider_samples),
            "total_output_tokens": sum((s["output_tokens"] or 0) for s in provider_samples),
            "total_latency_ms": sum((s["latency_ms"] or 0) for s in provider_samples),
        })

    bundle = {
        "schema_version": "1.3",
        "experiment": "EXP-L",
        "pilot_stage": "SEMANTIC_CALIBRATION_COLLECTION",
        "case_id": case_id,
        "execution_sha": execution_sha,
        "workflow_run_id": int(workflow_run_id),
        "scientific_status": "COLLECTION_ONLY_NOT_ADJUDICATED",
        "authority": "NONE",
        "threshold_applied": False,
        "note": "This stage measures observed within-model structured diagnosis stability without applying an invented production threshold. Stability is not reported from fewer than three valid samples. Mixed-cause contributors and semantic artifact-class authority are part of the signature; lexical physical-scope differences are not.",
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
