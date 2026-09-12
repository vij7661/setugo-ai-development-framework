# V8 Composite Precedence Audit and Case Evidence Profile Map

Status: **PROPOSED V8 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V8-M01 — Purpose

This artifact supplies two machine-oriented inputs required by the V8 hardening overlay:

1. the composite precedence-audit source set; and
2. the exact evidence-profile applicability rules for WDPC execution.

It does not itself claim that a CompositePrecedenceAudit has been executed. The runtime/test implementation must generate the owner-signed audit object defined by V8-C02.

## V8-M02 — Composite source set

The V8 candidate is composed in this strict order:

1. V5 base standard — `standards/conversation-drift-parent-child-impact-control.md`
2. V5 base matrix — `experiments/governed-platform/conversation-drift-parent-child-falsification-v1.md`
3. V6 hardening overlay — `standards/conversation-drift-parent-child-impact-control-v6-hardening.md`
4. V6 falsification extension — `experiments/governed-platform/conversation-drift-parent-child-falsification-v6-extension.md`
5. V7 hardening overlay — `standards/conversation-drift-parent-child-impact-control-v7-hardening.md`
6. V7 active-clause map — `standards/conversation-drift-parent-child-v7-active-clause-map.md`
7. V7 falsification extension — `experiments/governed-platform/conversation-drift-parent-child-falsification-v7-extension.md`
8. V8 hardening overlay — `standards/conversation-drift-parent-child-impact-control-v8-hardening.md`
9. this V8 precedence/evidence map
10. V8 falsification extension — `experiments/governed-platform/conversation-drift-parent-child-falsification-v8-extension.md`

Interpretation rule:

- V7 active-clause map resolves V5/V6/V7 precedence;
- V8 hardening narrows that resolved composite;
- V8 does not silently reactivate anything superseded by V7;
- V8-MAP rows below are execution-evidence requirements, not authority to change substantive policy.

At freeze/packet creation, the candidate manifest MUST bind exact Git blob SHAs for every source above. A source path without exact blob binding makes CompositePrecedenceAudit fail.

## V8-M03 — Evidence profiles

Every WDPC case inherits `EP-BASE` and `EP-ORACLE`. Additional profiles are exact and listed below.

### EP-BASE — universal authoritative proof

Required for every case:

- candidate commit and composite artifact-manifest digest;
- case ID and execution evidence class;
- opaque fixture ID;
- actor/service/principal identity;
- root/parent/task/workflow IDs as defined by fixture;
- candidate/policy/checkpoint bindings active for fixture;
- frozen expected endpoint ID/schema digest;
- observed owner-signed endpoint record or explicit owner-signed no-authority endpoint;
- authoritative state/sequence before and after;
- GEL event/record binding for governed transitions/rejections;
- PASS/FAIL;
- preserved prior RED history.

### EP-ORACLE — test-governor proof

Required for every case:

- FrozenExpectedEndpoint ID/digest;
- test-governor authority/version;
- proof expected endpoint was frozen before actor execution;
- proof actor did not receive oracle metadata;
- post-run oracle-integrity check.

### EP-ROOT — root/registry authority proof

Required fields:

- RootGovernanceManifest digest/version;
- relevant root-governed registry digests;
- guardian/notary/control-domain facts when genesis/root independence is under test;
- activation/revocation sequences;
- threshold/quorum proof.

Applies to: `WDPC-23,76,77,82,89,93,95,96,97,99,100,103,105,106,108,110,113,114,115,117,118,119,121,126,127,128,132,133,134,135`.

### EP-WCE-DGV — WCE/proposal/decision application proof

Required fields:

- WCE ID/digest/schema/nonce;
- WSA StateSnapshot digest;
- PRR PolicySnapshot digest;
- R1Proposal/action digest where applicable;
- DGVDecisionRecord ID/digest/lifecycle;
- DecisionConsumptionLedger result when decision is applied;
- final-authority revalidation result.

Applies to: `WDPC-18,20,21,22,34,36,44,49,50,55,56,57,58,65,76,84,87,93,95,98,99,100,108,117,133,134`.

### EP-DEP — dependency/PGR/impact proof

Required fields:

- DependencyGraphSnapshot root;
- mandatory dependency-template version;
- relevant PGR predicate IDs/versions;
- PredicateBootstrapAudit where required;
- changed/affected/unaffected/stale/revalidation/insufficient sets;
- DependencyImpactRecord/ChildImpactRecord IDs;
- graph-completeness result.

Applies to: `WDPC-04,05,06,08,10,24,25,27,42,64,75,88,101,102,119,120`.

### EP-QUORUM — confirmer/independence proof

Required fields:

- proposer identity;
- confirmer identities/keys;
- PrincipalIndependenceRegistry version;
- control/admin/credential-admin/recovery-admin/beneficial-owner/alias groups;
- final-commit independence recheck;
- quorum result.

Applies to: `WDPC-08,10,43,54,61,64,83,103,114,119,121,126`.

