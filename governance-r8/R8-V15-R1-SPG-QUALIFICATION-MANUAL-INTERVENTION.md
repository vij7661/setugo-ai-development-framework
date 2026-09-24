# R8 v15-r1 — SPG-1 Qualification Manual Intervention

Status: **MANUAL_INTERVENTION_REQUIRED — NON_AUTHORITATIVE**
Authority effect: **NONE**

Current executable-schema candidate:
- branch: `freeze/r8-v15-r1-executable-schema-v2`
- frozen semantic candidate: `c721b38cf8b00294797300b526596ce723a47ff8`

## Why execution stops here

The V2 schema candidate has restored the inherited executable-schema-freeze obligations, but final freeze remains blocked by:

- `SFV-36` — qualified SchemaProvenanceGenerator runtime/workload attestation;
- `SFV-45` — fresh independent review of the exact qualified schema candidate.

The current binding is intentionally unqualified:

`schemas/governance-r8/v15-r1/schema-provenance-generator-binding.json`

Current load-bearing values include:
- `qualification_status = UNATTESTED_RUNTIME`;
- `revocation_state = UNKNOWN`;
- `runtime_manifest.runtime_manifest_digest = null`;
- `workload_attestation_policy_digest = null`;
- `workload_attestation_proof_digest = null`;
- `signing_credential_id = null`.

These values MUST NOT be replaced with invented/local/model-generated values merely to satisfy the schema.

## Manual prerequisite

A real approved workload-attestation path must identify the exact execution environment used to run:

`tools/generate_r8_v15_r1_spm.py`

and must provide independently verifiable evidence for the binding fields required by SFG-003 / SFV-36.

At minimum the qualified execution must establish:

1. exact generator artifact bytes/digest;
2. interpreter/compiler/runtime identity;
3. crypto-library identity where applicable;
4. schema/parser bundle identity where applicable;
5. OS/container image identity where applicable;
6. runtime-manifest digest;
7. workload-attestation policy digest;
8. workload-attestation proof digest;
9. signing credential identity;
10. ACTIVE/non-revoked generator state.

## Forbidden shortcuts

Do NOT:
- change `qualification_status` to `QUALIFIED` by hand;
- use a Git commit, CI green check, model statement, local shell output, or ordinary SHA-256 alone as workload attestation;
- substitute `UNATTESTED_RUNTIME` with an assumed trusted developer machine;
- leave required qualification fields null while claiming final freeze;
- send V1 for review;
- send V2 for final qualifying review before the exact qualified generator output is fixed.

Any such shortcut is a false-green and must leave `EXECUTABLE_SCHEMA_FROZEN` blocked.

## Safe local pre-checks

These checks may be run locally but grant **no qualification**.

### Generator artifact identity

PowerShell:

```powershell
git switch freeze/r8-v15-r1-executable-schema-v2
git status --short
Get-FileHash .\tools\generate_r8_v15_r1_spm.py -Algorithm SHA256
```

Expected candidate generator artifact SHA-256:

`388fb8a61f31cbf99b001a2313d554c8a4aac36e61188eb95230b93c6b0077e6`

A mismatch means stop: the candidate generator bytes have drifted.

### Candidate-only deterministic regeneration

This is allowed only as a non-authoritative consistency check while the binding remains unqualified:

```powershell
python .\tools\generate_r8_v15_r1_spm.py `
  --schema-root .\schemas\governance-r8\v15-r1 `
  --source-map .\schemas\governance-r8\v15-r1\schema-provenance-source-map.json `
  --generator-binding .\schemas\governance-r8\v15-r1\schema-provenance-generator-binding.json `
  --output .\schemas\governance-r8\v15-r1\schema-provenance-manifest-recomputed.json
```

The output must remain candidate/non-authoritative while `qualification_status != QUALIFIED`.

## What must come back from the qualified environment

Provide the exact evidence/artifacts for:

- generator artifact SHA-256;
- complete RuntimeManifest field values;
- RuntimeManifest digest and its exact canonical/digest basis;
- workload-attestation policy identifier/digest;
- workload-attestation proof identifier/digest and independently verifiable proof artifact/reference;
- signing credential identifier;
- revocation/lifecycle state evidence;
- exact generated SPM-1 output bytes/digest;
- execution timestamp/sequence only if the approved attestation policy itself requires it.

Do not provide secrets/private keys. Only public identifiers, digests and verification evidence are required.

## Resume rule

After real qualification evidence exists:

1. update the SPG binding only from that evidence;
2. require `status = QUALIFIED_GENERATOR_BINDING`;
3. require `qualification_status = QUALIFIED`;
4. require `revocation_state = ACTIVE`;
5. rerun the exact generator in that qualified environment;
6. compare generated schema/SPM outputs to the current V2 candidate;
7. if any schema semantic bytes change, invalidate the candidate and reconcile before review;
8. recompute SFV-35..SFV-44 and the full schema-freeze validator contract;
9. freeze the exact qualified candidate;
10. create a fresh blind independent schema-review packet;
11. only an acceptable review of that exact candidate may close SFV-45.

## Current gate state

- semantic design: `BOUNDED_PASS`
- evidence closure: `EVIDENCE_CLOSURE_PASS`
- executable schema V1: `SUPERSEDED_BEFORE_EXTERNAL_REVIEW`
- executable schema V2 candidate construction: `CANDIDATE_COMPLETE`
- SPM-1 candidate: `CANDIDATE_COMPLETE / NON_AUTHORITATIVE`
- GCP-RVM-2: `CANDIDATE_COMPLETE`
- RPS-1: `CANDIDATE_COMPLETE`
- CaseProofContracts G001..G156: `CANDIDATE_COMPLETE`
- SPG qualification / SFV-36: **BLOCKED — MANUAL INTERVENTION REQUIRED**
- independent exact-candidate schema review / SFV-45: **BLOCKED behind SFV-36**
- executable-schema final freeze: **BLOCKED**
- implementation authority: **NONE**
