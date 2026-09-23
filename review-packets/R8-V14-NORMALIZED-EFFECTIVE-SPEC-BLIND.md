# R8 v14 — Normalized Effective Meta-Governance Specification

Status: **BLIND_REVIEW_SUBJECT — DESIGN_ONLY — NON_AUTHORITATIVE**
Authority effect: **NONE**

Purpose:
- present the currently intended effective R8 semantics once;
- eliminate co-effective historical overlays from the review surface;
- preserve traceability to immutable source designs;
- expose cross-mechanism dependencies for independent falsification.

This document does not replace the canonical v4-v14 source files. If this normalized view conflicts with a canonical source before NCG-1 closes, NCG-1 must fail and the conflict must be adjudicated before external review.

## 1. Trust and authority model

### NORM-001 — external trust boundary
Effective rule:
- T0/EBA/MTR/BTW/workload-attestation roots are explicit bounded trust assumptions.
- ordinary platform software cannot mint, replace, roll back, or weaken those roots.
- loss of lawful trust can block the platform permanently; no emergency weaker root is created.

Trace: v4 T0 model; v5/v6 MTR/BTW hardening; v7 MTR freshness; v8-v13 no weakening.

### NORM-002 — authority default
Effective rule:
- authority effect defaults to NONE;
- no candidate, review, test, packet, CI result, or model statement grants authority by itself;
- authority-bearing actions require the current effective governance state and exact qualifying evidence.

Trace: v4-v14 claim boundaries.

## 2. T0 / MTR / BTW

### NORM-003 — T0 manifests
Effective rule:
- T0 manifests are externally provisioned, generation-numbered, digest-bound, and successor-controlled.
- successor activation requires predecessor-authorized transition, atomic next-generation reservation, BTW consistency, and MTR activation.

Trace: v5 I001-I004; v6 MTR; v7 atomic T0 successor reservation; v8 authorized reservation ordering.

### NORM-004 — MTR freshness
Effective rule:
- authority-bearing use requires live challenge-bound MTR freshness;
- no stale cached-token fallback is allowed for authority;
- verifier/trust-domain/purpose/challenge binding and monotonic response state are required.

Trace: v7 MTRF-1; v8 MTRF-2 refinements.

### NORM-005 — BTW
Effective rule:
- BTW verification uses T0-pinned witness keys/policy and anti-rollback consistency;
- conflicting trusted roots/equivocation freeze affected authority paths.

Trace: v5/v6 BTW rules.

## 3. Identity, domain independence and revocation

### NORM-006 — canonical identity
Effective rule:
- authority identity resolves through canonical subject/controller/admin-domain records;
- aliases resolving to the same canonical subject count once for independence;
- domain diversity cannot be manufactured by aliasing.

Trace: v6 LineageGraph; v7 CanonicalSubjectRegistry.

### NORM-007 — ACTIVE-only quorum
Effective rule:
- only ACTIVE domains/credentials/controllers count toward required quorum/diversity at the relevant effective sequence;
- suspended/retired/revoked identities are non-voting.

Trace: v7 ACTIVE-only quorum.

### NORM-008 — revocation
Effective rule:
- revocation is append-only and sequence-bound;
- new authority use checks current committed revocation state;
- root/terminal-sensitive use additionally checks monotonic high-water protection;
- UNREVOKE does not retroactively validate the revoked interval.

Trace: v6/v7 revocation rules.

## 4. Genesis and configuration sequencers

### NORM-009 — GGS-3
Effective rule:
- one rollback-resistant genesis sequencer owns constitution namespace and bootstrap authorization consumption;
- committed namespace/authorization roots are monotonic and protected against rollback;
- configuration rotation uses the same barrier/state-transfer discipline as authority sequencers.

Trace: v6 GGS-1; v7 GGS-2; v8/v10/v11 GGS-3 STC/RBP integration.

### NORM-010 — LAS-3
Effective rule:
- LAS-3 is the sole authority-bearing sequencer;
- non-commutative authority state transitions use atomic StreamHeadMap compare-and-advance;
- rollback-resistant hard state preserves term/index/vote/head/idempotency state;
- configuration changes use joint consensus and exact activation index.

