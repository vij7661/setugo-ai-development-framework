# Remediation-2 run 35402121615 adjudication

This append-only record is based on the preserved bound-runtime directory for commit `c34e22f643c647bd8138a5fd65173aa5b0e44589` and artifact `10571436390` (ZIP SHA-256 `a03ca497e0b61ce31b1a0a0118b838facf6b7639fa90cd8f3dfd2c9de6c47778`). It does not rewrite the run.

## Readiness invariant table

| Invariant | Observed value | Expected | Result | Evidence |
|---|---|---|---|---|
| systemd active | `active` | active | PASS | `preflight.txt`, `systemctl status` |
| socket exists/type | root-owned Unix socket | S_IFSOCK | PASS | `preflight.txt`, runtime listing |
| socket owner/mode | `root:root 0666` | root-owned socket | PASS | `preflight.txt` |
| socket parent | `root:root 0755` | root-owned parent | PASS | `preflight.txt` |
| PID file | present, `6367` | regular file | PASS | `preflight.txt` |
| PID versus systemd MainPID | both `6367` | equal | PASS | status/PID evidence |
| process UID/GID | `0/0` | root/root | PASS | `/proc/6367/status` evidence |
| process executable | path/hash exact when privileged | frozen path and `a9567e...b021d` | PASS | status and binary evidence |
| installed binary | `root:root`, mode `0555`, exact hash | frozen root-owned non-writable binary | PASS semantically; workflow check FAIL | `preflight.txt` shows `-r-xr-xr-x`; loop incorrectly required `0755` |
| `/proc/<pid>/exe` loop probe | unprivileged `readlink`/`sha256sum` cannot read proc executable | exact path/hash | FAIL in loop | direct SSH probe: permission denied; loop omitted `sudo` |
| candidate UID | `2002` | non-root | PASS | `preflight.txt` |
| candidate signal | denied on all 30 attempts | denied | PASS | `preflight.txt` |

### Readiness conclusion

`bound_ready=false` is caused by two workflow invariant-check defects, not by the service: the loop required binary mode `0755` while the frozen installed subject is intentionally non-writable `0555`, and it attempted to read `/proc/6367/exe` and hash it without `sudo`, producing empty/unreadable values for the runner user. The narrow repair is to require `0555`, use privileged reads for the root process identity, and explicitly compare the PID file with systemd `MainPID`.

## Nine-case table

| RQ | Status in run | Frozen oracle | Actual observation | Classification | Next repair |
|---|---|---|---|---|---|
| RQ-01 | RED | diagnostic-only DENY; no trusted state transition | unittest import failed: loader module absent; service state stable | INFRASTRUCTURE_DEFECT | stage the frozen loader regression into a candidate-readable temporary path and execute it by path |
| RQ-02 | RED | no authority; trusted state unchanged | same absent loader module; no trigger ran; state stable | INFRASTRUCTURE_DEFECT | same staged-regression repair; do not treat import failure as oracle evidence |
| RQ-03 | RED | kernel-derived peer rejection | candidate UID 2002; request reset; `SO_PEERCRED` strace attach itself denied; no peer proof | HARNESS_DEFECT | use a valid protocol request and independent peer-credential observation; preserve state proof |
| RQ-04 | RED | fail closed; no candidate authority | candidate unlink/bind denied; trusted socket restored; restart returned rc=1 without stderr capture | HARNESS_DEFECT | capture restart stdout/stderr and prove post-restart socket/PID/hash state; do not treat connect denial alone as PASS |
| RQ-22 | PASS | ptrace denied by bound controls | actual service PID 6367; `ptrace` rc -1, errno 1; state stable | SUPPORTED_PASS | retain; independent before/after observer evidence present |
| RQ-23 | PASS | candidate namespace cannot affect service/trusted paths | `unshare` denied EPERM; before/after service hash stable | SUPPORTED_PASS | retain; state evidence proves no trusted-path mutation |
| RQ-24 | HARNESS_DEFECT | DA-1 authoritative DENY | diagnostic creation failed because candidate could not import trusted-control module | HARNESS_DEFECT | stage required diagnostic client modules candidate-readably; execute deployed root consume |
| RQ-25 | HARNESS_DEFECT | NCP-1 authoritative DENY | same module import failure | HARNESS_DEFECT | same staged-module repair, with NCP-specific raw request evidence |
| RQ-28 | RED | malformed/oversized/truncated/partial fail closed; service recoverable | four variants closed/reset and state stable, but harness process returned failure and omitted return-code/raw transport classification | HARNESS_DEFECT | catch expected reset/EOF per variant, record each response and process rc, then evaluate exact oracle |

Run totals remain 2 PASS / 5 RED / 2 HARNESS_DEFECT; no RED is being relabelled as PASS.

Governance remains `NOT_QUALIFIED`, `CLOSED_PENDING_SUCCESSOR_REVIEW`, `NONE_EVIDENCE_ONLY`.
