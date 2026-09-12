# Workflow Drift and Parent-Child Impact Control — V16 Threshold Atomicity Hardening

Status: **PROPOSED V16 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V16-C01 — Exact base binding

V16 is an additive hardening layer over exact V15 candidate:

- V15 candidate commit: `7805e68c8f256dabe420faf34788df26bef0255e`
- V15 qualification-surface blob: `b4e11ea2cd573c47632e0abe840375dc440bc9ca`
- V15 qualification map blob: `b237ded202a2c0f9261cf938a325b28690b582c8`
- V15 falsification extension blob: `cacde45c6364e452ccd6a1e4ab8b33655ddf4702`

V5–V15 remain preserved source/history artifacts. V16 narrows only packet-generation visibility, qualification/count atomicity, re-expression-verifier independence, canonical-equivalence positive assurance, scanner false-negative fixtures, and endpoint-export candidate binding.

V16 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V16-C02 — PacketGenerationRecord is mandatory and reviewer-visible

Every review packet MUST carry a signed/content-addressed `PacketGenerationRecord` binding:

- packet ID;
- immutable `packet_generation` sequence;
- packet class;
- exact candidate commit;
- exact projection digest;
- exact proof-view digest;
- packet manifest digest;
- predecessor packet digest when one exists;
- supersession state;
- creation sequence;
- anti-rollback log sequence.

The reviewer-safe manifest and proof view MUST expose `packet_generation`, predecessor/supersession state, and whether the generation is current for the exact candidate/projection.

A missing generation record emits `REVIEW_PACKET_GENERATION_STALE` and `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`.

No packet created as `DESIGN_REVIEW_PACKET` may later change class in the same generation.

## V16-C03 — Atomic qualification-to-threshold consumption

`ReviewQualificationSnapshot` and `ReviewThresholdRecord` are a single governed atomic-consumption protocol.

A threshold count may occur only when one of these equivalent conditions holds:

1. qualification snapshot creation and threshold consumption commit atomically in the same authoritative transaction/consensus operation; or
2. immediately before threshold consumption, the platform performs a fresh live recheck and proves no relevant state transition occurred between recheck sequence and threshold commit.

The consumed snapshot binds:

- candidate;
- projection;
- packet ID/class/generation;
- eligible reviewer identity/role/evidence class;
- RHCA/RPB/RPAA independence;
- metadata scanner state;
- canonicalizer state;
- independent re-expression-verifier state;
- authoritative endpoint registry export;
- source-repository attestation;
- reviewer clean-room attestation;
- anti-rollback state;
- review-gate policy/version;
- threshold counter sequence.

If any bound predicate changes before threshold commit, consumption fails closed and a new snapshot is required.

Failure emits `REVIEW_THRESHOLD_SNAPSHOT_STALE` and `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`.

## V16-C04 — ReviewThresholdRecord exact-consumption semantics

`ReviewThresholdRecord` MUST persist:

- consumed qualification snapshot ID/digest/sequence;
- threshold gate ID/version;
- reviewer evidence ID;
- idempotency key;
- threshold-count result;
- commit sequence;
- exact predicate digest consumed.

One qualification snapshot may contribute at most once to the same threshold gate unless the governing gate explicitly permits otherwise.

Retries reuse the same idempotency key and MUST NOT double count.

A snapshot that becomes stale before consumption contributes zero.

## V16-C05 — Independent NormativeReExpressionVerifier authority

A separate `NormativeReExpressionVerifierAuthority` (`NRVA`) governs semantic-preservation verification.

NRVA MUST be independent from:

- RHCA;
- RPB;
- RPAA;
- canonicalizer/canonical-clause registry operators;
- candidate authors;
- beneficiaries of a permissive re-expression;
- any root-threshold-capable combination able to control the re-expression producer.

A signed `NormativeReExpressionVerifierIndependenceRecord` binds verifier principals/keys and control, admin, identity, credential, recovery, HSM/cloud-root, alias, and beneficial-owner domains.

NRVA cannot create or modify the re-expression it verifies.

Collusion or insufficient independence emits `NORMATIVE_REEXPRESSION_VERIFIER_INDEPENDENCE_REJECTED`.

