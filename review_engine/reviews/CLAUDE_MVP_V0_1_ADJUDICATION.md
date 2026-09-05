# Claude MVP v0.1 Adjudication

Reviewed external report: Claude independent adversarial review of frozen Review Engine MVP v0.1 at `5fda61c3078c80ac0d607f546f40db316f2c9b6d`.

Claude findings are external evidence, not authority. Each finding was independently checked against the frozen source before remediation.

## Adjudication and remediation

| Finding | External severity | Platform classification | Remediation status |
| --- | --- | --- | --- |
| R-01 reviewer severity/material self-report mismatch | CRITICAL | REAL CODE DEFECT / CORE TRUST GAP | REMEDIATED. Platform computes effective finding materiality; HIGH/CRITICAL findings cannot be hidden by `material=false`. Raw reviewer flag retained separately. |
| R-02 caller-controlled `operation_class` / tools / target | CRITICAL | DESIGN GAP + CONTRACT OVERCLAIM | REMEDIATED FOR MVP BOUNDARY. Added trusted application `PlatformExecutionEnvelope`; caller fields are explicit untrusted declarations that may only raise conservatism. Qualification task type comes from the trusted envelope. Conservative request-text consequence hints can raise the floor. Full authenticated tool/environment provenance remains a declared integration boundary. |
| R-03 missing R1/R2 foundation-lineage check | HIGH | REAL CODE DEFECT | REMEDIATED. Required R2 must differ from R1; required R3 must differ from both R1 and R2. |
| R-04 unqualified mode permits consequential governed flow | CRITICAL | REAL DESIGN GAP | REMEDIATED. `EXPERIMENTAL_UNQUALIFIED` is capped to bounded R1-only low-risk review. Any condition requiring independent review, ambiguity, or incomplete evidence fails closed to `HUMAN_REQUIRED`. |
| R-05 client-controlled request/session identifier reuse | HIGH | REAL CODE DEFECT | REMEDIATED. Duplicate `REQUEST_RECEIVED` is rejected atomically and `FINAL_DECISION` seals the session. Idempotent replay remains future work rather than silent chain reuse. |
| R-06 artifact hash is platform-side bookkeeping, not reviewer attestation | MEDIUM | INTEGRATION BOUNDARY / DOCUMENTATION OVERCLAIM | REMEDIATED AS GUARANTEE CLARIFICATION. README now states platform-side bookkeeping rather than reviewer attestation; non-conformant hash mismatch regression added. |
| R-07 `REVIEW_EVIDENCE` leaks through R3 phase B if future-populated | LOW | LATENT CODE DEFECT + TEST GAP | REMEDIATED. Ambient `REVIEW_EVIDENCE` is filtered from every reviewer context, including R3 phase B; frozen prior reviews are passed explicitly. |
| R-08 SQLite contention / retry behavior | MEDIUM | ROBUSTNESS GAP / NEEDS LOAD EVIDENCE | HARDENED. Explicit 30s busy timeout + WAL added to memory/evidence stores; concurrent evidence-writer regression added. Single-node/distributed limitation remains explicit. |
| R-09 Anthropic retries without backoff | LOW | REAL ROBUSTNESS DEFECT | REMEDIATED. Bounded exponential backoff + jitter and `Retry-After` support added with regression coverage. |

## Core trust-model decision

The external verdict `REOPEN CORE DESIGN` was accepted in a bounded sense: the frozen v0.1 trust model was not retained as-is. The R1/R2/R3 architecture remains, but governance-critical signal ownership was changed and the vertical slice revalidated.

### Signal ownership after remediation

1. **Server/platform execution envelope**: application-owned route/tool/environment/task facts. Models and arbitrary HTTP callers cannot lower these.
2. **Caller declarations**: may increase review conservatism, but never count as independently verified platform facts.
3. **Request-text consequence hints**: deterministic conservative floor only; not a complete semantic-intent classifier.
4. **R1 interpretation**: may only escalate risk/materiality/uncertainty/ambiguity; never lower earlier floors.
5. **Reviewer finding materiality**: reviewer raw flags are evidence; platform computes effective materiality with a minimum severity mapping.
6. **Qualification and independence**: required review stages count only when matching qualification evidence exists and lineage-independence constraints hold.
7. **Action authority**: remains disabled in MVP v0.1.x; convergence is not action authorization.

## Remediation validation baseline

Remediation implementation head:

`40d2e3012d6bd974f0ea897ba9e22f4c5ff0d086`

Exact-head workflow:

- Workflow: `Governed Platform + Review Engine Harness`
- Run: `33980165263`
- Result: `SUCCESS`
- Review Engine system regressions: SUCCESS
- Scorer regressions: SUCCESS
- Runner regressions: SUCCESS
- Protected-truth regressions: SUCCESS
- Observability regressions: SUCCESS
- Continuation-authority regressions: SUCCESS
- Governor falsification regressions: SUCCESS

The green run is verification evidence for this remediation head; it is not production/release authorization.

## Remaining remediation gate

System-level experiments remain paused until a targeted independent re-review checks the governance-critical closure claims for **R-01 through R-05** against this remediated source. If the re-review identifies a valid residual/bypass, reopen that finding and add another regression before experimentation.
