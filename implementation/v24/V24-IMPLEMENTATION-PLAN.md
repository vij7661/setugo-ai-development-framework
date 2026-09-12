# V24 Implementation Plan

Status: `PLANNING_ONLY`
Frozen design: `db9e4b349fd26e128f4486878a4af64929000a7c`
Implementation baseline: `a0c780b516b83ff8a1d0cdfd3724545d7dd6668b`
Authority effect: `NONE_EVIDENCE_ONLY`

## Operating rule

This plan implements the reviewed V24 design without modifying its normative semantics. Reviewer recommendations are evidence only. Every implementation slice must preserve inherited V5–V23 controls, exact-artifact binding, evidence-vs-authority separation, fail-closed behavior, idempotency/recovery properties, and historical failure evidence.

No implementation slice may be declared complete from code existence alone. Completion requires the slice-specific contract, impact analysis, targeted negative tests, positive controls, affected regression tests, and explicit unresolved evidence.

## V24-I0 — Baseline and traceability

Purpose: establish the exact pre-change state and implementation boundary before runtime mutation.

Deliverables:
- exact V24/V23 baseline binding;
- implementation traceability manifest;
- ChangeImpactManifest;
- reconciled DeepSeek Round-2 evidence;
- exact implementation dependency order;
- base→I0 diff proving planning-only changes.

Exit criterion: zero runtime files changed and all I0 planning artifacts are committed.

## V24-I1 — Normative control foundation

Implement:
- `NormativeArtifactManifest`;
- `NormativeControlCatalog`;
- machine-readable `ControlDescriptor` bundle;
- `LegacyControlContinuityManifest` mapping active V5–V23 controls.

Primary existing surfaces:
- `governance-runtime/validate_runtime.py`;
- `governance-runtime/review_protocol.py`;
- V5–V24 standards/experiment artifacts.

Key rule: one authoritative machine-readable semantic source; do not duplicate policy logic in multiple runtimes.

Required evidence before exit:
- exact artifact/blob binding;
- descriptor completeness tests;
- inherited-control continuity positive/negative tests;
- no active V5–V23 obligation silently dropped.

## V24-I2 — Authority universe, sinks, dependency graph and functional closure

Implement:
- `AuthoritySinkRegistry`;
- `ConsequentialEffectorRegistry`;
- `AuthorityDependencyGraph`;
- independently qualified edge completeness;
- `AuthorityEffectPathAudit`;
- `ControlPlaneConformanceRecord`;
- automatic completeness-required classification for functionally authority-affecting paths.

Primary existing surfaces:
- execution gateway;
- repository gateway;
- terminal authority/executor;
- remote transport;
- credential/control-plane path;
- external side-effect gateway.

Key rule: authority classification is based on functional effect, not component name.

## V24-I3 — Effective control and independent capability/deployment attestation

Implement:
- `EffectiveControlSourceRegistry`;
- `EffectiveControlRelationshipRegistry`;
- deterministic `EffectiveControlClosure`;
- `AuthorityCapabilityInventory`;
- `CapabilityInventoryEntryAttestation`;
- independent deployment/capability measurement record and re-attestation.

Primary existing surfaces:
- capability guard;
- authority binding;
- qualification guard;
- credential profile/lease logic;
- reviewer/witness/evaluator independence predicates.

Key rules:
- silence is never proof of no control relationship;
- source availability failure becomes insufficient evidence, not fabricated negative evidence;
- capability/deployment drift invalidates stale attestation.

## V24-I4 — Completeness qualification and bootstrap

Implement:
- `CompletenessQualificationRecord`;
- `CompletenessQualificationLedger`;
- IUDA set and `UniverseDerivationDecisionRecord`;
- `BootstrapCompletenessAuthoritySet`;
- `GovernanceGenerationGenesisRecord`;
- explicit residual trust declaration;
- self-qualification/self-activation prohibitions.

Primary existing surfaces:
- qualification guard;
- runtime validator;
- authoritative-state persistence primitives.

Key rule: completeness machinery cannot bootstrap itself into authority.

## V24-I5 — Endpoint and proof compilers

Implement:
- compiled, kernel-bound `AuthorityEndpointPrecedenceTable`;
- proof-view applicability compiler;
- `ProofViewCompletenessManifest`.

Primary existing surfaces:
- per-gateway deny/dispatch logic;
- runtime validator;
- candidate-review materialization;
- review protocol;
- provider-review telemetry/dashboard.

