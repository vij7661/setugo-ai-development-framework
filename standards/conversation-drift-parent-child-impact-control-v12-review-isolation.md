# Workflow Drift and Parent-Child Impact Control — V12 Review-Isolation Hardening

Status: **PROPOSED V12 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V12-C01 — Exact base binding

V12 is an additive hardening layer over exact V11 candidate:

- V11 candidate commit: `a90044c6e71d64916b05eadd1b085d375be68281`
- V11 hardening blob: `33445f97b77f606be0a0a0f731bbac4ed1b39844`
- V11 precedence/review map blob: `9c7f52a2a508c4e1968d17c49af2fd1f1e763612`
- V11 falsification extension blob: `2eeaaeb403c25ad340b1ab464bc5eba21d3bdfa7`

V5–V11 remain source-history artifacts. For an independent reviewer, the normative review target is the V12 `IndependentReviewCandidateProjection` defined below.

V12 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V12-C02 — IndependentReviewCandidateProjection

Independent review MUST NOT expose prior-review findings, dispositions, baselines, adjudication conclusions, or reviewer-history summaries merely because those records exist in the repository.

A canonical `IndependentReviewCandidateProjection` is generated from the exact source-candidate artifacts.

The projection contains:

- every active normative clause;
- every active endpoint definition;
- every authority/role/credential rule;
- every active registry/object/schema definition;
- every active state/transition rule;
- every active WDPC falsification case and its expected endpoint/evidence profile;
- candidate identity, source-artifact digests, and projection algorithm/version;
- reference-only material only when explicitly allowed and isolated from candidate authority.

The projection excludes only sections classified `REVIEW_HISTORY_ONLY`.

The projection itself is content-addressed and becomes the exact review surface for independent review.

## V12-C03 — ReviewHistoryIsolationRegistry

RGA governs a signed `ReviewHistoryIsolationRegistry` (`RHIR`) that classifies each source section/block as exactly one of:

- `NORMATIVE_REVIEWABLE`;
- `FALSIFICATION_REVIEWABLE`;
- `REFERENCE_REVIEWABLE`;
- `REVIEW_HISTORY_ONLY`.

A block may be `REVIEW_HISTORY_ONLY` only if it contains **none** of:

- `MUST`, `MUST NOT`, `SHALL`, `REQUIRED`, `PROHIBITED`;
- endpoint definitions;
- authority grants/denials;
- state/transition definitions;
- evidence-class rules;
- registry/object/schema requirements;
- case IDs or expected endpoints;
- qualification/freeze conditions;
- implementation obligations.

If any such content is present, exclusion is prohibited and projection generation fails with `REVIEW_PROJECTION_NORMATIVE_LOSS`.

## V12-C04 — Projection equivalence proof

Every projection requires a signed `ReviewProjectionEquivalenceProof` binding:

- exact candidate commit;
- exact source-artifact set and blob digests;
- RHIR digest/version;
- projection algorithm/version;
- included source block IDs;
- excluded source block IDs;
- source normative-clause manifest digest;
- projected normative-clause manifest digest;
- source endpoint/case/authority/object manifest digests;
- projected endpoint/case/authority/object manifest digests;
- set-difference results;
- projection content digest;
- result `PASS | FAIL`.

Qualification requires exact set equality for all reviewable normative/falsification manifests.

Any missing, duplicated, or newly introduced normative item yields `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

## V12-C05 — Review-history namespace separation

Review findings, dispositions, raw reviewer outputs, adjudication artifacts, reviewer-comparison material, and reviewer-history metadata live in a separate `REVIEW_HISTORY` namespace.

Independent reviewer context construction MUST deny access to:

- review branches/directories;
- prior-review raw outputs;
- prior-review metadata/dispositions;
- adjudication artifacts;
- reviewer comparison summaries;
- review-history search/retrieval indexes;
- cached prior-review context.

The clean-room attestation records `review_history_namespace_access = DENIED`.

If the reviewer runtime can access review-history material, status cannot be `CLEAN`.

## V12-C06 — Candidate source may retain history without contaminating review

Historical source artifacts MAY retain review-history sections for auditability and provenance.

Those sections:

- remain immutable evidence;
- are not deleted or rewritten;
- are excluded from the independent-review projection only through RHIR;
- cannot carry normative authority while classified `REVIEW_HISTORY_ONLY`;
- cannot be cited by the reviewer as candidate authority;
- remain available later to authorized adjudication/cross-review stages.

This preserves history without contaminating independent review.

## V12-C07 — Projection-source provenance chain

`SourceRepositoryAttestation` extends to the projection.

It binds:

- exact source candidate commit;
- source artifact path/blob/tree membership;
- RHIR digest;
- projection algorithm digest;
- ReviewProjectionEquivalenceProof digest;
- final projection content digest;
- projection packet manifest digest.

A projection cannot qualify from self-asserted source bytes alone.

Any source/projection mismatch emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

## V12-C08 — No hidden historical metadata channels

The projection generator scans and classifies:

- headings;
- tables;
- comments;
- footnotes;
- YAML/JSON metadata;
- filenames/display labels;
- embedded manifests;
- artifact descriptions;
- base64/reference payload metadata;
- reviewer-status fields;
- disposition fields.

Historical reviewer identity/outcome/disposition data is excluded unless explicitly necessary for a normative rule and then rewritten only as an abstract role/rule, never as a prior outcome.

Failure emits `REVIEW_HISTORY_LEAKED_TO_REVIEWER`.

## V12-C09 — Abstract reviewer rules are allowed

Independent-review governance rules may mention abstract concepts such as:

- `R1`, `R2`, `R3`;
- `CLEAN`, `CONTAMINATED`, `INSUFFICIENT_EVIDENCE`;
- eligible/ineligible evidence classes;
- reviewer isolation requirements;
- prior-review access prohibition.

Such abstract rules do not constitute contamination unless they disclose or encode a concrete prior reviewer finding, disposition, agreement, baseline, or outcome for the candidate lineage.

## V12-C10 — New source artifact default

Any new source artifact/block not yet classified by RHIR defaults to `UNCLASSIFIED_BLOCKED`.

It cannot enter an independent-review projection until classified and included in a successful equivalence proof.

No unknown artifact inherits reviewability by default.

## V12-C11 — Projection rollback protection

Each projection is appended to the immutable review-provenance log with:

- candidate commit;
- projection digest;
- RHIR digest;
- equivalence-proof digest;
- monotonic projection sequence;
- predecessor projection digest.

An older projection cannot be reused after a newer projection for the same exact candidate is marked superseding.

Rollback emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

## V12-C12 — New endpoints

V12 adds owner-bound endpoints:

- `REVIEW_PROJECTION_NORMATIVE_LOSS`
- `REVIEW_PROJECTION_EQUIVALENCE_FAILED`
- `REVIEW_HISTORY_LEAKED_TO_REVIEWER`
- `REVIEW_PROJECTION_UNCLASSIFIED_BLOCKED`

All must exist in EndpointSchemaRegistry before associated cases execute.

## V12-C13 — Freeze and review rule

Independent review may count only when:

- exact candidate binding is valid;
- projection provenance is valid;
- equivalence proof is PASS;
- no review-history leakage is detected;
- clean-room attestation denies review-history namespace access;
- evidence class is eligible for the active review gate.

A contamination refusal caused by leaked review-history content is preserved as a successful isolation-control event and contributes zero to the independent-review threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
