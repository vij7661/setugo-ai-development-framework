# R8 Meta-Governance Redesign — Preregistered Contract

Status: **PREREGISTERED_DESIGN — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**

Authority effect: **NONE**

Parent adjudication:
- `review-adjudications/GOVERNANCE-HOLISTIC-R1-R3-CONSOLIDATED.md`
- commit `0c14c5e98ad0e98545f0e5586e2f89751167b069`

## 1. Objective

Replace prose-only or caller-controlled governance assumptions with explicit deterministic authority mechanisms that close the consolidated R1/R3 false-green classes.

R8 is a meta-governance layer. It governs who may define rules, classify materiality, define review requirements, mint/revoke authority, compose project policy, resume interrupted work, ingest evidence, and perform governed recovery.

R8 does not itself grant release, merge, deploy, production, qualification, or terminal authority.

## 2. Load-bearing components

1. Meta-Governor / Authority Decision Engine
2. Platform Invariant Registry
3. Review Requirement & Dimension Authority
4. Governance Impact / Materiality Classifier
5. Authenticated Authority Issuer Registry
6. Authority Revocation Registry
7. Policy Registry
8. Deterministic Policy Composition Engine
9. Effective Governance Snapshot
10. Integrity-Bound Continuity Checkpoint
11. Evidence Provenance / Ingestion State Machine
12. Recovery / Migration / Revocation Protocol
13. Authoritative Reference / History Integrity Guard
14. Structural Reviewer Isolation Boundary

## 3. Frozen invariants

### R8-I01 — Meta-governor is the authority boundary
No model, proposer, reviewer, user-authored document, telemetry record, chat message, or policy text may directly grant a governed transition. Material transitions require a deterministic Meta-Governor decision over verified inputs.

### R8-I02 — Stable platform invariant registry
Every non-overridable or overridable platform invariant has:
- stable invariant ID;
- version;
- scope;
- semantic requirement;
- enforcement owner;
- overridable boolean;
- override authority class when overridable;
- retirement/supersession metadata.

Absence of an explicit overridable declaration means non-overridable.

### R8-I03 — Policy authorship is not authority
Writing platform/org/project/experiment policy does not grant qualification or terminal authority.

### R8-I04 — Policy-layer RBAC
Policy writes require an authenticated actor/capability authorized for the exact policy layer and scope. Lower-level actors cannot write higher-level policy.

### R8-I05 — Deterministic policy composition
For identical ordered authenticated policy inputs and invariant registry version, composition returns byte-identical effective policy output.

### R8-I06 — Fail-closed conflicts
Ambiguous, incompatible, cyclic, or mutually impossible policy requirements produce `POLICY_CONFLICT`; no permissive tie-break is inferred.

### R8-I07 — Effective Governance Snapshot binding
Every governed candidate is bound to an immutable Effective Governance Snapshot containing all contributing policy identities, invariant registry version, composition result, actor authorization evidence, and snapshot digest.

### R8-I08 — Policy drift invalidates stale evidence
Evidence/review produced under policy snapshot A cannot authorize candidate under materially different policy snapshot B without the defined migration/revalidation path.

### R8-I09 — Review dimensions are platform-derived
Material ReviewRequest dimensions and mandatory flags are derived from effective policy/invariant rules, not proposer choice.

### R8-I10 — Non-vacuous material review
Every material ReviewRequest has at least one mandatory dimension and all policy-required dimensions. Zero mandatory dimensions is invalid.

### R8-I11 — Mandatory dimension cannot be downgraded
A proposer, reviewer, project owner, or lower-level policy cannot mark a platform-required mandatory dimension optional.

### R8-I12 — Self-review prohibited
The authenticated proposer/constructor identity cannot satisfy an independent-review slot for the same governed candidate where independence is required.

### R8-I13 — Reviewer isolation is structural
Independent reviewer executions use separately instantiated contexts with no prior reviewer substantive findings unless a preregistered cross-review stage explicitly authorizes sharing.

### R8-I14 — Review assertions are evidence, not proof
Reviewer self-report of inspection does not independently prove inspection. Promotion consumes inspectable evidence references, exact artifact binding, execution provenance, deterministic contradiction checks, and applicable independent coverage rules.

### R8-I15 — Materiality classification is deterministic
Governance impact/materiality is derived from changed governed objects, declared schemas, policy/invariant dependencies, and authority-bearing effects. Caller labels cannot lower classification.

### R8-I16 — Unknown authority-bearing change fails closed
A changed object that participates in governance but is not recognized by the classifier cannot silently default to routine/non-material.

