# V24-I11-V6 Runtime Qualification 1 — Preregistered Plan

Status: **PREREGISTERED / EXECUTION NOT STARTED / NOT QUALIFIED**

Scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`

Runtime qualification: `IN_PROGRESS_NOT_QUALIFIED`

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Phase identity and immutable predecessor

Phase ID: `V24-I11-V6-RUNTIME-QUALIFICATION-1`

Phase branch: `qualification/v24-i11-v6-runtime-qualification-1`

Immutable reviewed construction evidence:

- repository: `vij7661/setugo-ai-development-framework`;
- branch: `remediation/v24-i11-v6-successor-9`;
- commit: `c6304d0f14914c3b1e9f30a8a42ac231f152fa8f`;
- tree: `dc55289eff2294dbc172e41b045ec80b05d61299`;
- exact-final workflow run: `35352723840`;
- exact-final workflow job: `105624480838`;
- construction result: `338/338 PASS`;
- independent technical-review disposition: `PASS`;
- independent-review blocking findings: `NONE`.

The predecessor branch is frozen. This phase must not rewrite its commit, tree, historical RED evidence, failed workflow evidence, or manual-review record. Construction CI and manual-review PASS are entry evidence only; neither is runtime qualification.

## 2. Exact qualification subject

The subject is the Successor-9 trusted-consume mechanism deployed into one explicitly bound production-representative runtime:

- service ID: `V24-V6-TRUSTED-AUTHORITY-SERVICE`;
- service version: `3`;
- protocol: `V24-V6-S9-CONSUME/1`;
- consumption mode: `ROOT_PEER_SEMANTIC_ONE_SHOT`;
- authority record schema: `V24_V6_S8_AUTHORITY_RECORD_V1`;
- service binary SHA-256: `a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d`;
- service build-input SHA-256: `b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc`;
- gate binary SHA-256: `7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`;
- gate build-input SHA-256: `b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9`;
- external bootstrap commit: `af3ab8ab846119292a1b3a36fca5d0cc2c71b1ee`;
- external bootstrap tree: `fc063773b077c855cf34eebf28c886ee496d3fe9`;
- trusted root: `/opt/v24-v6-trusted-runtime`;
- trusted socket: `/run/v24-v6-authority/service.sock`;
- candidate identity: `v24candidate`.

Qualification, if later established, applies only to the exact subject and runtime binding. It does not transfer to another binary, bootstrap, image, kernel, unit, dependency set, filesystem topology, or operational procedure.

## 3. Scope

In scope:

1. exact artifact installation and startup provenance;
2. host identity, kernel and OS security boundary;
3. root/candidate identity and process-domain separation;
4. service-manager unit, environment and capability configuration;
5. socket ownership, permissions, creation and replacement resistance;
6. private record/consumed directories and same-filesystem atomic rename;
7. concurrent consume, replay, restart and reboot behavior;
8. crash/interruption recovery around validation and rename boundaries;
9. disk-full, read-only, permission-loss and I/O failure behavior;
10. namespace, mount, ptrace and process-injection restrictions;
11. bootstrap, update, rollback and drift invalidation;
12. evidence capture and audit completeness;
13. DA-1, NCP-1, loader, semantic-rebinding and replay attacks in the bound runtime;
14. preservation of all Successor-9 and inherited security regressions.

Out of scope:

- hostile-root or compromised-kernel resistance;
- distributed or multi-host consumption and replay resistance;
- remote-service security;
- production IAM/HSM/KMS custody unless separately bound and reviewed;
- real scientific execution or scientific WDPC outcomes;
- real authority-bearing external effects;
- general native-code memory-safety certification;
- any runtime other than the exact recorded qualification subject.

## 4. Trust assumptions requiring evidence

1. The host kernel, boot chain and root administrator are trusted.
2. The candidate cannot acquire UID 0 or equivalent capabilities.
3. The candidate cannot ptrace, inject into, debug, signal-control or replace the trusted service.
4. The candidate cannot modify the service unit, executable, libraries, bootstrap, trusted root, socket parent or private state directories.
5. The service and trusted caller are launched outside candidate-controlled environment and path selection.
6. The trusted caller obtains exact operation/reference/subject/context/boundary/payload material from a protected control source.
7. Record and consumed directories share one filesystem with measured atomic-rename semantics.
8. The kernel correctly enforces `SO_PEERCRED`, ownership, modes, namespaces and process credentials.
9. The identified SHA-256/OpenSSL and runtime dependencies behave as measured.
10. The pinned bootstrap authority remains independent from candidate-controlled source and manifests.
11. Runtime telemetry is evidence-only and cannot authorize an operation.
12. Candidate access to logs or diagnostics conveys no authority.

An assumption that cannot be evidenced is an entry failure or qualification failure. It must not be replaced with an undocumented fixture assumption.

## 5. Production/runtime evidence requirements

The evidence bundle must contain:

- immutable host or image identity and digest;
- OS, kernel, architecture and relevant kernel configuration;
- boot/security posture evidence where available;
- user and mount namespace policy;
- SELinux/AppArmor/seccomp/capability state, including explicit absence;
- exact service-manager unit and effective configuration;
- service account, groups, capabilities and process ancestry;
- effective service environment and loader/library resolution;
- installed bootstrap, binary, build-manifest and dependency hashes;
- ownership/mode evidence for every trusted path;
- socket parent/socket ownership and modes;
- private record/consumed directory ownership and modes;
- filesystem type, mount options and same-filesystem proof;
- candidate endpoint-denial and injection-denial transcripts;
- concurrency, restart, reboot, replay and crash-recovery transcripts;
- state reconciliation after interruption;
- update and rollback procedure with exact binding;
- drift-detection results for binary, dependency, unit, permission and kernel changes;
- complete raw logs plus machine-readable case results;
- exact qualification commit/tree and independent final-review disposition.

All tests use synthetic records and evidence-only sinks. Missing evidence is `NOT_VERIFIED` and prevents qualification when it is required by the subject.

## 6. Preregistered falsification matrix

| ID | Falsification case | Required fail-closed result |
|---|---|---|
| RQ-01 | Candidate launches consume/service with loader interposition | Diagnostic-only DENY; no trusted state transition |
| RQ-02 | Fake euid/filesystem/record/rename functions | No authority; trusted state unchanged |
| RQ-03 | Candidate invokes root-control protocol | Kernel-derived peer rejection |
| RQ-04 | Candidate replaces socket before start or during restart | Fail closed; no candidate authority |
| RQ-05 | Symlink, bind-mount or trusted-path substitution | Install/start/consume rejected |
| RQ-06 | Candidate-selected environment or trusted root | Bootstrap/service rejected |
| RQ-07 | Coherent source plus self-manifest substitution | External pin verification rejects it |
| RQ-08 | Genuine ALLOW reused for another operation | `AUTHORITY_RECORD_BINDING_INVALID` |
| RQ-09 | Genuine ALLOW reused for another payload/effect | `AUTHORITY_RECORD_BINDING_INVALID` |
| RQ-10 | Record ID combined with different semantic material | Rejected |
| RQ-11 | Concurrent consumers use one record | Exactly one success; all others replay/unavailable |
| RQ-12 | Replay after service restart | Rejected |
| RQ-13 | Crash before validation | No consume or authoritative result |
| RQ-14 | Crash after validation and before rename | Recoverable without duplicate success |
| RQ-15 | Crash immediately after rename | One consumed state; never a second success |
| RQ-16 | Disk full/read-only/I/O/permission failure | Fail closed without fabricated success |
| RQ-17 | Records and consumed directories span filesystems | Configuration rejected |
| RQ-18 | Binary/build-manifest mismatch | Startup or qualification gate fails |
| RQ-19 | Shared-library/dependency drift | Qualification invalidated |
| RQ-20 | Service-unit/environment drift | Qualification invalidated |
| RQ-21 | Ownership/mode drift | Startup or qualification gate fails |
| RQ-22 | Candidate ptrace/process injection | Denied by bound runtime controls |
| RQ-23 | Candidate-created user/mount namespace | Cannot affect service or trusted paths |
| RQ-24 | DA-1 through deployed trusted consume | Authoritative DENY in evidence-only harness |
| RQ-25 | NCP-1 through deployed trusted consume | Authoritative DENY in evidence-only harness |
| RQ-26 | Stale decision/effect or clause/control substitution | DENY |
| RQ-27 | Cross-control composition | DENY |
| RQ-28 | Malformed/oversized/truncated/partial protocol | Fail closed; service remains recoverable |
| RQ-29 | Connection/resource exhaustion | No bypass; bounded recovery |
| RQ-30 | Upgrade/rollback to unpinned binary | Rejected or qualification invalidated |
| RQ-31 | Logging/telemetry failure | No authority from absent evidence |
| RQ-32 | Reboot and cold-start recovery | Consistent state; replay still rejected |

Every genuine unexpected success is preserved as RED. Tests, threat assumptions and expected outcomes may not be weakened to obtain GREEN.

## 7. Exact entry criteria

Runtime execution is prohibited until all criteria are recorded as satisfied:

1. frozen predecessor commit/tree reverified;
2. phase branch ancestry verified from that exact commit;
3. this preregistration and subject binding committed before runtime tests;
4. exact service/gate/bootstrap/protocol/schema identities bound;
5. target host/image bound by immutable evidence;
6. runtime owner and evidence custodian identified;
7. trust assumptions explicitly accepted and measurable;
8. every falsification case has a deterministic oracle and evidence location;
9. synthetic/evidence-only sinks confirmed;
10. scientific execution asserted closed;
11. authority effect asserted `NONE_EVIDENCE_ONLY`;
12. phase state asserted `IN_PROGRESS_NOT_QUALIFIED`;
13. trusted and candidate identities independently provisioned;
14. required OS controls and filesystem semantics measurable;
15. Successor-9 and inherited regressions available unchanged;
16. historical RED and failed workflow evidence immutably bound;
17. independent final reviewer designated;
18. unavailable production dependencies are not silently replaced by fixtures.

Any unmet entry criterion stops execution. It is not a test failure and cannot be waived implicitly.

## 8. Execution stages after entry approval

1. bind target runtime and collect baseline evidence;
2. verify pinned bootstrap installation and exact provenance;
3. add permanent runtime falsification harnesses before positive controls;
4. run RQ-01 through RQ-32 and preserve all RED evidence;
5. run positive lifecycle/concurrency/recovery controls;
6. rerun all Successor-9 and inherited regressions unchanged;
7. freeze exact evidence head and raw evidence bundle;
8. obtain independent technical/manual review;
9. propose a bounded qualification disposition.

## 9. Exit and state-transition rule

The strongest permitted later disposition is `QUALIFIED_FOR_BOUND_RUNTIME`. It may be proposed only after all entry criteria, falsification cases, positive controls, regressions, evidence freeze and independent review succeed.

It applies only to the exact commit/tree, binaries, bootstrap, host/image, kernel, service unit, dependency set, filesystem topology and operating procedure. Material drift invalidates the disposition and returns the subject to `NOT_QUALIFIED` pending requalification.

This phase must not open scientific execution or change `authority_effect`. Qualification is not inferred from construction CI, manual-review PASS, code existence, an incomplete evidence bundle, or absence of observed failure.

## 10. Current phase boundary

At preregistration:

- runtime execution has not started;
- no runtime has been nominated or bound;
- no RQ case has been executed;
- runtime qualification is not claimed;
- scientific execution remains closed;
- authority effect remains evidence-only.
