# Workflow Drift and Parent-Child Impact Control — V9 Hardening Overlay

Status: **PROPOSED V9 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V9-C01 — Exact base binding

V9 is an additive hardening layer over exact V8 candidate:

- V8 candidate commit: `3db75f359854dc95285e18a75a72c533ecc455a8`
- V8 overlay blob: `86118314e55577d9d02393eb972a5e50cc00ee02`
- V8 precedence/evidence map blob: `188ae90b3ace17ef4293c5408d46065e127d3c51`
- V8 falsification extension blob: `cc91a00c2437cef0882d559c20bc8c99f33fa69e`

V5/V6/V7/V8 remain active only as resolved by the composite map plus this V9 overlay. Where V9 is stricter, V9 controls.

V9 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V9-C02 — Normative Clause Registry and extraction completeness proof

V8 mechanical precedence auditing is strengthened so correctness does not depend only on keyword extraction.

A root-governed `NormativeClauseRegistry` (`NCR`) is generated during candidate build from three independent sources:

1. syntactic normative extraction (`MUST`, `MUST NOT`, `SHALL`, `REQUIRED`, `PROHIBITED`, endpoint/authority/state definitions);
2. author-declared clause IDs embedded in V8+ documents and machine-derived stable IDs for legacy clauses;
3. semantic/static reference extraction of endpoint codes, object types, authority names, registry names, state names, and transition predicates appearing in candidate/test artifacts.

The candidate cannot freeze unless all three manifests reconcile.

`NormativeExtractionProof` contains:

- candidate commit and artifact digest set;
- syntactic clause manifest digest;
- author-declared/machine-derived clause manifest digest;
- semantic/reference manifest digest;
- endpoint/reference graph digest;
- missing-from-any-source set;
- multiply/conflictingly classified set;
- extraction algorithm/corpus version;
- adversarial extraction corpus digest;
- result `PASS | FAIL`;
- CompositeAuditAuthority signature.

A clause/reference appearing in any one source but missing from another is fail-closed until explicitly dispositioned. This prevents a norm written without listed keywords or an implicit endpoint reference from silently escaping the audit.

The adversarial extraction corpus MUST include normative instructions expressed without standard keywords, indirect endpoint references, aliases, headings-only constraints, table-cell constraints, and negative/prohibition paraphrases.

Failure emits `NORMATIVE_EXTRACTION_INCOMPLETE` and also causes `COMPOSITE_PRECEDENCE_AMBIGUOUS`.

## V9-C03 — Genesis acceptance as an explicit external qualification gate

V8's `GenesisTrustAssumption` remains an irreducible out-of-band boundary. V9 prevents it from becoming an implicit PASS.

Before any design candidate may be represented as execution-freezable, there MUST be a signed `GenesisQualificationRecord` with one of:

- `ACCEPTED_OUT_OF_BAND_ASSUMPTION`
- `REJECTED`
- `INSUFFICIENT_EVIDENCE`

The record binds:

- GenesisTrustAssumption ID/digest;
- guardian and genesis-notary identities;
- notarization package digest;
- root/storage/key-control architecture evidence digest;
- named accountable human/organization accepting the assumption;
- acceptance scope and expiry/review date;
- explicit statement that acceptance is not in-system proof of real-world independence;
- independent manual-review evidence reference when policy requires it.

No automated model/service may issue `ACCEPTED_OUT_OF_BAND_ASSUMPTION` as terminal qualification authority.

If the record is missing or `INSUFFICIENT_EVIDENCE`, execution freeze is blocked. This is not a failed cryptographic check; it is a bounded trust-assumption gate.

Root/notary key-storage architecture MUST demonstrate that an ordinary platform/cloud/org super-admin cannot invoke enough guardian/notary keys to satisfy threshold. Missing proof => `GENESIS_QUALIFICATION_INSUFFICIENT`.

## V9-C04 — Consequence Classification Authority (`CCA`)

A beneficiary, business-logic service, effector, or PRR policy cannot self-classify an operation as non-consequential.

RGA governs a `ConsequenceClassificationRegistry` containing every externally reachable or authority-relevant operation class and its consequence class:

- `READ_ONLY`
- `REVERSIBLE_INTERNAL`
- `IRREVERSIBLE_INTERNAL`
- `EXTERNAL_CONSEQUENTIAL`
- `TERMINAL_AUTHORITY`

Each classification requires:

- operation/route/capability ID;
- code/artifact/interface digest or version range;
- call-path owner;
- consequence class;
- required gateway/fencing mode;
- classification rationale/predicate ID;
- CCA approver quorum;
- activation/sunset sequence.

Default for any reachable operation absent from the registry is **consequential-deny**, not READ_ONLY.

Any new network-capable provider/client/connector call path is considered `EXTERNAL_CONSEQUENTIAL` until positively classified otherwise by CCA.

Changing an operation from a stricter class to a weaker class requires independent review/quorum and emits `CONSEQUENCE_CLASS_DOWNGRADE_REVIEWED` before activation.

