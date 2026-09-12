# Workflow Drift and Parent-Child Impact Control — V8 Hardening Overlay

Status: **PROPOSED V8 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V8-C01 — Exact base binding and precedence

V8 is an additive hardening layer over the exact V7 composite candidate:

- V7 candidate commit: `5b436e4bca26b041b9bfdf3526594c0234e9dc03`
- V7 hardening blob: `12b9cc651c91dabc2445f28ac3f6cb8cb9289eed`
- V7 active-clause map blob: `7800ce565b87f77efe736bf58e8e184d3d4dd88d`
- V7 falsification extension blob: `926d536d740469f0dee47626f67d15026b6d4ab3`
- V6/V5 artifacts remain active only as resolved by the V7 map plus this V8 overlay.

V8 is design/preregistered falsification material only. It is not runtime implementation evidence.

Where V8 is stricter, V8 controls. V8 MUST NOT silently revive a permissive V5/V6/V7 interpretation.

## V8-C02 — Mechanical composite precedence audit

Precedence completeness MUST be mechanically auditable rather than inferred by a reviewer.

A root-governed `CompositeAuditAuthority` produces a signed `CompositePrecedenceAudit` before a composite candidate may be frozen.

The audit contains:

- audit ID/schema version;
- exact composite candidate commit;
- ordered candidate artifact list and blob digests;
- extracted normative clause manifest digest;
- extracted endpoint-code manifest digest;
- active-clause-map digest;
- per-clause disposition `ACTIVE | NARROWED_BY | SUPERSEDED_BY | REFERENCE_ONLY`;
- per-endpoint owner/schema mapping;
- set of unmapped clauses;
- set of multiply/conflictingly mapped clauses;
- set of unmapped endpoint codes;
- set of endpoint codes referenced by cases but absent from EndpointSchemaRegistry;
- audit algorithm/version digest;
- audit result `PASS | FAIL`;
- signer/key/root-governance binding.

### V8-C02.1 — Stable legacy clause identity

Legacy V5/V6/V7 normative clauses do not require source-file rewrites. The composite compiler assigns stable clause identity from:

`(source_blob_sha, normalized_heading_path, clause_ordinal_within_heading, canonical_clause_text_sha256)`.

Any clause containing a normative keyword (`MUST`, `MUST NOT`, `SHALL`, `REQUIRED`, `PROHIBITED`) or defining an endpoint/authority transition is included in the manifest. Candidate-build tooling MAY include additional clauses, but may not omit a clause matching the normative extraction rule.

### V8-C02.2 — Fail-closed result

If any normative clause or endpoint lacks exactly one valid composite disposition, the CompositeAuditAuthority emits owner-signed `COMPOSITE_PRECEDENCE_AMBIGUOUS` and the candidate cannot freeze or execute qualification tests.

A prose reviewer statement cannot satisfy this endpoint.

The active-clause map itself is an input to this audit, not the source of authority for claiming that the audit passed.

## V8-C03 — Bounded genesis trust assumption and offline notarization

V8 explicitly acknowledges an irreducible root-of-trust boundary: no in-system registry can prove the real-world independence of the actors who create the first registry without circularity.

The project therefore defines a bounded `GenesisTrustAssumption` rather than pretending this problem is eliminated.

### V8-C03.1 — GenesisTrustAssumption

The genesis package MUST name:

- accountable bootstrap owner;
- five proposed root guardians and their asserted organizations/control domains;
- three offline genesis notaries who are not root guardians and will hold no runtime authority;
- the assumption that notary real-world identities and physical/offline signing controls are independent at the time of genesis;
- evidence package digest supporting that assertion;
- expiry condition: the assumption applies only to creation of the first RootGovernanceManifest and does not automatically validate later rotations;
- explicit statement that this assumption is out-of-band trust, not runtime-derived proof.

### V8-C03.2 — GenesisIndependenceNotarization

The first `RootGuardianIndependenceSnapshot` requires at least **2-of-3 offline genesis-notary signatures** over the same guardian-independence facts and ceremony transcript digest, in addition to the root-guardian threshold.

A genesis notary:

- cannot be a root guardian;
- cannot be a runtime WSA/DGV/PRR/RCB/DR/GEL/WAS/TestGovernor/Provenance/PGR authority;
- cannot share the asserted organization, cloud-root account, HSM-admin domain, identity-admin domain, or credential-recovery domain with any guardian it attests;
- has no power to authorize runtime transitions or later registry changes.

