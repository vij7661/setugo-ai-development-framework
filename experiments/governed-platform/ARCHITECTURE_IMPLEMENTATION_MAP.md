# Governed Platform — Architecture Implementation Map

Status: **Working architecture gap map**

This file maps the target product architecture in `ARCHITECTURE.md` to the current experimental repository. `IMPLEMENTED` below means a deterministic experimental implementation exists and is regression-tested; it does not mean production-ready or scientifically proven.

## Status legend

- **IMPLEMENTED-EXPERIMENTAL** — working deterministic implementation/tests exist.
- **PARTIAL** — important mechanism exists, but service/data/runtime integration is incomplete.
- **DESIGNED** — architecture contract exists, but no product implementation yet.
- **MISSING** — required product mechanism has not yet been designed sufficiently.

## 1. Intent and contract plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Authoritative requirement/invariant representation | PARTIAL | `semantic_invariants.py`, case/ground-truth schemas | No persistent production Requirement/Invariant Registry |
| Requirement ambiguity handling | IMPLEMENTED-EXPERIMENTAL | `diagnosis.py`, `governor.py`, Review Decision Engine | Needs product workflow/UI for requirements-owner resolution |
| Artifact taxonomy | PARTIAL | failure-class artifact scopes in governor/diagnosis | Needs versioned extensible product taxonomy |
| Risk/materiality classification | IMPLEMENTED-EXPERIMENTAL | `review_decision_engine.py` | Classification source/approval policy not yet productized |
| Change-impact graph | IMPLEMENTED-EXPERIMENTAL | `impact_graph.py`, `CHANGE_IMPACT.md` | Persistent graph and integration with repository/artifact inventory |
| Intent/contract service | DESIGNED | target architecture only | API, persistence, versioning, ownership and UI missing |

## 2. Governance and orchestration plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Deterministic authoritative governor | IMPLEMENTED-EXPERIMENTAL | `governor.py` | Persistent transactional product service |
| Event-driven continuation | PARTIAL | `continuation/`, `EVENT_CONTINUATION.md` | Production event gateway/webhooks and authenticated event adapters |
| Replay/out-of-order protection | IMPLEMENTED-EXPERIMENTAL | governor + idempotency tests | Needs durable atomic storage at product scale |
| Failure diagnosis routing | IMPLEMENTED-EXPERIMENTAL | continuation diagnosis + governor | Need richer diagnostic evidence model and UI |
| Review escalation | IMPLEMENTED-EXPERIMENTAL | `review_decision_engine.py` | Calibration/policy promotion still experimental |
| Convergence/adjudication | IMPLEMENTED-EXPERIMENTAL | `review_convergence.py`, `tri_reviewer_convergence.py` | Production orchestration and durable reviewer-stage state |
| Manual/human gates | IMPLEMENTED-EXPERIMENTAL | governor/review engine | Product approval identities, permissions and audit UX |
| Budget/retry governance | PARTIAL | review/budget/failover experiments | Unified product budget/cost policy missing |

## 3. Authority and policy plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Capability validation | IMPLEMENTED-EXPERIMENTAL | `capability_guard.py` | Persistent capability service |
| Model claim vs effective authority separation | IMPLEMENTED-EXPERIMENTAL | `authority_binding.py` | General runner/tool integration after frozen Pilot 8 |
| Use-time authorization | IMPLEMENTED-EXPERIMENTAL | `execution_authority.py` | Must wrap all consequential product tool calls |
| Policy binding / policy epochs | IMPLEMENTED-EXPERIMENTAL | `policy_binding.py` | Central Policy Service and policy distribution |
| Capability issuance | DESIGNED | target architecture | Issuer, token/envelope format, signing and lifecycle API |
| Revocation | PARTIAL | guards support revoked/epoch state | Durable revocation store and propagation mechanism |
| Subject/action/artifact scoped permission model | PARTIAL | capability tests | Canonical product permission vocabulary not yet frozen |
| Release/completion authority | PARTIAL | governor completion gate | Dedicated release policy and human approval identities |

