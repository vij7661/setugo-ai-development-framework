# Remediation-7 Review Backlog

- F-01: RQ-15 retry/replay must require parseable explicit replay denial and zero deltas. Corrected by the shared pure predicate.
- F-02: regression suite must behaviorally falsify load-bearing mutations. Corrected by evaluator-driven behavioural tests.
- F-03: boundary evidence must be load-bearing, including PID, syscall, phase, paths, and rename return value. Corrected by the shared pure predicate.
- F-04: RQ-13 syscall phase entry is inferred rather than register-proven. Non-blocking backlog.
- F-05: tracer non-syscall stops, decode errors, atomic ready writes, and renameat/renameat2 coverage. Non-blocking backlog.
- F-06: detach return evidence, ordering hygiene, and tracer stdout/stderr persistence. Non-blocking backlog.
- F-07: packaging/specification chronology issues. Non-blocking backlog.

No trusted-runtime change is authorized or included.
