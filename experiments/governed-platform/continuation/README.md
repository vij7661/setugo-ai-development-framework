# Continuation Controller (MVP)

Purpose: prevent routine CI/environment failures from turning into user-managed stop points.

## Contract

Terminal execution event -> verify exact SHA -> collect evidence -> classify -> authority gate -> scoped repair/continue -> regression -> next event.

The controller itself is deterministic and provider-independent. It does not grant corrective authority merely because a run failed.

### Decisions

- `CONTINUE`: execution succeeded; proceed to evidence adjudication/next governed step.
- `DIAGNOSE`: collect logs and classify using the five-class failure taxonomy.
- `REQUEST_HUMAN`: only for unresolved requirements, explicit manual QA/security/business/credential decisions, unsafe states, or exhausted bounded repair attempts.
- `IGNORE`: event is stale/non-terminal/not authoritative.

### Corrective authority

Classification determines permissible artifact scope. Example: an `ENVIRONMENT-TOOLING DEFECT` may authorize workflow/runner/config changes, but never production code, tests, fixtures, requirements, or protected truth merely to make CI green.

Every repair must rerun the original failing check and affected regression checks at an exact SHA. A green workflow is execution evidence, not automatically a scientific PASS.

## MVP boundary

This commit establishes durable state and deterministic continuation decisions. The next slice connects GitHub terminal events/log collection to the controller and a provider-independent repair-agent adapter. Protected experiment truth remains outside public CI.
