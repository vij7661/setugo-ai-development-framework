# TESTING Qualification Boundary Ownership — Construction Evidence 001

Status: `OPEN_AWAITING_INDEPENDENT_REFALSIFICATION`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`

## Preserved evidence sequence

1. Original ownership construction was reported green before the test harness defect was discovered.
2. Run `34438769149` at `726eaa695c78346e678e104360949ef96800301e` was later classified as a test-harness false green because `python -m unittest` did not collect module-level `test_*` functions in the ownership/frozen-regression files.
3. The unittest bridge repaired collection without weakening the frozen attacks.
4. Genuine RED: run `34438867816` at `d415d60cbb29d1943ef926fea384aa91c9be2043` failed exactly four frozen MR-001/MR-002 attacks.
5. Construction repair introduced exact-SHA/policy/scope authority bindings and platform-owned governed-rule phase mapping.
6. Genuine construction green: run `34439504323` at `9fcce813ac92b369d5ce30bb7e9afbd197fffa6c` ran 68 governance tests successfully; terminal-authority regressions ran 26 tests successfully.
7. Manual re-falsification then attacked the trust boundary itself and froze MR-003/MR-004.
8. RED: run `34439769044` at `5897ffae47f0cb17b06c0c13ee9095bc351516ba` ran 69 tests and failed exactly two frozen tests: candidate-callable authority issuer and contradictory legacy phase label.
9. MR-004 was narrowly repaired by rejecting every non-null caller-supplied legacy phase label.
10. Post-MR-004 run `34439904660` at `11d6734fae37520f77f7e9598ac104d4b1d4fcb6` ran 69 tests and failed exactly one frozen attack: candidate-callable authority issuer.
11. Verification-only Ed25519 v4 removed the candidate-callable issuer. A real human-controlled private key remained off-repository. Historical construction green at `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`, run `34441939120`, executed 77 governance tests and 26 terminal-authority tests successfully, including the corrected signed-attestation harness.
12. Manual re-falsification identified MR-005: the public trust root and its policy pin were still candidate-modifiable in the evaluated repository.
13. A first MR-005 repair attempted an externally enforced GitHub branch ruleset requiring one approving review. In the actual single-owner repository this requirement was not satisfiable without a genuinely independent collaborator.
14. PR #27 was merged as `6fb96bb8fd0dd4c5ed9c065a2e4350eec0e0cf67`. Post-merge run `34449284629` correctly went RED with `FAIL_CLOSED: at least one approving review is required`. This RED is preserved; it was not reinterpreted as a pass.
15. Because no independent collaborator exists, a replacement mechanism was preregistered in `TESTING-QUALIFICATION-EXTERNAL-GOVERNANCE-ROOT-005.md` before changing the trust-source mechanism.
16. The user created `vij7661/setugo-governance-root`, made it public, and archived it. It contains only public Ed25519 verification material and metadata; no private key. The pinned exact external-root commit is `5f470774ec8c17f5519da8db2aaae59af114cef9`, repository numeric ID `1363676838`.
17. The production manual-authority verifier was changed to retrieve the public key from that exact external root. Candidate-local PEM material is no longer the production authority source.
18. PR #28 initial construction run `34451220505` passed with 103 governance tests and 26 terminal-authority tests. This was construction evidence only.
19. Further falsification found MR-006: policy v4 did not bind the external repository identity, numeric ID, exact root commit, or public/archived requirement in the signed policy hash.
20. MR-006 was preregistered before mechanism repair in `TESTING-QUALIFICATION-EXTERNAL-ROOT-POLICY-BINDING-006.md`.
21. Genuine MR-006 RED: run `34451357447` at PR head `4d444718650a314751041de25777aa98f4ef3e76` executed the frozen external-root policy-binding tests. The governance suite ran 105 tests and failed with exactly one assertion failure and one error: policy version remained 4 and the external-root repository field was absent from policy material. Terminal-authority tests were skipped after the RED.
22. The qualification policy was then bumped to v5 and its policy hash now binds the external repository full name, repository ID, exact external-root commit, trust-root ID, DER fingerprint, and public/archived requirements. Historical v4 signatures remain preserved as historical cryptographic evidence but are rejected as current v5 authority.
23. Real repaired construction green: run `34451635830` at PR head `81dfbcdcf4f684677c57ce92fa3fdaf5734d4546` completed successfully. The live external governance boundary passed, 106 governance tests passed, and 26 terminal-authority tests passed. Logs explicitly collected the external-root substitution/rebinding tests, external-root policy-binding tests, historical-v4/current-v5 distinction tests, and earlier frozen harness/authority tests.

## Current adjudication

- QO-01..QO-08: construction mechanisms and regressions are present; they are **not independently/scientifically closed**.
- MR-001 raw privileged role spoofing: construction-repaired.
- MR-002 caller-selected phase deferral: construction-repaired.
- MR-003 candidate-callable authority issuer: construction-repaired by verification-only Ed25519 ingress; still requires independent refalsification of the full resulting boundary.
- MR-004 contradictory legacy phase label: construction-repaired and frozen regression passes.
- MR-005 candidate-modifiable trust root: replacement construction now uses exact-commit public archived external governance root plus protected TESTING branch; **construction-repaired, awaiting independent refalsification**.
- MR-006 external root absent from signed policy binding: construction-repaired in policy v5; genuine RED and later green preserved; **awaiting independent refalsification**.

## Current trust boundary

The configured manual-governance private key is external/off-repository and is not available to candidate/runtime code. Production verification retrieves only the public key from exact external repository commit `5f470774ec8c17f5519da8db2aaae59af114cef9`. The external repository is required to remain public and archived, and its repository identity, numeric ID, exact commit, root ID and public-key fingerprint are bound into qualification policy v5.

`phase/testing` remains governed by an active repository ruleset requiring pull-request flow, strict `falsify-qualification-boundary` status checking, deletion protection, non-fast-forward protection, review-thread resolution and no bypass actors. The single-owner profile uses zero mandatory GitHub approvals; this is a replacement preregistered mechanism, not a reinterpretation of the earlier one-approval RED.

The external root demonstrates control of the configured private key when a valid signature is produced. It does not independently establish a real-world human identity.

## Remaining scientific boundary

Construction green does not close TESTING qualification. Independent manual falsification must attack QO-01..QO-08 and the full current authority boundary, including candidate-local key/pin substitution, external-root repository/commit rebinding, archived-state loss, signature/payload tampering, stale v4 replay, policy v5 binding, ruleset weakening, phase relabeling, and harness omission.

Any newly exposed material defect must remain BLOCK_TESTING until repaired and independently refalsified.

## Nonclaims

- No CI success here is terminal authority.
- No assistant/implementer review is independent acceptance.
- Historical REDs and false greens remain part of the evidence history.
- A valid Ed25519 signature proves possession/control of the configured private key, not human identity by itself.
- No TESTING completion, RELEASE qualification, or PRODUCTION qualification is claimed by this construction evidence.
