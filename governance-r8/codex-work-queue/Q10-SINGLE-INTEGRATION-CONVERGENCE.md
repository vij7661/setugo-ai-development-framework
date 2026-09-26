# Q10 — Single integration-candidate convergence

This task replaces further separate-PR remediation loops.

Work only on:
`integration/r8-v15-r1-post-sg1-convergence-2026-09-26`

The candidate is composed from exact source heads listed in
`governance-r8/R8-V15-R1-POST-SG1-CONVERGENCE-MANIFEST.json`.

## Required behavior

1. Run the candidate invariant workflow.
2. Repair the integration branch itself until the invariant gate and all listed tests pass.
3. Treat failures as candidate-level defects; do not patch source PR branches independently.
4. Do not add historical review packets to the candidate implementation tree.
5. Do not hand-edit test counts or evidence summaries.
6. Do not weaken invariants/tests.
7. When green, stop coding and report the exact candidate HEAD/tree.
8. Do not merge or grant any authority.
9. A separate frozen branch will be created from the exact green SHA.
10. Linux evidence and independent-review packet will be generated only from that frozen SHA.

Fallback-to-3 remains ACTIVE. Six-slice cadence remains NOT restored.
