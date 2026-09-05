# Durable Evidence Correspondence — Status

## Verified implementation baseline

- Implementation SHA: `a250cff5dfe897b7c0cfd61cbdc0b11948925143`
- Exact-head GitHub Actions run: `33986007485`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The exact-head run passed the Review Engine system suite and the existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

`SQLiteQualifiedEvidenceCorrespondenceRegistry` provides single-node durable persistence for evidence-correspondence attestations that already satisfy structured verifier identity and qualification requirements.

Each retained attestation persists:

- attestation ID;
- exact artifact hash;
- exact claim fingerprint;
- evidence reference;
- evidence-content hash;
- correspondence verdict;
- verifier ID;
- provenance;
- qualification reference;
- verifier provider/model/SKU/deployment path/foundation lineage/qualification epoch.

The registry uses SQLite WAL plus a busy timeout and transactional admission. It rejects conflicting rewrites of an existing attestation ID or of the same artifact/claim/evidence/verifier binding.

At assessment time it re-evaluates the retained structured verifier identity against the current qualification registry using the actual platform review risk and task type. Persisted support therefore becomes `UNVERIFIED` after verifier revocation or when the current review exceeds the verifier's qualification scope.

`ReviewEngineApp` now requires a configured evidence-correspondence validator in GOVERNED mode to enforce both:

1. qualified verifier assessment; and
2. durable attestation state.

The raw and in-memory qualified registries remain reference/experimental components and cannot be used to claim the stronger governed correspondence configuration.

## Falsification coverage

The durable correspondence tests verify:

1. an attestation survives a new registry/process instance;
2. exact support remains usable after restart while qualification remains valid;
3. conflicting rewrite of a persisted attestation ID is rejected;
4. verifier revocation after restart removes previously persisted support at assessment time;
5. concurrent conflicting admissions cannot both win;
6. GOVERNED app rejects raw correspondence storage;
7. GOVERNED app rejects qualified-but-in-memory correspondence storage;
8. GOVERNED app accepts the SQLite qualified store;
9. actual HIGH review risk continues to prevent a LOW-only verifier from producing `VERIFIED_SUPPORT` in the application path.

## What this does not prove

This milestone is deliberately limited to single-node durable verifier-qualified correspondence state. It does not establish:

- authenticity of the evidence source represented by `evidence_ref`;
- proof that `evidence_content_hash` was computed from an authenticated source snapshot;
- semantic entailment between the evidence snapshot and the claim;
- cryptographic provider/model runtime identity;
- external/WORM immutability;
- protection from privileged SQLite rewrite;
- distributed consensus or multi-node linearizability.

The next source-ingestion boundary must authenticate the evidence snapshot before an attestation can rely on its content hash. A model, verifier or caller naming an evidence reference is still not authority.
