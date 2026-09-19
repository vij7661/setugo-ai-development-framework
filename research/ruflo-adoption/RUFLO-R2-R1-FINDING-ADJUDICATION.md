# Ruflo Selective Adoption R2 — R1 Finding Adjudication

Status: `R1_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R2_REVIEW`

Authority effect: `NONE`

The R1 independent review found 0 Critical and 2 High findings. All R1 High and Medium/Low/cross-composition items below are treated as valid design feedback and incorporated into R2 unless explicitly marked otherwise.

## High closure

### H-01 — RA-04 per-child bound amplifies consumables

Disposition: `REPAIRED_FOR_R2_REVIEW`

R2 changes:

- split non-consumable subset semantics from consumable conservation;
- atomic parent-ledger reservation;
- hierarchical child subdelegation consumes child reserved balance;
- parent own-use + all live child reservations must remain <= grant;
- recorded release/re-lend;
- child lifetime cannot exceed parent;
- depth/breadth/sibling race fixtures;
- check-then-write mutation required to fail.

### H-02 — RA-11 enforcement absent from automation prerequisites

Disposition: `REPAIRED_FOR_R2_REVIEW`

R2 changes:

- explicit RA-11 diagnostic vs enforcement distinction;
- prerequisite matrix replaces ordinal presence-only gating;
- RA-11 enforcement required before RA-10/12/13 authority-bearing automation;
- RA-03/04/09/11 enforcement required before multi-writer/swarm/research;
- additional RA-06/07/08/10 dependencies for the research cycle;
- verified-load TOCTOU, revoked publisher/key, transitive dependency, dynamic-code fetch and valid-signature sandbox-escape scenarios.

## Medium/Low closure

### M-01 — unscoped qualified

Replaced bare qualification with a subject/scope/program/version/generation-bound predicate. Health cannot renew invalidated qualification. Stale-generation use is tested.

### M-02 — assurance composition undefined

Evidence assurance is per subject/claim/evidence. Trust roots are explicit. Derived assurance cannot launder weaker inputs. Accepted combinations are governing rules outside candidate write authority.

### M-03 — promotion authority / concurrency bootstrap

External authorization derives from authority snapshot and defaults required when no lower rule exists. Evaluator cannot write authority state. Receipt issuer trust is separated. FP-02 AuthorityGenerationCAS plus serialized-writer precondition precedes RA-10.

### M-04 — RA-07 depends on RA-08 primitives

CanonicalRecordIdentity is extracted as FP-01 and reviewed before RA-07/08. RA-07 may use opaque/digest links without authority-bearing memory semantics.

### M-05 — append-only mechanism / quarantine

Added FP-03 TamperEvidentLedger with hash chain, monotonic sequence and independent anchor. Added rollback/truncation/fork tests. Sensitive payload can be quarantined while digest/tombstone/history remains. RA-07 cannot act as a deny-list.

### M-06 — source vs execution context

Separated SourceStateReceipt and ExecutionContextReceipt. Added independent canonical SHA-256, toolchain/container/dependency/runtime-input identities and non-secret credential version/fingerprint where relevant. Promotion requires committed source; dirty evidence never transfers without rerun.

### M-07 — tests were scenario seeds only

All R2 experiment families now require deterministic pass/fail predicate, positive control, negative fixtures, test-the-test mutation, first-failure preservation and generated counts.

### M-08 — withheld findings unverifiable

R2 publishes SHA-256 commitment to the withheld self-adjudication ledger. Reveal occurs only after independent R2 review.

### M-09 — fencing local self-check

Protected resource/write authority must atomically validate fencing token. Writer-only check is insufficient.

### L-01 — authority boundary undefined

R2 enumerates authority-changing/credential/network/egress/evidence/memory/concurrency/budget/plugin/release boundaries.

### L-02 — stable EXP-M trigger undefined

R2 defines exact stable deterministic EXP-M conditions, including R5 source freeze, A-T exit, zero mutation survivors and independent implementation review.

### L-03 — package identity

R2 review handoff uses non-recursive package manifest plus separately reported manifest and ZIP SHA-256 values. Manual pasted review remains user-attested external evidence unless separately authenticated.

### L-04 — Ruflo source status absent

R2 adds `RUFLO-R2-SOURCE-STATUS-MANIFEST.json` recording the exact source blob and Ruflo-declared status (Proposed/Accepted/implemented where declared). Ruflo status is contextual only.

### L-05 — failure archive as deny-list

Explicitly prohibited. Revocation/blocking requires a current authority-bearing policy decision.

## Cross-composition closure

### E-01 — RA-05 -> RA-01 registry laundering

Dependency is one-way: named authoritative stores -> capability projection -> generated report. Generated registry cannot mint qualified/authorized state.

### E-02 — RA-06 + RA-02/03 dirty evidence transfer

Receipts carry source-state type. Promotion requires COMMITTED_SOURCE_STATE. Dirty-snapshot evidence does not transfer even if later committed tree bytes match; rerun is required.

### E-03 — RA-04 + RA-12/13 aggregate amplification

Closed with hierarchical consumable conservation and prerequisite matrix.

### E-04 — RA-09 + RA-11/04 composed exfiltration

Added FP-04 DataFlowLabel. Sensitive-read + untrusted-ingest + external-egress is denied by default without an exact composed-flow grant. Labels propagate; declassification is separately authorized.

### E-05 — RA-07/08/11 persistent injection

Archived model/agent/external text returns as provenance-bound data, not instructions/authority. Quarantine/redaction status travels with the record.

## Additional R2 hardening before handoff

R2 also adds:

- FP-01 CanonicalRecordIdentity;
- FP-02 AuthorityGenerationCAS;
- FP-03 TamperEvidentLedger;
- FP-04 DataFlowLabel;
- hierarchical conservation across descendant delegation;
- dynamic plugin-code fetch closure;
- platform-owned ToolRiskRegistry;
- execution receipt binding for secret/credential version identity where relevant;
- RA-08 active projection requiring CAS;
- RA-10 requiring exact source/execution receipts;
- RA-12 requiring capability projection correctness;
- RA-13 requiring governed memory provenance/supersession.

This document is a proposer remediation record only. The independent R2 reviewer must reconstruct closure from the current R2 sources and may reject any claimed closure.
