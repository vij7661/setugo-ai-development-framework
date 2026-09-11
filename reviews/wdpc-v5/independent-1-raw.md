A. Overall disposition

CHANGES_REQUIRED

The V5 packet is a design/preregistered falsification packet only. It is not runtime evidence. Several trust-boundary, root-of-trust, dependency-predicate, external-effect, fencing, reviewer-isolation, and anchor-completeness gaps remain material enough that V5 should not proceed unchanged to execution freeze.

---

B. Critical findings

C-01 — Bootstrap/root-of-trust gap for GovernanceKeyRegistry and PRR authority

· Severity: Critical
· Affected section/case: §3, §4.2, §15; WDPC-23, WDPC-77
· Concrete failure/false-green path: The packet defines append-only GovernanceKeyRegistry and signed PolicySnapshot, but never defines the initial root authority, bootstrap ceremony, threshold, or independent governance path that authorizes the first registry/policy. A single bootstrap actor could seed keys/policies that later self-authorize.
· Why V5 insufficient: Separate service identities do not solve the initial trust problem. PRR policy changes are said to require a separately authorized governance path, but that path is not specified.
· Narrow required fix: Define an out-of-band root governance authority, threshold activation, initial registry attestation, and explicit prohibition on R1/DGV/WSA bootstrapping their own authority.
· Exact falsification test: Attempt to activate an initial PRR PolicySnapshot granting R1 downgrade/terminal authority using only bootstrap credentials; expected rejection with signed root-authority proof absent.

C-02 — Shared infrastructure/credential compromise can collapse WSA/DGV/PRR separation

· Severity: Critical
· Affected section/case: §2; WDPC-77, WDPC-83
· Concrete failure/false-green path: “Separate service identities + non-overlapping credentials + distinct signing-key handles” is not sufficient if one administrator, HSM domain, container orchestrator, or cloud root can use all three. A single compromise could write WSA state, PRR policy, and DGV decisions.
· Why V5 insufficient: The standard says shared process/container does not satisfy independence if one principal can write all three, but does not require independent administrative domains, hardware-backed separation, quorum, or split knowledge.
· Narrow required fix: Require independent administrative authority domains, HSM/key-use policy separation, and threshold/quorum for any operation that spans WSA/DGV/PRR authority.
· Exact falsification test: Compromise one infrastructure principal and attempt to produce an ALLOW decision plus WSA transition plus PRR policy mutation; expected signed INSUFFICIENT_EVIDENCE or DENY.

C-03 — WCE nonce and DGV decision nonce atomicity across crash/restart is incomplete

· Severity: Critical
· Affected section/case: §5, §8; WDPC-65, WDPC-80
· Concrete failure/false-green path: WCE nonce is consumed atomically with the DGV decision record, but WSA accepts a transition only with an unused decision nonce. If DGV persists a decision and WSA crashes before commit, replay or duplicate evaluation may occur unless the decision-consumption protocol is transactionally bound across DGV/WSA.
· Why V5 insufficient: The packet specifies atomic consumption inside DGV, but not the atomic protocol between DGV decision persistence, WSA acceptance, and restart recovery.
· Narrow required fix: Define a durable idempotent decision nonce ledger, WSA/DGV transaction or outbox, and recovery rule that rejects duplicate decision nonces after crash.
· Exact falsification test: Crash between DGV decision persistence and WSA commit, restart both, replay same WCE/decision; expected no second effect and signed CONTEXT_ENVELOPE_REJECTED or idempotent no-op.

C-04 — Dependency predicates can be policy-owner manipulated to produce false PARENT_UNAFFECTED

· Severity: Critical
· Affected section/case: §6, §10; WDPC-04, WDPC-08, WDPC-75, WDPC-88
· Concrete failure/false-green path: Every edge has a validation predicate and policy owner. A policy owner could define predicates that classify material dependency changes as UNCHANGED_VALID or omit material edges, allowing PARENT_UNAFFECTED.
· Why V5 insufficient: The packet requires predicates and materiality flags, but does not define who independently authorizes predicate definitions/versions or how predicate soundness is falsified.
· Narrow required fix: Add independent predicate-definition authorization, versioned predicate registry, materiality quorum, and adversarial predicate-omission tests.
· Exact falsification test: Insert a changed candidate dependency while owner-authorized predicate falsely returns unaffected; expected DGV graph traversal and independent predicate audit reject PARENT_UNAFFECTED.

