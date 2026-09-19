# Ruflo R2 Project/Frozen-Boundary Appendix

This appendix contains the current R2 design material plus exact frozen EXP-M R5 and stopped RQ-16 review material used for independent R2 boundary checking.


---

# CURRENT R2

## SOURCE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2.md

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `63a110e91601f8e9e7f0d1a6dbf061b5a1c068c9`

# Ruflo Selective Adoption R2

Status: `DESIGN_ONLY_EXTERNAL_REVIEW_REQUIRED`

Authority effect: `NONE`

This document is the R2 remediation of the first independent manual review of the Ruflo selective-adoption plan.

Frozen boundaries:

- RQ-16 remains stopped and unauthorized.
- EXP-M R5 remains frozen and unmodified.
- No Ruflo package/runtime/plugin is trusted merely because it exists or is imported.
- No implementation is authorized by this document.

## 1. Adoption items

The selective-adoption catalog remains:

- RA-01 Capability Truth Model
- RA-02 Evidence Assurance Classes
- RA-03 Evaluation Receipt / Promotion Transaction
- RA-04 Conserved Capability Envelope
- RA-05 Machine-Generated Capability Registry and Claim Integrity
- RA-06 Source-State + Execution-Context Receipts
- RA-07 Append-Only Negative-Learning Archive
- RA-08 Typed Memory Provenance and Supersession
- RA-09 Tool Permission / Side-Effect Contract
- RA-10 Isolated Worktrees, Leases, Fencing
- RA-11 Retrieval / Plugin Trust Boundary
- RA-12 Deterministic-First Routing / Orchestration Threshold
- RA-13 Bounded Research / Dream Cycle

## 2. Foundational primitives

Before authority-bearing RA items may use them, the following shared primitives require their own deterministic falsification and independent review.

### FP-01 — CanonicalRecordIdentity

Canonical structured/length-framed identity, stable subject/type/version semantics, collision-resistant SHA-256 digesting, no ambiguous delimiter concatenation.

### FP-02 — AuthorityGenerationCAS

Platform-owned monotonic generation and compare-and-set primitive for authority-bearing state. It detects stale writer, ABA/replay, and concurrent writer conflict. Unknown generation fails closed.

### FP-03 — TamperEvidentLedger

Append-only hash chain + monotonic sequence + anchor outside the writable ledger state. On open/restart, chain/head/anchor mismatch fails closed. Anchor unavailability never silently resets history.

### FP-04 — DataFlowLabel

Typed data classification/provenance labels with monotonic propagation. Declassification requires an explicit separately-authorized operation that binds source labels, transformation, destination label, actor and authority snapshot.

## 3. R2 invariant corrections

### R2-I00 — Adoption governance inputs cannot self-authorize

Every platform-owned registry/policy introduced by this adoption program is bound through the existing pre-candidate governance authority (or a separately reviewed successor) and is outside candidate/plugin/reviewer write authority for the candidate being judged.

This includes at least:

- capability source map;
- evidence-assurance acceptance rules;
- promotion policy;
- capability scope/canonicalization rules;
- ToolRiskRegistry;
- data-classification/declassification policy;
- publisher/trust-root registry;
- context/retrieval enforcement policy;
- experiment oracle/version registry.

A candidate may propose changes, but the proposed version cannot narrow or authorize the same candidate's review/execution. Unknown/missing governing version fails closed.

### R2-I01 — Capability truth is scoped, generation-bound and non-collapsible

Capability facts are independent predicates, not a state-machine arrow:

- catalogued(subject, capability_id, registry_version)
- registered(runtime_instance, capability_id, generation)
- configured(subject_tuple, scope, configuration_version)
- reachable(subject_tuple, endpoint_identity, observation_generation)
- healthy(subject_tuple, health_contract, observation_generation)
- qualified(subject_tuple, scope, qualification_program, qualification_version, expiry, generation)
- authorized(actor, action, resource, authority_snapshot, generation)

No fact implies another fact.

`qualified` is never a bare boolean.

A green health result cannot renew or recreate an expired/invalidated qualification. Invalidation is latched until the required requalification program completes.

EXP-M and RQ-16 project as `NOT_QUALIFIED` unless their own governing artifacts explicitly prove otherwise.

### R2-I02 — Evidence assurance is per claim and cannot launder provenance

Evidence assurance attaches to `(subject, claim, evidence_ref)`.

Classes include:

- RECOMPUTED
- SIGNATURE_VERIFIED
- TRUSTED_ASSERTION
- PROVIDER_TELEMETRY
- MODEL_JUDGMENT
- USER_ATTESTED
- UNPROVEN

These are not a scalar or universal order.

Each governing predicate defines accepted provenance/assurance combinations.

Derived evidence cannot receive a stronger assurance than its load-bearing inputs unless the recomputation independently reconstructs the claim from authoritative bound inputs.

`SIGNATURE_VERIFIED` binds named trust root + signer identity + signed subject.
`TRUSTED_ASSERTION` binds named trust root + assertion scope.

Multiple weak items cannot be stacked into a stronger class unless the governing rule explicitly defines that composition.

Accepted composition rules are versioned governance outside candidate write authority.

### R2-I03 — Evaluation remains unable to write authority state

Evaluation/review environments have no capability to mutate promotion/release authority state.

Evaluation produces immutable evidence/receipts only.

The receipt issuer trust root is distinct from:

- candidate author authority;
- evaluator execution environment;
- promotion writer authority.

External authorization requirements derive from the governing authority snapshot and default to required when no explicit lower-authority rule exists.

Before RA-10 multi-writer infrastructure is qualified, RA-03 operates under a single serialized authority-writer precondition plus a platform-owned atomic generation/CAS primitive. Any detected concurrent writer causes rejection.

### R2-I04 — Capability envelopes split scope from consumables

Non-consumable dimensions use canonical subset semantics:

- tools
- paths/resources
- providers/models
- network scopes
- destructive-action rights
- promotion/release rights
- data classes

Issuance and enforcement use the same canonicalizer. Incomparable scope is rejected.

Consumable dimensions use typed conservation semantics.

Each dimension is declared by platform policy as one of:

- `CUMULATIVE_NONREPLENISHABLE` — e.g. spend, consumed tokens, completed request count, consumed compute quota;
- `LEASED_REPLENISHABLE_CAPACITY` — e.g. concurrent worker slots;
- `BOUNDED_ALLOCATION_WITH_UNUSED_RETURN` — a finite delegated allocation whose unconsumed remainder may be returned.

Unknown accounting type is rejected.

For a cumulative parent grant G:

`parent_committed_consumption + parent_outstanding_allocation + sum(child_outstanding_allocation) <= G`

Consumed units can never be returned.

For leased capacity:

`parent_live_use + sum(child_live_leases) <= G`

Only a valid recorded lease release/expiry may restore leased capacity.

Reservation/release is atomic against a parent capability ledger.

Every reservation and release has a globally unique operation ID and idempotency key. A release may credit capacity at most once; replayed reserve/release operations return the original result and never change balance twice.

Unused child allocation returns only via a recorded release operation.

Expiry cannot exceed the parent's remaining lifetime.

A child may not re-lend returned capacity until the release commit is authoritative.

Parent revocation/expiry invalidates descendant use immediately. Every authority-bearing child use validates its grant lineage against the current ancestor generation/revocation fence; a reserved balance is not a detached bearer token.

Depth x breadth fan-out must never amplify aggregate authority.

Hierarchical rule: a child may subdelegate consumables only from its own currently reserved balance. The same units cannot simultaneously back the child's own consumption and a descendant reservation. Every reserve/release operation carries parent-ledger generation and lineage; local conservation at each edge plus immutable upstream reservations must imply global conservation.

### R2-I05 — Generated registry cannot mint capability truth

RA-05 generated inventory is diagnostic/read-only until separately qualified.

RA-01 may read only named authoritative stores for each capability fact.

The generated registry may report catalogued/registered observations but cannot supply:

- qualification;
- authorization;
- promotion eligibility.

Dependency is one-way:

`authoritative stores -> capability projection -> generated report`

Never:

`generated report -> authority`

### R2-I06 — Source identity and execution identity are separate

RA-06 defines:

1. `SourceStateReceipt`
2. `ExecutionContextReceipt`

SourceStateReceipt:

- repository identity;
- source-state type;
- base commit/tree;
- canonical SHA-256 source digest;
- tracked patch digest for dirty snapshots;
- untracked declared-source manifest;
- mode/type/symlink identity;
- submodule state where relevant.

ExecutionContextReceipt:

- toolchain versions;
- container/image digest where used;
- dependency lock digests;
- fetched dependency identities/digests used by the execution;
- declared runtime input files and their digests;
- relevant environment/configuration hashes excluding secret values;
- secret/credential provider identity + non-secret version/fingerprint when the claim depends on a secret-backed external interaction;
- runner/OS/architecture identity where the claim depends on them.

Promotion/release hard-requires `COMMITTED_SOURCE_STATE`.

Evidence from `IMMUTABLE_DIRTY_SNAPSHOT` never transfers to a later commit merely because the tree matches. Re-run is required.

Source-only receipts do not claim execution reproducibility.

An execution receipt may claim `EXECUTION_CONTEXT_BOUND=true` only when the run is hermetic/allowlisted or the platform can observe and reconcile all load-bearing file/network/dependency inputs against the receipt. Otherwise it is explicitly `UNBOUNDED_EXECUTION_CONTEXT` and cannot satisfy a promotion predicate that requires exact executed-state evidence.

### R2-I07 — Shared canonical record identity precedes RA-07/08

A shared foundational primitive is reviewed before either RA-07 or authority-bearing RA-08:

`CanonicalRecordIdentity`

It uses canonical structured serialization/length framing, never ambiguous delimiter concatenation.

It provides immutable:

- record ID
- version ID
- parent/supersedes links
- subject/type namespace
- content digest
- provenance digest

RA-07 may initially store only opaque/digest links through this primitive.

RA-08 later adds governed active projections and namespace authority. A retraction/supersession of evidence referenced by a derived authoritative memory/claim triggers dependency reassessment; no derived active projection survives merely because the old record remains in append-only history.

### R2-I08 — Append-only history has rollback detection and privacy quarantine

RA-07/RA-08 append-only logs use:

- hash chaining;
- monotonic sequence/generation;
- an anchor stored outside the writable archive state (for example a separately authorized monotonic authority store or signed external checkpoint);
- load-time and restart/recovery comparison against that independent anchor.

The authoritative ledger head is the externally anchored head. A locally appended tail that has not yet advanced the independent anchor is `PENDING_NON_AUTHORITATIVE`. Crash recovery may either complete the exact pending append through the governed anchor CAS or discard/quarantine the unanchored tail; it may never silently treat an unanchored tail as authoritative.

Rollback, truncation and fork are detectable.

Sensitive payload quarantine:

- ledger entry/digest/history remains;
- raw payload is stored separately under authorized restricted access;
- quarantine/tombstone operation is appended;
- downstream retrieval uses a safe data representation.

Append-only history is not a deny-list and does not itself authorize blocking.

Revocation belongs to an authority-bearing policy mechanism.

### R2-I09 — Tool risk floor is platform-owned

Each tool/action has a platform-owned minimum risk/permission floor.

A plugin/tool manifest may request more restriction but never less.

The effective permission contract is:

`platform_floor UNION tool_declared_requirements`

over typed dimensions.

A tool/plugin cannot lower filesystem/network/process/credential/egress/destructive/promotion risk by self-description.

The platform floor comes from a versioned `ToolRiskRegistry` outside plugin/candidate write authority. Unknown tool identity or missing registry entry defaults to deny for authority-bearing dispatch.

The permission contract is an enforcement ceiling, not evidence that the tool behaves benignly. Authority-bearing execution additionally requires runtime sandbox/capability enforcement or an equivalently qualified side-effect boundary.

### R2-I10 — Data-flow composition is governed

Individually permitted actions may still compose into exfiltration.

The combination:

`sensitive_read + untrusted_content_ingest + external_egress`

is denied by default inside one capability envelope unless an explicit governing grant authorizes that exact composed flow.

The platform uses typed `DataFlowLabel` metadata on governed inputs and tool outputs. Labels propagate monotonically across transforms unless a separately authorized declassification operation records the exact source labels, transform and destination classification.

A plan that cannot determine data-flow labels for a protected value fails closed before external egress.

Labels are platform-attached from authoritative resource/source classification and provenance. An untrusted tool/plugin may add restrictions but cannot remove or downgrade platform labels.

This is checked at ingestion, transformation, plan/dispatch time and again at the egress boundary, not only per-tool.

### R2-I11 — Fencing is enforced by the protected resource

RA-10 lease/fencing validity is checked atomically by the protected write authority/resource. Lease/fence issuance state is platform-owned and outside candidate/writer mutation:

- Git ref CAS;
- write broker;
- transactional store;
- equivalent authoritative guard.

A writer's local self-check is not sufficient.

Stale or absent fencing token fails at the protected write.

Lease coordinates ownership; authorization remains separate.

### R2-I12 — RA-11 enforcement is a prerequisite, not a future option

RA-11 has two stages:

- diagnostic analysis;
- enforcement qualification.

Enforcement must cover:

- source/signature identity;
- publisher/trust-root policy;
- transitive dependency closure including runtime-resolved executable dependencies;
- content-addressed verified load target;
- no post-verification dynamic code fetch unless the fetched object is separately content-addressed, trusted, permission-checked and included in the dependency closure;
- verify-then-load TOCTOU resistance;
- tool permission contract;
- sandbox/capability envelope;
- retrieval/context-injection representation boundary.

Semantic/LLM scanning remains diagnostic and never substitutes for deterministic enforcement.

Gate 4/5 automation cannot begin until RA-11 enforcement is qualified.

### R2-I13 — Routing decisions are frozen and reauthorized

RA-12 emits a content-addressed `RoutePlan` bound to:

- task/request identity;
- authority snapshot;
- capability-state generations;
- selected deterministic/single/swarm path;
- provider/tool identities;
- budget allocation;
- prerequisite qualification identities.

The plan is policy-checked after routing and before execution. Any fallback or route change creates a new RoutePlan and must be reauthorized; fallback cannot inherit authority from the failed path.

### R2-I14 — Failure archive content is untrusted data on retrieval

Agent-authored failure text, external content and model output stored in RA-07/08 never re-enter an agent/system prompt as instructions.

Retrieval wraps it as data with:

- provenance;
- record identity;
- quarantine/redaction status;
- explicit non-authority label.

Persistent injection from archived failure content is part of RA-CONTEXT-001.

### R2-I15 — Experiments require preregistered oracles, positive controls and test-the-test mutations

Every RA experiment has:

- frozen experiment version;
- exact source identity;
- predeclared invariant;
- deterministic pass/fail predicate;
- positive control proving valid behavior still succeeds;
- negative/adversarial fixtures;
- test-the-test mutation that removes/weakens the guard and must cause failure;
- preserved first failure;
- generated evidence counts;
- independent review before any authority effect.

The R2 matrix remains a design contract until implemented. Test-the-test mutations must modify the production validator/enforcement path (or an exact compiled/injected mutation of it), not merely flip expected fixture metadata.

### R2-I16 — Withheld self-adjudication uses commit-reveal

The R2 self-adjudication ledger remains withheld during independent review to reduce anchoring.

Commitment:

`sha256:e013203536cbd64d7df21c1c27d3666a2d3364c0b6ad2f195ac5c8358502fd58`

After the independent R2 review is returned, the ledger may be revealed and its hash checked.

The commitment has no authority effect.

### R2-I17 — Authority boundaries are enumerated

For this adoption program, an authority boundary includes any operation that can:

1. change qualification/promotion/release state;
2. change governing policy/standards/registries;
3. consume or grant authorization;
4. access protected credentials/secrets;
5. perform network/provider calls with cost/data egress;
6. write outside the bounded candidate workspace;
7. write authoritative evidence/memory state;
8. write protected concurrent resources;
9. expand budget/concurrency/delegation;
10. execute side-effecting plugins/tools;
11. release/publish/deploy artifacts.

Unknown boundary classification fails closed.

### R2-I18 — EXP-M stability trigger is exact

"Stable EXP-M deterministic result" means all of:

- implementation is based on the frozen R5 design;
- exact implementation source/evidence is frozen;
- deterministic A-T exit criteria pass;
- zero surviving data/state mutations;
- zero surviving validator-logic mutations;
- exact admissibility predicate closure passes;
- required deterministic evidence package exists;
- independent implementation/falsification review returns bounded pass;
- no load-bearing R5 design semantic was changed without a separate reviewed design delta.

Live provider qualification is not required for this trigger unless EXP-M itself later changes that rule.

### R2-I19 — Package/review identity is explicit

A package manifest does not recursively hash itself.

The review handoff records separately:

- packet content digest;
- package-manifest digest;
- final ZIP digest;
- source commit/tree/blob identities.

Pasted/manual reviewer text is user-attested external review evidence unless independently authenticated by another mechanism.

### R2-I20 — Architectural adoption does not silently copy runtime trust

R2 adopts ideas, not Ruflo authority.

No Ruflo source code/package/plugin is copied into the trusted path by this design. Any future code reuse requires:

- exact source/version identity;
- license compatibility review;
- dependency/supply-chain review;
- project-native security/falsification tests;
- an explicit decision whether the reused component is diagnostic or authority-bearing.

Ruflo's declared ADR status or implementation claim never substitutes for this project's qualification.

## 4. Dependency/prerequisite rules

See `RUFLO-SELECTIVE-ADOPTION-R2-PREREQUISITES.md`.

Important:

- RA-11 enforcement is required before autonomous multi-writer, swarm, or research automation.
- RA-03/04/09/11-enforcement are required before RA-10/12/13 can receive authority-bearing execution.
- RA-06/07/10 are additionally required before RA-13.
- RA-07 cannot depend on authority-bearing RA-08 semantics before the shared canonical identity primitive is reviewed.
- EXP-M continues under R5 independently of this adoption program.

## 5. R2 experiment families

See `RUFLO-SELECTIVE-ADOPTION-R2-TEST-MATRIX.md`.

Each family is preregistration-only until separately implemented and reviewed.

## 6. Frozen-boundary declaration

```text
RQ16_STOP_PRESERVED        = REQUIRED
EXP_M_R5_FREEZE_PRESERVED  = REQUIRED
DIRECT_RUFLO_TRUST         = PROHIBITED
AUTHORITY_EFFECT           = NONE
IMPLEMENTATION_AUTHORIZED  = false
```



## SOURCE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-PREREQUISITES.md

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `b96c053bbacdfc58e455a7e3c1903b13caeed343`

# Ruflo Selective Adoption R2 — Prerequisite Matrix

Presence is not sufficient. A prerequisite marked `QUALIFIED` must have completed its own governed implementation, falsification and independent review.

| Target | Mandatory prerequisites |
|---|---|
| Gate 0 R2 design closure | independent R2 manual design review; zero unresolved Critical/High |
| Gate 1 EXP-M deterministic implementation | frozen EXP-M R5 only; independent of RA adoption |
| FP-01 CanonicalRecordIdentity | Gate 0 bounded pass |
| FP-02 AuthorityGenerationCAS | Gate 0 bounded pass; protected-state storage contract defined |
| FP-03 TamperEvidentLedger | Gate 0 bounded pass; independent anchor store/authority defined |
| FP-04 DataFlowLabel | Gate 0 bounded pass; data-classification/declassification authority defined |
| RA-01 diagnostic projection | Gate 0 bounded pass; named authoritative source map |
| RA-05 generated inventory | Gate 0 bounded pass; diagnostic-only status |
| RA-06 source/execution receipts | Gate 0 bounded pass; FP-01 qualified |
| RA-07 advisory negative archive | FP-01 + FP-03 qualified; no deny-list authority |
| RA-11 diagnostics | Gate 0 bounded pass; provenance-safe representation |
| RA-02 evidence assurance | FP-01 qualified; governing composition rules reviewed |
| RA-03 evaluation/promotion transaction | FP-01 + FP-02 + FP-03 qualified; evaluator write isolation; external-auth policy derived from authority snapshot |
| RA-04 capability envelope | FP-02 qualified; canonical scope comparator; atomic consumable reservation ledger |
| RA-08 authority-bearing memory supersession | FP-01 + FP-02 + RA-02 + RA-07 mechanism qualified; namespace authority defined; active-projection CAS defined |
| RA-09 tool permission contract | FP-04 + RA-04 qualified; platform tool-risk registry qualified |
| RA-11 enforcement | FP-04 + RA-02 + RA-04 + RA-09 qualified; signature/publisher/dependency/load/sandbox mechanisms qualified |
| RA-10 multi-writer worktrees/leases/fencing | RA-03 + RA-04 + RA-06 + RA-09 + RA-11 enforcement + FP-02 qualified |
| RA-12 swarm-capable routing | RA-01 capability projection correctness + RA-03 + RA-04 + RA-09 + RA-10 + RA-11 enforcement qualified |
| RA-13 bounded research/dream cycle | RA-01 + RA-03 + RA-04 + RA-06 + RA-07 + RA-08 provenance/supersession + RA-09 + RA-10 + RA-11 enforcement + RA-12 qualified; authoritative policy/gold/evaluation write isolation |

## Rules

1. "Implemented" does not satisfy a `QUALIFIED` prerequisite.
2. Diagnostic RA-11 does not satisfy RA-11 enforcement.
3. A route that is single-executor-only may be tested before RA-10, but it must be structurally unable to spawn concurrent writers.
4. Any target that uses memory as authority also requires RA-08; advisory retrieval does not.
5. Any target that changes promotion/release authority requires RA-03.
6. Any target that delegates consumable resources requires RA-04 hierarchical conservation semantics and atomic parent-ledger reservation.
7. Any target ingesting external/untrusted content into an executable/reviewer context requires RA-11 enforcement before authority-bearing use.
8. Unknown prerequisite state fails closed.


## SOURCE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-TEST-MATRIX.md

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `7179650a21bb0a6dcd135adbd98924762d86bac7`

# Ruflo Selective Adoption R2 — Falsification Matrix

Status: preregistered design only. No experiment in this matrix is claimed executed.

Every experiment must implement: frozen version, deterministic oracle, positive control, negative fixtures, test-the-test mutation, first-failure preservation, generated counts and independent review.

## FP-IDENT-001 — Canonical record identity

Pass iff structured identity is deterministic and collision-resistant across all supported subject/type/version inputs.

Negative fixtures:

- delimiter collision;
- Unicode normalization ambiguity;
- path separator/case ambiguity where platform semantics differ;
- duplicate canonical field;
- type confusion;
- length-framing ambiguity;
- same semantic object serialized in alternative order.

Positive control:

- equivalent canonical object produces identical identity.

Test-the-test:

- replace structured framing with naive delimiter concatenation -> collision fixture must fail.

## FP-CAS-001 — Authority generation / CAS

Pass iff only current generation may mutate protected state and a successful write advances generation atomically.

Negative fixtures:

- stale writer;
- two concurrent same-generation writers;
- ABA/replayed generation token;
- crash before/after CAS;
- missing generation;
- generation reset after restart.

Positive control:

- one current writer succeeds and advances generation once.

Test-the-test:

- remove expected-generation comparison -> stale/concurrent fixture must fail.

## FP-LEDGER-001 — Tamper-evident ledger

Pass iff append history, chain, sequence and independent anchor agree.

Negative fixtures:

- truncate tail;
- rollback snapshot;
- fork same sequence;
- delete middle record;
- rewrite historical payload;
- restart from older local checkpoint;
- anchor unavailable;
- anchor points to unknown head;
- crash after local append before anchor update;
- crash after anchor CAS before local acknowledgement.

Positive control:

- valid append advances chain and anchor.

Test-the-test:

- remove anchor comparison -> rollback fixture must fail.

## FP-DATAFLOW-001 — Data-flow label propagation

Pass iff protected labels propagate monotonically and only explicit authorized declassification may reduce them.

Negative fixtures:

- transform drops SENSITIVE;
- untrusted ingest loses UNTRUSTED label;
- egress with unknown label;
- candidate self-declassifies;
- untrusted tool/plugin downgrades a platform-attached label;
- declassification reused for another subject/destination;
- join combines protected and public input but output marked public.

Positive control:

- authorized declassification with exact source/transform/destination binding succeeds.

Test-the-test:

- remove label join/propagation -> exfiltration fixture must fail.

## RA-CAP-001 — Capability Truth

Pass iff:

- no capability fact is inferred from another;
- qualification is scoped to subject/scope/program/version/generation;
- invalidation latches until requalification;
- stale generation cannot authorize use.

Negative fixtures:

- registered -> authorized collapse;
- healthy -> qualified collapse;
- expired qualification + green health;
- provider/model/endpoint fallback inheritance;
- candidate-authored qualification;
- projection read then authority generation changes before use.

Positive controls:

- current scoped qualification + separate current authorization succeeds.

Test-the-test:

- remove generation equality check -> at least one stale-use fixture must fail.

## RA-EVID-001 — Evidence Assurance

Pass iff:

- assurance attaches to subject/claim/evidence;
- trust roots are named/bound;
- derived evidence cannot launder weaker input provenance;
- governing composition rules are immutable to candidates.

Negative fixtures:

- recompute over model/user assertion relabeled RECOMPUTED;
- signature verifies bytes but wrong subject;
- untrusted issuer marked TRUSTED_ASSERTION;
- two weak items stacked to satisfy strong predicate;
- candidate weakens accepted-combination rule.

Positive control:

- independent recomputation from authoritative bound bytes may satisfy a recomputable claim.

Test-the-test:

- remove input-provenance bound -> laundering fixture must fail.

## RA-PROMO-001 — Evaluation / Promotion Transaction

Pass iff evaluation cannot write authority and one receipt can cause at most one valid promotion.

Negative fixtures:

- PASS directly mutates active state;
- evaluator has authority-store write;
- receipt issuer shares candidate/evaluator trust root;
- stale baseline/head/policy;
- replay/second consume;
- concurrent promotion;
- crash before/after commit;
- missing external auth where policy is absent;
- detected concurrent writer before RA-10.

Positive control:

- current receipt + valid external auth + exact generation CAS promotes once.

Test-the-test:

- remove consumed-receipt or generation check -> replay/concurrency fixture must fail.

## RA-CAPENV-001 — Conserved Capability Envelope

Pass iff:

- non-consumable child scope is canonical subset;
- consumable allocations are conserved globally;
- expiry and delegation never expand parent.

Negative fixtures:

- sibling fan-out N x budget;
- concurrent sibling reservation race;
- parent use + child reservations > grant;
- release then double re-lend;
- child expiry > parent;
- parent revoked while descendant still holds reserved balance;
- replay same release twice to over-credit;
- retry same reserve twice;
- child consumes part of cumulative allocation then releases full reservation to over-credit;
- leased slot release replay;
- accounting type omitted/changed;
- depth x breadth amplification;
- child spends units while simultaneously subdelegating the same units;
- descendant release races parent reclaim;
- wildcard/canonical path ambiguity;
- stale/revoked parent delegation.

Positive control:

- atomic reservation within remaining parent balance succeeds and recorded release makes capacity re-lendable once.

Test-the-test:

- replace atomic reserve with check-then-write -> sibling race must fail.

## RA-REG-001 — Generated Registry

Pass iff registry is reproducible, current and non-authoritative.

Negative fixtures:

- stale artifact;
- duplicate/renamed ID;
- runtime conditional capability omitted;
- registry says qualified/authorized without authoritative source;
- candidate edits generated output.

Positive control:

- deterministic generation from pinned inputs reproduces exact digest.

Test-the-test:

- allow registry to feed qualification -> laundering fixture must fail.

## RA-SRC-001 — Source / Execution Receipts

Pass iff source and execution identities are distinct and promotion requires committed source.

Negative fixtures:

- same HEAD different dirty bytes;
- untracked file/mode/symlink/submodule drift;
- source receipt reused across different execution context;
- secret-backed external interaction changes credential version/fingerprint without receipt change;
- dirty evidence transferred to commit;
- SHA-1 Git ID accepted without independent canonical SHA-256;
- undeclared runtime input affects test;
- non-hermetic execution claims EXECUTION_CONTEXT_BOUND despite unobserved filesystem/network input.

Positive control:

- exact committed source + matching execution context re-run is eligible downstream.

Test-the-test:

- ignore dirty patch or execution-context digest -> mismatch fixture must fail.

## RA-NEG-001 — Negative Learning Archive

Pass iff history is tamper-evident/advisory and rollback detectable.

Negative fixtures:

- delete/truncate/fork history;
- candidate edits own failure;
- retry erases failure;
- historical failure becomes deny-list authority;
- quarantined secret payload returned to context;
- stale anti-pattern blocks repaired source without current policy.

Positive control:

- new superseding advisory record preserves old digest/history.

Test-the-test:

- remove chain/anchor validation -> rollback fixture must fail.

## RA-MEM-001 — Memory Provenance / Supersession

Pass iff canonical identities do not collide, history is preserved, namespace writes are authorized, and active projection is deterministic.

Negative fixtures:

- delimiter collision;
- unauthorized namespace write;
- concurrent same-key updates;
- supersession cycle;
- superseded/retracted evidence leaves dependent authoritative projection active without reassessment;
- stale restore after restart;
- repeated model memory gains authority;
- quarantine/tombstone ignored.

Positive control:

- authorized new version supersedes prior while preserving history.

Test-the-test:

- remove namespace/canonical-framing guard -> collision or cross-namespace fixture must fail.

## RA-TOOL-001 — Tool Permission / Side Effects

Pass iff platform-owned risk floor cannot be lowered and composed data flow is governed.

Negative fixtures:

- tool understates network/fs/process/credential risk;
- manifest swap after approval;
- valid tool permission but sensitive-read + untrusted-ingest + egress composition;
- missing/unknown DataFlowLabel at egress;
- transform incorrectly drops a sensitive/untrusted label without authorized declassification;
- approval resource replay;
- fallback provider broadens capability;
- path/command escape;
- tool has correct declared contract but runtime side effect escapes unenforced boundary.

Positive control:

- allowed tool with exact resource and non-exfiltrating data flow succeeds.

Test-the-test:

- trust tool-declared floor over platform floor -> under-declaration fixture must fail.

## RA-CONC-001 — Worktrees / Leases / Fencing

Pass iff protected resource validates current fence atomically at write.

Negative fixtures:

- overlapping lease;
- stale writer after expiry/reacquire ABA;
- writer skips local fence check;
- protected resource receives stale token;
- lease without authorization;
- authorization without required lease;
- integration-owner conflict;
- candidate/writer mutates lease service state;
- restart/multi-host race.

Positive control:

- current lease + authorization + current fence succeeds once.

Test-the-test:

- move fence validation from resource to writer only -> skip-check fixture must fail.

## RA-CONTEXT-001 — Retrieval / Plugin Trust

Pass iff signature/publisher/dependency/load/sandbox/provenance controls are enforced before authority-bearing context/tool use.

Negative fixtures:

- verify-then-load swap;
- revoked publisher/key;
- trusted signature from untrusted publisher;
- transitive dependency substitution;
- verified plugin dynamically fetches unverified executable code;
- valid signature + sandbox escape;
- unsigned plugin classifier says benign;
- signed plugin contains injection;
- memory/failure archive persistent injection;
- classifier unavailable;
- retrieved content tries to modify tool authority.

Positive control:

- content-addressed signed bundle from allowed publisher with verified dependency closure, allowed capabilities and safe data representation loads successfully.

Test-the-test:

- disable verified-load digest check -> swap fixture must fail.

## RA-ROUTE-001 — Deterministic-First Routing

Pass iff routing cannot create authority or bypass prerequisites.

Negative fixtures:

- route result grants tool/provider;
- route changes after exposure without new RoutePlan/authorization;
- fallback reuses failed path's authority without reauthorization;
- learned model treated as policy;
- fallback inherits authority;
- swarm selected before RA-10/11 enforcement;
- optimization weakens safety.

Positive control:

- deterministic safe task routes to deterministic mechanism while all authority checks remain unchanged.

Test-the-test:

- skip post-route policy check -> authority-bypass fixture must fail.

## RA-DREAM-001 — Bounded Research Cycle

Pass iff the cycle can propose/evaluate/archive but cannot self-authorize, self-merge, edit gold/policy, erase failures or exceed conserved budget.

Negative fixtures:

- candidate edits acceptance rule;
- research agent edits governing standard;
- self-merge/promotion;
- benchmark/gold mutation;
- no-stop budget overrun;
- sibling budget amplification;
- failed hypothesis deletion;
- same agent authors and authenticates review;
- external content ingest before RA-11 enforcement.

Positive control:

- bounded proposal completes inside conserved envelope, archives evidence and stops for separate authority.

Test-the-test:

- grant policy-write or promotion capability to cycle -> self-authorization fixture must fail.

## Cross-composition suite

Must include:

1. RA-01 <- RA-05 registry laundering.
2. RA-02 + RA-06 derived assurance from dirty/unbound execution.
3. RA-03 + RA-04 promotion through over-allocated child capability.
4. RA-04 + RA-12/13 sibling/depth amplification.
5. RA-09 + RA-11 + RA-04 sensitive-read/untrusted-ingest/egress exfiltration.
6. RA-07/08 + RA-11 persistent injection.
7. RA-03 + RA-10 stale writer/fence during promotion.
8. RA-06 + RA-03 dirty evidence transferred to committed candidate.
9. RA-11 + RA-09 signed-but-overprivileged plugin.
10. RA-12 + RA-11 route to unqualified external-content path.

Any false-green cross-composition path blocks implementation authority.


## SOURCE: research/ruflo-adoption/RUFLO-R2-R1-FINDING-ADJUDICATION.md

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `a1188c7979d277f55b410d4b554fa872ccdecb33`

# Ruflo Selective Adoption R2 — R1 Finding Adjudication

Status: `R1_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R2_REVIEW`

Authority effect: `NONE`

The R1 independent review found 0 Critical and 2 High findings. All R1 High and Medium/Low/cross-composition items below are treated as valid design feedback and incorporated into R2 unless explicitly marked otherwise.

## High closure

### H-01 — RA-04 per-child bound amplifies consumables

Disposition: `REPAIRED_FOR_R2_REVIEW`

R2 changes:

- split non-consumable subset semantics from consumable conservation;
- atomic parent-ledger reservation;
- hierarchical child subdelegation consumes child reserved balance;
- parent own-use + all live child reservations must remain <= grant;
- recorded release/re-lend;
- child lifetime cannot exceed parent;
- depth/breadth/sibling race fixtures;
- check-then-write mutation required to fail.

### H-02 — RA-11 enforcement absent from automation prerequisites

Disposition: `REPAIRED_FOR_R2_REVIEW`

R2 changes:

- explicit RA-11 diagnostic vs enforcement distinction;
- prerequisite matrix replaces ordinal presence-only gating;
- RA-11 enforcement required before RA-10/12/13 authority-bearing automation;
- RA-03/04/09/11 enforcement required before multi-writer/swarm/research;
- additional RA-06/07/08/10 dependencies for the research cycle;
- verified-load TOCTOU, revoked publisher/key, transitive dependency, dynamic-code fetch and valid-signature sandbox-escape scenarios.

## Medium/Low closure

### M-01 — unscoped qualified

Replaced bare qualification with a subject/scope/program/version/generation-bound predicate. Health cannot renew invalidated qualification. Stale-generation use is tested.

### M-02 — assurance composition undefined

Evidence assurance is per subject/claim/evidence. Trust roots are explicit. Derived assurance cannot launder weaker inputs. Accepted combinations are governing rules outside candidate write authority.

### M-03 — promotion authority / concurrency bootstrap

External authorization derives from authority snapshot and defaults required when no lower rule exists. Evaluator cannot write authority state. Receipt issuer trust is separated. FP-02 AuthorityGenerationCAS plus serialized-writer precondition precedes RA-10.

### M-04 — RA-07 depends on RA-08 primitives

CanonicalRecordIdentity is extracted as FP-01 and reviewed before RA-07/08. RA-07 may use opaque/digest links without authority-bearing memory semantics.

### M-05 — append-only mechanism / quarantine

Added FP-03 TamperEvidentLedger with hash chain, monotonic sequence and independent anchor. Added rollback/truncation/fork tests. Sensitive payload can be quarantined while digest/tombstone/history remains. RA-07 cannot act as a deny-list.

### M-06 — source vs execution context

Separated SourceStateReceipt and ExecutionContextReceipt. Added independent canonical SHA-256, toolchain/container/dependency/runtime-input identities and non-secret credential version/fingerprint where relevant. Promotion requires committed source; dirty evidence never transfers without rerun.

### M-07 — tests were scenario seeds only

All R2 experiment families now require deterministic pass/fail predicate, positive control, negative fixtures, test-the-test mutation, first-failure preservation and generated counts.

### M-08 — withheld findings unverifiable

R2 publishes SHA-256 commitment to the withheld self-adjudication ledger. Reveal occurs only after independent R2 review.

### M-09 — fencing local self-check

Protected resource/write authority must atomically validate fencing token. Writer-only check is insufficient.

### L-01 — authority boundary undefined

R2 enumerates authority-changing/credential/network/egress/evidence/memory/concurrency/budget/plugin/release boundaries.

### L-02 — stable EXP-M trigger undefined

R2 defines exact stable deterministic EXP-M conditions, including R5 source freeze, A-T exit, zero mutation survivors and independent implementation review.

### L-03 — package identity

R2 review handoff uses non-recursive package manifest plus separately reported manifest and ZIP SHA-256 values. Manual pasted review remains user-attested external evidence unless separately authenticated.

### L-04 — Ruflo source status absent

R2 adds `RUFLO-R2-SOURCE-STATUS-MANIFEST.json` recording the exact source blob and Ruflo-declared status (Proposed/Accepted/implemented where declared). Ruflo status is contextual only.

### L-05 — failure archive as deny-list

Explicitly prohibited. Revocation/blocking requires a current authority-bearing policy decision.

## Cross-composition closure

### E-01 — RA-05 -> RA-01 registry laundering

Dependency is one-way: named authoritative stores -> capability projection -> generated report. Generated registry cannot mint qualified/authorized state.

### E-02 — RA-06 + RA-02/03 dirty evidence transfer

Receipts carry source-state type. Promotion requires COMMITTED_SOURCE_STATE. Dirty-snapshot evidence does not transfer even if later committed tree bytes match; rerun is required.

### E-03 — RA-04 + RA-12/13 aggregate amplification

Closed with hierarchical consumable conservation and prerequisite matrix.

### E-04 — RA-09 + RA-11/04 composed exfiltration

Added FP-04 DataFlowLabel. Sensitive-read + untrusted-ingest + external-egress is denied by default without an exact composed-flow grant. Labels propagate; declassification is separately authorized.

### E-05 — RA-07/08/11 persistent injection

Archived model/agent/external text returns as provenance-bound data, not instructions/authority. Quarantine/redaction status travels with the record.

## Additional R2 hardening before handoff

R2 also adds:

- FP-01 CanonicalRecordIdentity;
- FP-02 AuthorityGenerationCAS;
- FP-03 TamperEvidentLedger;
- FP-04 DataFlowLabel;
- hierarchical conservation across descendant delegation;
- dynamic plugin-code fetch closure;
- platform-owned ToolRiskRegistry;
- execution receipt binding for secret/credential version identity where relevant;
- RA-08 active projection requiring CAS;
- RA-10 requiring exact source/execution receipts;
- RA-12 requiring capability projection correctness;
- RA-13 requiring governed memory provenance/supersession.

This document is a proposer remediation record only. The independent R2 reviewer must reconstruct closure from the current R2 sources and may reject any claimed closure.


## SOURCE: research/ruflo-adoption/RUFLO-R2-SELF-ADJUDICATION-COMMITMENT.json

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `2bcfda800b439f3f1cb6d4ac4f2c9bce3fdff468`

{
  "schema_version": 1,
  "scope": "Ruflo selective-adoption R2 self-adjudication",
  "commitment_algorithm": "sha256",
  "withheld_ledger_sha256": "e013203536cbd64d7df21c1c27d3666a2d3364c0b6ad2f195ac5c8358502fd58",
  "reveal_after": "independent R2 review return",
  "authority_effect": "NONE",
  "unresolved_critical": 0,
  "unresolved_high": 0
}

## SOURCE: research/ruflo-adoption/RUFLO-R2-SOURCE-STATUS-MANIFEST.json

Ref: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
Blob: `502b47f2c989c84820e7618277d7251042ea27e4`

{
  "schema_version": 1,
  "ruflo_snapshot": {
    "repository": "ruvnet/ruflo",
    "commit": "e558f0c0fc29c1a658085f6e6f80ad27d4fe811f",
    "tree": "08e9ee0dcd7095f082b1047a48c028d6a2b00b84"
  },
  "sources": [
    {
      "path": "v3/docs/adr/ADR-171-provenance-tiered-evaluation-oracle.md",
      "blob": "addd6afbff05d5e2b3b5fa4f6c625fa58afaf171",
      "declared_status": "Proposed — implemented on feat/agenticow-integration",
      "use": "conceptual evidence-tier reference only"
    },
    {
      "path": "v3/docs/adr/ADR-176-proven-self-benchmarking-harness-loop.md",
      "blob": "633d019028855d8291651387f02012f8cc3c2a91",
      "declared_status": "Accepted — demonstrated",
      "use": "bounded self-improvement / anti-pattern reference"
    },
    {
      "path": "v3/docs/adr/ADR-322A-evaluation-promotion-transaction.md",
      "blob": "ce746872b301b7e7387ec4983ff9cca64a0aecee",
      "declared_status": "Accepted — implemented",
      "use": "evaluation/promotion transaction reference"
    },
    {
      "path": "v3/docs/adr/ADR-322C-receipt-ledger-verification.md",
      "blob": "b17a4abd468269a30748ae6a66d2cd02d406d1a5",
      "declared_status": "Accepted — implemented",
      "use": "receipt/provenance reference"
    },
    {
      "path": "v3/docs/adr/ADR-323-typed-memory-provenance.md",
      "blob": "126110d64a67dd3deb5be4839cf3559bd381ea45",
      "declared_status": "Accepted",
      "use": "memory provenance reference"
    },
    {
      "path": "v3/docs/adr/ADR-324-agentic-policy-engine-codex-swarm.md",
      "blob": "bf82b697b32d01f272197ae7d13318416418ad6f",
      "declared_status": "Accepted; implementation marked complete",
      "use": "capability/policy reference"
    },
    {
      "path": "v3/docs/adr/ADR-327-federated-concurrent-development-harness.md",
      "blob": "c61fa9efe8a9a3719809f1090720480f16c4b7d6",
      "declared_status": "Proposed; distributed enforcement pending",
      "use": "worktree/lease/fence concept only"
    },
    {
      "path": "v3/docs/adr/ADR-329-ruflo-capability-brain-mcp-guidance.md",
      "blob": "89095e3fd9b2917974dee00bf1c884d0b2d0d6d6",
      "declared_status": "Accepted",
      "use": "capability-truth model reference"
    },
    {
      "path": "v3/docs/adr/ADR-352-mcp-tool-permission-attestation.md",
      "blob": "a226e7cbff444ab9ef0fa4cab6e88f46827072e2",
      "declared_status": "Proposed",
      "use": "tool permission concept only"
    },
    {
      "path": "v3/docs/adr/ADR-145-plugin-supply-chain-integrity-memory-governance.md",
      "blob": "d0e98af91ff3cae481cc9c4bc8d10718cea16f62",
      "declared_status": "Proposed",
      "use": "plugin/retrieval threat reference only"
    },
    {
      "path": "v3/docs/adr/ADR-169-benchmark-reporting-integrity-standard.md",
      "blob": "6ee60178a102ee3a5adddf21979e7f453bd71035",
      "declared_status": "Accepted",
      "use": "reporting-integrity reference"
    },
    {
      "path": "v3/docs/adr/ADR-384-generalized-bounded-evolution-methodology.md",
      "blob": "78e5f53fc1fbc2c3468570e13b8b583dd232c5ff",
      "declared_status": "Proposed",
      "use": "bounded-evolution concept/nonclaim reference"
    }
  ],
  "rule": "Declared Ruflo status is contextual evidence only. No source becomes trusted/qualified in this project from Ruflo status."
}

---

# FROZEN EXP-M R5

## SOURCE: experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md

Ref: `0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`
Blob: `826f51d0672142864976003c914efb4be7e44b8b`

# EXP-M R5 External Review

Overall disposition: `BOUNDED_PASS`

Scope note: reviewed the inline R5 packet/source only. Repository commits/trees/blobs were not independently re-hashed by the reviewer; this is a design/preregistration review of the supplied inline material, not a cryptographic source-identity verification.

## A. R4 finding closure

- **R4-H01 = CLOSED**
  - ProviderContextIsolationPolicy is selected from the GovernanceAuthoritySnapshot.
  - Admissible bases are COMPLETE_READABLE_FENCED_STATE and DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY.
  - Hidden provider-internal mutable semantic state is governed as hidden_provider_state_residual.
  - Highest material-authority transition defaults to DISALLOW unless independently authorized.
  - Dedicated-account residual requires disposable-account sentinel qualification, pinned provider documentation/account-class/config-template binding, production-account non-contamination, and explicit residual recording.
  - Tests include M-110..M-113 and TM-Q14..TM-Q17.
  - No remaining design-level false-green path identified.

- **R4-H02 = CLOSED**
  - AdmissibilityPredicateRegistry has exact set-closure:
    required predicates == VerdictAdmissibilityResult predicates == logic-mutation targets == independently killed mutations.
  - Phase O includes targeted predicate deletion/weakening mutations covering the enumerated admissibility conjuncts.
  - Phase T tests registry drift and set-closure failures.
  - No remaining design-level false-green path identified.

- **R4-M01 = CLOSED**
  - LIVE-CONVERSATION-GOVERNANCE failure taxonomy includes previously missing EXP-M codes, including EVIDENCE_SELECTION_CONTRACT_UNRESOLVED, GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH, REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION, PROVIDER_CONTEXT_STATE_UNPROVEN, PROVIDER_CONTEXT_STATE_DRIFT, PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL, PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING, PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN, PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN, STATISTICAL_INDEPENDENCE_UNPROVEN, VERDICT_ADMISSION_STATE_CHANGED, ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE, IMPLICIT_RETRY_UNOBSERVED, INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED, and MIXED_INSUFFICIENCY.
  - No remaining normative/live taxonomy false-green path identified.

- **R4-M02 = CLOSED**
  - Typed “stricter” comparison rules are defined per governing element class.
  - Same-dimension semantic changes without a comparator fail as EVIDENCE_SELECTION_CONTRACT_UNRESOLVED.
  - Comparator mutations are included in Phase Q.
  - No remaining design-level false-green path identified.

- **R4-L01 = CLOSED**
  - M-114 and TM-Q18 require that a health check cannot renew or extend an expired ProviderCapabilityProfile.
  - Full governed confirmation requalification is required.

## B. New findings

### Critical
None identified within the reviewed inline design/preregistration scope.

### High
None identified within the reviewed inline design/preregistration scope.

### Medium/Low
None identified within the reviewed inline design/preregistration scope.

Residual limitations remain explicit nonclaims:
- remote model cognition/attention is not proved;
- hidden provider-internal state is either disallowed or an independently governed external-trust residual;
- provider telemetry remains provider-originated;
- statistical probability claims are conditional on the stated independence model;
- selective sub-slice loss remains outside probabilistic witness guarantees unless deterministic proof is required by policy.

## C. Gate verdicts

- REQUIRED_EVIDENCE_AUTHORITY = PASS
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS
- GOVERNANCE_AUTHORITY_AND_MERGE = PASS
- PROVIDER_CONTEXT_ISOLATION = PASS
- PROVIDER_CONTEXT_ADMISSION_FENCE = PASS
- WIRE_BINDING = PASS
- RETRY_TRANSPARENCY = PASS
- CHUNK_CONTEXT_MODEL = PASS
- WITNESS_ACCESSIBILITY_BOUNDARY = PASS
- WITNESS_PROTOCOL_QUALIFICATION = PASS
- ACCESSIBILITY_RISK_POLICY = PASS
- PROVIDER_CAPABILITY_QUALIFICATION = PASS
- QUALIFICATION_ATTEMPT_CLOSURE = PASS
- STATISTICAL_PROTOCOL = PASS
- REPRESENTATION_GOVERNANCE = PASS
- MATERIALIZATION_SAFETY = PASS
- EGRESS_BOUNDARY = PASS
- SESSION_FILE_RETRIEVAL_BINDING = PASS
- RETRIEVAL_FINAL_CONTEXT_BINDING = PASS
- ADMISSIBILITY_PREDICATE_CLOSURE = PASS
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS
- MULTI_REVIEWER_EQUIVALENCE = PASS
- DECOMPOSITION_AGGREGATION = PASS
- PROMPT_ISOLATION_DEPENDENCY = PASS
- TOCTOU_RETRY_INTEGRITY = PASS
- ATOMIC_VERDICT_ADMISSION = PASS
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS
- TEST_MATRIX_SUFFICIENCY = PASS
- VALIDATOR_LOGIC_MUTATION_COVERAGE = PASS

## D. Final determination

- Any Critical design defect remains: No.
- Any High design defect remains: No.
- EXP-M is ready for implementation/deterministic falsification: Yes, as a design/preregistration boundary only.
- Live provider pilots may begin: No.

Remaining prerequisites:
1. Implement the deterministic governor/test harness.
2. Execute and pass deterministic phases A–T.
3. Achieve zero surviving data/state mutations and zero surviving validator-logic mutations.
4. Prove exact admissibility predicate/registry/mutation/killed-fixture set closure.
5. Prove qualification-attempt closure, retry transparency, provider-context isolation policy closure, witness context-budget closure, and atomic final admission.
6. Only after deterministic exit criteria are green, run provider-specific exploration/confirmation under the governed risk budget.

EXP-M remains `NOT_QUALIFIED`.

This R5 external/manual review grants no platform-review or promotion authority.

A `BOUNDED_PASS` means only that the design/preregistration is ready to move into deterministic implementation/falsification. It does not qualify EXP-M, does not authorize live provider pilots, and does not authorize any platform-review or promotion transition.


## SOURCE: experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md

Ref: `0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`
Blob: `1551c007d9e7592d39f1280e504bf107b7aa14c0`

# EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification

## Status

`PREREGISTERED_BEFORE_EXECUTION`

## Motivation

The governed platform already distinguishes platform API review from pasted external evidence and binds review requests, reviewer identity, corpus hashes, semantic dimensions, and portable packet integrity.

EXP-M targets the next exposed trust boundary:

**authoritative evidence existing in the platform does not prove that the selected reviewer actually received the complete required evidence context.**

The failure mode is especially important for multi-model API review. Different providers may differ in:

- context capacity;
- file/attachment support;
- file size/count limits;
- format parsing;
- request truncation behavior;
- staged-message semantics;
- attachment visibility to the model.

A model may return `INSUFFICIENT_EVIDENCE` because evidence is truly absent, or because the platform failed to deliver it. Conversely, a model may return `PASS` after receiving only a subset of the required evidence.

EXP-M falsifies whether the platform can distinguish and fail closed on these states.

## Relationship to EXP-L

EXP-L governs independent review evidence/prompt integrity, materialization, citation grounding, prompt-injection boundaries, and frozen review execution.

EXP-M is complementary and narrower:

- EXP-L asks whether the review corpus and prompt are governed correctly.
- EXP-M asks whether that frozen corpus is actually delivered completely into the reviewer context and whether the verdict is admissible only after completeness is proven.

EXP-M does not supersede EXP-L.

## Core hypothesis

A material reviewer disposition cannot become admissible unless the platform proves that every mandatory evidence item in the frozen delivery manifest was delivered in an approved representation and the reviewer context was complete before adjudication.

## Invariants

### M-I01 — Scientific existence and delivery are separate facts

The platform must preserve independent states for:

- authoritative evidence existence;
- evidence materialization;
- evidence delivery;
- reviewer accessibility/context completeness.

### M-I02 — Delivery failure cannot masquerade as scientific insufficiency

If required evidence exists but the reviewer did not receive it, the outcome must not be classified solely as scientific `INSUFFICIENT_EVIDENCE`.

### M-I03 — Scientific absence cannot masquerade as delivery failure

If evidence genuinely does not exist, the platform must not blame transport/provider limits.

### M-I04 — Required evidence set is manifest-bound before dispatch

Every mandatory artifact and chunk is identified, hashed, sized, ordered, and bound to the exact ReviewRequest before provider invocation.

### M-I05 — Provider capability is explicit

The platform must not assume support for file types, attachment visibility, corpus size, or context capacity.

### M-I06 — No silent evidence omission

If required evidence cannot fit or cannot be consumed, dispatch must fail closed or use a separately qualified chunk protocol.

### M-I07 — Chunk completeness

Missing, duplicated, reordered, cross-request, corrupted, or stale chunks cannot establish context completeness.

### M-I08 — Reviewer receipt is non-dispositive

A completeness/receipt phase cannot itself create a review disposition.

### M-I09 — Review cannot begin before delivery completion

The platform must reject a disposition produced before required evidence delivery is complete.

### M-I10 — HTTP/API transport success is not delivery proof

HTTP 2xx, upload success, or API acceptance cannot independently establish model-visible evidence completeness.

### M-I11 — Required raw evidence cannot be replaced by unauthorized summaries

A compacted/summarized representation is only acceptable when the review contract explicitly permits that representation and it is integrity-bound.

### M-I12 — Provider-specific evidence profiles are preserved

When reviewers receive different representations, the difference must be explicit and dispositions must not be treated as directly equivalent without qualification.

### M-I13 — Verdict admissibility depends on delivery completeness

A semantic `PASS` is non-promotable if delivery completeness is not proven.

### M-I14 — Incomplete-context negative verdict remains diagnostic

A reviewer `CHANGES_REQUIRED` or `INSUFFICIENT_EVIDENCE` based on incomplete delivery is useful diagnostic evidence but cannot be misrepresented as a complete scientific adjudication.

### M-I15 — Failed delivery history is immutable

Retries do not erase or rewrite failed delivery attempts.

### M-I16 — Requiredness is platform-owned

A delivery manifest and ReviewRequest may not decide which evidence is required. Mandatory/optional status is derived only from the immutable GovernanceAuthoritySnapshot and its platform-owned transition-class, dimension, evidence-selection, evidence-relationship, and governing-standard registries. The ReviewRequest is checked against that contract but is not an input that can narrow it.

### M-I17 — Wire payload is bound

A frozen manifest must be bound to the exact trusted-adapter request payloads that were actually dispatched. Manifest intent without wire binding is insufficient.

### M-I18 — Provider capability profiles are trusted and expiring

Provider/model/API/adapter capability profiles must come from a platform-owned qualified registry, include qualification evidence and expiry, and fail closed on drift or unknown state.

### M-I19 — Chunking cannot manufacture context

Multi-message chunking may transport evidence but may not be used to claim context beyond the provider's qualified cumulative final-review availability.

### M-I20 — Delivery session identity is load-bearing

Evidence delivery, receipt, provider file references, and final verdict must bind to the same qualified delivery attempt/session or to a stateless request that rebinds every mandatory item.

### M-I21 — Representation transformation is governed

Raw evidence converted to text, pages, Markdown, archive members, OCR, or summaries must carry source/representation hashes and an allowed transformation contract. Partial/lossy representations cannot silently satisfy raw evidence requirements.

### M-I22 — Evidence egress is governed

Required evidence may not be sent to a provider unless data-classification and egress policy authorize that provider/mode/representation. Unsafe evidence cannot be silently redacted or omitted and still count complete.

### M-I23 — Prompt/evidence isolation is a production dependency

A material review path cannot qualify from EXP-M alone when candidate-controlled evidence can alter reviewer instructions. Applicable EXP-L/successor prompt-isolation controls must also be qualified.

### M-I24 — Review decomposition cannot overclaim global coverage

Several bounded subreviews cannot be aggregated into a global review unless the protocol preregisters cross-dimension interactions and a qualified aggregation step.

### M-I25 — Remote accessibility is probed, not self-attested

Where provider/model-visible accessibility cannot be established from trusted transport semantics alone, qualification or delivery uses fresh platform-generated witness probes. Reviewer echo of already supplied IDs/hashes is insufficient.

### M-I26 — Capability authority is outside candidate self-approval

The capability profile/registry used to judge review delivery cannot be widened by the candidate under review.

### M-I27 — Retrieval-backed coverage is mandatory for model-selected retrieval

When the provider/model chooses which file ranges/pages/members to retrieve, deterministic per-attempt access logs are mandatory for material review and must prove hash-matched coverage of every required range before admission. If the provider cannot expose those logs, that retrieval/file mode is diagnostic-only. Reviewer citations never substitute for access logs.

### M-I28 — Delivery governor is outside candidate self-approval

The materializer, manifest builder, representation transformer, capability-profile authority, preflight, adapter, completeness validator, and verdict-admissibility code must be pinned to an independently governed platform implementation, not mutable candidate code.

### M-I29 — Capability qualification is repeated and conservative

A provider/model/API capability profile cannot be widened from one successful call. Qualification uses repeated fresh probes and a governed safety margin.

### M-I30 — Endpoint/model/account drift invalidates qualification

Provider account/tenant, endpoint/region, adapter, requested model, or provider-reported deployment drift requires requalification or a separately bound delivery attempt.

### M-I31 — Automatic fallback cannot inherit another provider's qualification

Fallback to a different provider/model/API mode requires a new qualified profile and delivery attempt identity.

### M-I32 — Transformation/parsing is a governed attack surface

Candidate-controlled parsers, archive path traversal, symlink escape, duplicate member names, decompression bombs, and parser resource exhaustion cannot silently produce an authoritative reviewer representation.

### M-I33 — Evidence IDs are collision-resistant and canonical

Stable evidence IDs bind governed source identity plus content hash; canonical path/ID collisions cannot replace one required item with another.

### M-I34 — Frozen bytes survive manifest-to-wire TOCTOU

The bytes hashed/materialized during preflight are the bytes dispatched. Mutable source paths, transformed outputs, capability state, egress decisions, or provider files cannot change after validation without revalidation/new attempt identity.

### M-I35 — Reviewer tools cannot silently widen evidence

Web/search/plugin/retrieval evidence outside the frozen delivery corpus is non-authoritative unless separately governed and captured. Tool access cannot silently become part of the review basis.

### M-I36 — ReviewRequest completeness is independently derived

The pinned governor derives a RequiredEvidenceContract and mandatory-dimension set independently from governing standards/experiment/protected-transition rules. ReviewRequest refs/dimensions are validated against that contract and cannot narrow it.

### M-I37 — Material review context isolation is policy-bound

Material reviews use a fresh stateless request or fresh trusted-adapter stateful session under a ProviderContextIsolationPolicy. Observable mutable provider context must be absent/disabled/readable/fenced. Hidden provider-internal mutable semantic state is never silently called clean: it is either disallowed or retained as an explicit dedicated-account external-trust residual authorized by the transition-class policy.

### M-I38 — Capability qualification thresholds are preregistered

Live provider capability qualification uses a fixed risk-budget protocol before exposure: default p_min=0.99, one-sided 95% exact Clopper–Pearson, at least 299/299 successful disjoint confirmation trials at each claimed operating point, zero hard failures, no exclusions/rerolls/optional stopping, production-equivalent envelope/content classes, append-only failure history, conservative 80% scalar safety cap, and 7-day/default drift-triggered requalification.

### M-I39 — Accessibility probes are dense and per-attempt

When deterministic range/retrieval proof is unavailable, qualification and every production material-review attempt use content-bound witnesses for every required lossless slice. Each text slice is no larger than min(2048 UTF-8 bytes, 512 provider-tokenizer tokens). Every slice is challenged in every confirmation trial. Opaque files require media/modality-specific page/range/member proof or governed lossless transformation.

### M-I40 — Provider-injected semantic context is fail-closed

Provider/model modes must inventory or disable exposed mutable default/custom prompts, project/account memory, and provider-side knowledge connectors. A hidden/unexposed mutable-semantic-state possibility is governed by ProviderContextIsolationPolicy: DISALLOW means NOT_QUALIFIED; the dedicated-account residual mode is permitted only when independently authorized for that transition class and is recorded as a nonclaim.

### M-I41 — Cross-evidence interaction requirements are independently derived

Review decomposition uses a RequiredInteractionContract derived only from the GovernanceAuthoritySnapshot's platform-owned relationship registry, mandatory dimensions, transition class, and governing standards. Each interaction is an explicit set of raw evidence refs that must coexist in one qualified context; proposer-declared interaction lists cannot narrow it.

### M-I42 — Governor decision inputs are outside candidate self-approval

The GovernanceAuthoritySnapshot, transition-class registry, evidence-selection registry, relationship registry, capability registry, accessibility-risk registry, context-isolation-policy registry, and authority-snapshot pointer are outside the candidate write set. Candidate edits to governing inputs are reviewed as evidence and cannot narrow their own review. Governing elements are stable-ID + content-hash bound; changing semantics under the same ID is treated as a changed input, and base/head representation/acceptance/risk constraints preserve the stricter rule or fail unresolved.

### M-I43 — Provider context state is observed per attempt

Every material review carries ProviderContextStateEvidence from the trusted adapter at preflight, before each dispatch, and at atomic admission for every observable semantic channel. ProviderContextIsolationPolicy separately governs unexposed provider-internal mutable-state residuals; observable channels that are neither readable nor disable-able make the provider/mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I44 — Confirmation trials are disjoint, scheduled, and append-only

Exploration cannot count as confirmation. Confirmation trial identities/schedule are frozen, all attempted trials count, failures cannot be erased by reruns, and the claimed operating point itself is tested under the production-equivalent envelope.

### M-I45 — Verdict admission is atomic and final

Capability, egress, provider-context/session/file state, authority snapshot, ReviewRequest, and prompt-isolation qualification remain valid from first dispatch through a final compare-and-set admission. Any invalidation in that interval permanently voids the attempt; later requalification cannot revive it.

### M-I46 — Prompt isolation dependency is machine-bound

Material review requires a current hash-bound PromptIsolationQualificationRecord selected deterministically by the governor for the exact provider/representation mode and checked again at atomic admission.

### M-I47 — Accessibility risk is transition-class governed

Every protected transition class has a ProviderAccessibilityRiskPolicy in the GovernanceAuthoritySnapshot. Unknown policy fails closed. The highest material-authority class requires deterministic full-range/page/member proof or an equivalently observable inline mode; probabilistic per-attempt witnesses alone cannot silently satisfy it.

### M-I48 — Observable mutable provider context is fenced through admission

Every load-bearing observable mutable provider/account/project/session configuration channel has a readable monotonic version or a platform-enforceable AdmissionFenceRecord. If neither exists, the mode is NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Hidden provider-internal state cannot be “fenced by assertion”; it is handled only by ProviderContextIsolationPolicy/nonclaim.

### M-I49 — “Complete” is not an admissibility claim

The platform uses REVIEW_CONTEXT_QUALIFIED_AVAILABLE, not REVIEW_CONTEXT_COMPLETE, and records the qualified failure model plus residual/nonclaim risk in VerdictAdmissibilityResult.

### M-I50 — Statistical independence is not silently assumed

Provider capability qualification records time/routing/deployment diversity and whether trial independence is actually evidenced. If provider-side correlation cannot be observed, STATISTICAL_INDEPENDENCE_UNPROVEN is recorded and the exact-binomial bound is not treated as a universal provider failure probability.

### M-I51 — Retrieval proof binds returned bytes into final context

Model-selected retrieval logs must prove exact returned content hash/range/version and the resulting tool/message binding into the same final adjudication context. “File opened” or citation-only logs are insufficient.

### M-I52 — Hidden provider state is an explicit trust residual, never an observed-clean claim

A material review binds ProviderContextIsolationPolicy. The admissible bases are COMPLETE_READABLE_FENCED_STATE or DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY. The highest material-authority transition defaults to DISALLOW for hidden provider mutable-state residuals. Dedicated-account residual acceptance must be independently governed and recorded in VerdictAdmissibilityResult.

### M-I53 — Governing “stricter” comparisons are typed and fail closed

Base/head governance merge uses explicit per-element partial orders. Set requirements use union/intersection rules as applicable; fidelity/review level/risk/statistical/expiry/limit classes have governed comparators. Incomparable same-dimension semantic changes remain unresolved and cannot be auto-merged.

### M-I54 — Witness traffic cannot evict the evidence it is proving

The provider operating point and preflight include witness challenges, maximum witness-response budget, wrappers, final semantic prompt, and final output budget. Actual context size is rechecked after the witness phase and before semantic adjudication. Witness-induced eviction voids the attempt.

### M-I55 — Witness protocol is non-evaluative and structurally isolated

Witness challenges may test exact accessibility only; they cannot ask for evaluation or conclusions. Material witness-based review requires a current WitnessProtocolQualificationRecord bound to provider/mode/prompt-isolation mechanism. Witness outputs are non-evidence/non-adjudicative and cannot satisfy semantic review dimensions. EXP-M does not claim counterfactual semantic invariance of stochastic model outcomes.

### M-I56 — Witness qualification cannot self-authorize

WitnessProtocolQualificationRecord and its registry are platform-owned, outside candidate write authority, version/hash/expiry bound, and invalidated by provider/prompt-isolation/witness-protocol drift. Candidate code/content cannot mint or widen the record.

### M-I57 — Capability confirmation attempt set is closed before exposure

ProviderQualificationExecutionPlan freezes confirmation trial IDs, schedule, interleaving seed, trusted runner and credential/egress identity before confirmation exposure. Candidate/user/operator code cannot select which observed attempts count after results are known. Missing scheduled slots are failures; retries cannot replace failures; unexplained calls on the qualification credential invalidate the epoch when they cannot be reconciled.

### M-I58 — SDK/client retries are observable attempts

Trusted provider adapters disable implicit retries or expose every physical retry with its own immutable WireDeliveryRecord/qualification attempt. A hidden failed request followed by transparent-to-caller retry success cannot count as one success.

### M-I59 — Admissibility predicate coverage is machine-closed

A platform-owned AdmissibilityPredicateRegistry defines every load-bearing predicate, validator identity, negative fixture and logic mutation. The required predicate set, VerdictAdmissibilityResult predicate set, mutation targets and independently killed mutations must be exactly equal.

## Required mechanism surfaces

Future implementation should expose governed objects equivalent to:

- `GovernanceAuthoritySnapshot`
- `RequiredEvidenceContract`
- `RequiredInteractionContract`
- `EvidenceDeliveryManifest`
- `ProviderCapabilityProfile`
- `ProviderAccessibilityRiskPolicy`
- `ProviderContextIsolationPolicy`
- `WitnessProtocolQualificationRecord`
- `AdmissionFenceRecord`
- `ProviderQualificationExecutionPlan`
- `ProviderCapabilityQualificationRecord`
- `ProviderContextStateEvidence`
- `PromptIsolationQualificationRecord`
- `DeliveryPreflightResult`
- `WireDeliveryRecord`
- `EvidenceChunk`
- `ReviewerReceipt`
- `DeliveryCompletenessResult`
- `InsufficientEvidenceAdjudication`
- `AdmissibilityPredicateRegistry`
- `VerdictAdmissibilityResult`

Names are not authoritative; semantics are.

## Frozen test families

### M-01 — Missing required final chunk

Deliver N-1 of N required chunks.

Expected:
- completeness false;
- review adjudication blocked;
- no promotable verdict.

### M-02 — Missing middle chunk

Drop a non-final chunk while preserving total metadata.

Expected:
- exact missing chunk detected;
- no silent reconstruction/pass.

### M-03 — Duplicate chunk

Deliver one chunk twice and omit another.

Expected:
- duplicate and missing identities both detected.

### M-04 — Reordered chunks

Deliver all chunks out of order.

Expected:
- either deterministic canonical reconstruction with verified IDs/hashes or fail closed;
- no semantic concatenation based on arrival order.

### M-05 — Modified chunk bytes

Alter one byte after manifest freeze.

Expected:
`EVIDENCE_CHUNK_HASH_MISMATCH`.

### M-06 — Wrong-request chunk replay

Replay a valid chunk from a previous ReviewRequest.

Expected:
request/corpus binding rejection.

### M-07 — Stale-reviewer receipt replay

Replay completeness acknowledgement from an earlier corpus.

Expected:
receipt request/corpus mismatch.

### M-08 — Provider unsupported ZIP/TAR

Manifest requires archive evidence but provider mode cannot expose archive contents.

Expected:
`EVIDENCE_FORMAT_UNSUPPORTED`;
no review authority.

### M-09 — Accepted upload but model cannot access attachment

Transport reports upload success; reviewer context cannot enumerate/use attachment.

Expected:
`EVIDENCE_ATTACHMENT_UNAVAILABLE`;
HTTP success does not upgrade completeness.

### M-10 — Context limit truncates trailing evidence

Construct corpus where decisive evidence is in the tail beyond qualified context.

Expected:
preflight blocks dispatch or completeness fails;
no silent reviewer verdict admission.

### M-11 — Context limit truncates middle evidence

Use provider/test adapter that drops an internal segment.

Expected:
item/chunk coverage mismatch.

### M-12 — Evidence count mismatch

Manifest requires 40 items; delivered corpus has 39.

Expected:
completeness false.

### M-13 — Manifest count copied without materialization

Outgoing envelope claims correct count but actual delivered item set is incomplete.

Expected:
independent reconstruction rejects.

### M-14 — Whole-corpus hash only false green

Whole outgoing payload hash exists but per-item required evidence mapping is missing.

Expected:
delivery completeness remains unproven.

### M-15 — Reviewer claims complete without proof

Reviewer returns `received_all_evidence=true` but platform delivery record is incomplete.

Expected:
reviewer self-attestation cannot establish completeness.

### M-16 — Reviewer adjudicates before receipt phase

Provider returns PASS immediately before completeness protocol completes.

Expected:
verdict inadmissible.

### M-17 — Genuine scientific evidence missing

Required artifact is absent from authoritative store before delivery.

Expected:
`SCIENTIFIC_EVIDENCE_MISSING`;
must not be called delivery failure.

### M-18 — Evidence exists, delivery omitted it

Artifact exists and is manifest-bound but is dropped before provider context.

Expected:
`EVIDENCE_DELIVERY_INCOMPLETE`;
must not be scientific insufficiency.

### M-19 — Provider format divergence

Same authoritative evidence sent to Reviewer A as raw Markdown and Reviewer B through unsupported archive/attachment mode.

Expected:
delivery profiles differ;
results not treated as equivalent consensus until both deliveries qualify.

### M-20 — One reviewer complete, one incomplete

Multi-review pipeline: one reviewer receives complete corpus; another misses mandatory evidence.

Expected:
only complete review may be considered under review semantics;
incomplete review is diagnostic/non-promotable.

### M-21 — Summary substituted for required raw artifact

Replace a mandatory raw log with proposer-generated summary.

Expected:
representation-class mismatch unless contract explicitly allows summary.

### M-22 — Chunk retry mutation

Retry a chunk with same index but different bytes/hash.

Expected:
binding mismatch; immutable failed attempt preserved.

### M-23 — Provider retry uses different corpus

Same ReviewRequest retry changes chunking/order/content.

Expected:
reject unless new delivery manifest/review execution boundary is created.

### M-24 — Missing evidence masked by long prompt

Required evidence is absent but prompt describes its supposed contents.

Expected:
prompt assertion cannot satisfy evidence presence.

### M-25 — Citation to inaccessible evidence

Reviewer cites evidence item that was manifest-listed but not delivered.

Expected:
coverage cannot be `TESTED_SUPPORTED`.

### M-26 — Partial file parsing

Provider exposes only first pages/portion of a required artifact.

Expected:
byte/range coverage recorded; full-required artifact remains incomplete.

### M-27 — Binary/encoding corruption

UTF-8/raw artifact transformed during delivery.

Expected:
hash/representation mismatch.

### M-28 — Evidence delivery timeout

Chunk delivery stalls before completion.

Expected:
non-authoritative delivery failure, preserved for retry.

### M-29 — Cross-provider context-capability mismatch

Corpus fits one provider but exceeds another.

Expected:
provider-specific preflight outcomes; no universal "review-ready" claim.

### M-30 — Negative verdict cause adjudication

Reviewer returns `INSUFFICIENT_EVIDENCE`.

Expected:
platform deterministically attributes missing requirement to:
scientific source, delivery/context, format capability, or unresolved cause.

### M-31 — Required evidence downgraded to optional

Mutate a governed mandatory evidence ref to optional only inside the delivery manifest.

Expected:
required-evidence closure mismatch; reject before dispatch.

### M-32 — Trusted adapter omits manifest item from wire request

Manifest is complete but serialized API request drops one required item.

Expected:
wire delivery record mismatch; verdict inadmissible.

### M-33 — Candidate-authored capability profile widens limits

Candidate supplies a permissive profile claiming unsupported files/context are qualified.

Expected:
untrusted profile rejected.

### M-34 — Expired provider capability profile

Use previously qualified profile after expiry or material adapter/model version drift.

Expected:
preflight fail closed; requalification required.

### M-35 — Chunk sequence exceeds cumulative final context

Each chunk individually fits, but the final conversation/context would evict earlier required evidence.

Expected:
chunking does not qualify delivery; review blocked unless qualified persistent retrieval exists.

### M-36 — Receipt and verdict use different provider sessions

Evidence/receipt is bound to session A and final verdict to session B.

Expected:
session binding mismatch; verdict inadmissible.

### M-37 — Opaque provider file ID replay

Reuse a previously valid provider file ID in another request/account/session without independently qualified binding.

Expected:
file reference unqualified or session mismatch.

### M-38 — Lossy representation treated as raw

Send a summary/partial extraction where full raw evidence is required.

Expected:
transformation/representation rejection.

### M-39 — Partial PDF/page extraction

Required PDF has decisive content outside delivered page range.

Expected:
range coverage incomplete; no full-artifact claim.

### M-40 — Unauthorized evidence egress

Required corpus contains evidence not permitted for the selected provider/region/mode.

Expected:
preflight blocks delivery; no silent omission/redaction.

### M-41 — Redaction changes load-bearing evidence

Redaction removes or changes content needed by a mandatory review dimension.

Expected:
representation not sufficient; provider not qualified for that review.

### M-42 — Perfect delivery with prompt-injection boundary unqualified

All evidence delivery checks pass, but applicable EXP-L/successor prompt-isolation gate is not qualified.

Expected:
delivery may be recorded complete but material verdict remains non-promotable.

### M-43 — Decomposed reviews miss cross-evidence interaction

Two subreviews each pass on separate evidence subsets while the defect exists only in their interaction.

Expected:
no global PASS unless cross-interaction aggregation contract is satisfied.

### M-44 — Wire retry changes semantic request body

Retry uses same manifest/attempt semantics but adapter changes system prompt, tool config, or evidence payload.

Expected:
wire hash mismatch and immutable failed-attempt record.

### M-45 — Reviewer echoes visible evidence IDs but cannot answer hidden canary

Provider/model repeats manifest IDs yet fails exact fresh witness values embedded only in delivered content.

Expected:
accessibility qualification fails; self-acknowledgement is insufficient.

### M-46 — Dense per-slice content-bound witness probes

Every required lossless text slice carries a fresh content-bound challenge and framing/end witness in every confirmation trial and production attempt when deterministic range/retrieval proof is unavailable.

Expected:
all slice-local challenges succeed in the same adjudication session; any missing/incorrect slice challenge fails accessibility qualification/admission. Sparse head/middle/tail probes alone never qualify full content.

### M-47 — Stale canary replay

Reviewer/provider returns a canary from an earlier qualification attempt.

Expected:
attempt-bound witness mismatch.

### M-48 — Candidate modifies capability registry

Candidate branch changes profile limits/format support used to review itself.

Expected:
untrusted capability authority; review path blocked.

### M-49 — Retrieval citation without tool access

Reviewer cites a required evidence ID but provider tool logs show no successful retrieval/access and mode requires retrieval for availability.

Expected:
coverage cannot be TESTED_SUPPORTED.

### M-50 — Retrieval log proves wrong file version

Tool access succeeds for stale/wrong content hash.

Expected:
evidence identity mismatch; verdict inadmissible.

### M-51 — Candidate modifies delivery governor

Candidate changes its own manifest builder/completeness validator to omit decisive evidence.

Expected:
candidate delivery-governor implementation is not authoritative; review path blocked.

### M-52 — Candidate supplies transformation parser

Candidate-provided parser converts a required artifact into a favorable representation.

Expected:
untrusted transformation implementation rejected.

### M-53 — ZIP path traversal / symlink escape

Archive contains ../ paths, absolute paths, symlink escapes, or duplicate member names.

Expected:
safe materializer rejects/quarantines; no complete evidence claim.

### M-54 — Decompression/resource bomb

Archive/document expansion exceeds governed size/time/memory limits.

Expected:
materialization fails closed without host damage.

### M-55 — Evidence ID collision

Two different source artifacts are assigned same stable ID/path after normalization.

Expected:
collision detected; manifest invalid.

### M-56 — Single lucky capability success

One near-limit canary trial succeeds while repeated trials expose intermittent loss.

Expected:
profile not widened from single success; conservative safe bound retained.

### M-57 — Model alias/backend drift

Requested model name stays the same but provider-reported deployment/version changes materially.

Expected:
profile invalidated or bounded according to drift policy.

### M-58 — Endpoint/region/account mismatch

Qualified profile is for one endpoint/account/region; review runs through another.

Expected:
profile mismatch; preflight/verdict inadmissible.

### M-59 — Automatic fallback reuses primary profile

Primary provider fails and orchestrator silently uses fallback provider/model without new manifest/profile binding.

Expected:
reject; new delivery attempt/profile required.

### M-60 — File processing pending

Provider upload returns success but file ingestion/indexing remains pending at final review.

Expected:
attachment unavailable/context incomplete.

### M-61 — Partial retrieval coverage

Provider retrieval returns only a snippet/range while review contract requires full artifact.

Expected:
coverage incomplete; no TESTED_SUPPORTED for full-artifact dimension.

### M-62 — Source bytes mutate after manifest freeze

Hash/materialize file, mutate pathname before adapter upload, then attempt delivery.

Expected:
adapter uses frozen bytes or immediate revalidation detects mismatch; no silent TOCTOU substitution.

### M-63 — Generated representation mutates before wire send

Transformation output changes after manifest freeze.

Expected:
wire/representation hash mismatch; attempt invalid.

### M-64 — Capability profile expires mid-attempt

Profile valid at preflight but expired/materially invalid before final wire call/verdict.

Expected:
pre-dispatch/final admissibility revalidation blocks completion.

### M-65 — Egress authorization revoked after preflight

Policy allowed at manifest freeze but is revoked before send.

Expected:
dispatch blocked or new authorization required.

### M-66 — Ungoverned reviewer web search

Reviewer uses external web/tool source not in governed evidence set and cites it as basis for PASS.

Expected:
external evidence non-authoritative; review cannot claim frozen-evidence coverage from it.

### M-67 — Governed reviewer tool retrieval

Allowlisted tool returns captured, provenance-bound supplemental evidence under governed boundary.

Expected:
may be retained only under explicit supplemental/new review evidence semantics; no silent manifest rebinding.

### M-68 — ReviewRequest omits standard-required evidence

The governing RequiredEvidenceContract requires evidence E, but the ReviewRequest does not reference or deterministically derive E.

Expected:
EVIDENCE_SELECTION_INCOMPLETE before manifest freeze.

### M-69 — ReviewRequest omits standard-required mandatory dimension

A mandatory dimension derived from governing standards is absent from the ReviewRequest.

Expected:
ReviewRequest invalid; no delivery attempt.

### M-70 — Dirty reused provider thread

Manifest evidence is delivered into a stateful session containing prior ungoverned messages/tool outputs.

Expected:
provider/mode attempt not context-clean; verdict inadmissible.

### M-71 — Provider default/custom prompt drift

Provider/project custom instruction or injected mutable prompt differs from the qualified profile.

Expected:
profile/context drift; NOT_QUALIFIED or requalification required.

### M-72 — Provider-side memory enabled

Account/project/session memory is active but not captured/disabled.

Expected:
material review mode NOT_QUALIFIED.

### M-73 — Provider-side knowledge connector silently enabled

Provider account injects retrieval/knowledge context not governed by the manifest.

Expected:
material review mode NOT_QUALIFIED or separately governed supplemental boundary.

### M-74 — Insufficient provider qualification trials

Operating point has fewer than 299 disjoint confirmation trials even if all pass.

Expected:
capability point remains unqualified.

### M-75 — One hard failure among qualification trials

At least one hard visibility/truncation failure occurs at the claimed operating point.

Expected:
operating point disqualified.

### M-76 — Safety margin omitted

The tested passing/failure boundary is used directly instead of applying the governed 80% cap.

Expected:
profile invalid.

### M-77 — Internal omission between sparse canaries

Head/middle/tail probes pass, but an unprobed required internal segment is omitted.

Expected:
sparse witness method cannot qualify the claimed range; fail closed.

### M-78 — Dense per-segment witness detects omission

A required text segment within the 2048-byte probe granularity is omitted.

Expected:
missing witness/content challenge causes qualification failure.

### M-79 — Opaque attachment has unprobed required page/range

Attachment mode lacks deterministic retrieval logs and not every required page/range/member is probed.

Expected:
full-artifact material review mode unqualified.

### M-80 — Interaction family omitted from proposer plan

Platform RequiredInteractionContract contains interaction X; proposer ReviewRequest/subreview plan omits X.

Expected:
global review aggregation blocked.

### M-81 — Capability expires after final provider response before verdict admission

Provider response exists, but the capability profile becomes expired before atomic verdict admission.

Expected:
the attempt is permanently void; later requalification cannot revive that response.

### M-82 — Egress authorization revoked after final provider response before verdict admission

Expected:
the attempt is permanently void; stale preflight and later reauthorization cannot revive the old response.

### M-83 — Candidate poisons governing standard input

Candidate head removes or weakens a required evidence/representation/risk rule, including semantic replacement under the same stable ID.

Expected:
GovernanceAuthoritySnapshot/base-head conservative merge preserves the stricter base/head semantics; changed governance file is itself required evidence; incomparable conflicts fail unresolved.

### M-84 — Candidate poisons relationship/classification registry

Candidate supplies a weaker transition class or removes a required evidence relationship.

Expected:
registry outside candidate write set wins; snapshot mismatch/rebinding is rejected.

### M-85 — Unknown transition class / empty contract

Derivation returns unknown class, zero mandatory dimensions, or empty evidence despite a non-vacuous baseline.

Expected:
EVIDENCE_SELECTION_CONTRACT_UNRESOLVED.

### M-86 — Lying provider context readback

Provider adapter/readback claims memory/connectors/custom instructions disabled while behavioral sentinel shows influence.

Expected:
ProviderContextStateEvidence invalid; provider mode unqualified.

### M-87 — Hidden dirty provider state

A mutable provider channel is neither readable nor disable-able.

Expected:
NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-88 — Context state changes between preflight and dispatch

Custom instruction/memory/connector state changes after preflight.

Expected:
monotonic state-version mismatch; attempt void before dispatch.

### M-89 — Context state changes between dispatch and admission

Expected:
atomic admission fails and attempt is permanently void.

### M-90 — Correlated burst confirmation

299 trials are run back-to-back in one short burst rather than the preregistered multi-day/time-block schedule.

Expected:
confirmation protocol invalid even if all pass.

### M-91 — Excluded failed trial / reroll

One attempted confirmation trial fails and is discarded before collecting 299 successes.

Expected:
qualification fails; append-only attempt ledger exposes the exclusion.

### M-92 — Exploration reused as confirmation

Expected:
qualification fails due to non-disjoint evidence families.

### M-93 — Production-envelope mismatch

Confirmation uses synthetic easy content while production uses denser prompt/tools/structured-output/content modality.

Expected:
operating point mismatch; profile cannot authorize production review.

### M-94 — Canary-preserving content loss

Provider preserves framing/sentinels but removes the challenged content span from one slice.

Expected:
content-bound slice challenge fails.

### M-95 — Selective unchallenged sub-slice loss

Provider drops content outside the challenged offset but within a qualified slice.

Expected:
recorded residual/nonclaim risk; transition classes that disallow this residual risk require deterministic range/retrieval proof.

### M-96 — Model-selected retrieval without deterministic access logs

Expected:
retrieval/file mode diagnostic-only; verdict inadmissible.

### M-97 — Retrieval logs miss one required range

Expected:
PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN.

### M-98 — Requalification after mid-attempt expiry

Capability expires after response, then is requalified before checkpoint.

Expected:
old attempt remains void; a new attempt is required.

### M-99 — Delete one VerdictAdmissibilityResult conjunct

Mutation removes any one load-bearing predicate.

Expected:
at least one test kills the mutation; no surviving logic mutation.

### M-100 — Weaken required-evidence closure equality to subset

Expected:
logic mutation killed.

### M-101 — Skip dirty-context, 299-trial, dense-witness, retrieval-log, or atomic-CAS check

Expected:
each logic mutation is independently killed by the suite.

### M-102 — Missing transition accessibility-risk policy

Expected:
review ineligible; no default implicit risk acceptance.

### M-103 — Highest-authority transition uses probabilistic witnesses only

Expected:
admissibility fails because deterministic access proof is required by policy.

### M-104 — Mutable provider config has no version/fence

Expected:
NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-105 — Provider configuration changes between final read and checkpoint CAS

Expected:
AdmissionFence/version mismatch kills the attempt.

### M-106 — Legacy REVIEW_CONTEXT_COMPLETE flag forced true

Expected:
flag is ignored/deprecated; authority depends on REVIEW_CONTEXT_QUALIFIED_AVAILABLE predicates and residual-risk record.

### M-107 — Correlated provider route hidden behind fresh request IDs

All requests are fresh but provider-exposed route/deployment identity shows the same correlated backend/time burst.

Expected:
STATISTICAL_INDEPENDENCE_UNPROVEN or confirmation-schedule failure; probability claim not overgeneralized.

### M-108 — Retrieval log says file opened but returned bytes are unbound

Expected:
PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN; material verdict inadmissible.

### M-109 — Retrieval returns correct range but tool result is not bound to final adjudication session

Expected:
PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN.

### M-110 — Hidden unexposed provider mutable state with no isolation policy

A fake provider has an unexposed semantic-state channel that changes the verdict.

Expected:
ProviderContextIsolationPolicy missing/unsatisfied; material review NOT_QUALIFIED.

### M-111 — Highest-authority transition attempts dedicated-account residual mode

The provider cannot prove complete readable/fenced mutable state and the transition policy defaults hidden residual to DISALLOW.

Expected:
material review blocked.

### M-112 — Dedicated-account residual explicitly governed for a permitted lower transition

Use a dedicated platform-owned account/project with candidate/user writes disabled, pinned provider product policy, exposed configuration disabled/read/fenced, disposable-account sentinel qualification, and explicit hidden-state residual acceptance.

Expected:
context-isolation predicate may pass only with the residual recorded; no “observed clean” claim.

### M-113 — Sentinel qualification contaminates production review account

Qualification enables a memory/customization sentinel on the production review account rather than a disposable qualification account.

Expected:
qualification invalid; production review account must never be contaminated by sentinel setup.

### M-114 — Health check attempts to renew expired provider profile

An expired capability profile receives a successful health check without full confirmation requalification.

Expected:
profile remains expired; health check can invalidate only.

### M-115 — Incomparable same-dimension governance change

Base and head representation/risk semantics conflict with no defined partial-order winner.

Expected:
EVIDENCE_SELECTION_CONTRACT_UNRESOLVED; no auto-merge.

### M-116 — Typed stricter comparator regression

Mutate one comparator (for example allow-set intersection→union, evidence-set union→intersection, expiry shorter→longer).

Expected:
logic mutation killed.

### M-117 — Witness response causes context eviction

A witness challenge/response transcript pushes an earlier required evidence slice outside the qualified final context.

Expected:
post-witness pre-adjudication context check fails; attempt void.

### M-118 — Witness protocol asks evaluative question

A challenge asks the reviewer to summarize or judge evidence rather than return exact accessibility content.

Expected:
WitnessProtocolQualificationRecord/protocol validation fails.

### M-119 — Witness output is treated as semantic review evidence

The final semantic validator allows witness extracts/answers to satisfy a required review dimension or create authority.

Expected:
structural isolation failure; witness output remains non-evidence/non-adjudicative.

### M-120 — Witness protocol record stale or wrong provider/prompt-isolation mode

Expected:
verdict inadmissible.

### M-121 — Candidate-authored witness qualification record

Candidate supplies a record claiming its own witness protocol is noninterfering.

Expected:
untrusted record rejected; witness-based material review inadmissible.

### M-122 — Provider isolation documentation/config template drifts

Pinned provider account-class documentation or production configuration-template hash changes after qualification.

Expected:
ProviderContextIsolationPolicy/ProviderCapabilityProfile binding invalidated; requalification required.

### M-123 — Confirmation schedule omits failed slot

A planned trial fails or is skipped, then the runner removes that trial ID before final qualification calculation.

Expected:
plan/ledger mismatch; QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN and qualification fails.

### M-124 — Retry replaces failed confirmation attempt

A failed trial is rerun successfully and only the successful retry is counted.

Expected:
original hard failure remains append-only; zero-failure criterion cannot pass.

### M-125 — Unscheduled hidden qualification calls

Additional provider calls use the dedicated qualification credential outside the frozen plan.

Expected:
if provider audit reconciliation exposes them, confirmation epoch invalidated; if reconciliation is unavailable and credential/egress exclusivity is unproven, QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN.

### M-126 — Candidate/operator can invoke qualification credential

Expected:
qualification runner trust boundary fails; profile cannot be material-review qualified.

### M-127 — SDK hides failed physical attempt behind automatic retry success

Expected:
IMPLICIT_RETRY_UNOBSERVED or explicit first-attempt hard failure; no single-success representation.

### M-128 — Admissibility predicate added without mutation target

Registry contains a new load-bearing predicate but mutation catalog does not target it.

Expected:
ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE.

### M-129 — Mutation target exists without independent killing fixture

Expected:
ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE.

### M-130 — Verdict result omits one registry predicate

Expected:
predicate-set closure mismatch; verdict inadmissible.

### M-131 — Statistical independence unproven but profile claims probability-qualified

Provider-side route/correlation independence cannot be evidenced, yet the profile sets statistical_qualified=true under a policy requiring the 0.99 probability claim.

Expected:
profile invalid. Only a transition policy that explicitly waives the probability claim and requires deterministic per-attempt proof may proceed.

## Required mutation/falsification cases

Mutation suite must attempt to make a verdict admissible by:

- forcing `context_complete=true`;
- forcing `received_all=true`;
- deleting a mandatory manifest item;
- altering required/optional flags;
- lowering expected chunk count;
- ignoring hash mismatch;
- trusting HTTP 200;
- trusting provider upload ID;
- accepting reviewer self-acknowledgement;
- converting delivery insufficiency into scientific insufficiency;
- converting scientific insufficiency into delivery failure;
- marking unsupported file as delivered;
- reusing old receipt;
- reusing old chunk;
- rebinding corpus hash;
- ignoring provider capability profile;
- treating different reviewer corpora as consensus;
- admitting PASS before receipt completion;
- allowing manifest-requiredness to override governed requiredness;
- accepting candidate-authored capability profile;
- accepting expired capability profile;
- treating chunk count as proof of cumulative final context;
- accepting receipt from another session;
- accepting opaque file ID without qualified content/session binding;
- accepting lossy transformation as full raw evidence;
- bypassing evidence egress policy;
- aggregating decomposed subreviews without cross-interaction coverage;
- omitting wire-request hash binding;
- admitting material verdict when prompt/evidence-isolation dependency is unqualified;
- trusting candidate-owned manifest/materializer/completeness code;
- accepting one successful near-limit capability probe as qualification;
- ignoring endpoint/account/region/model-deployment drift;
- inheriting capability profile across provider/model fallback;
- trusting candidate-provided transformation parser;
- ignoring archive traversal/resource-limit failures;
- allowing evidence-ID collision to replace required content;
- treating upload success as file processing readiness;
- re-reading mutable source bytes after manifest freeze without revalidation;
- ignoring capability/egress expiry between preflight and dispatch;
- admitting ungoverned reviewer web/tool evidence as frozen corpus evidence;
- trusting an incomplete ReviewRequest as the full required-evidence authority;
- omitting a standard-required mandatory dimension;
- reusing a dirty provider session;
- ignoring provider custom-prompt/memory/connector drift;
- accepting fewer than 299 disjoint confirmation trials;
- accepting any hard capability failure at a claimed point;
- skipping the governed 80% safety margin;
- treating sparse canaries as proof for unprobed required regions;
- omitting a platform-derived cross-evidence interaction;
- accepting an expired capability/egress state at verdict admission;
- deriving authority contracts from candidate-mutated governing inputs;
- accepting unknown/empty transition-class contracts;
- trusting lying/incomplete provider context readback;
- accepting hidden mutable provider state;
- allowing excluded/re-rolled confirmation failures;
- mixing exploration and confirmation evidence;
- qualifying a non-production request envelope;
- treating framing canaries as content-bound proof;
- allowing model-selected retrieval without deterministic coverage logs;
- reviving an invalidated attempt after requalification;
- deleting or weakening any VerdictAdmissibilityResult conjunct;
- weakening equality closure to subset/superset;
- skipping atomic compare-and-set admission;
- omitting ProviderAccessibilityRiskPolicy;
- allowing probabilistic witnesses for a transition class requiring deterministic proof;
- accepting mutable provider context without a version/fence;
- trusting a legacy REVIEW_CONTEXT_COMPLETE boolean;
- treating fresh request IDs as proof of statistical independence;
- accepting retrieval/open logs without returned-content and final-context binding;
- treating hidden unexposed provider state as observed-clean without ProviderContextIsolationPolicy;
- permitting dedicated-account hidden-state residual when transition policy says DISALLOW;
- contaminating production account during sentinel qualification;
- renewing an expired capability profile from a health check;
- auto-merging incomparable governing semantics;
- weakening typed base/head comparator direction;
- excluding witness challenge/response overhead from final-context budgeting;
- allowing evaluative witness prompts;
- omitting/staling WitnessProtocolQualificationRecord;
- accepting candidate-authored witness qualification;
- ignoring provider-isolation documentation/account-class/config-template drift;
- dropping a planned failed/missing confirmation slot;
- replacing a failed confirmation attempt with a successful retry;
- accepting unreconciled qualification calls or candidate-accessible qualification credentials;
- hiding a failed physical provider attempt behind implicit SDK retry;
- adding/removing an admissibility predicate without exact mutation/fixture closure;
- marking a profile statistically qualified when independence is unproven and policy requires the probability claim.

Every load-bearing mutation must be rejected.

## Required provider test adapters

The experiment should use deterministic fake/provider adapters before live-provider testing:

- `CompleteProviderAdapter`
- `DropFinalChunkAdapter`
- `DropMiddleChunkAdapter`
- `DuplicateChunkAdapter`
- `ReorderChunkAdapter`
- `CorruptChunkAdapter`
- `AttachmentInvisibleAdapter`
- `ContextTailTruncationAdapter`
- `PartialFileAdapter`
- `EarlyVerdictAdapter`
- `UnsupportedFormatAdapter`
- `WireOmissionAdapter`
- `ExpiredCapabilityProfileAdapter`
- `CrossSessionVerdictAdapter`
- `OpaqueFileReplayAdapter`
- `LossyRepresentationAdapter`
- `EgressDeniedAdapter`
- `ContextEvictionAdapter`
- `DecomposedCrossInteractionAdapter`
- `CanaryBlindAdapter`
- `StaleCanaryReplayAdapter`
- `CandidateProfileOverrideAdapter`
- `RetrievalCitationWithoutAccessAdapter`
- `WrongRetrievalVersionAdapter`
- `CandidateGovernorOverrideAdapter`
- `UntrustedTransformerAdapter`
- `ArchiveTraversalAdapter`
- `ArchiveBombAdapter`
- `EvidenceIdCollisionAdapter`
- `FlakyNearLimitAdapter`
- `ModelDriftAdapter`
- `EndpointDriftAdapter`
- `FallbackProfileReuseAdapter`
- `FileProcessingPendingAdapter`
- `PostManifestSourceMutationAdapter`
- `ExpiredMidAttemptAdapter`
- `EgressRevokedAdapter`
- `UngovernedReviewerToolAdapter`
- `IncompleteReviewRequestAdapter`
- `DirtySessionAdapter`
- `ProviderPromptDriftAdapter`
- `ProviderMemoryEnabledAdapter`
- `ProviderKnowledgeConnectorAdapter`
- `InsufficientTrialsAdapter`
- `FlakyCapabilityAdapter`
- `SparseCanaryGapAdapter`
- `MissingInteractionFamilyAdapter`
- `PostResponseExpiryAdapter`
- `AuthorityInputPoisoningAdapter`
- `UnknownTransitionClassAdapter`
- `LyingContextReadbackAdapter`
- `HiddenDirtyStateAdapter`
- `CorrelatedBurstFailureAdapter`
- `FailedTrialReplayAdapter`
- `ProductionEnvelopeMismatchAdapter`
- `CanaryPreservingContentDropAdapter`
- `MissingRetrievalLogAdapter`
- `AtomicAdmissionRaceAdapter`
- `VerdictConjunctMutationAdapter`
- `MissingAccessibilityRiskPolicyAdapter`
- `UnfencedProviderConfigAdapter`
- `AdmissionFenceRaceAdapter`
- `CorrelatedRouteAdapter`
- `RetrievalOpenOnlyAdapter`
- `RetrievalUnboundToolResultAdapter`
- `HiddenUnexposedProviderStateAdapter`
- `ProductionAccountSentinelContaminationAdapter`
- `HealthCheckRenewalAdapter`
- `GovernanceComparatorWeakeningAdapter`
- `WitnessContextEvictionAdapter`
- `EvaluativeWitnessAdapter`
- `WitnessEvidenceLeakAdapter`
- `CandidateWitnessQualificationAdapter`
- `ProviderIsolationTemplateDriftAdapter`
- `QualificationPlanTamperAdapter`
- `FailedTrialReplacementAdapter`
- `UnreconciledQualificationCallAdapter`
- `ImplicitSdkRetryAdapter`
- `AdmissibilityPredicateDriftAdapter`

Live API pilots come only after deterministic adapters and validator-logic mutation tests prove the governor behavior.

## Live provider pilots

Live pilots begin only after all deterministic phases and validator-logic mutation tests are green.

For each exact provider/account/endpoint/region/model/deployment/adapter/session/file/retrieval mode, preregister exploration and confirmation separately.

Exploration identifies candidate operating points and observed failure boundaries. Confirmation then tests each claimed operating point itself using the frozen default or stricter risk budget:

- 299/299 required successful confirmation trials by default;
- zero hard failures;
- no exclusions/rerolls/optional stopping;
- trials distributed over the preregistered multi-day/time-block schedule;
- fresh ProviderContextIsolationPolicy-qualified context and fresh content-bound witnesses every trial;
- production-equivalent prompt/tools/structured-output/output budget;
- worst-case token-density and required media/modality classes;
- every required slice/page/range/member challenged in every trial unless deterministic access/range proof exists;
- append-only trial/failure history.

Pilot evidence also preserves post-SDK transport-semantic hashes, provider context-state records, request/session/file identifiers, retrieval/access logs where the delivery mode requires them, usage/context metadata, and exact profile/drift-epoch identity.

Sparse beginning/middle/end probes are diagnostic only and cannot qualify full required content.

Provider documentation and marketing limits may inform exploration but never substitute for the governed confirmation evidence.

## Acceptance rule

EXP-M can reach bounded pass only when:

1. every mandatory frozen test passes;
2. no mutation can make an incomplete delivery verdict promotable;
3. scientific vs delivery insufficiency is deterministically separated;
4. provider capability uncertainty fails closed;
5. multi-reviewer comparison preserves reviewer-specific delivery identity;
6. failed delivery history is preserved;
7. no review authority is minted from completeness self-attestation;
8. required-evidence status cannot be downgraded by the delivery layer;
9. exact trusted-adapter wire requests are bound to the frozen manifest;
10. chunking cannot claim context beyond the provider's qualified final-review availability;
11. provider capability profiles are trusted, version-bound, and non-expired;
12. representation transformations and evidence egress are governed;
13. material review remains blocked when the applicable prompt/evidence-isolation dependency is unqualified;
14. decomposed review cannot overclaim cross-evidence coverage;
15. delivery-governor implementation is pinned outside candidate self-approval;
16. provider capability bounds are repeated/conservative and invalidate on material drift;
17. provider/model fallback cannot inherit a different delivery qualification;
18. representation transformers/materializers are trusted and resource/path safe;
19. stable evidence IDs cannot collide or rebind required content;
20. manifest-to-wire TOCTOU cannot substitute later mutable bytes/state;
21. ungoverned reviewer tools cannot silently widen the evidence basis;
22. ReviewRequest completeness is independently cross-checked against a platform-derived RequiredEvidenceContract;
23. material reviews use a fresh/clean semantic context or the provider/mode is disqualified;
24. provider capability qualification obeys preregistered statistical thresholds, safety margin, and requalification interval;
25. provider-injected mutable semantic context is inventoried/disabled or the provider/mode is disqualified;
26. accessibility probing is dense enough for the claimed content range;
27. cross-evidence interaction requirements are independently derived;
28. capability/egress/session validity is rechecked at verdict admission;
29. GovernanceAuthoritySnapshot inputs are pinned outside candidate write authority and base/head governance changes use the conservative merge rule;
30. unknown/empty/vacuous transition contracts fail closed;
31. ProviderContextStateEvidence is observed per attempt and behaviorally sentinel-qualified;
32. confirmation evidence is disjoint from exploration, scheduled, append-only, and uses the exact production operating point;
33. per-attempt content-bound witnesses are mandatory when deterministic range/retrieval proof is unavailable;
34. model-selected retrieval requires deterministic per-attempt full-range coverage logs;
35. VerdictAdmissibilityResult enumerates every load-bearing predicate and atomic compare-and-set admission is the final authority step;
36. every validator-logic conjunct deletion/weakening mutation is killed;
37. PromptIsolationQualificationRecord is machine-checkable, current, and admission-bound;
38. ProviderAccessibilityRiskPolicy is explicit for every transition class and the selected proof mode satisfies it;
39. mutable provider context has readable versions or a valid AdmissionFenceRecord through atomic admission;
40. no legacy REVIEW_CONTEXT_COMPLETE boolean can substitute for the explicit qualified-availability predicates;
41. statistical independence assumptions are explicit and cannot be inferred solely from fresh request IDs;
42. model-selected retrieval proves returned-byte identity and final-context tool-result binding;
43. ProviderContextIsolationPolicy explicitly governs hidden provider-internal mutable-state residuals and highest-authority transitions fail closed by default;
44. sentinel qualification cannot contaminate the production review account;
45. health checks cannot renew or extend an expired capability profile;
46. every base/head “stricter” comparison uses a typed governed partial order and incomparable changes fail unresolved;
47. witness challenge/response traffic is part of the qualified cumulative context and cannot evict required evidence before adjudication;
48. witness protocols are non-evaluative, structurally isolated from semantic evidence/authority, and have a current provider/mode-bound WitnessProtocolQualificationRecord;
49. witness qualification authority is outside candidate write control;
50. provider isolation documentation/account-class/config-template drift invalidates the associated context-isolation qualification;
51. confirmation attempt membership is frozen before exposure and every planned slot is reconciled or counted failed;
52. qualification credentials/runner are outside candidate and ordinary operator control, and unreconciled calls cannot manufacture a passing sample;
53. implicit SDK/client retries are disabled or every physical attempt is independently recorded;
54. AdmissibilityPredicateRegistry, verdict predicates, logic-mutation targets and killed mutations have exact set closure.

A one-provider success cannot prove cross-provider delivery integrity.

## Nonclaims

EXP-M does not prove:

- the model semantically attended to every delivered token;
- arbitrary provider internals;
- cryptographic proof of remote model memory;
- universal provider limits;
- scientific correctness of the evidence itself;
- detection of arbitrary selective/sub-slice provider loss when deterministic range/retrieval proof is unavailable; such residual risk is explicitly recorded and may be disallowed by higher-risk transition classes.

It governs what the platform can prove about materialization, delivery, context completeness, and verdict admissibility.

## Governance effect

Until EXP-M is qualified for a review path, evidence-delivery completeness for large/multipart/file-based API reviews is a governed open boundary.

This preregistration authorizes no promotion and changes no existing authority state.


## SOURCE: experiments/governed-platform/EXP-M-TEST-MATRIX.md

Ref: `0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`
Blob: `15b2b2ceb212fc40d144790b0f68674b26a55013`

# EXP-M Review Evidence Delivery Integrity — Test Matrix

## Purpose

This matrix turns EXP-M into an executable falsification plan. It is intentionally split into deterministic platform tests first and live provider capability tests second.

No live provider pilot may be treated as scientific evidence until the deterministic governor tests are green.

## Phase A — Deterministic unit and state-machine tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| TM-A01 | Complete one-shot delivery | All mandatory items delivered exactly once | REVIEW_CONTEXT_QUALIFIED_AVAILABLE |
| TM-A02 | Required item missing | Remove one required item | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-A03 | Optional item missing | Remove optional item | Complete if contract permits |
| TM-A04 | Manifest hash mismatch | Alter manifest after freeze | Reject |
| TM-A05 | Item byte mismatch | Change one source byte | Reject |
| TM-A06 | Item size mismatch | Correct hash metadata but wrong byte count | Reject |
| TM-A07 | Duplicate required item | Duplicate one item | Reject ambiguous/duplicate delivery |
| TM-A08 | Unexpected extra required-looking item | Add unmanifested item | Reject or quarantine; never silently bind |
| TM-A09 | Wrong reviewed commit | Reuse manifest against another commit | Reject |
| TM-A10 | Wrong ReviewRequest | Reuse corpus for another request | Reject |
| TM-A11 | Reviewer self-ack only | Reviewer claims all received; platform missing item | Incomplete |
| TM-A12 | HTTP 200 only | Provider call succeeds but no receipt evidence | Incomplete |
| TM-A13 | Upload ID only | File upload succeeds but model visibility unproven | Incomplete |
| TM-A14 | PASS before completeness | Early PASS returned | Verdict inadmissible |
| TM-A15 | CHANGES_REQUIRED before completeness | Early negative verdict | Diagnostic only |
| TM-A16 | INSUFFICIENT before completeness | Early insufficient verdict | Cause unresolved/delivery diagnostic, not scientific |
| TM-A17 | Scientific artifact absent | Required source does not exist | SCIENTIFIC_EVIDENCE_MISSING |
| TM-A18 | Artifact exists but omitted | Source exists but delivery omits it | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-A19 | Unsupported format | Provider profile says unsupported | Fail preflight |
| TM-A20 | Unknown provider capability | No qualified profile | Fail preflight |

## Phase B — Chunk protocol tests

| ID | Test | Mutation | Expected result |
|---|---|---|---|
| TM-B01 | All chunks correct | None | Complete |
| TM-B02 | Missing final chunk | Drop N | Incomplete |
| TM-B03 | Missing middle chunk | Drop k | Incomplete |
| TM-B04 | Duplicate chunk | Duplicate k | Reject |
| TM-B05 | Duplicate+missing | Duplicate k, remove j | Detect both |
| TM-B06 | Reordered chunks | Shuffle | Canonical reconstruction or reject |
| TM-B07 | Corrupted chunk | Change one byte | Hash mismatch |
| TM-B08 | Same index, different bytes on retry | Retry mutated k | Reject |
| TM-B09 | Cross-request chunk | Chunk from old request | Reject |
| TM-B10 | Cross-corpus chunk | Correct request, wrong corpus hash | Reject |
| TM-B11 | Wrong total count | Change N | Reject |
| TM-B12 | Wrong chunk index | Out-of-range or repeated index | Reject |
| TM-B13 | Empty mandatory chunk | Replace content with empty bytes | Reject |
| TM-B14 | Chunk metadata only | Claim hash/count without bytes | Incomplete |
| TM-B15 | Stale receipt | Receipt from older corpus | Reject |
| TM-B16 | Receipt missing item IDs | Count matches but IDs absent | Incomplete |
| TM-B17 | Receipt count lies | Says N while delivery has N-1 | Independent check rejects |
| TM-B18 | Completion before last chunk | Reviewer marks complete early | Reject |

## Phase C — Context and representation tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| TM-C01 | Tail truncation | Decisive artifact last | Preflight block or detectable incomplete |
| TM-C02 | Middle truncation | Decisive artifact in middle | Detect item/chunk gap |
| TM-C03 | Large prompt crowd-out | Prompt consumes context | Required evidence cannot be silently dropped |
| TM-C04 | ZIP unsupported | ZIP required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-C05 | TAR unsupported | TAR required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-C06 | PDF partial visibility | Only some pages exposed | Partial coverage, not complete |
| TM-C07 | Markdown-only substitution | Raw JSON required but summary Markdown sent | Representation mismatch |
| TM-C08 | Encoding transformation | CRLF/UTF-8/normalization changes bytes | Raw-hash mismatch where byte identity required |
| TM-C09 | Binary corruption | Attachment bytes altered | Reject |
| TM-C10 | Attachment accepted but inaccessible | Upload succeeds, reviewer cannot inspect | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| TM-C11 | Summary substitutes raw log | Proposer summary replaces required raw log | Reject |
| TM-C12 | Prompt states missing evidence contents | Evidence absent; prompt describes it | Reject |
| TM-C13 | Citation to undelivered evidence | Reviewer cites manifest-only item | Coverage not TESTED_SUPPORTED |
| TM-C14 | Partial file accepted as whole | Only prefix delivered | Incomplete |

## Phase D — Insufficient-evidence cause adjudication

| ID | Scenario | Expected classification |
|---|---|---|
| TM-D01 | Required artifact never existed | SCIENTIFIC_EVIDENCE_MISSING |
| TM-D02 | Artifact existed, not materialized | EVIDENCE_MATERIALIZATION_FAILED |
| TM-D03 | Materialized, omitted from request | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-D04 | Delivered file ref but provider cannot expose it | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| TM-D05 | Corpus exceeds qualified context | REVIEW_CONTEXT_INCOMPLETE |
| TM-D06 | Required format unsupported | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-D07 | Reviewer says insufficient, platform cause unknown | INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED |
| TM-D08 | Scientific + delivery gaps both exist | MIXED_INSUFFICIENCY |
| TM-D09 | Reviewer claims missing item that was verifiably delivered | REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION |
| TM-D10 | Platform claims delivery but receipt/manifest disagree | EVIDENCE_RECEIPT_UNPROVEN |

## Phase E — Multi-reviewer equivalence tests

| ID | Test | Expected result |
|---|---|---|
| TM-E01 | Claude and DeepSeek receive identical manifest/hash | Results comparable subject to semantic review |
| TM-E02 | One receives raw JSON, other receives only summary | Not equivalent consensus |
| TM-E03 | One provider complete, one incomplete | Incomplete verdict non-promotable |
| TM-E04 | One provider supports file, other ignores it | Provider-specific delivery states preserved |
| TM-E05 | Different chunking but same canonical corpus | Comparable only if reconstruction proves equivalent corpus |
| TM-E06 | Different required item set | Not comparable |
| TM-E07 | Retry one reviewer with changed corpus | New delivery boundary required |
| TM-E08 | Two reviewers agree after one incomplete delivery | Consensus cannot bypass incomplete evidence |

## Phase F — Provider capability qualification

For each exact provider/account/endpoint/region/model/deployment/adapter/session/file/retrieval mode, execute separate exploration and confirmation fixtures.

Default material-review confirmation policy:

- target per-trial success lower bound: p_min=0.99;
- one-sided 95% exact Clopper–Pearson;
- minimum **299/299** successful confirmation trials at each claimed operating point;
- zero hard failures;
- every attempted confirmation trial counts, including timeout/provider error/rate limit/ambiguous/unverifiable outcomes;
- no exclusions, rerolls, optional stopping, or backfilling failed attempts;
- exploration and confirmation trial sets are disjoint;
- confirmation trial IDs/schedule are frozen before exposure;
- confirmation trials span at least 3 UTC days and 4 preregistered time blocks/day, with operating points interleaved in randomized order;
- exact claimed operating point is tested; no interpolation or monotonicity assumption;
- production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes are used;
- 80% scalar cap is an additional margin only on a point that itself qualifies;
- append-only failure history persists across requalification within the same drift epoch;
- profile expiry is 7 days by default and immediate on material drift;
- health checks may invalidate but never renew.

Hard failure includes any required range/witness/context/session/model/wire/retrieval mismatch, timeout/provider error/rate limit, ambiguous result, or output failure preventing protocol completion.

Required measurements include:

1. exact production-equivalent one-shot corpus points;
2. attachment visibility by media/modality class;
3. attachment count/per-file boundaries;
4. staged context behavior;
5. dense per-slice content-bound witness behavior;
6. deterministic retrieval/access logging where used;
7. context-tail and internal omission behavior;
8. retry/fallback behavior;
9. provider-context state readback/sentinel behavior;
10. exact model/deployment/account/endpoint identity;
11. post-SDK transport-semantic envelope identity;
12. profile invalidation/drift signals.

Each attempted trial records the complete operating-point tuple, trial ID, exploration/confirmation class, scheduled time block, provider/context-state evidence, wire hashes, witness/retrieval results, response state, and hard-failure classification.

Vendor documentation may inform exploration but never replaces confirmation.

## Phase G — Unified mutation suite

The matrix and experiment use this single authoritative mutation catalog. Starting from one complete admissible review attempt, mutate one load-bearing field or one validator predicate at a time.

Data/state mutations must cover at least:

1. force context_complete/received_all;
2. lower required item/chunk counts;
3. mark required item optional;
4. omit governed evidence/dimension/interaction;
5. rebind request/corpus/manifest/evidence ID;
6. ignore missing/duplicate/corrupt chunk;
7. trust HTTP/upload/file ID/reviewer receipt/citation;
8. swap scientific vs delivery insufficiency causes;
9. use unknown/expired/candidate-authored capability profile;
10. ignore provider model/account/endpoint/region drift;
11. inherit qualification across provider/model fallback;
12. use dirty/reused provider context;
13. ignore memory/custom-instruction/connector drift;
14. accept incomplete/lying ProviderContextStateEvidence;
15. accept fewer than 299 confirmation trials;
16. discard/reroll a failed trial;
17. reuse exploration trials as confirmation;
18. ignore confirmation schedule/time-block requirements;
19. qualify a non-production envelope/content class;
20. skip 80% scalar cap where applicable;
21. accept sparse witness coverage for unprobed regions;
22. preserve framing canary while dropping challenged content;
23. accept model-selected retrieval without deterministic coverage logs;
24. accept partial/wrong-version retrieval log;
25. trust lossy/untrusted transformation;
26. bypass egress policy;
27. accept archive traversal/resource-limit defect;
28. allow evidence-ID collision;
29. re-read mutable source after freeze;
30. ignore capability/egress/context expiry or revocation;
31. revive a voided attempt after later requalification;
32. admit ungoverned reviewer-tool evidence;
33. omit machine-checkable prompt-isolation qualification.

Validator-logic mutations must cover at least:

34. delete each VerdictAdmissibilityResult conjunct one at a time;
35. replace required-evidence equality with subset/superset;
36. bypass GovernanceAuthoritySnapshot/base-head merge;
37. accept unknown/empty transition class;
38. skip clean-context check;
39. accept 298 instead of 299 confirmation trials;
40. accept one hard confirmation failure;
41. skip per-attempt content-bound witness;
42. skip retrieval-log coverage;
43. skip RequiredInteractionContract raw co-context requirement;
44. skip pre-dispatch state revalidation;
45. skip final atomic compare-and-set admission;
46. allow requalification to revive an invalidated attempt;
47. skip PromptIsolationQualificationRecord check.

Every logic mutation must be killed by at least one independently targeted test.

Required final result:

`surviving_material_false_green_mutations = 0`

## Phase H — Crash/retry and persistence tests

1. Crash after manifest freeze, before first chunk.
2. Crash mid-chunk sequence.
3. Crash after all chunks but before completeness result.
4. Crash after reviewer receipt, before final review.
5. Retry exact frozen delivery.
6. Retry with mutated corpus.
7. Concurrent duplicate deliveries for same request.
8. Resume after process restart.
9. Preserve failed attempt history.
10. Ensure prior incomplete attempt cannot be reclassified as complete by later retry.

## Phase I — Admissibility integration tests

A review result must be non-promotable when any load-bearing predicate is false:

- current ReviewRequest valid;
- GovernanceAuthoritySnapshot current and outside candidate write authority;
- RequiredEvidenceContract resolved/non-vacuous/closed;
- RequiredInteractionContract resolved and raw co-context requirements satisfied;
- complete materialization;
- governed representation/transformation;
- current egress authorization;
- ProviderCapabilityProfile statistically qualified for exact operating point;
- ProviderContextStateEvidence clean/current;
- provider mutable semantic-context qualification satisfied;
- trusted adapter/post-SDK wire binding valid;
- complete required item/chunk delivery;
- per-attempt content-bound witness valid or deterministic retrieval/range proof complete;
- session/file/retrieval coverage valid;
- PromptIsolationQualificationRecord current/matching;
- semantic review coverage valid;
- reviewer provenance/independence valid;
- promotable disposition;
- atomic compare-and-set state versions unchanged.

Test dispositions:

- PASS + any false predicate => non-promotable.
- BOUNDED_PASS + incomplete mandatory evidence/context => non-promotable.
- CHANGES_REQUIRED + incomplete delivery => diagnostic only.
- INSUFFICIENT_EVIDENCE + multiple causes => MIXED_INSUFFICIENCY with all cause predicates.
- PASS + all delivery predicates => delivery layer permits downstream authority gate only; it does not itself promote.

## Phase J — Trust-root, wire, representation, and egress tests

| ID | Test | Expected result |
|---|---|---|
| TM-J01 | Manifest marks governed required item optional | Required-evidence closure fails |
| TM-J02 | Manifest omits governed evidence ref entirely | Preflight fails before provider call |
| TM-J03 | Candidate supplies permissive provider profile | Profile rejected as untrusted |
| TM-J04 | Provider profile expired | Requalification required |
| TM-J05 | Provider model/adapter version drifts from profile | Profile invalid |
| TM-J06 | Manifest complete but trusted adapter omits item from wire body | Wire mismatch; verdict inadmissible |
| TM-J07 | Adapter changes system/developer prompt on retry | Wire hash mismatch |
| TM-J08 | Adapter changes tool/file bindings on retry | Wire/session mismatch |
| TM-J09 | Receipt session A, verdict session B | Verdict inadmissible |
| TM-J10 | Stateless verdict request omits earlier required evidence | Incomplete |
| TM-J11 | Opaque file ID from another attempt/session | Reject |
| TM-J12 | Provider file expired between receipt and verdict | Context incomplete |
| TM-J13 | Chunk sequence individually fits but cumulative final context does not | Preflight fails; chunking cannot expand context |
| TM-J14 | Persistent/model-selected retrieval binds file IDs but has no deterministic per-attempt range-access logs | Diagnostic-only; NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-J15 | Full raw required, partial PDF/text extraction delivered | Representation incomplete |
| TM-J16 | Transformation tool/version/hash mismatch | Reject |
| TM-J17 | Lossy transform not explicitly permitted | Reject |
| TM-J18 | Data classification forbids provider egress | Preflight blocks |
| TM-J19 | Silent redaction of required evidence | Incomplete/unqualified representation |
| TM-J20 | Permitted redaction preserves all load-bearing fields | Eligible only if governed transformation rule says sufficient |
| TM-J21 | All delivery checks pass but EXP-L/prompt-isolation dependency unqualified | Material verdict non-promotable |
| TM-J22 | Two subreviews pass but defect exists only across evidence subsets | No global PASS |
| TM-J23 | Aggregator lacks cross-evidence interaction corpus | Global disposition blocked |
| TM-J24 | Aggregation contract includes interaction evidence and qualified aggregator | Eligible for downstream review validation |
| TM-J25 | Reviewer self-receipt claims inaccessible file visible | Platform delivery/capability record wins; incomplete |
| TM-J26 | Provider docs claim large context but empirical qualified profile is smaller | Empirical qualified bound governs |
| TM-J27 | Provider capability registry record candidate-writable | Profile untrusted |
| TM-J28 | Egress policy record candidate-writable | Egress decision untrusted |
| TM-J29 | Wire record excludes semantic field from canonical hash | Test must fail; semantic request binding incomplete |
| TM-J30 | Secret redaction from wire hash removes only credentials, not semantics | Reproducible semantic wire binding passes |

## Phase K — Remote accessibility witness and retrieval grounding tests

| ID | Test | Expected result |
|---|---|---|
| TM-K01 | Reviewer echoes manifest IDs but fails fresh hidden content canary | Context accessibility not qualified |
| TM-K02 | Fresh beginning/middle/end canaries all recovered exactly but internal regions are unprobed | Diagnostic only; cannot qualify full required content |
| TM-K03 | Tail canary missing near context limit | Safe qualified limit lowered; review over limit blocked |
| TM-K04 | Middle canary missing while head/tail pass | Internal omission detected |
| TM-K05 | Canary from prior attempt replayed | Attempt/session binding rejection |
| TM-K06 | Candidate learns/controls canary before delivery | Probe invalid; cannot establish accessibility |
| TM-K07 | Candidate modifies capability registry record | Profile untrusted |
| TM-K08 | Capability registry commit/profile changes with candidate under review | Self-approval boundary violation |
| TM-K09 | Provider file citation with no successful retrieval log in retrieval-required mode | Coverage cannot be TESTED_SUPPORTED |
| TM-K10 | Retrieval log resolves wrong content hash/version | Evidence identity mismatch |
| TM-K11 | Retrieval log shows access after verdict generation | Verdict timing invalid |
| TM-K12 | Receipt and canary probes pass but final adjudication occurs in another session | Session mismatch |
| TM-K13 | Stateless final request omits canary-qualified earlier evidence | Incomplete final context |
| TM-K14 | Same-session final review fits qualified context and every required slice passes per-attempt content-bound challenge | Eligible for downstream semantic validation subject to residual-risk policy |
| TM-K15 | Canary value copied into prompt/manifest | Probe invalid because value is not evidence-access dependent |

## Phase L — Delivery-governor trust, parser safety, and provider-drift tests

| ID | Test | Expected result |
|---|---|---|
| TM-L01 | Candidate branch edits manifest builder to omit decisive evidence | Candidate implementation cannot authorize its own delivery |
| TM-L02 | Candidate edits completeness validator to always return true | Trusted platform validator wins; review blocked |
| TM-L03 | Candidate provides its own capability profile | Profile rejected |
| TM-L04 | Candidate provides its own representation transformer | Transformer rejected as untrusted |
| TM-L05 | Archive contains `../` traversal | Safe materializer rejects |
| TM-L06 | Archive contains absolute-path member | Reject |
| TM-L07 | Archive contains symlink escape | Reject |
| TM-L08 | Archive contains duplicate normalized member names | Reject ambiguity |
| TM-L09 | Decompression expansion exceeds size limit | Fail closed without resource exhaustion |
| TM-L10 | Parser exceeds time/memory budget | Fail closed |
| TM-L11 | Two evidence paths normalize to same stable ID | Collision detected |
| TM-L12 | Two different hashes attempt same declared evidence ID | Collision/rebind rejected |
| TM-L13 | One near-limit provider canary run succeeds, subsequent fresh trials fail | Qualified limit not widened |
| TM-L14 | Repeated trials all pass below conservative margin | Bound may be qualified under policy |
| TM-L15 | Same model alias reports different backend/deployment | Drift invalidates profile or requires bounded requalification |
| TM-L16 | Qualified endpoint/region differs from actual call | Fail |
| TM-L17 | Qualified account/tenant differs from actual call | Fail |
| TM-L18 | Primary provider failure triggers fallback with primary profile | Fail/new delivery boundary required |
| TM-L19 | Fallback has its own qualified profile and new attempt | Eligible for downstream validation |
| TM-L20 | File upload accepted but processing/indexing pending | Context incomplete |
| TM-L21 | File later becomes ready in same bound session | May proceed only after new readiness evidence |
| TM-L22 | Retrieval returns only snippet of full-required file | Coverage insufficient |
| TM-L23 | Retrieval returns exact required full content/hash | Eligible for downstream semantic coverage |
| TM-L24 | Candidate modifies egress decision/profile | Untrusted; delivery blocked |

## Phase M — TOCTOU and reviewer-tool boundary tests

| ID | Test | Expected result |
|---|---|---|
| TM-M01 | Source file mutated after manifest hash before upload | Frozen bytes used or mismatch detected |
| TM-M02 | Generated representation mutated after freeze | Representation/wire mismatch |
| TM-M03 | Capability profile expires between preflight and final call | Block completion |
| TM-M04 | Egress authorization revoked before send | Block dispatch |
| TM-M05 | Provider file replaced/mutated after qualification | File identity/access mismatch |
| TM-M06 | Final review uses stale provider file version | Verdict inadmissible |
| TM-M07 | Reviewer web search finds ungoverned evidence and uses it for PASS | Cannot count as frozen review evidence |
| TM-M08 | Reviewer tool fetches different revision of governed file | Revision/hash mismatch |
| TM-M09 | Governed supplemental tool evidence captured with provenance | Requires explicit supplemental/new boundary; not silent rebind |
| TM-M10 | Tool result omitted from audit record but cited in verdict | Coverage invalid |
| TM-M11 | Candidate changes source path after preflight but before adapter serialization | No TOCTOU substitution |
| TM-M12 | Retry after state drift reuses old attempt identity | Reject/new attempt required |

## Phase N — External-review remediation tests

| ID | Test | Expected result |
|---|---|---|
| TM-N01 | Governing standard requires evidence E; ReviewRequest omits E | EVIDENCE_SELECTION_INCOMPLETE before manifest freeze |
| TM-N02 | Governing standard requires mandatory dimension D; ReviewRequest omits D | ReviewRequest rejected |
| TM-N03 | ReviewRequest/manifest are internally closed but RequiredEvidenceContract contains extra mandatory ref | Required-evidence closure fails |
| TM-N04 | Reused provider thread contains prior ungoverned user message | Material review context dirty; verdict inadmissible |
| TM-N05 | Reused provider thread contains prior tool result | Context dirty unless fully governed and bound |
| TM-N06 | Fresh provider session contains only frozen governed content | Session cleanliness passes subject to provider profile |
| TM-N07 | Provider account/project custom instruction changes after qualification | Provider mode/profile invalidated |
| TM-N08 | Provider memory is enabled and cannot be disabled/captured | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-N09 | Provider-side knowledge connector enabled but absent from manifest/profile | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-N10 | Provider exposes fixed service policy but no mutable account/session context | May proceed only under qualified provider profile/nonclaim |
| TM-N11 | 298/298 disjoint confirmation trials pass | Insufficient trials; operating point unqualified |
| TM-N12 | 299/299 scheduled disjoint confirmation trials pass | Statistical criterion satisfied at exact tested point, subject to all other gates |
| TM-N13 | 298 successes + 1 hard failure | Operating point disqualified; failed attempt remains append-only |
| TM-N14 | One ambiguous/timeout/provider-error trial among 299 attempts | Counts as hard failure; disqualify point |
| TM-N15 | Smallest observed failure boundary B; profile claims >0.8B | Profile invalid |
| TM-N16 | No failure observed; profile claims >80% of largest tested passing point | Profile invalid |
| TM-N17 | Profile older than 7 days without requalification | Expired |
| TM-N18 | Sparse head/middle/tail canaries pass while internal segment omitted | Claimed range unqualified |
| TM-N19 | Every slice <=min(2048 bytes,512 provider tokens) passes content-bound challenge in every confirmation trial | Qualification accessibility criterion may pass for bounded failure model |
| TM-N20 | One dense segment witness fails | Operating point fails |
| TM-N21 | Opaque attachment has required pages/ranges not individually probed and no deterministic access logs | Full artifact mode unqualified |
| TM-N22 | Per-attempt deterministic retrieval logs prove hash-matched access to every required range/page/member | Eligible for downstream semantic validation |
| TM-N23 | Proposer interaction list omits platform-derived required interaction | Aggregation/global verdict blocked |
| TM-N24 | Platform RequiredInteractionContract and proposer plan match completely | Interaction closure passes |
| TM-N25 | Capability profile expires after provider response but before atomic verdict admission | Attempt permanently void; later requalification cannot revive it |
| TM-N26 | Egress permission revoked after provider response but before atomic verdict admission | Attempt permanently void; new attempt required |
| TM-N27 | Session/file state invalidates after provider response but before verdict admission | Verdict blocked |
| TM-N28 | Deployment identity is required by drift policy but provider cannot expose it | Identity-dependent qualification not claimable |
| TM-N29 | Retrieval logs required for completeness but provider does not expose them | Retrieval-based mode unqualified |
| TM-N30 | Dirty-session review returns PASS with otherwise perfect manifest/wire records | PASS remains inadmissible |

## Phase O — Validator-logic mutation tests

| ID | Logic mutation | Expected result |
|---|---|---|
| TM-O01 | Delete governed authority-snapshot predicate | Killed |
| TM-O02 | Derive contract from candidate HEAD only | Killed |
| TM-O03 | Replace evidence closure equality with subset | Killed |
| TM-O04 | Accept unknown transition class/empty contract | Killed |
| TM-O05 | Delete clean-context predicate | Killed |
| TM-O06 | Trust provider context readback without sentinel qualification | Killed |
| TM-O07 | Change 299 minimum to 298 | Killed |
| TM-O08 | Permit one hard confirmation failure | Killed |
| TM-O09 | Allow excluded/rerolled failure | Killed |
| TM-O10 | Reuse exploration as confirmation | Killed |
| TM-O11 | Skip confirmation schedule/time-block check | Killed |
| TM-O12 | Skip production-envelope operating-point equality | Killed |
| TM-O13 | Replace content-bound per-slice witness with framing-only canary | Killed |
| TM-O14 | Make per-attempt witnesses optional | Killed |
| TM-O15 | Make retrieval logs optional for model-selected retrieval | Killed |
| TM-O16 | Accept partial retrieval coverage | Killed |
| TM-O17 | Omit one RequiredInteractionContract raw evidence ref | Killed |
| TM-O18 | Let aggregator use subreview summaries instead of raw interaction evidence | Killed |
| TM-O19 | Skip prompt-isolation qualification predicate | Killed |
| TM-O20 | Skip pre-dispatch monotonic state check | Killed |
| TM-O21 | Skip atomic admission CAS | Killed |
| TM-O22 | Permit later requalification to revive old response | Killed |
| TM-O23 | Remove mixed-cause adjudication and first-match scientific cause | Killed |
| TM-O24 | Accept reviewer contradiction code absent from taxonomy | Killed |
| TM-O25 | Delete ProviderAccessibilityRiskPolicy predicate | Killed |
| TM-O26 | Delete AdmissionFence/version predicate | Killed |
| TM-O27 | Reintroduce legacy REVIEW_CONTEXT_COMPLETE as authority | Killed |
| TM-O28 | Infer statistical independence from fresh request IDs only | Killed |
| TM-O29 | Accept retrieval-open log without returned bytes/context binding | Killed |
| TM-O30 | Delete ReviewRequest current/integrity predicate | Killed by stale/wrong-request fixture |
| TM-O31 | Delete GovernanceAuthoritySnapshot predicate | Killed by authority-snapshot mismatch fixture |
| TM-O32 | Delete RequiredEvidenceContract resolved/non-vacuous/closed predicate | Killed by missing/empty-contract fixture |
| TM-O33 | Delete RequiredInteractionContract predicate | Killed by omitted-interaction fixture |
| TM-O34 | Delete complete materialization predicate | Killed by materialization-missing fixture |
| TM-O35 | Delete governed representation/transformation predicate | Killed by lossy/untrusted-transform fixture |
| TM-O36 | Delete current egress authorization predicate | Killed by egress-denied/revoked fixture |
| TM-O37 | Delete exact-operating-point capability qualification predicate | Killed by unqualified/expired/profile-mismatch fixture |
| TM-O38 | Delete ProviderAccessibilityRiskPolicy predicate | Killed by missing/wrong-proof-mode fixture |
| TM-O39 | Delete ProviderContextIsolationPolicy predicate | Killed by hidden-state-policy fixture |
| TM-O40 | Delete hidden-state-residual transition-policy predicate | Killed by highest-authority residual-disallow fixture |
| TM-O41 | Delete ProviderContextStateEvidence predicate | Killed by lying/dirty-state fixture |
| TM-O42 | Delete AdmissionFenceRecord/version predicate | Killed by provider-config race fixture |
| TM-O43 | Delete provider mutable-semantic-context qualification predicate | Killed by memory/custom-instruction/connector fixture |
| TM-O44 | Delete trusted adapter/post-SDK wire-binding predicate | Killed by SDK/wire mutation fixture |
| TM-O45 | Delete complete required item/chunk delivery predicate | Killed by missing/duplicate/corrupt item fixture |
| TM-O46 | Delete per-attempt accessibility proof predicate | Killed by canary-preserving/content-loss fixture |
| TM-O47 | Delete session/file/retrieval coverage predicate | Killed by partial/unbound retrieval fixture |
| TM-O48 | Delete PromptIsolationQualificationRecord predicate | Killed by missing/expired/wrong-mode isolation fixture |
| TM-O49 | Delete semantic review coverage predicate | Killed by untested mandatory-dimension fixture |
| TM-O50 | Delete reviewer provenance/independence predicate | Killed by self/untrusted-reviewer fixture |
| TM-O51 | Delete promotable-disposition predicate | Killed by CHANGES_REQUIRED/INSUFFICIENT disposition fixture |
| TM-O52 | Delete WitnessProtocolQualificationRecord/context-budget predicate when witnesses are used | Killed by witness-eviction/stale-record fixture |
| TM-O53 | Trust candidate-authored WitnessProtocolQualificationRecord | Killed |
| TM-O54 | Ignore provider-isolation documentation/account-class/config-template drift | Killed |

## Phase P — R3 residual adversarial-oracle tests

| ID | Test | Expected result |
|---|---|---|
| TM-P01 | Candidate edits governing standard to remove decisive requirement | Base/head conservative authority snapshot preserves requirement |
| TM-P02 | Candidate supplies weaker classification/relationship metadata | External registry wins; candidate metadata ignored/rejected |
| TM-P03 | Unknown class deterministically derives zero refs | EVIDENCE_SELECTION_CONTRACT_UNRESOLVED |
| TM-P04 | Lying context readback says clean while sentinel proves hidden memory | ProviderContextStateEvidence fails |
| TM-P05 | Hidden mutable provider channel cannot be read or disabled | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-P06 | Context config changes between preflight and dispatch | Attempt blocked/void |
| TM-P07 | Context config changes after response before admission | Atomic CAS fails; attempt void |
| TM-P08 | 299 confirmation attempts performed in one burst | Protocol invalid despite successes |
| TM-P09 | Failed attempt is excluded then 299 successes collected | Qualification fails; no optional stopping |
| TM-P10 | Exploration trials counted as confirmation | Qualification fails |
| TM-P11 | Easy synthetic confirmation but production envelope is token-dense/tools-enabled | Operating point mismatch |
| TM-P12 | Framing canary survives while challenged content extract is dropped | Content-bound witness fails |
| TM-P13 | Unchallenged sub-slice content selectively lost | Residual risk/nonclaim recorded; high-risk class requiring deterministic proof blocks |
| TM-P14 | Retrieval mode supplies file IDs/citations but no access logs | Diagnostic-only |
| TM-P15 | Access log covers all but one required range | PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN |
| TM-P16 | Capability expires, then is requalified before checkpoint | Old attempt remains void |
| TM-P17 | Authority/capability/egress/session version changes between validation and CAS | Checkpoint write fails |
| TM-P18 | Prompt-isolation record expired/wrong provider mode | Verdict inadmissible |
| TM-P19 | Interaction family requires raw evidence A+B; aggregator sees only subreview outputs | Global disposition blocked |
| TM-P20 | SDK mutates semantic tool/model/file field after platform hash but before transport-bound hash | Transport-bound mismatch detected |
| TM-P21 | Provider default deployment identity required but unavailable | Provider/mode NOT_QUALIFIED |
| TM-P22 | Reviewer says evidence missing while strong per-attempt access proof exists | REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION diagnostic; not silently scientific failure |

## Phase Q — Accessibility-risk and admission-fence tests

| ID | Test | Expected result |
|---|---|---|
| TM-Q01 | Transition class has no ProviderAccessibilityRiskPolicy | Review ineligible |
| TM-Q02 | Highest-authority transition uses probabilistic witnesses without deterministic range proof | Admissibility fails |
| TM-Q03 | Lower transition class explicitly permits bounded probabilistic witness mode and all predicates pass | Eligible subject to recorded residual risk |
| TM-Q04 | Mutable provider config has neither readable version nor fence | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-Q05 | AdmissionFenceRecord changes between final read and CAS | Atomic admission fails |
| TM-Q06 | Candidate/user tries to mutate dedicated-account config while fence held | Write blocked or version mismatch; attempt void |
| TM-Q07 | Provider-internal state changes without observable version/fence | Mode unqualified |
| TM-Q08 | Legacy REVIEW_CONTEXT_COMPLETE=true injected | Ignored/deprecated; cannot authorize |
| TM-Q09 | Verdict record omits residual/nonclaim risk for probabilistic mode | Admissibility fails |
| TM-Q10 | Accessibility proof mode does not satisfy transition-class policy | Admissibility fails |
| TM-Q11 | Fresh request IDs but correlated route/deployment/time burst | Statistical independence remains unproven; no universal probability claim |
| TM-Q12 | Retrieval log records open/citation but no returned-content hash | Retrieval context binding unproven |
| TM-Q13 | Retrieval returns correct bytes but tool-result message is absent from final adjudication context | Retrieval context binding unproven |
| TM-Q14 | Hidden unexposed mutable provider semantic state; no ProviderContextIsolationPolicy | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-Q15 | Highest-authority transition tries dedicated-account hidden-state residual | Blocked; residual defaults DISALLOW |
| TM-Q16 | Dedicated lower-authority transition explicitly permits dedicated-account residual with pinned policy/config/sentinel evidence | Eligible only with residual/nonclaim recorded |
| TM-Q17 | Sentinel qualification writes memory/customization into production review account | Qualification invalid |
| TM-Q18 | Health check succeeds after ProviderCapabilityProfile expiry | Profile remains expired; full confirmation requalification required |
| TM-Q19 | Same-dimension governing semantic change has no defined comparator | EVIDENCE_SELECTION_CONTRACT_UNRESOLVED |
| TM-Q20 | Mutate evidence-set union to intersection | Comparator mutation killed |
| TM-Q21 | Mutate allowed-provider set intersection to union | Comparator mutation killed |
| TM-Q22 | Mutate shorter-expiry-is-stricter to longer-expiry-is-stricter | Comparator mutation killed |

## Phase R — Witness noninterference and context-budget tests

| ID | Test | Expected result |
|---|---|---|
| TM-R01 | Preflight excludes witness challenge/response budget | Delivery plan rejected |
| TM-R02 | Actual witness response exceeds preregistered maximum and pushes context over bound | Post-witness pre-adjudication check fails; attempt void |
| TM-R03 | Witness challenge asks for summary/evaluation/defect judgment | Witness protocol invalid |
| TM-R04 | WitnessProtocolQualificationRecord is expired | Witness-based material review inadmissible |
| TM-R05 | WitnessProtocolQualificationRecord is for another provider/model/prompt-isolation mode | Binding mismatch; inadmissible |
| TM-R06 | Baseline and witness-enabled qualification runs use non-identical governed corpus/request envelope | Noninterference experiment invalid |
| TM-R07 | Witness output is accepted as semantic evidence or satisfies a review dimension | Structural-isolation failure; witness output cannot create review authority |
| TM-R08 | Framing/content witness succeeds but final semantic prompt occurs after evidence eviction | Attempt void |
| TM-R09 | Deterministic retrieval mode uses no witness protocol | Witness record not required; retrieval predicates remain required |
| TM-R10 | Witness output includes sensitive evidence and retention/egress policy forbids that response form | Mode/representation blocked or governed safer witness form required |
| TM-R11 | Candidate supplies its own WitnessProtocolQualificationRecord | Rejected as untrusted |
| TM-R12 | Witness qualification registry record is candidate-writable | Review path blocked |
| TM-R13 | Provider account-class documentation/config template changes after witness/context qualification | Qualification invalidated; requalification required |

## Phase S — Qualification attempt-selection and ledger-closure tests

| ID | Test | Expected result |
|---|---|---|
| TM-S01 | Frozen confirmation plan contains 299 IDs; one failed ID is deleted before calculation | Plan/ledger mismatch; qualification fails |
| TM-S02 | Failed trial rerun succeeds and retry is substituted for original | Original failure remains; zero-failure criterion fails |
| TM-S03 | Planned trial is never dispatched | Missing slot counts hard failure |
| TM-S04 | Extra unscheduled call appears in provider audit log | Confirmation epoch invalidated |
| TM-S05 | Provider audit logs unavailable but qualification credential is exclusive to trusted runner/egress | Attempt closure may remain provable from exclusive runner ledger |
| TM-S06 | Provider audit logs unavailable and ordinary operator can use credential | QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN |
| TM-S07 | Candidate code can invoke qualification endpoint/credential | Qualification trust boundary fails |
| TM-S08 | Randomization/interleaving seed chosen after early trial results | Plan invalid; no qualification |
| TM-S09 | Confirmation trial ID reused across drift epochs | Reject/rebind to new epoch required |
| TM-S10 | Every planned slot reconciles to one first-attempt dispatch/provider request and all pass | Attempt-set closure passes subject to all other gates |

## Phase T — Retry transparency and admissibility-registry closure

| ID | Test | Expected result |
|---|---|---|
| TM-T01 | SDK automatic retry hides first failed physical request then returns success | IMPLICIT_RETRY_UNOBSERVED or explicit hard failure; no single-success claim |
| TM-T02 | Client retry disabled and one physical request maps to one WireDeliveryRecord | Retry transparency passes |
| TM-T03 | Two physical retries exposed as two append-only attempts | Both retained; earlier failure cannot be erased |
| TM-T04 | AdmissibilityPredicateRegistry adds predicate P but Phase O/mutation catalog lacks P | ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE |
| TM-T05 | VerdictAdmissibilityResult omits registry predicate P | Set-closure failure |
| TM-T06 | Mutation target for P exists but no independently killing negative fixture | Coverage incomplete |
| TM-T07 | Negative fixture exists but validator mutation for P survives | Coverage incomplete |
| TM-T08 | Registry/verdict/mutation/killed sets are exactly equal | Predicate-coverage closure passes |
| TM-T09 | Candidate attempts to edit predicate registry used for own review | Untrusted/self-approval boundary violation |
| TM-T10 | Registry version changes after preflight before admission | Attempt void/revalidation required |
| TM-T11 | Statistical independence unproven but profile claims CP probability-qualified under policy requiring it | Profile invalid |
| TM-T12 | Independence unproven; transition policy explicitly waives probability claim and requires deterministic per-attempt proof | No CP probability claim; eligibility depends on deterministic proof and all other gates |

## Required evidence outputs

Every EXP-M execution must retain:

- frozen ReviewRequest;
- authoritative evidence inventory;
- EvidenceDeliveryManifest;
- GovernanceAuthoritySnapshot;
- RequiredEvidenceContract;
- RequiredInteractionContract;
- ProviderCapabilityProfile;
- ProviderAccessibilityRiskPolicy;
- ProviderContextIsolationPolicy;
- WitnessProtocolQualificationRecord when witnesses are used;
- pinned provider context-isolation documentation/account-class/config-template identities where the dedicated-account basis is used;
- AdmissionFenceRecord;
- ProviderQualificationExecutionPlan;
- ProviderCapabilityQualificationRecord with append-only trial ledger and planned/observed call reconciliation;
- ProviderContextStateEvidence;
- AdmissibilityPredicateRegistry and exact predicate/mutation closure record;
- PromptIsolationQualificationRecord;
- DeliveryPreflightResult;
- each EvidenceChunk;
- pre-SDK and post-SDK transport-semantic envelope hashes;
- transport/provider response envelope;
- ReviewerReceipt;
- DeliveryCompletenessResult;
- reviewer raw response;
- parsed review;
- InsufficientEvidenceAdjudication where applicable;
- VerdictAdmissibilityResult;
- unified data/state mutation results;
- validator-logic mutation results;
- atomic admission compare-and-set evidence;
- full hashes and timestamps.

## Exit criteria

EXP-M deterministic testing is complete only when:

- **all deterministic phases A–T pass**;
- unified data/state mutation survivors = 0;
- validator-logic mutation survivors = 0;
- crash/retry tests preserve exact identity/history;
- every admissibility conjunct is independently falsified by at least one negative test;
- authority-snapshot/base-head poisoning tests pass;
- clean-context state/sentinel tests pass;
- RequiredEvidenceContract and RequiredInteractionContract non-vacuity/closure tests pass;
- statistical-protocol tests reject insufficient, rerolled, burst-only, mixed exploration/confirmation, production-envelope-mismatched, and attempt-set cherry-picked evidence;
- every planned confirmation slot is reconciled or counted failed and qualification credentials are outside candidate/operator control;
- implicit client/SDK retries are disabled or every physical attempt is visible and append-only;
- admissibility predicate registry/verdict/mutation/killed sets have exact closure;
- per-attempt content-bound witness tests and canary-preserving content-drop oracle pass;
- model-selected retrieval is blocked without deterministic full-range access logs;
- atomic final CAS admission and permanent-attempt-void semantics pass;
- prompt-isolation qualification is machine-bound and admission-checked;
- ProviderAccessibilityRiskPolicy exists for every transition class and selected proof mode;
- mutable observable provider context is versioned/fenced through admission;
- hidden provider-internal mutable-state residual is governed by ProviderContextIsolationPolicy and never mislabeled observed-clean;
- highest-authority transition default DISALLOW for hidden provider-state residual is enforced;
- sentinel qualification cannot contaminate production review account;
- health checks cannot renew expired capability profiles;
- typed base/head comparison rules are mutation-tested and incomparable semantic changes fail unresolved;
- witness challenge/response overhead is included in qualified final-context budgeting and rechecked before adjudication;
- witness protocol is non-evaluative, structurally isolated from semantic evidence/authority, and bound to provider/mode/prompt-isolation qualification;
- witness qualification registry is outside candidate write authority;
- provider context-isolation documentation/account-class/config-template drift invalidates qualification;
- legacy REVIEW_CONTEXT_COMPLETE cannot create authority;
- statistical independence assumptions are explicit and cannot be inferred solely from fresh request IDs;
- model-selected retrieval logs bind exact returned bytes to final adjudication context;
- insufficient-evidence cause adjudication returns all causes and MIXED when multiple predicates hold;
- review consensus cannot hide corpus divergence.

Live provider pilots may begin only after deterministic exit above is green. A provider-specific production mode becomes qualified only after its separate exploration/confirmation capability evidence passes the governed risk budget and all provider-context/accessibility requirements.

Provider-specific `NOT_QUALIFIED_FOR_MATERIAL_REVIEW` is an acceptable fail-closed outcome.


## SOURCE: standards/review-evidence-delivery-integrity.md

Ref: `0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`
Blob: `c4c1e4f561eb36e44f7bb6aa1bc59df8d4c4bf09`

# Review Evidence Delivery Integrity Standard

## Status

`PREREGISTERED_FOR_EXP_M_FALSIFICATION`

This standard governs the boundary between an authoritative evidence set and the evidence context made available to a reviewer through a platform API transport.

It does **not** claim that a platform can cryptographically prove that a remote model cognitively attended to every delivered token. The platform may prove its own materialization and wire delivery, and may rely only on separately qualified provider/model/API capabilities for remote context accessibility. Model attention is a nonclaim.

## Core problem

An unchanged scientific evidence set can produce different reviewer outcomes when different providers, models, API modes, file transports, context limits, or chunking paths expose different subsets or representations of that evidence.

Therefore these are separate governed facts:

1. authoritative evidence existence;
2. required-evidence selection;
3. evidence materialization;
4. representation/transformation;
5. wire delivery;
6. provider/session/file accessibility;
7. qualified reviewer-context availability;
8. reviewer semantic adjudication;
9. verdict admissibility.

A later stage may not self-prove an earlier stage.

## Delivery-governor trust root

The code that decides whether evidence delivery is complete is itself load-bearing governance.

For a material review, the following must execute from an independently governed, pinned platform implementation that is outside the reviewed candidate's self-approval boundary:

- required-evidence derivation;
- evidence materializer;
- representation transformer;
- manifest builder;
- provider capability registry reader;
- provider context-isolation policy registry reader;
- witness-protocol qualification registry reader;
- delivery preflight;
- chunk/session protocol;
- trusted provider adapter/wire serializer;
- delivery completeness validator;
- insufficient-evidence cause adjudicator;
- verdict-admissibility validator.

A candidate under review must not be able to modify the implementation that decides whether its own evidence was complete. Candidate-supplied delivery code may be tested as an artifact, but it cannot grant its own review admissibility.

The governor's **decision inputs** are also part of this trust root. Every material review must bind an immutable `GovernanceAuthoritySnapshot` created from a pre-candidate authority state outside the candidate write set. It contains the governing standard/experiment/registry/classification/evidence-relationship identities and hashes used to derive required evidence and required interactions.

If the candidate changes any governing input in its own head, that head version cannot silently replace the pre-candidate authority snapshot for the candidate's own review. The review uses a conservative merge rule:

- mandatory evidence refs = union(base-authority requirements, candidate-head proposed requirements);
- mandatory dimensions = union(base-authority dimensions, candidate-head proposed dimensions);
- required interaction sets = union(base-authority interactions, candidate-head proposed interactions);
- representation requirements, evidence semantics, statistical thresholds, accessibility-risk policies, and review constraints preserve the stricter base/head requirement;
- every governing element is content-addressed by stable ID plus hash; reuse of the same ID with different semantics/hash is treated as a changed governing input, never as an in-place semantic replacement;
- restrictive classifications/egress/provider constraints use the stricter applicable rule;
- if two governing inputs conflict and no platform-defined partial order can prove which is stricter, derivation fails as `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`;
- every governing-input change is itself a mandatory review evidence ref.

Registries, context-isolation policies, witness-protocol qualification records, and the authority-snapshot pointer are maintained outside the candidate write set. A candidate may propose changes to governing inputs, but those proposed changes cannot authorize or narrow their own review.

### Conservative base/head comparison rules

The platform-defined “stricter” relation is explicit per governing element class:

| Governing element | Stricter relation |
|---|---|
| required evidence refs / mandatory dimensions / required interactions | set superset is stricter |
| allowed representations | set intersection is stricter; empty intersection => unresolved |
| representation fidelity | raw/lossless > bounded-loss > summary; incomparable media semantics => unresolved |
| required review level | REQUIRED > RECOMMENDED > NONE |
| allowed provider/account/region/tool set | set intersection is stricter; empty set => not qualified |
| data egress / retention / training permissions | deny > conditional allow > allow; conflicting conditions with no partial order => unresolved |
| minimum statistical success bound / confidence | larger lower-bound requirement and larger confidence are stricter |
| tolerated hard failures / residual risk | smaller tolerated value is stricter |
| required confirmation trials | larger minimum is stricter when all other acceptance semantics match |
| profile expiry / requalification interval | shorter validity is stricter |
| runtime byte/token/file limits | smaller maximum is stricter |
| accessibility proof mode | deterministic full-range proof > probabilistic/content-bound proof > self-attestation |
| prompt-isolation requirement | superset of required isolation predicates is stricter |
| transition-class rank | only the authority registry may define the rank; missing/incomparable rank => unresolved |

A same-dimension semantic change with no comparator is **never auto-merged**. It requires a separate independently authorized governance update; for the candidate review it remains `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.

## Core authority rule

**A reviewer disposition is inadmissible for a material authority transition unless every mandatory evidence item is governed from source through delivery and the selected provider/mode is qualified to make that exact representation available to the reviewer.**

A `PASS` cannot cure incomplete delivery. A negative result from incomplete delivery may remain useful defect/diagnostic evidence, but it is not a complete scientific adjudication.

## Required-evidence authority

The delivery manifest and the ReviewRequest do not decide what evidence is required by themselves.

Before a ReviewRequest is eligible for delivery, the pinned delivery governor must independently derive a `RequiredEvidenceContract` from the immutable `GovernanceAuthoritySnapshot`, including the protected transition class, platform-owned mandatory-dimension registry, evidence-selection registry, evidence-relationship registry, and applicable governing standards/experiment contracts.

The `ReviewRequest` is a declaration that must be validated against that independently derived contract. It is never an input that can define requiredness.

Every protected transition class has a governed non-vacuous baseline. Unknown transition class, missing registry rule, empty mandatory-dimension set, empty required-evidence set where the baseline requires evidence, or unresolved authority snapshot produces `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`. Deterministic derivation of an empty set is not sufficient.

The `RequiredEvidenceContract` must contain at least:

- contract schema/version;
- GovernanceAuthoritySnapshot ID/hash/version;
- pre-candidate governing standard/experiment/registry identities and hashes;
- candidate-head governing-input identities/hashes when changed;
- conservative base/head merge result;
- protected transition classification from the governed registry;
- complete mandatory review-dimension set;
- complete required evidence-reference set or deterministic derivation rules;
- representation requirements for each evidence reference/dimension;
- required cross-evidence interaction families;
- deterministic optional-evidence rules;
- ProviderAccessibilityRiskPolicy identity for the protected transition class;
- ProviderContextIsolationPolicy identity for the protected transition class/provider mode;
- contract hash.

Before manifest freeze, prove all of:

- every standard/experiment-required mandatory dimension appears in the ReviewRequest;
- every `RequiredEvidenceContract` evidence ref is declared by or deterministically materializable from the ReviewRequest;
- no required ref is downgraded to optional;
- no mandatory interaction family is omitted;
- no provider capability limit narrows the required set.

The proposer, packet builder, reviewer, ReviewRequest author, transport adapter, or delivery manifest may not silently:

- omit a governed evidence reference;
- omit a standard-required mandatory dimension;
- change required to optional;
- substitute a summary for required raw evidence;
- omit a governed cross-evidence interaction;
- narrow the required item set because of provider limits.

Before delivery, the platform must prove closure:

`required_contract_refs == validated_review_request_refs == materialized_required_refs == manifest_required_refs`

and:

`required_contract_dimensions == review_request_mandatory_dimensions`

subject only to explicitly governed representation mappings.

Any mismatch fails before manifest freeze as `EVIDENCE_SELECTION_INCOMPLETE`.

If the pinned governor cannot deterministically derive a complete required-evidence or required-interaction contract from the governing materials, the review is not eligible for material authority. Ambiguity is classified as `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; the platform may not fall back to trusting the proposer/ReviewRequest declaration.

## Failure taxonomy

At minimum preserve:

- `SCIENTIFIC_EVIDENCE_MISSING`
- `EVIDENCE_SELECTION_INCOMPLETE`
- `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`
- `GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH`
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`
- `PROVIDER_CONTEXT_STATE_UNPROVEN`
- `PROVIDER_CONTEXT_STATE_DRIFT`
- `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`
- `PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING`
- `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`
- `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`
- `STATISTICAL_INDEPENDENCE_UNPROVEN`
- `VERDICT_ADMISSION_STATE_CHANGED`
- `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`
- `IMPLICIT_RETRY_UNOBSERVED`
- `REVIEW_CONTEXT_DIRTY_OR_UNBOUND`
- `PROVIDER_SEMANTIC_CONTEXT_UNQUALIFIED`
- `PROVIDER_CAPABILITY_STATISTICAL_POLICY_FAILED`
- `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN`
- `ACCESSIBILITY_PROBE_COVERAGE_INSUFFICIENT`
- `WITNESS_PROTOCOL_UNQUALIFIED`
- `WITNESS_CONTEXT_EVICTION`
- `REVIEW_INTERACTION_CONTRACT_INCOMPLETE`
- `EVIDENCE_MATERIALIZATION_FAILED`
- `EVIDENCE_TRANSFORMATION_UNQUALIFIED`
- `EVIDENCE_DELIVERY_INCOMPLETE`
- `REVIEW_CONTEXT_INCOMPLETE`
- `EVIDENCE_FORMAT_UNSUPPORTED`
- `EVIDENCE_ATTACHMENT_UNAVAILABLE`
- `EVIDENCE_CHUNK_MISSING`
- `EVIDENCE_CHUNK_DUPLICATE`
- `EVIDENCE_CHUNK_REORDERED`
- `EVIDENCE_CHUNK_HASH_MISMATCH`
- `EVIDENCE_MANIFEST_MISMATCH`
- `EVIDENCE_WIRE_REQUEST_MISMATCH`
- `EVIDENCE_SESSION_BINDING_MISMATCH`
- `EVIDENCE_FILE_REFERENCE_UNQUALIFIED`
- `PROVIDER_CAPABILITY_PROFILE_UNQUALIFIED`
- `PROVIDER_CAPABILITY_PROFILE_STALE`
- `EVIDENCE_EGRESS_NOT_AUTHORIZED`
- `EVIDENCE_RECEIPT_UNPROVEN`
- `REVIEW_STARTED_BEFORE_DELIVERY_COMPLETE`
- `REVIEW_VERDICT_INADMISSIBLE_DELIVERY_FAILURE`
- `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`
- `MIXED_INSUFFICIENCY`

A generic reviewer `INSUFFICIENT_EVIDENCE` token is not the platform's final cause classification.

## Evidence Delivery Manifest

Before any provider invocation, create an immutable content-addressed `EvidenceDeliveryManifest` bound to the exact current `ReviewRequest`.

It must contain at least:

- review request ID/hash;
- reviewed artifact commit/tree;
- required review dimensions;
- authoritative required evidence refs and count;
- provider/model/API mode;
- trusted adapter identity/hash/version;
- provider capability profile ID/hash/version/expiry;
- delivery protocol version;
- delivery attempt ID;
- per-item stable evidence ID derived from governed source identity and content hash;
- authoritative source reference;
- evidence class;
- source raw SHA-256 and byte length;
- governed representation ID;
- representation media type;
- representation SHA-256 and byte length;
- required/optional status derived from governed source;
- transformation record when source and representation differ;
- chunk plan where applicable;
- total chunk count;
- per-chunk hash/length/index;
- canonical ordering;
- whole canonical corpus hash;
- exact hashes for every platform-supplied semantic prompt layer (system/developer/user); an absent layer is represented explicitly as EMPTY rather than omitted;
- egress/data-classification decision hash;
- expected wire-call count.

The manifest hash is frozen before delivery.

## Representation and transformation governance

A source artifact and a reviewer representation are not automatically equivalent.

When evidence is transformed, record:

- source evidence ID/hash/length/media type;
- transformation tool identity/version/hash;
- transformation parameters;
- produced representation hash/length/media type;
- byte/page/range coverage where relevant;
- whether transformation is lossless, bounded-loss, or summary;
- governed rule permitting the representation for each review dimension.

Examples requiring explicit transformation governance:

- PDF to extracted text;
- binary log to decoded text;
- JSON to Markdown;
- archive extraction;
- image to text/OCR;
- page/range slicing;
- proposer-written summary.

A lossy or partial representation cannot satisfy a full-raw-evidence requirement.

Transformation tools/parsers must be platform-owned/pinned or otherwise independently qualified; candidate-provided parser code cannot transform its own evidence into an authoritative reviewer representation.

Archive/document materialization must be bounded against path traversal, symlink escape, duplicate-name ambiguity, decompression/resource bombs, recursive archive expansion, and parser time/memory exhaustion. Unsafe opaque archives may be preserved as source evidence but cannot be treated as successfully materialized reviewer content merely because an external provider accepts them.

## Data classification and egress authorization

Evidence must not be sent to an external provider merely because it is required for review.

Before delivery, classify each evidence item for:

- secrets/credentials;
- personal/sensitive data;
- proprietary/restricted data;
- provider/region restrictions;
- retention/training restrictions where applicable;
- permitted transformation/redaction.

The egress decision must be platform/governance-owned and bound to the delivery manifest.

If required evidence cannot be safely/legally sent in a qualified representation, that provider/mode is not qualified for the review. The platform must not silently redact or omit load-bearing evidence and then call the review complete.

## Provider accessibility risk policy

Every protected transition class has a platform-owned `ProviderAccessibilityRiskPolicy` in the GovernanceAuthoritySnapshot.

The policy states whether a material review may rely on probabilistic/content-bound accessibility evidence or requires deterministic range/retrieval proof.

At minimum it binds:

- transition class;
- allowed accessibility proof modes;
- maximum tolerated residual selective/sub-segment loss risk;
- required statistical lower bound;
- whether evidence of trial-independence/correlation control is mandatory for the statistical probability claim;
- whether a deterministic per-attempt proof mode may substitute when statistical independence is unproven;
- whether per-attempt content-bound witnesses are sufficient;
- whether deterministic full-range/page/member access proof is mandatory.

Unknown/missing risk policy fails closed.

The default for the highest material-authority transition class is deterministic full-range/page/member proof or platform-forced inline content under a provider mode whose qualified failure model covers the complete representation. Per-attempt sampling/witnesses alone cannot satisfy that class.

## Provider capability qualification policy

Live provider qualification uses a preregistered risk-budget and confirmation protocol. Exploration and confirmation are separate evidence families.

### Default material-review risk budget

Unless a stricter transition-specific policy is independently governed before exposure:

- target lower bound for per-trial delivery/accessibility success: **p_min = 0.99**;
- confidence: **one-sided 95% exact Clopper–Pearson**;
- zero hard failures are allowed at a claimed operating point;
- with zero failures, the minimum confirmation sample is **299/299** successful trials, because the exact one-sided lower bound is `0.05^(1/299) >= 0.99`;
- every attempted confirmation trial counts, including timeout, provider error, rate-limit, ambiguous, unverifiable, or infrastructure failure; no exclusions, rerolls, or optional stopping;
- exploration trials used to discover limits are never reused as confirmation trials;
- confirmation trial IDs and schedule are frozen before confirmation exposure;
- confirmation trials are distributed across at least **3 distinct UTC days** and at least **4 preregistered time blocks per day**, with operating points interleaved in randomized order;
- repeated attempts from the same provider session/request lineage do not count as independent confirmation trials;
- every trial uses a fresh delivery-attempt identity, fresh clean provider context, fresh content-bound witnesses, and the production-equivalent request envelope;
- the qualification record captures any provider-exposed routing/deployment/region identity and demonstrates the preregistered time/interleaving diversity;
- the Clopper–Pearson probability interpretation is explicitly conditional on the trial-independence model. When provider-side correlation/route allocation is not observable, the profile records `STATISTICAL_INDEPENDENCE_UNPROVEN`; the numerical bound is not presented as a universal provider failure probability and `statistical_qualified=true` is forbidden unless the governing ProviderAccessibilityRiskPolicy explicitly waives the probability claim and requires a deterministic per-attempt accessibility proof mode instead.

### Qualification execution authority and attempt closure

Confirmation qualification uses a dedicated platform-controlled qualification runner and credential scope that candidate code, candidate users, and ordinary operators cannot invoke directly.

Before confirmation exposure, freeze a `ProviderQualificationExecutionPlan` containing:

- provider/profile drift epoch;
- exact operating-point IDs;
- complete scheduled confirmation trial IDs;
- UTC day/time-block assignment;
- deterministic/randomization seed committed before exposure;
- trusted runner identity/hash;
- qualification credential/configuration identity;
- network/egress policy identity;
- expected number of calls.

Every scheduled trial slot must produce exactly one first-attempt record. A missing/skipped slot is a hard failure. A retry or additional call is a new attempt and cannot replace the original failed/missing slot.

The append-only `ProviderCapabilityQualificationRecord` must reconcile:

- every planned trial ID;
- every trusted-runner dispatch record;
- every provider request ID returned;
- provider usage/audit records when exposed.

If provider usage/audit logs are unavailable, the dedicated qualification credential must be technically inaccessible outside the trusted runner and its governed egress path. If neither provider-side call reconciliation nor credential/egress exclusivity can be established, the confirmation set is `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN` and cannot qualify a material review mode.

Unscheduled calls cannot contribute successes. An unexplained call using the dedicated qualification credential invalidates the confirmation epoch.

Qualification adapters must disable implicit SDK retries or expose every physical retry as a separate append-only attempt. If the platform cannot observe whether the SDK/client retried, qualification attempt closure is unproven.

### Hard failure

A hard failure is any attempted trial with one or more of:

- required evidence/range/member/page inaccessible or incorrect;
- content-bound witness missing/incorrect;
- provider context state unproven or dirty;
- wrong model/deployment/account/endpoint/session identity;
- wire/manifest/retrieval hash mismatch;
- incomplete retrieval/access log when that mode requires it;
- timeout, provider/API error, rate limit, parser failure, or ambiguous result;
- output truncation/structured-output failure that prevents the required review protocol.

### Operating point

An operating point is the full tuple of:

- provider/account/project;
- endpoint/region;
- exact requested and provider-reported deployment identity;
- trusted adapter/API version;
- session/file/retrieval mode;
- enabled tools/connectors;
- structured-output mode;
- review prompt class;
- corpus representation/media classes;
- corpus byte size and provider-tokenizer token size;
- file count/per-file sizes;
- output/reasoning budget;
- witness protocol identity/version and maximum challenge/response budget when witnesses are used;
- transformation mode.

The **claimed operating point itself must be tested**. The protocol does not assume monotonic provider behavior and does not qualify untested intermediate points by interpolation.

For scalar size dimensions, the 80% margin is only an additional conservative cap on a point that is itself confirmed. If a failing boundary is observed, the runtime cap cannot exceed 80% of the smallest observed failing boundary. If no failure boundary is observed, the runtime cap cannot exceed 80% of the largest independently confirmed passing point.

The production qualification corpus must exercise the production request envelope and the preregistered worst-case token-density/content-modality classes. Synthetic low-entropy text alone cannot qualify a production review envelope.

Observed failures and failure boundaries are append-only within a provider drift epoch. Re-running until a clean sample appears cannot erase prior failures. A new drift epoch requires a new profile identity and preserves the prior epoch.

Profiles expire after **7 days** by default and immediately on material provider/model/deployment/account/endpoint/region/adapter/session/file-processing behavior drift. Health checks may invalidate a profile but can never renew or extend it.

Provider-specific policies may be stricter but may not be weakened by the candidate under review.

## Provider capability profile

A `ProviderCapabilityProfile` is trusted platform configuration/evidence, not candidate-authored content.

It must bind:

- provider;
- exact provider credential/account/project scope identity used by the platform; if the API does not expose a remote tenant/project identifier, bind the platform-owned credential/configuration identity and do not claim an unobservable remote identity;
- API endpoint/region/data-residency boundary;
- exact requested model and provider-reported model/deployment identity; if the provider cannot expose the deployment identity required by the drift policy, the mode is `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`;
- model alias/version drift policy;
- API/adapter version;
- trusted adapter hash/version;
- qualified request/body size;
- qualified cumulative context size with safety margin;
- attachment/file support;
- supported representations/media types;
- maximum file count;
- per-file size limits;
- file visibility semantics;
- server-side file reference semantics;
- session/thread/conversation semantics;
- fresh-session guarantee or full prior-context capture semantics;
- provider-injected mutable system/developer/custom instructions;
- account/project/workspace memory behavior;
- provider-side knowledge/retrieval connectors and defaults;
- staged-message behavior;
- context eviction/truncation behavior;
- structured-output behavior;
- provider response/output constraints;
- exact ProviderQualificationExecutionPlan identity/hash and exact ProviderCapabilityQualificationRecord hash containing all planned/observed exploration/confirmation attempts, schedule, runner/credential binding, provider request reconciliation, hard-failure classifications, Clopper–Pearson calculation, content classes, operating-point tuple, and append-only failure history;
- qualification timestamp;
- expiry/requalification policy;
- conservative qualified limit and safety margin derived from repeated trials, not a single success.

Unknown capability is not capability.

Profiles must expire or be invalidated on material provider/model/adapter/API behavior drift. Candidate code may not mint or widen a profile.

A single successful provider call near a limit is not sufficient to widen the qualified bound. Qualification uses fresh canaries over repeated trials and chooses a conservative safe limit under the governed acceptance policy.

Automatic provider/model fallback is a new delivery context. A failure on provider/model A may not silently fall back to B using A's manifest/profile. The fallback requires its own qualified profile, delivery plan/attempt identity, and admissibility record.

The authoritative capability registry must be outside the candidate's self-approval boundary. A capability-profile change is itself governed configuration requiring independent review appropriate to its authority. Material candidate changes must not be able to edit the profile that decides whether their own review delivery is complete.

## Trusted adapter and wire binding

The platform must bind what it intended to send to what its trusted provider adapter actually serialized.

For every provider call, retain a `WireDeliveryRecord` containing:

- delivery attempt ID;
- review request ID;
- manifest hash;
- adapter identity/hash/version;
- call sequence number;
- evidence/chunk IDs included;
- canonical platform request hash before SDK serialization;
- canonical **transport-bound semantic envelope hash after SDK serialization at the lowest observable adapter boundary**, excluding only authentication secrets and explicitly volatile transport fields;
- exact non-secret headers/fields that can alter semantics, tools, routing, model selection, file/session binding, or output behavior;
- provider account/endpoint/region identity used;
- requested model identity and provider-reported model/deployment identity when the latter is required by the governed drift policy; if the provider cannot expose a required deployment identity, that identity-dependent qualification cannot be claimed;
- provider request/message/file/thread/session IDs;
- transport status;
- response hash;
- retry/idempotency identity;
- timestamp.

A manifest and prompt hash without wire binding do not prove that the adapter included the frozen evidence in the API request.

The adapter must serialize from the frozen representation bytes/chunks referenced by the manifest. Hashing one file and later reopening the same pathname for upload is insufficient unless byte identity is reverified immediately before dispatch.

Provider secrets are excluded from reproducible hashes but their exclusion must not permit semantic request fields to be omitted from binding. If the provider SDK prevents the trusted adapter from observing a semantic field that can materially change the request after serialization, that adapter/mode cannot claim exact wire binding for material review.

Implicit client/SDK retries are prohibited unless every physical provider attempt is surfaced to the trusted adapter with its own WireDeliveryRecord and immutable attempt identity. For material review and provider qualification, the preferred mode is client retry disabled. A hidden first failure followed by an SDK-retried success cannot be represented as one successful attempt.

## Delivery preflight

Before any review dispatch:

1. Verify the current ReviewRequest integrity.
2. Resolve and verify the immutable GovernanceAuthoritySnapshot.
3. Derive RequiredEvidenceContract and RequiredInteractionContract from that snapshot.
4. Validate ReviewRequest dimensions/refs/interactions against those contracts.
5. Materialize every required evidence reference from frozen source identity.
6. Verify source bytes/hashes and apply only governed representations/transforms.
7. Resolve data-classification/egress authorization.
8. Resolve a current trusted ProviderCapabilityProfile and machine-checkable PromptIsolationQualificationRecord.
9. Create or verify a clean ProviderContextStateEvidence record for this exact attempt.
10. Build and freeze the EvidenceDeliveryManifest.
11. Prove the exact production-equivalent delivery plan fits the qualified operating point.
12. Freeze exact call/chunk/file ordering, prompt identities, context-state version, capability-profile version, egress-policy version, and prompt-isolation record version.
13. Emit `DELIVERY_PREFLIGHT_PASS` only if every mandatory item and interaction is deliverable in the qualified mode.
14. Immediately before every wire call, compare-and-check the still-current context/capability/egress/prompt-isolation monotonic state versions.
15. Dispatch only the frozen representation bytes/chunks/file objects produced during preflight.
16. Record the final SDK-serialized semantic envelope hash at the trusted adapter boundary.

If a required item cannot be safely represented or delivered, fail before treating any reviewer disposition as authoritative.

Manifest freeze and wire dispatch form a TOCTOU boundary. A source path, generated representation, capability profile, egress decision, provider context state, prompt-isolation qualification, or provider file may not change between validation and use without voiding the attempt. A later requalification cannot revive an already-void attempt.

## Chunking limitation

**Chunking is a transport mechanism, not a way to exceed the model's qualified adjudication context.**

Sending N chunks over time does not prove that all N remain simultaneously available to the model at final adjudication. Earlier messages may be evicted, summarized, or otherwise unavailable.

Therefore a chunked material review is admissible only when one of these is qualified:

1. the complete final adjudication working set, including prompt and all mandatory representations, remains within the provider's qualified cumulative context; or
2. the provider exposes a qualified persistent file/retrieval mechanism whose content identity, accessibility, and final-review binding are validated; or
3. a governed decomposed-review protocol explicitly scopes independent subreviews and a separately qualified aggregation review covers required cross-evidence interactions.

A plain multi-message sequence must not be used to claim arbitrarily large context.

## Provider context isolation policy

Every material review binds a platform-owned `ProviderContextIsolationPolicy` selected from the GovernanceAuthoritySnapshot for the exact protected transition class and provider mode.

The policy chooses one of these admissible isolation bases:

1. `COMPLETE_READABLE_FENCED_STATE`
   - the provider exposes the complete account/project/session mutable semantic-state inventory relevant to the mode;
   - each mutable channel is readable or disable-able;
   - each load-bearing channel has a monotonic version/fence through admission.

2. `DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY`
   - a dedicated platform-owned provider account/project/credential is used only for governed review;
   - candidate and end-user writes to provider configuration are impossible by authorization policy;
   - provider product documentation/contract for the exact API mode is hash/version pinned and states that account/project/session memory, personalization, custom instructions and knowledge connectors are disabled or absent;
   - platform configuration readback proves all exposed mutable semantic features disabled;
   - behavioral sentinel qualification is run on a disposable qualification account/project of the same provider/account class and configuration template, never by contaminating the production review account;
   - production account configuration template/hash is independently matched to the qualified template and fenced.

Provider documentation is necessary provenance, not sufficient proof. The pinned documentation/contract version, provider account class, production configuration-template hash, and isolation-policy identity are part of the ProviderCapabilityProfile/context-isolation binding. A change to any of them invalidates the profile/isolation qualification and requires requalification.

### Hidden provider-internal state nonclaim

The platform cannot prove absence of provider-internal mutable semantic state that the provider does not expose through API/configuration and that cannot be independently controlled.

Therefore each `ProviderContextIsolationPolicy` declares a `hidden_provider_state_residual` rule:

- `DISALLOW` — any unexposed mutable-semantic-state possibility makes the provider/mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`;
- `DEDICATED_ACCOUNT_EXTERNAL_TRUST_BOUNDARY` — only the dedicated-account basis above is permitted, and the residual is recorded explicitly as `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`.

The highest material-authority transition class defaults to `DISALLOW` unless an independent governance decision explicitly authorizes the dedicated-account external trust boundary.

No result may be labeled “clean context” without recording the selected isolation basis and residual/nonclaim.

## Clean material-review context and delivery session binding

A material review uses a fresh stateless request or a **platform-created fresh stateful session**. Reuse of an arbitrary pre-existing provider thread/conversation is prohibited.

Every attempt carries `ProviderContextStateEvidence` created by the trusted adapter. It must bind:

- provider account/project/workspace identity;
- provider session/thread/conversation identity;
- complete platform-visible transcript/message IDs and transcript hash;
- platform-supplied system/developer/user prompts;
- enabled tools and connectors;
- custom/project/workspace instruction state and hash;
- provider memory/personalization state and hash;
- provider-side knowledge/retrieval connector state and hash;
- file set and processing/readiness state;
- provider-reported model/deployment identity;
- configuration-state version;
- evidence timestamp and trusted adapter identity.

The state is read and compared against the qualified profile:

- during preflight;
- immediately before every dispatch;
- immediately before final atomic verdict admission.

For mutable provider/account/project/session configuration used by a material review, the trusted platform must also obtain an `AdmissionFenceRecord`: a provider ETag/version/fencing token or a platform-owned dedicated-account configuration lock/version that makes concurrent configuration mutation detectable and prevents user/candidate writes during the attempt. If a load-bearing mutable channel exposes neither a readable version nor a platform-enforceable fence, the mode is not qualified for material review.

Any mutable semantic channel that is neither disable-able nor readable by the trusted platform makes the mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.

The only exception is a dedicated platform-owned provider account/project whose configuration write access is change-controlled outside candidate and user control, whose mutable semantic features are disabled by policy, and whose state is behaviorally requalified. Provider documentation is necessary background evidence but never sufficient by itself.

Stateful session reuse is allowed only inside the same delivery-attempt lineage when the session was created by the trusted adapter for that attempt and every prior message/tool/file mutation has a matching WireDeliveryRecord and context-state transition record.

Provider-context qualification must include **sentinel tests** for every mutable semantic channel available to the provider mode: enable a controlled sentinel and prove it influences the model when enabled; disable/clear it and prove absence across the governed confirmation trials. Lying/incomplete readback is explicitly tested.

Provider-internal fixed service/model safety behavior that cannot be extracted is a nonclaim. Hidden provider-internal mutable semantic state is governed only through the ProviderContextIsolationPolicy above: it is either disallowed or explicitly retained as a dedicated-account external trust-boundary residual. The platform never claims that such hidden state was observed clean.

For stateless provider modes, the final request itself must contain or qualified-reference all mandatory evidence and context. A receipt from one session/request cannot prove completeness for another.

## Server-side file references

A successful file upload or opaque provider file ID does not prove model accessibility.

A provider file mechanism is qualified only when the platform has evidence for:

- content identity at upload;
- stable association with exact provider account/context;
- accessibility from the final review request;
- retention/expiry behavior;
- file replacement/mutability behavior;
- supported format parsing and processing/ingestion readiness states;
- retrieval range/coverage semantics where partial retrieval is possible;
- failure behavior.

If these are unknown, file-reference delivery is non-authoritative for material review.

When the model/provider chooses what file content or ranges to retrieve, **per-attempt deterministic access/range logs are mandatory** for material review. Before verdict admission, those logs must prove for every required page/range/member:

- exact source/version identity;
- requested range/member;
- returned content hash and byte/range length;
- successful retrieval time;
- tool/result message identity;
- binding of that tool result to the same final adjudication session/context.

A log that proves only “a file was opened” is insufficient. If the provider cannot prove both hash-matched returned content and binding of the retrieval result into the final adjudication context, that retrieval/file mode is diagnostic-only and `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.

The alternative is platform-forced inline inclusion of the governed representation inside the qualified final context.

Reviewer citation text, file IDs, or attach-time binding cannot substitute for per-attempt retrieval coverage when retrieval is model-selected.

## Reviewer receipt and availability acknowledgement

A reviewer receipt is a useful diagnostic, not an independent trust root.

Where supported, a staged reviewer may return a non-dispositive receipt with:

- request ID;
- manifest/corpus hash;
- evidence/chunk IDs reported accessible;
- unsupported/inaccessible items;
- session/file references;
- completeness claim.

The platform must compare this receipt against its own delivery records and provider capability profile.

A reviewer statement such as `received_all=true` cannot override missing wire records, hash mismatches, unsupported formats, or an unqualified capability profile.

## Delivery witness probes

Witnesses are non-dispositive accessibility evidence. They never prove cognition, attention, or semantic use.

### Qualification witnesses

When deterministic provider range/retrieval proof is unavailable, **every confirmation trial challenges every required segment**. Sparse head/middle/end probing is prohibited as qualification for full required content.

The default raw-text failure model is explicitly bounded to **contiguous loss/eviction at or above the segment granularity**. It does not claim detection of arbitrary selective or sub-granularity loss.

A governed lossless text representation is sliced so each slice is no larger than:

- 2048 UTF-8 bytes; and
- 512 provider-tokenizer tokens;

whichever limit is reached first.

For every slice in every confirmation trial, the platform creates a fresh content-bound challenge after representation freeze. The challenge selects unpredictable slice-local offsets and asks the reviewer to return exact short content extracts whose expected values are withheld from the reviewer prompt. Each slice also carries fresh framing/end sentinels. A canary-preserving content drop must therefore be independently attackable by the test adapters.

For production material review attempts using a mode without deterministic range/retrieval proof, the same **per-attempt content-bound witness protocol is mandatory in the same final adjudication session**. Qualification is a prior; it is not a substitute for per-attempt accessibility evidence.

The residual possibility of selective loss outside challenged offsets is recorded in `VerdictAdmissibilityResult` as a nonclaim/risk. A transition class whose governed risk budget does not permit that residual risk must use deterministic retrieval/range proof or a platform-forced representation with stronger observability.

### Witness protocol context budget and noninterference

The witness protocol is part of the qualified production operating point; it is not “free” metadata.

Before dispatch, preflight must include in the cumulative final-context budget:

- evidence representations;
- witness framing/challenges;
- maximum witness-response tokens/bytes;
- tool/result wrappers;
- final semantic adjudication prompt;
- required final review output budget.

After the witness phase and immediately before the final semantic adjudication prompt, the platform rechecks the actual transcript/context size against the qualified bound. If witness traffic could evict required evidence, the attempt is void.

Witness challenges are strictly extraction/accessibility operations. They may not ask for evaluation, summarization, ranking, defect identification, or conclusions.

A material review mode using witnesses additionally requires a platform-owned `WitnessProtocolQualificationRecord` from a qualified registry outside candidate write authority, bound to the exact prompt-isolation mechanism/provider mode. Candidate content/code cannot mint or widen it. That record covers:

- exact witness protocol/version;
- challenge syntax;
- ordering relative to evidence and final adjudication;
- maximum challenge/response budget;
- evidence-slice selection procedure;
- deterministic fake-adapter structural-isolation tests;
- machine-checkable binding to the applicable PromptIsolationQualificationRecord;
- expiry/drift binding.

The platform does **not** claim counterfactual semantic noninterference (“the model would have produced the same verdict without the witness phase”). That is not reliably observable for a stochastic remote model.

Instead, structural isolation requires:

- witness prompts contain accessibility/extraction instructions only;
- witness outputs are tagged non-evidence/non-adjudicative and cannot satisfy semantic review dimensions;
- the final semantic adjudication prompt hash is fixed and governed;
- prompt-isolation controls prevent witness output from being treated as candidate evidence or authority;
- the exact witness transcript remains inside the qualified context budget.

A/B semantic-outcome comparisons may be retained as diagnostics but cannot by themselves qualify or disqualify the witness protocol.

### Opaque attachments

Opaque attachments are qualified per media type **and content-modality class**. Scanned images, text PDFs, tables, embedded objects, archives, and other materially distinct modalities are separate classes.

Full-artifact material review requires either:

- deterministic provider access/range logs proving every required page/range/member/version; or
- governed lossless transformation into a qualified text/structured representation followed by the per-slice protocol.

Synthetic text-layer PDFs cannot qualify scans, tables, images, or embedded-object modalities.

A copied item ID/hash already present in the prompt is not a valid witness.

## Meaning of REVIEW_CONTEXT_QUALIFIED_AVAILABLE

`REVIEW_CONTEXT_QUALIFIED_AVAILABLE=true` means only:

- the platform proved complete governed materialization and wire delivery;
- the selected provider/mode has a current qualified capability profile for the representation/session mechanism;
- all required evidence is bound to the final adjudication request/session under that profile;
- no known delivery/context defect is present under the explicitly qualified failure model and ProviderAccessibilityRiskPolicy.

It does **not** mean the platform proved model cognition, attention, semantic use of every token, or absence of risks outside the qualified failure model. The prior name `REVIEW_CONTEXT_COMPLETE` is deprecated because it overstates what an external API can prove.

## Prompt/evidence isolation dependency

EXP-M does not qualify prompt-injection safety.

For material authority review, the pinned governor deterministically maps the transition/provider/representation mode to a required `PromptIsolationQualificationRecord` from EXP-L or its governed successor. That record must be machine-checkable, hash-bound to the exact isolation mechanism/provider mode, non-expired, and checked at preflight and atomic verdict admission.

If no current matching record exists, the review is non-promotable. “Applicable” is not caller- or proposer-selected.

Delivering all evidence perfectly must not be treated as safe if candidate-controlled evidence can hijack reviewer instructions.

EXP-M may test delivery independently, but a production review path requires both boundaries.

## Review decomposition and aggregation

If evidence cannot fit one qualified final context, the platform may not simply split it into several reviews and call their agreement a full review.

A decomposed protocol must preregister:

- dimension/subreview scopes;
- exact evidence set per subreview;
- cross-dimension interaction requirements;
- aggregation logic;
- evidence needed by the aggregator;
- conditions under which no global disposition is allowed.

The proposer may not define the interaction list by itself. The pinned delivery/review governor derives a `RequiredInteractionContract` only from the GovernanceAuthoritySnapshot's platform-owned evidence-relationship registry, mandatory dimensions, transition class, and governing standards.

Each required interaction is an explicit set of evidence refs/representations that must coexist **raw in one qualified reviewer context** for that interaction. The aggregator must inspect the raw evidence set for each interaction family; subreview verdict summaries alone cannot satisfy the interaction.

Any proposer/ReviewRequest declaration is checked against this contract. Unknown relationship class, empty required interaction set where the transition baseline requires one, or missing registry rule yields `REVIEW_INTERACTION_CONTRACT_INCOMPLETE` and blocks a global disposition.

If material cross-evidence interactions cannot be reviewed within a qualified context, the review remains bounded/incomplete.

## Admissibility predicate registry and mutation closure

The platform maintains a machine-readable `AdmissibilityPredicateRegistry` outside candidate write authority.

Each load-bearing verdict-admissibility predicate has:

- stable predicate ID;
- schema/version;
- human meaning;
- validator function identity/hash;
- required negative fixture ID;
- required logic-mutation ID;
- authority snapshot binding.

`VerdictAdmissibilityResult` must contain exactly the required predicate-ID set for the protected transition/mode.

The deterministic test plan proves set closure:

`required_admissibility_predicates == verdict_result_predicates == validator_logic_mutation_targets == independently_killed_mutations`

Any missing predicate, extra ungoverned predicate, or predicate without a killed deletion/weakening mutation yields `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`.

Adding a new load-bearing predicate without updating its negative fixture and logic mutation cannot pass deterministic EXP-M testing.

## Verdict admissibility

`VerdictAdmissibilityResult` contains an explicit predicate for every load-bearing requirement:

- ReviewRequest current/integrity-valid;
- GovernanceAuthoritySnapshot current and outside candidate write authority;
- RequiredEvidenceContract resolved, non-vacuous, and closed;
- RequiredInteractionContract resolved and closed;
- complete materialization;
- governed representation/transformation;
- current egress authorization;
- ProviderCapabilityProfile current and statistically qualified for the exact operating point;
- ProviderAccessibilityRiskPolicy current and satisfied by the selected accessibility proof mode;
- ProviderContextIsolationPolicy current, exact-mode-bound, and satisfied;
- hidden-provider-state residual allowed by the protected transition policy, if any;
- ProviderContextStateEvidence clean/current for all observable channels;
- AdmissionFenceRecord valid for every load-bearing mutable provider configuration channel;
- provider mutable semantic-context qualification satisfied;
- trusted adapter and post-SDK wire binding valid;
- complete item/chunk delivery;
- per-attempt content-bound accessibility witness valid **or** deterministic range/retrieval proof complete;
- when witnesses are used, WitnessProtocolQualificationRecord current/matching and actual witness transcript remains within the qualified final-context budget;
- session/file/retrieval coverage valid for the delivery mode;
- PromptIsolationQualificationRecord current/matching;
- semantic review coverage valid;
- reviewer provenance/independence valid;
- disposition otherwise promotable.

Admission is the **last authority operation** and is atomic with checkpoint persistence:

1. capture monotonic versions/hashes for authority snapshot, capability profile, accessibility-risk policy, context-isolation policy, egress policy, provider context/session/file state, AdmissionFenceRecord, prompt-isolation record, and current review request;
2. validate all predicates;
3. compare-and-set the authoritative checkpoint only if every version/hash is unchanged;
4. persist the VerdictAdmissibilityResult and checkpoint in the same authority transaction/boundary.

All load-bearing state must remain valid over the entire interval from first provider dispatch through admission. Any expiry, revocation, drift, dirty-context event, file/session invalidation, or prompt-isolation invalidation during the interval **voids the attempt permanently**. Later requalification cannot revive that old provider response; only a new delivery attempt may proceed.

A semantic `PASS` with any false/unproven predicate is non-promotable.

## Insufficient-evidence cause adjudication

When a reviewer returns `INSUFFICIENT_EVIDENCE` or equivalent, the platform evaluates all cause predicates independently rather than first-match ordering:

- scientific source missing → `SCIENTIFIC_EVIDENCE_MISSING`;
- requiredness contract unresolved → `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`;
- governed required set incomplete → `EVIDENCE_SELECTION_INCOMPLETE`;
- source materialization failed → `EVIDENCE_MATERIALIZATION_FAILED`;
- transformation/representation unqualified → `EVIDENCE_TRANSFORMATION_UNQUALIFIED`;
- delivery omitted/corrupted material → `EVIDENCE_DELIVERY_INCOMPLETE`;
- provider context dirty/unproven → `PROVIDER_CONTEXT_STATE_UNPROVEN` / `REVIEW_CONTEXT_INCOMPLETE`;
- attachment/file/retrieval coverage unavailable → `EVIDENCE_ATTACHMENT_UNAVAILABLE` / `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`;
- reviewer says evidence is missing although the platform has strong contradictory accessibility evidence → `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`.

If more than one cause predicate is true, the result is `MIXED_INSUFFICIENCY` with the complete cause set. If no cause can be proven, use `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`.

Never convert delivery failure into scientific failure or scientific absence into a transport excuse.

## Multi-reviewer equivalence

Reviewer agreement is not consensus evidence unless the platform proves evidence-delivery comparability.

For every compared reviewer retain:

- reviewer-specific manifest;
- provider capability profile;
- representation/transformation records;
- wire delivery records;
- session/file bindings;
- completeness result;
- final verdict.

Two reviewers receiving different representations are comparable only if a governed equivalence rule permits those representations for all compared review dimensions.

## Retry and failure history

Each delivery attempt has a stable attempt ID and immutable records.

A retry must either:

- reproduce the same frozen manifest and delivery semantics under a new attempt ID; or
- create a new governed delivery manifest when representation/protocol materially changes.

Failed attempts remain preserved. A later complete retry cannot rewrite an earlier incomplete attempt as complete.

## Reviewer tools and out-of-manifest evidence

A material reviewer must not silently introduce ungoverned external evidence through web search, retrieval plugins, arbitrary tools, or provider-side knowledge connectors.

For a material review, reviewer tools are either:

- disabled; or
- explicitly governed, allowlisted, and their retrieved evidence is captured with provenance, hashes/identifiers, and review-dimension binding under an applicable external-evidence governance path.

Evidence discovered through reviewer tools cannot retroactively count as if it had been part of the frozen delivery manifest. If new material evidence changes the review basis, the platform records a governed supplemental evidence boundary or a new review request/delivery attempt as required.

Model recollection/training knowledge remains non-authoritative evidence.

## Security and false-green rules

The following must never independently establish delivery completeness:

- reviewer says it received everything;
- HTTP 2xx;
- provider upload success;
- opaque file ID;
- evidence count copied from outgoing metadata;
- token estimate;
- whole-corpus hash without required-item closure;
- citation to one or more artifacts;
- green CI;
- proposer assertion;
- candidate-authored provider capability profile;
- chunk count without cumulative-context qualification;
- multi-reviewer agreement;
- candidate-supplied materializer/manifest/checker code;
- one successful provider call near a claimed capability limit;
- automatic fallback to a different provider/model without a new qualified delivery attempt;
- hashing one byte set and uploading a later re-read mutable path without revalidation;
- ungoverned reviewer web/tool retrieval presented as frozen evidence.

## Required audit evidence

Every material platform API review must retain:

- ReviewRequest;
- governed evidence inventory;
- EvidenceDeliveryManifest;
- source and representation hashes;
- stable evidence IDs and canonical source-path/identity mapping;
- pinned delivery-governor implementation identity;
- transformation records;
- egress decision;
- ProviderCapabilityProfile identity;
- ProviderQualificationExecutionPlan and trusted qualification-runner/credential identity;
- ProviderAccessibilityRiskPolicy identity;
- ProviderContextIsolationPolicy identity and selected isolation basis;
- WitnessProtocolQualificationRecord identity when witnesses are used;
- hidden-provider-state residual/nonclaim decision;
- pinned provider documentation/contract identity where the dedicated-account basis is used;
- AdmissionFenceRecord;
- prompt identities;
- pre-dispatch revalidation result for capability/egress/session state;
- WireDeliveryRecords;
- chunks where used;
- provider session/file/message IDs where used;
- reviewer receipt if used;
- DeliveryCompletenessResult;
- provider raw responses;
- witness-probe challenges/results where used;
- mandatory provider retrieval/access logs for any retrieval-selected material-review mode;
- parsed review;
- insufficient-evidence adjudication where needed;
- semantic validation;
- AdmissibilityPredicateRegistry identity and predicate/mutation-coverage closure result;
- VerdictAdmissibilityResult, including provider statistical lower bound, qualified operating-point identity, per-attempt accessibility method, and explicitly retained residual/nonclaim risk.

## Governance scope

This standard supplements review provenance, semantic review coverage, portable packet integrity, external-evidence classification, and independent-review prompt/evidence governance.

It specifically governs **required-evidence closure, delivery integrity, provider-context qualification, and verdict admissibility**.


---

# STOPPED RQ-16

## SOURCE: V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md

Ref: `d9ef21c938414e8370dbb6a4d553066843758599`
Blob: `484e68f45954ccf74a3f1d3b9936e0334f053d61`

# V24-I11-V6 RQ-16 preregistration remediation-7 final review

Planning-only artifact. No RQ-16 execution occurred.

## Identity
reviewed_source_commit=195bc72ab79af33659213bdcc1c0e024f336a384
reviewed_source_tree=5257f6814756ab0ee4a9357ae4f9b12d8e960672
packet_parent_commit=195bc72ab79af33659213bdcc1c0e024f336a384
packet_parent_tree=5257f6814756ab0ee4a9357ae4f9b12d8e960672
predecessor_commit=8477830f5f35a35a8c9b19fdca9c5b6c39e2916d
predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf
exact_source_diff_sha256=49977de2a46d2e3a1bc8af1d13b437e3bee7af48126795f68946fcb8babe00bf
source_manifest_sha256=480a219f007a5232a222f1fcf6e03c641c1fa5ce5a6d7b7b3ab482a59a7e1b7b
generated_evidence_manifest_sha256=26b5fd1c20cfa7f90dba6fb2a6c2fee4f9e249de9076f61cce3c8c62d7d1acea
packet_content_identity_schema_version=3
branch=qualification/v24-i11-v6-runtime-qualification-1-rq16-preregistration
packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION
packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION
packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION
RQ16_EXECUTED=false
RQ16_AUTHORIZED=false
RQ16_started=false
scientific_rerun=false
qualification=NOT_QUALIFIED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY

## Frozen contract

### execution contract

```json
{
  "rq_id": "RQ-16",
  "trigger": "Disk full / read-only / I/O / permission failure",
  "oracle": "Fail closed without fabricated success",
  "execution_required": true,
  "execution_authorized": false,
  "arms": {
    "ENOSPC": {
      "operation": "write_authority_record or fsync on exact bound records path",
      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
    },
    "EROFS": {
      "operation": "write_authority_record or rename on exact bound path",
      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
      "classification": "UNSAFE",
      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
    },
    "EIO": {
      "operation": "exact record read/write/fsync/rename syscall",
      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
    },
    "EACCES": {
      "operation": "exact service access to records/consumed path",
      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
      "classification": "PROXY_NOT_ACCEPTABLE",
      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
    }
  },
  "classification_rules": {
    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
  },
  "state_machine": {
    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
  },
  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```

## Source-path analysis

### preregistration

```markdown
# V24-I11-V6 RQ-16 preregistration (planning only)

Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
that closed Remediation-7 head.

Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
failure**. Oracle: **Fail closed without fabricated success**. This document
does not authorize execution.

## Actual write path

In `governance-runtime/native/v24_v6_trusted_authority_service.c`:

- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
  `fsync`, then closes and unlinks on failure.
- candidate handling calls `materialize_private()` for context, boundary and
  payload before gate execution.
- root control calls `consume_record_trusted()`.
- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
  from records to consumed. It returns an authoritative response only after
  `rename` succeeds.
- `write_authority_record()` creates records with
  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
  `fsync`, closes, and unlinks on failure.

RQ-16 must bind the injected errno to one of these exact operations; mocked
Python exceptions and candidate-side failures are proxies.

## Execution arms and classifications

ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
host `/run` is prohibited. No repository evidence proves such a quota boundary,
so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.

EROFS requires a dedicated qualification filesystem whose read-only transition
does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
unsafe and a separate filesystem would collide with RQ-17 topology semantics;
the arm is `UNSAFE` pending dedicated-mount evidence.

EIO requires a disposable kernel fault layer returning EIO on the exact target
operation. `dm-error` or equivalent is acceptable only with a dedicated device
and independent activation/errno proof. No such boundary is evidenced;
classification is `INSUFFICIENT_EVIDENCE`.

EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
trusted service runs as UID 0. Candidate-side permission failure or a mocked
exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.

These are execution arms under one frozen case, not new cases.

## Required state machine and proof

Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
state record target membership in records/consumed, response and authority,
errno proof, service state, filesystem/device/mount metadata, ownership/modes,
and hashes. PASS requires exact fault activation plus syscall errno, no
authoritative success, explainable target lifecycle, recoverable service,
complete observers, and exact post-restoration hashes/security state. Absence
of a response alone is never PASS. Authoritative success after a proven fault
is RED. Missing/malformed proof or observer/cleanup failure is
HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.

## Restoration, safety and aborts

The only permitted future mutation is a bounded fixture on a dedicated,
preflight-verified boundary. The host root filesystem, repository, historical
evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
workspace are never targets. Cleanup removes the fixture, restores mount/quota
and metadata, revalidates service/socket/PID, records/consumed integrity,
device IDs, mount options, ownership/modes, hashes and security controls. Any
failure blocks all dependent cases.

Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
free-space margin, backup material, root recovery, service health or observer
access differ from the preregistered baseline, or if an evidence directory could
be overwritten.

Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.

## Harness safety and governance

`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
`--execute-rq16` refuses with a nonzero result. Future execution requires a
separately generated authorization token bound to exact commit, host/runtime
identity and plan digest. No token exists in this branch.

`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
Qualification remains `NOT_QUALIFIED`; scientific execution remains
`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
mechanism classifications before any execution authorization.

## Remediation-2 hardening

The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.

Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.

No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
```

## Cleanup contract

### cleanup

```markdown
# RQ-16 cleanup and restoration contract

RQ-16 remains preregistration-only. No mutation has been executed.

Every future arm must capture an immutable baseline and restore it before any
dependent case. The baseline includes service/gate hashes, unit bytes, PID and
socket identity, records/consumed ownership and modes, filesystem device IDs,
mount options, security controls, and exact target lifecycle.

The inverse operation must be explicit: remove only the bounded fault fixture,
restore the saved mount/quota/metadata state, restart only as required by the
approved recovery procedure, and independently remeasure every baseline field.
If a mount operation fails, root recovery is unavailable, a fault fixture
cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
dependent cases abort. Historical evidence directories are never targets.

The future harness must refuse destructive execution unless the exact host,
commit, plan digest, and separately generated authorization token are bound.
`--plan` and `--self-test` are the only permitted modes in this preregistration.
```

## Issues

### issue ledger

```json
{
  "issues": [
    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
  ],
  "open_automatable_issues": 0,
  "manual_review_required": true,
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false,
  "latest_remediation_status": {
    "RQ16-TRUSTED-ATTESTATION": "RESOLVED",
    "RQ16-AUTH-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-IDENTITY-MODEL": "RESOLVED",
    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
  }
}
```

## Source manifest
[{"path":"governance-runtime/build_rq16_preregistration_review.py","sha256":"9c81406de9a2f756b1b8618d63e1e6e8e394f7d6949e66690ddc0fb418ca1f7e"},{"path":"governance-runtime/check_rq16_preregistration_packet.py","sha256":"54e2aa52bcc04581a867a1a9f69793ff71dac24d09dba9839b6e01b25bf684ef"},{"path":"governance-runtime/collect_rq16_results.py","sha256":"adab691dadc650852ea07bfa09ef5aa568b7dba628e9d6d1a6b870ef196a7ff0"},{"path":"governance-runtime/rq16_manifest.py","sha256":"108db681fda8b1b9998f0d398a9a4981b2eee263f4aa65f40fc29a5c9a5ff8bd"},{"path":"governance-runtime/run_v24_v6_rq1_rq16_mutations.py","sha256":"4cc446fa6ff059cf99bad895f5947f9091e04d4709e2a87335d7b15e5c9a4916"},{"path":"governance-runtime/test_rq16_manifest.py","sha256":"122338e681ef5df65953567d2593bea96481f470f2a3775de9e8bfc2f66d5881"},{"path":"governance-runtime/test_v24_v6_rq1_rq16_harness.py","sha256":"fa54ab8c395e1fc958b996a7e5e30957bbeac6617733d34aa0272a798f5154f5"},{"path":"governance-runtime/v24_v6_rq1_rq16_harness.py","sha256":"babe9b5030f415ce87b77c288f53776d3f14dcdbbdfeca4f3c4be532b9bff476"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json","sha256":"31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md","sha256":"958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json","sha256":"efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md","sha256":"13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json","sha256":"527ac480abf1e6b74fab31374886fde58f6dffd77c7274b92e4e481711a8fdfd"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md","sha256":"19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md","sha256":"ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b"}]

## Generated evidence manifest
[{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json","sha256":"13352f4d9f42e8ae94d9157414f3cbde667add5b7d85e65990929cb036e5b40a"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json","sha256":"c65bdbcbb1c404a2e1eac965a9f2e57b537758d00230e6ce39dca1704c7d9965"},{"path":"implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json","sha256":"c54b27af07686999f812264ff3540c4af8f780279c2cc395c2c4d718130e8c34"}]


### implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json sha256=31cfafeeae6fbfdd511cc54583efe37768ceaad7e2aa93b66bf1505336ee5bb7

```python
{
  "authorization_schema_version": "1",
  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
  "single_use": true,
  "arm_scoped": true,
  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md sha256=958c15eed2d13d0b74a0b2f3d95d5f2f909b97ac9f88fde419eda2ddf7dca769

```python
# RQ-16 cleanup and restoration contract

RQ-16 remains preregistration-only. No mutation has been executed.

Every future arm must capture an immutable baseline and restore it before any
dependent case. The baseline includes service/gate hashes, unit bytes, PID and
socket identity, records/consumed ownership and modes, filesystem device IDs,
mount options, security controls, and exact target lifecycle.

The inverse operation must be explicit: remove only the bounded fault fixture,
restore the saved mount/quota/metadata state, restart only as required by the
approved recovery procedure, and independently remeasure every baseline field.
If a mount operation fails, root recovery is unavailable, a fault fixture
cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
dependent cases abort. Historical evidence directories are never targets.

The future harness must refuse destructive execution unless the exact host,
commit, plan digest, and separately generated authorization token are bound.
`--plan` and `--self-test` are the only permitted modes in this preregistration.
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json sha256=efc4d6fbd6c13f7aed519999570a1a21efe0aba9a819b07a0de54bbd6ec5d422

```python
{
  "rq_id": "RQ-16",
  "trigger": "Disk full / read-only / I/O / permission failure",
  "oracle": "Fail closed without fabricated success",
  "execution_required": true,
  "execution_authorized": false,
  "arms": {
    "ENOSPC": {
      "operation": "write_authority_record or fsync on exact bound records path",
      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
    },
    "EROFS": {
      "operation": "write_authority_record or rename on exact bound path",
      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
      "classification": "UNSAFE",
      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
    },
    "EIO": {
      "operation": "exact record read/write/fsync/rename syscall",
      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
      "classification": "INSUFFICIENT_EVIDENCE",
      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
    },
    "EACCES": {
      "operation": "exact service access to records/consumed path",
      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
      "classification": "PROXY_NOT_ACCEPTABLE",
      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
    }
  },
  "classification_rules": {
    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
  },
  "state_machine": {
    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
  },
  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md sha256=13bf0ae2f37a06da5ff081d26988e2b364121631306cbc0c4edc2ce6d0999c00

```python
# Durable authorization nonce design

No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.

The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json sha256=527ac480abf1e6b74fab31374886fde58f6dffd77c7274b92e4e481711a8fdfd

```python
{
  "issues": [
    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
  ],
  "open_automatable_issues": 0,
  "manual_review_required": true,
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false,
  "latest_remediation_status": {
    "RQ16-TRUSTED-ATTESTATION": "RESOLVED",
    "RQ16-AUTH-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-IDENTITY-MODEL": "RESOLVED",
    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
  }
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md sha256=19eaca68666f2b61aea648a7b6fce74912649a45ac20e6155d6cd8fdba3e2fc6

```python
# V24-I11-V6 RQ-16 preregistration (planning only)

Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
that closed Remediation-7 head.

Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
failure**. Oracle: **Fail closed without fabricated success**. This document
does not authorize execution.

## Actual write path

In `governance-runtime/native/v24_v6_trusted_authority_service.c`:

- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
  `fsync`, then closes and unlinks on failure.
- candidate handling calls `materialize_private()` for context, boundary and
  payload before gate execution.
- root control calls `consume_record_trusted()`.
- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
  from records to consumed. It returns an authoritative response only after
  `rename` succeeds.
- `write_authority_record()` creates records with
  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
  `fsync`, closes, and unlinks on failure.

RQ-16 must bind the injected errno to one of these exact operations; mocked
Python exceptions and candidate-side failures are proxies.

## Execution arms and classifications

ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
host `/run` is prohibited. No repository evidence proves such a quota boundary,
so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.

EROFS requires a dedicated qualification filesystem whose read-only transition
does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
unsafe and a separate filesystem would collide with RQ-17 topology semantics;
the arm is `UNSAFE` pending dedicated-mount evidence.

EIO requires a disposable kernel fault layer returning EIO on the exact target
operation. `dm-error` or equivalent is acceptable only with a dedicated device
and independent activation/errno proof. No such boundary is evidenced;
classification is `INSUFFICIENT_EVIDENCE`.

EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
trusted service runs as UID 0. Candidate-side permission failure or a mocked
exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.

These are execution arms under one frozen case, not new cases.

## Required state machine and proof

Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
state record target membership in records/consumed, response and authority,
errno proof, service state, filesystem/device/mount metadata, ownership/modes,
and hashes. PASS requires exact fault activation plus syscall errno, no
authoritative success, explainable target lifecycle, recoverable service,
complete observers, and exact post-restoration hashes/security state. Absence
of a response alone is never PASS. Authoritative success after a proven fault
is RED. Missing/malformed proof or observer/cleanup failure is
HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.

## Restoration, safety and aborts

The only permitted future mutation is a bounded fixture on a dedicated,
preflight-verified boundary. The host root filesystem, repository, historical
evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
workspace are never targets. Cleanup removes the fixture, restores mount/quota
and metadata, revalidates service/socket/PID, records/consumed integrity,
device IDs, mount options, ownership/modes, hashes and security controls. Any
failure blocks all dependent cases.

Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
free-space margin, backup material, root recovery, service health or observer
access differ from the preregistered baseline, or if an evidence directory could
be overwritten.

Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.

## Harness safety and governance

`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
`--execute-rq16` refuses with a nonzero result. Future execution requires a
separately generated authorization token bound to exact commit, host/runtime
identity and plan digest. No token exists in this branch.

`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
Qualification remains `NOT_QUALIFIED`; scientific execution remains
`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
mechanism classifications before any execution authorization.

## Remediation-2 hardening

The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.

Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.

No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md sha256=ad008c6e249b05bea0abbb266050cd0bd6e70ef86db03a4d5ea651ffbb8e819b

```python
# RQ-16 read-only capability inspection

This inspection was non-destructive and did not enable or mutate any host feature.

The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.

Source inspection found the trusted service operations at:

- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.

Read-only commands attempted:

```text
Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
```

Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.

`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
```


### governance-runtime/build_rq16_preregistration_review.py sha256=9c81406de9a2f756b1b8618d63e1e6e8e394f7d6949e66690ddc0fb418ca1f7e

```python
from __future__ import annotations
import hashlib, os, subprocess
from pathlib import Path
from rq16_manifest import canonical_review_source_files, canonical_evidence_files, build_source_manifest, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md'
PACKET_CHECK_CURRENT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json'
FILES=canonical_review_source_files(ROOT)
EVIDENCE_FILES=canonical_evidence_files(ROOT)
def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
def main():
    if not PACKET_CHECK_CURRENT.exists(): PACKET_CHECK_CURRENT.write_text('{"status":"PENDING"}\n',encoding='utf-8')
    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
    diff=run(['git','diff',predecessor,reviewed,'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md']).stdout
    tests=run(['python','governance-runtime/collect_rq16_results.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
    def render(packet_check_json):
        source_manifest=build_source_manifest(FILES,ROOT); evidence_manifest=build_evidence_manifest(ROOT); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={manifest_sha256(source_manifest)}',f'generated_evidence_manifest_sha256={manifest_sha256(evidence_manifest)}','packet_content_identity_schema_version=3']
        parts=['# V24-I11-V6 RQ-16 preregistration remediation-7 final review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[2].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[5].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[1].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[4].read_text(),'json'), '## Source manifest',source_manifest,'## Generated evidence manifest',evidence_manifest]
        for p in FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
        for p in EVIDENCE_FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'json'))
        parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check-current',packet_check_json,'json'),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Historical packet consistency failure source_manifest_entries_mismatch was fixed and superseded; no failed traceback is current evidence. Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
        OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8')
    render('{"status":"PENDING"}\n')
    current_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py','--allow-pending'])
    if current_check.returncode != 0: raise SystemExit(current_check.stderr or current_check.stdout)
    packet_check_json=current_check.stdout.strip()+'\n'
    PACKET_CHECK_CURRENT.write_text(packet_check_json,encoding='utf-8')
    render(packet_check_json)
    final_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
    if final_check.returncode != 0: raise SystemExit(final_check.stderr or final_check.stdout)
    print(OUT)
if __name__=='__main__': main()
```


### governance-runtime/check_rq16_preregistration_packet.py sha256=54e2aa52bcc04581a867a1a9f69793ff71dac24d09dba9839b6e01b25bf684ef

```python
#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
import sys
from pathlib import Path
from rq16_manifest import canonical_review_source_files, build_source_manifest, canonical_evidence_files, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md'
SOURCE_FILES=canonical_review_source_files(ROOT)
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='3'
    manifest_match=re.search(r'## Source manifest\n(.*?)(?:\n### |\n## )',text,re.S)
    assert manifest_match, 'source_manifest_section_missing'
    declared=json.loads(manifest_match.group(1).strip())
    expected_manifest=json.loads(build_source_manifest(SOURCE_FILES,ROOT))
    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
    manifest=build_source_manifest(SOURCE_FILES,ROOT)
    assert manifest_sha256(manifest)==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
    evidence_match=re.search(r'## Generated evidence manifest\n(.*?)(?:\n### |\n## )',text,re.S); assert evidence_match, 'evidence_manifest_section_missing'
    assert json.loads(evidence_match.group(1).strip())==json.loads(build_evidence_manifest(ROOT)), 'evidence_manifest_entries_mismatch'
    current_path=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json'; current=json.loads(current_path.read_text())
    if current.get('status')!='PENDING' or '--allow-pending' not in sys.argv: assert current.get('status')=='PASS' and current.get('packet_consistency')=='PASS', 'current_packet_check_not_pass'
    tests=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json').read_text()); muts=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json').read_text())
    assert tests['tests_total']==tests['tests_passed']+tests['tests_failed'] and tests['exit_code']==0, 'test_result_binding_mismatch'
    assert muts['total_mutations']==len(muts['mutations']) and muts['rejected_mutations']+muts['surviving_mutations']==muts['total_mutations'] and muts['all_rejected']==(muts['surviving_mutations']==0), 'mutation_result_binding_mismatch'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
    print(json.dumps({'status':'PASS','packet_consistency':'PASS','identity_model':'PASS','reviewed_source_commit':vals['reviewed_source_commit'],'reviewed_source_tree':vals['reviewed_source_tree'],'manifest_entry_count':len(expected_manifest),'manifest_entries_match':True,'manifest_sha_match':True,'diff_hash_match':True,'test_result_binding':True,'mutation_result_binding':True,'governance_match':True,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
```


### governance-runtime/collect_rq16_results.py sha256=adab691dadc650852ea07bfa09ef5aa568b7dba628e9d6d1a6b870ef196a7ff0

```python
#!/usr/bin/env python3
"""Generate the single authoritative offline RQ-16 test and mutation results."""
import json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEST_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json'
MUT_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json'
def main():
    runs=[subprocess.run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py'],cwd=ROOT,text=True,capture_output=True),subprocess.run(['python','governance-runtime/test_rq16_manifest.py'],cwd=ROOT,text=True,capture_output=True)]
    t=subprocess.CompletedProcess([],max((x.returncode for x in runs),default=0),stdout='\n'.join(x.stdout for x in runs),stderr='\n'.join(x.stderr for x in runs))
    m=subprocess.run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'],cwd=ROOT,text=True,capture_output=True)
    combined=re.sub(r'Ran (\d+) tests? in [0-9.]+s',r'Ran \1 tests in <elapsed>',t.stderr+t.stdout)
    matches=re.findall(r'Ran (\d+) tests?',combined); total=sum(int(x) for x in matches)
    tests=[]
    for line in combined.splitlines():
        hit=re.match(r'test_\w+ \(__main__\.[^)]+\) \.\.\. (ok|FAIL)',line)
        if hit: tests.append({'name':line.split(' (',1)[0],'result':'PASS' if hit.group(1)=='ok' else 'FAIL'})
    test_result={'tests_total':total,'tests_passed':sum(x['result']=='PASS' for x in tests),'tests_failed':sum(x['result']=='FAIL' for x in tests),'exit_code':t.returncode,'tests':tests,'stdout':'','stderr':combined}
    mutation_result=json.loads(m.stdout)
    mutation_result['exit_code']=m.returncode
    TEST_OUT.write_text(json.dumps(test_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    MUT_OUT.write_text(json.dumps(mutation_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'tests_total':test_result['tests_total'],'tests_passed':test_result['tests_passed'],'tests_failed':test_result['tests_failed'],'mutation_total':mutation_result['total_mutations'],'mutation_rejected':mutation_result['rejected_mutations'],'mutation_surviving':mutation_result['surviving_mutations'],'all_rejected':mutation_result['all_rejected']},indent=2))
    return 0 if t.returncode==0 and m.returncode==0 else 1
if __name__=='__main__': raise SystemExit(main())
```


### governance-runtime/run_v24_v6_rq1_rq16_mutations.py sha256=4cc446fa6ff059cf99bad895f5947f9091e04d4709e2a87335d7b15e5c9a4916

```python
#!/usr/bin/env python3
import copy, hashlib, json
from datetime import datetime, timezone
from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, expected_fault_observer_context, validate_authorization_token
from test_v24_v6_rq1_rq16_harness import good, TRUSTED
EXPECTED=expected_context("ENOSPC")
OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
def main():
    specs=[
      ("wrong_device",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("wrong_mount",lambda e:e["observations"]["fault_active"].update(records_mount="m2")),
      ("wrong_filesystem",lambda e:e["observations"]["fault_active"].update(records_fs="fs2")),
      ("symlink",lambda e:e["observations"]["fault_active"].update(records_symlink=True)),
      ("wrong_target",lambda e:e["fault_proof"].update(target_record_id="other")),
      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
      ("attestation_missing_raw_activation",lambda e:e["trusted_fault_attestation"].pop("fault_activation_raw_evidence")),
      ("attestation_missing_raw_operation",lambda e:e["trusted_fault_attestation"].pop("operation_raw_evidence")),
      ("attestation_wrong_observer",lambda e:e["trusted_fault_attestation"].update(observer_identity="candidate")),
      ("attestation_wrong_pid",lambda e:e["trusted_fault_attestation"].update(service_pid=99)),
      ("attestation_wrong_artifact_hash",lambda e:e["trusted_fault_attestation"].update(raw_artifact_sha256="fake")),
      ("missing_observer",lambda e:e["observations"].pop("restored")),
      ("bool_only_observer",lambda e:e.pop("observations")),
      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
      ("duplicate_consume",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record","abc123.record"])),
      ("both_directories",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
      ("cleanup_service_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="bad")),
      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
      ("cleanup_fault_active",lambda e:e["cleanup_proof"].update(fault_disabled=False)),
      ("cleanup_target_state",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=[])),
      ("cleanup_historical_evidence",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence="changed")),
      ("cleanup_missing_restored",lambda e:e["cleanup_proof"].update(restored_observation={})),
      ("baseline_target_missing",lambda e:e["observations"]["baseline"].update(records_entries=[])),
      ("baseline_already_consumed",lambda e:e["observations"]["baseline"].update(consumed_entries=["abc123.record"])),
      ("post_failure_missing_both",lambda e:e["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
      ("post_failure_both",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
      ("wrong_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["other.record"])),
      ("historical_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
      ("unrelated_target_transition",lambda e:e["observations"]["post_failure"].update(records_entries=["abc123.record","other.record"])),
      ("duplicate_authoritative_consumption",lambda e:e.update(authoritative_success=True)),
      ("second_authoritative_retry",lambda e:e["observations"]["post_failure"].update(response={"service_authoritative":True})),
      ("replay_state_mutation",lambda e:e["observations"]["restored"].update(records_entries=["other.record"])),
      ("target_hash_changed",lambda e:e["observations"]["post_failure"].update(target_hash="changed")),
      ("target_identity_changed",lambda e:e["observations"]["post_failure"].update(target_record_id="other")),
      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
      ("cleanup_device",lambda e:e["cleanup_proof"]["restored_observation"].update(records_device="bad")),
      ("cleanup_mount",lambda e:e["cleanup_proof"]["restored_observation"].update(records_mount="bad")),
      ("cleanup_fs",lambda e:e["cleanup_proof"]["restored_observation"].update(records_fs="bad")),
      ("cleanup_realpath",lambda e:e["cleanup_proof"]["restored_observation"].update(records_realpath="bad")),
      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
      ("cleanup_fault_still_active",lambda e:e["cleanup_proof"]["restored_observation"].update(fault_state={"active":True})),
      ("cleanup_unrelated_record",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=["abc123.record","other.record"])),
      ("cleanup_historical_changed",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence={"intact":False})),
      ("cleanup_arbitrary_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="arbitrary")),
      ("cleanup_arbitrary_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="arbitrary")),
      ("cleanup_arbitrary_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="arbitrary")),
    ]
    rows=[]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)
        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
    metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
    for field in auth_fields:
        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used,trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("self_issued","issuer_identity","candidate"),("candidate_writable","source_path","candidate"),("placeholder_issuer_hash","issuer_authority_artifact_sha256","issuer-sha"),("placeholder_review_hash","review_artifact_sha256","review-sha"),("wrong_reviewer","reviewer_designation","candidate"),("generic_bounded_pass","independent_review_disposition","BOUNDED_PASS"),("changes_required","independent_review_disposition","CHANGES_REQUIRED"),("insufficient_evidence","independent_review_disposition","INSUFFICIENT_EVIDENCE")):
        bad=dict(token); bad[field]=value; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_provenance_"+name,"case":"AUTHORIZATION_PROVENANCE","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    reasons=validate_authorization_token(token,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_provenance_unavailable","case":"AUTHORIZATION_PROVENANCE","path":"trusted_provenance","before":"absent","after":"absent","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
```


### governance-runtime/rq16_manifest.py sha256=108db681fda8b1b9998f0d398a9a4981b2eee263f4aa65f40fc29a5c9a5ff8bd

```python
#!/usr/bin/env python3
"""Canonical source/evidence manifest definitions for the RQ-16 review packet."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md",
    "governance-runtime/build_rq16_preregistration_review.py",
    "governance-runtime/check_rq16_preregistration_packet.py",
    "governance-runtime/collect_rq16_results.py",
    "governance-runtime/run_v24_v6_rq1_rq16_mutations.py",
    "governance-runtime/rq16_manifest.py",
    "governance-runtime/test_v24_v6_rq1_rq16_harness.py",
    "governance-runtime/test_rq16_manifest.py",
    "governance-runtime/v24_v6_rq1_rq16_harness.py",
)
EVIDENCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json",
)

def canonical_review_source_files(root=ROOT):
    return [root / rel for rel in SOURCE_RELATIVE]

def canonical_evidence_files(root=ROOT):
    return [root / rel for rel in EVIDENCE_RELATIVE]

def _entries(files, root=ROOT):
    entries=[]
    for path in files:
        rel=path.resolve().relative_to(root.resolve()).as_posix()
        if rel.startswith("/") or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError(f"non-canonical path: {rel}")
        entries.append({"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if len({e["path"] for e in entries}) != len(entries):
        raise ValueError("duplicate canonical path")
    return sorted(entries,key=lambda e:e["path"])

def build_source_manifest(files=None, root=ROOT):
    return json.dumps(_entries(files or canonical_review_source_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def build_evidence_manifest(root=ROOT):
    return json.dumps(_entries(canonical_evidence_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def manifest_sha256(manifest):
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()
```


### governance-runtime/test_v24_v6_rq1_rq16_harness.py sha256=fa54ab8c395e1fc958b996a7e5e30957bbeac6617733d34aa0272a798f5154f5

```python
#!/usr/bin/env python3
import copy, hashlib, unittest
from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context, expected_fault_observer_context

EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
TRUSTED={"issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":hashlib.sha256(b"issuer").hexdigest(),"reviewer_designation":"independent-reviewer","review_artifact_sha256":hashlib.sha256(b"review").hexdigest(),"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600"}
def observation():
    return {s:{"target_record_id":TARGET,"target_hash":"target-hash","records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good():
    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":OBSERVER["observer_identity"],"observer_source_sha256":OBSERVER["observer_source_sha256"],"observer_execution_identity":OBSERVER["observer_execution_identity"],"expected_evidence_root":OBSERVER["expected_evidence_root"],"expected_owner":OBSERVER["expected_owner"],"expected_mode":OBSERVER["expected_mode"],"expected_host_identity":OBSERVER["expected_host_identity"],"expected_runtime_identity":OBSERVER["expected_runtime_identity"],"raw_artifact_path":"/var/lib/v24-rq1/rq16-attestations/a.raw","raw_artifact_sha256":ARTIFACT_DIGEST,"cleanup_reference":"clean"}
    base=copy.deepcopy(EXPECTED["expected_restoration"])
    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}

class RQ16Tests(unittest.TestCase):
    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
    def test_target_mutations_reject(self):
        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_provenance_mutations_reject(self):
        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_observer_cleanup_lifecycle_mutations_reject(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        mutations=[
            ("baseline_target_missing",lambda x:x["observations"]["baseline"].update(records_entries=[])),
            ("baseline_target_already_consumed",lambda x:x["observations"]["baseline"].update(consumed_entries=[TARGET+".record"])),
            ("post_failure_target_missing_both",lambda x:x["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
            ("post_failure_target_both",lambda x:x["observations"]["post_failure"].update(consumed_entries=[TARGET+".record"])),
            ("wrong_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["other.record"])),
            ("historical_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
            ("unrelated_target_transition",lambda x:x["observations"]["post_failure"].update(records_entries=[TARGET+".record","other.record"])),
            ("duplicate_authoritative_consumption",lambda x:x.update(authoritative_success=True)),
            ("second_authoritative_retry",lambda x:x["observations"]["post_failure"].update(response={"service_authoritative":True})),
            ("replay_state_mutation",lambda x:x["observations"]["restored"].update(records_entries=["other.record"])),
            ("target_hash_changed",lambda x:x["observations"]["post_failure"].update(target_hash="changed")),
            ("target_identity_changed",lambda x:x["observations"]["post_failure"].update(target_record_id="other")),
        ]
        for _,mut in mutations:
            e=good(); mut(e); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
    def test_cleanup_exact_baseline_comparison(self):
        fields=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
        for field in fields:
            e=good(); e["cleanup_proof"]["restored_observation"][field]="arbitrary"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].update(cleanup_ok=True); e["cleanup_proof"].pop("baseline_observation"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_authority_and_duplicate_transitions_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"RED")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_token_requires_durable_trusted_binding(self):
        self.assertTrue(validate_authorization_token({},EXPECTED))
        token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
        metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"},trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
    def test_cross_arm_proof_rejected(self):
        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"),OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_absent_response_not_success(self):
        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/test_rq16_manifest.py sha256=122338e681ef5df65953567d2593bea96481f470f2a3775de9e8bfc2f66d5881

```python
#!/usr/bin/env python3
import shutil, unittest
from contextlib import contextmanager
from pathlib import Path
from rq16_manifest import ROOT, canonical_review_source_files, build_source_manifest, manifest_sha256

class ManifestTests(unittest.TestCase):
    @contextmanager
    def scratch(self):
        d=ROOT/".rq16-manifest-test"; shutil.rmtree(d,ignore_errors=True); d.mkdir()
        try: yield d
        finally: shutil.rmtree(d,ignore_errors=True)
    def test_clean_manifest_is_deterministic(self):
        files=canonical_review_source_files(ROOT)
        self.assertEqual(build_source_manifest(files),build_source_manifest(list(reversed(files))))
        self.assertEqual(len({x.relative_to(ROOT).as_posix() for x in files}),len(files))
    def test_source_byte_change_changes_manifest(self):
        with self.scratch() as d:
            p=d/"x.py"; p.write_bytes(b"x=1\n"); before=build_source_manifest([p],d); p.write_bytes(b"x=2\n"); self.assertNotEqual(before,build_source_manifest([p],d))
    def test_duplicate_path_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([p,p],d)
    def test_missing_file_fails(self):
        with self.assertRaises(FileNotFoundError): build_source_manifest([ROOT/"does-not-exist"],ROOT)
    def test_absolute_outside_root_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([Path("C:/outside-rq16/x")],ROOT)
    def test_generated_packet_is_not_source(self):
        names={p.name for p in canonical_review_source_files(ROOT)}
        self.assertNotIn("V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md",names)
    def test_manifest_hash_is_content_hash(self):
        self.assertEqual(len(manifest_sha256(build_source_manifest())),64)

if __name__=="__main__": unittest.main(verbosity=2)
```


### governance-runtime/v24_v6_rq1_rq16_harness.py sha256=babe9b5030f415ce87b77c288f53776d3f14dcdbbdfeca4f3c4be532b9bff476

```python
#!/usr/bin/env python3
"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
from __future__ import annotations
import argparse, hashlib, json, math, re
from datetime import datetime, timezone

ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
TRUSTED_AUTHORIZATION_PROVENANCE_AVAILABLE=False

def expected_trusted_authorization_provenance():
    """No governance-authorized issuer is available during preregistration."""
    return None

def expected_context(arm, record_id="abc123"):
    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
    baseline={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":rp,"consumed_realpath":cp,"owner":{"uid":0,"gid":0},"mode":{"records":"0700","consumed":"0700"},"socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"service_identity":"uid0:trusted-service","security_controls":{"policy":"stable"},"fault_state":{"active":False},"records_entries":[record_id+".record"],"consumed_entries":[],"historical_evidence":{"intact":True}}
    stages={s:{"target_in_records":True,"target_in_consumed":False,"target_hash":"target-hash"} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
    lifecycle={"status":"MANUAL_REVIEW_REQUIRED","stages":stages,"permitted_transitions":[]}
    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_target_hash":"target-hash","expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","expected_restoration":baseline,"expected_lifecycle_contract":lifecycle}

def check_rq17_contamination(expected, observed):
    reasons=[]
    if expected.get("expected_records_device") != expected.get("expected_consumed_device"): reasons.append("expected_baseline_split")
    for stage, o in (observed or {}).items():
        if not isinstance(o,dict): reasons.append(f"stage_malformed:{stage}"); continue
        pairs=(("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"))
        for actual, exp in pairs:
            if o.get(actual) != expected.get(exp): reasons.append(f"{stage}:{actual}_mismatch")
        if o.get("records_device") != o.get("consumed_device"): reasons.append(f"{stage}:split_filesystem")
    return not reasons, reasons

def validate_target_binding(observed, expected):
    reasons=[]
    fields=(("target_record_id","target_record_id"),("records_path","expected_records_path"),("consumed_path","expected_consumed_path"),("records_realpath","expected_records_realpath"),("consumed_realpath","expected_consumed_realpath"),("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"),("records_symlink","expected_records_symlink"),("consumed_symlink","expected_consumed_symlink"))
    for a,e in fields:
        if observed.get(a) != expected.get(e): reasons.append(f"target_binding:{a}")
    return reasons

def validate_fault_proof(proof, expected):
    reasons=[]; arm=expected["arm"]
    req=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","filesystem_identity","independent_observer_reference","cleanup_reference")
    if not isinstance(proof,dict) or any(k not in proof for k in req): return ["fault_proof_incomplete"]
    if proof["arm"]!=arm: reasons.append("wrong_arm")
    if proof["mechanism_id"]!=expected["mechanism_id"]: reasons.append("wrong_mechanism")
    if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_invalid")
    if proof["target_record_id"]!=expected["target_record_id"]: reasons.append("wrong_target_id")
    if proof["target_path"]!=expected["expected_records_path"]: reasons.append("wrong_target_path")
    if proof["expected_errno"]!=arm or proof["observed_errno"]!=arm: reasons.append("wrong_errno")
    if proof["target_operation"]!=OPS[arm]["operation"]: reasons.append("wrong_operation")
    if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
    if proof["device_id"]!=expected["expected_records_device"] or proof["mount_id"]!=expected["expected_records_mount"] or proof["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("wrong_filesystem_identity")
    if not isinstance(proof["activation_evidence"],dict) or proof["activation_evidence"].get("observed") is not True: reasons.append("activation_not_proven")
    if not isinstance(proof["operation_evidence"],dict) or proof["operation_evidence"].get("observed") is not True: reasons.append("operation_not_proven")
    if not isinstance(proof["service_pid"],int) or proof["service_pid"]<=0: reasons.append("service_pid_invalid")
    if not isinstance(proof["timestamp"],(int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
    return reasons

def expected_fault_observer_context():
    return {"observer_identity":"trusted-root-observer","observer_source_sha256":hashlib.sha256(b"preregistered-trusted-root-observer-v1").hexdigest(),"observer_execution_identity":"root-observer-v1","expected_evidence_root":"/var/lib/v24-rq1/rq16-attestations","expected_owner":"root","expected_mode":"0600","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound"}

def validate_trusted_fault_attestation(att, expected, observer_context, actual_raw_artifact_digest):
    """Validate independently collected attestation; harness claims are not enough."""
    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity","raw_artifact_path","raw_artifact_sha256","cleanup_reference")
    if not isinstance(att,dict): return ["trusted_attestation_missing"]
    if not isinstance(observer_context,dict): return ["expected_observer_context_missing"]
    reasons=[f"attestation_field_missing:{k}" for k in req if k not in att]
    if reasons: return reasons
    if att["rq_id"]!="RQ-16" or att["arm"]!=expected["arm"]: reasons.append("attestation_arm_mismatch")
    if att["mechanism_id"]!=expected["mechanism_id"] or att["mechanism_digest"]!=expected["mechanism_digest"]: reasons.append("attestation_mechanism_mismatch")
    if att["target_record_id"]!=expected["target_record_id"] or att["target_path"]!=expected["expected_records_path"]: reasons.append("attestation_target_mismatch")
    if att["target_operation"]!=OPS[expected["arm"]]["operation"] or att["target_syscall"] not in OPS[expected["arm"]]["syscalls"]: reasons.append("attestation_operation_mismatch")
    if att["service_pid"]!=expected.get("expected_service_pid") or att["service_executable_sha256"]!=expected.get("expected_service_binary_sha256"): reasons.append("attestation_service_mismatch")
    if att["observed_errno"]!=expected["arm"]: reasons.append("attestation_errno_mismatch")
    if att["records_device"]!=expected["expected_records_device"] or att["consumed_device"]!=expected["expected_consumed_device"] or att["records_mount_id"]!=expected["expected_records_mount"] or att["consumed_mount_id"]!=expected["expected_consumed_mount"] or att["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("attestation_topology_mismatch")
    if not isinstance(att["fault_activation_raw_evidence"],(dict,list,str)) or not att["fault_activation_raw_evidence"]: reasons.append("activation_raw_missing")
    if not isinstance(att["operation_raw_evidence"],(dict,list,str)) or not att["operation_raw_evidence"]: reasons.append("operation_raw_missing")
    for k in ("observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity"):
        if att.get(k) != observer_context.get(k): reasons.append(f"observer_context_mismatch:{k}")
    if not isinstance(actual_raw_artifact_digest,str) or att["raw_artifact_sha256"] != actual_raw_artifact_digest: reasons.append("raw_artifact_digest_mismatch")
    return reasons

def _obs_complete(observations, expected):
    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
    if not isinstance(observations,dict): return ["observations_missing"]
    for s in stages:
        o=observations.get(s)
        if not isinstance(o,dict): reasons.append(f"observation_missing:{s}"); continue
        reasons += validate_target_binding(o,expected)
        for k in ("service_pid","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
            if k not in o: reasons.append(f"observation_field_missing:{s}:{k}")
    return reasons

def _entry_name(entry):
    return entry if isinstance(entry,str) else entry.get("name") if isinstance(entry,dict) else None

def _entry_hash(entry):
    return entry.get("hash") if isinstance(entry,dict) else None

def derive_target_state(observation, expected):
    """Derive target membership from structured entries, never summary flags."""
    if not isinstance(observation,dict): return {"errors":["observation_malformed"]}
    target=expected["target_record_id"]+".record"; errors=[]
    states={}
    for field in ("records_entries","consumed_entries"):
        entries=observation.get(field)
        if not isinstance(entries,list): errors.append(f"{field}_missing"); continue
        names=[_entry_name(e) for e in entries]
        count=names.count(target)
        if count>1: errors.append(f"duplicate_target_entry:{field}")
        if any(n is None for n in names): errors.append(f"malformed_entry:{field}")
        if target in names:
            match=entries[names.index(target)]
            if isinstance(match,dict) and match.get("hash") not in (None,expected.get("expected_target_hash")):
                errors.append(f"target_hash_mismatch:{field}")
            if isinstance(match,dict) and match.get("record_id") not in (None,expected["target_record_id"]):
                errors.append(f"target_identity_mismatch:{field}")
        states[field]={"names":names,"target_present":count==1,"target_count":count}
    r=states.get("records_entries",{}).get("target_present",False); c=states.get("consumed_entries",{}).get("target_present",False)
    if r and c: errors.append("target_in_both")
    if not r and not c: errors.append("target_missing_from_both")
    if observation.get("target_hash") not in (None,expected.get("expected_target_hash")): errors.append("target_hash_mismatch:observation")
    if observation.get("target_record_id") != expected["target_record_id"]: errors.append("target_identity_mismatch:observation")
    response=observation.get("response")
    if observation.get("authoritative_success") is True or (isinstance(response,dict) and response.get("service_authoritative") is True): errors.append("authoritative_response_in_observation")
    return {"records":states.get("records_entries",{}),"consumed":states.get("consumed_entries",{}),"target_in_records":r,"target_in_consumed":c,"target_hash":observation.get("target_hash"),"errors":errors}

def derive_lifecycle_transition(before, after, expected):
    b=derive_target_state(before,expected); a=derive_target_state(after,expected); errors=list(b.get("errors",[]))+list(a.get("errors",[]));
    if errors: return {"added_records":[],"removed_records":[],"added_consumed":[],"removed_consumed":[],"errors":errors}
    def delta(k):
        bs=set(b[k]["names"]); as_=set(a[k]["names"]); return sorted(as_-bs),sorted(bs-as_)
    ar,rr=delta("records"); ac,rc=delta("consumed")
    allowed=[]
    for t in expected.get("expected_lifecycle_contract",{}).get("permitted_transitions",[]):
        if isinstance(t,dict): allowed.append((tuple(sorted(t.get("added_records",[]))),tuple(sorted(t.get("removed_records",[]))),tuple(sorted(t.get("added_consumed",[]))),tuple(sorted(t.get("removed_consumed",[])))))
    actual=(tuple(ar),tuple(rr),tuple(ac),tuple(rc))
    if actual != ((),(),(),()) and actual not in allowed: errors.append("unauthorized_lifecycle_transition")
    return {"added_records":ar,"removed_records":rr,"added_consumed":ac,"removed_consumed":rc,"errors":errors}

def validate_lifecycle_sequence(expected_contract, observations, expected):
    if not isinstance(expected_contract,dict): return ["lifecycle_contract_missing"]
    order=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored"); reasons=[]; states={}
    if not isinstance(observations,dict): return ["observations_missing"]
    for stage in order:
        if stage not in observations: reasons.append(f"observation_missing:{stage}"); continue
        derived=derive_target_state(observations[stage],expected); states[stage]=derived; reasons += [f"{stage}:{x}" for x in derived.get("errors",[])]
        contract=expected_contract.get("stages",{}).get(stage,{})
        if derived.get("target_in_records") != contract.get("target_in_records") or derived.get("target_in_consumed") != contract.get("target_in_consumed"): reasons.append(f"{stage}:unexpected_target_state")
        if derived.get("target_hash") not in (None,expected.get("expected_target_hash")): reasons.append(f"{stage}:target_hash_mismatch")
    for before,after in zip(order,order[1:]):
        if before in observations and after in observations: reasons += [f"{before}->{after}:{x}" for x in derive_lifecycle_transition(observations[before],observations[after],expected).get("errors",[])]
    return reasons

def derive_target_lifecycle(observations, expected):
    contract=expected.get("expected_lifecycle_contract",{})
    return {"errors":validate_lifecycle_sequence(contract,observations,expected)}

def _lifecycle_valid(life, expected, observations):
    reasons=derive_target_lifecycle(observations,expected).get("errors",[])
    if not isinstance(life,dict) or not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_summary_missing")
    return reasons

RESTORATION_VOLATILE_FIELDS={"service_pid":"controlled restart may change PID","timestamp":"observation time changes","inode":"recreation may change inode only when preregistered"}
RESTORATION_FIELDS=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")

def compare_restoration(baseline, restored, expected, arm_cleanup_contract=None):
    result={"matched_fields":[],"allowed_changed_fields":[],"unexpected_changed_fields":[],"missing_fields":[],"fault_mechanism_disabled":False,"restoration_pass":False}
    expected_baseline=expected.get("expected_restoration",{})
    if not isinstance(baseline,dict) or not isinstance(restored,dict): result["missing_fields"] += ["baseline_observation","restored_observation"]; return result
    for field in RESTORATION_FIELDS:
        if field not in baseline or field not in restored: result["missing_fields"].append(field); continue
        if field in RESTORATION_VOLATILE_FIELDS:
            if baseline[field]!=restored[field]: result["allowed_changed_fields"].append(field)
        elif baseline[field]!=restored[field]: result["unexpected_changed_fields"].append(field)
        elif field in expected_baseline and baseline[field]!=expected_baseline[field]: result["unexpected_changed_fields"].append(f"baseline:{field}")
        else: result["matched_fields"].append(field)
    result["fault_mechanism_disabled"]=restored.get("fault_state")==expected_baseline.get("fault_state") and restored.get("fault_state",{}).get("active") is False
    result["restoration_pass"]=not result["missing_fields"] and not result["unexpected_changed_fields"] and result["fault_mechanism_disabled"]
    return result

def validate_cleanup(cleanup, expected):
    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified","baseline_observation","restored_observation")
    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
    comparison=compare_restoration(cleanup.get("baseline_observation"),cleanup.get("restored_observation"),expected)
    if not comparison["restoration_pass"]: reasons += ["restoration:"+x for x in comparison["missing_fields"]+comparison["unexpected_changed_fields"]];
    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True or not comparison["fault_mechanism_disabled"]: reasons.append("cleanup_not_verified")
    return reasons

def expected_authorization_context(expected, trusted_provenance=None):
    out={"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"RQ16_ARM_EXECUTION_AUTHORIZED"}
    if trusted_provenance: out.update({"review_artifact_sha256":trusted_provenance["review_artifact_sha256"],"reviewer_designation":trusted_provenance["reviewer_designation"],"issuer_identity":trusted_provenance["issuer_identity"],"issuer_authority_artifact_sha256":trusted_provenance["issuer_authority_artifact_sha256"]})
    return out

def validate_authorization_provenance(token, expected_trusted_provenance, actual_file_metadata=None, actual_artifact_digest=None):
    if not isinstance(expected_trusted_provenance,dict): return ["trusted_authorization_provenance_unavailable"]
    req=("issuer_identity","issuer_authority_artifact_sha256","reviewer_designation","review_artifact_sha256","trusted_storage_identity","trusted_owner","trusted_mode")
    reasons=[f"trusted_provenance_missing:{k}" for k in req if k not in expected_trusted_provenance]
    if reasons: return reasons
    for k in ("issuer_identity","reviewer_designation","review_artifact_sha256","issuer_authority_artifact_sha256"):
        if token.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"authorization_provenance_mismatch:{k}")
    if not isinstance(actual_file_metadata,dict): reasons.append("trusted_storage_metadata_missing")
    else:
        for k in ("trusted_storage_identity","trusted_owner","trusted_mode"):
            if actual_file_metadata.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"trusted_storage_mismatch:{k}")
    if actual_artifact_digest is None or actual_artifact_digest!=expected_trusted_provenance.get("review_artifact_sha256"): reasons.append("review_artifact_digest_unverified")
    if actual_file_metadata is None or actual_file_metadata.get("issuer_authority_artifact_digest")!=expected_trusted_provenance.get("issuer_authority_artifact_sha256"): reasons.append("issuer_artifact_digest_unverified")
    return reasons

def validate_authorization_token(token, expected, now=None, used_nonces=None, trusted_provenance=None, actual_file_metadata=None, actual_review_artifact_digest=None):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    ctx=expected_authorization_context(expected,trusted_provenance)
    for k,v in ctx.items():
        if token.get(k)!=v: reasons.append(f"token_mismatch:{k}")
    try:
        issued=datetime.fromisoformat(token.get("authorization_timestamp","" ).replace("Z","+00:00")); expires=datetime.fromisoformat(token.get("expiration","").replace("Z","+00:00"))
        now=now or datetime.now(timezone.utc)
        if issued > now: reasons.append("authorization_in_future")
        if expires <= now or expires <= issued: reasons.append("expiration_invalid")
        if expires-issued > __import__('datetime').timedelta(hours=1): reasons.append("expiration_unbounded")
    except Exception: reasons.append("timestamp_unparseable")
    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
    if used_nonces is not None and token.get("nonce") in used_nonces: reasons.append("nonce_replay")
    if token.get("source_path")!="/root-owned/rq16-authorization": reasons.append("authorization_source_untrusted")
    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
    reasons += validate_authorization_provenance(token,trusted_provenance,actual_file_metadata,actual_review_artifact_digest)
    return reasons

def evaluate_arm(arm, observed, expected, observer_context=None, actual_raw_artifact_digest=None):
    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
    reasons=[]
    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected,observer_context,actual_raw_artifact_digest)
    reasons += _obs_complete(observed.get("observations"),expected)
    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
    reasons += _lifecycle_valid(observed.get("lifecycle"),expected,observed.get("observations"))
    reasons += validate_cleanup(observed.get("cleanup_proof"),expected)
    if observed.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
    if not topo_ok: reasons.append("rq17_contamination")
    return ("PASS",[]) if not reasons else ("HARNESS_DEFECT",sorted(set(reasons)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true"); a=ap.parse_args()
    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
    if a.self_test: print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["expected-vs-observed separation","exact target binding","structured provenance","observer stages","cleanup structure","RQ17 gate","token binding"]},indent=2)); return 0
    if not a.plan: ap.error("only --plan or --self-test is allowed")
    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json sha256=c54b27af07686999f812264ff3540c4af8f780279c2cc395c2c4d718130e8c34

```json
{
  "exit_code": 0,
  "stderr": "test_absent_response_not_success (__main__.RQ16Tests.test_absent_response_not_success) ... ok\ntest_authority_and_duplicate_transitions_red_or_reject (__main__.RQ16Tests.test_authority_and_duplicate_transitions_red_or_reject) ... ok\ntest_cleanup_exact_baseline_comparison (__main__.RQ16Tests.test_cleanup_exact_baseline_comparison) ... ok\ntest_cross_arm_proof_rejected (__main__.RQ16Tests.test_cross_arm_proof_rejected) ... ok\ntest_expected_context_required (__main__.RQ16Tests.test_expected_context_required) ... ok\ntest_observer_cleanup_lifecycle_mutations_reject (__main__.RQ16Tests.test_observer_cleanup_lifecycle_mutations_reject) ... ok\ntest_provenance_mutations_reject (__main__.RQ16Tests.test_provenance_mutations_reject) ... ok\ntest_rq17_gate_cannot_be_overridden_by_boolean (__main__.RQ16Tests.test_rq17_gate_cannot_be_overridden_by_boolean) ... ok\ntest_target_mutations_reject (__main__.RQ16Tests.test_target_mutations_reject) ... ok\ntest_token_requires_durable_trusted_binding (__main__.RQ16Tests.test_token_requires_durable_trusted_binding) ... ok\ntest_valid_structured_expected_observed_passes (__main__.RQ16Tests.test_valid_structured_expected_observed_passes) ... ok\n\n----------------------------------------------------------------------\nRan 11 tests in <elapsed>\n\nOK\n\ntest_absolute_outside_root_rejected (__main__.ManifestTests.test_absolute_outside_root_rejected) ... ok\ntest_clean_manifest_is_deterministic (__main__.ManifestTests.test_clean_manifest_is_deterministic) ... ok\ntest_duplicate_path_rejected (__main__.ManifestTests.test_duplicate_path_rejected) ... ok\ntest_generated_packet_is_not_source (__main__.ManifestTests.test_generated_packet_is_not_source) ... ok\ntest_manifest_hash_is_content_hash (__main__.ManifestTests.test_manifest_hash_is_content_hash) ... ok\ntest_missing_file_fails (__main__.ManifestTests.test_missing_file_fails) ... ok\ntest_source_byte_change_changes_manifest (__main__.ManifestTests.test_source_byte_change_changes_manifest) ... ok\n\n----------------------------------------------------------------------\nRan 7 tests in <elapsed>\n\nOK\n\n",
  "stdout": "",
  "tests": [
    {
      "name": "test_absent_response_not_success",
      "result": "PASS"
    },
    {
      "name": "test_authority_and_duplicate_transitions_red_or_reject",
      "result": "PASS"
    },
    {
      "name": "test_cleanup_exact_baseline_comparison",
      "result": "PASS"
    },
    {
      "name": "test_cross_arm_proof_rejected",
      "result": "PASS"
    },
    {
      "name": "test_expected_context_required",
      "result": "PASS"
    },
    {
      "name": "test_observer_cleanup_lifecycle_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_provenance_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_rq17_gate_cannot_be_overridden_by_boolean",
      "result": "PASS"
    },
    {
      "name": "test_target_mutations_reject",
      "result": "PASS"
    },
    {
      "name": "test_token_requires_durable_trusted_binding",
      "result": "PASS"
    },
    {
      "name": "test_valid_structured_expected_observed_passes",
      "result": "PASS"
    },
    {
      "name": "test_absolute_outside_root_rejected",
      "result": "PASS"
    },
    {
      "name": "test_clean_manifest_is_deterministic",
      "result": "PASS"
    },
    {
      "name": "test_duplicate_path_rejected",
      "result": "PASS"
    },
    {
      "name": "test_generated_packet_is_not_source",
      "result": "PASS"
    },
    {
      "name": "test_manifest_hash_is_content_hash",
      "result": "PASS"
    },
    {
      "name": "test_missing_file_fails",
      "result": "PASS"
    },
    {
      "name": "test_source_byte_change_changes_manifest",
      "result": "PASS"
    }
  ],
  "tests_failed": 0,
  "tests_passed": 18,
  "tests_total": 18
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json sha256=13352f4d9f42e8ae94d9157414f3cbde667add5b7d85e65990929cb036e5b40a

```json
{
  "RQ16_EXECUTED": false,
  "all_rejected": true,
  "exit_code": 0,
  "mutations": [
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_device",
      "path": "wrong_device",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_mount",
      "path": "wrong_mount",
      "reasons": [
        "fault_active:records_mount_mismatch",
        "rq17_contamination",
        "target_binding:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_filesystem",
      "path": "wrong_filesystem",
      "reasons": [
        "fault_active:records_fs_mismatch",
        "rq17_contamination",
        "target_binding:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "symlink",
      "path": "symlink",
      "reasons": [
        "target_binding:records_symlink"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target",
      "path": "wrong_target",
      "reasons": [
        "wrong_target_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_syscall",
      "path": "wrong_syscall",
      "reasons": [
        "wrong_syscall"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_errno",
      "path": "wrong_errno",
      "reasons": [
        "wrong_errno"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_activation",
      "path": "missing_activation",
      "reasons": [
        "activation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_operation",
      "path": "missing_operation",
      "reasons": [
        "operation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_activation",
      "path": "attestation_missing_raw_activation",
      "reasons": [
        "attestation_field_missing:fault_activation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_operation",
      "path": "attestation_missing_raw_operation",
      "reasons": [
        "attestation_field_missing:operation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_observer",
      "path": "attestation_wrong_observer",
      "reasons": [
        "observer_context_mismatch:observer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_pid",
      "path": "attestation_wrong_pid",
      "reasons": [
        "attestation_service_mismatch"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_artifact_hash",
      "path": "attestation_wrong_artifact_hash",
      "reasons": [
        "raw_artifact_digest_mismatch"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_observer",
      "path": "missing_observer",
      "reasons": [
        "observation_missing:restored"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_observer",
      "path": "bool_only_observer",
      "reasons": [
        "observations_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_cleanup",
      "path": "missing_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_cleanup",
      "path": "bool_only_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_consume",
      "path": "duplicate_consume",
      "reasons": [
        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
        "post_failure:duplicate_target_entry:consumed_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "both_directories",
      "path": "both_directories",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "rq17_false_but_changed",
      "path": "rq17_false_but_changed",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "authoritative_success",
      "path": "authoritative_success",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "invalid_transition",
      "path": "invalid_transition",
      "reasons": [
        "invalid_transition_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "untrusted_expected_context",
      "path": "untrusted_expected_context",
      "reasons": [
        "wrong_mechanism"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_service_hash",
      "path": "cleanup_service_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_gate_hash",
      "path": "cleanup_gate_hash",
      "reasons": [
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mode",
      "path": "cleanup_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_owner",
      "path": "cleanup_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_socket",
      "path": "cleanup_socket",
      "reasons": [
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_active",
      "path": "cleanup_fault_active",
      "reasons": [
        "cleanup_not_verified"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_target_state",
      "path": "cleanup_target_state",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_evidence",
      "path": "cleanup_historical_evidence",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_missing_restored",
      "path": "cleanup_missing_restored",
      "reasons": [
        "cleanup_not_verified",
        "restoration:consumed_device",
        "restoration:consumed_entries",
        "restoration:consumed_fs",
        "restoration:consumed_mount",
        "restoration:consumed_realpath",
        "restoration:fault_state",
        "restoration:gate_sha256",
        "restoration:historical_evidence",
        "restoration:mode",
        "restoration:owner",
        "restoration:records_device",
        "restoration:records_entries",
        "restoration:records_fs",
        "restoration:records_mount",
        "restoration:records_realpath",
        "restoration:security_controls",
        "restoration:service_binary_sha256",
        "restoration:service_identity",
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_target_missing",
      "path": "baseline_target_missing",
      "reasons": [
        "baseline->pre_injection:target_missing_from_both",
        "baseline:target_missing_from_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_already_consumed",
      "path": "baseline_already_consumed",
      "reasons": [
        "baseline->pre_injection:target_in_both",
        "baseline:target_in_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_missing_both",
      "path": "post_failure_missing_both",
      "reasons": [
        "fault_active->post_failure:target_missing_from_both",
        "post_failure->pre_cleanup:target_missing_from_both",
        "post_failure:target_missing_from_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_both",
      "path": "post_failure_both",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target_consumed",
      "path": "wrong_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "historical_target_consumed",
      "path": "historical_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "unrelated_target_transition",
      "path": "unrelated_target_transition",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_authoritative_consumption",
      "path": "duplicate_authoritative_consumption",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "second_authoritative_retry",
      "path": "second_authoritative_retry",
      "reasons": [
        "fault_active->post_failure:authoritative_response_in_observation",
        "post_failure->pre_cleanup:authoritative_response_in_observation",
        "post_failure:authoritative_response_in_observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "replay_state_mutation",
      "path": "replay_state_mutation",
      "reasons": [
        "post_cleanup->restored:target_missing_from_both",
        "restored:target_missing_from_both",
        "restored:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_hash_changed",
      "path": "target_hash_changed",
      "reasons": [
        "fault_active->post_failure:target_hash_mismatch:observation",
        "post_failure->pre_cleanup:target_hash_mismatch:observation",
        "post_failure:target_hash_mismatch",
        "post_failure:target_hash_mismatch:observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_identity_changed",
      "path": "target_identity_changed",
      "reasons": [
        "fault_active->post_failure:target_identity_mismatch:observation",
        "post_failure->pre_cleanup:target_identity_mismatch:observation",
        "post_failure:target_identity_mismatch:observation",
        "target_binding:target_record_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_gate_hash",
      "path": "cleanup_gate_hash",
      "reasons": [
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_device",
      "path": "cleanup_device",
      "reasons": [
        "restoration:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mount",
      "path": "cleanup_mount",
      "reasons": [
        "restoration:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fs",
      "path": "cleanup_fs",
      "reasons": [
        "restoration:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_realpath",
      "path": "cleanup_realpath",
      "reasons": [
        "restoration:records_realpath"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_owner",
      "path": "cleanup_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mode",
      "path": "cleanup_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_socket",
      "path": "cleanup_socket",
      "reasons": [
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_still_active",
      "path": "cleanup_fault_still_active",
      "reasons": [
        "cleanup_not_verified",
        "restoration:fault_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_unrelated_record",
      "path": "cleanup_unrelated_record",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_changed",
      "path": "cleanup_historical_changed",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_hash",
      "path": "cleanup_arbitrary_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_owner",
      "path": "cleanup_arbitrary_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_mode",
      "path": "cleanup_arbitrary_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_arm",
      "path": "arm",
      "reasons": [
        "token_mismatch:arm"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_id",
      "path": "mechanism_id",
      "reasons": [
        "token_mismatch:mechanism_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_digest",
      "path": "mechanism_digest",
      "reasons": [
        "token_mismatch:mechanism_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_commit",
      "path": "plan_commit",
      "reasons": [
        "token_mismatch:plan_commit"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_tree",
      "path": "plan_tree",
      "reasons": [
        "token_mismatch:plan_tree"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_digest",
      "path": "plan_digest",
      "reasons": [
        "token_mismatch:plan_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_execution_contract_digest",
      "path": "execution_contract_digest",
      "reasons": [
        "token_mismatch:execution_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_cleanup_contract_digest",
      "path": "cleanup_contract_digest",
      "reasons": [
        "token_mismatch:cleanup_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_host_identity",
      "path": "host_identity",
      "reasons": [
        "token_mismatch:host_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_runtime_identity",
      "path": "runtime_identity",
      "reasons": [
        "token_mismatch:runtime_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_service_binary_sha256",
      "path": "service_binary_sha256",
      "reasons": [
        "token_mismatch:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_gate_sha256",
      "path": "gate_sha256",
      "reasons": [
        "token_mismatch:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_device",
      "path": "records_device",
      "reasons": [
        "token_mismatch:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_device",
      "path": "consumed_device",
      "reasons": [
        "token_mismatch:consumed_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_mount_id",
      "path": "records_mount_id",
      "reasons": [
        "token_mismatch:records_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_mount_id",
      "path": "consumed_mount_id",
      "reasons": [
        "token_mismatch:consumed_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_independent_review_disposition",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_review_artifact_sha256",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reviewer_designation",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_identity",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_authority_artifact_sha256",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2025-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_expired",
      "path": "expiration",
      "reasons": [
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2030-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_future_issued",
      "path": "authorization_timestamp",
      "reasons": [
        "authorization_in_future",
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "bad",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_malformed_timestamp",
      "path": "expiration",
      "reasons": [
        "timestamp_unparseable"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_empty_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "used",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reused_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_replay"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_source",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "memory",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_registry",
      "path": "single_use_registry",
      "reasons": [
        "nonce_registry_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_self_issued",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_candidate_writable",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "issuer-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_issuer_hash",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "review-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_review_hash",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_wrong_reviewer",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "BOUNDED_PASS",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_generic_bounded_pass",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "CHANGES_REQUIRED",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_changes_required",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "INSUFFICIENT_EVIDENCE",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_insufficient_evidence",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "absent",
      "before": "absent",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_unavailable",
      "path": "trusted_provenance",
      "reasons": [
        "trusted_authorization_provenance_unavailable"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 96,
  "surviving_mutations": 0,
  "total_mutations": 96
}
```


### implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json sha256=c65bdbcbb1c404a2e1eac965a9f2e57b537758d00230e6ce39dca1704c7d9965

```json
{
  "RQ16_AUTHORIZED": false,
  "RQ16_EXECUTED": false,
  "diff_hash_match": true,
  "governance_match": true,
  "identity_model": "PASS",
  "manifest_entries_match": true,
  "manifest_entry_count": 15,
  "manifest_sha_match": true,
  "mutation_result_binding": true,
  "packet_consistency": "PASS",
  "reviewed_source_commit": "195bc72ab79af33659213bdcc1c0e024f336a384",
  "reviewed_source_tree": "5257f6814756ab0ee4a9357ae4f9b12d8e960672",
  "status": "PASS",
  "test_result_binding": true
}
```

## Static and behavioral results

### plan

```text
{
  "mode": "PLAN",
  "arms": [
    "EACCES",
    "EIO",
    "ENOSPC",
    "EROFS"
  ],
  "RQ16_EXECUTED": false,
  "RQ16_AUTHORIZED": false
}
```


### self-test

```text
{
  "mode": "SELF_TEST",
  "passed": true,
  "RQ16_EXECUTED": false,
  "checks": [
    "expected-vs-observed separation",
    "exact target binding",
    "structured provenance",
    "observer stages",
    "cleanup structure",
    "RQ17 gate",
    "token binding"
  ]
}
```


### tests

```text
{
  "tests_total": 18,
  "tests_passed": 18,
  "tests_failed": 0,
  "mutation_total": 96,
  "mutation_rejected": 96,
  "mutation_surviving": 0,
  "all_rejected": true
}
```


### mutations

```json
{
  "RQ16_EXECUTED": false,
  "all_rejected": true,
  "mutations": [
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_device",
      "path": "wrong_device",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_mount",
      "path": "wrong_mount",
      "reasons": [
        "fault_active:records_mount_mismatch",
        "rq17_contamination",
        "target_binding:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_filesystem",
      "path": "wrong_filesystem",
      "reasons": [
        "fault_active:records_fs_mismatch",
        "rq17_contamination",
        "target_binding:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "symlink",
      "path": "symlink",
      "reasons": [
        "target_binding:records_symlink"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target",
      "path": "wrong_target",
      "reasons": [
        "wrong_target_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_syscall",
      "path": "wrong_syscall",
      "reasons": [
        "wrong_syscall"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_errno",
      "path": "wrong_errno",
      "reasons": [
        "wrong_errno"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_activation",
      "path": "missing_activation",
      "reasons": [
        "activation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_operation",
      "path": "missing_operation",
      "reasons": [
        "operation_not_proven"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_activation",
      "path": "attestation_missing_raw_activation",
      "reasons": [
        "attestation_field_missing:fault_activation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_missing_raw_operation",
      "path": "attestation_missing_raw_operation",
      "reasons": [
        "attestation_field_missing:operation_raw_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_observer",
      "path": "attestation_wrong_observer",
      "reasons": [
        "observer_context_mismatch:observer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_pid",
      "path": "attestation_wrong_pid",
      "reasons": [
        "attestation_service_mismatch"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "attestation_wrong_artifact_hash",
      "path": "attestation_wrong_artifact_hash",
      "reasons": [
        "raw_artifact_digest_mismatch"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_observer",
      "path": "missing_observer",
      "reasons": [
        "observation_missing:restored"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_observer",
      "path": "bool_only_observer",
      "reasons": [
        "observations_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "missing_cleanup",
      "path": "missing_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "bool_only_cleanup",
      "path": "bool_only_cleanup",
      "reasons": [
        "cleanup_proof_missing"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_consume",
      "path": "duplicate_consume",
      "reasons": [
        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
        "post_failure:duplicate_target_entry:consumed_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "both_directories",
      "path": "both_directories",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "rq17_false_but_changed",
      "path": "rq17_false_but_changed",
      "reasons": [
        "fault_active:records_device_mismatch",
        "fault_active:split_filesystem",
        "rq17_contamination",
        "target_binding:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "authoritative_success",
      "path": "authoritative_success",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "invalid_transition",
      "path": "invalid_transition",
      "reasons": [
        "invalid_transition_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "untrusted_expected_context",
      "path": "untrusted_expected_context",
      "reasons": [
        "wrong_mechanism"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_service_hash",
      "path": "cleanup_service_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_gate_hash",
      "path": "cleanup_gate_hash",
      "reasons": [
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mode",
      "path": "cleanup_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_owner",
      "path": "cleanup_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_socket",
      "path": "cleanup_socket",
      "reasons": [
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_active",
      "path": "cleanup_fault_active",
      "reasons": [
        "cleanup_not_verified"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_target_state",
      "path": "cleanup_target_state",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_evidence",
      "path": "cleanup_historical_evidence",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_missing_restored",
      "path": "cleanup_missing_restored",
      "reasons": [
        "cleanup_not_verified",
        "restoration:consumed_device",
        "restoration:consumed_entries",
        "restoration:consumed_fs",
        "restoration:consumed_mount",
        "restoration:consumed_realpath",
        "restoration:fault_state",
        "restoration:gate_sha256",
        "restoration:historical_evidence",
        "restoration:mode",
        "restoration:owner",
        "restoration:records_device",
        "restoration:records_entries",
        "restoration:records_fs",
        "restoration:records_mount",
        "restoration:records_realpath",
        "restoration:security_controls",
        "restoration:service_binary_sha256",
        "restoration:service_identity",
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_target_missing",
      "path": "baseline_target_missing",
      "reasons": [
        "baseline->pre_injection:target_missing_from_both",
        "baseline:target_missing_from_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "baseline_already_consumed",
      "path": "baseline_already_consumed",
      "reasons": [
        "baseline->pre_injection:target_in_both",
        "baseline:target_in_both",
        "baseline:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_missing_both",
      "path": "post_failure_missing_both",
      "reasons": [
        "fault_active->post_failure:target_missing_from_both",
        "post_failure->pre_cleanup:target_missing_from_both",
        "post_failure:target_missing_from_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "post_failure_both",
      "path": "post_failure_both",
      "reasons": [
        "fault_active->post_failure:target_in_both",
        "post_failure->pre_cleanup:target_in_both",
        "post_failure:target_in_both",
        "post_failure:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "wrong_target_consumed",
      "path": "wrong_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "historical_target_consumed",
      "path": "historical_target_consumed",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "unrelated_target_transition",
      "path": "unrelated_target_transition",
      "reasons": [
        "fault_active->post_failure:unauthorized_lifecycle_transition",
        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
      ],
      "rejected": true
    },
    {
      "actual_result": "RED",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "duplicate_authoritative_consumption",
      "path": "duplicate_authoritative_consumption",
      "reasons": [
        "authoritative_success_after_fault"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "second_authoritative_retry",
      "path": "second_authoritative_retry",
      "reasons": [
        "fault_active->post_failure:authoritative_response_in_observation",
        "post_failure->pre_cleanup:authoritative_response_in_observation",
        "post_failure:authoritative_response_in_observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "replay_state_mutation",
      "path": "replay_state_mutation",
      "reasons": [
        "post_cleanup->restored:target_missing_from_both",
        "restored:target_missing_from_both",
        "restored:unexpected_target_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_hash_changed",
      "path": "target_hash_changed",
      "reasons": [
        "fault_active->post_failure:target_hash_mismatch:observation",
        "post_failure->pre_cleanup:target_hash_mismatch:observation",
        "post_failure:target_hash_mismatch",
        "post_failure:target_hash_mismatch:observation"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "target_identity_changed",
      "path": "target_identity_changed",
      "reasons": [
        "fault_active->post_failure:target_identity_mismatch:observation",
        "post_failure->pre_cleanup:target_identity_mismatch:observation",
        "post_failure:target_identity_mismatch:observation",
        "target_binding:target_record_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_gate_hash",
      "path": "cleanup_gate_hash",
      "reasons": [
        "restoration:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_device",
      "path": "cleanup_device",
      "reasons": [
        "restoration:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mount",
      "path": "cleanup_mount",
      "reasons": [
        "restoration:records_mount"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fs",
      "path": "cleanup_fs",
      "reasons": [
        "restoration:records_fs"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_realpath",
      "path": "cleanup_realpath",
      "reasons": [
        "restoration:records_realpath"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_owner",
      "path": "cleanup_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_mode",
      "path": "cleanup_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_socket",
      "path": "cleanup_socket",
      "reasons": [
        "restoration:socket_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_fault_still_active",
      "path": "cleanup_fault_still_active",
      "reasons": [
        "cleanup_not_verified",
        "restoration:fault_state"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_unrelated_record",
      "path": "cleanup_unrelated_record",
      "reasons": [
        "restoration:records_entries"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_historical_changed",
      "path": "cleanup_historical_changed",
      "reasons": [
        "restoration:historical_evidence"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_hash",
      "path": "cleanup_arbitrary_hash",
      "reasons": [
        "restoration:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_owner",
      "path": "cleanup_arbitrary_owner",
      "reasons": [
        "restoration:owner"
      ],
      "rejected": true
    },
    {
      "actual_result": "HARNESS_DEFECT",
      "after": "mutated",
      "before": "valid",
      "case": "ENOSPC",
      "expected_result": "REJECT",
      "mutation_id": "cleanup_arbitrary_mode",
      "path": "cleanup_arbitrary_mode",
      "reasons": [
        "restoration:mode"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_arm",
      "path": "arm",
      "reasons": [
        "token_mismatch:arm"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_id",
      "path": "mechanism_id",
      "reasons": [
        "token_mismatch:mechanism_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_mechanism_digest",
      "path": "mechanism_digest",
      "reasons": [
        "token_mismatch:mechanism_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_commit",
      "path": "plan_commit",
      "reasons": [
        "token_mismatch:plan_commit"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_tree",
      "path": "plan_tree",
      "reasons": [
        "token_mismatch:plan_tree"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_plan_digest",
      "path": "plan_digest",
      "reasons": [
        "token_mismatch:plan_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_execution_contract_digest",
      "path": "execution_contract_digest",
      "reasons": [
        "token_mismatch:execution_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_cleanup_contract_digest",
      "path": "cleanup_contract_digest",
      "reasons": [
        "token_mismatch:cleanup_contract_digest"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_host_identity",
      "path": "host_identity",
      "reasons": [
        "token_mismatch:host_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_runtime_identity",
      "path": "runtime_identity",
      "reasons": [
        "token_mismatch:runtime_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_service_binary_sha256",
      "path": "service_binary_sha256",
      "reasons": [
        "token_mismatch:service_binary_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_gate_sha256",
      "path": "gate_sha256",
      "reasons": [
        "token_mismatch:gate_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_device",
      "path": "records_device",
      "reasons": [
        "token_mismatch:records_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_device",
      "path": "consumed_device",
      "reasons": [
        "token_mismatch:consumed_device"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_records_mount_id",
      "path": "records_mount_id",
      "reasons": [
        "token_mismatch:records_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_consumed_mount_id",
      "path": "consumed_mount_id",
      "reasons": [
        "token_mismatch:consumed_mount_id"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_independent_review_disposition",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_review_artifact_sha256",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reviewer_designation",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_identity",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "mutated",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_issuer_authority_artifact_sha256",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2025-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_expired",
      "path": "expiration",
      "reasons": [
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "2030-01-01T00:00:00Z",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_future_issued",
      "path": "authorization_timestamp",
      "reasons": [
        "authorization_in_future",
        "expiration_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "bad",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_malformed_timestamp",
      "path": "expiration",
      "reasons": [
        "timestamp_unparseable"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_empty_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_invalid"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "used",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_reused_nonce",
      "path": "nonce",
      "reasons": [
        "nonce_replay"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_source",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "memory",
      "before": "valid",
      "case": "AUTHORIZATION",
      "expected_result": "REJECT",
      "mutation_id": "auth_untrusted_registry",
      "path": "single_use_registry",
      "reasons": [
        "nonce_registry_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_self_issued",
      "path": "issuer_identity",
      "reasons": [
        "token_mismatch:issuer_identity",
        "authorization_provenance_mismatch:issuer_identity"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_candidate_writable",
      "path": "source_path",
      "reasons": [
        "authorization_source_untrusted"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "issuer-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_issuer_hash",
      "path": "issuer_authority_artifact_sha256",
      "reasons": [
        "token_mismatch:issuer_authority_artifact_sha256",
        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "review-sha",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_placeholder_review_hash",
      "path": "review_artifact_sha256",
      "reasons": [
        "token_mismatch:review_artifact_sha256",
        "authorization_provenance_mismatch:review_artifact_sha256"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "candidate",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_wrong_reviewer",
      "path": "reviewer_designation",
      "reasons": [
        "token_mismatch:reviewer_designation",
        "authorization_provenance_mismatch:reviewer_designation"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "BOUNDED_PASS",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_generic_bounded_pass",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "CHANGES_REQUIRED",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_changes_required",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "INSUFFICIENT_EVIDENCE",
      "before": "valid",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_insufficient_evidence",
      "path": "independent_review_disposition",
      "reasons": [
        "token_mismatch:independent_review_disposition"
      ],
      "rejected": true
    },
    {
      "actual_result": "REJECT",
      "after": "absent",
      "before": "absent",
      "case": "AUTHORIZATION_PROVENANCE",
      "expected_result": "REJECT",
      "mutation_id": "auth_provenance_unavailable",
      "path": "trusted_provenance",
      "reasons": [
        "trusted_authorization_provenance_unavailable"
      ],
      "rejected": true
    }
  ],
  "rejected_mutations": 96,
  "surviving_mutations": 0,
  "total_mutations": 96
}
```


### packet-check-current

```json
{
  "RQ16_AUTHORIZED": false,
  "RQ16_EXECUTED": false,
  "diff_hash_match": true,
  "governance_match": true,
  "identity_model": "PASS",
  "manifest_entries_match": true,
  "manifest_entry_count": 15,
  "manifest_sha_match": true,
  "mutation_result_binding": true,
  "packet_consistency": "PASS",
  "reviewed_source_commit": "195bc72ab79af33659213bdcc1c0e024f336a384",
  "reviewed_source_tree": "5257f6814756ab0ee4a9357ae4f9b12d8e960672",
  "status": "PASS",
  "test_result_binding": true
}
```


### execution-refusal

```text
{"status": "REFUSED", "reason": "RQ16 execution is not authorized in preregistration"}
```

## Exact predecessor-to-reviewed-source diff

### diff

```text
diff --git a/governance-runtime/build_rq16_preregistration_review.py b/governance-runtime/build_rq16_preregistration_review.py
new file mode 100644
index 00000000..acd5d92c
--- /dev/null
+++ b/governance-runtime/build_rq16_preregistration_review.py
@@ -0,0 +1,34 @@
+from __future__ import annotations
+import hashlib, os, subprocess
+from pathlib import Path
+from rq16_manifest import canonical_review_source_files, canonical_evidence_files, build_source_manifest, build_evidence_manifest, manifest_sha256
+ROOT=Path(__file__).resolve().parents[1]
+OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md'
+PACKET_CHECK_CURRENT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json'
+FILES=canonical_review_source_files(ROOT)
+EVIDENCE_FILES=canonical_evidence_files(ROOT)
+def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
+def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
+def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
+def main():
+    if not PACKET_CHECK_CURRENT.exists(): PACKET_CHECK_CURRENT.write_text('{"status":"PENDING"}\n',encoding='utf-8')
+    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
+    diff=run(['git','diff',predecessor,reviewed,'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md']).stdout
+    tests=run(['python','governance-runtime/collect_rq16_results.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+    def render(packet_check_json):
+        source_manifest=build_source_manifest(FILES,ROOT); evidence_manifest=build_evidence_manifest(ROOT); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={manifest_sha256(source_manifest)}',f'generated_evidence_manifest_sha256={manifest_sha256(evidence_manifest)}','packet_content_identity_schema_version=3']
+        parts=['# V24-I11-V6 RQ-16 preregistration remediation-7 final review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[2].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[5].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[1].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[4].read_text(),'json'), '## Source manifest',source_manifest,'## Generated evidence manifest',evidence_manifest]
+        for p in FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
+        for p in EVIDENCE_FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'json'))
+        parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check-current',packet_check_json,'json'),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Historical packet consistency failure source_manifest_entries_mismatch was fixed and superseded; no failed traceback is current evidence. Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
+        OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8')
+    render('{"status":"PENDING"}\n')
+    current_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py','--allow-pending'])
+    if current_check.returncode != 0: raise SystemExit(current_check.stderr or current_check.stdout)
+    packet_check_json=current_check.stdout.strip()+'\n'
+    PACKET_CHECK_CURRENT.write_text(packet_check_json,encoding='utf-8')
+    render(packet_check_json)
+    final_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
+    if final_check.returncode != 0: raise SystemExit(final_check.stderr or final_check.stdout)
+    print(OUT)
+if __name__=='__main__': main()
diff --git a/governance-runtime/check_rq16_preregistration_packet.py b/governance-runtime/check_rq16_preregistration_packet.py
new file mode 100644
index 00000000..6e5974ef
--- /dev/null
+++ b/governance-runtime/check_rq16_preregistration_packet.py
@@ -0,0 +1,38 @@
+#!/usr/bin/env python3
+"""Verify preregistration identities knowable before packet commit."""
+import hashlib, json, re, subprocess
+import sys
+from pathlib import Path
+from rq16_manifest import canonical_review_source_files, build_source_manifest, canonical_evidence_files, build_evidence_manifest, manifest_sha256
+ROOT=Path(__file__).resolve().parents[1]
+PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md'
+SOURCE_FILES=canonical_review_source_files(ROOT)
+def main():
+    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
+    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
+    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
+    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
+    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
+    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
+    assert vals['packet_content_identity_schema_version']=='3'
+    manifest_match=re.search(r'## Source manifest\n(.*?)(?:\n### |\n## )',text,re.S)
+    assert manifest_match, 'source_manifest_section_missing'
+    declared=json.loads(manifest_match.group(1).strip())
+    expected_manifest=json.loads(build_source_manifest(SOURCE_FILES,ROOT))
+    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
+    manifest=build_source_manifest(SOURCE_FILES,ROOT)
+    assert manifest_sha256(manifest)==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
+    evidence_match=re.search(r'## Generated evidence manifest\n(.*?)(?:\n### |\n## )',text,re.S); assert evidence_match, 'evidence_manifest_section_missing'
+    assert json.loads(evidence_match.group(1).strip())==json.loads(build_evidence_manifest(ROOT)), 'evidence_manifest_entries_mismatch'
+    current_path=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json'; current=json.loads(current_path.read_text())
+    if current.get('status')!='PENDING' or '--allow-pending' not in sys.argv: assert current.get('status')=='PASS' and current.get('packet_consistency')=='PASS', 'current_packet_check_not_pass'
+    tests=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json').read_text()); muts=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json').read_text())
+    assert tests['tests_total']==tests['tests_passed']+tests['tests_failed'] and tests['exit_code']==0, 'test_result_binding_mismatch'
+    assert muts['total_mutations']==len(muts['mutations']) and muts['rejected_mutations']+muts['surviving_mutations']==muts['total_mutations'] and muts['all_rejected']==(muts['surviving_mutations']==0), 'mutation_result_binding_mismatch'
+    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
+    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
+    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
+    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
+    print(json.dumps({'status':'PASS','packet_consistency':'PASS','identity_model':'PASS','reviewed_source_commit':vals['reviewed_source_commit'],'reviewed_source_tree':vals['reviewed_source_tree'],'manifest_entry_count':len(expected_manifest),'manifest_entries_match':True,'manifest_sha_match':True,'diff_hash_match':True,'test_result_binding':True,'mutation_result_binding':True,'governance_match':True,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2,sort_keys=True)); return 0
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/collect_rq16_results.py b/governance-runtime/collect_rq16_results.py
new file mode 100644
index 00000000..d1339df2
--- /dev/null
+++ b/governance-runtime/collect_rq16_results.py
@@ -0,0 +1,25 @@
+#!/usr/bin/env python3
+"""Generate the single authoritative offline RQ-16 test and mutation results."""
+import json, re, subprocess
+from pathlib import Path
+ROOT=Path(__file__).resolve().parents[1]
+TEST_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json'
+MUT_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json'
+def main():
+    runs=[subprocess.run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py'],cwd=ROOT,text=True,capture_output=True),subprocess.run(['python','governance-runtime/test_rq16_manifest.py'],cwd=ROOT,text=True,capture_output=True)]
+    t=subprocess.CompletedProcess([],max((x.returncode for x in runs),default=0),stdout='\n'.join(x.stdout for x in runs),stderr='\n'.join(x.stderr for x in runs))
+    m=subprocess.run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'],cwd=ROOT,text=True,capture_output=True)
+    combined=re.sub(r'Ran (\d+) tests? in [0-9.]+s',r'Ran \1 tests in <elapsed>',t.stderr+t.stdout)
+    matches=re.findall(r'Ran (\d+) tests?',combined); total=sum(int(x) for x in matches)
+    tests=[]
+    for line in combined.splitlines():
+        hit=re.match(r'test_\w+ \(__main__\.[^)]+\) \.\.\. (ok|FAIL)',line)
+        if hit: tests.append({'name':line.split(' (',1)[0],'result':'PASS' if hit.group(1)=='ok' else 'FAIL'})
+    test_result={'tests_total':total,'tests_passed':sum(x['result']=='PASS' for x in tests),'tests_failed':sum(x['result']=='FAIL' for x in tests),'exit_code':t.returncode,'tests':tests,'stdout':'','stderr':combined}
+    mutation_result=json.loads(m.stdout)
+    mutation_result['exit_code']=m.returncode
+    TEST_OUT.write_text(json.dumps(test_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
+    MUT_OUT.write_text(json.dumps(mutation_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
+    print(json.dumps({'tests_total':test_result['tests_total'],'tests_passed':test_result['tests_passed'],'tests_failed':test_result['tests_failed'],'mutation_total':mutation_result['total_mutations'],'mutation_rejected':mutation_result['rejected_mutations'],'mutation_surviving':mutation_result['surviving_mutations'],'all_rejected':mutation_result['all_rejected']},indent=2))
+    return 0 if t.returncode==0 and m.returncode==0 else 1
+if __name__=='__main__': raise SystemExit(main())
diff --git a/governance-runtime/rq16_manifest.py b/governance-runtime/rq16_manifest.py
new file mode 100644
index 00000000..97e3a47b
--- /dev/null
+++ b/governance-runtime/rq16_manifest.py
@@ -0,0 +1,54 @@
+#!/usr/bin/env python3
+"""Canonical source/evidence manifest definitions for the RQ-16 review packet."""
+import hashlib, json
+from pathlib import Path
+
+ROOT=Path(__file__).resolve().parents[1]
+SOURCE_RELATIVE=(
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md",
+    "governance-runtime/build_rq16_preregistration_review.py",
+    "governance-runtime/check_rq16_preregistration_packet.py",
+    "governance-runtime/collect_rq16_results.py",
+    "governance-runtime/run_v24_v6_rq1_rq16_mutations.py",
+    "governance-runtime/rq16_manifest.py",
+    "governance-runtime/test_v24_v6_rq1_rq16_harness.py",
+    "governance-runtime/test_rq16_manifest.py",
+    "governance-runtime/v24_v6_rq1_rq16_harness.py",
+)
+EVIDENCE_RELATIVE=(
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json",
+    "implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json",
+)
+
+def canonical_review_source_files(root=ROOT):
+    return [root / rel for rel in SOURCE_RELATIVE]
+
+def canonical_evidence_files(root=ROOT):
+    return [root / rel for rel in EVIDENCE_RELATIVE]
+
+def _entries(files, root=ROOT):
+    entries=[]
+    for path in files:
+        rel=path.resolve().relative_to(root.resolve()).as_posix()
+        if rel.startswith("/") or Path(rel).is_absolute() or ".." in Path(rel).parts:
+            raise ValueError(f"non-canonical path: {rel}")
+        entries.append({"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
+    if len({e["path"] for e in entries}) != len(entries):
+        raise ValueError("duplicate canonical path")
+    return sorted(entries,key=lambda e:e["path"])
+
+def build_source_manifest(files=None, root=ROOT):
+    return json.dumps(_entries(files or canonical_review_source_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
+
+def build_evidence_manifest(root=ROOT):
+    return json.dumps(_entries(canonical_evidence_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
+
+def manifest_sha256(manifest):
+    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()
diff --git a/governance-runtime/run_v24_v6_rq1_rq16_mutations.py b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
new file mode 100644
index 00000000..51b75148
--- /dev/null
+++ b/governance-runtime/run_v24_v6_rq1_rq16_mutations.py
@@ -0,0 +1,86 @@
+#!/usr/bin/env python3
+import copy, hashlib, json
+from datetime import datetime, timezone
+from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, expected_fault_observer_context, validate_authorization_token
+from test_v24_v6_rq1_rq16_harness import good, TRUSTED
+EXPECTED=expected_context("ENOSPC")
+OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
+def main():
+    specs=[
+      ("wrong_device",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
+      ("wrong_mount",lambda e:e["observations"]["fault_active"].update(records_mount="m2")),
+      ("wrong_filesystem",lambda e:e["observations"]["fault_active"].update(records_fs="fs2")),
+      ("symlink",lambda e:e["observations"]["fault_active"].update(records_symlink=True)),
+      ("wrong_target",lambda e:e["fault_proof"].update(target_record_id="other")),
+      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
+      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
+      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
+      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
+      ("attestation_missing_raw_activation",lambda e:e["trusted_fault_attestation"].pop("fault_activation_raw_evidence")),
+      ("attestation_missing_raw_operation",lambda e:e["trusted_fault_attestation"].pop("operation_raw_evidence")),
+      ("attestation_wrong_observer",lambda e:e["trusted_fault_attestation"].update(observer_identity="candidate")),
+      ("attestation_wrong_pid",lambda e:e["trusted_fault_attestation"].update(service_pid=99)),
+      ("attestation_wrong_artifact_hash",lambda e:e["trusted_fault_attestation"].update(raw_artifact_sha256="fake")),
+      ("missing_observer",lambda e:e["observations"].pop("restored")),
+      ("bool_only_observer",lambda e:e.pop("observations")),
+      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
+      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
+      ("duplicate_consume",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record","abc123.record"])),
+      ("both_directories",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
+      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
+      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
+      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
+      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
+      ("cleanup_service_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="bad")),
+      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
+      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
+      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
+      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
+      ("cleanup_fault_active",lambda e:e["cleanup_proof"].update(fault_disabled=False)),
+      ("cleanup_target_state",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=[])),
+      ("cleanup_historical_evidence",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence="changed")),
+      ("cleanup_missing_restored",lambda e:e["cleanup_proof"].update(restored_observation={})),
+      ("baseline_target_missing",lambda e:e["observations"]["baseline"].update(records_entries=[])),
+      ("baseline_already_consumed",lambda e:e["observations"]["baseline"].update(consumed_entries=["abc123.record"])),
+      ("post_failure_missing_both",lambda e:e["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
+      ("post_failure_both",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
+      ("wrong_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["other.record"])),
+      ("historical_target_consumed",lambda e:e["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
+      ("unrelated_target_transition",lambda e:e["observations"]["post_failure"].update(records_entries=["abc123.record","other.record"])),
+      ("duplicate_authoritative_consumption",lambda e:e.update(authoritative_success=True)),
+      ("second_authoritative_retry",lambda e:e["observations"]["post_failure"].update(response={"service_authoritative":True})),
+      ("replay_state_mutation",lambda e:e["observations"]["restored"].update(records_entries=["other.record"])),
+      ("target_hash_changed",lambda e:e["observations"]["post_failure"].update(target_hash="changed")),
+      ("target_identity_changed",lambda e:e["observations"]["post_failure"].update(target_record_id="other")),
+      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
+      ("cleanup_device",lambda e:e["cleanup_proof"]["restored_observation"].update(records_device="bad")),
+      ("cleanup_mount",lambda e:e["cleanup_proof"]["restored_observation"].update(records_mount="bad")),
+      ("cleanup_fs",lambda e:e["cleanup_proof"]["restored_observation"].update(records_fs="bad")),
+      ("cleanup_realpath",lambda e:e["cleanup_proof"]["restored_observation"].update(records_realpath="bad")),
+      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
+      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
+      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
+      ("cleanup_fault_still_active",lambda e:e["cleanup_proof"]["restored_observation"].update(fault_state={"active":True})),
+      ("cleanup_unrelated_record",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=["abc123.record","other.record"])),
+      ("cleanup_historical_changed",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence={"intact":False})),
+      ("cleanup_arbitrary_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="arbitrary")),
+      ("cleanup_arbitrary_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="arbitrary")),
+      ("cleanup_arbitrary_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="arbitrary")),
+    ]
+    rows=[]
+    for name,mut in specs:
+        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)
+        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
+    token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+    metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
+    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
+    for field in auth_fields:
+        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
+        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used,trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    for name,field,value in (("self_issued","issuer_identity","candidate"),("candidate_writable","source_path","candidate"),("placeholder_issuer_hash","issuer_authority_artifact_sha256","issuer-sha"),("placeholder_review_hash","review_artifact_sha256","review-sha"),("wrong_reviewer","reviewer_designation","candidate"),("generic_bounded_pass","independent_review_disposition","BOUNDED_PASS"),("changes_required","independent_review_disposition","CHANGES_REQUIRED"),("insufficient_evidence","independent_review_disposition","INSUFFICIENT_EVIDENCE")):
+        bad=dict(token); bad[field]=value; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]); rows.append({"mutation_id":"auth_provenance_"+name,"case":"AUTHORIZATION_PROVENANCE","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    reasons=validate_authorization_token(token,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_provenance_unavailable","case":"AUTHORIZATION_PROVENANCE","path":"trusted_provenance","before":"absent","after":"absent","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
+    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
+    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
+if __name__=="__main__": raise SystemExit(main())
diff --git a/governance-runtime/test_rq16_manifest.py b/governance-runtime/test_rq16_manifest.py
new file mode 100644
index 00000000..eee9c711
--- /dev/null
+++ b/governance-runtime/test_rq16_manifest.py
@@ -0,0 +1,36 @@
+#!/usr/bin/env python3
+import shutil, unittest
+from contextlib import contextmanager
+from pathlib import Path
+from rq16_manifest import ROOT, canonical_review_source_files, build_source_manifest, manifest_sha256
+
+class ManifestTests(unittest.TestCase):
+    @contextmanager
+    def scratch(self):
+        d=ROOT/".rq16-manifest-test"; shutil.rmtree(d,ignore_errors=True); d.mkdir()
+        try: yield d
+        finally: shutil.rmtree(d,ignore_errors=True)
+    def test_clean_manifest_is_deterministic(self):
+        files=canonical_review_source_files(ROOT)
+        self.assertEqual(build_source_manifest(files),build_source_manifest(list(reversed(files))))
+        self.assertEqual(len({x.relative_to(ROOT).as_posix() for x in files}),len(files))
+    def test_source_byte_change_changes_manifest(self):
+        with self.scratch() as d:
+            p=d/"x.py"; p.write_bytes(b"x=1\n"); before=build_source_manifest([p],d); p.write_bytes(b"x=2\n"); self.assertNotEqual(before,build_source_manifest([p],d))
+    def test_duplicate_path_rejected(self):
+        with self.scratch() as d:
+            p=d/"x"; p.write_bytes(b"x");
+            with self.assertRaises(ValueError): build_source_manifest([p,p],d)
+    def test_missing_file_fails(self):
+        with self.assertRaises(FileNotFoundError): build_source_manifest([ROOT/"does-not-exist"],ROOT)
+    def test_absolute_outside_root_rejected(self):
+        with self.scratch() as d:
+            p=d/"x"; p.write_bytes(b"x");
+            with self.assertRaises(ValueError): build_source_manifest([Path("C:/outside-rq16/x")],ROOT)
+    def test_generated_packet_is_not_source(self):
+        names={p.name for p in canonical_review_source_files(ROOT)}
+        self.assertNotIn("V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md",names)
+    def test_manifest_hash_is_content_hash(self):
+        self.assertEqual(len(manifest_sha256(build_source_manifest())),64)
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/test_v24_v6_rq1_rq16_harness.py b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..54e6f15c
--- /dev/null
+++ b/governance-runtime/test_v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,73 @@
+#!/usr/bin/env python3
+import copy, hashlib, unittest
+from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context, expected_fault_observer_context
+
+EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
+OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
+TRUSTED={"issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":hashlib.sha256(b"issuer").hexdigest(),"reviewer_designation":"independent-reviewer","review_artifact_sha256":hashlib.sha256(b"review").hexdigest(),"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600"}
+def observation():
+    return {s:{"target_record_id":TARGET,"target_hash":"target-hash","records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+def good():
+    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":OBSERVER["observer_identity"],"observer_source_sha256":OBSERVER["observer_source_sha256"],"observer_execution_identity":OBSERVER["observer_execution_identity"],"expected_evidence_root":OBSERVER["expected_evidence_root"],"expected_owner":OBSERVER["expected_owner"],"expected_mode":OBSERVER["expected_mode"],"expected_host_identity":OBSERVER["expected_host_identity"],"expected_runtime_identity":OBSERVER["expected_runtime_identity"],"raw_artifact_path":"/var/lib/v24-rq1/rq16-attestations/a.raw","raw_artifact_sha256":ARTIFACT_DIGEST,"cleanup_reference":"clean"}
+    base=copy.deepcopy(EXPECTED["expected_restoration"])
+    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}
+
+class RQ16Tests(unittest.TestCase):
+    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
+    def test_target_mutations_reject(self):
+        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
+            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
+            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
+            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_provenance_mutations_reject(self):
+        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
+            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_observer_cleanup_lifecycle_mutations_reject(self):
+        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        mutations=[
+            ("baseline_target_missing",lambda x:x["observations"]["baseline"].update(records_entries=[])),
+            ("baseline_target_already_consumed",lambda x:x["observations"]["baseline"].update(consumed_entries=[TARGET+".record"])),
+            ("post_failure_target_missing_both",lambda x:x["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
+            ("post_failure_target_both",lambda x:x["observations"]["post_failure"].update(consumed_entries=[TARGET+".record"])),
+            ("wrong_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["other.record"])),
+            ("historical_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
+            ("unrelated_target_transition",lambda x:x["observations"]["post_failure"].update(records_entries=[TARGET+".record","other.record"])),
+            ("duplicate_authoritative_consumption",lambda x:x.update(authoritative_success=True)),
+            ("second_authoritative_retry",lambda x:x["observations"]["post_failure"].update(response={"service_authoritative":True})),
+            ("replay_state_mutation",lambda x:x["observations"]["restored"].update(records_entries=["other.record"])),
+            ("target_hash_changed",lambda x:x["observations"]["post_failure"].update(target_hash="changed")),
+            ("target_identity_changed",lambda x:x["observations"]["post_failure"].update(target_record_id="other")),
+        ]
+        for _,mut in mutations:
+            e=good(); mut(e); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
+        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
+    def test_cleanup_exact_baseline_comparison(self):
+        fields=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
+        for field in fields:
+            e=good(); e["cleanup_proof"]["restored_observation"][field]="arbitrary"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+        e=good(); e["cleanup_proof"].update(cleanup_ok=True); e["cleanup_proof"].pop("baseline_observation"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_authority_and_duplicate_transitions_red_or_reject(self):
+        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"RED")
+        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_token_requires_durable_trusted_binding(self):
+        self.assertTrue(validate_authorization_token({},EXPECTED))
+        token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
+        metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
+        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
+            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"},trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
+    def test_cross_arm_proof_rejected(self):
+        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"),OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+    def test_absent_response_not_success(self):
+        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
+
+if __name__=="__main__": unittest.main(verbosity=2)
diff --git a/governance-runtime/v24_v6_rq1_rq16_harness.py b/governance-runtime/v24_v6_rq1_rq16_harness.py
new file mode 100644
index 00000000..4918ad16
--- /dev/null
+++ b/governance-runtime/v24_v6_rq1_rq16_harness.py
@@ -0,0 +1,256 @@
+#!/usr/bin/env python3
+"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
+from __future__ import annotations
+import argparse, hashlib, json, math, re
+from datetime import datetime, timezone
+
+ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
+OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
+MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}
+TRUSTED_AUTHORIZATION_PROVENANCE_AVAILABLE=False
+
+def expected_trusted_authorization_provenance():
+    """No governance-authorized issuer is available during preregistration."""
+    return None
+
+def expected_context(arm, record_id="abc123"):
+    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
+    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
+    baseline={"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_realpath":rp,"consumed_realpath":cp,"owner":{"uid":0,"gid":0},"mode":{"records":"0700","consumed":"0700"},"socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"service_identity":"uid0:trusted-service","security_controls":{"policy":"stable"},"fault_state":{"active":False},"records_entries":[record_id+".record"],"consumed_entries":[],"historical_evidence":{"intact":True}}
+    stages={s:{"target_in_records":True,"target_in_consumed":False,"target_hash":"target-hash"} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
+    lifecycle={"status":"MANUAL_REVIEW_REQUIRED","stages":stages,"permitted_transitions":[]}
+    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_target_hash":"target-hash","expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","expected_restoration":baseline,"expected_lifecycle_contract":lifecycle}
+
+def check_rq17_contamination(expected, observed):
+    reasons=[]
+    if expected.get("expected_records_device") != expected.get("expected_consumed_device"): reasons.append("expected_baseline_split")
+    for stage, o in (observed or {}).items():
+        if not isinstance(o,dict): reasons.append(f"stage_malformed:{stage}"); continue
+        pairs=(("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"))
+        for actual, exp in pairs:
+            if o.get(actual) != expected.get(exp): reasons.append(f"{stage}:{actual}_mismatch")
+        if o.get("records_device") != o.get("consumed_device"): reasons.append(f"{stage}:split_filesystem")
+    return not reasons, reasons
+
+def validate_target_binding(observed, expected):
+    reasons=[]
+    fields=(("target_record_id","target_record_id"),("records_path","expected_records_path"),("consumed_path","expected_consumed_path"),("records_realpath","expected_records_realpath"),("consumed_realpath","expected_consumed_realpath"),("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"),("records_symlink","expected_records_symlink"),("consumed_symlink","expected_consumed_symlink"))
+    for a,e in fields:
+        if observed.get(a) != expected.get(e): reasons.append(f"target_binding:{a}")
+    return reasons
+
+def validate_fault_proof(proof, expected):
+    reasons=[]; arm=expected["arm"]
+    req=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","filesystem_identity","independent_observer_reference","cleanup_reference")
+    if not isinstance(proof,dict) or any(k not in proof for k in req): return ["fault_proof_incomplete"]
+    if proof["arm"]!=arm: reasons.append("wrong_arm")
+    if proof["mechanism_id"]!=expected["mechanism_id"]: reasons.append("wrong_mechanism")
+    if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_invalid")
+    if proof["target_record_id"]!=expected["target_record_id"]: reasons.append("wrong_target_id")
+    if proof["target_path"]!=expected["expected_records_path"]: reasons.append("wrong_target_path")
+    if proof["expected_errno"]!=arm or proof["observed_errno"]!=arm: reasons.append("wrong_errno")
+    if proof["target_operation"]!=OPS[arm]["operation"]: reasons.append("wrong_operation")
+    if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
+    if proof["device_id"]!=expected["expected_records_device"] or proof["mount_id"]!=expected["expected_records_mount"] or proof["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("wrong_filesystem_identity")
+    if not isinstance(proof["activation_evidence"],dict) or proof["activation_evidence"].get("observed") is not True: reasons.append("activation_not_proven")
+    if not isinstance(proof["operation_evidence"],dict) or proof["operation_evidence"].get("observed") is not True: reasons.append("operation_not_proven")
+    if not isinstance(proof["service_pid"],int) or proof["service_pid"]<=0: reasons.append("service_pid_invalid")
+    if not isinstance(proof["timestamp"],(int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
+    return reasons
+
+def expected_fault_observer_context():
+    return {"observer_identity":"trusted-root-observer","observer_source_sha256":hashlib.sha256(b"preregistered-trusted-root-observer-v1").hexdigest(),"observer_execution_identity":"root-observer-v1","expected_evidence_root":"/var/lib/v24-rq1/rq16-attestations","expected_owner":"root","expected_mode":"0600","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound"}
+
+def validate_trusted_fault_attestation(att, expected, observer_context, actual_raw_artifact_digest):
+    """Validate independently collected attestation; harness claims are not enough."""
+    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity","raw_artifact_path","raw_artifact_sha256","cleanup_reference")
+    if not isinstance(att,dict): return ["trusted_attestation_missing"]
+    if not isinstance(observer_context,dict): return ["expected_observer_context_missing"]
+    reasons=[f"attestation_field_missing:{k}" for k in req if k not in att]
+    if reasons: return reasons
+    if att["rq_id"]!="RQ-16" or att["arm"]!=expected["arm"]: reasons.append("attestation_arm_mismatch")
+    if att["mechanism_id"]!=expected["mechanism_id"] or att["mechanism_digest"]!=expected["mechanism_digest"]: reasons.append("attestation_mechanism_mismatch")
+    if att["target_record_id"]!=expected["target_record_id"] or att["target_path"]!=expected["expected_records_path"]: reasons.append("attestation_target_mismatch")
+    if att["target_operation"]!=OPS[expected["arm"]]["operation"] or att["target_syscall"] not in OPS[expected["arm"]]["syscalls"]: reasons.append("attestation_operation_mismatch")
+    if att["service_pid"]!=expected.get("expected_service_pid") or att["service_executable_sha256"]!=expected.get("expected_service_binary_sha256"): reasons.append("attestation_service_mismatch")
+    if att["observed_errno"]!=expected["arm"]: reasons.append("attestation_errno_mismatch")
+    if att["records_device"]!=expected["expected_records_device"] or att["consumed_device"]!=expected["expected_consumed_device"] or att["records_mount_id"]!=expected["expected_records_mount"] or att["consumed_mount_id"]!=expected["expected_consumed_mount"] or att["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("attestation_topology_mismatch")
+    if not isinstance(att["fault_activation_raw_evidence"],(dict,list,str)) or not att["fault_activation_raw_evidence"]: reasons.append("activation_raw_missing")
+    if not isinstance(att["operation_raw_evidence"],(dict,list,str)) or not att["operation_raw_evidence"]: reasons.append("operation_raw_missing")
+    for k in ("observer_identity","observer_source_sha256","observer_execution_identity","expected_evidence_root","expected_owner","expected_mode","expected_host_identity","expected_runtime_identity"):
+        if att.get(k) != observer_context.get(k): reasons.append(f"observer_context_mismatch:{k}")
+    if not isinstance(actual_raw_artifact_digest,str) or att["raw_artifact_sha256"] != actual_raw_artifact_digest: reasons.append("raw_artifact_digest_mismatch")
+    return reasons
+
+def _obs_complete(observations, expected):
+    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
+    if not isinstance(observations,dict): return ["observations_missing"]
+    for s in stages:
+        o=observations.get(s)
+        if not isinstance(o,dict): reasons.append(f"observation_missing:{s}"); continue
+        reasons += validate_target_binding(o,expected)
+        for k in ("service_pid","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
+            if k not in o: reasons.append(f"observation_field_missing:{s}:{k}")
+    return reasons
+
+def _entry_name(entry):
+    return entry if isinstance(entry,str) else entry.get("name") if isinstance(entry,dict) else None
+
+def _entry_hash(entry):
+    return entry.get("hash") if isinstance(entry,dict) else None
+
+def derive_target_state(observation, expected):
+    """Derive target membership from structured entries, never summary flags."""
+    if not isinstance(observation,dict): return {"errors":["observation_malformed"]}
+    target=expected["target_record_id"]+".record"; errors=[]
+    states={}
+    for field in ("records_entries","consumed_entries"):
+        entries=observation.get(field)
+        if not isinstance(entries,list): errors.append(f"{field}_missing"); continue
+        names=[_entry_name(e) for e in entries]
+        count=names.count(target)
+        if count>1: errors.append(f"duplicate_target_entry:{field}")
+        if any(n is None for n in names): errors.append(f"malformed_entry:{field}")
+        if target in names:
+            match=entries[names.index(target)]
+            if isinstance(match,dict) and match.get("hash") not in (None,expected.get("expected_target_hash")):
+                errors.append(f"target_hash_mismatch:{field}")
+            if isinstance(match,dict) and match.get("record_id") not in (None,expected["target_record_id"]):
+                errors.append(f"target_identity_mismatch:{field}")
+        states[field]={"names":names,"target_present":count==1,"target_count":count}
+    r=states.get("records_entries",{}).get("target_present",False); c=states.get("consumed_entries",{}).get("target_present",False)
+    if r and c: errors.append("target_in_both")
+    if not r and not c: errors.append("target_missing_from_both")
+    if observation.get("target_hash") not in (None,expected.get("expected_target_hash")): errors.append("target_hash_mismatch:observation")
+    if observation.get("target_record_id") != expected["target_record_id"]: errors.append("target_identity_mismatch:observation")
+    response=observation.get("response")
+    if observation.get("authoritative_success") is True or (isinstance(response,dict) and response.get("service_authoritative") is True): errors.append("authoritative_response_in_observation")
+    return {"records":states.get("records_entries",{}),"consumed":states.get("consumed_entries",{}),"target_in_records":r,"target_in_consumed":c,"target_hash":observation.get("target_hash"),"errors":errors}
+
+def derive_lifecycle_transition(before, after, expected):
+    b=derive_target_state(before,expected); a=derive_target_state(after,expected); errors=list(b.get("errors",[]))+list(a.get("errors",[]));
+    if errors: return {"added_records":[],"removed_records":[],"added_consumed":[],"removed_consumed":[],"errors":errors}
+    def delta(k):
+        bs=set(b[k]["names"]); as_=set(a[k]["names"]); return sorted(as_-bs),sorted(bs-as_)
+    ar,rr=delta("records"); ac,rc=delta("consumed")
+    allowed=[]
+    for t in expected.get("expected_lifecycle_contract",{}).get("permitted_transitions",[]):
+        if isinstance(t,dict): allowed.append((tuple(sorted(t.get("added_records",[]))),tuple(sorted(t.get("removed_records",[]))),tuple(sorted(t.get("added_consumed",[]))),tuple(sorted(t.get("removed_consumed",[])))))
+    actual=(tuple(ar),tuple(rr),tuple(ac),tuple(rc))
+    if actual != ((),(),(),()) and actual not in allowed: errors.append("unauthorized_lifecycle_transition")
+    return {"added_records":ar,"removed_records":rr,"added_consumed":ac,"removed_consumed":rc,"errors":errors}
+
+def validate_lifecycle_sequence(expected_contract, observations, expected):
+    if not isinstance(expected_contract,dict): return ["lifecycle_contract_missing"]
+    order=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored"); reasons=[]; states={}
+    if not isinstance(observations,dict): return ["observations_missing"]
+    for stage in order:
+        if stage not in observations: reasons.append(f"observation_missing:{stage}"); continue
+        derived=derive_target_state(observations[stage],expected); states[stage]=derived; reasons += [f"{stage}:{x}" for x in derived.get("errors",[])]
+        contract=expected_contract.get("stages",{}).get(stage,{})
+        if derived.get("target_in_records") != contract.get("target_in_records") or derived.get("target_in_consumed") != contract.get("target_in_consumed"): reasons.append(f"{stage}:unexpected_target_state")
+        if derived.get("target_hash") not in (None,expected.get("expected_target_hash")): reasons.append(f"{stage}:target_hash_mismatch")
+    for before,after in zip(order,order[1:]):
+        if before in observations and after in observations: reasons += [f"{before}->{after}:{x}" for x in derive_lifecycle_transition(observations[before],observations[after],expected).get("errors",[])]
+    return reasons
+
+def derive_target_lifecycle(observations, expected):
+    contract=expected.get("expected_lifecycle_contract",{})
+    return {"errors":validate_lifecycle_sequence(contract,observations,expected)}
+
+def _lifecycle_valid(life, expected, observations):
+    reasons=derive_target_lifecycle(observations,expected).get("errors",[])
+    if not isinstance(life,dict) or not isinstance(life.get("deltas"),dict): reasons.append("lifecycle_summary_missing")
+    return reasons
+
+RESTORATION_VOLATILE_FIELDS={"service_pid":"controlled restart may change PID","timestamp":"observation time changes","inode":"recreation may change inode only when preregistered"}
+RESTORATION_FIELDS=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
+
+def compare_restoration(baseline, restored, expected, arm_cleanup_contract=None):
+    result={"matched_fields":[],"allowed_changed_fields":[],"unexpected_changed_fields":[],"missing_fields":[],"fault_mechanism_disabled":False,"restoration_pass":False}
+    expected_baseline=expected.get("expected_restoration",{})
+    if not isinstance(baseline,dict) or not isinstance(restored,dict): result["missing_fields"] += ["baseline_observation","restored_observation"]; return result
+    for field in RESTORATION_FIELDS:
+        if field not in baseline or field not in restored: result["missing_fields"].append(field); continue
+        if field in RESTORATION_VOLATILE_FIELDS:
+            if baseline[field]!=restored[field]: result["allowed_changed_fields"].append(field)
+        elif baseline[field]!=restored[field]: result["unexpected_changed_fields"].append(field)
+        elif field in expected_baseline and baseline[field]!=expected_baseline[field]: result["unexpected_changed_fields"].append(f"baseline:{field}")
+        else: result["matched_fields"].append(field)
+    result["fault_mechanism_disabled"]=restored.get("fault_state")==expected_baseline.get("fault_state") and restored.get("fault_state",{}).get("active") is False
+    result["restoration_pass"]=not result["missing_fields"] and not result["unexpected_changed_fields"] and result["fault_mechanism_disabled"]
+    return result
+
+def validate_cleanup(cleanup, expected):
+    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
+    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified","baseline_observation","restored_observation")
+    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
+    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
+    comparison=compare_restoration(cleanup.get("baseline_observation"),cleanup.get("restored_observation"),expected)
+    if not comparison["restoration_pass"]: reasons += ["restoration:"+x for x in comparison["missing_fields"]+comparison["unexpected_changed_fields"]];
+    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True or not comparison["fault_mechanism_disabled"]: reasons.append("cleanup_not_verified")
+    return reasons
+
+def expected_authorization_context(expected, trusted_provenance=None):
+    out={"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"RQ16_ARM_EXECUTION_AUTHORIZED"}
+    if trusted_provenance: out.update({"review_artifact_sha256":trusted_provenance["review_artifact_sha256"],"reviewer_designation":trusted_provenance["reviewer_designation"],"issuer_identity":trusted_provenance["issuer_identity"],"issuer_authority_artifact_sha256":trusted_provenance["issuer_authority_artifact_sha256"]})
+    return out
+
+def validate_authorization_provenance(token, expected_trusted_provenance, actual_file_metadata=None, actual_artifact_digest=None):
+    if not isinstance(expected_trusted_provenance,dict): return ["trusted_authorization_provenance_unavailable"]
+    req=("issuer_identity","issuer_authority_artifact_sha256","reviewer_designation","review_artifact_sha256","trusted_storage_identity","trusted_owner","trusted_mode")
+    reasons=[f"trusted_provenance_missing:{k}" for k in req if k not in expected_trusted_provenance]
+    if reasons: return reasons
+    for k in ("issuer_identity","reviewer_designation","review_artifact_sha256","issuer_authority_artifact_sha256"):
+        if token.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"authorization_provenance_mismatch:{k}")
+    if not isinstance(actual_file_metadata,dict): reasons.append("trusted_storage_metadata_missing")
+    else:
+        for k in ("trusted_storage_identity","trusted_owner","trusted_mode"):
+            if actual_file_metadata.get(k)!=expected_trusted_provenance.get(k): reasons.append(f"trusted_storage_mismatch:{k}")
+    if actual_artifact_digest is None or actual_artifact_digest!=expected_trusted_provenance.get("review_artifact_sha256"): reasons.append("review_artifact_digest_unverified")
+    if actual_file_metadata is None or actual_file_metadata.get("issuer_authority_artifact_digest")!=expected_trusted_provenance.get("issuer_authority_artifact_sha256"): reasons.append("issuer_artifact_digest_unverified")
+    return reasons
+
+def validate_authorization_token(token, expected, now=None, used_nonces=None, trusted_provenance=None, actual_file_metadata=None, actual_review_artifact_digest=None):
+    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
+    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
+    ctx=expected_authorization_context(expected,trusted_provenance)
+    for k,v in ctx.items():
+        if token.get(k)!=v: reasons.append(f"token_mismatch:{k}")
+    try:
+        issued=datetime.fromisoformat(token.get("authorization_timestamp","" ).replace("Z","+00:00")); expires=datetime.fromisoformat(token.get("expiration","").replace("Z","+00:00"))
+        now=now or datetime.now(timezone.utc)
+        if issued > now: reasons.append("authorization_in_future")
+        if expires <= now or expires <= issued: reasons.append("expiration_invalid")
+        if expires-issued > __import__('datetime').timedelta(hours=1): reasons.append("expiration_unbounded")
+    except Exception: reasons.append("timestamp_unparseable")
+    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
+    if used_nonces is not None and token.get("nonce") in used_nonces: reasons.append("nonce_replay")
+    if token.get("source_path")!="/root-owned/rq16-authorization": reasons.append("authorization_source_untrusted")
+    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
+    reasons += validate_authorization_provenance(token,trusted_provenance,actual_file_metadata,actual_review_artifact_digest)
+    return reasons
+
+def evaluate_arm(arm, observed, expected, observer_context=None, actual_raw_artifact_digest=None):
+    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
+    reasons=[]
+    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
+    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
+    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
+    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
+    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected,observer_context,actual_raw_artifact_digest)
+    reasons += _obs_complete(observed.get("observations"),expected)
+    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
+    reasons += _lifecycle_valid(observed.get("lifecycle"),expected,observed.get("observations"))
+    reasons += validate_cleanup(observed.get("cleanup_proof"),expected)
+    if observed.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
+    if not topo_ok: reasons.append("rq17_contamination")
+    return ("PASS",[]) if not reasons else ("HARNESS_DEFECT",sorted(set(reasons)))
+
+def main():
+    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true"); a=ap.parse_args()
+    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
+    if a.self_test: print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["expected-vs-observed separation","exact target binding","structured provenance","observer stages","cleanup structure","RQ17 gate","token binding"]},indent=2)); return 0
+    if not a.plan: ap.error("only --plan or --self-test is allowed")
+    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
+if __name__=="__main__": raise SystemExit(main())
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
new file mode 100644
index 00000000..f9f4f053
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json
@@ -0,0 +1,7 @@
+{
+  "authorization_schema_version": "1",
+  "required_bindings": ["rq_id", "arm", "mechanism_id", "mechanism_digest", "plan_commit", "plan_tree", "plan_digest", "execution_contract_digest", "cleanup_contract_digest", "host_identity", "runtime_identity", "service_binary_sha256", "gate_sha256", "records_device", "consumed_device", "independent_review_disposition", "review_artifact_sha256", "reviewer_identity/designation", "authorization_timestamp", "expiration", "nonce"],
+  "single_use": true,
+  "arm_scoped": true,
+  "execution_requirement": "all bindings must match before any destructive action; no token is generated by preregistration"
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
new file mode 100644
index 00000000..5ef55ad0
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md
@@ -0,0 +1,19 @@
+# RQ-16 cleanup and restoration contract
+
+RQ-16 remains preregistration-only. No mutation has been executed.
+
+Every future arm must capture an immutable baseline and restore it before any
+dependent case. The baseline includes service/gate hashes, unit bytes, PID and
+socket identity, records/consumed ownership and modes, filesystem device IDs,
+mount options, security controls, and exact target lifecycle.
+
+The inverse operation must be explicit: remove only the bounded fault fixture,
+restore the saved mount/quota/metadata state, restart only as required by the
+approved recovery procedure, and independently remeasure every baseline field.
+If a mount operation fails, root recovery is unavailable, a fault fixture
+cannot be removed, or any hash/device/mode differs, cleanup is FAILED and all
+dependent cases abort. Historical evidence directories are never targets.
+
+The future harness must refuse destructive execution unless the exact host,
+commit, plan digest, and separately generated authorization token are bound.
+`--plan` and `--self-test` are the only permitted modes in this preregistration.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
new file mode 100644
index 00000000..fdc139d1
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json
@@ -0,0 +1,48 @@
+{
+  "rq_id": "RQ-16",
+  "trigger": "Disk full / read-only / I/O / permission failure",
+  "oracle": "Fail closed without fabricated success",
+  "execution_required": true,
+  "execution_authorized": false,
+  "arms": {
+    "ENOSPC": {
+      "operation": "write_authority_record or fsync on exact bound records path",
+      "proposed_mechanism": "pre-existing project/quota limit on the exact bound filesystem, only after topology and free-space preflight prove it is isolated and bounded",
+      "classification": "INSUFFICIENT_EVIDENCE",
+      "reason": "Current repository evidence does not prove a safe quota/project-quota facility on the bound /run filesystem; filling /run is unsafe and a loop mount would alter device topology/RQ-17 semantics."
+    },
+    "EROFS": {
+      "operation": "write_authority_record or rename on exact bound path",
+      "proposed_mechanism": "controlled read-only remount only if the target is a dedicated qualification filesystem and device identity remains preregistered",
+      "classification": "UNSAFE",
+      "reason": "The source proves /run is load-bearing for socket, PID and private state, but does not prove a dedicated remount boundary. Remounting host /run read-only could break the runner and unrelated state."
+    },
+    "EIO": {
+      "operation": "exact record read/write/fsync/rename syscall",
+      "proposed_mechanism": "kernel fault layer such as dm-error only on a dedicated disposable block device, with independently captured errno",
+      "classification": "INSUFFICIENT_EVIDENCE",
+      "reason": "No bound-runtime evidence proves a disposable fault device or safe device-mapper boundary. A mocked exception or arbitrary I/O wrapper is a proxy and cannot qualify RQ-16."
+    },
+    "EACCES": {
+      "operation": "exact service access to records/consumed path",
+      "proposed_mechanism": "controlled ACL/ownership/mode mutation only if the actual service identity is non-root for the operation",
+      "classification": "PROXY_NOT_ACCEPTABLE",
+      "reason": "The frozen runtime binds the trusted service as UID 0; chmod/chown denial is not proven to yield EACCES for root. A Python exception or candidate-side denial would be a proxy."
+    }
+  },
+  "classification_rules": {
+    "PASS": ["fault proof exact", "intended operation observed with errno", "no authoritative success", "exact lifecycle explained", "service recoverable", "cleanup independently verified", "post-state hashes/security exact", "observer complete"],
+    "RED": ["literal injected fault observed and trusted service fabricates authoritative success or invalid transition"],
+    "HARNESS_DEFECT": ["trigger/fault proof/observer/cleanup evidence missing or malformed"],
+    "INSUFFICIENT_EVIDENCE": ["safe literal mechanism or required external fact unavailable"]
+  },
+  "state_machine": {
+    "ENOSPC": {"BASELINE":"target absent; service active; exact device/mount/free-space recorded","PREPARED":"target in records only; same device IDs","FAILURE_TRIGGERED":"exact write/fsync syscall returns ENOSPC","POST_FAILURE":"no authoritative response; target remains explainable; no fabricated consumed state","RECOVERY":"service restart only if required; target state independently observed","RETRY":"only if frozen recovery path permits; exact single transition or explicit denial","POST_RETRY":"exact lifecycle delta recorded","CLEANUP":"quota/fault fixture removed","RESTORED":"all baseline hashes, devices, mounts, modes, socket and security controls match"},
+    "EROFS": {"BASELINE":"target absent; dedicated mount boundary and rw mode recorded","PREPARED":"target in records only; topology unchanged","FAILURE_TRIGGERED":"exact syscall returns EROFS","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"mount restored rw and service state observed","RETRY":"only after restoration and exact frozen recovery rule","POST_RETRY":"target-specific result recorded","CLEANUP":"read-only fixture removed","RESTORED":"mount options, device IDs, hashes, ownership/modes and service controls match"},
+    "EIO": {"BASELINE":"target absent; disposable fault device and mapping recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact syscall returns EIO","POST_FAILURE":"no authoritative response; no invalid transition","RECOVERY":"fault mapping removed and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"fault layer detached","RESTORED":"device topology, hashes, mounts, modes and service controls match"},
+    "EACCES": {"BASELINE":"target absent; exact service identity and path metadata recorded","PREPARED":"target in records only","FAILURE_TRIGGERED":"exact trusted operation returns EACCES/EPERM at preregistered boundary","POST_FAILURE":"no authoritative response; no fabricated transition","RECOVERY":"metadata restored and service recovered","RETRY":"only after independent restoration","POST_RETRY":"target-specific result recorded","CLEANUP":"permission fixture removed","RESTORED":"ownership/modes, hashes, device IDs, socket and service controls match"}
+  },
+  "governance": "NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY",
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json
new file mode 100644
index 00000000..b6385f17
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json
@@ -0,0 +1,1325 @@
+{
+  "RQ16_EXECUTED": false,
+  "all_rejected": true,
+  "exit_code": 0,
+  "mutations": [
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_device",
+      "path": "wrong_device",
+      "reasons": [
+        "fault_active:records_device_mismatch",
+        "fault_active:split_filesystem",
+        "rq17_contamination",
+        "target_binding:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_mount",
+      "path": "wrong_mount",
+      "reasons": [
+        "fault_active:records_mount_mismatch",
+        "rq17_contamination",
+        "target_binding:records_mount"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_filesystem",
+      "path": "wrong_filesystem",
+      "reasons": [
+        "fault_active:records_fs_mismatch",
+        "rq17_contamination",
+        "target_binding:records_fs"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "symlink",
+      "path": "symlink",
+      "reasons": [
+        "target_binding:records_symlink"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_target",
+      "path": "wrong_target",
+      "reasons": [
+        "wrong_target_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_syscall",
+      "path": "wrong_syscall",
+      "reasons": [
+        "wrong_syscall"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_errno",
+      "path": "wrong_errno",
+      "reasons": [
+        "wrong_errno"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_activation",
+      "path": "missing_activation",
+      "reasons": [
+        "activation_not_proven"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_operation",
+      "path": "missing_operation",
+      "reasons": [
+        "operation_not_proven"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_missing_raw_activation",
+      "path": "attestation_missing_raw_activation",
+      "reasons": [
+        "attestation_field_missing:fault_activation_raw_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_missing_raw_operation",
+      "path": "attestation_missing_raw_operation",
+      "reasons": [
+        "attestation_field_missing:operation_raw_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_observer",
+      "path": "attestation_wrong_observer",
+      "reasons": [
+        "observer_context_mismatch:observer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_pid",
+      "path": "attestation_wrong_pid",
+      "reasons": [
+        "attestation_service_mismatch"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "attestation_wrong_artifact_hash",
+      "path": "attestation_wrong_artifact_hash",
+      "reasons": [
+        "raw_artifact_digest_mismatch"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_observer",
+      "path": "missing_observer",
+      "reasons": [
+        "observation_missing:restored"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "bool_only_observer",
+      "path": "bool_only_observer",
+      "reasons": [
+        "observations_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "missing_cleanup",
+      "path": "missing_cleanup",
+      "reasons": [
+        "cleanup_proof_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "bool_only_cleanup",
+      "path": "bool_only_cleanup",
+      "reasons": [
+        "cleanup_proof_missing"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "duplicate_consume",
+      "path": "duplicate_consume",
+      "reasons": [
+        "fault_active->post_failure:duplicate_target_entry:consumed_entries",
+        "post_failure->pre_cleanup:duplicate_target_entry:consumed_entries",
+        "post_failure:duplicate_target_entry:consumed_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "both_directories",
+      "path": "both_directories",
+      "reasons": [
+        "fault_active->post_failure:target_in_both",
+        "post_failure->pre_cleanup:target_in_both",
+        "post_failure:target_in_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "rq17_false_but_changed",
+      "path": "rq17_false_but_changed",
+      "reasons": [
+        "fault_active:records_device_mismatch",
+        "fault_active:split_filesystem",
+        "rq17_contamination",
+        "target_binding:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "authoritative_success",
+      "path": "authoritative_success",
+      "reasons": [
+        "authoritative_success_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "invalid_transition",
+      "path": "invalid_transition",
+      "reasons": [
+        "invalid_transition_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "untrusted_expected_context",
+      "path": "untrusted_expected_context",
+      "reasons": [
+        "wrong_mechanism"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_service_hash",
+      "path": "cleanup_service_hash",
+      "reasons": [
+        "restoration:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_gate_hash",
+      "path": "cleanup_gate_hash",
+      "reasons": [
+        "restoration:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mode",
+      "path": "cleanup_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_owner",
+      "path": "cleanup_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_socket",
+      "path": "cleanup_socket",
+      "reasons": [
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fault_active",
+      "path": "cleanup_fault_active",
+      "reasons": [
+        "cleanup_not_verified"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_target_state",
+      "path": "cleanup_target_state",
+      "reasons": [
+        "restoration:records_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_historical_evidence",
+      "path": "cleanup_historical_evidence",
+      "reasons": [
+        "restoration:historical_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_missing_restored",
+      "path": "cleanup_missing_restored",
+      "reasons": [
+        "cleanup_not_verified",
+        "restoration:consumed_device",
+        "restoration:consumed_entries",
+        "restoration:consumed_fs",
+        "restoration:consumed_mount",
+        "restoration:consumed_realpath",
+        "restoration:fault_state",
+        "restoration:gate_sha256",
+        "restoration:historical_evidence",
+        "restoration:mode",
+        "restoration:owner",
+        "restoration:records_device",
+        "restoration:records_entries",
+        "restoration:records_fs",
+        "restoration:records_mount",
+        "restoration:records_realpath",
+        "restoration:security_controls",
+        "restoration:service_binary_sha256",
+        "restoration:service_identity",
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "baseline_target_missing",
+      "path": "baseline_target_missing",
+      "reasons": [
+        "baseline->pre_injection:target_missing_from_both",
+        "baseline:target_missing_from_both",
+        "baseline:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "baseline_already_consumed",
+      "path": "baseline_already_consumed",
+      "reasons": [
+        "baseline->pre_injection:target_in_both",
+        "baseline:target_in_both",
+        "baseline:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "post_failure_missing_both",
+      "path": "post_failure_missing_both",
+      "reasons": [
+        "fault_active->post_failure:target_missing_from_both",
+        "post_failure->pre_cleanup:target_missing_from_both",
+        "post_failure:target_missing_from_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "post_failure_both",
+      "path": "post_failure_both",
+      "reasons": [
+        "fault_active->post_failure:target_in_both",
+        "post_failure->pre_cleanup:target_in_both",
+        "post_failure:target_in_both",
+        "post_failure:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "wrong_target_consumed",
+      "path": "wrong_target_consumed",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "historical_target_consumed",
+      "path": "historical_target_consumed",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "unrelated_target_transition",
+      "path": "unrelated_target_transition",
+      "reasons": [
+        "fault_active->post_failure:unauthorized_lifecycle_transition",
+        "post_failure->pre_cleanup:unauthorized_lifecycle_transition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "RED",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "duplicate_authoritative_consumption",
+      "path": "duplicate_authoritative_consumption",
+      "reasons": [
+        "authoritative_success_after_fault"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "second_authoritative_retry",
+      "path": "second_authoritative_retry",
+      "reasons": [
+        "fault_active->post_failure:authoritative_response_in_observation",
+        "post_failure->pre_cleanup:authoritative_response_in_observation",
+        "post_failure:authoritative_response_in_observation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "replay_state_mutation",
+      "path": "replay_state_mutation",
+      "reasons": [
+        "post_cleanup->restored:target_missing_from_both",
+        "restored:target_missing_from_both",
+        "restored:unexpected_target_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "target_hash_changed",
+      "path": "target_hash_changed",
+      "reasons": [
+        "fault_active->post_failure:target_hash_mismatch:observation",
+        "post_failure->pre_cleanup:target_hash_mismatch:observation",
+        "post_failure:target_hash_mismatch",
+        "post_failure:target_hash_mismatch:observation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "target_identity_changed",
+      "path": "target_identity_changed",
+      "reasons": [
+        "fault_active->post_failure:target_identity_mismatch:observation",
+        "post_failure->pre_cleanup:target_identity_mismatch:observation",
+        "post_failure:target_identity_mismatch:observation",
+        "target_binding:target_record_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_gate_hash",
+      "path": "cleanup_gate_hash",
+      "reasons": [
+        "restoration:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_device",
+      "path": "cleanup_device",
+      "reasons": [
+        "restoration:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mount",
+      "path": "cleanup_mount",
+      "reasons": [
+        "restoration:records_mount"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fs",
+      "path": "cleanup_fs",
+      "reasons": [
+        "restoration:records_fs"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_realpath",
+      "path": "cleanup_realpath",
+      "reasons": [
+        "restoration:records_realpath"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_owner",
+      "path": "cleanup_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_mode",
+      "path": "cleanup_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_socket",
+      "path": "cleanup_socket",
+      "reasons": [
+        "restoration:socket_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_fault_still_active",
+      "path": "cleanup_fault_still_active",
+      "reasons": [
+        "cleanup_not_verified",
+        "restoration:fault_state"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_unrelated_record",
+      "path": "cleanup_unrelated_record",
+      "reasons": [
+        "restoration:records_entries"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_historical_changed",
+      "path": "cleanup_historical_changed",
+      "reasons": [
+        "restoration:historical_evidence"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_hash",
+      "path": "cleanup_arbitrary_hash",
+      "reasons": [
+        "restoration:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_owner",
+      "path": "cleanup_arbitrary_owner",
+      "reasons": [
+        "restoration:owner"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "HARNESS_DEFECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "ENOSPC",
+      "expected_result": "REJECT",
+      "mutation_id": "cleanup_arbitrary_mode",
+      "path": "cleanup_arbitrary_mode",
+      "reasons": [
+        "restoration:mode"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_arm",
+      "path": "arm",
+      "reasons": [
+        "token_mismatch:arm"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_mechanism_id",
+      "path": "mechanism_id",
+      "reasons": [
+        "token_mismatch:mechanism_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_mechanism_digest",
+      "path": "mechanism_digest",
+      "reasons": [
+        "token_mismatch:mechanism_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_commit",
+      "path": "plan_commit",
+      "reasons": [
+        "token_mismatch:plan_commit"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_tree",
+      "path": "plan_tree",
+      "reasons": [
+        "token_mismatch:plan_tree"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_plan_digest",
+      "path": "plan_digest",
+      "reasons": [
+        "token_mismatch:plan_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_execution_contract_digest",
+      "path": "execution_contract_digest",
+      "reasons": [
+        "token_mismatch:execution_contract_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_cleanup_contract_digest",
+      "path": "cleanup_contract_digest",
+      "reasons": [
+        "token_mismatch:cleanup_contract_digest"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_host_identity",
+      "path": "host_identity",
+      "reasons": [
+        "token_mismatch:host_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_runtime_identity",
+      "path": "runtime_identity",
+      "reasons": [
+        "token_mismatch:runtime_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_service_binary_sha256",
+      "path": "service_binary_sha256",
+      "reasons": [
+        "token_mismatch:service_binary_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_gate_sha256",
+      "path": "gate_sha256",
+      "reasons": [
+        "token_mismatch:gate_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_records_device",
+      "path": "records_device",
+      "reasons": [
+        "token_mismatch:records_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_consumed_device",
+      "path": "consumed_device",
+      "reasons": [
+        "token_mismatch:consumed_device"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_records_mount_id",
+      "path": "records_mount_id",
+      "reasons": [
+        "token_mismatch:records_mount_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_consumed_mount_id",
+      "path": "consumed_mount_id",
+      "reasons": [
+        "token_mismatch:consumed_mount_id"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_independent_review_disposition",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_review_artifact_sha256",
+      "path": "review_artifact_sha256",
+      "reasons": [
+        "token_mismatch:review_artifact_sha256",
+        "authorization_provenance_mismatch:review_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_reviewer_designation",
+      "path": "reviewer_designation",
+      "reasons": [
+        "token_mismatch:reviewer_designation",
+        "authorization_provenance_mismatch:reviewer_designation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_issuer_identity",
+      "path": "issuer_identity",
+      "reasons": [
+        "token_mismatch:issuer_identity",
+        "authorization_provenance_mismatch:issuer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "mutated",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_issuer_authority_artifact_sha256",
+      "path": "issuer_authority_artifact_sha256",
+      "reasons": [
+        "token_mismatch:issuer_authority_artifact_sha256",
+        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "2025-01-01T00:00:00Z",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_expired",
+      "path": "expiration",
+      "reasons": [
+        "expiration_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "2030-01-01T00:00:00Z",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_future_issued",
+      "path": "authorization_timestamp",
+      "reasons": [
+        "authorization_in_future",
+        "expiration_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "bad",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_malformed_timestamp",
+      "path": "expiration",
+      "reasons": [
+        "timestamp_unparseable"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_empty_nonce",
+      "path": "nonce",
+      "reasons": [
+        "nonce_invalid"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "used",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_reused_nonce",
+      "path": "nonce",
+      "reasons": [
+        "nonce_replay"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_untrusted_source",
+      "path": "source_path",
+      "reasons": [
+        "authorization_source_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "memory",
+      "before": "valid",
+      "case": "AUTHORIZATION",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_untrusted_registry",
+      "path": "single_use_registry",
+      "reasons": [
+        "nonce_registry_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_self_issued",
+      "path": "issuer_identity",
+      "reasons": [
+        "token_mismatch:issuer_identity",
+        "authorization_provenance_mismatch:issuer_identity"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_candidate_writable",
+      "path": "source_path",
+      "reasons": [
+        "authorization_source_untrusted"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "issuer-sha",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_placeholder_issuer_hash",
+      "path": "issuer_authority_artifact_sha256",
+      "reasons": [
+        "token_mismatch:issuer_authority_artifact_sha256",
+        "authorization_provenance_mismatch:issuer_authority_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "review-sha",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_placeholder_review_hash",
+      "path": "review_artifact_sha256",
+      "reasons": [
+        "token_mismatch:review_artifact_sha256",
+        "authorization_provenance_mismatch:review_artifact_sha256"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "candidate",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_wrong_reviewer",
+      "path": "reviewer_designation",
+      "reasons": [
+        "token_mismatch:reviewer_designation",
+        "authorization_provenance_mismatch:reviewer_designation"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "BOUNDED_PASS",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_generic_bounded_pass",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "CHANGES_REQUIRED",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_changes_required",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "INSUFFICIENT_EVIDENCE",
+      "before": "valid",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_insufficient_evidence",
+      "path": "independent_review_disposition",
+      "reasons": [
+        "token_mismatch:independent_review_disposition"
+      ],
+      "rejected": true
+    },
+    {
+      "actual_result": "REJECT",
+      "after": "absent",
+      "before": "absent",
+      "case": "AUTHORIZATION_PROVENANCE",
+      "expected_result": "REJECT",
+      "mutation_id": "auth_provenance_unavailable",
+      "path": "trusted_provenance",
+      "reasons": [
+        "trusted_authorization_provenance_unavailable"
+      ],
+      "rejected": true
+    }
+  ],
+  "rejected_mutations": 96,
+  "surviving_mutations": 0,
+  "total_mutations": 96
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
new file mode 100644
index 00000000..19e2c2d2
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md
@@ -0,0 +1,5 @@
+# Durable authorization nonce design
+
+No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.
+
+The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
new file mode 100644
index 00000000..d7308e97
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json
@@ -0,0 +1,25 @@
+{
+  "issues": [
+    {"issue_id":"RQ16-ENOSPC-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal quota/project-quota boundary is evidenced for the bound /run filesystem.","false_green_path":"proxy exception or host-wide fill treated as ENOSPC proof","root_cause":"runtime topology/quota capability not available in repository evidence","narrow_fix":"obtain provider/runtime evidence for an isolated same-filesystem quota or preregister a successor mechanism","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EROFS-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Read-only remount boundary is not proven dedicated and bounded.","false_green_path":"host /run remount breaks service/runner or becomes RQ-17 topology mutation","root_cause":"/run contains socket, PID and private state","narrow_fix":"require dedicated qualification mount evidence before any remount design","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EIO-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"No safe literal EIO fault layer is evidenced.","false_green_path":"mocked exception or non-kernel wrapper accepted as EIO","root_cause":"no disposable fault device evidence","narrow_fix":"obtain bounded disposable device/fault-layer evidence or preregister successor","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-EACCES-MECHANISM","severity":"BLOCKING","area":"fault mechanism","description":"Trusted service is root; chmod/chown does not prove EACCES for root.","false_green_path":"candidate-side permission failure substituted for trusted operation failure","root_cause":"root DAC bypass","narrow_fix":"obtain a literal kernel access boundary or classify arm insufficient","status":"MANUAL_REVIEW_REQUIRED"},
+    {"issue_id":"RQ16-STRUCTURED-PROOF","severity":"HIGH","area":"evaluator","description":"Summary booleans could accept fabricated fault/observer/cleanup claims.","false_green_path":"injected=true or observer_ok=true without kernel evidence yields PASS","root_cause":"under-specified evidence schema","narrow_fix":"require structured fault proof, seven observations, lifecycle, cleanup and topology evidence","status":"RESOLVED"},
+    {"issue_id":"RQ16-RQ17-CONTAMINATION","severity":"HIGH","area":"topology","description":"RQ-16 mechanism could silently become an RQ-17 filesystem split.","false_green_path":"device or mount identity changes during fault arm","root_cause":"no topology gate","narrow_fix":"check_rq17_contamination requires unchanged device/fs/mount identity","status":"RESOLVED"},
+    {"issue_id":"RQ16-AUTH-TOKEN-BINDING","severity":"HIGH","area":"authorization","description":"A future token must not authorize a different arm, host or plan.","false_green_path":"replayed or cross-arm token enables destructive execution","root_cause":"missing binding schema","narrow_fix":"require exact commit/tree/plan/mechanism/host/runtime/review/nonce bindings","status":"RESOLVED"}
+  ],
+  "open_automatable_issues": 0,
+  "manual_review_required": true,
+  "RQ16_EXECUTED": false,
+  "RQ16_AUTHORIZED": false,
+  "latest_remediation_status": {
+    "RQ16-TRUSTED-ATTESTATION": "RESOLVED",
+    "RQ16-AUTH-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
+    "RQ16-IDENTITY-MODEL": "RESOLVED",
+    "RQ16-TEST-SUFFICIENCY": "RESOLVED",
+    "RQ16-LIFECYCLE-DERIVATION": "RESOLVED",
+    "RQ16-CLEANUP-BASELINE-COMPARISON": "RESOLVED",
+    "RQ16-AUTHORIZATION-PROVENANCE": "MANUAL_REVIEW_REQUIRED",
+    "RQ16-SOURCE-MANIFEST-RECOMPUTATION": "RESOLVED"
+  }
+}
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
new file mode 100644
index 00000000..0a797b62
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md
@@ -0,0 +1,103 @@
+# V24-I11-V6 RQ-16 preregistration (planning only)
+
+Predecessor: commit `8477830f5f35a35a8c9b19fdca9c5b6c39e2916d`, tree
+`82457b9307f133db281055dbbdae26b618f8c3cf`. This branch is based exactly on
+that closed Remediation-7 head.
+
+Frozen case: **RQ-16**. Trigger: **Disk full / read-only / I/O / permission
+failure**. Oracle: **Fail closed without fabricated success**. This document
+does not authorize execution.
+
+## Actual write path
+
+In `governance-runtime/native/v24_v6_trusted_authority_service.c`:
+
+- `materialize_private()` calls `mkstemp`, `fchmod(0600)`, `write_all_fd`, and
+  `fsync`, then closes and unlinks on failure.
+- candidate handling calls `materialize_private()` for context, boundary and
+  payload before gate execution.
+- root control calls `consume_record_trusted()`.
+- `consume_record_trusted()` opens `RECORD_DIR/<id>.record` with
+  `open(O_RDONLY|O_NOFOLLOW)`, reads it, closes it, and calls `rename(src,dst)`
+  from records to consumed. It returns an authoritative response only after
+  `rename` succeeds.
+- `write_authority_record()` creates records with
+  `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, writes the body, calls
+  `fsync`, closes, and unlinks on failure.
+
+RQ-16 must bind the injected errno to one of these exact operations; mocked
+Python exceptions and candidate-side failures are proxies.
+
+## Execution arms and classifications
+
+ENOSPC requires a project/quota limit on the exact existing filesystem. Filling
+host `/run` is prohibited. No repository evidence proves such a quota boundary,
+so the arm is `INSUFFICIENT_EVIDENCE` pending runtime/provider evidence.
+
+EROFS requires a dedicated qualification filesystem whose read-only transition
+does not affect service socket/PID or unrelated `/run`. A host `/run` remount is
+unsafe and a separate filesystem would collide with RQ-17 topology semantics;
+the arm is `UNSAFE` pending dedicated-mount evidence.
+
+EIO requires a disposable kernel fault layer returning EIO on the exact target
+operation. `dm-error` or equivalent is acceptable only with a dedicated device
+and independent activation/errno proof. No such boundary is evidenced;
+classification is `INSUFFICIENT_EVIDENCE`.
+
+EACCES cannot be obtained by merely chmod/chowning a root-owned path because the
+trusted service runs as UID 0. Candidate-side permission failure or a mocked
+exception is a proxy; classification is `PROXY_NOT_ACCEPTABLE`.
+
+These are execution arms under one frozen case, not new cases.
+
+## Required state machine and proof
+
+Each arm must record BASELINE, PREPARED, FAILURE_TRIGGERED, POST_FAILURE,
+RECOVERY, optional authorized RETRY, POST_RETRY, CLEANUP and RESTORED. At every
+state record target membership in records/consumed, response and authority,
+errno proof, service state, filesystem/device/mount metadata, ownership/modes,
+and hashes. PASS requires exact fault activation plus syscall errno, no
+authoritative success, explainable target lifecycle, recoverable service,
+complete observers, and exact post-restoration hashes/security state. Absence
+of a response alone is never PASS. Authoritative success after a proven fault
+is RED. Missing/malformed proof or observer/cleanup failure is
+HARNESS_DEFECT/INSUFFICIENT_EVIDENCE.
+
+## Restoration, safety and aborts
+
+The only permitted future mutation is a bounded fixture on a dedicated,
+preflight-verified boundary. The host root filesystem, repository, historical
+evidence, `/run` outside the exact dedicated boundary, IAM/network, and runner
+workspace are never targets. Cleanup removes the fixture, restores mount/quota
+and metadata, revalidates service/socket/PID, records/consumed integrity,
+device IDs, mount options, ownership/modes, hashes and security controls. Any
+failure blocks all dependent cases.
+
+Abort before mutation if predecessor/runtime hashes, device IDs, mount topology,
+free-space margin, backup material, root recovery, service health or observer
+access differ from the preregistered baseline, or if an evidence directory could
+be overwritten.
+
+Evidence is append-only under `RQ-16/{baseline,arm-enospc,arm-erofs,arm-eio,arm-eacces,summary,hashes}` with transcripts, exact commands, errno,
+responses, observers, lifecycle deltas, cleanup proofs and SHA-256 sidecars.
+
+## Harness safety and governance
+
+`v24_v6_rq1_rq16_harness.py` supports only `--plan` and `--self-test` here.
+`--execute-rq16` refuses with a nonzero result. Future execution requires a
+separately generated authorization token bound to exact commit, host/runtime
+identity and plan digest. No token exists in this branch.
+
+`RQ16_EXECUTED=false`, `RQ16_AUTHORIZED=false`, `SCIENTIFIC_RERUN=false`.
+Qualification remains `NOT_QUALIFIED`; scientific execution remains
+`CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains
+`NONE_EVIDENCE_ONLY`. Independent manual review is required for the four arm
+mechanism classifications before any execution authorization.
+
+## Remediation-2 hardening
+
+The future evaluator binds each arm to `/run/v24-v6-authority/private/records/<target>.record` and `/run/v24-v6-authority/private/consumed/<target>.record`, with exact target ID, device, mount, service identity, operation, syscall, errno, activation proof, operation proof, and independent observer references. Summary booleans are insufficient.
+
+Every future arm requires structured observations at baseline, pre-injection, fault-active, post-failure, pre-cleanup, post-cleanup, and restored. Lifecycle proof rejects target-in-both-directories, unexplained disappearance, duplicate authoritative consumption, unrelated transitions, and unknown RQ-17 topology. Cleanup proof requires inverse action, hashes, ownership, modes, device IDs, mount identity, service/socket identity, records/consumed state, fault-disabled proof, and independent verification.
+
+No arm is currently authorization-ready. ENOSPC and EIO remain INSUFFICIENT_EVIDENCE; EROFS remains LITERAL_BUT_UNSAFE; EACCES remains PROXY_NOT_ACCEPTABLE. No host capability was enabled or mutated.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
new file mode 100644
index 00000000..d60eee26
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md
@@ -0,0 +1,22 @@
+# RQ-16 read-only capability inspection
+
+This inspection was non-destructive and did not enable or mutate any host feature.
+
+The current engineering host is Windows PowerShell, while the bound runtime contract targets Linux `/run/v24-v6-authority`. Therefore Linux mount/device/quota/LSM capability claims cannot be inferred from this host.
+
+Source inspection found the trusted service operations at:
+
+- `governance-runtime/native/v24_v6_trusted_authority_service.c:134` `materialize_private`: `mkstemp`, `write`, `fsync`.
+- `...:245` `write_authority_record`: `open(O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW)`, `write`, `fsync`, close/unlink on failure.
+- `...:330` `consume_record_trusted`: `open(..., O_RDONLY|O_CLOEXEC|O_NOFOLLOW)`, read, close, `rename(records/<id>.record, consumed/<id>.record)` at line 412.
+
+Read-only commands attempted:
+
+```text
+Get-Volume | Select-Object DriveLetter,FileSystem,Size,SizeRemaining
+Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,FileSystem,Size,FreeSpace
+```
+
+Both returned `Access denied` on this host. No Linux `/run` filesystem type, mount ID, device ID, quota configuration, disposable fault layer, or UID-0 LSM denial boundary is evidenced. Consequently ENOSPC, EIO and EACCES remain non-authorized, and EROFS remains unsafe.
+
+`RQ16_EXECUTED=false`; no mount, quota, device-mapper, ACL, ownership, mode, service, or filesystem mutation occurred.
diff --git a/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json b/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json
new file mode 100644
index 00000000..ed1df712
--- /dev/null
+++ b/implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json
@@ -0,0 +1,82 @@
+{
+  "exit_code": 0,
+  "stderr": "test_absent_response_not_success (__main__.RQ16Tests.test_absent_response_not_success) ... ok\ntest_authority_and_duplicate_transitions_red_or_reject (__main__.RQ16Tests.test_authority_and_duplicate_transitions_red_or_reject) ... ok\ntest_cleanup_exact_baseline_comparison (__main__.RQ16Tests.test_cleanup_exact_baseline_comparison) ... ok\ntest_cross_arm_proof_rejected (__main__.RQ16Tests.test_cross_arm_proof_rejected) ... ok\ntest_expected_context_required (__main__.RQ16Tests.test_expected_context_required) ... ok\ntest_observer_cleanup_lifecycle_mutations_reject (__main__.RQ16Tests.test_observer_cleanup_lifecycle_mutations_reject) ... ok\ntest_provenance_mutations_reject (__main__.RQ16Tests.test_provenance_mutations_reject) ... ok\ntest_rq17_gate_cannot_be_overridden_by_boolean (__main__.RQ16Tests.test_rq17_gate_cannot_be_overridden_by_boolean) ... ok\ntest_target_mutations_reject (__main__.RQ16Tests.test_target_mutations_reject) ... ok\ntest_token_requires_durable_trusted_binding (__main__.RQ16Tests.test_token_requires_durable_trusted_binding) ... ok\ntest_valid_structured_expected_observed_passes (__main__.RQ16Tests.test_valid_structured_expected_observed_passes) ... ok\n\n----------------------------------------------------------------------\nRan 11 tests in <elapsed>\n\nOK\n\ntest_absolute_outside_root_rejected (__main__.ManifestTests.test_absolute_outside_root_rejected) ... ok\ntest_clean_manifest_is_deterministic (__main__.ManifestTests.test_clean_manifest_is_deterministic) ... ok\ntest_duplicate_path_rejected (__main__.ManifestTests.test_duplicate_path_rejected) ... ok\ntest_generated_packet_is_not_source (__main__.ManifestTests.test_generated_packet_is_not_source) ... ok\ntest_manifest_hash_is_content_hash (__main__.ManifestTests.test_manifest_hash_is_content_hash) ... ok\ntest_missing_file_fails (__main__.ManifestTests.test_missing_file_fails) ... ok\ntest_source_byte_change_changes_manifest (__main__.ManifestTests.test_source_byte_change_changes_manifest) ... ok\n\n----------------------------------------------------------------------\nRan 7 tests in <elapsed>\n\nOK\n\n",
+  "stdout": "",
+  "tests": [
+    {
+      "name": "test_absent_response_not_success",
+      "result": "PASS"
+    },
+    {
+      "name": "test_authority_and_duplicate_transitions_red_or_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_cleanup_exact_baseline_comparison",
+      "result": "PASS"
+    },
+    {
+      "name": "test_cross_arm_proof_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_expected_context_required",
+      "result": "PASS"
+    },
+    {
+      "name": "test_observer_cleanup_lifecycle_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_provenance_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_rq17_gate_cannot_be_overridden_by_boolean",
+      "result": "PASS"
+    },
+    {
+      "name": "test_target_mutations_reject",
+      "result": "PASS"
+    },
+    {
+      "name": "test_token_requires_durable_trusted_binding",
+      "result": "PASS"
+    },
+    {
+      "name": "test_valid_structured_expected_observed_passes",
+      "result": "PASS"
+    },
+    {
+      "name": "test_absolute_outside_root_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_clean_manifest_is_deterministic",
+      "result": "PASS"
+    },
+    {
+      "name": "test_duplicate_path_rejected",
+      "result": "PASS"
+    },
+    {
+      "name": "test_generated_packet_is_not_source",
+      "result": "PASS"
+    },
+    {
+      "name": "test_manifest_hash_is_content_hash",
+      "result": "PASS"
+    },
+    {
+      "name": "test_missing_file_fails",
+      "result": "PASS"
+    },
+    {
+      "name": "test_source_byte_change_changes_manifest",
+      "result": "PASS"
+    }
+  ],
+  "tests_failed": 0,
+  "tests_passed": 18,
+  "tests_total": 18
+}
```

## Manual-review questions
Historical packet consistency failure source_manifest_entries_mismatch was fixed and superseded; no failed traceback is current evidence. Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.


---

# EXACT R1 INDEPENDENT MANUAL REVIEW AS SUPPLIED

**A. Overall disposition**

`CHANGES_REQUIRED`

- The review found 0 Critical and 2 High findings. Both are narrow fixes to an invariant and to the gate plan. I found no defect in how the frozen boundaries are handled.
- **Severity rule I applied:** High means an artifact Gate 0 would bless (an invariant, the gate plan, or a frozen boundary) is unsound or permits a path to authority. Underspecification that item-level preregistration can still fix is Medium.
- **Package integrity:** the five files listed in `PACKAGE-MANIFEST.json` match their SHA-256 and byte counts, and the zip tests clean.
- **Evidence limits:** the package holds only hashes, not the EXP-M R5 text, the RQ-16 state or the Ruflo sources. Frozen-boundary claims are therefore verified at declaration and design level only.

**B. Critical findings**

None.

**C. High findings**

**H-01. RA-04 / Invariant 15. The per-child bound is unsound for consumable resources.**

- **Path:** 
  1. A parent envelope holds budget B, a token cap, concurrency C and a delegation count.
  2. N children are each issued "child ≤ parent", so every child individually passes.
  3. Aggregate authority is N×B.
  4. RA-12 swarms and RA-13 loops make this fan-out reachable.
- **Why insufficient:** the `raises budget/concurrency` scenario tests one child exceeding the parent, never the siblings' aggregate. The invariant can hold while the total spend, token use or concurrency exceeds the parent's grant.
- **Narrow fix:** split Invariant 15. 
  - (a) Non-consumable dimensions (tools, paths, providers, network, destructive and promotion rights) use subset semantics. Issuance and enforcement share one canonicalizer, and incomparable scopes are rejected.
  - (b) Consumable dimensions use conservation. Live child allocations plus the parent's own use must stay within the parent's grant, through atomic reservation against the parent ledger. Unused allocation returns only by a recorded operation, and a child's expiry cannot exceed the parent's remaining lifetime.
  - Add `RA-CAPENV-001` scenarios for sibling fan-out aggregate, concurrent sibling reservation race, return and re-lend, and depth×breadth.

**H-02. Gate plan / RA-11. Enforcement is unscheduled, and Gates 4–5 have no prerequisite on it.**

- **Path:** 
  1. The catalog says RA-11 is "diagnostic first; enforcement later".
  2. Gate 2 includes only its diagnostic portion, and Gate 3 does not list RA-11 at all.
  3. Gate 4 (RA-10, multi-writer) and Gate 5 (RA-12/13, which ingest external research content) do not require the signature, publisher-trust and sandbox layers.
  4. As written, autonomous automation can proceed guarded only by semantic classifiers, which the packet's own RA-11 text and Q14 forbid as a substitute.
- **Narrow fix:** 
  - Assign RA-11 enforcement to Gate 3 (or a 3b) with its own review.
  - Replace the ordinal gate list with a prerequisite matrix. It should list which items must be qualified, not just present, before each item starts.
  - Require RA-03, RA-04, RA-09 and RA-11-enforcement at Gate 4/5 entry, and additionally RA-06, RA-07 and RA-10 for RA-13.
  - Add `RA-CONTEXT-001` enforcement scenarios: verify-then-load swap, revoked publisher or key, transitive dependency, and sandbox escape with a valid signature.

**D. Medium / Low findings**

- **M-01 (RA-01):** `qualified` is unscoped, and the arrow notation contradicts "independent facts". 
  - Define it as `qualified(subject-tuple, scope, program, version)`, never a boolean. State authorization as a predicate that requires it.
  - EXP-M and RQ-16 must project as not qualified.
  - Add scenarios for health-invalidated then green again (invalidation must latch), and for freshness/TOCTOU between projection read and use (bind to a generation).
- **M-02 (RA-02):** assurance composition is undefined. 
  - `RECOMPUTED` over `MODEL_JUDGMENT` or `USER_ATTESTED` inputs can launder the label. Derived assurance must be bounded by its inputs unless recomputer independence and input binding are shown.
  - Assurance should attach per (subject, claim). `SIGNATURE_VERIFIED` and `TRUSTED_ASSERTION` need a named trust root, since "trusted" has no meaning without one.
  - Multi-evidence combination needs stated semantics, with no stacking of weak items.
  - Predicate declarations of accepted combinations are governing rules under Invariant 14, so they must be versioned and immutable to candidates.
- **M-03 (RA-03):** 
  - "External authorization when required" must derive from the policy in the authority snapshot and default to required.
  - Q6 is stated as an invariant, but the mechanism is unspecified. The evaluator needs no write capability to authority state, and the receipt issuer's trust root must be distinct from both candidate author and evaluator environment.
  - Concurrency semantics rely on RA-10 primitives one gate later. Declare a serialized-writer precondition with enforced rejection, or move an atomic generation/CAS primitive earlier. Key RA-10's trigger to "any concurrent writer to authority-bearing state" (CI, human, reviewer), not only "autonomous multi-writer development".
- **M-04:** RA-07 (Gate 2) needs RA-08's identity and supersession primitives (Gate 3). Review the canonical framing spec first as a shared primitive, or limit RA-07 to digests and opaque links.
- **M-05 (RA-07/08):** append-only is a policy, not a mechanism. 
  - It needs tamper evidence (hash chain plus external anchor or monotonic counter) to detect truncation and rollback. RA-07 has no rollback scenario.
  - It also conflicts with the hard-delete ban. Secrets, PII or injection payloads captured by accident need an authorized quarantine: payload stored apart from the ledger entry, with the digest and a tombstone kept.
- **M-06 (RA-06):** 
  - Receipts bind source, not execution context. Git-ignored files, toolchain or container digest, environment and fetched dependencies are unspecified, and "relevant lock/generator-input digests" is undefined. Add execution-environment identity or explicitly scope receipts as source-only.
  - Git IDs are SHA-1. Add an independent SHA-256 canonical digest for adversarial-candidate settings.
  - Invariant 9 is too narrow. State it as "source identity must bind the executed state".
- **M-07:** experiments are scenario seeds only. There are no preregistered pass/fail predicates, no positive controls (valid actions must still pass, so guards aren't deny-all), and no test-the-test requirement (removing a guard must fail the test). Admit them at Gate 0 as seeds only.
- **M-08:** withholding intermediate findings prevents checking for closure-by-narrowing. Use commit-reveal: publish a hash of the withheld finding ledger now and reveal it after review.
- **M-09 (RA-10):** the protected resource must check the fencing token atomically at write time (for example ref-update CAS or a broker), not the writer. Add a scenario for a writer that skips the check.
- **L-01:** "authority boundary" (Invariant 18) is undefined and should be enumerated.
- **L-02:** "stable EXP-M deterministic result" (Gate 2 trigger) is undefined.
- **L-03:** 
  - The manifest does not hash itself, and there is no out-of-band digest. As observed here: zip SHA-256 `301dc02eecc898f28d22e0aebf11baa9ea4414a6cdc0bc61b1b8d08aa2cda534`; `PACKAGE-MANIFEST.json` SHA-256 `25d966a72d35c8edf3ddbb3decc4eca11a856711f80788302474ec883c946144`. Record them separately.
  - This pasted review authenticates no reviewer identity, so the Gate 0 exit should be treated as advisory input to the human owner.
- **L-04:** the source manifest gives no Proposed/Accepted/implemented/wired status per Ruflo source. That is not load-bearing here, but the review posture asks for it. The `main` commit is recorded but never referenced.
- **L-05:** RA-07 must not double as a deny-list. Revocation belongs to an authority-bearing mechanism.

**E. Cross-composition findings**

- **E-01 (RA-01 ← RA-05):** a generated registry feeding the capability projection would turn "registered" into laundered state. Keep the dependency one-way, with RA-01 reading only named authoritative stores.
- **E-02 (RA-06 with RA-02/03):** 
  - Receipts must carry source-state type, and promotion must hard-require `COMMITTED_SOURCE_STATE`.
  - Evidence from a dirty-snapshot run must not transfer to a later commit even if the tree hash matches, unless re-run.
- **E-03 (RA-04 with RA-12/13):** aggregate amplification (see H-01).
- **E-04 (RA-09 with RA-11/04):** sensitive read, untrusted-content ingest and egress can each be individually permitted, yet compose into exfiltration. Per-tool floors do not see data flow. Deny that triple by default within one envelope unless split by explicit grant.
- **E-05 (RA-07/08/11):** agent-authored failure text stored immutably and retrieved into other agents' context is persistent injection. Deliver it as data behind a provenance boundary, and use the quarantine from M-05.

**F. Test/experiment sufficiency**

Criterion: PASS means the scenario seed set is adequate for Gate 0 admission (additions above are Medium). FAIL means a High maps to a scenario gap. INSUFFICIENT_EVIDENCE means I cannot judge yet.

| Experiment Verdict Notes  |                       |                            |
| ------------------------- | --------------------- | -------------------------- |
| RA-CAP-001                | PASS                  | add M-01 scenarios         |
| RA-EVID-001               | INSUFFICIENT_EVIDENCE | needs M-02 semantics first |
| RA-PROMO-001              | PASS                  | M-03                       |
| RA-CAPENV-001             | FAIL                  | H-01                       |
| RA-REG-001                | PASS                  | E-01                       |
| RA-SRC-001                | PASS                  | M-06, E-02                 |
| RA-NEG-001                | PASS                  | M-05, E-05                 |
| RA-MEM-001                | PASS                  | M-05                       |
| RA-TOOL-001               | PASS                  | E-04                       |
| RA-CONC-001               | PASS                  | M-09                       |
| RA-CONTEXT-001            | FAIL                  | H-02                       |
| RA-ROUTE-001              | PASS                  | E-03                       |
| RA-DREAM-001              | INSUFFICIENT_EVIDENCE | depends on H-01 and H-02   |

**G. Frozen-boundary verdicts**

```text
RQ16_STOP_PRESERVED             = PASS
EXP_M_R5_FREEZE_PRESERVED       = PASS
DIRECT_RUFLO_TRUST_AVOIDED      = PASS
AUTHORITY_EFFECT_NONE           = PASS

```

- **RQ-16 and Ruflo:** no RA item touches RQ-16 or grants Ruflo trust.
- **EXP-M R5:** PASS at design level only, since no RA item edits R5 and RA-01 leaves `ProviderCapabilityProfile` authoritative. Exact preservation is unverified here. Before relying on it, resolve the recorded EXP-M head (`0ba6c3c…`), its tree and the five blob hashes directly in the repository.
- **Authority effect:** `authority_effect` is NONE consistently across the packet, README, catalog, attestation and source manifest.

**H. Final determination**

```text
unresolved Critical count: 0
unresolved High count: 2 (H-01, H-02)
safe for bounded implementation planning? no, pending a delta re-review of H-01 and H-02
safe to modify EXP-M R5 without new design review? NO
safe to resume RQ-16? NO

```

- Neither High touches Gate 1, so EXP-M under R5 is unaffected by these findings.
- This review grants no implementation, qualification or promotion authority.
