# Workflow Drift and Parent-Child Impact Control — V6 Hardening Overlay

Status: **PROPOSED V6 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Exact base binding and precedence

This V6 overlay is bound to the V5 base candidate:

- V5 candidate commit: `08d7e745aaabaffb9b36b448012e9248b4217d74`
- V5 standard blob: `596a9244c779645ae09e98fcedc0aed29dddb290`
- V5 matrix blob: `65423e8cd2aee26c484964aed152eb18d40890f7`

V6 preserves those V5 artifacts unchanged as historical/base design evidence. This overlay adds stricter rules. Where a V6 rule conflicts with V5, the stricter V6 rule governs the V6 candidate. Where V6 is silent, V5 remains applicable.

V6 is still design/preregistered falsification work. It is not runtime implementation evidence.

## 2. Root Governance Authority (`RGA`)

The GovernanceKeyRegistry, initial PRR PolicySnapshot, trust-domain identities, schema registry, predicate registry, and witness identities require a root authority that is outside R1, WSA, DGV, PRR, RCB, DR, GEL, and WAS runtime authority.

### 2.1 Root bootstrap ceremony

Bootstrap MUST create a signed `RootGovernanceManifest` containing:

- root governance manifest ID and schema version;
- exact repository/design revision used for bootstrap;
- root guardian public keys and principal identities;
- `control_domain_id` for each guardian;
- threshold policy;
- allowed root-governance object types;
- initial GovernanceKeyRegistry digest;
- initial PRR PolicySnapshot digest;
- initial schema-registry digest;
- initial PredicateRegistry digest;
- initial WAS identity/key digest;
- ceremony transcript digest;
- predecessor root-manifest digest, null only for genesis;
- root threshold signatures.

Genesis and root-policy rotation require **3-of-5 root guardian signatures spanning at least three independent control domains**. No guardian may control more than one root key. R1, WSA, DGV, and PRR runtime principals are prohibited root guardians.

A root guardian key MUST be hardware-backed or offline-held with independently auditable key-use policy. Runtime service credentials cannot invoke root keys.

Without a valid threshold-signed RootGovernanceManifest, WSA/DGV/PRR objects are `UNTRUSTED_BOOTSTRAP_STATE` and cannot authorize consequential execution.

### 2.2 Root change control

Changes to the GovernanceKeyRegistry root, PRR authority model, schema sunset rules, predicate governance, or WAS witness identity require a new threshold-signed RootGovernanceManifest linked to the previous root digest. Runtime components cannot self-bootstrap or self-expand root authority.

## 3. Administrative-domain separation

Service-key separation is necessary but not sufficient.

Each of WSA, DGV, and PRR MUST have:

- distinct service principal;
- distinct signing-key handle;
- distinct write credential;
- distinct `administrative_domain_id`;
- HSM/KMS policy that prevents one service or one ordinary administrator from invoking another service's signing key;
- separate audit stream for privileged key use.

No single non-root infrastructure principal may possess or assume administrative authority over more than one of WSA, DGV, and PRR production signing domains.

Any operation that simultaneously changes trust configuration for two or more of WSA/DGV/PRR requires root-governance approval or a threshold change-control policy pre-authorized by RGA.

A shared host, cluster, cloud account, or orchestrator is not qualified if one compromise principal can obtain all three authority paths.

## 4. DGV decision ledger and WSA application protocol

V6 replaces any ambiguous cross-service nonce handling with an idempotent decision-application protocol.

### 4.1 `DGVDecisionRecord`

Every DGV decision contains:

- decision ID;
- decision nonce;
- WCE ID/digest;
- R1Proposal/action digest;
- exact WSA pre-state digest/sequence;
- exact PRR policy digest;
- actor principal/role/key;
- decision `ALLOW | DENY | INSUFFICIENT_STATE`;
- reason code;
- lifecycle `PREPARED | APPLIED | SUPERSEDED | EXPIRED`;
- created sequence/time;
- DGV signature.

