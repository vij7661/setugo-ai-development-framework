# R8 v15-r1 Executable Schema V1 — Internal Supersession Record

Status: **SUPERSEDED_BEFORE_EXTERNAL_REVIEW**
Authority effect: **NONE**

Superseded candidate:
- branch: `freeze/r8-v15-r1-executable-schema-v1`
- prepared review branch: `review/r8-v15-r1-executable-schema-v1-2026-09-23`

Reason:

Internal pre-handoff review found that V1 encoded the current normalized runtime and registry semantics, but its executable-schema freeze package did not carry forward several inherited schema-freeze obligations that remain unsuperseded:

1. SPM-1 per-schema-element provenance and RG-1 enforcement — R8V7-I030/I031.
2. SchemaProvenanceGenerator enrollment/runtime-attestation requirement — R8V8-I020..I022.
3. GCP-RVM-2 — R8V8-I034/I035.
4. RPS-1 reviewer-visible semantic classification — R8V7-I038/I039.
5. CaseProofContracts and FP0..FP6 requirements for every current guard — inherited schema-freeze gates through R8 v13, extended to G001..G156 by current GuardRegistry.

This is a schema-freeze-process completeness defect, not a change to the accepted R8 v15-r1 semantic design.

V1 must not be sent for independent review or used for implementation authorization.

Successor:
- `freeze/r8-v15-r1-executable-schema-v2`

The V2 successor must close the inherited freeze obligations without changing semantic candidate:
- `c721b38cf8b00294797300b526596ce723a47ff8`.
