# GOV-POSTMERGE-CONTINUITY-001 — Post-Merge Continuity Reconciliation

Status: **PREREGISTERED BEFORE REPAIR**

## Observed defect

After PR #10 merged at `a2fcd2ba9bc0e5828ee69056c23207fb431ecea6`, durable `session-state.json` and `shared-memory.json` remained at checkpoint 041 and still described PR #10 integration review reissuance as the execution frontier. Later PR #11 review `REV-GOV-PR11-001` returned PASS and marked continuity grounding supported, but the reviewed candidate still contained this stale post-merge pointer. The PASS therefore contains a false-negative on continuity freshness and is not sufficient by itself for PR #11 promotion.

## Frozen repair contract

1. A merged/closed governed transition MUST make any older pending-review/pending-merge handoff stale and non-resumable.
2. The durable execution handoff MUST advance to the actual next frontier only after verifying Git merge state and retained review evidence.
3. Shared memory MUST exactly mirror the authoritative handoff fields required by the validator and remain non-authoritative independently.
4. Generic `CONTINUE` MUST resolve to the repaired durable handoff, never the stale pre-merge PR #10 action.
5. Prior PR #10 and PR #11 review/provider-failure history MUST remain preserved; no prior failure may be rewritten.
6. `REV-GOV-PR11-001` remains valid evidence for the request-integrity mechanism dimensions it actually tested, but its continuity-grounding conclusion MUST NOT be used as authority for the stale checkpoint.
7. A corrected PR #11 review MUST independently reassess the reconciled continuity state before promotion.

## Frozen cases

- `GPC-01`: merged PR #10 + pending PR #10 handoff is classified stale.
- `GPC-02`: repaired authoritative handoff points to the verified post-merge frontier.
- `GPC-03`: shared-memory handoff exactly mirrors authoritative handoff.
- `GPC-04`: generic `CONTINUE` follows repaired handoff.
- `GPC-05`: old PR #10 review/provider-failure history is retained.
- `GPC-06`: prior independent PASS cannot override contradictory Git merge evidence.
- `GPC-07`: PR #11 promotion remains blocked until corrected independent review of the reconciled state.

## Claim boundary

A pass establishes deterministic repository continuity reconciliation for the tested Git-backed checkpoint and handoff. It does not guarantee that external chat products always bootstrap Git automatically; inability to verify authoritative state must still fail closed to `GROUNDING_REQUIRED`.
