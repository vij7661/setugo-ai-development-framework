A. Overall disposition

CHANGES_REQUIRED

No implementation evidence is included. The packet is a design/matrix review only. Several named mechanisms are not specified enough to be independently enforceable, and multiple runtime cases are only prose-bound. The candidate cannot be treated as ready for execution/freeze.

---

B. Critical findings

CF-01 — WSA/DGV/PRR trust boundary is not independently enforceable
Severity: Critical
Affected: Standard §§2.1–2.3, 5, 8, 10, 12, 18; Matrix WDPC-17, 36, 37, 41, 43, 49–54
Failure path: WSA, DGV, and PRR may share infrastructure. R1 cannot directly write WSA in prose, but there is no identity/key/deployment separation, no DGV algorithm, and no PRR policy language. A compromised or R1-aligned shared service can recompute “permitted” actions permissively or accept R1’s proposal.
Why V4 insufficient: Names independent authority boundaries but does not define independent trust domains, signed state, policy evaluation, or enforcement APIs.
Narrow fix: Define WSA/PRR signed state APIs, DGV deterministic evaluator, key-bound identities, independent deployment/authority domains, and no R1 write path.
Falsification test: Simulate R1-controlled/shared-infra compromise and attempt to convert RED to PASS without independent WSA/PRR contradiction.

CF-02 — WCE integrity/replay/key semantics are incomplete
Severity: Critical
Affected: Standard §5, §5.1; Matrix WDPC-49, 50, 65
Failure path: A forged, stale, wrong-workflow, or replayed WCE can pass if canonicalization, signature algorithm, key rotation/revocation, nonce cache, sequence high-water mark, and clock-skew rules are absent.
Why V4 insufficient: Lists fields and validation steps but omits exact canonical form, MAC/signature algorithm, key lifecycle, replay storage, and supersession semantics.
Narrow fix: Specify canonicalization, asymmetric signing, key registry with rotation/revocation, nonce/replay cache, WSA sequence high-water mark, and schema migration rules.
Falsification test: Replay valid old WCE after checkpoint advance and after key revocation; require CONTEXT_ENVELOPE_REJECTED.

CF-03 — Deterministic definitions lack formal dependency/policy schemas
Severity: Critical
Affected: Standard §3, §12, §13; Matrix WDPC-04–08, 24, 64, 75
Failure path: “Material drift,” “unaffected,” “stale evidence,” and “qualified policy” are only prose. PARENT_UNAFFECTED can be claimed with an empty affected set or incomplete dependency comparison.
Why V4 insufficient: Requires dependency comparison but does not define dependency graph, digest inputs, comparison algorithm, or independent verification.
Narrow fix: Define formal workflow/evidence/policy dependency graph, DGV comparison algorithm, and mandatory affected/unaffected/stale set schema.
Falsification test: Hide one dependency change while returning empty affected set; require CHILD_IMPACT_RECORD_REJECTED and no parent resume.

CF-04 — Downgrade/impact authority separation is under-specified
Severity: Critical
Affected: Standard §10, §12; Matrix WDPC-43, 54, 61
Failure path: R1 alone cannot confirm downgrade, but independent confirmer is not identity-bound, quorum-controlled, or separated by role/key. A misconfigured PRR can let R1 or a child self-authorize.
Why V4 insufficient: No role/key binding, conflict-of-interest rule, quorum, revocation, or independent confirmation schema.
Narrow fix: Define key-bound confirmer identities, quorum/separation rules, no proposer-confirmer overlap, and immutable downgrade history.
Falsification test: R1 holds RELATIONSHIP_DOWNGRADE and self-confirms; require RELATIONSHIP_DOWNGRADE_REJECTED.

CF-05 — Disclosure/approval binding is not strong enough
Severity: Critical
Affected: Standard §14, §14.1, §14.2; Matrix WDPC-51, 52, 66, 67
Failure path: A disclosure can be recorded as delivered to the wrong user/workflow/checkpoint, or asynchronous disclosure can be reported clean while still pending/failed. Approval is separate in prose but lacks schema.
Why V4 insufficient: No signed delivery receipt, recipient-binding proof, async timeout/escalation, or approval-object schema.
Narrow fix: Define DR delivery receipts, exact recipient/workflow/checkpoint binding, separate approval schema, and async failure consequences.
Falsification test: Deliver disclosure to wrong recipient then capture approval; require DISCLOSURE_GATE_FAILED.

