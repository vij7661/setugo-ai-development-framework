# Workflow Drift & Parent-Child Impact Falsification Matrix — V16 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V16`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V16 inherits WDPC-01…250 as mandatory regressions under composite V5→V16 rules.

V16 adds WDPC-251…WDPC-260.

## 2. New cases

### WDPC-251 — Threshold counting after stale qualification snapshot

Mechanisms: `MECH-QUALIFICATION-THRESHOLD-ATOMICITY`, `MECH-THRESHOLD-IDEMPOTENT-CONSUMPTION`
Profiles: `EP-BASE + EP-QUALIFICATION-THRESHOLD-ATOMICITY + EP-THRESHOLD-IDEMPOTENT-CONSUMPTION`

Fault: qualification snapshot is valid, then RPAA/admin/recovery/beneficial-owner/scanner/canonicalizer/source/clean-room state changes before `ReviewThresholdRecord` commits.

Expected: old snapshot cannot be consumed; `REVIEW_THRESHOLD_SNAPSHOT_STALE` + `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; threshold count remains zero until a new snapshot is issued.

### WDPC-252 — NormativeReExpressionVerifier collusion/self-verification

Mechanisms: `MECH-REEXPRESSION-VERIFIER-INDEPENDENCE`
Profiles: `EP-BASE + EP-REEXPRESSION-VERIFIER-INDEPENDENCE`

Fault: re-expression producer/canonicalizer/projection authority also controls enough verifier authority to approve a weakened obligation while preserving claimed canonical ID.

Expected: `NORMATIVE_REEXPRESSION_VERIFIER_INDEPENDENCE_REJECTED` and `NORMATIVE_REEXPRESSION_WEAKENED`; projection/review qualification blocked.

### WDPC-253 — Semantically equivalent obligations falsely treated as different

Mechanisms: `MECH-CANONICAL-EQUIVALENCE-POSITIVE`
Profiles: `EP-BASE + EP-CANONICAL-EQUIVALENCE-POSITIVE`

Positive/overblocking control: two materially equivalent obligations use different surface wording, order, or syntactic form.

Expected: governed equivalence corpus recognizes equivalent obligation semantics; no false collision/equivalence failure. If falsely separated, emit `CANONICAL_EQUIVALENCE_FALSE_NEGATIVE` and fail the positive control.

### WDPC-254 — Scanner false negative through MIME/reference/attachment metadata

Mechanisms: `MECH-SCANNER-HIDDEN-METADATA-FIXTURES`
Profiles: `EP-BASE + EP-SCANNER-HIDDEN-METADATA-FIXTURES`

Fault: protected history signal exists only in MIME metadata, connector/reference metadata, attachment name, content-disposition, or wrapper metadata while visible text remains clean.

Expected: scanner detects leak; `REVIEW_HISTORY_METADATA_LEAKED` or `REVIEW_HISTORY_COMMITMENT_SIDECHANNEL` as applicable.

### WDPC-255 — Packet generation omitted from proof view

Mechanisms: `MECH-PACKET-GENERATION-VISIBILITY`, `MECH-PROOF-VIEW-COMPLETENESS`
Profiles: `EP-BASE + EP-PACKET-GENERATION-VISIBILITY + EP-PROOF-VIEW-COMPLETENESS`

Fault: reviewer-safe manifest/proof omits `packet_generation`, predecessor/currentness, or supersession state.

Expected: predicate treated `NOT_PRESENT`; `REVIEW_PACKET_GENERATION_STALE` + `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; threshold contribution zero.

### WDPC-256 — Authoritative endpoint registry export bound to wrong candidate

Mechanisms: `MECH-ENDPOINT-EXPORT-CANDIDATE-BINDING`
Profiles: `EP-BASE + EP-ENDPOINT-EXPORT-CANDIDATE-BINDING`

Fault: authoritative endpoint tuple export comes from another candidate with identical registry/schema version.

Expected: exact-candidate binding mismatch; `REVIEW_ENDPOINT_TUPLE_AUTHORITY_MISSING` or `REVIEW_ENDPOINT_TUPLE_MISMATCH`; qualification blocked.

### WDPC-257 — Atomic qualification-to-threshold positive control

Mechanisms: `MECH-QUALIFICATION-THRESHOLD-ATOMICITY`, `MECH-THRESHOLD-IDEMPOTENT-CONSUMPTION`
Profiles: `EP-BASE + EP-QUALIFICATION-THRESHOLD-ATOMICITY + EP-THRESHOLD-IDEMPOTENT-CONSUMPTION`

Positive control: all qualification predicates are current and one `ReviewThresholdRecord` atomically consumes the exact snapshot with no intervening governed state change.

Expected: one eligible count may commit; retry with the same idempotency key does not double count.

### WDPC-258 — Independent re-expression verifier positive control

Mechanisms: `MECH-REEXPRESSION-VERIFIER-INDEPENDENCE`
Profiles: `EP-BASE + EP-REEXPRESSION-VERIFIER-INDEPENDENCE`

Positive control: independent NRVA verifies a semantically equivalent mixed-block re-expression that removes concrete history while preserving scope, timing, authority, evidence, and fail-closed semantics.

Expected: verification may PASS without false block; RPAA independently agrees on projection equivalence.

### WDPC-259 — Reviewer-safe packet generation positive control

Mechanisms: `MECH-PACKET-GENERATION-VISIBILITY`, `MECH-PROOF-VIEW-COMPLETENESS`
Profiles: `EP-BASE + EP-PACKET-GENERATION-VISIBILITY + EP-PROOF-VIEW-COMPLETENESS`

Positive control: packet manifest/proof exposes current packet generation, predecessor/supersession state, candidate/projection/proof digests, and class without exposing protected review history.

Expected: no false `REVIEW_PACKET_GENERATION_STALE`; design packet remains threshold contribution zero unless otherwise qualifying.

### WDPC-260 — Scanner hidden-metadata clean positive control

Mechanisms: `MECH-SCANNER-HIDDEN-METADATA-FIXTURES`
Profiles: `EP-BASE + EP-SCANNER-HIDDEN-METADATA-FIXTURES`

Positive control: benign MIME/reference/attachment/wrapper metadata contains no protected history and passes the current governed scanner.

Expected: no false metadata-leak block.

## 3. Coverage accounting

WDPC-240 and WDPC-244 remain `DUPLICATIVE_BUT_USEFUL` for history-commitment side-channel coverage and count as one unique enforcement path unless independently demonstrated otherwise.

## 4. Freeze rule

V16 remains `NOT EXECUTED`.

No execution freeze while unresolved Critical/High design findings remain. No stale qualification snapshot, omitted packet generation, colluding semantic verifier, false canonical split, hidden metadata leak, or wrong-candidate endpoint export may satisfy qualification.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
