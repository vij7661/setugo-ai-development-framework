# Workflow Drift & Parent-Child Impact Falsification Matrix — V14 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V14`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V14 inherits WDPC-01…224 as mandatory regressions under the composite V5→V14 rules.

V14 adds WDPC-225…WDPC-237.

## 2. New cases

### WDPC-225 — Reviewer-facing proof leaks history cardinality

Mechanisms: `MECH-HISTORY-NONDISCLOSURE`
Profiles: `EP-BASE + EP-HISTORY-NONDISCLOSURE`

Fault: design-review proof contains excluded-history count/cardinality.

Expected: `REVIEW_HISTORY_METADATA_LEAKED`; packet ineligible until regenerated without cardinality.

### WDPC-226 — Reviewer-facing projection leaks history block IDs

Mechanisms: `MECH-HISTORY-NONDISCLOSURE`
Profiles: `EP-BASE + EP-HISTORY-NONDISCLOSURE`

Fault: reviewer-facing projection/manifest contains source history block identifiers, filenames, reviewer identities, or outcome-bearing ordering metadata.

Expected: `REVIEW_HISTORY_METADATA_LEAKED`.

### WDPC-227 — Endpoint tuple mismatch hidden by endpoint-name equality

Mechanisms: `MECH-ENDPOINT-TUPLE-EQUALITY`
Profiles: `EP-BASE + EP-ENDPOINT-TUPLE-EQUALITY`

Fault: endpoint ID survives projection but owner/schema/predecessor/successor/evidence-profile binding changes or disappears.

Expected: `REVIEW_ENDPOINT_TUPLE_MISMATCH` or `REVIEW_PROJECTION_EQUIVALENCE_FAILED`.

### WDPC-228 — Missing signed RHCA/RPB/RPAA records in qualifying packet

Mechanisms: `MECH-PROJECTION-AUTHORITY-ATTESTATION`
Profiles: `EP-BASE + EP-PROJECTION-AUTHORITY-ATTESTATION`

Fault: packet is labeled `QUALIFYING_INDEPENDENT_REVIEW_PACKET` but one or more authority-independence records or RPAA signature is absent/stale.

Expected: `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; threshold count remains zero.

### WDPC-229 — Source-only canonical normative/endpoint item

Mechanisms: `MECH-CANONICAL-NORMATIVE-EQUALITY`, `MECH-ENDPOINT-TUPLE-EQUALITY`
Profiles: `EP-BASE + EP-CANONICAL-NORMATIVE-EQUALITY + EP-ENDPOINT-TUPLE-EQUALITY`

Fault: any active canonical normative clause or endpoint tuple exists in source but not projection.

Expected: exact set difference non-empty; projection fails.

### WDPC-230 — Missing clean-room attestation in qualifying packet

Mechanisms: `MECH-QUALIFYING-CLEANROOM`
Profiles: `EP-BASE + EP-QUALIFYING-CLEANROOM`

Fault: packet attempts to count toward independent threshold without platform-signed clean-room evidence.

Expected: `REVIEWER_CLEAN_ROOM_INSUFFICIENT` + `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; count zero.

### WDPC-231 — Missing source attestation in qualifying packet

Mechanisms: `MECH-QUALIFYING-SOURCE-ATTESTATION`
Profiles: `EP-BASE + EP-QUALIFYING-SOURCE-ATTESTATION`

Fault: exact packet bytes are self-consistent but no independent source-repository attestation exists.

Expected: `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`; review may remain engineering feedback only.

### WDPC-232 — Design-review packet relabeled qualifying after review

Mechanisms: `MECH-PACKET-CLASS`, `MECH-QUALIFICATION-SNAPSHOT`
Profiles: `EP-BASE + EP-PACKET-CLASS + EP-QUALIFICATION-SNAPSHOT`

Fault: actor changes metadata from `DESIGN_REVIEW_PACKET` to `QUALIFYING_INDEPENDENT_REVIEW_PACKET` after review.

Expected: `REVIEW_PACKET_CLASS_MISMATCH`; original class/history remains authoritative; count zero.

### WDPC-233 — Review outcome token misclassified as endpoint

Mechanisms: `MECH-CANONICAL-NORMATIVE-EQUALITY`, `MECH-REVIEWER-SAFE-PROOF`
Profiles: `EP-BASE + EP-CANONICAL-NORMATIVE-EQUALITY + EP-REVIEWER-SAFE-PROOF`

Fault: uppercase review status token is interpreted as governed endpoint solely due lexical shape.

Expected: typed extractor classifies it `REVIEW_HISTORY_STATUS`; it cannot satisfy endpoint contract equality.

### WDPC-234 — Mixed history/normative block safe re-expression positive

Mechanisms: `MECH-NORMATIVE-REEXPRESSION`, `MECH-CANONICAL-NORMATIVE-EQUALITY`
Profiles: `EP-BASE + EP-NORMATIVE-REEXPRESSION + EP-CANONICAL-NORMATIVE-EQUALITY`

Positive control: a source block contains concrete review-history wording plus an active generic obligation.

Expected: projected abstract text removes concrete outcome but preserves identical canonical normative clause IDs; equivalence passes.

### WDPC-235 — Qualification snapshot mixed-generation rollback

Mechanisms: `MECH-QUALIFICATION-SNAPSHOT`
Profiles: `EP-BASE + EP-QUALIFICATION-SNAPSHOT`

Fault: current projection is paired with stale source attestation, clean-room record, RPAA record, or proof/log sequence.

Expected: `REVIEW_PACKET_PROVENANCE_MISMATCH`; qualifying status blocked.

### WDPC-236 — Design-review packet positive control

Mechanisms: `MECH-PACKET-CLASS`, `MECH-REVIEWER-SAFE-PROOF`
Profiles: `EP-BASE + EP-PACKET-CLASS + EP-REVIEWER-SAFE-PROOF`

Positive control: packet is explicitly `DESIGN_REVIEW_PACKET`, carries reviewer-safe bounded proof, omits live qualifying attestations, and is used only for AI engineering feedback.

Expected: review may proceed; threshold contribution remains zero; no false requirement that absent runtime attestations be fabricated.

### WDPC-237 — Fully attested qualifying packet positive control

Mechanisms: `MECH-PACKET-CLASS`, `MECH-PROJECTION-AUTHORITY-ATTESTATION`, `MECH-QUALIFYING-CLEANROOM`, `MECH-QUALIFYING-SOURCE-ATTESTATION`, `MECH-QUALIFICATION-SNAPSHOT`
Profiles: `EP-BASE + EP-PACKET-CLASS + EP-PROJECTION-AUTHORITY-ATTESTATION + EP-QUALIFYING-CLEANROOM + EP-QUALIFYING-SOURCE-ATTESTATION + EP-QUALIFICATION-SNAPSHOT`

Positive control: every required current attestation is valid for the same candidate/projection/packet generation and eligible reviewer evidence class.

Expected: packet may be eligible to count under the active gate; no authority is granted merely by packet eligibility.

## 3. Freeze rule

V14 remains `NOT EXECUTED`.

No design-review packet or AI engineering review can satisfy qualifying independent-review thresholds.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
