# V16 Slice 2 IAR3 Repair Contract

Status: **CONSTRUCTION REPAIR CONTRACT / NON-AUTHORITATIVE**

Reviewed predecessor candidate: `685a56eab5c058f1120c22aca59d78f428874add`

Predecessor internal review: `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-003.md`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## R1 — graph-qualify validator-binding bootstrap quorum

A cryptographically valid bootstrap signature on a Slice 2 validator-binding certificate may count toward the binding threshold only when its root control domain is, under the exact graph bound by that certificate:

1. represented in the graph;
2. not candidate-controlled; and
3. part of a threshold-sized pairwise-independent signing-root set.

Distinct domain labels alone are insufficient. Unknown, absent, candidate-controlled, or shared-ancestor binding roots fail closed.

The binding result must expose only graph-qualified root domains as its authenticated quorum.

## R2 — version the revised baseline manifest instead of reusing old semantic identities

Preserve `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001` as historical evidence. It must not be used as the current semantic baseline after the IAR2 oracle changes.

Create a new current baseline manifest with:

- manifest ID `REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-002`;
- `semantic_revision = 2`;
- `supersedes_manifest_id = REVIEW-SAFE-EVIDENCE-V16-SLICE2-MANDATORY-TESTS-001`;
- exact current `test_source_git_blob_sha`;
- a concise `semantic_change_reason` describing fail-closed global promotion/authority plus graph-qualified bootstrap quorum semantics;
- new requirement IDs for the 30 baseline test oracles.

The current canonical workflow must validate the manifest's exact test-source blob before executing tests, and must use baseline v2 rather than the historical v1 manifest.

## Mandatory adversarial additions

The repaired candidate must add stable tests proving at least:

- a binding signer domain absent from the exact bound graph is rejected;
- a binding signer that the graph derives as candidate-controlled is rejected;
- binding signers sharing a load-bearing graph ancestor cannot satisfy quorum;
- a graph-represented, non-candidate, pairwise-independent binding quorum structurally validates;
- a failed outer binding quorum can never produce `construction_binding_valid=true`;
- the current baseline manifest has semantic revision 2, explicit predecessor identity, exact current test-source Git blob SHA, and new requirement IDs;
- the historical baseline manifest is not used as a current canonical manifest;
- all existing IAR1/IAR2 repair tests remain green;
- global promotion/authority stays blocked and no implementation/runtime/scientific/effect authority is claimed.

## Preserved boundaries

This repair does not prove real-world control ownership/completeness, independent runtime source measurement, bootstrap/currentness provisioning, final authenticated governance-generation currentness, implementation qualification, runtime qualification, scientific authority, or effect authority.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
