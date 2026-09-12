# ECC-Derived V6 Eligibility Provenance Ledger

Status: `V6_CLEAN_PRE_REPAIR_RED_PRESERVED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V5 closed ledger head: `3691af1642c1b68d7a1c9612a91bda4a49998de2`
- V5 state: `V5_BOUNDED_REFERENCE_GREEN_PROVENANCE_FALSIFICATION_REQUIRED`
- V5 open risk: `V5-OPEN-ELIGIBILITY-PROVENANCE-001`

## V6 hypothesis

V6 tests whether a consumer can self-grant candidate eligibility merely by reconstructing the correct serialized fields.

A positive V6 reference result must:

1. originate from the governed candidate boundary in the current process;
2. carry process-local opaque provenance that a plain dictionary does not carry;
3. bind provenance to the exact result payload so any post-issuance mutation invalidates eligibility;
4. lose eligibility after plain-dict copying or JSON reconstruction;
5. reject pickle laundering of the process-local provenance object;
6. reject marker injection into direct strict-core results; and
7. re-run runtime-policy verification when eligibility is consumed.

This is deliberately a process-local reference provenance mechanism. It is not a durable cross-process signature, an independent production trust root, or live platform attestation. Durable signed receipts remain a later integration boundary.

## Frozen assertions

- V6 assertion commit: `f0c9889ca5dbb6c504344575150bcbf896c91daa`
- V6 runner initial commit: `509a908796d1f05563f0be37f905ad4b2e6ef730`
- V6 workflow-enabled SHA: `fcb41b8ae0e4d0a8bebec4020601d0ec0ba5c4ac`
- V6 runner-filter-only repair SHA: `169ec0e5da3c5648a73065ca972dd757347d3fca`

The V6 assertion file was frozen before mechanism repair and remains unchanged.

## RED-001

- exact SHA: `fcb41b8ae0e4d0a8bebec4020601d0ec0ba5c4ac`
- run: `34693050639`
- job: `103551624872`
- result: `156 tests; 11 failures; 0 errors`
- additional finding: runner test-level supersession filter defect; obsolete V5 raw-dict positive assertion still ran but passed pre-repair.

The harness defect was preserved separately and authorized only a runner-filter repair.

## RED-002 — clean pre-repair RED

- exact SHA: `169ec0e5da3c5648a73065ca972dd757347d3fca`
- run: `34693109203`
- job: `103551787848`
- result: `155 tests; 11 failures; 0 errors`
- superseded V5 raw-dict positive assertion: correctly excluded
- mechanism repair begun: `NO`

The 11 failures prove the current V5 field-only marker is caller-forgeable and mutation/reconstruction blind.

## Current disposition

`V6_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
