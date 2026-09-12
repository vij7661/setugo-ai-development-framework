# Workflow Drift and Parent-Child Impact Control — V14 Review-Proof Hardening

Status: **PROPOSED V14 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V14-C01 — Exact base binding

V14 is an additive hardening layer over exact V13 candidate:

- V13 candidate commit: `61fadbeb96f938105c6013e82d07af682354df2a`
- V13 projection-assurance overlay blob: `eb9334c775154c267e8f90ca6614ee830329ce75`
- V13 independent-review assurance map blob: `79a2c5f5cf6553140c4f7c18de2965224eaabdcf`
- V13 falsification extension blob: `2386d89ac7ca0154dfae2e580bc50d7980727ef3`

V5–V13 remain preserved source/history artifacts. V14 narrows only the independent-review proof surface and qualification rules.

V14 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V14-C02 — Two packet classes

Every reviewer packet is exactly one of:

- `DESIGN_REVIEW_PACKET`
- `QUALIFYING_INDEPENDENT_REVIEW_PACKET`

A `DESIGN_REVIEW_PACKET`:
- may be used for adversarial engineering feedback;
- may carry bounded design-build proofs;
- may omit live independent attestations;
- MUST state every omitted qualification artifact explicitly;
- contributes zero to any independent-review threshold.

A `QUALIFYING_INDEPENDENT_REVIEW_PACKET`:
- MUST satisfy every active qualification predicate, including source provenance, projection-authority independence, executed equivalence, clean-room attestation, proof/log anti-rollback, eligible reviewer evidence class, and exact candidate binding;
- fails closed if any predicate is missing, stale, conflicting, or unverifiable.

No actor may relabel a design-review packet as qualifying after review.

## V14-C03 — No reviewer-facing history cardinality or identity

Reviewer-facing packet/projection/proof material MUST NOT reveal:
- excluded-history counts;
- source-side history block IDs;
- source-side history block identifiers;
- source history filenames;
- prior reviewer identities;
- prior dispositions/findings;
- history ordering/timestamps that encode prior review outcomes.

The reviewer-facing proof may contain only a non-enumerating opaque `review_history_commitment` whose preimage is confined to the protected audit namespace.

Absence is checked mechanically by a reviewer-facing metadata scanner.

Leakage emits `REVIEW_HISTORY_METADATA_LEAKED`.

## V14-C04 — Canonical typed manifest equality

Projection equivalence uses typed canonical manifests rather than raw token-count equality.

The source and projection each produce:
1. `CanonicalNormativeClauseManifest`
2. `EndpointContractTupleManifest`
3. `AuthorityObjectSchemaManifest`
4. `EvidenceProfileManifest`
5. `WDPCCaseManifest`

`CanonicalNormativeClauseManifest` uses stable semantic clause IDs and preserves every active obligation even when reviewer-facing wording is abstracted to remove concrete review-history details.

`EndpointContractTupleManifest` contains tuples:
`(endpoint_id, owner_authority, schema_version, legal_predecessors, legal_successors, evidence_profile_binding)`.

Review outcome/status vocabulary such as reviewer dispositions is typed `REVIEW_HISTORY_STATUS`, never inferred as an endpoint merely because it is uppercase.

Qualification requires exact zero set difference for every active manifest family.

