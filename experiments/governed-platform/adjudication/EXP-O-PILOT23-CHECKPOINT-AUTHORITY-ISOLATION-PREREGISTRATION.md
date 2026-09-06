# EXP-O Pilot 23 — Checkpoint Authority Process Isolation Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 23 IMPLEMENTATION OR TEST EXECUTION**

Parent Pilot 22 adjudication: `ab83a5b1e8ec711a89fb3875c758bed878b8b868`

## Motivation

Pilot 22 authenticated each witness-history checkpoint with HMAC. HMAC is symmetric: any component holding the raw key for verification can also mint a new checkpoint. The tested Pilot 22 witness therefore still possessed checkpoint-minting material, so checkpoint authority was not actually separated from witness signing authority.

Pilot 23 removes the raw checkpoint key from witness processes. A separate checkpoint-authority subprocess owns the checkpoint HMAC key and durable monotonic checkpoint history. Witness processes may ask this authority to verify a presented checkpoint, but may not receive the raw checkpoint key or mint checkpoints themselves.

This is a bounded process-isolation experiment, not an asymmetric-cryptography or HSM/KMS claim.

## Scientific hypothesis

Across the frozen Pilot 23 cases:

1. witness processes have no raw checkpoint signing key in environment, argv or request payload;
2. the checkpoint-authority process alone mints checkpoint records;
3. checkpoint issuance is monotonic per witness/store and durably refuses generation rollback and same-generation conflicting roots;
4. anti-equivocation survives checkpoint-authority process restart;
5. a witness cannot locally forge a current checkpoint by using its own witness signing key;
6. unknown, forged, stale or scope-substituted checkpoint records are rejected by the authority verification path;
7. checkpoint-authority unavailability fails closed for new witness signatures;
8. delayed/replayed prior verification success cannot be reused for a changed checkpoint or changed witness history;
9. post-history-commit / pre-checkpoint-publication ambiguity remains non-authorizing until the checkpoint authority reconciles exact state;
10. one checkpoint-authority process plus two honest witness processes retain clean higher-generation liveness on the tested path.

Any tested path where a witness obtains checkpoint minting authority, where checkpoint rollback/equivocation is accepted after authority restart, or where verification can be replayed for a changed state falsifies Pilot 23 on that path.

## Frozen architecture

Pilot 23 must use new isolated files and must not modify Pilots 14–22.

### Checkpoint authority process

One subprocess for this bounded pilot:

- owns the raw checkpoint HMAC key in its child-only environment;
- owns a distinct SQLite database containing durable checkpoint issuance history;
- receives canonical checkpoint statements over stdin/stdout JSON;
- supports `issue` and `verify` operations;
- commits checkpoint issuance history before returning a positive issue response;
- refuses lower checkpoint generations after a higher generation;
- refuses a different checkpoint statement/root at an already issued generation;
- exact replay at same generation/same statement is idempotent;
- restart reuses the same durable database and retains monotonic history;
- no raw key is returned in responses.

### Witness processes

Witness processes:

- retain only their own witness-signing key;
- do **not** receive checkpoint HMAC key in environment, argv or stdin request;
- must obtain an explicit current verification decision from the checkpoint-authority process before signing;
- bind that verification decision to the exact checkpoint digest, witness id, store identity and minimum checkpoint generation;
- may not convert authority unavailability into permission.

### Coordinator/test harness

The parent harness may know fixture keys for independent test verification, but the requesting witness path must not possess checkpoint minting material.

No model/provider call participates.

## Threat model

The adversarial harness may:

- inspect witness argv/environment and request payloads;
- terminate/restart checkpoint authority and witness processes;
- delay/drop/replay checkpoint verification responses;
- forge checkpoint records with witness signing keys or unrelated keys;
- submit stale/current/conflicting checkpoint roots;
- tamper/reseal witness stores as in Pilot 22;
- replay old valid checkpoint records below a separately trusted minimum generation.

The adversary may not directly read the checkpoint-authority child environment containing the checkpoint key for the positive isolation cases. This does not model privileged host compromise.

## Pre-registered primary falsifiers

