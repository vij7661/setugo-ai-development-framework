# EXP-O Pilot 15 — Storage Crash Consistency / Durable Authority Adjudication

Status: **ADJUDICATED — PASS WITH BOUNDED DETERMINISTIC-DURABILITY CLAIM**

A green workflow conclusion is operational evidence only. This adjudication is based on the preregistered storage model, the exact twenty frozen falsifiers, inspection of the first scientific-run job log, and the exercised recovery outcomes.

## Frozen lineage

Preregistration:

`experiments/governed-platform/adjudication/EXP-O-PILOT15-STORAGE-CRASH-CONSISTENCY-PREREGISTRATION.md`

Preregistration commit:

`72cb17eafbe638af6153535e34ef523cf4c1ca92`

Parent Pilot 14 adjudication commit:

`c58e3bf9d63ca54b50532fd2b58c49280e8c599a`

Pilot 15 isolated implementation:

`experiments/governed-platform/governance/storage_crash_consistency_exp_o.py`

Initial implementation commit:

`822d463997a580ee7785e6a69e97d3e9ffe9c4af`

Before any Pilot 15 test execution, independent code review found that a durable effect-ledger row with missing journal evidence could otherwise leave earlier checkpointed authority recoverable. That pre-execution gap was closed at:

`df6843b216d60af4b4535b3a809a4914ff6f020b`

No Pilot 15 result had been observed at that point.

The exact twenty-case falsification suite was then frozen at:

`03d6ad14fc44ac23ffd2337f1e286e0e52311a5a`

No Pilot 15 case was removed, renamed, weakened, or modified after first scientific execution.

## Frozen prototype boundary

The exercised isolated prototype contains:

- append-only newline-framed canonical JSON journal records;
- monotonically increasing sequence numbers;
- SHA-256 record digests;
- previous-record digest chaining;
- explicit process-model durable-sequence marker;
- durable checkpoint sequence + digest binding;
- independent external higher-fence anchor used by the stale-substitution falsifier;
- independent deterministic effect ledger keyed by idempotency identity;
- exact idempotency-key/effect-digest rebinding denial;
- restart recovery that validates integrity before reconstructing authority;
- fail-closed recovery for corruption or ambiguous durable ordering;
- no model-visible authority and no model-issued recovery authority.

The registered crash points remain exactly those in the preregistration.

## First scientific execution

GitHub Actions workflow run:

`34024368643`

Job:

`101462597735`

Exact checkout SHA:

`03d6ad14fc44ac23ffd2337f1e286e0e52311a5a`

Observed Pilot 15 results:

- P15-01 clean durable authority control — PASS
- P15-02 authority write lost before fsync — PASS
- P15-03 authority fsynced but checkpoint not advanced — PASS
- P15-04 torn final authority frame — PASS
- P15-05 parseable record with invalid digest — PASS
- P15-06 broken previous-digest chain — PASS
- P15-07 checkpoint beyond validated prefix — PASS
- P15-08 checkpoint digest mismatch — PASS
- P15-09 duplicate sequence with conflicting content — PASS
- P15-10 stale lower snapshot substituted after higher anchored fence — PASS
- P15-11 takeover-fence write lost before fsync — PASS
- P15-12 durable takeover fence before checkpoint — PASS
- P15-13 effect commits before evidence write — PASS
- P15-14 effect evidence written but not durable — PASS
- P15-15 durable effect evidence before consumed authority — PASS
- P15-16 consumed record written but not durable — PASS
- P15-17 consumed record durable before checkpoint — PASS
- P15-18 effect-ledger idempotency rebinding corruption — PASS
- P15-19 consumed record references missing effect identity — PASS
- P15-20 clean restart / exactly-once positive control — PASS

Regression totals from the same job:

- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation authority: 12/12
- governance/falsification: 553/553
- total: **663/663**

There was no first-run Pilot 15 failure requiring diagnosis or repair.

## Independent endpoint adjudication

### Authority resurrection

**PASS on tested paths.**

