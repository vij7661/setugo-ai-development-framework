# Evidence Verifier Qualification — Status

## Verified implementation baseline

- Implementation SHA: `e184c415f2cbc8fa8aa2fbe79a8204e0986509c5`
- Exact-head GitHub Actions run: `33985812402`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The exact-head run completed the Review Engine system regressions and all existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

Evidence-correspondence verification no longer relies on a free `verifier_id` or qualification label in GOVERNED application mode.

`EvidenceVerifierIdentity` binds verifier bookkeeping identity to:

- provider;
- model;
- SKU;
- deployment path;
- foundation lineage;
- qualification reference;
- qualification epoch.

`EvidenceVerifierQualificationRegistry` binds eligibility to the same identity plus:

- qualification status;
- maximum risk;
- allowed task types.

`QualifiedRetainedEvidenceCorrespondenceRegistry` requires a structured verifier identity before an attestation can enter its retained evidence set. It rejects missing qualifications, revoked/pending status, stale qualification epochs, and provider/model/SKU/deployment/lineage substitution.

Verifier qualification is re-evaluated at **assessment time** against the actual review risk and platform task type. A previously admitted attestation therefore stops producing `VERIFIED_SUPPORT` after verifier revocation, and a verifier whose qualification ceiling is below the current review risk cannot clear the claim.

`ReviewEngine` passes the effective platform review risk and trusted platform task type into Truth & Veracity evidence correspondence assessment at R1, R2, revised R1, blinded R3 and staged R3 adjudication.

`ReviewEngineApp` refuses a configured evidence-correspondence validator in GOVERNED mode unless it advertises qualified-verifier assessment enforcement. Raw `RetainedEvidenceCorrespondenceRegistry` remains available only as a reference/experimental component.

## Falsification coverage

The new verifier tests cover:

1. exact qualified verifier acceptance;
2. rejection of a plausible free verifier label without structured identity;
3. provider/model/SKU/deployment path/foundation lineage/epoch substitution;
4. pending/revoked verifier rejection at admission;
5. revocation after admission removing support at assessment time;
6. risk above verifier qualification ceiling becoming `UNVERIFIED`;
7. task type outside verifier qualification scope becoming `UNVERIFIED`;
8. GOVERNED application rejection of the raw correspondence registry;
9. GOVERNED application acceptance of the qualified registry;
10. end-to-end propagation of actual HIGH review risk into verifier qualification instead of silently using a LOW default.

## What this does not prove

This control strengthens qualification and scope binding; it does not prove semantic truth by itself.

It does **not** establish:

- cryptographic provider/model runtime identity;
- authenticity of the referenced evidence source;
- semantic entailment between arbitrary source text and the claim;
- durable persistence or external immutability of correspondence attestations;
- distributed consensus;
- WORM evidence storage.

The current qualified correspondence registry is still an in-memory reference store. Durable attestation persistence and authenticated source snapshots remain separate governance boundaries.
