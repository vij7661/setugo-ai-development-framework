# WDPC V24 I11 Falsification Plan V8 — Clean Independent Review Packet

**PLAN_BODY_SHA256:** `0a9620d696d853bb6a60de123504f5958345a3ebf63a6297c76e85c319dbb717`  
**Harness blob:** `189d050831166868397e1ba063da57fa77f2dd42`  
**Harness version:** `1.6.0-PLAN-REVIEW`  
**Design SHA:** `db9e4b349fd26e128f4486878a4af64929000a7c`  
**Design tree:** `7986f7a016d97e6c9bbd03c035b3e9c63effda75`  
**Implementation SHA:** `9836dc3ff233cca582f485434fc1c6494cf7eb05`  
**Implementation tree:** `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`  
**Status:** `REVIEW_REQUIRED / NOT_EXECUTED`  
**Authority effect:** `NONE_EVIDENCE_ONLY`

This packet is self-contained for independent plan review. `SELF_CONTAINED_BINDING` concerns this packet's internal consistency. Full packet SHA-256 and the detached V8 review-binding Git blob are intentionally verified only in the post-review repository adjudication gate.

---

# WDPC V24 I11 Falsification Plan V8 — Clean Independent Review Surface

**Packet class:** `TEST_PLAN_REVIEW_PACKET`  
**Review context:** `CLEAN_PACKET_ONLY_CONTEXT`  
**Exact frozen V24 design candidate:** `db9e4b349fd26e128f4486878a4af64929000a7c`  
**Exact implementation subject through I10:** `9836dc3ff233cca582f485434fc1c6494cf7eb05`  
**I10 tree:** `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`  
**Frozen harness contract version:** `1.6.0-PLAN-REVIEW`  
**Frozen harness Git blob:** `189d050831166868397e1ba063da57fa77f2dd42`  
**Plan status:** `REVIEW_REQUIRED / NOT_EXECUTED`  
**Authority effect:** `NONE_EVIDENCE_ONLY`

## 1. Reviewer isolation and admissibility

Review only this clean V8 packet. Do not import prior reviewer findings, dispositions, chats, model memory, or prior V1–V7 review/adjudication artifacts. No WDPC-431…506 case has been executed by this packet.

**Reviewer type is not an admissibility gate.** Do not classify or self-disqualify the review merely because the reviewer is a human or an AI system.

A review is admissible for this TESTING/FALSIFICATION plan gate when all of the following are true:

1. it is initiated manually by the user in a fresh clean review context;
2. the reviewer receives only the exact V8 clean review surface and the explicitly permitted exact repository objects/evidence;
3. prior reviewer findings/dispositions are not supplied to the reviewer;
4. the reviewer independently evaluates the packet and verifies the required exact bindings;
5. no reviewer/provider API call is automatically initiated by the governed platform during TESTING/FALSIFICATION;
6. the reviewer returns the required plan-review disposition and findings.

An external LLM used in a user-initiated clean chat is therefore permitted as an independent reviewer. Its conclusions remain evidence, not self-granted runtime/release authority; the execution gate is satisfied only by the governed adjudication of the exact reviewed V8 artifact.

`REVIEWER_API_CALLS = PROHIBITED` remains mandatory. This means **no automated programmatic reviewer dispatch**, not “AI reviewers are forbidden.”

## 2. Frozen sources and role neutrality

- WDPC-431…470 blob `0f52617114f7d9d549d9822f11d5bc0156c6e676`
- WDPC-471…486 blob `ff8677ca1170f5cef6318662309ba119145e68cf`
- WDPC-487…496 blob `17bfa33f6388934d47323cea3c375466c178aadf`
- WDPC-497…506 blob `042b881795929f9e8d9ff5bb72f8eda8ca93fad0`

`R1`, `R2`, and `R3` are abstract governed review-role slots only: R1 is the first governed review role, R2 is an independently selected second role where governing policy requires it, and R3 is an escalation/tie-break role only where governing policy explicitly requires it. These labels carry no provider/model identity. No V24 I11 fixture may contain a hard-coded provider/model mapping for R1/R2/R3; such a mapping is `FAIL_FIXTURE_DEFECT`. No WDPC-431…506 expected outcome depends on a named LLM.

EXP-ECC-6 and EXP-ECC-7 remain deferred.

### 2.1 Meaning of `manual` in execution/evidence classes

In class names such as `EXTERNAL_MANUAL_REQUIRED`, `MANUAL_SEMANTIC_REQUIRED`, and `STATIC_OR_MANUAL_REQUIRED`, **manual means user-mediated / non-automated review or evidence handling**. It does not require a human reviewer merely by label.

A human reviewer or an external AI reviewer may perform the analysis if the review is manually initiated by the user, isolated from prior findings, supplied the exact qualifying evidence, and no automated reviewer API call is used. Where the evidence itself requires a real-world fact (for example IAM configuration, witness control-domain separation, or bootstrap ceremony), the reviewer may assess only supplied authenticated/qualified evidence and must return `INSUFFICIENT_EVIDENCE` when that evidence is absent.

## 3. Exact plan and harness identity

The review surface is frozen in two layers: (a) this document contains a `PLAN_BODY_SHA256` in the wrapper generated from the exact body bytes; (b) a detached repository binding records the full review-packet SHA-256 and Git blob identity after materialization. The harness contract is already frozen by Git blob above. Every execution record must bind all three identities; filename or paraphrase is insufficient.

Every executed case `CaseRunBinding` must bind **all three governed review identities**: `packet_sha256` (full packet bytes), `plan_body_sha256`, and `plan_binding_blob_sha` (Git blob of the detached V8 review binding), plus the exact harness blob/version, V24 design SHA, I10 implementation SHA/tree, fixture digest, environment digest, and target module blobs. A binding that omits or mismatches any of these fields is a harness failure and cannot execute.

The detached V8 review binding is materialized **after** the packet hash/body hash are finalized. Its Git blob SHA is then supplied to the execution harness as `plan_binding_blob_sha`. The clean review packet does not attempt to self-embed that later blob SHA.

### 3.1 Self-contained review binding and post-review repository adjudication

The independent reviewer is **not required to have repository access**. Lack of repository access is not, by itself, `INSUFFICIENT_TO_ASSESS`.

The reviewer assesses only the supplied **V8 clean packet** and the exact embedded **V8 harness contract V7**, and reports:

`SELF_CONTAINED_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_PACKET_CONTENT`

`CONSISTENT` means the packet is internally coherent: one V8 packet identity, one frozen V24 design/I10 implementation identity, one harness version/blob declaration, all 76 cases are present exactly once, the matrix and prose agree, and the embedded harness semantics do not contradict the plan.

`SELF_CONTAINED_BINDING = CONSISTENT` evaluates only the supplied clean packet's internal identity and semantic coherence. It does **not** require the reviewer to know the later `packet_sha256` or detached `plan_binding_blob_sha`; those are deliberately verified by the second, repository-connected adjudication gate.

The reviewer must not claim to have independently verified GitHub state if it cannot access GitHub. After a `READY_FOR_EXECUTION` review, the repository-connected governed adjudicator separately verifies:

1. exact V8 packet SHA-256 and plan-body SHA-256;
2. committed detached V8 review-binding Git blob;
3. harness Git blob `testing/v24/v24_i11_harness_contract_v7.py`;
4. frozen V24 design commit/tree;
5. frozen I10 implementation commit/tree;
6. the four frozen V24 falsification source blobs.

A review disposition does not become execution authority until this post-review repository-binding adjudication succeeds.

### 3.2 Hash and object-identity scopes

The integrity identifiers have distinct scopes:

- `packet_sha256`: SHA-256 of the complete UTF-8 V8 packet bytes, wrapper plus plan body;
- `PLAN_BODY_SHA256`: SHA-256 of only the exact V8 plan-body bytes;
- `plan_binding_blob_sha`: Git object ID of the detached V8 review-binding file, materialized after packet/body hashes are finalized;
- `harness_blob_sha`: Git object ID of the exact harness source;
- `target_module_git_blobs`: exact Git object IDs for implementation modules under test;
- `target_module_content_sha256s`: SHA-256 digests of those same module contents.

Git object IDs are validated as Git object IDs (40-hex in the current repository, with 64-hex allowed for Git SHA-256 repositories); they are not mislabeled as SHA-256 content digests.

Every executed `CaseRunBinding` must bind `packet_sha256`, `plan_body_sha256`, `plan_binding_blob_sha`, harness blob/version, frozen V24/I10 identities, target-module Git IDs and SHA-256 content digests, fixture digest, environment digest, run ID, and case status.

## 4. Environment and fixture lock

