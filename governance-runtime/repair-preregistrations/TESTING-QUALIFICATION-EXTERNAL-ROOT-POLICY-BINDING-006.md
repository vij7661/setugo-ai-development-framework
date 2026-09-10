# TESTING Qualification External-Root Policy Binding Preregistration 006

Status: PREREGISTERED_BEFORE_MECHANISM_CHANGE
Phase: TESTING
Authority effect: NONE_EVIDENCE_ONLY
Parent repair: TESTING-QUALIFICATION-EXTERNAL-GOVERNANCE-ROOT-005
Finding: MR-006 — EXTERNAL_ROOT_NOT_BOUND_IN_SIGNED_POLICY

## Observation

While implementing the archived external governance root, the current qualification policy remained version 4 and its signed policy hash bound only the trust-root ID and public-key DER fingerprint. It did not bind the external repository identity, repository numeric ID, exact external commit, external metadata blob, or archived-root requirement.

That leaves a policy-binding ambiguity: an attestation signed under the earlier local-root policy can remain cryptographically valid after the trust-source mechanism changes, even though the authority trust boundary materially changed.

## Frozen failure expectation

Before repair, a regression requiring the qualification policy material to bind the external governance-root identity and exact commit must fail.

## Repair contract

1. Bump qualification policy version from 4 to 5.
2. Include at least the following in policy material/hash:
   - external repository full name `vij7661/setugo-governance-root`
   - external repository numeric ID `1363676838`
   - exact external root commit `5f470774ec8c17f5519da8db2aaae59af114cef9`
   - trust-root ID `SETUGO_MANUAL_GOVERNANCE_ED25519_V1`
   - public-key DER SHA-256 `2b1b97ab0bf99e71f4a93f51fd8e6c3eb30063d83ba2eb4c091492a95f9c11f2`
   - archived/public external-root requirement
3. Any version-4 signed authority attestation must become stale/non-authoritative under policy v5 even if its Ed25519 signature remains valid over its own historical payload.
4. Existing version-4 signed artifacts remain preserved as historical evidence and must not be rewritten.
5. A fresh human signature will be required for any exact candidate that needs v5 governance-owner authority.

CI green after repair remains construction evidence only and grants no terminal authority.