Trace: v6 LAS-2; v7 LAS-3; v9 formal version; v10 STC; v11/v12 RBP.

## 5. Rotation barrier and state transfer

### NORM-011 — rotation barrier
Effective rule:
- ROTATION_PREPARE commits barrier index B;
- authority-bearing writes covered by the rotating state are frozen after B;
- one barrier can serve at most one lawful rotation;
- abort permanently closes B; retry requires a new barrier.

Trace: v11 RBP-1; v12 RBP-2; v14 barrier taxonomy.

### NORM-012 — state transfer
Effective rule:
- STC binds the exact committed state at the barrier;
- old quorum certifies the snapshot; new quorum attests installation of the same snapshot;
- ENTER_JOINT and ACTIVATE bind that same STC and transition certificate;
- mismatch makes a joining replica non-voting and blocks rotation.

Trace: v10 STC-1; v11 STC-2/barrier close; v12 semantic-head equality.

## 6. Authority input execution environment

### NORM-013 — AIEP/AIG
Effective rule:
- authority evaluators run only under a qualified broker-only execution profile;
- direct ungoverned mutable env/config/db/network/file reads are prohibited;
- mutable/configurable authority inputs pass through AuthorityInputGateway;
- unqualified runtime profile has authority effect NONE.

Trace: v7 AIEP-1; v8 attested gateway.

## 7. Current semantic state

### NORM-014 — CSM-5
Effective rule:
- CSM-5 is the current authority-semantic bundle;
- it includes semantic entries, mappings, ANY permissions, AIM descriptors, ResolverPolicy reference, and CSM-bound supporting registries/rules;
- updates are LAS-governed authority events.

Trace: v10 CSM-3; v11 CSM-4; v12 CSM-5.

### NORM-015 — named semantic heads
Effective rule:
LASAuthorityStateRoot exposes named committed heads for:
- CSM;
- AIM;
- semantic ANY permission;
- AIM scope policy;
- ResolverPolicy;
- ResolverImplementationRegistry;
- GuardRegistry;
plus the inherited revocation/nonce/effect/configuration state.

Trace: v12/v13/v14 authority-state-root rules.

### NORM-016 — semantic_state_sequence
Effective rule:
- semantic_state_sequence is the current LAS-3 committed sequence fixing the semantic heads used for the authority decision;
- it is derived internally and never caller-selected for authority-bearing resolution;
- historical replay is separate and authority NONE.

Trace: v12 semantic_state_sequence; v14 explicit root field.

## 8. AIM-4 applicability

### NORM-017 — immutable AIM descriptors
Effective rule:
- AIM descriptors are append-only/versioned;
- source lineage, semantic class, scope policy, resolver policy and other authority-relevant changes require a successor descriptor under the required constitutional path.

Trace: v12 AIM-3; v13 AIM-4.

### NORM-018 — AIM candidate/Smax order
Effective rule:
1. select effective descriptors matching semantic_input_id/class and exact decision-scope components;
2. do **not** discard candidates because current AIM ANY permission is invalid;
3. derive specificity;
4. compute AIM_Smax over the full effective matching candidate set;
5. evaluate AIMScopePolicy validity at AIM_Smax;
6. invalid/narrowed/revoked permission -> AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED;
7. then apply lifecycle precedence;
8. no lower-specificity fallback after an AIM_Smax blocker.

Trace: v13 AIMApplicability-1 superseded by v14 AIMApplicability-2.

## 9. Resolver authorization and qualification

### NORM-019 — ResolverPolicy
Effective rule:
- ResolverPolicy is a machine-readable CSM-bound algorithm contract defining lineage start, candidate construction, specificity, lifecycle/error precedence, mapping traversal, replacement evaluation, ANY validation, fallback prohibition and conformance-suite identity.

Trace: v12 ResolverPolicy-1, v13/v14 extensions.

### NORM-020 — ResolverImplementationRegistry
Effective rule:
- exact active ResolverPolicy → implementation/runtime/workload/conformance tuple must match exactly one temporally eligible ACTIVE RIR record;
- conformance alone is not authorization.