C-05 — External effect idempotency is not transactionally bound to provider side effects

· Severity: Critical
· Affected section/case: §14; WDPC-32, WDPC-38, WDPC-92
· Concrete failure/false-green path: The lifecycle permits at most one governance effect via unique effect record, but an external provider side effect may occur before the effect record is reconciled. Retry after crash can duplicate the external side effect.
· Why V5 insufficient: “Unique persistent constraint on (workflow_id, intent_idempotency_key)” prevents duplicate intents, but not duplicate provider effects unless the provider itself is idempotent or a two-phase reservation exists.
· Narrow required fix: Require effect reservation before dispatch, provider idempotency keys, and transactional/outbox reconciliation for external side effects.
· Exact falsification test: Dispatch external request, crash after provider success but before effect record, restart and retry same intent; expected exactly one external side effect or signed EXTERNAL_EFFECT_DEDUPLICATED with proof.

C-06 — Fencing monotonicity under split brain/consensus is unspecified

· Severity: Critical
· Affected section/case: §16; WDPC-17, WDPC-37, WDPC-70, WDPC-81, WDPC-91
· Concrete failure/false-green path: WSA maintains a durable monotonic fencing counter, but no consensus protocol or single-writer leader requirement is specified. Under network partition, two WSA replicas could issue equal or conflicting tokens.
· Why V5 insufficient: “Durable monotonic” is not sufficient under replication/split brain unless backed by linearizable consensus or quorum lease.
· Narrow required fix: Require linearizable consensus or quorum-fenced single-writer authority for fencing token issuance and commit.
· Exact falsification test: Partition WSA replicas, issue two mutations with claimed tokens n+1; expected one winner and one STALE_WORKFLOW_WRITER_REJECTED, with no dual commit.

C-07 — Reviewer isolation relies on provenance tags that a compromised producer can forge

· Severity: Critical
· Affected section/case: §13; WDPC-07, WDPC-19, WDPC-53, WDPC-68, WDPC-78
· Concrete failure/false-green path: The forbidden-origin scan checks provenance tags/field classes, not semantic guessing. If the producer of context or artifact payload is compromised, it can lie about provenance and leak prior findings.
· Why V5 insufficient: RCB schema whitelisting helps, but does not independently attest that the payload did not originate from prohibited prior-review content.
· Narrow required fix: Require independently signed provenance/attestation, payload origin verification, and adversarial forged-tag tests.
· Exact falsification test: Submit prohibited prior finding with a forged allowed provenance tag; expected REVIEW_CONTEXT_REJECTED_LEAKAGE or INSUFFICIENT_TEST_INDEPENDENCE.

C-08 — WAS anchoring does not prove historical completeness, only consistency of anchored subsets

· Severity: Critical
· Affected section/case: §18; WDPC-94
· Concrete failure/false-green path: Before first anchor or between anchor intervals, a privileged actor can rewrite recent GEL records. An anchor proves a Merkle root for a batch, not that all historical events were included.
· Why V5 insufficient: The packet does not require continuous anchoring, inclusion proofs for every event, or coverage attestations.
· Narrow required fix: Require continuous or bounded-interval anchoring, per-event inclusion proofs, and anchor coverage that proves no unanchored authoritative history exists.
· Exact falsification test: Rewrite an unanchored recent R1_SELF_DRIFT_BLOCKED event before next anchor; expected LEDGER_ANCHOR_MISMATCH or INSUFFICIENT_EVIDENCE.

C-09 — Dual-control quorum lacks organizational/benefit independence

· Severity: Critical
· Affected section/case: §9; WDPC-43, WDPC-54, WDPC-61, WDPC-83
· Concrete failure/false-green path: Two distinct principals/keys can still be aliases, service accounts, or controlled by same organizational authority or beneficiary. R1/proposer exclusion is necessary but not sufficient.
· Why V5 insufficient: “Distinct principals” does not prove independent control, no shared benefit, or no shared revocation authority.
· Narrow required fix: Require signed organizational independence/conflict declarations, alias/service-account resolution, and beneficiary-conflict checks.
· Exact falsification test: Use two keys controlled by same principal/org alias; expected RELATIONSHIP_DOWNGRADE_REJECTED and INSUFFICIENT_EVIDENCE.

C-10 — Cross-standard EXP-K boundary flags are self-asserted

