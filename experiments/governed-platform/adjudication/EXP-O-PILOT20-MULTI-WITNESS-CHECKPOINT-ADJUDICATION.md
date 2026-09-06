# EXP-O Pilot 20 — Multi-Witness Authenticated Checkpoint Adjudication

Status: **SCIENTIFICALLY ADJUDICATED — BOUNDED PASS ON THE TESTED 2-OF-3 WITNESS VERIFICATION BOUNDARY**

## Frozen lineage

- preregistration commit: `c8827da5a0a9223172af6da46520aa4719dfd0da`
- isolated implementation commit: `de8c44a2cc49288ce2531a2f6c94eaa5b21f07c1`
- first-execution / frozen twenty-case suite SHA: `0ca15b70ef58e5ad9ffb5f726cae3818308cba02`
- first scientific workflow run: `34025770714`
- validation job: `101466344283`
- first-run operational conclusion: SUCCESS
- post-result repair before adjudication: **none**

Scientific adjudication below is based on the individual frozen P20 case outcomes and the actual first-run job log, not on workflow SUCCESS alone.

## First-run evidence

The first-run job log at frozen SHA `0ca15b70ef58e5ad9ffb5f726cae3818308cba02` directly records:

- P20-01 through P20-20: **20/20 PASS**
- governance/falsification suite: **651/651 PASS**
- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation: 12/12
- total full harness: **761/761 PASS**

No Pilot 20 case was removed, renamed, weakened, or repaired after observing the first scientific run.

## Endpoint adjudication

Across the exact frozen Pilot 20 cases:

- sub-threshold authority promotion: **0 observed**
- duplicate same-witness quorum manufacture: **0 observed**
- one honest + forged second-witness quorum acceptance: **0 observed**
- single compromised witness conflicting-root acceptance: **0 observed**
- mixed-root witness acceptance: **0 observed**
- mixed-generation witness acceptance: **0 observed**
- mixed-scope witness acceptance: **0 observed**
- old valid 2-of-3 quorum rollback below trusted minimum generation: **0 accepted**
- stale DB + valid old quorum promotion: **0 observed**
- coherent DB rewrite with only one compromised witness re-signing: **0 observed**
- coherent DB rewrite with retained old honest quorum: **0 observed**
- unknown witness vote acceptance: **0 observed**
- revoked witness vote acceptance: **0 observed**
- witness identity/key substitution acceptance: **0 observed**
- repeated one-witness forged/conflicting bundle eventual promotion: **0 observed**
- clean 2-of-3 liveness with one witness unavailable: **PASS**
- clean higher-generation quorum liveness: **PASS**
- P20-20 durable local effect count after clean higher-generation consume/recovery: **exactly one**

P20-09 also demonstrated the intended minority-conflict behavior on the tested path: two honest witnesses agreeing on the exact canonical statement established the quorum while one conflicting valid witness did not alter the accepted statement.

## Scientific result

`NO_TESTED_SUBTHRESHOLD_DUPLICATE_COMPROMISED_SINGLE_WITNESS_OR_MIXED_STATEMENT_BUNDLE_BYPASSED_TWO_OF_THREE_CHECKPOINT_QUORUM`

Supported summary:

> No tested sub-threshold, duplicated-witness, single-compromised-witness, mixed-statement, revoked/unknown witness, key-substitution, or old-quorum replay bypassed the frozen 2-of-3 checkpoint verifier.

## Architectural implication

Pilot 20 strengthens the external integrity boundary by removing the single-signer acceptance condition tested in Pilot 19. On the frozen prototype, effective authority required two distinct currently trusted witness identities to authenticate the exact same canonical checkpoint statement, while a separately trusted minimum generation still supplied freshness/rollback protection.

The result also preserves an important distinction: cryptographic witness thresholding does not prove operational witness independence. In this pilot, witness independence is represented by distinct identities and keys, not by separately administered hosts, processes, networks, KMS/HSM boundaries, or failure domains.

## What this result does not establish

Pilot 20 does **not** prove:

- production HSM/KMS or key-custody correctness;
- security after compromise of two threshold witnesses;
- actual administrative/failure-domain independence of witnesses;
- process or host isolation of witness signing keys;
- durable anti-equivocation memory at each witness;
- resistance to a witness that signs two conflicting statements at the same generation unless the verifier happens to observe both;
- asynchronous distributed consensus or partition-tolerant liveness;
- remote transport authentication or replay handling between coordinator and witnesses;
- transparency-log or external witness-audit correctness;
- formal Byzantine fault tolerance;
- physical power-loss/storage durability;
- exactly-once semantics for arbitrary external non-idempotent services.

HMAC-SHA256 and in-process witness keys remain bounded prototype mechanisms only.

## Next distinct falsification boundary

The next scientific gap is **actual witness process and durability isolation plus anti-equivocation behavior**. A stronger next pilot should place each witness in a separate process with only its own signing key and its own durable monotonic statement log; require the witness to refuse lower-generation signing and refuse a second conflicting statement at the same generation; then test process kill/restart, unavailable witnesses, duplicate/reordered transport, one malicious witness, and 2-of-3 liveness without exposing signer keys to the coordinator.
