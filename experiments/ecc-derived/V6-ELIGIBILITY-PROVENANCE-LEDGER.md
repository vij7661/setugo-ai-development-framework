# ECC-Derived V6 Eligibility Provenance Ledger

Status: `V6_BOUNDED_PROCESS_LOCAL_PROVENANCE_GREEN_PENDING_EXTERNAL_REREVIEW`

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

The V6 assertion file was frozen before mechanism repair and remained unchanged during repair.

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

The same 11 mechanism failures remained after the harness-only correction, proving the V5 field-only marker was caller-forgeable and mutation/reconstruction blind.

## Deterministic provenance repair

- repair input SHA: `40dec44bdc2d682a397871a2628256fbad73b098`
- repair workflow run: `34693224638`
- repair job: `103552117673`
- repair-generated mechanism SHA: `f445442b8727ac14b19f4fe6103bda69af14dbee`
- V6 assertion modification during repair: `NONE`
- candidate-boundary SHA-256: `72625006fa79efb013857b008b6ed0f2603751f08d3ef843520064626ccdf358`
- trust-manifest SHA-256: `9362fa6c2dde51d7bf0354ec6b0ccb0ec83b6e9e6880415aba888b7ca2578d22`

The repair adds a process-local boundary-issued dict subclass with a hidden issuer token and canonical payload digest. Only successful candidate-eligible results are sealed. Eligibility consumption requires valid provenance, unchanged payload, favorable kind/status, and a current runtime-policy check. Pickling the sealed object is intentionally rejected; plain-dict or JSON reconstruction loses candidate eligibility.

Manifest posture:

- `eligibility_provenance_policy = PROCESS_LOCAL_OPAQUE_SEAL_AND_PAYLOAD_DIGEST`
- `serialized_candidate_authority = REJECT_UNSEALED_RECONSTRUCTION`
- `process_local_provenance_only = true`
- `durable_cross_process_signature_claimed = false`
- remaining provenance boundary: `DURABLE_SIGNED_RECEIPT_OR_EXTERNAL_TRUST_SERVICE_FOR_CROSS_PROCESS_USE`

## GREEN-003

- exact tested SHA: `e7341a273f5b37459007a93e3165bff9b5a1ed0e`
- run: `34693257804`
- job: `103552209262`
- result: `155/155 PASS`
- retained V1/V2 active suites: `PASS`
- retained non-superseded V5 assertions: `PASS`
- frozen V6 assertions: `PASS`

All 11 V6 provenance failure classes changed from RED to GREEN without modifying the frozen V6 assertion file.

The single V5 test that positively accepted a raw caller-constructed dictionary remains preserved in V5 history but is explicitly superseded in V6 because it conflicts with provenance-sealing semantics.

## Bounded interpretation

V6 supports only this claim: within the current reference process and under the verified V6 module set, a plain caller-constructed/copy/serialized dictionary cannot satisfy `candidate_result_eligible`; positive eligibility is tied to a boundary-issued process-local seal and the exact sealed payload.

V6 does **not** support any claim that:

- provenance survives process restart;
- serialized results are authoritative across processes;
- the process-local token is a production cryptographic trust root;
- arbitrary malicious in-process introspection is defeated;
- live platform enforcement-point, registry, approval, provider, gateway, or configuration attestations exist;
- independent production trust-root separation exists;
- EXP-ECC-6/7 are ready; or
- any requirement is adopted.

## Current disposition

- V6 reference provenance: `BOUNDED_GREEN_PENDING_EXTERNAL_ENGINEERING_REREVIEW`
- EXP-ECC-1..5: `REFERENCE_MECHANISM_HARDENED_BUT_LIVE_INTEGRATION_EVIDENCE_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze: `NOT_FROZEN`
- manual-review threshold contribution from AI reviews: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
