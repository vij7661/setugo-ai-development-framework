# Integrated Governed MVP — Slice 9 External Credential Lease Gate Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Current authoritative `main` parent: `417e60aab4f8d220e3de889e5683e6642ddd3431`.
Accepted remote-terminal lineage already contained in that parent: Slice 8 merge `3a19eff0a735f702bac2807040f361b2dc7a37b6`, exact accepted Slice 8 candidate `4873d7a11383b5ba684cb92e399b18cfe2ffb304`.

## 1. Goal

Falsify whether an exact already-governed terminal execution binding can obtain and consume a short-lived platform-owned external credential lease without allowing a model, worker, reviewer, retry path, stale authority record, or downstream adapter to select a different credential, widen provider/action/resource scope, refresh expired authority, persist the secret, leak the secret into evidence, or convert possession of a credential into terminal authority.

Slice 9 adds a deterministic local reference credential broker and lease-consumption gate. It proves only the lease/identity/control semantics under the frozen cases below.

It does **not** call a real GitHub/GitLab/cloud/provider API, does **not** read a real production secret manager, does **not** store a real API key, and does **not** perform any real merge/deploy/release/completion side effect.

## 2. Included

- exact consumption of an accepted terminal execution / remote-transport lineage;
- platform-owned credential profile identity distinct from secret value;
- deterministic local reference credential broker;
- lease issuance bound to exact provider, credential profile, project, task, effect, action, artifact, state version, terminal execution identity, and authority epoch;
- short-lived `not_before` / `expires_at` validity;
- use-time ACTIVE / REVOKED state check;
- one lease identifier → one exact frozen binding;
- lease replay for the same exact binding without minting broader authority;
- rejection of model/worker supplied secret material or replacement credential identity;
- secret-handle / opaque-token use at the consumer boundary rather than evidence-visible raw secret values;
- deterministic evidence that records credential identity and lease metadata but never the secret value;
- fail-closed handling of expiry, revocation, moved artifact/state, provider/profile substitution, malformed lease, and missing broker evidence;
- restart/recovery of lease metadata without persisting secret material in the governed evidence store;
- preserved accepted Slice 1→Slice 8 regression lineage.

## 3. Deferred / nonclaims

- AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault, GitHub App installation tokens, OAuth, OIDC federation, KMS/HSM, or hardware-backed secret isolation;
- production IAM-policy correctness;
- production provider identity attestation;
- TLS/PKI, DNS, proxy, service-mesh, or host-compromise resistance;
- real third-party API correctness or provider-specific rate limits;
- secret rotation across a distributed fleet;
- multi-region lease consensus;
- operating-system process isolation against a malicious root-equivalent worker;
- autonomous merge/deploy/release authority;
- proof that a credential was cryptographically bound by the external provider to the declared profile.

## 4. Frozen input contract

### Credential lease request

- `lease_request_id`
- `project_id`
- `task_id`
- `effect_id`
- `action`
- `artifact_sha`
- `state_version`
- `terminal_execution_id`
- `terminal_binding_hash`
- `authority_snapshot_hash`
- `provider_id`
- `credential_profile_id`
- `now_epoch`

No raw credential/secret field is permitted in the request.

### Current credential profile material

- `provider_id`
- `credential_profile_id`
- `profile_status`: `ACTIVE` or `REVOKED`
- `allowed_actions`
- `allowed_project_ids`
- `allowed_resource_classes`
- `profile_epoch`
- `not_before_epoch`
- `expires_at_epoch`
- `profile_snapshot_hash`

This is identity/policy material only. It must not contain a raw API key/token/password.

### Lease record

- `credential_lease_id`
- exact frozen request lineage
- `provider_id`
- `credential_profile_id`
- `profile_epoch`
- `lease_not_before_epoch`
- `lease_expires_at_epoch`
- `lease_status`: `ACTIVE`, `REVOKED`, `EXPIRED`, `CONSUMED`, or `DENIED`
- `opaque_secret_handle`
- `lease_binding_hash`
- `lease_evidence_hash`

`opaque_secret_handle` is a reference identifier for the deterministic local broker. It is not the secret value and must not be accepted as terminal authority by itself.

## 5. Frozen invariants

**S9-I01 Exact upstream binding required** — no credential lease is issuable without a valid exact terminal execution/binding lineage already accepted by the prior governed path.

**S9-I02 Platform-owned credential identity** — `provider_id` and `credential_profile_id` must resolve from platform-owned configuration/policy; a model/worker/reviewer cannot replace them.

**S9-I03 No raw secret in governed inputs** — a request containing a raw API key/token/password/secret value is rejected before lease issuance.

**S9-I04 Use-time profile validity** — profile ACTIVE status, epoch, scope, `not_before`, and expiry must be revalidated at lease issuance/use time; historical validity is insufficient.

**S9-I05 Scope intersection only** — requested provider/project/action/resource scope must be a subset of both terminal authority and credential-profile policy. A lease cannot widen either side.

**S9-I06 One lease ID, one binding** — reuse of a lease identifier with changed provider/profile/project/task/effect/action/artifact/state/binding is rejected.

**S9-I07 Expiry is terminal for that lease** — an expired lease cannot be refreshed merely by retrying the old request or replaying old evidence; a new lease requires fresh current authority/profile validation.

**S9-I08 Revocation dominates possession** — possession of a previously issued opaque handle cannot override current profile or lease revocation.