The only non-falsifiable boundary retained is the real-world truthfulness/physical independence of the offline genesis notaries at the ceremony. This assumption MUST be displayed in qualification documentation rather than converted into a hidden PASS.

If notarization is missing, self-attested, or control-domain overlap is established, the RGA verifier emits `GENESIS_ATTESTATION_REJECTED` and no trusted genesis state exists.

### V8-C03.3 — Infrastructure-provider override

Root keys MUST be stored such that an ordinary cloud/org/platform super-administrator cannot invoke enough guardian/notary keys to satisfy the threshold. If the claimed storage architecture does not provide this property, root independence is `INSUFFICIENT_EVIDENCE` for execution freeze.

## V8-C04 — Consequential Effector Registry and default deny

A root-governed `ConsequentialEffectorRegistry` inventories every downstream operation capable of a consequential external or authoritative side effect.

Each entry binds:

- effector ID/version;
- operation/action classes;
- consequence class;
- provider/service identity;
- `fencing_enforcement_mode = DIRECT_TOKEN_VALIDATE | WSA_EFFECT_GATEWAY_MEDIATED`;
- accepted fencing token schema/version;
- authoritative token source;
- provider idempotency capability reference where applicable;
- activation/sunset sequence;
- registry predecessor digest;
- root-governed signature/approval.

**Default is DENY.**

If a consequential action targets an effector/operation absent from the active registry, or the entry lacks a qualifying fencing mode, the Effect Gateway MUST emit `UNREGISTERED_EFFECTOR_BLOCKED` before reservation or network dispatch.

A PRR policy entry alone cannot create an effector registration.

An effector cannot downgrade itself from consequential to non-consequential.

## V8-C05 — Emergency policy content constraints

A valid signature does not make an emergency policy safe.

RGA maintains a signed `EmergencyPolicyConstraintRegistry` that defines hard bounds which ordinary EmergencyExceptionPolicy objects cannot exceed.

Every emergency policy MUST contain:

- exact emergency policy ID/version;
- exact allowed action classes (no wildcard or `ANY`);
- exact trigger predicate ID/version;
- maximum duration bounded by the root constraint registry;
- maximum invocation count;
- affected workflow scope;
- required quorum;
- mandatory audit/disclosure/escalation actions;
- explicitly excluded consequence classes;
- expiry/sunset sequence.

At minimum, ordinary emergency policies MUST NOT directly authorize:

- `TERMINAL_AUTHORITY`;
- release/production qualification;
- removal of preserved RED history;
- disabling GEL/WAS/provenance/oracle controls;
- unregistered external effectors;
- bypass of mandatory independent review.

Changing those exclusions requires a new RootGovernanceManifest revision and automatically invalidates any prior candidate freeze until independently re-reviewed.

An emergency policy with wildcard scope, unbounded duration, overly broad trigger, missing invocation ceiling, or forbidden consequence class is rejected as `EMERGENCY_POLICY_SCOPE_REJECTED` even if correctly signed.

## V8-C06 — Predicate audit authority independence from root guardians

V7 PredicateBootstrapAudit independence is extended to the root layer.

RGA maintains a `PredicateAuditAuthorityRegistry` whose audit quorum MUST:

- contain at least two predicate-audit principals;
- use principals that are not root guardians;
- use control, administrative, credential-admin, recovery-admin, and beneficial-owner domains distinct from the predicate proposer/policy owner/beneficiary;
- use audit principals whose control/admin domains do not overlap with any three-guardian set capable of satisfying the active root 3-of-5 threshold;
- be rechecked at predicate activation and at any `PARENT_UNAFFECTED` decision relying on a newly activated predicate family.

Failure emits `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`.

A root guardian may authorize the registry entry through RGA governance, but cannot itself count as the independent predicate auditor whose analysis supplies the bootstrap-audit result.

## V8-C07 — External OUTCOME_UNKNOWN fact/authority separation

V7 ExternalEffectReconciliationDecision is split into two non-substitutable objects.

### V8-C07.1 — ExternalEffectObservation

An `ExternalEffectObservation` is evidentiary only. It binds:

- observation ID;
- EffectReservation ID;
- provider/operation/effect identity;
- evidence source type `PROVIDER_SIGNED_RECEIPT | PROVIDER_AUDIT_QUERY | INDEPENDENT_SETTLEMENT_QUERY | OTHER_REGISTERED_SOURCE`;
- raw evidence digest/provenance;
- observer principal/service;
- observer administrative/control domain;
- observation result `OCCURRED | NOT_OCCURRED | INDETERMINATE`;
- observation time/sequence;
- signature.

