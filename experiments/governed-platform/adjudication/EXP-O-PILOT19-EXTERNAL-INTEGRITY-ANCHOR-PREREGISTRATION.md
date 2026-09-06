# EXP-O Pilot 19 — External Authenticated Integrity Anchor Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 19 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT18-SQLITE-STORAGE-FAULT-ADJUDICATION.md`

Parent adjudication commit:

`5632425ccd820b3415d8486b599de3c8c5b20c26`

## Motivation

Pilot 18 passed the tested software-level SQLite storage-fault and corruption cases, but its application row seals are stored inside the same SQLite trust domain as the state they protect. That detects the tested accidental/isolated mutations but does not establish resistance to a privileged actor that can coherently rewrite both database state and local seals.

Pilot 19 therefore moves the integrity root outside the database/storage-admin trust domain. It tests whether consequential authority remains fail-closed when database state and local seals are coherently altered, replayed, substituted, or paired with forged/stale external checkpoints.

## Scientific hypothesis

Across the frozen Pilot 19 cases:

1. coherent state + local-seal rewriting cannot create effective consequential authority when the external authenticated root no longer matches;
2. a forged external checkpoint cannot validate under an unknown/wrong key or modified signature;
3. a previously valid but old authenticated checkpoint cannot be replayed below a separately supplied minimum trusted generation;
4. semantic/effect/idempotency/fence changes remain bound by the external root even if local seals are recomputed by the attacker;
5. missing, malformed, unknown-key, mismatched-scope, or unverifiable external checkpoint state fails closed;
6. a clean higher generation can be anchored and remains live.

Any tested case that promotes coherently rewritten or rolled-back state to authority despite external-root mismatch/authentication failure falsifies Pilot 19 on that path.

## Frozen architecture under test

Pilot 19 must use new isolated files and must not modify Pilots 14–18.

Required components:

- Pilot-18 SQLite state shape and local integrity seals may be reused as inputs;
- an external checkpoint record stored outside the SQLite database;
- checkpoint record contains at minimum: checkpoint version, key id, project/task binding, logical state identity, monotonic generation, monotonic fence, logical-state root digest, and authentication tag;
- authentication uses HMAC-SHA256 in this bounded prototype, with the signing key supplied outside SQLite and never stored in the database;
- verifier is given a separately trusted minimum generation; a cryptographically valid older checkpoint below that generation must still fail closed;
- logical-state root is computed from canonical authority/effect/meta state, not raw SQLite file bytes;
- verification of external checkpoint precedes any return of effective consequential authority;
- no model-visible input, provider call, or model-issued authority.

HMAC in this pilot is a prototype trust-boundary mechanism, not a production key-management claim.

## Threat model

The adversarial mutation harness may modify:

- SQLite authority/effect/meta rows;
- in-database local integrity seals;
- copied database/WAL files;
- candidate external checkpoint bytes supplied to the verifier.

The adversarial mutation harness may **not** possess the trusted HMAC key or alter the verifier's separately supplied minimum trusted generation. Cases that use an old valid checkpoint represent replay of previously legitimate evidence, not signature forgery.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must exist before first scientific execution.

### P19-01 — clean externally anchored authority control
Expected: exact current DB + local seals + authenticated external checkpoint at current generation may recover authority.

### P19-02 — coherent authority-row rewrite plus recomputed local seals
Expected: local integrity becomes internally clean but external root mismatch denies authority.

### P19-03 — coherent owner/fence rewrite plus recomputed local seals
Expected: external root mismatch blocks changed authority despite valid SQLite/local seals.

### P19-04 — forged checkpoint signed with wrong key
Expected: authentication fails; no authority.

### P19-05 — checkpoint authentication-tag byte mutation
Expected: authentication fails; no authority.

### P19-06 — valid old checkpoint replay below trusted minimum generation
Expected: rollback is rejected even though old checkpoint signature is valid.

### P19-07 — stale DB plus matching stale local seals plus valid old checkpoint
Expected: trusted minimum generation blocks the coherent stale bundle.

### P19-08 — database from different logical lineage paired with current checkpoint
Expected: state-root/scope identity mismatch fails closed.

### P19-09 — committed effect rewritten plus recomputed local seals
Expected: external root mismatch prevents treating rewritten effect history as authoritative.

### P19-10 — consumed authority resurrected to ACTIVE plus recomputed local seals
Expected: external root mismatch prevents authority resurrection.

### P19-11 — monotonic metadata lowered plus recomputed local seals
Expected: external checkpoint fence/root blocks rollback.

### P19-12 — idempotency key changed plus recomputed local seals
Expected: external root mismatch denies rebinding.

### P19-13 — semantic digest changed plus recomputed local seals
Expected: external root mismatch denies semantic rebinding.

### P19-14 — effect digest changed consistently in authority/effect plus recomputed local seals
Expected: external root mismatch denies coherent effect-history rewrite.

### P19-15 — checkpoint project/task scope substituted
Expected: scope binding mismatch denies even if remaining fields are unchanged.

### P19-16 — checkpoint root replaced without valid authentication
Expected: invalid authentication/root binding denies.

### P19-17 — external checkpoint missing
Expected: absence is distinguished from clean no-authority state and fails closed.

### P19-18 — unknown checkpoint key id
Expected: verifier cannot authenticate and denies.

### P19-19 — repeated recovery with same coherent forged bundle
Expected: retries never eventually promote tampered state to authority.

### P19-20 — clean higher-generation liveness control
Expected: fresh legitimate state can advance to a higher authenticated generation, execute/consume exactly once, and recover as consumed without false blocking.

## Primary endpoints

1. coherent local-state rewrite authority-promotion rate;
2. forged-checkpoint acceptance rate;
3. valid-old-checkpoint rollback acceptance rate;
4. semantic/effect/idempotency rewrite acceptance rate;
5. missing/unverifiable checkpoint fail-open rate;
6. clean higher-generation liveness.

Any non-zero tampered-state authority promotion, forged-checkpoint acceptance, or trusted-generation rollback acceptance is a falsification on the exact tested path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- each tamper/replay case must prove the mutation or substituted evidence differs from the frozen clean source;
- first-run failures are retained exactly;
- no case may be removed, renamed, weakened, or silently converted after first execution;
- any post-result repair requires recorded diagnosis and rerun lineage;
- workflow SUCCESS is operational evidence only; scientific adjudication reads exact case outcomes.

## Isolation

Pilot 19 must not modify:

- Pilots 14–18 runtime/tests/adjudication;
- frozen EXP-N Pilot 8/9 provider paths.

## Frozen limitations

Even a complete Pilot 19 pass will not prove:

- production HSM/KMS correctness or secret-key custody;
- resistance to an attacker who compromises the trusted verifier/key and minimum-generation source simultaneously;
- physical storage durability or real power-loss behavior;
- remote transparency-log or witness availability;
- distributed consensus correctness for checkpoint publication;
- every rollback/equivocation strategy;
- formal Byzantine fault tolerance;
- exactly-once behavior for arbitrary external non-idempotent services.

Allowed conclusions must remain limited to the exact externally authenticated HMAC checkpoint and trusted-generation boundary exercised by this pilot.