Temporal eligibility:
`activation_sequence <= semantic_state_sequence`
and
`retirement_or_revocation_sequence == null || > semantic_state_sequence`.

Trace: v13 RIR-1; v14 RIR-2.

### NORM-021 — Resolver conformance freshness
Effective rule:
- exact implementation/runtime executes the exact bound conformance suite;
- evidence is invalidated by any bound policy/implementation/runtime/suite/registry change;
- evidence also obeys the record's explicit freshness profile;
- missing/failed/expired evidence leaves the resolver unqualified.

Trace: v13 RCS-1; v14 RCS-2.

## 10. Semantic resolution

### NORM-022 — Smax before lifecycle
Effective rule:
- within the active AIM-selected semantic lineage, CSRULE computes matching candidates and Smax before lifecycle filtering;
- lower-specificity fallback is prohibited after any Smax blocker.

Trace: v9 CSRULE-2 through v14 CSRULE-5 effective order.

### NORM-023 — ANY at semantic-entry level
Effective rule:
- current semantic ANY permission is checked at Smax from the same current CSM snapshot;
- invalid/missing/narrowed/revoked permission blocks with SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED even if lifecycle bookkeeping did not mark entries.

Trace: v12 resolver-time ANY validation.

### NORM-024 — revoked dominance
Effective rule:
- any applicable REVOKED entry at Smax suspends ordinary ACTIVE selection;
- each revoked branch requires one unique valid linked successor/replacement discharge path;
- zero path -> SEMANTIC_SCOPE_REVOKED;
- multiple non-equivalent paths -> SEMANTIC_SUCCESSOR_CONFLICT;
- only after all revoked blockers are discharged are resulting successors compared with genuine ACTIVE peers.

Trace: v13 CSRULE-5.

### NORM-025 — semantic-result equivalence
Effective rule:
- every resolved semantic result is normalized to `{semantic_input_id, semantic_class, terminal_semantic_entry_id, terminal_rule_digest, terminal_lineage_id, effective_scope_tuple_digest}`;
- each field is derived from the final selected entry and final authorized effective scope;
- equality means identical GCP-1 semantic_result_digest only;
- resolution-path evidence is preserved separately;
- implementation-local equivalence is forbidden.

Trace: v14 SREP-1.

## 11. Scope and lineage transitions

### NORM-026 — lineage mapping
Effective rule:
- cross-lineage transition requires an explicit constitutional SemanticLineageMapping;
- no implicit lineage fallback.

Trace: v10/v11 lineage mapping rules.

### NORM-027 — scope replacement
Effective rule:
- scope replacement uses the total SRTT-3 machine-readable decision table;
- exact replacement requires SAME exact destination;
- mapped SAME/NARROWER replacement may be allowed;
- BROADER requires SEMANTIC_SCOPE_EXPANSION_AMENDMENT plus decision inside the AuthorizedExpansionDomain;
- invalid ANY, ineffective mapping, invalid lineage mapping, or unauthorized expansion cannot unblock revoked scope.

Trace: v13 SRTT-2, normalized by v14 SRTT-3.

## 12. Review-visible materiality and independent review

### NORM-028 — review materiality
Effective rule:
- every reviewer-visible semantic field relied on for a decision is bound into the review packet;
- unknown reviewer influence defaults to semantic/material.

Trace: v6/v7 ReviewPresentationSchema lineage.

### NORM-029 — reviewer authenticity
Effective rule:
- required human review is signed/attested and independent under canonical identity rules;
- model/provider review is bounded by provider qualification/isolation assumptions and cannot silently replace required human review.

Trace: v6 Channel H/X and inherited review rules.

## 13. Decision read set, time, seal and commit

### NORM-030 — AuthorityReadSet
Effective rule:
- every mutable authority input consumed by a predicate is registered and captured with exact source/head/value digest;
- unregistered or unsealed input blocks authority.

Trace: v6 AuthorityReadSet; v7 AIM/AIEP.

### NORM-031 — DecisionPresealContext
Effective rule:
preseal binds:
- candidate/action/scope;
- governance snapshot;
- AuthorityReadSet;
- semantic_state_sequence;
- CSM/AIM/ANY/ResolverPolicy heads;
- RIR record/head;
- resolver implementation/runtime/conformance identity;
- revocation/runtime/workload state;
- effect class where relevant.

