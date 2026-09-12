# Workflow Drift & Parent-Child Impact Falsification Matrix — V7 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V7`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Composite binding

V7 inherits WDPC-01…113 as mandatory regressions under the V7 active-clause map.

Base candidate:

- V6 candidate commit: `a5958f1877e0971d8e95d1fddfa4292e26062683`
- V5 standard blob: `596a9244c779645ae09e98fcedc0aed29dddb290`
- V5 matrix blob: `65423e8cd2aee26c484964aed152eb18d40890f7`
- V6 hardening blob: `02365ffec8afd54d6f1c7e3ad50f1288b69b27b3`
- V6 extension blob: `8c0c0e17298829b5ab4c638f456a5c45d8f71099`

V7 adds WDPC-114…135. Current review evidence class remains `DESIGN_MANUAL_REVIEW`; no runtime PASS may be inferred from this design alone.

## 2. Universal V7 PASS evidence

Every executed V7 case requires, where applicable:

- exact composite candidate revision and all active artifact digests;
- active-clause-map digest;
- signed root/registry snapshot IDs and versions;
- actor/principal/control/admin/credential domains;
- WSA/DGV/PRR state and decision records;
- final-commit authority revalidation result;
- fencing/effect reservation/provider capability evidence;
- PGR/bootstrap audit/dependency template evidence;
- provenance/authentication/disclosure/approval evidence;
- authoritative transition commitment/GEL/WAS inclusion evidence;
- test-governor signed EvidenceClassRecord and FrozenExpectedEndpoint;
- expected vs observed endpoint;
- preserved RED history.

A prose label, reviewer statement, or unsigned status cannot satisfy an endpoint.

## 3. New V7 cases

### WDPC-114 — Root guardian alias/common-cloud-root collusion

Fault: three nominal guardians use distinct keys/control-domain labels but one cloud/org root, HSM admin, identity admin, recovery admin, or alias controller can assume enough identities to satisfy 3-of-5.

Expected: final root-ceremony independence validation fails with `ROOT_GOVERNANCE_REJECTED` / `ROOT_GUARDIAN_INDEPENDENCE_FAILED`; no new RootGovernanceManifest activates.

Positive variant: three genuinely independent control/admin domains satisfy the threshold and root rotation succeeds.

### WDPC-115 — Provenance authority compromise / forged ingestion origin

Fault: producer or compromised provenance path signs an attestation claiming prohibited prior-review content originated from an allowed source.

Expected: root-governed provenance-chain/authenticated-ingestion validation fails as `INSUFFICIENT_REVIEW_PROVENANCE` or `REVIEW_CONTEXT_REJECTED_LEAKAGE`; contaminated context cannot qualify independent review.

Positive variant: allowed artifact captured through independent ingestion path produces a valid attestation and `REVIEW_CONTEXT_DELIVERED`.

### WDPC-116 — Downstream effector ignores stale fencing token

Fault: partitioned/deposed writer sends a consequential downstream command with a stale fencing token to an effector that would otherwise accept it.

Expected: effect is rejected by the effector or WSA-backed mediation layer before side effect. Any actual side effect is FAIL even if WSA later rejects the state transition.

### WDPC-117 — Schema-registry migration replay/downgrade

Fault: replay an older root-signed GovernanceSchemaRegistry snapshot or migration object after a newer monotonic version/sunset is active.

Expected: historical verification only; new authority use rejected. Registry version cannot roll back; dependent WCE/Approval/Impact/Decision objects under sunset schema cannot regain authority.

### WDPC-118 — Trusted-time source compromise/disagreement

Fault: one trusted-time source rolls backward or reports a time outside root-governed skew while other source/quorum evidence disagrees.

Expected: sequence/digest freshness still applies; any time-dependent authority enters `TIME_AUTHORITY_CONFLICT_BLOCKED` unless the registered quorum rule yields a deterministic valid time.

Positive variant: bounded permitted skew with valid quorum produces deterministic acceptance.

### WDPC-119 — Independent falsification of permissive predicate logic

Fault: a PGR predicate has valid signatures but its adversarial corpus demonstrates a material dependency can be falsely classified `UNCHANGED_VALID`.

Expected: PredicateBootstrapAudit is `REJECTED`/`INSUFFICIENT`; predicate cannot support `PARENT_UNAFFECTED`; dependent conclusion fails closed.

Positive variant: independently audited predicate passes required corpus and may be used.

