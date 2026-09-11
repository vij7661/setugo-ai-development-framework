# Workflow Drift and Parent-Child Impact Control

Status: **PROPOSED V5 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent workflow drift, context loss, child-task substitution, reviewer contamination, stale-state replay, or R1 self-drift from changing governed workflow state without an independently verifiable authorization path.

> Labels are never enforcement. `PASS`, `BLOCKED`, `REVIEWED`, `DELIVERED`, `UNAFFECTED`, or any other status has no authority unless the named owner commits the required signed record under this contract.

## 1. Scope and operating modes

Production execution is API-backed only.

- `MANUAL_GOVERNED`: a human principal authorizes policy-eligible transitions through platform UI/API.
- `AUTOMATIC_GOVERNED`: a qualified policy authorizes policy-eligible transitions without synchronous human approval.

Both modes use the same authoritative state, policy, drift-validation, evidence, idempotency, reviewer-isolation, and authority mechanisms. Copy/paste reviewer/worker transport is not a normal runtime execution mode.

Current development/testing review of this candidate is manual-only. Manual review evidence may qualify this design for the next design stage only; it MUST NOT be represented as runtime API enforcement evidence.

## 2. Trust domains and service identities

The following logical trust domains are normative:

- `WSA` — Workflow State Authority
- `DGV` — Drift Guard Validator
- `PRR` — Policy & Role Registry
- `RCB` — Reviewer Context Builder
- `DR` — Disclosure Recorder
- `GEL` — Governance/Evidence Ledger
- `WAS` — Witness Anchor Service

They may share physical infrastructure, but qualification requires separate service identities, non-overlapping write credentials, and distinct signing-key handles for `WSA`, `DGV`, and `PRR`.

R1 MUST NOT possess:

- WSA state-write credentials;
- WSA/PRR/DGV signing keys;
- PRR policy-write credentials;
- DGV decision-write credentials;
- GEL administrative rewrite credentials;
- WAS anchoring keys.

DGV may read WSA + PRR and write DGV decisions, but may not modify PRR policy or WSA state directly. WSA may commit a consequential transition only when it validates a current DGV decision token for the exact pre-state/action. PRR policy changes require a separately authorized governance path and cannot be written by R1/DGV as part of action evaluation.

A shared process/container does not satisfy independence if one compromise principal can write WSA state, PRR policy, and DGV decisions or use all three signing keys.

## 3. Cryptographic object contract

All signed governance objects use:

- canonical JSON: RFC 8785 JSON Canonicalization Scheme;
- digest: SHA-256 over canonical bytes;
- signature: Ed25519;
- key reference: `key_id` in the `GovernanceKeyRegistry`;
- identity binding: `service_principal_id` + `key_id` + allowed object type.

The `GovernanceKeyRegistry` is versioned and append-only. Every key entry contains:

- `key_id`
- `service_principal_id`
- public key
- allowed object types
- `not_before_sequence`
- optional `not_after_sequence`
- status `ACTIVE | RETIRING | REVOKED`
- revocation sequence/reason where applicable
- predecessor registry digest
- registry signature

A key cannot sign an object type outside its registry scope. A WCE or decision presented for new consequential use is rejected if its signing key is revoked or outside its active sequence range. Historical objects remain verifiable as historical evidence if they were valid at their recorded issuance sequence; they do not regain current action authority.

## 4. Authoritative state objects

### 4.1 WSA StateSnapshot

WSA signs a `StateSnapshot` containing:

- `snapshot_id`
- `schema_version`
- `root_workflow_id`
- `workflow_graph_digest`
- current task/parent IDs
- phase
- checkpoint ID/sequence
- candidate manifest digest
- dependency graph root digest
- bound policy ID/version/digest
- pending gate set digest
- approval set digest
- active child set digest
- authority-state digest
- permitted-state-transition basis digest
- WSA high-water sequence
- predecessor snapshot digest
- issuer/key/signature

WSA sequence is monotonically increasing per workflow root and persisted atomically with the state transition. WSA restart MUST recover the maximum committed sequence; rollback is forbidden.

### 4.2 PRR PolicySnapshot

PRR signs a `PolicySnapshot` containing:

