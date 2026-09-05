# Review Engine MVP

This package is the first product implementation promoted from the governed-platform experiments.

## Product goal

Provide a model-neutral governed review workflow in which a user selects:

- **Reviewer 1 / Interpreter-Builder**: primary model that interprets the request and produces the working artifact.
- **Reviewer 2 / Detector-Challenger**: independently checks material work when the platform Review Decision Engine requires review.
- **Reviewer 3 / Verifier-Adjudicator**: independently evaluates unresolved material disagreement or a material revision before prior reviewer conclusions are disclosed.

The platform owns routing mechanics, context visibility, reviewer eligibility/independence checks, convergence rules and termination. Model proposals and caller declarations are evidence/signals, not governance authority.

## MVP flow

```text
User request
  -> trusted application execution envelope + caller declarations + conservative text floor
  -> R1 interpreter/builder
  -> platform risk/review decision
     -> direct finalization when bounded policy permits
     -> blinded R2 detection when review is required
        -> finalization if no effectively material finding
        -> scoped R1 revision if a material finding is accepted
           -> blinded R3 verification for material change/disagreement
           -> staged disclosure/adjudication
  -> final decision state or HUMAN_REQUIRED
```

## Request trust model

Governance-critical request facts have explicit provenance:

1. **Trusted execution envelope** — supplied by application/platform code, not arbitrary request JSON. In v0.1 the HTTP/CLI service is review-only: `ANALYSIS`, no connected tools, no production target, task type `GENERAL`.
2. **Caller declarations** — `operation_class`, requested target, connected-tool declarations, requested task type, user risk/materiality, etc. These may only increase conservatism; they are not described as independently verified platform facts.
3. **Deterministic request-text hints** — obvious production/release/deploy/mutation wording can raise the review floor. This is conservative coverage, not a complete semantic classifier.
4. **R1 interpretation** — may escalate risk/materiality/uncertainty/ambiguity; it cannot lower earlier floors.

A future authenticated tool/agent system must inject real platform-owned tool grants, environment and task routing into the trusted execution envelope. v0.1 does not claim it can prove hidden/euphemistic consequential intent from text alone.

## Finding materiality

Reviewer-supplied `material` is evidence rather than final authority. The platform computes effective finding materiality. At minimum, `HIGH` and `CRITICAL` findings are treated as material even if a reviewer emits `material=false`. Raw reviewer flags are retained separately in evidence.

## Reviewer independence

Whenever R2 is required, its `foundation_lineage` must differ from R1. Whenever R3 is required, it must differ from both R1 and R2. Cross-model agreement is evidence and never release/action authority.

## Qualification / assurance modes

- **GOVERNED**: retained qualification records are present and each invoked reviewer must match provider + model + SKU + deployment path + role + foundation lineage + risk + task scope.
- **EXPERIMENTAL_UNQUALIFIED**: no retained qualification evidence is configured. This mode is intentionally capped to bounded R1-only low-risk review. Any condition that requires independent R2, consequential/mutation/external review, high uncertainty, authoritative ambiguity or incomplete evidence fails closed to `HUMAN_REQUIRED`.

The multi-provider example configuration intentionally contains no qualification records and therefore runs only in `EXPERIMENTAL_UNQUALIFIED` mode until real retained qualifications are added.

## Shared memory

Memory is typed and versioned rather than a raw shared chat log. Records have lifecycle states (`ACTIVE`, `SUPERSEDED`, `REVOKED`, `HISTORICAL`, `PENDING`). Model-private reasoning and protected experimental truth are never compiled into another reviewer's context. Ambient `REVIEW_EVIDENCE` is also excluded from all reviewer context phases; the exact frozen prior reviews needed for R3 adjudication are supplied explicitly instead. Authoritative memory can only be advanced by external/platform authority.

## Evidence and artifact binding

The MVP session ledger is append-only at the application API and hash-linked. A request/session identifier represents one lifecycle: duplicate `REQUEST_RECEIVED` events are rejected and `FINAL_DECISION` seals the session. The hash chain is tamper-evident, not externally immutable against privileged database rewrite.

Reviewer response `artifact_hash` binding is **platform-side bookkeeping integrity**: the provider adapter binds a response to the artifact hash in the platform-created context, and the orchestrator rejects mismatches. It is not a cryptographic reviewer attestation that proves the model semantically analyzed that exact content.

## API-key rule

Reviewer configuration stores only the **environment/secret name** that contains a provider API key. Raw API keys must never be committed, written to shared memory, review evidence or logs.

## Current boundary

This is an MVP orchestration core, not a production authorization system.

- HTTP is local-only until authentication/tenancy are implemented.
- Action/tool execution is disabled; `CONVERGED_PASS` never authorizes an external/production action.
- SQLite memory/evidence are single-node reference stores, not distributed-consensus proof.
- Hash-linked evidence is not external/WORM immutability.
- Provider runtime identity is not universally cryptographically attested.
- Request-text consequence hints are not complete semantic intent detection.
- The platform still needs authenticated tool-state integration before it can claim independently verified execution consequences.

Future experiments should exercise this package end-to-end rather than adding isolated experiment-only orchestration paths.
