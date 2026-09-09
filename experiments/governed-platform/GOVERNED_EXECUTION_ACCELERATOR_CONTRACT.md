# Governed Execution Accelerator — Frozen Contract

Status: PRE-IMPLEMENTATION FROZEN TOOLING BOUNDARY

Base frontier: `main` at `a5726dcb9236e31028ec70603bee35b30b9dbe66` (administrative cleanup after accidental noop commit; Slice10 content remains the merged `58b3d19d...` tree lineage).

## Goal
Reduce repeated orchestration, polling, evidence-packet construction, and serial regression wall-clock time without weakening governance or falsification requirements.

## Included
1. `governed_status.py` — one deterministic status snapshot from exact checkout + governance state.
2. `review_packet_builder.py` — deterministic full/delta packet generation from an explicit manifest.
3. `review_ingest.py` — deterministic structural/evidence-bound intake of reviewer JSON; never promotion authority.
4. reusable parallel regression workflow with aggregate fail-closed gate.
5. standard adversarial matrix for new slices.

## Invariants
A1 accelerator output is evidence/orchestration metadata only; it cannot mint authority.
A2 status fails closed when checkout SHA and declared candidate/head mismatch.
A3 packets bind an exact 40-char candidate SHA and SHA-256 every embedded artifact.
A4 full/delta packets explicitly list included and omitted evidence.
A5 delta packets bind prior/current candidates and prior packet manifest identity.
A6 reviewer intake validates candidate binding, mandatory dimension uniqueness/coverage, and non-empty evidence.
A7 parallelism may change order/time only; every required regression group must succeed.
A8 missing/cancelled/skipped required groups fail aggregate.
A9 no bypass of red-first exposure, candidate freeze, independent review, deterministic adjudication, or SHA-pinned closure.
A10 adversarial matrix includes before-operation, after-dispatch-before-response, remote-commit-before-local-persist, after-local-persist, restart, concurrent duplicate, same-key/different-binding, changed lineage/lease, revocation-between-checks, exact expiry, malformed response, unexpected exception, post-commit exception, secret-bearing error.

## Acceptance
ACC-01 status reports exact checkout/governance heads and mismatch fails.
ACC-02 status reports stop condition + next action in one JSON object.
ACC-03 full packet hashes/embeds all required files.
ACC-04 missing required file fails packet build.
ACC-05 delta packet binds prior/current candidate and inherited manifest.
ACC-06 tampered embedded artifact fails verification.
ACC-07 reviewer intake rejects wrong candidate.
ACC-08 reviewer intake rejects duplicate/missing mandatory dimensions.
ACC-09 reviewer PASS remains non-authoritative evidence.
ACC-10 aggregate fails if any required regression fails/skips/cancels.
ACC-11 aggregate passes only when all required groups succeed.
ACC-12 adversarial matrix contains all A10 classes.

## Nonclaims
No automatic merge/release/deploy authority; no replacement of independent review; no claim that parallel CI proves semantic correctness; no weakening of external-evidence provenance rules.
