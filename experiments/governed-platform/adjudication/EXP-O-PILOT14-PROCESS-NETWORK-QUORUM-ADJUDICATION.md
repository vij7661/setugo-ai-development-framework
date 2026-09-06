# EXP-O Pilot 14 — Process / Network Quorum Adjudication

Status: **ADJUDICATED — PASS WITH BOUNDED CLAIM AND RECORDED OPERATIONAL LIVENESS LIMITATION**

This adjudication is based on the frozen preregistration, the original sixteen process/network falsifiers, the post-first-run coverage-hardening preregistration and supplemental falsifiers, the preserved same-SHA liveness failures, the preregistered transport-stability amendment, and two consecutive complete stabilized executions at the exact same SHA.

A green workflow conclusion is not itself the scientific verdict. The verdict below comes from independent review of the specific exercised endpoints and retained failure evidence.

## Frozen design and evidence lineage

Primary preregistration:

`experiments/governed-platform/adjudication/EXP-O-PILOT14-PROCESS-NETWORK-QUORUM-PREREGISTRATION.md`

Parent Pilot 13 adjudication commit:

`806e5d3868298cc962f447b28305ac5788c89386`

Primary Pilot 14 boundary:

- exactly three independent Python replica processes: `r1`, `r2`, `r3`;
- separate SQLite authority state per replica;
- loopback HTTP transport between processes;
- HMAC-SHA256 canonical-envelope authentication;
- quorum = two distinct authenticated replica identities;
- monotonic terms and commit indexes;
- 1000 ms trusted authority lease;
- lease-owner and lease-epoch fencing;
- semantic/effect/worker/idempotency bindings;
- fresh current-quorum revalidation before a consequential effect;
- durable SQLite exactly-once effect sink;
- deterministic injected drop, delay, reorder, duplicate, and corrupted-auth transport faults.

This is a falsification prototype, not a production consensus implementation.

## Original sixteen falsifiers

The frozen P14-01 through P14-16 suite exercises:

1. replica process independence and durable identity;
2. two-distinct-voter term-1 election;
3. forged/unauthenticated peer acknowledgement rejection;
4. duplicate-delivery resistance;
5. quorum-committed authority acquisition to independent durable stores;
6. isolated former-leader denial at consequential use time;
7. delayed acknowledgement non-retroactivity;
8. higher-term majority failover while preserving an unexpired old lease;
9. stale-term authenticated response rejection;
10. exact-expiry higher-term takeover with a single lease-epoch advance;
11. reordered old authority-message rollback prevention;
12. process restart preserving stale fencing and the replay ledger;
13. total process-level quorum loss denying new consequential authority;
14. network heal/catch-up convergence without rollback;
15. post-effect leader crash plus higher-term recovery remaining exactly once;
16. fresh clean authority remaining live after faults, restart, and repair.

The first complete execution of those sixteen cases was operationally green. Independent review nevertheless withheld scientific approval because two adversarial instantiations were not exact enough for the preregistered wording.

## Post-first-run coverage hardening

Preregistered hardening:

`experiments/governed-platform/adjudication/EXP-O-PILOT14-POST-FIRST-RUN-COVERAGE-HARDENING.md`

Two supplemental falsifiers were added without rewriting the original sixteen-case evidence:

### H1 — forged post-generation positive acknowledgement

A genuine positive peer acknowledgement is generated first, then mutated after generation and supplied to the exact production response-verification/voter-counting path. The forged acknowledgement must not add that peer to the authoritative voter set.

Observed outcome: **PASS**.

### H2 — already-generated valid acknowledgement released after deny

A peer processes the request and produces a genuine authenticated acknowledgement. The response is withheld while the requesting leader completes a deny, then released afterward. The late acknowledgement must not reopen or retroactively authorize the completed denied operation.

Observed outcome: **PASS**.

These two supplemental probes close the two coverage gaps that caused the initial scientific verdict to be withheld.

## Preserved pre-stabilization liveness failures

Hardening head before transport stabilization:

`ff83e0c879093b6cd31a6becc2438e2595fe3cb2`

GitHub Actions workflow run:

`34023026420`

### Attempt 1

- H1: PASS.
- H2: PASS.
- P14-05 failed during its otherwise clean bootstrap election.
- Decision: `DENY / ELECTION_QUORUM_REQUIRED`.
- Observed voters: `['r1']`.
- No unsafe authority or consequential effect was created.

### Attempt 2 — exact same SHA, no repository change

- H1: PASS.
- H2: PASS.
- P14-05: PASS.
- P14-14 then failed during its clean bootstrap election.
- Decision: `DENY / ELECTION_QUORUM_REQUIRED`.
- Observed voters: `['r1']`.
- No unsafe authority or consequential effect was created.

Because the same clean-election liveness failure moved between separate positive-path tests at the identical SHA while all affected operations failed closed, this is classified as bounded independent-process / CI scheduling sensitivity at the original 200 ms peer-response deadline, not as evidence that one voter could manufacture authority.

The failures remain part of the scientific record and are not erased by later green executions.

## Transport-stability amendment

Preregistered before the runtime change:

`experiments/governed-platform/adjudication/EXP-O-PILOT14-TRANSPORT-STABILITY-AMENDMENT.md`

Amendment commit:

`5b7f6122`

The amendment authorized exactly one runtime behavior change:

- `experiments/governed-platform/governance/process_network_quorum_exp_o.py`
- `PEER_TIMEOUT_S = 0.20` → `PEER_TIMEOUT_S = 1.00`

It explicitly prohibited retry loops, retry-on-deny, backoff, quorum weakening, voter-count changes, authentication weakening, stale/late-response acceptance, lease extension, hardening-probe changes, or loosened assertions.

