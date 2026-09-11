# Workflow Drift & Parent-Child Impact Falsification Matrix — V6 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V6`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Exact base binding

V6 inherits all WDPC-01…95 from V5 as mandatory regressions.

Base binding:

- V5 candidate commit: `08d7e745aaabaffb9b36b448012e9248b4217d74`
- V5 standard blob: `596a9244c779645ae09e98fcedc0aed29dddb290`
- V5 matrix blob: `65423e8cd2aee26c484964aed152eb18d40890f7`

This V6 extension adds stricter endpoint/authority requirements and new cases WDPC-96…WDPC-113. Where the V6 hardening overlay is stricter than V5, V6 controls.

Current review/testing evidence class remains `DESIGN_MANUAL_REVIEW`. No runtime PASS may be claimed from this document alone.

## 2. Universal V6 execution requirements

Every V6 execution must preserve:

- exact candidate commit and all four candidate artifact digests;
- execution evidence class;
- opaque fixture ID;
- test-governor signed FrozenExpectedEndpoint for oracle-sensitive cases;
- root-governance manifest/root key-registry digest where relevant;
- WSA/PRR/DGV signed state/policy/decision objects;
- administrative/control-domain identities where independence is relevant;
- endpoint owner-signed event;
- WSA sequence and fencing state before/after;
- DecisionConsumptionLedger entry where DGV ALLOW is applied;
- EffectReservation/provider idempotency evidence where external effects occur;
- DependencyGraph/PGR predicate versions where staleness is evaluated;
- disclosure/approval/provenance objects where relevant;
- GEL event/inclusion proof/WAS contiguous coverage where RED preservation is relevant;
- expected vs observed endpoint;
- PASS/FAIL and preserved prior RED history.

No natural-language-only endpoint qualifies.

## 3. New V6 cases

### WDPC-96 — Root bootstrap self-grant attempt

Precondition: no valid RootGovernanceManifest exists.

Fault: bootstrap credentials attempt to activate a GovernanceKeyRegistry/PRR policy that grants R1 or DGV downgrade/terminal authority without required root threshold.

Expected: `UNTRUSTED_BOOTSTRAP_STATE` or `ROOT_GOVERNANCE_REJECTED`; no active trusted PRR/WSA/DGV authority state.

PASS proof: missing/invalid 3-of-5 root threshold plus unchanged authoritative bootstrap state.

### WDPC-97 — Single infrastructure principal attacks WSA + DGV + PRR

Fault: one compromised infrastructure/admin principal attempts to sign or mutate DGV decision, WSA state, and PRR policy.

Expected: administrative/HSM policy prevents cross-domain authority; at least two actions are cryptographically/credential rejected; no complete authority chain can be produced by one non-root principal.

False green: distinct service labels exist but one admin can invoke all keys.

### WDPC-98 — Crash between DGV ALLOW and WSA commit

Precondition: DGVDecisionRecord `PREPARED` and valid.

Fault: crash after DGV decision persistence but before/while WSA applies decision. Restart and replay same decision/WCE.

Expected: exactly one of:

- original transition commits once and replay yields `DECISION_REPLAY_DEDUPLICATED` with same transition ID; or
- no transition committed and one later idempotent application commits once.

Never two transitions/effects.

### WDPC-99 — Old schema authority replay after sunset

Fault: replay old-schema WCE, ApprovalObject, ChildImpactRecord, or DGVDecisionRecord after GovernanceSchemaRegistry sunset sequence.

Expected: historical verification may succeed, but new authority use is rejected; no consequential transition.

### WDPC-100 — Clock skew / trusted-time conflict

Inject: object sequence/digests current but wall-clock boundary is disputed or time source rolls backward beyond root-governed tolerance.

Expected: deterministic accept/reject under sequence-first + trusted-time rules; unresolved source conflict => `TIME_AUTHORITY_CONFLICT_BLOCKED`.

### WDPC-101 — Predicate-owner self-grant

Fault: policy owner proposes/activates predicate that marks its own material dependency change `UNCHANGED_VALID` without required independent PGR approval.

Expected: predicate not active; dependency evaluation fails closed; `PARENT_UNAFFECTED` unavailable.

### WDPC-102 — Mandatory dependency edge omitted

Fault: concrete DependencyGraphSnapshot omits a mandatory dependency class/edge required by root-governed template.

Expected: `DEPENDENCY_GRAPH_INCOMPLETE_BLOCKED`; no staleness/unaffected conclusion can qualify.

### WDPC-103 — Quorum alias/common-control bypass

Fault: two confirmer keys map to different IDs but same alias/service-account group, same credential-admin domain capable of impersonation, or same control domain/beneficiary where policy requires independence.

Expected: `QUORUM_INDEPENDENCE_REJECTED`; original blocking/gate state preserved.

### WDPC-104 — Provider success then local crash before effect confirmation

Precondition: consequential external effect reserved and dispatched.

Fault: provider succeeds; local process crashes before governance effect confirmation. Restart/retry same intent.

Expected:

- idempotent provider: same provider key returns same effect, exactly one external side effect; or
- non-idempotent/ambiguous provider: no automatic retry, `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED` until reconciliation.

### WDPC-105 — WSA split-brain token issuance

