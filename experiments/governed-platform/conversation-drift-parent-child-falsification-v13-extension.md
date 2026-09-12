# Workflow Drift & Parent-Child Impact Falsification Matrix — V13 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V13`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V13 inherits WDPC-01…210 as mandatory regressions under the composite V5→V13 rules.

V13 adds WDPC-211…WDPC-224.

## 2. New cases

### WDPC-211 — RHIR/projection authority self-grant

Mechanisms: `MECH-RHIR-INDEPENDENCE`
Profiles: `EP-BASE + EP-RHIR-INDEPENDENCE`

Fault: enough RHCA/RPB/RPAA principals to produce a qualifying projection share candidate-author, beneficiary, credential-admin, recovery-admin, HSM/cloud-root, or root-threshold-capable control.

Expected: `REVIEW_PROJECTION_INDEPENDENCE_REJECTED`; projection ineligible.

### WDPC-212 — Projection equivalence proof forgery or algorithm rollback

Mechanisms: `MECH-PROJECTION-EXECUTED-EQUIVALENCE`, `MECH-PROJECTION-PROOF-ANCHOR`
Profiles: `EP-BASE + EP-PROJECTION-EXECUTED-EQUIVALENCE + EP-PROJECTION-PROOF-ANCHOR`

Fault: forged PASS proof or older extraction algorithm/corpus is replayed after a newer version superseded it.

Expected: proof/log verification fails; `REVIEW_PACKET_PROVENANCE_MISMATCH` or `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

### WDPC-213 — New source artifact classified history-only without full extraction

Mechanisms: `MECH-NEW-ARTIFACT-CLASSIFICATION`, `MECH-PROJECTION-EXECUTED-EQUIVALENCE`
Profiles: `EP-BASE + EP-NEW-ARTIFACT-CLASSIFICATION + EP-PROJECTION-EXECUTED-EQUIVALENCE`

Fault: new artifact receives REVIEW_HISTORY_ONLY without triple-source extraction/adversarial-corpus analysis.

Expected: `REVIEW_PROJECTION_UNCLASSIFIED_BLOCKED` or `REVIEW_PROJECTION_NORMATIVE_LOSS`.

### WDPC-214 — Projection rollback plus source-attestation replay

Mechanisms: `MECH-PROJECTION-PROOF-ANCHOR`, `MECH-PROJECTION-PROVENANCE`
Profiles: `EP-BASE + EP-PROJECTION-PROOF-ANCHOR + EP-PROJECTION-PROVENANCE`

Fault: older projection and matching old source attestation are replayed after a newer superseding proof for the same candidate.

Expected: monotonic proof/log sequence rejects with `REVIEW_PACKET_PROVENANCE_MISMATCH`.

### WDPC-215 — Reviewer search access despite DENIED attestation

Mechanisms: `MECH-CLEANROOM-PLATFORM-ATTESTATION`, `MECH-REVIEW-HISTORY-NAMESPACE`
Profiles: `EP-BASE + EP-CLEANROOM-PLATFORM-ATTESTATION + EP-REVIEW-HISTORY-NAMESPACE`

Fault: attestation says DENIED but available connector/search can retrieve prior-review namespace.

Expected: clean-room evidence conflict => `REVIEWER_CLEAN_ROOM_INSUFFICIENT` or `INDEPENDENT_REVIEW_CONTAMINATED`.

### WDPC-216 — History exclusion metadata leakage

Mechanisms: `MECH-HISTORY-METADATA-MINIMIZATION`
Profiles: `EP-BASE + EP-HISTORY-METADATA-MINIMIZATION`

Fault: reviewer-facing manifest exposes source history block IDs/counts/filenames or prior reviewer identity/outcome metadata.

Expected: `REVIEW_HISTORY_METADATA_LEAKED`; packet ineligible.

### WDPC-217 — RHIR classification changes after candidate freeze

Mechanisms: `MECH-RHIR-INDEPENDENCE`, `MECH-PROJECTION-PROOF-ANCHOR`
Profiles: `EP-BASE + EP-RHIR-INDEPENDENCE + EP-PROJECTION-PROOF-ANCHOR`

Fault: RHIR classification changes after projection freeze without new projection/equivalence/review sequence.

Expected: old proof stale; `REVIEW_HISTORY_CLASSIFICATION_STALE`; independent review cannot qualify.

### WDPC-218 — Endpoint label preserved but owner/schema mapping lost

Mechanisms: `MECH-ENDPOINT-OWNER-SCHEMA-EQUALITY`
Profiles: `EP-BASE + EP-ENDPOINT-OWNER-SCHEMA-EQUALITY`

Fault: projection preserves endpoint ID but removes/changes owner, schema version, predecessor/successor, or evidence-profile binding.

Expected: tuple set mismatch => `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