### R8-I17 — Authenticated authority issuer
Terminal/root authority records require authenticated issuer identity or a separately qualified deterministic platform-policy issuer. A self-declared `HUMAN` string is insufficient.

### R8-I18 — PLATFORM_POLICY is narrowly scoped
Composed project/org/experiment policy cannot itself act as terminal authority. A `PLATFORM_POLICY` terminal issuer, if supported, must be separately registered and qualified as a deterministic authority issuer with exact allowed conditions.

### R8-I19 — Authority minting is explicit
Only an authenticated issuer authorized for exact authority class/scope may mint an authority record.

### R8-I20 — Revocation dominates use
Authority status is checked at use time. Revoked/suspended/expired authority cannot authorize a new terminal action or mutating retry.

### R8-I21 — Anti-replay binding
Authority records bind issuer, subject/project, task/effect where applicable, action, artifact, state version, policy snapshot, issue sequence/time, expiry, and nonce/idempotency identity.

### R8-I22 — Cross-scope replay rejected
Evidence/review/authority from project/task/effect A cannot authorize project/task/effect B merely because artifact SHA/action match.

### R8-I23 — Integrity-bound continuity checkpoint
Authoritative continuation fields, including phase, next action, pending gates, policy snapshot, candidate identity, and sequence/predecessor, are covered by an integrity binding anchored in authoritative storage.

### R8-I24 — Authoritative bootstrap before advisory memory
Session/resumption establishes authoritative checkpoint/evidence first. Advisory memory/chat may assist navigation only after authority is grounded.

### R8-I25 — Handoff conflict has deterministic resolution state
If handoff next action conflicts with authoritative evidence/policy, enter `CONTINUITY_CONFLICT` / `GROUNDING_REQUIRED`; do not execute either side until governed resolution is recorded.

### R8-I26 — Reviewer barriers survive interruption
Pending review set, reviewer isolation, artifact binding, and approval scope survive chat/device/session/model changes.

### R8-I27 — Authoritative history cannot depend on movable refs alone
Previously authoritative evidence is anchored by immutable object identities and/or an append-only external ledger/anchor sufficient to detect ref/history substitution.

### R8-I28 — Portable packet origin is typed
Portable packets have explicit producer/origin attestation when available. Self-manifest integrity does not authenticate origin. Unauthenticated packet remains external evidence only.

### R8-I29 — Evidence ingestion is a closed state machine
Each evidence class has defined allowed transitions and allowed uses. Telemetry success cannot become review PASS; user-attested external evidence cannot become authenticated platform review without a separately governed provenance transition.

### R8-I30 — Recovery is governed
Emergency recovery, migration, root/credential loss, reviewer unavailability, and store failure have explicit states, authorized recovery actors, evidence requirements, and audit history. No ad hoc bypass may weaken non-overridable invariants.

### R8-I31 — Blocked states are observable
Long-lived `GROUNDING_REQUIRED`, `POLICY_CONFLICT`, reviewer-unavailable, revocation, and recovery states produce externally observable status/alert evidence.

### R8-I32 — Bounded references cannot be promoted by implication
Reference/local mechanisms may not be described or consumed as production authentication, IAM, KMS, external-provider, or terminal-enforcement proof unless separately qualified for that claim.

## 4. Frozen decision states

At minimum:
- `ALLOW_NON_AUTHORITY_WORK`
- `REVIEW_REQUIRED`
- `HUMAN_REQUIRED`
- `DENY_POLICY`
- `POLICY_CONFLICT`
- `DENY_REVIEW_CONTRACT`
- `DENY_REVIEW_INDEPENDENCE`
- `DENY_AUTHORITY_ISSUER`
- `DENY_AUTHORITY_REVOKED`
- `DENY_SCOPE_REPLAY`
- `CONTINUITY_CONFLICT`
- `GROUNDING_REQUIRED`
- `RECOVERY_REQUIRED`
- `TERMINAL_AUTHORITY_REQUIRED`
- `AUTHORIZED_FOR_BOUND_ACTION`

No state except a separately qualified terminal gate may authorize merge/release/deploy/completion.

## 5. Preregistered falsification matrix

### Review-policy attacks
- R8-01 zero mandatory dimensions on material ReviewRequest -> reject.
- R8-02 omit one platform-required review dimension -> reject.
- R8-03 proposer marks mandatory dimension optional -> reject.
- R8-04 proposer equals independent reviewer -> reject.
- R8-05 reviewer B receives reviewer A findings in blind stage -> reject/isolation violation.
- R8-06 review says TESTED_SUPPORTED but evidence ref is absent/wrong artifact -> non-promotable.
- R8-07 BOUNDED_PASS with all mandatory dimensions untested -> reject.