- policy ID/version/digest;
- workflow scope;
- role definitions and principal/key bindings;
- allowed transitions;
- gate prerequisites;
- relationship-classification rules;
- downgrade permissions/quorum;
- impact-decision permissions/quorum;
- approval rules;
- disclosure timing rules;
- fallback activation rules;
- external request/result rules;
- migration/continuation rules;
- effective and superseding sequences;
- predecessor policy digest;
- issuer/key/signature.

A policy is `qualified` only if the exact signed PRR snapshot is active for the current WSA state.

## 5. Workflow Context Envelope (`WCE`)

Before any consequential R1 proposal, WSA issues a one-use WCE bound to the current snapshot.

Required fields:

- `envelope_id`
- `schema_version`
- root/parent/task IDs
- phase
- checkpoint ID/sequence
- WSA snapshot digest
- workflow graph digest
- candidate manifest digest
- dependency graph root digest
- policy ID/version/digest
- pending gate digest
- active child digest
- permitted-action-basis digest
- prohibited-action-basis digest where applicable
- `issued_authority_sequence`
- `envelope_nonce`
- `issued_at`
- `expires_at`
- WSA issuer/key/signature

DGV keeps a durable per-workflow high-water mark and a consumed-envelope set. Before evaluation it MUST verify:

1. RFC8785 canonical bytes/signature;
2. WSA key active for WCE object type;
3. supported schema version;
4. workflow/task scope match;
5. WCE checkpoint/WSA sequence equals current WSA snapshot;
6. candidate/policy/graph/gate digests equal current authoritative values;
7. envelope not expired beyond policy clock-skew tolerance;
8. envelope nonce not previously consumed;
9. envelope sequence is not lower than DGV high-water mark;
10. no key revocation/superseding snapshot invalidates current use.

Failure emits signed `CONTEXT_ENVELOPE_REJECTED` and blocks consequential work. Time is never the sole freshness signal; sequence/digest equality is mandatory.

After DGV accepts a proposal for evaluation, the WCE nonce is consumed atomically with the DGV decision record. Replaying the WCE for another proposal is rejected.

## 6. Formal dependency graph and staleness

WSA maintains a signed `DependencyGraphSnapshot` whose canonical root digest is included in StateSnapshot/WCE.

Node types include at minimum:

- candidate artifact;
- policy;
- gate;
- review/test evidence;
- approval;
- authority source;
- identity/credential;
- provider/model qualification;
- acceptance/falsification criterion;
- external request/result;
- workflow transition.

Every edge contains:

- parent node ID/digest;
- child/dependent node ID/digest;
- dependency type;
- validation predicate ID/version;
- materiality flag;
- policy owner.

DGV staleness algorithm:

1. compute changed-node set from old/new signed snapshots;
2. traverse reverse dependency closure;
3. execute each bound predicate against current signed inputs;
4. classify each dependent node `UNCHANGED_VALID | STALE | REVALIDATION_REQUIRED | INSUFFICIENT_DEPENDENCY_EVIDENCE`;
5. produce signed `DependencyImpactRecord` listing changed, affected, unaffected, stale, and insufficient sets plus graph root/digest inputs.

`PARENT_UNAFFECTED` is valid only if the complete required dependency closure has no `STALE`, `REVALIDATION_REQUIRED`, or `INSUFFICIENT_DEPENDENCY_EVIDENCE` nodes relevant to parent progression. Empty affected sets without this record are invalid.

## 7. Deterministic R1 drift classification

Definitions:

- **Consequential action**: any action capable of mutating authoritative workflow/task/candidate/policy/evidence/approval/authority state; issuing/reconciling external reviewer/worker/model work; creating/cancelling/superseding a child; changing evidence validity; or causing an external side effect.
- **Material workflow drift**: a proposal that changes root/parent/task identity, phase, candidate/policy binding, pending gates, authority state, permitted-action basis, or creates a consequential child.
- **Information-only child**: no consequential permission and no shared mutable dependency with parent.
- **Exact next permitted action**: action set computed by DGV from signed WSA StateSnapshot + signed PRR PolicySnapshot, never from R1 prose.

R1 may propose:

