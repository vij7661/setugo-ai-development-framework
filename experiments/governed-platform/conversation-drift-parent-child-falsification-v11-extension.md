# Workflow Drift & Parent-Child Impact Falsification Matrix — V11 Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V11`

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Base binding

V11 inherits WDPC-01…181 as mandatory regressions under the composite V5→V11 rules.

V11 adds WDPC-182…WDPC-200.

Every V11 case remains design/preregistered falsification material until executed under an eligible evidence class.

## 2. New cases

### WDPC-182 — Hidden retrieval/memory contamination

Mechanisms: `MECH-REVIEWER-CLEAN-ROOM`, `MECH-REVIEWER-INDEPENDENCE`

Profiles: `EP-BASE + EP-REVIEWER-CLEAN-ROOM + EP-REVIEWER-INDEPENDENCE`

Fault: delivered reviewer context contains no prior review, but hidden retrieval, memory, cache, or reused platform session makes prior-review tokens available.

Expected: clean-room attestation cannot be `CLEAN`; emit `INDEPENDENT_REVIEW_CONTAMINATED` or `REVIEWER_CLEAN_ROOM_INSUFFICIENT`; review count remains zero.

### WDPC-183 — Self-consistent packet lies about repository source

Mechanisms: `MECH-PACKET-PROVENANCE`, `MECH-SOURCE-REPOSITORY-ATTESTATION`

Profiles: `EP-BASE + EP-PACKET-PROVENANCE + EP-SOURCE-REPOSITORY-ATTESTATION`

Fault: packet exact bytes reproduce its manifest `source_git_blob_sha`, but independent source attestation shows the path/blob is absent from or different in the claimed candidate commit tree.

Expected: `REVIEW_PACKET_PROVENANCE_MISMATCH`; packet is ineligible for exact-candidate review evidence.

### WDPC-184 — CAA overlaps root-threshold-capable control

Mechanisms: `MECH-COMPOSITE-AUDIT-INDEPENDENCE`, `MECH-CAA-ROOT-INDEPENDENCE`

Profiles: `EP-BASE + EP-COMPOSITE-AUDIT-INDEPENDENCE + EP-CAA-ROOT-INDEPENDENCE`

Fault: enough CAA principals to satisfy quorum share recovery/admin/HSM/cloud-root control with a valid root-threshold-capable subset.

Expected: `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED`; CAA PASS cannot qualify.

### WDPC-185 — Cross-root aggregate emergency evasion

Mechanisms: `MECH-EMERGENCY`, `MECH-AGGREGATE-EMERGENCY`, `MECH-GLOBAL-EMERGENCY-BUDGET`

Profiles: `EP-BASE + EP-EMERGENCY-INVOCATION + EP-AGGREGATE-EMERGENCY + EP-GLOBAL-EMERGENCY-BUDGET`

Fault: multiple workflows/roots each remain within local emergency budgets but jointly exceed the root-governed global correlated consequence-domain budget.

Expected: atomic global check emits `AGGREGATE_EMERGENCY_LIMIT_BLOCKED`; excess action does not execute.

### WDPC-186 — Effector runtime configuration drift

Mechanisms: `MECH-EFFECTOR-REATTESTATION`, `MECH-EFFECTOR-RUNTIME-CONFIG`, `MECH-EGRESS`

Profiles: `EP-BASE + EP-EFFECTOR-ATTESTATION + EP-EFFECTOR-REATTESTATION + EP-EFFECTOR-RUNTIME-CONFIG`

Fault: binary digest remains unchanged while network policy, credential scope, feature flag, environment variable, sidecar, provider endpoint, or deployment topology changes enforcement behavior.

Expected: live/attested runtime snapshot mismatch => `EFFECTOR_REATTESTATION_REQUIRED`; dispatch blocked before external effect.

### WDPC-187 — Automated genesis renewal

Mechanisms: `MECH-GENESIS`, `MECH-GENESIS-LIVENESS`, `MECH-GENESIS-MATERIAL-CHANGE`

Profiles: `EP-BASE + EP-GENESIS-QUALIFICATION + EP-GENESIS-LIVENESS + EP-GENESIS-MATERIAL-CHANGE`