CF-06 — RCB isolation lacks leakage detection mechanics
Severity: Critical
Affected: Standard §16; Matrix WDPC-19, 53, 68
Failure path: RCB lists allowed/prohibited fields but does not define payload validation, source signatures, side-channel controls, or independent leakage audit. Prior findings can leak through metadata or narrative fields.
Why V4 insufficient: REVIEW_CONTEXT_REJECTED_LEAKAGE is named but no detection algorithm or schema is specified.
Narrow fix: Define whitelist schema, source signatures, content digest, forbidden-field scanner, and independent audit record.
Falsification test: Inject prior finding into allowed metadata; require REVIEW_CONTEXT_REJECTED_LEAKAGE.

CF-07 — Endpoint vocabulary is not fully schema/owner-bound
Severity: Critical
Affected: Matrix §3, §6; multiple cases
Failure path: Some endpoints are labels only, e.g. NO_GOVERNED_TRANSITION, WORKFLOW_DRIFT_DETECTED, CROSS_STANDARD_INCIDENT_LINKED, INSUFFICIENT_TEST_INDEPENDENCE. A case can be marked PASS by prose.
Why V4 insufficient: Every endpoint must have a required record schema and owner; not all do.
Narrow fix: Define schema, owner, required fields, and GEL/WSA commit rule for every endpoint.
Falsification test: Attempt to claim endpoint without committed schema record; require INSUFFICIENT_EVIDENCE.

CF-08 — Concurrency/fencing lacks lease issuance and monotonic persistence rules
Severity: Critical
Affected: Standard §18, §20; Matrix WDPC-17, 37, 70
Failure path: Fencing tokens are required, but no lease issuance, expiry, generation, persistence, or restart recovery is defined. Stale writers may commit after WSA restart.
Why V4 insufficient: CAS/fencing is named but not fully specified.
Narrow fix: Define WSA fencing-token generation, monotonic persistence, lease expiry, and restart recovery.
Falsification test: Restart WSA, reuse stale fencing token; require STALE_WORKFLOW_WRITER_REJECTED.

---

C. High / Medium / Low findings

HF-01 — Fallback authority activation is not independently proven
Severity: High
Affected: Standard §15; Matrix WDPC-56
Failure path: R1_FALLBACK_ORCHESTRATOR can be treated as active without signed PRR activation.
Why insufficient: Expiry/effective sequence named but not identity-bound or independently verified.
Narrow fix: Require signed PRR activation, exact scope, expiry, and independent DGV validation.
Falsification test: Fallback self-activates; require R1_UNAVAILABLE_BLOCKED.

HF-02 — Policy migration and late-result rules are not exact enough
Severity: High
Affected: Standard §20; Matrix WDPC-23, 69
Failure path: Old-policy late result may be silently applied under new policy.
Why insufficient: POLICY_REBIND_DECISION exists but no exact in-flight continuation/late-result matrix.
Narrow fix: Define per-result binding to policy ID/version/digest and continuation rules.
Falsification test: Old-policy result arrives after rebind; require STALE_RESULT_REJECTED.

HF-03 — External request/result reconciliation lacks full state machine
Severity: High
Affected: Standard §19; Matrix WDPC-21, 29, 31, 33, 38
Failure path: Duplicate, late, or wrong-bound results can produce two governance effects.
Why insufficient: Lifecycle fields named but no exact dedup/effect state machine.
Narrow fix: Define request/result lifecycle, idempotency key, effect dedup, and late-result quarantine.
Falsification test: Provider timeout + late success + retry success; require one effect.

HF-04 — EXP-K cross-standard linkage lacks joint authority schema
Severity: High
Affected: Standard §17; Matrix WDPC-74
Failure path: Workflow disposition may implicitly validate a claim or vice versa.
Why insufficient: Separation stated but no dual-signature/joint-incident schema.
Narrow fix: Define CROSS_STANDARD_INCIDENT_LINKED schema with separate dispositions and explicit non-authorization.
Falsification test: Workflow recovery attempts to validate claim; require rejection.

