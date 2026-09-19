**Overall disposition:** **`CHANGES_REQUIRED`**

The R2 repairs are real but incomplete. Every R2 finding except M-01..M-03's cores is only PARTIAL, and I found one new Critical and five new High defects. The R2 remediation's claim of "no new Critical/High" is not supported.

*Scope:* I read the inline packet: the standard, the experiment invariants and the frozen tests M-42..M-82, the mutation, adapter, pilot and acceptance sections, all of the test matrix, the relevant live-governance sections, and the R2 review and remediation. I skimmed M-01..M-41. I had no repository access, so I did not verify the commit, tree or blob hashes and treated the inline text as faithful.

## 1. R2 finding closure

| ID Status Remaining false-green path (details in §2)  |             |                                                                                                                                                                                                                                        |
| ----------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-01                                                  | **PARTIAL** | The ReviewRequest can no longer narrow the contract. The contract's own inputs (standards, experiment contract, selection rules, classification, relationship graph) are not bound to an authority the candidate cannot edit. → R3-C01 |
| H-01                                                  | **PARTIAL** | The rule and tests exist, but cleanliness is declared or documented rather than observed per attempt. Nothing defines how "pre-existing context is governed" is proven. → R3-H01                                                       |
| H-02                                                  | **PARTIAL** | Thresholds are fixed, but the protocol around them (independence, exclusions, re-roll, content coverage) is not falsifiable. → R3-H02                                                                                                  |
| H-03                                                  | **PARTIAL** | Fail-closed on paper. The "drift-bound" alternative, the reliance on provider documentation, and the absence of any per-attempt state read leave a gap. → R3-H01                                                                       |
| H-04                                                  | **PARTIAL** | Dense probing exists only at qualification, on synthetic artifacts. Production attempts carry no mandatory witnesses, and K02 and the pilot section still endorse the sparse method. → R3-H03                                          |
| H-05                                                  | **PARTIAL** | Tests were added, but they contradict each other, the exit criteria omit most phases, and none of the new tests attack the validator's own logic. → R3-H05                                                                             |
| M-01                                                  | **PARTIAL** | Hedges remain. → R3-M03                                                                                                                                                                                                                |
| M-02                                                  | **PARTIAL** | The source of "evidence relationships" is undefined, and interaction families are too coarse. → R3-C01, R3-M02                                                                                                                         |
| M-03                                                  | **PARTIAL** | The revalidation step sits before the final gate, and re-admission after the fact is permitted. → R3-M01                                                                                                                               |

## 2. New and residual findings

### Critical

**R3-C01: Requiredness contracts have no bound input authority** (keeps C-01 and M-02 open)

- **Affected:** the standard's "Required-evidence authority", "Delivery-governor trust root" and "Review decomposition" sections; M-I16 versus M-I36; tests M-68, M-69, M-80, N01–N03, N23.
- **False-green path:** 
  - The governor's code is pinned, but its inputs are not.
  - `standards/` and `experiments/governed-platform/` are governance paths in the same repo as the change under review.
  - A candidate that edits those files, or supplies the relationship or classification metadata, gets a contract derived from its own HEAD.
  - The four-way closure equality then passes against the narrowed contract.
  - N01–N03 mutate only the ReviewRequest or manifest, never the contract inputs.
- **Additional defects:** 
  - M-I16 still lists the ReviewRequest as a requiredness input.
  - `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` appears in the standard only. It is absent from the runtime taxonomy and from every test and adapter.
  - A vacuous derivation (unknown transition class → zero refs) is "deterministic", not "ambiguous", so it passes.
- **Fix:** 
  1. Resolve all derivation inputs from a pre-candidate authority snapshot, hash-pinned in the contract. Registries and the pin pointer sit outside the candidate write set.
  2. When the inputs themselves change, use the strictest of base and head per element, and make the input change a required evidence ref.
  3. Remove the ReviewRequest from M-I16. Take relationships and classification only from the governed registry.
  4. Add per-transition-class minimum baselines and a non-vacuity rule. Unknown class, empty set, or missing rule → `UNRESOLVED`. Add the code to the runtime taxonomy.
  5. Add tests for each input-poisoning path, base/head divergence, unknown class, and empty contract.

