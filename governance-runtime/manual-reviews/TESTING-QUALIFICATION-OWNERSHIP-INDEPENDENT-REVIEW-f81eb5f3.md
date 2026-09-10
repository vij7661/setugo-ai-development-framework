# Independent Falsification Review — TESTING Qualification Boundary Ownership

**Candidate SHA:** `f81eb5f3cbde819d60c134ba73287dedc6b67e0b`

**Review basis:** Full extraction and direct execution/attack of the actual source, tests, and trust root supplied in `TESTING-QUALIFICATION-REVIEW-f81eb5f3.zip` (a tar archive, despite its name). I did not rely on the packet's narrative or the CI evidence text as proof — I independently ran the test suite, forged attestations with my own generated Ed25519 keys, and directly called the policy functions with adversarial inputs.

## What I actually did (not inferred)

1. Read every listed implementation file in full: `qualification_boundary_policy.py`, `qualification_boundary_policy_v4.py`, `manual_authority_verifier.py`, `phase_policy.py`, `review_protocol.py`, the committed PEM, the CI workflow, and the standards doc.
2. Ran `python -m unittest` locally on the CI-listed governance tests.
3. Independently recomputed the trust-root public key's DER SHA-256 and compared it against the pinned constant in code.
4. Independently recomputed `qualification_policy_hash()` and compared it against the policy hash the packet claims is embedded in the signed attestation.
5. Forged my own Ed25519 keypair and mounted real attacks — signature forgery against the real trust root, replay, authority-class escalation, decision-scope escalation, payload tampering, signature tampering, policy-hash rebinding, trust-root-ID rebinding, naked role-string impersonation, candidate-callable-issuer minting, contradictory/unknown phase labels — directly against the running code, not just the test files.

## Findings

### F-01 — Real signed-attestation fixture is absent from this evidence bundle

- **Severity:** Medium (evidentiary gap, not a demonstrated control failure)
- **Affected case:** QO-05, "Manual authority evidence" claim
- **Concrete failure path:** `test_manual_authority_signed_attestation.py` reads `governance-runtime/manual-attestations/ed265f37487bccffcc5f4463f5f3b62ee9f2b713.acceptance-boundary.json` and a matching `.sig.b64`. Neither file is present in this bundle. Running the CI-listed suite locally produces 8 `ERROR`s (`FileNotFoundError`) for exactly these tests; everything else in that run passes.
- **Why the mechanism doesn't block it:** it isn't a mechanism failure — it's missing evidence. I substituted my own self-signed attestation against a monkey-patched trust root to isolate and test the *business logic* (see below), which held up. But I cannot confirm the actual production-signed artifact verifies, because it wasn't supplied.
- **Repro:** `cd governance-runtime && python -m unittest -v test_manual_authority_signed_attestation.py` → 8 errors, all `FileNotFoundError` on the same two missing paths.
- **Phase:** TESTING (evidence completeness)
- **Repair:** Include the fixture JSON + signature file (or a reproducible generation path) in any bundle used for independent review; a reviewer cannot verify what it cannot read.

### F-02 — Candidate-SHA mismatch between the packet's stated attestation and the test fixture's bound SHA

- **Severity:** High (undermines the packet's headline authority claim)
- **Affected case:** QO-05 / "Manual authority evidence" section
- **Concrete failure path:** The packet states the signed attestation's `candidate_sha` is `f81eb5f3cbde819d60c134ba73287dedc6b67e0b` (the exact candidate under review). But `test_manual_authority_signed_attestation.py` hard-codes `SIGNED_SHA = "ed265f37487bccffcc5f4463f5f3b62ee9f2b713"` — a different 40-hex-char SHA — and uses it as the fixture's filename *and* as the `candidate_sha` it verifies against.
- **Why this matters mechanically:** I confirmed (by direct attack) that `verify_manual_authority_attestation` performs an exact-match check: `supplied.get("candidate_sha") != candidate_sha` → reject. That check is doing its job correctly. But it means one of two things must be true, and I cannot tell which from what's provided: (a) the real fixture's `candidate_sha` field is actually `ed265f37...`, so the packet's stated candidate SHA for the attestation is wrong/stale, and the "human-signed authority" does **not** in fact bind to `f81eb5f3...`; or (b) the fixture's field really is `f81eb5f3...` and the test file's `SIGNED_SHA` constant/filename is simply stale, in which case `test_real_human_signed_attestation_verifies_for_exact_signed_candidate` as currently written would actually **fail** against a correctly-updated fixture (contradicting the CI evidence's claim that all 8 signed-attestation tests passed).
- **Why the mechanism doesn't block it:** this is a bundle/documentation consistency problem, not something the runtime can detect — the runtime only knows what SHA it's told to check against.
- **Repro:** diff `f81eb5f3cbde819d60c134ba73287dedc6b67e0b` (packet header, and the file everything else in this bundle is named after) against `ed265f37487bccffcc5f4463f5f3b62ee9f2b713` (test file line 14).
- **Phase:** TESTING
- **Repair:** Reconcile which SHA the real signed attestation is actually bound to; if it's not `f81eb5f3...`, the packet's authority claim for *this exact candidate* is unsupported until a fresh attestation is signed for it, and QO-05 completion for this SHA specifically should be treated as unresolved rather than assumed.

