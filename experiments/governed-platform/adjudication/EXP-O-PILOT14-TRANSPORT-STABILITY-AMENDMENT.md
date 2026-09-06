# EXP-O Pilot 14 — Transport Stability Amendment

Status: **PRE-REGISTERED AFTER TWO SAME-SHA FAIL-CLOSED LIVENESS FAILURES AND BEFORE ANY TRANSPORT DEADLINE CHANGE**

This amendment is operational/liveness stabilization only. It does not rewrite the original Pilot 14 preregistration, first-run evidence, post-first-run coverage hardening, or either observed same-SHA failure.

## Frozen evidence motivating this amendment

Pilot 14 supplemental hardening head before this amendment:

`ff83e0c879093b6cd31a6becc2438e2595fe3cb2`

GitHub Actions workflow run: `34023026420`.

### Attempt 1

- Supplemental H1 forged post-generation acknowledgement falsifier: PASS.
- Supplemental H2 generated-valid-acknowledgement-held-until-after-deny falsifier: PASS.
- P14-05 failed during its clean bootstrap election.
- Returned decision: `DENY / ELECTION_QUORUM_REQUIRED`.
- Observed voters: `['r1']`.
- No unsafe authority or effect was created.

### Attempt 2 — exact same SHA, no code/test change

- Supplemental H1: PASS.
- Supplemental H2: PASS.
- P14-05 passed.
- P14-14 then failed during its clean bootstrap election.
- Returned decision: `DENY / ELECTION_QUORUM_REQUIRED`.
- Observed voters: `['r1']`.
- No unsafe authority or effect was created.

The same clean-election liveness failure moving between independent positive paths at the identical SHA is treated as evidence of bounded loopback-process response-window sensitivity under CI load. It is not converted into a scientific safety pass, and both failures remain part of the Pilot 14 record.

## Frozen narrow change

The only production-prototype behavior change authorized by this amendment is:

- file: `experiments/governed-platform/governance/process_network_quorum_exp_o.py`
- constant: `PEER_TIMEOUT_S`
- old value: `0.20`
- new value: `1.00`

No other runtime or test behavior may be changed as part of this stabilization step.

## Explicitly unchanged scientific boundary

The following remain frozen and must not be changed by this amendment:

- replica membership: exactly `r1`, `r2`, `r3`;
- quorum: exactly 2 distinct authenticated replica identities;
- HMAC-SHA256 envelope authentication and exact sender/receiver/cluster/message/payload binding;
- duplicate-voter elimination and durable replay/conflicting-message rejection;
- term monotonicity and stale-term rejection;
- commit-index/revision monotonicity;
- lease duration: 1000 ms;
- trusted-time rule;
- unexpired-lease preservation during higher-term failover;
- exact-expiry takeover and lease-epoch fencing;
- semantic/effect/worker/idempotency bindings;
- current-quorum use-time revalidation before consequential effect;
- durable exactly-once effect boundary;
- transport fault vocabulary and existing P14-01 through P14-16 expected outcomes;
- supplemental H1 and H2 expected outcomes;
- EXP-N isolation;
- allowed scientific interpretation and production limitations.

## Prohibited stabilization techniques

This amendment does **not** authorize:

- retry loops, retry-on-deny, backoff, or repeated elections inside a test to turn an initial denial into success;
- changing quorum from 2;
- counting duplicate acknowledgements or one peer identity more than once;
- accepting unauthenticated, stale-term, stale-revision, mismatched, or late responses;
- altering H1/H2 transport shims or expected outcomes;
- weakening fail-closed behavior after quorum loss;
- extending the 1000 ms authority lease;
- changing test assertions to tolerate denied clean paths;
- changing any scientific endpoint after observing the stabilized results.

A clean operation still makes one bounded peer request per peer through the existing collection path. The deadline is simply widened so normal independent-process scheduling on CI has additional headroom.

## Stabilized-SHA acceptance rule

Pilot 14 remains scientifically open after the timeout edit. Final adjudication requires all of the following:

1. The timeout edit is exactly `PEER_TIMEOUT_S = 0.20` to `PEER_TIMEOUT_S = 1.00` and no other implementation/test change is bundled with it.
2. The complete harness passes once at the resulting stabilized SHA.
3. Without any repository change, the complete harness is executed again at the **exact same stabilized SHA** and passes a second consecutive time.
4. P14-01 through P14-16 all pass in both executions.
5. Supplemental H1 and H2 both pass in both executions.
6. No tested path creates authority/effect from one voter, duplicate/forged/stale/late response, quorum loss, stale owner, or stale replica.
7. Both pre-amendment fail-closed liveness failures remain explicitly recorded in final adjudication.

The first stabilized green execution alone is insufficient for final approval.

If either stabilized execution shows an authority-safety false green, Pilot 14 is falsified on that path and must not be approved. If clean-path liveness still flakes, Pilot 14 remains operationally unstable and must not be approved by repeated reruns until green.

## Allowed interpretation if the stabilization rule is satisfied

Satisfying the two-run rule may support only the original Pilot 14 bounded claim for the tested three-process loopback-HTTP prototype, with an explicit note that the original 200 ms peer deadline demonstrated CI/process-scheduling liveness sensitivity.

It does not establish production consensus correctness, formal linearizability, arbitrary asynchronous-network liveness, Byzantine tolerance, WAN behavior, real TLS/mTLS security, compromised-host/key resistance, disk/power-loss durability, clock synchronization across machines, or dynamic-membership correctness.
