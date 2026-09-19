**Overall disposition:** **`CHANGES_REQUIRED`**

I reviewed the R4 packet as inline source only. I did not have repository access, so I did not independently verify the commit/tree/blob hashes and treated the inline text as faithful. The R3 repairs are substantial and many findings are design-closed, but several load-bearing gaps remain, including one High provider-context residual and one High test/mutation-sufficiency gap.

---

## A. R3 finding closure

| R3 ID | Status | Exact current-source evidence | Remaining false-green path | Narrow fix if not CLOSED |
|---|---|---|---|---|
| R3-C01 | **CLOSED** | `GovernanceAuthoritySnapshot`; base/head conservative union/stricter merge; same-ID + hash semantics; unknown/empty/vacuous contract fails `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; registries/pointer outside candidate write set; tests M-83..M-85, TM-P01..TM-P03, TM-N01..TM-N03. | None material at design level, provided the external authority snapshot/pointer is actually outside candidate write authority. The undefined “platform-defined partial order” is a residual implementation risk, not a direct narrowing path because incomparable must fail closed. | Define per-element partial-order/comparison rules for “stricter” representation, semantics, statistical, risk, and review constraints. |
| R3-H01 | **PARTIAL** | `ProviderContextStateEvidence`; fresh stateless/trusted-adapter session; transcript/prompt/tool/memory/connector/file/deployment/config binding; checks at preflight, pre-dispatch, admission; `AdmissionFenceRecord`; sentinel tests; lying-readback and hidden-dirty-state adapters. | Provider-internal mutable semantic state that is not exposed by the provider API and not covered by behavioral sentinels can still influence review output while the platform records a clean context. The design says “unknown mutable semantic context is never tolerated,” but it cannot detect unknown hidden mutable state. | Record an explicit nonclaim/residual for hidden provider-internal mutable state not exposed by the provider API; require material review only on a dedicated platform-owned account/project whose mutable semantic features are disabled by provider policy and behaviorally requalified; or require a provider-exposed complete mutable-state inventory and fence. Add an adversarial adapter that simulates hidden unexposed mutable state. |
| R3-H02 | **CLOSED** | `p_min=0.99`; one-sided 95% exact Clopper–Pearson; 299/299 zero-failure minimum; all attempts counted; no rerolls/exclusions/optional stopping; exploration ≠ confirmation; ≥3 UTC days, ≥4 blocks/day; interleaved; exact operating point tested; production-equivalent envelope; append-only failures; health checks invalidate only; `STATISTICAL_INDEPENDENCE_UNPROVEN` when correlation cannot be evidenced. Tests M-74..M-76, M-90..M-93, TM-N11..TM-N17, TM-P08..TM-P11, TM-Q11. | Independence remains conditional, but the design explicitly bounds it and makes per-attempt accessibility proof mandatory when deterministic proof is unavailable. | Minor: add explicit test that a health check cannot renew an expired profile. |
| R3-H03 | **CLOSED** | Per-attempt content-bound witnesses mandatory when deterministic range/retrieval proof unavailable; slices ≤ min(2048 UTF-8 bytes, 512 provider tokens); every slice challenged every confirmation trial; production attempt same session; framing canaries supplemental; selective/sub-slice loss nonclaim; `ProviderAccessibilityRiskPolicy`; highest authority class deterministic proof; opaque modalities separate. Tests M-46, M-94, M-95, TM-N18..TM-N21, TM-P12..TM-P13. | None material at design level. | None required for closure. |
| R3-H04 | **CLOSED** | Model-selected retrieval requires unconditional deterministic per-attempt access logs: source/version, range/page/member, returned-content hash/length, time, tool/result identity, final-context binding. “File opened,” file ID, citation insufficient. Tests M-96..M-98, M-108, M-109, TM-N22, TM-N29, TM-Q12, TM-Q13. | None material at design level. | None required for closure. |
| R3-H05 | **PARTIAL** | Matrix IDs namespaced `TM-`; Phase G unified mutation catalog; phases A–Q required; many validator-logic mutations; adversarial adapters added. | The validator-logic mutation list does not delete/weaken every `VerdictAdmissibilityResult` conjunct one at a time. Missing targeted logic mutations include egress authorization, wire binding, session/file/retrieval coverage, complete materialization, governed representation/transformation, semantic review coverage, reviewer provenance, and promotable disposition. | Add one targeted `TM-O` logic mutation for each remaining admissibility conjunct, with an independently killed expected result. |
| R3-M01 | **CLOSED** | Atomic final compare-and-set admission; all state versions/hashes re-read at admission; any invalidation from first dispatch through admission permanently voids attempt; later requalification cannot revive. Tests M-81, M-82, M-98, TM-N25..TM-N27, TM-P16..TM-P17, TM-O21..TM-O22. | None material at design level. | None required for closure. |
| R3-M02 | **CLOSED** | `RequiredInteractionContract` derived from authority snapshot; each interaction is explicit raw evidence refs/representations that must coexist in one qualified context; aggregator must inspect raw set, not summaries. Tests M-80, TM-N23..TM-N24, TM-O17..TM-O18. | None material at design level. | None required for closure. |
| R3-M03 | **CLOSED** | Load-bearing provider deployment/retrieval/context facts mandatory when needed; missing required identity/logs/context makes mode not qualified rather than silently optional. | None material at design level. | None required for closure. |
| R3-M04 | **CLOSED** | `VerdictAdmissibilityResult` enumerates authority snapshot, evidence contract, interaction contract, materialization, transformation, egress, statistical capability, accessibility-risk policy, provider context, admission fence, wire binding, per-attempt accessibility, retrieval/session/file coverage, prompt isolation, semantic coverage, provenance, disposition. | None material at design level. | None required for closure. |
| R3-M05 | **PARTIAL** | Standard evaluates causes independently; multiple true causes → `MIXED_INSUFFICIENCY`; unresolved → `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`; added `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION` in standard. | The live governance failure taxonomy still omits critical codes: `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`, `GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH`, `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, `PROVIDER_CONTEXT_STATE_UNPROVEN`, `PROVIDER_CONTEXT_STATE_DRIFT`, `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`, `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`, `STATISTICAL_INDEPENDENCE_UNPROVEN`, `VERDICT_ADMISSION_STATE_CHANGED`, `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`, `MIXED_INSUFFICIENCY`. | Add all missing codes to `LIVE-CONVERSATION-GOVERNANCE.md` failure taxonomy and reconcile with the standard and test matrix. |
| R3-L01 | **CLOSED** | Live procedure now resolves authority snapshot/contracts before materialization; pre-dispatch revalidation explicit. | None material at design level. | None required for closure. |
| R3-L02 | **CLOSED** | `WireDeliveryRecord` includes pre-SDK platform request hash and post-SDK transport-bound semantic envelope hash; if SDK hides load-bearing semantic field, adapter/mode cannot claim exact wire binding. | None material at design level. | None required for closure. |
| R3-L03 | **CLOSED** | Governor deterministically selects machine-checkable, hash-bound, non-expired `PromptIsolationQualificationRecord` for exact provider/representation mode; checked at preflight and atomic admission. | None material at design level. | None required for closure. |

