# EXP-O Pilot 24 — AWS KMS Asymmetric Checkpoint Authority

Status: **PRE-REGISTERED / NO PILOT 24 EXECUTION YET**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Motivation

Pilots 19–23 progressively moved integrity and checkpoint authority outside mutable local state. Pilot 23 isolated the checkpoint-minting HMAC key in a separate process, but symmetric verification still means any component that receives the HMAC verification key could also mint valid checkpoints. Pilot 24 moves the signing authority to an external asymmetric trust root so verification can occur with public material only.

The claim under test is deliberately narrow:

> A GitHub Actions workload authenticated through OIDC can request signatures from one exact AWS KMS asymmetric signing key without receiving private-key material, while independent verifier processes holding only the public key can validate exact checkpoint statements but cannot mint valid signatures or widen the AWS authority granted to the workflow.

This is not a production KMS/HSM certification, not a proof of AWS KMS internals, and not a general cloud-IAM proof.

## Frozen external execution path

- GitHub repository: `vij7661/setugo-ai-development-framework`
- GitHub branch: `experiment/governed-platform-falsification-harness`
- Authentication: GitHub Actions OIDC -> AWS STS `AssumeRoleWithWebIdentity`
- AWS role ARN: `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`
- AWS region: `ap-southeast-2`
- AWS KMS key ARN: `arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`
- Expected key type: asymmetric `SIGN_VERIFY`
- Expected key spec: `ECC_NIST_P256`
- Expected signing algorithm: `ECDSA_SHA_256`
- Workflow static AWS access keys: **forbidden**
- Private-key export/materialization: **forbidden and not part of the AWS KMS API path**

The IAM role is expected to have only these KMS data-plane permissions on the exact key:

- `kms:Sign`
- `kms:GetPublicKey`
- `kms:DescribeKey`

No KMS administration permission is required for the experiment.

## Authority model

AWS KMS signing authority is an external capability. A successful signature proves only that the configured AWS path signed the supplied bytes under the configured key. It does not grant release, merge, deployment, mutation, reviewer, or model authority.

The model layer is not involved in Pilot 24.

The checkpoint statement remains application-bound and must include at minimum:

- experiment/pilot identity;
- project/task/logical-state identity;
- generation;
- checkpoint/root digest;
- nonce/purpose.

A cryptographically valid signature on an old or wrong statement remains semantically ineligible if it violates current trusted minimum generation or exact binding.

## Frozen scientific cases

All cases are retained. A failed safety case is not replaced by another case.

1. **P24-01 — OIDC role acquisition.** The workflow obtains temporary AWS credentials through GitHub OIDC for the exact configured role; no static AWS access-key secret is supplied by the workflow.
2. **P24-02 — Exact caller identity.** `sts:GetCallerIdentity` resolves to an assumed-role session for `setugo-pilot24-kms-signer`.
3. **P24-03 — Exact KMS metadata.** `DescribeKey` reports the exact configured key ARN, asymmetric signing usage, and `ECC_NIST_P256` key spec.
4. **P24-04 — Public key export only.** `GetPublicKey` succeeds and returns public SubjectPublicKeyInfo material usable by an independent verifier.
5. **P24-05 — Exact checkpoint signing.** KMS signs one canonical Pilot 24 checkpoint statement using `ECDSA_SHA_256`.
6. **P24-06 — Independent local verification.** A verifier using only exported public key material verifies the exact KMS signature over the exact statement.
7. **P24-07 — Message substitution.** The same valid signature fails verification after statement bytes are changed.
8. **P24-08 — Signature mutation.** Byte-mutated signature fails verification against the original statement.
9. **P24-09 — Local private-key forgery.** A signature produced by an unrelated locally generated EC private key fails against the KMS public key.
10. **P24-10 — Credentialless verifier.** Verification still succeeds in a subprocess with AWS credential environment removed, demonstrating that verification does not require signing authority.
11. **P24-11 — Wrong signing algorithm.** A signing request using an algorithm incompatible with the frozen KMS key is rejected and produces no eligible Pilot 24 signature.
12. **P24-12 — Different key substitution.** The role cannot turn a different/unregistered KMS key identifier into eligible evidence; wrong/unregistered key responses are rejected or unavailable and never accepted by the Pilot 24 verifier.
13. **P24-13 — Key disable attempt denied.** The signing role cannot disable the configured KMS key.
14. **P24-14 — Key deletion scheduling denied.** The signing role cannot schedule deletion of the configured KMS key.
15. **P24-15 — Key creation denied.** The signing role cannot create a replacement KMS key.
16. **P24-16 — Old valid signed generation remains semantically stale.** A cryptographically valid older-generation checkpoint is rejected when trusted minimum generation has advanced.
17. **P24-17 — Scope substitution remains semantically invalid.** A valid signature cannot be rebound to a different project/task/logical-state checkpoint statement.
18. **P24-18 — Signature replay cannot change statement identity.** Reusing the same signature bytes is acceptable only for the exact original canonical statement and cannot authorize a different candidate/root/generation.
19. **P24-19 — Two credentialless verifier processes agree.** Two independently launched verifier subprocesses using only the public key both validate the same exact KMS-signed checkpoint without AWS credentials.
20. **P24-20 — Clean higher-generation liveness.** A fresh higher-generation canonical checkpoint is signed by KMS and independently verified successfully while all authority remains external and no consequential platform effect is implied.

## Required evidence

The frozen execution artifact must retain:

- workflow run/commit identity;
- OIDC/assumed-role caller ARN (account identifier may be retained in internal artifact but should not be unnecessarily repeated in user-facing summaries);
- KMS key ARN and `KeyId` returned by AWS;
- key spec, key usage, signing algorithms;
- exported public-key digest (not private material);
- canonical statement bytes or digest per signing case;
- signature digest and verification outcome;
- AWS CLI exit status/error class for denied administrative or invalid requests;
- explicit proof that static AWS credential secrets are not referenced by the Pilot 24 workflow;
- exact outcomes for P24-01 through P24-20.

Raw temporary AWS credentials, OIDC tokens, or private key material must never be uploaded as artifacts.

## Execution guard

Provider/KMS calls are forbidden until:

1. this preregistration exists in Git;
2. the Pilot 24 runner/workflow and integrity tests are committed;
3. the full deterministic harness is green;
4. a final pre-execution design SHA is frozen;
5. a trigger file binds the execution to that exact design SHA.

The trigger may be added after the design SHA and is excluded from protected-design drift only if the workflow explicitly enforces that rule.

## Adjudication rules

- Workflow `success` is operational evidence only.
- Each P24 case must be inspected from retained artifact/log evidence.
- Any AWS access denial that prevents the experiment from reaching its intended path is operational/infrastructure evidence, not a scientific pass.
- Safety failures remain failures even if another sample/path is clean.
- A valid signature is provenance/cryptographic evidence only; it does not create broader platform authority.
- No universal claim about AWS, KMS, GitHub OIDC, HSMs, or cloud security may be made from this pilot.

## Explicit limitations

Even a full pass will not establish:

- AWS KMS or HSM implementation correctness beyond the observed API behavior;
- protection against AWS account-root compromise;
- protection against compromise of two cloud control planes simultaneously;
- general IAM-policy correctness outside the tested role/key path;
- production network/TLS implementation correctness beyond managed-service behavior;
- distributed witness consensus;
- formal non-extractability of the private key (the experiment can only show no private material is exposed through the tested APIs/workflow);
- production release/deployment authorization.
