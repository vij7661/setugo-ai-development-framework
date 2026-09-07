# PR5 Combined Review Repair 001 — Preregistration

## Status

`PREREGISTERED_BEFORE_COMBINED_REPAIR`

## Evidence inputs

1. DeepSeek-origin review content originally submitted under `REV-GOV-PR5-003` with false Anthropic self-declared metadata; identity corrected by `REV-GOV-PR5-003-reviewer-identity-correction.json`.
2. Actual Claude manual-relay review of the same superseded candidate, preserved as `REV-GOV-PR5-003-claude-manual-relay-unverified.json`.
3. User-performed reviewer-identity spoof falsification: a DeepSeek response declaring Anthropic/Claude metadata was accepted by the runtime's prior structural validator as if provider identity were proven.

None of these reviews count as promotion evidence for the current/future candidate. They are defect evidence only.

## Combined defects to close

### C1 — Reviewer identity self-attestation

Review content must not authenticate its own provider/model identity. Production API modes must derive identity from a trusted provider-adapter execution envelope. `MANUAL_RELAY` without authenticated provenance must be marked `IDENTITY_UNVERIFIED` and cannot satisfy a provider-specific mandatory-review requirement.

### C2 — Proposer-controlled review classification

A proposer-controlled `trigger`, `material_authority_transition`, or `standard_requires_review` flag must not be sufficient to waive mandatory review. Material authority promotion must fail closed to review-required. Governance-relevant path/action classification must come from platform-owned deterministic context, not R1 self-labeling.

### C3 — Review transport/evidence/promotion wiring

The promotion gate must consume actual ReviewRequest + ReviewEvidence + trusted reviewer execution provenance directly. No caller-supplied boolean or unrecognized transport state may mint review validity.

### C4 — Reviewer invariant defense in depth

Evidence acceptance must independently require valid required-reviewer provider and model/model-class constraints even if an earlier builder normally enforces them.

### C5 — Shared-memory grounding

Promotion must require shared-memory pointers/state to reconcile with authoritative checkpoint state. Stale/conflicting memory blocks promotion until reconciled.

### C6 — Portable packet completeness and reproducible integrity

Manual review export must contain the required review artifact set, evidence-reference coverage, and raw canonical artifact bytes with reproducible hashes. Markdown is convenience only and must not be the sole byte-authoritative representation.

### C7 — Review request/replay identity

Superseded review requests cannot count toward later candidates. Active packet replay must bind to original reviewed candidate/evidence and must not silently rebind to later metadata runs.

## Frozen repair expectations

The combined repair must add deterministic regressions proving at least:

1. A materially authoritative transition mislabeled `ROUTINE_FORMATTING` cannot avoid required review.
2. A governance-relevant path change cannot be downgraded by R1 trigger choice.
3. A DeepSeek/manual response that self-declares `provider=anthropic` cannot satisfy an Anthropic-specific requirement without authenticated provenance.
4. `MANUAL_RELAY` with `IDENTITY_UNVERIFIED` remains useful as review content but cannot satisfy provider-specific mandatory review.
5. `AUTOMATIC_API` and `USER_INITIATED_API` derive provider/model identity from trusted adapter metadata, not reviewer-authored response fields.
6. API error/timeout/unrecognized dispatch state cannot become valid review evidence.
7. Missing required reviewer provider/model constraints fail at evidence acceptance.
8. Stale shared memory blocks material promotion.
9. Missing required packet artifact/evidence reference fails packet validation.
10. Raw exported artifact hashes are independently reproducible without Markdown newline/fence normalization.
11. Superseded/wrong-revision review evidence remains non-promotable.
12. AUTO_MODE and MANUAL_MODE continue to differ only in initiation, not authority semantics.

## Scientific/engineering discipline

- Do not alter Slice 3 frozen tests or preregistration.
- Preserve all previous review requests and evidence.
- Do not count model consensus as evidence.
- Do not merge PR #5 based on the proposing model's own repair/CI.
- After combined repair is CI-green, freeze a new exact candidate and obtain a fresh independent review of that exact candidate.
