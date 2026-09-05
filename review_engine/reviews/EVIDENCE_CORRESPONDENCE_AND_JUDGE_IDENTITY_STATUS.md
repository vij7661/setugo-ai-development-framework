# Evidence Correspondence + Judge Identity Falsification Status

Implementation line reviewed here: `feature/review-engine-mvp` after the Truth & Veracity Contract / Judge Health additions.

This record is platform-side evidence. Green tests are verification evidence, not production/release authority.

## Evidence Correspondence Validator

Implemented controls:

- reviewer `SUPPORTED` is not sufficient for a material empirical claim;
- retained correspondence attestations bind exact artifact hash + normalized claim fingerprint + evidence ref + evidence-content hash + verifier identity/provenance;
- fake handles, stale artifacts and rephrased claims do not reuse an attestation;
- conflicting retained attestations surface `CONFLICT`;
- material claims without `VERIFIED_SUPPORT` become `TVC-EVIDENCE-CORRESPONDENCE` findings;
- correspondence attestations are constructor-injected at the trusted application boundary and are not writable through public review JSON;
- evidence-correspondence assessments are retained in reviewer-stage session evidence;
- a material R1 truth/veracity finding is not erased merely because R2 omits it.

Falsification coverage includes:

1. fake evidence handle;
2. stale artifact reuse;
3. rephrased claim reuse;
4. conflicting support/contradiction attestations;
5. conflicting rewrite of one attestation ID;
6. R2 clean response attempting to erase an R1 material truth finding;
7. successful correction followed by blinded R3 verification.

Declared remaining boundary:

The registry does not itself solve semantic entailment from source text. Admission of `SUPPORTS` / `CONTRADICTS` attestations still depends on a trusted evidence-verification integration with authenticated source snapshots and qualified verifier identity. Claim extraction/classification completeness is also not a deterministic language oracle.

## Judge Health Identity Binding

Implemented controls:

- judge-health observations require a platform-bound identity by default;
- `judge_id` is derived from provider + model + SKU + deployment path + role + foundation lineage + qualification ref + qualification epoch;
- free-form/self-reported judge IDs are rejected by the governed default monitor;
- a forged ID that disagrees with its binding is rejected;
- aliases pointing to the same provider/model/SKU/deployment path are not counted as two judges;
- same-foundation-lineage pairs remain mathematically analyzable but receive an explicit correlation warning;
- `NO_LOGICAL_ALARM` still never establishes correctness/alignment.

Falsification coverage includes:

1. arbitrary unbound model name;
2. forged judge ID against a retained binding;
3. conflicting retained observation for the same task/judge;
4. same runtime path disguised by different qualification records/roles;
5. same foundation lineage correlation warning;
6. unanimous bound judges jointly wrong with no ground-truth alarm.

Declared remaining boundary:

The binding is platform bookkeeping identity. It is not universal cryptographic proof that the remote provider actually executed the configured model/SKU/deployment path. Runtime provider attestation remains an integration boundary.

## Verification evidence

Implementation/documentation head immediately before this status record: `eab1994a8af0226a3a953f0e277522fd3bb10f9a`.

GitHub Actions run `33983544190` completed `success` at that exact head. Review Engine system regressions plus scorer, runner, protected-truth, observability, continuation-authority and governor falsification steps all succeeded.

## Next attack surface

The next useful product-level falsification target is **claim coverage / truth-bearer omission**: a model may omit or misclassify a material empirical assertion from its own `epistemic_review`. The safe next design should use independently retained claim-coverage evidence or an independently qualified extractor/challenger; it should not pretend that a simple deterministic keyword classifier can solve semantic claim extraction.
