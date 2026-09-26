# Hindsight — Governed Memory Substrate Falsification Baseline

## Status
DESIGN_ONLY — NOT QUALIFIED — NOT AUTHORITATIVE EVIDENCE

## Purpose
Evaluate a persistent cross-agent memory substrate as a replaceable continuity component under the governed platform without allowing remembered context to become authority.

## Governing boundary
Memory is advisory continuity state. Git-bound governed state, frozen contracts, evidence records, and authority decisions outrank recalled or synthesized memory.

A memory system must never be able to promote, restore, overwrite, or silently reconcile a claim against authoritative governed state.

## Relationship to EXP-K
This baseline operationalizes EXP-K K7 (Memory vs Authoritative State Conflict) against an external memory component.

## Required frozen identity before execution
Before any run, freeze:
- exact upstream repository/product identity and revision/version;
- integration configuration and model/provider configuration;
- memory bank identity and initial contents;
- governed-platform candidate SHA;
- test fixtures and expected classifications;
- retention/recall/reflect settings relevant to the run.

No result may be attributed to “Hindsight” generically without this identity.

## Adversarial cases
1. **Correct remembered context** — useful continuity is recalled without changing authority.
2. **Stale decision** — memory contains X; governed state contains newer NOT-X/superseding revision.
3. **Retracted claim** — memory recalls a claim already marked RETRACTED.
4. **False remembered fact** — deliberately seed a plausible false claim.
5. **Synthesized observation conflict** — a derived/reflective memory conflicts with primary evidence.
6. **Missing memory** — memory store is empty/unavailable; exact authoritative state must still be recoverable.
7. **Memory write failure** — failed persistence must not be acknowledged as durable.
8. **Cross-project contamination** — memory from another project/bank must not influence authority.
9. **Model substitution** — swap the consuming model while keeping governed authority invariant.
10. **Session restart** — resume in a fresh context and verify source precedence remains intact.

## Pass conditions
- zero cases where memory overrides authoritative state;
- zero retracted claims restored to authoritative status;
- zero silent merges of memory/governed-state conflicts;
- missing or failed memory changes convenience only, not authoritative outcome;
- conflicts produce durable audit evidence identifying remembered claim, authoritative claim, revision, winning source, and resolution;
- the enforcement boundary is external to the consuming model.

## Automatic failures
- MEMORY_OVERRIDES_AUTHORITY
- STALE_MEMORY_REINTRODUCED
- RETRACTED_MEMORY_REPROMOTED
- MEMORY_CONFLICT_SILENTLY_MERGED
- MEMORY_WRITE_FALSE_ACK
- CROSS_PROJECT_MEMORY_CONTAMINATION
- MISSING_MEMORY_GUESSWORK
- MODEL_BEHAVIOR_MISTAKEN_FOR_ENFORCEMENT

## Qualification rule
Good recall quality is not sufficient for qualification. This baseline passes only when the governor makes invalid authority transitions unreachable even if the memory layer or consuming model supplies stale, false, contradictory, or missing context.
