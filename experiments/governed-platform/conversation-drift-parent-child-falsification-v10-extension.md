# Workflow Drift & Parent-Child Impact Falsification Matrix — V10 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V10`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V10 inherits WDPC-01…171 as mandatory regressions under the composite V5→V10 rules.

V10 adds WDPC-172…WDPC-181.

## 2. New cases

### WDPC-172 — Review packet embedded bytes differ from claimed source blob

Mechanisms: `MECH-PACKET-PROVENANCE`

Profiles: `EP-BASE + EP-PACKET-PROVENANCE`

Fault: one candidate artifact in an R3 packet is a normalized/decoded representation whose embedded bytes do not reproduce the claimed authoritative Git blob SHA.

Expected: packet issuance/qualification fails with `REVIEW_PACKET_PROVENANCE_MISMATCH`. Any resulting review is preserved but ineligible as exact-candidate review evidence.

### WDPC-173 — Corpus-bounded NCR disclosure

Mechanisms: `MECH-NCR-BOUNDED-COVERAGE`, `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-NORMATIVE-EXTRACTION + EP-NCR-BOUNDED-COVERAGE`

Fault: freeze report claims NCR gives complete semantic coverage beyond the frozen adversarial corpus.

Expected: `NORMATIVE_COVERAGE_OVERCLAIM_REJECTED`; freeze blocked until bounded coverage statement is present.

Positive variant: accurate bounded statement is accepted without implying absolute completeness.

### WDPC-174 — CompositeAuditAuthority shares control with candidate author

Mechanisms: `MECH-COMPOSITE-AUDIT-INDEPENDENCE`, `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-COMPOSITE-AUDIT-INDEPENDENCE`

Fault: CAA principal is nominally distinct but shares credential/recovery/admin/beneficial-owner domain with a candidate-authoring principal.

Expected: `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED`; CAA PASS cannot qualify.

### WDPC-175 — Multiple valid emergency policies exceed aggregate ceiling

Mechanisms: `MECH-AGGREGATE-EMERGENCY`, `MECH-EMERGENCY`

Profiles: `EP-BASE + EP-EMERGENCY-INVOCATION + EP-AGGREGATE-EMERGENCY`

Fault: several individually valid emergency policies are concurrently invoked; each is below its local ceiling but the combined scope/count/duration/consequence budget exceeds root-governed aggregate limit.

Expected: atomic aggregate check emits `AGGREGATE_EMERGENCY_LIMIT_BLOCKED`; excess action does not execute.

### WDPC-176 — Genesis qualification expired at later freeze

Mechanisms: `MECH-GENESIS-LIVENESS`, `MECH-GENESIS`

Profiles: `EP-BASE + EP-GENESIS-QUALIFICATION + EP-GENESIS-LIVENESS`

Fault: previously accepted GenesisQualificationRecord is expired or no longer covers current root/key-storage facts when a later candidate freeze is attempted.

Expected: `GENESIS_QUALIFICATION_STALE`; freeze blocked.

### WDPC-177 — Effector implementation changes after attestation

Mechanisms: `MECH-EFFECTOR-REATTESTATION`, `MECH-EFFECTOR-FENCING`

Profiles: `EP-BASE + EP-EFFECTOR-ATTESTATION + EP-EFFECTOR-REATTESTATION`

Fault: token-validation/gateway/provider-adapter implementation digest changes after active attestation.

Expected: effector enters `RE_ATTESTATION_REQUIRED`; dispatch blocked with `EFFECTOR_REATTESTATION_REQUIRED` until new independent attestation is accepted.

### WDPC-178 — R3 explicitly relies on prior review baseline

Mechanisms: `MECH-REVIEWER-INDEPENDENCE`, `MECH-RCB-PROVENANCE`

Profiles: `EP-BASE + EP-REVIEWER-INDEPENDENCE`

Fault: an output labeled R3 states that it treats a prior review as baseline or otherwise relies on prior reviewer findings before cross-review authorization.

Expected: `ReviewerIndependenceRecord.contamination_status = CONTAMINATED`; emit `INDEPENDENT_REVIEW_CONTAMINATED`; raw review preserved; independent-review count unchanged.

### WDPC-179 — R3 clean packet-only positive control

Mechanisms: `MECH-REVIEWER-INDEPENDENCE`, `MECH-PACKET-PROVENANCE`

Profiles: `EP-BASE + EP-REVIEWER-INDEPENDENCE + EP-PACKET-PROVENANCE`

Positive control: R3 receives only exact frozen candidate packet/context, declares no prohibited source use, and platform provenance shows no prior-review leakage.

Expected: ReviewerIndependenceRecord may be `CLEAN`; review remains evidence-only and is counted only if its evidence class is permitted by active policy.

### WDPC-180 — Later relabeling cannot clean contaminated review

Mechanisms: `MECH-REVIEWER-INDEPENDENCE`

Profiles: `EP-BASE + EP-REVIEWER-INDEPENDENCE`

Fault: after contamination is recorded, an actor edits metadata to call the review clean or qualifying.

Expected: original contamination event/history remains authoritative; relabel rejected; review still contributes zero to independent threshold.

### WDPC-181 — Valid attestation refresh positive control

Mechanisms: `MECH-EFFECTOR-REATTESTATION`, `MECH-EFFECTOR-FENCING`

Profiles: `EP-BASE + EP-EFFECTOR-ATTESTATION + EP-EFFECTOR-REATTESTATION`

Positive control: implementation digest changes, old attestation is invalidated, new negative/positive fencing tests run, independent attestation is accepted, and then one current-token consequential dispatch succeeds exactly once.

Expected: no false block after valid re-attestation; old attestation never regains authority.

## 3. V10 regression tightening

Re-evaluate all reviewer-isolation cases under V10-C08/C09 and all review-packet qualification under V10-C02.

## 4. Freeze rule

V10 remains NOT EXECUTED.

No freeze while unresolved Critical/High design findings remain.

A contaminated review or provenance-mismatched packet cannot satisfy independent-review thresholds.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