---

## B. Newly discovered findings

### High

**R4-H01 — Hidden unexposed mutable provider semantic state can still escape `ProviderContextStateEvidence`**

- **Severity:** High
- **Affected rule/invariant/test:** M-I37, M-I40, M-I43; standard “Clean material-review context and delivery session binding”; tests TM-P04, TM-P05, TM-N07..TM-N10.
- **Concrete false-green path:** A provider has an undocumented mutable memory/instruction/connector state that is not exposed by its API and is not triggered by the chosen behavioral sentinels. The platform cannot read it, disable it, or fence it. `ProviderContextStateEvidence` appears clean; admission proceeds; the review verdict is treated as material.
- **Why current design is insufficient:** The design requires behavioral sentinel qualification for “every mutable semantic channel available to the provider mode” and says “unknown mutable semantic context is never tolerated.” But if the channel is hidden from the provider API and not discovered by sentinels, the platform cannot know it is unknown. The design does not record this as a residual nonclaim or force a dedicated account with all mutable features disabled by provider policy.
- **Narrow required correction:** Add an explicit nonclaim/residual for hidden provider-internal mutable semantic state not exposed by the provider API. For material review, require either (a) a provider-exposed complete mutable-state inventory plus readable monotonic version/fence, or (b) a dedicated platform-owned account/project whose mutable semantic features are disabled by provider policy and behaviorally requalified. Add an adversarial adapter that simulates hidden unexposed mutable state.

