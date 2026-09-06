# EXP-O Pilot 20 — Multi-Witness Authenticated Checkpoint Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 20 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT19-EXTERNAL-INTEGRITY-ANCHOR-ADJUDICATION.md`

Parent adjudication commit:

`2cade979ed0faa8b9a4c825a239d29c3028171b1`

## Motivation

Pilot 19 moved logical-state integrity outside the SQLite/storage-admin trust domain and rejected coherent local rewrites, forged checkpoints, and valid-old checkpoint rollback beneath a separately trusted minimum generation. Its remaining central trust concentration is a **single checkpoint signer/key**. If that signer is compromised or equivocates, it can authenticate a conflicting root.

Pilot 20 therefore tests a 2-of-3 independently keyed witness checkpoint boundary. One witness may be malicious, compromised, unavailable, stale, or equivocating; it must not independently establish effective consequential authority. A clean checkpoint requires two distinct currently trusted witnesses agreeing on the same exact checkpoint statement.

## Scientific hypothesis

Across the frozen Pilot 20 cases:

1. one valid witness signature is insufficient;
2. duplicated evidence from the same witness cannot manufacture quorum;
3. one compromised witness signing a conflicting root cannot override two honest witnesses;
4. two witnesses that sign different roots/generations/scopes do not form quorum;
5. valid-old two-witness evidence cannot roll back below the separately trusted minimum generation;
6. unknown, revoked, malformed, wrong-scope, and substituted witness identities do not count;
7. a 2-of-3 clean agreeing witness set remains live when one witness is unavailable;
8. a clean higher-generation checkpoint can advance with two agreeing independent witnesses.

Any tested case in which fewer than two distinct trusted agreeing witnesses authorize a consequentially usable recovered state falsifies Pilot 20 on that path.

## Frozen architecture under test

Pilot 20 must be implemented in new isolated files and must not modify Pilots 14–19.

Checkpoint statement must canonically bind at minimum:

- protocol version;
- project;
- task;
- logical-state identity;
- monotonic generation;
- logical-state root;
- monotonic fence `(term, commit_index, lease_epoch)`.

Witness evidence must bind at minimum:

- witness id;
- key id;
- exact checkpoint-statement digest;
- authentication tag.

Verifier requirements:

- exactly three configured witness identities for this pilot;
- threshold = 2 distinct trusted witnesses;
- each witness uses a distinct HMAC-SHA256 key in this bounded prototype;
- one witness id contributes at most one vote to one statement;
- quorum requires two valid signatures over the **same exact statement**;
- unknown or revoked witness/key evidence contributes zero votes;
- valid old quorum below separately trusted minimum generation is rejected;
- local SQLite seals and strict relational integrity remain prerequisites;
- quorum verification occurs before any return of effective consequential authority;
- no model-visible input, provider call, or model-issued authority.

HMAC and in-process witness keys are test mechanisms only, not production HSM/KMS claims.

## Threat model

The adversarial harness may:

- rewrite SQLite state and recompute local seals;
- forge or modify witness records without the relevant honest witness key;
- fully control one configured witness key/identity;
- replay prior valid witness records;
- duplicate/reorder witness records;
- omit one or more witnesses;
- combine individually valid witness records for different statements.

The adversary may **not** possess two honest witness keys simultaneously or alter the verifier's separately supplied trusted minimum generation.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must exist before first scientific execution.

### P20-01 — clean 2-of-3 agreeing witness control
Expected: two distinct valid trusted witnesses over the exact current statement establish quorum and may recover current authority.

### P20-02 — one valid witness only
Expected: insufficient quorum; no authority.

### P20-03 — duplicate same-witness record presented twice
Expected: duplicate identity counts once; insufficient quorum.

### P20-04 — one valid honest witness plus forged second witness
Expected: forged evidence contributes zero; no quorum.

### P20-05 — one compromised witness signs forged conflicting state
Expected: one malicious valid signer alone cannot authorize conflicting state.

### P20-06 — two valid witnesses sign different state roots
Expected: no same-statement quorum.

### P20-07 — two valid witnesses sign different generations
Expected: no same-statement quorum.

### P20-08 — two valid witnesses sign different project/task scope
Expected: no same-statement quorum; wrong-scope evidence cannot count for requested scope.

### P20-09 — three records where two honest agree and one compromised conflicts
Expected: honest 2-of-3 exact-statement quorum wins; conflicting minority does not alter the accepted statement.

### P20-10 — three records where no two agree
Expected: no quorum.

### P20-11 — valid old 2-of-3 quorum below trusted minimum generation
Expected: rollback denied despite threshold-valid signatures.

### P20-12 — stale DB + recomputed local seals + valid old 2-of-3 witnesses
Expected: trusted minimum generation blocks coherent stale bundle.

### P20-13 — coherent DB rewrite + local reseal + only compromised witness re-signs new root
Expected: one malicious signer insufficient; no authority.

### P20-14 — coherent DB rewrite + local reseal + old honest quorum retained
Expected: state root mismatch blocks authority.

### P20-15 — unknown witness identity paired with valid-looking authentication
Expected: unknown witness contributes zero votes.

### P20-16 — revoked witness plus one honest current witness
Expected: revoked witness contributes zero; one remaining vote insufficient.

### P20-17 — witness identity/key substitution
Expected: evidence cannot transfer between witness identities or key ids.

### P20-18 — one witness unavailable, remaining two honest agree
Expected: clean liveness with exact 2-of-3 quorum.

### P20-19 — repeated retry of one-witness forged/conflicting bundle
Expected: retries never eventually manufacture quorum.

### P20-20 — clean higher-generation quorum liveness control
Expected: state advances legitimately, two independent witnesses sign the higher-generation exact statement, effect remains exactly once/consumed, and recovery accepts the quorum-bound consumed state without false blocking.

## Primary endpoints

1. sub-threshold authority-promotion rate;
2. duplicate-witness quorum-manufacture rate;
3. single-compromised-witness conflicting-root acceptance rate;
4. mixed-statement witness acceptance rate;
5. valid-old-quorum rollback acceptance rate;
6. revoked/unknown/substituted witness vote acceptance rate;
7. exact 2-of-3 liveness with one unavailable witness;
8. higher-generation clean quorum liveness.

Any non-zero authority promotion from fewer than two distinct valid agreeing trusted witnesses, or acceptance of a below-minimum old quorum, falsifies Pilot 20 on the exact tested path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- each attack must prove the witness/state mutation, disagreement, duplication, replay, revocation, or absence it claims;
- first-run failures are retained exactly;
- no case may be removed, renamed, weakened, or silently converted after first execution;
- any post-result repair requires explicit diagnosis and rerun lineage;
- workflow SUCCESS remains operational evidence only; scientific adjudication reads individual P20 outcomes.

## Isolation

Pilot 20 must not modify:

- Pilots 14–19 runtime/tests/adjudications;
- frozen EXP-N Pilot 8/9 provider paths.

## Frozen limitations

Even a complete Pilot 20 pass will not prove:

- production HSM/KMS or key-custody correctness;
- security after compromise of two threshold witnesses;
- independence of witnesses deployed in the same administrative/failure domain;
- remote transparency-log correctness;
- asynchronous distributed consensus or network-partition liveness;
- prevention of all equivocation when witnesses do not share a common observation channel;
- formal Byzantine fault tolerance;
- physical power-loss/storage durability;
- exactly-once semantics for arbitrary external non-idempotent services.

Allowed conclusions must remain limited to the exact 2-of-3 independently keyed witness-verification boundary tested here.
