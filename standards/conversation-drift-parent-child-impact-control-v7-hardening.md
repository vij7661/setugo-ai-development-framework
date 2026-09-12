# Workflow Drift and Parent-Child Impact Control — V7 Hardening Overlay

Status: **PROPOSED V7 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Exact base binding

V7 is an additive hardening layer over the exact V6 candidate:

- V6 candidate commit: `a5958f1877e0971d8e95d1fddfa4292e26062683`
- V5 standard blob: `596a9244c779645ae09e98fcedc0aed29dddb290`
- V5 matrix blob: `65423e8cd2aee26c484964aed152eb18d40890f7`
- V6 hardening blob: `02365ffec8afd54d6f1c7e3ad50f1288b69b27b3`
- V6 matrix-extension blob: `8c0c0e17298829b5ab4c638f456a5c45d8f71099`

V7 does not rewrite those artifacts. The separately versioned V7 active-clause map defines exactly which clauses remain active, are narrowed, or are superseded.

V7 remains design/preregistered falsification work only. It is not runtime implementation evidence.

## 2. Root-guardian independence attestation

A root threshold is valid only if guardian independence is itself proven.

The Root Governance Authority (`RGA`) maintains a threshold-signed `RootGuardianIndependenceSnapshot` binding each guardian to:

- guardian principal/key ID;
- human/service legal/controller identity;
- `control_domain_id`;
- cloud/root-account ownership domain;
- HSM/KMS administration domain;
- identity-provider administration domain;
- credential-recovery administration domain;
- beneficial-owner/sponsoring-authority ID;
- alias/service-account group;
- activation/revocation sequence;
- independent attestation sources/digests;
- predecessor snapshot digest;
- root threshold signatures.

A root threshold is invalid if enough participating guardians to satisfy the threshold are controlled by any common cloud/org root administrator, common HSM/KMS administrator, common identity administrator, common credential-recovery authority, or same alias/service-account group.

Root ceremonies and rotations MUST validate the independence snapshot atomically at the final root-manifest commit.

Guardian aliases, delegated service accounts, or recoverable credentials count as the same control authority when one administrator can assume multiple guardian identities.

Failure emits `ROOT_GOVERNANCE_REJECTED` with `reason_code=ROOT_GUARDIAN_INDEPENDENCE_FAILED`.

## 3. Root-governed registries and monotonic change control

The following registries are root-governed, append-only, monotonic, and cannot be changed by runtime WSA/DGV/PRR/RCB/DR/GEL/WAS principals:

- GovernanceKeyRegistry;
- GovernanceSchemaRegistry;
- EndpointSchemaRegistry;
- PredicateGovernanceRegistry;
- DependencyClassTemplateRegistry;
- PrincipalIndependenceRegistry;
- ProvenanceAuthorityRegistry;
- TestGovernorAuthorityRegistry;
- CrossStandardAuthorityRegistry;
- TrustedTimeAuthorityRegistry;
- ProviderCapabilityRegistry.

Every registry update requires the root-governed threshold defined for that registry class and includes predecessor digest, activation sequence, and rollback-prohibited monotonic version.

A registry version lower than the latest root-accepted version can be historically verified but cannot regain authority for new consequential use.

## 4. DGV decision application: final-authority revalidation

WSA `ApplyDecision(decision_id)` MUST revalidate authority at the actual state-commit boundary, even when the DGV decision was valid when prepared.

Before commit WSA MUST verify:

- DGV key still active and not revoked;
- DGV service role still authorized;
- actor role/key still active;
- bound PRR policy still active or explicitly grandfathered;
- schema versions still authority-valid;
- approval/disclosure/session prerequisites still valid;
- decision not expired/superseded;
- exact candidate/checkpoint/pre-state/action digest unchanged;
- quorum/independence facts still current where applicable;
- decision nonce not already consumed.

A prepared decision whose authority changed is rejected as `DECISION_AUTHORITY_REVOKED_BLOCKED` and cannot be applied.