- Reference runtime family is Python `3.12`, but each run must bind an exact `3.12.<patch>` version string. A caller-supplied `3.12` without patch level is invalid.
- `PYTHONHASHSEED=0`; timezone `UTC`; fixture random seed `24011`.
- Reference cases use `NETWORK_POLICY=DENY`. External/manual evidence is pre-materialized and hash-bound; the test runner never fetches it via reviewer/provider APIs.
- Each run captures `/etc/os-release`, `uname`, exact Python version, and dependency-lock material. Preferred method is sorted `python -m pip freeze` with `dependency_lock_method=PIP_FREEZE`.
- If `pip` is unavailable, use `dependency_lock_method=STDLIB_ONLY_PIP_UNAVAILABLE`. Harness V7 recomputes SHA-256 over the exact canonical literal `PIP_UNAVAILABLE|STDLIB_ONLY_HARNESS|PYTHON=<exact-version>` and requires equality with `dependency_lock_digest`. The run records `nonstdlib_imports`; any non-empty value under this fallback is `FAIL_HARNESS_DEFECT`.
- All environment/file digests used by the harness must be lowercase hexadecimal SHA-256 values, not merely 64-character strings.
- The resulting environment fields form `EnvironmentIdentity`; any changed captured identity creates a new run identity.
- Synthetic time uses only `FROZEN_LOGICAL_CLOCK` or explicit case timestamps. Instrumentation records `unexpected_wall_clock_read_count`; any non-zero value is `FAIL_HARNESS_DEFECT`.
- External evidence currentness uses the governing source/policy's bound currentness rule. If no qualifying currentness rule/evidence is supplied, classify `INSUFFICIENT_EVIDENCE`; do not invent a TTL.
- Every case gets a fresh temporary DB/store/repository and deterministic fixture identity. No mutable state is shared across cases.

## 5. Canonical governed endpoint schema

Each executed case produces `GovernedEndpointObservation{endpoint, emission_surface, raw_result_digest, internal_diagnostics[]}`. `endpoint` must be emitted by the implementation's governed result/interface. The harness must never translate, normalize, or alias an internal diagnostic/problem code into the expected endpoint. Missing `endpoint` when one is required is `FAIL_CODE_DEFECT` after fixture/harness preflight succeeds.

For negative cases the result also contains `AuthorityEffectObservation{profile_id,before_digest,after_digest,unauthorized_effect_count_before,unauthorized_effect_count_after,...}`. PASS requires the exact expected endpoint and unauthorized-effect delta exactly zero.

### 5.1 Conjunctive assertion model

Where a case requires both an endpoint and a preserved-state/history invariant, the harness uses `ConjunctiveAssertionObservation{primary_endpoint,required_invariants,satisfied_invariants,invariant_evidence_digests}`. The endpoint and **every** required invariant are independently asserted. Satisfying only the endpoint or only the invariant is not PASS.

For WDPC-457 the primary governed endpoint is exactly `AUTHORITY_EVIDENCE_SOURCE_INVALID` and the mandatory conjunctive invariant tuple is exactly `("HISTORICAL_RESULT_UNCHANGED",)`. Harness V7 owns that exact tuple in `REQUIRED_CONJUNCTIVE_INVARIANTS`; the fixture cannot substitute another invariant name.

### 5.2 Blocked cases are statuses, not endpoints

WDPC-469 and WDPC-495 are pre-execution gates. They are the **only** cases permitted to use `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`; any other case carrying that status is a harness failure. While I1 semantic qualification is incomplete:
- `case_status = BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`;
- no case body executes;
- no `GovernedEndpointObservation` is produced;
- no execution result state is produced;
- the strings describing the missing qualification are **not** governed endpoints.

Unblocking either case requires the underlying semantic qualification evidence plus a successor exact execution surface if a governed positive endpoint/assertion is required. This V8 plan does not silently convert the blocked status into PASS.

## 6. Result-classification criteria

- `FAIL_FIXTURE_DEFECT`: the fixture does not satisfy its preregistered preconditions, does not inject the target fault/positive condition, or accidentally activates another stricter predicate.
- `FAIL_HARNESS_DEFECT`: fixture is valid but harness binding/observation/isolation/environment machinery fails before a scientific endpoint can be evaluated.
- `FAIL_CODE_DEFECT`: fixture and harness are valid, but implementation emits wrong/missing governed endpoint, permits unauthorized effect, violates positive expected behavior, or produces inconsistent bound state.
- `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`: required external/manual artifact set was not supplied, so the operational case was not executed.
- `INSUFFICIENT_EVIDENCE`: supplied evidence was evaluated but fails required independence/currentness/completeness/custody qualification, or the frozen case explicitly chooses this endpoint.
- `BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE`: positive control cannot execute because its same-mechanism negative invariant has an unresolved code/harness/fixture failure.
- `PASS`: every exact case assertion is satisfied. Synthetic/reference PASS never upgrades an external/manual requirement.

### 6.1 Normative execution-class policy

Execution class is distinct from result classification.

| Execution class | Execution permission after plan approval | Required evidence | Operational PASS allowed? | Missing-evidence behavior |
|---|---|---|---|---|
| `REFERENCE_HARNESS` | Deterministic reference execution permitted | Exact synthetic fixture + bound environment | Yes, for the bounded reference assertion only | Fixture/harness/code classification applies |
| `REFERENCE_MECHANISM_ONLY` | Deterministic mechanism execution permitted | Exact synthetic fixture + bound environment | **No operational qualification**; PASS means mechanism-only behavior | Fixture/harness/code classification applies |
| `HYBRID_EXTERNAL_REQUIRED` | Reference leg may execute; operational case also requires external/manual evidence | Synthetic mechanism evidence **and** named per-case external profile | Only after both legs qualify | No external bundle → `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`; supplied but unqualified → `INSUFFICIENT_EVIDENCE` |
| `EXTERNAL_MANUAL_REQUIRED` | No synthetic operational PASS | Named per-case external evidence + independent adjudication | Yes only from qualifying external/manual evidence | Missing bundle → `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`; unqualified bundle → `INSUFFICIENT_EVIDENCE` |
| `MANUAL_SEMANTIC_REQUIRED` | No synthetic semantic PASS | Exact artifacts + semantic rubric + independent adjudication | Yes only when every load-bearing dimension qualifies | Missing review/evidence → `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`; unresolved dimension → `INSUFFICIENT_EVIDENCE` |
| `STATIC_OR_MANUAL_REQUIRED` | Static repository evidence and independent adjudication only | Named static checklist + exact blobs/records | Yes only when checklist and expected governed outcome qualify | Missing checklist/evidence → `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`; unresolved proof → `INSUFFICIENT_EVIDENCE` |
| `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` | **Execution prohibited** | This is a prerequisite-status gate, not an external/manual evidence request | No | Case remains a blocked **status**; no result and no endpoint observation |

A governed endpoint named `INSUFFICIENT_EVIDENCE` is not the same thing as the execution-result classification `INSUFFICIENT_EVIDENCE`. The audit matrix `Expected kind` column disambiguates endpoint cases from blocked/status/positive cases. If the preregistered endpoint is exactly `INSUFFICIENT_EVIDENCE` and a valid harness observes that endpoint with all other assertions satisfied, the **execution result is `PASS`**. The execution-result classification `INSUFFICIENT_EVIDENCE` is used when required evidence for adjudicating the case itself was supplied but cannot qualify.

### 6.2 Exact anti-false-green contract for governed endpoint `INSUFFICIENT_EVIDENCE`

For every case whose expected governed endpoint is exactly `INSUFFICIENT_EVIDENCE`, PASS requires a scientifically executable case and the **exact preregistered target reason** owned by Harness V7.

`target_reason` must equal the case-specific constant in `IE_TARGET_REASONS`:

| Case | Exact target reason |
|---|---|
| WDPC-443 | `IUDA shares prohibited effective control with candidate` |
| WDPC-458 | `required external completeness authority is present but independence is unproven` |
| WDPC-472 | `exact current admission-ledger lineage cannot be established` |
| WDPC-473 | `completeness result lacks a bound durable ledger record` |
| WDPC-474 | `exact current completeness-ledger lineage cannot be established` |
| WDPC-476 | `capability attestation relies only on deployment self-report` |
| WDPC-480 | `universe projection lacks a qualifying bound UniverseDerivationDecisionRecord` |
| WDPC-497 | `unadmitted direct sink writer prevents closed-world qualification` |
| WDPC-500 | `operational root is relabeled independent without control-domain separation` |
| WDPC-502 | `ordinary IUDA lacks qualifying governed predecessor lineage` |
| WDPC-504 | `material sink lacks unavoidable deny-by-default admission boundary` |

PASS additionally requires the case evidence bundle and preconditions to be valid, target-condition evidence present and observed, no missing case-execution evidence, candidate-emitted `INSUFFICIENT_EVIDENCE`, a lowercase hexadecimal SHA-256 trigger digest, exact target reason, and zero unauthorized authority-effect delta.

Absent required external evidence yields `NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED`; evidence present but insufficient to establish the target condition yields execution-class `INSUFFICIENT_EVIDENCE`, not PASS. Missing evidence therefore cannot masquerade as the expected governed endpoint.

### 6.3 Run binding and positive-control classification

`run_id` is canonical: `<case-id>:<16..64 lowercase hex characters>`, and its case prefix must equal `CaseRunBinding.case_id`.

Each target module is bound twice: its Git object ID and SHA-256 content digest. The two tuples must be non-empty and cardinality-equal.

Positive controls use `PositiveAssertionObservation{assertion_id,satisfied,evidence_digests}` and `classify_positive`; PASS requires a named assertion, `satisfied=true`, at least one evidence digest, and all evidence digests valid lowercase SHA-256.

## 7. Exact fallback/precedence narrowing

The V8 fixtures remove disjunctive ambiguity rather than accepting arbitrary OR outcomes:

