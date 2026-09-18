# RQ1 Remediation 2 Oracle Implementation Contract
Planning-only artifact. No executable harness or runtime was modified.

| RQ ID | Exact frozen trigger | Exact frozen oracle | Current implementation | Claude #2 | Semantic status | Literal trigger? | Literal oracle proof? | Independent evidence? | Cleanup demonstrated? | Bound mutation? |
|---|---|---|---|---|---|---|---|---|---|---|
| RQ-01 | Candidate launches consume/service with loader interposition | Diagnostic-only DENY; no trusted state transition | loader | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-02 | Fake euid/filesystem/record/rename functions | No authority; trusted state unchanged | loader | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-03 | Candidate invokes root-control protocol | Kernel-derived peer rejection | candidate | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-04 | Candidate replaces socket before start or during restart | Fail closed; no candidate authority | socket | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-05 | Symlink, bind-mount or trusted-path substitution | Install/start/consume rejected | path | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-06 | Candidate-selected environment or trusted root | Bootstrap/service rejected | environment | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-07 | Coherent source plus self-manifest substitution | External pin verification rejects it | manifest | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-08 | Genuine ALLOW reused for another operation | AUTHORITY_RECORD_BINDING_INVALID | wrong-operation | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-09 | Genuine ALLOW reused for another payload/effect | AUTHORITY_RECORD_BINDING_INVALID | wrong-payload | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-10 | Record ID combined with different semantic material | Rejected | rebind | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-11 | Concurrent consumers use one record | Exactly one success; all others replay/unavailable | concurrency | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-12 | Replay after service restart | Rejected | replay-restart | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-13 | Crash before validation | No consume or authoritative result | crash-before | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-14 | Crash after validation and before rename | Recoverable without duplicate success | crash-mid | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-15 | Crash immediately after rename | One consumed state; never a second success | crash-after | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-16 | Disk full/read-only/I/O/permission failure | Fail closed without fabricated success | io-failure | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-17 | Records and consumed directories span filesystems | Configuration rejected | cross-filesystem | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-18 | Binary/build-manifest mismatch | Startup or qualification gate fails | binary-drift | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-19 | Shared-library/dependency drift | Qualification invalidated | dependency-drift | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-20 | Service-unit/environment drift | Qualification invalidated | unit-drift | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-21 | Ownership/mode drift | Startup or qualification gate fails | permission-drift | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-22 | Candidate ptrace/process injection | Denied by bound runtime controls | ptrace | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-23 | Candidate-created user/mount namespace | Cannot affect service or trusted paths | namespace | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-24 | DA-1 through deployed trusted consume | Authoritative DENY in evidence-only harness | da1 | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-25 | NCP-1 through deployed trusted consume | Authoritative DENY in evidence-only harness | ncp1 | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-26 | Stale decision/effect or clause/control substitution | DENY | stale-substitution | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-27 | Cross-control composition | DENY | composition | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | False |
| RQ-28 | Malformed/oversized/truncated/partial protocol | Fail closed; service remains recoverable | protocol | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-29 | Connection/resource exhaustion | No bypass; bounded recovery | exhaustion | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-30 | Upgrade/rollback to unpinned binary | Rejected or qualification invalidated | rollback | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-31 | Logging/telemetry failure | No authority from absent evidence | logging | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |
| RQ-32 | Reboot and cold-start recovery | Consistent state; replay still rejected | reboot | PENDING | CURRENT_IMPLEMENTATION_IS_PROXY | NO | NO | NO | NO | True |

Every row is conservatively classified CURRENT_IMPLEMENTATION_IS_PROXY until a literal bound-runtime trigger, oracle proof, independent raw artifact, and cleanup proof are demonstrated.