No preregistered non-durable, torn, checksum-invalid, chain-invalid, checkpoint-invalid, stale-snapshot, or ambiguous durable state produced effective consequential authority contrary to the frozen expectation.

Notably:

- a pre-fsync authority record is removed by simulated power loss and does not become authority;
- an fsynced authority transition ahead of checkpoint is not silently promoted to consequential authority;
- stale lower authority cannot replace an independently anchored higher fence;
- a durable higher takeover fence ahead of checkpoint blocks stale-owner execution rather than rolling back for liveness.

Observed authority-resurrection events: **0/20 cases**.

### Corruption / ambiguity promotion

**PASS on tested paths.**

The exercised torn frame, record-digest mismatch, previous-digest break, checkpoint-beyond-prefix, checkpoint-digest mismatch, conflicting sequence, stale anchored rollback, effect-ledger rebinding corruption, and missing effect identity all fail closed or require reconciliation.

No exercised corruption was treated as clean authoritative success.

Observed silent ambiguity promotions: **0/20 cases**.

### Exactly-once effect boundary

**PASS on tested paths.**

When the deterministic effect ledger contains the original `(idempotency_key, effect_digest)` identity:

- missing post-effect journal evidence does not authorize a blind second effect;
- non-durable effect-evidence loss does not cause re-execution;
- durable evidence with missing consumed record converges to the original result identity;
- non-durable or checkpoint-lagged consumed records do not reopen the effect;
- a different effect digest for the same idempotency key is denied as rebinding;
- the clean restart control returns the same durable result identity without a second effect.

Observed duplicate durable effects for one logical intent: **0**.

### Monotonic fence preservation

**PASS on tested paths.**

The independently anchored higher term/index/lease-epoch fence prevents the stale lower journal/checkpoint substitution case from reviving the prior owner. The durable-takeover/checkpoint-lag case also fails toward reconciliation rather than choosing the lower checkpoint for convenience.

### Clean recovery liveness

**PASS on tested controls.**

A fully durable authority checkpoint survives restart as authoritative state in P15-01. A fully durable authority/effect/evidence/consumed sequence in P15-20 recovers the original effect identity and remains exactly-once.

## Scientific result

**Result:**

`NO_TESTED_DETERMINISTIC_STORAGE_CRASH_OR_CORRUPTION_PATH_RESURRECTED_AUTHORITY_OR_DUPLICATED_EFFECT_WITH_FAIL_CLOSED_AMBIGUITY_RECOVERY`

Within the exact deterministic EXP-O Pilot 15 durability prototype and the twenty preregistered cases, no tested crash cut, non-durable-tail loss, torn/corrupt journal state, invalid checkpoint, stale anchored snapshot substitution, incomplete effect evidence, consumed-state gap, or idempotency rebinding condition manufactured effective consequential authority or a second durable effect for the same logical intent.

The clean durable controls remained recoverable.

## Important limitations

This result does **not** establish production crash consistency or general exactly-once semantics.

It does not prove:

- actual hardware power-loss behavior;
- drive-controller write-cache or barrier semantics;
- directory-fsync / rename durability guarantees across filesystems;
- sector atomicity assumptions;
- kernel, hypervisor, container-runtime, or cloud-volume correctness;
- SQLite's complete production crash-consistency behavior;
- multi-host consensus or distributed transaction correctness;
- Byzantine storage, malicious administrator, rollback-device, or compromised-kernel resistance;
- exactly-once semantics for arbitrary non-idempotent external services;
- correctness under every possible crash interleaving beyond the named registered cuts.

The prototype's `durable` marker is part of the deterministic falsification model. A successful `os.fsync()` call in CI is not evidence that real hardware has survived power loss.

## Next boundary

The next distinct falsification step should cross from deterministic local durability into a stronger storage boundary rather than adding more synthetic variants to this same model. Candidate Pilot 16 scope: subprocess termination around actual SQLite WAL/transaction boundaries plus directory/file reopen and independently retained rollback anchors, while still avoiding claims about physical power-loss hardware semantics.
