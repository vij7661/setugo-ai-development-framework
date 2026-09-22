# R8 v3 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v3 commit: `aa4a5e6a320002731926e0c9ccbbb62c2bfbb0ca`
- R8 v3 blob: `4c063ef124947723383735b27dadaa3ded6dfb54`

Independent review evidence:
- preserved at `review-evidence/R8-V3-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- uploaded artifact SHA-256: `a70a721b7cc4b02df36c036e69abcd7e49d3b67258b2c69b282289e0dbcaa4fc`
- disposition: `CHANGES_REQUIRED`
- review type: blind design/static review only
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v3 closed many prior semantic and mechanism-proof gaps, but implementation must still not begin because the design still bootstraps trust from self-asserted principal/controller identifiers and assumes infrastructure independence without an externally anchored qualification mechanism.

R8 v3 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blockers

### V3-C1 — Non-self-asserted controller identity
**ACCEPTED — BLOCKER**

A successor must introduce an explicit external trust axiom and an out-of-band controller-attestation mechanism. Platform-generated `controller_id`, `credential_id`, or principal labels cannot by themselves establish independence.

Required successor properties:
- pre-genesis trust anchor outside ordinary governed state;
- externally attested controller identity;
- attestation chain and revocation;
- administrative-domain identity for independence decisions;
- no platform self-enrollment into root/recovery/time/anchor/controller authority.

### V3-C2 — Anchor replica independence/collusion
**ACCEPTED — BLOCKER**

Two named replicas are insufficient without controller qualification and an external witness.

Required successor properties:
- anchor replicas enrolled through externally attested controller identities;
- distinct administrative domains;
- quorum certificate over each authoritative anchor append;
- external transparency witness/inclusion proof;
- explicit bounded claim: collusion beyond the qualified threshold remains outside proof.

### V3-C3 — Bootstrap self-authentication
**ACCEPTED — BLOCKER**

Signing genesis with keys named inside that same genesis is circular.

Required successor properties:
- pre-genesis bootstrap certificate/manifest issued by the external trust anchor;
- exact authorized initial controllers and key fingerprints;
- one-time bootstrap ceremony identifier;
- first-seen/singleton registration at an external witness;
- atomic genesis append.

### V3-C4 — Concurrent successor race
**ACCEPTED — BLOCKER**

Constitutional and registry successor operations require atomic predecessor consumption.

Required successor properties:
- compare-and-swap/conditional append over exact predecessor sequence+digest;
- only one successor may consume a non-commutative predecessor;
- losing concurrent writer receives conflict;
- competing committed heads remain detectable as a fault.

## 3. Accepted high findings

Adopt into successor design:

- CSR semantic-surface classification must be rule-driven; unknown semantic impact is constitutional/material, not silently non-CSR.
- Root-sensitive and terminal issuer configurator/beneficiary separation is non-overridable.
- Every revocation event is immediately anchored and use-time validation requires a head at least as new as the authority decision context.
- Time attestations bind an exact `decision_context_digest`, nonce, tenant, action/candidate scope, and validity window.
- Strong evidence classes may only be minted by preregistered qualified producer classes; “trusted execution path” becomes an explicit registry object.
- Out-of-band mutation detection requires periodic/in-use state-root verification against anchored state, not prose assertion.
- Load-bearing independent review must compensate for provider-internal-memory uncertainty using policy-defined independent channels (for constitutional review: at least two independent review channels, with at least one human or separately administered provider class where required).

## 4. Accepted medium findings

Adopt into successor design:

- GCP integer range and lexical form must be exact.
- allowed non-material mutations must be schema-level field masks, not prose categories.
- checkpoint anchor maximum lag must be bounded exactly.
- recovery trigger schemas are constitutional mandatory objects and cannot be omitted/weakened through ordinary policy.
- complete guard catalog and positive-control mapping must be frozen before implementation.
- authority resolution must use stable IDs only; aliases are prohibited inputs to authority APIs.
- SPR lifecycle operations must be explicit and append-only.

## 5. Bounded interpretation

The review cannot prove runtime exploits because no implementation exists. Findings are design blockers only.

A system cannot prove real-world non-collusion mathematically. The successor must therefore:
1. define the external trust assumptions explicitly;
2. bind them to verifiable attestation artifacts;
3. test that software cannot replace those assumptions with self-issued labels;
4. state the collusion threshold outside the claim boundary.

## 6. Successor rule

Create R8 v4 as a new preregistered design.

Do not mutate R8 v3.

R8 v4 must receive a fresh blind independent design review before implementation begins.

Until then:
- R8 v1 = `CHANGES_REQUIRED`
- R8 v2 = `CHANGES_REQUIRED`
- R8 v3 = `CHANGES_REQUIRED / NOT_IMPLEMENTED`
- R8 v4 = not yet reviewed
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
