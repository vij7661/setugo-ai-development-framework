# Ruflo Selective Adoption R2.1 — Post-Review Clarifications

Status: `REVIEWER_REQUIRED_CLARIFICATIONS_FOR_IMPLEMENTATION_PREREGISTRATION`

Authority effect: `NONE`

This file does not reopen or modify EXP-M R5, does not resume RQ-16, and does not authorize implementation. It records the three non-blocking clarifications required by the R2 external reviewer before any RA/FP implementation can qualify.

## C-01 — Unambiguous RA-04 cumulative conservation

For `CUMULATIVE_NONREPLENISHABLE` resources, define each node's `reserved_balance` as the portion of its ancestor-provided grant not yet released back to the parent, including:

- the node's committed/consumed amount charged to that grant;
- live allocation delegated to descendants;
- any other unreleased allocation held by that node.

A parent's root conservation invariant is:

`root_committed_direct + sum(direct_child_reserved_balance) <= root_grant`

and recursively for every child C:

`C_committed_direct + sum(C.direct_child_reserved_balance) <= C_reserved_from_parent`

No term is counted both in a parent outstanding bucket and again as a child balance.

Consumed cumulative units are never returnable. Only unconsumed reserved balance may be released, once, through an idempotent recorded release.

Required implementation tests include a two-level and three-level hierarchy, sibling concurrency, partial consumption then release, duplicate release, and ancestor revocation.

## C-02 — RA-12 route-policy failure is fail-closed

Before execution, a RoutePlan must have:

- current authority snapshot;
- all required prerequisite qualification identities;
- successful policy evaluation;
- current capability generations;
- exact route-plan digest.

If policy evaluation errors, is unavailable, returns unresolved/unknown, the authority snapshot is missing/stale, or any prerequisite qualification cannot be proven current:

`EXECUTION = ABORTED`

Only a non-authoritative diagnostic event may be emitted. No fallback route may inherit the failed route's authority; any fallback creates a new RoutePlan and must be independently evaluated.

## C-03 — RA-11 enforcement path is outside candidate/plugin write authority

The authority-bearing enforcement path for:

- signature verification;
- publisher/trust-root validation;
- dependency closure;
- content-addressed verified-load;
- dynamic-code-fetch verification;
- sandbox/capability enforcement;
- retrieval/context boundary enforcement

must be platform-owned or separately independently qualified and must be outside candidate/plugin write authority for the subject being evaluated.

Candidate/plugin-supplied enforcement code or policy cannot satisfy RA-11 enforcement qualification for itself.

Any unknown enforcement identity/version fails closed.

## Closure condition

These three clarifications must appear as explicit implementation predicates and direct mutation/falsification targets in the applicable FP/RA implementation preregistration before that component can be marked qualified.
