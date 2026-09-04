# Later-Stage Adversarial Experiments

These experiments are registered now but intentionally **not implemented first**. They require a minimal governor/orchestrator to exist.

## EXP-D — Adversarial System Escape

Status: REGISTERED / DEFERRED UNTIL MINIMAL GOVERNOR EXISTS

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

Attack construction should be separated from the system/design team where practical.

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

Status: REGISTERED / DEFERRED UNTIL MINIMAL GOVERNOR EXISTS

Attack the code implementing governance rather than only model reasoning. Target:

- gate/status transitions;
- permission enforcement;
- evidence ingestion and append-only history;
- exact-artifact/SHA binding;
- semantic graph and change invalidation;
- reviewer/mechanism routing;
- checkpoint/recovery/replay;
- COMPLETE promotion.

Representative goals:
- move UNPROVEN to COMPLETE without required evidence;
- reuse old evidence for a changed artifact;
- let CODE authority modify a protected oracle/test path;
- accept forged CI provenance;
- skip required downstream invalidation;
- execute a forbidden side effect.
