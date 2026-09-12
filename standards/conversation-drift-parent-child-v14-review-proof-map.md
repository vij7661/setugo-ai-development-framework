# V14 Review-Proof and Qualification Map

Status: **PROPOSED V14 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13 -> V14`

## 2. Reviewer-facing proof rules

Reviewer-facing evidence is split into:
- `DESIGN_BUILD_VIEW`
- protected `AUDIT_DETAIL`
- `QUALIFICATION_ATTESTATION_SET`

Only `DESIGN_BUILD_VIEW` is exposed to an ordinary design reviewer.

`AUDIT_DETAIL` may contain protected history preimages and authority internals.
`QUALIFICATION_ATTESTATION_SET` is required only when a review is intended to count toward a qualifying gate.

## 3. Active V14 mechanism IDs

- `MECH-PACKET-CLASS`
- `MECH-HISTORY-NONDISCLOSURE`
- `MECH-CANONICAL-NORMATIVE-EQUALITY`
- `MECH-ENDPOINT-TUPLE-EQUALITY`
- `MECH-NORMATIVE-REEXPRESSION`
- `MECH-PROJECTION-AUTHORITY-ATTESTATION`
- `MECH-QUALIFYING-CLEANROOM`
- `MECH-QUALIFYING-SOURCE-ATTESTATION`
- `MECH-QUALIFICATION-SNAPSHOT`
- `MECH-REVIEWER-SAFE-PROOF`

## 4. Evidence profiles

- `EP-PACKET-CLASS`
- `EP-HISTORY-NONDISCLOSURE`
- `EP-CANONICAL-NORMATIVE-EQUALITY`
- `EP-ENDPOINT-TUPLE-EQUALITY`
- `EP-NORMATIVE-REEXPRESSION`
- `EP-PROJECTION-AUTHORITY-ATTESTATION`
- `EP-QUALIFYING-CLEANROOM`
- `EP-QUALIFYING-SOURCE-ATTESTATION`
- `EP-QUALIFICATION-SNAPSHOT`
- `EP-REVIEWER-SAFE-PROOF`

## 5. Design-review versus qualification

A design reviewer may review V14 from a `DESIGN_REVIEW_PACKET` and return engineering findings.

Such a review:
- is preserved;
- may drive another design revision;
- has `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`;
- contributes zero to any gate requiring qualifying independent review unless separately proven eligible.

A qualifying review must use `QUALIFYING_INDEPENDENT_REVIEW_PACKET` and satisfy the full attestation set.

## 6. History metadata rule

Reviewer-facing manifests expose no history count, block ID, reviewer identity, disposition, or ordering metadata.

Only a fixed-shape opaque history commitment is allowed.

## 7. Equality rule

Qualification requires exact equality of canonical reviewable sets, not equality of raw review-history tokens.

Review-history statuses are typed separately and never counted as endpoint/status contracts.

Mixed history/normative blocks require canonical-clause-preserving re-expression.

## 8. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
