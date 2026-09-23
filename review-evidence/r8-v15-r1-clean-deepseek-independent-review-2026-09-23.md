A. Overall disposition: **BOUNDED_PASS**

The supplied R8 v15-r1 clean blind review packet, machine-readable companions, and SRTT-4 total table are internally consistent at the level required for executable-schema freeze, with one evidence caveat: the omitted legacy guard-table source ranges are not independently reparseable from the handoff surface, so the GuardOmissionManifest’s source-reparse equality is manifest-attested rather than directly recomputed here. No critical semantic contradiction or undefined decisive rule was found.

B. Critical findings

None.

C. High findings

1. **H-1 — Omitted legacy guard-table source reparse is not independently verifiable from the supplied handoff.**  
   The GuardOmissionManifest claims exact source/manifest case-set equality for 11 omitted tables, including inclusive range expansion such as `V4-024..V4-030`. All referenced guard IDs and case IDs are present in `R8-V15-GUARD-REGISTRY-1.json` and `R8-V15-CASE-REGISTRY-1.json`, and the manifest is internally consistent. However, the canonical omitted source tables are not included in the handoff, so the exact `section_sha256` and source-parsed set equality cannot be independently recomputed from the supplied materials. This is an evidence-boundary limitation, not a demonstrated semantic defect.

D. Medium findings

1. **M-1 — Duplicate unversioned status line outside the BSP-5 current-status block.**  
   The packet contains the required marked `BSP:CURRENT_STATUS_BEGIN version=15` block, but also contains an additional unversioned `Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE` line later in the packet. BSP-5’s explicit block binding prevents this from becoming a structural current-status block, and the residual expectation of one current-status block is satisfied. Still, a naive non-grammar parser could misclassify it. Recommend removing or explicitly marking it as non-status prose.

2. **M-2 — SRTT-4 row-by-row exhaustive verification was not performed manually.**  
   The aggregate distribution and sampled rows are consistent with the RuleRegistry. The full 2304-row table is internally consistent by distribution and precedence recomputation, but a complete row-by-row independent semantic recomputation was not feasible in this review pass. The aggregate recomputation strongly supports correctness.

E. Normalized-spec completeness / no-regression assessment

The normalized effective specification contains `NORM-001` through `NORM-043`. The traceability manifest reports `rule_count: 43`, `missing_rules: []`, and `untraced_rules: []`. No contradiction was found between the normalized prose and the machine companions. The closure note preserves the inherited mapped-effect rule that `REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH` may terminate at `EXACT_MATCH`. No silent weakening or missing inherited rule was identified in the supplied surface.

F. SRTT-4 assessment

The SRTT-4 fixed domain is explicitly `source_entry_state = REVOKED`. The variable Cartesian domain is exactly 2304 tuples. The RuleRegistry declares `SRTT15-R00` outside the table and `SRTT15-R01` through `SRTT15-R11` for the table.

Independent precedence recomputation matches the declared distribution:

- R01: `mapping_effective == false` → 1152 rows → `SEMANTIC_SCOPE_REVOKED`
- R02: `lineage_mapping_valid == false` → 576 rows → `SEMANTIC_SCOPE_REVOKED`
- R03: `any_permission_valid == false` → 288 rows → `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`
- R04: `old_scope_match == NO_MATCH` → 144 rows → `MAPPING_NOT_APPLICABLE`
- R05: `old_scope_effect == BLOCK_OLD_SCOPE` → 48 rows → `SEMANTIC_SCOPE_REVOKED`
- R06: `destination_scope_match == NO_MATCH` → 32 rows → `SEMANTIC_SCOPE_REVOKED`
- R07: exact effect, destination `EXACT_MATCH`, relation `SAME` → 4 rows → `REPLACEMENT_ELIGIBLE`
- R08: exact effect remaining → 28 rows → `SEMANTIC_SCOPE_REPLACEMENT_INVALID`
- R09: mapped effect, destination `EXACT_MATCH`/`MAPPED_MATCH`, relation `SAME`/`NARROWER` → 16 rows → `REPLACEMENT_ELIGIBLE`
- R10: mapped effect, destination `EXACT_MATCH`/`MAPPED_MATCH`, relation `BROADER`, both expansion flags true → 2 rows → `REPLACEMENT_ELIGIBLE`
- R11: mapped effect remaining → 14 rows → `SEMANTIC_SCOPE_REPLACEMENT_INVALID`

Aggregate results match the declared distribution: revoked 1808, permission re-evaluation 288, mapping not applicable 144, replacement eligible 22, replacement invalid 42. Every sampled row references exactly one declared decisive rule. No undefined or conflicting decisive-rule IDs were found.

G. Multi-revoked composition assessment

`NORM-024` defines complete blocker-set construction, per-blocker independent discharge, no partial discharge into authority selection, and final SREP comparison only after every blocker is uniquely discharged. Cross-mechanism cases `X15-046` through `X15-049` exercise same-digest convergence, partial discharge, distinct terminal results, and non-equivalent successor paths. The evaluation-order matrix places semantic ANY validation before revoked-branch dominance, which resolves the interaction between invalid ANY and multi-revoked composition consistently with `X14-024`. No unresolved false-green path was identified in the supplied corpus.

