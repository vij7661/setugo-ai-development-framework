# V16 Slice 2 IAR5 Repair Contract

Predecessor reviewed candidate: `5a182a4263191ad3ed250eff25d143858a948178`.

Accepted findings: `IAR5-H1`, `IAR5-H2` from `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-005.md`.

This is a construction-stage repair contract only. It cannot grant implementation, runtime, scientific, promotion, or effect authority.

## IAR5-H1 repair requirements

The successor harness MUST:

- start from the exact workflow commit and record candidate commit/tree;
- prove the governed checkout is clean before test execution;
- execute candidate-controlled tests under a principal without write permission to the repository checkout;
- prove the governed checkout remains clean after test execution, including untracked files;
- re-verify exact Git blob identities for all load-bearing Slice 2 validators, test sources, current manifests, historical manifests, manifest index, dependency lock input, and strict manifest validator after test execution and before post-test evidence interpretation;
- fail closed on any byte drift;
- keep all construction success explicitly non-authoritative.

## IAR5-H2 repair requirements

The successor manifest system MUST:

- preserve the original IAR1 manifest Git blob `a63d613298ba2514a3d11fb86fd2a67dc70c756b` exactly;
- preserve the original IAR2 manifest Git blob `d72f7c72b46c680e8d4f94b1d03bbb4e0765dc5c` exactly;
- introduce new current IAR1 and IAR2 manifest identities rather than rewriting the historical identities;
- bind each current successor to its exact historical predecessor manifest ID and Git blob;
- bind current IAR1 to test-source Git blob `f5f130543641d7675fe4eba9f52dca969d52d74e`;
- bind current IAR2 to test-source Git blob `d62eb7cde62805ace95b1dff6d27a08cdf295213`;
- require semantic revision and a non-empty semantic change reason;
- require exact schema fields and duplicate-key rejection;
- require the current-manifest index to enumerate current and historical manifest IDs plus exact historical Git blob bindings;
- reject same-ID/different-content predecessor substitution and current source-byte drift.

## Mandatory adversarial coverage

At minimum, add tests proving:

1. current IAR1 is source-byte bound;
2. current IAR2 is source-byte bound;
3. exact historical IAR1 predecessor content passes;
4. same historical IAR1 ID with changed content fails;
5. exact historical IAR2 predecessor content passes;
6. same historical IAR2 ID with changed content fails;
7. current index excludes historical IAR1/IAR2 identities from the current set and binds their exact blobs;
8. current IAR1/IAR2 source drift fails strict validation.

The harness must continue source/manifest/execution-set equality checks for every current mandatory test. Any failure is preserved as RED and classified before repair.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
