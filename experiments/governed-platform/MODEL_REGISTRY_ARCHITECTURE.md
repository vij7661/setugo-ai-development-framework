# Governed Platform — Model & Execution-Path Registry Architecture

Status: **Architecture Candidate**

The Model Registry is a platform-owned control-plane service. Its purpose is not to rank a globally “best” model. It answers a narrower question:

> Is this exact execution path currently eligible for this role, task class, risk/privacy/policy scope, and evidence purpose?

## 1. Identity layers

The registry separates four concepts that must not be collapsed.

### Provider identity
Examples: OpenAI, Anthropic, Google, Groq, OpenRouter, Mistral.

Provider identity describes the contractual/API counterparty. It does not identify the exact model path.

### Model identity
The provider-facing model identifier/family requested by the platform.

Returned response labels are runtime metadata only and do not prove the serving identity.

### Offering / SKU identity
A concrete commercial/technical offering where relevant: free tier, paid SKU, hosted endpoint class, dedicated deployment, region, context/tool profile or versioned serving product.

### Execution-path identity
The exact platform-relevant route through which execution occurs.

This must capture material differences such as:
- direct provider vs aggregator;
- deployment/endpoint;
- project/account provenance class;
- region/tenant class where it affects privacy or routing;
- provider routing mode;
- free vs paid route when behavior/capacity differs;
- tool/API mode;
- privacy/logging mode;
- any routing alias or fallback policy that can change the actual serving path.

Raw account IDs/API keys are not registry evidence. Use an opaque `execution_path_class` or internal path ID whose mapping is protected inside the control plane.

## 2. Route record

Recommended conceptual record:

```json
{
  "route_id": "route_openrouter_nemotron_free_primary",
  "provider": "openrouter",
  "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
  "sku": "free",
  "deployment_path": "openrouter-chat-completions",
  "execution_path_class": "or-account-path-A/free-default-routing",
  "foundation_lineage": "nemotron-3-ultra",
  "privacy_class": "EXTERNAL_PROVIDER_STANDARD",
  "enabled": true
}
```

`execution_path_class` is platform-internal and must not expose secrets or personally identifying account metadata.

## 3. Qualification is scoped, not attached to the model globally

One route may be qualified for Builder work but not Security Judge work. Qualification records therefore bind:
- route ID;
- role;
- task class;
- risk tier or maximum risk tier;
- privacy class;
- policy hash/version;
- tool mode where material;
- evidence purpose;
- qualification evidence reference;
- qualification epoch;
- qualified/expired/revoked state;
- expiry/requalification date.

Examples of roles:
- Builder
- Architecture Reviewer
- Requirements Reviewer
- Security Reviewer
- Test Judge
- Researcher
- R1
- R2
- R3
- Adjudicator candidate

A route can hold multiple independent qualifications.

## 4. Candidate discovery vs production eligibility

External/public evidence can populate `candidate_sources`, for example:
- public benchmarks;
- vendor capability documentation;
- leaderboards;
- community/research reports.

These sources may justify running a qualification suite. They do **not** set `QUALIFIED`.

Production eligibility requires retained internal evidence from the platform’s qualification suite for the relevant role/task/risk scope.

## 5. Qualification lifecycle

Recommended states:
- `CANDIDATE`
- `QUALIFICATION_PENDING`
- `QUALIFIED`
- `SUSPENDED`
- `EXPIRED`
- `REVOKED`
- `REQUALIFICATION_REQUIRED`

Transitions are platform-owned.

A qualification epoch increments whenever a material qualification binding changes or a route is requalified. Evidence produced under an older epoch may become inadmissible under current-policy decisions where freshness is required.

## 6. Operational runtime state is separate

A route can be `QUALIFIED` and simultaneously `UNAVAILABLE`.

Runtime availability states:
- `AVAILABLE`
- `DEGRADED`
- `RATE_LIMITED`
- `QUOTA_EXHAUSTED`
- `PROVIDER_OUTAGE`
- `CREDENTIAL_ERROR`
- `POLICY_BLOCKED`
- `UNKNOWN`

Runtime state fields should include:
- availability status;
- last checked/observed time;
- last success/failure;
- normalized error class;
- quota source/class;
- quota remaining if observable;
- reset time if observable;
- rate-limit window;
- capacity class;
- health evidence ref.

Pilot 8 is the canonical example: the OpenRouter route remained reasoning-qualified while daily free-model quota made it operationally unavailable.

## 7. Eligibility equation

A route may be selected only when all required dimensions are true:

`ROUTABLE = QUALIFIED_CURRENT ∧ ROLE_MATCH ∧ TASK_MATCH ∧ RISK_MATCH ∧ POLICY_MATCH ∧ PRIVACY_MATCH ∧ PATH_CURRENT ∧ OPERATIONALLY_AVAILABLE`