**R4-H02 — Validator-logic mutation coverage does not delete/weaken every admissibility conjunct**

- **Severity:** High
- **Affected rule/invariant/test:** Phase O; exit criteria “every admissibility conjunct is independently falsified”; standard mutation suite “delete each `VerdictAdmissibilityResult` conjunct one at a time”; R3-H05 closure.
- **Concrete false-green path:** A validator implementation omits or weakens an admissibility predicate not covered by a targeted logic mutation, such as egress authorization, wire binding, session/file/retrieval coverage, complete materialization, governed representation/transformation, semantic review coverage, reviewer provenance, or promotable disposition. No Phase O mutation kills that omission, so a false-green verdict could be admitted.
- **Why current design is insufficient:** Phase O lists many logic mutations but not one for every enumerated `VerdictAdmissibilityResult` conjunct. Data/state negative tests may catch some omissions, but the exit criteria and standard require targeted predicate deletion/weakening mutation coverage.
- **Narrow required correction:** Add one targeted `TM-O` logic mutation for each remaining admissibility conjunct, with an independently killed expected result.

### Medium/Low

**R4-M01 — Live governance failure taxonomy still omits critical EXP-M codes**

- **Severity:** Medium
- **Affected rule/invariant/test:** R3-M05; standard failure taxonomy; live procedure step 25; tests TM-D07..TM-D09, TM-P22.
- **Concrete false-green path:** Runtime returns `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` or `MIXED_INSUFFICIENCY`, but the live taxonomy does not preserve the code. The cause may be collapsed into a generic or first-match failure, weakening the independent-cause adjudication requirement.
- **Why current design is insufficient:** The standard defines the codes, but `LIVE-CONVERSATION-GOVERNANCE.md` does not list them in its failure taxonomy.
- **Narrow required correction:** Add all missing codes to the live taxonomy and reconcile with the standard and test matrix.

**R4-M02 — “Stricter” base/head merge lacks a defined partial order**

- **Severity:** Medium
- **Affected rule/invariant/test:** M-I42; standard “Delivery-governor trust root”; R3-C01 remediation.
- **Concrete false-green path:** If the platform-defined partial order is not actually specified per governing element class, an implementation may treat incomparable representation/semantic/risk changes as comparable and silently accept a weakening. Alternatively, it may fail closed so often that legitimate changes are impossible.
- **Why current design is insufficient:** The standard requires “the stricter base/head requirement” and says incomparable conflicts fail unresolved, but it does not define the comparison operator for each governing element type.
- **Narrow required correction:** Specify per-element partial-order/comparison rules, or require independent authority approval for any same-dimension semantic change rather than attempting automatic merge.

**R4-L01 — Health-check renewal prohibition lacks a targeted test**

- **Severity:** Low
- **Affected rule/invariant/test:** M-I38; Phase F.
- **Concrete false-green path:** A health check could be implemented to renew an expired profile despite the rule that health checks may invalidate but never renew.
- **Why current design is insufficient:** The design states the rule, but no test explicitly attempts health-check renewal.
- **Narrow required correction:** Add a test that an expired profile cannot be renewed by a health check and requires requalification.

---

## C. Gate verdicts

| Gate | Verdict |
|---|---|
| REQUIRED_EVIDENCE_AUTHORITY | **PASS** |
| DELIVERY_GOVERNOR_TRUST_ROOT | **PASS** |
| GOVERNANCE_AUTHORITY_SNAPSHOT | **PASS** |
| CLEAN_SESSION_CONTEXT | **FAIL** |
| PROVIDER_SEMANTIC_CONTEXT_BINDING | **FAIL** |
| PROVIDER_CONTEXT_ADMISSION_FENCE | **FAIL** |
| WIRE_BINDING | **PASS** |
| CHUNK_CONTEXT_MODEL | **PASS** |
| REMOTE_ACCESSIBILITY_MODEL | **PASS** |
| PROVIDER_ACCESSIBILITY_RISK_POLICY | **PASS** |
| PROVIDER_CAPABILITY_QUALIFICATION | **PASS** |
| STATISTICAL_PROTOCOL | **PASS** |
| REPRESENTATION_GOVERNANCE | **PASS** |
| MATERIALIZATION_SAFETY | **PASS** |
| EGRESS_BOUNDARY | **PASS** |
| SESSION_FILE_RETRIEVAL_BINDING | **PASS** |
| RETRIEVAL_FINAL_CONTEXT_BINDING | **PASS** |
| INSUFFICIENT_EVIDENCE_TAXONOMY | **FAIL** |
| MULTI_REVIEWER_EQUIVALENCE | **PASS** |
| DECOMPOSITION_AGGREGATION | **PASS** |
| PROMPT_ISOLATION_DEPENDENCY | **PASS** |
| TOCTOU_RETRY_INTEGRITY | **FAIL** |
| ATOMIC_VERDICT_ADMISSION | **FAIL** |
| REVIEWER_TOOL_EVIDENCE_BOUNDARY | **PASS** |
| TEST_MATRIX_SUFFICIENCY | **FAIL** |
| VALIDATOR_LOGIC_MUTATION_COVERAGE | **FAIL** |

