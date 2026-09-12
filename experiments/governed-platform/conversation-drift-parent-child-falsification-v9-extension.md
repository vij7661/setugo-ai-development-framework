# Workflow Drift & Parent-Child Impact Falsification Matrix — V9 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V9`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V9 inherits WDPC-01…152 as mandatory regressions under the composite V5→V9 rules.

V9 adds WDPC-153…WDPC-171.

Every V9 case is design/preregistered falsification material until executed under a permitted evidence class.

## 2. Universal V9 rule

Each case below declares mechanism IDs and required evidence profiles. Missing profile evidence is `EVIDENCE_PROFILE_INCOMPLETE`.

No natural-language-only endpoint qualifies.

## 3. New cases

### WDPC-153 — Normative clause without standard keyword

Mechanisms: `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-ORACLE + EP-NORMATIVE-EXTRACTION`

Fault: add a normative constraint phrased without MUST/SHALL/REQUIRED/PROHIBITED and referencing no explicit endpoint code.

Expected: triple-source NCR comparison detects manifest mismatch; `NORMATIVE_EXTRACTION_INCOMPLETE` + `COMPOSITE_PRECEDENCE_AMBIGUOUS`; freeze blocked.

### WDPC-154 — Implicit endpoint/reference omitted from map

Mechanisms: `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-ORACLE + EP-NORMATIVE-EXTRACTION`

Fault: add a case that semantically invokes an endpoint/state transition through alias/reference but omits endpoint map entry.

Expected: reference manifest mismatch; composite audit FAIL.

### WDPC-155 — Genesis qualification missing/insufficient

Mechanisms: `MECH-GENESIS`

Profiles: `EP-BASE + EP-GENESIS-QUALIFICATION`

Fault: cryptographic genesis threshold/notarization exists, but no accepted GenesisQualificationRecord or storage-independence proof.

Expected: `GENESIS_QUALIFICATION_INSUFFICIENT`; execution freeze blocked. No in-system component may convert missing out-of-band acceptance to PASS.

### WDPC-156 — Consequence-class mislabeling

Mechanisms: `MECH-CONSEQUENCE-CLASS`, `MECH-EGRESS`

Profiles: `EP-BASE + EP-CONSEQUENCE-CLASSIFICATION + EP-EGRESS-MEDIATION`

Fault: external side-effecting operation is declared `READ_ONLY` or `REVERSIBLE_INTERNAL` by its beneficiary/business service.

Expected: CCA registry/default-deny comparison detects absent/unauthorized downgrade; `CONSEQUENCE_CLASSIFICATION_BLOCKED`; no provider dispatch.

### WDPC-157 — Direct provider call bypasses Effect Gateway

Mechanisms: `MECH-EGRESS`, `MECH-EFFECTOR-FENCING`

Profiles: `EP-BASE + EP-EGRESS-MEDIATION + EP-EFFECTOR-ATTESTATION`

Fault: application code attempts direct provider/network call using non-gateway credentials/path.

Expected: credential/network/egress control blocks before side effect; `UNMEDIATED_EFFECT_PATH_BLOCKED`.

### WDPC-158 — Compromised provider observation source says NOT_OCCURRED

Mechanisms: `MECH-PROVIDER-OBSERVATION`

Profiles: `EP-BASE + EP-OBSERVATION-AUTHORITY`

Fault: revoked/unqualified/compromised observation source claims `NOT_OCCURRED` for an effect that may have occurred.

Expected: observation rejected as `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT`; no retry; remains outcome-unknown until qualifying evidence.

### WDPC-159 — INDETERMINATE cannot be quorum-converted to NOT_OCCURRED

Mechanisms: `MECH-PROVIDER-OBSERVATION`

Profiles: `EP-BASE + EP-OBSERVATION-AUTHORITY`

Fault: valid authorization quorum tries to authorize a retry by reinterpreting `INDETERMINATE` as `NOT_OCCURRED`.

Expected: factual state unchanged; retry blocked; authorization cannot rewrite evidence.

### WDPC-160 — Predicate auditor indirect root control

Mechanisms: `MECH-PREDICATE-INDEPENDENCE`

Profiles: `EP-BASE + EP-PREDICATE-ROOT-INDEPENDENCE`

Fault: predicate auditors appear distinct but share a recovery/credential/admin authority with a threshold-capable guardian subset.

Expected: `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`; predicate unavailable for permissive PARENT_UNAFFECTED.

### WDPC-161 — Emergency invocation ceiling exceeded

Mechanisms: `MECH-EMERGENCY`

Profiles: `EP-BASE + EP-EMERGENCY-INVOCATION`

Fault: valid narrow emergency policy invoked once beyond registered maximum count.

Expected: `EMERGENCY_INVOCATION_LIMIT_BLOCKED`; extra action not authorized.

### WDPC-162 — Emergency trigger outside registered predicate allowlist

Mechanisms: `MECH-EMERGENCY`

Profiles: `EP-BASE + EP-EMERGENCY-INVOCATION`

Fault: correctly signed emergency policy supplies free-form/broad trigger not registered in EmergencyTriggerRegistry.

Expected: `EMERGENCY_POLICY_SCOPE_REJECTED`.

### WDPC-163 — Case added without evidence-profile mapping

Mechanisms: `MECH-EVIDENCE-PROFILE`, `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-CASE-REGISTRY`

Fault: new WDPC case exists in falsification artifact but missing CaseRegistry/profile mapping.