DGV persists `PREPARED` before WSA application. Decision ID and decision nonce are globally unique within workflow scope.

### 4.2 WSA `ApplyDecision`

WSA exposes an idempotent logical operation `ApplyDecision(decision_id)`.

WSA MUST atomically:

1. verify DGV signature/key/role;
2. verify decision is `ALLOW`;
3. verify exact current pre-state/policy/action/actor binding;
4. verify decision not expired/superseded;
5. verify `decision_id` has not been applied to another transition;
6. commit the state transition;
7. persist `(decision_id, transition_id, post_state_digest)` in a durable `DecisionConsumptionLedger` in the same transactional/consensus commit.

Replaying the same valid decision after a crash returns the same committed `transition_id` and post-state digest with event `DECISION_REPLAY_DEDUPLICATED`; it never creates a second transition.

A different pre-state, action, actor, policy, or expired/revoked authority rejects the decision.

DGV may later mark its local record `APPLIED` from WSA's durable result via outbox/reconciliation, but DGV local loss cannot erase WSA consumption history.

## 5. Schema authority, sunset, and downgrade prevention

RGA owns the signed `GovernanceSchemaRegistry`.

For each signed object type it defines:

- schema ID/version;
- canonical schema digest;
- `min_version_for_new_authority_use`;
- supported historical verification versions;
- activation sequence;
- sunset sequence;
- migration rules;
- prohibited downgrade paths.

After sunset, old-schema objects remain historical evidence only and are rejected for new consequential authority use even if their signatures are valid.

Schema version migration cannot be implicitly inherited across WCE, ApprovalObject, ChildImpactRecord, DGVDecisionRecord, PolicyRebindDecision, disclosure, or reviewer-context objects.

## 6. Trusted time and freshness precedence

Authority freshness is sequence-first.

- WSA/PRR sequence and digest equality take precedence over wall-clock time.
- Expiry additionally uses a signed trusted-time source or authenticated platform time service whose identity is root-governed.
- PRR specifies bounded clock-skew tolerance per object class, but RGA defines the maximum permitted tolerance.
- An object with stale sequence/digest is rejected even if its wall-clock expiry appears valid.
- An object outside permitted time/skew is rejected even if sequence matches when the object class requires expiry.

Clock rollback or source disagreement produces `TIME_AUTHORITY_CONFLICT_BLOCKED` for authority uses dependent on time.

## 7. Predicate Governance Registry (`PGR`)

Dependency soundness cannot be delegated to the policy owner that benefits from a permissive result.

RGA establishes a signed `PredicateGovernanceRegistry` separate from ordinary PRR policy content.

Every validation predicate contains:

- predicate ID/version/digest;
- executable or formally specified deterministic logic digest;
- allowed node/edge types;
- required inputs;
- output domain;
- materiality semantics;
- property/adversarial test corpus digest;
- approving predicate-governance principals;
- activation/sunset sequence;
- predecessor predicate digest.

Creation or change of a predicate that can mark parent-progression evidence `UNCHANGED_VALID` or `PARENT_UNAFFECTED` requires at least two predicate-governance approvers independent of the proposing policy owner and beneficiary workflow actor.

### 7.1 Dependency completeness

Every candidate/policy/gate/evidence object type has a root-governed dependency-class template defining mandatory dependency classes. A `DependencyGraphSnapshot` is invalid if a mandatory class is omitted.

DGV MUST compare the concrete graph to the mandatory template before staleness evaluation. Missing required node/edge classes produce `DEPENDENCY_GRAPH_INCOMPLETE_BLOCKED`.

Cycles are either prohibited by template or evaluated with a deterministic strongly-connected-component/fixpoint algorithm. Traversal may not silently stop at a cycle.

`PARENT_UNAFFECTED` requires:

1. complete graph/template validation;
2. active PGR predicates;
3. full reverse dependency closure/fixpoint;
4. no relevant `STALE`, `REVALIDATION_REQUIRED`, or `INSUFFICIENT_DEPENDENCY_EVIDENCE` nodes;
5. required quorum/impact authority.

