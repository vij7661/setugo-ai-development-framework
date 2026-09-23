# R8 v14 — NCG-1 Dependency, Evaluation-Order, and Ownership Matrices

Status: **INTERNAL_NORMALIZATION_ARTIFACT — NON_AUTHORITATIVE — NCG-1 INPUT**
Authority effect: **NONE**

## 1. Invariant / dependency matrix

| Mechanism | Depends on | Must precede | Blocking conditions | Normalized rule |
|---|---|---|---|---|
| T0 successor | predecessor T0, EBA authorization, MTR reservation, BTW consistency | T0 activation | wrong/duplicate generation, invalid auth, rollback/equivocation | one authorized digest per next generation |
| MTR freshness | live challenge, trust-domain/purpose binding, monotonic MTR state | root-sensitive authority use | stale/replayed/wrong-context response | no stale-token authority fallback |
| Canonical identity | subject registry, controller attestations, lineage | quorum/reviewer independence | alias collision, stale/revoked identity | aliases never manufacture independence |
| Revocation | LAS revocation head, MTR high-water where required | credential/producer/reviewer use | stale head, revoked interval | no retroactive validity via UNREVOKE |
| GGS-3 | T0/MTR/BTW, namespace state, barrier/STC for rotation | genesis/config activation | namespace rollback, double genesis, state-transfer mismatch | one committed genesis per constitution |
| LAS-3 | hard state, config, StreamHeadMap, idempotency ledger | all authority transitions | stale term/index, head conflict, equivocation | serialized authority state |
| RBP/STC | current sequencer state + barrier | ENTER_JOINT/ACTIVATE | write during freeze, state mismatch | one frozen snapshot per rotation |
| AIEP/AIG | runtime/workload identity, broker policy | authority input reads | direct undeclared read, unqualified runtime | broker-only mutable input access |
| CSM-5 | LAS semantic streams | semantic resolution | mixed/stale semantic heads | one current semantic snapshot |
| AIM-4 | CSM-5, AIMScopePolicy, decision scope | ResolverPolicy/CSRULE | permission drift, revoked descriptor, conflict | Smax before ANY/lifecycle filtering |
| ResolverPolicy | CSM-5, RIR, RCS | CSRULE | implementation/policy/runtime mismatch | policy + implementation identity |
| RIR-2 | ResolverPolicy, runtime/workload identity, RCS | resolver execution | temporal ineligibility, conflict | exact active tuple at sequence |
| RCS-2 | RIR record, suite/vector/harness identity | resolver qualification | stale/failed/mismatched evidence | conformance necessary, not sufficient |
| CSRULE | AIM-selected lineage, CSM, ANY permission, mappings, SREP | semantic result | Smax blocker, revoked unresolved, peer conflict | no lower fallback |
| SRTT-3 | revoked source, mappings, current ANY permission | replacement discharge | invalid relation, unauthorized broader scope | total deterministic replacement table |
| SREP-1 | resolved rule/effect/scope/lineage | successor/peer comparison | different result digest | canonical equivalence only |
| AuthorityReadSet | AIG + current heads | DPS/seal | undeclared/unsealed mutable input | every authority read sealed |
| DPS/time | read set, semantic heads, revocation, runtime | VerifiedStateSeal | stale/mismatched context, nonce replay | single-use context-bound time |
| VerifiedStateSeal | DPS + time proof + current state | COMMIT_WITH_SEAL | head/state changed | no consequential use of stale decision |
| External effect | committed EffectIntent, executor, reconciliation | success state | duplicate/altered/uncertain effect | intent != success |
| Review projection | normalized spec, GuardRegistry, BSP manifests | independent review | prior outcome leakage, semantic omission | TXT authoritative |
| GuardRegistry | canonical guard/case records | mechanism-proof review | missing/duplicate/conflict | one active record per ID |
| NCG-1 | all normalized artifacts | external review packet | contradiction, ambiguous order, unowned state | zero unresolved material contradictions |

## 2. Evaluation-order matrix

The following order is normative for authority-bearing semantic resolution and consequential action.