### Materiality/classification attacks
- R8-08 caller labels governance change ROUTINE_FORMATTING -> material classification preserved.
- R8-09 governance-bearing file outside known path prefixes -> still classified by dependency/registry.
- R8-10 unknown authority-bearing object type -> fail closed.

### Policy-composition attacks
- R8-11 project disables platform-required review -> reject.
- R8-12 project enables self-approval -> reject.
- R8-13 project lowers mandatory threshold -> reject.
- R8-14 unauthorized project actor writes org/platform policy -> reject.
- R8-15 override invariant without overridable tag -> reject.
- R8-16 authorized override of explicitly overridable rule -> exact audited result.
- R8-17 same-level mutually incompatible stricter rules -> POLICY_CONFLICT.
- R8-18 identical ordered policy inputs -> identical snapshot.
- R8-19 policy snapshot changes after evidence -> prior evidence stale.
- R8-20 evidence from policy A presented under B -> reject.

### Terminal/root-authority attacks
- R8-21 self-declared HUMAN with valid content hash but no authenticated issuer -> reject.
- R8-22 project composed policy used as PLATFORM_POLICY terminal issuer -> reject.
- R8-23 unregistered deterministic platform-policy issuer -> reject.
- R8-24 authority revoked after issuance before use -> reject.
- R8-25 authority replayed for new artifact/action/state -> reject.
- R8-26 authority from project A replayed in B -> reject.
- R8-27 valid authority record but issuer scope excludes action -> reject.

### Continuity attacks
- R8-28 alter next_required_action without valid checkpoint integrity -> reject/conflict.
- R8-29 memory says PASS, checkpoint says review pending -> checkpoint/policy wins.
- R8-30 checkpoint says merge, evidence says review pending -> CONTINUITY_CONFLICT.
- R8-31 policy version changes during interruption -> explicit migration/rebind required.
- R8-32 partial reviewer set after session switch -> review barrier preserved.
- R8-33 prior reviewer findings leak into blind reviewer context -> isolation violation.

### History/provenance attacks
- R8-34 authoritative branch/ref rewritten after accepted evidence -> detect lineage substitution.
- R8-35 portable packet self-manifest valid but producer origin unauthenticated -> remains external evidence.
- R8-36 tampered packet plus recomputed self-manifest -> cannot become platform-authenticated review.
- R8-37 old external evidence replayed against new candidate -> reject.

### Evidence/telemetry attacks
- R8-38 provider telemetry SUCCESS used as review PASS -> reject.
- R8-39 user-attested external LLM review used as authenticated platform review -> reject.
- R8-40 evidence class transitions without authorized ingestion event -> reject.

### Recovery/availability attacks
- R8-41 zero qualified reviewers available -> observable blocked state, no bypass.
- R8-42 authority issuer credential/root lost -> RECOVERY_REQUIRED, no self-issued replacement.
- R8-43 continuity store unavailable while authoritative store valid -> governed degraded path only.
- R8-44 authoritative store unavailable -> fail closed unless prequalified recovery policy applies.
- R8-45 recovery actor attempts to weaken non-overridable invariant -> reject.

## 6. Construction order

1. Independently review this preregistered R8 design before implementation.
2. Freeze R8-01..R8-45 expectations.
3. Implement the minimal deterministic meta-governor and registries.
4. Preserve first RED evidence.
5. Implement policy composition, review-dimension derivation, authority issuer/revocation, continuity integrity, evidence-ingestion, history and recovery controls.
6. Run mutation/self-falsification focused on authority/self-grant paths.
7. Freeze exact implementation candidate.
8. Obtain fresh independent review of the exact implementation.
9. Do not promote PR #39 or PR #40 merely because R8 design exists; each must be rebased/reconciled against qualified R8 semantics and independently closed.

## 7. Claim boundary

A future R8 pass would establish only the tested meta-governance mechanisms and falsification cases. It would not by itself prove production IAM/KMS, hosting-provider branch protection, cryptographic human identity, disaster recovery, or external reviewer/model truthfulness beyond the exact qualified mechanisms.

Until R8 closes:
- holistic governance status = CHANGES_REQUIRED;
- PR #39 remains non-authoritative;
- PR #40 remains non-authoritative;
- authority effect = NONE.
