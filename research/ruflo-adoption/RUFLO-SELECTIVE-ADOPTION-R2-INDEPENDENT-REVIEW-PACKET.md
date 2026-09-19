# Ruflo Selective Adoption R2 — Independent Manual Review Packet

## Status

`R2_EXTERNAL_MANUAL_REVIEW_REQUESTED_NO_AUTHORITY_EFFECT`

This packet reviews a selective adoption plan derived from Ruflo. It does not implement any adoption item.

## Exact reviewed design

- repository: `vij7661/setugo-ai-development-framework`
- branch: `design/ruflo-selective-adoption-r2`
- reviewed design commit: `2778ebd8777fe4d3df9933a1158ffc842be5fd13`
- reviewed design tree: `c25ae025966c2a6ba454e4641a544f6467cfc369`
- EXP-M R5 frozen commit: `0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`
- RQ-16 stopped commit: `d9ef21c938414e8370dbb6a4d553066843758599`
- Ruflo research snapshot: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`

The representation appendices supplied with this packet are:

1. `RUFLO-R2-PROJECT-BOUNDARY-APPENDIX.md`
2. `RUFLO-R2-SOURCE-APPENDIX-A.md`
3. `RUFLO-R2-SOURCE-APPENDIX-B.md`

The project-boundary appendix contains exact frozen EXP-M R5 material, stopped RQ-16 material, and the exact R1 independent review as supplied.

The Ruflo appendices contain exact source files from the pinned Ruflo snapshot used to derive the adoption ideas.

## Authority boundary

This review has no authority effect.

Required invariants:

```text
RQ16_STOP_PRESERVED = true
EXP_M_R5_FREEZE_PRESERVED = true
DIRECT_RUFLO_TRUST = false
AUTHORITY_EFFECT = NONE
IMPLEMENTATION_AUTHORIZED = false
```

A `BOUNDED_PASS` may only mean that the R2 adoption design is safe enough for the next explicitly bounded implementation/experiment planning step.

It must not:

- modify EXP-M R5;
- resume RQ-16;
- authorize live provider/API qualification;
- import Ruflo directly into the trusted path;
- grant promotion/release authority.

## R1 context

R1 returned `CHANGES_REQUIRED`:

- Critical: 0
- High: 2

H-01 found consumable authority amplification under per-child subset semantics.

H-02 found that RA-11 enforcement was not a prerequisite for later multi-writer/swarm/research automation.

R2 claims both are closed and also incorporates every R1 Medium/Low and cross-composition correction.

Do not accept the closure claims without reconstructing them.

## Review posture

Assume false-green.

Attack both each component and combinations of components.

Do not treat:

- Ruflo ADR status as project qualification;
- a signature as publisher authorization;
- a lease as permission;
- health as qualification;
- registration as availability;
- model consensus as evidence authority;
- memory as policy;
- a generated registry as qualification state;
- a dirty source receipt as release-qualified evidence;
- an append-only claim as proof of rollback resistance;
- an LLM security classifier as a sandbox;
- self-adjudication as independent review.

## Required review questions

### A. R1 closure

Return CLOSED/PARTIAL/OPEN for:

- H-01
- H-02
- M-01 through M-09
- L-01 through L-05
- E-01 through E-05

For any item not CLOSED, provide the exact remaining failure path and narrow fix.

### B. Foundational primitives

Adjudicate:

- FP-01 CanonicalRecordIdentity
- FP-02 AuthorityGenerationCAS
- FP-03 TamperEvidentLedger
- FP-04 DataFlowLabel

Try collision, ABA, stale writer, restart rollback, fork, anchor crash, label downgrade and unauthorized declassification attacks.

### C. Capability truth

Verify the design never collapses:

`catalogued / registered / configured / reachable / healthy / qualified / authorized`

Verify:

- qualification is subject/scope/program/version/generation bound;
- invalidation latches;
- health cannot renew qualification;
- generated registry cannot mint qualification/authorization;
- fallback/provider drift does not inherit qualification.

### D. Evidence assurance

Try assurance laundering through:

- model/user assertions;
- transformations;
- signatures over wrong subjects;
- untrusted issuers;
- multiple weak evidence items;
- candidate-edited acceptance rules.

### E. Evaluation / promotion separation

Try:

- evaluator authority writes;
- self-issued receipt;
- receipt replay;
- stale baseline/head/policy;
- concurrent promotion;
- crash at each boundary;
- missing external authorization;
- stale CAS generation.

### F. Capability envelope conservation

Attack:

- sibling fan-out;
- depth x breadth;
- cumulative vs leased vs returnable resource types;
- reserve/release replay;
- child consumption followed by over-return;
- descendant use after parent revocation;
- wildcard/incomparable scopes;
- parent/child expiry.

### G. Source and execution identity

Attack:

- dirty bytes;
- untracked/ignored runtime input;
- symlink/mode/submodule drift;
- dependency/toolchain/container drift;
- credential version drift;
- non-hermetic execution falsely marked bound;
- dirty evidence transferred to a later commit.

### H. History / memory / negative learning

Attack:

- truncation/rollback/fork;
- unanchored tail;
- restart recovery;
- quarantine privacy leak;
- failure archive used as deny-list;
- superseded source leaves dependent active projection;
- persistent prompt injection from archived failure text.

### I. Tool/plugin/retrieval boundary

Attack:

- tool under-declared privilege;
- valid permission but runtime side-effect escape;
- sensitive read + untrusted ingest + external egress;
- data label downgrade;
- unsigned-but-benign classifier;
- signed-but-malicious plugin;
- valid signature from untrusted/revoked publisher;
- verify-then-load swap;
- transitive dependency substitution;
- dynamic executable fetch;
- sandbox escape.

### J. Concurrency

Attack:

- stale fence;
- lease ABA;
- resource that trusts writer-side check;
- candidate-controlled lease state;
- source receipt/worktree mismatch;
- shared integration resource conflict.

### K. Routing / research automation

Attack:

- route changes after exposure;
- fallback reuses authority;
- route selects swarm before prerequisites;
- research edits policy/gold/oracle;
- self-review authentication;
- self-merge/promotion;
- budget amplification;
- external content before RA-11 enforcement.

### L. Prerequisite graph

Verify:

- no cycles;
- no missing qualification prerequisite;
- `present` is never treated as `qualified`;
- diagnostic RA-11 never satisfies enforcement;
- authority-bearing target cannot start before its foundational primitive qualifies.

### M. Experiment/test sufficiency

For every FP/RA experiment in the matrix, require:

- deterministic oracle;
- positive control;
- adversarial fixtures;
- mutation of the real production guard, not fixture metadata;
- first-failure preservation;
- generated counts.

Return PASS/FAIL/INSUFFICIENT_EVIDENCE for:

- FP-IDENT-001
- FP-CAS-001
- FP-LEDGER-001
- FP-DATAFLOW-001
- RA-CAP-001
- RA-EVID-001
- RA-PROMO-001
- RA-CAPENV-001
- RA-REG-001
- RA-SRC-001
- RA-NEG-001
- RA-MEM-001
- RA-TOOL-001
- RA-CONC-001
- RA-CONTEXT-001
- RA-ROUTE-001
- RA-DREAM-001

### N. Cross-composition

At minimum attempt:

1. RA-01 <- RA-05 registry laundering.
2. RA-02 + RA-06 assurance laundering over unbound execution.
3. RA-03 + RA-04 over-allocated promotion.
4. RA-04 + RA-12/13 aggregate amplification.
5. RA-09 + RA-11 + RA-04 exfiltration composition.
6. RA-07/08 + RA-11 persistent injection.
7. RA-03 + RA-10 stale fence during promotion.
8. RA-06 + RA-03 dirty-to-committed evidence transfer.
9. RA-11 + RA-09 signed-but-overprivileged plugin.
10. RA-12 + RA-11 unqualified external-content route.

### O. Frozen boundaries

Using the project-boundary appendix, verify:

- RQ-16 remains stopped and unauthorized;
- EXP-M R5 remains frozen;
- no RA item is silently inserted into R5 as a new load-bearing predicate;
- no RA item supplies missing RQ-16 Linux/manual evidence;
- direct Ruflo trust is avoided;
- authority effect remains NONE.

## Required disposition

Return exactly one:

`BOUNDED_PASS`
`CHANGES_REQUIRED`
`INSUFFICIENT_EVIDENCE`

Any unresolved Critical or High requires `CHANGES_REQUIRED`.

## Required response structure

### 1. Overall disposition

### 2. R1 finding closure
H-01/H-02/M-01..M-09/L-01..L-05/E-01..E-05.

### 3. New Critical findings
For each:
- ID
- affected item
- exact false-green/authority path
- why insufficient
- narrow fix

### 4. New High findings
Same fields.

### 5. Medium/Low findings

### 6. Cross-composition findings

### 7. Experiment sufficiency
All FP/RA experiments listed above.

### 8. Frozen-boundary verdicts

```text
RQ16_STOP_PRESERVED = PASS|FAIL
EXP_M_R5_FREEZE_PRESERVED = PASS|FAIL
DIRECT_RUFLO_TRUST_AVOIDED = PASS|FAIL
AUTHORITY_EFFECT_NONE = PASS|FAIL
```

### 9. Final determination

State:

- unresolved Critical count;
- unresolved High count;
- safe for next bounded implementation/experiment planning? yes/no;
- safe to modify EXP-M R5 without separate design review? must remain NO;
- safe to resume RQ-16? must remain NO;
- implementation authority granted by this review? must remain NO.

## Self-adjudication commitment

The proposer withheld its internal R2 finding ledger to reduce reviewer anchoring.

Commitment:

`sha256:e013203536cbd64d7df21c1c27d3666a2d3364c0b6ad2f195ac5c8358502fd58`

It may be revealed only after the independent R2 review is returned.

## Reviewed file blobs

- `research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2.md` — `63a110e91601f8e9e7f0d1a6dbf061b5a1c068c9`
- `research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-PREREQUISITES.md` — `b96c053bbacdfc58e455a7e3c1903b13caeed343`
- `research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-TEST-MATRIX.md` — `7179650a21bb0a6dcd135adbd98924762d86bac7`
- `research/ruflo-adoption/RUFLO-R2-R1-FINDING-ADJUDICATION.md` — `a1188c7979d277f55b410d4b554fa872ccdecb33`
- `research/ruflo-adoption/RUFLO-R2-SELF-ADJUDICATION-COMMITMENT.json` — `2bcfda800b439f3f1cb6d4ac4f2c9bce3fdff468`
- `research/ruflo-adoption/RUFLO-R2-SOURCE-STATUS-MANIFEST.json` — `502b47f2c989c84820e7618277d7251042ea27e4`

## Current reviewed material

The exact R2 files are inlined below for convenience.


---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2.md

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



---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-PREREQUISITES.md

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


---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-SELECTIVE-ADOPTION-R2-TEST-MATRIX.md

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


---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-R2-R1-FINDING-ADJUDICATION.md

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


---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-R2-SELF-ADJUDICATION-COMMITMENT.json

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

---

# INLINE REVIEWED FILE: research/ruflo-adoption/RUFLO-R2-SOURCE-STATUS-MANIFEST.json

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