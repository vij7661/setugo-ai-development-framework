# EXP-I Pilot 15 — Root-Rotation Crash Consistency and Recovery

Status: **PREREGISTERED / IMPLEMENTATION NOT YET EXPOSED**

Parent: EXP-I Pilot 14 `BOUNDED_PASS`.

## Scientific question

Can the platform fail closed and recover deterministically when the process coordinating root-key rotation is externally terminated at real process boundaries between durable root-trust history mutation and advancement of the separate trusted-minimum authority, without resurrecting a revoked root, duplicating a transition, or losing clean higher-root liveness?

## Frozen authority model

- Root signer processes own their own Ed25519 private keys.
- Platform root-trust authority mutates append-only root-trust history.
- Trusted-minimum authority is a separate durable authority and is not writable by a root signer or reviewer/model.
- Root-trust history mutation and trusted-minimum advancement remain separate durable operations for this pilot; the experiment must test the ambiguity instead of pretending cross-store atomicity.
- Parent test process performs external termination. Child must not self-terminate, catch the kill, rely on `finally`, or perform graceful cleanup to satisfy an endpoint.
- Recovery is evaluated from a fresh process/connection after termination.

## Frozen termination boundaries

1. Before root-trust transaction begins.
2. After root-trust transaction begins but before new root record insert.
3. After new root record insert but before root-trust commit.
4. Immediately after root-trust commit but before trusted-minimum advancement.
5. After trusted-minimum transaction begins but before its update/insert.
6. After trusted-minimum update/insert but before commit.
7. Immediately after trusted-minimum commit but before acknowledgement.

Parent-observed readiness must identify the exact boundary reached before external termination.

## Frozen falsification vectors

- **P15-01** — Parent/child readiness proves a distinct externally terminated rotation worker.
- **P15-02** — Kill before root transaction leaves R1 current and creates no false R2.
- **P15-03** — Kill after root transaction begins but before insert leaves no partial R2 record.
- **P15-04** — Kill after R2 insert before root commit rolls back R2 on fresh reopen.
- **P15-05** — Kill after durable R2 root commit before minimum advance is treated as ambiguous/non-current for consequential use until reconciliation; R1 must not regain new-issuance authority merely because the minimum is stale.
- **P15-06** — Recovery of exact durable R2 transition advances the independent minimum exactly once and yields current R2.
- **P15-07** — Kill after minimum transaction begins before mutation preserves the pre-advance minimum and remains fail closed against ambiguous R2.
- **P15-08** — Kill after minimum mutation before commit rolls the minimum transaction back and remains fail closed until exact reconciliation.
- **P15-09** — Kill after minimum commit before acknowledgement replays the same R2 transition/minimum idempotently; no R3 or duplicate R2 is minted.
- **P15-10** — Same transition identity with changed R2 public key or activation semantics is denied after any killed/recovered path.
- **P15-11** — A stale pre-rotation root-store snapshot cannot restore R1 after the trusted minimum has advanced to R2.
- **P15-12** — An R1 signer cannot mint new currently eligible registry state once a durable R2 root record exists, even during pre-minimum reconciliation ambiguity.
- **P15-13** — Two recovery workers racing the same ambiguous R2 transition cannot produce divergent minimum bindings or duplicate root epochs.
- **P15-14** — Restart/reopen repeatedly preserves the highest reconciled root epoch/digest and never converts ambiguity into implicit success.
- **P15-15** — Models, reviewers, registry writers, and root signers retain zero authority to self-resolve ambiguous root state, mutate the trusted minimum, release, or deploy.
- **P15-16** — Clean R2→R3 rotation remains live after all crash/recovery vectors and advances the minimum to the exact R3 record.

## Frozen acceptance rule

A scientific pass requires all P15-01…P15-16 to reach their intended endpoints plus the complete governed-platform regression suite. Workflow success alone is not sufficient.

A crash state is not accepted merely because one store contains a newer record. Consequential current-root use must be justified by a reconciled pair: authenticated root history plus matching trusted-minimum epoch/digest.

Exact replay may repair a valid incomplete transition only when semantic identity, predecessor, root epoch, root ID, public-key fingerprint, and activation binding match the durable record exactly.

## Forbidden repair strategies after first exposure

- weakening any frozen expected outcome;
- turning fail-closed ambiguity into implicit liveness;
- allowing R1 to remain eligible after durable R2 history exists;
- merging the two authorities into one store solely to make the experiment pass;
- replacing external process termination with raised exceptions or graceful shutdown hooks;
- granting model/reviewer/root-signer authority to mutate root trust or minimum state.

## Bounded claim if passed

Pass would show only that the tested same-host SQLite/process prototype handles the preregistered abrupt-termination boundaries and two-store reconciliation rules. It would not prove physical power-loss durability, distributed transaction atomicity, HSM/KMS nonextractability, independent administrative domains, Byzantine consensus, or production/release authority.
