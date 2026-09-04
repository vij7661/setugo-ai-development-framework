# Later-Stage Adversarial Experiments

These experiments require the minimum governance capabilities appropriate to their attack surface. Activation is evidence-based rather than calendar-based.

## EXP-D — Adversarial System Escape

Status: **ACTIVE — MINIMAL GOVERNOR QUALIFIED FOR PILOT ATTACKS**

Activation evidence:
- deterministic minimal governor implemented in `governance/governor.py`;
- exact project/task/SHA binding;
- authenticated-event requirement;
- replay/deduplication guard using stable source + event identity;
- optimistic state-version guard for race/out-of-order events;
- mandatory human-gate enforcement;
- required-evidence and COMPLETE-promotion enforcement;
- corrective-scope restriction by canonical failure class;
- CI regression run 33902305725 passed at exact head `652589858dae3341cb5ec5a2f805de0ad4a9e320`.

The pilot attack set begins with `EXP-D-001` through `EXP-D-004` covering stale-SHA acceptance, manual-gate bypass, replayed side effects, and unauthorized COMPLETE promotion. These are baseline attacks, not an exhaustive red-team portfolio.

An independent red-team process is not constrained to the known failure taxonomy. It attempts to achieve one or more of:

- false-green acceptance;
- unauthorized artifact modification;
- evidence suppression or spoofing;
- incorrect COMPLETE promotion;
- unsafe/destructive external side effect;
- semantic-staleness escape;
- permission-boundary bypass;
- budget/reviewer denial-of-service;
- another governance escape not anticipated by the designers.

Attack construction should be separated from the system/design team where practical. Deterministic baseline attacks may be authored by the implementation team, but they do not satisfy the independent-red-team requirement by themselves.

## EXP-E — Accepted-Baseline Change/Revalidation

Status: REGISTERED / BUILD AFTER MINIMAL INVARIANT + DEPENDENCY GRAPH

Begin from a known accepted baseline. Introduce compatible, modifying, contradictory, foundational, lexically-different-but-semantically-conflicting, and interacting changes. Include hidden missing/incorrect dependency edges.

Measure:
- change classification;
- affected invariant detection;
- contradiction detection;
- downstream invalidation precision/recall;
- correct lifecycle re-entry;
- stale evidence retained incorrectly;
- unnecessary revalidation;
- intentional change vs old defect vs unresolved-requirement classification.

## EXP-F — Governance/Orchestrator Falsification

Status: **PARTIALLY UNBLOCKED — MINIMAL GOVERNOR EXISTS; BROADER ORCHESTRATOR/GRAPH ATTACKS REMAIN DEFERRED**

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
- interpret resource/budget exhaustion as successful convergence or PASS.

Event-driven continuation is governed by `governance/EVENT_CONTINUATION.md`. Schedules/polling are fallback mechanisms and must not be treated as the primary continuation architecture.