## 4. Model qualification and routing plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Task-specific qualification | IMPLEMENTED-EXPERIMENTAL | `qualification_guard.py`, reviewer qualification profile | Persistent qualification registry and qualification jobs |
| Provider+model+SKU+deployment path binding | IMPLEMENTED-EXPERIMENTAL | qualification/failover guards | Extend deployment path to explicit account/execution-path provenance class |
| Fail-closed failover | IMPLEMENTED-EXPERIMENTAL | `failover_guard.py` | Runtime router integration across all providers |
| Out-of-band identity/qualification check | PARTIAL | provider router tests | Strong provider/runtime attestation unavailable |
| Model Registry | DESIGNED | target architecture | Production schema, API, history, admin UX |
| Operational availability | PARTIAL | provider runtime evidence | First-class quota/capacity/health state missing |
| Reasoning qualification vs operational eligibility separation | DESIGNED | target architecture + Pilot 8 quota lesson | Product data model/routing logic missing |
| Account/path equivalence qualification | DESIGNED | target architecture | Need explicit equivalence experiment and registry rule |
| Foundation lineage independence metadata | PARTIAL | reviewer independence tests | Registry lineage data source/maintenance process missing |

## 5. Execution plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Provider adapters | IMPLEMENTED-EXPERIMENTAL | `runner/` OpenAI-compatible/Ollama adapters | Product adapter interface and lifecycle |
| Structured result normalization | IMPLEMENTED-EXPERIMENTAL | runner contracts/normalizers | Unified product event/evidence envelope |
| Tool execution sandbox | MISSING | none as a product boundary | Required before autonomous coding/tool execution |
| Repository write gateway | MISSING | GitHub workflows are experiment infrastructure | Scoped repo mutation service needed |
| Browser/network gateway | MISSING | none | Network egress policies and evidence capture needed |
| Test execution gateway | PARTIAL | CI/test experiments | Product sandbox/test runner abstraction needed |
| Secret manager integration | MISSING | CI secrets only | Production secrets boundary/credential leasing needed |
| Use-time capability wrapper on every consequential adapter | PARTIAL | authority modules exist | General integration deliberately deferred until Pilot 8 closes |

## 6. Evidence and verification plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Tamper-evident evidence chain | IMPLEMENTED-EXPERIMENTAL | `evidence_chain.py` | Durable append-only implementation |
| Evidence retention/invalidation | IMPLEMENTED-EXPERIMENTAL | `evidence_retention.py` | Product evidence index/query service |
| Evidence provenance binding | IMPLEMENTED-EXPERIMENTAL | governor/qualification/policy tests | Canonical cross-service evidence envelope |
| Complementary verification | PARTIAL | EXP-A/F harness | Product verifier registry and dispatch |
| Independent model review evidence | IMPLEMENTED-EXPERIMENTAL | cross-model review | Provider integrations and qualification promotion |
| Immutable artifact storage | DESIGNED | content hashes in harness | Object store + retention/immutability policy |
| Scientific/acceptance evidence separation | PARTIAL | experiment adjudications | Product acceptance policy still to be defined |

## 7. Review and adjudication plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| R1/R2/R3 policy | IMPLEMENTED-EXPERIMENTAL | review decision + tri-review | Threshold calibration/promotion |
| Reviewer blinding | IMPLEMENTED-EXPERIMENTAL | `reviewer_blinding.py` | Product context-builder integration |
| Staged disclosure | IMPLEMENTED-EXPERIMENTAL | EXP-M modules | Durable frozen-review state |
| Reviewer independence | IMPLEMENTED-EXPERIMENTAL | `reviewer_independence.py` | Registry-backed lineage metadata |
| Cross-model sequential review | IMPLEMENTED-EXPERIMENTAL | EXP-G | Claude/DeepSeek/provider extension still desired |
| Human adjudication | PARTIAL | HUMAN_REQUIRED states | Product adjudication UI/workflow |
| Review evidence retention | PARTIAL | evidence chain + frozen artifacts | Unified product evidence service integration |

