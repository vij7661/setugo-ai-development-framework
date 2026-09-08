# GOV-R3-ROLE-ATTESTATION-001

## Classification
Production review prompt-role defect discovered before Slice5 R3 dispatch.

## Defect
`platform_candidate_review.py::build_prompt()` hard-codes every review as an independent blind review and hard-codes the example independence attestation `BLIND_TO_PROPOSER_CONCLUSION`.

That is correct for blind R2 requests but false for sequential R3, which is intentionally exposed to the frozen R2 result. Dispatching R3 through the existing prompt would invite a false independence claim.

## Frozen subject
- Slice5 candidate: `d9459af74533fbb60477dfcec00b30e82a0e2534`
- Frozen authenticated R2 handoff: `sha256:5aebbdd249042a4ab8013a2f9235d5965808fe976e84e2e52d2cad9f339d1b0f`
- R3 is mandatory and must be review-of-review, not independent R2.

## Repair contract
1. `blind_review_required=true` preserves current R2 prompt semantics and requires output example attestation `BLIND_TO_PROPOSER_CONCLUSION`.
2. `blind_review_required=false` produces an explicit R3/review-of-review prompt that states prior reviewer content is intentionally visible and must be challenged rather than deferred to.
3. Exposed review output example attestation must be `REVIEW_OF_REVIEW_EXPOSED_TO_PRIOR_REVIEW`.
4. The validator must enforce the attestation that corresponds to the request's blind/exposed mode, preventing a false independence claim from becoming schema-valid review evidence.
5. Candidate/request/provider/model/evidence/coverage validation remains unchanged.
6. No provider API call is needed to qualify this deterministic prompt/validator repair.

## Required tests
- RA-01 blind request prompt retains independent reviewer role and blind attestation.
- RA-02 exposed request prompt states review-of-review role and exposed attestation.
- RA-03 blind review with exposed attestation is invalid.
- RA-04 exposed review with blind attestation is invalid.
- RA-05 exposed review with correct attestation remains valid when all other fields/coverage are valid.
- RA-06 existing R2 PASS validation behavior remains unchanged.

## Authority
No R3 dispatch and no Slice5 promotion authority until this repair passes deterministically.
