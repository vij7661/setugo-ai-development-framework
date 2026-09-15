# V16 Slice 2 Internal Adversarial Review 005

Review target: exact post-IAR4 construction candidate `5a182a4263191ad3ed250eff25d143858a948178` (tree `bdf83c671d4b985bb9a12cf0c2fbd5658d747a37`).

Review posture: falsification-first. A green construction run is evidence only. It does not grant implementation, runtime, scientific, promotion, or effect authority.

## Disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## High findings

### IAR5-H1 — Candidate-controlled test execution can mutate the governed workspace after the initial blob attestation

Affected surface: `.github/workflows/review-safe-evidence-v16-slice2-independence-v5.yml`.

The workflow verifies selected Git blob identities only before compilation and test execution. It then executes candidate-controlled Python test code with the runner user's normal workspace write privileges. The post-test manifest/source/execution verifier reads the mutable working tree, but the workflow does not prove that the governed files still equal the initially attested commit bytes before that verifier runs.

Concrete false-green path: a test can rewrite one or more current manifest/source files after the initial blob checks, allow the post-test verifier to consume the rewritten files, and thereby make the post-test evidence describe a different workspace state from the state initially attested. The existing source/manifest/execution set equality does not itself close this because it is computed from those post-test workspace bytes.

Narrow repair:

1. Execute the Python tests as a principal that cannot write the repository checkout.
2. Assert a clean tracked and untracked working tree immediately before tests and immediately after tests.
3. Recompute the load-bearing source/test/manifest/index/validator blobs after tests and require them to match the exact committed candidate bytes before any post-test evidence verifier consumes them.
4. Keep the verifier itself on the attested byte set and fail closed on any mutation.

### IAR5-H2 — Current IAR1/IAR2 mandatory-test manifests do not bind the exact test-source bytes they describe

Affected artifacts:
- `governance-runtime/review-safe-evidence-v16-slice2-test-manifest-iar1.json`
- `governance-runtime/review-safe-evidence-v16-slice2-test-manifest-iar2.json`
- `governance-runtime/review_safe_evidence_v16_manifest_validation.py`

The IAR1 and IAR2 manifests identify tests only by Python test IDs. Unlike the current baseline and later IAR3/IAR4 manifests, they carry no `test_source_git_blob_sha` and no semantic-revision/supersession binding. Their manifest IDs can therefore remain unchanged while the named test implementations change. The V5 workflow separately pins the present source blobs, which protects that one workflow run, but the manifest itself is not a portable durable statement of which test semantics it governs.

Concrete false-green path: a later harness can accept changed IAR1/IAR2 test source bytes while retaining the same manifest identities and requirement mappings. A consumer validating only the manifest set cannot detect the semantic substitution.

Narrow repair:

1. Preserve the original IAR1/IAR2 manifests exactly as historical artifacts.
2. Create current semantic-revision successors with new manifest IDs, exact predecessor Git-blob bindings, and exact `test_source_git_blob_sha` values.
3. Extend the strict manifest validator and current-manifest index so predecessor IDs alone are insufficient; historical content and current test-source content must both match their bound Git blobs.
4. Add adversarial tests for same-ID/different-content predecessor substitution and current test-source drift.

## Confirmed non-findings in this pass

The reviewed direct-core independence/authority APIs still return construction-only structural results with `promotion_blocked=true`, `authority_admissible=false` where applicable, and `qualified=false`. No direct-core route was found in this pass that upgrades those results into generic promotion or effect authority.

The IAR4 owned-snapshot repair remains present for public bound operations. The strict manifest parser continues to reject duplicate JSON keys and unknown schema fields.

## Required next state

Do not freeze Slice 2. Repair IAR5-H1 and IAR5-H2, add mandatory adversarial coverage, execute a new governed construction harness, preserve any RED encountered, and then perform another internal adversarial pass against the exact resulting candidate.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
