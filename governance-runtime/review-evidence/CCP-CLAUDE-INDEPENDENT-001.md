# Claude Independent Review — Conversation Continuity & Resumption Governance

Frozen candidate SHA: `1029e8a7883abc30975a6bff908f43cf9192dab5`

Authority effect: `NONE_EVIDENCE_ONLY`

Raw reviewer response follows unchanged.

---

A. Overall disposition: CHANGES_REQUIRED

This is a design-level review only. The artifacts are directionally strong but non-authoritative and unexecuted. For platform qualification, the packet is INSUFFICIENT_EVIDENCE because no qualified implementation or executed falsification matrix is included. Before freeze, multiple exact endpoint, authority-precedence, idempotency, and isolation gaps must be closed.

B. Top strengths

· Clear core invariant: conversation/session/device is an interface, not authoritative workflow state.
· Correctly separates development-time GitHub/repository recovery from production-time coordination-backend/ledger authority.
· Preregistered CCP-01 through CCP-25 cover many interruption/resumption failure classes.
· Exact-artifact binding, approval-scope preservation, RED-history preservation, and fail-closed intent are explicitly stated.
· Reviewer isolation and self-contained external-review packet rules are recognized.
· Runtime checkpoint ownership and rejection of worker self-issued checkpoints are directionally correct.

C. Findings ordered by severity

F-01 — Critical — No single authoritative continuity source / conflict-resolution algorithm

Component: Continuity standard §4, §5, §11; CCP-10, CCP-11, CCP-19, CCP-20.
Failure path: Two durable checkpoints, split-brain ledger/backend, rollback to an older valid checkpoint, or GitHub/ledger disagreement. The system cannot prove which sequence is authoritative.
Why not prevented: “Latest valid durable checkpoint” is undefined without a single authoritative ledger identity, monotonic sequence domain, signed predecessor chain, fencing token, and tie-break rule.
Impact: Unauthorized advance, regression, fork, or stale resumption.
Known/New: Known issue class; split-brain/rollback specifics are new.
Recommended control: Define one authoritative (backend, ledger, sequence-domain) root. Require signed checkpoint chain, predecessor digest, monotonic sequence, fencing token, and fail-closed CONTINUITY_CONFLICT with exact error code and durable resolution record.
Falsification: Strengthen CCP-10/11; add CCP-27 rollback/replay and CCP-28 split-brain ledger/backend.

F-02 — Critical — Checkpoint schema is optional and self-described

Component: Continuity standard §4, §16; CCP-22.
Failure path: A checkpoint omits pending reviewer/test, policy version, authority state, or predecessor digest. Resumption treats omission as absence of the gate.
Why not prevented: “As applicable” permits incomplete checkpoints. Requirements are not derived from bound policy independently of checkpoint self-description.
Impact: Required gates can be deleted by omission.
Known/New: Known issue class.
Recommended control: Mandatory checkpoint schema. Required fields include workflow, phase, candidate digest set, policy/schema version, required reviewer/test set, completed/pending evidence refs, authority state, next permitted action, sequence, predecessor digest, and signer. Reject incomplete checkpoints with exact code.
Falsification: Add CCP-36 checkpoint omission of authority/predecessor/policy.

F-03 — High — Exact-artifact binding lacks a definition of “material change”

Component: Continuity standard §7; CCP-06, CCP-08, CCP-18.
Failure path: Candidate A is reviewed, then branch/candidate changes to B through a change not classified as material. A-bound reviews are reused to qualify B.
Why not prevented: “Material candidate change” is not defined by artifact manifest, digest set, policy/schema version, dependency lock, generated outputs, or allowed non-material edits.
Impact: Review/test evidence applies to wrong artifact.
Known/New: Known issue class.
Recommended control: Define exact artifact manifest and digest algorithm. Define material-change policy per workflow. Any mismatch marks bound evidence stale and triggers policy-defined revalidation/re-review.
Falsification: Strengthen CCP-06; add non-material-edit false-green case.

F-04 — High — Approval scope preservation lacks a durable approval object