MF-01 — Hard-negative coverage is still incomplete
Severity: Medium
Affected: Matrix §4–5
Failure path: Overblocking may not be detected for many normal operations.
Why insufficient: Only some positive controls exist.
Narrow fix: Add normal WSA/DGV/PRR/RCB/DR positive cases.
Falsification test: Run accepted normal parent action with no drift; require no false block.

MF-02 — Manual testing vs runtime API execution can be confused
Severity: Medium
Affected: Standard §1, §19; Matrix §1
Failure path: Manual review may be mistaken for runtime API qualification.
Why insufficient: Stated but no per-case execution-mode flag.
Narrow fix: Add mandatory execution-mode and API-call-prohibition metadata per case.
Falsification test: Attempt to qualify runtime case from manual-only evidence; require INSUFFICIENT_EVIDENCE.

MF-03 — GEL immutability lacks external anchoring
Severity: Medium
Affected: Standard §2.6, §8; Matrix WDPC-60
Failure path: Append-only ledger can be rewritten by privileged compromise.
Why insufficient: No Merkle root, checkpoint, or external anchor.
Narrow fix: Add hash-chain/Merkle checkpoint and external/witness anchor.
Falsification test: Attempt to rewrite R1_SELF_DRIFT_BLOCKED; require contradiction.

LF-01 — Duplicate but useful cases
Severity: Low
Affected: Matrix WDPC-47/72, WDPC-53/68
Failure path: Overlap may inflate qualification count.
Why insufficient: Not harmful but should be tracked.
Narrow fix: Mark duplicates as complementary, not independent.
Falsification test: Count unique enforcement paths only.

LF-02 — Some endpoint names lack owner clarity
Severity: Low
Affected: Matrix §3
Failure path: Cases may pass by prose.
Why insufficient: Owner not always named.
Narrow fix: Add owner field to endpoint vocabulary.
Falsification test: Endpoint without owner => INSUFFICIENT_EVIDENCE.

---

D. R1/WSA/DGV trust-boundary assessment

WSA is described as authoritative and R1 cannot directly write it. DGV is described as recomputing from WSA + PRR. However, the packet does not prove independent trust domains, signed WSA state, independent PRR policy evaluation, key-bound role identities, or a deterministic DGV algorithm. Because WSA/DGV/PRR may share infrastructure, R1-aligned or compromised shared infrastructure could collapse the trust boundary. The design is directionally correct but not yet independently enforceable.

---

E. WCE integrity/replay assessment

The WCE field list is useful, but incomplete. Missing: canonicalization algorithm, signing/MAC algorithm, key rotation/revocation, schema-version migration, nonce replay cache, sequence high-water mark, clock-skew policy, and exact supersession semantics. A forged/stale/wrong-workflow WCE can still reach consequential action if these are absent.

---

F. Disclosure + approval assessment

Disclosure and approval are correctly separated conceptually. MANUAL_GOVERNED timing is reasonably clear. AUTOMATIC_GOVERNED async disclosure correctly forbids a clean PASS while pending/failed. However, there is no signed delivery receipt, no strong wrong-recipient prevention, no async timeout/escalation rule, and no approval-object schema. “Eventually told” can still become a false green.

---

G. PRR / ChildImpact / downgrade authority assessment

PRR is named as the policy/role authority. ChildImpactRecord has many required fields. Downgrades require independent confirmation when a gate is removed. But the independent confirmer is not identity-bound, quorum-controlled, or separated by key/role. PARENT_UNAFFECTED requires dependency comparison, but the comparison is not formal. Self-grant remains possible through misconfigured PRR or incomplete dependency state.

---

H. R2/R3 isolation assessment

RCB’s allowed/prohibited field list is a good start. But there is no payload validation algorithm, source signature requirement, side-channel control, or independent leakage audit. REVIEW_CONTEXT_REJECTED_LEAKAGE is named but not mechanically specified. R2/R3 isolation is not yet enforceable.

---

I. EXP-K cross-standard boundary assessment

The standard correctly states that workflow recovery does not validate a claim and claim validation does not authorize a workflow transition. However, the joint incident schema, dual-disposition record, and explicit non-authorization mechanics are not specified enough to prevent one standard from assuming the other handled a joint failure.

---

J. WDPC-01..WDPC-75 audit

