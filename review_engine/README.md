# Review Engine MVP

This package is the first product implementation promoted from the governed-platform experiments.

## Product goal

Provide a model-neutral governed review workflow in which a user selects:

- **Reviewer 1 / Interpreter-Builder**: primary model that interprets the request and produces the working artifact.
- **Reviewer 2 / Detector-Challenger**: independently checks material work when the platform Review Decision Engine requires review.
- **Reviewer 3 / Verifier-Adjudicator**: independently evaluates unresolved material disagreement or a material revision before prior reviewer conclusions are disclosed.

The platform, not any model, owns review routing, context visibility, authority, convergence and termination.

## MVP flow

```text
User request
  -> R1 interpreter/builder
  -> platform risk/review decision
     -> direct finalization when policy permits
     -> blinded R2 detection when review is required
        -> finalization if no material finding
        -> scoped R1 revision if a material finding is accepted
           -> blinded R3 verification for material change/disagreement
           -> staged disclosure/adjudication
  -> final decision state or HUMAN_REQUIRED
```

## Shared memory

Memory is typed and versioned rather than a raw shared chat log. Records have lifecycle states (`ACTIVE`, `SUPERSEDED`, `REVOKED`, `HISTORICAL`, `PENDING`). Model-private reasoning and protected experimental truth are never compiled into another reviewer's context. Authoritative memory can only be advanced by external/platform authority.

## API-key rule

Reviewer configuration stores only the **environment/secret name** that contains a provider API key. Raw API keys must never be committed, written to shared memory, review evidence or logs.

## Current boundary

This is an MVP orchestration core, not a production authorization system. Existing experimental governance controls remain the source of falsification evidence. Future experiments should exercise this package end-to-end rather than adding isolated experiment-only orchestration paths.