Component: Continuity standard §8; CCP-07, CCP-08, CCP-25.
Failure path: User approves Reviewer 2 on candidate A. After interruption, replay or scope expansion authorizes Reviewer 3, repair, adjudication, merge, or a new candidate B.
Why not prevented: No required approval record with principal, exact action, candidate binding, nonce, expiry, session/device context, and rejection codes.
Impact: Approval broadening and terminal-action replay.
Known/New: Known issue class.
Recommended control: Durable approval object with exact scope grammar, nonce, expiry, candidate digest, actor/principal, and revocation status. Reject stale/replayed approvals with exact codes.
Falsification: Add CCP-29 approval issuance interrupted before durable record.

F-05 — High — API/remote-worker continuity lacks idempotency and external-effect control

Component: Continuity standard §14; CCP-14, CCP-15, CCP-16.
Failure path: Retry/resume causes duplicate remote completion, wrong task/workflow association, or non-idempotent external side effect.
Why not prevented: Request/response identity fields are not mandatory. Idempotency key scope, dedupe window, effect ledger, compensation, and reconciliation are unspecified.
Impact: Duplicate review/validation/terminal effect or misbound result.
Known/New: Known issue class.
Recommended control: Mandatory durable request identity, workflow/task/candidate identity, worker/reviewer identity, idempotency key, response digest, lifecycle state, effect ledger, and reconciliation rules.
Falsification: Add CCP-34 non-idempotent external effect duplicate/compensation.

F-06 — High — Reviewer isolation is not enforceable across resumption

Component: Continuity standard §13; CCP-13.
Failure path: Reviewer 1 findings leak into Reviewer 2 through shared checkpoint metadata, same chat context, device state, or resume prompt.
Why not prevented: The standard says not to expose findings, but no access-control model, separate reviewer workspace, data minimization, or leakage test is defined.
Impact: Reviewer independence lost; contaminated adjudication.
Known/New: Known issue class.
Recommended control: Separate reviewer contexts, strict field-level access, metadata-only status sharing, and explicit protocol flag for any cross-review. Add leakage-detection test.
Falsification: Add CCP-32 reviewer context leakage via checkpoint metadata/chat.

F-07 — High — Runtime checkpoint ownership lacks an authorization model

Component: Continuity standard §15; CCP-21.
Failure path: Worker/candidate/reviewer self-issues a checkpoint advancing its own lifecycle.
Why not prevented: “Trusted coordination/governance component” is not defined by role, credential, signature, event schema, or separation-of-duties rule.
Impact: Self-advancement through continuity mechanism.
Known/New: Known issue class.
Recommended control: Define trusted component identity, signing keys, role/event authorization matrix, separation of duties, and exact rejection code for unauthorized checkpoint.
Falsification: Strengthen CCP-21 with forged signer, wrong role, and replay.

F-08 — High — Concurrent sessions/multiple chats acting on same task are not controlled

Component: Continuity standard §1, §4; CCP-01 covers device switch, not concurrency.
Failure path: Laptop and phone sessions both resume, one modifies candidate while the other reviews/adjudicates.
Why not prevented: No single-writer lease, fencing token, session identity, active-session lock, or conflict state.
Impact: Forked workflow, stale evidence, conflicting adjudication.
Known/New: New issue class.
Recommended control: Single active writer per workflow/candidate with lease/fencing token. Concurrent consequential action must fail closed with exact conflict code.
Falsification: Add CCP-26 concurrent multi-session active writer; CCP-40 multiple chats adjudicating same review set.

F-09 — High — Development GitHub recovery and production authority separation lacks phase detection and DR policy

Component: Continuity standard §2, §3, §17; CCP-19, CCP-20.
Failure path: Development manual rule using GitHub is applied during production outage; GitHub mirror is promoted ad hoc to continuity authority.
Why not prevented: No required phase detection, no qualified disaster-recovery policy, no exact rule for backend/ledger unavailability.
Impact: Production terminal action under wrong authority.
Known/New: Known issue class.
Recommended control: Explicit environment/phase detection. Production must fail closed when ledger/backend cannot be verified unless a separately qualified DR policy authorizes a bounded substitute.
Falsification: Add CCP-38 ledger/backend unavailable but local/GitHub cache available.

