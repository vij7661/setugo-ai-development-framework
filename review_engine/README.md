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
  -> R1 interpreter/builder + structured epistemic review
  -> platform Truth & Veracity Contract + evidence-correspondence evaluation
  -> platform risk/review decision
     -> direct finalization when bounded policy permits
     -> blinded R2 detection when review is required
        -> finalization only if no material finding remains
        -> scoped R1 revision when material findings remain
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

A material finding already attached to the current R1 artifact is not erased merely because R2 omits the same finding. The artifact must be revised, the platform evidence state must change, or the workflow must fail to human review.

## Truth & Veracity Contract (TVC-1)

Reviewer reasoning is decomposed into four separate epistemic dimensions rather than one vague confidence judgment:

- **Correspondence** — whether empirical claims have admissible evidence or remain explicitly unsupported/unverified.
- **Coherence** — whether the artifact is internally consistent or contains unresolved contradictions.
- **Pragmatic utility** — whether a proposal is operationally viable; usefulness never overrides factual/logical/governance defects.
- **Semantic precision** — whether the response cleanly distinguishes empirical facts, logical claims, definitions, inferences, assumptions, hypotheses, opinions and recommendations.

The implemented provider adapters require a structured `epistemic_review` object in model JSON. An empirical claim marked `SUPPORTED` must include at least one evidence handle. That remains only a structural requirement; the model cannot certify evidence correspondence by naming a source.

Explicit TVC failures are converted into platform-visible findings. Unsupported/unverified **material empirical facts**, reported contradictions and materially misleading semantic presentation cannot be silently ignored just because the model omitted a matching free-form finding.

R1 self-reported material truth/veracity failures force independent review. `EXPERIMENTAL_UNQUALIFIED` mode cannot clear such an escalation. Agreement between R1/R2/R3 remains evidence only and never establishes truth or action authority.

## Evidence Correspondence Validator

`evidence_correspondence.py` closes the specific gap between **having an evidence reference** and **having retained evidence that supports the exact claim**.

A retained correspondence attestation is bound to:

- exact artifact SHA-256,
- normalized claim-text fingerprint,
- evidence reference,
- exact evidence-content SHA-256 snapshot,
- verifier identity and provenance,
- optional verifier qualification reference.

The reference registry returns one of:

- `VERIFIED_SUPPORT`
- `VERIFIED_CONTRADICTION`
- `CONFLICT`
- `INSUFFICIENT`
- `UNVERIFIED`

For a material empirical claim that a reviewer labels `SUPPORTED`, anything other than `VERIFIED_SUPPORT` becomes a platform-visible `TVC-EVIDENCE-CORRESPONDENCE` finding. A fake handle, stale artifact, rephrased claim, insufficient attestation or conflicting retained evidence therefore cannot be converted into verified correspondence by model assertion alone.

The validator is constructor-injected at the trusted application boundary and has no public HTTP write surface in the MVP. Models and arbitrary API callers cannot add correspondence attestations through review JSON.

This control is **not a semantic truth oracle**. The reference registry does not itself decide whether source text entails a claim; it evaluates independently retained attestations. A future evidence/source service must authenticate source snapshots, verifier identity, qualification and provenance before admitting those attestations.

## Reviewer independence

Whenever R2 is required, its `foundation_lineage` must differ from R1. Whenever R3 is required, it must differ from both R1 and R2. Cross-model agreement is evidence and never release/action authority.

## No-ground-truth Judge Health Monitor

`judge_health.py` adds a conservative logical-consistency alarm for retained judge decisions when the answer key is unknown.

For two judges evaluated on the same `Q` single-label tasks, if both are required to have accuracy at least `a` against the same unknown answer key, they cannot disagree on more than `2 * (1-a) * Q` tasks. If observed disagreements exceed that bound, the platform can conclude only that **both judges cannot simultaneously satisfy the configured accuracy requirement**.

Monitor states remain deliberately non-certifying:

- `INSUFFICIENT_DATA`
- `NO_LOGICAL_ALARM`
- `LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET`

`NO_LOGICAL_ALARM` is intentionally not called `HEALTHY`, `CORRECT` or `ALIGNED`. Agreement cannot establish correctness without ground truth. The monitor also cannot identify which judge is wrong. It is a qualification/monitoring alarm, not a release gate or correctness oracle.

### Judge identity binding

Judge-health observations now require a platform-bound `JudgeIdentityBinding` by default. The monitor derives the judge identifier from provider + model + SKU + deployment path + role + foundation lineage + qualification reference + qualification epoch instead of trusting a free-form or model self-reported name.

- a forged `judge_id` that does not match its binding is rejected;
- two aliases for the same provider/model/SKU/deployment path are not counted as two judges;
- same-foundation-lineage pairs can still be analyzed by the mathematical disagreement bound, but the report emits an explicit correlation warning.

This is stronger bookkeeping identity, not universal runtime cryptographic attestation. Provider-side runtime identity proof remains an integration boundary.

## Qualification / assurance modes

- **GOVERNED**: retained qualification records are present and each invoked reviewer must match provider + model + SKU + deployment path + role + foundation lineage + risk + task scope.
- **EXPERIMENTAL_UNQUALIFIED**: no retained qualification evidence is configured. This mode is intentionally capped to bounded R1-only low-risk review. Any condition that requires independent R2, consequential/mutation/external review, high uncertainty, authoritative ambiguity, incomplete evidence, or a material Truth & Veracity escalation fails closed to `HUMAN_REQUIRED`.

The multi-provider example configuration intentionally contains no qualification records and therefore runs only in `EXPERIMENTAL_UNQUALIFIED` mode until real retained qualifications are added.

## Shared memory

Memory is typed and versioned rather than a raw shared chat log. Records have lifecycle states (`ACTIVE`, `SUPERSEDED`, `REVOKED`, `HISTORICAL`, `PENDING`). Model-private reasoning and protected experimental truth are never compiled into another reviewer's context. Ambient `REVIEW_EVIDENCE` is also excluded from all reviewer context phases; the exact frozen prior reviews needed for R3 adjudication are supplied explicitly instead. Authoritative memory can only be advanced by external/platform authority.

## Evidence and artifact binding

The MVP session ledger is append-only at the application API and hash-linked. A request/session identifier represents one lifecycle: duplicate `REQUEST_RECEIVED` events are rejected and `FINAL_DECISION` seals the session. The hash chain is tamper-evident, not externally immutable against privileged database rewrite.

Reviewer response `artifact_hash` binding is **platform-side bookkeeping integrity**: the provider adapter binds a response to the artifact hash in the platform-created context, and the orchestrator rejects mismatches. It is not a cryptographic reviewer attestation that proves the model semantically analyzed that exact content.

Structured epistemic review evidence, TVC-derived findings and evidence-correspondence assessments are retained with stage evidence. This improves auditability but does not make model statements authoritative or make the evidence store externally immutable.

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
- The correspondence registry consumes retained verifier attestations; it does not independently solve semantic entailment from arbitrary source text.
- Claim extraction/classification completeness remains a reviewer + independent-review problem; a model could still misclassify or omit a truth-bearer unless another control detects it.
- Judge-health `NO_LOGICAL_ALARM` does not establish correctness or alignment.
- Same foundation lineage is a correlation warning, not proof of shared training data or identical reasoning.
- The platform still needs authenticated tool-state integration before it can claim independently verified execution consequences.

Future experiments should exercise this package end-to-end rather than adding isolated experiment-only orchestration paths.
