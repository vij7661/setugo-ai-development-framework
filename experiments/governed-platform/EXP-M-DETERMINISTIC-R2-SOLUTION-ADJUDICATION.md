# EXP-M Deterministic R2 — Reviewer Solution Adjudication

Status: `ACCEPT_WITH_CORRECTIONS`

Authority effect: `NONE`

The independent reviewer also supplied a remediation design. Its governing direction is correct:

- no boolean laundering;
- one authoritative path;
- no production bypass;
- evidence rather than caller strings;
- independent predicate/mutation/fixture closure;
- commit-bound fresh evidence.

However, several example solutions require correction before implementation.

## Accepted directly

The following directions are accepted:

- remove `disabled_predicates` from production;
- introduce an externally bound predicate context/evidence bundle;
- make provider qualification record/plan/attempt closure load-bearing;
- make context isolation and fence currentness load-bearing;
- add persistent/permanent attempt voiding;
- wire retrieval into authoritative admissibility/admission;
- compute delivery completeness from returned bytes;
- make witness qualification/accessibility load-bearing;
- strengthen materialization and qualified transforms;
- independent closure across independently generated evidence;
- authentic validator-logic mutation;
- required-evidence/manifest binding;
- explicit retry lineage;
- external egress/prompt expected values;
- commit-bound fresh execution evidence.

## Required corrections to the proposed solutions

### SA-01 — Mutation example must create a false-green, not another rejection

The supplied example monkeypatch returns `False`, which leaves the guard rejecting.

Correct rule:

1. independent malformed fixture fails under normal production code;
2. isolated mutation removes/weakens the exact guard or forces that predicate validator to accept;
3. the mutated code becomes false-green;
4. the test suite detects the false-green and therefore kills the mutation.

No mutation-control hook may exist in the production public API.

### SA-02 — PredicateContext must contain every externally expected value

The context must include, where applicable:

- expected request/attempt/session;
- expected reviewed source commit/tree;
- expected authority snapshot ID/hash/version;
- expected provider/model/adapter/operating point;
- expected profile/plan/qualification identities;
- expected egress version;
- expected transition class/risk-policy version;
- expected fence version;
- expected prompt provider/mode;
- expected witness provider/mode/prompt mode;
- expected retrieval source/version/range;
- expected final-context ID/hash;
- max final-context/witness budgets;
- current trusted clock value;
- expected predicate-registry version.

Expected values may not be read back from the evidence object being validated.

### SA-03 — Retrieval examples must not self-bind

The proposed example uses `record.attempt_id`, `record.session_id`, `record.source_id` and `record.source_version` as their own expected values.

That is self-referential.

Expected retrieval identity/range must come from the frozen request/interaction/retrieval contract and PredicateContext.

### SA-04 — Qualification closure must be recomputed from attempt records

A field such as `record.all_trials_closed=True` is not itself authoritative.

The validator must recompute closure from immutable attempt records and verify any summary field only as a consistency assertion.

Trial/confirmation requirements must follow the frozen R5 qualification program, including non-empty required sets, zero hard failures, no replacement/reroll and exact physical-attempt closure.

### SA-05 — Closure compares target mappings, not raw mutation/fixture IDs

Mutation IDs such as `TM-O-x` and fixture IDs such as `negative:x` are not equal to predicate ID `x`.

Each mutation and negative fixture must expose `target_predicate_id`.

Closure compares:

- required predicate IDs;
- actual verdict predicate IDs;
- mutation target predicate IDs;
- actually executed mutation target predicate IDs;
- killed mutation target predicate IDs;
- negative fixture target predicate IDs.

Also require every required predicate to have at least one executed/killed mutation and at least one negative fixture.

### SA-06 — Retry linkage example needs corrected semantics

A retry is itself a physical dispatched request, so rejecting a retry merely because its retry ID is in the physical dispatch ledger would be wrong.

Use structured attempt records:

- first attempt ID equals/plugs into one planned root attempt;
- retry ID is globally unique and not a planned root ID;
- retry has `parent_attempt_id` pointing to an existing failed attempt;
- retry appears in the physical request ledger;
- failed parent remains preserved;
- retry cannot replace the parent in closure counts;
- unscheduled first attempts cannot count toward confirmation.

### SA-07 — Representation qualification cannot rely on `qualified=True`

A RepresentationRecord may carry a cached summary, but authoritative validation must check:

- transform ID;
- transform implementation/hash/version;
- transform registry version;
- source hash;
- representation hash;
- transformation parameters/coverage;
- registry entry outside candidate write authority.

### SA-08 — Materialization needs typed entries for symlink/archive semantics

A plain `Mapping[str, bytes]` cannot faithfully model symlinks, archive recursion or compressed-vs-uncompressed size.

Introduce typed materialization entries with at least:

- raw member name;
- normalized path;
- kind (file/symlink/archive/etc.);
- bytes or link target;
- compressed/uncompressed sizes where relevant;
- recursion depth;
- source member identity.

Then enforce path, symlink, recursion, member count, per-member, total and decompression-ratio bounds.

### SA-09 — Witness proof needs trusted challenge/expected-answer binding

A non-empty challenge/response is not proof of accessibility.

The trusted harness must freeze:

- challenge ID;
- source slice identity/hash;
- expected extraction answer/hash;
- challenge generation after evidence freeze;
- expected answer hidden from reviewer adapter.

Witness output remains non-semantic/non-evidence.

### SA-10 — Admission ledger must survive process restart in deterministic proof

A purely ephemeral in-memory ledger would not prove permanent void semantics.

For the deterministic implementation, use a persistence-backed test ledger or a storage abstraction with restart/recovery tests proving:

- VOID persists;
- COMMITTED persists;
- compare-and-set generation survives restart;
- an old snapshot cannot revive an attempt.

### SA-11 — Freshness binds to the NEW final remediation source commit

The supplied solution says fresh results must bind to `66129025...`.

That commit is the source that just failed review and will change during remediation.

Required two-stage identity:

1. freeze final remediation source commit/tree S;
2. execute all tests/mutations/self-falsification against exactly S;
3. generate result/log/review artifacts that explicitly bind to S;
4. commit those evidence files later in packet/evidence commit E;
5. E must not be confused with reviewed source S.

The historical `66129025...` evidence remains superseded and preserved.

### SA-12 — Egress, reviewer provenance and disposition must be externally governed

Expected egress policy/version, reviewer trust/provenance requirements and promotable dispositions come from the frozen authority/policy context.

They may not be supplied by the candidate evidence state.

## Result

The reviewer solution is a strong basis, but implementation must follow the corrected R2 remediation file rather than copy the supplied snippets literally.
