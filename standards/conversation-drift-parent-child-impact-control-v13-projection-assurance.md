# Workflow Drift and Parent-Child Impact Control — V13 Projection Assurance Hardening

Status: **PROPOSED V13 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V13-C01 — Exact base binding

V13 is an additive hardening layer over exact V12 candidate:

- V12 candidate commit: `21eab0166db224c46a811461750533fbbd7e9b8f`
- V12 review-isolation overlay blob: `ebe742a63bc1319c9e73c661ac115fc325da26e0`
- V12 independent-review map blob: `9712e85a3ecf5f154d932b373ea8b9f8bc712a03`
- V12 falsification extension blob: `9d8de047a6de67f59fa435483ad579323ab5d5f7`

V5–V12 remain source-history artifacts. Independent review consumes the canonical V13 review projection and its proof bundle.

V13 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V13-C02 — Three-authority projection pipeline

Projection qualification requires three non-overlapping functions:

1. `ReviewHistoryClassificationAuthority` (`RHCA`) classifies source blocks.
2. `ReviewProjectionBuilder` (`RPB`) constructs the projection mechanically from the classifications.
3. `ReviewProjectionAuditAuthority` (`RPAA`) independently recomputes source-versus-projection manifests and decides only `PASS | FAIL | INSUFFICIENT_EVIDENCE`.

No one principal/control domain may satisfy more than one of these functions for the same candidate.

RHCA, RPB, and RPAA MUST be independent from:
- candidate authors and candidate-author-controlled service accounts;
- beneficiaries of a permissive projection outcome;
- reviewer identities;
- any root-threshold-capable control combination that can control enough members of another projection function;
- shared credential-admin, recovery-admin, identity-admin, HSM/cloud-root, service-account alias, and beneficial-owner domains.

Failure emits `REVIEW_PROJECTION_INDEPENDENCE_REJECTED`.

## V13-C03 — Executed triple-source projection equivalence

Projection equivalence is not a prose assertion.

For every candidate, RPAA MUST mechanically execute three independent discovery passes over the source candidate and separately over the generated projection:

1. syntactic normative extraction;
2. author-declared/machine-derived clause and case manifests;
3. semantic/static reference extraction for endpoint, state, authority, object, schema, evidence-profile, registry, transition, and case references.

The adversarial extraction corpus MUST include:
- normative language without MUST/SHALL/REQUIRED;
- tables, comments, footnotes, headings, aliases, negative paraphrases;
- indirect endpoint/state references;
- authority implications without explicit authority keywords;
- nested metadata and structured fields.

The result is a `ProjectionEquivalenceExecutionRecord` containing source and projection manifest digests, extraction algorithm/corpus digests, exact set differences for every manifest family, duplicate/conflict sets, and deterministic result.

Any missing, duplicated, newly introduced, or owner/schema-unbound item emits `REVIEW_PROJECTION_EQUIVALENCE_FAILED` or `REVIEW_PROJECTION_NORMATIVE_LOSS`.

## V13-C04 — Machine-readable proof bundle is mandatory review input

Every independent-review packet MUST carry a machine-readable `ProjectionProofBundle` as design-build evidence.

It contains:
- exact candidate commit;
- exact source artifact path/blob/tree membership manifest;
- RHCA classification manifest digest;
- RPB algorithm digest;
- RPAA algorithm/corpus digest;
- source and projection normative-clause manifests;
- endpoint-owner-schema manifests;
- authority/object/registry/schema manifests;
- evidence-profile manifests;
- WDPC case manifests;
- exact set-difference results;
- projection digest;
- source-repository attestation references;
- review-provenance-log sequence;
- result.

Missing proof bundle means the packet may still be read for informal engineering feedback but cannot be represented as an equivalence-proven independent-review packet.

The proof bundle is evidence of candidate-build processing only; it is not runtime implementation evidence.

## V13-C05 — Projection proof anchoring and anti-rollback

`ProjectionEquivalenceExecutionRecord`, `ProjectionProofBundle`, RHCA classification manifest, and source-repository attestation are appended atomically or through a durable outbox to the same append-only review-provenance log used by packet manifests.

Each entry binds:
- monotonic sequence;
- predecessor digest;
- exact candidate;
- projection digest;
- proof-bundle digest;
- authority identities;
- supersession state.

An older algorithm, classification, proof, attestation, or projection cannot qualify after a newer non-revoked entry supersedes it.

Rollback/replay emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

## V13-C06 — History classification cannot self-grant

A block may become `REVIEW_HISTORY_ONLY` only when:

- RHCA classification is independently authorized;
- triple-source extraction finds no active normative/falsification item;
- no endpoint/authority/object/schema/evidence-profile/case/freeze/qualification requirement is lost;
- candidate author and beneficiary cannot satisfy RHCA quorum;
- the classification is exact-source-block-digest bound.

If a new extraction version discovers a normative item in a previously history-only block, that classification becomes `STALE_REVALIDATION_REQUIRED` and the projection becomes ineligible until rebuilt and re-reviewed.