## V16-C06 — Semantic-preservation and false-negative assurance

`CanonicalClauseIdentityRegistry` MUST separately test:

- collision resistance: materially different obligations must not collapse to one canonical ID;
- semantic equivalence acceptance: materially equivalent obligations expressed differently must not be falsely separated;
- obligation-strength preservation;
- scope/timing/authority/evidence/fail-closed preservation.

A governed positive corpus of equivalent paraphrases is mandatory.

If equivalent obligations are falsely separated, emit `CANONICAL_EQUIVALENCE_FALSE_NEGATIVE` and fail the positive control.

No PASS can be based only on collision-resistance negatives.

## V16-C07 — Re-expression verification decision

A `NormativeReExpressionVerificationRecord` qualifies only when all of the following agree for the exact source/projected clauses:

- canonical-clause identity result;
- semantic-equivalence result;
- obligation-strength comparison;
- prohibited-history-removal result;
- NRVA verification;
- RPAA projection-equivalence verification.

NRVA and RPAA are separate assurance functions. Agreement is required but neither grants workflow terminal authority.

Weakening emits `NORMATIVE_REEXPRESSION_WEAKENED`.

## V16-C08 — Scanner negative corpus must cover hidden metadata surfaces

`ReviewerSafeMetadataScannerRegistry` negative corpus MUST contain direct fixtures for leakage solely through:

- MIME type/subtype/parameters;
- connector/reference metadata;
- attachment names;
- payload/display labels;
- filename/path aliases;
- ordinals;
- content-disposition metadata;
- base64/reference wrapper metadata.

Each surface requires isolated negative tests and at least one combined fixture.

Scanner coverage merely listing a surface without falsification fixtures is insufficient.

## V16-C09 — Duplicative coverage accounting

Cases that exercise the same authoritative enforcement path may be retained as `DUPLICATIVE_BUT_USEFUL`, but MUST NOT inflate unique-path coverage.

`MechanismCoverageRecord` records:

- primary enforcement-path case;
- duplicate-supporting cases;
- unique-path count;
- reason for retaining duplicates.

WDPC-240 and WDPC-244 share the same history-commitment side-channel enforcement family and count as one unique enforcement path unless future evidence proves otherwise.

## V16-C10 — Authoritative endpoint export candidate binding

Every authoritative endpoint registry export used for qualification MUST bind:

- canonical repository/system identity;
- exact candidate commit;
- exact registry version/digest;
- exact endpoint tuple set digest;
- export sequence/time;
- authority principal/key;
- source/registry attestation.

An export from another candidate, even with an identical schema/version, is ineligible.

Failure emits `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING` or `REVIEW_ENDPOINT_TUPLE_MISMATCH`.

## V16-C11 — Proof-view completeness

Reviewer-safe proof view MUST explicitly expose:

- `packet_generation`;
- predecessor/supersession/currentness state;
- threshold-snapshot atomic-consumption status;
- NRVA independence status;
- canonical-equivalence positive-control status;
- scanner hidden-metadata fixture status;
- authoritative endpoint export candidate-binding status.

A required predicate that is absent is treated as `NOT_PRESENT`, never implicitly PASS.

## V16-C12 — New endpoints

V16 adds owner-bound endpoints:

- `REVIEW_THRESHOLD_SNAPSHOT_STALE`
- `NORMATIVE_REEXPRESSION_VERIFIER_INDEPENDENCE_REJECTED`
- `CANONICAL_EQUIVALENCE_FALSE_NEGATIVE`

V16 narrows enforcement of:

- `REVIEW_PACKET_GENERATION_STALE`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`
- `NORMATIVE_REEXPRESSION_WEAKENED`
- `REVIEW_HISTORY_METADATA_LEAKED`
- `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING`
- `REVIEW_ENDPOINT_TUPLE_MISMATCH`

## V16-C13 — Freeze rule

V16 cannot freeze for execution while unresolved Critical/High design findings remain.

No packet with missing/stale generation state, non-atomic qualification consumption, insufficient NRVA independence, missing semantic-equivalence positive assurance, or wrong-candidate endpoint export may satisfy a qualifying independent-review gate.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