· Severity: Critical
· Affected section/case: §20; WDPC-74, WDPC-86
· Concrete failure/false-green path: workflow_authorizes_claim=false and claim_authorizes_workflow=false can be set by the same authority or shared infrastructure. Workflow recovery could still indirectly rely on claim status.
· Why V5 insufficient: The record binds separate dispositions, but does not require independently signed authority from both standards or a shared-authority separation proof.
· Narrow required fix: Require separate signing authorities for workflow and claim dispositions, no shared keys, and explicit non-inference verification.
· Exact falsification test: Workflow authority sets both flags false while using EXP-K claim status to advance; expected cross-standard linkage rejection or INSUFFICIENT_EVIDENCE.

---

C. High / Medium / Low findings

H-01 — Endpoint registry incomplete for matrix endpoints

· Severity: High
· Affected section/case: §19; WDPC-06, WDPC-18, WDPC-27, WDPC-46, WDPC-82
· Failure path: Endpoints such as PARENT_CONSTRAINT_ADDED, conflict-blocked states, and policy-qualified timeout resolution appear in cases but are not all listed with owner/payload in §19.
· Why insufficient: An endpoint claimed without owner-signed required record is INSUFFICIENT_EVIDENCE, but missing registry entries prevent deterministic owner binding.
· Narrow fix: Add every matrix endpoint to the signed event registry with owner, payload schema, and reason codes.
· Falsification: WDPC-06 with only prose PARENT_CONSTRAINT_ADDED and no owner-signed event; expected INSUFFICIENT_EVIDENCE.

H-02 — AUTOMATIC_GOVERNED async disclosure can progress before actual delivery

· Severity: High
· Affected section/case: §11.1; WDPC-52, WDPC-79
· Failure path: If async_disclosure_allowed=true, transition and disclosure record commit atomically, but delivery may remain pending until max_delivery_age. This can create a temporary false green for material drift.
· Why insufficient: The packet correctly forbids reporting pending as PASS, but allows progression before delivery if policy permits. Product semantics may not allow that for material drift.
· Narrow fix: Restrict async-before-delivery to explicitly non-material transitions or require escrowed/conditional effect activation until delivery or timeout escalation.
· Falsification: WDPC-79 variant where transition commits and disclosure times out; expected no unqualified progression or explicit PRR escalation proof.

H-03 — Approval session assurance downgrade/replay not fully bounded

· Severity: High
· Affected section/case: §11.2; WDPC-35, WDPC-89, WDPC-90
· Failure path: Approval binds session assurance level, but the packet does not define minimum assurance enforcement, downgrade detection, or replay after session compromise.
· Why insufficient: Expired/replayed/wrong-action approvals are rejected, but session assurance downgrade is not a first-class falsification target.
· Narrow fix: Bind minimum assurance to action class and reject approval if assurance drops before final DGV/WSA commit.
· Falsification: Capture approval under high assurance, downgrade session, commit action; expected denial.

H-04 — Positive controls may not detect broad overblocking

· Severity: High
· Affected section/case: §8 of matrix; WDPC-13, 14, 57, 61, 62, 63, 64, 68, 87
· Failure path: A system could pass positive controls by allowing only those exact narrow paths while blocking many legitimate normal-operation variants.
· Why insufficient: The positive set is small and does not include high-volume, partial-failure, legitimate edge-case, or recovery-positive controls.
· Narrow fix: Add normal-operation positive controls for concurrent legitimate actions, late-but-valid results under policy, approved migrations, and non-material disclosures.
· Falsification: Run a broad normal-operation suite; expected no false R1_SELF_DRIFT_BLOCKED, R1_UNAVAILABLE_BLOCKED, or disclosure gate failures for valid operations.

H-05 — Schema migration/version downgrade bypass not fully addressed

· Severity: High
· Affected section/case: §3, §15; WDPC-23, WDPC-69, WDPC-82
· Failure path: Old schema versions may re-enable bypass if not explicitly rejected for new consequential use.
· Why insufficient: Supported schema version is checked, but migration/continuation rules do not clearly prohibit old-schema WCE/approval/impact objects.
· Narrow fix: Add explicit schema-version sunset and downgrade rejection rules.
· Falsification: Replay old-schema WCE after policy upgrade; expected CONTEXT_ENVELOPE_REJECTED.

M-01 — Clock skew tolerance undefined