| Case | Exact V8 branch chosen | Exact required outcome |
|---|---|---|
| WDPC-457 | No stricter source-specific invalid endpoint is configured; historical record is separately asserted unchanged | primary endpoint `AUTHORITY_EVIDENCE_SOURCE_INVALID`; conjunctive invariant `HISTORICAL_RESULT_UNCHANGED` |
| WDPC-472 | Competing admission lineage is supplied but exact current lineage cannot be established | `INSUFFICIENT_EVIDENCE` |
| WDPC-474 | Competing completeness lineage is supplied but exact current lineage cannot be established | `INSUFFICIENT_EVIDENCE` |
| WDPC-479 | All stricter admission/completeness predicates were valid at decision; only bound state changes before apply | `ROOT_KERNEL_DECISION_STALE` |
| WDPC-483 | New admitted instance deterministically makes old universe-completeness record stale | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` |
| WDPC-497 | Direct unadmitted writer exists and this fixture intentionally does not invoke a separate stricter inherited fence endpoint | `INSUFFICIENT_EVIDENCE` |
| WDPC-498 | All stricter predicates valid at decision; only IAM/perimeter drift occurs before apply | `ROOT_KERNEL_DECISION_STALE` |
| WDPC-499 | Circularity is explicitly in genesis configuration | `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE` |
| WDPC-502 | Ordinary IUDA has absent/untraceable qualifying lineage branch | `INSUFFICIENT_EVIDENCE` |
| WDPC-503 | Attempt is an in-place mutation of the active genesis-bound bootstrap authority powers in unchanged generation | `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED` |

Any fixture that accidentally triggers a different earlier predicate is `FAIL_FIXTURE_DEFECT`; the harness may not accept an alternative endpoint merely because it is stricter.

## 8. Authority-effect observation profiles

- **O-AGG:** Snapshot required keys, per-key durable rows, reconciliation outcome, authority_transition_state and external/effect counter immediately before injection and after terminal observation. Negative PASS requires effect delta 0 and transition not SUCCESS.
- **O-CONTROL:** Snapshot source/relationship/capability qualification, downstream guarded-decision invocation count and material effect count. Negative PASS requires exact endpoint and zero downstream/material effect delta.
- **O-ENDPOINT:** Snapshot table activation digest/state, dispatch counter and material effect counter. Negative PASS requires table not active/dispatched and effect delta 0.
- **O-NORMATIVE:** Snapshot catalog qualification digest/state, control activation set, decision-dispatch count and effect count. Negative PASS requires no authority derived from omitted/weakened prose/control.
- **O-PROOF:** Snapshot proof manifest/applicability state, consuming authority-decision count and effect count. Negative PASS requires proof not PASS and zero consuming authority effect.
- **O-UNIVERSE:** Snapshot admitted universe/path/graph digests, guarded writer invocation count, sink effect count. Negative PASS requires no unknown/unqualified path reaches sink.
- **O-MIGRATION:** Snapshot predecessor/successor inventory digests, read-acceptance flags, successor activation state and effect count. Negative PASS requires rejected read/activation and zero effect delta.
- **O-APPLICATION:** Snapshot kernel decision state/digest, application-record count/digests, witness/ledger digests and sink effect count. Negative PASS requires no valid applied state and zero unauthorized effect delta.
- **O-APPLY:** Snapshot decision/admission/completeness/perimeter digests, worker invocation count, application-record count and effect count immediately before final apply and after result.
- **O-HISTORY:** Snapshot immutable historical decision digest/result before and after later evidence plus new-evaluation endpoint/effect count. Historical digest/result must not be upgraded.
- **O-BOOTSTRAP:** Snapshot genesis/bootstrap-set digest, completeness current-record count, generation activation state and material effect count. Negative PASS requires no bootstrap/completeness activation/effect.
- **O-PERIMETER:** Snapshot sink identity, admitted writer set, enforcement configuration digest, credential/principal inventory and observed material write/effect counter. Negative PASS requires no qualifying closed-world authority path.

## 9. External/manual evidence profiles and custody

Every external/manual artifact is represented by a manifest entry containing `artifact_id`, exact case IDs, source system/domain, source identity, retrieval/collection method, collector identity, captured-at time/sequence, SHA-256, authentication/signature/attestation reference where applicable, governing currentness evidence, transfer/custody steps, redaction class, and storage/reference identity. Missing load-bearing custody/currentness/authentication fields means the evidence cannot qualify.

Candidate/self-produced assertions cannot establish independence, IAM closure, witness independence, bootstrap ceremony, control-plane completeness, or deployment measurement.

- **E-CONTROL-INDEPENDENCE:** Authoritative control-domain exports/records for candidate and IUDA; admin/deployment/credential/recovery/root relationships; signed or authenticated source identity where available; independent derivation worksheet. Independence passes only if prohibited shared effective-control paths are absent; silence is insufficient.
- **E-WITNESS:** Witness identity/key or authenticated identity, control-domain ownership/admin/recovery evidence, ledger attestation digest/signature, ledger-operator control domain, currentness/revocation evidence. At least one required witness must be outside prohibited root/operator control.
- **E-WITNESS-LINEAGE:** All E-WITNESS fields plus exact signed/current ledger lineage digest and predecessor/sequence per witness. Incompatible lineages produce RECONCILIATION_CONFLICT; local preference is forbidden.
- **E-IUDA:** IUDA identity, qualifying authority/lineage, control-domain evidence, exact source contracts, UniverseDerivationDecisionRecord binding subject/sources/algorithm/projection/currentness, independent source artifacts and digests.
- **E-CAPABILITY-ATTESTATION:** Independent attestor identity/control domain, measured executable/API/config/deployment digests, measurement method, source provenance/currentness and candidate self-report separation evidence.
- **E-CONTROL-PLANE:** Authoritative or independently collected inventory covering application/provider/account/org-root/HSM/KMS/CI-CD/configuration/credential/recovery/emergency control planes; exact principals, roles/permissions, source identity/digest/currentness and relationship responses.
- **E-LEDGER-LINEAGE:** Current and competing ledger heads, predecessor/sequence/hash links, independent anchor/witness evidence, revocation/admission events and capture currentness. If exact current lineage cannot be established, result is INSUFFICIENT_EVIDENCE.
- **E-COMPLETENESS-LEDGER-LINEAGE:** Current and competing `CompletenessQualificationLedger` heads, predecessor/sequence/hash links, exact completeness subject/generation bindings, independent anchor/witness evidence, revocation/staleness/requalification events, and capture currentness. If exact current completeness-ledger lineage cannot be established, the governed outcome under WDPC-474 is `INSUFFICIENT_EVIDENCE`.
- **E-ADMISSION-COMPLETENESS:** Current AuthorityAdmissionLedger identity/digest, current witnessed CompletenessQualificationLedger identity/digest, independent IUDA derivation evidence, exact kernel decision bindings and apply-time revalidation evidence.
- **E-COMPOSITE-486:** E-SEMANTIC + E-CAPABILITY-ATTESTATION + E-IUDA + E-WITNESS, all bound to one governance generation/current decision surface.
- **E-SEMANTIC:** Exact predecessor artifact blob/clause digest, exact successor descriptor/blob/clause, predecessor status/lineage and completed equal-or-stronger worksheet signed/identified by an independent reviewer.
- **E-IAM-PERIMETER:** Exact sink/effect identity; exported IAM/ACL/capability policy/config digest; admitted guarded writers; direct/maintenance/emergency/recovery principals; denied classes; independently observed enforcement/negative-access evidence; configuration/credential currentness.
- **E-BOOTSTRAP-CONTROL:** Genesis member identities plus operational-root identities, admin/deployment/credential/recovery/control-domain evidence sufficient to test claimed separation; relabeling alone never counts.
- **E-STATIC-GOVERNANCE:** Exact active genesis record/root-kernel digest, governance_generation_id, pre-change bootstrap authority powers, proposed mutation diff, successor-generation/genesis presence or absence, active mutation/strength rules and reviewer-safe repository evidence.
- **E-BOOTSTRAP:** Exact GovernanceGenerationGenesisRecord, bootstrap authority identities/keys, ceremony transcript/evidence digest, participant identities/control domains, threshold/diversity, external source contracts, signatures/attestations where required, predecessor/migration identity and declared residual trust assumptions.

### 9.1 Per-case external/manual evidence mapping

| Case | Required evidence profile |
|---|---|
| WDPC-443 | `E-CONTROL-INDEPENDENCE` |
| WDPC-449 | `E-WITNESS` |
| WDPC-458 | `E-IUDA` |
| WDPC-460 | `E-WITNESS-LINEAGE` |
| WDPC-466 | `E-CAPABILITY-ATTESTATION` |
| WDPC-467 | `E-WITNESS` |
| WDPC-468 | `E-IUDA` |
| WDPC-469 | `E-SEMANTIC` |
| WDPC-472 | `E-LEDGER-LINEAGE` |
| WDPC-474 | `E-COMPLETENESS-LEDGER-LINEAGE` |
| WDPC-477 | `E-WITNESS` |
| WDPC-484 | `E-WITNESS-LINEAGE` |
| WDPC-485 | `E-ADMISSION-COMPLETENESS` |
| WDPC-486 | `E-COMPOSITE-486` |
| WDPC-489 | `E-CONTROL-PLANE` |
| WDPC-491 | `E-SEMANTIC` |
| WDPC-494 | `E-CONTROL-PLANE` |
| WDPC-495 | `E-SEMANTIC` |
| WDPC-497 | `E-IAM-PERIMETER` |
| WDPC-498 | `E-IAM-PERIMETER` |
| WDPC-500 | `E-BOOTSTRAP-CONTROL` |
| WDPC-503 | `E-STATIC-GOVERNANCE` |
| WDPC-504 | `E-IAM-PERIMETER` |
| WDPC-505 | `E-IAM-PERIMETER` |
| WDPC-506 | `E-BOOTSTRAP` |

## 10. Manual semantic equal-or-stronger rubric

For WDPC-491 and WDPC-495, compare the exact predecessor clause to the proposed V24 continuity descriptor/re-expression across every dimension below. Each dimension is `SAME`, `STRONGER`, `WEAKER`, or `INSUFFICIENT_EVIDENCE/NOT_COMPARABLE`:

1. trigger/applicability scope; 2. protected subject/object scope; 3. mandatory evidence set; 4. evidence identity/currentness/revocation rules; 5. reviewer/attestor/source independence; 6. threshold/quorum/diversity; 7. failure endpoint/fail-closed behavior; 8. exceptions/waivers/fallbacks; 9. lineage/history/non-retroactivity; 10. sink/apply-time enforcement; 11. recovery/emergency/migration behavior; 12. authority granted on success.

A continuity mapping qualifies only if every material dimension is SAME or STRONGER, no dimension is WEAKER, no load-bearing dimension is unresolved, exact artifact/clause digests are bound, and the independent reviewer is independent of the mapping author. WDPC-491 expects a deliberately WEAKER dimension and must block catalog continuity. WDPC-495 remains blocked until every inherited active control completes this rubric.

## 11. WDPC-503 static governance checklist

Before WDPC-503 may be adjudicated, bind: active governance_generation_id; exact genesis record/root-kernel digest; current BootstrapCompletenessAuthoritySet powers; proposed change diff; evidence that generation id is unchanged; evidence that no successor genesis/migration record authorizes the new powers; applicable root/meta-governance rule identity; repository/blob identities. The fixture changes genesis-bound bootstrap subject powers in place, so the required endpoint is exactly `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`.

## 12. Case audit matrix

`Expected kind` is normative: `GOVERNED_ENDPOINT` requires an exact implementation-emitted endpoint; `CONJUNCTIVE_ASSERTION` requires all named components; `POSITIVE_ASSERTION` is a bounded success property rather than necessarily an endpoint; `BLOCKED_STATUS` is a pre-execution state and produces no `GovernedEndpointObservation` or execution result.

| Case | Type | Expected kind | Exact expected value / required assertion | Class | Observation | Evidence | Implementation surface | Injection/positive condition | Status |
|---|---|---|---|---|---|---|---|---|---|
| WDPC-431 | NEG | `GOVERNED_ENDPOINT` | `AGGREGATION_DIMENSION_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-AGG` | `NONE` | `v24_aggregate_budget.py` | Remove exactly one mandatory independently-derived aggregation dimension while all other dimensions/records remain valid; assert no transition success/effect. | `NOT_EXECUTED` |
| WDPC-432 | NEG | `GOVERNED_ENDPOINT` | `EFFECTIVE_CONTROL_SOURCE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | Remove one mandatory source class for an admitted authority-bearing subject; keep relationships for remaining classes valid. | `NOT_EXECUTED` |
| WDPC-433 | NEG | `GOVERNED_ENDPOINT` | `ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE` | `REFERENCE_HARNESS` | `O-ENDPOINT` | `NONE` | `v24_endpoint_proof_compiler.py` | Omit exactly one active predicate from the compiled mapping while every remaining mapping stays uniquely ordered; do not inject an ordering ambiguity. Table activation/dispatch must remain disabled. | `NOT_EXECUTED` |
| WDPC-434 | NEG | `GOVERNED_ENDPOINT` | `AGGREGATE_BUDGET_OUTCOME_UNKNOWN` | `REFERENCE_HARNESS` | `O-AGG` | `NONE` | `v24_aggregate_budget.py` | One transaction spans A/B/C; inject partial durable visibility after acknowledgement loss so exact outcome remains unresolved and authority transition cannot succeed. | `NOT_EXECUTED` |
| WDPC-435 | NEG | `GOVERNED_ENDPOINT` | `GENERATION_MIGRATION_INVENTORY_INCOMPLETE` | `REFERENCE_HARNESS` | `O-MIGRATION` | `NONE` | `v24_generation_migration.py` | Independent predecessor derivation contains object O2 absent from migration inventory; successor activation remains blocked. | `NOT_EXECUTED` |
| WDPC-436 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_CAPABILITY_INVENTORY_ENTRY_STALE` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | After a valid attestation, change measured deployment/configuration identity without re-attestation; downstream authority use remains zero. | `NOT_EXECUTED` |
| WDPC-437 | NEG | `GOVERNED_ENDPOINT` | `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | Delete both relationship and bound negative-response evidence for one mandatory subject/source tuple. | `NOT_EXECUTED` |
| WDPC-438 | NEG | `GOVERNED_ENDPOINT` | `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED` | `REFERENCE_HARNESS` | `O-MIGRATION` | `NONE` | `v24_generation_migration.py` | Successor reads predecessor-generation cached object without qualifying successor disposition/revalidation. | `NOT_EXECUTED` |
| WDPC-439 | NEG | `GOVERNED_ENDPOINT` | `AGGREGATION_DIMENSION_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-AGG` | `NONE` | `v24_aggregate_budget.py` | Mark aggregation window expired while authority effect remains effective and aggregation obligation is cleared without cessation proof. | `NOT_EXECUTED` |
| WDPC-440 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID` | `REFERENCE_HARNESS` | `O-APPLICATION` | `NONE` | `v24_admission_application_witness.py` | Mark decision APPLIED with zero matching current AuthorityApplicationRecord. | `NOT_EXECUTED` |
| WDPC-441 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py + v24_apply_guard.py` | Introduce a functionally authority-capable writer/path absent from current admission records; sink/effect invocation remains zero. | `NOT_EXECUTED` |
| WDPC-442 | NEG | `GOVERNED_ENDPOINT` | `META_GOVERNANCE_SELF_ACTIVATION_REJECTED` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Make proposed completeness authority use descendant completeness machinery to approve its own activation. | `NOT_EXECUTED` |
| WDPC-443 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `HYBRID_EXTERNAL_REQUIRED` | `O-CONTROL` | `E-CONTROL-INDEPENDENCE` | `v24_effective_control.py` | Nominally distinct IUDA shares prohibited effective control with candidate; reference mechanism plus real control-domain evidence required. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-444 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Supply two qualifying projections that materially disagree on one admitted authority-bearing path/entity with no governed conservative resolution. | `NOT_EXECUTED` |
| WDPC-445 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-APPLY` | `NONE` | `v24_apply_guard.py` | Add an admitted universe member after completeness qualification while reusing the old completeness record; no apply. | `NOT_EXECUTED` |
| WDPC-446 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `REFERENCE_HARNESS` | `O-NORMATIVE` | `NONE` | `normative_control_catalog.py` | Exact authoritative artifact contains required material clause/locator omitted from control catalog. | `NOT_EXECUTED` |
| WDPC-447 | NEG | `GOVERNED_ENDPOINT` | `PROOF_VIEW_APPLICABILITY_INCOMPLETE` | `REFERENCE_HARNESS` | `O-PROOF` | `NONE` | `v24_endpoint_proof_compiler.py` | Decision-path applicability requires field F but producer omits/self-selects NOT_APPLICABLE. | `NOT_EXECUTED` |
| WDPC-448 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_DEPENDENCY_GRAPH_INCOMPLETE` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Remove one independently derived material edge so visible graph becomes deceptively acyclic; acyclicity cannot qualify. | `NOT_EXECUTED` |
| WDPC-449 | NEG | `GOVERNED_ENDPOINT` | `WITNESS_INDEPENDENCE_INSUFFICIENT` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-WITNESS` | `v24_admission_application_witness.py` | All required witnesses resolve to root/operator-controlled domains under real effective-control evidence. | `NOT_EXECUTED` |
| WDPC-450 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Introduce genuinely new semantic authority class in same generation and attempt ordinary-instance admission. | `NOT_EXECUTED` |
| WDPC-451 | NEG | `GOVERNED_ENDPOINT` | `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | Mandatory registered source returns no current response and no bound no-relationship evidence for an in-scope subject. | `NOT_EXECUTED` |
| WDPC-452 | NEG | `GOVERNED_ENDPOINT` | `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | Remove one root-threshold-capable controlling set from closure while source/relationship rows otherwise remain complete. | `NOT_EXECUTED` |
| WDPC-453 | NEG | `GOVERNED_ENDPOINT` | `ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE` | `REFERENCE_HARNESS` | `O-ENDPOINT` | `NONE` | `v24_endpoint_proof_compiler.py` | Remove exactly the admitted stricter subsystem predicate from the compiled table while the generic fallback remains present and otherwise correctly ordered. | `NOT_EXECUTED` |
| WDPC-454 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `REFERENCE_HARNESS` | `O-NORMATIVE` | `NONE` | `normative_control_catalog.py` | Uncatalogued normative-looking prose is cited as authorization; catalog qualification/authority dispatch stays blocked. | `NOT_EXECUTED` |
| WDPC-455 | NEG | `GOVERNED_ENDPOINT` | `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED` | `REFERENCE_HARNESS` | `O-MIGRATION` | `NONE` | `v24_generation_migration.py` | Discover predecessor-tagged object only at successor shared-store read; object was absent from predecessor inventory and has no qualifying disposition. | `NOT_EXECUTED` |
| WDPC-456 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID` | `REFERENCE_HARNESS` | `O-APPLICATION` | `NONE` | `v24_admission_application_witness.py` | ApplicationRecord sink-set digest/identity differs from exact decision mandatory sink set. | `NOT_EXECUTED` |
| WDPC-457 | NEG | `CONJUNCTIVE_ASSERTION` | `AUTHORITY_EVIDENCE_SOURCE_INVALID` **AND invariant** `HISTORICAL_RESULT_UNCHANGED` | `REFERENCE_HARNESS` | `O-HISTORY` | `NONE` | `v24_generation_migration.py + source qualification guard` | Use `ConjunctiveAssertionObservation`: historical digest/result must remain unchanged and new current evaluation must emit exactly `AUTHORITY_EVIDENCE_SOURCE_INVALID`; both halves are mandatory. | `NOT_EXECUTED` |
| WDPC-458 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `EXTERNAL_MANUAL_REQUIRED` | `O-BOOTSTRAP` | `E-IUDA` | `completeness/IUDA evidence` | The required external completeness authority is present, but qualifying control-domain evidence cannot prove its independence; no root-only downgrade is permitted. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-459 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Projection source_kind is exclusively candidate-self-derived; no independent source evidence. | `NOT_EXECUTED` |
| WDPC-460 | NEG | `GOVERNED_ENDPOINT` | `RECONCILIATION_CONFLICT` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-WITNESS-LINEAGE` | `witness reconciliation` | Two independently qualified witness domains bind incompatible current ledger lineages; local selection is prohibited. | `NOT_EXECUTED` |
| WDPC-461 | POS | `POSITIVE_ASSERTION` | `AGGREGATION_COMPLETENESS_QUALIFIES` | `REFERENCE_MECHANISM_ONLY` | `O-AGG` | `NONE` | `v24_aggregate_budget.py` | All independently derived dimensions present, active effects remain charged, no false completeness failure. | `NOT_EXECUTED` |
| WDPC-462 | POS | `POSITIVE_ASSERTION` | `EFFECTIVE_CONTROL_COMPLETENESS_QUALIFIES` | `REFERENCE_MECHANISM_ONLY` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | All source classes/mandatory tuples answered and closure includes root-threshold sets. | `NOT_EXECUTED` |
| WDPC-463 | POS | `POSITIVE_ASSERTION` | `ENDPOINT_PRECEDENCE_TABLE_ACTIVATABLE` | `REFERENCE_MECHANISM_ONLY` | `O-ENDPOINT` | `NONE` | `v24_endpoint_proof_compiler.py` | Every active predicate maps exactly once with total within-phase order and explicit stricter subsystem mappings. | `NOT_EXECUTED` |
| WDPC-464 | POS | `POSITIVE_ASSERTION` | `AGGREGATE_TRANSACTION_COMPLETE_IDEMPOTENT` | `REFERENCE_HARNESS` | `O-AGG` | `NONE` | `v24_aggregate_budget.py` | One canonical transaction identity spans all required keys and replay preserves committed identity. | `NOT_EXECUTED` |
| WDPC-465 | POS | `POSITIVE_ASSERTION` | `SUCCESSOR_MIGRATION_ACTIVATABLE` | `REFERENCE_MECHANISM_ONLY` | `O-MIGRATION` | `NONE` | `v24_generation_migration.py` | Independent predecessor set equals inventory; every object tagged/dispositioned; reads fenced/revalidated. | `NOT_EXECUTED` |
| WDPC-466 | POS | `POSITIVE_ASSERTION` | `CAPABILITY_REATTESTATION_QUALIFIES` | `HYBRID_EXTERNAL_REQUIRED` | `O-CONTROL` | `E-CAPABILITY-ATTESTATION` | `v24_effective_control.py` | Drift first blocks; then an independently controlled measurement attests exact new deployment/config state before reactivation. | `NOT_EXECUTED` |
| WDPC-467 | POS | `POSITIVE_ASSERTION` | `WITNESSED_LEDGER_INTEGRITY_QUALIFIES` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-WITNESS` | `v24_admission_application_witness.py` | Required quorum includes at least one independently controlled domain and all current witnesses bind one lineage. | `NOT_EXECUTED` |
| WDPC-468 | POS | `POSITIVE_ASSERTION` | `COMPLETENESS_RECORD_CURRENT` | `EXTERNAL_MANUAL_REQUIRED` | `O-BOOTSTRAP` | `E-IUDA` | `completeness/IUDA evidence` | Required independent IUDAs derive matching/conservatively compatible universes from independent sources. | `NOT_EXECUTED` |
| WDPC-469 | POS | `BLOCKED_STATUS` | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` | `NONE_WHILE_BLOCKED` | `E-SEMANTIC` | `normative catalog + proof compiler` | Pre-execution gate only. No case body or `GovernedEndpointObservation` until real V5–V23 continuity and V24 semantic mappings are qualified. | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` |
| WDPC-470 | POS | `POSITIVE_ASSERTION` | `ATOMIC_APPLICATION_LINKAGE_QUALIFIES` | `REFERENCE_HARNESS` | `O-APPLICATION` | `NONE` | `v24_admission_application_witness.py + V24ExecutionGateway` | Exact decision, sink apply and application record bind one transition/post-state with matching sink set. | `NOT_EXECUTED` |
| WDPC-471 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-APPLICATION` | `NONE` | `v24_admission_application_witness.py + v24_apply_guard.py` | One authority-affecting decision input lacks a current exact admission record. | `NOT_EXECUTED` |
| WDPC-472 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-LEDGER-LINEAGE` | `AuthorityAdmissionLedger lineage` | Fixture is deliberately constructed so an earlier/sibling admission lineage is presented but exact current lineage cannot be established; therefore only INSUFFICIENT_EVIDENCE is admissible. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-473 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Completeness result exists only in memory/local cache and has no bound durable ledger record. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-474 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `HYBRID_EXTERNAL_REQUIRED` | `O-BOOTSTRAP` | `E-COMPLETENESS-LEDGER-LINEAGE` | `CompletenessQualificationLedger lineage` | Fixture deliberately prevents establishment of exact current completeness-ledger lineage; earlier/sibling record cannot qualify. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-475 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Nominally distinct IUDAs use one common omission-sensitive source/control path. | `NOT_EXECUTED` |
| WDPC-476 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `REFERENCE_HARNESS` | `O-CONTROL` | `NONE` | `v24_effective_control.py` | Capability attestation approval exists but all measurement evidence originates from deployment subsystem being attested. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-477 | NEG | `GOVERNED_ENDPOINT` | `WITNESS_INDEPENDENCE_INSUFFICIENT` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-WITNESS` | `v24_admission_application_witness.py` | All witnesses are inside same root/operator effective-control domain. | `NOT_EXECUTED` |
| WDPC-478 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py + v24_apply_guard.py` | Runtime observes unadmitted material authority path but discovery event is suppressed/ignored; normal authority processing must not continue. | `NOT_EXECUTED` |
| WDPC-479 | NEG | `GOVERNED_ENDPOINT` | `ROOT_KERNEL_DECISION_STALE` | `REFERENCE_HARNESS` | `O-APPLY` | `NONE` | `v24_apply_guard.py + V24ExecutionGateway` | Fixture holds all stricter admission/completeness predicates valid at decision time; only bound completeness/admission digest changes after decision and before effect. | `NOT_EXECUTED` |
| WDPC-480 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Projection lacks qualifying bound UniverseDerivationDecisionRecord for subject/sources/algorithm/identity/currentness. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-481 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `REFERENCE_HARNESS` | `O-NORMATIVE` | `NONE` | `normative_control_catalog.py` | Inherited active clause is designated authoritative but has no exact admitted legacy descriptor mapping. | `NOT_EXECUTED` |
| WDPC-482 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `REFERENCE_HARNESS` | `O-NORMATIVE` | `NONE` | `normative_control_catalog.py` | Descriptor keeps the correct artifact blob, locator, and predecessor lineage but binds one deliberately wrong clause digest. | `NOT_EXECUTED` |
| WDPC-483 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-APPLY` | `NONE` | `v24_apply_guard.py + completeness state` | New instance fits existing semantic class and is admitted, but dependent completeness record is deterministically stale and not requalified. | `NOT_EXECUTED` |
| WDPC-484 | NEG | `GOVERNED_ENDPOINT` | `RECONCILIATION_CONFLICT` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-WITNESS-LINEAGE` | `witness reconciliation` | Independent witnesses conflict and root/operator attempts local override. | `NOT_EXECUTED` |
| WDPC-485 | POS | `POSITIVE_ASSERTION` | `ADMISSION_COMPLETENESS_APPLY_QUALIFIES` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLY` | `E-ADMISSION-COMPLETENESS` | `v24_apply_guard.py + admission/application/witness` | Current exact admissions plus independently-derived witnessed completeness are bound into decision and revalidated at apply. | `NOT_EXECUTED` |
| WDPC-486 | POS | `POSITIVE_ASSERTION` | `NORMATIVE_CAPABILITY_COMPLETENESS_WITNESS_QUALIFIES` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLICATION` | `E-COMPOSITE-486` | `catalog + capability + IUDA + witness` | Exact descriptors, independent capability measurement, signed universe derivation and external witness quorum are all current and mutually consistent. | `NOT_EXECUTED` |
| WDPC-487 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Novel service is nominally labeled non-authority but functionally mutates/qualifies an authority sink. | `NOT_EXECUTED` |
| WDPC-488 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_ADMISSION_REQUIRED` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Independent effect-path projection contains a direct writer missing from admission/capability/sink/guard state. | `NOT_EXECUTED` |
| WDPC-489 | NEG | `GOVERNED_ENDPOINT` | `EFFECTIVE_CONTROL_SOURCE_COMPLETENESS_INVALID` | `HYBRID_EXTERNAL_REQUIRED` | `O-CONTROL` | `E-CONTROL-PLANE` | `v24_effective_control.py` | Real provider/account/organization-root administrative path is omitted from source/control-plane registry. | `NOT_EXECUTED` |
| WDPC-490 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `REFERENCE_HARNESS` | `O-NORMATIVE` | `NONE` | `legacy continuity + normative catalog` | Remove one inherited active WDPC control from continuity disposition/catalog. | `NOT_EXECUTED` |
| WDPC-491 | NEG | `GOVERNED_ENDPOINT` | `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` | `MANUAL_SEMANTIC_REQUIRED` | `O-NORMATIVE` | `E-SEMANTIC` | `legacy continuity semantic comparison` | A successor descriptor claims continuity while weakening at least one rubric dimension; independent semantic assessment must mark WEAKER. | `NOT_EXECUTED` |
| WDPC-492 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Introduce new omission-sensitive registry/derived set but omit it from COMPLETENESS_REQUIRED_SUBJECT classification. | `NOT_EXECUTED` |
| WDPC-493 | POS | `POSITIVE_ASSERTION` | `FUNCTIONAL_CATCHALL_REQUALIFICATION_ACCEPTS` | `REFERENCE_MECHANISM_ONLY` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | Novel authority-capable component is caught functionally, admitted under generic rule, and dependent completeness is requalified. | `NOT_EXECUTED` |
| WDPC-494 | POS | `POSITIVE_ASSERTION` | `CONTROL_PLANE_SOURCE_COMPLETENESS_QUALIFIES` | `EXTERNAL_MANUAL_REQUIRED` | `O-CONTROL` | `E-CONTROL-PLANE` | `real control-plane conformance` | Independent evidence covers provider/cloud-root/HSM/KMS/CI-CD/config/credential/recovery/emergency domains with current responses. | `NOT_EXECUTED` |
| WDPC-495 | POS | `BLOCKED_STATUS` | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` | `NONE_WHILE_BLOCKED` | `E-SEMANTIC` | `legacy continuity + normative catalog` | Pre-execution gate only. No case body or `GovernedEndpointObservation` until every active predecessor control has exact disposition and equal-or-stronger semantic verification. | `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` |
| WDPC-496 | POS | `POSITIVE_ASSERTION` | `UNNAMED_COMPLETENESS_SUBJECT_ACCEPTS_AFTER_QUALIFICATION` | `REFERENCE_MECHANISM_ONLY` | `O-UNIVERSE` | `NONE` | `v24_authority_universe.py` | New omission-sensitive derived set is automatically classified/admitted/projected/qualified without named-list change. | `NOT_EXECUTED` |
| WDPC-497 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `EXTERNAL_MANUAL_REQUIRED` | `O-PERIMETER` | `E-IAM-PERIMETER` | `real sink IAM/perimeter` | Fixture/evidence proves an unadmitted principal retains direct sink capability and deliberately does not invoke a separate stricter inherited sink-fence endpoint; closed-world qualification remains IE. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-498 | NEG | `GOVERNED_ENDPOINT` | `ROOT_KERNEL_DECISION_STALE` | `HYBRID_EXTERNAL_REQUIRED` | `O-APPLY` | `E-IAM-PERIMETER` | `v24_apply_guard.py + real IAM drift` | All stricter predicates qualify at decision; after decision one IAM/credential principal is added, making bound perimeter record stale before apply. | `NOT_EXECUTED` |
| WDPC-499 | NEG | `GOVERNED_ENDPOINT` | `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Place circularity in genesis: initial IUDA qualification depends on descendant V24 completeness record requiring same IUDA. | `NOT_EXECUTED` |
| WDPC-500 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `HYBRID_EXTERNAL_REQUIRED` | `O-BOOTSTRAP` | `E-BOOTSTRAP-CONTROL` | `bootstrap evidence` | Operational root principal is merely relabeled as external independent bootstrap completeness authority; real control evidence shows same domain. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-501 | NEG | `GOVERNED_ENDPOINT` | `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Bootstrap source contract for authority universe contains candidate-self source only. | `NOT_EXECUTED` |
| WDPC-502 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `REFERENCE_HARNESS` | `O-BOOTSTRAP` | `NONE` | `v24_completeness_bootstrap.py` | Ordinary IUDA has null/untraceable parent and no qualifying governed predecessor; fixture selects absent-lineage branch. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-503 | NEG | `GOVERNED_ENDPOINT` | `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED` | `STATIC_OR_MANUAL_REQUIRED` | `O-BOOTSTRAP` | `E-STATIC-GOVERNANCE` | `root/meta-governance + bootstrap genesis` | Fixture is specifically an in-place mutation of genesis-bound BootstrapCompletenessAuthoritySet subject powers inside unchanged governance_generation_id, with no successor genesis record. | `NOT_EXECUTED` |
| WDPC-504 | NEG | `GOVERNED_ENDPOINT` | `INSUFFICIENT_EVIDENCE` | `EXTERNAL_MANUAL_REQUIRED` | `O-PERIMETER` | `E-IAM-PERIMETER` | `real sink enforcement` | Material sink lacks technically/equivalently unavoidable deny-by-default boundary for unadmitted writers. | `NOT_EXECUTED` — IE endpoint anti-false-green condition required. |
| WDPC-505 | POS | `POSITIVE_ASSERTION` | `ADMISSION_PERIMETER_QUALIFIES` | `EXTERNAL_MANUAL_REQUIRED` | `O-PERIMETER` | `E-IAM-PERIMETER` | `real sink IAM/perimeter` | Independent evidence proves sink accepts material writes only from admitted guarded writer set and current apply revalidates perimeter/admissions. | `NOT_EXECUTED` |
| WDPC-506 | POS | `POSITIVE_ASSERTION` | `BOOTSTRAP_RESIDUAL_TRUST_BOUNDARY_QUALIFIES` | `EXTERNAL_MANUAL_REQUIRED` | `O-BOOTSTRAP` | `E-BOOTSTRAP` | `bootstrap ceremony` | Genesis record + out-of-band ceremony bind external bootstrap authorities/source contracts without descendant self-proof; later rotations use active rules. | `NOT_EXECUTED` |