H. Guard / Case / omission proof assessment

`R8-V15-GUARD-REGISTRY-1.json` contains `G001`–`G156` contiguously. `R8-V15-CASE-REGISTRY-1.json` contains 467 cases with no missing guard-referenced cases and no duplicate conflicts. The GuardOmissionManifest reports 11 omitted tables, all with guard IDs and case IDs present in the current registries. Inclusive range expansion is handled explicitly for `G008` (`V4-024..V4-030` → seven explicit IDs). The manifest is internally consistent and cross-checks against the registries.

The only limitation is H-1: the canonical omitted source tables are not in the handoff, so the manifest’s `source_reparse_verification` cannot be independently recomputed here. Within the supplied review surface, no falsification was found.

I. BSP-5 / blindness assessment

The packet contains exactly one explicit version-15 current-status block:

`<!-- BSP:CURRENT_STATUS_BEGIN version=15 -->` … `<!-- BSP:CURRENT_STATUS_END -->`

The cross-mechanism adversarial corpus is enclosed in exactly one marked semantic-test section with stable ID `cross-mechanism-adversarial-corpus`. No nested, mismatched, or unterminated BSP-5 markers were found. Status literals inside the marked semantic-test section are retained as attack-vector data, not interpreted as prior disposition. The residual expectation of zero `PRIOR_STATUS`, zero `PRIOR_REVIEW_METADATA`, one `CURRENT_STATUS_BLOCK`, and zero malformed semantic-test sections is satisfied. The duplicate unversioned status line noted in M-1 does not violate the BSP-5 structural contract but should be cleaned up.

J. Dependency / evaluation-order assessment

`R8-V15-NCG-1-STRUCTURED-CLOSURE.json` declares 18 dependency nodes and 29 direct authority-relevant edges. The graph is acyclic and has a declared topological order. The edges are sourced from the matrix, not hand-added. Reviewer-suggested edges are explicitly dispositioned: `Revocation -> RIR2` not added without direct consumption; `CSM5 -> RCS2` not duplicated as transitive; `Review_Guard_NCG -> CSRULE_SRTT_SREP` rejected as a runtime edge.

The evaluation-order matrix defines 21 stages, from T0/MTR/current authority-state verification through external-effect reconciliation. No stage consumes authority state before qualification, and later stages do not reinterpret earlier blockers as eligible authority. No hidden direct dependency or cycle was identified.

K. Cross-mechanism coverage assessment

The supplied corpus covers:

- AIM × ANY × specificity (`X14-001`–`X14-004`, `X15-043`)
- AIM × successor × source lineage (`X14-005`–`X14-007`)
- RIR × sequence × conformance (`X14-008`–`X14-013`)
- Semantic Smax × ANY × revoked × peer ACTIVE (`X14-014`–`X14-018`, `X15-046`–`X15-049`)
- Scope replacement × ANY × expansion (`X14-019`–`X14-024`)
- Semantic state × seal × rotation (`X14-025`–`X14-029`, `X15-045`, `X15-050`)
- Guard registry × projection (`X14-030`–`X14-032`, `X15-044`)
- BSP blindness × semantic literals (`X14-033`–`X14-036`, `X15-051`)
- Effect / revocation / semantic state (`X14-037`–`X14-039`)
- Recovery / liveness interactions (`X14-040`–`X14-042`, `X15-052`, `X15-053`)

All cases have deterministic expected dispositions. No unresolved contradiction was found between the normalized spec and the cross-mechanism corpus.

L. Over-governance / liveness assessment

The design remains fail-closed during temporary qualified-dependency outages. Cached PASS, stale time/conformance/revocation evidence, local clock, operator override, or weaker emergency roots cannot substitute for authority. Retry is allowed only after the same qualified dependency or a constitutionally authorized equal-or-stronger successor is restored, followed by full current-state re-evaluation. No liveness workaround weakens authority semantics.

M. Minimal required changes before executable-schema freeze

No blocking changes were identified. Recommended non-blocking cleanups:

1. Remove or explicitly mark the duplicate unversioned status line discussed in M-1.
2. If NCG-1 requires direct source-reparse evidence rather than manifest-attested equality, include the canonical omitted legacy guard-table source ranges or a verifiable source-reparse artifact in the review handoff.

Neither item was shown to be a semantic defect.

N. Final bounded statement

The normalized R8 v15-r1 design is sufficiently closed at design level to proceed to executable-schema freeze under the supplied clean blind review handoff. The SRTT-4 table, RuleRegistry, BSP-5 projection, dependency graph, guard/case registries, and cross-mechanism corpus are internally consistent and support the declared semantics. The only material limitation is that omitted legacy guard-table source reparse equality is manifest-attested and not independently recomputable from the supplied materials. No critical contradiction, undefined decisive rule, or unresolved false-green path was found. This review grants no implementation, release, deployment, production, qualification, adjudication, or terminal authority.