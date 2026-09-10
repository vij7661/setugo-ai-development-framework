# TESTING Qualification Boundary Independent Re-falsification — Repair Preregistration 008

Status: `FROZEN_BEFORE_REPAIR`
Authority effect: `NONE_EVIDENCE_ONLY`
Exposed scientific subject: exact TESTING candidate `61e98ba0ca8fc461b407e91e4f60ffc687fc784e`.
Trigger: user-relayed independent DeepSeek review returned `CHANGES_REQUIRED` after exact-SHA candidate CI and external-App checks were green.

## Chronology rule

This preregistration is committed before any R8 mechanism repair. The eventual repaired successor SHA cannot exist yet and therefore is not invented here. Instead, the successor MUST be recorded by exact SHA after construction and MUST receive fresh exact-SHA candidate testing, external qualification, and independent re-falsification. Evidence from `61e98ba0...` cannot be replayed to its successor.

## Frozen R8 adversarial requirements

1. `R8-01 VERIFIER SUBSTITUTION`: replacing `governance-runtime/manual_authority_verifier.py` with a verifier that returns success for arbitrary bindings MUST cause external qualification to fail closed. The production verifier implementation used by the active terminal-authority path must be independently pinned/validated together with its policy/root dependencies.
2. `R8-02 REQUIRED-CHECK SOURCE`: authoritative branch governance MUST require `external-governance-qualification` specifically from dedicated GitHub App integration `4895420`; same-name candidate GitHub Actions output must not satisfy it. Packet/live evidence must include the actual ruleset, not merely candidate-local expectations.
3. `R8-03 CHECKER CREDENTIAL/REVISION CONTROL`: candidate-controlled changes MUST NOT be able to obtain the GitHub App credential or alter the external checker implementation that publishes an authoritative required check. A historical checker SHA alone is insufficient use-time evidence. The App private key/credential boundary and checker-revision governance must be explicit and fail closed.
4. `R8-04 RUNTIME IMPORT-SURFACE SUBSTITUTION`: changing the compatibility facade or any authority-critical imported runtime module while leaving the currently pinned policy file unchanged MUST fail external qualification. External validation must cover the actual authority-critical runtime dependency closure, not a convenient subset.
5. `R8-05 REVIEW PACKET REPRODUCIBILITY`: the independent review packet MUST contain referenced non-secret signed-attestation fixtures and the source/test material needed to reproduce the claimed signature/replay/tamper tests. Private keys remain forbidden.
6. `R8-06 SUCCESSOR EXACT-SHA LINEAGE`: the repair record MUST distinguish exposed subject SHA from repaired successor SHA and explicitly record fresh exact-SHA qualification evidence for the successor. A preregistration is not permitted to fabricate a future commit SHA.
7. `R8-07 ADMIN/RULESET VISIBILITY`: authoritative qualification must independently validate the live ruleset's active target, strict checks, dedicated App integration, and empty bypass actors from an evidence channel that exposes those fields. Missing material administrative/ruleset evidence fails closed.
8. Candidate CI, external App PASS, repository archive state, reviewer/model output, and cryptographic verification remain evidence only. None grants terminal authority by itself.
9. Prior failures and green runs remain append-only history; no later repair may reinterpret or erase them.
10. TESTING remains manual-review only. No external reviewer API is introduced by this lineage.

## Reconciliation already exposed before repair

The reviewer classified `R8-02` as CRITICAL because its packet lacked live ruleset evidence. Independent live GitHub inspection after the review shows ruleset `22736961` currently contains `external-governance-qualification` with `integration_id: 4895420`, while GitHub Actions uses integration `15368`, and `bypass_actors` is empty. This does not erase R8-02: it reclassifies the immediate observation as a **review-packet evidence omission**, while the frozen R8-02/R8-07 tests require that the external qualification mechanism itself verify and package this state going forward.

The reviewer classified `R8-03` against a real condition: external checker `main` at `b42fb00a03a41b6eea9a233bc8281de081649cc0` is unprotected and the workflow obtains the GitHub App private key from repository Actions secrets. Repair MUST address the credential/revision boundary rather than merely adding another self-asserted checker SHA constant.

## Nonclaims

This contract protects the evaluated candidate from self-qualification. It does not claim that one human GitHub account is cryptographically immune to account compromise or that a governance owner can never change governance. Human governance changes must be explicit; they must not be achievable by the evaluated candidate code itself.
