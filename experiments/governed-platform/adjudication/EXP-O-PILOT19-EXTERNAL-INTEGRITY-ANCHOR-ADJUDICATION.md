# EXP-O Pilot 19 — External Authenticated Integrity Anchor Adjudication

Status: **SCIENTIFICALLY ADJUDICATED — BOUNDED PASS ON THE TESTED EXTERNAL-INTEGRITY BOUNDARY**

## Frozen lineage

- preregistration commit: `bfc4d000e17ef029e40a993334e199f5537df4d8`
- isolated implementation commit: `bce990e1278c44c42aa7ac000993cc5543e8cc2b`
- first-execution / frozen twenty-case suite SHA: `53d695ee2452bd96f1448aadbb2a0ea39ac23f4b`
- first scientific workflow run: `34025629240`
- validation job: `101465963880`
- first-run operational conclusion: SUCCESS
- post-result repair before adjudication: **none**

Scientific adjudication below is based on the individual frozen case results, not on workflow SUCCESS alone.

## First-run evidence

The first-run job log at frozen SHA `53d695ee2452bd96f1448aadbb2a0ea39ac23f4b` directly records:

- P19-01 through P19-20: **20/20 PASS**
- governance/falsification suite: **631/631 PASS**
- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation: 12/12
- total full harness: **741/741 PASS**

No Pilot 19 case was removed, renamed, weakened, or repaired after observing the first scientific run.

## Endpoint adjudication

Across the exact frozen Pilot 19 cases:

- coherent DB-state + recomputed-local-seal authority promotion: **0 observed**
- forged/wrong-key checkpoint acceptance: **0 observed**
- modified authentication-tag acceptance: **0 observed**
- valid-old-checkpoint rollback below trusted minimum generation: **0 accepted**
- stale DB + stale seals + valid old checkpoint promotion: **0 observed**
- cross-lineage database/checkpoint substitution acceptance: **0 observed**
- consumed-authority resurrection after coherent local rewrite: **0 observed**
- semantic/idempotency/effect-history coherent rewrite acceptance: **0 observed**
- wrong project/task checkpoint scope acceptance: **0 observed**
- missing or unknown-key checkpoint fail-open: **0 observed**
- repeated forged-bundle retry eventual promotion: **0 observed**
- clean higher-generation liveness control: **PASS**

The important causal distinction from Pilot 18 is that multiple Pilot 19 attacks deliberately recomputed the in-database local integrity seals after tampering. Local verification therefore became internally clean, yet the unchanged external authenticated state root rejected the rewritten logical state.

The valid-old-checkpoint cases also showed that authentication alone is insufficient for rollback resistance: a separately trusted minimum generation was required and blocked old-but-valid evidence.

## Scientific result

`NO_TESTED_COHERENT_LOCAL_STATE_REWRITE_FORGED_CHECKPOINT_OR_VALID_OLD_CHECKPOINT_REPLAY_BYPASSED_EXTERNAL_INTEGRITY_BOUNDARY`

Supported summary:

> No tested coherent local-state rewrite, forged checkpoint, or valid-old-checkpoint rollback bypassed the externally authenticated integrity boundary in the frozen Pilot 19 cases.

## Architectural implication

Pilot 19 supports separating integrity authority from the database/storage-admin trust domain. A local database may prove internal consistency while still being untrustworthy relative to a separately retained authenticated root.

It also establishes a second independent requirement: checkpoint authenticity does not by itself provide freshness. The verifier needs a monotonic freshness/fencing source outside the replayable checkpoint bundle.

## What this result does not establish

Pilot 19 does **not** prove:

- production HSM/KMS correctness or secret-key custody;
- security if the single trusted checkpoint signer/key is compromised;
- security if the verifier and trusted minimum-generation source are compromised together;
- resistance to a legitimate signer equivocating by signing two conflicting roots at the same generation;
- remote transparency-log or witness correctness;
- distributed checkpoint-publication consensus;
- physical disk/power-loss durability;
- formal Byzantine fault tolerance;
- every rollback/equivocation strategy;
- exactly-once behavior for arbitrary external non-idempotent systems.

HMAC-SHA256 here is a bounded prototype mechanism, not a production key-management claim.

## Next distinct falsification boundary

The remaining central trust concentration is the **single external checkpoint signer/freshness authority**. The next pilot should test a multi-witness checkpoint boundary in which one compromised or equivocating witness cannot independently validate a conflicting root, while a threshold of independently keyed witnesses can advance a clean checkpoint.
