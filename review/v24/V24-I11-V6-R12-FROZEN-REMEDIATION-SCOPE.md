# V24 I11 V6 R12 — Frozen Remediation Scope

Status: **FROZEN FOR R12 IMPLEMENTATION**

Frozen predecessor candidate:
- R11 commit `68ce0df63ce0133ae19ec4402b41c4c09adfb54e`
- R11 tree `d202b039285213b386557083a26de42e0fb20cf4`

Authority effect: `NONE_EVIDENCE_ONLY`

## A. R11-A / external execution boundary

1. Verify actual interpreter isolation state from the running trusted process, not pinset booleans.
2. Separate candidate-controlled code from trusted result-accounting state; candidate code must execute across a process boundary and cannot mutate the authority that decides PASS contribution.
3. Bind Python/runtime version and stdlib-shadow universe to the intended interpreter contract.

## B. Mandatory adversarial-check evidence

4. Replace adversarial-check name-only attestation with exact executed evidence records bound to check identity, candidate commit/tree, runtime/environment contract, terminal result, evidence digest, and independent witness/authority where required.

## C. Runtime/result evidence integrity

5. `validate_runtime.py` latest-result accounting must bind to executed harness/process evidence rather than caller-provided passed/total/failures counts.
6. SHA/commit fields used in material authority paths must resolve to governed Git objects and the expected branch/head/path identity; 40-hex syntax alone is insufficient.

## D. Completeness / admission / generation / aggregate closures

7. Derive reviewer-proof `load_bearing` status from an authoritative subject catalog; caller labels cannot neutralize blocking completeness states.
8. `NO_COMMIT_CONFIRMED` cannot coexist with successful authority transition; only positively confirmed commit states may yield SUCCESS.
9. I6 admission/decision/application authority sets cannot vacuously pass empty when construction/authority application is claimed; require independently bound non-empty universes where applicable.
10. I4 completeness `required_subjects` cannot vacuously be empty when completeness construction is claimed; bind required-subject universe independently and require exactly one CURRENT record per required subject.
11. I8 predecessor migration cannot vacuously pass empty predecessor universe when a predecessor generation exists; derive and bind the predecessor-object universe independently.
12. Authority-surface inventory must derive the governed surface universe from an authoritative catalog and verify `base_commit` against governed repository identity; arbitrary caller-provided 14-file lists cannot satisfy completion.

## E. Independent evidence / caller-label elimination

13. Witness quorum policy, operational-domain/root-domain inventory, and witness independence must be externally bound; names/control-domain strings alone cannot create independence.
14. Completeness bootstrap source contracts must reject `CANDIDATE_SELF` wherever load-bearing independence is required, even when mixed with another source-kind label.
15. Generation/cache guard and qualifying-disposition checks must bind executed/verified evidence rather than caller booleans.
16. Historical-failure preservation must bind actual preserved historical records/digests; a boolean cannot establish preservation.

## F. review_protocol.py authority closure

17. Schema-4 material review requests must contain at least one mandatory dimension. BOUNDED_PASS requires a non-empty mandatory set, all mandatory dimensions TESTED_SUPPORTED, no defect/contradiction statuses capable of promotion, and no contradictory assessment text.
18. Reviewer/provider/model authentication must come from a trusted, verifiable adapter receipt/registry rather than caller-constructible DispatchResult fields or transport-name strings.
19. Material review commit identity must be mandatory, resolve to a governed Git object, equal the ReviewRequest commit, and equal the authoritative transition/workstream candidate.
20. Legacy schemas must have a separate explicitly historical/non-authoritative validation path; material `validate_review_evidence` cannot return authoritative success for schema <4.
21. Promotion must bind active ReviewRequest state, `material_authority_transition`, request trigger, authoritative transition trigger, and supplied trigger; rejected/superseded/stale/differently-triggered requests cannot promote.
22. Shared-memory review grounding must validate the complete pending-review set and uniqueness of the active review; checking only `pending_reviews[0]` is insufficient.

## G. Open adversarial target retained from R11 review

23. Strengthen the anti-false-green AST/static scanner against demonstrated or plausible casing, unicode/confusable, and runtime string-construction evasions. This remains a required R12 adversarial test target even though the R11 reviewer did not demonstrate a working exploit.

## H. Non-goals / unchanged posture

- Do not reopen approved V6 semantics except where required by the frozen repairs above.
- Do not treat construction CI as scientific or runtime qualification.
- Do not erase or overwrite any historical RED/NEEDS_REVISION evidence.
- Do not use automated external reviewer APIs during TESTING/FALSIFICATION; manual independent review remains required.
- R12 implementation/construction evidence cannot grant scientific execution or runtime authority.

## Exit from implementation/construction

R12 may be frozen as a successor candidate only after deterministic construction tests and adversarial probes cover every item above. It must then undergo a new clean manual successor review before scientific WDPC can reopen.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
