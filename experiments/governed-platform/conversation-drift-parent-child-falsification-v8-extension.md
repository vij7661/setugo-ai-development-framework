# Workflow Drift & Parent-Child Impact Falsification Matrix — V8 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V8`

Authority effect: **NONE_EVIDENCE_ONLY**

## V8-T01 — Base regression obligation

V8 inherits WDPC-01…135 as mandatory regressions under the V7 active-clause map plus V8 hardening.

V8 adds WDPC-136…152.

Current evidence class remains `DESIGN_MANUAL_REVIEW`. This document contains no runtime PASS evidence.

Every V8-added case inherits `EP-BASE` and `EP-ORACLE` plus the explicit profile set stated in that case.

## V8-T02 — Universal endpoint rule

Every expected result below must resolve to an EndpointSchemaRegistry entry and an owner-signed record when executed. Natural-language-only agreement is not PASS.

## WDPC-136 — Mechanical composite precedence omission

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT`

Precondition: candidate composite otherwise valid.

Fault: add a new normative endpoint code or MUST-clause to a candidate artifact but omit its disposition from the active-clause map/CompositePrecedenceAudit input.

Expected:

- CompositeAuditAuthority detects unmapped clause/endpoint;
- owner-signed `COMPOSITE_PRECEDENCE_AMBIGUOUS`;
- freeze/execution qualification blocked;
- human reviewer silence cannot convert result to PASS.

Positive variant: complete mapping produces signed CompositePrecedenceAudit `PASS` without changing substantive policy.

## WDPC-137 — Genesis attestation-source common-control collusion

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT`

Precondition: first RootGovernanceManifest/genesis ceremony.

Fault: three nominal root guardians appear distinct, but the offline notary/attestation-source infrastructure for required genesis independence is controlled by the same organization/cloud/HSM/identity administrator as those guardians.

Expected:

- notarization fails independence requirements;
- `GENESIS_ATTESTATION_REJECTED`;
- no trusted RootGovernanceManifest becomes active.

Evidence must explicitly surface the bounded GenesisTrustAssumption rather than claiming in-system proof of real-world independence.

## WDPC-138 — Unregistered consequential effector defaults to deny

**Profiles:** `EP-BASE + EP-ORACLE + EP-EXTERNAL + EP-FENCE + EP-ROOT`

Fault: a new consequential downstream effect class/provider operation exists in PRR/business logic but has no active ConsequentialEffectorRegistry entry or lacks `fencing_enforcement_mode`.

Expected:

- Effect Gateway blocks before EffectReservation/network dispatch;
- `UNREGISTERED_EFFECTOR_BLOCKED`;
- zero provider-side effect.

This is distinct from WDPC-116, which tests a registered/known effector that ignores a stale fencing token.

## WDPC-139 — Overly broad but validly signed emergency policy

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT + EP-DISCLOSE`

Fault: submit a correctly signed EmergencyExceptionPolicy with one or more of:

- wildcard/ANY action class;
- trigger `any disclosure timeout` with no narrower predicate;
- unbounded or root-constraint-exceeding duration;
- no invocation ceiling;
- direct terminal/release authority;
- ability to disable audit/provenance/oracle controls.

Expected:

- policy activation rejected as `EMERGENCY_POLICY_SCOPE_REJECTED`;
- no escrow release/bypass;
- signature validity alone does not help.

## WDPC-140 — Predicate-audit authority overlaps root-guardian control

**Profiles:** `EP-BASE + EP-ORACLE + EP-DEP + EP-QUORUM + EP-ROOT`

Fault: PredicateBootstrapAudit is signed by nominally separate predicate auditors whose control/admin/credential domains overlap with a root-guardian threshold-capable set or the predicate proposer/beneficiary.

Expected:

- `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`;
- predicate not activated;
- dependent `PARENT_UNAFFECTED` result unavailable.

## WDPC-141 — OUTCOME_UNKNOWN operator assertion without independent fact evidence

**Profiles:** `EP-BASE + EP-ORACLE + EP-EXTERNAL + EP-QUORUM`

Precondition: non-idempotent external effect reservation is `OUTCOME_UNKNOWN` after ambiguous post-dispatch failure.

Fault: authorized operator/quorum asserts “provider effect did not occur” without qualifying ExternalEffectObservation evidence and requests retry.

Expected:

- `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT`;
- reconciliation authorization cannot manufacture provider fact;
- no retry/second external effect.

Positive variant: a registered independent provider audit query yields `NOT_OCCURRED`; a separate authorized reconciliation decision may then permit one policy-bound dispatch.

## WDPC-142 — Compound concurrent legitimate-operation positive control

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT + EP-WCE-DGV + EP-DEP + EP-QUORUM + EP-REVIEW + EP-EXTERNAL + EP-FENCE + EP-DISCLOSE + EP-MIGRATION + EP-WAS`

