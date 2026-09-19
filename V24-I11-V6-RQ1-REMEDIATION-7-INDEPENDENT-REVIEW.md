# V24-I11-V6 RQ1 Remediation-7 Independent Review Packet

## Frozen identity

- Branch: `qualification/v24-i11-v6-runtime-qualification-1-remediation-7`
- Final local commit: `6c6b5c64a17bee5b8d1cf5f52f1d38f223a759de`
- Final local tree: `926ae8f91d80d72707b23578bbc201a851866fbc`
- Base: `d79db50568cccaffe67ed1de5a6ee63bf5027284`
- Scientific run reused: `35433799081`
- Scientific rerun: `false`
- RQ-16 started: `false`

The local branch is one commit ahead of the remote branch because the
intermittent GitHub proxy prevented the final push. The self-contained review
tarball contains the exact final source and diff.

## DeepSeek findings and corrections

DeepSeek reported CHANGES_REQUIRED for mismatches between the evaluator and
the immutable Run-35 representation: first-consume `rc=1`, `trigger` versus
`boundary`, nested `restart.rc`, authoritative DENY with `record_state=CONSUMED`
for recovery, and replay's `trusted_record_id="-"` sentinel. It also noted
that raw `stdout`/`stderr` were not represented as `parsed` fields.

The correction is an explicit `adapt_case()` normalization in
`governance-runtime/replay_rq1_crash_evidence.py`. It reads dedicated raw
observer and boundary files, parses preserved stdout, aliases nested
`restart.rc`, and records normalization provenance. No fact is invented.

The shared predicate now requires:

```python
first["rc"] != 0
and (a parsed response is non-authoritative, or stderr contains
     "trusted service closed before control response")
```

Recovery consumption requires `service_authoritative == true`, exact target
ID, and `record_state == "CONSUMED"`; it does not invent an ALLOW requirement.
Replay requires parseable explicit `service_authoritative == false`, reason
`AUTHORITY_RECORD_UNAVAILABLE_OR_REPLAYED`, and zero state deltas. The
protocol's `trusted_record_id == "-"` unavailable sentinel is accepted only
for replay rejection, with target binding supplied by immutable lifecycle
state and exact deltas.

## Direct untouched-detail replay

Calling `evaluate_crash_case()` directly on each untouched `result["detail"]`
fails closed, as expected, because the frozen detail omits canonical PID,
raw observer objects, and canonical boundary fields. It does not silently
PASS. The complete output is in `direct-untouched-detail-replay.json` in the
self-contained package.

The explicit reasons include `service_pid_invalid`,
`tracer_ready_invalid`, `trace_inputs_invalid`, missing canonical observer
objects, and recovery/retry schema mismatches.

## Normalized offline replay

The same immutable Run-35 files, after traceable normalization, produce:

| Case | Result | Reasons |
|---|---|---|
| RQ-13 | PASS | `[]` |
| RQ-14 | PASS | `[]` |
| RQ-15 | PASS | `[]` |

The machine-readable normalization provenance is embedded in
`offline-replay.json`.

## F-01/F-02/F-03 closure matrix

| Finding | Status | Evidence |
|---|---|---|
| F-01 explicit retry/replay denial and zero deltas | PASS | Shared predicate plus Run-35 replay; malformed/empty/authoritative mutations rejected |
| F-02 behavioral falsification | PASS | Tests invoke `evaluate_crash_case`; 46/46 Run-35-shaped mutations rejected |
| F-03 load-bearing boundary evidence | PASS | PID, target, boundary, syscall, phase, exact paths, trace error, rename result, first authority checks |

## Automated evidence

- Behavioral tests: `8/8 PASS`.
- Oracle validator: `PASS`.
- Mutation result: `all_rejected=true`, `46` checks.
- Package internal file manifest: `PASS`.
- Package tar manifest: `PASS`.
- Python cache files in package: `0`.
- Immutable input ZIP SHA-256: `8c689ef763b9758e52fe72e73ad0381480b2b8f996d32558de6961ec10483d3b`.

## Governance

`NOT_QUALIFIED` / `CLOSED_PENDING_SUCCESSOR_REVIEW` /
`NONE_EVIDENCE_ONLY`.

No scientific RQ case was rerun. RQ-16 was not started. F-04, F-05, F-06,
and F-07 remain non-blocking backlog items and are not silently adjudicated.

## Independent-review request

Please independently verify that F-01, F-02, and F-03 are closed using the
full source, raw Run-35 evidence, direct untouched-detail failure output,
normalization provenance, behavioral tests, and 46/46 mutation results in the
accompanying self-contained package. Confirm that normalization is purely
representational, that no scientific rerun occurred, and that no runtime
qualification or RQ-16 authorization follows from this packet.
