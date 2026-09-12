### A. Review-context contamination check
`CLEAN_PACKET_ONLY_CONTEXT`

### B. Review-evidence declaration
`AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

### C. Program-level disposition
`CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`

The family shows useful bounded reference-mechanism evidence and preserves RED history, but it is not yet sufficient for governed impact adjudication. The executable full-coverage harness was added after the first mechanism existed, the tests mostly exercise a shared in-memory module via status-string assertions, and no production/V18/live-harness integration evidence is present. Several candidate requirements are directionally useful but need narrowing before adoption.

### D. Per-experiment assessment

#### EXP-ECC-1 — Enforcement Execution Attestation
- **Impact recommendation:** `NARROW_REQUIREMENT_CANDIDATE`
- **Strongest supported claim:** The reference model can reject missing, mismatched, stale, non-authoritative, or non-recorded control-execution events and can distinguish `CONFIGURED` from `VERIFIED`.
- **Strongest unsupported/overclaimed claim:** It does not prove that a live hook, gate, adapter, or runtime control actually executed. The test event is a caller-supplied dictionary.
- **Concrete false-green path:** Provide an `event` dict with matching control ID/version/digest, correct candidate/action, `started=True`, `result_recorded=True`, `execution_ok=True`, and syntactically valid digests. The reference returns `VERIFIED`.
- **Missing evidence/test:** Trusted hook-side execution receipt, signed or platform-attested event provenance, time-of-check/time-of-use binding to the governed action, live harness invocation.
- **Narrow required change:** Require platform-attested execution receipts from the enforcement point, not worker-populated event records.

#### EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence
- **Impact recommendation:** `NARROW_REQUIREMENT_CANDIDATE`
- **Strongest supported claim:** A reference equivalence checker can reject obvious declared/executable mismatches in fixture dictionaries.
- **Strongest unsupported/overclaimed claim:** It does not inspect executable code or runtime semantics. A fail-open wrapper, undocumented disable flag, alternate path, or generated documentation can remain stronger than the actual executable.
- **Concrete false-green path:** The executable profile dict says `mode=BLOCKING`, `on_internal_error=DENY`, but the real implementation catches errors and allows. The checker compares only the dict.
- **Missing evidence/test:** Static or dynamic extraction of real enforcement semantics, multi-path code inspection, environment-flag detection, generated-doc comparison, runtime failure injection.
- **Narrow required change:** Bind the executable profile to machine-verified code/runtime behavior rather than to a declaration dictionary.

#### EXP-ECC-3 — Qualified Harness Capability Envelope
- **Impact recommendation:** `NARROW_REQUIREMENT_CANDIDATE`
- **Strongest supported claim:** The reference can model stale harness qualification, role-binding changes, and insufficient capability classes.
- **Strongest unsupported/overclaimed claim:** The global ordinal `NATIVE > ADAPTER > INSTRUCTION > REFERENCE` is not generally valid. Capabilities may be incomparable, e.g., native file confinement versus adapter-backed network denial.
- **Concrete false-green path:** A capability envelope claims `NATIVE_ENFORCEMENT` for a surface without external attestation. The reference accepts the envelope as data.
- **Missing evidence/test:** Per-capability dimensions, gateway/harness identity attestation, downgrade detection, incomparable capability cases, live harness qualification.
- **Narrow required change:** Replace global ranking with per-capability qualification matrices and require attestable harness/runtime identity.

#### EXP-ECC-4 — Capability / Power-Surface Activation Consent
- **Impact recommendation:** `NARROW_REQUIREMENT_CANDIDATE`
- **Strongest supported claim:** The reference can enforce exact manifest digest, role, power, resource, expiry, and revocation checks for activation fixtures.
- **Strongest unsupported/overclaimed claim:** It does not distinguish authenticated principal authority from a mere approval record. Consent can still be mistaken for authorization if the approval object is self-asserted.
- **Concrete false-green path:** An `approval` dict with `approved=True`, matching `manifest_digest`, `role`, and approved powers passes without proof of the approving principal.
- **Missing evidence/test:** Authenticated approver identity, authority issuance, revocation propagation, TOCTOU between approval and activation, cross-project replay.
- **Narrow required change:** Require a platform-issued authenticated activation record bound to exact manifest, principal, scope, and sequence.

#### EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift
- **Impact recommendation:** `NARROW_REQUIREMENT_CANDIDATE`
- **Strongest supported claim:** The reference can compare canonical fields and mark dependent qualifications stale on configured drift.
- **Strongest unsupported/overclaimed claim:** It does not prove cryptographic attestation, secret-safe canonicalization, or complete runtime state. Digest collision or redaction collision can merge materially different configs.
- **Concrete false-green path:** Two different MCP endpoints or credential profiles are represented with the same `canonical_digest` or `semantic_digest`; the reference treats the configuration as current.
- **Missing evidence/test:** Cryptographic attestation, secret-redaction collision tests, DNS/endpoint rebinding, executable/argv provenance, read-unavailable behavior in live config.
- **Narrow required change:** Require a secret-safe cryptographic configuration attestation and explicit `UNKNOWN` state when configuration cannot be read.

#### EXP-ECC-6 — External Review Egress + Provider-Relationship Binding
- **Impact recommendation:** `DEFER_PENDING_INTEGRATION_EVIDENCE`
- **Strongest supported claim:** The reference can model packet/role/provider/evidence-class binding and keeps AI-generated feedback at zero manual-threshold contribution.
- **Strongest unsupported/overclaimed claim:** It does not prove provider identity, gateway routing, real external reviewer transport, or independent human/manual review.
- **Concrete false-green path:** Set `returned_provider` to a value different from `selected_provider`; the reference returns `DIFFERENT_PROVIDER_CONFIRMED` without cryptographic provider attestation.
- **Missing evidence/test:** Real provider identity attestation, gateway route proof, manual review attestation validation, packet replay, egress consent enforcement.
- **Narrow required change:** Keep transport disabled; require cryptographic provider/gateway identity evidence and separate authenticated manual-review attestation before any manual threshold credit.

#### EXP-ECC-7 — Learned-Artifact Proposal / Promotion Boundary
- **Impact recommendation:** `DEFER_PENDING_INTEGRATION_EVIDENCE`
- **Strongest supported claim:** The reference prevents confidence, consensus, non-correction, or generation success from directly promoting a learned artifact.
- **Strongest unsupported/overclaimed claim:** It does not integrate with an actual learning pipeline, dependency graph, retraction traversal, or independent-support validation.
- **Concrete false-green path:** A proposal dict with `source_verified=True`, `independent_support=True`, and `governed_approval=True` promotes, but those flags are self-asserted in the fixture.
- **Missing evidence/test:** Real claim/dependency graph integration, retraction propagation, session-injection prevention, stale learned artifact detection.
- **Narrow required change:** Reuse existing claim/requirement governance machinery rather than a parallel set of promotion flags.

### E. Cross-experiment coupling / independence assessment
The seven experiments are not fully independent. They share `ecc_governance.py`, share helper factories in the full-coverage harness, and assert statuses returned by the same module. This creates hidden coupling: a single faulty abstraction or status convention can make multiple children appear green. The hypotheses address distinct trust boundaries conceptually, but the executed evidence does not demonstrate independent implementations or independent falsification paths.

### F. Test-design and preregistration assessment
The prose specifications and named cases were preregistered before the first mechanism, which is a positive discipline. However, the full executable 86-case harness was added after the first mechanism existed and immediately produced RED-002. That sequencing materially limits conclusions: the exact executable assertions for each named case were written after the mechanism, allowing post-hoc tailoring. Many tests directly mutate dictionaries and assert exact status strings. This is useful unit-level falsification but weak end-to-end evidence. A stronger design would freeze the exact executable harness before mechanism implementation or reproduce it independently.

### G. RED/repair-history assessment
The preserved RED history is a strength. Construction RED, intermediate nonterminal GREEN, full-coverage RED, full-coverage GREEN, and terminal child results are recorded. The history is sufficient to prevent a purely green-only narrative. It is not sufficient to establish production integration or live enforcement.

### H. Positive-control / overblocking assessment
Positive controls exist and generally check that exact valid fixtures remain live. They are shallow. They do not strongly detect a block-all integrated implementation, because most positives exercise the same in-memory function paths as the negatives. Additional benign-variation and end-to-end liveness tests are needed, especially for integration surfaces.

### I. Production-integration gap assessment
The production-integration gap is large and decisive. The evidence does not prove:
- integration into V18 or the production runtime;
- live execution of third-party hooks, adapters, or harness controls;
- cryptographic provider identity;
- qualified real external reviewer API transport;
- independent human/manual review;
- automatic promotion of any ECC-derived requirement;
- merge/release/deploy/completion authority.

### J. R1/R2/R3 provider-neutral role-binding assessment
The reference preserves the rule that R1/R2/R3 are configurable governed roles, not hardcoded providers/models. The code uses selected model/provider strings and role bindings without provider-specific branches. That is directionally correct. However, live role binding requires attested harness capability envelopes, exact durable binding, and revalidation on substitution. The current evidence is only fixture-level.

### K. External-review/manual-evidence boundary assessment
This review is `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` and contributes zero to any manual-review threshold. EXP-ECC-6’s reference correctly avoids laundering AI feedback into manual review, but it does not validate a real human/manual attestation. The manual-only testing rule remains intact in the packet, and no real external reviewer-model API transport is evidenced.

### L. Missing falsification cases
Additional cases should include:
- EXP-ECC-1: spoofed execution receipt, TOCTOU between verification and action, hook process replacement.
- EXP-ECC-2: real fail-open wrapper, undocumented disable flag, generated documentation stronger than code, multi-path enforcement.
- EXP-ECC-3: incomparable capabilities, gateway/harness identity spoofing, downgrade after qualification.
- EXP-ECC-4: forged approval principal, cross-project consent replay, revocation race, scope widening after approval.
- EXP-ECC-5: canonical/semantic digest collision, secret-redaction collision, DNS/endpoint rebinding, config read failure.
- EXP-ECC-6: provider identity spoofing, gateway route attestation failure, forged manual attestation, packet replay after consent.
- EXP-ECC-7: retraction dependency traversal, self-asserted independent support, stale learned artifact injected into a new session.

### M. Impact-adjudication recommendation
No requirement is ready for automatic adoption or promotion. The strongest candidates for a later governed impact-adjudication step, after narrowing, are EXP-ECC-1, EXP-ECC-2, EXP-ECC-3, EXP-ECC-4, and EXP-ECC-5, but only as narrowed requirement candidates with integration evidence. EXP-ECC-6 and EXP-ECC-7 should be deferred pending integration evidence. None should be promoted by this review.

### N. Freeze recommendation
`DO_NOT_FREEZE_EXPERIMENT_EVIDENCE`

### O. Authority limitation
`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