### F-03 — Trust-root pin is declarative, not self-verified at runtime

- **Severity:** Low–Medium (defense-in-depth gap, not a demonstrated exploit)
- **Affected case:** "trust-root rebinding" (additional falsification target)
- **Concrete failure path:** `TRUST_ROOT_PUBLIC_KEY_DER_SHA256` is declared in `qualification_boundary_policy_v4.py` and flows into `qualification_policy_hash()`, but no code path re-derives the DER SHA-256 of the actual on-disk `trust-roots/governance-public.pem` and asserts it equals that constant before trusting the key for signature verification. I independently computed the DER SHA-256 of the committed PEM (`openssl pkey ... -outform DER | sha256sum`) and it **does** currently match the pinned constant exactly — so there's no discrepancy today.
- **Why the mechanism doesn't fully block it:** if a PR simultaneously swapped the PEM file and the constant to a self-consistent attacker-controlled pair, nothing in the code I have would catch it — that's left to `review_required()`'s `governance-runtime/`-path flag plus whatever branch-protection/human-review gate exists outside this bundle, which I have no visibility into.
- **Repro:** `openssl pkey -pubin -in governance-runtime/trust-roots/governance-public.pem -outform DER | sha256sum` → matches `TRUST_ROOT_PUBLIC_KEY_DER_SHA256`.
- **Phase:** TESTING
- **Repair:** Add a runtime self-check asserting the on-disk PEM's DER hash equals the pinned constant (fail closed if not), as defense-in-depth independent of any external branch-protection assumption.

### F-04 — Five referenced test files and an entire experiment suite are absent from this bundle

- **Severity:** Medium (verification-scope gap)
- **Affected case:** "verify the test harness actually executes the intended adversarial tests" requirement; partially QO-04, QO-07
- **Concrete failure path:** The CI workflow (and CI evidence file) reference `test_review_protocol.py`, `test_review_semantics.py`, `test_review_classification.py`, `test_single_file_review_container.py`, `test_platform_candidate_review_request_integrity.py`, and `experiments/governed-platform/governance/test_integrated_governed_mvp_slice6_terminal_authority.py` (the "26 terminal-authority tests"). None of these files exist in this bundle.
- **Why this matters:** I read `review_protocol.py` in full and it's structurally sound (exact commit/hash binding throughout, explicit proposer≠reviewer independence check, canonical-hash tamper detection, fail-closed malformed-input handling) — but I could not run it or attack it, and I have zero visibility into the terminal-authority experiment module the CI evidence credits with 26 passing tests covering model/worker/orchestrator/platform-policy substitution and stale/tampered-authority rejection.
- **Repro:** `find . -iname "test_review_protocol*" -o -iname "*terminal_authority*"` under the extracted archive → no matches.
- **Phase:** TESTING
- **Repair:** Include these files in any bundle intended for independent falsification review, or scope the review request explicitly to exclude them.

### No contradictions found in what I could directly execute

