# EXP-O Pilot 24 — AWS KMS Asymmetric Checkpoint Adjudication

## Verdict

`NO_TESTED_OIDC_KMS_ASYMMETRIC_SIGNATURE_FORGERY_SUBSTITUTION_REPLAY_OR_STALE_GENERATION_PATH_CREATED_EFFECTIVE_AUTHORITY_ON_THE_BOUNDED_AWS_KMS_PATH`

## Frozen lineage

- Initial preregistration/design lineage culminated in pre-execution design SHA `0d11f19afd9d5c64b2937e6d301804f0588e77d6`.
- Exact AWS role: `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`.
- Exact KMS key: `arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`.
- Region: `ap-southeast-2`.
- Key spec: `ECC_NIST_P256`; usage `SIGN_VERIFY`; algorithm `ECDSA_SHA_256`.
- No static AWS credentials were referenced by the workflow. GitHub Actions used OIDC to obtain temporary role credentials.

## Failure history retained

### OIDC trust-policy mismatch

The first workflow attempt of run `34031562729` failed before any KMS call because AWS IAM trusted the legacy name-based GitHub OIDC subject while GitHub emitted the immutable repository-ID subject. The exact emitted subject was diagnosed non-secretly and the AWS trust policy was manually corrected. This was an external configuration failure, not Pilot 24 runtime evidence.

### P24-05 assertion defect

The same workflow run was then rerun after the IAM correction. OIDC succeeded and the KMS suite executed. It produced 16/17 runtime passes plus 3/3 configuration-bound passes. Only P24-05 failed.

The failure was classified and recorded before repair in `EXP-O-PILOT24-FIRST-RUNTIME-FAILURE-FINDING.md`. The runner incorrectly compared `Sign.KeyId` (returned as the full key ARN) with `DescribeKey.KeyMetadata.KeyId` (returned as the UUID). P24-06 independently verified the exact P24-05 KMS signature successfully, proving the failure was an identifier-form assertion defect rather than a signing failure.

The permitted repair changed only P24-05 to bind `Sign.KeyId` directly to the frozen full KMS key ARN. Repair SHA: `1a66533278dfb8db0f4989dfb96f749e219e28fe`.

Pilot 24 therefore must **not** be described as first-run 20/20.

## Final repaired execution evidence

- Trigger rebind commit: `7ad0c5148f67458489de831905e756e6bfe61336`.
- Workflow run: `34032843924`.
- Protected design verified at repair SHA `1a66533278dfb8db0f4989dfb96f749e219e28fe` before OIDC/KMS execution.
- OIDC assumption succeeded as `arn:aws:sts::297165774800:assumed-role/setugo-pilot24-kms-signer/setugo-exp-o-pilot24`.
- Runtime cases: **17/17 PASS**.
- Configuration-bound non-destructive cases: **3/3 PASS**.
- Total frozen endpoints: **20/20 satisfied after the recorded repair**.
- `private_key_material_observed=false`.
- `static_aws_credentials_referenced_by_workflow=false`.
- `model_authority_effect=false`.
- `authoritative_platform_effect_count=0`.

Observed runtime properties included:

1. exact OIDC assumed-role identity;
2. exact KMS key metadata and public-key export;
3. successful KMS ECDSA signing bound to the exact key ARN and algorithm;
4. independent local OpenSSL verification using only the exported public key;
5. changed-message rejection;
6. mutated-signature rejection;
7. locally generated private-key forgery rejection;
8. credentialless verifier success;
9. wrong-signing-algorithm rejection by KMS;
10. different-key substitution rejection;
11. cryptographically valid but semantically stale generation rejection;
12. scope substitution rejection;
13. replay remains bound to the exact original statement;
14. two credentialless verifier processes agree;
15. clean higher-generation liveness.

P24-13/14/15 were deliberately changed before runtime execution by the safety amendment into `CONFIGURATION_BOUND_NOT_RUNTIME_PROBED` checks. Destructive KMS admin actions such as disable, schedule deletion, or create-key were not invoked merely to test denial.

## Scientific interpretation

This pilot establishes bounded evidence that, on the tested GitHub Actions OIDC → AWS STS temporary role → AWS KMS asymmetric signing path, the verifier can validate KMS signatures using public material without access to the private key, and the tested forgery/substitution/replay/stale-generation attacks did not create effective authority or consequential platform effects.

It does **not** prove universal KMS security, AWS control-plane correctness, physical HSM properties, compromise resistance of the AWS account/root administrators, correctness under arbitrary key-policy changes, revocation/rotation safety, cross-region behavior, or full production witness integration.

## Next boundary

The next distinct experiment should integrate the externally KMS-signed checkpoint into the durable witness/recovery path itself, so a real witness process must validate the asymmetric checkpoint plus its local monotonic history before it can contribute to quorum. That integration remains separate from Pilot 24's cryptographic-path evidence.