The observation source/observer MUST be registered in ProviderCapabilityRegistry or a root-governed reconciliation-evidence registry and cannot be supplied solely by the operator requesting a retry.

A quorum decision cannot transform `INDETERMINATE` into a factual claim that the effect occurred or did not occur.

Missing/unqualified evidence emits `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT`.

### V8-C07.2 — ExternalEffectReconciliationDecision

The reconciliation decision is authorization only. It MUST reference one or more qualifying ExternalEffectObservation objects and choose a policy-allowed next action.

For non-idempotent effects:

- `OCCURRED` => no retry; reconcile local state to the observed provider effect;
- `NOT_OCCURRED` => a new dispatch may occur only through a new/continued authorized reservation under policy;
- `INDETERMINATE` => no automatic duplicate dispatch; remain `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED`, escalate, compensate, or require a policy-defined human resolution that still cannot assert an unproven provider fact.

The fact-finder and authorization quorum MUST be independent according to PRR/PIR policy for high-consequence effects.

## V8-C08 — GrandfatherDecision contract for newly mandatory criteria

WDPC-06 is narrowed.

A newly mandatory acceptance/falsification criterion may be grandfathered only through a signed `GrandfatherDecision` containing:

- exact old/new policy/criterion IDs and digests;
- affected workflows/candidates/evidence IDs;
- disposition `PRESERVE_EXACT | REVALIDATE_BEFORE_USE | INVALIDATE_AND_REISSUE | QUARANTINE_PENDING_DECISION`;
- reason code;
- effective sequence and expiry;
- deciding authority and independent quorum;
- predecessor decision digest.

`PRESERVE_EXACT` is allowed only if the new criterion's root/PRR definition explicitly marks grandfathering as permitted for that action/evidence class.

No missing/default GrandfatherDecision means preserve. Missing or unauthorized grandfathering emits `GRANDFATHER_DECISION_REJECTED`.

## V8-C09 — Positive rejection endpoint for terminal-authority claims

WDPC-11 is narrowed.

When a ChildImpactRecord, model/reviewer result, UI label, or other non-terminal artifact claims PASS/release/terminal authority without a valid separately authorized terminal transition, DGV MUST emit owner-signed `TERMINAL_AUTHORITY_CLAIM_REJECTED` referencing the claim artifact and proving unchanged terminal-authority state.

Absence of a transition alone is not sufficient PASS evidence for this falsification case.

## V8-C10 — Complete policy-rebind disposition taxonomy

WDPC-69 and all policy/schema migration paths use one closed disposition enum for each in-flight object:

- `PRESERVE_EXACT`
- `REVALIDATE_BEFORE_USE`
- `INVALIDATE_AND_REISSUE`
- `QUARANTINE_PENDING_DECISION`

No other/default disposition exists.

`PolicyRebindDecision` MUST enumerate every live in-flight object class present in the workflow, including at minimum:

- WCE;
- ApprovalObject;
- DriftDisclosureRecord/DeliveryReceipt;
- ChildImpactRecord/DependencyImpactRecord;
- DGVDecisionRecord;
- external request/result/EffectReservation;
- reviewer-context/provenance object;
- fallback activation;
- write lease/fencing object;
- cross-standard incident/order record.

Provider-request submodes (`CONTINUE_OLD_POLICY`, `CANCEL_AND_REISSUE`, `REVALIDATE_ON_RETURN`) MUST map deterministically onto the closed disposition enum and provider lifecycle.

An omitted live object class emits `REBIND_DISPOSITION_MISSING` and blocks migration.

## V8-C11 — Cross-standard simultaneous ordering without authority coupling

Workflow and EXP-K claim/evidence authorities retain separate local sequences. Equal-looking local sequence numbers do not imply a shared order.

A non-substantive root-governed `CrossDomainOrderingService` may issue a signed `CrossStandardOrderingRecord` binding:

- workflow event ID/local sequence;
- EXP-K claim/retraction event ID/local sequence;
- common correlation/causal inputs;
- ordering class `WORKFLOW_BEFORE_CLAIM | CLAIM_BEFORE_WORKFLOW | CONCURRENT_REEVALUATION_REQUIRED`;
- ordering evidence digest;
- global ordering record sequence;
- signature.

The ordering service cannot decide workflow or claim disposition.

