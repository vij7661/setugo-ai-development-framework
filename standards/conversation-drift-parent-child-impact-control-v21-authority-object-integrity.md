# Workflow Drift and Parent-Child Impact Control — V21 Authority-Object Integrity

Status: **PROPOSED V21 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V21-C01 — Exact base and precedence

V21 is additive over exact V20 candidate `cbe00858fea092d278772671f2328da2b771ac73`.

All active V5–V20 controls remain in force except where V21 narrows an ambiguity in the stricter fail-closed direction. V21 grants no implementation qualification, execution freeze, merge, release, deployment, or terminal authority.

## V21-C02 — Immutable governed-object identity and anti-reclassification

Every root-governed ledger, registry, policy object, authority object, and equivalent authority-bearing state has one immutable `governed_object_id` in a root-governed `GovernedObjectIdentityRegistry`.

The identity record binds:

- immutable governance identity;
- object type/class and schema version;
- physical/logical store identities and aliases;
- predecessor identity and lineage;
- current mutation-threshold floor;
- applicable root-policy version;
- split/merge ancestry where applicable;
- activation/effective sequence.

Rename, alias, storage migration, namespace change, wrapper creation, class relabeling, or equivalent indirection does not create a new governance identity and cannot lower the threshold floor.

If one governed object is split, every descendant retaining any authority/state derived from the parent inherits a mutation-threshold floor no weaker than the parent's immediately preceding floor. If governed objects are merged, the resulting object inherits a floor no weaker than the strongest immediately preceding floor among all authority-bearing ancestors.

A reclassification, alias, split, merge, migration, or rename that would evade an existing threshold or policy obligation is rejected before activation.

Failure endpoint: `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`.

## V21-C03 — Authority-meta-policy non-weakening

Authority-bearing policies that define who may evaluate, classify, attest, witness, interpret scope, or mutate authority state are themselves protected governance objects under V21-C02 and V20-C02.

This includes at minimum:

- reconciliation-evaluator policy;
- `AuthorityPublicationClassRegistry` mutation policy;
- `DependencyUniverseAuthority` independence policy;
- witness quorum/currentness policy;
- control-execution attestation issuer policy;
- activation-scope schema policy;
- credential-fingerprint scheme policy.

For each policy class, a root-governed versioned strength predicate compares the immediately preceding effective policy with the proposed policy. A transition that expands unilateral authority, lowers required independence/quorum, broadens accepted issuer/evaluator classes, weakens currentness/revocation requirements, broadens pre-existing activation interpretation, or weakens secret-protection guarantees is rejected before activation.

Policy renaming/reclassification cannot avoid this comparison because the immutable `governed_object_id` and ancestry rules govern the transition.

Failure endpoint: `AUTHORITY_META_POLICY_WEAKENING_REJECTED`.

## V21-C04 — Independent reconciliation evaluator and authenticated evidence

`REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` may be resolved only by an evaluator selected from a root-governed `ReconciliationEvaluatorRegistry`.

A qualifying evaluator record binds:

- evaluator identity, implementation/version/digest;
- control/admin/recovery/credential domains;
- allowed evidence-source classes;
- forbidden relationships to commit initiator, candidate, beneficiary, threshold-ledger writer, publication writer, and retry requester;
- active independence-policy version and threshold;
- effective sequence, expiry/revocation state.

The commit initiator, retry requester, candidate/beneficiary, or any principal below the required independence threshold may not self-select, self-authorize, or control the evaluator.

Every authority-bearing input used by reconciliation must be independently authenticated and bound to exact source identity, source class, candidate/gate/intent tuple, sequence/version, evidence digest, and authentication proof. The evaluator may read/verify such evidence but may not manufacture or rewrite authority-bearing source evidence.

The fixed V20 branch order remains mandatory:

1. authenticated structural contradiction → `RECONCILIATION_CONFLICT`;
2. exactly one complete canonical committed decision identity → `COMMIT_CONFIRMED_EXISTING`;
3. authenticated complete proof of absence → `NO_COMMIT_CONFIRMED`;
4. otherwise → `INSUFFICIENT_EVIDENCE`.

