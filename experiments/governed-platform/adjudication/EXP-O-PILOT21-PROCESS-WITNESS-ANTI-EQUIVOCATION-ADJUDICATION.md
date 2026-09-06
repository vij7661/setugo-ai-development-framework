# EXP-O Pilot 21 — Process-Isolated Witness Anti-Equivocation Adjudication

Status: **SCIENTIFICALLY ADJUDICATED — BOUNDED PASS ON TESTED PATHS**

## Frozen lineage

- Preregistration commit: `16c3b81a89a1d18ef926bfa162b85af1dbc9cb67`
- Implementation commit: `7e8ed5b03f76d07e00ca00a569dca6d70dd3bc53`
- Frozen first-execution/test SHA: `1b95b772793c3841b70000a0a8ea4344c92e2630`
- First scientific workflow run: `34026113711`
- First scientific job: `101467261714`
- Workflow conclusion: `success` (operational only)
- Post-result scientific repair before adjudication: **none**

## First-run evidence

The actual first-run job log was inspected. All frozen Pilot 21 tests passed:

- P21-01 through P21-20: **20/20 PASS**
- Governance suite: **671/671 PASS**
- Scorer: 36/36
- Runner: 51/51
- Protected truth: 4/4
- Observability: 7/7
- Continuation: 12/12
- Full harness: **781/781 PASS**

The run checked out the exact frozen SHA `1b95b772793c3841b70000a0a8ea4344c92e2630`.

## Endpoint adjudication

Observed on the exact tested subprocess/HMAC/SQLite path:

1. three configured honest witnesses ran as distinct live child processes with distinct durable SQLite history files;
2. two distinct honest witness processes formed a same-statement 2-of-3 quorum;
3. the coordinator request payload and process arguments did not contain raw witness signing keys;
4. exact same-generation/same-statement replay was idempotent and reused the durable logical signature;
5. an honest witness refused a different statement at an already signed generation;
6. that same-generation anti-equivocation refusal survived process kill/restart using the same durable store;
7. an honest witness refused lower-generation signing after a higher generation was durably recorded;
8. lower-generation refusal survived process restart;
9. higher-generation signing advanced durable maximum generation monotonically;
10. crash after durable signing commit but before response produced transport uncertainty, while restart exact replay recovered the same durable signature without a conflicting history entry;
11. duplicate response from one witness did not count as a second voter;
12. delayed positive response did not mutate a previously failed quorum decision; a new verification attempt was required;
13. reordered individually valid signatures over different statements did not combine into quorum;
14. one conflicting malicious witness did not override two agreeing honest witnesses;
15. one unavailable witness preserved clean liveness when the other two honest witnesses agreed;
16. one unavailable honest witness plus one malicious conflicting witness did not form a conflicting quorum;
17. threshold-valid old process signatures below the separately trusted minimum generation were rejected as rollback;
18. coherent local DB rewrite/reseal plus one malicious re-signing did not validate rewritten state against the old honest quorum root;
19. repeated witness restarts did not erase same-generation or lower-generation refusal memory;
20. a clean higher-generation 2-of-3 quorum over consumed state recovered as consumed with exactly one local durable effect.

Primary endpoint failures observed: **0**.

## Result

`NO_TESTED_PROCESS_RESTART_EQUIVOCATION_ROLLBACK_DUPLICATE_DELAY_REORDER_OR_SINGLE_MALICIOUS_WITNESS_PATH_BYPASSED_DURABLE_TWO_OF_THREE_WITNESS_AUTHORITY_BOUNDARY`

A permitted concise interpretation is:

> No tested process-restart, same-generation equivocation, lower-generation rollback, duplicate/delayed/reordered transport, single-malicious-witness, or old-valid-quorum attack bypassed the durable 2-of-3 witness boundary in this Pilot 21 prototype.

This is **not** evidence of universal Byzantine safety, production key-custody security, or correctness under arbitrary distributed-system failures.

## Non-endpoint observation retained from first run

The job emitted Python `ResourceWarning` messages for unclosed subprocess stdio pipe objects during test cleanup. These warnings did not change any P21 decision, durable witness history, quorum result, process restart result, or harness conclusion. They are classified as implementation-hygiene debt, not a scientific endpoint failure. The frozen first-run evidence is retained unchanged; any later cleanup fix must not be represented as part of the first-run scientific result.

## Frozen limitations

This pass does not prove:

- production HSM/KMS or secret custody;
- administrative, geographic, or cloud-provider independence;
- security after compromise of two threshold witness keys;
- correctness under arbitrary asynchronous partitions;
- global transparency/gossip detection of equivocation;
- formal Byzantine consensus;
- physical power-loss durability;
- kernel/filesystem correctness for witness SQLite stores;
- resistance to coherent tampering or rollback of an honest witness's own SQLite signing-history store when the adversary can rewrite that store;
- exactly-once semantics for arbitrary external non-idempotent systems.

The next falsification boundary should therefore attack **witness durable-store integrity and rollback itself**, rather than repeating coordinator-level quorum cases.