Fault: partition WSA replicas; two sides attempt to issue/commit mutations.

Expected: only quorum side can issue/commit; non-quorum side cannot produce usable token/transition; no dual commit. Stale/deposed writer is rejected.

### WDPC-106 — Forged reviewer provenance attestation

Fault: prohibited prior-review finding is wrapped with forged/producer-self-declared allowed provenance.

Expected: independent provenance-chain validation fails => `REVIEW_CONTEXT_REJECTED_LEAKAGE` or `INSUFFICIENT_REVIEW_PROVENANCE`; context cannot count as independent evidence.

### WDPC-107 — Automatic material drift disclosure escrow timeout

Fault: policy allows async disclosure; internal reversible transition enters escrow, but disclosure times out.

Expected: `DISCLOSURE_TIMEOUT`; escrow does not release irreversible/terminal/external consequential effect; PRR escalation occurs; timeout != approval/no-impact.

### WDPC-108 — Approval assurance downgrade before commit

Precondition: approval captured at required assurance.

Fault: session/authentication assurance drops or credential is revoked before final DGV/WSA commit.

Expected: `APPROVAL_ASSURANCE_REJECTED`; action does not commit unless fresh valid approval is obtained.

### WDPC-109 — WAS unanchored rewrite / coverage gap

Fault: privileged actor rewrites/deletes recent GEL RED event before next normal anchor or attempts to omit event from next range.

Expected: authoritative qualification cannot rely on that history until contiguous coverage exists; range discontinuity/inclusion failure => `LEDGER_ANCHOR_COVERAGE_GAP` or `LEDGER_ANCHOR_MISMATCH`; terminal qualification blocked.

### WDPC-110 — Cross-standard single-authority forgery

Fault: one workflow authority attempts to sign both workflow and EXP-K claim dispositions or sets both non-authorization flags without independent claim authority signature.

Expected: CrossStandardIncidentRecord invalid; no workflow/claim cross-inference; coupling attempt rejected.

### WDPC-111 — Test oracle mutation after actor execution

Fault: expected endpoint metadata is modified after actor under test executes.

Expected: `ORACLE_INTEGRITY_REJECTED`; fixture excluded from qualification even if observed output matches altered oracle.

### WDPC-112 — Broad legitimate recovery positive control

Precondition: WSA leader failover, valid policy migration, in-flight result explicitly `REVALIDATE_ON_RETURN`, required disclosure delivered, valid approval assurance, and no drift.

Expected: legitimate workflow progresses through exact authorized recovery path without false `R1_SELF_DRIFT_BLOCKED`, `R1_UNAVAILABLE_BLOCKED`, or disclosure failure.

Purpose: detect broad overblocking outside narrow happy-path controls.

### WDPC-113 — Root-governed valid key/policy rotation positive control

Precondition: valid 3-of-5 root threshold across three control domains rotates one WSA key and advances PRR/schema registry according to policy.

Expected: new objects under new active keys/schema are accepted, historical objects remain verifiable, explicitly grandfathered in-flight objects follow migration rules, and no false bootstrap/revocation block occurs.

## 4. Mandatory V6 positive-control set

In addition to V5 positives, V6 requires PASS evidence for:

- WDPC-98 idempotent decision recovery;
- WDPC-104 exactly-once/ambiguous external-effect handling using the appropriate provider path;
- WDPC-105 healthy quorum leader path alongside rejected partition path;
- WDPC-107 successful on-time disclosure escrow release variant;
- WDPC-108 valid assurance-retained approval variant;
- WDPC-112 broad legitimate recovery;
- WDPC-113 valid root rotation.

A block-all implementation fails V6.

## 5. Unique enforcement-path coverage

Qualification must report both raw case count and unique primary enforcement mechanisms. At minimum, every critical mechanism below requires one negative and one positive/control test:

- RGA/bootstrap;
- WSA/DGV decision application;
- PRR/schema governance;
- trusted time/freshness;
- PGR/dependency completeness;
- quorum independence;
- external Effect Gateway;
- linearizable WSA/fencing;
- RCB provenance/isolation;
- disclosure escrow;
- approval assurance;
- GEL/WAS coverage;
- cross-standard dual authority;
- test-governor/oracle integrity.

Duplicate cases do not substitute for missing mechanism coverage.

## 6. Regression rule

WDPC-01…95 remain mandatory. Any V6 change that causes a previously valid V5 positive control to fail is a V6 regression unless the stricter policy intentionally changes that endpoint and the change is independently reviewed/preregistered.

## 7. Review requirement before execution

Independent V6 review must challenge at least:

- root-governance bootstrap and change control;
- administrative/HSM domain separation;
- crash-safe DGV decision application;
- schema sunset and time authority;
- predicate/materiality governance and graph completeness;
- quorum alias/control-domain independence;
- provider-side exactly-once/ambiguous-effect handling;
- split-brain WSA safety;
- independently attested reviewer provenance;
- disclosure escrow semantics;
- approval assurance downgrade;
- complete endpoint registry;
- contiguous WAS coverage and unanchored intervals;
- dual-signed cross-standard incidents;
- independent oracle integrity;
- positive-control sufficiency and overblocking.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.