· Severity: Medium
· Affected section/case: §5
· Failure path: “expired beyond policy clock-skew tolerance” leaves tolerance unspecified. Delayed delivery could look valid.
· Why insufficient: Sequence/digest equality is mandatory, which helps, but clock skew still affects expiry and disclosure timing.
· Narrow fix: Define bounded skew, signed time, and sequence-based freshness precedence.
· Falsification: Delayed WCE within/outside skew; expected deterministic accept/reject.

M-02 — Policy migration implicit defaults not fully prohibited in all objects

· Severity: Medium
· Affected section/case: §15; WDPC-69, WDPC-82, WDPC-89
· Failure path: “No implicit default migration” is stated, but approvals/disclosures/impact records may still be reused if not explicitly rebound.
· Why insufficient: The exact rebind classes exist, but binding checks across all object types are not enumerated.
· Narrow fix: Require explicit rebind decision for every in-flight object class.
· Falsification: Reuse approval after rebind without explicit preservation; expected rejection.

M-03 — Test governor hidden oracle independence is asserted, not proven

· Severity: Medium
· Affected section/case: §3 of matrix; WDPC-59, WDPC-73
· Failure path: System under test could influence fixture/oracle if governor shares infrastructure or data.
· Why insufficient: Hidden oracle and opaque handles are required, but independence proof is not specified.
· Narrow fix: Require independent oracle signing authority and leakage attestation.
· Falsification: Tamper with fixture metadata to reveal expected endpoint; expected INSUFFICIENT_TEST_INDEPENDENCE.

L-01 — Duplicate-path accounting needs a minimum independent-mechanism metric

· Severity: Low
· Affected section/case: §9 of matrix
· Failure path: Raw case count could inflate confidence despite duplicate enforcement paths.
· Why insufficient: The matrix acknowledges duplicate accounting but does not require a minimum unique-mechanism threshold.
· Narrow fix: Define unique enforcement path metric and minimum independent mechanism coverage.
· Falsification: Execute duplicate cases only; expected no qualification credit for repeated path.

---

D. WSA/DGV/PRR trust-boundary assessment

The intended separation is directionally correct: R1 cannot write WSA/PRR/DGV, DGV can read but not mutate policy/state, and WSA validates DGV decisions. However, the separation is not sufficient as designed. The packet lacks a bootstrap/root-of-trust model, independent administrative domains, and a cross-service transaction protocol for WCE/decision nonce consumption. Shared infrastructure compromise can still collapse the three authorities. The trust boundary should be considered NEEDS_NARROWING before execution freeze.

E. GovernanceKeyRegistry / WCE cryptographic assessment

RFC8785 + SHA-256 + Ed25519 is a reasonable base. Key registry object-type scoping and historical verification are good. The main gaps are bootstrap authority, revocation timing at final commit, schema-version sunset, and atomic WCE/decision nonce consumption across DGV/WSA crash/restart. WCE replay/freshness is stronger because sequence/digest equality is mandatory, but the transaction protocol is incomplete.

F. Dependency graph / ChildImpact assessment

The formal graph, reverse closure, staleness classes, and PARENT_UNAFFECTED closure requirement are valuable. The critical weakness is predicate authorization and materiality manipulation. Policy owners can define predicates that mark material dependencies unaffected. ChildImpactRecord is well bound, but its correctness depends on graph completeness and predicate soundness. This area requires independent predicate governance and adversarial omission tests.

G. Downgrade/quorum assessment

The dual-control rule correctly excludes R1/proposer/beneficiary as sole confirmer. However, “distinct principals/keys” is not enough to prove organizational independence. Aliases, service accounts, shared controllers, or common revocation authority can defeat quorum. Add conflict-of-interest attestation and alias resolution.

H. Disclosure + approval assessment

Disclosure and approval are correctly separated. MANUAL_GOVERNED requires delivery before approval/transition. AUTOMATIC_GOVERNED async disclosure correctly forbids pending/failed/timeout being reported as PASS, but it may still allow transition before actual delivery. For material drift, that may be a false-green risk unless policy restricts async-before-delivery to non-material transitions or enforces escalation. Approval binding is generally strong, but session assurance downgrade is not fully addressed.

I. RCB reviewer-isolation assessment

