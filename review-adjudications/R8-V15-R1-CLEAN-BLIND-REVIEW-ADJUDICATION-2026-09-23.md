# R8 v15-r1 Clean Blind Review — Adjudication

Status: **BOUNDED_PASS_ACCEPTED_WITH_EVIDENCE_CLOSURE_REQUIRED**
Authority effect: **NONE**

Frozen reviewed candidate:
- semantic candidate source commit: `c721b38cf8b00294797300b526596ce723a47ff8`
- clean review packaging head: `4ceedf7c151fae69e3d8dfd462d611e35e51e346`
- preserved independent review: `review-evidence/r8-v15-r1-clean-deepseek-independent-review-2026-09-23.md`

## Overall disposition

The independent reviewer returned `BOUNDED_PASS` and found:
- no critical findings;
- one high evidence-boundary limitation (H-1);
- two medium observations (M-1, M-2);
- no demonstrated semantic false-green path.

That external disposition is accepted as a bounded design assessment. It does **not** by itself authorize executable-schema freeze because H-1 concerns a load-bearing review-evidence proof that our own gate requires to be independently reproducible.

## Finding adjudication

### H-1 — omitted legacy guard-table source reparse not independently verifiable
**ACCEPTED — EVIDENCE-CLOSURE BLOCKER, NOT A SEMANTIC DESIGN DEFECT**

The reviewer correctly observed that the clean handoff contains the GuardOmissionManifest and current registries but not the canonical omitted source table ranges themselves. Therefore the reviewer could not independently reparse those 11 source tables.

Additional adjudication check:
- the exact canonical source line ranges were fetched using each manifest source commit/blob;
- the guard/case sets can be reparsed and matched;
- however the existing `section_sha256` values do not reproduce from the exact inclusive line-range UTF-8 text under the straightforward raw-LF/no-trailing-LF or raw-LF/with-trailing-LF interpretations;
- the manifest does not declare the digest-basis transformation for `section_sha256`.

Therefore H-1 is stronger than a transport omission alone: the old section digest field is not independently reproducible from its declared line-range evidence without an unspecified normalization rule.

Required narrow closure:
1. include all 11 exact canonical source excerpts in the review handoff;
2. declare one exact digest basis;
3. recompute fresh section digests from that basis;
4. reparse guard/case IDs from those excerpts and require exact set equality;
5. retain the old ambiguous digest only as historical/non-authoritative data, or omit it from the new evidence artifact;
6. obtain targeted independent verification of this evidence closure before executable-schema freeze.

### M-1 — duplicate unversioned review status line
**ACCEPTED — NON-SEMANTIC PACKAGING CLEANUP**

The canonical current-status block is deterministic and the extra `Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE` line is inside the embedded reviewer prompt, not a second structural BSP current-status block.

No authority ambiguity exists under BSP-5, but the duplicate line should be removed/renamed to prevent naive-parser confusion.

Required cleanup:
- change the reviewer-prompt metadata label from `Status:` to a non-status label such as `Review contract mode:`;
- preserve the one and only structural BSP current-status block.

### M-2 — reviewer did not perform exhaustive row-by-row SRTT-4 verification
**NOT A CANDIDATE DEFECT — REVIEW-METHOD LIMITATION**

The reviewer independently recomputed the rule-precedence distribution and sampled rows, but did not manually verify all 2304 rows.

The candidate already has an internal full-row recomputation against the dedicated SRTT-4 RuleRegistry. That internal result is not substituted for independent review authority, but the reviewer's inability to manually inspect all rows does not create a semantic defect.

No semantic remediation is required. A future executable-schema gate should automate full table recomputation from the frozen RuleRegistry and fail on any row mismatch.

## Accepted positive review results

The following reviewer conclusions are sustained:
- NORM-001..NORM-043 are present and traced;
- fixed SRTT-4 domain is explicit;
- 2304-tuple Cartesian size is correct;
- mapped-effect EXACT_MATCH semantics are preserved;
- multi-revoked composition is explicit;
- GuardRegistry G001-G156 is contiguous;
- CaseRegistry contains 467 cases with no missing guard-referenced case;
- BSP-5 structural current-status and marked semantic-test section behavior is coherent;
- dependency graph is acyclic under declared direct-edge semantics;
- no unresolved cross-mechanism false-green path was identified;
- transient qualified-dependency outage remains fail-closed.

## Gate state

- design review disposition: **BOUNDED_PASS**
- semantic redesign required: **NO**
- evidence/packet cleanup required: **YES**
- executable-schema freeze: **BLOCKED pending H-1 evidence closure**
- implementation: **BLOCKED**
- authority effect: **NONE**

The next action is a narrow review-evidence revision only. The frozen semantic candidate remains unchanged.
