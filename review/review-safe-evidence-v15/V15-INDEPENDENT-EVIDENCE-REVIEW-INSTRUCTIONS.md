# V15 — Independent Manual Implementation Evidence Review Instructions

Status: **FRESH MANUAL INDEPENDENT EVIDENCE REVIEW REQUIRED / NO AUTHORITY EFFECT**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 1. Clean-context requirement

Perform this review in a fresh context. Do not use prior reviewer conclusions, prior chat reasoning, model memory about this project, or hidden project state outside this package. Do not call another reviewer/model/provider API. Treat all green construction evidence as challengeable rather than authoritative.

This review is evidence-only. It cannot grant runtime, scientific, release, deployment, or terminal authority.

## 2. Exact frozen candidate

Review only the implementation frozen at:

- repository: `vij7661/setugo-ai-development-framework`
- candidate commit: `380e1d9db083a6477691bf187d5cba7c61eee280`
- candidate tree: `6bdd7bf8ec214e406383e084bd7c28b8c9738ee9`
- baseline main commit: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`
- expected changed candidate files: `30`
- implementation surface claim: `33/33 implemented, construction-only`

If package bytes, manifest, Git identity, or construction evidence do not bind to that exact candidate, report the mismatch and stop positive adjudication.

## 3. Review objective

Determine whether the frozen implementation actually enforces the V15 governance design and stopping rule without a concrete false-green or authority-bypass path.

Do not infer operational safety merely because tests pass. Read the implementation, tests, workflows, schema registry, frozen standard, historical RED, and construction evidence. Search for self-authored authority, caller-controlled booleans, unbound strings, stale/replay paths, incomplete universes, hidden control-domain collapse, mismatch between test assertions and implementation behavior, and any path by which missing/insufficient evidence can be converted into a positive result.

## 4. Mandatory implementation dimensions

Review every dimension below separately. Use `INSUFFICIENT_TO_ASSESS` where supplied evidence is insufficient; never silently convert missing evidence to PASS.

A. Canonical schema enforcement for control domains, ancestry, residual roots, independent-root proofs, governed proof, challenge certificate, currentness, reviewer response coverage, blocker record and fenced effect token.

B. ReviewGovernanceRoot and role-authority ancestry closure, including candidate/self qualification and common-control collapse.

C. Multi-root evidence-universe derivation, conservative union, shared-source circularity, unknown material surfaces, negative-space challenge and completeness certificates.

D. Raw evidence registry; explicit missing evidence; governed N/A lifecycle, contradiction/expiry/challenge; observation applicability.

E. Independent obligation/materiality graph, reviewer-safe exact/structured-redaction projection, raw-access verifier and disclosure completeness.

F. Hidden-evidence monitor quorum: identity count, control-domain threshold, implementation diversity, pairwise independent roots, per-obligation `REOPEN_REQUIRED` or `NO_REOPEN_FOUND`, silence blocking, coverage certificate and currentness.

G. Atomic sealed review snapshot, rollback/fork/mixed-state handling, independent snapshot witness/anchor and exact snapshot binding.

H. Clean-room review session assurance. Provider identity alone must not establish promotable context isolation. Manual paste must remain non-promotable. Unavailable provider-side isolation must fail closed for material promotion.

I. Reviewer qualification/currentness/expiry and authenticated exact review-response receipt, including complete mandatory dimension coverage.

J. Append-only review response ledger and blocker ledger, witnessed current head, predecessor integrity, replay/tamper handling and reopened-review blocker resolution.

K. Currentness vector and decision-time revalidation.

L. Governance generation: load-bearing control/policy changes always create a material generation; unknown impact blocks; transition is independently witnessed.

M. ResidualTrustState: exact roots/currentness/generation, risk-owner acceptance, common-control disclosure and inability to override blockers/insufficiency/unproven independence.

N. Adjudication firewall: no hidden raw-evidence read capability; exact allowed input set; current ledger heads; monitor certificate; policy; currentness; residual trust; clean-room and review response binding.

O. Fenced effect issuance and external gateway: exact candidate/snapshot/generation/ledger/currentness/content receipt/gateway version, single use, expiry, replay, atomic consumption, immediate pre-effect revalidation, and unfenceable effect rejection.

P. Post-review taint/provenance graph: transitive `POST_REVIEW_FINDING` propagation through summaries/extracts/transforms/imports, clean-package allowlist, unknown provenance fail-closed and candidate self-label rejection.

Q. Implementation stopping rule: all schemas, all construction/adversarial tests, no unresolved Critical/High, preserved RED history, exact freeze, bound evidence/environment, reviewer-safe projection, independent evidence review next, with runtime/scientific authority still unclaimed.

## 5. Adversarial review requirements

Actively attempt to falsify, at minimum:

- forged or omitted independence proofs;
- shared residual root hidden behind distinct nominal domains;
- role authority or verifier self-qualification;
- incomplete derivation stream or shared-source universe false green;
- negative-space challenge that removes rather than adds obligations;
- missing evidence relabelled captured or N/A without proof;
- stale/expired/contradicted N/A proof;
- load-bearing projection omission or modification;
- generated reviewer-visible field not present in raw evidence;
- hidden monitor silence, duplicate identity/domain counting, single implementation, stale certificate, `REOPEN_REQUIRED` laundering;
- unsealed/mixed/replayed/rollback snapshot;
- witness from candidate/writer/downstream governance domain;
- provider-side context isolation unavailable but treated promotable;
- expired reviewer qualification at decision time;
- truncated response or missing mandatory review dimension;
- review/blocker ledger predecessor or witnessed-head tamper;
- open blocker neutralized by majority, silence or administrative label;
- adjudicator raw-hidden-evidence access;
- load-bearing governance change labelled non-impacting;
- stale residual root or unresolved common-control risk accepted as promotable;
- stale currentness vector;
- fenced token replay, expiry, context drift, gateway-version drift, non-atomic consumption or unfenceable effect;
- POST_REVIEW_FINDING laundering into clean package via derived summaries/transforms;
- stopping-rule false green when an adversarial test, preserved RED, exact freeze or evidence binding is absent.

For every Critical/High blocker provide the exact file/function/mechanism, a concrete false-green or authority-bypass path, why existing controls do not stop it, and the narrowest repair.

## 6. Historical RED handling

The package intentionally preserves construction RED evidence. A later PASS must not erase or rewrite it. Determine whether the RED is correctly classified and whether its correction changes only the invalid fixture/harness or weakens the mechanism.

## 7. Required output

Return all sections:

A. `CONTENT_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_TO_ASSESS`

B. `CRYPTOGRAPHIC_RECOMPUTATION = VERIFIED | NOT_VERIFIED | INSUFFICIENT_TO_ASSESS`

C. `IMPLEMENTATION_SCOPE = COMPLETE | INCOMPLETE`

D. Overall = `IMPLEMENTATION_BOUNDED_PASS | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`

E. Critical findings.

F. High findings.

G. Medium findings.

H. Low findings.

I. Canonical schemas / independence / authority assessment.

J. Universe / evidence / N/A assessment.

K. Projection / disclosure / hidden-monitor assessment.

L. Snapshot / clean-room / reviewer-response assessment.

M. Ledgers / adjudication / generation / currentness / residual-trust assessment.

N. Effect fencing / external gateway assessment.

O. Taint/provenance / clean-package assessment.

P. Historical RED preservation assessment.

Q. Test/evidence sufficiency and false-green analysis.

R. Remaining concrete bypass paths or untested trust assumptions.

S. Exact required changes.

T. `ZERO_CRITICAL_HIGH = YES | NO`

U. `INDEPENDENT_EVIDENCE_REVIEW_RECOMMENDATION = ACCEPT_FOR_ADJUDICATION | REVISE_AND_REREVIEW | INSUFFICIENT_TO_ASSESS`

End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