## 8. Quorum identity and conflict-of-interest model

A distinct key is not automatically an independent confirmer.

The signed `PrincipalIndependenceRegistry` binds each confirmer principal to:

- principal ID;
- human/service identity;
- `control_domain_id`;
- `administrative_domain_id`;
- `credential_admin_domain_id`;
- `beneficial_owner_or_sponsoring_authority_id`;
- alias/service-account group ID;
- permitted confirmer roles;
- activation/revocation sequence.

For any decision that removes a mandatory gate or declares `PARENT_UNAFFECTED` where progression was blocked:

- proposer and confirmer cannot overlap;
- R1 cannot be a confirmer;
- at least two confirmers are required;
- confirmers must have distinct principal IDs;
- confirmers must span at least two `control_domain_id` values;
- confirmers cannot share the same alias/service-account group;
- confirmers cannot share the same credential-admin domain when that domain could impersonate both;
- a direct beneficiary actor cannot satisfy quorum;
- role/key status is rechecked at final WSA commit.

Failure emits `QUORUM_INDEPENDENCE_REJECTED` and cannot be relabeled as ordinary insufficient evidence.

## 9. External effect exactly-once boundary

Internal idempotency does not prove external provider effects are exactly once.

Before dispatching any consequential external side effect, the Effect Gateway MUST create a durable `EffectReservation` containing:

- intent ID/idempotency key;
- workflow/task/candidate/policy binding;
- provider/operation identity;
- provider idempotency capability;
- normalized request digest;
- reserved effect ID;
- lifecycle `RESERVED | DISPATCHED | CONFIRMED | OUTCOME_UNKNOWN | CANCELLED`;
- reservation sequence;
- predecessor digest.

### 9.1 Idempotent provider path

If the provider supports idempotency, the same provider idempotency key MUST be reused across retries. Provider response identity/proof is stored before governance effect application.

### 9.2 Non-idempotent or ambiguous provider path

If the provider does not provide a qualifying idempotency contract, the gateway MUST use at-most-once dispatch and MUST NOT automatically retry after an ambiguous post-dispatch failure. The state becomes `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED` until deterministic reconciliation proves whether the provider effect occurred.

A governance retry cannot create a second external provider effect merely because the local effect record is missing.

## 10. Linearizable WSA and split-brain fencing

WSA mutation authority MUST be backed by a linearizable consensus/quorum system or equivalent single-writer primitive with externally testable safety.

Fencing-token allocation and state commit are quorum-committed in the same authoritative state machine.

Rules:

- no quorum => no new lease/token and no consequential write;
- only the current quorum-elected leader/single writer may issue tokens;
- token is monotonically increasing within mutation scope;
- token and checkpoint/pre-state are validated at commit;
- a deposed/partitioned writer cannot commit even with a previously current token;
- split-brain attempts are preserved as rejected events.

A lease holder with the current token still fails if policy/candidate/checkpoint/pre-state binding changed.

## 11. Reviewer provenance attestation and side-channel control

RCB MUST NOT trust self-declared provenance tags from an artifact producer.

Every artifact/context source entering an independent-review packet carries a signed `SourceProvenanceAttestation` from an ingestion/provenance service separate from the producing reviewer/worker. It binds:

- source object ID/digest;
- origin service/principal;
- workflow/task/reviewer scope;
- allowed-use class;
- prohibited cross-review origin flags;
- ingestion sequence;
- source chain/predecessor digest;
- provenance-service signature.

RCB validates the provenance chain to signed WSA/GEL/PRR state. Forged or missing provenance becomes `REVIEW_CONTEXT_REJECTED_LEAKAGE` or `INSUFFICIENT_REVIEW_PROVENANCE`.

Before adjudication, reviewer context surfaces MUST normalize or suppress independence-sensitive side channels including other-reviewer completion count, ordering, provider identity, timing, file/fixture names, expected result labels, and free-form metadata unless explicitly required by policy.