### WDPC-120 — Mandatory dependency-class omission at bootstrap

Fault: initial dependency-class template omits a known material class before any concrete graph exists.

Expected: independent bootstrap audit detects omission; template cannot activate for `PARENT_UNAFFECTED`; later graph evaluation emits `DEPENDENCY_GRAPH_INCOMPLETE_BLOCKED`.

### WDPC-121 — Quorum credential-admin impersonation

Fault: two confirmer identities/keys appear independent but one credential-admin or recovery authority can impersonate both.

Expected: final PrincipalIndependenceRegistry check yields `QUORUM_INDEPENDENCE_REJECTED`; mandatory gate remains.

Positive variant: confirmers have independent credential-admin/control domains and valid quorum succeeds.

### WDPC-122 — Provider falsely claims idempotency

Fault: provider advertises idempotency but independent ProviderCapabilityRegistry evidence is absent/expired/contradictory; ambiguous post-dispatch crash occurs.

Expected: gateway treats operation as non-qualified idempotency and does not auto-retry; enters `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED` until reconciliation.

### WDPC-123 — Dispatch attempted before durable EffectReservation

Fault: dispatcher sends consequential provider request before reservation commit or with reservation not visible in authoritative effect state.

Expected: dispatch gateway rejects before network side effect; no provider call/effect occurs.

### WDPC-124 — Split-brain Effect Gateway duplicate dispatch

Fault: partition creates two gateway writers for same intent/reservation.

Expected: only quorum/current fenced dispatcher may send; deposed side cannot dispatch. Exactly one provider-side effect opportunity exists.

### WDPC-125 — Reviewer artifact-content leakage despite clean metadata

Fault: metadata/provenance fields are syntactically clean, but allowed artifact payload includes substantive prior-review findings.

Expected: allowed-content manifest/origin policy rejects payload as `REVIEW_CONTEXT_REJECTED_LEAKAGE`; reviewer independence ineligible.

### WDPC-126 — Emergency exception becomes general bypass

Fault: material disclosure escrow times out; actor invokes generic emergency/safety flag to release terminal or external effect not named in active EmergencyExceptionPolicy.

Expected: release rejected; exact action class/trigger/quorum/duration must match root-governed policy. Timeout remains blocked/escalated.

Positive variant: exact registered emergency action class under valid trigger/quorum executes only within declared scope and remains audited.

### WDPC-127 — EndpointSchemaRegistry mutation to legalize bad outcome

Fault: after a failing run, actor attempts to add/change endpoint schema or reason code so observed invalid outcome appears valid.

Expected: runtime actor cannot mutate root-governed registry; post-run registry change cannot retroactively qualify run; run remains FAIL/INSUFFICIENT.

### WDPC-128 — Evidence-class metadata forgery/reclassification

Fault: `DESIGN_MANUAL_REVIEW` result is relabeled `RUNTIME_IMPLEMENTATION` by actor/storage mutation.

Expected: test-governor signed EvidenceClassRecord mismatch detected; runtime qualification remains `INSUFFICIENT_EVIDENCE_FOR_RUNTIME_QUALIFICATION`.

### WDPC-129 — Authoritative transition outside GEL commitment sequence

Fault: WSA state changes consequentially without a matching AuthoritativeTransitionCommitment/GEL event.

Expected: recovery/qualification detects gap as `STATE_LEDGER_DIVERGENCE_BLOCKED` or `LEDGER_ANCHOR_COVERAGE_GAP`; transition cannot support terminal qualification.

### WDPC-130 — Privileged actor races/replaces event before WAS anchor

Fault: after WSA commitment but before WAS anchor, privileged actor removes/replaces GEL event and tries to anchor altered range.

Expected: WSA commitment digest/sequence and contiguous coverage disagree; anchor rejected with coverage/mismatch event; altered history cannot qualify.

### WDPC-131 — Witness rollback/overlap/duplicate sequence

Fault: witness store serves older anchor head, overlapping inconsistent ranges, duplicate event sequence, or gap.

Expected: verifier rejects as `LEDGER_ANCHOR_COVERAGE_GAP`/`LEDGER_ANCHOR_MISMATCH`; terminal authority blocked.

Positive variant: one contiguous non-overlapping chain from trusted start through qualification boundary verifies.

### WDPC-132 — One administrative domain controls both cross-standard authorities

Fault: WorkflowDispositionAuthority and ClaimEvidenceDispositionAuthority use different service IDs/keys but same admin or credential-admin domain.

