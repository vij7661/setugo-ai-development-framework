# EXP-O Pilot 26 — Multi-KMS External Root Quorum / Single-Root Compromise Preregistration

## Status

PRE-EXECUTION AND EXTERNALLY BLOCKED.

Pilot 26 must not execute until three distinct external asymmetric signing keys are provisioned. One key already exists from Pilots 24–25; two additional keys are required. No locally generated private key may substitute for a missing external root.

## Purpose

Pilots 24–25 established a bounded real AWS KMS asymmetric signing path and credentialless witness integration for one external checkpoint root. Pilot 26 tests the next distinct boundary: whether a 2-of-3 quorum over **three distinct external asymmetric KMS key identities** resists one compromised/conflicting root, duplicate/aliased use of one root, mixed-statement signatures, stale generations, and one-root unavailability.

This experiment tests separate cryptographic roots. If all three keys remain in the same AWS account and IAM administrative trust domain, they must **not** be described as administratively independent trust domains.

## External resources required

All three keys must be:

- AWS KMS customer-managed asymmetric keys;
- key spec `ECC_NIST_P256`;
- key usage `SIGN_VERIFY`;
- signing algorithm `ECDSA_SHA_256`;
- in the frozen AWS region unless a later pre-execution amendment explicitly preregisters a cross-region design;
- referenced by exact full KMS key ARN;
- usable only through temporary GitHub OIDC role credentials; no static AWS access keys.

Existing root A:

`arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`

Roots B and C: **UNPROVISIONED / MANUAL INTERVENTION REQUIRED**.

The existing role `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer` may be extended only with `kms:Sign`, `kms:GetPublicKey`, and `kms:DescribeKey` on roots B and C. No KMS administration permissions are required for the experiment workflow.

## Frozen quorum rule

A checkpoint is external-root eligible only when at least **2 distinct registered KMS key ARNs** produce valid signatures over the **exact same canonical checkpoint statement bytes**.

Rules:

1. distinctness is by the registered full KMS key ARN, not alias, label, array position, or signature count;
2. the same key cannot count more than once;
3. signatures over different statement hashes cannot combine;
4. a valid signature below the trusted minimum generation is semantically ineligible;
5. checkpoint quorum remains evidence only and creates no model, release, merge, deploy, or execution authority by itself.

## Frozen canonical statement

The signed statement binds at minimum:

- experiment `EXP-O`;
- pilot `PILOT26-MULTI-KMS-ROOT-QUORUM`;
- project `setugo`;
- task `exp-o-pilot26`;
- generation;
- checkpoint/root digest;
- purpose `multi-root-checkpoint-integrity`;
- nonce.

## Frozen endpoints

1. **P26-01** — exact OIDC assumed-role identity and exact metadata for all three registered KMS keys.
2. **P26-02** — public keys for A/B/C export successfully; three registered key ARNs and public-key fingerprints are distinct.
3. **P26-03** — clean A+B signatures over one exact current statement satisfy 2-of-3 quorum.
4. **P26-04** — clean B+C signatures over one exact current statement satisfy 2-of-3 quorum.
5. **P26-05** — one valid root alone is insufficient.
6. **P26-06** — duplicate copies of one root's signature cannot count as two roots.
7. **P26-07** — one valid root plus a locally forged signature pretending to be a second root is insufficient.
8. **P26-08** — valid A and B signatures over different checkpoint statement hashes do not form quorum.
9. **P26-09** — valid A and B signatures over different generations do not form quorum.
10. **P26-10** — valid A and B signatures over different project/task scope do not form quorum.
11. **P26-11** — one deliberately conflicting externally signed root plus two honest roots agreeing on the current statement resolves only to the exact two-root agreeing statement; the conflicting root cannot redirect quorum.
12. **P26-12** — three valid signatures with no statement receiving two distinct-root signatures form no quorum.
13. **P26-13** — a valid old 2-of-3 quorum below trusted minimum generation is semantically ineligible.
14. **P26-14** — stale old signature from one root cannot combine with a current signature from another root when statement identity/generation differ.
15. **P26-15** — alias/identifier duplication of the same underlying registered key ARN cannot manufacture root distinctness.
16. **P26-16** — public-key/key-ARN substitution causes that signature contribution to be rejected rather than reassigned to another root.
17. **P26-17** — one root unavailable while the other two sign the exact same current statement retains liveness.
18. **P26-18** — signature reordering does not change quorum identity or result.
19. **P26-19** — all tested multi-root evidence paths retain `model_authority_effect=false` and `authoritative_platform_effect_count=0`.
20. **P26-20** — clean higher-generation two-root quorum remains live after earlier isolated attacks/replays.

## Compromised-root simulation boundary

P26-11 may intentionally request a valid signature from one external KMS root over a conflicting but non-consequential synthetic checkpoint statement. This models one signing root producing conflicting evidence; it does **not** claim the KMS service or AWS account was actually compromised.

No destructive KMS administration calls are permitted merely to simulate compromise or revocation.

## Safety constraints

- No `DisableKey`, `ScheduleKeyDeletion`, `CreateKey`, key-policy mutation, alias mutation, or destructive KMS admin probe from the experiment workflow.
- No static AWS credentials.
- No local private key may stand in for root B or C in scientific endpoints.
- Valid unsafe/conflicting signatures are retained as evidence; do not retry until a desired answer appears.
- Quorum signatures are evidence only; authority remains external to the model and external to the root-quorum verifier.
- Workflow success is operational completion only.

## Success criterion

All twenty frozen endpoints must be satisfied on a frozen execution SHA with:

- exactly three registered external KMS key ARNs;
- threshold 2-of-3 distinct roots;
- zero duplicate-root threshold manufacture;
- zero mixed-statement threshold manufacture;
- zero model authority effect;
- zero authoritative platform effects.

## Bounded interpretation

A successful Pilot 26 with all keys in the same AWS account would establish evidence about distinct cryptographic KMS key roots under one administrative domain. It would **not** establish multi-account, multi-provider, multi-cloud, or administratively independent trust-domain tolerance; universal AWS/KMS security; Byzantine consensus; or safety under compromise of the AWS account's IAM/KMS administrators.

A later stronger pilot should place roots in separate administrative accounts/providers if that independence is required by the production threat model.