## 8. Memory and state plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Typed memory classes | IMPLEMENTED-EXPERIMENTAL | `shared_memory_policy.py` | Persistent service + retrieval policy |
| Protected truth isolation | IMPLEMENTED-EXPERIMENTAL | reviewer memory/context tests | Product acceptance data boundary |
| Model-private reasoning exclusion | IMPLEMENTED-EXPERIMENTAL | memory/cross-review policy | Integration across every provider/session |
| Authoritative-memory external write authority | IMPLEMENTED-EXPERIMENTAL | shared memory policy | Capability-service integration |
| Versioned working/project memory | PARTIAL | data model exists | Storage/query/relevance service missing |

## 9. Observability and audit plane

| Capability | Status | Current evidence / module | Main gap |
|---|---|---|---|
| Operational vs scientific status separation | IMPLEMENTED-EXPERIMENTAL | observability tests/dashboard JSON | Product dashboard/UI |
| Execution provenance | PARTIAL | run bindings, qualification metadata | Single normalized product provenance record |
| Unsafe authority-attempt visibility | PARTIAL | authority-binding evidence | Dashboard/event type and alerts |
| Cost/latency tracking | PARTIAL | runner/review efficiency metrics | Unified cost ledger/budgets |
| Quota/capacity visibility | MISSING | only provider failure metadata | Registry/runtime availability service |
| Audit trail | PARTIAL | evidence/event chains | Durable queryable audit service |

## 10. Persistence / infrastructure gaps

The experimental harness is intentionally file/CI-oriented. The product architecture still needs these production boundaries:

1. PostgreSQL schema for project/task/policy/qualification/capability/memory state.
2. Atomic event ledger + authoritative state transition transaction.
3. Durable tamper-evident evidence ledger.
4. Immutable artifact/object store addressed by content digest.
5. Secret manager and short-lived credential leases.
6. Worker/sandbox execution pool.
7. Event gateway/webhook authentication.
8. Queue used only for work dispatch, never authoritative state.
9. Observability pipeline and operator/user dashboard.
10. Backup/restore and disaster-recovery rules that preserve append-only audit semantics.

## 11. Highest-priority architecture work after Pilot 8

### P0 — Wire external authority into the general execution path
Use `authority_binding.py` and `execution_authority.py` around every consequential adapter. Pilot 9 is the behavioral falsification of the stronger design.

### P0 — Define persistent authoritative state + event transaction
The product must atomically record the accepted event/idempotency key and resulting state version before dispatching downstream side effects.

### P0 — Define Model/Execution-Path Registry schema
Include task-specific qualification, role/risk/privacy scope, provider/model/SKU/deployment path, execution-path provenance class, epochs, expiry, revocation, operational quota/capacity and lineage independence.

### P1 — Define canonical evidence envelope
One product evidence schema should bind artifact digest, project/task/execution, policy, capability and qualification lineage.

### P1 — Design sandbox/tool gateway
No model should receive ambient repository, shell, browser or deployment permissions.

### P1 — Productize typed memory/context construction
Reviewer context must be built by policy from typed memory rather than conversation history.

### P1 — Separate release authorization from execution success
Release is a distinct externally authorized state transition with independent evidence requirements.

## 12. MVP boundary recommendation

Build the first backend as a **modular monolith plus isolated worker pool**, not microservices.

Suggested modules inside one transactional backend:
- contracts
- governance
- policy/capabilities
- registry/routing
- evidence
- review
- memory
- change-impact
- observability

Separate process boundary initially:
- sandbox/execution workers

External infrastructure:
- PostgreSQL
- immutable object storage
- secret manager
- queue/event transport

Split services later only when a real boundary appears: independent scaling, security isolation, separate ownership, reliability needs, or regulatory/privacy separation.