## 13. Clustering, locks, and serialization

- Cluster A Normative/endpoint/proof: 433,446,447,453,454,463,469,481,482,490,491,495.
- Cluster B Authority universe/effect paths: 441,444,448,450,459,478,480,487,488,492,493,496.
- Cluster C Effective control/capability: 432,436,437,443,451,452,458,462,466,475,476,486,489,494.
- Cluster D Admission/application/witness: 440,449,456,460,467,470,471,472,477,484,485.
- Cluster E Aggregation: 431,434,439,461,464.
- Cluster F Generation/migration/history: 435,438,455,457,465.
- Cluster G Apply/perimeter: 445,479,483,497,498,504,505.
- Cluster H Completeness/bootstrap/meta-governance: 442,468,473,474,499,500,501,502,503,506.

Negative cases run before positive controls within the same mechanism. Multi-key/reconciliation/fork cases are serial. All cases using the same witness lineage, ledger lineage, IAM/perimeter evidence bundle, IUDA evidence bundle, semantic-review worksheet, or bootstrap ceremony obtain an exclusive evidence lock and may not run in parallel across clusters. External evidence collection itself is serialized per source snapshot; one snapshot digest may be reused only when case scope/currentness is identical and explicitly listed in the evidence manifest.

## 14. Inherited regression boundary