### 4.1 Prepared-decision expiry and reconciliation

Every `DGVDecisionRecord` has `expires_at_sequence` and, if time-bounded, `expires_at_time`.

A never-applied `PREPARED` decision becomes `EXPIRED` or `SUPERSEDED` deterministically when:

- its expiry boundary is crossed;
- its pre-state is superseded;
- its policy/key/role authority is revoked;
- its schema sunsets;
- a conflicting committed transition invalidates its preconditions.

Reconciliation is idempotent. Expiry never creates permission to regenerate the same decision without a fresh WCE/evaluation.

## 5. Provider capability qualification and external-effect safety

Provider claims are not authority.

The root-governed `ProviderCapabilityRegistry` stores signed qualification records for consequential providers/operations, including:

- provider/operation ID;
- supported idempotency mechanism;
- scope and semantics of provider idempotency key;
- provider effect-identity guarantee;
- retry behavior;
- duplicate suppression window;
- evidence/test corpus digest;
- qualification issuer(s);
- activation/expiry/revocation sequence;
- allowed execution mode `IDEMPOTENT_RETRY | AT_MOST_ONCE_ONLY | MANUAL_RECONCILIATION_ONLY`.

If provider idempotency is missing, expired, contradictory, or unproven, the Effect Gateway MUST use at-most-once dispatch and enter `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED` after an ambiguous post-dispatch failure.

### 5.1 Reservation-before-dispatch invariant

A durable `EffectReservation` MUST be quorum/transactionally committed before network dispatch. A dispatcher cannot send a consequential provider request without a current reservation ID and fencing token.

### 5.2 Gateway split-brain protection

Effect Gateway dispatch authority is single-writer/linearizable per effect scope. Dispatchers must validate the current fencing token. A partitioned/deposed gateway cannot dispatch a second provider effect.

### 5.3 Unknown-outcome override

Manual/operator resolution of `OUTCOME_UNKNOWN_BLOCKED` requires a signed `ExternalEffectReconciliationDecision` authorized by PRR with independent quorum for operations capable of duplicate irreversible effects. An operator cannot simply relabel the outcome as safe.

## 6. End-to-end fencing enforcement

WSA fencing is insufficient unless every consequential downstream effector enforces it.

Each consequential effector MUST either:

1. validate the current WSA-issued fencing token and exact pre-state/action binding itself; or
2. be reachable only through a WSA/Effect-Gateway mediation layer that validates them before the effect.

A stale/deposed writer request without current fencing proof MUST fail before the downstream effect.

PRR registers each effect class with `fencing_enforcement_mode` and the accountable enforcement component.

## 7. Authoritative event completeness from WSA to GEL to WAS

Every consequential WSA commit produces a monotonically sequenced `AuthoritativeTransitionCommitment` in the same consensus/transactional boundary as state mutation.

Each commitment contains:

- authoritative sequence;
- transition ID;
- pre/post-state digests;
- endpoint/event type;
- outbox/GEL payload digest;
- predecessor commitment digest.

GEL may only append events matching these commitments and may not introduce an authority-bearing event without a matching commitment where the endpoint class requires WSA authority.

WAS verifies contiguous inclusion of all authoritative commitments from a root-governed `trusted_history_start_sequence` through the qualification boundary.

Qualification fails if:

- an authoritative commitment lacks a GEL event;
- a GEL authority event lacks its required commitment;
- sequence numbers duplicate or overlap;
- anchor ranges overlap inconsistently or contain gaps;
- witness history rolls back;
- an event has no exactly-one-range inclusion proof.

Failure emits `LEDGER_ANCHOR_COVERAGE_GAP`, `LEDGER_ANCHOR_MISMATCH`, or `STATE_LEDGER_DIVERGENCE_BLOCKED` as appropriate.

## 8. PGR bootstrap audit and predicate falsification governance