Expected: CrossStandardAuthorityRegistry independence check fails; `CROSS_STANDARD_AUTHORITY_COUPLING_REJECTED`; neither disposition can authorize the other.

### WDPC-133 — Test-governor bootstrap/authority compromise

Fault: runtime implementation or same admin domain attempts to install/change test-governor key, oracle storage, or EvidenceClass authority.

Expected: root-governed TestGovernorAuthorityRegistry rejects unqualified change; run cannot qualify if independence cannot be proven.

Positive variant: independently governed test authority rotates correctly without exposing oracle to actor.

### WDPC-134 — Oracle mutation after actor start

Fault: any authority, including root governance, changes FrozenExpectedEndpoint after actor-start sequence.

Expected: run permanently invalidated as `ORACLE_INTEGRITY_REJECTED`; no override/re-review can convert that run to PASS. A new fixture/run is required.

### WDPC-135 — Minimum unique-enforcement-path coverage gate

Fault: qualification attempt has high raw case count but lacks required positive/negative/recovery coverage for one or more critical mechanisms.

Expected: design/execution freeze denied; report identifies uncovered mechanism IDs. Duplicate cases cannot satisfy the missing path.

Positive variant: every critical/high active mechanism has the required coverage triplet where applicable and no unresolved RED.

## 4. Revised V7 constraints on earlier cases

The following prior cases remain mandatory but must be evaluated under V7 rules:

- WDPC-04/05/08/64/75/88/101/102: require current PredicateBootstrapAudit and dependency-class completeness proof.
- WDPC-17/37/70/81/91/105: downstream effectors must enforce fencing, not only WSA.
- WDPC-32/38/92/104: ProviderCapabilityRegistry + reservation-before-dispatch + gateway single-writer rules apply.
- WDPC-43/54/61/83/103: final PrincipalIndependenceRegistry recheck applies.
- WDPC-52/79/107: irreversible/external/terminal effects cannot leave material-drift escrow before required disclosure.
- WDPC-59/73/111: TestGovernorAuthorityRegistry and immutable FrozenExpectedEndpoint rules apply.
- WDPC-68/78/106: root-governed independent provenance plus content/side-channel rules apply.
- WDPC-84: EndpointSchemaRegistry itself must be root-governed and active at run freeze.
- WDPC-85: signed EvidenceClassRecord applies.
- WDPC-94/109: WSA commitment -> GEL -> WAS contiguous completeness proof applies.
- WDPC-96/113: root guardian independence proof applies.
- WDPC-98: ApplyDecision final authority/revocation/schema/session revalidation applies.
- WDPC-99: monotonic root-governed schema registry applies.
- WDPC-100: root-governed trusted-time quorum applies.
- WDPC-108: current AuthenticationAssuranceSnapshot at final commit applies.
- WDPC-110: cross-standard authorities must also be administratively independent.

## 5. V7 positive-control suite

V7 cannot qualify by blocking everything. In addition to all prior positives, execute successful variants for:

- independent root guardian threshold/rotation;
- DGV PREPARED -> WSA commit with unchanged authority and idempotent replay;
- independently qualified provider idempotent retry;
- non-idempotent provider deterministic reconciliation without duplicate effect;
- healthy WSA/gateway leader failover with downstream fencing;
- independently audited predicate and complete dependency graph;
- independent confirmer quorum;
- clean provenance/context delivery;
- material automatic drift disclosure delivered then escrow release;
- current high-assurance approval at commit;
- monotonic schema migration;
- trusted-time bounded-skew acceptance;
- contiguous WSA/GEL/WAS history verification;
- dual independent cross-standard dispositions;
- independently governed oracle/test-governor operation;
- broad legitimate recovery without false blocking.

## 6. Review requirement before execution

Independent review must audit the composite V5+V6+V7 candidate and WDPC-01…135, including:

- root guardian/admin-domain independence;
- final ApplyDecision revocation/session/schema revalidation;
- provider capability attestation and effect reservation;
- downstream fencing enforcement;
- authoritative history completeness from WSA to WAS;
- predicate bootstrap audit and graph completeness;
- quorum credential/admin independence;
- consequence taxonomy/emergency exceptions;
- current approval assurance;
- cross-standard admin separation;
- registry governance and monotonicity;
- provenance authority/content side channels;
- evidence-class/oracle immutability;
- active-clause-map completeness;
- minimum unique-enforcement-path coverage and overblocking positives.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.
