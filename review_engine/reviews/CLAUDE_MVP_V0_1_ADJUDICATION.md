# Claude MVP v0.1 Adjudication

Reviewed external report: Claude independent adversarial review of frozen Review Engine MVP v0.1 at `5fda61c3078c80ac0d607f546f40db316f2c9b6d`.

This document records platform-side adjudication before remediation. Claude findings are evidence, not authority.

## Adjudication

| Finding | External severity | Platform classification | Disposition |
| --- | --- | --- | --- |
| R-01 reviewer severity/material self-report mismatch | CRITICAL | REAL CODE DEFECT / CORE TRUST GAP | Remediate now. Platform-owned effective materiality must treat HIGH/CRITICAL findings as material even if reviewer says `material=false`; preserve reviewer raw flag separately in evidence. |
| R-02 caller-controlled `operation_class` / tools / target | CRITICAL | DESIGN GAP + CONTRACT OVERCLAIM | Remediate trust model now. HTTP user fields are declarations, not platform facts. Separate server-owned execution envelope from caller declarations; because v0.1 executes no actions, server envelope remains review-only/no-tool. Caller declarations may only escalate. Add conservative text consequence hints and document that full semantic action classification requires authenticated platform/tool state. |
| R-03 missing R1/R2 lineage check | HIGH | REAL CODE DEFECT | Remediate now. Whenever R2 is required, R2 must be foundation-lineage independent from R1. Whenever R3 is required, R3 must be independent from both R1 and R2. |
| R-04 unqualified mode permits consequential governed flow | CRITICAL | REAL DESIGN GAP | Remediate now. `EXPERIMENTAL_UNQUALIFIED` may only complete bounded R1-only low-risk review. Any condition requiring R2 or consequential/mutation/external routing fails closed to `HUMAN_REQUIRED`. |
| R-05 client-controlled request/session identifier reuse | HIGH | REAL CODE DEFECT | Remediate now. A second `REQUEST_RECEIVED` for an existing session must be atomically rejected; no evidence-chain conflation. Idempotent replay can be added later. |
| R-06 artifact hash is platform-side bookkeeping, not reviewer attestation | MEDIUM | INTEGRATION BOUNDARY / DOCUMENTATION OVERCLAIM | Clarify wording and add explicit regression around non-conformant mismatched responses. Do not represent this as cryptographic reviewer attestation. |
| R-07 `REVIEW_EVIDENCE` leaks through R3 phase B if future-populated | LOW | LATENT CODE DEFECT + TEST GAP | Remediate now for consistency; phase B must filter shared review-evidence memory because explicit frozen prior reviews are passed separately. |
| R-08 SQLite contention / retry behavior | MEDIUM | ROBUSTNESS GAP / NEEDS LOAD EVIDENCE | Harden now with explicit busy timeout and concurrency regression. Keep single-node limitation explicit. |
| R-09 Anthropic retries without backoff | LOW | REAL ROBUSTNESS DEFECT | Remediate now using bounded backoff and `Retry-After` handling equivalent to OpenAI-compatible provider. |

## Core trust-model decision

The external verdict `REOPEN CORE DESIGN` is accepted in a bounded sense: the frozen v0.1 trust model is not retained as-is. We are not discarding the R1/R2/R3 architecture. We are reopening the governance-critical signal ownership rules and then revalidating the whole vertical slice.

### Signal ownership after remediation

1. **Server/platform execution envelope**: route-owned, tool-registry-owned, environment-owned facts. Models and arbitrary HTTP callers cannot lower these.
2. **Caller declarations**: may increase review conservatism, but never count as independently verified platform facts.
3. **R1 interpretation**: may only escalate risk/materiality/uncertainty/ambiguity; never lower platform/caller floors.
4. **Reviewer finding materiality**: reviewer raw flags are evidence; platform computes effective materiality with a minimum severity mapping.
5. **Qualification and independence**: required review stages count only when matching qualification evidence exists and lineage-independence constraints hold.
6. **Action authority**: remains disabled in MVP v0.1.x; convergence is not action authorization.

## Remediation gate

Do not resume system-level experiments until:

- all confirmed/accepted findings above have regression coverage,
- the full Review Engine + governed-platform harness is exact-head green,
- README/packet wording matches implemented guarantees,
- a second adversarial review or targeted re-review confirms R-01/R-02/R-03/R-04/R-05 are closed.
