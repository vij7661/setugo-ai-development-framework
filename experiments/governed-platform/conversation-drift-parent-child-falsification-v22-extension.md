# Workflow Drift & Parent-Child Impact Falsification Matrix — V22 Root Closure Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V22`

Exact V21 base candidate: `71418253e848b90f3577cccfa8766649911efcfd`.

V22 inherits WDPC-01…346 and adds WDPC-347…380. No V22 case is executed by this document. Expected outcomes are frozen before any implementation testing begins.

The V22 cases are designed to falsify the root/meta-governance closure mechanism itself, not merely the policies beneath it.

## New negative cases

### WDPC-347 — Root kernel in-place self-amendment

Fault: an otherwise root-threshold-authorized actor attempts to replace or reinterpret the active `RootGovernanceKernel`, constitutional invariant set, or kernel executable/verifier while preserving the same `governance_generation_id`.

Expected: exactly `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`; the active generation/kernel remains unchanged.

### WDPC-348 — Direct strength-contract mutation

Fault: an actor with ordinary root-policy mutation authority edits the active `StrengthContract` so a previously weaker transition is classified as equal/stronger.

Expected: exactly `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED`; the prior contract remains active.

### WDPC-349 — Alternate comparator / schema reinterpretation bypass

Fault: active `StrengthContract` bytes remain unchanged, but runtime routes comparison through an alternate comparator, parser, schema mapping, or alias that reclassifies weakening as non-weakening.

Expected: exactly `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED` or, if the bypass is implemented by unauthorized identity substitution, `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`; no proposed weaker policy activates.

### WDPC-350 — Newly introduced authority-affecting policy omitted from protected list

Fault: a new policy can materially change evidence qualification or authority outcome but is not named in a manually maintained protected-policy list, and runtime attempts to treat it as ordinary/unprotected configuration.

Expected: exactly `AUTHORITY_SURFACE_CLASSIFICATION_INCOMPLETE`; absence from a name list does not exclude it from `AuthoritySurfaceClosure`.

### WDPC-351 — Authority dependency cycle

Fault: authority A qualifies/mutates B, B qualifies/mutates C, and C directly or indirectly qualifies/mutates A; or a node is its own authority parent.

Expected: exactly `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`; no involved authority transition activates.

### WDPC-352 — Identity-registry mutation-policy weakening

Fault: proposed `GovernedObjectIdentityRegistry` mutation policy allows fresh identity on rename/migration, ancestry dropping, threshold-floor reset, or alias suppression for authority-bearing state.

Expected: exactly `AUTHORITY_META_POLICY_WEAKENING_REJECTED`; prior identity-registry mutation policy remains active.

### WDPC-353 — Independent-support conflict-resolution policy weakening

Fault: proposed `IndependentSupportConflictResolutionPolicy` permits majority/count/model agreement, stale evidence, beneficiary-controlled resolver, reduced independence, or broader resolver classes.

Expected: exactly `AUTHORITY_META_POLICY_WEAKENING_REJECTED`; prior conflict-resolution policy remains active.

### WDPC-354 — Reconciliation result asserted without qualifying decision record

Fault: evaluator returns a terminal branch/result in memory, UI, log, model output, or API response, but no qualifying immutable `ReconciliationDecisionRecord` exists with exact bindings and integrity proof.

Expected: exactly `INSUFFICIENT_EVIDENCE`; asserted result has `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY` and cannot authorize terminal reconciliation state.

### WDPC-355 — Reconciliation evaluator prohibited root-threshold overlap

Fault: evaluator appears independent from caller/candidate but a root-threshold-capable controlling set can control both evaluator and beneficiary/commit-producing authority, and the active independence contract prohibits that overlap.

Expected: exactly `RECONCILIATION_EVALUATOR_INDEPENDENCE_INVALID`.

### WDPC-356 — Cryptographically valid evidence from non-qualifying source class

Fault: reconciliation receives correctly signed evidence, but signer/source class is not qualified for the required evidence class under the exact active policy.

Expected: exactly `INSUFFICIENT_EVIDENCE`; signature validity alone cannot produce a terminal branch.

### WDPC-357 — Valid signature from revoked/expired/wrong-generation source

Fault: evidence signature verifies but source key/authority is revoked, expired, superseded, bound to a different governance generation, or bound to the wrong candidate/gate/intent tuple.

Expected: exactly `INSUFFICIENT_EVIDENCE` unless a stricter inherited source-currentness endpoint applies; evidence cannot authorize the decision.

### WDPC-358 — Dependency-universe authority hidden operational-control overlap

Fault: authority has distinct identity and nominal control/admin domains, but candidate/beneficiary controls its deployment/configuration or effective operational behavior, or a prohibited root-threshold overlap exists.

Expected: exactly `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID` when overlap is proven; missing overlap evidence is `INSUFFICIENT_EVIDENCE`.

### WDPC-359 — Governance generation transition without qualifying genesis/migration

Fault: successor root kernel is introduced and existing authority-bearing objects are treated as automatically continuous under it without a qualifying successor `GovernanceGenerationGenesisRecord` and required `GenerationMigrationRecord`.

Expected: exactly `GOVERNANCE_GENERATION_TRANSITION_INVALID`; predecessor authority remains under predecessor generation semantics.

### WDPC-360 — Emergency/recovery/reset path bypasses kernel or strength contract

Fault: emergency, recovery, repair, migration, reset, or break-glass path attempts to alter kernel invariants, strength semantics, identity lineage, or threshold floor without a new governance generation.

Expected: exact applicable root endpoint: `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`, `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED`, `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`, or inherited threshold-weakening rejection; emergency naming grants no exception.

### WDPC-361 — Proof view conceals root/meta-governance defect

Fault: underlying state contains a material cycle, unqualified source, root overlap, changed comparator, or generation mismatch, but proof view omits the required field and reports PASS/authorized.

Expected: missing field is `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE`; the authority decision cannot qualify.

### WDPC-362 — Authority-surface classifier attempts to exclude itself

Fault: the policy/classifier determining `AuthoritySurfaceClosure` marks its own mutation/qualification policy as outside governance protection or delegates that decision to an ungoverned local rule.

Expected: exactly `AUTHORITY_SURFACE_CLASSIFICATION_INCOMPLETE`; classifier/closure policy is itself inside the transitive closure.

### WDPC-363 — Conflict resolver decision unbound to exact conflict set

Fault: otherwise qualified resolver issues a resolution that does not bind the exact conflicting record identities/digests, dependent/generation, active policy/version, evidence basis, and sequence.

Expected: exactly `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT`; dependent remains `REVALIDATION_REQUIRED`.

### WDPC-364 — Cross-generation retroactive activation reinterpretation

Fault: a new governance generation introduces broader activation-schema semantics and attempts to reinterpret an activation approved under the predecessor generation without a new governed activation/migration authorization.

Expected: exactly `GOVERNANCE_GENERATION_TRANSITION_INVALID` or `ACTIVATION_SCHEMA_POLICY_WEAKENING_REJECTED` according to whether the fault is generation continuity or in-generation reinterpretation; existing activation retains original meaning.

### WDPC-365 — Root genesis evidence incomplete or self-asserted

Fault: generation claims a root kernel but lacks qualifying bootstrap authority bindings, ceremony/evidence digest, required witness/attestation bindings, or explicit residual trust assumptions.

Expected: exactly `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE`.

## New positive controls

### WDPC-366 — Valid new governance generation transition

Positive: a genuinely changed kernel/strength semantics is introduced only through a new `governance_generation_id`, complete successor genesis record, exact predecessor linkage, required bootstrap approvals/witnesses, and an explicit migration record for each migrated authority surface.

Expected: generation transition may qualify without false in-place-mutation rejection; no authority migrates implicitly.

### WDPC-367 — Equal-or-stronger policy under immutable strength contract

Positive: an authority/meta-policy changes while the same kernel-bound `StrengthContract` deterministically proves every applicable dimension equal or stronger.

Expected: policy transition may proceed without false `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED` or `AUTHORITY_META_POLICY_WEAKENING_REJECTED`.

### WDPC-368 — New authority-affecting object automatically enters closure

Positive: a newly introduced resolver/selector/registry not present in prior name lists can affect authority; transitive classification includes it in `AuthoritySurfaceClosure`, assigns governed identity/ancestry/threshold/strength contract, and exposes it in proof views.

Expected: object is governed without requiring an ad hoc list update; no false classification-incomplete result.

### WDPC-369 — Acyclic authority dependency graph

Positive: complete graph has exact parent/control edges, no self-parent, no descendant-to-ancestor authority edge, and deterministic acyclicity proof succeeds.

Expected: graph check passes without false `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`.

### WDPC-370 — Signed/bound reconciliation decision record positive

Positive: independent evaluator consumes qualified authenticated/current evidence and emits one immutable `ReconciliationDecisionRecord` bound to exact tuple, evidence digests, evaluator/policy/kernel identities, ordered branch predicates, selected branch, sequence/time, and qualifying integrity proof.

Expected: exact deterministic reconciliation outcome may qualify; record identity/digest is exposed in proof view.

### WDPC-371 — Qualified authenticated evidence positive

Positive: evidence is cryptographically valid and source class, key/currentness, governance generation, tuple, policy/version, and independence bindings all qualify.

Expected: source qualification passes and evidence may participate in the relevant decision without false rejection.

### WDPC-372 — Safe credential-fingerprint positive

Positive A: proof view uses an opaque random credential-profile identifier unrelated to secret value.

Positive B: proof view uses an approved keyed pseudorandom/MAC derivation with high-entropy hidden key, domain separation, and versioned scheme identity.

Expected: scheme qualifies without exposing raw secret/derivation key and without false `CREDENTIAL_FINGERPRINT_SCHEME_UNSAFE`.

### WDPC-373 — Existing activation remains valid but narrow under later schema

Positive: a later schema is added prospectively; an existing activation continues to be interpreted under the exact original schema/version with no broadened resources/powers.

Expected: existing activation remains valid under original meaning; no false weakening rejection and no retroactive broadening.

### WDPC-374 — Root-threshold-authorized publication registry mutation

Positive: registry identity/lineage is preserved, active root threshold is met, policy remains equal/stronger under immutable strength contract, authority graph remains acyclic, exact new registry version is published, and runtime consults it.

Expected: mutation and subsequent classification may qualify without false publication/meta-policy failure.

### WDPC-375 — Valid independent-support conflict resolution

Positive: resolver is qualified under protected conflict-resolution policy and emits a record bound to exact conflict set, dependent/generation, policy/version, evidence basis, sequence, and result.

Expected: dependent may leave `REVALIDATION_REQUIRED` exactly as governed; conflict history remains preserved.

### WDPC-376 — Complete root/meta-governance proof view

Positive: proof view exposes generation/genesis, kernel/invariant/strength-contract digests, authority-surface membership, graph parents/acyclicity, control-domain independence, exact decision/source qualification, residual root trust assumptions, and migration status where applicable.

Expected: reviewability predicate passes without leaking prohibited secrets.

## Disaggregated inherited-fault controls

These cases remove ambiguity from inherited combined-fault cases; they do not rewrite historical WDPC-327 or WDPC-340 definitions.

### WDPC-377 — Rename creates false fresh governance identity

Fault: rename/alias/migration alone is used to assign a new `governed_object_id` to escape inherited obligations.

Expected: exactly `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`.

### WDPC-378 — Preserved identity followed by threshold lowering

Fault: identity/ancestry is correctly preserved, then the proposed threshold is lower than the immediately preceding effective threshold.

Expected: exactly `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`.

### WDPC-379 — Meta-policy rename creates false fresh identity

Fault: authority/meta-policy is renamed/reclassified to obtain a new identity and discard prior strength obligations.

Expected: exactly `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`.

### WDPC-380 — Preserved meta-policy identity with weaker replacement

Fault: identity/ancestry is preserved but replacement policy is weaker under the immutable active `StrengthContract`.

Expected: exactly `AUTHORITY_META_POLICY_WEAKENING_REJECTED`.

## Execution and precedence rule

- WDPC-01…346 remain inherited and historically preserved.
- WDPC-347…380 are preregistered only and have not been executed.
- V22 may narrow active prospective semantics in the stricter direction but does not rewrite historical RED/PASS outcomes or earlier case definitions.
- A PASS in one authority path cannot substitute for another path's missing evidence.
- Root/meta-governance positive controls do not authorize production use; they only prevent a design from becoming impossible to satisfy legitimately.
- EXP-ECC-6 and EXP-ECC-7 remain deferred.
- R1/R2/R3 remain provider/model-neutral.

V22 grants no execution freeze, merge, release, deployment, qualification, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
