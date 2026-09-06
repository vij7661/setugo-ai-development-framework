# EXP-O Pilot 25 — KMS-Signed Checkpoint → Credentialless Witness Integration Adjudication

## Verdict

`NO_TESTED_KMS_SIGNED_CHECKPOINT_FORGERY_SUBSTITUTION_STALE_GENERATION_RESTART_DUPLICATE_VOTE_CORRUPT_STORE_OR_MIXED_STATEMENT_PATH_MANUFACTURED_THE_TESTED_TWO_WITNESS_QUORUM_AFTER_RECORDED_TRANSACTION_REPAIR`

## Frozen lineage

- Pilot 25 preregistration commit: `d0353f8fa70dd45d7737fb0babbe0595b97a218a`.
- Initial frozen pre-execution design SHA: `e5beafb470a65322d3a03d673a9e3b6851d63967`.
- Exact AWS role: `arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer`.
- Exact KMS key: `arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c`.
- Region: `ap-southeast-2`.
- Key spec: `ECC_NIST_P256`; usage `SIGN_VERIFY`; algorithm `ECDSA_SHA_256`.
- Witness subprocesses received only the exported KMS public key plus their own local witness vote key; all `AWS_*` variables were removed from child environments.
- Static AWS access keys were not used.

## First runtime execution — retained failure

- Trigger commit: `e2dd24fa9828df5fb2d33fa6d77e1ccdab540c86`.
- Workflow run: `34033188237`.
- OIDC role assumption: PASS.
- AWS KMS path reached: YES.
- Artifact ID: `9989292496`.
- Artifact ZIP SHA-256: `00d5e650914de0c7aa3ffa494839ccb2d3cbf46015f5c5c5df22b92e6950fd60`.
- Frozen endpoints passed: **12/20**.
- Frozen endpoints failed: **8/20**.
- `model_authority_effect=false`.
- `authoritative_platform_effect_count=0`.
- `private_key_material_observed=false`.

The eight failures were P25-03, P25-04, P25-09, P25-10, P25-11, P25-14, P25-16, and P25-20. They were positive/durable witness-store paths. The negative signature/substitution/staleness/quorum safety cases continued to fail closed.

The failure was classified and recorded before repair in `EXP-O-PILOT25-FIRST-RUNTIME-FAILURE-FINDING.md` as a **mechanism implementation defect that failed closed**, not an AWS KMS failure and not a false green. Python SQLite schema bootstrap DML opened an implicit transaction, after which the witness attempted `BEGIN IMMEDIATE`, producing `OperationalError: cannot start a transaction within a transaction` on clean durable paths.

The same review also identified that the original anti-equivocation reads occurred before the intended explicit serialized write transaction. That was tightened as part of the same recorded repair.

Pilot 25 therefore must **not** be described as first-run 20/20.

## Permitted repair and repaired design

Repair SHA: `bcd1e2c4fbf6848a9443ee96b5986f58884caf3f`.

The repair changed only the witness SQLite transaction boundary:

1. finish and commit deterministic schema/bootstrap DML before the operational transaction;
2. run the SQLite integrity check;
3. acquire `BEGIN IMMEDIATE` before reading durable `max_generation` and same-generation history;
4. make the anti-equivocation decision, vote insert, and maximum-generation update within that serialized transaction;
5. explicitly rollback before exact-replay, same-generation-conflict, or lower-generation return paths.

No KMS key, IAM role, region, algorithm, checkpoint statement, trusted-minimum rule, witness credential stripping, quorum threshold, authority rule, or scientific endpoint was weakened or changed.

- Trigger rebind commit: `9d7cfac72d32928dbedc0d4639eefbced1c9cef3`.

## Repaired runtime evidence

- Workflow run: `34033357401`.
- Job: `101486896711`.
- Protected design guard verified repair SHA `bcd1e2c4fbf6848a9443ee96b5986f58884caf3f` before OIDC/KMS execution.
- Assumed identity: `arn:aws:sts::297165774800:assumed-role/setugo-pilot24-kms-signer/setugo-exp-o-pilot25`.
- Frozen endpoints: **20/20 PASS after the recorded repair**.
- `all_endpoints_satisfied=true`.
- `model_authority_effect=false`.
- `authoritative_platform_effect_count=0`.
- `private_key_material_observed=false`.
- Exported KMS public-key SHA-256: `2ea6a915cfff30a02e2d6027e12a5182cca642533d6202e61661faa7e4bea7b3`.
- Artifact ID: `9989343091`.
- Artifact ZIP SHA-256: `2cd7329372ed3e9ce96ccdf250f2eb7493f14ec49a8ef9fa7fac2e790ae349fb`.

Endpoint evidence included:

- P25-03: child witness explicitly reported `aws_credentials_present=false` and produced a valid durable vote.
- P25-05/P25-06/P25-07: changed message, mutated KMS signature, and locally forged signature were rejected.
- P25-08: a cryptographically valid checkpoint below the trusted minimum generation was semantically ineligible.
- P25-09: a second valid KMS checkpoint with a different statement at the same generation was refused as `SAME_GENERATION_CONFLICT`.
- P25-10: a valid lower-generation KMS checkpoint after durable generation advancement was refused as `LOWER_GENERATION`.
- P25-11: same-generation and lower-generation refusals survived fresh subprocess restart against the same durable witness stores.
- P25-13: unrelated public-key substitution could not validate the KMS checkpoint.
- P25-14: exact replay returned `IDEMPOTENT_REPLAY` with the same logical vote.
- P25-15: duplicate copies of one witness vote did not manufacture a two-witness quorum.
- P25-16: two distinct credentialless witness subprocesses validating the same current KMS checkpoint formed the bounded two-witness quorum.
- P25-17: corrupted witness SQLite state returned `STORE_INTEGRITY_ERROR`; the remaining single healthy witness was insufficient for quorum.
- P25-18: two valid witness votes over different checkpoint statement hashes did not form quorum.
- P25-20: the clean higher-generation checkpoint remained live across witness restart and exact replay.

## Regression evidence

The repaired SHA also completed the main deterministic harness successfully in run `34033334045`:

- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation: 12/12
- governance/falsification: 728/728
- total: **838/838**

The previously known Pilot 21 subprocess-pipe `ResourceWarning`s remain implementation-hygiene debt and did not change the Pilot 25 endpoint decisions.

## Scientific interpretation

Within this bounded path, a real AWS-KMS-signed asymmetric checkpoint was consumed by separate witness subprocesses that had no AWS credentials and no checkpoint private key. The tested forgery, substitution, stale-generation, restart, duplicate-vote, corrupted-store, and mixed-statement paths did not manufacture the tested two-witness quorum after the recorded fail-closed transaction repair. No model authority or authoritative platform effect was created by checkpoint provenance or witness agreement.

This does **not** prove universal AWS KMS security, production-grade witness quorum correctness, Byzantine tolerance, multi-account or multi-cloud trust independence, physical HSM properties, arbitrary filesystem/power-loss behavior, or safety under administrative compromise of the AWS account or IAM/KMS policy layer.

## Next boundary

The next distinct scientific boundary is a quorum of **multiple external asymmetric signing roots**. A single KMS key cannot establish tolerance to one externally compromised signing root or prove that duplicate/aliased signatures from one root cannot manufacture a multi-root threshold. A meaningful 2-of-3 external-root pilot requires two additional asymmetric signing keys (or stronger: keys in separate administrative trust domains). That provisioning is external to this repository and is therefore a manual-intervention boundary.