Misclassification or absent classification emits `CONSEQUENCE_CLASSIFICATION_BLOCKED`.

## V9-C05 — Mandatory egress mediation

All outbound consequential provider/network effects MUST traverse a root-governed `EffectEgressControl` or a registered direct-effector enforcement boundary that is technically unable to dispatch without a valid active ConsequentialEffectorRegistry entry, EffectReservation, current fencing proof, and permitted consequence class.

Application/business logic credentials MUST NOT have direct provider credentials/network authority for consequential providers when the governed Effect Gateway is the required mediation path.

Qualification requires an egress inventory proving:

- approved provider destinations;
- credential ownership;
- route/gateway mediation;
- direct-call exceptions, if any;
- direct-call exception root authority and expiry.

Unknown/unmediated consequential egress emits `UNMEDIATED_EFFECT_PATH_BLOCKED` before provider side effect.

## V9-C06 — Provider Observation Authority and high-consequence fact independence

V8 ExternalEffectObservation is strengthened.

RGA governs an `EffectObservationAuthorityRegistry` (`EOAR`) defining which evidence sources may establish `OCCURRED` or `NOT_OCCURRED` per provider/operation/consequence class.

For `TERMINAL_AUTHORITY` or high-consequence `EXTERNAL_CONSEQUENTIAL` operations:

- operator assertion alone is never sufficient;
- authorization quorum alone is never factual evidence;
- source must be independently qualified and cryptographically/provenance bound;
- where provider supports it, provider-signed receipt/audit query is required;
- where provider does not support authoritative observation, result remains `INDETERMINATE` unless a separately qualified independent settlement/query source proves state;
- an `INDETERMINATE` result can never be converted to `NOT_OCCURRED` by policy or quorum.

Observation-source principal/admin/credential domains must be independent from the operator requesting retry and from the authorization quorum for high-consequence effects.

A compromised/revoked/unqualified source causes `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT` and no duplicate dispatch.

Observation freshness is bound to provider/operation semantics. A stale `NOT_OCCURRED` observation cannot authorize retry after its freshness window or after a later provider event could have occurred.

## V9-C07 — Predicate auditor independence from every root-threshold-capable subset

Predicate audit independence is evaluated against the complete set of currently root-threshold-capable guardian combinations.

`PredicateAuditorIndependenceProof` contains:

- active guardian set and threshold;
- enumerated threshold-capable control-domain combinations or a formally equivalent proof;
- predicate auditor principal/control/admin/credential/recovery/beneficial-owner domains;
- overlap analysis;
- activation sequence;
- proof result.

A predicate auditor quorum is invalid if the same infrastructure/control authority can both:

1. satisfy any active root threshold capable of changing predicate governance; and
2. control/impersonate enough predicate-audit principals to approve the predicate.

Independence is rechecked at predicate activation and every `PARENT_UNAFFECTED` decision using a predicate family whose auditor/control facts changed.

Failure emits `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`.

## V9-C08 — Emergency trigger registry and invocation ledger

V8 emergency constraints are strengthened from signed policy content to enforceable trigger/invocation controls.

RGA governs an `EmergencyTriggerRegistry` with an allowlist of trigger predicate IDs/versions and maximum scope/duration/invocation limits.

No free-form trigger text or wildcard trigger is executable.

Each emergency invocation creates an `EmergencyInvocationRecord` containing:

- policy ID/version;
- trigger predicate ID/version;
- trigger evidence digest;
- workflow/action scope;
- consequence class;
- invocation ordinal under policy;
- remaining invocation budget;
- start/expiry sequence/time;
- approver quorum;
- resulting action/event IDs.

Invocation count is enforced atomically. Exceeding the ceiling emits `EMERGENCY_INVOCATION_LIMIT_BLOCKED`.

A signed policy with trigger outside the registry, overly broad trigger evidence, or action outside exact allowlist emits `EMERGENCY_POLICY_SCOPE_REJECTED`.

Emergency constraint changes are versioned and cannot retroactively legalize an earlier invocation.

## V9-C09 — Evidence Profile Completeness Authority

Case evidence applicability is moved from mapping discipline to a mechanically complete registry.

A root/test-governor jointly governed `CaseRegistry` enumerates every WDPC case ID, candidate-introduced case, case version, and active status.

Every active case MUST have:

- exactly one CaseRegistry entry;
- exactly one current evidence-profile mapping version;
- at least `EP-BASE` and every mechanism profile derived from its referenced endpoint/object/authority graph;
- frozen-start profile digest in the run record.

`CompositePrecedenceAudit` compares:

- case IDs parsed from all active falsification artifacts;
- CaseRegistry IDs;
- CaseEvidenceProfileMap IDs.

Any set difference blocks freeze/execution with `EVIDENCE_PROFILE_INCOMPLETE`.

Executors cannot remove profiles. A profile reduction is a candidate change requiring new review and new test run.

## V9-C10 — Grandfatherability authority

Whether a criterion is grandfatherable is not ordinary policy-owner discretion.

