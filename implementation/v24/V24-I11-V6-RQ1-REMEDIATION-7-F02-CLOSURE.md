# Remediation-7 F-02 Candidate Closure

This record distinguishes the historical scientific execution from current
harness reuse validation. It does not authorize scientific execution or
qualify the runtime.

## Chronology and harness identity

- Historical Run-35: workflow `35433799081`, scientific commit
  `d79db50568cccaffe67ed1de5a6ee63bf5027284`.
- Historical harness SHA-256: `7ce7d5fb9817898198aa3b2be89706cd9ac561a2763386f2cd1cd9412eb81e1d`.
- Current Remediation-7 harness SHA-256 is measured from the current source;
  it is intentionally different.
- Run-35 did not use the Remediation-7 shared evaluator. Its immutable output
  is consumed offline by `replay_rq1_crash_evidence.py::adapt_case`, which is
  a representation-only historical-schema adapter. Current/future live runs
  use `current_live_first_attempt` and the canonical evidence builder directly,
  then call `evaluate_crash_case` from `v24_v6_rq1_crash_predicates.py`.

## F-02 correction

The live harness no longer manufactures `parsed={}` for empty stdout. The
shared `interpret_first_attempt` function requires the exact observed transport
close diagnostic for empty stdout, parses non-empty stdout from raw bytes, and
rejects malformed, contradictory, authoritative, wrong-target, or rc-only
claims. Historical adaptation and current live construction are separate paths
but converge on the same fail-closed evaluator.

## Candidate status

F-01: independently CLOSED.
F-02: CANDIDATE_CLOSED_PENDING_REVIEW.
F-03: independently CLOSED.
F-04/F-05/F-06/F-07: non-blocking backlog.

The offline harness-reuse result is `HARNESS_REUSE_CANDIDATE_PASS`; this is not
independent approval. No scientific rerun occurred, RQ-16 was not started,
and Run-35 evidence remains immutable.

Governance: `NOT_QUALIFIED`, `CLOSED_PENDING_SUCCESSOR_REVIEW`,
`NONE_EVIDENCE_ONLY`.
