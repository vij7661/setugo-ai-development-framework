# EXP-O Pilot 13 — Replicated Quorum Authority Under Partition Adjudication

Status: **FINAL FOR THE PRE-REGISTERED PILOT 13 BOUNDARY**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Parent Pilot 12 adjudication commit: `c7c5d9dc05a6483e2def5e9abefe3bc1352f2fff`
- Pilot 13 preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT13-REPLICATED-QUORUM-AUTHORITY-PREREGISTRATION.md`
- Preregistration commit: `1c60158355d07343448da11d66dc862af82dfc96`
- Versioned Pilot 13 implementation commit: `c2a357053dd4b837ad52adfb439b7fbdcf1eef8d`
- Final tested test/implementation commit: `28097710f2108a47570a64705315e1ca2dd2b9a8`
- Main harness run: `34022224085`
- Operational workflow conclusion: `success`
- Remote model/provider calls: **none**
- Experiment type: deterministic three-replica quorum/partition structural falsification

Workflow success is regression/operational evidence only. The Pilot 13 conclusion below is based on independent inspection of the preregistered P13-01 through P13-16 endpoints, the actual implementation path, the exact test executions, and the frozen critical-failure criteria.

## Boundary evaluated

Pilot 13 deliberately advances beyond Pilot 12's single-host SQLite ownership serialization into a deterministic three-replica authority-state simulation with explicit partitions, leadership terms, commit indexes, quorum certificates, trusted lease expiry, and use-time majority revalidation.

The tested boundary requires:

- exactly three frozen authority replicas: `r1`, `r2`, `r3`;
- quorum of two **distinct** replicas;
- monotonically increasing leader terms;
- monotonically increasing quorum commit indexes;
- exact semantic/effect/worker/base/contract/idempotency bindings;
- current quorum confirmation before every consequential execution;
- cached/local authority state and old quorum certificates to remain evidence only, not sufficient use-time authority;
- minority and stale leaders to have zero acquire/renew/takeover/finalize/effect authority;
- loss of the old leader/owner not to justify stealing an unexpired lease;
- exact takeover at/after trusted expiry to advance the lease epoch exactly once;
- stale replicas to remain non-authoritative until catch-up;
- repair to preserve the highest committed term/index and never roll authority state backward;
- an idempotent effect boundary to retain exactly-once authoritative effects across post-effect/pre-finalize ambiguity.

Model output has no authority role in this pilot.

## Independent case adjudication

### P13-01 — Three-member election requires two distinct voters
**PASS.** Duplicate voter identity and single-replica election attempts were rejected. `r1+r2` successfully elected `r1` in term 1. The tested quorum cannot be manufactured by counting the same replica twice.

### P13-02 — Initial exact authority acquisition is quorum committed
**PASS.** Exact authority issuance/acquisition produced identical committed state on the quorum replicas, owner `gateway-a`, lease epoch 1, a common commit index/record digest, and a certificate containing two distinct frozen voter IDs.

### P13-03 — Isolated former leader cannot revalidate consequential use
**PASS.** After partitioning `r1` alone from `r2+r3`, execution through former leader `r1` failed on fresh quorum revalidation as `QUORUM_UNAVAILABLE`. A previously issued certificate did not preserve effective authority and the effect count remained zero.

### P13-04 — Minority former leader cannot renew
**PASS.** Isolated `r1` could not renew the lease. Its local commit index and authority record remained unchanged.

### P13-05 — Minority partition cannot advance term/epoch or mint authority
**PASS.** Single-node election failed, expiry takeover through the minority failed, local term and lease epoch did not advance, and a duplicate-voter certificate shape was rejected.

### P13-06 — Majority partition elects a higher-term leader
**PASS.** The connected `r2+r3` majority elected `r2` in term 2 while isolated `r1` remained on stale term-1 leadership state. The new majority term advanced monotonically.

### P13-07 — New majority leader cannot steal an unexpired old lease
**PASS.** At `lease_expires_at_ms - 1`, exact takeover through the new term-2 majority leader was denied as `AUTHORITY_LIVE_OWNER_UNEXPIRED`. Owner, lease epoch and commit index remained unchanged. Loss of contact with the old leader was not treated as revocation authority.

### P13-08 — Exact expiry allows majority takeover under higher term
**PASS.** At exactly `lease_expires_at_ms`, the exact unchanged request could be quorum-committed by term-2 leader `r2`: ownership moved to `gateway-b`, lease epoch advanced 1 -> 2 exactly once, a fresh trusted expiry was assigned, and the returned certificate was term 2.

### P13-09 — Stale term-1 leader cannot use, renew, finalize, or overwrite after takeover
**PASS.** The isolated stale side could not execute, renew, finalize or elect itself with one vote after the term-2/epoch-2 majority takeover. No effect was produced and stale local authority state did not mutate.

### P13-10 — Stale replica or old certificate cannot be promoted to authoritative use
**PASS.** The stale replica could not provide an authoritative read. Execution through the stale side failed, and even the current majority side rejected the old owner/epoch despite receiving the earlier certificate. The old certificate therefore remained historical evidence rather than effective authority.

### P13-11 — Competing leadership claims cannot both commit authority
**PASS.** The isolated side could not self-elect with one voter. The majority side rejected a changed effect binding without advancing its commit index, then successfully committed only the exact unchanged expiry takeover. No second competing committed authority revision was produced.

### P13-12 — Total quorum loss fails closed
**PASS.** With all three replicas isolated from each other, renew, takeover, finalize, execution and new election attempts all failed closed. No authoritative effect occurred.

### P13-13 — Quorum restoration preserves highest committed term/index
**PASS.** After term-2 takeover, the stale `r1` state had lower term and commit index. On topology repair, catch-up copied the highest committed state; `r1` converged to the current term/index, record digest and lease epoch without rollback.

### P13-14 — Stale replica cannot serve authoritative read until caught up
**PASS.** Immediately after healing topology, stale `r1` was rejected as `STALE_REPLICA_TERM`. After explicit catch-up, the same node could expose the current quorum-confirmed owner `gateway-b` and epoch 2, never the stale owner as authority.

### P13-15 — Effect remains exactly once across leader crash after commit ambiguity
**PASS.** The valid term-2 owner reached the durable idempotent effect boundary once, then the harness injected a post-effect/pre-finalize ambiguity. A different majority subsequently elected `r3` in term 3 from the up-to-date state and retried the exact logical effect. The effect boundary returned replay rather than a second effect, the replicated authority record finalized to `CONSUMED`, term advanced monotonically, and authoritative effect count remained one.

### P13-16 — Fresh clean authority remains live after partition and repair
**PASS.** After partition, higher-term recovery and stale-node catch-up, a fresh independently bound permit could be quorum-issued, acquired and executed exactly once. This positive control shows the tested quorum rules are not blanket denial.

## Critical-failure review

No preregistered critical failure was observed in the tested deterministic state space:

- one replica or duplicate voter IDs did not satisfy quorum;
- minority/stale leadership did not mint or revalidate effective consequential authority;
- stale/cached state did not bypass current-quorum use-time confirmation;
- majority failover did not steal an unexpired lease;
- tested term, lease epoch and commit index transitions did not roll backward;
- competing minority/majority leadership claims did not both commit authority;
- expiry takeover advanced lease epoch exactly once;
- stale owner paths did not renew, finalize or execute after higher-term takeover;
- total quorum loss denied new consequential authority;
- stale state did not overwrite newer state on repair;
- changed effect binding was rejected before takeover commit;
- failover/recovery produced no duplicate authoritative effect;
- fresh liveness remained available.

The implementation additionally binds semantic payload digest, effect digest, idempotency key, worker identity/thumbprint, effect contract and base SHA in each replicated authority record and certificate binding digest. Pilot 13 does not test hostile/Byzantine mutation of the simulation internals themselves.

## Harness evidence

Run `34022224085` checked out exact SHA `28097710f2108a47570a64705315e1ca2dd2b9a8`.

The actual job log explicitly executed and passed all 16 preregistered Pilot 13 tests:

- `test_p13_01_three_member_election_requires_two_distinct_voters`
- `test_p13_02_initial_exact_authority_acquisition_is_quorum_committed`
- `test_p13_03_isolated_former_leader_cannot_revalidate_consequential_use`
- `test_p13_04_minority_former_leader_cannot_renew`
- `test_p13_05_minority_partition_cannot_advance_term_epoch_or_mint_authority`
- `test_p13_06_majority_partition_elects_higher_term_leader`
- `test_p13_07_new_majority_leader_cannot_steal_unexpired_old_lease`
- `test_p13_08_exact_expiry_allows_majority_takeover_under_higher_term`
- `test_p13_09_stale_term_one_leader_cannot_use_renew_finalize_or_overwrite`
- `test_p13_10_stale_replica_or_old_certificate_cannot_be_promoted_to_authoritative_use`
- `test_p13_11_competing_leadership_claims_cannot_both_commit_authority`
- `test_p13_12_total_quorum_loss_fails_closed`
- `test_p13_13_quorum_restoration_preserves_highest_committed_term_and_index`
- `test_p13_14_stale_replica_cannot_serve_authoritative_read_until_caught_up`
- `test_p13_15_effect_remains_exactly_once_across_leader_crash_after_commit_ambiguity`
- `test_p13_16_fresh_clean_authority_remains_live_after_partition_and_repair`

Harness totals at the tested commit:

- scorer: **36 / 36**
- runner: **51 / 51**
- protected truth: **4 / 4**
- observability: **7 / 7**
- continuation: **12 / 12**
- governance: **515 / 515**
- total: **625 / 625**

The first Pilot 13 test execution required no post-result implementation or test repair. The recurring GitHub Actions Node 20-to-24 deprecation warning remains a tooling warning and did not determine the scientific conclusion.

## Final bounded conclusion

**`REPLICATED_QUORUM_AUTHORITY_PASS_16_OF_16 / MINORITY_EFFECTIVE_AUTHORITY_SUCCESS_0 / STALE_LEADER_EFFECTIVE_AUTHORITY_SUCCESS_0 / UNEXPIRED_FAILOVER_LEASE_STEAL_SUCCESS_0 / EXACT_EXPIRY_TAKEOVER_EPOCH_ADVANCE_1_TO_2 / TOTAL_QUORUM_LOSS_NEW_AUTHORITY_SUCCESS_0 / STALE_READ_PROMOTION_SUCCESS_0 / TESTED_TERM_INDEX_EPOCH_ROLLBACK_0 / AUTHORITATIVE_DUPLICATE_EFFECTS_0 / CLEAN_POST_REPAIR_CONTROL_EXECUTED_EXACTLY_ONCE`**

Within the tested deterministic three-replica EXP-O quorum simulation, no minority/stale-leader authority false green was observed. Consequential authority required current majority confirmation, unexpired leases were preserved across majority leader failover, exact-expiry takeover advanced the authority fence monotonically, stale replicas could not be promoted to authoritative use before catch-up, total quorum loss failed closed, and the tested failover/recovery path retained at-most-once authoritative effects while fresh liveness was preserved.

This materially strengthens the architecture beyond Pilot 12's single serialization point **for the tested simulated state transitions only**.

## Important limitations

Pilot 13 does **not** establish production distributed-consensus correctness.

1. The three replicas are deterministic in-memory simulation objects inside one test process, not independent authority-server processes on separate hosts.
2. Topology changes are synchronous harness operations; no real packet loss, delay, duplication, reordering, partial delivery or asynchronous election timing is tested.
3. Election/log-repair rules are purpose-built falsification logic, not a full Raft, Paxos, Viewstamped Replication or equivalent implementation.
4. The simulation assumes non-Byzantine replicas and trusted harness state. Replica compromise, forged internal messages, hostile same-index divergent logs, disk corruption and key theft remain out of scope.
5. One platform-controlled deterministic clock is used. Cross-host clock skew, drift, rollback, NTP compromise and lease-clock uncertainty are not tested.
6. Membership is fixed to `r1/r2/r3`; configuration changes, joint consensus, replica replacement and quorum reconfiguration are not tested.
7. The effect boundary remains a local SQLite idempotency store. A genuinely distributed effect sink and atomic relationship between consensus commit and external side effect are not established.
8. TLS/mTLS workload identity, network authentication, certificate/key rotation, service discovery and real multi-host gateway identity are not tested.
9. Multi-region latency, disaster recovery, prolonged partitions and correlated infrastructure failures remain out of scope.
10. Semantic-verification correctness remains assumed; this pilot tests authority replication/fencing and effect behavior, not whether the semantic judgment itself was substantively correct.
11. No remote model/provider qualification conclusion follows because Pilot 13 made no provider call.

## Next falsification boundary

The next materially different experiment should move the Pilot 13 invariants across a **real process/network boundary**: independent replica processes, authenticated inter-node messages, durable per-node state, and transport fault injection for dropped/delayed/duplicated/reordered messages and leader loss. It should remain explicitly a prototype unless backed by a production consensus substrate; Pilot 13 is not evidence that hand-rolled consensus should be deployed.

## EXP-N isolation

Pilot 13 added and exercised versioned EXP-O-specific paths only. It did not modify or execute the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.