RGA/PRR jointly govern a `CriterionMigrationRegistry` with, per criterion/action/evidence class:

- criterion ID/version;
- `grandfatherable = true | false`;
- allowed GrandfatherDecision dispositions;
- required independent quorum;
- activation/sunset sequence;
- rationale/evidence digest.

Changing `grandfatherable` from false to true is a permissive governance change requiring independent quorum and re-review of affected workflows. Policy owner/proposer/beneficiary cannot satisfy the quorum alone.

Missing registry entry defaults to `grandfatherable=false`.

## V9-C11 — Mechanical live-object inventory for policy rebind

WSA maintains a signed `LiveAuthorityObjectInventory` per workflow/checkpoint generated from authoritative stores and object registries, not from the migration requestor.

It enumerates every live authority-bearing/in-flight object instance and object class at rebind time.

`PolicyRebindDecision` is valid only if its disposition map exactly covers the inventory set. Set mismatch emits `REBIND_DISPOSITION_MISSING`.

New object classes become non-migratable by default until the rebind taxonomy/schema registry defines their allowed dispositions. No unknown class inherits a default.

The inventory digest is bound to the DGV rebind decision and WSA commit.

## V9-C12 — Causal Evidence Registry for cross-standard ordering

`CrossDomainOrderingService` may classify order only from registered causal evidence.

RGA governs a `CausalEvidenceRegistry` defining admissible evidence types (e.g. signed authoritative event references, shared causal request ID, explicit predecessor digest, authenticated external sequence) and their validation rules.

Ordering service cannot create substantive evidence; it only verifies and references registered evidence.

If evidence is missing, conflicting, forged, or does not prove strict order, output MUST be `CONCURRENT_REEVALUATION_REQUIRED`.

Attempted forced order from invalid evidence emits `CROSS_STANDARD_ORDERING_EVIDENCE_REJECTED`.

The ordering record remains evidence-only and cannot itself advance workflow or claim status.

## V9-C13 — Registered-effector end-to-end fencing attestation

Effector registration is insufficient unless enforcement is verified.

Before activation, every ConsequentialEffectorRegistry entry requires a signed `EffectorEnforcementAttestation` containing:

- effector/operation ID;
- enforcement mode;
- token-validation/gateway implementation digest;
- negative stale-token test digest;
- positive current-token test digest;
- downstream side-effect proof method;
- attesting authority independent from effector owner for high-consequence operations;
- activation/sunset sequence.

Missing/expired attestation => effector cannot activate.

A stale/deposed writer reaching the provider through a registered effector is a qualification failure even if registry metadata says fencing is enforced.

## V9-C14 — Unique-enforcement-path coverage threshold

Qualification requires more than one compound happy path.

For each critical mechanism ID, the coverage report MUST contain at least:

- one adversarial negative;
- one isolated positive;
- one cross-mechanism/compound positive or a documented reason why concurrency is not applicable;
- at least one recovery/failover positive when the mechanism has persistent/distributed state.

The test governor computes `MechanismCoverageRecord` from case-to-mechanism mappings and observed PASS evidence.

Missing category yields `MECHANISM_COVERAGE_INCOMPLETE` and blocks freeze.

No single case may satisfy all coverage categories for more than one mechanism unless the report separately demonstrates each mechanism's independent exercised endpoint/evidence.

## V9-C15 — Frozen interpretation rule

Every test run is interpreted only under the exact candidate, registry, endpoint-schema, CaseRegistry, evidence-profile, consequence-classification, provider-capability, observation-authority, causal-evidence, and root-governance digests frozen at run start.

Later versions cannot retroactively change PASS/FAIL/INSUFFICIENT_EVIDENCE of the old run. A changed interpretation requires a new run.

## V9-C16 — Machine-only legacy clause keys

Human section labels are non-authoritative display metadata. Composite maps and audits MUST use stable legacy clause keys derived from source blob SHA + normalized heading path + ordinal + canonical clause digest. Formatting/heading changes create a new source blob and therefore a new candidate mapping; they cannot silently reuse a legacy key by section number alone.

## V9-C17 — New endpoints

V9 adds root/owner-bound endpoint schemas for:

- `NORMATIVE_EXTRACTION_INCOMPLETE`
- `GENESIS_QUALIFICATION_INSUFFICIENT`
- `CONSEQUENCE_CLASSIFICATION_BLOCKED`
- `UNMEDIATED_EFFECT_PATH_BLOCKED`
- `EMERGENCY_INVOCATION_LIMIT_BLOCKED`
- `CROSS_STANDARD_ORDERING_EVIDENCE_REJECTED`
- `MECHANISM_COVERAGE_INCOMPLETE`

All must be registered before associated cases execute.

## V9-C18 — Freeze rule

V9 cannot freeze for execution while any Critical/High design finding remains unresolved under the governing review policy.

AI/model engineering reviews remain engineering evidence only and cannot by themselves satisfy a qualifying independent manual-review gate.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.