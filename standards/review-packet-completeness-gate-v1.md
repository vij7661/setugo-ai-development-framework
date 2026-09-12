# Review Packet Completeness Gate — V1

Status: **PROPOSED — IMPLEMENTED RUNTIME VALIDATOR — REVIEW REQUIRED**

Authority effect: **NONE_EVIDENCE_ONLY**

## RPCG-01 — Purpose

No independent-review packet may be sent as a governed review surface unless a deterministic preflight proves that the packet contains the complete review surface requested by its own instructions.

A packet defect is distinct from a design defect. Missing review material, malformed embedding, hash mismatch, or clean-room contamination must not create a new design version by itself.

## RPCG-02 — Required review-surface manifest

Every governed packet has a machine-readable manifest binding at minimum:

- exact candidate Git commit;
- packet class;
- every required artifact path;
- exact Git blob SHA for each artifact;
- `FULL_TEXT` review-surface status for each required artifact;
- every required clause identifier;
- every required falsification/test-case identifier;
- clean-room forbidden strings or other prior-review contamination markers applicable to the packet;
- whether unlisted embedded artifacts are permitted.

A path/SHA reference alone is not sufficient when the reviewer is instructed to operate in packet-only or clean-room context.

## RPCG-03 — Requested audit set must be a subset of supplied review surface

Before packet emission:

`REQUESTED_AUDIT_SET ⊆ SUPPLIED_EXACT_REVIEW_SURFACE`

must evaluate true.

If a prompt asks the reviewer to audit `P24-01…P24-25`, each requested clause must appear as a definition in the packet. A mere mention in a summary does not count.

If a prompt asks the reviewer to audit `WDPC-431…506`, each case must be physically present as a case definition.

Failure returns `PACKET_INVALID`.

## RPCG-04 — Exact artifact bytes

Every required embedded artifact is delimited by deterministic BEGIN/END markers carrying its repository path and expected Git blob SHA.

The preflight recomputes the Git blob SHA from the exact embedded UTF-8 bytes. Any mismatch returns `PACKET_INVALID`.

The packet assembler must verify source bytes before assembly and the resulting embedded bytes after assembly.

## RPCG-05 — Clean-room isolation

For a clean independent review, prior concrete reviewer findings, prior disposition text, or other forbidden contamination must be absent unless the active protocol explicitly requires them.

The preflight uses manifest-bound forbidden markers and fails closed on a match.

Historical review evidence remains preserved outside the clean packet.

## RPCG-06 — Candidate binding

The packet must explicitly bind the exact candidate commit. A review of one candidate cannot authorize a successor candidate.

A packet whose candidate binding is missing or inconsistent is `PACKET_INVALID`.

## RPCG-07 — Fail-closed emission

The governed assembler must not create or retain the final output packet unless deterministic preflight returns exactly:

`PACKET_READY`

Any missing artifact, hash mismatch, missing clause/case definition, duplicate artifact, unlisted artifact when prohibited, malformed marker, candidate mismatch, or clean-room contamination blocks packet emission.

## RPCG-08 — Packet defect classification

If an independent reviewer cannot perform the requested audit because required review material is absent, classify the event as:

`REVIEW_PACKET_DEFECT`

not automatically as a design defect.

The deficient packet and reviewer response are preserved historically. Repairing only the packet does not require a new design candidate SHA.

A design version changes only when design/artifact bytes change.

## RPCG-09 — Machine-readable report

Every packet preflight emits a report containing:

- `PACKET_READY` or `PACKET_INVALID`;
- exact candidate commit;
- packet SHA-256;
- required/embedded artifact counts;
- required clause count;
- required case count;
- per-check `PASS`/`FAIL` details.

The report is evidence only and does not grant review authority.

## RPCG-10 — Runtime implementation

The reference implementation is:

- `governance-runtime/review_packet_preflight.py`
- `governance-runtime/assemble_clean_review_packet.py`
- `governance-runtime/test_review_packet_preflight.py`

Future packet builders may use another implementation only if they satisfy the same fail-closed contract and are independently qualified under the applicable governance.

## RPCG-11 — Mandatory future attacks

Reviews/tests of the gate must attempt at least:

- requested clause absent but mentioned in summary;
- requested case range partially absent;
- embedded artifact content changed without blob update;
- declared blob rebound to another artifact;
- duplicate/unlisted artifact injection;
- prior-review finding/disposition contamination;
- candidate SHA rebound;
- malformed/missing artifact terminator;
- packet emitted despite failed preflight.

## RPCG-12 — Nonclaims

This gate proves packet construction properties only. It does not prove that the underlying design is correct, that an independent reviewer is qualified, or that the reviewer actually performed the requested audit.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