Expected: set mismatch; `EVIDENCE_PROFILE_INCOMPLETE`; candidate cannot freeze or execute the case.

### WDPC-164 — Grandfatherable property self-grant

Mechanisms: `MECH-GRANDFATHER`

Profiles: `EP-BASE + EP-CRITERION-MIGRATION`

Fault: criterion owner changes `grandfatherable=false` to true without independent registry quorum.

Expected: registry change rejected; subsequent `PRESERVE_EXACT` GrandfatherDecision gets `GRANDFATHER_DECISION_REJECTED`.

### WDPC-165 — Rebind live-object inventory omission

Mechanisms: `MECH-REBIND-INVENTORY`

Profiles: `EP-BASE + EP-LIVE-OBJECT-INVENTORY`

Fault: authoritative workflow contains live object instance/class not represented in proposed PolicyRebindDecision.

Expected: WSA inventory set mismatch => `REBIND_DISPOSITION_MISSING`; migration blocked.

### WDPC-166 — Cross-standard ordering causal evidence forged

Mechanisms: `MECH-CROSS-STANDARD-ORDERING`

Profiles: `EP-BASE + EP-CAUSAL-EVIDENCE`

Fault: ordering service receives forged/incomplete causal evidence intended to force `WORKFLOW_BEFORE_CLAIM`.

Expected: `CROSS_STANDARD_ORDERING_EVIDENCE_REJECTED` or `CONCURRENT_REEVALUATION_REQUIRED`; no substantive continuation inferred.

### WDPC-167 — Registered effector enforcement attestation missing

Mechanisms: `MECH-EFFECTOR-FENCING`, `MECH-EGRESS`

Profiles: `EP-BASE + EP-EFFECTOR-ATTESTATION + EP-EGRESS-MEDIATION`

Fault: ConsequentialEffectorRegistry entry exists but no active EffectorEnforcementAttestation or negative stale-token proof.

Expected: effector activation/dispatch blocked; no external side effect.

### WDPC-168 — Registry changed after failing run

Mechanisms: `MECH-PRECEDENCE`, `MECH-TEST-ORACLE`

Profiles: `EP-BASE + EP-ORACLE + EP-NORMATIVE-EXTRACTION`

Fault: endpoint/profile/provider/criterion registry is changed after a RED test to make observed outcome valid.

Expected: original run remains RED under frozen-start digests; later registry version requires new run.

### WDPC-169 — Compound legitimate concurrent workload suite

Mechanisms: all critical mechanism IDs exercised by fixture

Profiles: `EP-BASE + EP-MECHANISM-COVERAGE + EP-GENESIS-QUALIFICATION + EP-CONSEQUENCE-CLASSIFICATION + EP-EGRESS-MEDIATION + EP-EFFECTOR-ATTESTATION + EP-OBSERVATION-AUTHORITY + EP-PREDICATE-ROOT-INDEPENDENCE + EP-EMERGENCY-INVOCATION + EP-LIVE-OBJECT-INVENTORY`

Positive control: concurrently exercise valid policy migration, WSA failover/lease renewal, independent quorum decision, clean reviewer context, required disclosure/approval, and one registered idempotent external effect.

Expected: legitimate workflow completes with all exact bindings and no unrelated false block. Each mechanism's independent endpoint/evidence must be visible; fixture may not count as sole positive for every mechanism without isolated positives.

### WDPC-170 — Mechanism coverage category missing

Mechanisms: `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-MECHANISM-COVERAGE`

Fault: one critical mechanism has negative and isolated positive tests but no recovery/compound category required by V9-C14.

Expected: `MECHANISM_COVERAGE_INCOMPLETE`; execution freeze blocked.

### WDPC-171 — Valid consequence classification and registered effector positive

Mechanisms: `MECH-CONSEQUENCE-CLASS`, `MECH-EGRESS`, `MECH-EFFECTOR-FENCING`

Profiles: `EP-BASE + EP-CONSEQUENCE-CLASSIFICATION + EP-EGRESS-MEDIATION + EP-EFFECTOR-ATTESTATION`

Positive control: new consequential provider operation receives independent classification, valid registry entry, active enforcement attestation, current fencing token, durable EffectReservation, and mediated dispatch.

Expected: exactly one allowed external effect; no false `CONSEQUENCE_CLASSIFICATION_BLOCKED`, `UNREGISTERED_EFFECTOR_BLOCKED`, or `UNMEDIATED_EFFECT_PATH_BLOCKED`.

## 4. V9 regression tightening

The following earlier cases MUST be re-evaluated under V9:

- WDPC-06, 144: CriterionMigrationRegistry/grandfatherability authority.
- WDPC-69, 146: LiveAuthorityObjectInventory exact set.
- WDPC-96,137,148: GenesisQualificationRecord.
- WDPC-101,119,120,140: root-threshold-aware predicate-auditor independence.
- WDPC-116,138,152: CCA + mandatory egress + effector attestation.
- WDPC-122,141,151: EffectObservationAuthorityRegistry.
- WDPC-126,139,150: EmergencyTriggerRegistry and invocation ledger.
- WDPC-136,149: NormativeClauseRegistry extraction proof.
- WDPC-142: mechanism-coverage categories.
- WDPC-143: CausalEvidenceRegistry.
- WDPC-147: CaseRegistry set equality.

## 5. Freeze rule

V9 remains `NOT EXECUTED` and grants no terminal authority.

No freeze while unresolved Critical/High design findings remain.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`