WDPC-01…430 remain historically preserved. Green I1–I10 construction tests are not substitutes. After the V24-specific plan is independently approved and V24 load-bearing failures are adjudicated, execute the affected inherited regression subset; then execute the full inherited set where the frozen V24 design/review requires it. Earlier RED/PASS/history is append-only. EXP-ECC-6/7 remain deferred.

## 15. Required clean independent-review output

A. `SELF_CONTAINED_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_PACKET_CONTENT`  
B. Overall disposition: `READY_FOR_EXECUTION | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`  
C. Critical findings  
D. High / Medium / Low findings  
E. Per-case audit table with `ADEQUATE | NEEDS_NARROWING | AMBIGUOUS_ASSERTION | FALSE_GREEN_RISK | INSUFFICIENT_DETAIL`  
F. Fixture/data-model audit  
G. Clustering/parallelism audit  
H. Exact-endpoint + no-authority-effect audit  
I. External/evidence and custody audit  
J. Environment/clock/dependency audit  
K. Semantic-rubric/static-governance audit  
L. Missing cases/attributes  
M. End exactly `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

Do not add a reviewer-type declaration. Reviewer type does not decide admissibility.

## 16. Execution gate

No WDPC-431…506 case is authorized by this plan.

Execution may begin only after **both** gates succeed:

1. **Independent review gate:** the exact V8 packet receives `SELF_CONTAINED_BINDING = CONSISTENT` and `READY_FOR_EXECUTION` from an admissible clean independent review. The reviewer may be human or AI; the review must be manually user-initiated, clean-context, exact-packet-bound, and not dispatched through an automated reviewer API.
2. **Governed repository adjudication gate:** after that review, the repository-connected adjudicator verifies the exact V8 packet/hash, detached V8 review-binding blob, harness blob, V24 design commit/tree, I10 implementation commit/tree, and frozen falsification source blobs, then confirms that the review corresponds to that exact V8 artifact.

If either gate fails, execution remains blocked. If any semantic plan byte, harness-contract byte, case expected outcome, execution class, observation profile, evidence profile, or fixture branch changes afterward, the review does not carry to the successor.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Appendix A — Embedded V8 harness contract V7

The following is the exact UTF-8 harness-contract source represented by declared Git blob `189d050831166868397e1ba063da57fa77f2dd42`. It is embedded so the independent reviewer can inspect plan/harness consistency without repository access.

```python
"""WDPC V24 I11 falsification harness contract V7.

Schema/invariant definitions only. Importing this module executes no WDPC case.
Reviewer type is not an admissibility gate; automated reviewer API dispatch remains prohibited.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import hashlib
import json
import re

HARNESS_ID = "WDPC-V24-I11-HARNESS"
HARNESS_VERSION = "1.6.0-PLAN-REVIEW"
FROZEN_V24_DESIGN_SHA = "db9e4b349fd26e128f4486878a4af64929000a7c"
FROZEN_I10_IMPLEMENTATION_SHA = "9836dc3ff233cca582f485434fc1c6494cf7eb05"
FROZEN_I10_TREE = "d68cbccdceebad88715c8b37ddfcd524fc16ce8a"
GOVERNANCE_GENERATION = "V24"
PYTHON_RUNTIME_FAMILY = "3.12"
PYTHONHASHSEED = "0"
TIMEZONE = "UTC"
FIXTURE_RANDOM_SEED = 24011
REVIEWER_API_CALLS = "PROHIBITED"
REVIEW_MODE = "USER_INITIATED_CLEAN_INDEPENDENT_REVIEW"
REFERENCE_NETWORK_POLICY = "DENY"

RESULT_STATES = {
    "PASS",
    "FAIL_CODE_DEFECT",
    "FAIL_HARNESS_DEFECT",
    "FAIL_FIXTURE_DEFECT",
    "INSUFFICIENT_EVIDENCE",
    "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
    "BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE",
}
CASE_STATUSES = {
    "NOT_EXECUTED",
    "EXECUTABLE",
    "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION",
    "RUNNING",
    "EXECUTED",
}
EXECUTION_CLASSES = {
    "REFERENCE_HARNESS",
    "REFERENCE_MECHANISM_ONLY",
    "HYBRID_EXTERNAL_REQUIRED",
    "EXTERNAL_MANUAL_REQUIRED",
    "MANUAL_SEMANTIC_REQUIRED",
    "STATIC_OR_MANUAL_REQUIRED",
    "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION",
}
CASE_IDS = tuple(f"WDPC-{i}" for i in range(431, 507))
BLOCKED_CASES = {"WDPC-469", "WDPC-495"}

IE_TARGET_REASONS = {
    "WDPC-443": "IUDA shares prohibited effective control with candidate",
    "WDPC-458": "required external completeness authority is present but independence is unproven",
    "WDPC-472": "exact current admission-ledger lineage cannot be established",
    "WDPC-473": "completeness result lacks a bound durable ledger record",
    "WDPC-474": "exact current completeness-ledger lineage cannot be established",
    "WDPC-476": "capability attestation relies only on deployment self-report",
    "WDPC-480": "universe projection lacks a qualifying bound UniverseDerivationDecisionRecord",
    "WDPC-497": "unadmitted direct sink writer prevents closed-world qualification",
    "WDPC-500": "operational root is relabeled independent without control-domain separation",
    "WDPC-502": "ordinary IUDA lacks qualifying governed predecessor lineage",
    "WDPC-504": "material sink lacks unavoidable deny-by-default admission boundary",
}
IE_EXPECTED_CASES = frozenset(IE_TARGET_REASONS)

REQUIRED_CONJUNCTIVE_INVARIANTS = {
    "WDPC-457": ("HISTORICAL_RESULT_UNCHANGED",),
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")
GIT_OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
PYTHON_312_PATCH = re.compile(r"^3\.12\.\d+$")
RUN_ID = re.compile(r"^WDPC-\d{3}:[0-9a-f]{16,64}$")


def digest(v: Any) -> str:
    return hashlib.sha256(
        json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def is_sha256_hex(value: str) -> bool:
    return bool(HEX64.fullmatch(value))


def is_git_oid(value: str) -> bool:
    return bool(GIT_OID.fullmatch(value))


def expected_stdlib_fallback_digest(exact_python_version: str) -> str:
    literal = (
        "PIP_UNAVAILABLE|STDLIB_ONLY_HARNESS|PYTHON="
        + exact_python_version
    )
    return hashlib.sha256(literal.encode()).hexdigest()


@dataclass(frozen=True)
class ExecutionClassPolicy:
    execution_class: str
    synthetic_execution_permitted: bool
    external_or_manual_evidence_required: bool
    operational_pass_permitted_without_external_evidence: bool
    default_missing_evidence_result: str | None


EXECUTION_CLASS_POLICY = {
    "REFERENCE_HARNESS": ExecutionClassPolicy(
        "REFERENCE_HARNESS", True, False, True, None
    ),
    "REFERENCE_MECHANISM_ONLY": ExecutionClassPolicy(
        "REFERENCE_MECHANISM_ONLY", True, False, False, None
    ),
    "HYBRID_EXTERNAL_REQUIRED": ExecutionClassPolicy(
        "HYBRID_EXTERNAL_REQUIRED",
        True,
        True,
        False,
        "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
    ),
    "EXTERNAL_MANUAL_REQUIRED": ExecutionClassPolicy(
        "EXTERNAL_MANUAL_REQUIRED",
        False,
        True,
        False,
        "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
    ),
    "MANUAL_SEMANTIC_REQUIRED": ExecutionClassPolicy(
        "MANUAL_SEMANTIC_REQUIRED",
        False,
        True,
        False,
        "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
    ),
    "STATIC_OR_MANUAL_REQUIRED": ExecutionClassPolicy(
        "STATIC_OR_MANUAL_REQUIRED",
        False,
        True,
        False,
        "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED",
    ),
    "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION": ExecutionClassPolicy(
        "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION", False, True, False, None
    ),
}


@dataclass(frozen=True)
class GovernedEndpointObservation:
    endpoint: str | None
    emission_surface: str
    raw_result_digest: str
    internal_diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConjunctiveAssertionObservation:
    primary_endpoint: GovernedEndpointObservation
    required_invariants: tuple[str, ...]
    satisfied_invariants: tuple[str, ...]
    invariant_evidence_digests: tuple[str, ...]


@dataclass(frozen=True)
class PositiveAssertionObservation:
    assertion_id: str
    satisfied: bool
    evidence_digests: tuple[str, ...]


@dataclass(frozen=True)
class InsufficientEvidenceEndpointCondition:
    case_id: str
    case_execution_evidence_bundle_present: bool
    case_preconditions_valid: bool
    target_condition_evidence_present: bool
    target_condition_observed: bool
    missing_case_execution_evidence: bool
    endpoint_emitted_by_candidate: bool
    endpoint_trigger_evidence_digest: str
    target_reason: str

    @property
    def qualifies_for_endpoint_pass(self) -> bool:
        expected = IE_TARGET_REASONS.get(self.case_id)
        return (
            expected is not None
            and self.case_execution_evidence_bundle_present
            and self.case_preconditions_valid
            and self.target_condition_evidence_present
            and self.target_condition_observed
            and not self.missing_case_execution_evidence
            and self.endpoint_emitted_by_candidate
            and is_sha256_hex(self.endpoint_trigger_evidence_digest)
            and self.target_reason == expected
        )


@dataclass(frozen=True)
class AuthorityEffectObservation:
    profile_id: str
    before_digest: str
    after_digest: str
    unauthorized_effect_count_before: int
    unauthorized_effect_count_after: int
    sink_state_before: str | None = None
    sink_state_after: str | None = None

    @property
    def unauthorized_effect_delta(self) -> int:
        return (
            self.unauthorized_effect_count_after
            - self.unauthorized_effect_count_before
        )


@dataclass(frozen=True)
class EnvironmentIdentity:
    python_version: str
    os_release_digest: str
    uname_digest: str
    dependency_lock_digest: str
    dependency_lock_method: str
    timezone: str
    pythonhashseed: str
    fixture_random_seed: int
    clock_model: str
    nonstdlib_imports: tuple[str, ...] = ()
    unexpected_wall_clock_read_count: int = 0


@dataclass(frozen=True)
class CaseRunBinding:
    case_id: str
    run_id: str
    packet_sha256: str
    plan_body_sha256: str
    plan_binding_blob_sha: str
    harness_blob_sha: str
    harness_version: str
    design_sha: str
    implementation_sha: str
    implementation_tree: str
    governance_generation: str
    target_module_git_blobs: tuple[str, ...]
    target_module_content_sha256s: tuple[str, ...]
    fixture_digest: str
    environment_digest: str
    case_status: str


def validate_environment(
    env: EnvironmentIdentity, *, exact_python_version: str
) -> list[str]:
    p: list[str] = []

    if not PYTHON_312_PATCH.fullmatch(exact_python_version):
        p.append("HARNESS_EXPECTED_PYTHON_VERSION_NOT_EXACT_PATCH")
    if env.python_version != exact_python_version:
        p.append("HARNESS_EXACT_PYTHON_VERSION_MISMATCH")
    if not PYTHON_312_PATCH.fullmatch(env.python_version):
        p.append("HARNESS_CAPTURED_PYTHON_VERSION_NOT_EXACT_PATCH")
    if env.timezone != TIMEZONE:
        p.append("HARNESS_TIMEZONE_MISMATCH")
    if env.pythonhashseed != PYTHONHASHSEED:
        p.append("HARNESS_PYTHONHASHSEED_MISMATCH")
    if env.fixture_random_seed != FIXTURE_RANDOM_SEED:
        p.append("HARNESS_RANDOM_SEED_MISMATCH")
    if env.clock_model not in {"FROZEN_LOGICAL_CLOCK", "EXPLICIT_CASE_TIMESTAMPS"}:
        p.append("HARNESS_CLOCK_MODEL_INVALID")
    if env.unexpected_wall_clock_read_count != 0:
        p.append("HARNESS_UNEXPECTED_WALL_CLOCK_READ")

    if env.dependency_lock_method not in {
        "PIP_FREEZE",
        "STDLIB_ONLY_PIP_UNAVAILABLE",
    }:
        p.append("HARNESS_DEPENDENCY_LOCK_METHOD_INVALID")

    if env.dependency_lock_method == "STDLIB_ONLY_PIP_UNAVAILABLE":
        if env.nonstdlib_imports:
            p.append("HARNESS_NONSTDLIB_IMPORT_UNDER_PIP_UNAVAILABLE")
        if (
            env.dependency_lock_digest
            != expected_stdlib_fallback_digest(exact_python_version)
        ):
            p.append("HARNESS_STDLIB_FALLBACK_DIGEST_MISMATCH")

    for f in ("os_release_digest", "uname_digest", "dependency_lock_digest"):
        if not is_sha256_hex(getattr(env, f)):
            p.append(f"HARNESS_ENV_DIGEST_INVALID:{f}")

    return p


def validate_binding(
    b: CaseRunBinding,
    *,
    packet_sha256: str,
    plan_body_sha256: str,
    plan_binding_blob_sha: str,
    harness_blob_sha: str,
) -> list[str]:
    p: list[str] = []

    if b.case_id not in CASE_IDS:
        p.append("CASE_ID_OUTSIDE_V24_I11")
    if not RUN_ID.fullmatch(b.run_id):
        p.append("RUN_ID_INVALID")
    elif not b.run_id.startswith(b.case_id + ":"):
        p.append("RUN_ID_CASE_BINDING_MISMATCH")
    if b.packet_sha256 != packet_sha256:
        p.append("PLAN_PACKET_SHA256_MISMATCH")
    if b.plan_body_sha256 != plan_body_sha256:
        p.append("PLAN_BODY_SHA_MISMATCH")
    if b.plan_binding_blob_sha != plan_binding_blob_sha:
        p.append("PLAN_BINDING_BLOB_SHA_MISMATCH")
    if b.harness_blob_sha != harness_blob_sha:
        p.append("HARNESS_BLOB_SHA_MISMATCH")
    if b.harness_version != HARNESS_VERSION:
        p.append("HARNESS_VERSION_MISMATCH")
    if b.design_sha != FROZEN_V24_DESIGN_SHA:
        p.append("DESIGN_SHA_MISMATCH")
    if b.implementation_sha != FROZEN_I10_IMPLEMENTATION_SHA:
        p.append("IMPLEMENTATION_SHA_MISMATCH")
    if b.implementation_tree != FROZEN_I10_TREE:
        p.append("IMPLEMENTATION_TREE_MISMATCH")
    if b.governance_generation != GOVERNANCE_GENERATION:
        p.append("GOVERNANCE_GENERATION_MISMATCH")
    if b.case_status not in CASE_STATUSES:
        p.append("CASE_STATUS_INVALID")

    if (
        b.case_id in BLOCKED_CASES
        and b.case_status != "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"
    ):
        p.append("BLOCKED_CASE_STATUS_REQUIRED")

    if (
        b.case_id not in BLOCKED_CASES
        and b.case_status == "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"
    ):
        p.append("NONBLOCKED_CASE_CANNOT_USE_I1_BLOCKED_STATUS")

    if not b.target_module_git_blobs:
        p.append("TARGET_MODULE_GIT_BLOB_SET_REQUIRED")
    if not b.target_module_content_sha256s:
        p.append("TARGET_MODULE_SHA256_SET_REQUIRED")
    if len(b.target_module_git_blobs) != len(b.target_module_content_sha256s):
        p.append("TARGET_MODULE_IDENTITY_COUNT_MISMATCH")

    for oid in b.target_module_git_blobs:
        if not is_git_oid(oid):
            p.append("TARGET_MODULE_GIT_BLOB_INVALID")
    for sha in b.target_module_content_sha256s:
        if not is_sha256_hex(sha):
            p.append("TARGET_MODULE_CONTENT_SHA256_INVALID")

    if not is_sha256_hex(b.packet_sha256):
        p.append("PLAN_PACKET_SHA256_INVALID")
    if not is_sha256_hex(b.plan_body_sha256):
        p.append("PLAN_BODY_SHA256_INVALID")
    if not is_git_oid(b.plan_binding_blob_sha):
        p.append("PLAN_BINDING_GIT_BLOB_INVALID")
    if not is_git_oid(b.harness_blob_sha):
        p.append("HARNESS_GIT_BLOB_INVALID")
    if not is_sha256_hex(b.fixture_digest):
        p.append("FIXTURE_DIGEST_INVALID")
    if not is_sha256_hex(b.environment_digest):
        p.append("ENVIRONMENT_DIGEST_INVALID")

    return p


def classify_negative(
    *,
    case_id: str,
    expected_endpoint: str,
    observed: GovernedEndpointObservation | None,
    effect: AuthorityEffectObservation | None,
    fixture_valid: bool,
    harness_valid: bool,
    ie_condition: InsufficientEvidenceEndpointCondition | None = None,
) -> str:
    """No diagnostic-to-endpoint normalization is permitted."""
    if not fixture_valid:
        return "FAIL_FIXTURE_DEFECT"
    if not harness_valid:
        return "FAIL_HARNESS_DEFECT"
    if observed is None or observed.endpoint is None:
        return "FAIL_CODE_DEFECT"
    if observed.endpoint != expected_endpoint:
        return "FAIL_CODE_DEFECT"

    if expected_endpoint == "INSUFFICIENT_EVIDENCE":
        if case_id not in IE_EXPECTED_CASES:
            return "FAIL_HARNESS_DEFECT"
        if ie_condition is None:
            return "FAIL_HARNESS_DEFECT"
        if ie_condition.case_id != case_id:
            return "FAIL_HARNESS_DEFECT"
        if not ie_condition.case_execution_evidence_bundle_present:
            return "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"
        if ie_condition.missing_case_execution_evidence:
            return "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"
        if not ie_condition.qualifies_for_endpoint_pass:
            return "INSUFFICIENT_EVIDENCE"

    if effect is None:
        return "FAIL_HARNESS_DEFECT"
    if effect.unauthorized_effect_delta != 0:
        return "FAIL_CODE_DEFECT"
    return "PASS"


def classify_conjunctive_negative(
    *,
    case_id: str,
    expected_endpoint: str,
    observation: ConjunctiveAssertionObservation | None,
    effect: AuthorityEffectObservation | None,
    fixture_valid: bool,
    harness_valid: bool,
) -> str:
    if not fixture_valid:
        return "FAIL_FIXTURE_DEFECT"
    if not harness_valid:
        return "FAIL_HARNESS_DEFECT"
    if observation is None:
        return "FAIL_HARNESS_DEFECT"
    if observation.primary_endpoint.endpoint != expected_endpoint:
        return "FAIL_CODE_DEFECT"

    exact_required = REQUIRED_CONJUNCTIVE_INVARIANTS.get(case_id)
    if exact_required is None:
        return "FAIL_HARNESS_DEFECT"
    if observation.required_invariants != exact_required:
        return "FAIL_CODE_DEFECT"
    if observation.satisfied_invariants != exact_required:
        return "FAIL_CODE_DEFECT"
    if len(observation.invariant_evidence_digests) != len(exact_required):
        return "FAIL_CODE_DEFECT"
    if not all(is_sha256_hex(x) for x in observation.invariant_evidence_digests):
        return "FAIL_CODE_DEFECT"

    if effect is None:
        return "FAIL_HARNESS_DEFECT"
    if effect.unauthorized_effect_delta != 0:
        return "FAIL_CODE_DEFECT"
    return "PASS"


def classify_positive(
    *,
    observation: PositiveAssertionObservation | None,
    fixture_valid: bool,
    harness_valid: bool,
) -> str:
    if not fixture_valid:
        return "FAIL_FIXTURE_DEFECT"
    if not harness_valid:
        return "FAIL_HARNESS_DEFECT"
    if observation is None:
        return "FAIL_HARNESS_DEFECT"
    if not observation.assertion_id:
        return "FAIL_HARNESS_DEFECT"
    if not observation.satisfied:
        return "FAIL_CODE_DEFECT"
    if not observation.evidence_digests:
        return "FAIL_HARNESS_DEFECT"
    if not all(is_sha256_hex(x) for x in observation.evidence_digests):
        return "FAIL_HARNESS_DEFECT"
    return "PASS"
```

The embedded source is review evidence only. Post-review governed adjudication verifies the declared harness Git blob and detached V8 review-binding blob before case execution.
