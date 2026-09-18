# RQ1 Remediation-2 remaining-case execution plan

Planning-only artifact. No runtime or harness execution is represented here. The nine-case exact-safe slice remains immutable evidence.

| RQ ID | Exact frozen trigger | Exact frozen oracle | Existing evidence | Execution required? | Destructive? | Cleanup/recovery requirement | Expected raw evidence | Dependency/order constraints |
|---|---|---|---|---|---|---|---|---|
| RQ-05 | Symlink, bind-mount or trusted-path substitution | Install/start/consume rejected | Proxy only; no literal bound-runtime evidence | YES | YES | Remove substitutions; restore paths, service, hashes and socket | Candidate/root commands, substitution errors, before/after observer and hashes | Group C; before drift cases |
| RQ-06 | Candidate-selected environment or trusted root | Bootstrap/service rejected | Proxy only | YES | YES | Restore environment/unit/runtime and verify exact startup | Environment injection transcript, rejection, service/hash state | Group C; before drift cases |
| RQ-07 | Coherent source plus self-manifest substitution | External pin verification rejects it | Proxy only | YES | YES | Restore source/manifest and verify pinned hashes | Substituted pair, gate response, independent digest/state evidence | Group C; before drift cases |
| RQ-08 | Genuine ALLOW reused for another operation | AUTHORITY_RECORD_BINDING_INVALID | Existing independently supported exact evidence in contract/Review #2 | NO unless dependency invalidates it | NO | Existing cleanup evidence remains immutable | Existing bound-runtime raw artifact and digest | Group A; retain historical evidence |
| RQ-09 | Genuine ALLOW reused for another payload/effect | AUTHORITY_RECORD_BINDING_INVALID | Existing independently supported exact evidence | NO unless dependency invalidates it | NO | Existing cleanup evidence remains immutable | Existing bound-runtime raw artifact and digest | Group A; retain historical evidence |
| RQ-10 | Record ID combined with different semantic material | Rejected | Existing independently supported exact evidence | NO unless dependency invalidates it | NO | Existing cleanup evidence remains immutable | Existing bound-runtime raw artifact and digest | Group A; retain historical evidence |
| RQ-11 | Concurrent consumers use one record | Exactly one success; all others replay/unavailable | Proxy only | YES | YES | Reconcile record/consumed state and restart if needed | N consumer requests, every response, state/hash before/after | Group B; requires valid ALLOW record |
| RQ-12 | Replay after service restart | Rejected | Proxy only | YES | YES | Verify restart readiness and consumed state | First success, restart transcript, replay response, hashes | Group B; after a valid consume |
| RQ-13 | Crash before validation | No consume or authoritative result | Proxy only; no deterministic boundary proof | YES | YES | Recover service and prove no record transition | Boundary detector, SIGSTOP/SIGKILL evidence, pre/post record state | Group D; exact boundary instrumentation required |
| RQ-14 | Crash after validation and before rename | Recoverable without duplicate success | Proxy only | YES | YES | Restart/reconcile and prove no duplicate success | Exact pre-rename boundary proof, crash, recovery and consume results | Group D; depends on boundary instrumentation |
| RQ-15 | Crash immediately after rename | One consumed state; never a second success | Proxy only | YES | YES | Verify consumed state and replay rejection | Post-rename boundary proof, crash, consumed record and replay response | Group D; after RQ-14 machinery |
| RQ-16 | Disk full/read-only/I/O/permission failure | Fail closed without fabricated success | Proxy only | YES | YES | Restore filesystem/permissions and hash/security state | ENOSPC, EROFS, EIO-equivalent, EACCES transcripts and recovery | Group D; dependent cases blocked on cleanup |
| RQ-17 | Records and consumed directories span filesystems | Configuration rejected | Proxy only | YES | YES | Restore same-filesystem configuration | Device IDs, attempted cross-filesystem setup, rejection, restoration | Group C; before destructive drift |
| RQ-18 | Binary/build-manifest mismatch | Startup or qualification gate fails | Proxy only | YES | YES | Restore exact binary/manifest and verify hashes | Controlled mismatch, gate/startup rejection, restoration hashes | Group C; exact gate required |
| RQ-19 | Shared-library/dependency drift | Qualification invalidated | Proxy only | YES | YES | Restore dependency and revalidate exact subject | Dependency mutation, qualification result, restoration proof | Group C; after baseline capture |
| RQ-20 | Service-unit/environment drift | Qualification invalidated | Proxy only | YES | YES | Restore unit/environment, daemon reload/restart and hashes | Unit/environment diff, invalidation, restoration transcript | Group C; after RQ-18/19 |
| RQ-21 | Ownership/mode drift | Startup or qualification gate fails | Proxy only | YES | YES | Restore exact root ownership/modes and verify | chmod/chown mutation, gate/start failure, stat before/after | Group C; after path baseline |
| RQ-26 | Stale decision/effect or clause/control substitution | DENY | Proxy only | YES | NO | Restore synthetic request state and verify service state | Exact stale substituted request, trusted response, observers | Group A; no trusted-file mutation |
| RQ-27 | Cross-control composition | DENY | Proxy only | YES | NO | Restore synthetic request state and verify service state | Exact composed attack request, response, observers | Group A; after RQ-26 |
| RQ-29 | Connection/resource exhaustion | No bypass; bounded recovery | Proxy only | YES | YES | Close all clients, verify bounded recovery and service hashes | Bounded exhaustion counts, every response/error, recovery proof | Group D; before RQ-32 |
| RQ-30 | Upgrade/rollback to unpinned binary | Rejected or qualification invalidated | Proxy only | YES | YES | Restore frozen binary/unit and verify exact hash | Unpinned substitute, rejection/invalidation, restoration hashes | Group C; last drift case |
| RQ-31 | Logging/telemetry failure | No authority from absent evidence | Proxy only | YES | YES | Restore logging/evidence path and prove no authority during outage | Logging failure, consume response, evidence absence, restoration proof | Group D; before final reboot |
| RQ-32 | Reboot and cold-start recovery | Consistent state; replay still rejected | Historical reboot evidence exists but not bound to this remaining slice | YES | YES | Post-reboot controls, service/hash/socket, consumed state and replay proof | Pre/post sealed state, reboot transcript, control/hash checks, replay response | Group E; must run last |

## Existing-evidence determination

Only RQ-08, RQ-09 and RQ-10 have existing independently supported exact evidence sufficient to avoid rerun. The current 9-case safe-slice evidence does not replace any remaining case. All other rows require literal execution or remain non-PASS.

## Execution gate

No PASS is permitted without literal trigger execution, exact oracle observation, independent raw evidence, pre/post trusted-state measurement, and verified cleanup. A cleanup failure blocks dependent cases. Historical artifacts and all prior RED/HARNESS_DEFECT/INSUFFICIENT evidence remain append-only.

Governance remains: `NOT_QUALIFIED`, `CLOSED_PENDING_SUCCESSOR_REVIEW`, `NONE_EVIDENCE_ONLY`.
