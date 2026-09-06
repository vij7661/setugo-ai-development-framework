# EXP-O Pilot 26 — First Frozen Execution Configuration Failure

## Classification

`ENVIRONMENT / AWS IAM CONFIGURATION FAILURE — NO SCIENTIFIC ADJUDICATION`

This record preserves the first frozen Pilot 26 execution failure. It must not be rewritten as a mechanism failure or a successful scientific endpoint result.

## Frozen execution lineage

- Design SHA: `f14cd23ea2e5c8a2988ded2acda1c813d4f42dd8`
- Trigger SHA: `44c9bdd6f6820cc4b680463bc36cedf50e9bacea`
- GitHub Actions run: `34034090542`
- Workflow: `Governed Platform EXP-O Pilot 26 Multi-KMS Root Quorum`

## What succeeded

- Protected-design guard passed against the frozen design SHA.
- GitHub OIDC successfully assumed `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`.
- The runner began the preregistered three-root metadata phase.

## Failure evidence

The run stopped on `kms:DescribeKey` for registered root B:

`arn:aws:kms:ap-southeast-2:297165774800:key/aad32262-2396-485e-a6f2-0ae0cd10f52e`

AWS returned `AccessDeniedException` stating that the assumed role was not authorized because no identity-based policy allowed `kms:DescribeKey` on that resource.

Because the failure occurred during prerequisite metadata validation, before the 20-case scientific suite could produce its result artifact, no Pilot 26 endpoint set is adjudicated from this run.

The artifact upload also failed only because the runner terminated before creating the output directory; that is downstream of the IAM denial and is not an independent scientific failure.

## Required recovery

Extend the existing role's identity-based KMS permissions to roots B and C for exactly:

- `kms:DescribeKey`
- `kms:GetPublicKey`
- `kms:Sign`

Do not add KMS administration permissions. After the IAM change, rerun the same frozen Pilot 26 design without changing the runner, endpoints, roots, threshold, workflow, or scientific inputs.

## Scientific interpretation

Current status remains `INCONCLUSIVE / EXECUTION BLOCKED BY IAM CONFIGURATION`.

This run establishes only that OIDC role assumption worked and that the role policy had not yet been extended to root B. It does not test multi-root quorum safety or liveness.
