# TESTING Qualification Boundary Independent Re-falsification — Repair Preregistration 007

Status: `FROZEN_BEFORE_REPAIR`
Authority effect: `NONE_EVIDENCE_ONLY`
Scientific subject: exact merged TESTING candidate `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`.

## Trigger
A user-relayed independent DeepSeek re-falsification returned `CHANGES_REQUIRED` with six concrete findings. Before any mechanism repair, this preregistration freezes the acceptance conditions for the next repair lineage.

## Frozen repair requirements
1. Terminal authority authorization must consume a trusted authority binding and exact candidate SHA; naked issuer/provenance/current booleans are evidence only.
2. The authoritative trust-root identity and policy identity used to judge a candidate must have an anchor outside the candidate-modifiable revision. Candidate-local mirrors may be checked but cannot be authoritative by themselves.
3. The qualification check accepted by branch governance must not be satisfiable solely by changing candidate-controlled workflow/test files while preserving a check-name string.
4. External-root lifecycle assumptions must be explicit. Repository archival is evidence/control state, not a claim of cryptographic immutability.
5. A policy hash computed only from candidate-controlled material cannot authorize adoption of that material. The accepted policy identity/hash must be independently anchored.
6. Rule-to-phase ownership for TESTING-blocking classification must be independently anchored or otherwise enforced so candidate-local remapping cannot lower the current phase floor.
7. Unknown or unavailable authoritative external anchor evidence fails closed.
8. All first RED/failure evidence must be preserved. No repair may rewrite the `2fee17ad...` review disposition as PASS.
9. Green CI, reviewer/model PASS, archived-repository state, or successful signature verification is evidence only and grants no TESTING/RELEASE/PRODUCTION authority.
10. TESTING review remains manual-only; no external reviewer API is introduced by this repair.

## Frozen adversarial cases
- `R7-01`: naked terminal-authority role + booleans must fail closed without signed exact-SHA authority binding.
- `R7-02`: simultaneous candidate-local root repository/ID/commit/fingerprint replacement plus recomputed local policy hash must fail closed against the authoritative external anchor.
- `R7-03`: candidate workflow/test body replaced with unconditional success while retaining `falsify-qualification-boundary`; this must not satisfy authoritative qualification.
- `R7-04`: external root unarchived/missing/rebound; authoritative verification must fail closed.
- `R7-05`: candidate-local policy material changed and hash recomputed without external governance authorization; must fail closed.
- `R7-06`: candidate remaps `TESTING_QUALIFICATION_BOUNDARY_OWNERSHIP` to RELEASE; phase disposition must still block TESTING.

## Nonclaims
This preregistration does not prescribe a specific vendor mechanism and does not itself prove GitHub administration immutable. It freezes the security property: the evaluated candidate must not be able to redefine the authority, trust root, policy, phase map, or required-check mechanism that qualifies that same candidate.