### EP-REVIEW — reviewer context/provenance proof

Required fields:

- ReviewerContextRecord ID/digest;
- whitelist schema/version;
- SourceProvenanceAttestation chain;
- provenance authority version;
- artifact payload digest;
- side-channel normalization result;
- reviewer identity/scope.

Applies to: `WDPC-07,19,53,68,73,78,106,115,125,133,134`.

### EP-EXTERNAL — external request/effect proof

Required fields:

- request/intent IDs and idempotency key;
- EffectReservation ID/state;
- ProviderCapabilityRegistry entry/version;
- provider request/response/effect identity;
- dispatch authority/leader/fencing proof where relevant;
- effect result/effect-application record;
- ExternalEffectObservation and reconciliation decision when OUTCOME_UNKNOWN occurs.

Applies to: `WDPC-18,21,29,31,32,33,38,39,69,82,92,104,122,123,124`.

### EP-FENCE — lease/consensus/downstream effector proof

Required fields:

- WriteLease ID/fencing token;
- WSA consensus/leader epoch;
- pre-state/checkpoint binding;
- downstream effector ID/registry entry;
- fencing enforcement mode;
- downstream accepted/rejected token proof.

Applies to: `WDPC-13,14,17,29,37,70,81,91,105,116,123,124`.

### EP-DISCLOSE — disclosure/approval/assurance proof

Required fields:

- consequence class;
- DriftDisclosureRecord/DeliveryReceipt IDs;
- disclosure target/recipient binding;
- escrow state where applicable;
- ApprovalObject ID;
- AuthenticationAssuranceSnapshot;
- minimum required assurance;
- final commit assurance/revocation check;
- emergency policy/constraint registry if exception invoked.

Applies to: `WDPC-35,51,52,66,67,79,89,90,107,108,112,126,127`.

### EP-MIGRATION — policy/schema/object rebind proof

Required fields:

- old/new policy/schema digests;
- PolicyRebindDecision ID;
- complete live object inventory;
- per-object closed-enum disposition;
- grandfather decision where applicable;
- migration activation sequence;
- evidence of no implicit/default rebind.

Applies to: `WDPC-06,23,35,69,82,89,95,99,113,117`.

### EP-WAS — historical completeness/tamper proof

Required fields:

- GEL authoritative sequence range;
- AuthoritativeTransitionCommitment where applicable;
- Merkle inclusion proof;
- WAS anchor/range identity;
- previous/next contiguous range checks;
- trusted history start;
- gap/overlap/duplicate/witness-rollback result.

Applies to: `WDPC-28,41,60,80,94,109,129,130,131`.

### EP-XSTD — cross-standard authority/ordering proof

Required fields:

- workflow disposition record/signature;
- EXP-K claim/evidence disposition/signature;
- administrative/credential-domain independence proof;
- CrossStandardIncidentRecord;
- ordering record when events are concurrent/causally ambiguous;
- proof neither disposition grants the other's authority.

Applies to: `WDPC-74,86,110,132`.

### EP-ECLASS — evidence-class and runtime-qualification proof

Required fields:

- immutable EvidenceClassRecord;
- original class at test start;
- attempted reclassification if any;
- test-governor decision;
- proof design evidence did not qualify runtime enforcement.

Applies to: `WDPC-47,72,85,128`.

## V8-M04 — Applicability algorithm

For case `C`, required evidence is:

`EP-BASE ∪ EP-ORACLE ∪ every additional profile whose Applies-to set contains C`.

There is no executor discretion to remove a required profile.

If a V8-added case is absent from this artifact, the V8 falsification extension MUST state its explicit profile set inline. Before execution freeze, CompositePrecedenceAudit/TestGovernor MUST verify every WDPC-01…latest case has either:

- an explicit entry through the profile sets above; or
- an explicit V8-extension profile assignment.

Missing mapping emits `EVIDENCE_PROFILE_INCOMPLETE`.

## V8-M05 — Mechanical precedence audit inputs

The CompositePrecedenceAudit implementation MUST ingest:

- all source artifacts listed in V8-M02;
- V7 active-clause map;
- V8 hardening clauses;
- EndpointSchemaRegistry active version;
- this evidence-profile map;
- complete WDPC case registry.

It MUST reject freeze if:

- a normative clause has zero or multiple conflicting active dispositions;
- an endpoint code referenced in any matrix is unregistered;
- a registered endpoint owner/schema cannot be resolved;
- a WDPC case lacks evidence-profile coverage;
- an older clause superseded by V7/V8 is reactivated by omission;
- a source artifact path/digest is not exact-bound.

## V8-M06 — Human-readable section references

Human references such as “V6 §18” are convenience labels only. Machine traceability uses source blob SHA + normalized heading path + clause ordinal + canonical clause text digest as defined in V8-C02.1.

This artifact grants no merge, release, production, qualification, adjudication, or terminal authority.