The PredicateGovernanceRegistry (`PGR`) and dependency-class templates cannot self-certify completeness.

Before any predicate/template may support `PARENT_UNAFFECTED`, a signed `PredicateBootstrapAudit` is required from a root-governed audit authority separate from the proposing policy owner and workflow beneficiary.

The audit binds:

- predicate/template versions/digests;
- domain dependency inventory digest;
- mandatory dependency classes;
- omitted-edge adversarial corpus;
- false-unaffected corpus;
- property/fixpoint/cycle test results;
- reviewer/audit principal independence;
- disposition `QUALIFIED_FOR_UNAFFECTED | REJECTED | INSUFFICIENT`.

A predicate/template lacking a current qualifying audit cannot produce `UNCHANGED_VALID` for parent-progression authority; output is `INSUFFICIENT_DEPENDENCY_EVIDENCE`.

Template migration requires re-running impact analysis against previously accepted `PARENT_UNAFFECTED` decisions whose validity depended on changed classes/predicates.

## 9. Principal-independence final recheck

`PrincipalIndependenceRegistry` is root-governed under Section 3.

At final DGV/WSA commit for quorum-dependent decisions, independence is re-evaluated from the latest active snapshot.

Quorum fails when any threshold-satisfying subset shares a credential-admin authority capable of impersonating multiple confirmers, common control domain prohibited by policy, alias group, or disallowed beneficial-owner relation.

Stale independence metadata cannot grandfather a gate-removing decision unless an exact root-governed grandfather rule exists.

## 10. Irreversible-effect taxonomy and emergency exceptions

PRR maintains a root-approved `ConsequenceClassRegistry` classifying actions as:

- `READ_ONLY`
- `REVERSIBLE_INTERNAL`
- `IRREVERSIBLE_INTERNAL`
- `EXTERNAL_CONSEQUENTIAL`
- `TERMINAL_AUTHORITY`

Disclosure escrow may precede delivery only for `REVERSIBLE_INTERNAL` bookkeeping explicitly allowed by policy.

`IRREVERSIBLE_INTERNAL`, `EXTERNAL_CONSEQUENTIAL`, and `TERMINAL_AUTHORITY` actions cannot be released from material-drift escrow before required delivery.

Emergency exceptions require a root-governed `EmergencyExceptionPolicy` naming the exact action class, triggering condition, maximum duration, approving authority/quorum, audit obligations, and forbidden uses. A generic emergency flag is invalid.

## 11. Approval authentication freshness

Approval assurance is evaluated from the current authentication event, not the historical recorded level alone.

The authentication service emits signed `AuthenticationAssuranceSnapshot` objects binding principal, session, assurance level, authentication method, revocation state, compromise state, issued/expiry sequence/time, and predecessor digest.

DGV/WSA final commit MUST load a current qualifying assurance snapshot. Stale, revoked, compromised, or downgraded assurance produces `APPROVAL_ASSURANCE_REJECTED`.

## 12. Cross-standard administrative separation

`WorkflowDispositionAuthority` and `ClaimEvidenceDispositionAuthority` are separately authorized in the root-governed `CrossStandardAuthorityRegistry`.

They MUST differ in:

- service principal;
- signing key;
- administrative domain;
- credential-admin domain;
- authority policy lineage.

No single administrator may invoke both disposition keys. The linker/GEL cannot synthesize either signature.

Any shared-domain or single-authority attempt emits `CROSS_STANDARD_AUTHORITY_COUPLING_REJECTED`.

Workflow predicates may consume claim state only through a separately registered policy transition that explicitly declares the claim-status dependency; claim status alone never authorizes workflow progression.

## 13. Trusted-time hardening

TrustedTimeAuthority is root-governed. When multiple time sources are configured, PRR defines quorum/median rules and maximum skew.

For time-dependent authority:

- sequence/digest freshness remains primary;
- time-source disagreement beyond root maximum yields `TIME_AUTHORITY_CONFLICT_BLOCKED`;
- local host clock alone is never sufficient;
- time rollback cannot extend an expired authority object.

