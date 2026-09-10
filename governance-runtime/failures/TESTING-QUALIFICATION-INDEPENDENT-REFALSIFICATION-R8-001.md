# TESTING Qualification Boundary — Independent Re-falsification R8

Status: `CHANGES_REQUIRED_PRESERVED`
Authority effect: `NONE_EVIDENCE_ONLY`
Exposed candidate SHA: `61e98ba0ca8fc461b407e91e4f60ffc687fc784e`
Independent reviewer disposition: `CHANGES_REQUIRED`

## Preserved findings

- `R8-01 CRITICAL`: `manual_authority_verifier.py` was not externally pinned, allowing a candidate-modified verifier to forge signed-authority acceptance while the externally pinned policy file remained unchanged.
- `R8-02 CRITICAL as packet evidence gap`: the review packet did not prove that the protected TESTING branch required `external-governance-qualification` from dedicated GitHub App `4895420`. Subsequent live administrative inspection showed that source binding does exist; this does not erase the packet defect.
- `R8-03 CRITICAL/HIGH`: the external checker revision was mutable and its workflow was not exact-revision governed at use time.
- `R8-04 HIGH`: the compatibility facade and other authority-critical imports were outside the externally pinned dependency closure.
- `R8-05 HIGH`: referenced non-secret signed-attestation fixtures were omitted from the review packet, preventing independent reproduction of signature/tamper/replay tests.
- `R8-06 HIGH`: the earlier R7 preregistration named exposed predecessor `2fee17ad...`, while the reviewed candidate was `61e98ba...`; successor exact-SHA lineage was not demonstrated in the packet.
- `R8-07 MEDIUM/HIGH`: runner-visible ruleset validation could not prove empty bypass actors when GitHub omitted that field.

## Subsequent falsification chronology

1. External checker was strengthened to pin `manual_authority_verifier.py`, the active policy implementation, `external_governance_root.py`, and the compatibility facade; to exercise the facade import surface; to pin third-party Actions by exact SHA; and to publish its exact checker SHA.
2. `setugo-governance-check/main` was protected by an active ruleset requiring PRs, blocking deletion and non-fast-forward updates, requiring review-thread resolution, and defining no bypass actors.
3. GitHub App `setugo-governance-vij7661` was granted `Administration: read` in addition to Checks write and Contents read; the checker was changed through protected PR #1 to use the App token for authoritative ruleset retrieval.
4. External run `34468054756` against exact candidate `61e98ba...` failed closed because unauthenticated ruleset retrieval omitted `bypass_actors`.
5. External run `34469665042` against the same exact candidate, using checker SHA `5888775a2c6b845fd6b50222221a405491a69d1a` and an App token with `Administration: read`, again failed closed because GitHub still omitted `bypass_actors` from the App-visible ruleset representation.
6. The second failure published external App check `external-governance-qualification` on exact candidate `61e98ba...` with conclusion `failure` and authority effect `NONE_EVIDENCE_ONLY`.

## Current adjudication

The R8-07 failure is an observability boundary, not evidence that bypass actors exist. Independent administrative inspection of live ruleset `22736961` shows `bypass_actors: []`, `current_user_can_bypass: "never"`, strict required checks, and `external-governance-qualification` source-bound to App `4895420`. However, the frozen R8 contract requires missing material administrative evidence to fail closed. Therefore TESTING remains blocked until that empty-bypass state is bound into an evidence mechanism the external checker can verify without silently treating an omitted field as empty.

No later green run may erase this record.
