# TESTING Qualification Boundary Independent Re-falsification — Repair Preregistration 007

Status: `FROZEN_BEFORE_REPAIR`
Authority effect: `NONE_EVIDENCE_ONLY`
Scientific subject: exact merged TESTING candidate `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`.

## Trigger

A user-relayed independent DeepSeek re-falsification returned `CHANGES_REQUIRED` with six concrete findings. Before any mechanism repair, this preregistration freezes the acceptance conditions for the next repair lineage.

## Findings under adjudication

- `RF-007-01` CRITICAL — naked terminal-authority inputs (`issuer_class`, `provenance_verified`, `current`) must not authorize without a signed, exact-SHA/policy/scope-bound authority record.
- `RF-007-02` CRITICAL — candidate-local replacement of external root repository identity, repository ID, commit, and key fingerprint must not redirect verification to a candidate-chosen trust root.
- `RF-007-03` CRITICAL — candidate modification of the required-check workflow or falsification harness must not be able to produce a qualified required status merely by retaining the status-context name.
- `RF-007-04` HIGH — external root archival state alone is insufficient as immutability proof; unarchive/rebind/delete/force-mutation assumptions must be explicitly bounded and fail closed where materially relevant.
- `RF-007-05` HIGH — candidate-local changes to qualification policy material plus self-recomputed hash must not create a new self-authorizing policy lineage.
- `RF-007-06` MEDIUM/HIGH — candidate-local remapping of current TESTING governed rules to RELEASE/PRODUCTION must not turn a current material defect into deferred disposition.

## Frozen repair requirements

1. Terminal authority authorization must consume a trusted authority binding and exact candidate SHA; naked issuer/provenance/current booleans are evidence only.
2. The authoritative trust-root identity and policy identity used to judge a candidate must have an anchor outside the candidate-modifiable revision. Candidate-local mirrors may be checked but cannot be authoritative by themselves.
3. The qualification check accepted by branch governance must not be satisfiable solely by changing candidate-controlled workflow/test files while preserving a check-name string.
4. External-root lifecycle assumptions must be explicit. Repository archival is evidence/control state, not a claim of cryptographic immutability.
5. A policy hash computed only from candidate-controlled material cannot authorize adoption of that material. The accepted policy identity/hash must be independently anchored.
6. Rule-to-phase ownership for TESTING-blocking classification must be independently anchored or otherwise enforced so candidate-local remapping cannot lower the current phase floor.
7. Unknown or unavailable authoritative external anchor evidence fails closed.
8. All first RED/failure evidence must be preserved. No repair may rewrite the `2fee17ad...` review disposition as PASS.
9. Green CI, a reviewer/model PASS, archived-repository state, or successful signature verification is evidence only and grants no TESTING/RELEASE/PRODUCTION authority.
10. TESTING review remains manual-only; no external reviewer API is introduced by this repair.

## Frozen adversarial cases

- `R7-01`: call terminal authority with naked `HUMAN_GOVERNANCE_OWNER`, `provenance_verified=True`, `current=True`; must fail closed without signed exact-SHA authority binding.
- `R7-02`: replace all candidate-local external-root constants with an attacker-controlled archived repo/key and recompute candidate-local policy hash; must fail closed against the authoritative external anchor.
- `R7-03`: replace candidate workflow/test body with an unconditional success while retaining `falsify-qualification-boundary`; this must not satisfy the authoritative qualification check.
- `R7-04`: external root reports unarchived/missing/rebound identity; authoritative verification must fail closed.
- `R7-05`: alter candidate-local policy material and recompute its hash without external governance authorization; must fail closed.
- `R7-06`: remap `TESTING_QUALIFICATION_BOUNDARY_OWNERSHIP` to RELEASE in candidate code; phase disposition must still block TESTING.

## Nonclaims

This preregistration does not prescribe a specific vendor mechanism and does not itself prove that GitHub repository administration is immutable. It freezes the security property: the evaluated candidate must not be able to redefine the authority, trust root, policy, phase map, or required-check mechanism that qualifies that same candidate.
