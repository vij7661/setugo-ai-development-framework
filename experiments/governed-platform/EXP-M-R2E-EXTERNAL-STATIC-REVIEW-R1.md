# Independent Static Review — EXP-M Deterministic Implementation R2E

Static review only: I cannot fetch the Git objects, recompute hashes, or execute the suites from this handoff alone. With that limitation, the handoff is mostly internally coherent, but I would **not** treat it as a clean PASS without clarifying several anomalies.

## Internally consistent points

- Authority boundary is stated correctly: `EXP-M = NOT_QUALIFIED`, `Authority effect = NONE`, no live provider/API execution.
- S → E → P identity chain is present and self-consistent:
  - S is source commit/tree.
  - E is evidence commit/tree.
  - P is packet-content commit/tree.
  - E → P changes only `EXP-M-R2E-PACKET-CONTENT.md`.
  - The post-P handoff carries the P SHA, avoiding Git self-reference.
- Source vs evidence separation looks correct: S → E changed paths are evidence artifacts, while source files are frozen via `EXP-M-SOURCE-FREEZE.json`.
- Compound attack summary reports `CA-1..CA-10`, `survivors=0`, `all_rejected=true`.

## Findings requiring clarification

1. **CA-9 rejection reason is semantically suspicious.**
   - Attack: `test_ca9_caller_pass_with_failed_predicate`
   - Reported rejection reason: `disposition_promotable`
   - For a caller PASS with a failed predicate, the rejection reason should normally indicate the predicate failure or a non-promotable disposition. `disposition_promotable` reads inverted. This is the highest-priority item to inspect in the validator and test fixture.

2. **CA-10 rejection reason conflicts with the frozen R5 protocol.**
   - Attack: `test_ca10_missing_protocol_with_self_consistent_record`
   - Reported rejection reason: `r5_protocol_unavailable`
   - But the packet includes a frozen R5 protocol and the authority root references `r5_protocol_path` / `r5_protocol_sha256`.
   - Clarify whether `r5_protocol_unavailable` means “live execution is not authorized” or “the protocol is genuinely missing from the runtime.” If the latter, the packet’s inclusion of the protocol needs explanation.

3. **Evidence manifest omits itself.**
   - `EXP-M-R2E-EVIDENCE-MANIFEST.json` is listed in S → E changed paths but not in its own `artifacts` array.
   - This is not necessarily wrong, but it should be explicitly justified or separately attested.

4. **Several JSON result files and STDOUT files have identical hashes and sizes.**
   - `EXP-M-TEST-RESULTS.json` == `EXP-M-R2E-TEST-RUN-STDOUT.txt`
   - `EXP-M-DETERMINISTIC-RESULTS.json` == `EXP-M-R2E-PHASE-STDOUT.txt`
   - `EXP-M-MUTATION-RESULTS.json` == `EXP-M-R2E-MUTATION-STDOUT.txt`
   - This is plausible if the scripts emit the JSON document to stdout and it is saved as both `.json` and `.txt`. But it means the STDOUT evidence is not independent of the result artifact. Document this explicitly.

5. **Referenced authority files are not included in the evidence artifact hash list.**
   - Authority root references:
     - `EXP-M-R2E-TEST-EXPECTATIONS.json`
     - `EXP-M-R2E-TEST-EXPECTATIONS.sig`
     - `EXP-M-R5-QUALIFICATION-PROTOCOL.json`
     - retrieval, delivery, and qualification ledgers
   - Their SHA-256 values are given in the authority root, but their contents are not in the packet. A reviewer must fetch them at S and verify. The handoff should state that these are frozen at S and not part of E → P.

6. **Reproducibility is partial.**
   - Commands are listed, but there is no environment lockfile, dependency list, or exact checkout sequence.
   - For an independent reviewer, this limits full re-execution unless the repo already provides those controls.

7. **Prior failure preservation cannot be verified from the text alone.**
   - The table is plausible, but completeness against Git history and correct recomputation of pinned hashes requires running the index builder and checking the pinned commits.

## Recommended independent verification checklist

- Checkout S, E, and P; verify commit/tree SHAs.
- Verify E → P diff contains only `EXP-M-R2E-PACKET-CONTENT.md`.
- Recompute SHA-256 for every artifact in the evidence manifest and compare.
- Re-run every command in the manifest from a clean checkout of S; compare stdout hashes.
- Inspect `test_ca9_caller_pass_with_failed_predicate` and the validator path that emits `disposition_promotable`.
- Inspect `test_ca10_missing_protocol_with_self_consistent_record` and the R5 protocol availability logic.
- Verify all authority-root referenced files at S against their declared SHA-256 values.
- Re-run the prior-evidence index builder and confirm each pinned commit/hash.
- Confirm no live provider/API execution, no secrets, and no network-dependent behavior.

## Disposition

Static review disposition: **clarifications required before PASS**.  
Authority effect remains **NONE**.  
EXP-M remains **NOT_QUALIFIED**.