WDPC-01 — NEEDS_NARROWING — define NO_GOVERNED_TRANSITION schema and WSA graph digest proof.
WDPC-02 — NEEDS_NARROWING — define child edge schema and pause event binding.
WDPC-03 — NEEDS_NARROWING — define WSA root-proof and child lifecycle digest.
WDPC-04 — NEEDS_NARROWING — define formal candidate/evidence dependency graph.
WDPC-05 — NEEDS_NARROWING — define process-dependency comparison schema.
WDPC-06 — NEEDS_NARROWING — define PRR role/transition authority for constraint addition.
WDPC-07 — NEEDS_NARROWING — define reviewer contamination detection and stale-set schema.
WDPC-08 — NEEDS_NARROWING — define deterministic PARENT_UNAFFECTED comparison algorithm.
WDPC-09 — NEEDS_NARROWING — define missing-impact rejection schema and checkpoint proof.
WDPC-10 — NEEDS_NARROWING — define required affected-set schema and rejection endpoint.
WDPC-11 — NEEDS_NARROWING — define terminal-authority mapping and no-authority-effect endpoint.
WDPC-12 — NEEDS_NARROWING — define WSA reconstruction and client-memory authority-zero rule.
WDPC-13 — NEEDS_NARROWING — define cancellation binding schema and nonce/CAS rules.
WDPC-14 — NEEDS_NARROWING — define supersession binding and old-evidence non-rebind rule.
WDPC-15 — NEEDS_NARROWING — define graph-edge return schema and ancestor rejection.
WDPC-16 — NEEDS_NARROWING — define per-edge propagation schema.
WDPC-17 — NEEDS_NARROWING — define fencing-token issuance, expiry, and stale-writer rejection.
WDPC-18 — NEEDS_NARROWING — define in-flight request quarantine/validation policy.
WDPC-19 — NEEDS_NARROWING — define RCB leakage validation and contaminated-payload schema.
WDPC-20 — NEEDS_NARROWING — define adjudication gate binding to impact decision.
WDPC-21 — NEEDS_NARROWING — define in-flight result binding and stale-result rejection.
WDPC-22 — NEEDS_NARROWING — define repair authority and stale adjudication rejection.
WDPC-23 — NEEDS_NARROWING — define policy migration/rebind schema.
WDPC-24 — NEEDS_NARROWING — define authority-source dependency and affected-gate schema.
WDPC-25 — NEEDS_NARROWING — define child insufficient-evidence state limits.
WDPC-26 — NEEDS_NARROWING — define sibling independence schema.
WDPC-27 — NEEDS_NARROWING — define conflict-impact state and deterministic PRR rule.
WDPC-28 — NEEDS_NARROWING — define child instance/version immutability.
WDPC-29 — NEEDS_NARROWING — define parent-candidate change vs in-flight result rejection.
WDPC-30 — NEEDS_NARROWING — define WSA graph reconstruction from authoritative state.
WDPC-31 — NEEDS_NARROWING — define late-result quarantine and no-reactivation rule.
WDPC-32 — NEEDS_NARROWING — define idempotency/effect-dedup schema.
WDPC-33 — NEEDS_NARROWING — define wrong-workflow binding rejection.
WDPC-34 — NEEDS_NARROWING — define wrong-parent child creation rejection.
WDPC-35 — NEEDS_NARROWING — define approval replay/nonce/expiry schema.
WDPC-36 — NEEDS_NARROWING — define exact PRR transition set for automation.
WDPC-37 — NEEDS_NARROWING — define manual/auto race and authoritative sequence winner.
WDPC-38 — NEEDS_NARROWING — define external request/result lifecycle and dedup.
WDPC-39 — NEEDS_NARROWING — define provider qualification registry binding.
WDPC-40 — NEEDS_NARROWING — define UI-state authority-zero and governed-event boundary.
WDPC-41 — NEEDS_NARROWING — define WSA/GEL reconciliation policy and fail-closed source.
WDPC-42 — NEEDS_NARROWING — define impact-record replay/checkpoint binding.
WDPC-43 — NEEDS_NARROWING — define downgrade object, permission, confirmer, and history.
WDPC-44 — NEEDS_NARROWING — define information-only scope enforcement.
WDPC-45 — NEEDS_NARROWING — define graph depth/cycle policy and DGV check.
WDPC-46 — NEEDS_NARROWING — define timeout/escalation without no-impact conversion.
WDPC-47 — NEEDS_NARROWING — define unsupported-transport rejection and admin import boundary.
WDPC-48 — NEEDS_NARROWING — define device/session zero-authority rule.
WDPC-49 — NEEDS_NARROWING — define WCE barrier exposure and DGV self-drift proof.
WDPC-50 — NEEDS_NARROWING — define permitted-action-set recomputation and preserved proposal.
WDPC-51 — NEEDS_NARROWING — define disclosure gate object, timing, and wrong-recipient rejection.
WDPC-52 — NEEDS_NARROWING — define atomic async disclosure record and PENDING/Failed PASS prohibition.
WDPC-53 — NEEDS_NARROWING — define RCB source validation and prior-finding leakage rejection.
WDPC-54 — NEEDS_NARROWING — define PRR downgrade permission and R1 exclusion.
WDPC-55 — NEEDS_NARROWING — define dev checkpoint vs runtime WSA/PRR/GEL precedence.
WDPC-56 — NEEDS_NARROWING — define fallback activation, expiry, and no implicit inheritance.
WDPC-57 — NEEDS_NARROWING — define DGV positive acceptance and no false drift block.
WDPC-58 — NEEDS_NARROWING — define user-assertion non-authority and WSA gate precedence.
WDPC-59 — NEEDS_NARROWING — define oracle-leak detection and fixture discard rule.
WDPC-60 — NEEDS_NARROWING — define immutable RED history and no-retry-erasure proof.
WDPC-61 — NEEDS_NARROWING — define authorized downgrade positive schema and confirmer separation.
WDPC-62 — NEEDS_NARROWING — define information-only child scope and no-pause rule.
WDPC-63 — NEEDS_NARROWING — define non-blocking child policy and shared-dependency check.
WDPC-64 — NEEDS_NARROWING — define deterministic unaffected resume and checkpoint advance.
WDPC-65 — NEEDS_NARROWING — define WCE replay/supersession/key-revocation validation.
WDPC-66 — NEEDS_NARROWING — define disclosure recipient/workflow/checkpoint binding.
WDPC-67 — NEEDS_NARROWING — define separate approval object and acknowledgement non-approval rule.
WDPC-68 — NEEDS_NARROWING — define RCB minimum metadata schema and delivery record.
WDPC-69 — NEEDS_NARROWING — define old-policy late-result continuation/rebind rule.
WDPC-70 — NEEDS_NARROWING — define cancellation/supersession race and authoritative sequence.
WDPC-71 — NEEDS_NARROWING — define sibling impact aggregation and history retention.
WDPC-72 — NEEDS_NARROWING — define exceptional admin import qualification path.
WDPC-73 — NEEDS_NARROWING — define metadata/side-channel leak detection.
WDPC-74 — NEEDS_NARROWING — define cross-standard joint incident schema and dual non-authorization.
WDPC-75 — NEEDS_NARROWING — define process-only staleness dependency comparison.

---

K. Missing falsification cases

1. WCE key rotation/revocation replay after valid signature.
2. PRR registry compromise or self-granted policy entry.
3. RCB side-channel leakage via timing, metadata, or fixture naming.
4. DR delivery failure/timeout in async automatic mode.
5. WSA/GEL crash recovery and source reconciliation.
6. Fencing-token monotonicity across WSA restart.
7. Policy migration with in-flight child plus late external result.
8. Independent confirmer collusion/quorum bypass.
9. Endpoint claimed without required record schema/owner.
10. Manual review mistakenly counted as runtime API execution.
11. Cross-standard joint incident where workflow recovery attempts claim validation.
12. Positive control for normal WSA/DGV operation with no drift.
13. PARENT_UNAFFECTED with hidden dependency change.
14. Approval replay after policy rebind.
15. Disclosure delivered after approval capture in manual mode.
16. Child cancellation vs sibling completion race.
17. External request dedup after WSA restart.
18. R1 fallback expiry/revocation bypass.
19. GEL rewrite attempt by privileged actor.
20. PRR role revocation during in-flight transition.

---

L. Freeze recommendation

DO_NOT_FREEZE

---

M. Authority limitation

AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY