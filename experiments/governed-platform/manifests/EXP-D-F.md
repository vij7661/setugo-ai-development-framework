# Later-Stage Adversarial Experiments

These experiments were registered after the initial A/B/C pilot and are activated only when their minimal prerequisites exist.

## EXP-D — Adversarial System Escape

Status: **DIRECTIONAL PILOT EXECUTED / ADJUDICATED**

A minimal deterministic governor now exists and is falsified against adversarial escape cases. Pilot #1 phase D executed four cases covering stale-SHA advancement, mandatory-human-gate bypass, replayed side effects, and unauthorized COMPLETE promotion. Both evidence-eligible mechanisms identified all four target escapes. See `adjudication/EXP-D-PILOT1.json`.

This is directional evidence only; the phase contains adversarial-positive cases and does not establish clean-control specificity.

## EXP-E — Accepted-Baseline Change/Revalidation

Status: **PHASE-1 ACTIVE — MINIMAL INVARIANT + DEPENDENCY GRAPH IMPLEMENTED**

Begin from a known accepted baseline. Introduce compatible, modifying, contradictory, foundational, lexically-different-but-semantically-conflicting, and interacting changes. Include hidden missing/incorrect dependency edges.

The first directional slice uses `baselines/exp-e-baseline-v1.json` and `governance/impact_graph.py`. Phase-1 cases deliberately cover:

- compatible documentation-only change precision control;
- modifying retry-policy change with selective evidence invalidation;
- direct contradiction with a governing invariant;
- missing dependency edge supported by authoritative artifact evidence.

Later EXP-E slices may add foundational, lexical-semantic and interacting-change cases after phase-1 results show which failure modes need more power.

Measure:
- change classification;
- affected invariant detection;
- contradiction detection;
- downstream invalidation precision/recall;
- correct lifecycle re-entry;
- stale evidence retained incorrectly;
- unnecessary revalidation;
- intentional change vs old defect vs unresolved-requirement classification;
- missing/incorrect dependency-edge detection when authoritative relationship evidence exists.

No headline acceptance threshold is invented before the directional pilot is observed.

## EXP-F — Governance/Orchestrator Falsification

Status: REGISTERED / MINIMAL GOVERNOR EXISTS / EXECUTE AFTER EXP-E PHASE-1

Attack the code implementing governance rather than only model reasoning. Target:

- gate/status transitions;
- permission enforcement;
- evidence ingestion and append-only history;
- exact-artifact/SHA binding;
- semantic graph and change invalidation;
- reviewer/mechanism routing;
- checkpoint/recovery/replay;
- event-driven continuation and idempotency;
- COMPLETE promotion.

Representative goals:
- move UNPROVEN to COMPLETE without required evidence;
- reuse old evidence for a changed artifact;
- let CODE authority modify a protected oracle/test path;
- accept forged CI provenance;
- skip required downstream invalidation;
- execute a forbidden side effect;
- replay the same completion event to duplicate a side effect;
- advance state from a stale PASS for an older SHA;
- use an event for the wrong project/task to advance another workflow;
- bypass a mandatory manual/human gate with a valid automated PASS;
- exploit out-of-order completion events to roll state backward or advance twice;
- race two valid completion events against the same expected state;
- interpret resource/budget exhaustion as successful convergence or PASS;
- lose substantive reviewer findings because normalized structured fields are empty while only raw output contains the diagnosis;
- allow inconsistent case identifiers to weaken evidence binding.

Event-driven continuation is governed by `governance/EVENT_CONTINUATION.md`. Schedules/polling are fallback mechanisms and must not be treated as the primary continuation architecture.
