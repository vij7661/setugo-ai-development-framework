# V16 Slice 2 IAR6 Repair Contract

Reviewed predecessor candidate: `ab52366bfadea960fd803128e74274624720cf67` (tree `dc0be78c89326470434a1c89a8ee58afd11ca8b4`).

Accepted finding: `IAR6-H1` from `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-006.md`.

This is a construction-stage repair contract only. It cannot grant implementation, runtime, scientific, promotion, or effect authority.

## Trusted execution-receipt requirements

The successor harness MUST NOT derive load-bearing test execution identity or success from child stdout/stderr text.

The successor harness MUST:

- derive the exact current declared test-ID sequence from the exact current manifests using trusted parent logic;
- independently AST-discover the exact current test IDs from the exact current test-source files before child execution;
- require declared/source-discovered exact set equality, uniqueness, and the expected cardinality before execution;
- create a root-owned, read-only execution snapshot and execute tests under a principal that cannot mutate either the governed checkout or execution snapshot;
- invoke each exact declared test ID individually from a trusted parent;
- use a workflow-generated, root-owned child runner that exits success only when exactly one requested unittest case starts and succeeds without skip, failure, error, unexpected success, expected failure, or failing subtest;
- have the trusted parent record the exact test ID it invoked, deterministic sequence number, child return code, and SHA-256 digest of diagnostic output;
- treat diagnostic output as non-authoritative for execution identity and success;
- fail if any parent receipt row has a nonzero return code, duplicate ID, missing ID, extra ID, sequence gap, or mismatch from the declared/source-discovered set;
- include a falsification probe in which a child emits forged unittest-looking success text for another ID; the parent receipt mechanism must not create an execution receipt for the forged ID;
- retain pre/post clean-worktree and exact governed-blob checks;
- retain pre/post execution-snapshot equality checks;
- preserve all prior RED records.

## Evidence semantics

A successful parent receipt establishes only that the exact governed child runner was asked to execute each exact governed test ID and returned success under the construction harness. SHA-256 output digests are content addresses/integrity metadata only. They are not signatures, issuer authentication, runtime qualification, or scientific authority.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
