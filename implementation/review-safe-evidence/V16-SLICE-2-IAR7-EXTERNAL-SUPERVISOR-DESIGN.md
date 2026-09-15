# V16 Slice 2 — IAR7 External Assertion Supervisor Design

Status: **CONSTRUCTION DESIGN / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## 1. Purpose

This design repairs the execution-boundary defect confirmed by `V16-SLICE-2-CONSTRUCTION-RED-009.md`.

The governing distinction is:

- **evaluated worker** may compute candidate-controlled results;
- **trusted assertion supervisor** owns the expected oracle, parses the worker's bounded result as untrusted data, applies the oracle after worker completion, and writes the only load-bearing completion receipt.

A worker return code, console line, unittest result, self-issued marker, or self-declared PASS is never sufficient by itself.

## 2. Boundary model

For one operation, the supervisor owns:

- exact operation ID;
- exact request bytes/digest;
- timeout;
- response schema and maximum size;
- exact expected/oracle data or an independently defined supervisor predicate;
- worker process identity/return status as diagnostic facts;
- final verdict; and
- receipt serialization/digest.

The worker receives only the operation request needed to compute a result. The expected result/oracle is not passed to the worker by the supervisor protocol.

The worker's stdout is an untrusted result channel, not an authority channel. The worker's stderr is diagnostic-only.

## 3. Required response protocol

The current bounded construction protocol accepts exactly one UTF-8 JSON object with exact fields:

- `schema_version = 1`;
- `operation_id` exactly equal to the supervisor-owned requested operation ID;
- `result` containing only strict JSON values accepted by the supervisor's independent parser.

The parser must reject duplicate keys, floats/non-finite numbers, malformed UTF-8, multiple JSON values/lines, unknown top-level fields, oversized output, wrong operation identity, and unsupported value types.

## 4. Supervisor success rule

The supervisor may issue `SUPERVISOR_ORACLE_PASS` only when all are true:

1. worker launched under the configured bounded execution principal/environment;
2. worker completed before timeout;
3. worker did not terminate by signal;
4. worker process exit code is zero;
5. exactly one strict response object is present;
6. response identity equals the supervisor-owned operation identity;
7. response schema is exact;
8. the supervisor-owned oracle independently evaluates the returned `result` as correct;
9. the supervisor itself reaches and records the post-worker assertion point; and
10. the supervisor writes the receipt after those checks.

Worker exit 0 with no valid response is failure.

## 5. Mandatory mechanism falsification

The supervisor construction suite must prove fail-closed behavior for:

- abrupt worker `os._exit(0)` before response;
- nonzero exit;
- signal termination;
- timeout;
- malformed JSON;
- duplicate JSON keys;
- multiple response objects/extra console text;
- wrong operation ID;
- unsupported/unknown response fields;
- worker self-declared `PASS` field;
- valid protocol response with oracle-mismatching result;
- oversized response.

A normal worker result must pass only because the supervisor independently compares it with the hidden expected/oracle data after the worker has completed.

## 6. Process replacement and subprocess escape

A future authority-bearing runner must constrain process replacement/descendant escape through an OS-enforced worker sandbox. For the current bounded construction mechanism, `exec*`, fork/clone descendants, namespace escape, file/network access, and resource limits are separate sandbox obligations and cannot be inferred from the result protocol alone.

Accordingly:

`WORKER_PROCESS_REPLACEMENT_OS_ENFORCEMENT=NOT_YET_PROVEN`

`WORKER_DESCENDANT_PROCESS_ESCAPE_ENFORCEMENT=NOT_YET_PROVEN`

These limitations remain blockers to claiming a final arbitrary-code sandbox. They do not permit the supervisor to accept missing/malformed results.

## 7. Migration from the historical 77-test suite

The existing 77 in-process unit tests remain useful behavioral/construction evidence, but RED 009 proves they cannot by themselves establish arbitrary-code-resistant trusted completion.

They MUST NOT be silently relabeled as externally supervised tests.

Migration is explicit and additive:

1. define supervisor-owned operation/oracle cases for load-bearing Slice 2 requirements;
2. execute candidate logic in workers;
3. preserve mappings from each new supervised case to its predecessor requirement/test identity;
4. keep historical 77-test manifests intact;
5. do not mark Slice 2 freeze-eligible until the mandatory load-bearing requirement universe has a supervised-or-governed-exception disposition and another internal adversarial pass finds no unresolved Critical/High.

## 8. Non-claims

A supervisor PASS proves only the bounded black-box result/oracle relation exercised by that case. It does not prove hidden real-world control-domain completeness, provider ownership, credential custody, independent source measurement, runtime deployment identity, or scientific authority.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