Key rule: gateway-local ordering may consume a compiled table but cannot independently redefine endpoint precedence.

## V24-I6 — Admission, kernel decisions, application records and witnessing

Implement:
- `AuthorityAdmissionLedger`;
- `AdmissionPerimeterEnforcementRecord`;
- `AuthorityKernelDecisionRecord`;
- `AuthorityKernelDecisionLedger`;
- `AuthorityApplicationRecord`;
- independent witness/quorum integration;
- rollback/fork lineage detection.

Primary existing surfaces:
- authoritative state ledger;
- execution/repository gateways;
- terminal authority/executor;
- remote/external side-effect paths.

Key rule: every apply must bind the exact current decision to the exact sink set and resulting authoritative post-state.

Production evidence dependency:
- per-sink IAM enforcement;
- external witness identity/control-domain separation;
- HSM/KMS signer/control facts.

## V24-I7 — Aggregate authority budgets

Implement:
- aggregation dimension catalog;
- complete aggregation-key derivation;
- `AggregateAuthorityBudgetLedger`;
- per-key records;
- `AggregateBudgetTransactionId`;
- persistent-effect/window semantics;
- deterministic unknown-outcome reconciliation.

Primary existing surfaces:
- authoritative state ledger transaction/idempotency primitives;
- external side-effect reconciliation patterns.

Key rule: do not choose a persistence topology until all keys and sinks participating in one atomic authority transition are mapped.

## V24-I8 — Generation migration and fencing

Implement:
- generation identity on authority-bearing records;
- `GenerationAuthorityObjectInventory`;
- `LegacyPredecessorCompletenessQualification`;
- `GenerationReadGuard`;
- generation fencing for cache/replica/read/apply paths;
- migration, rollback and reconciliation plan.

Key rule: absence of repository-visible cache/replica code is not evidence that production has none.

## V24-I9 — Apply-time integration

Only after I1–I8 prerequisites exist, integrate V24 enforcement into:
- governed execution decision;
- execution gateway;
- repository gateway;
- terminal authority;
- terminal executor;
- remote transport;
- credential/control-plane path;
- external side-effect gateway;
- runtime validator.

Required behavior:
- admission and completeness currentness revalidated at use/apply time;
- exact generation checked;
- exact kernel decision bound;
- endpoint precedence taken from compiled table;
- application record written only on qualifying apply;
- unknown outcomes reconciled without duplicate authority/effect.

## V24-I10 — Review, proof and audit integration

Implement:
- reviewer-facing completeness evidence;
- proof-view manifest materialization;
- redaction/applicability conformance;
- audit/dashboard/telemetry exposure without self-selected omission;
- preserved separation between external content and authenticated review execution.

No review path may make evidence self-authorizing.

## V24-I11 — Falsification and regression

Bind WDPC-431…506 to executable harnesses.

Execute:
- targeted negative/adversarial tests per slice;
- corresponding positive controls;
- affected inherited regression tests;
- compatibility/migration tests;
- required inherited WDPC-01…430 regression after V24 implementation is falsification-ready.

TESTING/FALSIFICATION review rule:
- manual independent review only;
- no reviewer API call may be represented as qualifying manual review;
- historical failures remain preserved;
- no test deletion/weakening to obtain green status.

## Cross-slice change-control requirements

Before each runtime implementation slice:
1. bind exact base commit/tree;
2. identify direct and transitive affected surfaces;
3. choose exactly one compatibility strategy for each changed contract/state surface;
4. identify existing tests to rerun;
5. preregister new negative and positive tests;
6. classify every intended changed path;
7. implement one coherent slice;
8. reconcile actual Git diff against intended impact;
9. run targeted and regression evidence;
10. run cleanliness/static checks supported by the repository;
11. mark unavailable checks `NOT_VERIFIED`;
12. only then declare the slice review-ready.

Allowed compatibility strategies:
- `BACKWARD_COMPATIBLE_ADDITIVE`;
- `VERSIONED_DUAL_READ_WRITE`;
- `EXPLICIT_MIGRATION_WITH_ROLLBACK_RECONCILIATION`;
- `GOVERNED_INTENTIONAL_BREAKING_TRANSITION`.

Implicit breaking changes are prohibited.

## Current next permitted action

After I0 exits cleanly, the next permitted runtime-development action is **V24-I1 — Normative control foundation**.

Do not jump directly to gateway/sink code before I1–I8 dependencies are established.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
