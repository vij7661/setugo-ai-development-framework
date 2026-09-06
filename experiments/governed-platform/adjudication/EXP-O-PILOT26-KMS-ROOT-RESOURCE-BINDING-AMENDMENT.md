# EXP-O Pilot 26 — External KMS Root Resource-Binding Amendment

## Status

PRE-EXECUTION RESOURCE BINDING. This amendment resolves the provisioning dependency recorded in the Pilot 26 preregistration. It does not change the twenty scientific endpoints, quorum threshold, canonical statement, safety constraints, or bounded interpretation.

## Frozen external resources

AWS account / administrative domain: `297165774800`

Region: `ap-southeast-2`

GitHub OIDC role: `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`

Registered external asymmetric roots, frozen by exact full ARN:

- Root A: `arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`
- Root B: `arn:aws:kms:ap-southeast-2:297165774800:key/aad32262-2396-485e-a6f2-0ae0cd10f52e`
- Root C: `arn:aws:kms:ap-southeast-2:297165774800:key/992638b8-7086-41a6-a3dc-849a998c4f86`

All three must report:

- `KeySpec = ECC_NIST_P256`
- `KeyUsage = SIGN_VERIFY`
- `SigningAlgorithms` containing `ECDSA_SHA_256`

The execution workflow may use only `kms:DescribeKey`, `kms:GetPublicKey`, and `kms:Sign` for these roots through temporary GitHub OIDC credentials. No static AWS access keys and no KMS administration calls are permitted.

## Frozen root-distinctness rule

Root identity is the exact registered full KMS key ARN. Alias text, labels, array position, duplicate signatures, or repeated use of one ARN cannot create a second root.

Quorum is exactly 2-of-3 distinct registered root ARNs over byte-identical canonical checkpoint statements. Signature validity is necessary but not sufficient: mixed statement hashes, mixed generations/scopes, or generations below the trusted minimum cannot combine.

## Administrative-independence limitation

These are three distinct cryptographic KMS key identities in the same AWS account and IAM/KMS administrative trust domain. Pilot 26 must not be described as proving multi-account, multi-provider, multi-cloud, or administratively independent root tolerance.