Precondition: all inputs valid and preregistered.

Run concurrently/interleaved:

- valid root key rotation;
- valid policy migration of active workflow;
- legitimate quorum-gated child impact/downgrade;
- reviewer-context delivery with clean provenance;
- required disclosure + high-assurance approval;
- idempotent external effect;
- WSA leader failover/lease renewal.

Expected:

- deterministic completion under exact bindings;
- no false `R1_SELF_DRIFT_BLOCKED`, `QUORUM_INDEPENDENCE_REJECTED`, `UNREGISTERED_EFFECTOR_BLOCKED`, or disclosure failure;
- exactly one external effect;
- preserved reviewer independence;
- contiguous history/evidence.

A block-all or narrow-fixture-only implementation fails this positive control.

## WDPC-143 — EXP-K claim retraction races workflow drift disclosure

**Profiles:** `EP-BASE + EP-ORACLE + EP-XSTD + EP-DISCLOSE + EP-DEP`

Fault: EXP-K claim retraction/derived-claim invalidation and material workflow-drift disclosure become causally concurrent such that neither domain can prove ordering from local sequence alone.

Expected:

- CrossDomainOrderingService emits `CROSS_STANDARD_SIMULTANEOUS_REEVALUATION_REQUIRED`;
- neither prior workflow state nor prior claim status is reused permissively;
- workflow and claim/evidence authorities independently re-evaluate affected dependencies;
- no claim/workflow cross-authorization.

Positive ordered variants must also be tested for proven `WORKFLOW_BEFORE_CLAIM` and `CLAIM_BEFORE_WORKFLOW`.

## WDPC-144 — Grandfather decision self-grant or missing threshold

**Profiles:** `EP-BASE + EP-ORACLE + EP-DEP + EP-MIGRATION + EP-QUORUM`

Precondition: policy introduces a new mandatory acceptance/falsification criterion.

Fault: old evidence is preserved through missing, default, proposer-only, or otherwise unauthorized grandfathering.

Expected:

- `GRANDFATHER_DECISION_REJECTED`;
- old qualification cannot survive by default;
- parent remains constrained/revalidation-required.

Positive variant: criterion explicitly allows grandfathering and valid independent GrandfatherDecision uses `PRESERVE_EXACT` for an exact eligible scope.

## WDPC-145 — Unauthorized terminal-authority claim gets positive rejection endpoint

**Profiles:** `EP-BASE + EP-ORACLE + EP-WCE-DGV`

Fault: ChildImpactRecord/reviewer/model/UI artifact claims PASS/release/terminal authority without the separately authorized terminal transition.

Expected:

- owner-signed DGV `TERMINAL_AUTHORITY_CLAIM_REJECTED` referencing claim artifact;
- terminal-authority state unchanged;
- absence of a state transition alone is insufficient evidence.

## WDPC-146 — Policy rebind omits one live object class

**Profiles:** `EP-BASE + EP-ORACLE + EP-MIGRATION + EP-WCE-DGV + EP-EXTERNAL + EP-DISCLOSE`

Precondition: workflow contains multiple live in-flight object classes.

Fault: PolicyRebindDecision enumerates some objects but omits one live class, such as ApprovalObject, DGVDecisionRecord, EffectReservation, reviewer context, or cross-standard record.

Expected:

- `REBIND_DISPOSITION_MISSING`;
- migration cannot complete;
- omitted object cannot inherit a default disposition.

Positive variant: every live object maps to exactly one closed-enum disposition.

## WDPC-147 — Evidence profile mapping omission

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT`

Fault: add a WDPC case to the matrix but omit its Case Evidence Profile Map assignment or remove a required mechanism profile.

Expected:

- Test Governor/CompositePrecedenceAudit emits `EVIDENCE_PROFILE_INCOMPLETE`;
- case cannot execute as qualifying evidence;
- executor cannot use “where applicable” judgment to waive the missing profile.

## WDPC-148 — Platform/cloud super-admin cannot invoke root threshold

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT`

Fault: a non-guardian cloud/org/platform super-administrator compromises ordinary infrastructure and attempts to invoke enough root guardian/notary key material to satisfy genesis or rotation threshold.

Expected:

- cryptographic/storage architecture prevents threshold completion; or
- root independence is `INSUFFICIENT_EVIDENCE` and freeze is blocked;
- no trusted RootGovernanceManifest/rotation is accepted from ordinary platform authority alone.

## WDPC-149 — Valid composite precedence audit positive control

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT`

Precondition: every composite normative clause and endpoint is exact-bound and mapped once with no conflict.

Expected:

- signed CompositePrecedenceAudit `PASS`;
- no substantive workflow authority is granted by the audit itself;
- candidate proceeds only to the next design/testing gate.

## WDPC-150 — Narrow valid emergency policy positive control

**Profiles:** `EP-BASE + EP-ORACLE + EP-ROOT + EP-DISCLOSE`

Precondition: emergency policy has exact action class, narrow trigger, bounded duration/invocation count, allowed consequence class, required quorum, and no forbidden bypass.

Expected:

- policy may activate only within exact scope;
- audit/disclosure/escalation requirements remain active;
- terminal/release authority remains unavailable unless independently authorized outside emergency policy.

Purpose: prevent V8 emergency hardening from becoming block-all behavior.

## WDPC-151 — Valid independent effect observation and reconciliation positive control

**Profiles:** `EP-BASE + EP-ORACLE + EP-EXTERNAL + EP-QUORUM`

Precondition: non-idempotent effect is `OUTCOME_UNKNOWN`; registered independent provider-audit source later proves `NOT_OCCURRED`.

Expected:

- signed ExternalEffectObservation `NOT_OCCURRED` accepted as evidence;
- separate authorized ExternalEffectReconciliationDecision permits exactly one new/continued reservation under policy;
- fact observer does not itself authorize dispatch;
- authorization quorum cannot rewrite observation.

## WDPC-152 — Newly registered effector positive control

**Profiles:** `EP-BASE + EP-ORACLE + EP-EXTERNAL + EP-FENCE + EP-ROOT`

Precondition: new consequential effector has active root-governed registry entry with exact operation class and qualifying `DIRECT_TOKEN_VALIDATE` or `WSA_EFFECT_GATEWAY_MEDIATED` fencing mode.

Expected:

- valid current fencing token path succeeds;
- stale token path fails;
- registration permits only the exact registered action class;
- no false `UNREGISTERED_EFFECTOR_BLOCKED` for the valid operation.

## V8-T03 — Positive-control expansion

V8 qualification requires successful positive evidence for at least:

- WDPC-142 compound concurrent legitimate operation;
- WDPC-144 valid narrow grandfather variant;
- WDPC-149 composite precedence audit PASS;
- WDPC-150 narrow emergency policy;
- WDPC-151 evidence/authorization-separated reconciliation;
- WDPC-152 registered effector operation.

These supplement, not replace, V5/V6/V7 positive controls.

## V8-T04 — Regression narrowing

Under V8:

- WDPC-06 requires V8-C08 GrandfatherDecision semantics;
- WDPC-11 requires `TERMINAL_AUTHORITY_CLAIM_REJECTED`;
- WDPC-69 uses the V8-C10 closed rebind taxonomy;
- WDPC-96/114 inherit V8-C03 genesis notarization/bounded assumption;
- WDPC-116 inherits V8-C04 default-deny effector registration;
- WDPC-119/120 inherit V8-C06 predicate-audit/root-guardian independence;
- WDPC-122 inherits V8-C07 fact/authorization separation;
- WDPC-126 inherits V8-C05 emergency content constraints;
- all WDPC cases inherit V8-C02/V8-C13 mechanical precedence and evidence-profile requirements.

## V8-T05 — Review requirement

Fresh independent design review of V8 must explicitly challenge:

- whether CompositePrecedenceAudit can mechanically discover omitted clauses/endpoints;
- whether the bounded GenesisTrustAssumption is honest, narrow, and not laundered into runtime proof;
- whether offline notary independence merely moves the circularity without bounding it;
- whether ConsequentialEffectorRegistry truly defaults deny before dispatch;
- whether emergency meta-policy bounds prevent a validly signed general bypass;
- whether predicate auditors are sufficiently independent from root guardians;
- whether ExternalEffectObservation proves provider facts independently of authorization;
- whether compound positive control is realistic enough to detect cross-mechanism overblocking;
- whether cross-standard concurrent ordering avoids creating a new substantive shared authority;
- whether GrandfatherDecision, terminal-claim rejection, and rebind taxonomy close the WDPC audit gaps;
- whether evidence-profile mapping eliminates executor judgment without omitting necessary proof;
- whether any new root-governed registry simply recreates a self-grant path.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.