The CLEAN_SESSION_CONTEXT, PROVIDER_SEMANTIC_CONTEXT_BINDING, PROVIDER_CONTEXT_ADMISSION_FENCE, TOCTOU_RETRY_INTEGRITY, and ATOMIC_VERDICT_ADMISSION failures all stem primarily from R4-H01: hidden unexposed mutable provider state can change without a readable version/fence and without being covered by sentinels.

---

## D. Statistical protocol adjudication

- **299/299 exact minimum:** Yes. For zero failures, the one-sided 95% exact Clopper–Pearson lower bound is `0.05^(1/n)`. `0.05^(1/299) >= 0.99`, while `0.05^(1/298) < 0.99`. 299 is the exact minimum.
- **Independence/correlation nonclaim:** Honest enough at design level. The design records `STATISTICAL_INDEPENDENCE_UNPROVEN` when provider-side correlation/route allocation cannot be observed and refuses to present the bound as a universal provider failure probability. It also requires per-attempt accessibility proof when deterministic proof is unavailable.
- **3-day/4-time-block schedule and interleaving:** Falsifiable in principle. Tests M-90, TM-P08, TM-P11, and TM-Q11 cover burst, schedule, production-envelope, and correlated-route attacks. Minor gap: no explicit test that health checks cannot renew.
- **Every attempted trial forced into append-only ledger:** Yes at design level. Rules say all attempts count; no exclusions/rerolls/optional stopping; failed attempts preserved. Tests M-91, TM-P09, TM-O09, TM-N13..TM-N14.
- **Exploration/confirmation separation:** Yes. Disjoint families, frozen confirmation IDs/schedule, exploration never reused. Tests M-92, TM-P10, TM-O10.
- **Production-envelope equivalence:** Defined via the operating-point tuple and explicit production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes. Tests M-93, TM-P11, TM-O12.
- **80% margin:** Correctly supplemental. No monotonicity is inferred; the claimed point itself must be tested. If a failure boundary is observed, cap ≤80% of smallest observed failing boundary; if none, cap ≤80% of largest independently confirmed passing point.
- **Profile expiry/drift:** 7-day default, immediate on material provider/model/deployment/account/endpoint/region/adapter/session/file-processing drift; health checks invalidate only, never renew. Minor gap: add explicit health-check-renewal test.

---

## E. Accessibility and retrieval adjudication

- **Max slice ≤ min(2048 UTF-8 bytes, 512 provider tokens):** Yes, explicitly stated.
- **Every slice challenged every confirmation trial:** Yes, for qualification trials when deterministic range/retrieval proof is unavailable.
- **Per-attempt content-bound challenge in final adjudication session:** Yes, mandatory for production material-review attempts using modes without deterministic range/retrieval proof.
- **Framing canaries only supplemental:** Yes. Content-bound challenges are load-bearing; framing/end sentinels cannot substitute.
- **Selective/sub-slice loss recorded as nonclaim/residual:** Yes. The failure model is explicitly bounded to contiguous loss/eviction at or above slice granularity; arbitrary selective/sub-slice loss remains a nonclaim/residual.
- **ProviderAccessibilityRiskPolicy chooses whether residual acceptable:** Yes. Every protected transition class has a policy; unknown policy fails closed; highest material-authority class requires deterministic full-range/page/member proof or equivalently observable inline mode.
- **Highest material-authority transition requires deterministic proof:** Yes.
- **Opaque media/modalities cannot inherit text qualification:** Yes. Scans, tables, images, embedded objects, archives are separate media/modality classes; synthetic text-layer PDFs cannot qualify them.
- **Model-selected retrieval requires returned-byte hash/range/version plus tool-result binding into final context:** Yes. Unconditional for material review; “file opened,” file ID, or citation alone is insufficient.