## 14. Provenance-authority hardening

The provenance service is root-governed through `ProvenanceAuthorityRegistry` and has a separate administrative domain from reviewer/worker producers.

A `SourceProvenanceAttestation` is valid only if:

- ingestion occurred through an authorized ingestion path;
- source bytes/digest were captured before transformation;
- source origin identity is independently authenticated where possible;
- transformation chain is recorded;
- reviewer/worker producer cannot sign the provenance attestation for its own output;
- attestation key is active and independently administered.

For independent review contexts, RCB additionally applies an allowed-content manifest. Substantive findings from other reviewers remain prohibited even if wrapped in syntactically allowed metadata.

A root-governed side-channel test corpus covers timing, completion count, ordering, provider identity, file names, payload length buckets, fixture naming, and metadata aliases.

## 15. Endpoint, evidence-class, and test-governor authority

`EndpointSchemaRegistry`, evidence-class definitions, and TestGovernorAuthorityRegistry are root-governed and append-only.

### 15.1 Evidence-class record

Every test/review result carries a test-governor-signed `EvidenceClassRecord` binding:

- candidate revision;
- fixture/run ID;
- evidence class;
- acquisition method;
- prohibited upgrade classes;
- issuer authority;
- predecessor digest.

`DESIGN_MANUAL_REVIEW` cannot be reclassified post hoc as runtime evidence.

### 15.2 Oracle immutability

A `FrozenExpectedEndpoint` becomes immutable at actor-start sequence. Any later change, including a root-governance change, invalidates that run as `ORACLE_INTEGRITY_REJECTED`; no override can restore the run.

The test governor authority is bootstrapped/root-governed independently from the runtime implementation under test.

## 16. Explicit active-clause map

The V7 candidate MUST include `standards/conversation-drift-parent-child-v7-active-clause-map.md`.

That artifact enumerates V5 and V6 sections as:

- `ACTIVE_UNCHANGED`
- `ACTIVE_NARROWED_BY_V6`
- `ACTIVE_NARROWED_BY_V7`
- `SUPERSEDED`
- `REFERENCE_ONLY`

No reviewer or runtime implementation may choose a more permissive interpretation when the map identifies a narrowing overlay.

An unmapped normative clause is `COMPOSITE_PRECEDENCE_AMBIGUOUS` and blocks design freeze.

## 17. Minimum unique-enforcement-path coverage

Before design freeze, every Critical/High mechanism category in the active candidate requires at least:

- one adversarial negative fixture;
- one valid positive fixture;
- one recovery/failure-transition fixture when the mechanism has a recovery path;
- owner-signed post-hoc evidence requirements;
- no unresolved RED for the mechanism.

The qualification report MUST state `unique_primary_mechanisms_total`, `unique_primary_mechanisms_covered`, and per-mechanism positive/negative/recovery coverage.

Raw case count cannot substitute for missing mechanism coverage.

## 18. V7 regression obligation

WDPC-01…113 remain mandatory regressions under the V7 active-clause map. V7 adds WDPC-114 onward.

Any stricter V7 behavior that changes an earlier expected endpoint must be explicitly mapped and preregistered before execution.

## 19. Current testing rule

Current external review remains `DESIGN_MANUAL_REVIEW` only. No external reviewer/model API output is qualifying manual review evidence.

AI-generated reviewer output may be retained as non-authoritative engineering feedback, but it cannot satisfy the independent manual-review gate.

## 20. Freeze condition

V7 MUST NOT be frozen for execution until:

1. V5 base, V6 overlay/extension, V7 overlay/extension, and active-clause map are reviewed as one exact composite candidate;
2. every normative clause is mapped;
3. WDPC-01…113 remain mandatory regressions;
4. V7 new cases are preregistered;
5. no unresolved Critical/High design finding remains under the governing review policy.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
