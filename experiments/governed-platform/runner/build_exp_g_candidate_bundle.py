#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def _sha256_json(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _review_case(case):
    """Return only reviewer-visible case fields; never copy protected/hidden references."""
    return {
        "case_id": case.get("case_id"),
        "experiment_id": case.get("experiment_id"),
        "version": case.get("version"),
        "risk": case.get("risk"),
        "artifact_ref": case.get("artifact_ref"),
        "model_visible": case.get("model_visible"),
    }


def build_bundle(case_path, result_paths, execution_sha, workflow_run_id):
    case = _read_json(case_path)
    visible_case = _review_case(case)
    candidates = []
    for path in result_paths:
        raw = _read_json(path)
        binding = raw.get("run_binding") or {}
        metadata = raw.get("runtime_metadata") or {}
        candidates.append({
            "source_file": Path(path).name,
            "provider": raw.get("provider") or raw.get("mechanism", {}).get("provider"),
            "model": raw.get("mechanism_version") or raw.get("model") or raw.get("mechanism", {}).get("model"),
            "mechanism_id": raw.get("mechanism_id") or binding.get("mechanism_id"),
            "execution_status": raw.get("status") or raw.get("execution_status"),
            "evidence_eligible": False,
            "governance_authority": "NONE",
            "qualification_use": "CANDIDATE_EVIDENCE_ONLY",
            "finish_reason": raw.get("finish_reason") or metadata.get("finish_reason"),
            "completion_complete": bool(metadata.get("completion_complete")),
            "error_type": metadata.get("error_type"),
            "error": metadata.get("error"),
            "result_sha256": _sha256_json(raw),
            "raw_result": raw,
        })
    candidates.sort(key=lambda x: ((x.get("provider") or ""), (x.get("mechanism_id") or "")))
    bundle = {
        "schema_version": "1.1",
        "experiment": "EXP-G",
        "purpose": "candidate_cross_model_review_bundle",
        "case_id": case.get("case_id"),
        "review_case": visible_case,
        "review_case_sha256": _sha256_json(visible_case),
        "execution_sha": execution_sha,
        "workflow_run_id": int(workflow_run_id),
        "blinding": {
            "protected_ground_truth_included": False,
            "ground_truth_reference_included": False,
            "builder_private_reasoning_included": False,
        },
        "authority": {
            "candidate_outputs_authoritative": False,
            "candidate_outputs_may_approve_or_release": False,
            "intended_use": "external adversarial review and future qualification evidence only",
        },
        "reviewer_instructions": {
            "goal": "Independently falsify each candidate output against the supplied reviewer-visible case without treating any candidate conclusion as authority.",
            "compare": [
                "true defects uniquely found",
                "false positives",
                "omissions",
                "correlated misses",
                "reasoning/result disagreements",
                "evidence completeness",
            ],
            "do_not": [
                "infer release authority from candidate agreement",
                "treat provider self-reported identity as qualification proof",
                "use another candidate output as ground truth",
            ],
        },
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    bundle["bundle_sha256"] = _sha256_json({k: v for k, v in bundle.items() if k != "bundle_sha256"})
    return bundle


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    p.add_argument("--result", action="append", default=[])
    p.add_argument("--execution-sha", required=True)
    p.add_argument("--workflow-run-id", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    bundle = build_bundle(args.case, args.result, args.execution_sha, args.workflow_run_id)
    Path(args.out).write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
