# R8 v15-r1 — Executable Schema Freeze Preregistration V1

Status: **SCHEMA_FREEZE_CANDIDATE — NON_AUTHORITATIVE**
Authority effect: **NONE**

Frozen semantic candidate:
- `c721b38cf8b00294797300b526596ce723a47ff8`

Accepted review state:
- independent normalized-design review: `BOUNDED_PASS`
- targeted review-evidence closure: `EVIDENCE_CLOSURE_PASS`

This phase may encode the accepted semantics into machine schemas and deterministic validation contracts. It may not add, remove, weaken, reinterpret, or broaden authority.

## 1. Freeze rules

1. Every executable schema uses JSON Schema 2020-12.
2. Authority-bearing objects use `additionalProperties: false`.
3. Every authority-relevant field is required unless the frozen design explicitly defines absence/null as meaningful.
4. Unknown source details are represented only as opaque IDs/digests/references. The schema freeze must not invent semantics to make a field more specific.
5. Closed enum values are frozen only where the accepted design explicitly enumerates them.
6. Schema validation is not semantic authorization.
7. Cross-field, temporal, graph, cardinality, precedence, replay, equality, freshness and no-fallback invariants that JSON Schema cannot express are owned by the deterministic SchemaFreezeValidator contract.
8. Any semantic change invalidates this freeze and requires a successor design review.

## 2. Schema inventory

### ESF-01 — runtime authority contracts
Machine definitions for:
- semantic-head snapshot;
- SRTT-4 replacement input/output;
- semantic resolved result;
- AuthorityReadSet;
- DecisionPresealContext;
- qualified time proof;
- VerifiedStateSeal;
- EffectIntent / effect-state record;
- rotation barrier / state-transfer certificate;
- RecoveryContext;
- migration binding.

Trace:
- NORM-011..NORM-016;
- NORM-024..NORM-027;
- NORM-030..NORM-039;
- normalized detail appendix §§6,10,13,14,15.

### ESF-02 — GuardRegistry
Strict record shape for current guard identity, positive case references, negative cases and fault-proof classes.

Trace:
- NORM-040.

### ESF-03 — CaseRegistry
Strict case identity and source-lineage shape.

Trace:
- NORM-040 and GuardRegistry/CaseRegistry review closure.

### ESF-04 — SRTT-4
Strict fixed-domain, enum-domain, row, result and decisive-rule record shapes.

Trace:
- NORM-027;
- SRTT-4 RuleRegistry;
- SRTT-4 total table.

### ESF-05 — BSP-5
Strict current-candidate version, parser-state, semantic-test state, current-status binding and omission-policy shapes.

Trace:
- NORM-041.

### ESF-06 — guard-omission evidence
Strict reproducible evidence record with explicit SHA-256/UTF-8/LF/no-trailing-LF digest basis and exact explicit guard/case sets.

Trace:
- NORM-042;
- accepted H-1 evidence closure.

### ESF-07 — NCG structured closure
Strict dependency node/edge, evaluation-order and ownership structures.

Trace:
- NORM-043;
- v15 direct-edge contract.

## 3. Deterministic validator obligations

JSON Schema success alone is insufficient. The SchemaFreezeValidator must recompute at minimum:

### SFV-01 — SRTT domain cardinality
The declared variable Cartesian domain must equal exactly 2304 tuples with fixed `source_entry_state=REVOKED`.

### SFV-02 — SRTT tuple uniqueness
Exactly one row per declared variable tuple.

### SFV-03 — decisive-rule validity
Every table row references exactly one declared SRTT-4 RuleRegistry rule.

### SFV-04 — decisive-rule recomputation
Re-evaluate every row under the frozen precedence:
1. ineffective mapping;
2. invalid lineage;
3. invalid ANY;
4. old scope NO_MATCH;
5. BLOCK_OLD_SCOPE;
6. destination NO_MATCH;
7. exact-effect eligibility/invalidity;
8. mapped SAME/NARROWER;
9. mapped BROADER only with both expansion predicates;
10. mapped invalid remainder.

Any row mismatch fails the freeze.

### SFV-05 — GuardRegistry identity
Guard IDs must be unique and contiguous `G001..G156`.

### SFV-06 — CaseRegistry identity
Case IDs must be unique. Every guard-referenced positive/negative case must exist.

### SFV-07 — omission evidence
For all 11 source-evidence records:
- recompute the declared raw section SHA-256;
- parse guard IDs;
- expand inclusive case ranges;
- compare exact explicit guard/case sets;
- require no missing/extra IDs.

### SFV-08 — BSP structural authority
Exactly one structural current-status block for candidate version 15.
Structural markers are recognized only as exact standalone lines outside fenced code.
Marked semantic-test sections must be paired, non-nested, non-empty and ID-consistent.

### SFV-09 — dependency graph
Every edge endpoint must be declared.
The graph must be acyclic.
No duplicate edge.
Direct-edge semantics only; transitive closure must not be inserted as authority.

### SFV-10 — evaluation order
Every consumed stage output must originate at an earlier stage.
No later stage may reinterpret an earlier blocker as eligible authority.

### SFV-11 — effect success
Only `SUCCEEDED_RECONCILED` may be interpreted as external-effect success.
`ACKNOWLEDGED_UNVERIFIED` and `UNCERTAIN` are never success.

### SFV-12 — time threshold
Authority time evidence requires at least 2 distinct qualified source attestations out of the reference population of 3, bound to one DecisionPresealContext digest and one single-use nonce.

### SFV-13 — no optional authority bypass
Missing required authority field is validation failure, not a fallback/default.

## 4. Canonicalization boundary

The freeze does not redefine GCP-1.

Schemas define data shape only. Canonical signing/digest inputs continue to obey the inherited rules:
- absent != null;
- defaults before canonical digest only;
- NFC keys;
- duplicate/colliding keys reject;
- set arrays canonically sorted with duplicates rejected;
- signed-int64 frozen lexical/range rules;
- extension maps only when explicitly schema-declared;
- reserved `sys:` namespace prohibited for extensions.

## 5. Freeze acceptance criteria

The schema freeze may be marked internally ready for independent review only if:

- all listed schemas parse as JSON;
- all schemas declare JSON Schema 2020-12;
- authority-bearing schemas default closed;
- all current machine artifacts validate structurally against their matching schema;
- SFV-01..SFV-13 recompute PASS;
- schema manifest has no missing required subject;
- no frozen normalized rule is weakened by a schema default, omitted field, open enum, or open authority-bearing property set;
- semantic candidate commit remains `c721b38cf8b00294797300b526596ce723a47ff8`.

Internal PASS grants no implementation authority. It permits only a fresh independent executable-schema review.


## 6. Validator ownership expansion

The initial preregistration listed SFV-01..SFV-13 as the minimum deterministic obligations. The executable validator contract is now frozen at **SFV-01..SFV-34**.

The added obligations do not change semantic design. They make inherited enforcement ownership explicit for:
- T0 successor 4-of-5 / 3-domain threshold and monotonic generation;
- BTW rollback/equivocation;
- GGS/LAS quorum, rollback and atomicity;
- rotation barrier/STC one-barrier-one-rotation semantics;
- GCP canonicalization;
- review materiality and human-review independence;
- coherent CSM/current semantic-state sequence;
- external root anti-self-grant.

The machine-readable validator contract at
`schemas/governance-r8/v15-r1/schema-freeze-validator-contract.json`
is the complete validator-rule inventory for this freeze candidate.
