# EXP-O Pilot 25 — KMS-Signed Checkpoint → Credentialless Witness Integration Preregistration

## Status

PRE-EXECUTION. No Pilot 25 KMS call or witness execution may occur before the implementation, workflow, integrity tests, and trigger guard are frozen.

## Purpose

Pilot 24 established a bounded GitHub OIDC → AWS KMS asymmetric signing path and independent public-key verification. Pilot 25 tests the next boundary: a real witness subprocess that has **no AWS credentials and no checkpoint private key** must consume a KMS-signed checkpoint, validate the exact signature/scope/generation, combine that evidence with its own durable anti-equivocation state, and only then contribute a witness vote.

A valid KMS signature proves checkpoint provenance only. It does not by itself create execution, release, merge, deploy, or model authority.

## Frozen external path

- AWS region: `ap-southeast-2`
- OIDC role: `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`
- KMS key: `arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`
- key spec: `ECC_NIST_P256`
- usage: `SIGN_VERIFY`
- signing algorithm: `ECDSA_SHA_256`
- GitHub branch: `experiment/governed-platform-falsification-harness`
- static AWS access keys: forbidden

## Witness model

Two honest witness subprocesses (`w1`, `w2`) are sufficient for the bounded quorum control. Each witness has:

- its own SQLite durable signing history;
- its own witness HMAC key used only for the witness vote artifact;
- the KMS **public key only** for checkpoint verification;
- no `AWS_*` credentials in its child environment;
- no KMS private key material;
- durable refusal of lower-generation requests and same-generation conflicting checkpoint statements.

The coordinator may call KMS using the frozen OIDC role. The witness subprocess may not.

## Frozen canonical checkpoint statement

The signed statement binds at minimum:

- experiment `EXP-O`;
- pilot `PILOT25-KMS-WITNESS-INTEGRATION`;
- project `setugo`;
- task `exp-o-pilot25`;
- generation;
- checkpoint/root digest;
- purpose `witness-checkpoint-integrity`;
- nonce.

## Frozen endpoints

1. **P25-01** — exact OIDC assumed-role identity and exact KMS key metadata.
2. **P25-02** — exported public key is usable and fingerprint retained; no private key observed.
3. **P25-03** — witness child environment contains no AWS credentials.
4. **P25-04** — clean generation-1 KMS checkpoint is independently verified by witness and produces one durable witness vote.
5. **P25-05** — changed checkpoint/root statement with old KMS signature is rejected.
6. **P25-06** — mutated KMS signature is rejected.
7. **P25-07** — locally generated private-key forgery is rejected by the KMS public key.
8. **P25-08** — cryptographically valid generation below trusted minimum is semantically ineligible and produces no witness vote.
9. **P25-09** — same-generation conflicting valid KMS checkpoint is refused after an honest witness has durably voted for the first statement.
10. **P25-10** — lower-generation valid KMS checkpoint is refused after the witness has advanced to a higher generation.
11. **P25-11** — same-generation conflict and lower-generation refusal survive witness process restart.
12. **P25-12** — project/task scope substitution with an old signature is rejected.
13. **P25-13** — verifier/public-key substitution with an unrelated local public key cannot validate the KMS checkpoint.
14. **P25-14** — exact KMS checkpoint replay is idempotent and returns the same logical witness vote without advancing durable state.
15. **P25-15** — duplicate copies of one witness vote cannot manufacture two-witness quorum.
16. **P25-16** — two independent credentialless witness subprocesses validating the same current KMS checkpoint form the bounded two-witness quorum.
17. **P25-17** — one corrupted/unreadable witness store fails closed; the remaining single witness is insufficient for quorum.
18. **P25-18** — reordered valid witness votes for different checkpoint statement identities do not form quorum.
19. **P25-19** — all tested behavioral/checkpoint paths retain `model_authority_effect=false` and `authoritative_platform_effect_count=0`.
20. **P25-20** — clean higher-generation KMS checkpoint remains live after witness restart and earlier isolated attacks.

## Safety / execution constraints

- No destructive AWS KMS administration calls.
- No `DisableKey`, `ScheduleKeyDeletion`, `CreateKey`, policy mutation, alias mutation, or key deletion probes.
- No static AWS credentials in GitHub.
- Witness subprocess environments must strip all `AWS_*` variables.
- Valid unsafe or rejected outputs are retained as evidence; tests must not retry until green.
- A green workflow is operational completion only; endpoint evidence must be independently inspected.

## Success criterion

All twenty frozen endpoints must be satisfied on a frozen execution SHA, with zero effective model authority and zero consequential platform effects.

## Bounded interpretation

Even if successful, Pilot 25 will not prove AWS/KMS universal security, production witness quorum correctness, multi-account independence, key rotation/revocation safety, HSM physical properties, Byzantine tolerance, or independence of multiple KMS trust roots.
