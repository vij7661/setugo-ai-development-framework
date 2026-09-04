# Pilot #1 Execution Protocol

Status: **PREPARED — REQUIRES PRIVATE TRUTH + CONFIGURED MECHANISMS**

## Objective

Run the first directional falsification pilot for EXP-A/B/C without claiming general model superiority or statistical significance.

## Freeze before execution

Record:
- repository branch and exact HEAD;
- case IDs + versions;
- private truth versions + hashes;
- adjudication protocol version;
- instruction/prompt version;
- mechanism IDs and actual provider/model/tool versions;
- runtime/privacy/cost policy.

## Blinded run sequence

For each selected case/mechanism:

1. Load the committed case at the frozen exact HEAD.
2. Provide only the permitted model-visible arm/payload.
3. Invoke the configured mechanism with no protected truth access.
4. Preserve raw output immutably with run ID, timestamps and mechanism identity.
5. Normalize without deciding correctness.
6. After capture, adjudicate against private pre-registered truth using the frozen protocol.
7. Deterministically score detection, false positives and authority correctness.
8. Record latency and actual/estimated cost where available.

## Initial comparisons

EXP-A: compare independent reasoning mechanisms and any applicable deterministic verifier for complementary detection.

EXP-B: compare information arms defined by the experiment manifest; do not expose hidden intent/invariants to the blinded arm that is meant not to receive them.

EXP-C: compare unrestricted correction advice against diagnosis-gated/scoped-authority mechanisms only when the arm definitions are frozen before execution.

## No-result fabrication rule

A provider not configured, quota failure, timeout, parser failure or unavailable tool is recorded as BLOCKED/ERROR. It is never replaced by a simulated model answer and never converted to PASS.

## Pilot interpretation

Pilot #1 is directional. Report per-case outcomes, co-failures, false positives, diagnosis/authority errors, cost and latency. Do not invent thresholds or infer statistical significance from this small controlled corpus.

A surprising result should first trigger evidence review for case/truth/adjudication/harness error before changing V4.2 architecture.