Any source-only or projection-only active canonical item emits `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

## V14-C05 — Re-expression proof for mixed normative/history blocks

When a source block mixes concrete review history with an active normative requirement, the block cannot simply be excluded.

Instead, RHCA must produce a `NormativeReExpressionRecord` binding:
- exact source block digest;
- source canonical clause IDs;
- reviewer-safe abstract clause text;
- projected canonical clause IDs;
- proof that concrete review outcome metadata was removed while normative semantics were preserved;
- RPAA verification result.

The canonical clause-ID sets MUST be identical.

Missing or mismatched re-expression emits `REVIEW_PROJECTION_NORMATIVE_LOSS`.

## V14-C06 — Independent projection authority evidence

For a `QUALIFYING_INDEPENDENT_REVIEW_PACKET`, signed current records are mandatory:
- `RHCAIndependenceRecord`;
- `RPBIndependenceRecord`;
- `RPAAIndependenceRecord`;
- `ProjectionEquivalenceExecutionRecord`;
- RPAA signature over the exact execution record and proof bundle.

The independence records bind candidate, principals, keys, control/admin/identity/credential/recovery/HSM/cloud-root domains, service-account aliases, beneficial ownership, and root-threshold-capable combinations.

Missing records do not make a design-review packet invalid as engineering input, but MUST set:
`qualification_status = INSUFFICIENT_EVIDENCE`
and contribute zero to review thresholds.

## V14-C07 — Clean-room evidence classification

A reviewer may describe its apparent chat context as packet-only for engineering purposes, but only a platform-signed `ReviewerCleanRoomAttestation` can satisfy a qualifying independence gate.

For `QUALIFYING_INDEPENDENT_REVIEW_PACKET`, `CLEAN` requires platform evidence for:
- retrieval indexes;
- memory state;
- cache/session reuse;
- connector/search scopes;
- hidden/system context assembly;
- review-history namespace access;
- delivered context digest.

Missing platform evidence => `INSUFFICIENT_EVIDENCE`, never qualifying `CLEAN`.

A `DESIGN_REVIEW_PACKET` may proceed without this attestation only because it is ineligible for threshold counting by construction.

## V14-C08 — Independent source repository attestation

A qualifying packet requires an independently signed `SourceRepositoryAttestation` proving:
- canonical repository identity;
- exact candidate commit;
- commit tree digest;
- path/blob membership;
- packet artifact digests;
- attestor independence.

Git blob/path values carried by the packet alone are transport/source references, not independent provenance proof.

Missing source attestation => design feedback may proceed, but qualification status is `INSUFFICIENT_EVIDENCE`.

## V14-C09 — Proof/log anti-rollback

Qualification requires current monotonic review-provenance evidence covering:
- source attestation;
- RHCA/RPB/RPAA records;
- extraction algorithm/corpus;
- projection;
- proof bundle;
- packet manifest;
- clean-room attestation.

All are bound into one `ReviewQualificationSnapshot` with monotonic sequence, predecessor digest, candidate, projection digest, and supersession state.

Any stale component or mixed-generation set emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

## V14-C10 — Reviewer-safe proof view

The reviewer-facing proof view MUST expose:
- packet class;
- exact candidate/projection digests;
- qualification predicate names and statuses;
- zero-difference results for canonical manifests;
- endpoint-contract tuple equality status;
- opaque review-history commitment;
- explicit `NOT_PRESENT`/`INSUFFICIENT_EVIDENCE` for missing live attestations.

It MUST NOT expose protected history identities/cardinalities.

No bounded build proof may be labeled `PASS` for qualification if any required live attestation is absent.

## V14-C11 — Endpoint tuple registry export

The candidate build MUST export the complete `EndpointContractTupleManifest` from the authoritative endpoint/schema registry or source-declared contract registry.

An endpoint name without owner/schema/predecessor/successor/evidence-profile binding is incomplete and cannot satisfy equivalence.

A missing tuple export emits `REVIEW_PROJECTION_PROOF_MISSING`.

## V14-C12 — Projection equivalence acceptance rule

For design review:
- bounded build comparison may be supplied with explicit limitations;
- reviewer assesses whether the contract is sufficient.

For qualification:
- canonical normative set difference = empty;
- endpoint tuple set difference = empty;
- authority/object/schema set difference = empty;
- evidence-profile set difference = empty;
- WDPC case set difference = empty;
- RPAA verification = valid;
- source attestation = valid;
- clean-room attestation = valid;
- anti-rollback snapshot = current.

Anything else is `INSUFFICIENT_EVIDENCE` or FAIL, never PASS.

## V14-C13 — New endpoints

V14 adds owner-bound endpoints:
- `REVIEW_PACKET_CLASS_MISMATCH`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`
- `REVIEW_ENDPOINT_TUPLE_MISMATCH`

It narrows:
- `REVIEW_HISTORY_METADATA_LEAKED`
- `REVIEW_PROJECTION_NORMATIVE_LOSS`
- `REVIEW_PROJECTION_EQUIVALENCE_FAILED`
- `REVIEW_PROJECTION_INDEPENDENCE_REJECTED`
- `REVIEWER_CLEAN_ROOM_INSUFFICIENT`
- `REVIEW_PACKET_PROVENANCE_MISMATCH`
- `REVIEW_PROJECTION_PROOF_MISSING`

## V14-C14 — Freeze rule

V14 cannot freeze for execution while unresolved Critical/High design findings remain.

No AI-generated engineering review, design-review packet, bounded build proof, or missing-attestation packet may satisfy a human/manual or otherwise qualifying independent-review gate.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