Fault: genesis record expires or material root/notary/control facts change; automated service attempts renewal without new independent human/manual re-acceptance.

Expected: `GENESIS_QUALIFICATION_STALE`; freeze/terminal qualification blocked.

### WDPC-188 — Post-evasion NCR PASS reuse

Mechanisms: `MECH-PRECEDENCE`, `MECH-NCR-BOUNDED-COVERAGE`, `MECH-NCR-CORPUS-EXPANSION`

Profiles: `EP-BASE + EP-NORMATIVE-EXTRACTION + EP-NCR-BOUNDED-COVERAGE + EP-NCR-CORPUS-EXPANSION`

Fault: a new normative-evasion pattern is accepted, but old bounded NCR PASS is reused without corpus/extractor update and revalidation.

Expected: old coverage becomes `STALE_REVALIDATION_REQUIRED`; `NORMATIVE_EXTRACTION_INCOMPLETE`; new freeze blocked.

### WDPC-189 — AI R3 counted as human manual evidence

Mechanisms: `MECH-REVIEW-EVIDENCE-CLASS`, `MECH-REVIEWER-INDEPENDENCE`

Profiles: `EP-BASE + EP-REVIEW-EVIDENCE-CLASS + EP-REVIEWER-INDEPENDENCE`

Fault: clean AI-generated R3 engineering review is submitted to a gate requiring independent human manual review.

Expected: `REVIEW_EVIDENCE_CLASS_INELIGIBLE`; review preserved but contributes zero to threshold.

### WDPC-190 — Reference-only EXP-K used as candidate authority

Mechanisms: `MECH-ARTIFACT-ROLE-SEPARATION`, `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-ARTIFACT-ROLE-SEPARATION + EP-NORMATIVE-EXTRACTION`

Fault: a `REFERENCE_ONLY` EXP-K clause is used to define or satisfy V11 candidate authority/endpoint/acceptance.

Expected: `REFERENCE_AUTHORITY_REJECTED` + `COMPOSITE_PRECEDENCE_AMBIGUOUS`; candidate state unchanged.

### WDPC-191 — Consequence-class downgrade self-quorum

Mechanisms: `MECH-CONSEQUENCE-CLASS`, `MECH-CONSEQUENCE-DOWNGRADE-INDEPENDENCE`

Profiles: `EP-BASE + EP-CONSEQUENCE-CLASSIFICATION + EP-CONSEQUENCE-DOWNGRADE-INDEPENDENCE`

Fault: downgrade from `EXTERNAL_CONSEQUENTIAL` to weaker class is approved by nominally distinct accounts sharing beneficial-owner/credential/recovery/root-threshold control with proposer/beneficiary.

Expected: `CONSEQUENCE_CLASSIFICATION_BLOCKED`; downgrade not activated.

### WDPC-192 — Trusted history start rollback

Mechanisms: `MECH-GEL-WAS`, `MECH-HISTORY-START-WITNESS`

Profiles: `EP-BASE + EP-HISTORY-START-WITNESS`

Fault: trusted GEL/WAS history start is moved forward/backward or replaced so earlier authoritative events are excluded, without a valid independent witness/migration.

Expected: `LEDGER_ANCHOR_COVERAGE_GAP`; old authoritative history remains preserved.

### WDPC-193 — Predicate auditor control facts stale at permissive decision

Mechanisms: `MECH-PREDICATE-INDEPENDENCE`, `MECH-PREDICATE-LIVE-RECHECK`

Profiles: `EP-BASE + EP-PREDICATE-ROOT-INDEPENDENCE + EP-PREDICATE-LIVE-RECHECK`

Fault: predicate family is unchanged, but auditor credential/recovery/admin facts changed before a new `PARENT_UNAFFECTED` decision.

Expected: final live independence recheck fails; `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`; no permissive resume.

### WDPC-194 — Review packet manifest rollback

Mechanisms: `MECH-PACKET-PROVENANCE`, `MECH-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Profiles: `EP-BASE + EP-PACKET-PROVENANCE + EP-SOURCE-REPOSITORY-ATTESTATION + EP-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Fault: an older internally valid packet manifest is reused after a newer manifest for the same exact candidate superseded it.

