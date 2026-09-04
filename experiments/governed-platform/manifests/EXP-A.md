# EXP-A — Complementary Verification / Correlated Failure

Status: **PRE-REGISTERED PILOT — NOT YET RUN**

## Hypothesis

Different verification mechanisms will exhibit non-identical failure patterns. A portfolio selected for demonstrated marginal coverage will detect more validated defects than simply repeating the same verification method, but the gain may not justify its cost for every risk class.

## Null / falsifying outcome

The architecture's complementary-verification claim is weakened if additional mechanisms show negligible marginal validated defect coverage, strongly correlated misses, excessive false positives, or cost/latency that dominates the benefit.

## Pilot unit

A case is an artifact with independently established ground truth and one or more controlled material defects. Model-facing input must not disclose defect location or ground-truth labels.

## Initial mechanism families

- General reasoning reviewer(s), provider/model independent.
- Specialist reviewer where available and qualified.
- Deterministic verification appropriate to the artifact (schema validation, type/static analysis, unit/property checks, etc.).

No specific vendor/model is foundational to this manifest.

## Required measurements

- Ground-truth defects present.
- Validated defects detected per mechanism.
- False-positive findings.
- Pairwise co-failure on ground-truth defects.
- Unique/marginal validated detections added by each mechanism.
- Input/output token usage where exposed.
- Monetary cost where applicable.
- Latency.

## Pilot decision

Do not set a production routing threshold from theory. Use the pilot to estimate detection, false-positive, co-failure, marginal-coverage and cost distributions. If there is a meaningful signal, pre-register a larger stratified evaluation and choose sample size/decision thresholds from the observed effect sizes and required confidence.

## Anti-leakage controls

Ground truth should be stored outside model-visible case material. Case constructors and evaluated reviewers should be separated where practical. Repeated public benchmark cases must be treated as potentially contaminated.
