# EXP-O Pilot 22 — Witness Durable-Store Integrity and Rollback Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 22 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT21-PROCESS-WITNESS-ANTI-EQUIVOCATION-ADJUDICATION.md`

Parent adjudication commit:

`c5477e22570e69cde9c3eac5e1f1e47f088264fe`

## Motivation

Pilot 21 demonstrated, on the tested subprocess path, that honest witnesses durably remembered signed generations across normal process restart and refused same-generation equivocation and lower-generation rollback. However, the witness SQLite history itself remained inside the trust boundary. If an adversary can delete, truncate, rewrite, or coherently roll back that durable history, an honest restarted process could otherwise forget a prior signature and sign a conflicting or lower-generation statement.

Pilot 22 therefore moves integrity enforcement onto each witness durable store. A witness may not sign merely because its SQLite file opens. Before serving a signing request, its history must pass structural integrity, application-level seal verification, monotonic-history validation, and comparison to an externally supplied authenticated witness-history checkpoint held outside the mutable witness SQLite file.

## Scientific hypothesis

Across the frozen Pilot 22 cases:

1. structural SQLite corruption is detected before signing;
2. application-row mutation that leaves SQLite structurally valid is detected before signing;
3. deletion or truncation of signed history is not interpreted as clean absence;
4. coherent rewrite with recomputed local seals is detected by the external authenticated history checkpoint;
5. rollback to an older otherwise valid witness database is rejected when below the externally trusted witness generation/history root;
6. startup from a stale witness store fails closed rather than resetting durable anti-equivocation memory;
7. local metadata lowering cannot reduce the effective trusted maximum generation;
8. an attacker controlling only one witness store cannot manufacture a conflicting 2-of-3 authority quorum;
9. clean current witness stores remain live;
10. clean higher-generation signing advances both durable history and the externally anchored witness-history generation/root in the tested prototype.

Any tested path where witness-store tampering causes an honest witness to sign a previously refused same-generation conflict, sign below the externally trusted maximum generation, or contribute to sub-threshold/conflicting quorum falsifies Pilot 22 on that path.

## Frozen architecture under test

Pilot 22 must use new isolated files and must not modify Pilots 14–21 scientific test files or adjudications.

Each honest witness must have:

- its own subprocess identity and signing key as in Pilot 21;
- its own SQLite durable signing-history file;
- application-level row seals over signed statement history and monotonic metadata;
- a deterministic canonical logical history root;
- an authenticated external witness-history checkpoint that is not stored inside the same mutable SQLite database;
- checkpoint binding to witness id, key id, store identity, maximum signed generation, logical history root, and checkpoint generation;
- an externally supplied trusted minimum checkpoint generation;
- fail-closed startup/signing when local structural integrity, row seals, monotonic consistency, checkpoint authentication, checkpoint generation, witness/store scope, or history root do not verify.

The bounded prototype may use HMAC-SHA256 fixture keys and files outside the witness SQLite path. It does not claim HSM/KMS, administrative-domain, or physical-storage independence.

## Threat model

The adversarial harness may:

- mutate, delete, truncate, replace, or copy a witness SQLite database;
- alter authority-history rows and recompute local row seals;
- lower or delete local maximum-generation metadata;
- substitute an older valid witness DB snapshot;
- remove or corrupt WAL/main-file components where applicable;
- replay an older valid external witness-history checkpoint;
- forge a checkpoint with the wrong key;
- mismatch checkpoint witness/store identity;
- restart the witness repeatedly after tampering;
- fully control one designated malicious witness and its store/key;
- combine stale honest signatures with one malicious current signature.

The adversary may not possess two honest witness signing keys simultaneously or alter the separately supplied trusted minimum witness-checkpoint generation.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must exist before first scientific execution.

### P22-01 — clean sealed witness-store control
Expected: current sealed witness history plus current authenticated external history checkpoint allows clean exact replay/signing behavior.

### P22-02 — witness SQLite header corruption
Expected: witness refuses startup/signing; corruption is not treated as empty history.

### P22-03 — witness SQLite truncation
Expected: witness refuses startup/signing.

### P22-04 — signed-history row byte/payload mutation with structurally valid SQLite
Expected: application seal mismatch blocks signing.

### P22-05 — maximum-generation metadata lowered without matching history rewrite
Expected: monotonic inconsistency blocks signing.