If a material workflow-drift disclosure and claim-retraction/derived-claim invalidation are causally concurrent such that neither order is proven, the only permitted class is `CONCURRENT_REEVALUATION_REQUIRED`.

That state emits `CROSS_STANDARD_SIMULTANEOUS_REEVALUATION_REQUIRED`; both domains re-evaluate affected dependencies before either can infer permissive continuation from the other's prior state.

## V8-C12 — Clause traceability convention

All V8 normative clauses carry stable IDs (`V8-Cxx[.y]`).

For V5/V6/V7, machine identity is derived by the V8-C02 legacy clause-identity algorithm. Human section numbers are display aids only and MUST NOT be used as the sole machine key.

## V8-C13 — Evidence-profile applicability instead of “where applicable”

Qualification execution MUST use the V8 Case Evidence Profile Map. Each WDPC case has an explicit set of evidence profiles. The union of the fields required by those profiles is mandatory for that case.

An executor may not omit a field by reviewer judgment merely because a global checklist says “where applicable.”

Missing required profile evidence emits `EVIDENCE_PROFILE_INCOMPLETE` and the case cannot PASS.

The evidence-profile map is candidate-bound and mechanically audited for complete WDPC case coverage by CompositePrecedenceAudit/TestGovernor tooling.

## V8-C14 — Compound legitimate-operation control

V8 qualification MUST include a legitimate concurrent/compound positive scenario exercising multiple mechanisms at once, not only isolated happy paths.

At minimum the scenario combines:

- valid root key/policy rotation;
- policy migration of an active workflow;
- quorum-gated relationship/impact decision;
- one idempotent external effect;
- reviewer-context delivery;
- required disclosure/approval;
- WSA leader failover or lease renewal.

It must complete without false `R1_SELF_DRIFT_BLOCKED`, `QUORUM_INDEPENDENCE_REJECTED`, `UNREGISTERED_EFFECTOR_BLOCKED`, or other unrelated block while preserving all exact authority bindings.

## V8-C15 — Root-governed registry monotonicity and post-run immutability

Any registry that can change interpretation of an already executed test or governance object — including EndpointSchemaRegistry, GovernanceSchemaRegistry, EvidenceClassRegistry, CaseEvidenceProfileMap, TestGovernorAuthorityRegistry, ProviderCapabilityRegistry, PGR, ConsequentialEffectorRegistry, EmergencyPolicyConstraintRegistry, and CompositePrecedence rules — is versioned/append-only and bound by activation sequence.

A later registry version cannot retroactively legalize an earlier failing run. Each run is evaluated against the exact registry digests active at its frozen start. Post-run registry changes require a new test run.

## V8-C16 — Endpoint additions

V8 adds the following owner-bound endpoints, which MUST exist in EndpointSchemaRegistry before any corresponding case executes:

- `COMPOSITE_PRECEDENCE_AMBIGUOUS` — CompositeAuditAuthority;
- `GENESIS_ATTESTATION_REJECTED` — RGA genesis verifier;
- `UNREGISTERED_EFFECTOR_BLOCKED` — Effect Gateway/DGV;
- `EMERGENCY_POLICY_SCOPE_REJECTED` — RGA/PRR policy validator;
- `PREDICATE_AUDIT_INDEPENDENCE_REJECTED` — PGR/RGA verifier;
- `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT` — Effect Reconciliation Evidence Verifier;
- `GRANDFATHER_DECISION_REJECTED` — PRR/DGV;
- `TERMINAL_AUTHORITY_CLAIM_REJECTED` — DGV;
- `REBIND_DISPOSITION_MISSING` — PRR/DGV;
- `CROSS_STANDARD_SIMULTANEOUS_REEVALUATION_REQUIRED` — CrossDomainOrderingService + separate domain revalidation records;
- `EVIDENCE_PROFILE_INCOMPLETE` — Test Governor.

## V8-C17 — Review and freeze condition

V8 cannot freeze for execution unless:

1. the exact V5+V6+V7+V8 composite candidate passes a fresh independent design review under the governing review policy;
2. CompositePrecedenceAudit is preregistered and has no unmapped normative clause/endpoint in design artifacts;
3. WDPC-01…135 remain mandatory regressions under V8 narrowing;
4. all V8-added cases are preregistered with owner/schema-bound endpoints;
5. no unresolved Critical/High design finding remains;
6. AI-generated engineering feedback remains evidence-only and is not relabeled as the qualifying manual-review gate;
7. no design review is represented as runtime implementation evidence.

This overlay grants no merge, release, production, qualification, adjudication, or terminal authority.
