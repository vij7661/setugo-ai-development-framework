# EXP-M External Review R2 — Preserved Review

Disposition: `CHANGES_REQUIRED`

This file preserves the user-supplied independent external review used for the R2 remediation. It is evidence/history only and does not itself grant authority.

## Critical findings

### C-01 — Required-evidence authority is not independently closed against an incomplete ReviewRequest

- Severity: Critical
- Affected: review-evidence-delivery-integrity standard — Required-evidence authority; EXP-M M-I04/M-I16; tests M-31/J01-J02.
- False-green path: an incomplete or proposer-mutated ReviewRequest omits a standard-required evidence ref or mandatory dimension. The delivery layer closes against that incomplete request and can report complete delivery even though decisive evidence was never selected.
- Required fix: independently derive mandatory evidence and dimensions from governed standards/experiment contract and cross-check the ReviewRequest. Missing governed refs/dimensions fail before manifest freeze with EVIDENCE_SELECTION_INCOMPLETE.

## High findings

### H-01 — Material review lacks fresh/clean provider-session or full-context binding

- Severity: High
- False-green path: a reused provider thread contains prior ungoverned messages, tool output, cached evidence, custom instructions, memory, or prompt-injection content. Session ID matches but semantic context is dirty.
- Required fix: fresh provider session/thread for material review or governed capture/clear/hash of all pre-existing semantic context. If provider-side mutable context cannot be captured/disabled, mode is NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Add dirty-thread, prior-tool, default-prompt, and memory tests.

### H-02 — Provider capability qualification lacks preregistered statistical criteria

- Severity: High
- False-green path: a small number of lucky near-limit trials widens a capability profile despite intermittent omission/truncation.
- Required fix: preregister minimum fresh trials, acceptable failure rate, confidence/statistical bound, safety margin, nondeterminism handling, and expiry/requalification interval. Add insufficient-trial/flaky qualification tests.

### H-03 — Provider-injected/default semantic context not fully bound

- Severity: High
- False-green path: provider default prompts, memory, or knowledge connectors alter review instructions/evidence basis outside platform wire hashes.
- Required fix: capability profile binds or disables all mutable provider-injected semantic context; unknown mutable context means NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Add default-prompt drift, provider memory, and knowledge-connector tests.

### H-04 — Witness-canary coverage can be too sparse

- Severity: High
- False-green path: provider drops an internal segment between head/middle/tail canaries while all canaries pass.
- Required fix: per-chunk/evidence-boundary dense probes where deterministic truncation semantics are unavailable, or reduce qualified bound to densely probed region. Add internal-gap omission tests.

### H-05 — Test matrix omits adversarial families above

- Severity: High
- Required fix: explicit falsification/mutation tests for incomplete ReviewRequest requiredness, dirty reused sessions, provider-injected semantic context, insufficient qualification trials, and canary-gap omissions.

## Medium/Low findings

### M-01 — Permissive “where available/where applicable” wording

If information is load-bearing for context completeness and unavailable, the provider/mode must fail closed rather than silently treating it as optional.

### M-02 — Decomposition interaction completeness can be proposer-incomplete

Cross-dimension interaction requirements must be independently derived from governed dimensions/standards, not solely proposer-authored.

### M-03 — Capability/egress expiry after final wire call before verdict admission

Add admissibility-time revalidation and tests for capability, egress, and session invalidation after provider response but before verdict acceptance.

## Gate results from review

- REQUIRED_EVIDENCE_AUTHORITY = FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS
- WIRE_BINDING = PASS
- CHUNK_CONTEXT_MODEL = PASS
- REMOTE_ACCESSIBILITY_MODEL = FAIL
- PROVIDER_CAPABILITY_QUALIFICATION = FAIL
- REPRESENTATION_GOVERNANCE = PASS
- MATERIALIZATION_SAFETY = PASS
- EGRESS_BOUNDARY = PASS
- SESSION_FILE_RETRIEVAL_BINDING = FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS
- MULTI_REVIEWER_EQUIVALENCE = PASS
- DECOMPOSITION_AGGREGATION = PASS
- PROMPT_ISOLATION_DEPENDENCY = PASS
- TOCTOU_RETRY_INTEGRITY = PASS
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS
- TEST_MATRIX_SUFFICIENCY = FAIL

## Review conclusion

- Critical defect remained: C-01.
- High defects remained: H-01 through H-05.
- EXP-M was not ready for implementation/falsification as reviewed.
- EXP-M remained NOT QUALIFIED.
- The external/manual review granted no platform-review or promotion authority.