Exactly twenty cases must exist before first scientific execution.

### P23-01 — checkpoint authority has distinct process/store
Expected: distinct PID and durable authority-store path demonstrated.

### P23-02 — witness process has no checkpoint signing key
Expected: raw checkpoint key absent from witness env/argv/request surface.

### P23-03 — clean checkpoint issuance and witness verification
Expected: authority issues current checkpoint; witness verifies exact checkpoint and signs current statement.

### P23-04 — witness signing key cannot forge checkpoint
Expected: checkpoint record forged with witness signing key is rejected.

### P23-05 — unrelated key cannot forge checkpoint
Expected: wrong-key checkpoint is rejected.

### P23-06 — checkpoint authority lower-generation issuance refusal
Expected: after checkpoint generation N, issuance request for N-1 is denied.

### P23-07 — checkpoint authority same-generation conflicting-root refusal
Expected: different root at already issued generation is denied.

### P23-08 — checkpoint monotonicity survives authority restart
Expected: restart preserves lower-generation and same-generation-conflict refusal.

### P23-09 — exact checkpoint issue replay is idempotent
Expected: same generation/exact statement returns same logical checkpoint without conflicting history.

### P23-10 — checkpoint tag mutation rejected
Expected: modified auth tag cannot verify.

### P23-11 — checkpoint scope substitution rejected
Expected: witness/store/key identity substitution is denied.

### P23-12 — old valid checkpoint below trusted minimum rejected
Expected: rollback denied despite valid authentication.

### P23-13 — checkpoint authority unavailable fails closed
Expected: witness cannot sign a new statement without current checkpoint verification.

### P23-14 — delayed old positive verify cannot authorize changed checkpoint
Expected: old positive verification result cannot be rebound to a different checkpoint digest/root.

### P23-15 — delayed old positive verify cannot authorize changed witness history
Expected: prior verification cannot authorize signing after local history root changes.

### P23-16 — post-history-commit/pre-checkpoint ambiguity remains blocked
Expected: exact history committed but not checkpointed cannot be promoted until authority issues/verifies the exact new checkpoint.

### P23-17 — authority crash after durable issue commit before response
Expected: restart exact replay returns same logical checkpoint; no conflicting issuance.

### P23-18 — tampered/resealed witness store plus old checkpoint remains blocked
Expected: old checkpoint verification cannot validate changed local history.

### P23-19 — one checkpoint authority + two honest witnesses clean quorum liveness
Expected: current exact checkpoint verification allows two honest witnesses to form valid 2-of-3 authority quorum.

### P23-20 — clean higher-generation consumed-state liveness after restarts
Expected: checkpoint authority and witnesses restart, exact higher-generation checkpoint/signatures validate consumed recovery and exactly one local effect.

## Primary endpoints

1. witness possession of checkpoint-minting material;
2. unauthorized checkpoint forgery acceptance rate;
3. checkpoint rollback issuance rate;
4. same-generation checkpoint equivocation issuance rate;
5. restart loss-of-checkpoint-memory rate;
6. stale verification replay acceptance rate;
7. checkpoint-authority-unavailable fail-open rate;
8. post-history/pre-checkpoint ambiguity promotion rate;
9. clean two-witness quorum liveness;
10. clean higher-generation consumed recovery liveness.

## Evidence policy

- all twenty cases execute in the first scientific run;
- process PID/store isolation must be demonstrated;
- witness no-key test must inspect the actual launched witness environment/argv/request construction;
- first-run failures are retained;
- no case may be silently weakened after execution;
- repair requires explicit diagnosis and lineage;
- workflow SUCCESS is operational only; adjudication reads individual P23 outcomes.

## Limitations

Even a complete pass will not prove:

- asymmetric verify-only cryptographic separation;
- KMS/HSM custody;
- privileged-host isolation from child process environments;
- administrative/geographic/cloud-provider separation;
- multiple checkpoint authorities or threshold checkpoint issuance;
- security after checkpoint authority key compromise;
- arbitrary Byzantine safety or formal consensus;
- physical power-loss durability.