### High

**R3-H01: Provider context state is declared, not observed** (keeps H-01 and H-03 open)

- **Affected:** "Data classification and egress"; "Clean material-review context"; preflight step 7; M-70..M-73; N04–N10, N30.
- **False-green path:** 
  - Clause "cannot be enumerated, disabled, or drift-bound" lets un-enumerable context pass if it is "drift-bound". This is weaker than M-I40's "inventory or disable".
  - The fixed-policy carve-out rests on the provider "documenting" that no other context is injected. That is provider self-attestation, with no pinned document version and no behavioral check.
  - The exception "unless the platform can prove the pre-existing context is governed" has no proof mechanism. A readback that omits hidden turns looks the same as a clean one.
  - Preflight step 7 checks only profile expiry. Nothing reads current custom-instruction, memory, connector, or default-prompt state before dispatch or at admission. Drift is caught only at 7-day expiry.
  - The tests use adapters that self-report dirtiness, so undetected dirt is never falsified.
- **Fix:** 
  1. Require per-attempt `ProviderContextStateEvidence`. This means a platform-created session, a provider readback hash of the full transcript, tool and config state, and a config-state hash. Compare it with the profile at preflight, before each dispatch, and at admission.
  2. Any channel that is neither disable-able nor readable makes the mode `NOT_QUALIFIED`. The only exception is a dedicated platform-owned account whose configuration write access is change-controlled outside candidate and user.
  3. Delete the "drift-bound" alternative. Restrict the reuse exception to sessions created by the trusted adapter in the same attempt lineage, with wire records for every message.
  4. Add a behavioral sentinel qualification: plant a sentinel in each mutable channel of a test account and show it is visible when enabled and absent when disabled. Record provider documentation with a version hash as necessary but not sufficient.
  5. Add tests with a lying readback, hidden dirty state, and config change between qualification and dispatch or between dispatch and admission.

**R3-H02: The statistical protocol is not falsifiable** (keeps H-02 open)

- **Affected:** "Provider capability qualification policy"; M-I38; Phase F; M-74..M-76; N11–N17.
- **False-green path:** 
  - 59 back-to-back synthetic trials in one burst qualify the point for 7 days. "Independent" is defined only as fresh session plus fresh witness, so time, route and load correlation are ignored.
  - There are no rules on excluded trials, retries or optional stopping. There is no separation of exploration from confirmation.
  - Failure history is not persisted, so a point can be re-run until it passes.
  - "Hard failure" is undefined.
  - Trials use synthetic content, not the production envelope: real review prompt, output and reasoning limits, tools, structured output, or the worst-case token-dense content class.
  - The claimed point itself need not be tested. The 80% rule assumes monotonic behavior.
- **Fix:** 
  1. Fix the exact Clopper–Pearson criterion and remove "approximately".
  2. Require trials spread over preregistered time blocks and days with interleaved order.
  3. Count every attempted trial, including infrastructure errors. Forbid discarding and optional stopping. Keep confirmation trials disjoint from exploration trials.
  4. Persist observed failure boundaries across requalification within a drift epoch.
  5. Define hard failure and operating point. The claimed point must be tested itself or bracketed by two passing points, and monotonicity must be stated or dropped.
  6. Run qualification under the production request envelope and cover the token-worst-case content class.
  7. Let health checks invalidate a profile but never renew it.

**R3-H03: Dense witness coverage is qualification-only** (keeps H-04 open)

