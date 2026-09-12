# Workflow Drift & Parent-Child Impact Falsification Matrix — V21 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V21`

V21 inherits WDPC-01…326 and adds WDPC-327…346. It narrows active V21 expected evidence semantics for WDPC-310, WDPC-311, and WDPC-318 without rewriting their historical V20 definitions.

No V21 case is executed by this document. Expected outcomes are frozen before implementation testing begins.

## Narrowed inherited cases

### WDPC-310 — Phase-specific publication classification

Fault A: authority-bearing publication class is missing, invalidly classified, locally overridden, or classification is unauthorized at classification time.

Expected A: exactly `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID`.

Fault B: publication is validly classified as authority-bearing but the commit omits it from the mandatory atomic bound set.

Expected B: exactly `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`.

### WDPC-311 — Dependency-universe authority versus missing proof

Fault A: candidate/corpus/beneficiary or proven forbidden/control-domain-overlap authority attempts to define/finalize the eligible universe.

Expected A: exactly `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`.

Fault B: no current qualifying `DependencyUniverseAuthorityBinding` or independence proof is available.

Expected B: exactly `INSUFFICIENT_EVIDENCE`.

### WDPC-318 — Conflicting independent-support exemptions

Fault: two current-looking exemption records conflict for the same dependent/generation pair and no governed conflict-resolution record exists.

Expected: exactly `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT`; dependent status becomes/remains `REVALIDATION_REQUIRED`; neither exemption is accepted.

## New negative cases

### WDPC-327 — Governed-object rename/alias threshold bypass

Fault: a governed ledger is renamed or presented through a new alias/class label, then a lower threshold is proposed under the new label.

Expected: immutable `governed_object_id` remains unchanged and the lower threshold is rejected as `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED` or, when the same policy transition directly lowers the inherited floor, `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED` according to the phase-specific validator.

### WDPC-328 — Governed-object split/merge threshold-floor bypass

Fault A: governed object at threshold T is split and one authority-bearing descendant is assigned threshold T-1.

Expected A: `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`.

Fault B: two governed objects with floors T1 and T2 merge and the resulting object is assigned a floor lower than max(T1,T2).

Expected B: `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`.

### WDPC-329 — Reconciliation evaluator self-selection/self-grant

Fault: commit initiator, retry requester, candidate/beneficiary, or below-threshold related principal selects or controls the reconciliation evaluator for its own `OUTCOME_UNKNOWN` event.

Expected: exactly `RECONCILIATION_EVALUATOR_INDEPENDENCE_INVALID`; no terminal commit/non-commit decision is authorized.

### WDPC-330 — Reconciliation unauthenticated evidence injection

Fault: otherwise independent evaluator is supplied mandatory ledger/publication/witness/uniqueness evidence lacking qualifying source authentication or exact tuple/digest/version binding.

Expected: exactly `INSUFFICIENT_EVIDENCE`; unauthenticated evidence cannot produce `NO_COMMIT_CONFIRMED` or `COMMIT_CONFIRMED_EXISTING`.

### WDPC-331 — Duplicate byte-identical committed decision identities

Fault: two distinct committed decision identities for the same intent/candidate/gate tuple have byte-identical payloads.

Expected: exactly `RECONCILIATION_CONFLICT`; byte equality does not collapse distinct authoritative commits.

### WDPC-332 — Publication registry sub-threshold mutation/local override

Fault: sub-threshold principal set or local implementation attempts to mutate/override `AuthorityPublicationClassRegistry` so an authority-bearing class becomes optional/non-authority-bearing.

Expected: mutation/override rejected; classification remains unchanged; `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID` for attempted unauthorized classification use.

### WDPC-333 — Runtime skips current publication registry consultation

Fault: commit path uses stale registry version or no registry lookup, then excludes a material publication class.

Expected: exactly `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID` before commit can qualify.

### WDPC-334 — Dependency-universe authority control-domain overlap

Fault: `DependencyUniverseAuthority` has nominally distinct identity but its control/admin/recovery/credential domain is controlled by candidate, beneficiary, corpus/algorithm producer, or a below-threshold controlling subset.

Expected: exactly `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`.

### WDPC-335 — Witness quorum policy weakening

