# V16 Slice 2 Internal Adversarial Review 006

Review target: exact V6 construction candidate `ab52366bfadea960fd803128e74274624720cf67` (tree `dc0be78c89326470434a1c89a8ee58afd11ca8b4`) and its failed final evidence-reconciliation path in workflow run `34996050667`.

Review posture: falsification-first. The 77/77 behavioral green is construction evidence only and does not override the failed evidence endpoint or grant authority.

## Disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## High finding

### IAR6-H1 — Candidate-controlled human test output is treated as the authoritative execution receipt

Affected surface: `.github/workflows/review-safe-evidence-v16-slice2-independence-v6.yml`, final `Verify strict manifests against source and raw execution log` step.

The harness derives `executed` test identities by applying a regular expression to merged verbose unittest stdout/stderr produced by child test processes. That output is diagnostic text generated in the same execution context as candidate-controlled test code. It is not a trusted event channel.

Concrete false-green path: a test can print a line matching the harness's expected `test_id (...) ... ok` grammar for another declared test. Because the final set-equality check consumes printed text rather than a parent-controlled invocation record, forged child output can contribute an apparent execution identity that the parent did not establish. The V6 RED also demonstrated the converse: benign child diagnostics can split a genuine success line and erase an actually executed identity from the regex result.

A zero overall child exit status does not repair the identity problem. It only establishes that the invoked unittest process exited successfully; it does not make arbitrary strings emitted by that process authoritative evidence of which exact declared IDs the harness invoked and observed completing.

### Governing rule

Load-bearing construction evidence must derive from a channel the evaluated child cannot self-grant or fabricate. Diagnostic stdout/stderr may be retained as evidence, but it cannot be the sole authority for test identity or successful completion.

### Narrow required repair

Use a trusted parent execution harness whose load-bearing receipt is generated from parent-controlled inputs and subprocess return statuses:

1. Independently derive the exact current declared test-ID set from the exact current manifests and exact source discovery before execution.
2. Invoke every exact test ID individually as a child process under the existing non-repository-writer principal and root-owned read-only source snapshot.
3. The parent records the exact ID it invoked, deterministic sequence number, child return code, and diagnostic-output content digests. The child does not provide the receipt identity.
4. Any nonzero child return code blocks the construction result immediately. No parsed `ok`, `OK`, test count, or other child-written string may substitute for return-code success.
5. Require exact equality between declared IDs, independently source-discovered IDs, and parent receipt IDs, including cardinality, uniqueness, and no extras/omissions.
6. Add a harness-level falsification probe: a child prints a forged unittest-looking success line for an ID it was not invoked as. The trusted receipt must still contain only the parent's invoked probe identity and must not accept the forged line as execution evidence.
7. Preserve raw stdout/stderr for diagnostics, but label it non-authoritative for execution identity.
8. Keep the existing pre/post clean-worktree, read-only snapshot, and exact governed-blob re-attestation controls.

## Confirmed properties retained from V6

The exact V6 run demonstrated that the IAR5-H1 non-writer isolation direction is mechanically workable: the source snapshot was root-owned/non-writable to the test principal, 77 tests completed, and post-test source/worktree/blob equality held. It also demonstrated the current IAR1/IAR2/IAR4 manifest successor structure could support the 77-test suite. These are construction observations only; V6 remains RED because final evidence acceptance failed.

## Required next state

Retire V6 before changing the harness. Build a new V7 construction harness around parent-controlled per-test execution receipts, preserve all earlier REDs, execute against one exact stabilized candidate, then perform another internal adversarial pass against that exact candidate before any Slice 2 freeze decision.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