Stabilized implementation SHA:

`da759006e6fcf1a927c587ff2244819afd94bf14`

The diff from the hardening head to this stabilized SHA consists of the preregistered stability amendment plus the single timeout-constant change. No Pilot 14 test expectation was changed.

## Stabilized acceptance executions

GitHub Actions workflow run:

`34023739390`

### Stabilized execution 1

Job:

`101460922155`

Checkout SHA:

`da759006e6fcf1a927c587ff2244819afd94bf14`

Observed:

- H1: PASS.
- H2: PASS.
- P14-01 through P14-16: all PASS.
- scorer regressions: 36/36.
- runner regressions: 51/51.
- protected-truth regressions: 4/4.
- observability regressions: 7/7.
- continuation-authority regressions: 12/12.
- governance/falsification regressions: 533/533.
- total: **643/643**.

This first stabilized green was insufficient by preregistration for final approval.

### Stabilized execution 2 — exact same SHA, no repository change

Job:

`101461042716`

The job log explicitly checked out:

`da759006e6fcf1a927c587ff2244819afd94bf14`

Observed:

- H1: PASS.
- H2: PASS.
- P14-01 through P14-16: all PASS.
- scorer regressions: 36/36.
- runner regressions: 51/51.
- protected-truth regressions: 4/4.
- observability regressions: 7/7.
- continuation-authority regressions: 12/12.
- governance/falsification regressions: 533/533.
- total: **643/643**.

The preregistered two-consecutive-same-SHA acceptance condition is therefore satisfied.

## Independent endpoint adjudication

### Quorum identity / acknowledgement integrity

**PASS on tested paths.**

- A single local voter cannot satisfy quorum.
- A duplicate acknowledgement from the same peer cannot manufacture another voter.
- A corrupted or unauthenticated acknowledgement cannot satisfy quorum.
- A genuine acknowledgement that is forged after generation is rejected by the exact production verification/voter-counting path.
- A genuine acknowledgement held until after a completed deny cannot retroactively reopen authority.

No tested acknowledgement fault manufactured effective consequential authority.

### Partition and stale-leader safety

**PASS on tested paths.**

- An isolated former leader cannot revalidate consequential use from local state alone.
- Total quorum loss denies new consequential authority.
- A stale authenticated term cannot satisfy a higher-term quorum.
- Reordered old authority state cannot roll back a later committed takeover.

The tested path therefore keeps authority dependent on current quorum rather than a locally retained leader label or old certificate.

### Lease preservation and takeover fencing

**PASS on tested paths.**

- A higher-term majority does not steal an unexpired previous lease.
- At the exact trusted expiry boundary, takeover is permitted once and advances the lease epoch.
- The stale owner/epoch cannot be promoted back into current authority on the tested path.

### Durable restart / replay / repair behavior

**PASS on tested paths.**

- Replica restart preserves stale fencing and the inbound replay ledger.
- Network heal/catch-up preserves monotonic term/commit state and does not roll back to stale authority.
- Fresh clean authority remains usable after the exercised fault/restart/repair sequence when current quorum exists.

### Exactly-once effect boundary

**PASS on tested paths.**

- A post-effect leader crash followed by higher-term recovery does not create a duplicate effect in the exercised SQLite idempotency boundary.

### Operational liveness

**PASS only for the stabilized tested environment, with explicit limitation.**

The 200 ms peer deadline was empirically too sensitive to process/CI scheduling: two same-SHA executions produced fail-closed clean-election denials in different positive-path tests. After the preregistered increase to 1.00 s, the complete suite passed twice consecutively at the exact same SHA without retries or quorum weakening.

This supports bounded liveness for the tested loopback-process environment under the widened response budget. It does not support a general asynchronous-network liveness theorem.

## Scientific result

**Result:**

`NO_TESTED_PROCESS_NETWORK_MESSAGE_FAULT_MANUFACTURED_EFFECTIVE_AUTHORITY_WITH_PREREGISTERED_TRANSPORT_STABILIZATION_AND_BOUNDED_LIVENESS_LIMITATION`

Within the tested three-process loopback-HTTP EXP-O prototype, no tested forged, duplicate, delayed, stale, reordered, partitioned, or restarted message path manufactured effective consequential authority. Current-quorum use-time revalidation, unexpired-lease preservation, lease-epoch fencing, stale-term/rollback resistance, repair monotonicity, and the exercised exactly-once effect boundary held across the frozen cases and the two supplemental hardening probes.

The original 200 ms peer-response deadline demonstrated real clean-path CI/process-scheduling liveness sensitivity. That limitation is retained explicitly. After a preregistered deadline-only stabilization to 1.00 s, two consecutive complete harness executions at the exact stabilized SHA passed 643/643 each.

## What this does not prove

This Pilot 14 result must not be generalized to:

- production consensus correctness;
- formal linearizability or serializability proof;
- arbitrary asynchronous-network liveness;
- Byzantine-fault tolerance;
- compromised replica-host or signing-key resistance;
- WAN latency, packet loss, duplication, corruption, or reordering distributions beyond the deterministic injected cases;
- TLS/mTLS certificate, PKI, rotation, or channel-security correctness;
- real multi-host clock synchronization or bounded clock drift;
- disk controller, filesystem, fsync, power-loss, torn-write, or storage-corruption durability;
- dynamic cluster membership or reconfiguration;
- more than three replicas;
- operating-system/process scheduler behavior outside the tested runners;
- proof that all possible message interleavings are safe.

The correct conclusion is therefore a bounded falsification result for the exact tested process/network authority boundary, not a universal consensus or distributed-systems safety claim.
