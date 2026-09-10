# TESTING Qualification Boundary Ownership — Construction Evidence 001

Status: `OPEN_BLOCKED_ON_MANUAL_AUTHORITY_TRUST_BOUNDARY`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`

## Preserved evidence sequence

1. Original ownership construction was reported green before the test harness defect was discovered.
2. Run `34438769149` at `726eaa695c78346e678e104360949ef96800301e` was later classified as a test-harness false green because `python -m unittest` did not collect module-level `test_*` functions in the ownership/frozen-regression files.
3. The unittest bridge repaired collection without weakening the frozen attacks.
4. Genuine RED: run `34438867816` at `d415d60cbb29d1943ef926fea384aa91c9be2043` failed exactly four frozen MR-001/MR-002 attacks.
5. Construction repair introduced exact-SHA/policy/scope authority bindings and platform-owned governed-rule phase mapping.
6. Genuine construction green: run `34439504323` at `9fcce813ac92b369d5ce30bb7e9afbd197fffa6c` ran 68 governance tests successfully, including the bridge/frozen spoofing attacks; terminal-authority regressions ran 26 tests successfully.
7. Manual re-falsification then attacked the trust boundary itself and froze MR-003/MR-004.
8. RED: run `34439769044` at `5897ffae47f0cb17b06c0c13ee9095bc351516ba` ran 69 tests and failed exactly two frozen tests: candidate-callable authority issuer and contradictory legacy phase label.
9. MR-004 was narrowly repaired by rejecting every non-null caller-supplied legacy phase label.
10. Post-MR-004 run `34439904660` at `11d6734fae37520f77f7e9598ac104d4b1d4fcb6` ran 69 tests and failed exactly one frozen attack: candidate-callable authority issuer. The contradictory-phase attack passed.

## Current adjudication

- QO-01..QO-04: not defeated by the recent manual attacks; not independently closed.
- MR-001 raw privileged role spoofing: construction-repaired.
- MR-002 caller-selected phase deferral: construction-repaired.
- MR-004 contradictory legacy phase label: construction-repaired and frozen regression passes.
- MR-003 authority ingress trust-domain separation: **OPEN / BLOCK_TESTING**.

## MR-003 blocking fact

`_issue_authority_binding_for_platform_ingress(...)` and the HMAC signing capability reside in the same importable Python module as the verifier. A leading underscore is not access control. Code able to execute/import within that trust domain can invoke the issuer and mint a verifier-accepted privileged binding.

Therefore current construction does not establish that the evaluated actor is unable to mint its own authority. TESTING completion and promotion remain blocked.

## Required next boundary

The issuer/signing authority must be outside candidate-callable code. The evaluated runtime should receive only verification capability/material and an already-created manual-governance attestation. Establishing that trusted manual authority source requires a human-controlled credential or equivalent external trust root that the candidate runtime cannot access.

No external reviewer API may be used to satisfy this requirement in TESTING.

## Nonclaims

- No CI success here is terminal authority.
- No assistant/manual review performed by the implementer is independent acceptance.
- The in-process HMAC design does not cryptographically prove human identity.
- QO-01..QO-08 are not declared scientifically closed.
