# Integrated Governed MVP — Slice 2 Execution Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

This slice consumes the exact bounded authorization/evidence decision produced by Slice 1. It does not reopen EXP-I Pilot 20 and does not widen any prior experimental claim.

## 1. Goal

Demonstrate a local isolated execution-gateway boundary in which an exact Slice 1 decision may authorize one exact consequential development effect while authority remains external to the model, current state is revalidated at use time, retries are idempotent, crash/restart ambiguity fails closed or reconciles only to an exact durable result, and successful worker output cannot mint terminal authority.

## 2. Included

- exact Slice 1 decision binding and integrity checks;
- fresh use-time capability/current-state validation at the gateway;
- exact action + artifact binding;
- durable local idempotency ledger;
- semantic non-rebind of an idempotency identity;
- replay-safe exact result return;
- crash-boundary representation before durable effect and after durable effect/before response;
- restart-safe recovery from durable gateway state;
- concurrent identical request convergence;
- exact decision/capability/effect/result lineage evidence;
- explicit separation of execution success from RELEASE/DEPLOY/MERGE/production/completion authority.

## 3. Deferred / nonclaims

- production repository writes;
- production shell/browser/network access;
- container or VM escape resistance;
- remote multi-host atomicity;
- distributed consensus;
- cloud KMS/HSM production authority;
- provider attestation;
- physical power-loss/storage-controller durability;
- third-party independent certification;
- release, deploy, merge, production, or completion authority.

The reference implementation may use a local deterministic effect adapter and local durable storage. Passing this slice proves only the frozen local gateway composition boundary.

## 4. Frozen authority invariants

**S2-I01 External authority only** — worker/model output cannot create, widen, refresh, or replace platform capability or terminal authority.

**S2-I02 Exact upstream binding** — the gateway accepts only an exact Slice 1 `AUTHORIZED_FOR_ISOLATED_EXECUTION` decision bound to the same request, action, artifact, execution identity, and capability lineage.

**S2-I03 Fresh use-time validation** — capability/current-state changes between Slice 1 decision and gateway use are revalidated and fail closed.

**S2-I04 Durable idempotency** — one idempotency identity can correspond to at most one exact semantic effect binding and one durable effect/result identity.

**S2-I05 Semantic non-rebind** — reuse of an idempotency identity for a different action, artifact, request, decision, or effect fails closed.

**S2-I06 Crash/retry non-amplification** — crash, retry, restart, or duplicate delivery cannot duplicate the consequential effect or increase authority.

**S2-I07 Ambiguity fail-closed** — malformed, conflicting, or non-uniquely-reconcilable durable state does not become success.

**S2-I08 Concurrent convergence** — concurrent identical requests converge to one exact effect/result identity.

**S2-I09 Exact evidence lineage** — retained evidence binds Slice 1 decision, capability lineage, gateway request, effect identity, and exact result.

**S2-I10 Terminal separation** — execution success never implies RELEASE, DEPLOY, MERGE, production, completion, or self-issued authority.

## 5. Frozen acceptance cases

- **S2-01** clean exact Slice 1 decision + fresh capability/current state performs one exact local effect and returns success.
- **S2-02** missing, forged, denied, review-required, human-required, or terminal-required upstream decision fails before effect.
- **S2-03** request/action/artifact/execution-identity/capability-lineage substitution against the Slice 1 decision fails before effect.
- **S2-04** capability revocation, expiry, qualification/current-state drift after Slice 1 decision fails at gateway use time.
- **S2-05** exact replay with the same idempotency identity returns the exact prior durable result and does not repeat the effect.
- **S2-06** reuse of the same idempotency identity with changed semantics fails closed and preserves the original binding.
- **S2-07** crash before durable effect commit leaves zero consequential effect; retry may perform exactly one effect.
- **S2-08** crash after durable effect commit but before response preserves one durable effect; retry returns the exact prior result without duplicate effect.
- **S2-09** gateway restart preserves idempotency, replay, and semantic non-rebind memory.
- **S2-10** worker/model result claiming release/deploy/merge/completion authority cannot mint terminal authority.
- **S2-11** terminal action remains blocked behind a separate external gate even when the underlying worker effect reports success.
- **S2-12** malformed, partial, conflicting, or ambiguous durable gateway state fails closed rather than being selected by caller/model preference.
- **S2-13** concurrent identical retries converge on one exact durable effect/result identity.
- **S2-14** changed artifact/current-state binding between decision and use fails closed before effect.
- **S2-15** evidence record contains exact upstream decision hash, capability lineage, request/effect binding, effect identity, result hash, and replay/recovery disposition.
- **S2-16** after replay/crash/restart cases, a fresh clean independently authorized second request remains live and executes exactly once.

## 6. Construction and freeze rules

1. Implement only after this contract is committed.
2. Preserve the first construction failure/result before repair.
3. Repairs may not weaken an invariant or acceptance case.
4. Freeze one exact candidate SHA after construction is green.
5. The first complete governed workflow on that exact frozen SHA is authoritative acceptance evidence.
6. `BOUNDED_PASS` requires S2-01..S2-16 explicitly pass plus the complete governed-platform regression suite on the same exact SHA.
7. Workflow success alone is insufficient.
8. Any post-freeze repair requires a new candidate; the first frozen result remains retained.

## 7. Claim boundary

A positive Slice 2 result supports only that, in the tested local reference gateway, an exact externally authorized development effect can be performed at most once under the frozen bindings with replay/restart handling and exact evidence lineage. It does not establish production sandbox security, distributed trust-domain independence, external certification, or terminal/release/deploy authority.