- **Affected:** "Delivery witness probes"; M-I39; the "Live provider pilots" section; K02; M-46; N18–N21.
- **False-green path:** 
  - Production attempts carry no per-attempt witnesses ("may").
  - A provider that loses content selectively, compacts, or behaves differently on real content or token density passes synthetic dense probing. It can then silently drop a decisive ≤2048-byte region in production.
  - Framing witnesses do not bind content. No adapter models canary-preserving content loss; `SparseCanaryGapAdapter` removes canaries.
  - "Randomized content-location challenges" is not defined. If each trial challenges only a subset, per-position and all-segments claims get fewer than 59 tests.
  - Opaque attachments are probed on synthetic text-layer pages. Scans, tables, images and embedded objects pass through an ungoverned provider-side conversion.
  - K02 says head/middle/tail success passes "for tested bound", and the pilot section still lists beginning/middle/end. Both contradict N18 and the standard.
- **Fix:** 
  1. For any mode without deterministic range or retrieval proof, require per-attempt witnesses. Options: (a) a governed lossless slicing representation with slices ≤ the granularity and platform-framing witnesses per slice plus an end sentinel, verified in the same session as the adjudication; or (b) platform-chosen random-offset content extracts per slice, chosen after freeze, which also catch selective loss.
  2. State the failure model for 2048 explicitly. Cover contiguous loss only, in min(2048 bytes, token-equivalent), and put selective or sub-granularity loss in the nonclaims.
  3. Challenge every segment in every trial.
  4. Qualify opaque attachments per media-type and content-modality class, and block other modalities or convert them under a governed transformation.
  5. Fix K02, M-46 and the pilot section. Add a canary-preserving content-drop adapter.

**R3-H04: Retrieval- or file-dependent completeness is profile-discretionary** (drives the FAIL on `SESSION_FILE_RETRIEVAL_BINDING`)

- **Affected:** "Server-side file references"; M-I27; J14; K09; N22, N29.
- **False-green path:** 
  - The profile "declares whether logs are required". When the model decides what to read, attach-time file-ID binding and synthetic qualification cannot show that every range was read this attempt.
  - A profile declaring logs "not required" yields `TESTED_SUPPORTED` from citation text, the very thing M-I27 says is insufficient.
  - N29 fires only if logs are already "required". J14 treats "final request binds all file IDs" as eligible.
- **Fix:** For any mode where the model selects what to read, per-attempt deterministic access logs are unconditionally required. They must show hash-matched coverage of every required range, member or page before admission. Otherwise the mode is diagnostic-only. Platform-forced inline inclusion is the alternative. Change J14 and add tests for missing, partial and wrong-version logs.

**R3-H05: The test matrix does not falsify the repaired invariants** (keeps H-05 open)

