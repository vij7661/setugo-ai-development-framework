# RELEASE R3 — Trust-Root Scope Gap 001

Status: `REQUIREMENT_UNRESOLVED / RELEASE-BLOCKING`
Authority effect: `NONE_EVIDENCE_ONLY`
Exact reviewed candidate: `ffec566022fcd221fb4ab7569ed3bc245f75b546`

## Discovery

While implementing the preregistered merge-authority gate after the independent R2 `BOUNDED_PASS`, the external trust-root metadata was re-read at pinned root commit `5f470774ec8c17f5519da8db2aaae59af114cef9`.

The root metadata declares:

- `trust_root_id`: `SETUGO_MANUAL_GOVERNANCE_ED25519_V1`
- `authority_scope`: `TESTING_MANUAL_GOVERNANCE_ATTESTATION_VERIFICATION_ONLY`

The root README also calls it the **Authoritative TESTING trust root** and states that the repository does not itself grant RELEASE or PRODUCTION authority.

The exact RELEASE candidate policy v6, however, routes RELEASE terminal action verification through the same `TRUST_ROOT_ID` / manual authority verifier used for TESTING. RELEASE terminal policy permits `HUMAN_RELEASE_AUTHORITY` and action `MERGE_RELEASE_CANDIDATE`, but the pinned public root that would verify such a signature is explicitly scoped to TESTING in its authoritative metadata.

## Concrete false-authority risk

If the platform accepts a RELEASE merge signature under a public key whose authoritative root metadata is scoped only to TESTING, the verifier is effectively expanding the trust root's authority beyond its declared scope. The candidate policy cannot self-expand an external trust root's authority merely by naming a broader issuer/action.

## Classification

`GOVERNANCE_PROCESS_DEFECT / REQUIREMENT_UNRESOLVED`

This was discovered before any RELEASE merge-authority verifier or successful authority check was implemented. No terminal signature has been requested or accepted.

## Frozen repair boundary

A RELEASE merge gate must not be completed until the human governance owner establishes an unambiguous RELEASE-capable trust root. The preferred repair is a distinct RELEASE-specific Ed25519 trust root/key identity, pinned externally and consumed by a successor policy. Reusing or expanding the TESTING key is a material authority-scope decision and may not be inferred by candidate/checker code.

Any repair that changes policy/trust-root binding creates a successor RELEASE candidate and invalidates prior exact-SHA terminal qualification for the old policy binding. Existing R2 review remains preserved evidence for `ffec5660...`; it is not silently transferred to the successor.

No merge, production qualification, deployment, or terminal authority is granted by this record.
