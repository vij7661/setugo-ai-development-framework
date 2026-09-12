# V15 Review Qualification and Canonicalization Map

Status: **PROPOSED V15 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13 -> V14 -> V15`

## 2. Active V15 mechanisms

- `MECH-ENDPOINT-AUTHORITATIVE-REGISTRY`
- `MECH-REVIEW-METADATA-SCANNER-GOVERNANCE`
- `MECH-CANONICAL-CLAUSE-IDENTITY`
- `MECH-NORMATIVE-REEXPRESSION-VERIFICATION`
- `MECH-HISTORY-COMMITMENT-NONDISCLOSURE`
- `MECH-PACKET-GENERATION-ANTI-UPGRADE`
- `MECH-QUALIFICATION-SNAPSHOT-LIVE-RECHECK`
- `MECH-REVIEWER-LABEL-PATH-NONDISCLOSURE`

## 3. Evidence profiles

- `EP-ENDPOINT-AUTHORITATIVE-REGISTRY`
- `EP-REVIEW-METADATA-SCANNER-GOVERNANCE`
- `EP-CANONICAL-CLAUSE-IDENTITY`
- `EP-NORMATIVE-REEXPRESSION-VERIFICATION`
- `EP-HISTORY-COMMITMENT-NONDISCLOSURE`
- `EP-PACKET-GENERATION-ANTI-UPGRADE`
- `EP-QUALIFICATION-SNAPSHOT-LIVE-RECHECK`
- `EP-REVIEWER-LABEL-PATH-NONDISCLOSURE`

## 4. Prior-case tightening

- WDPC-225,226 -> scanner governance + label/path nondisclosure + commitment nondisclosure
- WDPC-227 -> authoritative endpoint registry required for qualification
- WDPC-229 -> canonical clause identity governance
- WDPC-234 -> normative re-expression verification
- WDPC-235 -> packet-generation anti-upgrade + live qualification recheck
- WDPC-237 -> all V15 qualification predicates are required

## 5. Design-review versus qualification

A `DESIGN_REVIEW_PACKET` may omit live qualification attestations but contributes zero to the qualifying threshold.

A `QUALIFYING_INDEPENDENT_REVIEW_PACKET` must bind all current V15 predicates to one exact `ReviewQualificationSnapshot`.

## 6. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
