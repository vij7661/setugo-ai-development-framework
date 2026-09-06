# EXP-O Pilot 12 — Trusted Lease Expiry and Live Cross-Instance Split-Brain Fencing Adjudication

Status: **FINAL FOR THE PRE-REGISTERED PILOT 12 BOUNDARY**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Parent Pilot 11 adjudication commit: `8429e7fff058c99757e0c70c475a10e5e84ed114`
- Pilot 12 preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT12-TRUSTED-LEASE-SPLIT-BRAIN-PREREGISTRATION.md`
- Preregistration commit: `40ed061ce5bf3172c0f69a27c4a6e0a3d218fda3`
- Versioned Pilot 12 trusted-lease implementation commits: `19c398ef862b6f7e6be28b61905de5474a2cdc54`, `e663151c03251ed8d269f322da117bc0b0787a7c`, `25cc0b4ad8313a7704f641019b5cf9351662bd19`
- Final tested test/implementation commit: `d4bc1fbd59be00f2a09c696d94cff573c752c946`
- Main harness run: `34021715624`
- Operational workflow conclusion: `success`
- Remote model/provider calls: **none**
- Experiment type: deterministic structural/process-concurrency falsification

Workflow success is regression/operational evidence only. The Pilot 12 conclusion below is based on independent inspection of the actual P12-01 through P12-16 executions, the preregistered failure criteria, and the versioned implementation path.

## Boundary evaluated

Pilot 12 closes one explicit limitation of Pilot 11. Pilot 11 allowed any different gateway instance to take over an exact `IN_FLIGHT` permit because its controlled harness proved the old process had crashed. Pilot 12 instead introduces a platform-trusted, durable 1000 ms lease:

- first exact owner receives epoch 1 and a trusted expiry;
- a different still-live gateway cannot take over while `trusted_now_ms < lease_expires_at_ms`;
- explicit renewal is current-owner/current-epoch only and does not change epoch;
- caller/model time is not authority for expiry or renewal;
- at `trusted_now_ms >= lease_expires_at_ms`, an otherwise exact different gateway can take over and atomically advance the epoch;
- stale owners cannot renew or finalize after takeover;
- candidate/effect/idempotency substitution remains blocked;
- MCP effect idempotency preserves at-most-once effects;
- a fresh positive control preserves liveness.

Lease owner, epoch and expiry are platform state, never model/caller authority.

## Independent case adjudication

### P12-01 — First owner receives trusted lease deadline
**PASS.** First exact use acquired owner epoch 1 at trusted time 100000 ms and durable expiry 101000 ms.

### P12-02 — Different live gateway before expiry cannot take over
**PASS.** A second concurrently live process presenting the exact request before expiry was denied as `TRUSTED_LEASE_LIVE_OWNER_UNEXPIRED`.

### P12-03 — Failed pre-expiry takeover cannot mutate fencing state
**PASS.** Owner, epoch and expiry remained unchanged and effect count stayed zero after the denied live contender.

### P12-04 — Current owner can renew before expiry without epoch change
**PASS.** Owner renewal extended expiry from the platform clock while preserving epoch 1.

### P12-05 — Non-owner cannot renew current lease
**PASS.** Different gateway renewal was denied as stale owner and did not mutate lease authority.

### P12-06 — Caller/model time claim cannot force early expiry
**PASS.** A fabricated time value supplied as untrusted request metadata did not control renewal or takeover; the lease decision remained governed by the platform clock.

### P12-07 — Exact expiry boundary is deterministic
**PASS.** `expiry - 1` denied cross-instance takeover; exactly `expiry` allowed the otherwise exact takeover. The boundary therefore follows the preregistered `trusted_now < expiry` active rule without an off-by-one ambiguity.

### P12-08 — Exact post-expiry takeover advances epoch
**PASS.** Exact expiry takeover changed owner, advanced epoch 1 -> 2 and assigned a fresh expiry from the trusted clock.

### P12-09 — Old owner cannot finalize after expiry takeover
**PASS.** Old owner/epoch finalization was denied after takeover.

### P12-10 — Old owner cannot renew after takeover
**PASS.** Old owner/epoch could not extend the new owner's lease.

### P12-11 — Changed candidate cannot use expired-lease takeover
**PASS.** Candidate substitution was rejected before ownership transfer; epoch remained unchanged.

### P12-12 — Changed effect or idempotency cannot use takeover
**PASS.** Both effect-binding and idempotency-binding variants failed closed and did not transfer ownership.

### P12-13 — Two different live gateways racing at expiry yield one next owner
**PASS.** Two concurrently live contender instances raced the exact post-expiry takeover through the durable `BEGIN IMMEDIATE` ownership boundary. Exactly one resolved as the next owner and epoch advanced exactly once to 2; the loser did not obtain a second fresh active authorization.

### P12-14 — Post-effect/pre-finalize ambiguity remains exactly once
**PASS.** After a controlled crash following authoritative MCP effect commit but before semantic/lease finalization, expiry recovery reconciled the historical idempotent effect. Effect count remained one and the permit reached `CONSUMED`.

### P12-15 — Consumed permit cannot be revived after lease expiry
**PASS.** Advancing trusted time far beyond the lease and starting another gateway could not revive a consumed semantic permit or create another effect.

### P12-16 — Fresh clean permit remains live
**PASS.** A newly independently verified permit executed normally and exactly once after the expiry/race/recovery scenarios.

## Harness evidence

Run `34021715624` checked out exact SHA `d4bc1fbd59be00f2a09c696d94cff573c752c946`.

The actual job log explicitly executed and passed all 16 preregistered Pilot 12 tests:

- `test_p12_01_first_owner_receives_trusted_lease_deadline`
- `test_p12_02_different_live_gateway_before_expiry_cannot_take_over`
- `test_p12_03_failed_preexpiry_takeover_does_not_mutate_fence`
- `test_p12_04_current_owner_renews_without_epoch_change`
- `test_p12_05_non_owner_cannot_renew`
- `test_p12_06_untrusted_time_claim_cannot_force_expiry`
- `test_p12_07_exact_expiry_boundary_is_deterministic`
- `test_p12_08_postexpiry_takeover_advances_epoch_and_expiry`
- `test_p12_09_old_owner_cannot_finalize_after_takeover`
- `test_p12_10_old_owner_cannot_renew_after_takeover`
- `test_p12_11_changed_candidate_cannot_use_expired_takeover`
- `test_p12_12_changed_effect_or_idempotency_cannot_use_takeover`
- `test_p12_13_two_live_gateways_racing_at_expiry_yield_one_owner`
- `test_p12_14_posteffect_crash_reconciles_without_duplicate`
- `test_p12_15_consumed_permit_cannot_revive_after_expiry`
- `test_p12_16_fresh_clean_permit_remains_live`

Harness totals at the tested commit:

- scorer: **36 / 36**
- runner: **51 / 51**
- protected truth: **4 / 4**
- observability: **7 / 7**
- continuation: **12 / 12**
- governance: **499 / 499**
- total: **609 / 609**

The recurring GitHub Actions Node 20-to-24 deprecation warning is a tooling warning and did not determine the scientific conclusion.

## Final bounded conclusion

**`TRUSTED_LEASE_SPLIT_BRAIN_FENCING_PASS_16_OF_16 / PREEXPIRY_LIVE_TAKEOVER_SUCCESS_0 / UNTRUSTED_TIME_AUTHORITY_EFFECT_0 / EXPIRY_BOUNDARY_MINUS1_DENY_EXACT_ALLOW / TAKEOVER_EPOCH_ADVANCE_EXACTLY_ONCE / STALE_OWNER_RENEW_OR_FINALIZE_SUCCESS_0 / SEMANTIC_OR_IDEMPOTENCY_SUBSTITUTION_TAKEOVER_SUCCESS_0 / AUTHORITATIVE_DUPLICATE_EFFECTS_0 / CLEAN_CONTROL_EXECUTED_EXACTLY_ONCE`**

Within the tested EXP-O same-host process boundary using a platform-trusted lease clock, an unexpired live semantic-permit owner could not be displaced by another gateway instance. Cross-instance takeover of the exact unchanged request became eligible only at/after trusted lease expiry, atomically advanced the fencing epoch, stale owners could not renew or finalize afterward, and authoritative effects remained at most once while fresh liveness was preserved.

This materially strengthens Pilot 11 for the tested boundary because a different gateway instance ID is no longer sufficient by itself to steal live in-flight ownership.

## Important limitations

Pilot 12 does **not** establish distributed production consensus or universal split-brain prevention.

1. Gateway processes run on the same CI host over loopback HTTP.
2. One local SQLite database serializes the trusted lease/fencing state; no distributed consensus or replicated lease store is tested.
3. The deterministic file-backed clock is platform-controlled in the harness, but cross-host clock synchronization and clock-source compromise are not tested.
4. Network partitions, multi-host simultaneous writers, replication lag, quorum loss and multi-region failover remain out of scope.
5. HMAC keys and local database/key custody remain trusted pilot infrastructure; Byzantine host/key/database compromise is out of scope.
6. Pilot 12 does not prove a production-grade failure detector. It proves only that takeover requires the tested trusted-expiry condition rather than a different instance ID alone.
7. Semantic-verification correctness itself remains assumed; this pilot tests binding, lease authority and effect execution, not whether the semantic judgment was substantively correct.
8. No remote model/provider identity, reasoning quality or model qualification conclusion follows because Pilot 12 made no provider call.

## EXP-N isolation

Pilot 12 added and exercised versioned EXP-O-specific paths only. It did not modify or execute the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.