## V13-C07 — Reviewer namespace denial must be platform-attested

A `ReviewerCleanRoomAttestation` can be `CLEAN` only when a platform/isolation authority independently attests:

- review-history indexes are excluded from retrieval;
- memory sources containing prior review content are disabled or cryptographically partitioned;
- session/cache reuse capable of carrying review history is disabled or partitioned;
- connectors/search scopes exclude review-history namespaces;
- hidden/system context assembly contains no concrete prior-review outcome;
- delivered packet/context digest matches the approved projection;
- reviewer runtime cannot fetch review branches/files through available tools.

If any required observation is unavailable, status is `INSUFFICIENT_EVIDENCE`, never `CLEAN`.

A self-declared reviewer statement cannot upgrade missing platform evidence.

## V13-C08 — Clean-room attestation authority independence

The platform/isolation authority issuing clean-room evidence MUST be independent from:
- reviewer;
- candidate author;
- R1;
- RHCA/RPB/RPAA;
- review-history repository owner where that owner can change namespace permissions;
- any actor whose review threshold benefits from a `CLEAN` result.

Its key/control/admin/recovery domains are recorded in `CleanRoomAuthorityIndependenceRecord`.

Failure emits `REVIEWER_CLEAN_ROOM_INSUFFICIENT`.

## V13-C09 — Review-history metadata minimization

Independent-review projections and packet manifests MUST NOT reveal:
- count of excluded history blocks;
- source-side history block IDs;
- reviewer identities;
- concrete prior dispositions/findings;
- timestamps or ordering that imply prior reviewer outcomes;
- source filenames whose names encode reviewer identity/outcome.

Reviewer-facing proof refers only to opaque aggregate commitments and set-equality results.

Detailed exclusion identities remain in the protected review-history/audit namespace.

## V13-C10 — Abstract-rule versus concrete-history boundary

A reviewer-facing rule is `ABSTRACT_GOVERNANCE_RULE` only if it describes generic roles, states, evidence classes, contamination predicates, or review process without identifying or encoding a concrete prior review event/outcome for the candidate lineage.

A block is `CONCRETE_REVIEW_HISTORY` if it contains any concrete:
- reviewer identity;
- candidate-specific review disposition;
- finding ID or finding summary;
- freeze recommendation;
- agreement/disagreement signal;
- prior-review baseline;
- adjudication result.

Ambiguous content defaults to `CONCRETE_REVIEW_HISTORY_BLOCKED` until independently classified.

## V13-C11 — New artifact exact classification

Any new candidate artifact or source block defaults to `UNCLASSIFIED_BLOCKED`.

A valid new artifact can enter the projection only after:
- exact source membership attestation;
- RHCA classification;
- RPAA triple-source extraction;
- projection rebuild;
- successful equivalence record;
- updated proof/log sequence.

No artifact inherits a prior artifact's classification by filename or directory.

## V13-C12 — Endpoint-owner-schema equality

Projection equivalence requires exact set equality not only for endpoint names but for tuples:

`(endpoint_id, owner_authority, schema_version, legal_predecessors, legal_successors, evidence_profile_binding)`

A projection that preserves an endpoint label while dropping/changing owner or schema binding fails with `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

## V13-C13 — Positive-control coverage for projection machinery

Projection qualification requires at least these positive categories:

1. complex mixed-format source with tables/comments/footnotes/aliases and legitimate history-only exclusions;
2. exact source/projection manifest equality under all three extraction passes;
3. valid new-artifact classification and projection update;
4. valid monotonic superseding projection/proof sequence;
5. valid clean-room namespace-denial attestation;
6. valid abstract reviewer-governance rules retained without concrete history leakage.

A block-all projector or classifier cannot satisfy qualification merely by refusing every projection.

## V13-C14 — New endpoints

V13 adds owner-bound endpoint schemas:
- `REVIEW_PROJECTION_INDEPENDENCE_REJECTED`
- `REVIEW_PROJECTION_PROOF_MISSING`
- `REVIEW_HISTORY_METADATA_LEAKED`
- `REVIEW_HISTORY_CLASSIFICATION_STALE`

V13 narrows existing enforcement of:
- `REVIEW_PROJECTION_NORMATIVE_LOSS`
- `REVIEW_PROJECTION_EQUIVALENCE_FAILED`
- `REVIEW_HISTORY_LEAKED_TO_REVIEWER`
- `REVIEW_PROJECTION_UNCLASSIFIED_BLOCKED`
- `REVIEWER_CLEAN_ROOM_INSUFFICIENT`
- `REVIEW_PACKET_PROVENANCE_MISMATCH`

## V13-C15 — Freeze/review rule

A V13 independent-review packet is eligible only when:
- exact source candidate and projection are bound;
- source-repository provenance is valid;
- RHCA/RPB/RPAA independence is valid;
- ProjectionProofBundle is present and PASS;
- review-provenance anti-rollback is current;
- reviewer clean-room platform attestation is CLEAN;
- review-history metadata minimization passes;
- evidence class is eligible for the active gate.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
