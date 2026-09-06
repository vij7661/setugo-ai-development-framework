# EXP-O Pilot 11 — IN_FLIGHT Ownership and Recovery Fencing Adjudication

Status: **FINAL FOR THE PRE-REGISTERED PILOT 11 BOUNDARY**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Parent Pilot 10 adjudication commit: `1d7c68ca265fb9ab501c38ff27b6aa75ade72f89`
- Pilot 11 preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT11-INFLIGHT-OWNERSHIP-FENCING-PREREGISTRATION.md`
- Preregistration commit: `6daeac731ae35a5d66f8976330efe5a6e83bca7b`
- Pre-execution atomic-finalization amendment: `experiments/governed-platform/adjudication/EXP-O-PILOT11-ATOMIC-FINALIZE-PREEXECUTION-AMENDMENT.md`
- Amendment commit: `b557ac55fe203ffaee50910aa001df8ec41c1d11`
- Final tested implementation/test commit: `5f388425b9e07379dd554f0ee926bb7e6c310f6a`
- Main harness run: `34021081550`
- Operational workflow conclusion: `success`
- Remote model/provider calls: **none**
- Experiment type: deterministic structural/process-concurrency falsification

Workflow success is regression/operational evidence only. The Pilot 11 conclusion below is based on inspection of the actual P11-01 through P11-16 executions, implementation path, preregistered failure criteria, and the pre-execution TOCTOU amendment.

## Boundary evaluated

Pilot 11 extends the finalized Pilot 10 process-separated semantic-permit path with durable in-flight ownership fencing:

- a platform-generated `lease_owner_gateway_instance_id`;
- monotonically increasing `lease_epoch`;
- one active owner per permit epoch;
- exact unchanged restart takeover under a higher epoch;
- stale-owner/epoch denial;
- exact candidate/effect/worker/base/contract/idempotency binding inherited from Pilot 10;
- consumed-permit non-revival;
- authoritative effect idempotency and crash reconciliation;
- a fresh liveness/specificity control.

Ownership and epoch are platform state and are not model/caller authority.

## Pre-test false-green closure

Before Pilot 11 falsification-test execution, implementation review identified a TOCTOU gap in an initial draft: owner/epoch validation and Pilot 10 semantic-permit finalization could occur in separate SQLite transactions. A stale owner could therefore pass its fence check, lose ownership, and still finalize afterward.

The pre-execution amendment required the Pilot 11 lease record to share the same SQLite database as the Pilot 10 semantic-permit record and required authoritative finalization in a single `BEGIN IMMEDIATE` transaction. The implemented `finalize_both()` path verifies current owner, current epoch, Pilot 10 `IN_FLIGHT` state and both integrity-protected records, then transitions both P10 and P11 records to `CONSUMED` with the same authoritative result digest before one commit.

The amendment did not change the scientific hypothesis, preregistered cases, authority scope, effect scope, or success/failure criteria. It strengthened the implementation before test execution.

## Independent case adjudication

### P11-01 — First use acquires owner epoch 1
**PASS.** Exact first use acquired the current gateway as owner at epoch 1 and completed to `CONSUMED`.

### P11-02 — Same-instance duplicate while held IN_FLIGHT
**PASS.** Duplicate on the same live gateway was non-authorizing with the already-owned/in-flight classification; winner remained the sole active execution path.

### P11-03 — Concurrent pair cannot manufacture two fresh authorizations
**PASS.** Exactly one member of the controlled pair obtained the fresh execution-authorizing path.

### P11-04 — Concurrent duplicate commits exactly one effect
**PASS.** Authoritative effect count remained exactly one.

### P11-05 — Changed candidate cannot bypass live owner
**PASS.** Candidate substitution was rejected on semantic binding; no additional effect was created.

### P11-06 — Changed effect cannot bypass live owner
**PASS.** Effect substitution was rejected on the bound effect digest; no additional effect was created.

### P11-07 — Semantic idempotency rebinding remains denied
**PASS.** Reuse of the external idempotency key for a different semantic effect remained denied; effect count remained one.

### P11-08 — Crash after resolve leaves durable owner/epoch
**PASS.** Controlled crash before effect preserved `IN_FLIGHT`, old owner ID and epoch 1, with zero effects.

### P11-09 — Exact restart takeover advances epoch
**PASS.** A different gateway instance took over the exact unchanged request at epoch 2 and executed/reconciled exactly once.

### P11-10 — Old owner/epoch cannot finalize after takeover
**PASS.** The trusted stale-finalization probe used the same authoritative finalization path and was denied as stale; no registry/effect mutation occurred.

### P11-11 — Changed candidate cannot use takeover
**PASS.** Changed candidate was denied without changing owner/epoch and without effect.

### P11-12 — Changed idempotency key cannot use takeover
**PASS.** Changed idempotency binding was denied without changing owner/epoch and without effect.

### P11-13 — Post-effect/pre-finalize crash reconciles without duplicate
**PASS.** After the authoritative MCP effect committed but before joint semantic/lease finalization, restart takeover reconciled through the existing idempotent result; the registry finalized and effect count remained one.

### P11-14 — Stale owner cannot overwrite authoritative result digest
**PASS.** Old owner/epoch could not finalize with either matching or alternate result content after takeover/finalization; committed result digest remained controlled by the current owner path.

### P11-15 — Consumed permit cannot be taken over
**PASS.** Restart after `CONSUMED` could not revive the permit, advance ownership or authorize a second effect.

### P11-16 — Fresh clean permit remains live
**PASS.** A new independently verified permit executed exactly once after the concurrency/restart scenarios, demonstrating that fencing is not blanket denial.

## Harness evidence

Run `34021081550` checked out exact SHA `5f388425b9e07379dd554f0ee926bb7e6c310f6a`.

The log explicitly executed and passed all 16 preregistered P11 tests:

- `test_p11_01_first_use_acquires_owner_epoch_one_and_consumes`
- `test_p11_02_same_instance_duplicate_while_held_is_non_authorizing`
- `test_p11_03_concurrent_pair_has_only_one_fresh_authorization_success`
- `test_p11_04_concurrent_duplicate_commits_exactly_one_effect`
- `test_p11_05_changed_candidate_cannot_bypass_live_owner`
- `test_p11_06_changed_effect_cannot_bypass_live_owner`
- `test_p11_07_semantic_idempotency_rebinding_remains_denied`
- `test_p11_08_crash_after_resolve_leaves_owner_epoch_one_inflight`
- `test_p11_09_restart_exact_takeover_advances_epoch_and_executes_once`
- `test_p11_10_old_owner_epoch_cannot_finalize_after_takeover`
- `test_p11_11_takeover_with_changed_candidate_is_denied_without_owner_change`
- `test_p11_12_takeover_with_changed_idempotency_key_is_denied_without_owner_change`
- `test_p11_13_post_effect_crash_takeover_reconciles_without_duplicate`
- `test_p11_14_stale_owner_cannot_overwrite_new_result_digest`
- `test_p11_15_consumed_permit_cannot_be_taken_over_after_restart`
- `test_p11_16_fresh_clean_permit_executes_after_concurrency_and_restart`

Harness totals at the tested commit:

- scorer: **36 / 36**
- runner: **51 / 51**
- protected truth: **4 / 4**
- observability: **7 / 7**
- continuation: **12 / 12**
- governance: **483 / 483**
- total: **593 / 593**

The recurring GitHub Actions Node 20-to-24 deprecation warning is a tooling warning and did not determine the scientific conclusion.

## Final bounded conclusion

**`INFLIGHT_OWNER_FENCING_PASS_16_OF_16 / STALE_OWNER_FINALIZATION_SUCCESS_0 / CONCURRENT_DUPLICATE_EFFECTS_0 / RESTART_TAKEOVER_EPOCH_ADVANCE_PRESERVED / SEMANTIC_BINDING_SUBSTITUTION_EFFECTS_0 / CONSUMED_REVIVAL_0 / CLEAN_CONTROL_EXECUTED_EXACTLY_ONCE`**

Within the tested EXP-O same-host loopback process lifecycle, semantic-bound permit use was fenced to one live gateway owner per lease epoch. Same-instance duplicates could not acquire a second active execution authorization; controlled restart takeover of an exact unchanged request advanced a durable epoch; stale owners could not finalize after takeover; candidate/effect/idempotency substitutions failed closed; and authoritative effects remained at most once while clean liveness was preserved.

The pre-execution atomic-finalization amendment materially strengthens this conclusion for the tested SQLite boundary because owner/epoch validation and P10/P11 consumption are one transactional operation rather than a check/use sequence.

## Important limitations

Pilot 11 does **not** establish distributed production consensus or universal failover safety.

Specifically:

1. Gateway processes run on the same CI host over loopback HTTP.
2. Pilot 11 uses one local SQLite database as the serialization/fencing authority; no distributed consensus protocol is tested.
3. Different gateway instance ID is sufficient for takeover only because the controlled harness owns the crash/restart lifecycle. It is not production failure-detector proof.
4. Network partitions, split brain across hosts, multi-region failover, replication lag and quorum loss are not tested.
5. HMAC keys and local database/key custody remain trusted pilot infrastructure; Byzantine host/key/database compromise is out of scope.
6. Semantic-verification correctness itself is assumed; this pilot tests binding, ownership and effect execution, not whether the verifier's semantic judgment is correct.
7. No remote model/provider identity, reasoning quality or model qualification conclusion follows because Pilot 11 made no provider call.

## EXP-N isolation

Pilot 11 changed and exercised EXP-O-specific paths only. It did not modify or execute the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.