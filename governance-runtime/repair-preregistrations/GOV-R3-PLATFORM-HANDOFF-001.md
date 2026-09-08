# GOV-R3-PLATFORM-HANDOFF-001

## Classification
Production integration handoff schema defect discovered before R3 dispatch.

## Frozen subject
- Slice5 repaired candidate: `d9459af74533fbb60477dfcec00b30e82a0e2534`
- Authenticated R2 ReviewRequest: `REV-MVP-SLICE5-SCIENTIFIC-003`
- Authenticated R2 run: `34232976825`
- R2 disposition: `PASS`
- R2 authority effect: `R2_EVIDENCE_ONLY_R3_MANDATORY`

## Defect
Qualified `sequential_review_v1.py` normalizes an older manual-review schema and rejects material fields emitted by the authenticated platform reviewer, including `review_request_id`, `reviewed_artifact_commit`, `reviewer`, `evidence_assessment`, `independence_attestation`, and `review_coverage`.

Using v1 would therefore prevent a deterministic lossless R2→R3 handoff for the actual production review schema. Silent field dropping is forbidden.

## Repair contract
Create a narrow v2 sequential handoff mechanism that:
1. accepts the authenticated platform-review schema without removing material fields;
2. requires exact ReviewRequest ID and reviewed candidate binding;
3. preserves the full raw R2 object losslessly;
4. hashes the full R2 object and the full frozen handoff;
5. carries reviewer provider/model and authenticated-review provenance as data, not authority;
6. requires R3 for `PERSISTENCE`, `IRREVERSIBLE_STATE`, `PROMOTION_AUTHORITY`, or any promotion-authoritative transition regardless of R2 PASS/FAIL;
7. forbids R1-middle opinion, recommendation, override, or mutation of R2 content;
8. fails closed on missing mandatory production R2 fields or candidate/request mismatch;
9. keeps the R2 semantic verdict non-authoritative until R3 and final deterministic adjudication complete.

## Required deterministic tests
- V2-01 accepts exact platform R2 schema losslessly.
- V2-02 candidate mismatch fails closed.
- V2-03 ReviewRequest ID mismatch fails closed.
- V2-04 missing review coverage fails closed.
- V2-05 missing reviewer identity fails closed.
- V2-06 R1-middle opinion fields fail closed.
- V2-07 raw R2 hash changes for any material R2 mutation.
- V2-08 high-risk PASS still requires R3.
- V2-09 high-risk FAIL still requires R3.
- V2-10 frozen handoff verification detects any mutation.

## Scientific posture
This repair does not change the Slice5 scientific candidate or R2 result. It repairs only the production R2→R3 handoff mechanism. R3 must not be dispatched until the deterministic repair passes.
