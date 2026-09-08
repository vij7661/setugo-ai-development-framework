# EXP-L L9 — Stage-2 Handoff Defect Adjudication

Date: 2026-09-08
Branch: `experiment/exp-l-independent-review-evidence-prompt`

## Classification

`INVALID_FIXTURE / PROTOCOL_HANDOFF_DEFECT / NONPROMOTABLE`

## What happened

L9 Manual Run 2 Stage 1 behaved correctly: all five reviewers returned `DISCOVERY_REQUEST` with `INSUFFICIENT_EVIDENCE` and requested only allow-listed paths.

The generated Stage-2 packet then materialized only the requested evidence excerpts and case IDs, but failed to carry forward the frozen original case question / decision target.

As a result, the reviewer had valid discovered evidence but an under-specified decision target. This was exposed directly in the returned outputs:

- `L9-M02` was originally about whether production scope supports **individual Goat + Lot**, but Stage 2 answered the **weighment accept/reject flow**.
- `L9-M03` was originally about **authoritative verified listing weight vs manual entry**, but Stage 2 answered the **general weighment decision tree**.

The outputs contain true facts from the requested authoritative files, but they are not valid answers to the frozen original cases.

## Root cause

The Stage-2 packet generator failed to bind and preserve the original review target across the discovery handoff.

This is a protocol/fixture construction defect, not evidence of reviewer semantic failure.

## Scientific treatment

- Do not count Stage-2 Run 1 as a pass.
- Do not classify the reviewer as failed for answering an under-specified handoff.
- Preserve all outputs as defect evidence.
- Repair only the handoff packet so it includes, per case:
  - immutable case ID,
  - immutable original review question / decision target,
  - Stage-1 requested paths,
  - exact materialized responses with commit/blob identity,
  - no unrequested evidence.
- Rerun Stage 2 in a fresh reviewer context.

## Governance implication

Reviewer-directed evidence discovery is unsafe if the discovery response is not cryptographically and semantically bound to the original review question. A correct broker therefore must bind **request identity + decision target + candidate/base + requested paths + materialized evidence** into the continued review packet.

L9 remains **NOT PASSED** pending repaired Stage-2 execution.
