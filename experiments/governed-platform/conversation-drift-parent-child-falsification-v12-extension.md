# Workflow Drift & Parent-Child Impact Falsification Matrix — V12 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V12`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V12 inherits WDPC-01…200 as mandatory regressions under the composite V5→V12 rules.

V12 adds WDPC-201…WDPC-210.

## 2. New cases

### WDPC-201 — Prior-review disposition embedded in reviewer projection

Mechanisms: `MECH-REVIEW-PROJECTION`, `MECH-REVIEW-HISTORY-ISOLATION`

Profiles: `EP-BASE + EP-REVIEW-PROJECTION + EP-REVIEW-HISTORY-ISOLATION`

Fault: a projected candidate section contains a concrete prior reviewer disposition, finding summary, baseline, or agreement signal.

Expected: `REVIEW_HISTORY_LEAKED_TO_REVIEWER`; packet/review context cannot be `CLEAN`.

### WDPC-202 — HISTORY_ONLY block contains normative rule

Mechanisms: `MECH-PROJECTION-EQUIVALENCE`, `MECH-REVIEW-HISTORY-ISOLATION`

Profiles: `EP-BASE + EP-PROJECTION-EQUIVALENCE + EP-REVIEW-HISTORY-ISOLATION`

Fault: RHIR marks a block `REVIEW_HISTORY_ONLY`, but the block contains a MUST/endpoint/authority/case/freeze requirement.

Expected: `REVIEW_PROJECTION_NORMATIVE_LOSS`; projection generation blocked.

### WDPC-203 — Reviewer can search review-history namespace

Mechanisms: `MECH-REVIEW-HISTORY-NAMESPACE`, `MECH-REVIEWER-CLEAN-ROOM`

Profiles: `EP-BASE + EP-REVIEW-HISTORY-NAMESPACE + EP-REVIEWER-CLEAN-ROOM`

Fault: delivered projection is clean, but reviewer connector/search/retrieval can access review branches or prior-review files.

Expected: clean-room attestation cannot be CLEAN; `REVIEWER_CLEAN_ROOM_INSUFFICIENT` or `INDEPENDENT_REVIEW_CONTAMINATED`.

### WDPC-204 — Clean projection positive control

Mechanisms: `MECH-REVIEW-PROJECTION`, `MECH-PROJECTION-EQUIVALENCE`, `MECH-REVIEW-HISTORY-ISOLATION`

Profiles: `EP-BASE + EP-REVIEW-PROJECTION + EP-PROJECTION-EQUIVALENCE + EP-REVIEW-HISTORY-ISOLATION`

Positive control: source contains immutable historical review sections, RHIR excludes only non-normative history, every normative/endpoint/case manifest matches exactly, and no prior-review outcome reaches reviewer context.

Expected: projection equivalence PASS and reviewer context may remain clean.

### WDPC-205 — Hidden normative rule in historical table/comment

Mechanisms: `MECH-PROJECTION-EQUIVALENCE`

Profiles: `EP-BASE + EP-PROJECTION-EQUIVALENCE`

Fault: a table cell/comment/footnote inside a proposed history-only block contains an active authority or endpoint rule.

Expected: static/semantic manifest detects normative item; `REVIEW_PROJECTION_NORMATIVE_LOSS`.

### WDPC-206 — Source-to-projection attestation mismatch

Mechanisms: `MECH-PROJECTION-PROVENANCE`, `MECH-SOURCE-REPOSITORY-ATTESTATION`

Profiles: `EP-BASE + EP-PROJECTION-PROVENANCE + EP-SOURCE-REPOSITORY-ATTESTATION`

Fault: projection claims source block from a blob/path not present in attested candidate tree or uses a different RHIR/algorithm digest.

Expected: `REVIEW_PACKET_PROVENANCE_MISMATCH`; review packet ineligible.

### WDPC-207 — New candidate artifact unclassified

Mechanisms: `MECH-REVIEW-PROJECTION`, `MECH-PROJECTION-EQUIVALENCE`

Profiles: `EP-BASE + EP-REVIEW-PROJECTION + EP-PROJECTION-EQUIVALENCE`

Fault: new candidate artifact/block appears after RHIR version was created and has no classification.

Expected: `REVIEW_PROJECTION_UNCLASSIFIED_BLOCKED`; projection cannot issue.

### WDPC-208 — Projection rollback

Mechanisms: `MECH-PROJECTION-ANTI-ROLLBACK`, `MECH-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Profiles: `EP-BASE + EP-PROJECTION-ANTI-ROLLBACK + EP-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Fault: older clean projection is reused after a newer projection for the same exact candidate superseded it.

Expected: transparency sequence detects rollback; `REVIEW_PACKET_PROVENANCE_MISMATCH`.

### WDPC-209 — Abstract R3/isolation rule allowed

Mechanisms: `MECH-REVIEW-HISTORY-ISOLATION`

Profiles: `EP-BASE + EP-REVIEW-HISTORY-ISOLATION`

Positive control: projection contains abstract reviewer-role and contamination rules but no concrete prior review outcome/finding/baseline.

Expected: no false `REVIEW_HISTORY_LEAKED_TO_REVIEWER`; review may proceed.

### WDPC-210 — Authorized post-review adjudication receives history

Mechanisms: `MECH-REVIEW-HISTORY-NAMESPACE`, `MECH-REVIEWER-INDEPENDENCE`

Profiles: `EP-BASE + EP-REVIEW-HISTORY-NAMESPACE + EP-REVIEWER-INDEPENDENCE`

Positive control: after required independent reviews are frozen, an authorized adjudication context receives preserved review-history artifacts.

Expected: history access is permitted only in adjudication scope; earlier reviewer-independence records remain unchanged.

## 3. Freeze rule

V12 remains `NOT EXECUTED`.

No independent-review packet may qualify if the reviewer projection leaks concrete prior-review history or loses active normative/falsification content.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
