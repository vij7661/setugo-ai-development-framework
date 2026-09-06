# EXP-I Systematic Analysis — Issuance Ledger / Anti-Rollback Anchor State Space

## State

**PREREGISTERED — IMPLEMENTATION EXPOSED FOR CONSTRUCTION, SCIENTIFIC CANDIDATE NOT YET FROZEN**

This is not EXP-I Pilot 20. It is the first systematic-analysis track created by the post-P19 prototype stop-criteria review.

## Scientific question

Within an explicit finite abstraction of the Pilot 19 issuance-ledger / independently authenticated anti-rollback-anchor protocol, do any bounded operation, crash, restart, replay, stale-state, conflicting-state, or reconciliation interleavings violate the frozen authority invariants even though the hand-authored P19 vectors passed?

## Relationship to Pilot 19

The model must preserve the essential P19 state distinctions:

- reconciled ledger + anchor + receipt;
- durable ledger commit before anchor advancement;
- anchor temporary write before atomic replace;
- atomic anchor replace before receipt commit;
- receipt persistence;
- stale ledger substitution;
- stale anchor substitution;
- same-generation conflicting anchor material;
- duplicate/replayed issuance intent;
- semantic rebind attempt;
- concurrent reconciliation attempts;
- crash/restart between every modeled transition.

The model is an abstraction. Passing it cannot upgrade P19 into a distributed, Byzantine, physical-power-loss, KMS/HSM, or production claim.

## Frozen finite bounds

- generations modeled: `0..3`
- distinct recovery identities: `A`, `B`, `C`
- distinct semantic targets per recovery identity: `T1`, `T2`
- maximum global transition depth from genesis for exhaustive safety exploration: `12`
- SA-09 local clean-liveness bound from each uniquely recoverable state: `8` transitions
- reconciliation actors: `R1`, `R2`
- search strategy: breadth-first search with state deduplication
- counterexample requirement: retain the shortest discovered transition trace for each violated invariant
- crash/restart abstraction: volatile/in-flight operation state is erased; durable ledger, anchor and receipt state remain as modeled

### Pre-scientific corrections preserved before candidate freeze

1. The initial preregistration named only `A`, `B` while also bounding generations through 3. Before any analysis implementation or scientific exposure, the identity domain was corrected to `A`, `B`, `C` so generation 3 is reachable without violating exact recovery-intent idempotency. No invariant, global depth bound, acceptance condition, or expected outcome changed.

2. Construction run `34061803290`, job `101563528187`, on head `d2e82fe2cc29be417d6488573619ce255147e6be` exposed a specification/harness defect in SA-09 before scientific freeze. The original wording incorrectly used the **remaining global depth from genesis** as the local recovery-liveness budget. A valid ledger-ahead state first reached at global depth 5 therefore had only 7 transitions left, although the exact worst-case clean obligation needs 8 transitions: current reconciliation (3), next issuance (1), next reconciliation (3), and trusted-minimum consequential use (1). This made liveness depend on discovery depth rather than protocol recoverability. The failure and classification are preserved in `EXP-I-STATE-SPACE-CONSTRUCTION-FAILURE-001.json`.

The correction separates the two bounds: global exhaustive safety exploration remains frozen at depth 12, while SA-09 is checked with a fixed local bound of 8 transitions from every uniquely recoverable state reached by that global exploration. No authority safety invariant, state classification, reconciliation rule, mutant expectation, generation bound, or global safety-search depth is weakened.

The global depth/state bound may be increased only in a later separately frozen analysis. It must not be reduced after first scientific exposure to obtain a pass. The SA-09 local bound is now frozen at 8 for this candidate and must not be increased after first scientific exposure to obtain a pass.

## Frozen invariants

**SA-01 No authority from ambiguity.** A conflicting or non-uniquely derivable durable state cannot authorize trusted-minimum use.

**SA-02 No ledger-only authority.** Ledger advancement without required anchor/receipt correspondence cannot authorize trusted-minimum use.

**SA-03 No anchor-only authority.** Anchor advancement without exact committed-ledger correspondence cannot authorize trusted-minimum use.

