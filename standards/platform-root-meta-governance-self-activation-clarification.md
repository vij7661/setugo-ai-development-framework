# Platform Root & Meta-Governance Closure — Self-Activation Clarification

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This clarification is additive over the platform root/meta-governance closure, runtime-enforcement, and authority-sink-fencing standards in the same frozen candidate.

Purpose: prevent a proposed governance-support registry/policy from using its own not-yet-authorized rules to validate, activate, or conceal the transition that creates it.

## PGR-A01 — Governance-support registries are inside AuthoritySurfaceClosure

The following classes, including their mutation/classification/selection policies, are members of `AuthoritySurfaceClosure` whenever present:

- `AuthorityCapabilityInventory` and inventory mutation/completeness policy;
- `AuthoritySinkRegistry` and sink classification/mutation policy;
- `AuthorityDependencyGraph` registry and authority-edge classification schema/policy;
- `GovernedObjectIdentityRegistry` and identity mutation/classification policy;
- `StrengthContract` applicability/catalog metadata, while the active contract semantics themselves remain kernel-bound and immutable in-generation;
- governance-generation genesis and migration registries/policies;
- root-kernel decision signer/key lifecycle policy;
- root-kernel decision verifier/guard configuration policy;
- reviewer/evaluator/attestor/witness/source selector and qualification registries;
- any registry/policy that can add, remove, relabel, suppress, qualify, or reclassify an authority-bearing surface, writer, sink, dependency edge, evidence source, or decision class.

No such support object may exclude itself or its mutation policy from governance protection.

## PGR-A02 — Old-effective-rules govern transition into new rules

A proposed governance-support registry/policy/version is non-authoritative until the transition that activates it has been validated under the immediately preceding effective governance generation, root kernel, applicable `StrengthContract`, authority-surface closure, dependency graph, sink fencing, and transition rules.

The proposed version may be inspected as candidate data but may not be used to:

- decide that its own transition is non-weakening;
- change which principals count toward its own approval;
- remove itself from `AuthoritySurfaceClosure`;
- redefine its own authority/dependency edge class;
- redefine its own sink/writer classification;
- qualify evidence needed to approve itself;
- change the current kernel-decision verifier or signer rules used to approve itself.

A transition that depends on the proposed version's rules to become valid is rejected with:

`META_GOVERNANCE_SELF_ACTIVATION_REJECTED`.

## PGR-A03 — Activation is atomic and prospective

The old effective version remains authoritative through validation and commit of the new version. The new version becomes eligible for consultation only after its activation record has committed successfully under the old-effective rules and the exact activation sequence/version is visible to all guarded writers/effectors.

A runtime must not consult a proposed or partially committed version for material authority decisions.

If a transition is partially visible, acknowledgement is lost, or activation outcome is unknown, callers may not infer success. The transition enters the applicable `OUTCOME_UNKNOWN`/reconciliation path and remains non-authoritative until exact committed identity is proven.

## PGR-A04 — No bootstrap-by-self-definition for newly introduced governance support objects

When a new governance-support object class is introduced inside an existing governance generation, it may activate only when a pre-existing kernel-bound generic rule already covers its authority class and applicable `StrengthContract`/closure semantics.

If no pre-existing rule can qualify the new support class without relying on the new class's own proposed semantics, introducing it requires a new governance generation.

Missing pre-existing qualification semantics returns `AUTHORITY_STRENGTH_CONTRACT_MISSING` or `META_GOVERNANCE_SELF_ACTIVATION_REJECTED` according to whether the missing element is a strength contract or a self-validating activation path.

## PGR-A05 — Self-protection applies to key and guard policy rotation

A proposed root-kernel decision signer/key lifecycle policy or guard/verifier configuration policy cannot use its own broadened issuer, key, verifier, currentness, recovery, or rotation rules to qualify the transition that activates those rules.

The immediately preceding effective rules determine whether the proposed rotation is equal-or-stronger and whether the approving/verifying identities qualify.

## PGR-A06 — Proof-view additions

Reviewer-safe proof views expose, where applicable:

- old effective governance-support object identity/version/digest;
- proposed object identity/version/digest;
- exact old-effective policy/StrengthContract used to validate transition;
- proposed-version consultation-before-activation result;
- self-exclusion/self-classification attempt result;
- atomic activation sequence/commit identity;
- post-activation consultation sequence/version;
- `OUTCOME_UNKNOWN`/reconciliation status where activation acknowledgement is lost.

Missing mandatory fields are `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE`, never implicit PASS.

## PGR-A07 — New endpoint

- `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`

All stricter platform/subsystem endpoints remain active.

## PGR-A08 — Mandatory future review attacks

Every later clean review of an authority-bearing design must attempt to falsify:

1. a registry/policy excluding its own mutation rules from `AuthoritySurfaceClosure`;
2. proposed rules being used to validate their own activation;
3. proposed edge/sink classifications hiding the authority path that approves them;
4. proposed signer/guard policies qualifying their own broadened issuer/verifier set;
5. partial/stale registry activation being consumed as current;
6. a newly introduced governance-support class bootstrapping itself where no pre-existing generic rule qualifies it.

## PGR-A09 — Nonclaims

This clarification is design-only. It does not prove runtime atomic activation, distributed configuration convergence, or production registry enforcement.

It grants no implementation qualification, execution freeze, merge, release, deployment, production authority, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
