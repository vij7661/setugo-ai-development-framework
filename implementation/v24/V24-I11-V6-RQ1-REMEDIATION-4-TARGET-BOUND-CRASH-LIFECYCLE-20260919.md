# V24-I11-V6 RQ1 Remediation 4: target-bound crash lifecycle

This harness-only remediation is based on `0ffef9e856974a1e774914e37ced74606edf4cf1`.
It does not modify the trusted service, protocol, filesystem permissions, or frozen RQ1 oracle.

## Frozen semantics

The authoritative plan and Remediation-2 contract define:

- RQ-13: crash before validation — “No consume or authoritative result”.
- RQ-14: crash after validation and before rename — “Recoverable without duplicate success”.
- RQ-15: crash immediately after rename — “One consumed state; never a second success”.

The documents do not state that a later legitimate recovery retry is forbidden. The harness therefore applies RQ-13's oracle to the interrupted attempt and observes recovery before retry; if the target remains in `records`, a subsequent single recovery consume and replay rejection are recorded separately. No global directory total is used as an oracle.

## Evidence lifecycle

Each case records baseline, prepared, recovery-before-retry, and final observer snapshots. The diagnostic's `trusted_record_id` defines the only target identity. Boundary paths must contain that exact record name. Target-specific membership and set deltas determine the result; historical unrelated entries are diagnostic only.

Observer errors, missing entries, malformed shapes, and inaccessible trusted directories are harness defects and cannot produce PASS or mechanism RED.