The whitelist schema, additionalProperties=false, opaque handles, and provenance scan are good design controls. They do not block a compromised producer from lying about provenance tags. Timing/provider metadata side channels are acknowledged but not fully solved. RCB isolation is NEEDS_NARROWING until independent provenance attestation and forged-tag tests are added.

J. External request / idempotency / fencing assessment

The lifecycle and unique intent/effect constraints are good, but external side effects are not transactionally bound before dispatch. Duplicate provider effects can occur before effect reconciliation. Fencing token monotonicity is asserted but not backed by specified consensus/quorum under split brain. This area is NEEDS_NARROWING.

K. WSA/GEL/WAS recovery and tamper-evidence assessment

The WSA/GEL atomicity/outbox rule is directionally correct. However, WAS anchoring proves consistency of anchored subsets, not historical completeness. Before first anchor or between intervals, privileged rewrite may go undetected. Witness-store independence is not fully specified. Add continuous anchoring, inclusion proofs, and coverage attestation.

L. Manual-vs-runtime evidence-class assessment

The packet correctly distinguishes DESIGN_MANUAL_REVIEW, RUNTIME_SIMULATION, and RUNTIME_IMPLEMENTATION. Manual review cannot grant runtime PASS. This is a strong point. However, the overall packet is still design-only; no runtime enforcement evidence exists. Any runtime PASS claim from this packet is INSUFFICIENT_EVIDENCE.

M. Positive-control / overblocking assessment

The positive controls are useful but insufficient to detect broad overblocking. They cover a few important paths but not high-volume normal operation, legitimate edge cases, partial failures, or recovery-positive paths. Add more normal-operation positive controls and a unique-mechanism coverage metric.

N. Cross-standard EXP-K boundary assessment

The CrossStandardIncidentRecord is a good start, but the non-authorization flags are self-asserted. Without independent signing authorities for workflow and claim dispositions, the linkage can still create circular or shared authority. This area requires independent authority separation proof.

---

O. WDPC-01..WDPC-95 audit

Note: Classifications assess the preregistered case specification, not runtime execution. Runtime PASS for any case remains INSUFFICIENT_EVIDENCE until executed under the required evidence class.

