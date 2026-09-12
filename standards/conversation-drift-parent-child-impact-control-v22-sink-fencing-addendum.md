# Workflow Drift and Parent-Child Impact Control — V22 Authority Sink Fencing Addendum

Status: **PROPOSED V22 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This addendum is additive over the V22 governance-root-closure and runtime-enforcement artifacts and adopts the platform authority-sink-fencing addendum in the same frozen V22 candidate.

## V22-S01 — WDPC authority sinks are explicit and root-bound

Every WDPC authority sink must be represented in the active `AuthoritySinkRegistry`, including as applicable:

- `ReviewThresholdConsumptionLedger` and related uniqueness state;
- packet/generation/sequence/governance ledgers;
- governed policy/identity/authority registries;
- authority-bearing publication/audit outputs;
- reconciliation decision-record store;
- independent-support conflict-resolution state;
- capability-activation state;
- release/testing/implementation promotion state;
- external effectors that can make a governed decision effective outside the platform.

Unknown material sinks return `AUTHORITY_SINK_CLASSIFICATION_INCOMPLETE`.

## V22-S02 — No direct write credential around the guard

A WDPC transition cannot qualify if the candidate, implementation under test, beneficiary, workflow-local service, maintenance actor, or another unregistered path has an equivalent direct capability to mutate an authority sink without the guarded writer/effector and current kernel decision.

Break-glass/recovery paths remain separately governed and must satisfy equal-or-stronger root enforcement.

Proven unguarded equivalent authority returns `AUTHORITY_SINK_FENCING_INVALID`; missing required exclusivity evidence returns `INSUFFICIENT_EVIDENCE`.

## V22-S03 — Apply-time atomic currentness

At the authority apply boundary, the guarded writer/effector must atomically or equivalently fence/revalidate the exact versions/digests bound by the `AuthorityKernelDecisionRecord`, including applicable:

- governance generation/kernel;
- authority capability inventory/closure;
- authority dependency graph;
- governed policy/strength contracts;
- threshold/sequence/predecessor state;
- evidence currentness/revocation;
- registry versions;
- witness state;
- proposed transition digest;
- sink precondition/version.

Any change between kernel decision and apply makes the decision stale and returns exactly `ROOT_KERNEL_DECISION_STALE` unless a stricter inherited endpoint applies first.

## V22-S04 — Multi-sink WDPC transitions remain complete under failure

Where a WDPC transition requires multiple mandatory ledger/registry/publication/effect sinks, the full mandatory sink set is bound into the kernel decision.

If the active subsystem rule requires atomic publication, partial success cannot be surfaced as complete authority. Crash/acknowledgement loss/partial commit follows the existing deterministic `OUTCOME_UNKNOWN` and reconciliation rules rather than caller inference.

A mandatory authority sink omitted from the transaction/effect group returns the applicable inherited atomic-publication endpoint; if none exists for the sink class, return `AUTHORITY_SINK_ATOMICITY_VIOLATION`.

## V22-S05 — Effective-control closure strengthens independence checks

For V22 independence predicates, nominally distinct identities are insufficient. The platform evaluates common effective control through aliases, delegated identities, beneficial ownership, super-admin/root, cloud account/organization root, HSM/KMS administration, credential recovery/reset, deployment/CI/CD, configuration/secret-store, emergency/break-glass, mutation/recovery authority, and root-threshold-capable colluding sets.

This applies to reviewer/evaluator, witness, dependency-universe authority, attestation issuer, conflict resolver, evidence source, and guarded writer/effector independence where required.

A residual terminal-root trust assumption may be disclosed, but disclosure cannot convert a relationship that violates an active independence predicate into independent status.

## V22-S06 — Guard executable/configuration identity is part of qualification

A WDPC guarded writer/effector qualifies only when the executable/runtime identity and digest, sink authorization configuration, kernel-decision verifier configuration, endpoint binding, credential profile, and required execution attestation are current.

Guard disabling, binary replacement, endpoint rebinding, credential widening, configuration drift, or deployment drift invalidates qualification before authority apply.

## V22-S07 — Kernel decision key currentness

A WDPC `AuthorityKernelDecisionRecord` cannot authorize apply when its signing/attestation identity is revoked, expired, compromised, superseded, wrong-generation, or lacks governed rotation continuity.

Historical signature validity alone is not sufficient current authority.

## V22-S08 — Proof-view additions

V22 proof views expose, where applicable:

- authority sink identity/class/registry version;
- guarded writer/effector identity and exclusive-capability result;
- break-glass/recovery capability status;
- apply-time atomic/CAS/fencing result;
- kernel decision current/stale result;
- full mandatory multi-sink set and outcome/reconciliation state;
- effective-control closure and independence result;
- guard executable/configuration attestation;
- kernel-decision signer/key lifecycle/currentness.

Missing mandatory fields are `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V22-S09 — Review requirement

The clean V22 design review must independently search for sink bypass, TOCTOU, partial multi-sink authority, hidden common control, guard drift, and stale/revoked kernel-decision signer paths. The reviewer must not assume the listed sinks are exhaustive.

## V22-S10 — Freeze rule

This is design-only. It does not prove production credential isolation, DB/IAM fencing, atomic/CAS enforcement, HSM/KMS independence, or executable attestation.

No implementation/falsification/execution freeze follows from this artifact alone.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
