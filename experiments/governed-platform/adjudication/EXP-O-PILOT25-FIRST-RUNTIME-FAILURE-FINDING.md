# EXP-O Pilot 25 — First Runtime Failure Finding

## Status

Recorded **before any Pilot 25 runner repair**.

## Frozen lineage

- Preregistered design SHA: `e5beafb470a65322d3a03d673a9e3b6851d63967`
- Trigger commit: `e2dd24fa9828df5fb2d33fa6d77e1ccdab540c86`
- First runtime workflow run: `34033188237`
- OIDC role assumption: PASS
- Exact AWS KMS path reached: YES
- Artifact ID: `9989292496`
- Artifact ZIP SHA-256 reported by Actions: `00d5e650914de0c7aa3ffa494839ccb2d3cbf46015f5c5c5df22b92e6950fd60`

## First-run result

- Total frozen endpoints: 20
- Passed: 12
- Failed: 8
- `model_authority_effect=false`
- `authoritative_platform_effect_count=0`
- `private_key_material_observed=false`

Passing negative/security endpoints included changed-message rejection, mutated-signature rejection, local private-key forgery rejection, stale-generation rejection, scope substitution rejection, unrelated-public-key rejection, duplicate-one-witness non-quorum, mixed-statement non-quorum, and the zero-authority endpoint.

The failed endpoints were the positive/durable witness-store paths: P25-03, P25-04, P25-09, P25-10, P25-11, P25-14, P25-16, and P25-20. Their witness responses consistently returned `STORE_INTEGRITY_ERROR` with SQLite `OperationalError`.

## Classification

**MECHANISM IMPLEMENTATION DEFECT — fail closed; not an AWS KMS failure and not a false green.**

The child witness opened SQLite with the default Python transaction mode, performed schema setup including `INSERT OR IGNORE INTO meta(...)`, and then later executed an explicit `BEGIN IMMEDIATE`. The preceding DML had already opened an implicit transaction, so the explicit begin raised `OperationalError` (`cannot start a transaction within a transaction`) on every clean path that reached durable witness-state processing.

No witness vote or quorum was manufactured through the defect. The implementation instead denied clean liveness.

## Concurrency observation

The same review identified that the original implementation read `max_generation` and the existing same-generation history row before acquiring its explicit write transaction. Although SQLite uniqueness/failure behavior remained fail closed in the observed run, the intended anti-equivocation decision should be serialized before those reads rather than relying on a later insert conflict.

## Permitted repair

The repair is limited to the witness SQLite transaction boundary:

1. finish/commit deterministic schema bootstrap before the operational transaction;
2. acquire `BEGIN IMMEDIATE` before reading `max_generation` and same-generation history;
3. perform anti-equivocation decision + history insert + max-generation update under that same serialized transaction;
4. preserve exact replay, same-generation conflict, lower-generation refusal, signature verification, trusted-minimum generation, KMS identity, witness credential stripping, quorum rule, and all twenty scientific endpoints unchanged.

No KMS key, role, region, signing algorithm, checkpoint payload, authority rule, quorum threshold, expected outcome, or negative test may be weakened.

After repair the complete original twenty-case suite must be rerun under a new frozen repair SHA. Final adjudication must retain this 12/20 first-run result and must not call Pilot 25 first-run 20/20.
