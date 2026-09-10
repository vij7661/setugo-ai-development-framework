# RELEASE Entry Control Gap — 001

Status: BLOCK_RELEASE_ENTRY_PENDING_CONTROL
Authority effect: NONE
Qualified TESTING source SHA: `15d50cc25ae524fc64e2c65269c91135e0361846`
Existing RELEASE branch SHA: `a5726dcb9236e31028ec70603bee35b30b9dbe66`

The signed TESTING terminal action authorizes only `READY_TO_BEGIN_RELEASE_QUALIFICATION` for the exact source SHA. Before the governed RELEASE phase can consume that source, the destination branch must have independently enforced controls appropriate to the RELEASE qualification boundary.

Observed live GitHub state at transition time:

- `phase/release` exists, but GitHub reports it as unprotected;
- the repository ruleset collection contains only the active `phase/testing` ruleset;
- therefore no repository ruleset currently targets `refs/heads/phase/release`.

Fail-closed decision: do not move, merge, fast-forward, or otherwise update `phase/release` yet. Creating RELEASE evidence against an unprotected destination would allow the candidate/repository writer to mutate the governed RELEASE subject outside the intended phase control.

Required before entry:

1. active repository ruleset targeting exactly `refs/heads/phase/release`;
2. deletion and non-fast-forward protection;
3. pull-request requirement with review-thread resolution;
4. strict required status checks for RELEASE qualification, source-bound where supported;
5. empty bypass actors / no user bypass under the selected single-owner governance profile;
6. live re-read of the installed control before the exact TESTING SHA is introduced to RELEASE;
7. preserve the existing stale `phase/release` history; do not rewrite historical evidence as though it had already represented this qualified TESTING candidate.

This is a RELEASE-entry boundary finding, not a defect in the already qualified TESTING subject. The TESTING bounded pass and signed readiness decision remain bound to the exact TESTING SHA and do not authorize bypassing this destination-control requirement.
