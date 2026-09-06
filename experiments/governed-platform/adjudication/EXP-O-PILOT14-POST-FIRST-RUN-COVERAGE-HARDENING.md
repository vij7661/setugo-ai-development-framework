# EXP-O Pilot 14 — Post-First-Run Coverage Hardening

Status: **PRE-REGISTERED BEFORE SUPPLEMENTAL HARDENING IMPLEMENTATION OR EXECUTION**

This document is intentionally post-first-run and does not rewrite Pilot 14 history.

## Frozen prior evidence

- Original Pilot 14 preregistration commit: `a448630d72b18b7ab732d589d8d45416ff5ca57f`
- Initial process implementation commit: `450c47c890cdda900abb7c1403ac8241e0a78efc`
- First 16-case tested commit: `dce381cfe06dbf0830052bf41484a3acdca7b4ab`
- First workflow run: `34022748621`
- First workflow operational conclusion: `success`
- Original P14-01 through P14-16 observed test outcomes: 16/16 green
- Full first-run harness: scorer 36, runner 51, protected truth 4, observability 7, continuation 12, governance 531 = **641/641**

The first run remains valid operational/regression evidence. Scientific final adjudication is **withheld** pending the two coverage corrections below.

## Independent-review finding H1 — P14-03 attacked the wrong side of authentication

Original P14-03 preregistered title: **Forged/unauthenticated peer acknowledgement cannot satisfy quorum**.

The first-run test `test_p14_03_forged_or_unauthenticated_peer_ack_cannot_satisfy_quorum` configured `CORRUPT_AUTH` on the outbound `VOTE` request from `r1` to `r2`. The receiver correctly rejected the unauthenticated request and no positive acknowledgement was produced.

That is useful authentication evidence, but it does **not exactly instantiate a forged/corrupted acknowledgement arriving at the leader**. A false-green could theoretically remain in response-envelope verification/counting even while request authentication is correct.

### Frozen supplemental H1 test

Obtain a genuine authenticated positive peer response envelope addressed to the current collector process, make a byte-level/auth-tag mutation **after** peer generation, and feed it to the exact response-validation/distinct-voter helper used by production quorum collection.

Expected:

- response verification fails;
- forged response sender is not added to the voter set;
- self alone does not satisfy quorum;
- no term/index/authority/effect mutation occurs.

No production quorum helper may be replaced with a test-only weaker/stronger implementation for this probe.

## Independent-review finding H2 — P14-07 delayed request delivery, not an already-generated acknowledgement

Original P14-07 preregistered title: **Delayed acknowledgement cannot retroactively authorize after timeout**.

The first-run `DELAY_UNTIL_RELEASE` implementation queued the outbound request before delivery. The authority operation failed closed and later release caused no retroactive effect. This demonstrates delayed-message safety, but not the narrower case in which:

1. the peer already receives and durably processes the request;
2. the peer generates a valid authenticated positive response;
3. the response is withheld from the leader until after the authority operation has completed as deny/timeout;
4. the old response is then released.

### Frozen supplemental H2 transport behavior

Add one test-only transport schedule named `DELAY_RESPONSE_UNTIL_RELEASE`:

- sender delivers the exact authenticated request to the peer immediately;
- peer processes it through the normal durable message ledger and returns its normal signed response;
- sender validates and stores the signed response but does not expose it to the in-progress quorum collector;
- current authority operation therefore completes without that voter and fails closed when no other quorum voter is available;
- later harness release may expose/report the already-generated stored response, but **must not resume, mutate, or reopen the completed authority operation**.

### Frozen supplemental H2 test

Use a clean in-flight authority record. Configure one peer response as `DELAY_RESPONSE_UNTIL_RELEASE` and drop the other peer confirmation.

Expected before release:

- peer inbound ledger proves request was processed;
- leader operation completes denied for insufficient fresh quorum;
- effect count remains zero;
- authority state remains `IN_FLIGHT` with unchanged owner/epoch.

Expected after release:

- exactly one previously generated authenticated response is surfaced by the test release endpoint;
- no effect is created;
- no certificate is retroactively created for the completed operation;
- owner/epoch/state/commit index remain unchanged.

## Scientific endpoint impact

These supplements **do not change**:

- Pilot 14 hypothesis;
- replica membership/quorum size;
- authority fixture;
- lease duration or trusted-time rule;
- semantic/effect bindings;
- leader/term/commit-index semantics;
- original P14-01 through P14-16 expected outcomes;
- allowed interpretation;
- EXP-N isolation.

They only close test-instantiation gaps discovered during independent post-run adjudication.

## Finalization rule

Pilot 14 may be finally adjudicated only if:

1. the frozen first-run P14-01..P14-16 evidence is retained;
2. both H1 and H2 supplemental tests pass through the same production response-validation/quorum-counting and durable peer-processing paths they target;
3. the full regression harness remains green;
4. the final report explicitly records that the initial 16/16 green run was **not** immediately accepted and that these two coverage gaps were found and hardened post-first-run.

A supplemental failure is scientific evidence and must not be hidden by rerunning only successful cases.