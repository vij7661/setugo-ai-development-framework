# Workflow Drift and Parent-Child Impact Control — V15 Qualification-Surface Hardening

Status: **PROPOSED V15 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V15-C01 — Exact base binding

V15 is an additive hardening layer over exact V14 candidate:

- V14 candidate commit: `3bc9b63dc6b2ed0086a216300977b35ce5edcfa8`
- V14 review-proof blob: `916fc107a8bb85e9411ab8e1597e1d418b03b2ed`
- V14 review-proof map blob: `454da528343143e313eb5c2c7efef29d016f0be2`
- V14 falsification extension blob: `1702b79188aac2708907fab3f2b1d0e2c1c405d2`

V5–V14 remain preserved source/history artifacts. V15 narrows only qualification-surface authority, canonicalization, metadata nondisclosure, and final qualification rechecks.

V15 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V15-C02 — Authoritative endpoint registry required for qualification

For `DESIGN_REVIEW_PACKET`, a source-declared endpoint/contract registry MAY be shown only as non-authoritative design input and MUST be labeled as a limitation.

For `QUALIFYING_INDEPENDENT_REVIEW_PACKET`, endpoint contract equality MUST be derived only from an authoritative endpoint/schema registry export independently bound to the exact candidate and qualification snapshot.

A source-declared registry cannot satisfy qualification.

Missing authoritative export emits:
- `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`

and qualification status is `INSUFFICIENT_EVIDENCE`.

## V15-C03 — Governed reviewer-safe metadata scanner

RGA governs a `ReviewerSafeMetadataScannerRegistry` binding:

- scanner ID/version;
- algorithm digest;
- adversarial corpus digest;
- scanner authority principal/key;
- authority-independence record;
- activation/sunset sequence;
- supported metadata surfaces;
- negative-test corpus;
- latest audit result.

The scanner MUST inspect reviewer-facing:
- filenames;
- labels;
- manifest ordinals;
- display paths;
- artifact descriptions;
- reference/base64 metadata;
- commitment encoding/length;
- timestamps/ordering fields;
- reviewer identity/outcome/disposition fields.

Scanner authority MUST be independent from candidate authors, RHCA, RPB, RPAA, and any beneficiary of a clean result.

Unauthorized, stale, missing, or failed scanner evidence emits `REVIEW_METADATA_SCANNER_UNAUTHORIZED`.

## V15-C04 — Fixed-shape opaque history commitment

A reviewer-facing `review_history_commitment` MUST have:

- fixed algorithm;
- fixed byte length;
- fixed encoding;
- fixed field name;
- no history count;
- no block identity;
- no reviewer identity;
- no timestamp/order metadata;
- no rotation-frequency signal.

Any cadence/rotation information remains only in protected audit detail.

Length, encoding, cadence, label, ordinal, filename, or path leakage emits `REVIEW_HISTORY_COMMITMENT_SIDECHANNEL`.

## V15-C05 — CanonicalClauseIdentityRegistry

RGA governs a `CanonicalClauseIdentityRegistry` binding:

- canonicalization algorithm/version/digest;
- normalization rules;
- semantic equivalence rules;
- collision-resistance corpus;
- obligation-distinction corpus;
- semantic-preservation corpus;
- independent verifier identity/key;
- activation/sunset sequence.

Two materially different obligations MUST NOT collapse to one canonical clause ID.

A collision emits `CANONICAL_CLAUSE_ID_COLLISION`.

Canonical IDs cannot be self-declared by a candidate author as proof of semantic equality.

## V15-C06 — NormativeReExpressionVerifier

Every mixed history/normative block re-expression requires a `NormativeReExpressionVerificationRecord` binding:

- exact source block digest;
- source canonical clause IDs;
- projected clause text;
- projected canonical clause IDs;
- semantic-delta result;
- obligation-strength comparison;
- prohibited-history-removal result;
- RPAA verification result.

The verifier MUST reject any re-expression that preserves a claimed canonical ID but weakens scope, obligation, timing, authority boundary, evidence requirement, or fail-closed behavior.

