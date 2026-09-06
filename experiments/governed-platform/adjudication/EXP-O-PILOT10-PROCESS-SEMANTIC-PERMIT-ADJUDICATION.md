# EXP-O Pilot 10 — Process-Separated Semantic-Bound Permit Registry Adjudication

Status: **FINAL FOR THE PRE-REGISTERED PILOT 10 BOUNDARY**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Parent Pilot 9 adjudication commit: `e0379af8e736921d8ac699750749e03c8cbbf7aa`
- Pilot 10 preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT10-PROCESS-SEMANTIC-PERMIT-PREREGISTRATION.md`
- Preregistration commit: `9918510336a0a47f8e334721ea4c0f6855874546`
- Final tested implementation/test commit: `75a9360b337c32f0bbdc3f1f3cc8f5a2dbcf690a`
- Main harness run: `34020613036`
- Operational workflow conclusion: `success`
- Remote model provider calls: **none**
- Experiment type: deterministic structural/process-boundary falsification

Workflow success is regression/operational evidence only. The Pilot 10 conclusion below is based on inspection of the actual named P10-01 through P10-15 test executions in the harness log against the preregistered failure criteria.

## Implemented boundary

New EXP-O-only components:

- `governance/semantic_permit_registry_exp_o.py`
  - integrity-protected SQLite semantic permit registry;
  - durable `ISSUED -> IN_FLIGHT -> CONSUMED` lifecycle;
  - exact candidate/effect/capability/worker/contract/base/idempotency binding;
  - raw inner LEP permit retained in platform registry;
  - semantic idempotency ledger preventing one external idempotency key from being rebound to a different semantic-effect digest;
  - exact `IN_FLIGHT` recovery only for the original bound permit.

- `governance/mcp_semantic_gateway_process_exp_o.py`
  - separate Python process;
  - loopback HTTP boundary;
  - process-owned trusted time source;
  - outer semantic-bound permit verification;
  - durable registry resolution and integrity checks;
  - historical MCP gateway invocation with resolved inner LEP permit;
  - test-only crash points before effect and after authoritative effect/before semantic registry finalization;
  - process configuration excludes semantic-verifier signing key and AuthorityKernel capability-issuing key.

- `governance/semantic_process_exp_o.py`
  - caller-facing HTTP client and process harness;
  - request surface carries only outer permit + exact candidate/effect/worker/idempotency data;
  - preserves transport-unknown separately from authoritative effect state.

- `governance/test_exp_o_pilot10_process_semantic_permit.py`
  - all 15 preregistered structural cases.

The finalized Pilot 9 module was not modified.

## Pre-test false-green closure

During implementation review, before the Pilot 10 falsification tests were added, a second boundary gap was identified: the historical MCP gateway's idempotency digest predates `semantic_payload_digest`. Therefore two semantically different candidates with identical legacy action/resource metadata could otherwise share the same external idempotency key and appear identical at the historical gateway.

Pilot 10 closed this before its test execution by adding a durable semantic idempotency ledger keyed by `(worker_id, idempotency_key)` and bound to the semantic-effect digest and bound permit ID. A changed semantic effect under an already-bound idempotency key is denied before inner gateway use.

The crash/recovery case was also strengthened to the harder ambiguity point: process termination occurs **after the authoritative MCP effect has committed but before the semantic registry can finalize `IN_FLIGHT -> CONSUMED`**. Restart then has to reconcile through the existing authoritative idempotency record without duplicating the effect.

## Independent case adjudication

### P10-01 — Missing outer permit
**PASS.** Separate process denied with `SEMANTIC_BOUND_OUTER_PERMIT_INVALID`; zero authoritative effects.

### P10-02 — Forged/tampered outer permit
**PASS.** Signature-forged outer permit denied; zero effects.

### P10-03 — Candidate substitution
**PASS.** Candidate B under candidate A's outer permit denied on semantic-payload binding; zero effects.

### P10-04 — Effect substitution
**PASS.** Same candidate with changed semantic effect metadata denied on `effect_digest`; zero effects.

### P10-05 — Missing registry record
**PASS.** Valid outer permit with deleted registry record denied `SEMANTIC_REGISTRY_RECORD_MISSING`; zero effects.

### P10-06 — Registry record tamper
**PASS.** Direct SQLite mutation without a valid integrity tag denied `SEMANTIC_REGISTRY_INTEGRITY_INVALID`; zero effects.

### P10-07 — Cross-record substitution
**PASS.** A valid registry row/tag pair from another bound permit substituted under the requested DB key was rejected as `SEMANTIC_REGISTRY_RECORD_BINDING_INVALID`; zero effects.

### P10-08 — Clean cross-process execution
**PASS.** Child gateway PID differed from test/LEP process; exact request crossed loopback HTTP, used `SEMANTIC_GATEWAY_PROCESS_TRUSTED_CLOCK`, executed exactly one authoritative effect, and registry transitioned to `CONSUMED`.

### P10-09 — Exact replay after completed execution
**PASS.** Completed outer permit replay denied as `SEMANTIC_BOUND_PERMIT_CONSUMED`; authoritative effect count remained one.

### P10-10 — Same idempotency key, changed semantic effect
**PASS.** Fresh independently verified candidate B attempting to reuse candidate A's external idempotency key was denied `SEMANTIC_IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_EFFECT`; authoritative effect count remained one.

### P10-11 — Gateway restart after completed execution
**PASS.** Gateway instance ID changed after restart; durable `CONSUMED` state persisted and the completed permit could not create a second effect.

### P10-12 — Recovery from durable IN_FLIGHT ambiguity
**PASS.** Test-only process fault terminated the gateway after the MCP SQLite effect committed but before semantic-registry finalization. Caller observed `TRANSPORT_OUTCOME_UNKNOWN`; authoritative effect count was already one and registry state remained `IN_FLIGHT`. After gateway restart, the identical request resolved as `RECOVERY_IN_FLIGHT`; the historical MCP gateway returned `IDEMPOTENT_REPLAY`, no second effect was executed, and the registry finalized `CONSUMED`.

### P10-13 — Caller-surface raw-permit non-exposure
**PASS.** The trusted harness inspected the raw inner permit in the platform registry solely for the falsification assertion. Its raw structure/signature did not occur in the LEP authorization object, caller HTTP request, or caller HTTP response. Only the bound outer permit and an inner-permit digest crossed the caller surface.

### P10-14 — Gateway key separation
**PASS within pilot key model.** Even when the parent test environment was deliberately populated with semantic-verifier and AuthorityKernel signing-key variables, the process harness removed them before child creation. Child health reported both absent. The child loaded only the Pilot 10 outer-permit HMAC key, registry-integrity HMAC key and historical inner-permit HMAC key needed by this test boundary.

### P10-15 — Clean specificity control after restart
**PASS.** A fresh independently verified candidate under a fresh bound permit/idempotency key executed exactly once after restart, showing the restart/replay controls did not reduce the path to blanket denial.

## Harness evidence

Run `34020613036` checked out exact SHA `75a9360b337c32f0bbdc3f1f3cc8f5a2dbcf690a`.

The log explicitly executed and passed every test named:

- `test_p10_01_missing_outer_permit_denies_before_effect`
- `test_p10_02_forged_outer_permit_denies`
- `test_p10_03_candidate_substitution_denies`
- `test_p10_04_effect_substitution_denies`
- `test_p10_05_missing_registry_record_denies`
- `test_p10_06_registry_record_tamper_denies`
- `test_p10_07_cross_record_substitution_denies`
- `test_p10_08_clean_cross_process_execution_once`
- `test_p10_09_exact_replay_after_consumed_does_not_authorize`
- `test_p10_10_same_idempotency_key_cannot_rebind_semantic_effect`
- `test_p10_11_consumed_state_survives_gateway_restart`
- `test_p10_12_post_effect_crash_reconciles_inflight_without_duplicate`
- `test_p10_13_raw_inner_permit_never_crosses_caller_surface`
- `test_p10_14_gateway_process_has_no_semantic_or_capability_signing_key`
- `test_p10_15_fresh_clean_effect_executes_after_restart`

Harness totals at the tested commit:

- scorer: **36 / 36**
- runner: **51 / 51**
- protected truth: **4 / 4**
- observability: **7 / 7**
- continuation: **12 / 12**
- governance: **467 / 467**
- total: **577 / 577**

The recurring GitHub Actions Node 20-to-24 deprecation warning remains a tooling warning and did not alter these results.

## Final bounded conclusion

**`PROCESS_SEPARATED_SEMANTIC_BOUNDARY_PASS_15_OF_15 / TAMPER_AND_SUBSTITUTION_EFFECTS_0 / CLEAN_PROCESS_EFFECT_EXACTLY_ONCE / COMPLETED_REPLAY_EFFECTS_0 / CHANGED_SEMANTIC_IDEMPOTENCY_REBIND_BLOCKED / POST_EFFECT_CRASH_RECONCILED_WITH_IDEMPOTENT_REPLAY / RAW_INNER_PERMIT_CALLER_EXPOSURE_0`**

Within the tested EXP-O loopback process boundary, exact signed semantic verification and effect authority survived process separation using a durable integrity-protected server-side permit registry; the caller did not receive the raw inner LEP permit, the tested substitutions/tampering failed closed, and the tested restart/recovery paths produced at most one authoritative effect.

This strengthens the governed execution architecture:

`Diagnosis -> permissible action -> qualified execution component -> platform capability -> candidate execution proposal -> independent semantic verification -> semantic-bound permit -> separate effect gateway -> authoritative effect evidence -> approval/release gate`

The model/candidate remains below the authority boundary. Process separation did not require exposing the raw inner authority permit to it.

## Important limitations

Pilot 10 does **not** establish production remote-MCP security.

Specifically:

1. Transport is loopback HTTP, not TLS/mTLS and not a hostile network.
2. Components run on the same CI host and share filesystem access; this is process separation, not hostile-host isolation.
3. HMAC keys are symmetric pilot keys. A process that possesses a Pilot 10 HMAC verification key cryptographically possesses signing capability for that HMAC domain. Pilot 10 therefore does not prove asymmetric verifier-only keys, HSMs, TPMs, non-exportable keys or production key custody.
4. The raw inner LEP permit is stored plaintext inside the trusted platform SQLite registry. Its integrity/binding are protected, but it is not encrypted at rest. The tested claim is **caller-surface non-exposure**, not database-confidentiality under host compromise.
5. SQLite registry and authoritative effect DB are distinct transactional stores. Pilot 10 handles the tested crash ambiguity by durable `IN_FLIGHT` state plus exact idempotent reconciliation; it does not prove distributed atomic commit.
6. No multi-host concurrency, distributed consensus, failover replication or multi-region durability is tested.
7. Semantic-verification correctness itself is assumed by this structural pilot; it tests binding and transport of verification evidence, not whether the verifier's judgment is semantically correct.
8. No remote model/provider identity or model qualification conclusion follows from Pilot 10 because there was no provider call.

## EXP-N isolation

Pilot 10 used new EXP-O-specific files only. It did not modify or execute the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 path.