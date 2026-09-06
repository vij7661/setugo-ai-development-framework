# EXP-O Pilot 23 — Checkpoint Authority Isolation Adjudication

Status: **FINAL FOR THE TESTED PILOT 23 PROCESS-ISOLATION BOUNDARY**

## Lineage

- Parent Pilot 22 adjudication: `ab83a5b1e8ec711a89fb3875c758bed878b8b868`
- Preregistration: `e5a4012f121d2f3e4ffcc6306615f815208b7bd6`
- Checkpoint-authority implementation: `15aebc7086ac7bd148e7288b4f23f7cec63410c4`
- Witness oracle-path implementation: `b5196f43508acf52239c33fb2be6d5b34e0f884e`
- Frozen first-execution SHA: `16f9fdf0716686eda5eee60e2b6c9f2b8ee6e3a1`
- Scientific run: `34026970018`
- Job: `101469559763`
- Post-result repair: **none**

## Boundary tested

Pilot 23 separated checkpoint minting from witness signing into distinct subprocesses.

The checkpoint-authority child alone received the raw checkpoint HMAC key and maintained durable SQLite issuance history. Witness children received only their witness-signing keys and no checkpoint HMAC key in environment, argv or request surface. Checkpoint issuance enforced per-witness/store monotonic checkpoint generation and same-generation exact-statement idempotency/equivocation refusal across authority restart.

Before signing, the bounded witness path required an explicit current checkpoint-authority verification result bound to the exact checkpoint digest, witness/store identity, local history root, local maximum generation and trusted minimum checkpoint generation.

No model/provider call participated.

## First-run evidence

The actual first-run job log was inspected. It records:

- P23-01 through P23-20: **20 / 20 PASS**;
- checkpoint authority and witness were distinct processes/stores;
- witness process environment/argv contained no checkpoint signing key;
- witness key and unrelated keys could not forge checkpoint records accepted by the authority verifier;
- lower-generation checkpoint issuance was refused;
- same-generation conflicting-root issuance was refused;
- monotonicity/equivocation refusal survived checkpoint-authority restart;
- exact issue replay remained idempotent;
- tag mutation, scope substitution and below-minimum rollback were rejected;
- checkpoint-authority unavailability failed closed;
- prior positive verification could not be rebound to changed checkpoint or changed local witness history in the tested path;
- post-history/pre-checkpoint ambiguity remained blocked until exact checkpoint reconciliation;
- crash after durable checkpoint issue commit/before response replayed the same logical checkpoint after restart;
- tampered/resealed witness history plus old checkpoint remained blocked;
- one checkpoint authority plus two honest witness processes retained clean quorum liveness;
- higher-generation consumed-state recovery after process restarts retained exactly one local durable effect.

Regression counts on the same frozen run:

- scorer: 36
- runner: 51
- protected truth: 4
- observability: 7
- continuation: 12
- governance/falsification: **711**
- full harness: **821 / 821**

## Endpoint adjudication

Across the tested cases:

- witness possession of raw checkpoint-minting key: **0 observed**
- checkpoint forged with witness key accepted: **0**
- checkpoint forged with unrelated key accepted: **0**
- lower-generation checkpoint issuance after higher durable issuance: **0**
- same-generation conflicting checkpoint issuance: **0**
- restart loss of checkpoint monotonicity/equivocation memory: **0**
- checkpoint-authority unavailable fail-open: **0**
- tested stale verification rebinding to changed checkpoint/history: **0**
- post-history/pre-checkpoint ambiguity promoted: **0**
- clean two-honest-witness quorum liveness: **PASS**
- clean higher-generation consumed recovery liveness: **PASS**

## Scientific conclusion

**`NO_TESTED_WITNESS_POSSESSED_CHECKPOINT_MINTING_KEY_OR_BYPASSED_DURABLE_CHECKPOINT_AUTHORITY_MONOTONICITY_ON_THE_BOUNDED_PROCESS_PATH`**

Within the tested same-host subprocess prototype, moving checkpoint minting into a separate durable authority process prevented the witness process from possessing the raw checkpoint-minting key and retained the tested checkpoint rollback/equivocation/restart safety and witness/quorum liveness properties.

This strengthens the architecture principle that authority-producing key material should remain outside the worker/witness execution process rather than relying on worker self-restraint.

## Critical remaining boundary

Pilot 23 does **not** establish a production-grade authenticated direct authority-to-witness verification channel.

The bounded test harness brokers the authority verification result and the witness validates exact binding fields before use. The witness does not possess the checkpoint HMAC key, but this experiment does not prove resistance to a privileged broker/host that forges the authority's positive verification response itself.

Closing that boundary meaningfully requires a verifier-only credential or authenticated channel whose trust root is not mint-capable inside the witness process, for example:

- asymmetric signatures with public-key verification in witnesses;
- a cloud KMS/HSM-held private signing key with public verification key distributed to witnesses;
- mutually authenticated service identity with an independently governed checkpoint authority;
- ideally separate administrative/host trust domains for checkpoint authority and witnesses.

Implementing another shared-secret same-host shim would not materially advance the evidence class.

## What this result does not prove

Pilot 23 must not be cited as proof of:

- asymmetric verify-only separation;
- production KMS/HSM custody;
- resistance to privileged same-host broker compromise;
- independent administrative, geographic or cloud-provider trust domains;
- safety after checkpoint-authority private-key compromise;
- threshold checkpoint-authority issuance;
- arbitrary Byzantine safety/formal consensus;
- physical power-loss durability;
- production mTLS/service-identity correctness.

## Manual/external dependency frontier

The next scientifically meaningful experiment should use a **real externally held asymmetric signing root or KMS/HSM-backed signing service** and a witness that receives only public verification material. That requires external key/service provisioning and credentials or workload identity not available from the current repository-only experiment harness.

Until that external trust root exists, further same-host symmetric simulations would mostly move the trust assumption rather than falsify it.