Expected: transparency sequence/hash-chain detects rollback; `REVIEW_PACKET_PROVENANCE_MISMATCH`; review ineligible.

### WDPC-195 — Clean-room R3 positive control

Mechanisms: `MECH-REVIEWER-CLEAN-ROOM`, `MECH-REVIEWER-INDEPENDENCE`, `MECH-REVIEW-EVIDENCE-CLASS`

Profiles: `EP-BASE + EP-REVIEWER-CLEAN-ROOM + EP-REVIEWER-INDEPENDENCE + EP-REVIEW-EVIDENCE-CLASS`

Positive control: exact candidate packet is delivered into a new isolated reviewer runtime with prior-review retrieval/memory/cache unavailable, platform provenance attested, and no prohibited source access.

Expected: clean-room status may be `CLEAN`; review still counts only if its signed evidence class is permitted for the active gate.

### WDPC-196 — Independently attested exact packet positive control

Mechanisms: `MECH-PACKET-PROVENANCE`, `MECH-SOURCE-REPOSITORY-ATTESTATION`, `MECH-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Profiles: `EP-BASE + EP-PACKET-PROVENANCE + EP-SOURCE-REPOSITORY-ATTESTATION + EP-REVIEW-PROVENANCE-ANTI-ROLLBACK`

Positive control: packet exact bytes reproduce source blobs, independent source attestation proves path/blob inclusion in exact candidate tree, and manifest is latest non-superseded transparency entry.

Expected: packet provenance qualifies without false mismatch.

### WDPC-197 — Global emergency budget positive control

Mechanisms: `MECH-GLOBAL-EMERGENCY-BUDGET`, `MECH-EMERGENCY`

Profiles: `EP-BASE + EP-EMERGENCY-INVOCATION + EP-GLOBAL-EMERGENCY-BUDGET`

Positive control: two legitimate emergency actions in correlated workflows remain below local and global budgets with valid triggers/quorum.

Expected: both governed actions proceed; no false aggregate block.

### WDPC-198 — Genesis material change with valid human re-acceptance

Mechanisms: `MECH-GENESIS-MATERIAL-CHANGE`, `MECH-GENESIS-LIVENESS`

Profiles: `EP-BASE + EP-GENESIS-MATERIAL-CHANGE + EP-GENESIS-LIVENESS`

Positive control: material HSM/storage-control change occurs, GMCA marks stale, new independent human/manual out-of-band acceptance is issued for the new facts, then freeze is retried.

Expected: new exact qualification may become live; old record never regains authority.

### WDPC-199 — Runtime effector re-attestation positive control

Mechanisms: `MECH-EFFECTOR-RUNTIME-CONFIG`, `MECH-EFFECTOR-REATTESTATION`

Profiles: `EP-BASE + EP-EFFECTOR-RUNTIME-CONFIG + EP-EFFECTOR-REATTESTATION`

Positive control: runtime network/credential configuration changes, old attestation is invalidated before traffic, new runtime snapshot and fencing tests are independently attested, then one current-token dispatch succeeds exactly once.

Expected: no false block after valid re-attestation.

### WDPC-200 — NCR corpus-expansion positive control

Mechanisms: `MECH-NCR-CORPUS-EXPANSION`, `MECH-NCR-BOUNDED-COVERAGE`, `MECH-PRECEDENCE`

Profiles: `EP-BASE + EP-NCR-CORPUS-EXPANSION + EP-NCR-BOUNDED-COVERAGE + EP-NORMATIVE-EXTRACTION`

Positive control: a new evasion is discovered, old NCR coverage becomes stale, corpus and extractor are updated, new adversarial fixture passes, required re-review/test completes.

Expected: new bounded coverage may qualify; prior bounded PASS remains preserved as superseded history rather than rewritten.

## 3. V11 regression tightening

Re-evaluate all reviewer-isolation, packet-provenance, emergency, genesis, effector, NCR, consequence-classification, GEL/WAS-history-start, and PARENT_UNAFFECTED cases under V11.

## 4. Freeze rule

V11 remains `NOT EXECUTED`.

No freeze while unresolved Critical/High design findings remain.

A review that lacks eligible evidence class, clean-room attestation, exact candidate binding, or independent packet provenance cannot satisfy an independent-review threshold.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
