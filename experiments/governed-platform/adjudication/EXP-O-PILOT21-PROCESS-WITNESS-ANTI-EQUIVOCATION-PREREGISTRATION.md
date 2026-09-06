# EXP-O Pilot 21 — Process-Isolated Witness Anti-Equivocation Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 21 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT20-MULTI-WITNESS-CHECKPOINT-ADJUDICATION.md`

Parent adjudication commit:

`5a62ac191825df875b4dcbf68aa50593c4938e78`

## Motivation

Pilot 20 passed the tested 2-of-3 independently keyed witness-verification cases, but witness independence was logical only: all keys and verification behavior were exercised inside one test/runtime trust domain. Pilot 20 also did not require each witness to durably remember what it had already signed, so a witness could in principle equivocate by signing conflicting statements at the same generation if a coordinator did not observe both statements.

Pilot 21 moves the witness boundary into three separate subprocesses. Each honest witness has only its own signing key and its own SQLite-backed monotonic signing log. The coordinator/verifier must not possess witness signing keys. Honest witnesses must durably refuse both generation rollback and same-generation conflicting statement signing across process restart.

## Scientific hypothesis

Across the frozen Pilot 21 cases:

1. two distinct live honest witness processes can establish the same-statement 2-of-3 quorum;
2. the coordinator cannot sign on behalf of a witness because witness keys are absent from its environment and process arguments;
3. an honest witness refuses a second different statement at the same generation;
4. an honest witness refuses lower-generation signing after a higher generation is durably recorded;
5. both refusal properties survive witness process termination and restart;
6. duplicate/reordered/delayed transport cannot manufacture a second witness or retroactively authorize a previously denied request;
7. one unavailable or malicious witness cannot prevent clean 2-of-3 liveness when the other two honest witnesses agree;
8. one malicious witness cannot independently create a conflicting quorum;
9. threshold-valid old statements remain subject to the separately trusted minimum generation at verification;
10. clean higher-generation authority/effect state remains live with exactly one local durable effect on the tested path.

Any tested path where one process identity contributes twice, an honest witness signs conflicting same-generation statements, an honest restarted witness signs below its durable maximum generation, or fewer than two distinct valid agreeing processes authorize recovery falsifies Pilot 21 on that path.

## Frozen architecture under test

Pilot 21 must use new isolated files and must not modify Pilots 14–20.

### Witness processes

Exactly three configured witness identities: `w1`, `w2`, `w3`.

Each witness process must have:

- a distinct process identity;
- a distinct HMAC-SHA256 signing key supplied only to that witness process;
- a distinct SQLite database file for durable signing history;
- request/response transport over a local process boundary (for example stdin/stdout JSON or localhost socket);
- no ability to read the other witnesses' keys;
- durable rows binding generation to exact statement digest;
- durable maximum-generation state.

Honest witness signing rule:

- first valid statement at a generation may be signed;
- exact replay of the same statement at the same generation may return the same logical approval without appending a conflicting record;
- a different statement at an already signed generation must be refused;
- any request below the highest durably signed generation must be refused;
- a higher generation may be signed and becomes the new durable maximum;
- signing state must be committed before the positive signature/acknowledgement is returned.

### Coordinator/verifier

- has witness public configuration/ids/key ids and verifier key material needed by this bounded HMAC prototype, but the process that requests signatures must not receive raw witness signing keys;
- counts each witness identity at most once;
- requires 2 distinct valid signatures over the exact same canonical Pilot-20-style checkpoint statement;
- enforces project/task/logical-state/generation/root/fence binding;
- enforces separately trusted minimum generation;
- verifies local SQLite seals and strict relational recovery before returning authority;
- no model-visible input, provider call, or model-issued authority.

For this bounded prototype, a parent test harness may know fixture keys in order to independently verify signatures; the **coordinator subprocess/request path** must not possess them. This does not claim HSM/KMS isolation.

## Threat model

The adversarial harness may:

- terminate/restart witness processes;
- delay, duplicate, drop, and reorder request/response messages;
- make one witness unavailable;
- fully control one designated malicious witness's behavior/key;
- replay prior valid signatures;
- submit lower-generation or conflicting same-generation statements;
- rewrite local authority DB state and reseal it as in Pilots 19–20;
- combine individually valid signatures from different statements.

The adversary may not possess two honest witness keys simultaneously or alter the verifier's separately supplied minimum generation.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must exist before first scientific execution.

### P21-01 — three independent witness processes and stores
Expected: distinct live PIDs and distinct durable SQLite paths/identities are demonstrated.

### P21-02 — clean two-process same-statement quorum
Expected: two honest witness subprocesses sign the exact current statement and recovery may authorize current clean authority.

