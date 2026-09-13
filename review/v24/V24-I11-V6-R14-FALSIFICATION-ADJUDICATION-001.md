# V24-I11-V6-R14 — Falsification Adjudication 001

Status: **R14 REJECTED / R15 REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound R14 candidate

- candidate commit: `5a1fb005e9c58e30b1dcfaa473d603dde90df72c`
- candidate tree: `6e65609ac09b78bcffefb6d6560b640ba7696521`
- successful native construction run before stronger falsification: `34775429489`
- stronger falsification run: `34775597496`
- falsification artifact ID: `10323311407`
- outer artifact SHA-256: `f8afce70f60bfef53fa952ef737a8b8250931afec6885511a03afaa7273792bb`
- preserved result SHA-256: `3d8460d83d917c707c1b45f9b40863739385e72ac5a4d4892ec7012f885714b6`
- exact native observer binary SHA-256: `d29adf52dc160801992eecff423cf5da19128693964baa1523d881aeefc79fa7`

## Critical mechanism defect — bytes-path process-memory bypass

**Accepted / Critical / `FAIL_CODE_DEFECT`.**

R14's execution contract explicitly requires:

- `candidate_python_direct_process_memory_access_forbidden = true`; and
- mandatory regression coverage for `CANDIDATE_PROC_SELF_MEM_ACCESS`.

The R14 audit hook rejects `/proc/...`, `/sys/...`, `/dev/mem`, and `/dev/kmem` only when the audit event's path object is a Python Unicode object. Python file APIs also accept byte-string paths.

The stronger falsification inserted a syntactically valid candidate import-time action:

```python
_r14_mem = open(b'/proc/self/mem', 'rb', buffering=0)
_r14_mem.close()
```

Observed result:

- the candidate opened `/proc/self/mem` successfully through the bytes-path alternate representation;
- the audit policy did not reject the operation;
- candidate execution continued normally;
- the native child produced a valid HMAC-authenticated frame;
- the trusted native parent emitted a normal `R14_NATIVE_OBSERVATION=...` record;
- native exit code was `0`;
- `authenticated_observation_emitted = true`;
- `forbidden_memory_open_bypassed_audit_policy = true`.

This is not a harness failure. The intended forbidden operation reached the semantic endpoint and was accepted.

## Why the earlier R14 construction PASS remains historical but insufficient

Run `34775429489` genuinely passed the attack set it executed, including the string-path `/proc/self/mem` probe, frame injection, early `os._exit(0)`, `sys._getframe`, `ctypes`, tracing, threading, exact-file substitutions, native-binary substitution, oracle isolation, and six external-oracle checks.

The stronger attack demonstrates that the process-memory prohibition was representation-incomplete. The prior construction PASS remains valid evidence for the tested paths, but cannot support R14 acceptance, successor freeze, scientific execution opening, or runtime qualification.

No historical evidence is deleted or rewritten.

## Required R15 structural property

R15 must be a new successor. Do not patch R14 in place.

At minimum:

1. process-memory/path restrictions must be representation-complete for `str`, `bytes`, and any path-like form normalized by CPython audit events;
2. `/proc`, `/sys`, `/dev/mem`, `/dev/kmem`, process-memory, process-map, and equivalent native-memory surfaces must fail closed before candidate-controlled code can use them;
3. the original Unicode-path probe and the new bytes-path probe must both be mandatory regressions;
4. successful audit rejection must be demonstrated at the exact semantic endpoint, not inferred from import failure elsewhere;
5. alternate low-level file APIs (`open`, `os.open`/`posix.open`, `_io.FileIO` where reachable) must be covered by the same normalized policy;
6. native extension / direct-memory escape restrictions remain mandatory and must not be weakened;
7. external oracle and native HMAC separation remain construction-only and non-authoritative until successor review completes.

## State transition

- R14: `REJECTED`
- R14 manual successor review package: `CANCELLED_KNOWN_BLOCKER`
- R15: `REQUIRED`
- scientific WDPC: `CLOSED`
- runtime qualification: `NOT_CLAIMED`
- automated external reviewer APIs during TESTING: `PROHIBITED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
