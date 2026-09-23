# R8 v14 Normalized Independent Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR_REQUIRED**
Authority effect: **NONE**

Reviewed normalized candidate:
- source commit: `a020a0c72c109e52efc9341d7e06e3f75615f68f`
- preserved independent review artifact: `review-evidence/r8-v14-normalized-deepseek-independent-review-2026-09-23.md`
- preserved review commit: `ce2be2849ac132e9c8fd45b9eb03d1309b431356`

This adjudication does not mutate v14. It classifies the DeepSeek findings against the canonical v13/v14 source semantics and defines the narrow successor work required before a new blind review.

## Overall disposition

The external `CHANGES_REQUIRED` disposition is sustained because the normalized review surface contains real closure defects: the SRTT machine-readable domain is not self-describing, decisive-rule references are not independently traceable, the v4 guard-omission range is incompletely expanded, BSP-4 current-status classification is underspecified, and multi-revoked composition/cross-mechanism coverage should be made machine-explicit.

One review claim is rejected as a semantic false positive after checking the canonical inherited SRTT-2 rules: mapped-replacement semantics intentionally permit an EXACT_MATCH destination in addition to MAPPED_MATCH.

## Finding dispositions

### B-1 — SRTT-3 source_entry_state domain
**ACCEPTED — NARROWED**

Canonical v14 I010 already defines `source_entry_state: {REVOKED}`; SRTT replacement evaluation is revoked-source-only. The defect is that the generated artifact's machine-readable domain does not carry that fixed dimension explicitly. The successor must add a fixed-domain declaration and state totality as fixed-domain × variable Cartesian product. No ACTIVE/SUSPENDED/RETIRED expansion is required.

### B-2 — mapped replacement + EXACT_MATCH alleged bypass
**REJECTED AS FALSE POSITIVE; CLARIFICATION REMEDIATION ACCEPTED**

Canonical v13 I013 explicitly defines mapped replacement as:
- SAME + (EXACT_MATCH or MAPPED_MATCH) -> eligible;
- NARROWER + (EXACT_MATCH or MAPPED_MATCH) -> eligible;
- BROADER -> eligible only with constitutional scope-expansion authorization and an in-domain decision;
- DISJOINT -> invalid.

Therefore an `old_scope_effect=REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH` tuple with `destination_scope_match=EXACT_MATCH` is not incoherent under the inherited design. Row 1888 is not a self-grant merely for that combination when the broader-scope authorization predicates are valid.

However, the normalized v14 wording compressed this inherited rule enough to invite misinterpretation. The successor must restate the full exact/mapped/broader semantics and expose the rule bundle used to generate the table.

### B-3 — guard-omission manifest skips V4-025..V4-029
**ACCEPTED**

The canonical v4 guard catalog uses the range `V4-024..V4-030` for G008. The v14 omission manifest expanded that range incorrectly by including V4-024 and V4-030 while omitting V4-025 through V4-029. The successor must deterministically expand ranges and verify every referenced case against CaseRegistry.

### C-1 — BSP-4 current-candidate status identification
**ACCEPTED**

The current-candidate version is an input, but the machine grammar does not define an unambiguous binding of a particular status block to that candidate. The successor must use explicit machine markers or an equivalent deterministic section-binding rule and define semantic-test parser states exactly.

### C-2 — multiple revoked branches
**ACCEPTED — NARROWED**

Canonical v13 I017-I020 already define the intended semantics: every revoked Smax blocker must be uniquely discharged; zero path blocks; multiple non-equivalent paths conflict; only after all blockers are discharged are their results compared with genuine ACTIVE peers.

The successor does not need a new safety policy. It must make this composition machine-explicit and add multi-branch adversarial vectors, including partial discharge, same-digest discharge, and different-digest discharge.

### C-3 / D-2 — SRTT rule traceability
**ACCEPTED — STRENGTHENED**

The review packet omitted the source rules used to justify the table. More importantly, the v14 table's `decisive_rule_id` values such as `R8V14-I011.2` and `R8V14-I013` are not a clean one-to-one mapping to the actual v14 preregistration rule text. The successor must define a dedicated machine-readable SRTT rule registry and require every row to reference exactly one declared rule ID.

### D-1 — cross-mechanism coverage
**ACCEPTED AS CLOSURE HARDENING**

Add explicit vectors for:
- AIM permission blocker × RIR/RCS blocker ordering;
- guard semantic preservation × NCG closure;
- rotation barrier × external-effect state;
- multiple revoked Smax branches;
- semantic_state_sequence rollback/replay with superficially matching heads.

These additions are adversarial closure requirements; their absence does not by itself prove each path is exploitable.

### D-3 — BSP semantic-test context
**ACCEPTED**

Define exact parser states and transitions. A status token is a semantic-test literal only inside an explicitly recognized case/vector/guard record or a fenced block explicitly marked as semantic test data.

### D-4 — dependency graph completeness
**ACCEPTED FOR RECOMPUTATION, NOT FOR BLIND EDGE INSERTION**

The successor must define whether graph edges mean direct dependency or transitive closure and regenerate the graph from the dependency matrix. Suggested reviewer edges are not automatically authoritative. In particular, qualification/review dependencies must not be confused with runtime semantic-resolution dependencies.

### M — transient non-authority dependency liveness
**DISPOSITIONED — FAIL-CLOSED IS INTENDED**

Temporary unavailability of qualified time, conformance, or equivalent non-authority dependencies does not authorize a weaker fallback, stale evidence, cached success, or emergency root. Authority remains blocked until the same or stronger qualified dependency path is restored. This is intentional safety behavior, not a defect.

## Successor requirement

R8 v14 remains immutable and `CHANGES_REQUIRED`.

Executable-schema freeze remains **BLOCKED**.

The next design candidate must be a narrow v15 successor that:
1. makes the SRTT fixed domain machine-readable;
2. freezes a dedicated SRTT rule registry and regenerates the table from it;
3. preserves the inherited mapped-replacement EXACT_MATCH semantics rather than deleting valid rows;
4. repairs guard-range expansion;
5. makes BSP current-status classification deterministic;
6. makes multi-revoked composition machine-explicit;
7. adds the accepted adversarial vectors;
8. recomputes the dependency graph under declared edge semantics;
9. explicitly preserves fail-closed behavior for transient dependency outages.

No implementation or executable-schema freeze is authorized by this adjudication.