Trace: v8 DPS-2, v12 DPS-v3, v13/v14 RIR binding.

### NORM-032 — time
Effective rule:
- time proof uses a single-use nonce bound to the decision preseal context;
- source status must be valid at sequence;
- replay/stale proof is rejected.

Trace: v6/v7 time/NonceLedger rules.

### NORM-033 — VerifiedStateSeal / COMMIT_WITH_SEAL
Effective rule:
- final seal binds the full authority read set and semantic/runtime/time/revocation state;
- consequential commit atomically rechecks current authority heads;
- any state change -> STATE_CHANGED and no effect intent.

Trace: v6-v8 seal/commit rules.

## 14. External effects

### NORM-034 — intent != completion
Effective rule:
- COMMIT_WITH_SEAL may commit an EffectIntent only;
- external effect success requires qualified idempotent executor plus provider-specific reconciliation;
- ambiguous result remains UNCERTAIN, never fabricated success.

Trace: v7 EESM-1; v8 executor revocation; v9 reconciler independence.

## 15. Evidence producers and transitions

### NORM-035 — evidence strength
Effective rule:
- strong evidence requires qualified producer/execution identity;
- byte copying or rewrapping does not upgrade evidence class;
- producer revocation/compromise has explicit temporal validity and reevaluation semantics.

Trace: v5-v7 QEP rules.

### NORM-036 — evidence transition
Effective rule:
- evidence-class transitions are closed and governed;
- missing/contradictory mandatory evidence blocks promotion.

Trace: inherited EXP-J and R8 evidence transition controls.

## 16. Tenant/migration

### NORM-037 — stable authority scope
Effective rule:
- authority-bearing object identity is constitution/tenant scoped;
- migration requires exact object map, scope comparison, destination-policy freshness and requalification;
- cross-constitution import carries historical/external evidence only, not authority.

Trace: v5-v8 tenant migration rules.

## 17. Recovery/trust loss

### NORM-038 — recovery
Effective rule:
- recovery uses predeclared triggers, exact recovery context, single-use nonce, lawful quorum and current trust state;
- old approvals/context cannot be replayed.

Trace: v6/v7 recovery rules.

### NORM-039 — permanent trust loss
Effective rule:
- unavailable lawful trust path blocks authority;
- TRUST_DOMAIN_UNRECOVERABLE may be authoritatively recorded only if a still-lawful recovery quorum can do so;
- otherwise the domain remains blocked indefinitely;
- a new constitution inherits no authority.

Trace: v6/v7 trust-loss rules.

## 18. Guard authority

### NORM-040 — GuardRegistry
Effective rule:
- GuardRegistry is the sole guard-ID/mechanism/positive/negative/FP identity authority;
- legacy manual consolidated guard tables are display/history artifacts and may not override current registry;
- exactly one ACTIVE record per required guard ID.

Trace: v13 GuardRegistry-1; v14 continuation.

## 19. Blind review projection

### NORM-041 — authoritative review surface
Effective rule:
- canonical blind TXT is authoritative;
- PDF is optional convenience only;
- predecessor review outcomes/adjudication metadata are removed by deterministic BSP grammar;
- current candidate status and semantic test literals remain.

Trace: v12 BSP-2; v13 BSP-3; v14 BSP-4.

### NORM-042 — embedded proof manifests
Effective rule:
- ProjectionManifest and GuardOmissionManifest are embedded in the authoritative review TXT;
- omission of legacy guard tables must prove all guard IDs remain in GuardRegistry and unique case/invariant semantics remain in the normalized spec.

Trace: v14.

## 20. NCG-1 closure rule

### NORM-043 — pre-review normalization gate
Effective rule:
No fresh independent design-review packet may be frozen until:
- normalized effective spec is complete;
- dependency/evaluation/ownership matrices are complete;
- cross-mechanism adversarial corpus has no unresolved false-green path;
- GuardRegistry is contiguous and unique;
- review projection is reproducible;
- unresolved material contradiction count = 0.


Trace: v14 NCG-1.
