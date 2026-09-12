# Workflow Drift and Parent-Child Impact Control — V20 Deterministic Authority Proof

Status: **PROPOSED V20 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V20-C01 — Exact base and precedence

V20 is additive over exact V19 candidate `c64379c9a7c5b2f80cc979a19cc39b3429a53fc9`.

All active V5–V19 controls remain in force except where V20 narrows ambiguity in the stricter fail-closed direction. Nothing in V20 grants implementation qualification, execution freeze, merge, release, deployment, or terminal authority.

## V20-C02 — Absolute root-threshold non-weakening

For every root-governed threshold/packet ledger, policy registry, mutation authority, emergency path, repair path, migration path, reset path, or recovery path, the effective mutation threshold may never become weaker than the immediately preceding effective mutation threshold for the same governed object class.

A policy change that would lower the effective threshold is invalid at the policy-change boundary itself, even when the change is approved under the old threshold and even when no immediate ledger mutation follows.

Permitted policy transitions are only:

- threshold unchanged with otherwise valid governed change; or
- threshold strengthened prospectively.

Any lower threshold is rejected before activation and can never become the active basis for later mutation.

Failure endpoint: `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`.

## V20-C03 — Governed authority-bearing publication classification

Authority-bearing audit/publication state is defined by a root-governed `AuthorityPublicationClassRegistry`, not by the candidate, implementation under test, local operator, or ungoverned policy text.

The registry binds each publication/event class to:

- class identity and schema/version;
- whether it can present, imply, expose, or authorize a governance outcome;
- mandatory atomic-bound inclusion status;
- approving root-policy version and principal threshold;
- effective sequence;
- predecessor/version digest.

A publication/event class that can expose an authoritative or apparently authoritative governance decision is mandatory atomic state. Unknown or unclassified publication classes that participate in a material transition are fail-closed and treated as authority-bearing until governed classification proves otherwise.

Failure endpoint: `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID`.

## V20-C04 — Deterministic reconciliation precedence table

`REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` reconciliation evaluates exact evidence in this fixed order. The evaluator may not choose a different branch by policy preference.

### Step 1 — structural conflict

If authoritative ledger, uniqueness, threshold-record, transaction/consensus identity, publication identity, predecessor/sequence, or required witness evidence contains mutually contradictory committed facts for the same intent/candidate/gate tuple, return `RECONCILIATION_CONFLICT`.

Examples include two different committed consumption identities, committed ledger state with incompatible uniqueness state, committed publication with a different decision identity, or a required current witness proving a different lineage.

### Step 2 — complete committed identity

If one and only one complete commit exists across every mandatory atomic-bound component and any required current witness confirms the same lineage/decision identity, return `COMMIT_CONFIRMED_EXISTING` and never count again.

### Step 3 — authoritative proof of absence

Return `NO_COMMIT_CONFIRMED` only if every authoritative mandatory component that would contain the commit proves absence for the exact intent/candidate/gate/idempotency tuple, no authority-bearing publication exists, uniqueness state is unused, and any required witness/current checkpoint is consistent with that absence.

### Step 4 — insufficient evidence

If evidence is missing, stale, unavailable, lagging, unclassified, or cannot distinguish committed from non-committed state without contradiction, return `INSUFFICIENT_EVIDENCE`.

Lost acknowledgement, timeout, process failure, or transport error never proves absence.

The decision table itself is root-governed/versioned and its version is bound into each reconciliation record.

## V20-C05 — Independently governed dependency-universe derivation

`eligible_dependency_set` must be produced by a root-governed `DependencyUniverseAuthority` whose rule set and implementation identity are independent from the corpus/algorithm generation being changed and from the candidate/beneficiary of the dependent decision.

The authority enumerates dependency-eligible decision classes and concrete decision identities from authoritative registries/state using exact class/version/rule bindings. The corpus/algorithm under review may supply evidence but cannot define, filter, suppress, or finalize the eligible universe.

Completeness requires:

- independently derived `eligible_dependency_set`;
- `indexed_dependency_set`;
- `revalidated_or_exempt_set`;
- empty `eligible - indexed` difference;
- empty `indexed - revalidated_or_exempt` difference.

Missing universe-authority evidence is `INSUFFICIENT_EVIDENCE`; a non-empty difference is `CANONICAL_DEPENDENCY_INDEX_INCOMPLETE`.

## V20-C06 — Independent-support freshness and conflict rules

Every `IndependentSupportRegistry` exemption is revalidated at the decision that consumes it. The platform checks exact support identities, evidence classes, expiry, revocation, source/provider/principal independence, generation binding, and current conflict status.

An expired, revoked, stale, superseded, self-supporting, or otherwise non-current exemption cannot be grandfathered.

If multiple exemption records conflict for the same dependent/generation pair, the dependent is `REVALIDATION_REQUIRED` until a root-governed conflict-resolution rule produces one current non-conflicting record. Agreement among stale/invalid exemptions does not cure the conflict.

Failure endpoint: `INDEPENDENT_SUPPORT_EXEMPTION_INVALID`.

## V20-C07 — Exact witness quorum, sequence and key lifecycle

A witness policy binds an exact quorum rule and every qualifying witness member to:

