# V12 Independent-Review Projection and Precedence Map

Status: **PROPOSED V12 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12`

For independent review, the review surface is the canonical V12 `IndependentReviewCandidateProjection`, not the unfiltered historical source-artifact corpus.

## 2. Source/history separation

Source artifacts remain authoritative history in the repository.

For reviewer context, only blocks classified by `ReviewHistoryIsolationRegistry` as:

- `NORMATIVE_REVIEWABLE`
- `FALSIFICATION_REVIEWABLE`
- permitted `REFERENCE_REVIEWABLE`

may enter the projection.

`REVIEW_HISTORY_ONLY` and unclassified blocks are excluded/blocked.

## 3. Initial exclusion set

The initial projection excludes five opaque source blocks identified only as:

- `HIST-001`
- `HIST-002`
- `HIST-003`
- `HIST-004`
- `HIST-005`

Their source-side identities, digests, and audit reasons are retained in the protected review-history registry and are not disclosed to an independent reviewer.

Each exclusion must pass V12-C03/C04 normative-loss and equivalence checks.

## 4. New mechanism IDs

- `MECH-REVIEW-PROJECTION`
- `MECH-REVIEW-HISTORY-ISOLATION`
- `MECH-PROJECTION-EQUIVALENCE`
- `MECH-PROJECTION-PROVENANCE`
- `MECH-REVIEW-HISTORY-NAMESPACE`
- `MECH-PROJECTION-ANTI-ROLLBACK`

## 5. Evidence profiles

- `EP-REVIEW-PROJECTION`
- `EP-REVIEW-HISTORY-ISOLATION`
- `EP-PROJECTION-EQUIVALENCE`
- `EP-PROJECTION-PROVENANCE`
- `EP-REVIEW-HISTORY-NAMESPACE`
- `EP-PROJECTION-ANTI-ROLLBACK`

## 6. Mechanical completeness

Projection construction reconciles:

1. source artifact manifest;
2. RHIR block classifications;
3. source and projected normative-clause sets;
4. source and projected endpoint sets;
5. source and projected authority/object/schema sets;
6. source and projected WDPC case sets;
7. source and projected evidence-profile mappings;
8. reference-only role separation;
9. prohibited review-history leakage scan;
10. clean-room namespace access policy.

Any mismatch is fail-closed.

## 7. Authority limitation

This map is design evidence only.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
