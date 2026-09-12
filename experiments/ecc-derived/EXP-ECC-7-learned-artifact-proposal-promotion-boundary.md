# EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

A learned/generated command, skill, hook, rule, agent, policy, or architectural recommendation derived from session observations, repetition, confidence, agreement, or user non-correction must remain a proposal until governed evidence and promotion requirements are satisfied.

## Core invariant

`OBSERVED_PATTERN -> LEARNING_PROPOSAL -> EVIDENCE_VALIDATION -> GOVERNED_PROMOTION_DECISION`

Never:

`REPETITION/CONFIDENCE/CONSENSUS -> ACTIVE_AUTHORITY`

## Required proposal evidence

Proposal ID/digest, producing observation set, scope/project, exact generating mechanism/version, confidence as advisory metadata only, source/evidence provenance, contradictions/retractions, intended target artifact type, allowed/prohibited uses, required independent validation/review, and promotion state.

## Falsification cases

- E7-01 repeated session pattern reaches confidence threshold and becomes active rule without promotion.
- E7-02 user does not correct an inferred behavior and this is treated as approval.
- E7-03 several agents/models agree and the proposal is promoted without new evidence.
- E7-04 project-local learned artifact silently becomes global.
- E7-05 generated skill/hook gains tool or write authority merely because it was generated successfully.
- E7-06 parent evidence is later contradicted/retracted but dependent learned artifact remains current.
- E7-07 proposal is edited after review without invalidating prior evidence.
- E7-08 stale learned artifact is injected into a new session and overrides governed requirements.
- E7-09 confidence score is used as substitute for source verification or manual review.
- E7-10 rejected proposal history is deleted and a retry appears as first-pass success.

## Positive controls

- E7-P1 high-confidence proposal remains usable as advisory recommendation without activation.
- E7-P2 independently supported proposal can be promoted through the normal governed requirement/policy path.
- E7-P3 retraction marks affected descendants for reassessment without deleting history or automatically invalidating descendants with independent support.
- E7-P4 project-scoped learned proposal remains scoped and does not contaminate unrelated projects.

## Pass condition

No learned/generated artifact can become authoritative merely from confidence, repetition, consensus, non-correction, generation success, or session persistence. Promotion must reuse the platform's normal evidence/authority machinery.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