F-10 — High — Terminal action interruption/partial effect is under-specified

Component: CCP-25 only covers replay.
Failure path: Terminal authorization is issued, interruption occurs during merge/release/deploy, and partial effect is later treated as complete or retried without idempotency.
Why not prevented: No two-phase commit/outbox, terminal nonce, partial-state record, or idempotent terminal-effect protocol.
Impact: Inconsistent terminal state or duplicate terminal action.
Known/New: New issue class.
Recommended control: Terminal action nonce, two-phase commit/outbox, effect ledger, partial-state recovery, exact rejection/reconciliation codes.
Falsification: Add CCP-30 terminal action partial execution; CCP-39 device switch during terminal action after authorization.

F-11 — Medium — Policy migration and revocation cascade are under-specified

Component: Continuity standard §4; CCP-23, CCP-24.
Failure path: Task bound to P1 resumes under P2, or credential K is revoked during interruption but cached evidence is reused.
Why not prevented: No explicit migration/rebinding event, approval requirement, revocation authority, check time, or cascade rules.
Impact: Qualification requirements silently broadened or invalid evidence reused.
Known/New: Known issue class.
Recommended control: Policy migration/rebinding must be an explicit governed event with approval. Revocation must trigger cascade before next action.
Falsification: Add CCP-31 policy/schema migration without rebinding; CCP-35 revocation cascade after resumption.

F-12 — Medium — External packet integrity lacks cryptographic binding and stale-packet nonce

Component: External Manual Review Packet Control §3, §7.
Failure path: Packet is altered, reused for a changed candidate, or reviewed without a verifiable file digest.
Why not prevented: Commit SHA is present, but individual artifact digests, packet manifest, packet ID/nonce, and signature are not required.
Impact: Review evidence may be bound to wrong or stale content.
Known/New: Known issue class.
Recommended control: Require packet manifest with artifact digests, candidate binding, packet ID/nonce, generation time, and signature/digest. Reject stale/reused packets.
Falsification: Add CCP-33 packet digest mismatch/stale packet reuse.

F-13 — High — CCP endpoints are generally not precise enough

Component: CCP matrix.
Failure path: Post-hoc interpretation decides whether an observed event satisfies “durable checkpoint wins,” “rejected,” “stale,” or “fail closed.”
Why not prevented: Most cases lack exact event type, lifecycle state, error/rejection code, authoritative record, actor/principal, and preserved-history requirement.
Impact: False-green execution.
Known/New: Known issue class.
Recommended control: Freeze enums/error codes before execution. Each case must require exact endpoint fields.
Falsification: Strengthen all CCP cases as below.

C.1 CCP-01 through CCP-25 individual endpoint precision review

Case Precise enough? Missing exact endpoint elements
CCP-01 Partial State CONTINUITY_REVIEW_BARRIER_PENDING present; missing event type, rejection code, authoritative record, actor/principal, exact pending reviewer list from bound policy.
CCP-02 Partial CONTINUITY_INSUFFICIENT_EVIDENCE present; missing evidence manifest, error code, durable record, fail-closed action.
CCP-03 Partial “Durable checkpoint wins” lacks binding-verification algorithm, authoritative record, stale-summary rejection event.
CCP-04 Partial CONTINUITY_CONFLICT or stricter; missing precedence rule, exact error code, denied-transition record.
CCP-05 Partial Zero authority stated; missing event type, non-effect record, exact checkpoint reference.
CCP-06 Partial Reviews stale; missing material-change definition, digest set, re-review trigger, error code.
CCP-07 Partial Scope limited; missing approval object, principal, nonce, expiry, rejection code.
CCP-08 Partial Rejected/stale; missing exact error code, authoritative record, candidate-binding fields.
CCP-09 Partial RED preserved; missing append-only proof, replay record, omission-detection rule.
CCP-10 Partial Conflict fail closed; missing ordering authority, tie-break, error code, resolution event.
CCP-11 Partial Sequence controls; missing sequence domain, fencing token, signed order proof.
CCP-12 Partial Insufficient evidence; missing model/session identity record, rejection code, claim record.
CCP-13 Partial Status not findings; missing enforcement, access control, leakage test, protocol flag.
CCP-14 Partial Durable request/response; missing mandatory identity fields, binding algorithm, recovery record.
CCP-15 Partial Non-authoritative; missing rejection code, insufficient-evidence record.
CCP-16 Partial Idempotency prevents duplicate; missing idempotency key scope, dedupe window, reconciliation record, error code.
CCP-17 Partial Resume adjudication pending; missing partial adjudication state, event type, rejection code.
CCP-18 Partial Incomplete repair; missing partial-repair state, exact candidate identity, invalidation cascade.
CCP-19 Partial Ledger controls; missing ledger identity, error code, terminal-block record.
CCP-20 Partial Fail closed; missing DR policy reference, error code, authority-unavailable record.
CCP-21 Partial Rejected authz failure; missing role/event authorization rule, signer proof, exact error code.
CCP-22 Partial Rejected/insufficient; missing policy-derived requirement set, omission detection, error code.
CCP-23 Partial Bound policy or migration; missing migration/rebinding protocol, approval, error code.
CCP-24 Partial Re-evaluate revocation; missing revocation authority, check time, cascade, error code.
CCP-25 Partial Exact binding/nonce/expiry; missing nonce schema, expiry, error code, terminal-action record.

