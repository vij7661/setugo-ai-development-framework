# RQ1 Remediation-2 lifecycle root-cause record

This append-only record preserves the pre-repair failure and the narrow repair decision. It does not alter the frozen RQ1 oracle contract or any historical evidence.

## Starting state

- Target branch: `qualification/v24-i11-v6-runtime-qualification-1-remediation-2`
- Starting commit: `61676bbc90e6a64319fb43ef308908cc8539c121`
- Starting tree: `3f05ab9316b56f4aca692ac68f353821cafab85a`
- Historical failed workflow: `35401096885` (`bound-runtime-safe-exact` failed before the service hash check).

## Classification

**TEST_HARNESS_RACE**, with a service-unit readiness characteristic: the frozen service unit is `Type=simple`, so systemd reports the process active as soon as the executable is started. The service's `serve()` function then unlinks the old socket, creates and listens on the new socket, and only afterwards writes `service.pid`. The workflow previously tested `systemctl is-active` and the socket/PID invariants immediately after restart without waiting for that required sequence to complete.

This is not an installation or binary-integrity defect. The sealed bound-runtime diagnostic proves that, after startup settled, the service was active, the socket was a Unix listener owned by root, the PID file identified the root service process, and both `/proc/<pid>/exe` and the installed binary had the frozen hash.

## Independent sealed evidence

- VM artifact: `/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-remediation2-lifecycle-diagnostics-20260919T223000Z.txt`
- Artifact SHA-256: `22e1dd615312dfaebd8b8839532e1d8df28b5c50cffb46eae24c5b81870cad23`
- Sidecar SHA-256: `8436c892b0fe8cac7b18c599893c4dd8f3bbc72b156dad05c03392785376b269`
- The failed run remains historical; no prior transcript or result is overwritten.

## Source-level sequence

In `governance-runtime/native/v24_v6_trusted_authority_service.c` (`serve()`):

1. `unlink(SOCKET_PATH)`;
2. `bind()`;
3. `chown()`/`chmod()` and `listen()`;
4. `fopen(PID_PATH, "w")`, write the process ID, then root ownership and mode `0444`;
5. enter the accept loop.

The previous check could observe the systemd active state between steps 1 and 4. The repair therefore leaves the service binary and unit semantics unchanged and adds a bounded readiness loop that accepts success only when all original invariants hold simultaneously: active service, Unix socket, PID file, root PID whose executable and hash match the frozen service, root-owned runtime/socket/binary, and candidate separation.

## Repair boundary

Only `.github/workflows/v24-v6-rq1-remediation2-safe-exact.yml` is changed for the repair. The loop is bounded and diagnostic; timeout remains a failure (`ready=false`) and cannot produce a case PASS. The exact safe slice runs only when the complete original invariant set is observed.

Runtime qualification remains `NOT_QUALIFIED`; scientific execution remains `CLOSED_PENDING_SUCCESSOR_REVIEW`; authority effect remains `NONE_EVIDENCE_ONLY`.