Fault: new witness policy lowers quorum, reduces independence-domain diversity, increases allowed lag, weakens key-revocation/compromise handling, or admits a previously non-qualifying witness class without equal-or-stronger proof.

Expected: exactly `WITNESS_QUORUM_POLICY_WEAKENING_REJECTED`; previous policy remains active.

### WDPC-336 — Attestation issuer-policy weakening

Fault: policy broadens allowed qualifying issuers to include the implementation under test/candidate/beneficiary or reduces issuer-independence/verification requirements.

Expected: exactly `ATTESTATION_ISSUER_POLICY_WEAKENING_REJECTED`; previous issuer policy remains active.

### WDPC-337 — Activation-schema policy retroactive broadening

Fault: later activation schema introduces wildcard/alias/parent/dynamic-selector semantics and attempts to reinterpret an existing narrower activation under the broader schema.

Expected: exactly `ACTIVATION_SCHEMA_POLICY_WEAKENING_REJECTED`; existing activation retains original schema/version/meaning.

### WDPC-338 — Unsafe low-entropy/reversible credential fingerprint

Fault: proof-view fingerprint is a raw secret, reversible encoding, unsalted/unkeyed hash of credential material, or other scheme disallowed by the active fingerprint policy.

Expected: exactly `CREDENTIAL_FINGERPRINT_SCHEME_UNSAFE`; proof view cannot qualify.

### WDPC-339 — Independent-support conflict accepted by count/majority

Fault: conflicting exemption records exist and implementation chooses one by majority/count/model agreement without a governed conflict-resolution record.

Expected: exactly `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT`; dependent remains `REVALIDATION_REQUIRED`.

### WDPC-340 — Authority-meta-policy renamed to evade anti-weakening

Fault: witness/issuer/activation/reconciliation policy is renamed or moved to a new class/object identifier and then weakened.

Expected: immutable governance ancestry preserves the policy identity/strength floor; `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED` or `AUTHORITY_META_POLICY_WEAKENING_REJECTED` according to phase.

## New positive controls

### WDPC-341 — Governed-object identity preservation positive control

Positive: governed object is renamed/migrated without authority change; immutable `governed_object_id`, ancestry, and threshold floor remain unchanged.

Expected: migration/rename may proceed without false reclassification rejection.

### WDPC-342 — Independent reconciliation evaluator positive table

Positive: a qualifying independent evaluator with authenticated mandatory evidence executes each V20 reconciliation branch using the fixed order.

Expected: exact branch outcomes are returned deterministically; evaluator independence proof is current; no duplicate count.

### WDPC-343 — Correct publication classification and atomic inclusion positive control

Positive: current root-governed registry classifies a material publication as authority-bearing, runtime consults exact registry version/digest, and atomic commit includes it.

Expected: classification and atomic-bound predicates pass; no false publication/classification endpoint.

### WDPC-344 — Independent dependency-universe authority positive control

Positive: authority binding is independent/current, source registries are authoritative, and eligible universe is derived without candidate/corpus filtering.

Expected: authority-independence predicate passes and derived universe may be used for completeness checking.

### WDPC-345 — Same-or-stronger authority-policy rotations positive controls

Positive subcases independently rotate: witness-quorum policy, attestation-issuer policy, and activation-schema policy while retaining or strengthening every applicable authority/independence/currentness/scope restriction. Object identities/ancestry remain intact.

Expected: each rotation may proceed without false anti-weakening rejection; existing activation records are not retroactively broadened.

### WDPC-346 — Governed independent-support conflict resolution positive control

Positive: conflicting exemption records are resolved by a root-governed conflict-resolution record bound to exact conflicts, policy/version, resolving authority, evidence basis and sequence.

Expected: dependent may leave `REVALIDATION_REQUIRED` only according to the governed resolution; prior conflict history remains preserved.

## Execution rule

WDPC-327…346 are preregistered only. No V21 case has been executed. Historical V20 and earlier definitions/results remain preserved; V21 only narrows active prospective semantics.

EXP-ECC-6 and EXP-ECC-7 remain deferred and have no integrated/pass case here.

V21 grants no execution freeze, merge, release, deployment, qualification, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