No CCP case is currently precise enough to prevent post-hoc interpretation without additional exact fields.

D. Previously identified continuity issue classes: status

Issue class Status
Skip required stage PARTIALLY_CLOSED
Resume stale/wrong state PARTIALLY_CLOSED
Broaden earlier approval PARTIALLY_CLOSED
Apply evidence to wrong artifact PARTIALLY_CLOSED
Lose reviewer independence PARTIALLY_CLOSED
Premature adjudication/repair PARTIALLY_CLOSED
Confuse development GitHub with production authority PARTIALLY_CLOSED
API/remote work under wrong identity PARTIALLY_CLOSED
Reconstruct cleaner history after interruption PARTIALLY_CLOSED
Device/chat/model/session change affects authority PARTIALLY_CLOSED
External review valid despite missing content/dependencies PARTIALLY_CLOSED

No class is CLOSED by this packet. Qualification-level status remains OPEN until implementation and executed falsification evidence exist.

E. New falsification cases required before freeze

· CCP-26 — Concurrent multi-session active writer / fencing token.
· CCP-27 — Checkpoint rollback/replay to older valid checkpoint.
· CCP-28 — Split-brain coordination backend/ledger with divergent sequences.
· CCP-29 — Approval issuance interrupted after user consent but before durable record.
· CCP-30 — Terminal action partial execution across interruption.
· CCP-31 — Policy/schema migration mid-interruption without explicit rebinding.
· CCP-32 — Reviewer context leakage via shared checkpoint metadata/chat.
· CCP-33 — Packet digest mismatch or stale packet reuse.
· CCP-34 — Non-idempotent external effect duplicate/compensation.
· CCP-35 — Revocation cascade after resumption across cached evidence.
· CCP-36 — Checkpoint omits authority state, predecessor digest, or policy version.
· CCP-37 — API response arrives after candidate changed.
· CCP-38 — Ledger/backend unavailable but local/GitHub cache available.
· CCP-39 — Device switch during terminal action after authorization.
· CCP-40 — Multiple chats adjudicating same completed review set.

F. Freeze decision

DO NOT FREEZE

Freeze conditions:

1. Freeze mandatory checkpoint schema, lifecycle states, event types, and exact error/rejection codes.
2. Define single authoritative continuity root and conflict-resolution algorithm.
3. Define exact artifact manifest and material-change policy.
4. Define durable approval object with nonce/expiry/principal binding.
5. Define API idempotency, request/response identity, and external-effect reconciliation.
6. Define enforceable reviewer isolation and concurrent-session control.
7. Define production DR/phase rules so GitHub cannot become ad hoc runtime authority.
8. Add and execute the new CCP cases with preserved RED history.
9. Obtain independent review of the strengthened matrix and implementation evidence.

This review is evidence only. It grants no merge, release, production, qualification, adjudication, or governance authority.

AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY