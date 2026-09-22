# Independent Blind Review - R8 Meta-Governance v4

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

## Frozen subject

Primary candidate:
- R8 v4 preregistration commit: `d779eb495b5830674e0258d4d27b768f77e10471`
- file: `governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V4.md`

Do not use prior R8 v1/v2/v3 reviewer findings, adjudications, or remediation conclusions. Review v4 from scratch.

## Objective

Attempt to falsify whether R8 v4 is sufficiently closed at design level to proceed to executable-schema freeze and implementation preparation.

The design now declares a T0 external trust axiom. Do not criticize the existence of an explicit root axiom merely because trust must terminate somewhere. Instead test whether:
- the axiom is clearly bounded;
- software can substitute self-issued labels for T0 attestations;
- the claimed threshold/independence properties are actually enforced by the design;
- lower layers can rewrite or bypass the T0-bound semantics.

## Mandatory attack areas

1. T0/EBA root boundary
   - EBA key/policy provisioning;
   - ControllerAttestation forgery/replay/revocation;
   - admin-domain independence;
   - whether self-issued IDs can still enter authority paths;
   - EBA version rollover and trust-root replacement.

2. BootstrapAuthorization / singleton genesis
   - first-seen witness;
   - concurrent bootstrap;
   - malicious replacement keys;
   - authorization expiry;
   - genesis/authorization byte mismatch;
   - atomicity of CAS_GENESIS.

3. Anchor quorum / transparency witness
   - 2-of-3 replica controller independence;
   - witness split-view/equivocation;
   - anchor quorum collusion;
   - stale signed tree heads;
   - witness outage;
   - anchor controller rotation.

4. Atomic CAS_APPEND
   - concurrent same-predecessor writers;
   - retry/idempotency;
   - split-brain commit certificates;
   - commutative-event exception abuse;
   - stream/head rollback.

5. Constitutional semantic artifact closure
   - whether any authority-relevant semantic input remains outside the digest-bound artifact set;
   - migration/recovery loopholes;
   - same bytes/different behavior;
   - schema extension maps;
   - parser/compiler/runtime dependency drift.

6. GCP-1
   - exact int64 boundaries;
   - leading zeros / -0 / + sign;
   - Unicode NFC;
   - escaping edge cases;
   - sets vs arrays;
   - absent/null;
   - extension maps;
   - reference vector completeness.

7. SPR
   - primitive retirement/supersession;
   - alias misuse;
   - unit/version migration;
   - old evidence under old primitive versions.

8. Reviewer independence
   - Channel H authenticity;
   - Channel X independence;
   - controller/admin-domain overlap;
   - provider-internal memory compensation;
   - packet contamination;
   - whether two-channel review can still be self-controlled.

9. Issuer/revocation
   - mandatory non-overridable SoD;
   - issuer key rotation;
   - revocation undo;
   - stale revocation head;
   - hidden revocation;
   - exact decision_context binding;
   - parent issuer compromise.

10. Time
   - decision-context replay;
   - challenge nonce reuse;
   - shared-controller sources;
   - skew manipulation;
   - stale signed attestations;
   - time authority rotation.

11. Strong evidence
   - QualifiedEvidenceProducer enrollment;
   - executable identity;
   - weak-to-strong laundering;
   - producer compromise;
   - producer revocation;
   - external manual-review boundary.

12. Out-of-band mutation
   - state-root completeness;
   - derived-index tampering;
   - unauthorized append;
   - auditor compromise;
   - time-of-check/time-of-use gap.

13. Materiality
   - field-mask incompleteness;
   - hidden semantics in "display" fields;
   - dependency extractor compromise;
   - unknown field handling.

14. Checkpoints/tenants
   - immediate anchoring;
   - stale checkpoint replay;
   - alias fallback;
   - tenant migration;
   - cross-tenant stable-ID replay.

15. Recovery
   - mandatory trigger schemas;
   - false trigger evidence;
   - root/recovery separation;
   - recovery quorum collusion;
   - unrecoverable state;
   - new-constitution authority inheritance.

16. Guard catalog / CaseProofContract
   - complete positive-control mapping;
   - target-guard proof;
   - earlier-guard masking;
   - independent fault proof;
   - constant-reject false green;
   - missing load-bearing guard.

17. Over-governance/deadlock
   - EBA unavailable/revoked;
   - transparency witness unavailable;
   - all anchors unavailable;
   - reviewer starvation;
   - state-integrity failure;
   - whether any recovery path creates an implicit bypass.

## Reviewer constraints

- Design review only; do not claim implementation/runtime verification.
- Do not grant implementation approval, qualification, merge, release, deploy, production, policy, or terminal authority.
- PR #39/#40 remain non-authoritative.
- Treat the explicit T0 axiom as a bounded trust assumption, not something the platform can self-prove.
- Attack whether the software can evade or counterfeit that assumption.
- Prefer concrete false-green/self-grant paths over stylistic concerns.
- Distinguish safe implementation details that may be frozen after design closure from design-level trust/authority gaps that must be fixed now.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. T0/EBA/bootstrap assessment.

F. Anchor/witness/CAS concurrency assessment.

G. Constitutional semantic/GCP-1/SPR assessment.

H. Reviewer/issuer/revocation/time independence assessment.

I. Evidence/materiality/state-integrity assessment.

J. Tenant/checkpoint/recovery assessment.

K. Guard catalog / falsification-mechanism-proof assessment.

L. Over-governance/deadlock assessment.

M. Minimal required changes before executable-schema freeze/implementation preparation.

N. Final bounded statement confirming:
- review grants no authority;
- R8 v4 remains NOT_IMPLEMENTED;
- PR #39/#40 remain NON_AUTHORITATIVE;
- unresolved material findings block implementation start.