### P21-03 — coordinator request path has no witness signing keys
Expected: coordinator environment/arguments/request surface cannot expose raw witness signing keys.

### P21-04 — same witness exact replay is idempotent
Expected: exact same-generation/same-statement replay returns consistent approval without creating a second logical vote/history conflict.

### P21-05 — honest witness same-generation conflicting statement refusal
Expected: second different statement at an already signed generation is denied and not signed.

### P21-06 — same-generation equivocation refusal survives restart
Expected: kill/restart witness after first signature; conflicting statement at that generation is still denied from durable history.

### P21-07 — honest witness lower-generation refusal
Expected: after signing generation N, request for N-1 is denied.

### P21-08 — lower-generation refusal survives restart
Expected: after kill/restart, lower-generation request remains denied.

### P21-09 — higher generation advances durable maximum
Expected: generation N+1 clean statement is signed and durable maximum advances exactly once.

### P21-10 — crash after durable signing commit but before response
Expected: response may be transport-unknown, but restart exact replay returns the same logical signature/approval and does not create a conflicting history row.

### P21-11 — duplicate response from one witness cannot count twice
Expected: coordinator/verifier counts the witness identity once; no manufactured quorum.

### P21-12 — delayed positive response cannot retroactively reopen an already failed quorum decision
Expected: a decision made without threshold remains non-authorizing for that attempt; a later response requires a new verification attempt rather than mutating the old decision.

### P21-13 — reordered signatures for different statements do not form quorum
Expected: individually valid process signatures over different statement digests do not combine.

### P21-14 — one malicious witness signs conflicting root, two honest agree
Expected: honest 2-of-3 exact-statement quorum wins; malicious minority cannot alter accepted statement.

### P21-15 — one honest witness unavailable, remaining honest pair agrees
Expected: 2-of-3 clean liveness succeeds.

### P21-16 — one honest witness unavailable plus one malicious conflicting witness
Expected: only one honest matching vote remains; no conflicting quorum is formed.

### P21-17 — old two-process valid signatures below trusted minimum generation
Expected: rollback denied despite valid process signatures.

### P21-18 — coherent DB rewrite/reseal plus one malicious witness re-signs
Expected: one malicious signer is insufficient; old honest signatures/root cannot validate rewritten DB.

### P21-19 — repeated restart/retry cannot erase honest anti-equivocation memory
Expected: repeated process restarts do not permit an honest witness to sign a previously refused same-generation conflict or lower generation.

### P21-20 — clean higher-generation quorum/effect liveness control
Expected: two honest process witnesses sign a higher-generation clean consumed state, verification succeeds as quorum-bound consumed recovery, and local durable effect count remains exactly one.

## Primary endpoints

1. honest same-generation equivocation-sign rate;
2. honest lower-generation rollback-sign rate;
3. restart loss-of-signing-memory rate;
4. duplicate-identity quorum-manufacture rate;
5. delayed-response retroactive-authorization rate;
6. mixed-statement signature-combination acceptance rate;
7. single-malicious-witness conflicting-quorum acceptance rate;
8. two-honest-with-one-unavailable liveness;
9. old-valid-quorum rollback acceptance rate;
10. clean higher-generation quorum/effect liveness.

Any non-zero honest equivocation signing, honest rollback signing, restart memory loss, sub-threshold authorization, or below-minimum quorum acceptance falsifies Pilot 21 on the exact tested path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- process-isolation cases must record distinct live PIDs and distinct durable store paths;
- restart cases must prove a new PID and reuse the same witness durable store;
- crash-after-commit case must prove durable state exists before process termination/response loss;
- transport duplicate/reorder/delay cases must retain the exact witness ids and statement digests involved;
- first-run failures are retained exactly;
- no case may be removed, renamed, weakened, or silently converted after first execution;
- any post-result repair requires explicit diagnosis and rerun lineage;
- workflow SUCCESS is operational evidence only; scientific adjudication reads individual P21 outcomes.

## Isolation

Pilot 21 must not modify:

- Pilots 14–20 runtime/tests/adjudications;
- frozen EXP-N Pilot 8/9 provider paths.

## Frozen limitations

Even a complete Pilot 21 pass will not prove:

- production HSM/KMS or secret custody;
- true administrative, geographic, or cloud-provider independence of witnesses;
- security after compromise of two threshold witness keys;
- correctness under arbitrary asynchronous network partitions;
- global transparency/gossip detection of equivocation outside the tested coordinator;
- formal Byzantine consensus;
- physical power-loss durability;
- kernel/filesystem correctness for witness SQLite stores;
- exactly-once semantics for arbitrary external non-idempotent systems.

Allowed conclusions must remain limited to the exact subprocess, durable witness-history, anti-equivocation, transport-fault, and 2-of-3 verification paths exercised by this pilot.
