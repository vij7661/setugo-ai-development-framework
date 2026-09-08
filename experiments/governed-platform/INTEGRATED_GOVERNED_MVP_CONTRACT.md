# Integrated Governed MVP — Composition Contract

Status: **PRE-IMPLEMENTATION FROZEN MVP BOUNDARY**

This is a product-integration stage, not EXP-I Pilot 20 and not a new scientific claim. It composes mechanisms already implemented and tested in the experimental repository into one deterministic minimum governed execution slice.

## 1. Goal

Demonstrate one end-to-end backend path in which a model may produce evidence/proposals, but consequential authority remains external to the model from routing through execution and completion.

Governed sequence:

1. Receive bound project/task/action intent.
2. Revalidate exact provider + model + SKU + deployment-path qualification at execution time.
3. Bind normalized model output to a platform-issued capability without granting model authority.
4. Revalidate the capability at the instant of consequential use.
5. Require review/manual escalation signals independently of model preference.
6. Admit consequential execution only when all deterministic gates are current and clean.
7. Produce a normalized decision/evidence record that distinguishes execution authorization from release/completion authority.

## 2. MVP boundaries

### Included

- exact task-specific qualification revalidation;
- provider/model/SKU/deployment-path binding;
- external platform capability as the sole mutation authority source;
- model authority claims retained as evidence but never effective authority;
- use-time capability validation;
- fail-closed review/manual-gate input;
- explicit block on RELEASE/DEPLOY/MERGE as MVP terminal authority;
- deterministic decision record suitable for evidence/audit persistence;
- negative-path tests for stale qualification, revocation, scope widening, model self-authorization, and manual-gate requirements.

### Deferred

- production PostgreSQL service and migrations;
- immutable object store;
- queue/event transport;
- real sandbox or repository write gateway;
- secret-manager leases;
- provider network calls;
- production UI;
- autonomous deployment/release;
- distributed consensus or multi-host correctness.

The MVP executor therefore returns an authorization decision only. It does **not** perform a real repository, browser, shell, deployment, or production side effect.

## 3. Frozen authority invariants

**MVP-01 External authority** — model output can never create, widen, refresh, revoke, or replace platform capability authority.

**MVP-02 Exact qualification** — consequential execution requires current exact provider + model + SKU + deployment path + qualification lineage.

**MVP-03 Use-time validation** — routing-time eligibility or prior capability validity cannot substitute for validation at the instant of requested use.

**MVP-04 Scope containment** — requested action and artifact classes must be a subset of the platform-issued capability.

**MVP-05 Review independence** — a model request to skip review cannot alter a platform review/manual-gate decision.

**MVP-06 Terminal-authority separation** — RELEASE, DEPLOY, and MERGE are never authorized by this MVP executor, even if included in a model claim or a broad capability. They require a separate external release/completion gate.

**MVP-07 Fail-closed composition** — malformed, stale, revoked, incomplete, contradictory, or HUMAN_REQUIRED gate inputs deny consequential execution.

**MVP-08 Evidence without authority** — unsafe model authority claims remain observable evidence while effective consequential authority remains false.

**MVP-09 Determinism** — identical bound inputs produce the same decision record, excluding explicitly external clock/state changes.

**MVP-10 No success laundering** — provider/model success, review agreement, test success, or workflow green status alone cannot become release/completion authority.

## 4. Decision states

- `DENY_QUALIFICATION`
- `DENY_AUTHORITY_BINDING`
- `DENY_CAPABILITY`
- `HUMAN_REQUIRED`
- `REVIEW_REQUIRED`
- `TERMINAL_AUTHORITY_REQUIRED`
- `AUTHORIZED_FOR_ISOLATED_EXECUTION`

`AUTHORIZED_FOR_ISOLATED_EXECUTION` means only that a separately isolated worker/gateway may be invoked for the exact requested action under the exact capability. It is not release, deploy, merge, completion, or production approval.

## 5. Input contract

The integration function receives explicit inputs only:

- `route`
- `registry_entry`
- `normalized_model_result`
- `capability`
- `execution_request`
- `review_gate`
- `now_epoch`
- `now_iso`

No ambient conversation history, model self-report, workflow label, or provider response label is authority.

`review_gate` is platform-derived and has:

- `state`: `CLEAR`, `REVIEW_REQUIRED`, or `HUMAN_REQUIRED`
- `evidence_refs`: list of immutable/frozen evidence identities where applicable

## 6. Acceptance tests

The implementation must demonstrate at minimum:

1. clean exact qualified scoped WRITE reaches `AUTHORIZED_FOR_ISOLATED_EXECUTION`;
2. provider/model/SKU/deployment-path substitution denies before capability use;
3. qualification epoch drift/revocation/expiry denies;
4. model-authorized-scope widening is retained as violation evidence and cannot authorize execution;
5. revoked/expired capability denies at use time;
6. action widening and artifact widening deny;
7. `HUMAN_REQUIRED` cannot be bypassed by model success or model skip-review request;
8. `REVIEW_REQUIRED` does not execute;
9. RELEASE/DEPLOY/MERGE always return `TERMINAL_AUTHORITY_REQUIRED` in this slice;
10. unsafe model authority attempt remains evidence-eligible when transport/result evidence was otherwise eligible;
11. malformed review-gate state fails closed;
12. clean deterministic replay returns the same decision body for the same inputs.

## 7. Nonclaims

Passing the MVP acceptance suite will not establish production readiness, sandbox security, database crash consistency, network correctness, provider attestation, secret isolation, release safety, or autonomous deployment authority. Existing experiment adjudications retain their own bounded claims and are not widened by this integration.