Two or more distinct committed decision identities for the same intent/candidate/gate tuple are a structural conflict even when their payloads are byte-identical. Authenticated replicas of the same canonical decision identity do not constitute multiple commits.

Missing/invalid evaluator independence or unauthenticated mandatory evidence cannot produce `NO_COMMIT_CONFIRMED`.

Failure endpoint: `RECONCILIATION_EVALUATOR_INDEPENDENCE_INVALID` or `INSUFFICIENT_EVIDENCE` according to whether disqualifying evidence is proven or required evidence is absent.

## V21-C05 — Publication-classification registry integrity and mandatory runtime consultation

`AuthorityPublicationClassRegistry` is a protected governance object under V21-C02/C03. Mutation requires the active root mutation threshold and may not be performed by local policy, implementation-under-test override, or sub-threshold principal set.

Every material authority commit must bind the exact current registry version/digest consulted before atomic-bound-set validation. Runtime omission, stale-registry use, local override, or an unknown/unclassified material publication class is fail-closed.

Classification-time invalidity returns `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID`. If a correctly classified authority-bearing publication is omitted from the atomic commit boundary, commit validation returns `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`.

## V21-C06 — Dependency-universe authority independence

Every `DependencyUniverseAuthority` has a root-governed `DependencyUniverseAuthorityBinding` containing:

- exact authority identity and implementation/version/digest;
- control/admin/recovery/credential domains;
- source registries from which eligibility is enumerated;
- independence policy/version and threshold;
- forbidden relationships to candidate, beneficiary, corpus/algorithm producer, dependent-decision author, and operational principal sets capable of controlling the authority below the required threshold;
- effective sequence, expiry/revocation state.

The candidate, beneficiary, corpus/algorithm generation under change, or a below-threshold controlling subset may not define, filter, suppress, finalize, or administratively control the eligible universe.

Proven forbidden/control-domain overlap returns `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`. Missing current independence proof returns `INSUFFICIENT_EVIDENCE`.

## V21-C07 — Witness-quorum policy anti-weakening

Witness quorum/currentness policy is a protected governance object. A proposed policy version is weaker and must be rejected if, for any governed witness class, it:

- lowers required quorum count/threshold;
- reduces required independent-domain diversity;
- removes a forbidden control/admin/recovery/credential/mutation relationship;
- increases permitted sequence/time lag;
- weakens key validity, revocation, compromise, or continuity requirements;
- permits a previously non-qualifying witness class without an equal-or-stronger governed independence proof.

Membership/key rotation may occur without weakening when the exact quorum and independence/currentness strength predicates remain equal or stronger and continuity verifies.

Failure endpoint: `WITNESS_QUORUM_POLICY_WEAKENING_REJECTED`.

## V21-C08 — Attestation-issuer policy anti-weakening

`ControlExecutionAttestation` issuer policy is a protected governance object. Expansion of allowed issuer classes, reduction of issuer independence, removal of external/independent verification requirements, or admission of the implementation under test/candidate/beneficiary as a qualifying issuer where it was previously disallowed is a weakening and is rejected before activation.

Replacing an issuer is permitted only when the active root-governed strength predicate proves the replacement satisfies equal-or-stronger identity, independence, evidence-class, verification, expiry/revocation, and action-binding requirements.

Failure endpoint: `ATTESTATION_ISSUER_POLICY_WEAKENING_REJECTED`.

## V21-C09 — Activation-schema policy integrity and non-retroactive scope semantics

Activation-scope schema policy is a protected governance object. Existing activation records retain the exact schema/version and interpretation in force when approved.

A later schema may not retroactively broaden an existing activation through aliases, wildcards, parent-resource expansion, dynamic selectors, derived resources, implicit power inheritance, or equivalent interpretation changes.

A schema transition that broadens default/implicit scope semantics is weakening and is rejected for existing authority. New expressive constructs may be introduced only prospectively and require a new governed activation record whose exact schema/version and expanded scope are explicitly approved.

Failure endpoint: `ACTIVATION_SCHEMA_POLICY_WEAKENING_REJECTED`.

## V21-C10 — Credential-fingerprint non-reversibility policy

