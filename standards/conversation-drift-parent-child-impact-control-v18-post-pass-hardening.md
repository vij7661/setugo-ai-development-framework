# Workflow Drift and Parent-Child Impact Control — V18 Post-Pass Hardening

Status: **PROPOSED V18 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V18-C01 — Exact base binding

V18 is additive over exact V17 candidate `da39da9ea02af6915d4283f6a09c6d18212fa4ed`.

V17 received a clean R3 design disposition `PASS_FOR_NEXT_DESIGN_STAGE` with no Critical findings, but the review remained `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` and recommended `INSUFFICIENT_EVIDENCE_TO_FREEZE`. V18 does not rewrite that result. It narrows five reviewer-identified falsification gaps before any execution freeze.

## V18-C02 — Atomic threshold transaction crash/recovery invariant

The authoritative qualification-to-threshold operation defined by V17-C02 must be implemented as one transactional/consensus commit boundary whose externally observable durable outcomes are only:

- all bound writes committed exactly once; or
- none of the bound writes committed.

The bound set includes at minimum snapshot-consumption state, `ReviewThresholdRecord`, `ReviewThresholdConsumptionLedger` uniqueness state, threshold sequence, predecessor/commit digest, and any required audit/event publication state that policy declares part of the atomic decision.

A crash, process kill, storage fault, leader change, retry, or acknowledgement loss between internal steps must not expose a durable state in which some committed components authorize progress while others are missing.

Recovery must re-read authoritative durable state; it may not infer rollback from a failed acknowledgement. Ambiguous acknowledgement is `REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` until reconciled.

## V18-C03 — Root-governed ledger mutation anti-self-grant

`ReviewThresholdConsumptionLedger`, `PacketGenerationLedger`, their policy registries, and any reset/migration/repair authority are root-governed objects subject to the active root-threshold rule.

No single root guardian, administrator, operator, service, candidate author, reviewer, beneficiary, or colluding subset below the active root threshold may create, replace, reset, fork, truncate, rebase, migrate, or relax these objects or their governing uniqueness/lineage rules.

Every governance mutation binds the exact root-policy version, approving principal set, threshold proof, object/version digest, predecessor digest, reason, and effective sequence.

Sub-threshold mutation attempts emit `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED`.

## V18-C04 — Cross-gate reuse rules are prospective only

A `ReviewEvidenceReusePolicy` allow rule has an immutable `effective_from_sequence` and may authorize only consumption events whose authoritative threshold-consumption sequence is at or after that boundary.

A rule created or widened after evidence was already consumed cannot retroactively convert an earlier denied or unqualified reuse into an authorized count.

Historical consumed records preserve the policy/version/effective-sequence that applied at their commit boundary.

Retroactive application emits `REVIEW_THRESHOLD_REUSE_RETROACTIVE_REJECTED`.

## V18-C05 — Canonical-corpus update dependency invalidation

Every `CanonicalSemanticCorpusRegistry` generation binds a dependency index of governed decisions whose validity depends on that corpus/algorithm generation, including applicable `PARENT_UNAFFECTED`, canonical-equivalence, re-expression, review-projection, and qualification decisions.

When an active corpus/algorithm generation changes, is retracted, becomes stale, or is superseded, affected downstream decisions become `REVALIDATION_REQUIRED` unless independent support proves they are unaffected under the governing dependency rule.

The platform must not silently carry forward a previous `PARENT_UNAFFECTED` or re-expression decision solely because the new corpus update occurred after a prior freeze.

Missing revalidation emits `CANONICAL_CORPUS_DEPENDENT_REVALIDATION_REQUIRED`.

## V18-C06 — ReviewThresholdConsumptionLedger anti-rollback / anti-fork

`ReviewThresholdConsumptionLedger` is append-only and predecessor-linked. Qualification requires current lineage proof against the active governance/evidence witness boundary.

Privileged replacement of the whole ledger, rollback to an earlier valid prefix, sibling-fork creation, hidden alternate lineage, truncation, or predecessor substitution must be detectable before any threshold count is accepted.

Where the authoritative store alone cannot prove non-replacement, the design requires an independently governed witnessed/anchored checkpoint or equivalent external monotonic commitment. Missing current witness evidence is `INSUFFICIENT_EVIDENCE`, never implicit PASS.

Rollback/fork detection emits `REVIEW_THRESHOLD_LEDGER_ROLLBACK_OR_FORK`.

## V18-C07 — Positive-path preservation

These controls must not block legitimate operation when:

- an atomic threshold transaction commits completely and recovery observes the same committed decision;
- a root-threshold-authorized registry migration preserves lineage and uniqueness;
- a reuse policy was valid before the destination consumption event;
- a corpus update triggers and completes the required dependent revalidations;
- a ledger compaction/migration preserves full authoritative history through governed predecessor/witness bindings.

## V18-C08 — Proof-view additions

Reviewer-safe proof/evidence views must expose, as applicable:

- atomic-commit recovery state;
- authoritative consumption sequence;
- root-threshold mutation proof/current policy version;
- reuse-policy effective sequence;
- corpus-generation dependency/revalidation state;
- threshold-ledger lineage/witness currentness.

Missing values are `NOT_PRESENT` or `INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V18-C09 — New endpoints

- `REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN`
- `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED`
- `REVIEW_THRESHOLD_REUSE_RETROACTIVE_REJECTED`
- `CANONICAL_CORPUS_DEPENDENT_REVALIDATION_REQUIRED`
- `REVIEW_THRESHOLD_LEDGER_ROLLBACK_OR_FORK`

## V18-C10 — Freeze rule

V18 grants no execution freeze. V17's design-pass evidence remains evidence for V17 only. V18 must be independently reviewed under the active policy, and execution freeze still requires the independent manual review and live-attestation evidence required by the governing policy.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