Fixture handles are random opaque IDs unrelated to expected outcome. Test governor verifies no oracle-bearing metadata is delivered.

## 12. Disclosure escrow for material automatic drift

For `AUTOMATIC_GOVERNED` material drift:

- reversible internal bookkeeping may enter `DISCLOSURE_PENDING_ESCROW` when policy explicitly allows asynchronous delivery;
- irreversible authority progression, terminal qualification, and external consequential effects MUST NOT activate until required disclosure is `DELIVERED`, unless a separately root-governed emergency/safety policy explicitly authorizes a named action class;
- `DISCLOSURE_TIMEOUT` blocks further escrow release and triggers the exact PRR escalation path;
- timeout never means approval/no-impact;
- a pending/failed/timed-out disclosure is never a clean disclosure PASS.

This rule supersedes any V5 interpretation that could permit an irreversible material-drift effect before actual required delivery.

## 13. Approval assurance binding

PRR maps each approval-required action class to `minimum_session_assurance_level` and accepted authentication methods.

ApprovalObject records the assurance level and authentication event ID. DGV and WSA revalidate at final commit:

- principal/session still valid;
- current assurance >= required minimum;
- authentication/role/key not revoked;
- exact action/policy/checkpoint binding unchanged;
- approval nonce unused;
- required disclosure ordering satisfied.

Assurance downgrade, session compromise/revocation, or reauthentication failure produces `APPROVAL_ASSURANCE_REJECTED`.

## 14. Complete endpoint registry requirement

Every endpoint referenced by the V5 or V6 matrices MUST exist in the signed EndpointSchemaRegistry with owner, schema digest, reason-code enum, state-transition effect, and authority effect.

V6 explicitly adds at minimum:

- `UNTRUSTED_BOOTSTRAP_STATE` — RGA verifier;
- `ROOT_GOVERNANCE_REJECTED` — RGA verifier;
- `DECISION_REPLAY_DEDUPLICATED` — WSA;
- `TIME_AUTHORITY_CONFLICT_BLOCKED` — DGV/WSA according to use;
- `DEPENDENCY_GRAPH_INCOMPLETE_BLOCKED` — DGV;
- `QUORUM_INDEPENDENCE_REJECTED` — DGV;
- `EXTERNAL_EFFECT_OUTCOME_UNKNOWN_BLOCKED` — Effect Gateway;
- `INSUFFICIENT_REVIEW_PROVENANCE` — RCB;
- `DISCLOSURE_PENDING_ESCROW` — DR/WSA;
- `APPROVAL_ASSURANCE_REJECTED` — DGV;
- `PARENT_CONSTRAINT_ADDED` — WSA/DGV with accepted impact record;
- `PARENT_IMPACT_CONFLICT_BLOCKED` — WSA/DGV;
- `CHILD_TIMEOUT_ESCALATED` — WSA/PRR-defined escalation owner;
- `INSUFFICIENT_EVIDENCE_FOR_RUNTIME_QUALIFICATION` — test governor;
- `ORACLE_INTEGRITY_REJECTED` — test governor;
- `LEDGER_ANCHOR_COVERAGE_GAP` — WAS verifier.

An unknown/unregistered endpoint cannot qualify a test.

## 15. Continuous GEL/WAS coverage

V6 requires coverage, not only periodic consistency.

GEL maintains a contiguous event sequence. WAS anchors signed contiguous ranges with no gaps. Every anchor includes:

- first and last event sequence;
- Merkle root;
- previous anchor digest;
- previous covered end sequence;
- event-count commitment;
- witness store identity;
- WAS signature.

Every authoritative event must have a Merkle inclusion proof to exactly one anchored contiguous history range before that event may be relied on for terminal qualification/release authority.

For RED-preservation tests, the RED event and all subsequent authority-relevant events MUST be covered by contiguous anchors. A gap yields `LEDGER_ANCHOR_COVERAGE_GAP` and blocks qualification.

Before the first anchor or between anchors, events may exist operationally but are not eligible as final tamper-evident qualification proof. Terminal authority waits for anchor coverage.

