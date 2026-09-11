# TESTING Qualification Boundary R7 — External Enforcement Construction Evidence

Status: `OPEN_AWAITING_PR_AND_EXTERNAL_REFALSIFICATION`
Authority effect: `NONE_EVIDENCE_ONLY`

## Preserved chronology

- Exact merged candidate `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1` had a green post-merge candidate CI run `34452469174`.
- User-relayed independent DeepSeek re-falsification returned `CHANGES_REQUIRED` with six material findings.
- The independent RED is preserved in failure history and review evidence.
- Repair preregistration `TESTING-QUALIFICATION-INDEPENDENT-REFALSIFICATION-007.md` was frozen before the mechanism repair.
- External GitHub App check run against exact `2fee17ad...` failed closed at `R7-01`: naked `HUMAN_GOVERNANCE_OWNER` + booleans granted terminal authority.
- The App still successfully published an exact-SHA `external-governance-qualification` failure check, proving the external publishing path functions independently of candidate CI.
- A checker fixture typo in the expected external-root repository numeric id was discovered before it could affect a candidate result and was preserved separately in the external governance-check repository before correction.
- R7-01 was repaired so terminal authorization requires exact candidate SHA plus signed authority binding scoped as `TERMINAL_ACTION:<PHASE>:<ACTION>`; legacy naked booleans remain fail-closed inputs only.
- A policy-semantic-version defect was preserved before bumping policy version from v5 to v6, because the terminal authority mechanism materially changed while the old policy material/hash would otherwise have remained unchanged.
- The external checker now independently pins the repaired qualification policy source blob, the candidate external-root module blob, root repository identity/id/commit/fingerprint, governed phase map, and verifies the live external root is public+archived and the pinned PEM fingerprint matches.

## Nonclaims

No construction run, external checker PASS, GitHub App check, repository archive state, or reviewer output grants terminal authority. Branch-rule source constraint to the dedicated GitHub App remains required before closure of R7-03 can be claimed.