| Order | Stage | Inputs | Output / blocker |
|---:|---|---|---|
| 1 | T0/MTR/current authority-state verification | T0/MTR/BTW/LAS config/revocation high-water | valid current authority context or fail closed |
| 2 | Runtime/AIEP verification | workload/runtime/AIG identity | qualified authority evaluator or NONE |
| 3 | Read current semantic snapshot | semantic_state_sequence + CSM/AIM/ANY/ResolverPolicy/RIR heads | one coherent snapshot or mixed-state reject |
| 4 | Resolve AIM candidates | semantic_input_id/class/scope/effective sequence | candidate set |
| 5 | Compute AIM_Smax | full effective matching AIM set | AIM_Smax |
| 6 | AIM ANY permission check | AIM_Smax + current AIMScopePolicy | permission blocker or continue |
| 7 | AIM lifecycle/successor resolution | AIM_Smax descriptors | one active AIM descriptor or blocker |
| 8 | Resolve RIR tuple | ResolverPolicy + attested implementation/runtime + sequence | one eligible RIR record or blocker |
| 9 | Verify RCS freshness | RIR-bound conformance evidence | qualified resolver or blocker |
| 10 | Build semantic candidates | AIM source lineage + CSM entries + decision scope | semantic candidate set |
| 11 | Compute semantic Smax | full matching semantic set | Smax |
| 12 | Semantic ANY validation | Smax + current semantic ANY permission | blocker or continue |
| 13 | Revoked-branch dominance | Smax lifecycle partition | discharge requirements |
| 14 | Successor / lineage / scope-replacement traversal | mappings + SRTT-3 | resolved successor candidates or blocker |
| 15 | SREP comparison | canonical result digests | one result or conflict |
| 16 | Capture AuthorityReadSet | all consumed inputs/heads | sealed read-set digest |
| 17 | Build DPS | read set + semantic/runtime/revocation/effect context | decision_preseal_digest |
| 18 | Obtain time proof | nonce + qualified time sources | time proof or blocker |
| 19 | Build VerifiedStateSeal | DPS + time proof | seal |
| 20 | COMMIT_WITH_SEAL | current heads vs seal | effect intent or STATE_CHANGED |
| 21 | External-effect execution/reconciliation | committed intent | reconciled success / uncertain / failure |

No later stage may reinterpret an earlier blocker as eligible authority.

## 3. State / registry ownership matrix

| State / registry | Sole authority owner | Monotonic/rollback protection | Included in authority root/seal? | Mutation path |
|---|---|---|---|---|
| T0 generation | MTR/T0 successor protocol | MTR monotonic register | referenced through current trust state | T0 successor ceremony |
| BTW high-water | MTR + BTW consistency | MTR | trust verification context | BTW append + MTR update |
| Controller/lineage identity | constitutional identity registries | LAS/anchor + revocation | via governance snapshot/read set | governed registry event |
| Revocation head | LAS revocation stream | LAS + MTR where sensitive | yes | revocation/UNREVOKE event |
| GGS namespace/auth roots | GGS-3 | GGS hard state + MTR checkpoint | GGS cert/state root | GGS command |
| LAS StreamHeadMap | LAS-3 | hard state + consensus | yes | LAS command |
| LAS idempotency ledger | LAS-3 | hard state + consensus | yes | LAS command |
| CSM-5 head | LAS-3 semantic stream | LAS | yes | constitutional semantic event |
| AIM-4 head | LAS-3 semantic stream | LAS | yes | AIM successor event |
| Semantic ANY permission head | LAS-3 semantic stream | LAS | yes | ANY_SCOPE_PERMISSION_AMENDMENT |
| AIMScopePolicy head | LAS-3 semantic stream | LAS | yes | constitutional semantic amendment |
| ResolverPolicy head | LAS-3 semantic stream | LAS | yes | constitutional semantic amendment |
| RIR head | LAS-3 semantic stream | LAS | yes | resolver enrollment/lifecycle event |
| GuardRegistry head | LAS-3 semantic stream / prereg design registry before implementation | LAS when implemented | yes | governed guard-record event |
| NonceLedger head | LAS-3 | LAS | yes | nonce issue/consume/expire |
| Effect stream head | LAS-3 | LAS | yes | effect state-machine event |
| Review packet projection | deterministic BSP generator | source digests + manifest | review artifact, not runtime root | regeneration only |
| NCG normalized spec | deterministic/manual normalization with traceability | Git exact commit/blob | review input only | successor normalization commit |

No authority-bearing mutable state may have two independent owners.

## 4. Cross-rule precedence matrix

| Conflict shape | Winning rule | Result |
|---|---|---|
| High AIM specificity vs lower active descriptor + invalid high ANY permission | high-specificity blocker | AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED |
| High semantic specificity vs lower active rule + revoked high rule | revoked high blocker | SEMANTIC_SCOPE_REVOKED unless valid discharge |
| Valid successor vs unrelated active peer | discharge revoked first, then SREP compare | unique result or conflict |
| Policy says implementation valid but RIR lacks exact tuple | RIR authorization | RESOLVER_IMPLEMENTATION_UNBOUND |
| RIR ACTIVE label but sequence not effective | temporal predicate | ineligible |
| Conformance PASS but evidence stale | RCS freshness | unqualified |
| Scope replacement says broader but no expansion authority | SRTT | invalid |
| Old review packet says PASS but current state changed | current seal/state | no authority |
| Legacy guard table conflicts with GuardRegistry | GuardRegistry | legacy table ignored as authority |
| Liveness need conflicts with trust proof unavailable | fail-closed rule | blocked; no weaker fallback |

## 5. Matrix consistency checks

Internal NCG checks required:
- every stage output consumed only by later stages;
- no cycle in authority-dependency edges except explicitly stateful commit loops;
- no blocker can be converted to eligible state by a later stage without a governed successor/recovery event;
- every mutable authority state has exactly one owner;
- every owner has an explicit head/digest or external trust root;
- review-only artifacts cannot directly mutate runtime authority.
