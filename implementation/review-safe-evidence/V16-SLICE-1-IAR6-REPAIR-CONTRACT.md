# V16 Slice 1 — IAR6 Repair Contract

Status: **CONSTRUCTION REPAIR / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This contract binds the repair of `V16-SLICE-1-INTERNAL-ADVERSARIAL-REVIEW-006` before any Slice 2 work may begin.

## Exact validator-artifact identity

The declarative validation-profile digest remains necessary but is not treated as complete executable identity. Slice 1 now adds an exact validator-source bundle digest over the source bytes of:

- `review_safe_evidence_v16_trust.py`; and
- `review_safe_evidence_v16_artifact_binding.py`.

The bundle material also includes the current declarative validation-profile digest and the artifact-binding signature-domain constants. Any change to either bound source artifact therefore changes the local validator-bundle digest.

This is construction-level source-drift detection only. The validator measures its own local source files, so the result explicitly remains:

`artifact_measurement = LOCAL_SOURCE_BYTES_SELF_MEASURED`

`artifact_measurement_independently_proven = false`

No claim is made that the measured source bytes independently prove the loaded machine code, interpreter, import path, monkeypatch state, runtime image, or deployment identity.

## Bootstrap-authenticated validator binding

A `VALIDATOR_ARTIFACT_BINDING` certificate binds:

- candidate ID;
- current registry ID, sequence and exact registry digest;
- digest of the complete supplied registry-chain digest sequence;
- trust-set ID and digest;
- validation-profile digest; and
- exact local validator-bundle digest.

The certificate receives a content digest and must be authenticated by the configured bootstrap threshold across distinct root control domains. Bootstrap root signatures remain domain-separated by root/key/domain identity and trust-set digest.

A separately provisioned `PinnedArtifactBoundHead` binds the expected current registry head, validator-binding certificate digest, validator-bundle digest and full registry-chain digest. Its provisioning and freshness are not proven by this construction code.

## Issuer binding to exact validator identity

A current governance record that is treated as artifact-bound is carried inside an `ARTIFACT_BOUND_SIGNED_GOVERNANCE_RECORD`. The outer envelope binds:

- validator-binding certificate digest;
- validator-bundle digest;
- canonical digest of the complete inner signed governance record; and
- the complete inner record itself.

The operational issuer signs the outer envelope with the same registry-resolved current key used for the inner record. Therefore changing the bound validator identity or replacing the inner record requires a fresh issuer signature.

The base signed-record validator remains available as a lower-level construction primitive, but it is not by itself evidence of artifact-bound verification. Downstream V16 authority-bearing integrations must use the artifact-bound verifier once they depend on this repair.

## Historical registry semantics

Slice 1 does not implement historical dispatch across multiple verifier versions. Instead it fails closed on mixed validation-profile identities within one registry chain. The binding certificate additionally re-attests the digest of the complete registry-chain digest sequence under the current exact source bundle.

A future change to verifier/profile identity must therefore start a separately anchored registry epoch/genesis unless a later governed design introduces explicit cross-version transition certificates and historical verifier dispatch.

## Canonical construction workflow

The legacy 64-test workflow has been retired from active execution. Its historical runs remain preserved. The only active intended Slice 1 construction workflow is:

`.github/workflows/review-safe-evidence-v16-trust-foundation-v2.yml`

The governed mandatory set is the exact union of:

- 64 base tests;
- 13 IAR5 tests; and
- 12 IAR6 artifact-binding tests.

Total: **89 mandatory test IDs**.

CI must prove exact equality among all three manifests, all statically discovered test functions in the three test modules, and all raw unittest `... ok` execution IDs. Missing, skipped, renamed, duplicate or undeclared tests fail closed.

## Preserved residuals

- bootstrap trust-set real-world ownership/provisioning is not independently proven;
- pinned current-head and pinned artifact-head freshness/provisioning are not independently proven;
- local source self-measurement is not runtime attestation;
- interpreter/import/bytecode/native-library state is not independently attested;
- dependency artifacts/transitives and hosted-runner image are not fully hash-locked;
- control-domain ancestry/shared-root recomputation is still a later V16 slice;
- downstream V15 governance surfaces are not yet migrated;
- implementation, runtime, scientific and effect authority remain unclaimed.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
