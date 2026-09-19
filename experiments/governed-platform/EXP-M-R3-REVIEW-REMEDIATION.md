# EXP-M R3 External Review Adjudication and Remediation

## Status

`R3_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R4_REVIEW`

The supplied R3 external review is accepted as valid defect evidence. It remains non-authoritative external/manual review evidence and grants no promotion or platform-review authority.

EXP-M remains `NOT_QUALIFIED`. No live provider pilot or scientific execution is authorized by this remediation.

## R3 source review disposition

R3 returned `CHANGES_REQUIRED` and found:

- one Critical: R3-C01;
- five High: R3-H01 through R3-H05;
- Medium/Low: R3-M01 through R3-M05;
- additional lower findings R3-L01 through R3-L03.

The reviewer also found the prior 59/59 statistical rule too weak for the implied assurance and required per-attempt content-bound witnesses plus stronger provider/retrieval/context controls.

## Finding-by-finding adjudication

### R3-C01 — Requiredness contracts have no bound input authority

Evaluation: **VALID / CRITICAL**

Remediation:

1. Added immutable `GovernanceAuthoritySnapshot` from a pre-candidate authority state outside the candidate write set.
2. Transition-class, mandatory-dimension, evidence-selection, evidence-relationship, accessibility-risk and governing-standard registries are authority inputs, not candidate declarations.
3. Candidate edits to governing inputs cannot narrow their own review.
4. Base/head governing changes use a conservative merge:
   - mandatory refs/dimensions/interactions are unioned;
   - representation, evidence semantics, statistical thresholds, accessibility-risk and review constraints preserve the stricter rule;
   - incomparable conflicts fail `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.
5. Governing elements are stable-ID + content-hash bound; same-ID semantic replacement is a changed authority input.
6. Unknown transition class, missing rule, empty/vacuous contract or missing risk policy fails closed.
7. RequiredInteractionContract is derived from the authority snapshot, not proposer metadata.
8. Added authority-input poisoning, same-ID semantic weakening, unknown-class and empty-contract falsification.

### R3-H01 — Provider context state declared rather than observed

Evaluation: **VALID / HIGH**

Remediation:

1. Added per-attempt `ProviderContextStateEvidence`.
2. Material reviews use a fresh stateless request or trusted-adapter-created fresh stateful session.
3. Context evidence binds transcript/message IDs, prompt layers, tools/connectors, custom instructions, memory state, knowledge connectors, files, model/deployment, configuration version and adapter identity.
4. Context/config state is checked at preflight, before every dispatch and at final admission.
5. Mutable semantic channels that are neither readable nor disable-able make the mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.
6. Stateful reuse is limited to the same trusted delivery-attempt lineage with a WireDeliveryRecord for every prior mutation.
7. Added behavioral sentinel qualification for every mutable provider semantic channel.
8. Added `AdmissionFenceRecord`/provider version requirement so concurrent candidate/user configuration changes cannot race final admission.
9. Provider documentation is background evidence only; it cannot prove clean context by itself.
10. Added lying-readback, hidden-dirty-state and configuration-race tests/adapters.

### R3-H02 — Statistical capability protocol not falsifiable

Evaluation: **VALID / HIGH**

Remediation:

The former 59/59 rule was replaced.

Default material-review risk budget is now:

- `p_min = 0.99`;
- one-sided 95% exact Clopper–Pearson;
- **299/299** successful confirmation trials at each claimed operating point;
- zero hard failures;
- all attempted trials count, including timeout/provider error/rate limit/ambiguous/unverifiable outcomes;
- no exclusions, rerolls, optional stopping or failed-attempt replacement;
- exploration and confirmation are disjoint;
- confirmation trial IDs and schedule are frozen before exposure;
- confirmation spans at least 3 UTC days and 4 preregistered time blocks/day with randomized/interleaved operating points;
- exact claimed operating point must be tested;
- no monotonic interpolation assumption;
- production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes required;
- append-only failure history persists through the provider drift epoch;
- health checks may invalidate but never renew;
- default expiry remains 7 days with immediate drift-triggered invalidation.

Hard failure and the full operating-point tuple are now explicitly defined.

The exact arithmetic is used: 298/298 is below a 0.99 one-sided 95% lower bound, while 299/299 exceeds it.

The statistical interpretation is also bounded: if provider-side route/trial independence cannot be evidenced, the profile records `STATISTICAL_INDEPENDENCE_UNPROVEN`; the Clopper–Pearson value cannot be presented as a universal provider failure probability.

### R3-H03 — Dense witness coverage qualification-only

Evaluation: **VALID / HIGH**

Remediation:

1. Sparse head/middle/tail canaries are explicitly diagnostic only.
2. For modes without deterministic range/retrieval proof, per-attempt content-bound witnesses are mandatory in the same final adjudication session.
3. Lossless text is sliced to at most:
   - 2048 UTF-8 bytes; and
   - 512 provider-tokenizer tokens;
   whichever is smaller.
4. Every required slice is challenged in every confirmation trial.
5. The platform selects unpredictable slice-local content extracts after representation freeze; expected values are withheld from the reviewer.
6. Framing/end sentinels remain supplemental and cannot substitute for content-bound checks.
7. The failure model is explicit: this witnesses contiguous loss/eviction at or above the slice granularity; arbitrary selective/sub-slice loss remains a nonclaim/residual risk.
8. Added `ProviderAccessibilityRiskPolicy` per transition class. Highest material-authority transitions require deterministic full-range/page/member proof or an equivalently observable inline mode; probabilistic witnesses alone cannot silently satisfy that class.
9. Opaque attachments are qualified by media/modality class; scans/tables/images/embedded objects cannot inherit text-PDF qualification.
10. Added canary-preserving content-loss and selective-loss tests.

### R3-H04 — Retrieval/file completeness discretionary

Evaluation: **VALID / HIGH**

Remediation:

For model-selected retrieval, deterministic per-attempt access logs are now unconditional for material review.

They must prove every required range/page/member with:

- exact source/version identity;
- requested range/member;
- returned content hash and length/range;
- retrieval time;
- tool/result message identity;
- binding of the tool result into the same final adjudication session/context.

“File opened”, file ID binding, citation text or attach-time success are insufficient.

If the provider cannot expose sufficient deterministic retrieval/context logs, that mode is diagnostic-only / `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`. Platform-forced inline inclusion is the alternative.

### R3-H05 — Test matrix did not falsify repaired invariants

Evaluation: **VALID / HIGH**

Remediation:

1. Matrix IDs are namespaced `TM-...` to avoid collision with frozen `M-...` experiment cases.
2. Phase G is now the single unified mutation catalog.
3. Added validator-logic mutation phase:
   - delete each admissibility conjunct;
   - weaken equality to subset;
   - bypass authority snapshot;
   - accept empty contract;
   - drop dirty-context check;
   - accept 298 instead of 299;
   - allow one hard failure;
   - make witnesses/retrieval logs optional;
   - skip final atomic CAS;
   - revive void attempt;
   - skip prompt-isolation/risk/fence predicates.
4. Added adversarial-oracle adapters for:
   - authority-input poisoning;
   - lying context readback;
   - hidden dirty state;
   - correlated/time-burst trials;
   - failed-trial replay;
   - production-envelope mismatch;
   - canary-preserving content loss;
   - missing retrieval logs;
   - atomic admission race.
5. Exit criteria now require **all deterministic phases A–Q** and zero data/state and validator-logic mutation survivors.
6. Defined `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION` and reconciled failure taxonomy.

## Medium/Low closure

### R3-M01 — revalidation not atomic/final

Accepted and repaired.

Verdict admission is now the final authority operation and uses compare-and-set with the checkpoint. Authority snapshot, capability profile, accessibility-risk policy, egress state, provider context/session/file state, AdmissionFenceRecord, prompt-isolation record and ReviewRequest identities are re-read at admission.

Any invalidation from first dispatch through admission permanently voids the attempt. Later requalification cannot revive the old response.

### R3-M02 — interaction granularity

Accepted and repaired.

Each RequiredInteractionContract interaction is an explicit set of raw evidence refs/representations that must coexist in one qualified reviewer context. The aggregator reviews the raw set, not only subreview outputs.

### R3-M03 — permissive hedges

Accepted and narrowed.

Load-bearing provider deployment/retrieval/context facts are mandatory when the selected proof mode needs them. Missing required deployment identity, range logs or context state makes the mode not qualified rather than silently optional.

### R3-M04 — incomplete admissibility conjunct list

Accepted and repaired.

`VerdictAdmissibilityResult` now enumerates all load-bearing predicates: authority snapshot, evidence contract, interaction contract, materialization, transformation, egress, statistical capability, accessibility-risk policy, provider context, admission fence, wire binding, per-attempt accessibility, retrieval/session/file coverage, prompt isolation, semantic coverage, provenance and disposition.

### R3-M05 — cause adjudication first-match

Accepted and repaired.

Insufficiency causes are evaluated independently. Multiple true causes yield `MIXED_INSUFFICIENCY` with the complete cause set.

Added/reconciled:
- `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`
- provider context/retrieval/admission failure codes.

### R3-L01 — live procedure ordering

Accepted and repaired.

Authority snapshot + required contracts are derived before materialization. Pre-dispatch state revalidation is explicit.

### R3-L02 — SDK serialization boundary

Accepted and repaired.

WireDeliveryRecord now includes:
- pre-SDK platform request hash;
- post-SDK transport-bound semantic envelope hash at the lowest observable adapter boundary;
- all non-secret semantic routing/model/tool/file/session fields.

If the SDK hides a load-bearing semantic mutation, the adapter/mode cannot claim exact wire binding.

### R3-L03 — EXP-L applicability

Accepted and repaired.

The governor now selects a machine-checkable, hash-bound, non-expired `PromptIsolationQualificationRecord` for the exact provider/representation mode. It is checked at preflight and atomic admission.

## Additional self-adjudication after R3 repair

A further false-green pass found and repaired four additional design weaknesses before R4 handoff:

### SA-R4-H01 — governing semantic replacement under same ID

A candidate could retain a required-ref ID while weakening representation/risk semantics.

Repair: governing elements are stable-ID + hash bound; base/head semantic changes preserve the stricter requirement or fail unresolved.

### SA-R4-H02 — probabilistic accessibility used without transition risk authority

Repair: added ProviderAccessibilityRiskPolicy to the authority snapshot. Highest material-authority class requires deterministic proof; missing policy fails closed.

### SA-R4-H03 — provider configuration race at admission

Repair: added AdmissionFenceRecord/readable monotonic provider config version. Unfenceable/unreadable load-bearing mutable channels make the mode unqualified.

### SA-R4-H04 — retrieval logs proved opening but not final-context insertion

Repair: retrieval evidence now binds returned bytes/hash/range and resulting tool-message identity to the final adjudication session.

### SA-R4-M01 — statistical independence overclaim

Repair: correlation/route independence is explicitly bounded. Fresh request IDs alone do not prove independent Bernoulli trials; `STATISTICAL_INDEPENDENCE_UNPROVEN` is recorded when provider-side correlation cannot be evidenced.

## Fresh self-adjudication result

After the above additional repairs, a fresh adversarial design pass found:

- open Critical design findings: **0**
- open High design findings: **0**

This is **self-review only**. It is not independent evidence and does not qualify EXP-M.

## R4 handoff

`READY_FOR_R4_INDEPENDENT_DESIGN_REVIEW`

No implementation or live provider pilot should begin until the R4 review closes the design boundary and deterministic implementation/falsification is separately authorized.
