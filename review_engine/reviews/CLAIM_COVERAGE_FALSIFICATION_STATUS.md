# Claim Coverage Falsification Status

This record evaluates the product-level Claim Coverage / truth-bearer omission control on `feature/review-engine-mvp`.

Green tests are verification evidence. They are not production, release, correctness, or external-action authority.

## Control under test

The product application can be configured with a platform-owned `ClaimCoverageValidator`. When configured, `ReviewEngineApp` wraps reviewer invocation with `ClaimCoverageGuardedInvoker` so coverage evaluation happens after the model/provider response is returned.

Retained `ClaimCoverageInventory` records bind:

- exact artifact SHA-256;
- a complete retained inventory of extracted claims;
- claim text fingerprints and claim type/materiality;
- platform-bound extractor identity;
- extractor qualification reference/epoch as identity metadata;
- provenance.

The governed comparison rejects or escalates:

- a material claim omitted from `epistemic_review`;
- a material claim declared under a different claim type;
- a material claim downgraded with `material=false`;
- stale inventories bound to a different artifact;
- same-foundation-lineage extraction as independent evidence;
- conflicting independent inventories;
- caller attempts to manufacture coverage evidence through review JSON.

A configured validator with no exact, complete, lineage-independent inventory fails closed through a material `TVC-COVERAGE` finding.

## Stronger multi-extractor policy

`MinimumIndependentClaimCoverage` optionally requires multiple extractors. Independence is not inferred from different labels alone. The policy requires both:

- distinct provider/model/SKU/deployment runtime paths; and
- distinct foundation lineages.

Aliases of the same runtime path and multiple extractors sharing one foundation lineage do not satisfy a multi-extractor requirement.

## Product falsification coverage

The retained regression set attacks:

1. model omits a material empirical truth-bearer entirely;
2. model relabels a material empirical fact as an inference;
3. model marks a material claim `material=false`;
4. stale artifact coverage inventory reuse;
5. same-lineage extractor presented as independent coverage;
6. conflicting independent inventories;
7. custom/product provider path attempts to omit coverage finding;
8. public request JSON attempts to inject a caller-created coverage inventory;
9. same runtime path disguised with separate extractor identities/qualification references;
10. different runtime paths sharing one foundation lineage;
11. paraphrase/claim-boundary drift attempting to reuse an exact retained claim inventory.

The paraphrase test is deliberately conservative: a semantically similar but textually different claim does not silently inherit coverage. It remains uncovered instead of receiving a false `VERIFIED_COVERAGE` result.

## Test-stimulus false start

GitHub Actions run `33984041835` at head `ec35977795a91a8d43313c4fc806c9aa613bc8bb` failed three application-path coverage tests because their user prompt contained the word `deployment`. The pre-existing request-risk floor correctly escalated and stopped the unqualified request before R1, so the tests never reached the claim-coverage control and then failed while looking for an `R1_COMPLETED` event.

This was classified as a test-stimulus defect, not a product defect. The stimulus was changed to a neutral request (`summarize the status statement`) while preserving the same model output under attack. Production risk logic was not weakened.

The isolated application-path rerun at head `6a5261c171ec614adace824378e049c38e131470`, run `33984093881`, completed successfully.

## Exact falsification verification

The expanded correlated-extractor and paraphrase-drift suite was validated at exact head:

`dfc70ebeefe6453dd6fab3e4451296209b2ffe16`

GitHub Actions run `33984169595` completed `success`. The exact run's `validate-harness` job shows successful:

- committed JSON/canonical case validation;
- Python compilation;
- Review Engine system regressions;
- scorer regressions;
- runner regressions;
- protected-truth regressions;
- observability regressions;
- continuation-authority regressions;
- governor falsification regressions.

Documentation/export commits after that implementation-test head do not replace the exact-head verification claim above. The final moving branch head must receive its own exact-head CI before being treated as the new baseline.

## What this control does not prove

Claim coverage verifies a reviewer-declared claim inventory against independently retained extraction evidence. It does **not** prove that the independent extractor found every material claim in the artifact.

Remaining boundaries:

1. **Extractor qualification admission** — `ClaimExtractorIdentity` carries provider/model/SKU/deployment/lineage/qualification-ref/epoch identity fields, but retained inventory admission is not yet independently checked against a dedicated extractor qualification registry. Today that admission is a trusted integration responsibility.
2. **Runtime identity** — the extractor binding is platform bookkeeping identity, not universal cryptographic proof that the remote provider executed the configured model/SKU/path.
3. **Correlated omission** — multiple extractors can still share unknown training/data/reasoning correlations. Distinct lineage/runtime metadata reduces some correlation risk but does not prove independence.
4. **Semantic equivalence** — exact normalized claim fingerprints intentionally do not solve paraphrase or claim-boundary equivalence.
5. **Extraction completeness** — agreement among extractors is evidence, not proof that no material truth-bearer was omitted.
6. **Low-level bypass boundary** — the standard `ReviewEngineApp` product path enforces coverage when configured; direct low-level construction of `ReviewEngine` without the guarded invoker is not claimed to enforce this control.
7. **Audit detail** — platform `TVC-COVERAGE` findings are retained in stage evidence, but full coverage assessment/provenance retention can be strengthened further.

## Next attack surface

The next governance-relevant component should close **extractor qualification admission** before a retained coverage inventory is accepted. It should use a dedicated qualification record rather than pretending R1/R2/R3 reviewer qualification automatically covers extraction. Required attacks include revoked/pending qualification, stale epoch, provider/model/SKU/deployment substitution, foundation-lineage mismatch, task/risk scope mismatch, and unqualified inventory admission.
