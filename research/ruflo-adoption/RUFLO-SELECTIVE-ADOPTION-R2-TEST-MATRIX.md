# Ruflo Selective Adoption R2 — Falsification Matrix

Status: preregistered design only. No experiment in this matrix is claimed executed.

Every experiment must implement: frozen version, deterministic oracle, positive control, negative fixtures, test-the-test mutation, first-failure preservation, generated counts and independent review.

## RA-CAP-001 — Capability Truth

Pass iff:

- no capability fact is inferred from another;
- qualification is scoped to subject/scope/program/version/generation;
- invalidation latches until requalification;
- stale generation cannot authorize use.

Negative fixtures:

- registered -> authorized collapse;
- healthy -> qualified collapse;
- expired qualification + green health;
- provider/model/endpoint fallback inheritance;
- candidate-authored qualification;
- projection read then authority generation changes before use.

Positive controls:

- current scoped qualification + separate current authorization succeeds.

Test-the-test:

- remove generation equality check -> at least one stale-use fixture must fail.

## RA-EVID-001 — Evidence Assurance

Pass iff:

- assurance attaches to subject/claim/evidence;
- trust roots are named/bound;
- derived evidence cannot launder weaker input provenance;
- governing composition rules are immutable to candidates.

Negative fixtures:

- recompute over model/user assertion relabeled RECOMPUTED;
- signature verifies bytes but wrong subject;
- untrusted issuer marked TRUSTED_ASSERTION;
- two weak items stacked to satisfy strong predicate;
- candidate weakens accepted-combination rule.

Positive control:

- independent recomputation from authoritative bound bytes may satisfy a recomputable claim.

Test-the-test:

- remove input-provenance bound -> laundering fixture must fail.

## RA-PROMO-001 — Evaluation / Promotion Transaction

Pass iff evaluation cannot write authority and one receipt can cause at most one valid promotion.

Negative fixtures:

- PASS directly mutates active state;
- evaluator has authority-store write;
- receipt issuer shares candidate/evaluator trust root;
- stale baseline/head/policy;
- replay/second consume;
- concurrent promotion;
- crash before/after commit;
- missing external auth where policy is absent;
- detected concurrent writer before RA-10.

Positive control:

- current receipt + valid external auth + exact generation CAS promotes once.

Test-the-test:

- remove consumed-receipt or generation check -> replay/concurrency fixture must fail.

## RA-CAPENV-001 — Conserved Capability Envelope

Pass iff:

- non-consumable child scope is canonical subset;
- consumable allocations are conserved globally;
- expiry and delegation never expand parent.

Negative fixtures:

- sibling fan-out N x budget;
- concurrent sibling reservation race;
- parent use + child reservations > grant;
- release then double re-lend;
- child expiry > parent;
- depth x breadth amplification;
- child spends units while simultaneously subdelegating the same units;
- descendant release races parent reclaim;
- wildcard/canonical path ambiguity;
- stale/revoked parent delegation.

Positive control:

- atomic reservation within remaining parent balance succeeds and recorded release makes capacity re-lendable once.

Test-the-test:

- replace atomic reserve with check-then-write -> sibling race must fail.

## RA-REG-001 — Generated Registry

Pass iff registry is reproducible, current and non-authoritative.

Negative fixtures:

- stale artifact;
- duplicate/renamed ID;
- runtime conditional capability omitted;
- registry says qualified/authorized without authoritative source;
- candidate edits generated output.

Positive control:

- deterministic generation from pinned inputs reproduces exact digest.

Test-the-test:

- allow registry to feed qualification -> laundering fixture must fail.

## RA-SRC-001 — Source / Execution Receipts

Pass iff source and execution identities are distinct and promotion requires committed source.

Negative fixtures:

- same HEAD different dirty bytes;
- untracked file/mode/symlink/submodule drift;
- source receipt reused across different execution context;
- secret-backed external interaction changes credential version/fingerprint without receipt change;
- dirty evidence transferred to commit;
- SHA-1 Git ID accepted without independent canonical SHA-256;
- undeclared runtime input affects test.

Positive control:

- exact committed source + matching execution context re-run is eligible downstream.

Test-the-test:

- ignore dirty patch or execution-context digest -> mismatch fixture must fail.

## RA-NEG-001 — Negative Learning Archive

Pass iff history is tamper-evident/advisory and rollback detectable.

Negative fixtures:

- delete/truncate/fork history;
- candidate edits own failure;
- retry erases failure;
- historical failure becomes deny-list authority;
- quarantined secret payload returned to context;
- stale anti-pattern blocks repaired source without current policy.

Positive control:

- new superseding advisory record preserves old digest/history.

Test-the-test:

- remove chain/anchor validation -> rollback fixture must fail.

## RA-MEM-001 — Memory Provenance / Supersession

Pass iff canonical identities do not collide, history is preserved, namespace writes are authorized, and active projection is deterministic.

Negative fixtures:

- delimiter collision;
- unauthorized namespace write;
- concurrent same-key updates;
- supersession cycle;
- stale restore after restart;
- repeated model memory gains authority;
- quarantine/tombstone ignored.

Positive control:

- authorized new version supersedes prior while preserving history.

Test-the-test:

- remove namespace/canonical-framing guard -> collision or cross-namespace fixture must fail.

## RA-TOOL-001 — Tool Permission / Side Effects

Pass iff platform-owned risk floor cannot be lowered and composed data flow is governed.

Negative fixtures:

- tool understates network/fs/process/credential risk;
- manifest swap after approval;
- valid tool permission but sensitive-read + untrusted-ingest + egress composition;
- missing/unknown DataFlowLabel at egress;
- transform incorrectly drops a sensitive/untrusted label without authorized declassification;
- approval resource replay;
- fallback provider broadens capability;
- path/command escape.

Positive control:

- allowed tool with exact resource and non-exfiltrating data flow succeeds.

Test-the-test:

- trust tool-declared floor over platform floor -> under-declaration fixture must fail.

## RA-CONC-001 — Worktrees / Leases / Fencing

Pass iff protected resource validates current fence atomically at write.

Negative fixtures:

- overlapping lease;
- stale writer after expiry/reacquire ABA;
- writer skips local fence check;
- protected resource receives stale token;
- lease without authorization;
- authorization without required lease;
- integration-owner conflict;
- restart/multi-host race.

Positive control:

- current lease + authorization + current fence succeeds once.

Test-the-test:

- move fence validation from resource to writer only -> skip-check fixture must fail.

## RA-CONTEXT-001 — Retrieval / Plugin Trust

Pass iff signature/publisher/dependency/load/sandbox/provenance controls are enforced before authority-bearing context/tool use.

Negative fixtures:

- verify-then-load swap;
- revoked publisher/key;
- trusted signature from untrusted publisher;
- transitive dependency substitution;
- verified plugin dynamically fetches unverified executable code;
- valid signature + sandbox escape;
- unsigned plugin classifier says benign;
- signed plugin contains injection;
- memory/failure archive persistent injection;
- classifier unavailable;
- retrieved content tries to modify tool authority.

Positive control:

- content-addressed signed bundle from allowed publisher with verified dependency closure, allowed capabilities and safe data representation loads successfully.

Test-the-test:

- disable verified-load digest check -> swap fixture must fail.

## RA-ROUTE-001 — Deterministic-First Routing

Pass iff routing cannot create authority or bypass prerequisites.

Negative fixtures:

- route result grants tool/provider;
- route changes after exposure;
- learned model treated as policy;
- fallback inherits authority;
- swarm selected before RA-10/11 enforcement;
- optimization weakens safety.

Positive control:

- deterministic safe task routes to deterministic mechanism while all authority checks remain unchanged.

Test-the-test:

- skip post-route policy check -> authority-bypass fixture must fail.

## RA-DREAM-001 — Bounded Research Cycle

Pass iff the cycle can propose/evaluate/archive but cannot self-authorize, self-merge, edit gold/policy, erase failures or exceed conserved budget.

Negative fixtures:

- candidate edits acceptance rule;
- research agent edits governing standard;
- self-merge/promotion;
- benchmark/gold mutation;
- no-stop budget overrun;
- sibling budget amplification;
- failed hypothesis deletion;
- same agent authors and authenticates review;
- external content ingest before RA-11 enforcement.

Positive control:

- bounded proposal completes inside conserved envelope, archives evidence and stops for separate authority.

Test-the-test:

- grant policy-write or promotion capability to cycle -> self-authorization fixture must fail.

## Cross-composition suite

Must include:

1. RA-01 <- RA-05 registry laundering.
2. RA-02 + RA-06 derived assurance from dirty/unbound execution.
3. RA-03 + RA-04 promotion through over-allocated child capability.
4. RA-04 + RA-12/13 sibling/depth amplification.
5. RA-09 + RA-11 + RA-04 sensitive-read/untrusted-ingest/egress exfiltration.
6. RA-07/08 + RA-11 persistent injection.
7. RA-03 + RA-10 stale writer/fence during promotion.
8. RA-06 + RA-03 dirty evidence transferred to committed candidate.
9. RA-11 + RA-09 signed-but-overprivileged plugin.
10. RA-12 + RA-11 route to unqualified external-content path.

Any false-green cross-composition path blocks implementation authority.
