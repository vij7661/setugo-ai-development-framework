# Workflow Drift & Parent-Child Impact Falsification Matrix — V15 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V15`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V15 inherits WDPC-01…237 as mandatory regressions under composite V5→V15 rules.

V15 adds WDPC-238…WDPC-250.

## 2. New cases

### WDPC-238 — Qualifying packet uses source-declared endpoint registry fallback

Mechanisms: `MECH-ENDPOINT-AUTHORITATIVE-REGISTRY`
Profiles: `EP-BASE + EP-ENDPOINT-AUTHORITATIVE-REGISTRY`

Fault: qualifying packet lacks authoritative endpoint registry export but presents source-declared tuple registry as sufficient.

Expected: `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING` + `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; threshold contribution zero.

### WDPC-239 — Reviewer-safe scanner ungoverned or unauthorized

Mechanisms: `MECH-REVIEW-METADATA-SCANNER-GOVERNANCE`
Profiles: `EP-BASE + EP-REVIEW-METADATA-SCANNER-GOVERNANCE`

Fault: metadata scan runs with unregistered/stale algorithm, corpus, authority, or independence state.

Expected: `REVIEW_METADATA_SCANNER_UNAUTHORIZED`; packet ineligible.

### WDPC-240 — Scanner side-channel evasion via commitment shape/cadence

Mechanisms: `MECH-REVIEW-METADATA-SCANNER-GOVERNANCE`, `MECH-HISTORY-COMMITMENT-NONDISCLOSURE`
Profiles: `EP-BASE + EP-REVIEW-METADATA-SCANNER-GOVERNANCE + EP-HISTORY-COMMITMENT-NONDISCLOSURE`

Fault: history commitment encodes protected facts through length, format, rotation frequency, or update cadence.

Expected: `REVIEW_HISTORY_COMMITMENT_SIDECHANNEL`.

### WDPC-241 — Scanner evasion through filename/label/ordinal/path

Mechanisms: `MECH-REVIEWER-LABEL-PATH-NONDISCLOSURE`
Profiles: `EP-BASE + EP-REVIEWER-LABEL-PATH-NONDISCLOSURE`

Fault: reviewer-facing artifact name, label, ordinal, description, display path, or payload metadata encodes protected review history.

Expected: `REVIEW_HISTORY_METADATA_LEAKED`.

### WDPC-242 — Canonical clause-ID collision

Mechanisms: `MECH-CANONICAL-CLAUSE-IDENTITY`
Profiles: `EP-BASE + EP-CANONICAL-CLAUSE-IDENTITY`

Fault: two materially distinct obligations collapse to the same canonical clause ID.

Expected: `CANONICAL_CLAUSE_ID_COLLISION`; equivalence fails.

### WDPC-243 — Re-expression preserves ID but weakens obligation

Mechanisms: `MECH-NORMATIVE-REEXPRESSION-VERIFICATION`, `MECH-CANONICAL-CLAUSE-IDENTITY`
Profiles: `EP-BASE + EP-NORMATIVE-REEXPRESSION-VERIFICATION + EP-CANONICAL-CLAUSE-IDENTITY`

Fault: projected text preserves claimed canonical ID but weakens scope/timing/authority/evidence/fail-closed semantics.

Expected: `NORMATIVE_REEXPRESSION_WEAKENED`; RPAA rejects.

### WDPC-244 — Opaque history commitment cadence/length side-channel

Mechanisms: `MECH-HISTORY-COMMITMENT-NONDISCLOSURE`
Profiles: `EP-BASE + EP-HISTORY-COMMITMENT-NONDISCLOSURE`

Fault: fixed content commitment still leaks via variable length, format, cadence, or rotation behavior.

Expected: `REVIEW_HISTORY_COMMITMENT_SIDECHANNEL`.

### WDPC-245 — Older design packet reused after newer candidate/projection

Mechanisms: `MECH-PACKET-GENERATION-ANTI-UPGRADE`
Profiles: `EP-BASE + EP-PACKET-GENERATION-ANTI-UPGRADE`

Fault: obsolete design-review packet is reused/upgraded after newer candidate/projection generation exists.

Expected: `REVIEW_PACKET_GENERATION_STALE`; threshold contribution zero.

### WDPC-246 — RPAA independence stale at final qualification snapshot

Mechanisms: `MECH-QUALIFICATION-SNAPSHOT-LIVE-RECHECK`
Profiles: `EP-BASE + EP-QUALIFICATION-SNAPSHOT-LIVE-RECHECK`

Fault: RPAA independence was valid earlier but admin/recovery/beneficial-owner state changed before final qualification snapshot.

Expected: `REVIEW_QUALIFICATION_SNAPSHOT_LIVE_RECHECK_FAILED` + `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`.

### WDPC-247 — Authoritative endpoint registry positive control

Mechanisms: `MECH-ENDPOINT-AUTHORITATIVE-REGISTRY`
Profiles: `EP-BASE + EP-ENDPOINT-AUTHORITATIVE-REGISTRY`

Positive control: authoritative endpoint registry export is current, exact-candidate-bound, and source/projection tuple sets are equal.

Expected: endpoint tuple predicate may PASS without self-consistency fallback.

### WDPC-248 — Governed scanner/canonicalizer positive control

Mechanisms: `MECH-REVIEW-METADATA-SCANNER-GOVERNANCE`, `MECH-CANONICAL-CLAUSE-IDENTITY`
Profiles: `EP-BASE + EP-REVIEW-METADATA-SCANNER-GOVERNANCE + EP-CANONICAL-CLAUSE-IDENTITY`

Positive control: registered current scanner/canonicalizer with independent audit handles a clean projection with zero metadata leak and no clause collision.

Expected: design predicates pass without false block.

### WDPC-249 — Mixed block re-expression positive control

Mechanisms: `MECH-NORMATIVE-REEXPRESSION-VERIFICATION`
Profiles: `EP-BASE + EP-NORMATIVE-REEXPRESSION-VERIFICATION`

Positive control: concrete review-history wording is removed while every active obligation remains semantically equivalent under independent verification.

Expected: re-expression accepted; no false weakening finding.

### WDPC-250 — Fully attested V15 qualifying packet positive control

Mechanisms: `MECH-PACKET-CLASS`, `MECH-ENDPOINT-AUTHORITATIVE-REGISTRY`, `MECH-REVIEW-METADATA-SCANNER-GOVERNANCE`, `MECH-CANONICAL-CLAUSE-IDENTITY`, `MECH-NORMATIVE-REEXPRESSION-VERIFICATION`, `MECH-PROJECTION-AUTHORITY-ATTESTATION`, `MECH-QUALIFYING-CLEANROOM`, `MECH-QUALIFYING-SOURCE-ATTESTATION`, `MECH-QUALIFICATION-SNAPSHOT-LIVE-RECHECK`, `MECH-PACKET-GENERATION-ANTI-UPGRADE`
Profiles: `EP-BASE + EP-PACKET-CLASS + EP-ENDPOINT-AUTHORITATIVE-REGISTRY + EP-REVIEW-METADATA-SCANNER-GOVERNANCE + EP-CANONICAL-CLAUSE-IDENTITY + EP-NORMATIVE-REEXPRESSION-VERIFICATION + EP-PROJECTION-AUTHORITY-ATTESTATION + EP-QUALIFYING-CLEANROOM + EP-QUALIFYING-SOURCE-ATTESTATION + EP-QUALIFICATION-SNAPSHOT-LIVE-RECHECK + EP-PACKET-GENERATION-ANTI-UPGRADE`

Positive control: every required V15 predicate is current for the same exact candidate/projection/packet generation and eligible reviewer evidence class.

Expected: packet may be eligible to count under the review gate; no workflow/terminal authority is granted by review eligibility.

## 3. Freeze rule

V15 remains `NOT EXECUTED`.

No unresolved Critical/High design finding may remain before execution freeze is reconsidered.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