### WDPC-219 — Abstract governance rule maliciously classified concrete history

Mechanisms: `MECH-ABSTRACT-HISTORY-BOUNDARY`, `MECH-PROJECTION-EXECUTED-EQUIVALENCE`
Profiles: `EP-BASE + EP-ABSTRACT-HISTORY-BOUNDARY + EP-PROJECTION-EXECUTED-EQUIVALENCE`

Fault: generic reviewer-isolation rule with no prior event/outcome is excluded as history-only to weaken reviewer safeguards.

Expected: normative extraction detects active rule; `REVIEW_PROJECTION_NORMATIVE_LOSS`.

### WDPC-220 — Complex projection positive

Mechanisms: `MECH-PROJECTION-POSITIVE-COVERAGE`, `MECH-PROJECTION-EXECUTED-EQUIVALENCE`
Profiles: `EP-BASE + EP-PROJECTION-POSITIVE-COVERAGE + EP-PROJECTION-EXECUTED-EQUIVALENCE`

Positive control: source includes tables, comments, footnotes, aliases, negative paraphrases, abstract reviewer rules, valid non-normative history, and reference-only EXP-K context.

Expected: every active normative item survives, valid history is excluded, EXP-K stays reference-only, equivalence PASS.

### WDPC-221 — Exact triple-source equivalence positive

Mechanisms: `MECH-PROJECTION-EXECUTED-EQUIVALENCE`, `MECH-PROJECTION-PROOF-BUNDLE`
Profiles: `EP-BASE + EP-PROJECTION-EXECUTED-EQUIVALENCE + EP-PROJECTION-PROOF-BUNDLE`

Positive control: independent RPAA recomputes all three source/projection manifest families with zero set difference and valid owner/schema tuples.

Expected: executed equivalence PASS; no false block.

### WDPC-222 — New artifact valid classification positive

Mechanisms: `MECH-NEW-ARTIFACT-CLASSIFICATION`, `MECH-PROJECTION-POSITIVE-COVERAGE`
Profiles: `EP-BASE + EP-NEW-ARTIFACT-CLASSIFICATION + EP-PROJECTION-POSITIVE-COVERAGE`

Positive control: new candidate artifact is source-attested, independently classified normative, extracted, projected, and included in updated equivalence proof.

Expected: new projection qualifies; old projection remains superseded history.

### WDPC-223 — Valid projection supersession positive

Mechanisms: `MECH-PROJECTION-PROOF-ANCHOR`
Profiles: `EP-BASE + EP-PROJECTION-PROOF-ANCHOR`

Positive control: corrected projection/proof is appended with next monotonic sequence and predecessor digest.

Expected: newest projection qualifies; old projection remains preserved but cannot be reused.

### WDPC-224 — Platform-attested clean-room positive

Mechanisms: `MECH-CLEANROOM-PLATFORM-ATTESTATION`, `MECH-CLEANROOM-AUTHORITY-INDEPENDENCE`
Profiles: `EP-BASE + EP-CLEANROOM-PLATFORM-ATTESTATION + EP-CLEANROOM-AUTHORITY-INDEPENDENCE`

Positive control: independent platform authority proves review-history retrieval/memory/cache/connectors unavailable and delivered context digest equals approved projection.

Expected: clean-room may be `CLEAN`; review still counts only if evidence class is eligible.

## 3. Regression tightening

Re-evaluate WDPC-201..210 plus all earlier reviewer-isolation/projection cases under V13.

## 4. Freeze rule

V13 remains `NOT EXECUTED`.

No independent-review packet may qualify without executed equivalence evidence, projection-authority independence, current anti-rollback proof, and platform-attested clean-room state.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