Additional constraints may apply:
- reviewer independence;
- cost ceiling;
- latency ceiling;
- geographic restrictions;
- tool support;
- context capacity;
- experiment frozen-route binding.

## 8. Failover policy

Failover candidates must be determined before execution where practical.

A candidate is not valid failover merely because:
- it uses the same provider;
- it has a similar model name;
- the provider claims it is equivalent;
- it returns a successful response;
- it has higher public benchmark scores.

For normal product execution, failover requires a current qualification compatible with the original route’s role/task/risk/privacy/policy contract.

For controlled experiments, substitution rules are stricter: a provider/model/path change after results are observed does not enter the primary endpoint unless pre-registered.

## 9. Account/path equivalence

Two API keys can be treated as operationally interchangeable only when they resolve to the **same already-qualified execution path** or when an explicit equivalence qualification proves the material path is the same.

Potential equivalence dimensions:
- provider account/project configuration;
- model availability/routing policy;
- privacy/logging setting;
- region;
- free/paid tier;
- fallback policy;
- provider-side preferences;
- tool access;
- quota pool/source;
- data-retention configuration.

A different account is therefore a different provenance path by default, not an invisible credential rotation.

Same-account key rotation may retain the same path identity when the key is only a credential for an unchanged qualified account/project/routing configuration.

## 10. Runtime identity and attestation

The platform should preserve:
- configured route/model identity;
- request endpoint/path;
- platform route ID;
- provider response model claim;
- provider response metadata;
- request/response timestamps;
- out-of-band attestation evidence when available.

The provider response model claim is not accepted as authority for route identity.

Future stronger mechanisms to investigate:
- provider-signed response identity;
- dedicated deployment IDs;
- endpoint-bound attestations;
- cloud workload/service identity;
- mutually authenticated provider gateways;
- provider audit/log APIs with signed or independently fetched execution records.

## 11. Reviewer independence

The registry tracks at least two independent diversity dimensions.

### Execution-path diversity
Different provider/deployment/path.

### Foundation-lineage diversity
Different underlying model/foundation lineage.

High-risk policy may require both.

Example: the same foundation model exposed directly and through an aggregator provides path diversity but not foundation independence.

## 12. Evidence binding

Every model-generated evidence record should bind:
- route ID;
- provider;
- configured model;
- SKU;
- deployment path;
- execution path class or opaque ID;
- qualification ID;
- qualification epoch;
- policy hash;
- execution ID;
- response model claim as non-authoritative metadata.

If qualification is revoked or path identity materially changes, evidence admissibility is re-evaluated according to evidence-retention policy.

## 13. Routing policy

After hard eligibility filters, a versioned routing policy may optimize among eligible routes using measured dimensions such as:
- qualification score by task dimension;
- historical false-green rate;
- false-positive rate;
- authority-safety behavior;
- latency;
- cost;
- reliability;
- quota headroom;
- context/tool capability.

Do not combine these into one opaque global “model score” unless the weighting is itself explicit, versioned and justified for the task.

Prefer a constrained selection approach:
1. establish hard eligibility;
2. satisfy independence/policy constraints;
3. optimize operational objectives among eligible routes.

## 14. Route snapshot at execution time

When execution starts, persist an immutable route snapshot with:
- route identity fields;
- qualification ref/epoch;
- runtime eligibility state observed at selection;
- routing policy version;
- selection reason;
- failover candidates authorized at selection if any.

Immediately before provider invocation, revalidate current qualification/path state. Runtime availability may have changed since route selection.

## 15. Registry APIs

Candidate administrative API:
- `POST /registry/routes`
- `PATCH /registry/routes/{route_id}`
- `POST /registry/routes/{route_id}/qualifications`
- `POST /registry/qualifications/{id}/revoke`
- `POST /registry/qualifications/{id}/requalify`
- `POST /registry/routes/{route_id}/runtime-observations`
- `GET /registry/routes`
- `GET /registry/routes/{route_id}`
- `GET /registry/routes/{route_id}/qualifications`
- `POST /routing/select`

`POST /routing/select` returns a route decision/snapshot, not a capability or mutation authority.

## 16. Dashboard view

For each route display separately:
- qualified roles/task classes;
- qualification freshness/expiry;
- privacy class;
- foundation lineage;
- execution path class (safe display alias);
- operational availability;
- quota/capacity status;
- last provider success/failure;
- recent measured quality dimensions;
- evidence refs supporting qualification.

Avoid a single green/red “model working” indicator because it conflates reasoning qualification with runtime availability.
