# V13 Independent Review Assurance Map

Status: **PROPOSED V13 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13`

Independent review consumes the V13 review projection plus its ProjectionProofBundle.

## 2. Projection authority domains

- `RHCA` — source block classification only.
- `RPB` — deterministic projection construction only.
- `RPAA` — independent recomputation/audit only.
- `CleanRoomAuthority` — reviewer-runtime isolation attestation only.

No one domain gains workflow terminal authority from these roles.

## 3. Active projection mechanisms

- `MECH-RHIR-INDEPENDENCE`
- `MECH-PROJECTION-EXECUTED-EQUIVALENCE`
- `MECH-PROJECTION-PROOF-BUNDLE`
- `MECH-PROJECTION-PROOF-ANCHOR`
- `MECH-CLEANROOM-PLATFORM-ATTESTATION`
- `MECH-CLEANROOM-AUTHORITY-INDEPENDENCE`
- `MECH-HISTORY-METADATA-MINIMIZATION`
- `MECH-ABSTRACT-HISTORY-BOUNDARY`
- `MECH-NEW-ARTIFACT-CLASSIFICATION`
- `MECH-ENDPOINT-OWNER-SCHEMA-EQUALITY`
- `MECH-PROJECTION-POSITIVE-COVERAGE`

## 4. Evidence profiles

- `EP-RHIR-INDEPENDENCE`
- `EP-PROJECTION-EXECUTED-EQUIVALENCE`
- `EP-PROJECTION-PROOF-BUNDLE`
- `EP-PROJECTION-PROOF-ANCHOR`
- `EP-CLEANROOM-PLATFORM-ATTESTATION`
- `EP-CLEANROOM-AUTHORITY-INDEPENDENCE`
- `EP-HISTORY-METADATA-MINIMIZATION`
- `EP-ABSTRACT-HISTORY-BOUNDARY`
- `EP-NEW-ARTIFACT-CLASSIFICATION`
- `EP-ENDPOINT-OWNER-SCHEMA-EQUALITY`
- `EP-PROJECTION-POSITIVE-COVERAGE`

## 5. Review-surface completeness

The V13 projection MUST preserve every active:
- normative clause;
- endpoint owner/schema tuple;
- authority/credential rule;
- state/transition rule;
- registry/object/schema rule;
- evidence-profile mapping;
- WDPC case and expected result.

Review-history-only content is never used to satisfy these sets.

## 6. Reviewer-facing metadata rule

The reviewer-facing manifest exposes aggregate proof results and candidate/projection digests, not concrete history-block identities or prior reviewer metadata.

## 7. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
