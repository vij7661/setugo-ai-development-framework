# RQ-07 gate-integrity RED and restoration record

## Immutable RED freeze

The original RQ-07 RED remains preserved from workflow `35427080422`, job
`d3ed9b4b-01ba-5652-9177-61d2ccac0359`, commit
`3bae61542f2b97a3906f0010914e3a9d7535c002`, tree
`db601811619830020602d3ef300651fc628abd07`.

The bound-run bundle digest was
`bfa1f5e9f92152ea4ce2b703619ada6e63d8caa68e63bbf75f4d526139567e96`.

Frozen expected gate SHA-256:
`7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`.

Observed live gate before restoration:

- SHA-256: `fbc4b960af6cd44f80072a0da1c0e26d7bc5168ac7526e044eeff3e05f66de89`
- size: 22 bytes
- owner/group: `root:root`
- content: `#!/bin/sh\necho forged\n`
- service binary remained `a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d`
- service was active
- build manifest still declared the frozen expected gate hash.

Classification: `RQ-07=RED`,
`defect_class=BOUND_RUNTIME_TRUSTED_GATE_INTEGRITY_DEFECT`.

## Provenance

The preserved post-subject install evidence records the expected gate hash at
2026-09-18T19:24:20Z. Repository history and the preserved RQ harnesses contain
no command that writes the live `/opt` gate; their substitution tests operate on
copies or assert permission denial. The earliest bad measurement currently
available is the RQ-07 run above. Therefore provenance is
`PROVENANCE_NOT_VERIFIED`; no responsible workflow or mutation command is
asserted without evidence.

## Exact restoration

The frozen build script was run from the bound Ubuntu runtime using the pinned
source/bootstrap lineage. It reproduced exactly:

- gate SHA-256 `7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`
- build-input SHA-256 `b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9`

The rebuilt binary and matching build manifest were installed root-owned at the
existing trusted path with the frozen non-writable modes. Pre/post raw evidence
is sealed under
`/var/lib/v24-rq1/runs/20260919T-gate-restore-3bae6154/` on the bound VM.

No service binary, socket, records, or consumed state was changed. Scientific
execution remains closed and no authority effect is enabled.