**S9-I09 Secret-value non-persistence** — governed ledger/evidence/telemetry/dashboard records may retain credential profile identity and opaque handle identity but must never retain the underlying secret value.

**S9-I10 Secret-value non-disclosure on failure** — exceptions, malformed responses, retry logs, structured failure objects, and diagnostic evidence must not disclose the underlying secret value.

**S9-I11 Credential possession is not authority** — a valid credential lease cannot substitute for terminal action authorization, current authority state, review requirements, or exact artifact/action binding.

**S9-I12 Replay non-amplification** — replay of the exact valid lease for the exact binding may recover the same deterministic result but cannot create a second broader lease or new effect authority.

**S9-I13 Profile epoch substitution denied** — moved/rotated profile epoch or profile snapshot hash invalidates stale lease issuance/use evidence unless a new lease is freshly issued under the new profile state.

**S9-I14 Deterministic lease evidence** — successful lease evidence binds all non-secret lineage fields and changes/invalidates if any bound field changes.

**S9-I15 Reference broker only** — a passing reference broker proves only tested lease-control semantics, not production secret-manager or external-provider security.

## 6. Frozen result states

- `DENY_UPSTREAM_BINDING`
- `DENY_CREDENTIAL_PROFILE`
- `DENY_RAW_SECRET_INPUT`
- `DENY_SCOPE_WIDENING`
- `DENY_LEASE_REBIND`
- `DENY_PROFILE_STALE_OR_REVOKED`
- `LEASE_EXPIRED`
- `LEASE_REVOKED`
- `LEASE_ISSUED`
- `LEASE_REPLAYED`
- `LEASE_CONSUMPTION_DENIED`
- `LEASE_CONSUMED_REFERENCE_ONLY`

Only `LEASE_ISSUED`, `LEASE_REPLAYED`, and `LEASE_CONSUMED_REFERENCE_ONLY` may carry positive lease evidence, and none of them constitutes merge/deploy/release/completion authority.

## 7. Frozen acceptance cases

- `S9-01` exact valid upstream terminal binding + active exact profile issues one bounded lease.
- `S9-02` exact same request replays the same lease identity/evidence without widening.
- `S9-03` missing/malformed/non-success upstream terminal binding denies before broker access.
- `S9-04` provider substitution denies.
- `S9-05` credential-profile substitution denies.
- `S9-06` project/task/effect/action/artifact/state-version widening denies.
- `S9-07` model/worker supplied replacement credential identity denies.
- `S9-08` any raw secret/API-key/token/password field in request denies before lease issuance.
- `S9-09` profile not-yet-valid denies.
- `S9-10` expired profile denies.
- `S9-11` revoked profile denies even if prior lease evidence exists.
- `S9-12` stale profile epoch/snapshot denies fresh use of old lease evidence.
- `S9-13` lease expiry denies consumption; retry cannot silently refresh it.
- `S9-14` explicit lease revocation denies consumption of an otherwise valid opaque handle.
- `S9-15` same lease ID with changed binding denies.
- `S9-16` allowed action/profile intersection succeeds only for the exact action.
- `S9-17` profile allowing broad actions cannot widen narrower terminal authority.
- `S9-18` terminal authority allowing broad scope cannot widen narrower credential-profile policy.
- `S9-19` governed lease/evidence JSON contains profile/lease identity but no raw secret value.
- `S9-20` failure/exception/diagnostic paths contain no raw secret value.
- `S9-21` restart/reopen preserves lease metadata/replay semantics without persisting secret material in governed evidence.
- `S9-22` mutated provider/profile/project/task/effect/action/artifact/state/epoch/timestamps changes or invalidates lease evidence hash.
- `S9-23` model/reviewer/CI/broker self-report cannot turn credential possession into terminal authority.
- `S9-24` secret-handle replacement or forged unknown handle denies.
- `S9-25` no result claims a real production provider/GitHub/cloud action occurred.

## 8. Construction and freeze rules

1. This contract must be committed before acceptance tests or mechanism implementation.
2. Add `S9-01..S9-25` falsification tests before mechanism implementation wherever scientifically feasible.
3. Preserve the first red execution evidence; do not weaken tests to obtain green.
4. Use synthetic deterministic secret material only inside the reference broker test fixture; it must never be committed to governed evidence or public telemetry output.
5. The reference implementation must require no external network credentials.
6. Provider/profile behavior must be registry/config driven; tests must include at least one synthetic future provider/profile name proving no provider-specific dashboard/evidence branch is required.
7. Preserve all accepted Slice 1→Slice 8 regressions.
8. Freeze an exact candidate only after Slice9 acceptance cases and prior regressions are green.
9. A fresh independent review of the exact candidate is mandatory before promotion.
10. Deterministic review-of-review and exact closure-head validation are mandatory before merge.
11. Green CI, credential possession, reviewer PASS, or provider success is evidence only and never merge/deploy/release authority by itself.

## 9. Claim boundary

A bounded pass supports only that the tested deterministic reference credential broker and lease-consumption gate prevented credential identity substitution, scope widening, stale/revoked/expired use, raw-secret persistence/disclosure in governed evidence, and credential-as-authority laundering under the frozen cases. It does not establish production secret-manager correctness, external-provider identity, production IAM security, host isolation, or real terminal-action safety.
