# EXP-O Pilot 18 — SQLite Storage-Fault / Corruption Recovery Adjudication

Status: **SCIENTIFICALLY ADJUDICATED — BOUNDED PASS ON THE TESTED SOFTWARE-LEVEL STORAGE FAULTS**

## Frozen lineage

- preregistration commit: `ee76be4f64b2c60736bfbee46f86ca24d52af22f`
- isolated storage-fault harness commit: `ab0f75f0f070146f33b338bf64774faaf916ca8d`
- pre-execution row-seal hardening commit: `8326096384fdb1ed7974828329d8836ce9c149a7`
- first-execution / frozen 20-case suite SHA: `26b4c036601f38ddbad5240fd40c3ad171423fe3`
- first scientific workflow run: `34025419894`
- validation job: `101465403149`
- first-run conclusion: operational SUCCESS; scientific conclusion determined from the individual P18 assertions below
- post-result repair before adjudication: **none**

The row-seal hardening was committed before the twenty-case test suite and before first scientific execution. It was added because SQLite structural integrity checks alone cannot detect every payload-byte mutation that leaves B-tree structure valid.

## First-run evidence

The job log at frozen SHA `26b4c036601f38ddbad5240fd40c3ad171423fe3` directly records:

- P18-01 through P18-20: **20/20 PASS**
- governance/falsification suite: **611/611 PASS**
- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation: 12/12
- total full harness: **721/721 PASS**

No case was removed, renamed, weakened, or repaired after observing first-run results.

## Endpoint adjudication

Across the exact frozen Pilot 18 cases:

- storage-fault-induced stale authority resurrection: **0 observed**
- independently anchored fence rollback: **0 observed**
- duplicate durable effects after the tested fault/recovery paths: **0 observed**
- silent storage-corruption-as-clean-absence promotion: **0 observed**
- accepted idempotency/effect rebinding after tested corruption: **0 observed**
- clean recovery/execution liveness control: **PASS**

The database-full cases observed actual SQLite errors containing `full`, rolled their target transactions back, and did not promote failed authority/takeover/effect writes.

The corruption cases exercised main-database header corruption, truncation, authority-bearing payload mutation, monotonic metadata mutation, effect-state corruption/deletion, duplicate active authority state, WAL removal/truncation/byte mutation, and stale/unrelated database-WAL pairings. Recovery remained non-authorizing whenever structural integrity, row seals, relational state, or independent fence evidence could not establish a trustworthy state.

## Scientific result

`NO_TESTED_SOFTWARE_LEVEL_SQLITE_STORAGE_FAULT_RESURRECTED_STALE_AUTHORITY_ROLLED_BACK_ANCHORED_FENCE_OR_DUPLICATED_EFFECT`

A supported summary is:

> No authority resurrection, anchored rollback, duplicate effect, or silent corruption-as-clean promotion was observed across the twenty preregistered software-level SQLite storage-fault/corruption cases.

## What this result does not establish

This is not evidence that SQLite, the host filesystem, or the physical storage stack is universally crash safe. Pilot 18 does **not** prove:

- real power-loss durability;
- physical drive/controller/cache/barrier correctness;
- sector atomicity;
- kernel panic or VM/host failure behavior;
- every SQLite corruption or WAL recovery interleaving;
- correctness across all SQLite builds, filesystems, or operating systems;
- multi-host database or distributed transaction correctness;
- Byzantine storage/admin resistance;
- that in-database row seals are an independent trust anchor;
- exactly-once semantics for arbitrary non-idempotent external services;
- formal linearizability/serializability beyond the exact tested operations.

## Important architectural implication

Pilot 18 also exposes the next trust-boundary question: the application row seals used here are stored in the same SQLite trust domain. They detect accidental/isolated mutations in the tested cases, but a sufficiently privileged actor that can coherently rewrite both state and its local seals could defeat that evidence.

The next distinct falsification boundary should therefore move the integrity root outside the database/storage-admin trust domain and test rollback, seal substitution, equivocation, and coherent state+seal forgery against an independently retained authenticated checkpoint.
