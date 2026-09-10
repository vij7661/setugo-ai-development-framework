# RELEASE R3 — Merge-Authority Gate Preregistration

Status: `FROZEN_BEFORE_MECHANISM`
Authority effect: `NONE_EVIDENCE_ONLY`
Exact RELEASE candidate: `ffec566022fcd221fb4ab7569ed3bc245f75b546`
Trigger: independent RELEASE R2 `BOUNDED_PASS`, residual findings R2-01 and R2-08.

## Problem statement

The current `phase/release` ruleset enforces App-bound qualification checks but does not itself enforce the separate signed terminal authority required by policy for `MERGE_RELEASE_CANDIDATE`. A repository writer could therefore reach GitHub's mergeable state after qualification checks without a platform-level check proving the exact signed RELEASE terminal decision.

## Frozen repair objective

Add a dedicated external App check, separate from qualification evidence, that is successful **only** when a valid human-signed manual governance attestation exists for:

- candidate SHA exactly `ffec566022fcd221fb4ab7569ed3bc245f75b546`;
- authority class exactly `HUMAN_RELEASE_AUTHORITY`;
- decision scope exactly `TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE`;
- qualification policy exactly `QUALIFICATION_BOUNDARY_OWNERSHIP` version `6` with the exact policy hash used by the candidate;
- trust root exactly `SETUGO_MANUAL_GOVERNANCE_ED25519_V1`;
- cryptographic Ed25519 verification against the pinned external public trust root.

The required GitHub status context will be named:

`external-release-merge-authority`

and must be produced by governance App ID `4895420`.

## Evidence transport

The signed attestation must live outside the reviewed candidate commit so adding authority evidence does not mutate the qualified candidate SHA. A mutable evidence branch/path is acceptable only because the checker must treat the file contents as untrusted and grant success solely after exact field validation plus signature verification against the external trust root. The evidence location itself grants no authority.

## Negative controls

Before any successful authority check is accepted, the checker must fail closed for at least:

1. missing attestation;
2. missing/invalid Base64 signature;
3. wrong candidate SHA;
4. wrong authority class;
5. wrong terminal action/scope;
6. stale or rebound policy id/version/hash;
7. wrong trust-root id;
8. altered attestation after signing;
9. same check name from a non-App producer (ruleset integration binding must remain App ID 4895420).

## Required sequence

1. Freeze this preregistration.
2. Implement checker-owned verification and publisher logic without changing the exact RELEASE candidate.
3. Demonstrate a genuine RED while no valid signed terminal attestation exists.
4. Add `external-release-merge-authority` to the `phase/release` ruleset, App-bound to ID 4895420, before any merge.
5. Only after independent review findings are adjudicated and the user intentionally signs the exact terminal action may the check become SUCCESS.
6. PR #37 remains unmerged until all required checks, including this authority gate, are green on the exact candidate.

This preregistration does not authorize signing, merging, production qualification, deployment, or any other terminal action.