Credential/configuration proof views must not use raw, unsalted, or unkeyed hashes of credential secrets as qualifying fingerprints, because low-entropy credentials may be dictionary-recoverable.

A root-governed `CredentialFingerprintSchemeRegistry` permits only schemes that derive proof-view identifiers from either:

- a random/opaque credential-profile identifier that is not the credential secret; or
- a keyed pseudorandom/MAC construction with a high-entropy key unavailable to proof-view consumers, with domain separation and versioned scheme identity.

Raw secret values, reversible encodings, direct hashes of low-entropy credential material, or schemes whose recovery resistance cannot be established under the active policy are rejected.

The proof view exposes scheme identity/version and the secret-non-exposure result, never the credential or derivation key.

Failure endpoint: `CREDENTIAL_FINGERPRINT_SCHEME_UNSAFE`.

## V21-C11 — Independent-support conflict resolution determinism

When multiple current-looking `IndependentSupportRegistry` records conflict for the same dependent/generation pair, the dependent deterministically becomes `REVALIDATION_REQUIRED` and no exemption is accepted.

Conflict resolution requires a root-governed conflict-resolution record bound to the exact conflicting record identities/digests, decision/generation identity, policy/version, resolving authority, evidence basis, sequence, and resulting current record or explicit no-exemption result.

Until that record exists, the endpoint is `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT` and dependent status remains `REVALIDATION_REQUIRED`.

## V21-C12 — Narrowed inherited endpoint semantics

For active V21 testing:

- WDPC-310 classification-time invalid/missing/unauthorized classification → exactly `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID`; omission of a validly classified authority-bearing publication at commit validation → exactly `ATOMIC_AUTHORITY_PUBLICATION_BOUNDARY_VIOLATION`.
- WDPC-311 self-derived or proven non-independent dependency-universe authority → exactly `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`; missing current authority/independence proof → exactly `INSUFFICIENT_EVIDENCE`.
- WDPC-318 conflicting exemptions without governed resolution → exactly `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT`, with dependent status `REVALIDATION_REQUIRED`.

Historical V20 definitions remain preserved and are not rewritten.

## V21-C13 — Proof-view additions

Reviewer-safe proof views expose, as applicable:

- immutable `governed_object_id`, ancestry, aliases, threshold floor, and anti-reclassification result;
- authority-meta-policy old/new versions and strength-comparison result;
- reconciliation evaluator identity/version/domains/independence result;
- authenticated reconciliation evidence source identities/classes/digests and branch predicate results;
- canonical-decision identity versus replica identity and duplicate-commit result;
- publication-registry version/digest, mutation authorization, runtime-consultation result, and phase-specific endpoint;
- dependency-universe authority binding and independence result;
- witness-quorum policy old/new strength dimensions and non-weakening result;
- attestation-issuer policy old/new allowed classes, independence/verification requirements and non-weakening result;
- activation-schema version, interpretation result, prospective/non-retroactive result;
- credential-fingerprint scheme identity/version and non-reversibility/non-exposure result;
- independent-support conflict identities and resolution-record status.

Missing mandatory values are `NOT_PRESENT` or `INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V21-C14 — New endpoints

- `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`
- `AUTHORITY_META_POLICY_WEAKENING_REJECTED`
- `RECONCILIATION_EVALUATOR_INDEPENDENCE_INVALID`
- `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`
- `WITNESS_QUORUM_POLICY_WEAKENING_REJECTED`
- `ATTESTATION_ISSUER_POLICY_WEAKENING_REJECTED`
- `ACTIVATION_SCHEMA_POLICY_WEAKENING_REJECTED`
- `CREDENTIAL_FINGERPRINT_SCHEME_UNSAFE`
- `INDEPENDENT_SUPPORT_EXEMPTION_CONFLICT`

All inherited V20 endpoints remain active.

## V21-C15 — Deferred boundaries, role neutrality, and freeze rule

R1/R2/R3 remain provider/model-neutral governed roles. EXP-ECC-6 and EXP-ECC-7 remain deferred.

V21 is design-only. It requires its own clean review before implementation/falsification may begin. Prior V20/ECC reviewer outputs do not qualify V21 and must not be counted as V21 review evidence.

Manual-review and live-attestation requirements remain unchanged.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