Weakening emits `NORMATIVE_REEXPRESSION_WEAKENED`.

## V15-C07 — Packet generation anti-upgrade

Every packet carries immutable:
- packet class;
- packet generation;
- candidate;
- projection digest;
- proof-view digest;
- predecessor/supersession state.

A packet created as `DESIGN_REVIEW_PACKET` can never be upgraded in place to `QUALIFYING_INDEPENDENT_REVIEW_PACKET`.

If a newer candidate/projection/packet generation supersedes an older design packet, the older packet remains historical engineering evidence only and cannot be reused for qualification.

Stale/upgrade attempts emit `REVIEW_PACKET_GENERATION_STALE` or `REVIEW_PACKET_CLASS_MISMATCH`.

## V15-C08 — Atomic live recheck at ReviewQualificationSnapshot

At the exact `ReviewQualificationSnapshot` sequence, qualification MUST atomically recheck current:

- RHCA independence;
- RPB independence;
- RPAA independence;
- scanner authority/algorithm/corpus state;
- canonical-clause registry state;
- authoritative endpoint registry export;
- source repository attestation;
- clean-room attestation;
- projection/proof anti-rollback state;
- packet generation/currentness.

A previously valid record cannot be relied upon if stale at the snapshot sequence.

Failure emits:
- `REVIEW_QUALIFICATION_SNAPSHOT_LIVE_RECHECK_FAILED`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`

## V15-C09 — Reviewer-facing label/path nondisclosure

Reviewer-facing material MUST NOT encode protected review history through:

- filenames;
- artifact labels;
- ordinals;
- display paths;
- descriptions;
- MIME/reference metadata;
- payload labels;
- attachment names.

The scanner must cover all of these surfaces.

## V15-C10 — Qualification proof-view predicates

Reviewer-safe proof views expose, at minimum:

- `packet_class`
- `packet_generation`
- `authoritative_endpoint_registry_export`
- `reviewer_safe_scanner_governance`
- `canonical_clause_identity_governance`
- `normative_reexpression_verification`
- `projection_authority_independence`
- `source_repository_attestation`
- `reviewer_clean_room_attestation`
- `qualification_snapshot_live_recheck`
- `anti_rollback_currentness`
- `qualification_status`
- `review_threshold_contribution`

Missing live qualification evidence MUST be shown as `NOT_PRESENT` or `INSUFFICIENT_EVIDENCE`; it may not be silently omitted.

## V15-C11 — Positive qualification path

A fully attested qualifying packet may proceed only when all current predicates for the exact same candidate/projection/packet generation are valid.

Eligibility to count under a review gate does not itself grant workflow, release, merge, production, or terminal authority.

## V15-C12 — New endpoints

V15 adds owner-bound endpoint schemas:

- `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING`
- `REVIEW_METADATA_SCANNER_UNAUTHORIZED`
- `CANONICAL_CLAUSE_ID_COLLISION`
- `NORMATIVE_REEXPRESSION_WEAKENED`
- `REVIEW_HISTORY_COMMITMENT_SIDECHANNEL`
- `REVIEW_PACKET_GENERATION_STALE`
- `REVIEW_QUALIFICATION_SNAPSHOT_LIVE_RECHECK_FAILED`

V15 narrows enforcement of:

- `REVIEW_ENDPOINT_TUPLE_MISMATCH`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`
- `REVIEW_HISTORY_METADATA_LEAKED`
- `REVIEW_PACKET_CLASS_MISMATCH`
- `REVIEW_PACKET_PROVENANCE_MISMATCH`

## V15-C13 — Freeze rule

V15 cannot freeze for execution while unresolved Critical/High design findings remain.

No `DESIGN_REVIEW_PACKET`, AI-generated engineering review, source-declared endpoint registry, ungoverned scanner/canonicalizer, stale qualification snapshot, or absent live attestation may satisfy a qualifying independent-review gate.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
