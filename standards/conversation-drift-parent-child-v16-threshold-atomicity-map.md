# V16 Threshold Atomicity and Semantic Assurance Map

Status: **PROPOSED V16 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13 -> V14 -> V15 -> V16`

## 2. Active V16 mechanisms

- `MECH-PACKET-GENERATION-VISIBILITY`
- `MECH-QUALIFICATION-THRESHOLD-ATOMICITY`
- `MECH-THRESHOLD-IDEMPOTENT-CONSUMPTION`
- `MECH-REEXPRESSION-VERIFIER-INDEPENDENCE`
- `MECH-CANONICAL-EQUIVALENCE-POSITIVE`
- `MECH-SCANNER-HIDDEN-METADATA-FIXTURES`
- `MECH-DUPLICATE-COVERAGE-ACCOUNTING`
- `MECH-ENDPOINT-EXPORT-CANDIDATE-BINDING`
- `MECH-PROOF-VIEW-COMPLETENESS`

## 3. Evidence profiles

- `EP-PACKET-GENERATION-VISIBILITY`
- `EP-QUALIFICATION-THRESHOLD-ATOMICITY`
- `EP-THRESHOLD-IDEMPOTENT-CONSUMPTION`
- `EP-REEXPRESSION-VERIFIER-INDEPENDENCE`
- `EP-CANONICAL-EQUIVALENCE-POSITIVE`
- `EP-SCANNER-HIDDEN-METADATA-FIXTURES`
- `EP-DUPLICATE-COVERAGE-ACCOUNTING`
- `EP-ENDPOINT-EXPORT-CANDIDATE-BINDING`
- `EP-PROOF-VIEW-COMPLETENESS`

## 4. Prior-case tightening

- WDPC-225,226,239,241 -> scanner hidden-metadata fixtures + proof-view completeness.
- WDPC-227,238,247 -> authoritative endpoint export exact-candidate binding.
- WDPC-228,237,250 -> packet generation + qualification/count atomicity + all active V16 predicates.
- WDPC-229,242,248 -> semantic-equivalence positive assurance in addition to collision resistance.
- WDPC-234,243,249 -> independent NRVA plus RPAA verification.
- WDPC-235,245 -> packet generation visibility/currentness and predecessor/supersession binding.
- WDPC-246 -> threshold count must atomically consume a current qualification snapshot.
- WDPC-240,244 -> retained as duplicate-supporting cases but count as one unique enforcement path unless evidence distinguishes them.

## 5. Review-gate rule

A review becomes threshold-count eligible only through one exact `ReviewThresholdRecord` consuming one current `ReviewQualificationSnapshot` for the same candidate/projection/packet generation.

No chat declaration, packet label, reviewer role, or previously valid snapshot can substitute for atomic current consumption.

## 6. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