WAS keys and witness storage administration are outside GEL administrative domain. Rewriting recent unanchored history cannot become qualified history merely by racing the next anchor; coverage verification compares the authoritative event sequence/outbox commitments and rejects discontinuity.

## 16. Cross-standard dual authority

A `CrossStandardIncidentRecord` is valid only when the same canonical incident digest carries separate signatures from:

- `WorkflowDispositionAuthority` authorized by workflow governance; and
- `ClaimEvidenceDispositionAuthority` authorized by EXP-K/claim-evidence governance.

These authorities MUST use different service principals and signing keys. The cross-standard linker/GEL cannot sign either substantive disposition.

The canonical record hard-codes non-authorization semantics:

- `workflow_authorizes_claim = false`
- `claim_authorizes_workflow = false`

Any attempt to infer claim acceptance from workflow recovery, or workflow progression from claim status, without a separate policy-authorized transition is rejected as `CROSS_STANDARD_AUTHORITY_COUPLING_REJECTED`.

## 17. Independent test governor and oracle integrity

The test governor has a signing identity and storage namespace inaccessible to R1, WSA, DGV, PRR, RCB, DR, GEL runtime writers, and the implementation under test.

Before each oracle-sensitive test it signs a `FrozenExpectedEndpoint` containing:

- opaque fixture ID;
- candidate revision;
- test case ID stored in evaluator-only metadata;
- expected endpoint/schema digest;
- expected unchanged/changed state constraints;
- freeze sequence/time;
- oracle digest;
- test-governor signature.

The actor under test receives only the opaque fixture input, never expected endpoint metadata. ExpectedEndpoint changes after actor execution invalidate the run as `ORACLE_INTEGRITY_REJECTED`.

## 18. Unique enforcement-path coverage and broader positives

Qualification reports MUST map each test to one or more enforcement mechanism IDs. Repeated cases on the same primary mechanism count as duplicate coverage, not independent-mechanism coverage.

Freeze requires, for every critical enforcement mechanism introduced by V5/V6:

- at least one adversarial negative test;
- at least one legitimate positive/control test;
- post-hoc owner-signed evidence;
- no unresolved RED for that mechanism.

V6 positive controls MUST include at minimum:

- valid root-governance/key rotation;
- valid WCE issuance/use exactly once;
- valid DGV decision applied then safely replayed as idempotent no-op;
- valid dependency predicate update under independent governance;
- valid `PARENT_UNAFFECTED` with complete graph;
- valid quorum across independent control domains;
- valid provider idempotent retry with one external effect;
- valid WSA failover/leader change with no false block;
- valid clean RCB provenance/context delivery;
- valid automatic material drift disclosure delivered before escrow release;
- valid high-assurance approval;
- valid policy/schema migration preserving explicitly grandfathered objects only;
- valid continuous WAS coverage across RED and later recovery;
- valid cross-standard incident with both independent signatures.

A system that blocks all actions, or only allows the exact happy-path fixtures, cannot qualify.

## 19. V6 regression obligation

V6 does not replace WDPC-01…95. All V5 cases remain mandatory regressions under the stricter V6 rules, with V6 endpoints/authority contracts controlling where they are stricter.

The V6 matrix adds targeted cases WDPC-96 onward for the new boundaries.

## 20. Current development/testing rule

Current external design review remains manual-only. No external reviewer/model API calls are used to qualify this design candidate.

Manual design review can support only `DESIGN_MANUAL_REVIEW` disposition. It cannot be represented as `RUNTIME_SIMULATION` or `RUNTIME_IMPLEMENTATION` evidence.

## 21. Freeze condition

V6 MUST NOT be frozen for execution until:

1. this overlay and the exact V5 base artifacts are independently reviewed as one exact candidate revision;
2. the V6 falsification extension is independently reviewed;
3. WDPC-01…95 remain mandatory regressions;
4. all V6-added cases are preregistered with exact endpoints;
5. no Critical/High design finding remains unresolved under the governing review policy.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