- witness identity and governance domain;
- public-key / credential identity or equivalent authority identity;
- key version and validity interval;
- revocation/compromise state;
- control, administration, credential, recovery, and mutation domains;
- observed authoritative ledger sequence and digest;
- checkpoint identity and issuance sequence/time;
- maximum permitted sequence lag and, where time is used, maximum permitted time lag;
- required continuity predecessor.

A witness is current only when its checkpoint satisfies the exact sequence/digest binding and every configured currentness bound. A revoked, compromised, expired, superseded, non-independent, or over-lag witness does not count toward quorum.

Key rotation requires governed continuity from the previous accepted key/witness identity to the replacement. Replay of a checkpoint signed by a revoked/superseded key is invalid even if the historical signature was valid.

If independence fails with sufficient evidence, return `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`. If required witness evidence is absent/unavailable such that independence/currentness cannot be evaluated, return `INSUFFICIENT_EVIDENCE`.

## V20-C08 — Deterministic endpoints for witness/migration/reset cases

The following endpoint precedence is fixed:

- proven non-independent / revoked / compromised / stale beyond governed bound witness → `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID`;
- witness required but unavailable or evidence insufficient to establish currentness/independence → `INSUFFICIENT_EVIDENCE`;
- migration/compaction while required witness is unavailable → preparation may occur, but authority activation remains `INSUFFICIENT_EVIDENCE` until continuity is proven;
- reset/repair/migration policy uses a weaker threshold → `ROOT_GOVERNANCE_THRESHOLD_WEAKENING_REJECTED`;
- threshold is unchanged/stronger but approving principal set is below required active threshold → `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED`.

## V20-C09 — Execution attestation anti-replay and issuer binding

Every authority-bearing `ControlExecutionAttestation` binds at minimum:

- exact control identity, version and digest;
- exact executable/runtime path identity and digest/version;
- exact candidate identity;
- exact workflow/gate/action identity;
- exact action-instance digest or immutable intent identity;
- invocation/execution identity;
- execution result and verification result;
- attestation issuer identity and evidence class;
- issuance sequence/time and expiry/currentness where applicable.

The implementation under test cannot self-grant a qualifying attestation unless the governing policy explicitly permits that issuer class and independent verification requirements are still satisfied. Reusing a valid attestation for a different action, candidate, control version, runtime path, or action-instance digest is invalid.

Failure endpoint: `CONTROL_EXECUTION_EVIDENCE_REQUIRED`.

## V20-C10 — Secret-safe proof-view predicate

Canonical tool/MCP configuration proof views expose only governed secret-safe fields. A root-governed `SecretExposurePolicy` defines forbidden raw-secret classes and allowed non-reversible attestations/fingerprints.

Before a proof view is reviewable/qualifying, a deterministic non-exposure predicate verifies that:

- no raw secret, token, password, private key, credential material, or recoverable secret encoding is present;
- credential fingerprints/attestations use an approved non-reversible scheme and do not embed recoverable secret material;
- canonical configuration identity can be checked without disclosing secret values.

Failure endpoint: `CONFIG_PROOF_SECRET_EXPOSURE_REJECTED`.

## V20-C11 — Exact activation scope semantics

Capability activation is interpreted by exact resource/power identifiers and governed scope schemas. Wildcards, aliases, parent-resource expansion, derived resource names, or broad textual interpretations are not permitted unless explicitly present in the governed activation record and allowed by the active activation-schema policy.

Any attempted scope broadening beyond exact approved project/workflow/resource/power/expiry boundaries returns `CAPABILITY_ACTIVATION_NOT_AUTHORIZED`.

## V20-C12 — Proof-view additions

Reviewer-safe V20 proof views expose, as applicable:

- old and proposed root mutation thresholds plus non-weakening result;
- authority-publication registry class/version and atomic inclusion result;
- reconciliation decision-table version and each branch predicate;
- dependency-universe authority identity/version, source registries, eligible/indexed/revalidated-or-exempt sets and differences;
- independent-support freshness/revocation/conflict result;
- witness quorum members, independence result, exact sequence/digest, lag bounds, key version/revocation/currentness and continuity result;
- control attestation control-version/runtime-path/action-instance/issuer binding;
- secret non-exposure predicate and approved fingerprint scheme identity;
- exact activation scope-schema interpretation result.

Missing mandatory values are `NOT_PRESENT` or `INSUFFICIENT_EVIDENCE`, never implicit PASS.

## V20-C13 — Deferred boundaries and role neutrality

R1/R2/R3 remain provider/model-neutral governed roles. No provider/model is hardcoded to a role.

EXP-ECC-6 and EXP-ECC-7 remain deferred. V20 does not claim live external-review/provider integration, qualifying manual-review transport, production trust-root separation, or a live learned-artifact promotion/retraction pipeline.

## V20-C14 — New endpoint

- `AUTHORITY_PUBLICATION_CLASSIFICATION_INVALID`
- `CONFIG_PROOF_SECRET_EXPOSURE_REJECTED`

All inherited V19 endpoints remain active.

## V20-C15 — Freeze rule

V20 is design-only. It requires its own clean review before implementation/falsification may begin. Earlier V19 or ECC review outcomes do not qualify V20.

Manual-review and live-attestation requirements remain unchanged.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