---

## F. Authority and atomic-admission adjudication

Attempted breaks:

- **Authority snapshot pointer:** Design places pointer/registries outside candidate write set. No direct candidate narrowing path at design level.
- **Base/head conservative merge:** Deletions/weakenings under same ID are treated as changed inputs; union/stricter merge preserves base requirements; incomparable conflicts must fail unresolved.
- **Same-ID semantic mutation:** Stable-ID + content-hash binding prevents silent in-place replacement.
- **Unknown/empty contract:** Fails `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; non-vacuity baselines required.
- **Relationship registry:** `RequiredInteractionContract` derived only from authority snapshot registry, not proposer metadata.
- **Risk policy registry:** Missing `ProviderAccessibilityRiskPolicy` fails closed.
- **Provider context state:** Known mutable channels must be readable/disable-able or mode is `NOT_QUALIFIED`; sentinel qualification required.
- **Provider admission fence:** Required for every load-bearing mutable provider/account/project/session configuration channel; readable monotonic version or platform-enforceable fence; otherwise mode not qualified.
- **Prompt-isolation qualification:** Deterministically selected, hash-bound, non-expired, checked at preflight and admission.
- **Atomic compare-and-set checkpoint:** Defined as final authority operation; all versions/hashes re-read and compared; any invalidation from first dispatch through admission permanently voids the attempt.
- **Can later requalification revive an old invalidated response?** No. The design explicitly forbids revival; only a new delivery attempt may proceed.

**Remaining break:** R4-H01. Hidden unexposed mutable provider state is not covered by a readable version/fence or sentinel, so it can change without detection and without voiding the attempt. This defeats the intended TOCTOU/atomic-admission guarantee for that hidden channel.

---

## G. Test-plan adjudication

- **Test IDs no longer collide:** Yes. Matrix uses `TM-` namespace; frozen experiment tests use `M-`.
- **Unified mutation catalog:** Yes. Phase G is the single authoritative mutation catalog.
- **All deterministic phases A–Q gated:** Yes. Exit criteria require all deterministic phases A–Q.
- **Logic mutations attack code predicates, not only data:** Partially. Phase O includes many predicate-level mutations, but it does not delete/weaken every `VerdictAdmissibilityResult` conjunct. See R4-H02.
- **Lying readback, hidden state, correlated burst, failed-trial replay, canary-preserving content loss, missing retrieval log, atomic-admission race have adversarial oracles:** Mostly yes. Adapters/adapters are listed and tests exist.
- **`REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`, provider-context/retrieval/admission codes defined consistently:** No. The standard defines them, but the live governance failure taxonomy is missing many of them. See R4-M01.

---

## H. Final determination

- **Any Critical design defect remains:** No new Critical beyond R3-C01, which is design-closed.
- **Any High design defect remains:** Yes. R4-H01 (hidden unexposed mutable provider state) and R4-H02 (incomplete validator-logic mutation coverage).
- **Is EXP-M ready for deterministic implementation/falsification?** Not yet as reviewed. The remaining High defects should be repaired at design/preregistration level first to avoid burning first exposure.
- **May live provider pilots begin?** No.
- **Exact remaining prerequisites:**
  1. Add explicit nonclaim/residual and dedicated-account/full-inventory requirement for hidden unexposed mutable provider semantic state (R4-H01).
  2. Add targeted validator-logic mutations for every remaining `VerdictAdmissibilityResult` conjunct (R4-H02).
  3. Reconcile live governance failure taxonomy with the standard and test matrix (R4-M01).
  4. Define per-element “stricter” partial-order/comparison rules or require independent authority approval for same-dimension semantic changes (R4-M02).
  5. Add explicit health-check-cannot-renew test (R4-L01).
  6. Keep all deterministic phases A–Q green before any live pilot.
- **EXP-M remains `NOT_QUALIFIED`.**
- **This external/manual review itself grants no platform review or promotion authority.**