- **Affected:** Phases G and K; Phases N, J–M and the "Exit criteria" section; the experiment's mutation list.
- **False-green path:** 
  - K02 contradicts N18.
  - Phase G still lists 24 mutations. The new families appear only in the experiment's separate list.
  - Exit criteria name phases A–E only, so phases F–N are not gated.
  - All mutations perturb data fields. None mutates the governor's logic, such as deleting an admissibility conjunct, weakening closure equality to ⊆, dropping the dirty-session check, accepting 58 trials, or skipping the margin.
  - The fake adapters self-report, so tests exercise helpers, not adversarial oracles.
  - M-10/M-11 and C01/C02 exercise wire-visible omission, not remote silent loss.
  - No tests exist for R3-C01/H01–H04 paths.
  - Test IDs collide: matrix M01–M12 versus M-01.., and the R2 IDs M-01..M-03 versus frozen tests M-01..M-03.
  - D09 expects `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, which is defined nowhere.
- **Fix:** 
  1. Add validator-logic mutation testing where every conjunct deletion or weakening must be killed by at least one test.
  2. Merge the mutation lists and make exit criteria cover all phases.
  3. Add adversarial-oracle adapters: lying readback, canary-preserving drop, correlated or time-burst failures, and failed-trial replay.
  4. Add tests for the contract-input, state-evidence, statistical-protocol, and log-mandatory paths.
  5. Namespace the IDs and define D09's code.

### Medium / Low

- **R3-M01 (M-03 residual): revalidation is neither atomic nor final.** 
  - Live-procedure step 19 (revalidate) precedes steps 20–23, which are semantic validation, gate and checkpoint.
  - M-81 says "until newly governed validation", M-82 and N26 say "according to current policy", and the standard allows "a newly governed decision". A requalification after the fact could re-admit the old response.
  - **Fix:** 
    - Make revalidation the last step, done as compare-and-set atomically with the checkpoint.
    - Require validity over the whole interval from first dispatch to admission, with monotonic state versions.
    - Any expiry, revocation or drift inside the interval voids the attempt, and only a new attempt can proceed.
    - Add tests for requalification after expiry and for expiry between steps 20 and 22.
- **R3-M02: interaction granularity.** 
  - Families are dimension-level, and the aggregator may see only subreview outputs.
  - **Fix:** 
    - Define each interaction as a set of evidence refs that must sit raw in one qualified context.
    - The aggregator reviews raw evidence per family, or the global disposition is blocked.
- **R3-M03 (M-01 residual): permissive hedges remain.** 
  - Examples: "identity where available" (the default drift policy decides whether identity is required), "context-middle omission detection if applicable", "estimated tokens if available", "session/file binding where used", "access logs where available", M-I27 "where possible".
  - **Fix:** Default drift policy requires provider-reported deployment identity for material review. Make each item mandatory or an explicit `NOT_QUALIFIED`.
- **R3-M04: the admissibility conjunct list is incomplete.** 
  - It omits clean context, provider-semantic-context qualification, statistical and accessibility qualification, and interaction closure.
  - **Fix:** Enumerate every predicate in `VerdictAdmissibilityResult`.
- **R3-M05: cause adjudication.** 
  - The numbered list reads as first-match, so step 2 (`SCIENTIFIC_EVIDENCE_MISSING`) pre-empts step 8 (`MIXED`).
  - `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` and D09's code are missing from the runtime taxonomy.
  - **Fix:** Evaluate the causes as independent predicates, return `MIXED` if more than one holds, and reconcile the standard's and live governance's taxonomies.
- **R3-L01:** Live procedure materializes (step 13) before deriving the contract (step 14), and lacks the standard's pre-dispatch revalidation.
- **R3-L02:** Hash the request bytes at the transport boundary after SDK serialization, so SDK-injected headers and fields are captured.
- **R3-L03:** Define "applicable" for the EXP-L dependency via the governor. Require a machine-checkable EXP-L qualification record with hash and expiry, checked at admission.

## 3. Gate verdicts

| Gate Verdict Gate Verdict            |                                                               |                                    |                                                |
| ------------------------------------ | ------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------- |
| REQUIRED\_EVIDENCE\_AUTHORITY        | **FAIL** (C01)                                                | INSUFFICIENT\_EVIDENCE\_TAXONOMY   | PASS (M05)                                     |
| DELIVERY\_GOVERNOR\_TRUST\_ROOT      | **FAIL** (C01: the boundary covers code, not decision inputs) | MULTI\_REVIEWER\_EQUIVALENCE       | PASS                                           |
| CLEAN\_SESSION\_CONTEXT              | **FAIL** (H01)                                                | DECOMPOSITION\_AGGREGATION         | **FAIL** (C01 relationship inputs; M02)        |
| PROVIDER\_SEMANTIC\_CONTEXT\_BINDING | **FAIL** (H01)                                                | PROMPT\_ISOLATION\_DEPENDENCY      | PASS (L03)                                     |
| WIRE\_BINDING                        | PASS (L02)                                                    | TOCTOU\_RETRY\_INTEGRITY           | PASS for manifest→wire (M01 open at admission) |
| CHUNK\_CONTEXT\_MODEL                | PASS                                                          | REVIEWER\_TOOL\_EVIDENCE\_BOUNDARY | PASS                                           |
| REMOTE\_ACCESSIBILITY\_MODEL         | **FAIL** (H03, H04)                                           | TEST\_MATRIX\_SUFFICIENCY          | **FAIL** (H05)                                 |
| PROVIDER\_CAPABILITY\_QUALIFICATION  | **FAIL** (H02)                                                | REPRESENTATION\_GOVERNANCE         | PASS (opaque modality classes under H03)       |
| MATERIALIZATION\_SAFETY              | PASS                                                          | EGRESS\_BOUNDARY                   | PASS                                           |
| SESSION\_FILE\_RETRIEVAL\_BINDING    | **FAIL** (H04)                                                |                                    |                                                |

## 4. Statistical policy adjudication

**Verdict: needs correction before preregistration freeze.**

- **The arithmetic is right.** 0.05^(1/59) ≈ 0.9505, and 58 gives ≈ 0.9497. So 59 is the exact minimum and "approximately" should go.
- **It claims less than it sounds like.** 59/59 supports only "per-trial success ≥ 0.95 at 95% confidence". That is a residual silent-failure rate of up to about 5% per attempt.
- **Power is weak.** A provider with a true 3% failure rate passes 59/59 about 17% of the time, and one at 2% passes about 30%. Since per-attempt witnesses are optional, those failures reach production as "complete".
- **Recommendation.** Preregister a risk budget per transition class. A 0.99 bound needs 299 trials. Or make per-attempt content-bound witnesses mandatory (R3-H03) and treat qualification as a prior. Record the residual in `VerdictAdmissibilityResult`. Do not call the outcome boolean "complete".
- **The 80% margin is an acceptable conservative heuristic,** but it needs the "claimed point is itself tested" rule.
- **The 7-day expiry is arbitrary and detects nothing between requalifications.** Add drift signals: identity headers, and health checks that can invalidate a profile but never renew it.

## 5. Dense-witness adjudication

- **≤2048-byte segments.** This is defensible as a qualification granularity for contiguous truncation or eviction, and not for selective or sub-granularity loss. A decisive line is tens of bytes, and 2048 is not tied to tokens. It does not by itself close H-04. It is honest only if the failure model is stated and the rest is a nonclaim.
- **Per-segment fresh framing.** It is sound for what it tests, but framing does not bind content.
- **Randomized locations.** They are only sound if every segment is challenged in every trial. Otherwise the 59-trial statistic is diluted.
- **Opaque page, range or member probes.** These are the right direction, but they need modality classes and must be page-count-bounded.
- **The design does not overclaim attention.** The fix that meets H-04 without doing so is per-attempt content-bound or slice-bound witnesses (R3-H03).

## 6. Final determination

- **Critical defect remains:** yes, R3-C01.
- **High defects remain:** yes, R3-H01 through R3-H05.
- **Ready for implementation or deterministic falsification:** no, not as reviewed. Under the frozen-evidence discipline, exposing the current text would burn first exposure and force a new boundary. Make a documentation-only revision first, then do a narrow R4 re-review of the items listed here.
- **Live provider pilots:** no.
- **Remaining prerequisites:** 
  1. R3-C01 fix with tests.
  2. Per-attempt provider state evidence and the sentinel qualification (R3-H01).
  3. A falsifiable statistical protocol, or a risk-budget policy (R3-H02).
  4. Per-attempt content-bound witnesses and an explicit failure model, with K02, M-46 and the pilot text corrected (R3-H03).
  5. Mandatory retrieval logs (R3-H04).
  6. Mutation-tested validator logic, merged mutation lists, exit criteria covering all phases, and the new adversarial adapters (R3-H05).
  7. Closure of R3-M01..M05 and R3-L01..L03.
  8. Deterministic phases green before any live pilot.
- **EXP-M remains NOT QUALIFIED.**
- **This review grants no platform-review or promotion authority.**