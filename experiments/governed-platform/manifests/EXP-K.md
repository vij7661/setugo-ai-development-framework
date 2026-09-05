# EXP-K — Conditional Review Cost and Token Efficiency

Status: **PRE-REGISTERED / NOT YET SCIENTIFICALLY ADJUDICATED**

## Goal

Measure whether conditional review can preserve safety/quality while reducing model calls, tokens, cost and latency compared with always-one-model and always-three-model strategies.

## Central hypothesis

A policy-owned Review Decision Engine can deliver lower cost per safely resolved case and lower cost per additional true defect found than indiscriminate multi-model review, without materially increasing false-green outcomes.

## Strategies under test

- `R1_ONLY` — only Reviewer 1 runs.
- `ALWAYS_THREE` — R1, R2 and R3 run for every case.
- `CONDITIONAL` — EXP-H policy chooses whether R2/R3 are called.

## Required retained metrics per case

- strategy
- correctness / false-green outcome from protected scoring
- true material defects discovered
- reviewer calls
- prompt tokens
- completion tokens
- total tokens
- monetary cost using frozen price table/version
- wall-clock latency
- human escalation state

## Mandatory falsification cases

- K001 low-risk clean case: CONDITIONAL should avoid unnecessary reviewer cost.
- K002 material defect caught by R2: CONDITIONAL must count added discovery and its marginal cost.
- K003 material defect only caught by R3: CONDITIONAL must not hide R3 cost.
- K004 conditional strategy skips a needed review and false-greens: efficiency claim must fail.
- K005 always-three has no extra true finding on clean case: extra tokens count as overhead.
- K006 provider failure/retry: consumed tokens/latency/cost remain attributable where measurable.
- K007 missing cost/token evidence: case cannot support an efficiency claim.
- K008 price-table version changes: cross-run monetary comparison must retain price version.

## Primary metrics

- average reviewer calls per case
- average tokens per case
- average cost per case
- p50/p95 latency
- false-green rate
- true material defects found
- marginal tokens/cost per additional true defect versus R1_ONLY
- avoidable review cost versus ALWAYS_THREE
- human-escalation rate

## Decision rule

EXP-K cannot be called successful because CONDITIONAL is cheaper. Directional success requires that cost/token savings are achieved without a materially worse protected false-green outcome. Any cheaper strategy that increases unsafe false-green outcomes is classified as false efficiency.

## Product boundary

Token reduction is an optimization layer below governance. Future compression, retrieval, summarization or context caching may reduce token use, but they must preserve authoritative requirements, evidence provenance and the context needed for independent review.
