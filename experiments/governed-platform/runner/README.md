# Pilot Runner Adapter Contract

The experiment runner must not encode a preferred provider or model in experiment logic.

## Adapter input

A runner receives:
- `case_id` and case version;
- only the `model_visible` payload for the selected arm;
- a versioned review/diagnosis instruction;
- mechanism configuration supplied outside the case;
- an authorized tool/permission profile, normally none for review-only pilots.

Protected ground truth is never passed to the evaluated mechanism.

## Normalized adapter output

Every adapter must normalize its native response to:

```json
{
  "run_id": "...",
  "case_id": "...",
  "case_version": "1.0",
  "mechanism_id": "configured-at-runtime",
  "mechanism_version": null,
  "provider": null,
  "status": "PASS|FAIL|BLOCKED|ERROR|UNCERTAIN",
  "findings": [
    {
      "finding_id": "mechanism-local-id",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|PREFERENCE|SPECULATIVE",
      "claim": "...",
      "evidence": ["..."]
    }
  ],
  "detected_defect_ids": [],
  "diagnosis": null,
  "authorized_scope": [],
  "changed_artifacts": [],
  "raw_output_ref": "...",
  "evidence_refs": [],
  "input_tokens": null,
  "output_tokens": null,
  "estimated_cost_usd": null,
  "latency_ms": null
}
```

`detected_defect_ids` are assigned only during blinded adjudication/scoring; the evaluated model is not told protected defect IDs.

## Separation of roles

1. **Mechanism adapter** invokes a model/tool and preserves raw output.
2. **Normalizer** maps native output to stable fields without deciding correctness.
3. **Blinded adjudicator** maps concrete findings to protected ground-truth defect IDs and marks unsupported findings.
4. **Deterministic scorer** calculates detection/false-positive/authority/cost metrics.

A model may be studied as an adjudicator in a separate experiment, but its judgment must not silently become ground truth.

## Required runtime configuration

Provider/model/tool identity, endpoint/auth method, cost metadata and privacy eligibility are configuration/registry data. They must not be hard-coded into EXP-A/B/C manifests or case files.

## Failure behavior

Provider timeout, quota, unavailable model, invalid response, parser error and policy denial are execution outcomes (`ERROR`/`BLOCKED`), not defect-detection misses unless the pre-registered analysis explicitly defines otherwise.