**SA-04 Monotonic trust.** Once a generation has been accepted/reconciled, no later reachable accepted state may move the trusted generation backward.

**SA-05 No semantic rebinding.** One recovery identity cannot become durably associated with two different target semantics.

**SA-06 At-most-once consequential advancement.** Crash/retry/replay does not create more than one authoritative issuance/advance for one recovery intent.

**SA-07 Deterministic reconciliation.** A uniquely derivable divergence has at most one authoritative reconciliation target and caller/reconciler identity cannot alter it.

**SA-08 Fail-closed conflict.** Same-generation conflict, stale substitution, non-contiguous divergence, or non-uniquely derivable state cannot auto-reconcile or authorize use.

**SA-09 Bounded liveness from safe recoverable states.** Every modeled uniquely recoverable crash state reached within the global depth-12 exploration has a clean path, within **8 local transitions from that state**, to exact reconciliation and then one clean next-generation consequential advancement. At generation 3, where no generation 4 exists inside the finite model, the obligation is exact reconciliation of the current recoverable state.

**SA-10 External authority.** Caller/model/reviewer-supplied target choice cannot select the trusted reconciliation state or bypass correspondence checks.

## Explorer-integrity / unsafe-mutant checks

The scientific candidate must also demonstrate that the explorer can falsify deliberately unsafe variants. At minimum:

- **MUT-01 Ledger-only authority:** a mutant that authorizes when the ledger is ahead of anchor/receipt must produce a counterexample to SA-02.
- **MUT-02 Caller-selects-conflict:** a mutant that allows a caller to select one side of conflicting same-generation state must produce a counterexample to SA-07 and/or SA-08/SA-10.
- **MUT-03 Anchor-only authority:** a mutant that authorizes anchor-ahead state must produce a counterexample to SA-03.
- **MUT-04 Semantic rebind:** a mutant that permits one recovery identity to bind to two targets must produce a counterexample to SA-05.

A mutant not being detected is a scientific failure of the analysis harness, not evidence that the production mechanism is correct.

## Acceptance rule

`BOUNDED_PASS` only if, on one exact frozen SHA:

1. the implementation corresponds to the preregistered abstraction and bounds;
2. exhaustive BFS completes for all reachable states within global depth 12 and generations 0..3;
3. SA-01..SA-10 have zero counterexamples in the production model, including SA-09 using the fixed local bound of 8;
4. MUT-01..MUT-04 each produce the expected counterexample class with retained shortest traces;
5. the complete governed-platform regression suite passes on the same exact frozen SHA;
6. first frozen-head result is preserved and classified before any repair;
7. result is reported as bounded model evidence only.

CI green alone is not scientific acceptance.

## Failure classification

Before repair, classify first failure as one or more of:

- mechanism counterexample / mechanism defect;
- model-abstraction defect;
- state-space harness defect;
- mutant-integrity defect;
- test expectation defect;
- regression defect;
- environment/tooling defect;
- requirement unresolved.

No frozen authority safety invariant may be weakened to obtain a pass. Any post-freeze change to the local SA-09 bound requires a separately preregistered candidate rather than mutation of the frozen one.

## Explicit nonclaims

A pass does **not** prove:

- correctness beyond global depth 12 or generation 3;
- liveness requiring more than 8 clean local transitions from a recoverable state;
- equivalence of the finite abstraction to every Python/SQLite/filesystem behavior;
- physical power-loss or storage-controller durability;
- exhaustive thread/process scheduling at the implementation instruction level;
- independent disks, hosts, administrators, clouds, KMS or HSM trust domains;
- network-partition correctness;
- Byzantine/malicious-host tolerance;
- cryptographic primitive correctness;
- formal theorem proof or unbounded model checking;
- production/release/deploy authority;
- third-party independent scientific certification.

## Next action after this analysis

If a production-model counterexample is found, preserve its exact shortest trace, diagnose it, and only then decide whether implementation repair and an isolated reproduction experiment are required.

If bounded analysis passes, do not automatically increase pilot count. Proceed toward the integrated governed-platform MVP and external independent evidence review; increase the model bound or add a second formalization only when it materially tests a new hypothesis.