- `SAME_WORKFLOW`
- `INFORMATION_ONLY_CHILD`
- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE`

R1 classification has zero state authority until DGV evaluation.

## 8. R1 proposal and deterministic DGV evaluation

Every consequential R1 proposal is first persisted immutably as `R1Proposal` with:

- proposal ID;
- R1 principal/model identity;
- WCE ID/digest;
- user/operator intent digest;
- action type + normalized action digest;
- proposed relationship;
- parent/child IDs;
- candidate/policy/checkpoint bindings;
- rationale reason code/digest;
- idempotency key;
- creation sequence/time.

DGV evaluation algorithm is fixed:

1. validate WCE;
2. load exact signed WSA StateSnapshot referenced by WCE;
3. load exact active signed PRR PolicySnapshot;
4. compute permitted transition set from `(state, phase, gates, authority, relationship, policy)`;
5. validate actor role/key and approval/disclosure prerequisites;
6. validate concurrency lease/fencing token when mutation is requested;
7. validate dependency-impact prerequisites;
8. produce one signed DGV decision: `ALLOW | DENY | INSUFFICIENT_STATE` with reason code and exact pre-state/action digest;
9. consume WCE nonce and persist decision atomically.

WSA accepts a consequential transition only when an `ALLOW` decision exactly matches current WSA pre-state digest, policy digest, action digest, actor, and unused decision nonce.

If R1 says `SAME_WORKFLOW` but DGV denies the action as outside the permitted set, DGV emits `R1_SELF_DRIFT_BLOCKED`; WSA state remains unchanged. The raw R1Proposal and denial remain immutable even if a later proposal succeeds.

## 9. Relationship downgrade and impact quorum

A change from `BLOCKING_CHILD | DEPENDENCY_CHILD | INCIDENT_CHILD` to `NON_BLOCKING_CHILD | INFORMATION_ONLY_CHILD` that weakens/removes a gate is a gate-reducing downgrade.

Gate-reducing downgrade requires:

- PRR permission `RELATIONSHIP_DOWNGRADE`;
- signed `RelationshipDowngradeDecision`;
- at least two distinct confirmer principals/keys when a mandatory gate is removed;
- proposer MUST NOT be a confirmer;
- R1 MUST NOT be a confirmer;
- child worker/reviewer whose result benefits from downgrade MUST NOT be sole confirmer;
- no confirmer keys sharing the same principal identity;
- all confirmer roles active/not revoked at final commit sequence.

If quorum/separation fails: `RELATIONSHIP_DOWNGRADE_REJECTED`.

Permissive ChildImpact classes that resume progression (`PARENT_UNAFFECTED` or removal of a blocking condition) use the same dual-control rule when they eliminate a mandatory gate. Original classifications/history are never overwritten.

## 10. ChildImpactRecord contract

Each record binds:

- impact record ID;
- parent/child workflow IDs;
- parent checkpoint/WSA sequence;
- parent candidate digest;
- child result digest;
- dependency graph root;
- `DependencyImpactRecord` ID/digest;
- impact class;
- affected/unaffected/stale/insufficient sets;
- required re-review/re-test/rebind actions;
- next permitted action identifier;
- policy ID/version/digest;
- deciding role/principal/key;
- required confirmer signatures/quorum;
- nonce/idempotency identity;
- predecessor impact/event digest;
- authoritative sequence/time.

Replay against changed checkpoint/candidate/policy/dependency root is rejected as `CHILD_IMPACT_RECORD_REJECTED`.

## 11. Disclosure and approval protocols

### 11.1 DriftDisclosureRecord

DR creates a signed record containing:

- disclosure ID;
- authenticated user principal ID;
- root/parent/child workflow IDs;
- checkpoint/WSA sequence;
- candidate/policy digest;
- relationship classification;
- parent paused/unaffected state;
- impact-handling-required flag;
- orchestration mode;
- canonical disclosure content digest;
- required delivery class;
- delivery target identity;
- delivery state `PENDING | SENT | DELIVERED | FAILED | TIMED_OUT`;
- issued/delivery sequences and timestamps;
- related R1Proposal/DGV event IDs;
- approval-required flag;
- issuer/key/signature.

`DELIVERED` requires a signed `DeliveryReceipt` from an authorized delivery service binding disclosure ID, authenticated/verified recipient principal or verified channel ID, workflow/checkpoint, delivery proof type, and delivery time/sequence.

For MANUAL_GOVERNED material drift requiring approval: `DELIVERED` MUST precede approval creation and consequential transition.

For AUTOMATIC_GOVERNED:

- if `async_disclosure_allowed=false`, `DELIVERED` precedes transition;
- if true, transition and disclosure record must be committed atomically; delivery may remain pending only until policy `max_delivery_age`;
- pending/failed/timed-out disclosure can never be reported as disclosure PASS;
- on timeout, DR emits `DISCLOSURE_TIMEOUT`; PRR defines whether subsequent consequential transitions pause/escalate, but the timeout cannot be interpreted as approval/no-impact.

Wrong recipient/workflow/checkpoint receipt fails as `DISCLOSURE_GATE_FAILED`.

### 11.2 ApprovalObject

Approval is separate from disclosure/acknowledgement. `ApprovalObject` binds:

- approval ID;
- authenticated principal ID/key/session assurance level;
- workflow/parent/child IDs;
- checkpoint/WSA sequence;
- candidate/policy digest;
- exact action type/digest;
- disclosure ID where required;
- nonce;
- issued/expiry sequence/time;
- issuer/authentication-service signature.

DGV verifies approval at final decision sequence. Expired, replayed, wrong-action, wrong-policy, or post-revocation approval is rejected.

## 12. R1 fallback activation

Fallback role `R1_FALLBACK_ORCHESTRATOR` exists only through a signed PRR `FallbackActivation` object binding principal/key, workflow scope, allowed actions, activation sequence, expiry sequence/time, reason, and predecessor policy digest.

DGV validates activation independently. No active valid fallback => `R1_UNAVAILABLE_BLOCKED`.

Fallback cannot self-activate and is subject to the same WCE/DGV/disclosure rules as R1.

## 13. Reviewer Context Builder isolation

RCB uses a strict versioned whitelist schema with `additionalProperties=false`. Default allowed fields:

- reviewer identity/role;
- review workflow/task ID;
- parent workflow ID;
- parent checkpoint/sequence;
- parent active/paused state;
- blocking-child existence/type when required;
- candidate manifest digest;
- policy identity;
- reviewer's own status;
- unresolved impact status;
- explicitly authorized artifact/evidence scope.

Before cross-review/adjudication authorization, prohibited content includes another reviewer's finding/disposition, R1 rationale/narrative, expected agreement, majority state, adjudication conclusion, golden/test oracle, and free-form arbitrary metadata.

RCB validation:

1. source fields must come from signed WSA/PRR/GEL records;
2. schema rejects unknown/free-form metadata;
3. artifact payloads use an explicit allowlist and provenance tag;
4. context is canonicalized/digested;
5. a forbidden-origin scan checks provenance tags/field classes, not semantic guessing alone;
6. test fixtures use opaque randomized handles so fixture names cannot reveal expected outcome;
7. signed `ReviewerContextRecord` binds source sequence, schema, field allowlist digest, payload digest, reviewer identity, and delivery event.

Violation emits `REVIEW_CONTEXT_REJECTED_LEAKAGE`; contaminated context cannot count as independent review evidence.

Timing/provider side channels are treated as separate falsification targets; reviewer context APIs MUST NOT expose other-reviewer completion counts/timing where independence policy forbids them.

## 14. External request/result lifecycle

Every runtime external request has durable lifecycle:

`CREATED -> DISPATCHED -> ACKNOWLEDGED -> {COMPLETED | TIMED_OUT | CANCELLED}`

Every received result has:

`RECEIVED -> BINDING_VALIDATED -> {ELIGIBLE | QUARANTINED_STALE | QUARANTINED_INVALID} -> EFFECT_APPLIED`

Required bindings: workflow/task/parent IDs, candidate digest, policy digest, provider/model/worker identity, request ID, intent-level idempotency key, payload digest, WSA sequence, evidence visibility scope.

A unique persistent constraint on `(workflow_id, intent_idempotency_key)` prevents duplicate intents. A unique effect record on `intent_id` permits at most one governance effect. Late success after timeout/cancel/retry is preserved but cannot create another effect. WSA restart does not clear idempotency/effect tables.

Policy/candidate/checkpoint mismatch at result validation emits `STALE_RESULT_REJECTED`.

## 15. Policy migration and role revocation

Policy migration requires signed `PolicyRebindDecision` stating:

- old/new policy IDs/versions/digests;
- workflow/checkpoint/candidate binding;
- whether each in-flight request class is `CONTINUE_OLD_POLICY | CANCEL_AND_REISSUE | REVALIDATE_ON_RETURN`;
- evidence/approval/disclosure revalidation requirements;
- deciding authority/quorum;
- effective WSA sequence.

No implicit default migration.

Role/key revocation is checked again at final DGV/WSA commit. A principal valid at proposal time but revoked before commit cannot authorize the transition unless PRR explicitly defines grandfathering for that exact action class.

## 16. Concurrency, leases, CAS, and restart-safe fencing

WSA maintains a durable monotonic fencing counter per mutation scope in the same transactional/consensus state as checkpoint sequence.

`WriteLease` fields:

- lease ID;
- workflow/task scope;
- checkpoint sequence;
- candidate digest;
- fencing token;
- issued sequence;
- expiry time/sequence;
- holder principal;
- issuer/signature.

On every mutation WSA requires token == current authorized token and checkpoint/pre-state match. Any token lower than current is `STALE_WORKFLOW_WRITER_REJECTED`.

Restart recovery loads the maximum committed fencing token and MUST NOT issue a lower/reused token. Lease expiry never converts a blocked transition into approval; a new lease gets a higher token.

Manual/automatic races, parent/child races, cancellation/supersession races, and child/sibling races use the same ordering rule.

## 17. WSA/GEL atomicity and crash recovery

Each consequential WSA transition and its GEL event are committed through one transactional boundary or durable outbox that binds the same transition ID/pre-state/post-state digest.

Recovery rules:

- WSA snapshot sequence is authoritative for executable state;
- GEL must contain or reconstruct the corresponding event for every committed transition;
- missing/mismatched event enters `STATE_LEDGER_DIVERGENCE_BLOCKED`;
- no component may choose whichever source is more permissive;
- recovery reconciles from signed transition/outbox records and blocks consequential work until digests match.

## 18. GEL tamper evidence and external witness anchoring

Every GEL record contains predecessor event digest and authoritative sequence. Batches produce a Merkle root.

WAS periodically signs `{workflow_scope, start_sequence, end_sequence, merkle_root, previous_anchor_digest}` with a key not available to GEL administrators and stores the signed anchor in an external append-only/write-once witness store.

Qualification requires anchor verification for RED-preservation tests. Rewriting/deleting a historical `R1_SELF_DRIFT_BLOCKED` or other event changes the Merkle root and yields `LEDGER_ANCHOR_MISMATCH`.

WAS does not grant workflow authority; it provides tamper evidence only.

## 19. Endpoint/Event registry

Every matrix endpoint is a signed record, not a prose label. All events share:

`event_id, event_type, schema_version, owner_service, workflow/root/parent/task IDs as applicable, actor_principal, pre_state_digest, post_state_digest, WSA_sequence, candidate_digest, policy_digest, related_object_ids, reason_code, predecessor_event_digest, created_at, key_id, signature`.

Normative owner/payload additions:

- `NO_GOVERNED_TRANSITION` — DGV; proposal/action digest + unchanged WSA snapshot digest.
- `WORKFLOW_DRIFT_DETECTED` — DGV; proposed action/class + expected scope.
- `R1_SELF_DRIFT_BLOCKED` — DGV; R1Proposal ID + permitted-set digest + unchanged WSA sequence proof.
- `CONTEXT_ENVELOPE_REJECTED` — DGV; WCE ID + validation failure code.
- `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE` — DGV; missing/conflicting signed object IDs.
- `PARENT_PAUSED_PENDING_CHILD_IMPACT` — WSA; child edge + preserved resume checkpoint.
- `PARENT_RESUMED_FROM_CHILD` — WSA; accepted impact ID + resume transition.
- `CHILD_RETURN_EDGE_ACCEPTED` — WSA; immediate from/to graph edge.
- `RELATIONSHIP_DOWNGRADE_REJECTED/ACCEPTED` — DGV/WSA; downgrade object + quorum proof.
- `CHILD_IMPACT_RECORD_REJECTED` — DGV; impact record ID + binding/quorum/dependency failure.
- `R1_UNAVAILABLE_BLOCKED` — DGV; required R1 role + absent/invalid fallback proof.
- `DRIFT_DISCLOSURE_RECORDED`, `DISCLOSURE_DELIVERED`, `DISCLOSURE_TIMEOUT`, `DISCLOSURE_GATE_FAILED` — DR; disclosure/receipt/recipient/checkpoint data.
- `REVIEW_CONTEXT_REJECTED_LEAKAGE`, `REVIEW_CONTEXT_DELIVERED` — RCB; context digest + schema/field/provenance result.
- `STALE_WORKFLOW_WRITER_REJECTED` — WSA; lease/fencing/current-token proof.
- `STALE_RESULT_REJECTED` — DGV; request/result and mismatched binding.
- `POLICY_REBIND_REQUIRED/ACCEPTED` — PRR/WSA; old/new policy and migration decision.
- `CANCELLATION_ACCEPTED`, `SUPERSESSION_ACCEPTED`, `CONFLICTING_TRANSITION_REJECTED` — WSA; competing transition IDs/sequences.
- `EXTERNAL_EFFECT_DEDUPLICATED` — WSA/GEL effect reconciler; intent/effect IDs.
- `ADMIN_EVIDENCE_IMPORT_REJECTED` — DGV; transport mode + attempted evidence binding.
- `CROSS_STANDARD_INCIDENT_LINKED` — GEL cross-standard linker; workflow event IDs + EXP-K claim/continuity IDs + separate dispositions.
- `INSUFFICIENT_TEST_INDEPENDENCE` — test governor; fixture ID + leak channel + invalidation proof.
- `STATE_LEDGER_DIVERGENCE_BLOCKED` — WSA recovery controller; mismatched sequence/digests.
- `LEDGER_ANCHOR_MISMATCH` — WAS verifier; batch/anchor/Merkle mismatch.

An endpoint claimed without its owner-signed required record is `INSUFFICIENT_EVIDENCE`, not PASS.

## 20. Cross-standard EXP-K incident contract

`CrossStandardIncidentRecord` binds:

- workflow drift event ID(s);
- EXP-K claim ID(s)/continuity-failure ID(s);
- root/parent/child workflow IDs;
- candidate/policy/checkpoint identities;
- workflow disposition;
- claim/evidence status;
- separate deciding authorities;
- explicit flags `workflow_authorizes_claim=false` and `claim_authorizes_workflow=false`;
- predecessor digest/sequence/signature.

Neither standard can infer completion from the other.

## 21. Manual testing versus runtime qualification

Every test evidence record MUST contain `execution_evidence_class` exactly one of:

- `DESIGN_MANUAL_REVIEW`
- `RUNTIME_SIMULATION`
- `RUNTIME_IMPLEMENTATION`

During the current testing phase, external reviews are `DESIGN_MANUAL_REVIEW` and use no reviewer/model API calls.

A runtime enforcement case cannot receive runtime PASS from `DESIGN_MANUAL_REVIEW` evidence. Attempting that emits/records `INSUFFICIENT_EVIDENCE_FOR_RUNTIME_QUALIFICATION` in the test governor.

## 22. Source precedence during development and runtime

Current development/testing: exact frozen GitHub/project artifacts and committed checkpoints are the durable recovery source. Memory/chat is advisory and cannot override them.

Eventual runtime: WSA + PRR + GEL under the signed/recovery rules above are authoritative. GitHub is not the live runtime state authority.

If authoritative source reconstruction is incomplete/conflicting, fail closed; do not ask memory/chat to decide the state.

## 23. Current project application

- Parent: MVP independent-review workflow.
- Parent state: `PARENT_PAUSED_PENDING_CHILD_IMPACT`.
- Child 1: continuity/resumption governance.
- Child 2: workflow-drift and parent-child impact governance.
- Parent reviewer barriers remain pending unless a separately governed impact decision changes them.

Prior reviews remain immutable evidence only for their exact candidate SHAs. V5 is a new candidate and requires fresh exact-revision review.

## 24. Freeze condition

V5 MUST NOT be frozen for execution until its paired V5 falsification matrix is independently reviewed against this exact revision and the governing policy threshold is satisfied.

No R1 statement, review, policy label, endpoint label, impact record, disclosure, majority, or model agreement grants merge, release, production, qualification, adjudication, or terminal authority except through a separately qualified exact transition contract.