Every adversarial input I constructed myself against the live code was correctly rejected: candidate-callable authority minting, raw role-string impersonation, replay to a different SHA, authority-class escalation, decision-scope escalation, attestation payload tampering, signature byte-tampering, policy-hash/version rebinding, in-payload trust-root-ID rebinding, contradictory phase labels (standalone and combined with a governed rule ID), unknown/unmapped governed-rule IDs, mandatory-review-dimension weakening, adversarial-matrix case omission, and matrix rebinding. None of these are taken on the packet's word — the tool outputs above show the actual rejection reasons returned by the running code.

## QO-01 through QO-08 — explicit results

| Case Result Basis  |                                                  |                                                                                                                                                                                                                                                                                                                            |
| ------------------ | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| QO-01              | **TESTED_SUPPORTED**                            | Directly attacked `review_required()`; benign trigger + governance-path change still forces `True`.                                                                                                                                                                                                                        |
| QO-02              | **TESTED_SUPPORTED**                            | Directly attacked `verify_review_dimensions()`; deletion, downgrade, and description-narrowing all rejected.                                                                                                                                                                                                               |
| QO-03              | **TESTED_SUPPORTED**                            | Directly attacked `verify_testing_matrix_results()`; case omission and matrix rebinding both rejected.                                                                                                                                                                                                                     |
| QO-04              | **TESTED_SUPPORTED** (bounded — see F-04)       | Directly attacked `terminal_authority_allowed()` (self-appointment, unverified provenance, action-scope escalation, all rejected) and the candidate-callable issuer trap (verifiably neutered). The separate 26-test terminal-authority experiment suite referenced by CI is **not** independently confirmed by me (F-04). |
| QO-05              | **TESTED_SUPPORTED** (bounded — see F-01, F-02) | Directly attacked `preregistration_required()` and `acceptance_boundary_change_allowed()`; both mechanisms hold. But the specific claim that a real human authority binding exists **for this exact candidate SHA** is unresolved (F-02).                                                                                  |
| QO-06              | **TESTED_SUPPORTED**                            | Directly attacked `root_cause_classification_allowed()`; naked privileged-role self-classification for a material finding rejected.                                                                                                                                                                                        |
| QO-07              | **TESTED_SUPPORTED**                            | Directly attacked `reviewer_finding_adjudication_allowed()`; naked adjudicator-role self-appointment rejected.                                                                                                                                                                                                             |
| QO-08              | **TESTED_SUPPORTED**                            | Directly attacked `phase_disposition()`; genuinely-current-phase defects stay blocked, genuinely-later-phase defects correctly defer, and candidate-supplied/unmapped/contradictory phase labels fail closed to `REQUIREMENT_UNRESOLVED` rather than silently deferring or vanishing.                                      |

## Independent verification of test-harness execution

**Partially performed, not fully.** I confirmed, by actually running it, that `test_qualification_boundary_unittest_bridge.py` genuinely walks every top-level `test_*` function in `test_qualification_boundary_policy.py` (24 functions, ≥15 required), `test_manual_review_authority_spoofing_regression.py` (exactly 4), and `test_manual_review_authority_ingress_regression.py` (exactly 2) via `inspect`-based discovery and executes each inside a `subTest` — this is the actual, code-level fix for the previously-documented "top-level `test_*` functions not collected by `unittest`" false-green, and it ran clean in my hands. I did **not** independently confirm execution of the five review-protocol/terminal-authority test files referenced by CI, because they are not present in this bundle (F-04).

## Evidence-only statement

This review is evidence only. It grants no terminal authority, does not constitute RELEASE or PRODUCTION qualification, and is not itself an independent-governance adjudication under the policy it is reviewing.

## Disposition: `TESTING_RULES_BOUNDED_PASS`

Every QO case I could directly and adversarially exercise held up under genuine attack — not merely passed pre-written tests, but resisted inputs I constructed myself with a self-generated signing key. That's real, substantive evidence the ownership mechanism works as designed. It is bounded, not a full pass, because of two open gaps that a PASS should not paper over: (1) the real signed-attestation fixture proving human authority is bound to *this exact* candidate SHA is either missing or internally inconsistent (F-01, F-02), and (2) roughly a third of the CI-referenced test surface (review-protocol semantics and the terminal-authority experiment suite) isn't in this bundle and remains unverified by me (F-04). Neither gap is a demonstrated contradiction of any QO case — but per the packet's own posture, unresolved evidence gaps should not be silently rounded up to a full pass.
