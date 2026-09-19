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

## 2. R2 invariant corrections

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

Consumable dimensions use conservation semantics:

- money/spend
- tokens
- concurrency slots
- request counts
- delegation counts
- bounded compute/time

For parent grant G:

`parent_own_reserved + sum(live_child_reserved) <= G`

Reservation/release is atomic against a parent capability ledger.

Unused child allocation returns only via a recorded release operation.

Expiry cannot exceed the parent's remaining lifetime.

A child may not re-lend returned capacity until the release commit is authoritative.

Depth x breadth fan-out must never amplify aggregate authority.

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
- fetched dependency identities used by the execution;
- declared runtime input files;
- relevant environment/configuration hashes excluding secrets;
- runner/OS/architecture identity where the claim depends on them.

Promotion/release hard-requires `COMMITTED_SOURCE_STATE`.

Evidence from `IMMUTABLE_DIRTY_SNAPSHOT` never transfers to a later commit merely because the tree matches. Re-run is required.

Source-only receipts do not claim execution reproducibility.

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

RA-08 later adds governed active projections and namespace authority.

### R2-I08 — Append-only history has rollback detection and privacy quarantine

RA-07/RA-08 append-only logs use:

- hash chaining;
- monotonic sequence/generation;
- externally anchored checkpoint or independent monotonic authority anchor;
- restart/recovery validation.

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

### R2-I10 — Data-flow composition is governed

Individually permitted actions may still compose into exfiltration.

The combination:

`sensitive_read + untrusted_content_ingest + external_egress`

is denied by default inside one capability envelope unless an explicit governing grant authorizes that exact composed flow.

This is checked at plan/dispatch time, not only per-tool.

### R2-I11 — Fencing is enforced by the protected resource

RA-10 lease/fencing validity is checked atomically by the protected write authority/resource:

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
- transitive dependency closure;
- content-addressed verified load target;
- verify-then-load TOCTOU resistance;
- tool permission contract;
- sandbox/capability envelope;
- retrieval/context-injection representation boundary.

Semantic/LLM scanning remains diagnostic and never substitutes for deterministic enforcement.

Gate 4/5 automation cannot begin until RA-11 enforcement is qualified.

### R2-I13 — Failure archive content is untrusted data on retrieval

Agent-authored failure text, external content and model output stored in RA-07/08 never re-enter an agent/system prompt as instructions.

Retrieval wraps it as data with:

- provenance;
- record identity;
- quarantine/redaction status;
- explicit non-authority label.

Persistent injection from archived failure content is part of RA-CONTEXT-001.

### R2-I14 — Experiments require preregistered oracles, positive controls and test-the-test mutations

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

The R2 matrix remains a design contract until implemented.

### R2-I15 — Withheld self-adjudication uses commit-reveal

The R2 self-adjudication ledger remains withheld during independent review to reduce anchoring.

Commitment:

`sha256:2692e6f66b80519980d2d2e46caf50cb00bda8ec712ad852703efa4c68e15d7e`

After the independent R2 review is returned, the ledger may be revealed and its hash checked.

The commitment has no authority effect.

### R2-I16 — Authority boundaries are enumerated

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

### R2-I17 — EXP-M stability trigger is exact

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

### R2-I18 — Package/review identity is explicit

A package manifest does not recursively hash itself.

The review handoff records separately:

- packet content digest;
- package-manifest digest;
- final ZIP digest;
- source commit/tree/blob identities.

Pasted/manual reviewer text is user-attested external review evidence unless independently authenticated by another mechanism.

## 3. Dependency/prerequisite rules

See `RUFLO-SELECTIVE-ADOPTION-R2-PREREQUISITES.md`.

Important:

- RA-11 enforcement is required before autonomous multi-writer, swarm, or research automation.
- RA-03/04/09/11-enforcement are required before RA-10/12/13 can receive authority-bearing execution.
- RA-06/07/10 are additionally required before RA-13.
- RA-07 cannot depend on authority-bearing RA-08 semantics before the shared canonical identity primitive is reviewed.
- EXP-M continues under R5 independently of this adoption program.

## 4. R2 experiment families

See `RUFLO-SELECTIVE-ADOPTION-R2-TEST-MATRIX.md`.

Each family is preregistration-only until separately implemented and reviewed.

## 5. Frozen-boundary declaration

```text
RQ16_STOP_PRESERVED        = REQUIRED
EXP_M_R5_FREEZE_PRESERVED  = REQUIRED
DIRECT_RUFLO_TRUST         = PROHIBITED
AUTHORITY_EFFECT           = NONE
IMPLEMENTATION_AUTHORIZED  = false
```