· WDPC-01 — ADEQUATE
· WDPC-02 — ADEQUATE
· WDPC-03 — ADEQUATE
· WDPC-04 — NEEDS_NARROWING: add predicate-definition authorization and adversarial omitted-edge fixture.
· WDPC-05 — NEEDS_NARROWING: add predicate-owner self-grant test for process-only staleness.
· WDPC-06 — NEEDS_NARROWING: PARENT_CONSTRAINT_ADDED lacks registry owner/payload binding.
· WDPC-07 — NEEDS_NARROWING: add forged-provenance-tag contamination fixture.
· WDPC-08 — NEEDS_NARROWING: add hidden-dependency omission test for closure completeness.
· WDPC-09 — ADEQUATE
· WDPC-10 — ADEQUATE
· WDPC-11 — ADEQUATE
· WDPC-12 — ADEQUATE
· WDPC-13 — ADEQUATE
· WDPC-14 — ADEQUATE
· WDPC-15 — ADEQUATE
· WDPC-16 — ADEQUATE
· WDPC-17 — NEEDS_NARROWING: add split-brain/consensus fencing fixture.
· WDPC-18 — ADEQUATE
· WDPC-19 — NEEDS_NARROWING: forged provenance tag bypass not covered.
· WDPC-20 — ADEQUATE
· WDPC-21 — ADEQUATE
· WDPC-22 — ADEQUATE
· WDPC-23 — NEEDS_NARROWING: add root-of-trust/bootstrap test for PRR rebind.
· WDPC-24 — ADEQUATE
· WDPC-25 — ADEQUATE
· WDPC-26 — ADEQUATE
· WDPC-27 — NEEDS_NARROWING: conflict-blocked endpoint not registry-bound.
· WDPC-28 — ADEQUATE
· WDPC-29 — ADEQUATE
· WDPC-30 — ADEQUATE
· WDPC-31 — ADEQUATE
· WDPC-32 — NEEDS_NARROWING: add external side-effect-before-effect-record fixture.
· WDPC-33 — ADEQUATE
· WDPC-34 — ADEQUATE
· WDPC-35 — ADEQUATE
· WDPC-36 — ADEQUATE
· WDPC-37 — NEEDS_NARROWING: add split-brain manual/automatic race.
· WDPC-38 — NEEDS_NARROWING: duplicate external side effects not fully tested.
· WDPC-39 — ADEQUATE
· WDPC-40 — ADEQUATE
· WDPC-41 — ADEQUATE
· WDPC-42 — ADEQUATE
· WDPC-43 — NEEDS_NARROWING: add organizational independence/alias quorum fixture.
· WDPC-44 — ADEQUATE
· WDPC-45 — ADEQUATE
· WDPC-46 — NEEDS_NARROWING: define exact policy-qualified resolution endpoint.
· WDPC-47 — ADEQUATE
· WDPC-48 — ADEQUATE
· WDPC-49 — ADEQUATE
· WDPC-50 — ADEQUATE
· WDPC-51 — ADEQUATE
· WDPC-52 — ADEQUATE
· WDPC-53 — ADEQUATE
· WDPC-54 — NEEDS_NARROWING: add quorum organizational independence test.
· WDPC-55 — ADEQUATE
· WDPC-56 — ADEQUATE
· WDPC-57 — ADEQUATE
· WDPC-58 — ADEQUATE
· WDPC-59 — ADEQUATE
· WDPC-60 — ADEQUATE
· WDPC-61 — NEEDS_NARROWING: add independent-confirmer organizational test.
· WDPC-62 — ADEQUATE
· WDPC-63 — ADEQUATE
· WDPC-64 — ADEQUATE
· WDPC-65 — ADEQUATE
· WDPC-66 — ADEQUATE
· WDPC-67 — ADEQUATE
· WDPC-68 — NEEDS_NARROWING: provenance-tag trust gap.
· WDPC-69 — ADEQUATE
· WDPC-70 — NEEDS_NARROWING: add split-brain fencing fixture.
· WDPC-71 — ADEQUATE
· WDPC-72 — ADEQUATE
· WDPC-73 — ADEQUATE
· WDPC-74 — NEEDS_NARROWING: cross-standard flags self-asserted.
· WDPC-75 — NEEDS_NARROWING: predicate-authority and blanket-preservation boundary.
· WDPC-76 — ADEQUATE
· WDPC-77 — NEEDS_NARROWING: root/bootstrap self-grant path.
· WDPC-78 — NEEDS_NARROWING: metadata side-channel and provenance trust.
· WDPC-79 — ADEQUATE
· WDPC-80 — ADEQUATE
· WDPC-81 — NEEDS_NARROWING: split-brain/consensus fencing.
· WDPC-82 — ADEQUATE
· WDPC-83 — NEEDS_NARROWING: aliases/service accounts/org independence.
· WDPC-84 — ADEQUATE
· WDPC-85 — ADEQUATE
· WDPC-86 — NEEDS_NARROWING: self-asserted cross-standard flags.
· WDPC-87 — ADEQUATE
· WDPC-88 — NEEDS_NARROWING: predicate/graph omission and materiality manipulation.
· WDPC-89 — ADEQUATE
· WDPC-90 — ADEQUATE
· WDPC-91 — NEEDS_NARROWING: split-brain fencing under sibling race.
· WDPC-92 — NEEDS_NARROWING: external side-effect transaction after restart.
· WDPC-93 — ADEQUATE
· WDPC-94 — NEEDS_NARROWING: unanchored recent-record rewrite interval.
· WDPC-95 — ADEQUATE

---

P. Missing falsification cases

Before V5 could be frozen for execution, add at least:

1. Root-of-trust/bootstrap compromise test for GovernanceKeyRegistry and PRR.
2. Single-infrastructure/credential compromise spanning WSA/DGV/PRR.
3. WCE/DGV decision nonce atomic crash/restart test.
4. Dependency predicate owner self-grant and predicate omission test.
5. External provider side-effect exactly-once test under crash before effect record.
6. Split-brain fencing token issuance and commit test.
7. Cross-standard flag forgery and independent authority separation test.
8. WAS unanchored interval and historical completeness test.
9. Forged reviewer provenance tag and metadata side-channel test.
10. Quorum organizational independence, alias, and service-account test.
11. Schema downgrade/old-schema WCE/approval/impact replay test.
12. Clock-skew and delayed WCE freshness test.
13. Approval session assurance downgrade test.
14. Disclosure acknowledgement versus approval confusion test.
15. Broader normal-operation positive-control suite for overblocking detection.

---

Q. Freeze recommendation

DO_NOT_FREEZE

---

R. Authority limitation

AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY