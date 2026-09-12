# Workflow Drift & Parent-Child Impact Falsification Matrix — V20 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V20`

V20 inherits WDPC-01…308 and adds WDPC-309…326. It also narrows expected evidence semantics for WDPC-284, WDPC-285, WDPC-287, WDPC-288, WDPC-290, WDPC-291, WDPC-292, WDPC-299 and WDPC-308.

No V20 case is executed by this document. Expected outcomes are frozen before implementation testing begins.

## Narrowed inherited cases

### WDPC-284 — Root-policy lowering is itself invalid

Fault: the current mutation threshold is T and a governed policy rotation approved under T proposes a lower future threshold T-1, with no immediate ledger mutation.

Expected: the policy change itself is rejected as `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`; T remains active.

### WDPC-285 — Independently derived eligible dependency universe

Fault: the corpus/algorithm generation omits a dependent from its own claimed universe, while the independent `DependencyUniverseAuthority` enumerates that dependent from authoritative registries.

Expected: `eligible_dependency_set` includes the omitted dependent, producing a non-empty eligible-minus-indexed difference and `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`.

### WDPC-287 — Proven witness non-independence

Fault: evidence proves a witness shares a forbidden control/admin/credential/recovery/mutation domain with the ledger/root operator below the required independence threshold.

Expected: exactly `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`.

### WDPC-288 — Required witness unavailable or currentness unprovable

Fault: a required witness is unavailable or currentness evidence is missing, without evidence proving non-independence/revocation/compromise.

Expected: exactly `INSUFFICIENT_EVIDENCE`.

### WDPC-290 — Migration while witness unavailable

Fault: physical migration completes while a required witness is unavailable; the system attempts to activate the migrated representation as qualification-authoritative.

Expected: exactly `INSUFFICIENT_EVIDENCE`; preparation may remain durable but authority activation does not occur.

### WDPC-291 — `OUTCOME_UNKNOWN` deterministic reconciliation

Fault: acknowledgement is lost after a possible commit. Reconciliation executes the V20 fixed decision table.

Expected: exactly one terminal endpoint selected by predicates: structural contradiction → `RECONCILIATION_CONFLICT`; one complete authoritative commit → `COMMIT_CONFIRMED_EXISTING`; authoritative proof of absence → `NO_COMMIT_CONFIRMED`; otherwise → `INSUFFICIENT_EVIDENCE`. No duplicate count.

### WDPC-292 — Weaker-threshold versus sub-threshold distinction

Fault A: reset/repair/migration policy proposes a weaker effective mutation threshold.

Expected A: `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`.

Fault B: effective threshold is unchanged/stronger, but approving principal set is below it.

Expected B: `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED`.

### WDPC-299 — Execution attestation replay hardening

Fault: a previously valid attestation is replayed against a different candidate, action, control version/digest, runtime path, or action-instance digest, or is self-declared by a non-qualifying issuer.

Expected: `CONTROL_EXECUTION_EVIDENCE_REQUIRED`.

### WDPC-308 — Secret-safe configuration proof

Positive control: current canonical tool/MCP attestation matches and proof view contains only approved secret-safe fields/fingerprints.

Expected: config predicate is current and deterministic secret non-exposure predicate passes.

## New negative cases

### WDPC-309 — Threshold lowering without immediate mutation

Fault: old threshold authorizes a lower future threshold; no mutation occurs until a later normal operation uses the lower value.

Expected: lowering is rejected at policy transition with `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`; later operation still sees original threshold.

### WDPC-310 — Authority-bearing publication misclassified as non-authority-bearing

Fault: a publication/event class capable of presenting an authoritative decision is locally/policy-labeled non-authority-bearing and omitted from atomic state.

Expected: root-governed registry/unknown-default rule prevents omission; `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID` or `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION` according to whether failure occurs at classification or commit validation.

### WDPC-311 — Circular dependency universe attempt

Fault: corpus/algorithm under change attempts to define/filter its own `eligible_dependency_set` and suppress one dependent.

Expected: self-derived universe is non-qualifying; independent universe authority controls; omitted dependent remains visible and blocks with `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE` or `INSUFFICIENT_EVIDENCE` if universe-authority proof is missing.

### WDPC-312 — Reconciliation contradictory durable evidence

Fault: ledger/threshold record claims commit A while uniqueness/publication or required current witness proves incompatible decision B for the same intent tuple.

Expected: exactly `RECONCILIATION_CONFLICT`.

### WDPC-313 — Reconciliation ambiguous but non-contradictory evidence

Fault: some required evidence is missing/lagging and remaining evidence cannot prove commit or absence, with no contradiction.

Expected: exactly `INSUFFICIENT_EVIDENCE`.

### WDPC-314 — Witness recovery-domain overlap hidden behind otherwise independent identity

Fault: witness has distinct nominal identity but its recovery credential or admin authority is controlled by the ledger/root operator below the independence threshold.

Expected: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`.

### WDPC-315 — Revoked/rotated witness checkpoint replay

Fault: old checkpoint signed by a previously valid but revoked/superseded witness key is replayed as current after governed key rotation.

Expected: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`.

### WDPC-316 — Witness exceeds exact lag bound

Fault: witness sequence/time lag exceeds the configured governed maximum while checkpoint digest is otherwise internally valid.

Expected: `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`.

### WDPC-317 — Expired independent-support exemption reused

Fault: exemption record is structurally valid but expired/revoked/stale at consuming decision time.

Expected: `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`; dependent remains `REVALIDATION_REQUIRED`.

### WDPC-318 — Conflicting independent-support exemptions

Fault: two current-looking exemption records conflict for the same dependent/generation pair and no governed conflict-resolution result exists.

Expected: `INDEPENDENT_SUPPORT_EXEMPTION_INVALID` or `REVALIDATION_REQUIRED` according to the active conflict rule; no exemption is accepted solely by count/majority.

### WDPC-319 — Execution attestation replay across action instance

Fault: exact control/version evidence from action instance A is reused for otherwise similar action instance B.

Expected: `CONTROL_EXECUTION_EVIDENCE_REQUIRED`.

### WDPC-320 — Self-declared execution attestation by implementation under test

Fault: implementation under test emits its own attestation under an issuer class not allowed by the governing attestation policy.

Expected: `CONTROL_EXECUTION_EVIDENCE_REQUIRED`.

### WDPC-321 — Canonical config proof exposes secret or reversible credential material

Fault: canonical configuration identity is correct but proof view contains a raw secret, token, private credential material, recoverable encoding, or disallowed reversible fingerprint.

Expected: `CONFIG_PROOF_SECRET_EXPOSURE_REJECTED`.

### WDPC-322 — Activation alias/wildcard scope creep

Fault: activation permits resource A, while runtime interprets alias/wildcard/parent scope to mutate resource B not explicitly covered by the governed scope schema.

Expected: `CAPABILITY_ACTIVATION_NOT_AUTHORIZED`.

## New positive controls

### WDPC-323 — Root threshold strengthening positive control

Positive: current threshold T validly rotates to stronger T+1 and later authorized ledger migration satisfies T+1.

Expected: policy rotation and migration may proceed without anti-weakening rejection.

### WDPC-324 — Reconciliation exact terminal outcomes positive table

Positive subcases exercise each deterministic V20 branch independently: one complete existing commit, authoritative absence with one same-idempotency retry, structural conflict, and insufficient evidence.

Expected: each subcase maps to exactly its specified terminal endpoint; no second threshold count.

### WDPC-325 — Governed witness key rotation/currentness recovery positive control

Positive: old witness key is retired, new key is governedly linked, quorum/currentness/continuity predicates pass, and new checkpoint binds current ledger sequence/digest.

Expected: new witness may qualify; retired key cannot.

### WDPC-326 — Independent universe and complete revalidation positive control

Positive: independent universe authority enumerates all eligible dependents, index matches exactly, each indexed dependent is revalidated or covered by one current non-conflicting governed exemption.

Expected: both set differences empty and downstream decisions may regain current status.

## Execution rule

WDPC-309…326 are preregistered only. No V20 case has been executed. Historical V19 cases remain preserved; V20 narrows expectations without rewriting earlier evidence.

EXP-ECC-6 and EXP-ECC-7 remain deferred and have no integrated/pass case here.

V20 grants no execution freeze, merge, release, deployment, qualification, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
