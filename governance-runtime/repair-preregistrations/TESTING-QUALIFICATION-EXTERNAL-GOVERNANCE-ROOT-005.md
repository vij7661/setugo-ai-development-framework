# TESTING Qualification External Governance Root Repair Preregistration 005

Status: PREREGISTERED_BEFORE_MECHANISM_CHANGE
Phase: TESTING
Authority effect: NONE_EVIDENCE_ONLY
Base candidate SHA: `6fb96bb8fd0dd4c5ed9c065a2e4350eec0e0cf67`
Preserved post-merge RED: workflow run `34449284629`
Open finding: MR-005 — CANDIDATE_MODIFIABLE_TRUST_ROOT

## Trigger

The first MR-005 repair attempted to require one independent approving GitHub review before changes could enter `phase/testing`. That mechanism is not usable in the current single-owner repository because no independent collaborator exists. The user explicitly rejected creating a second self-controlled account and instead created a separate governance-root repository, made it public, and archived it.

The earlier one-approval contract remains preserved as a failed mechanism attempt. This preregistration does **not** reinterpret its RED as green and does not weaken that frozen historical result.

## Replacement hypothesis

MR-005 can be repaired for the current single-owner TESTING boundary if all of the following are true:

1. The manual-governance Ed25519 public key is sourced from a separate repository: `vij7661/setugo-governance-root`.
2. The authoritative external root is pinned to exact commit `5f470774ec8c17f5519da8db2aaae59af114cef9`, not to a mutable branch name.
3. That repository is public and archived at qualification time; any non-public, non-archived, unavailable, or changed external state fails closed.
4. The external PEM bytes must equal the expected Ed25519 public-key DER fingerprint `2b1b97ab0bf99e71f4a93f51fd8e6c3eb30063d83ba2eb4c091492a95f9c11f2`.
5. Runtime authority verification must use the externally fetched pinned PEM, never a candidate-local PEM, for governance decisions.
6. Candidate-local replacement of the PEM, local pin, local metadata, or a self-signed attestation must not alter the external root or make verification succeed.
7. `phase/testing` remains protected by an active GitHub ruleset requiring a pull request, deletion protection, non-fast-forward protection, strict `falsify-qualification-boundary` status checks, and no bypass actors. Approval count may be zero in the single-owner profile; a human merge is still required because direct updates are blocked.
8. The workflow token remains read-only for repository contents. Candidate/runtime code must not possess credentials capable of mutating either the protected TESTING branch or the archived external governance-root repository.
9. External-state retrieval failure, malformed metadata, unarchived root, wrong exact commit, wrong PEM bytes/fingerprint, wrong trust-root ID, or trust-root substitution must fail closed.
10. The external root proves control of the configured private key, not independent real-world identity of a person.

## Frozen attacks to add before claiming repair

- Local PEM substitution while external root remains unchanged.
- Local fingerprint/pin substitution while external root remains unchanged.
- External root URL/commit rebinding.
- Wrong external PEM bytes.
- Unarchived external governance-root state.
- External root unavailable/malformed.
- Same candidate supplies a self-generated keypair and signature.
- Ruleset loses PR requirement, strict status check, force-push/deletion protection, or gains a bypass actor.

## Acceptance criteria

Construction PASS requires all frozen attacks above to be collected by the actual harness and to pass, plus the existing manual-authority and terminal-authority suites. A CI green remains evidence only.

Scientific closure still requires independent manual refalsification. This preregistration does not grant TESTING, RELEASE, or PRODUCTION authority.