### P22-06 — signed-history row deletion
Expected: missing previously anchored history is detected; witness does not forget the signature.

### P22-07 — coherent history rewrite plus recomputed local seals
Expected: external authenticated history root mismatch blocks signing.

### P22-08 — stale older valid witness DB substituted below current external checkpoint
Expected: rollback blocked before signing.

### P22-09 — stale DB plus replayed old valid external checkpoint below trusted minimum checkpoint generation
Expected: rollback blocked despite internally consistent old bundle.

### P22-10 — external checkpoint authentication tag mutation
Expected: checkpoint authentication failure blocks signing.

### P22-11 — forged external checkpoint signed with wrong key
Expected: authentication failure blocks signing.

### P22-12 — external checkpoint bound to wrong witness id/key id/store identity
Expected: scope substitution blocks signing.

### P22-13 — local metadata and history both lowered and resealed coherently
Expected: external checkpoint/root/minimum generation prevents forgotten higher history.

### P22-14 — same-generation conflicting statement after coherent local rollback attempt
Expected: honest witness still refuses; tampered store cannot erase prior anti-equivocation memory.

### P22-15 — lower-generation request after coherent local rollback attempt
Expected: honest witness still refuses below externally trusted maximum.

### P22-16 — repeated restart on corrupted/stale witness store
Expected: repeated restarts never convert integrity failure into a signing success.

### P22-17 — one tampered honest witness store plus one malicious witness
Expected: no conflicting 2-of-3 quorum can be formed from the compromised/tampered minority path.

### P22-18 — one witness store unavailable/corrupt, remaining two honest current stores agree
Expected: clean 2-of-3 liveness succeeds through the two intact honest witnesses.

### P22-19 — crash after current history commit but before external checkpoint publication
Expected: ambiguous intermediate state fails closed until checkpoint reconciliation; it must not silently sign past the unanchored history transition.

### P22-20 — clean higher-generation history + checkpoint liveness control
Expected: clean higher-generation statement is durably recorded, externally checkpointed, survives restart, and contributes to a valid current 2-of-3 quorum without duplicate effect.

## Primary endpoints

1. witness-store corruption false-clean rate;
2. local-seal bypass rate;
3. coherent-rewrite external-root bypass rate;
4. stale-store rollback acceptance rate;
5. old-valid-checkpoint rollback acceptance rate;
6. post-tamper same-generation equivocation sign rate;
7. post-tamper lower-generation sign rate;
8. repeated-restart fail-open rate;
9. single-tampered-witness conflicting-quorum acceptance rate;
10. intact-two-witness liveness;
11. uncheckpointed-postcommit fail-open rate;
12. clean higher-generation checkpointed liveness.

Any non-zero false-clean corruption result, coherent rollback acceptance, honest equivocation signing, honest lower-generation signing, or sub-threshold conflicting quorum is a Pilot 22 falsification on the exact tested path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- fault cases must mutate real witness SQLite/checkpoint artifacts, not only mock status flags;
- structurally valid coherent rewrites must recompute local seals where the case says so;
- rollback cases must retain the actual old DB/checkpoint generations and roots used;
- restart cases must prove reuse of the same tampered/stale store path with a new process id;
- P22-19 must retain pre-crash history state and external-checkpoint state separately;
- first-run failures are retained exactly;
- no case may be removed, renamed, weakened, or converted after first execution;
- any post-result repair requires explicit diagnosis and rerun lineage;
- workflow SUCCESS is operational evidence only; scientific adjudication reads each P22 result.

## Isolation

Pilot 22 must not modify:

- Pilots 14–21 scientific runtime/tests/adjudications;
- frozen EXP-N Pilot 8/9 provider paths.

## Frozen limitations

Even a complete Pilot 22 pass will not prove:

- HSM/KMS or production secret custody;
- truly independent administrative or physical checkpoint storage;
- security after compromise of two threshold witnesses;
- resistance to an attacker that can alter both the witness DB and the separately trusted minimum/checkpoint authority;
- arbitrary Byzantine consensus safety;
- physical power-loss guarantees;
- kernel/filesystem correctness;
- global transparency/gossip detection;
- exactly-once semantics for arbitrary external non-idempotent systems.

Allowed conclusions must remain limited to the exact witness-store corruption, rollback, local-seal, external-checkpoint, restart, and 2-of-3 paths exercised by this pilot.
