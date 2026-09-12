# Workflow Drift and Parent-Child Impact Control — V22 Meta-Governance Self-Activation Addendum

Status: **PROPOSED V22 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This addendum is additive over the V22 governance-root-closure, runtime-enforcement, and authority-sink-fencing artifacts and explicitly adopts `standards/platform-root-meta-governance-self-activation-clarification.md` for the V22 candidate.

## V22-A01 — WDPC governance-support objects cannot self-exclude

Every WDPC governance-support registry, selector, classifier, graph schema, sink registry, inventory, signer/key policy, guard/verifier policy, identity policy, reviewer/evaluator qualification policy, conflict-resolution policy, and equivalent authority-support object is in `AuthoritySurfaceClosure` whenever it can affect authority.

No WDPC support object may classify its own mutation/qualification policy as outside governance protection.

## V22-A02 — Immediately preceding effective rules govern activation

A proposed WDPC governance-support version remains candidate data until its activation has been validated and committed under the immediately preceding effective governance generation, root kernel, `StrengthContract`, authority-surface closure, dependency graph, sink-fencing rules, qualification rules, and authority endpoints.

The proposed version may not be used to validate its own non-weakening, approval set, evidence qualification, edge classification, sink/writer classification, signer/verifier qualification, or authority-surface membership.

A self-validating transition returns exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED` unless a stricter inherited endpoint applies earlier.

## V22-A03 — Prospective atomic activation

The old effective WDPC governance-support version remains authoritative through validation/commit. The new version is eligible for runtime consultation only after its exact activation record commits and its activation sequence/version is current at guarded writers/effectors.

Partial visibility, acknowledgement loss, or unknown activation outcome cannot be treated as success; the applicable deterministic outcome-unknown/reconciliation path governs.

## V22-A04 — New support class requires pre-existing qualification semantics

A newly introduced WDPC governance-support class may activate inside the current governance generation only if a pre-existing kernel-bound generic rule already covers its authority class and its applicable `StrengthContract`/closure semantics.

If qualification depends on the new class defining how it qualifies itself, the class cannot activate in the current generation. A new governance generation is required.

## V22-A05 — Signer/guard rotation follows old-effective rules

A proposed kernel-decision signer/key lifecycle or guard/verifier policy may not use its proposed broadened issuer, key, recovery, verifier, currentness, or rotation semantics to authorize the transition that activates those semantics.

The immediately preceding effective rules remain the authority for that transition.

## V22-A06 — Proof-view additions

V22 proof views expose, where applicable:

- old-effective support-object identity/version/digest;
- proposed identity/version/digest;
- old-effective `StrengthContract` and policy used for validation;
- proposed-version consultation-before-activation result;
- self-exclusion/self-classification result;
- atomic activation commit/sequence;
- post-activation consultation version;
- outcome-unknown/reconciliation status.

Missing mandatory values are `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V22-A07 — Review and freeze rule

The clean V22 review must independently attack self-validating registry/policy transitions, proposed-rule-before-activation use, support-class self-bootstrap, and signer/guard policy self-qualification.

This addendum is design-only. No V22 falsification case has been executed and no implementation/falsification/execution freeze follows from this artifact.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
