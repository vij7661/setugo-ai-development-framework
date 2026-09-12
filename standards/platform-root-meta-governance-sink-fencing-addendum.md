# Platform Root & Meta-Governance Closure — Authority Sink Fencing Addendum

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This addendum is additive over the platform root/meta-governance closure standard and its runtime-enforcement addendum in the same frozen candidate.

Purpose: make the root-kernel enforcement path structurally unavoidable at authority sinks, close time-of-check/time-of-use races, and evaluate independence over effective control rather than nominal identities.

## PGR-S01 — Root-bound authority sink registry

Each governance generation has a root-bound `AuthoritySinkRegistry` covering every ledger, database/table, registry, object-store namespace, authoritative publication channel, release/promotion state, external-effect adapter, credentialed actuator, or equivalent sink whose mutation can create or expose material authority.

Each sink record binds:

- immutable sink identity;
- sink class/schema;
- exact resource/store/endpoint identity;
- allowed guarded writer/effector identities;
- write/effect credential or capability profile identity;
- mandatory authority-publication/effect classification;
- required atomic/multi-sink group identity where applicable;
- guard executable identity/version/digest;
- root-kernel decision verification policy/version;
- control/admin/recovery/credential/mutation/deployment domains;
- effective sequence/version and predecessor.

Unknown material sinks fail closed with `AUTHORITY_SINK_CLASSIFICATION_INCOMPLETE`.

## PGR-S02 — Exclusive sink fencing

Authority sinks must be architected so that material writes/effects cannot be performed by bypassing the kernel guard with alternate credentials, direct database access, maintenance credentials, privileged local APIs, unregistered service accounts, or equivalent side paths.

The qualifying architecture must establish that:

- only registered guarded writer/effectors hold authority-capable sink credentials/capabilities in the normal authority path;
- candidate/beneficiary/implementation under test does not possess an equivalent direct sink capability;
- break-glass/recovery credentials are separately governed, inventoried, threshold-bound, logged, and subject to the same or stronger root-kernel decision requirement;
- credential rotation/recovery cannot silently introduce an unguarded writer;
- sink-side authorization rejects writers outside the current registry where the underlying platform permits such enforcement.

Proven unguarded equivalent write/effect capability returns `AUTHORITY_SINK_FENCING_INVALID`. Missing proof of required exclusivity is `INSUFFICIENT_EVIDENCE`.

## PGR-S03 — Atomic decision-currentness check at apply boundary

Verification of an `AuthorityKernelDecisionRecord` must be coupled to the actual state/effect application boundary so state cannot change after decision issuance and before apply without detection.

The apply operation must either:

- be one serializable/linearizable atomic transaction that revalidates every bound generation/inventory/closure/graph/policy/evidence/precondition version and commits the exact transition; or
- use an equivalent compare-and-set/fencing-token mechanism that proves all bound versions/preconditions are unchanged at apply.

If any bound version, predecessor, policy, evidence currentness, graph, inventory, closure, sink state, or transition digest changed after decision issuance, the decision is stale and apply returns:

`ROOT_KERNEL_DECISION_STALE`.

A fresh re-evaluation is required; timestamp freshness alone is not sufficient.

## PGR-S04 — Multi-sink completeness and partial-effect handling

Where one authoritative transition spans multiple mandatory sinks/publications/effectors, the exact mandatory sink set must be derived from the current root-bound authority-sink/publication classifications and bound into the kernel decision record.

If the subsystem requires atomic all-or-none authority publication, all mandatory sinks must commit atomically or enter an explicit `OUTCOME_UNKNOWN`/reconciliation state that cannot be represented as success until deterministic reconciliation proves the exact committed identity.

A partial authority effect cannot be treated as a complete success merely because the primary ledger/store committed.

Omission of a mandatory sink or false complete-success publication returns the subsystem's stricter atomic-boundary endpoint when defined; otherwise `AUTHORITY_SINK_ATOMICITY_VIOLATION`.

## PGR-S05 — Effective control closure for independence

Independence must be evaluated over `EffectiveControlClosure`, not nominal account/service identities.

For every supposedly independent authority, reviewer, evaluator, witness, source, writer, or resolver, control analysis includes at minimum:

- direct principal identity;
- aliases and delegated principals;
- beneficial owner/common owner where applicable;
- super-admin/root administrator;
- cloud account/organization root;
- HSM/KMS/key-administration control;
- credential issuance/recovery/reset control;
- deployment/CI/CD control;
- configuration/secret-store control;
- emergency/break-glass control;
- mutation/recovery authority;
- any root-threshold-capable colluding set.

Two nominally distinct identities are not independent when their effective-control closures violate the active independence contract.

Proven prohibited shared control returns the subsystem's applicable independence-invalid endpoint. Missing required control-closure evidence returns `INSUFFICIENT_EVIDENCE`.

## PGR-S06 — Guard executable/configuration attestation

The guarded writer/effector's executable/runtime identity, guard logic digest/version, sink authorization configuration, and kernel-verification configuration must be attested under the active control-execution/configuration policy.

A binary swap, deployment drift, configuration drift, endpoint rebinding, credential-profile widening, or guard-disable change makes the guard qualification stale before it may apply authority.

If the effect path cannot prove execution of the qualified guard/configuration, return `ROOT_KERNEL_ENFORCEMENT_REQUIRED` or the stricter applicable execution/configuration mismatch endpoint.

## PGR-S07 — Kernel-decision signing/key lifecycle

The kernel-decision integrity/signing identity bound in the generation genesis must have explicit version, validity, revocation/compromise, rotation continuity, and verification rules.

A decision signed by a revoked, expired, compromised, superseded, wrong-generation, or non-current kernel decision identity cannot authorize apply even if the historical signature verifies.

Key rotation must preserve governed continuity; local key substitution is prohibited.

## PGR-S08 — Proof-view additions

Reviewer-safe proof views add:

- exact authority sink registry version/digest and sink membership;
- writer/effector credential/capability exclusivity result;
- break-glass/recovery capability bindings;
- atomic/CAS/fencing precondition and apply result;
- kernel-decision stale/current result;
- multi-sink mandatory set and atomic/reconciliation state;
- effective-control-closure identities/domains and overlap result;
- guard executable/configuration attestation result;
- kernel-decision signing-key lifecycle/currentness result.

Missing mandatory values are `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE`, never PASS.

## PGR-S09 — New platform endpoints

- `AUTHORITY_SINK_CLASSIFICATION_INCOMPLETE`
- `AUTHORITY_SINK_FENCING_INVALID`
- `ROOT_KERNEL_DECISION_STALE`
- `AUTHORITY_SINK_ATOMICITY_VIOLATION`

All stricter subsystem endpoints remain active.

## PGR-S10 — Mandatory future review attacks

Every later clean review of an authority-bearing candidate must also attack:

1. direct sink/database/external-effect capability bypassing the guard;
2. maintenance/break-glass credential bypass;
3. credential rotation creating an unregistered writer;
4. decision-to-apply TOCTOU/race windows;
5. stale kernel decisions accepted after policy/evidence/graph/inventory changes;
6. omitted mandatory sink/publication/effect in a multi-sink transition;
7. nominal independence hiding common beneficial owner/admin/cloud/HSM/KMS/deployment/recovery control;
8. guard binary/configuration drift or replacement;
9. revoked/expired/compromised kernel-decision signing identity.

## PGR-S11 — Nonclaims

This addendum is design-only. It does not prove that a database/cloud/provider physically enforces exclusive credentials, that all sink capabilities are discoverable, or that production HSM/KMS/bootstrap infrastructure exists.

Those are implementation/runtime evidence obligations. Missing evidence cannot be upgraded to PASS by design text.

This addendum grants no implementation qualification, execution freeze, merge, release, deployment, production authority, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
