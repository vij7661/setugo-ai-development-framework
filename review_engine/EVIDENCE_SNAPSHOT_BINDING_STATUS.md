# Retained Evidence Snapshot Binding — Status

## Verified implementation baseline

- Implementation SHA: `eda41e81092466357638fc2c0e763515565dec0f`
- Exact-head GitHub Actions run: `33986278868`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The exact-head run passed Review Engine system regressions and all existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

A qualified evidence verifier can no longer make a correspondence attestation usable in GOVERNED mode merely by naming an `evidence_ref` and inventing a plausible `evidence_content_hash`.

`SQLiteEvidenceSnapshotRegistry` retains a single-node durable evidence snapshot manifest containing:

- snapshot ID;
- evidence reference;
- exact evidence-content SHA-256;
- source locator metadata;
- acquisition provenance metadata.

`SQLiteQualifiedEvidenceCorrespondenceRegistry` can be configured with the snapshot registry. When configured, attestation admission requires an exact retained `evidence_ref + evidence_content_hash` match. The same binding is rechecked at assessment time.

`ReviewEngineApp` now requires a configured GOVERNED evidence-correspondence path to enforce all of:

1. qualified verifier assessment;
2. durable correspondence-attestation state;
3. retained evidence-snapshot binding;
4. durable retained snapshot state.

The app exposes these controls independently in health/review output rather than collapsing them into one vague evidence-valid flag.

## Falsification coverage

The snapshot-binding regressions verify:

1. snapshot manifests survive registry/process restart;
2. an attestation whose evidence hash does not match a retained snapshot is rejected;
3. an evidence reference without any retained snapshot cannot be used to admit the attestation;
4. conflicting rewrite of an existing snapshot ID is rejected;
5. GOVERNED application rejects durable correspondence storage that has no retained snapshot binding;
6. GOVERNED application accepts the durable qualified correspondence path only when a durable snapshot registry is configured;
7. the prior HIGH-risk verifier-scope regression remains effective through the snapshot-bound application path.

## What this proves

This control establishes that the evidence hash used by a governed correspondence attestation must already exist in the platform's retained snapshot manifest for the same evidence reference.

It closes the specific false-green path where the verifier itself invents the content hash at attestation time.

## What this does not prove

A retained snapshot hash is **not** proof that the external source was authentic, complete, current or truthful.

`source_locator` and `acquisition_provenance` are metadata, not cryptographic source proof. This milestone does not establish:

- authenticated acquisition from an external source;
- cryptographic source identity;
- signed source revisions, trusted ETags or equivalent provider attestations;
- semantic entailment between the snapshot and the claim;
- cryptographic model/provider runtime identity;
- WORM/external immutability;
- protection from privileged SQLite rewrite;
- distributed consensus or multi-node linearizability.

External-source authentication must be implemented source-by-source at the ingestion boundary. Until then, the precise claim is **retained snapshot binding**, not source authenticity.
