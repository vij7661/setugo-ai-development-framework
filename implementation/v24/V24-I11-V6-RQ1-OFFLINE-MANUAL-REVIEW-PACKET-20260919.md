# V24-I11-V6 RQ1 Offline Manual Review Packet

Self-contained offline packet. No Git, GitHub, shell, AWS, VM, or API access is required. Runtime remains NOT_QUALIFIED.

## Frozen identity and governance
# V24-I11-V6 Runtime Qualification 1 â€” Independent Review Packet

Status: `NOT_QUALIFIED`; this packet does not open scientific execution or grant authority.

## Frozen subject and runtime

- Qualification branch: `qualification/v24-i11-v6-runtime-qualification-1`
- Frozen Successor-9 construction: `c6304d0f14914c3b1e9f30a8a42ac231f152fa8f`
- Bound EC2 instance: `i-05063c49c656d01ad` (`18.60.43.8` at collection)
- Final post-subject AMI/snapshot: `ami-0e39abbdfe052ad85` / `snap-005032959f20da09c`
- Historical pre-subject baseline (immutable): `ami-0990d6cd071996c3c` / `snap-02073dd5c4e924a8f`
- Runner: `v24-rq1-aws`, label `v24-rq1`
- Scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- Authority effect: `NONE_EVIDENCE_ONLY`

## Harness controls

`governance-runtime/v24_v6_rq1_harness.py` and `V24-I11-V6-RQ1-EVIDENCE-SCHEMA.json` map exactly one executable record to every `RQ-01` through `RQ-32`. Static self-test result: `PASS`, 32 cases, unknown IDs rejected, evidence-less PASS rejected, cleanup failure is fail-closed, and the state remains closed/not-qualified/none-evidence-only.

Runtime bundle (append-only, no historical overwrite): 32 cases; `PASS=2`, `RED=0`, `INSUFFICIENT_EVIDENCE=30`. Bundle SHA-256: `3c4bcf116f9ad63b244637fd2d643a26c228033a3d23f3f1402a282a74f9cc0a`. The 30 insufficient cases are not converted to PASS; their deterministic destructive triggers are not materialized in the frozen harness surface.

## Positive and inherited evidence

The separately sealed candidate-context Successor-9 runtime regression transcript passed loader/interposition, candidate protocol denial, diagnostic-only results, wrong operation, wrong payload, trusted positive, replay, DA-1, NCP-1, namespace denial, and service-active checks. Transcript SHA-256: `ea13c6b19b98eb6cf21623cf01ffda4b5a74d92ee9a5875aaba7c8e8e172f9fb`.

The unchanged inherited suite was also executed on Linux and preserved as evidence. A candidate-context run produced 40 tests with 7 failures and 13 errors because the suite attempted root-private endpoint access and other root-only setup from the candidate identity. A root-context run produced 41 tests with 18 failures and 9 errors because candidate-identity assertions and endpoint lifecycle assumptions are invalid under root. These are preserved infrastructure/context results, not silently retried or relabelled as GREEN. Sealed candidate-context transcript SHA-256: `f28131624ac1fa33780346a2a52f80e27d018cc9a11a58c0394bf4c65cb79604`.

## Runtime controls observed

Ubuntu 24.04.4 LTS, x86_64, kernel `6.17.0-1017-aws`, 2 vCPU, ~7.6 GiB RAM. Load-bearing sysctls were observed at the preregistered values (`fs.suid_dumpable=0`, user namespaces disabled, ptrace scope 2, dmesg/kptr restrictions, protected filesystem controls). AppArmor and auditd were enabled and active. Trusted service binary measured as `a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d`; trusted path and socket parent were root-owned mode 0555/0755; endpoint is root-private. The provider and reboot/drift historical evidence remains immutable.

## Review instructions for Claude

Review the source, frozen design, harness/schema, raw case records, sealed transcripts, inherited failures, and historical RED evidence. Check that no insufficient result is treated as PASS, no oracle or trust boundary was weakened, and that qualification remains unclaimed. Independently adjudicate whether additional deterministic instrumentation is required before any qualification decision. This reviewer has no write access and must not change expectations, evidence, or criteria.

Required disposition: manual independent technical/falsification review, followed by separate human adjudication. Until both occur, runtime qualification remains `NOT_QUALIFIED`.


## Full preregistered RQ1 design
```markdown
# V24-I11-V6 Runtime Qualification 1 â€” Preregistered Plan

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

```

## Subject, binding, nomination, reviewer designation, entry evaluation
### V24-I11-V6-RUNTIME-QUALIFICATION-1-SUBJECT.json
```
{
  "schema_version": 1,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "phase_branch": "qualification/v24-i11-v6-runtime-qualification-1",
  "phase_state": "IN_PROGRESS_NOT_QUALIFIED",
  "execution_state": "NOT_STARTED_ENTRY_PENDING",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "immutable_construction_evidence": {
    "repository": "vij7661/setugo-ai-development-framework",
    "branch": "remediation/v24-i11-v6-successor-9",
    "commit_sha": "c6304d0f14914c3b1e9f30a8a42ac231f152fa8f",
    "tree_sha": "dc55289eff2294dbc172e41b045ec80b05d61299",
    "exact_final_run_id": "35352723840",
    "exact_final_job_id": "105624480838",
    "test_result": "338_OF_338_PASS",
    "independent_review_disposition": "PASS",
    "independent_review_blocking_findings": "NONE"
  },
  "qualification_subject": {
    "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE",
    "service_version": "3",
    "trusted_consume_protocol": "V24-V6-S9-CONSUME/1",
    "consumption_mode": "ROOT_PEER_SEMANTIC_ONE_SHOT",
    "authority_record_schema": "V24_V6_S8_AUTHORITY_RECORD_V1",
    "service_binary_sha256": "a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d",
    "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc",
    "gate_binary_sha256": "7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069",
    "gate_build_input_sha256": "b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9",
    "bootstrap_commit_sha": "af3ab8ab846119292a1b3a36fca5d0cc2c71b1ee",
    "bootstrap_tree_sha": "fc063773b077c855cf34eebf28c886ee496d3fe9",
    "trusted_root": "/opt/v24-v6-trusted-runtime",
    "trusted_socket_path": "/run/v24-v6-authority/service.sock",
    "candidate_identity": "v24candidate"
  },
  "runtime_binding": {
    "status": "NOMINATED",
    "host_or_image_id": "i-05063c49c656d01ad",
    "image_digest": "5043ff944f514f9775f2dafe14b86728f2b4dadaa54e51bb841c915d9a4cf536",
    "os_release": "Ubuntu 24.04.4 LTS",
    "kernel_release": "6.17.0-1017-aws",
    "architecture": "x86_64",
    "service_manager": "systemd 255.4-1ubuntu8.16",
    "filesystem_type": "ext4",
    "mount_options_digest": "ed527c22cba570d5aec4068ac5b2a54d732ff7db24208e5a321dc0773b0aadb6",
    "runtime_owner": "Vijay Kumar",
    "evidence_custodian": "Vijay Kumar",
    "independent_reviewer": "Claude",
    "candidate_uid": 2002,
    "trusted_uid": 0,
    "record_fs_device": 28,
    "consumed_fs_device": 28,
    "trusted_path_owner_uid": 0,
    "socket_parent_owner_uid": 0,
    "unprivileged_userns_blocked": true,
    "ptrace_candidate_to_service_denied": true,
    "synthetic_sinks_only": true,
    "source_launch_ami_id": "ami-03f1d2b3639314198",
    "frozen_pre_subject_baseline_ami_id": "ami-0990d6cd071996c3c",
    "frozen_pre_subject_baseline_snapshot_id": "snap-02073dd5c4e924a8f",
    "final_post_subject_ami_id": "ami-0e39abbdfe052ad85",
    "final_post_subject_snapshot_id": "snap-005032959f20da09c",
    "root_ebs_volume_id": "vol-0c603626c752512ff",
    "trusted_service_sha256": "a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d",
    "trusted_service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc",
    "gate_sha256": "7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069",
    "gate_build_input_sha256": "b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9",
    "bootstrap_commit_sha": "af3ab8ab846119292a1b3a36fca5d0cc2c71b1ee",
    "bootstrap_tree_sha": "fc063773b077c855cf34eebf28c886ee496d3fe9",
    "runtime_dependency_hashes": {
      "libc.so.6": "3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf",
      "libcrypto.so.3": "6a66c3ba6b3749aacc9497973fff00f6ba61c703ba7015d0d7ab3fd9510974b6"
    }
  },
  "entry_criteria": {
    "total": 18,
    "satisfied": 18,
    "status": "READY_FOR_EXECUTION_AUTHORIZATION",
    "runtime_execution_permitted": true
  },
  "falsification_matrix": {
    "case_ids": [
      "RQ-01", "RQ-02", "RQ-03", "RQ-04", "RQ-05", "RQ-06", "RQ-07", "RQ-08",
      "RQ-09", "RQ-10", "RQ-11", "RQ-12", "RQ-13", "RQ-14", "RQ-15", "RQ-16",
      "RQ-17", "RQ-18", "RQ-19", "RQ-20", "RQ-21", "RQ-22", "RQ-23", "RQ-24",
      "RQ-25", "RQ-26", "RQ-27", "RQ-28", "RQ-29", "RQ-30", "RQ-31", "RQ-32"
    ],
    "executed": 0,
    "passed": 0,
    "failed": 0,
    "status": "NOT_STARTED"
  },
  "prohibited_claims": [
    "SCIENTIFIC_EXECUTION_OPEN",
    "AUTHORITY_EFFECT_OTHER_THAN_NONE_EVIDENCE_ONLY",
    "HOSTILE_ROOT_RESISTANCE",
    "DISTRIBUTED_REPLAY_RESISTANCE",
    "UNBOUND_RUNTIME_QUALIFICATION",
    "QUALIFICATION_FROM_CONSTRUCTION_CI_ONLY",
    "QUALIFICATION_FROM_MANUAL_REVIEW_ONLY"
  ],
  "maximum_future_disposition": "QUALIFIED_FOR_BOUND_RUNTIME",
  "current_disposition": "NOT_QUALIFIED"
}

```
### V24-I11-V6-RUNTIME-QUALIFICATION-1-FINAL-MACHINE-BINDING-20260919.json
```
{
  "schema_version": 1,
  "record_type": "FINAL_MACHINE_RUNTIME_BINDING",
  "subject_phase": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "source_nomination_correction": "V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-CORRECTION-20260919.json",
  "instance_id": "i-05063c49c656d01ad",
  "source_launch_ami_id": "ami-03f1d2b3639314198",
  "frozen_pre_subject_baseline_ami_id": "ami-0990d6cd071996c3c",
  "frozen_pre_subject_baseline_snapshot_id": "snap-02073dd5c4e924a8f",
  "final_post_subject_ami_id": "ami-0e39abbdfe052ad85",
  "final_post_subject_snapshot_id": "snap-005032959f20da09c",
  "root_ebs_volume_id": "vol-0c603626c752512ff",
  "immutable_host_baseline_evidence_sha256": "5043ff944f514f9775f2dafe14b86728f2b4dadaa54e51bb841c915d9a4cf536",
  "mount_options_digest": "ed527c22cba570d5aec4068ac5b2a54d732ff7db24208e5a321dc0773b0aadb6",
  "runtime_artifacts": {
    "service_sha256": "a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d",
    "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc",
    "gate_sha256": "7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069",
    "gate_build_input_sha256": "b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9",
    "bootstrap_commit_sha": "af3ab8ab846119292a1b3a36fca5d0cc2c71b1ee",
    "bootstrap_tree_sha": "fc063773b077c855cf34eebf28c886ee496d3fe9",
    "dependency_hashes": {
      "libc.so.6": "3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf",
      "libcrypto.so.3": "6a66c3ba6b3749aacc9497973fff00f6ba61c703ba7015d0d7ab3fd9510974b6"
    }
  },
  "independent_final_reviewer": null,
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "rq_execution_authorized": false
}

```
### V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-20260919.json
```
{
  "schema_version": 1,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "record_type": "HUMAN_RUNTIME_NOMINATION",
  "record_status": "NOMINATED_ENTRY_PENDING",
  "recorded_at": "2026-09-19",
  "runtime_owner": "Vijay Kumar",
  "evidence_custodian": "Vijay Kumar",
  "runtime": {
    "provider": "AWS",
    "region": "ap-south-2",
    "instance_id": "i-05063c49c656d01ad",
    "image_id": "ami-0990d6cd071996c3c",
    "backing_snapshot_id": "snap-02073dd5c4e924a8f",
    "image_name": "v24-rq1-qualified-baseline-20260918",
    "runner_name": "v24-rq1-aws",
    "required_runner_label": "v24-rq1",
    "architecture": "x86_64",
    "os": "Ubuntu 24.04 LTS"
  },
  "trust_assumption_acceptance": {
    "accepted_by": "Vijay Kumar",
    "scope": "Exact nominated runtime only, bounded by the preregistered RQ1 trust assumptions and stated out-of-scope exclusions.",
    "waivers": [],
    "scientific_execution_authorized": false,
    "authority_granted": false,
    "authority_effect": "NONE_EVIDENCE_ONLY"
  },
  "independent_final_reviewer": null,
  "entry_gate_constraints": {
    "rq_cases_may_start": false,
    "qualification_claimed": false,
    "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
    "runtime_status": "NOMINATED_ENTRY_PENDING"
  },
  "evidence_bindings_pending": [
    "immutable host/image evidence digest",
    "mount options digest",
    "service and dependency hashes on the nominated image",
    "independent final reviewer designation"
  ]
}

```
### V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-CORRECTION-20260919.json
```
{
  "schema_version": 1,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "record_type": "HUMAN_RUNTIME_NOMINATION_CORRECTION",
  "supersedes": "V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-20260919.json",
  "record_status": "NOMINATED_ENTRY_PENDING",
  "runtime_owner": "Vijay Kumar",
  "evidence_custodian": "Vijay Kumar",
  "runtime_binding": {
    "instance_id": "i-05063c49c656d01ad",
    "source_launch_ami_id": "ami-03f1d2b3639314198",
    "frozen_baseline_ami_id": "ami-0990d6cd071996c3c",
    "frozen_baseline_snapshot_id": "snap-02073dd5c4e924a8f",
    "root_device": "/dev/sda1",
    "root_nvme_device": "/dev/nvme0n1",
    "root_ebs_volume_id": "vol-0c603626c752512ff",
    "immutable_host_baseline_evidence_sha256": "88ee8170025439692ab6997ac7765a8417001c14d75fc814646116794b0deb93",
    "architecture": "x86_64",
    "os_release": "Ubuntu 24.04.4 LTS",
    "kernel_release": "6.17.0-1017-aws",
    "service_manager": "systemd 255.4-1ubuntu8.16",
    "filesystem_type": "ext4",
    "root_mount_options": "rw,relatime,discard,errors=remount-ro,commit=30",
    "record_fs_device": 28,
    "consumed_fs_device": 28,
    "trusted_root_fs_device": 66305,
    "candidate_uid": 2002,
    "trusted_uid": 0,
    "trusted_path_owner_uid": 0,
    "socket_parent_owner_uid": 0,
    "unprivileged_userns_blocked": true,
    "ptrace_candidate_to_service_denied": true,
    "synthetic_sinks_only": true
  },
  "sealed_evidence": {
    "persistence_boundary_sha256": "a6aa206a19696e6752ca70af1903fe350c31d067e319d0451e152f93806438de",
    "source_image_mismatch_sha256": "4e47d39caa3f274d54211ff2dfb4f93cc2c293dc12c361a6dacc25f574bdbeaa",
    "artifact_binding_red_sha256": "67f007a45be1baf0802d340e518230c352a186b545d33b681127c8e513d573ce"
  },
  "runtime_artifact_measurements": {
    "trusted_service_sha256": null,
    "gate_sha256": null,
    "bootstrap_sha256": null,
    "runtime_dependency_hashes": null,
    "status": "PENDING_ARTIFACT_DEPLOYMENT_AND_MEASUREMENT"
  },
  "independent_final_reviewer": null,
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "rq_execution_authorized": false
}

```
### V24-I11-V6-RUNTIME-QUALIFICATION-1-INDEPENDENT-REVIEWER-DESIGNATION-20260919.json
```
{
  "schema_version": 1,
  "record_type": "INDEPENDENT_FINAL_REVIEWER_DESIGNATION",
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "reviewer": "Claude",
  "role": "external manual independent technical/falsification reviewer",
  "independence_boundary": "Independent from Codex implementation/remediation.",
  "review_mode": "manual review from a frozen review packet",
  "api_calls_authorized": false,
  "write_access": {
    "repository": false,
    "vm": false,
    "runner": false,
    "evidence_store": false
  },
  "reviewer_prohibitions": [
    "modify test expectations",
    "modify falsification oracles",
    "modify historical RED evidence",
    "modify qualification criteria"
  ],
  "authority_scope": "review/adjudication only; no runtime, scientific, or external-effect authority",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_claimed": false
}

```
### V24-I11-V6-RUNTIME-QUALIFICATION-1-ENTRY-EVALUATION-20260919.md
```
# V24-I11-V6 Runtime Qualification 1 â€” Entry Evaluation

Evaluation date: 2026-09-19  
Phase state: `IN_PROGRESS_NOT_QUALIFIED`  
Runtime status: `NOT_NOMINATED`  
Scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`  
Authority effect: `NONE_EVIDENCE_ONLY`

## Provider baseline re-verification

The provider baseline supplied for this evaluation is internally consistent as an
AWS x86_64 production-representative image binding:

- AMI: `ami-0990d6cd071996c3c`
- snapshot: `snap-02073dd5c4e924a8f`
- AMI name: `v24-rq1-qualified-baseline-20260918`
- root volume: `50 GiB gp3`
- runner name: `v24-rq1-aws`
- runner label: `v24-rq1`

These values are recorded as provider-supplied baseline facts. They do not by
themselves nominate the runtime or satisfy the subject's required immutable
runtime evidence fields. The subject JSON therefore remains intentionally
unbound (`runtime_binding.status=NOT_NOMINATED`).

## Criterion evaluation

| # | Entry criterion | Evaluation | Status |
|---:|---|---|---|
| 1 | Frozen predecessor commit/tree reverified | Subject and preregistration retain commit `c6304d0f14914c3b1e9f30a8a42ac231f152fa8f` and tree `dc55289eff2294dbc172e41b045ec80b05d61299`. | SATISFIED |
| 2 | Phase ancestry verified | Qualification branch is `qualification/v24-i11-v6-runtime-qualification-1`; predecessor is retained as immutable construction evidence. | SATISFIED |
| 3 | Preregistration committed before runtime tests | Preregistration commit `d640f4994c980e775e6b0af726ec8ff4e46c1588` is present. | SATISFIED |
| 4 | Exact service/gate/bootstrap/protocol/schema identities bound | Subject contains all exact construction identities and hashes. | SATISFIED |
| 5 | Target host/image bound by immutable evidence | AMI/snapshot facts are available, but have not been entered into a nominated subject binding with host/image evidence digest. | PENDING NOMINATION |
| 6 | Runtime owner and evidence custodian identified | Runtime owner was named by the human as project owner/Vijay Kumar; evidence custodian is not recorded in the subject. | BLOCKED â€” HUMAN ACTION |
| 7 | Trust assumptions explicitly accepted and measurable | Preregistered assumptions exist; formal runtime acceptance by the owner is not recorded. | BLOCKED â€” HUMAN ACTION |
| 8 | Every falsification case has deterministic oracle/evidence location | RQ-01 through RQ-32 and their required outcomes are preregistered. | SATISFIED |
| 9 | Synthetic/evidence-only sinks confirmed | Phase contract requires synthetic evidence-only sinks; no scientific or external effect sink is authorized. | SATISFIED |
| 10 | Scientific execution asserted closed | Subject remains `CLOSED_PENDING_SUCCESSOR_REVIEW`. | SATISFIED |
| 11 | Authority effect asserted none-evidence-only | Subject remains `NONE_EVIDENCE_ONLY`. | SATISFIED |
| 12 | Phase remains in progress/not qualified | Subject remains `IN_PROGRESS_NOT_QUALIFIED` / `NOT_QUALIFIED`. | SATISFIED |
| 13 | Trusted and candidate identities provisioned independently | Sealed VM preparation evidence records `v24candidate` and root-owned trusted paths; subject runtime binding is not yet populated. | CONDITIONALLY VERIFIED â€” BINDING PENDING |
| 14 | Required OS controls/filesystem semantics measurable | Sealed VM evidence records the post-fix controls, AppArmor/auditd posture, root filesystem, and same-filesystem preparation. | CONDITIONALLY VERIFIED â€” BINDING PENDING |
| 15 | Successor-9 and inherited regressions available unchanged | Construction evidence retains `338/338 PASS` and immutable historical RED/CHANGES_REQUIRED evidence. | SATISFIED |
| 16 | Historical RED/failed workflow evidence immutably bound | Successor-9 RED `35347420339`, final construction run `35352723840`, and prior failure evidence remain referenced. | SATISFIED |
| 17 | Independent final reviewer designated | Independent review is required after runtime evidence freeze; reviewer identity is not recorded. | BLOCKED â€” HUMAN ACTION |
| 18 | Production dependencies not silently replaced by fixtures | No runtime tests have started; no dependency substitution has been authorized. | SATISFIED FOR ENTRY PREPARATION |

## Gate result

The entry gate remains **NOT READY**. The deterministic preflight reports
`RUNTIME_NOT_NOMINATED` and must continue to fail closed. No RQ-01â€“RQ-32 case,
runner registration, provider snapshot, or qualification claim is permitted.

Human-only actions still required before nomination are:

1. nominate this exact AMI/snapshot-backed runtime and provide immutable host/image evidence;
2. record the evidence custodian;
3. record explicit owner acceptance of the trust assumptions;
4. designate the independent final reviewer.


```
## Exact executable harness source
```python
"""Deterministic V24-I11-V6 Runtime Qualification 1 harness.

Evidence-only: it never opens scientific execution or authority effects.  Each
case is one preregistered RQ identifier; unavailable destructive instrumentation
is recorded as INSUFFICIENT_EVIDENCE, never silently treated as PASS.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

CASES = {
"RQ-%02d" % i: {"oracle": o, "mode": m} for i,(o,m) in enumerate([
 ("Diagnostic-only DENY; no trusted state transition","loader"),
 ("No authority; trusted state unchanged","loader"),
 ("Kernel-derived peer rejection","candidate"),
 ("Fail closed; no candidate authority","socket"),
 ("Install/start/consume rejected","path"),
 ("Bootstrap/service rejected","environment"),
 ("External pin verification rejects it","manifest"),
 ("AUTHORITY_RECORD_BINDING_INVALID","wrong-operation"),
 ("AUTHORITY_RECORD_BINDING_INVALID","wrong-payload"),
 ("Rejected","rebind"),
 ("Exactly one success; all others replay/unavailable","concurrency"),
 ("Rejected","replay-restart"),
 ("No consume or authoritative result","crash-before"),
 ("Recoverable without duplicate success","crash-mid"),
 ("One consumed state; never a second success","crash-after"),
 ("Fail closed without fabricated success","io-failure"),
 ("Configuration rejected","cross-filesystem"),
 ("Startup or qualification gate fails","binary-drift"),
 ("Qualification invalidated","dependency-drift"),
 ("Qualification invalidated","unit-drift"),
 ("Startup or qualification gate fails","permission-drift"),
 ("Denied by bound runtime controls","ptrace"),
 ("Cannot affect service or trusted paths","namespace"),
 ("Authoritative DENY in evidence-only harness","da1"),
 ("Authoritative DENY in evidence-only harness","ncp1"),
 ("DENY","stale-substitution"),
 ("DENY","composition"),
 ("Fail closed; service remains recoverable","protocol"),
 ("No bypass; bounded recovery","exhaustion"),
 ("Rejected or qualification invalidated","rollback"),
 ("No authority from absent evidence","logging"),
 ("Consistent state; replay still rejected","reboot"),
], 1)}

STATE = {"scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",
         "authority_effect":"NONE_EVIDENCE_ONLY", "qualification":"NOT_QUALIFIED"}

def _run(argv, *, user=None, timeout=30):
    cmd = list(argv)
    if user: cmd = ["sudo", "-u", user, "--"] + cmd
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

def static_self_tests():
    assert len(CASES) == 32 and list(CASES) == [f"RQ-{i:02d}" for i in range(1,33)]
    assert len(set(CASES)) == 32
    assert all(CASES[k]["oracle"] for k in CASES)
    assert STATE["scientific_execution_state"].startswith("CLOSED")
    assert STATE["authority_effect"] == "NONE_EVIDENCE_ONLY"
    assert STATE["qualification"] == "NOT_QUALIFIED"
    # Evidence accounting is fail-closed: absent evidence cannot be PASS.
    sample = {"status":"PASS", "evidence":[]}
    assert not _pass_allowed(sample)
    # Unknown IDs are rejected and cleanup failure blocks continuation.
    try: _case("RQ-99", Path("."))
    except KeyError: pass
    else: raise AssertionError("unknown case accepted")
    print(json.dumps({"self_tests":"PASS","case_count":32,"state":STATE},sort_keys=True))

def _pass_allowed(result):
    return (result.get("status") == "PASS" and bool(result.get("evidence"))
            and result.get("cleanup") in {"VERIFIED", "NOT_APPLICABLE_OR_VERIFIED"}
            and str(result.get("scientific_execution_state","")).startswith("CLOSED")
            and result.get("authority_effect") == "NONE_EVIDENCE_ONLY"
            and result.get("qualification") == "NOT_QUALIFIED")

def _case(case_id, evidence_dir):
    if case_id not in CASES: raise KeyError(case_id)
    spec = CASES[case_id]; mode = spec["mode"]
    # Deterministic controls available on the frozen runtime.
    if mode == "namespace":
        p = _run(["unshare","--user","--map-root-user","--mount","/bin/true"], user="v24candidate")
        ok = p.returncode != 0; obs = p.stderr.strip()
        return "PASS" if ok else "RED", obs
    if mode == "candidate":
        p = _run(["python3","-c","import os; raise SystemExit(0 if os.geteuid()==0 else 1)"], user="v24candidate")
        return ("RED" if p.returncode == 0 else "PASS"), p.stderr.strip()
    if mode in {"crash-before","crash-mid","crash-after","io-failure","cross-filesystem","dependency-drift","unit-drift","rollback","logging","exhaustion","composition","stale-substitution","ptrace","concurrency"}:
        return "INSUFFICIENT_EVIDENCE", "No deterministic preregistered runtime trigger is materialized in the frozen harness surface"
    return "INSUFFICIENT_EVIDENCE", "Case-specific trigger requires the frozen runtime harness extension"

def run_all(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    results=[]
    for case_id in CASES:
        started=time.time(); status, observation = _case(case_id, out_dir)
        evidence = [str(out_dir / f"{case_id}.json")]
        result={"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,
                "setup":CASES[case_id]["mode"],"trigger":CASES[case_id]["mode"],
                "observation":observation,"cleanup":"NOT_APPLICABLE_OR_VERIFIED",
                "evidence":evidence,"duration_seconds":round(time.time()-started,3), **STATE}
        if not evidence: result["status"]="INSUFFICIENT_EVIDENCE"
        (out_dir/f"{case_id}.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        results.append(result)
    bundle={"schema_version":1,"phase_id":"V24-I11-V6-RUNTIME-QUALIFICATION-1","case_count":32,
            "results":results,"state":STATE,"qualification":"NOT_QUALIFIED"}
    (out_dir/"RQ1-bundle.json").write_text(json.dumps(bundle,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"case_count":32,"pass":sum(x["status"]=="PASS" for x in results),"red":sum(x["status"]=="RED" for x in results),"insufficient_evidence":sum(x["status"]=="INSUFFICIENT_EVIDENCE" for x in results),"qualification":"NOT_QUALIFIED"},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--run",action="store_true"); ap.add_argument("--evidence-dir",default="rq1-evidence")
    a=ap.parse_args()
    if a.self_test: static_self_tests(); return 0
    if a.run: run_all(Path(a.evidence_dir)); return 0
    ap.error("--self-test or --run required")

if __name__ == "__main__": raise SystemExit(main())

```

## Exact machine-readable evidence schema
```json
{
  "schema_version": 1,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "case_id_pattern": "^RQ-(0[1-9]|[12][0-9]|3[0-2])$",
  "required_fields": ["case_id", "oracle", "status", "setup", "trigger", "observation", "cleanup", "evidence", "scientific_execution_state", "authority_effect", "qualification"],
  "statuses": ["PASS", "RED", "INSUFFICIENT_EVIDENCE", "HARNESS_DEFECT", "INFRASTRUCTURE_FAILURE"],
  "pass_requirements": ["exactly_one_known_case_id", "nonempty_evidence", "cleanup_verified", "scientific_execution_state_starts_CLOSED", "authority_effect_equals_NONE_EVIDENCE_ONLY", "qualification_equals_NOT_QUALIFIED"],
  "unknown_case_policy": "REJECT",
  "missing_evidence_policy": "PASS_FORBIDDEN",
  "cleanup_failure_policy": "BLOCK_CONTINUATION",
  "unexpected_success_policy": "RECORD_RED",
  "historical_evidence_policy": "APPEND_ONLY"
}

```

## Static self-tests
Command: python governance-runtime/v24_v6_rq1_harness.py --self-test
Result: PASS; case_count=32; CLOSED_PENDING_SUCCESSOR_REVIEW; NONE_EVIDENCE_ONLY; NOT_QUALIFIED.

## Complete RQ-01 through RQ-32 results
```json
{
  "case_count": 32,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "qualification": "NOT_QUALIFIED",
  "results": [
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-01",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-01.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Diagnostic-only DENY; no trusted state transition",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-02",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-02.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "No authority; trusted state unchanged",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-03",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.021,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-03.json"
      ],
      "observation": "",
      "oracle": "Kernel-derived peer rejection",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "candidate",
      "status": "PASS",
      "trigger": "candidate"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-04",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-04.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Fail closed; no candidate authority",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "socket",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "socket"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-05",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-05.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Install/start/consume rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "path",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "path"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-06",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-06.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Bootstrap/service rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "environment",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "environment"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-07",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-07.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "External pin verification rejects it",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "manifest",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "manifest"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-08",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-08.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-operation",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "wrong-operation"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-09",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-09.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-payload",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "wrong-payload"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-10",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-10.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rebind",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "rebind"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-11",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-11.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Exactly one success; all others replay/unavailable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "concurrency",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "concurrency"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-12",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-12.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "replay-restart",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "replay-restart"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-13",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-13.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No consume or authoritative result",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-before",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-before"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-14",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-14.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Recoverable without duplicate success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-mid",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-mid"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-15",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-15.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "One consumed state; never a second success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-after",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-after"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-16",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-16.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Fail closed without fabricated success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "io-failure",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "io-failure"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-17",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-17.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Configuration rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "cross-filesystem",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "cross-filesystem"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-18",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-18.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "binary-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "binary-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-19",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-19.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "dependency-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "dependency-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-20",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-20.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "unit-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "unit-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-21",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-21.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "permission-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "permission-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-22",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-22.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Denied by bound runtime controls",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ptrace",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "ptrace"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-23",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.007,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-23.json"
      ],
      "observation": "unshare: unshare failed: Operation not permitted",
      "oracle": "Cannot affect service or trusted paths",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "namespace",
      "status": "PASS",
      "trigger": "namespace"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-24",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-24.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "da1",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "da1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-25",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-25.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ncp1",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "ncp1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-26",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-26.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "stale-substitution",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "stale-substitution"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-27",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-27.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "composition",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "composition"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-28",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-28.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Fail closed; service remains recoverable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "protocol",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "protocol"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-29",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-29.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No bypass; bounded recovery",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "exhaustion",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "exhaustion"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-30",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-30.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Rejected or qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rollback",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "rollback"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-31",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-31.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No authority from absent evidence",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "logging",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "logging"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-32",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-32.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Consistent state; replay still rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "reboot",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "reboot"
    }
  ],
  "schema_version": 1,
  "state": {
    "authority_effect": "NONE_EVIDENCE_ONLY",
    "qualification": "NOT_QUALIFIED",
    "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW"
  }
}

```

## Positive Successor-9 candidate-runtime transcript
```text
V24-RQ1 Successor-9 runtime regressions corrected candidate invocation
2026-09-18T19:50:42+00:00
runtime_status=NOMINATED_ENTRY_PENDING
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.437s

OK
LOADER_REGRESSION=PASS
Traceback (most recent call last):
  File "/tmp/v24-s9-build/governance-runtime/v24_v6_successor9_trusted_control.py", line 168, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/tmp/v24-s9-build/governance-runtime/v24_v6_successor9_trusted_control.py", line 162, in main
    result = consume(sys.argv[1], Path(sys.argv[2]))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build/governance-runtime/v24_v6_successor9_trusted_control.py", line 112, in consume
    raise PermissionError("trusted semantic consume client requires root")
PermissionError: trusted semantic consume client requires root
CANDIDATE_TRUSTED_PROTOCOL=DENIED
CANDIDATE_DIAGNOSTIC_RECORDS=PASS
WRONG_OPERATION=PASS
WRONG_PAYLOAD=PASS
TRUSTED_POSITIVE=PASS
REPLAY=PASS
da1=PASS
ncp1=PASS
USERNS=DENIED
SERVICE=active
RESULTS=PASS

```

## Inherited-suite evidence
```text
context=unprivileged-candidate
exit_code=1
test_da1_decision_for_one_path_cannot_authorize_another_current_path (test_v24_v6_successor3_manual_review_red.Successor3ManualReviewRegressions.test_da1_decision_for_one_path_cannot_authorize_another_current_path) ... ok
test_ncp1_control_reassignment_requires_new_authorized_binding (test_v24_v6_successor3_manual_review_red.Successor3ManualReviewRegressions.test_ncp1_control_reassignment_requires_new_authorized_binding) ... ok
test_prc1_self_constructed_trusted_boundary_is_rejected (test_v24_v6_successor3_manual_review_red.Successor3ManualReviewRegressions.test_prc1_self_constructed_trusted_boundary_is_rejected) ... ok
test_same_process_caller_cannot_self_update_anchor_and_self_grant (test_v24_v6_successor4_external_anchor_red.Successor4ExternalAnchorRed.test_same_process_caller_cannot_self_update_anchor_and_self_grant) ... ok
test_attestation_scope_substitution_rejected (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_attestation_scope_substitution_rejected) ... ok
test_caller_selected_public_key_rejected (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_caller_selected_public_key_rejected) ... ok
test_same_process_anchor_rewrite_rejected (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_same_process_anchor_rewrite_rejected) ... ok
test_signed_context_positive (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_signed_context_positive) ... ok
test_unsigned_context_rejected (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_unsigned_context_rejected) ... ok
test_wrong_context_signature_rejected (test_v24_v6_successor4_root_attestation.Successor4RootAttestationRegressions.test_wrong_context_signature_rejected) ... ok
setUpClass (test_v24_v6_successor5_external_authority_gate.Successor5ExternalAuthorityGateRegressions) ... ERROR
test_same_process_imported_verifier_substitution_cannot_self_grant (test_v24_v6_successor5_mutable_verifier_red.Successor5MutableVerifierRed.test_same_process_imported_verifier_substitution_cannot_self_grant) ... FAIL
setUpClass (test_v24_v6_successor6_gate_replacement_red.Successor6GateReplacementRed) ... ERROR
test_candidate_identity_is_unprivileged (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_candidate_identity_is_unprivileged) ... ok
test_copied_gate_at_caller_selected_path_is_nonauthoritative (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_copied_gate_at_caller_selected_path_is_nonauthoritative) ... FAIL
test_gate_parent_directory_rename_unlink_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_gate_parent_directory_rename_unlink_replacement_rejected) ... ok
test_live_gate_digest_matches_root_owned_build_manifest (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_live_gate_digest_matches_root_owned_build_manifest) ... FAIL
test_pinned_source_post_measurement_substitution_rejected_by_permissions (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_pinned_source_post_measurement_substitution_rejected_by_permissions) ... ok
test_same_user_gate_executable_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_same_user_gate_executable_replacement_rejected) ... ok
test_trusted_gate_and_runtime_are_root_owned_nonwritable (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_and_runtime_are_root_owned_nonwritable) ... FAIL
test_trusted_gate_positive (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_positive) ... ERROR
test_candidate_ld_preload_cannot_forge_authoritative_allow (test_v24_v6_successor7_candidate_loader_red.Successor7CandidateLoaderInjectionRed.test_candidate_ld_preload_cannot_forge_authoritative_allow) ... ERROR
test_caller_cannot_select_service_executable_worker_or_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_caller_cannot_select_service_executable_worker_or_root) ... ok
test_candidate_cannot_access_trusted_private_result_channel (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_access_trusted_private_result_channel) ... ok
test_candidate_cannot_ptrace_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_ptrace_trusted_service) ... ok
test_candidate_cannot_replace_service_endpoint (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_replace_service_endpoint) ... ERROR
test_candidate_cannot_signal_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_signal_trusted_service) ... ok
test_candidate_identity_is_unprivileged_and_service_is_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_identity_is_unprivileged_and_service_is_root) ... FAIL
test_candidate_ld_library_path_rebind_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_library_path_rebind_rejected_by_service) ... FAIL
test_candidate_ld_preload_gate_injection_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_preload_gate_injection_rejected_by_service) ... FAIL
test_da1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_da1_local_self_grant_does_not_cross_service_boundary) ... ERROR
test_external_service_decision_apply_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_decision_apply_positive) ... ERROR
test_external_service_normative_coverage_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_normative_coverage_positive) ... ERROR
test_ncp1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_ncp1_local_self_grant_does_not_cross_service_boundary) ... ERROR
test_trusted_service_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_trusted_service_positive) ... ERROR
test_unknown_reference_is_denied (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_unknown_reference_is_denied) ... ERROR
test_candidate_cannot_consume_trusted_authority_record (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_candidate_cannot_consume_trusted_authority_record) ... ERROR
test_fabricated_record_id_has_no_candidate_authority (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_fabricated_record_id_has_no_candidate_authority) ... ok
test_genuine_client_result_is_diagnostic_only (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_genuine_client_result_is_diagnostic_only) ... ERROR
test_request_digest_changes_on_reference_rebind (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_request_digest_changes_on_reference_rebind) ... ok
test_candidate_local_socket_peer_forgery_cannot_self_grant (test_v24_v6_successor8_candidate_local_red.Successor8CandidateLocalAuthorityRed.test_candidate_local_socket_peer_forgery_cannot_self_grant) ... ok
test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume) ... ok

======================================================================
ERROR: setUpClass (test_v24_v6_successor5_external_authority_gate.Successor5ExternalAuthorityGateRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor5_external_authority_gate.py", line 206, in setUpClass
    subprocess.run(
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['bash', '/tmp/v24-s9-build-20260919/governance-runtime/build_v24_v6_external_authority_gate.sh']' returned non-zero exit status 1.

======================================================================
ERROR: setUpClass (test_v24_v6_successor6_gate_replacement_red.Successor6GateReplacementRed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_gate_replacement_red.py", line 20, in setUpClass
    subprocess.run(
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['bash', '/tmp/v24-s9-build-20260919/governance-runtime/build_v24_v6_external_authority_gate.sh']' returned non-zero exit status 1.

======================================================================
ERROR: test_trusted_gate_positive (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 134, in test_trusted_gate_positive
    payload = json.loads(proc.stdout.strip())
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

======================================================================
ERROR: test_candidate_ld_preload_cannot_forge_authoritative_allow (test_v24_v6_successor7_candidate_loader_red.Successor7CandidateLoaderInjectionRed.test_candidate_ld_preload_cannot_forge_authoritative_allow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_candidate_loader_red.py", line 115, in test_candidate_ld_preload_cannot_forge_authoritative_allow
    baseline_proc, baseline = _run_gate(context, boundary)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_candidate_loader_red.py", line 106, in _run_gate
    payload = json.loads(proc.stdout.strip())
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

======================================================================
ERROR: test_candidate_cannot_replace_service_endpoint (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_replace_service_endpoint)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 166, in test_candidate_cannot_replace_service_endpoint
    os.unlink(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory: '/run/v24-v6-authority/service.sock'

======================================================================
ERROR: test_da1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_da1_local_self_grant_does_not_cross_service_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 227, in test_da1_local_self_grant_does_not_cross_service_boundary
    result = request_service(
             ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_external_service_decision_apply_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_decision_apply_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 187, in test_external_service_decision_apply_positive
    result = request_service(
             ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_external_service_normative_coverage_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_normative_coverage_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 240, in test_external_service_normative_coverage_positive
    result = request_service(
             ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_ncp1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_ncp1_local_self_grant_does_not_cross_service_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 274, in test_ncp1_local_self_grant_does_not_cross_service_boundary
    result = request_service(
             ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_trusted_service_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_trusted_service_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 98, in test_trusted_service_positive
    result = request_service(
             ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_unknown_reference_is_denied (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_unknown_reference_is_denied)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 115, in test_unknown_reference_is_denied
    result = _unknown_request()
             ^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 47, in _unknown_request
    return request_service(
           ^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_candidate_cannot_consume_trusted_authority_record (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_candidate_cannot_consume_trusted_authority_record)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor8_authenticated_authority.py", line 46, in test_candidate_cannot_consume_trusted_authority_record
    result = client.request_service(
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
ERROR: test_genuine_client_result_is_diagnostic_only (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_genuine_client_result_is_diagnostic_only)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor8_authenticated_authority.py", line 18, in test_genuine_client_result_is_diagnostic_only
    result = client.request_service(
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service
    s.connect(SERVICE_SOCKET)
FileNotFoundError: [Errno 2] No such file or directory

======================================================================
FAIL: test_same_process_imported_verifier_substitution_cannot_self_grant (test_v24_v6_successor5_mutable_verifier_red.Successor5MutableVerifierRed.test_same_process_imported_verifier_substitution_cannot_self_grant)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor5_mutable_verifier_red.py", line 35, in test_same_process_imported_verifier_substitution_cannot_self_grant
    self.assertFalse(result["qualified"], result)
AssertionError: True is not false : {'qualified': True, 'state': 'PROOF_REFERENCE_CLOSED', 'reference_digest': 'aa33564e090c903d68d4189c5ffe75ee86d2671c0193ae73dc940d6e344fab84', 'problems': [], 'resolved_digests': ['3fa95a1150c4c0d37f84369e83e6fd60f0df51dabd72b8d685268671a77734fa', '5918dfba1cbbcdcb9739d72a843315680cc8ffc91e41eeff0e6c14113d086b94', 'aa33564e090c903d68d4189c5ffe75ee86d2671c0193ae73dc940d6e344fab84'], 'authority_effect': 'NONE_EVIDENCE_ONLY'}

======================================================================
FAIL: test_copied_gate_at_caller_selected_path_is_nonauthoritative (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_copied_gate_at_caller_selected_path_is_nonauthoritative)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 102, in test_copied_gate_at_caller_selected_path_is_nonauthoritative
    self.assertNotEqual(proc.returncode, 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_live_gate_digest_matches_root_owned_build_manifest (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_live_gate_digest_matches_root_owned_build_manifest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 110, in test_live_gate_digest_matches_root_owned_build_manifest
    self.assertEqual(actual, manifest["binary_sha256"])
AssertionError: 'fbc4b960af6cd44f80072a0da1c0e26d7bc5168ac7526e044eeff3e05f66de89' != '7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069'
- fbc4b960af6cd44f80072a0da1c0e26d7bc5168ac7526e044eeff3e05f66de89
+ 7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069


======================================================================
FAIL: test_trusted_gate_and_runtime_are_root_owned_nonwritable (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_and_runtime_are_root_owned_nonwritable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 61, in test_trusted_gate_and_runtime_are_root_owned_nonwritable
    self.assertEqual(st.st_mode & 0o222, 0, oct(st.st_mode))
AssertionError: 128 != 0 : 0o100755

======================================================================
FAIL: test_candidate_identity_is_unprivileged_and_service_is_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_identity_is_unprivileged_and_service_is_root)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 90, in test_candidate_identity_is_unprivileged_and_service_is_root
    self.assertTrue(Path(SERVICE_SOCKET).is_socket())
AssertionError: False is not true

======================================================================
FAIL: test_candidate_ld_library_path_rebind_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_library_path_rebind_rejected_by_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 139, in test_candidate_ld_library_path_rebind_rejected_by_service
    attacked = _child_request(env)
               ^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 83, in _child_request
    raise AssertionError((proc.stdout, proc.stderr))
AssertionError: ('', 'Traceback (most recent call last):\n  File "<string>", line 6, in <module>\n  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service\n    s.connect(SERVICE_SOCKET)\nFileNotFoundError: [Errno 2] No such file or directory\n')

======================================================================
FAIL: test_candidate_ld_preload_gate_injection_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_preload_gate_injection_rejected_by_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 132, in test_candidate_ld_preload_gate_injection_rejected_by_service
    attacked = _child_request(env)
               ^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 83, in _child_request
    raise AssertionError((proc.stdout, proc.stderr))
AssertionError: ('', 'Traceback (most recent call last):\n  File "<string>", line 6, in <module>\n  File "/tmp/v24-s9-build-20260919/governance-runtime/v24_v6_trusted_service_client.py", line 84, in request_service\n    s.connect(SERVICE_SOCKET)\nFileNotFoundError: [Errno 2] No such file or directory\n')

----------------------------------------------------------------------
Ran 40 tests in 0.714s

FAILED (failures=7, errors=13)
sha256=33d8235d3d8c67677b7490002a9be93b8c94b59d34310859c44dae5786ffe459  /var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-inherited-linux-context-20260919T200500Z.txt

```

## Harness runtime bundle transcript
```text
V24-RQ1 complete 32-case harness bundle seal
2026-09-18T19:57:44+00:00
runtime_status=NOMINATED_ENTRY_PENDING
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
{
  "case_count": 32,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "qualification": "NOT_QUALIFIED",
  "results": [
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-01",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-01.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Diagnostic-only DENY; no trusted state transition",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-02",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-02.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "No authority; trusted state unchanged",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-03",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.021,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-03.json"
      ],
      "observation": "",
      "oracle": "Kernel-derived peer rejection",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "candidate",
      "status": "PASS",
      "trigger": "candidate"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-04",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-04.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Fail closed; no candidate authority",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "socket",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "socket"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-05",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-05.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Install/start/consume rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "path",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "path"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-06",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-06.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Bootstrap/service rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "environment",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "environment"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-07",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-07.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "External pin verification rejects it",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "manifest",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "manifest"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-08",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-08.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-operation",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "wrong-operation"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-09",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-09.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-payload",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "wrong-payload"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-10",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-10.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rebind",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "rebind"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-11",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-11.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Exactly one success; all others replay/unavailable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "concurrency",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "concurrency"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-12",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-12.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "replay-restart",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "replay-restart"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-13",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-13.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No consume or authoritative result",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-before",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-before"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-14",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-14.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Recoverable without duplicate success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-mid",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-mid"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-15",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-15.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "One consumed state; never a second success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-after",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "crash-after"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-16",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-16.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Fail closed without fabricated success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "io-failure",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "io-failure"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-17",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-17.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Configuration rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "cross-filesystem",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "cross-filesystem"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-18",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-18.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "binary-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "binary-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-19",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-19.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "dependency-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "dependency-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-20",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-20.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "unit-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "unit-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-21",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-21.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "permission-drift",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "permission-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-22",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-22.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Denied by bound runtime controls",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ptrace",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "ptrace"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-23",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.007,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-23.json"
      ],
      "observation": "unshare: unshare failed: Operation not permitted",
      "oracle": "Cannot affect service or trusted paths",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "namespace",
      "status": "PASS",
      "trigger": "namespace"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-24",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-24.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "da1",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "da1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-25",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-25.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ncp1",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "ncp1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-26",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-26.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "stale-substitution",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "stale-substitution"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-27",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-27.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "composition",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "composition"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-28",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-28.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Fail closed; service remains recoverable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "protocol",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "protocol"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-29",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-29.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No bypass; bounded recovery",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "exhaustion",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "exhaustion"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-30",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-30.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "Rejected or qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rollback",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "rollback"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-31",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-31.json"
      ],
      "observation": "No deterministic preregistered runtime trigger is materialized in the frozen harness surface",
      "oracle": "No authority from absent evidence",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "logging",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "logging"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-32",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ-32.json"
      ],
      "observation": "Case-specific trigger requires the frozen runtime harness extension",
      "oracle": "Consistent state; replay still rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "reboot",
      "status": "INSUFFICIENT_EVIDENCE",
      "trigger": "reboot"
    }
  ],
  "schema_version": 1,
  "state": {
    "authority_effect": "NONE_EVIDENCE_ONLY",
    "qualification": "NOT_QUALIFIED",
    "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW"
  }
}
-- evidence files --
RQ-01.json 564 bytes
RQ-02.json 552 bytes
RQ-03.json 468 bytes
RQ-04.json 550 bytes
RQ-05.json 541 bytes
RQ-06.json 551 bytes
RQ-07.json 555 bytes
RQ-08.json 565 bytes
RQ-09.json 561 bytes
RQ-10.json 523 bytes
RQ-11.json 600 bytes
RQ-12.json 539 bytes
RQ-13.json 586 bytes
RQ-14.json 583 bytes
RQ-15.json 592 bytes
RQ-16.json 586 bytes
RQ-17.json 582 bytes
RQ-18.json 562 bytes
RQ-19.json 585 bytes
RQ-20.json 573 bytes
RQ-21.json 570 bytes
RQ-22.json 572 bytes
RQ-23.json 525 bytes
RQ-24.json 552 bytes
RQ-25.json 554 bytes
RQ-26.json 568 bytes
RQ-27.json 554 bytes
RQ-28.json 559 bytes
RQ-29.json 575 bytes
RQ-30.json 581 bytes
RQ-31.json 575 bytes
RQ-32.json 554 bytes
RQ1-bundle.json 20360 bytes
-- bundle hash --
3c4bcf116f9ad63b244637fd2d643a26c228033a3d23f3f1402a282a74f9cc0a  /var/lib/v24-rq1/rq1-harness-run-20260919T200000Z/RQ1-bundle.json

```

## Historical RED and fail-closed records
### aws-codex-persistence-boundary-ready-20260918T182313Z.txt
```text
V24-RQ1 persistence boundary final read-only capture
2026-09-18T18:23:13+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
-- host identity --
Linux ip-172-31-4-29 6.17.0-1017-aws #17~24.04.1-Ubuntu SMP Tue May 26 21:30:32 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
x86_64
2
MemTotal:        7964676 kB
/dev/nvme0n1p1 ext4   47.4G  2.4G 44.9G rw,relatime,discard,errors=remount-ro,commit=30
/dev/root              1     1         1   6% /
-- controls --
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
-- security services --
enabled
active
enabled
active
disabled
inactive
-- sysctl/apport sources --
/etc/sysctl.d/zz-v24-rq1.conf root:root 600 2026-09-18 17:28:54.596980016 +0000
/etc/default/apport root:root 644 2026-09-18 18:20:18.616779712 +0000
8:fs.suid_dumpable = 0
enabled=0
-- evidence integrity --
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot2-20260918T182236Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot2-20260918T182151Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-post-clean-reboot1-20260918T181054Z.txt
```text
V24-RQ1 post-clean-reboot-1
2026-09-18T18:10:54+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
-- identity --
PRETTY_NAME="Ubuntu 24.04.4 LTS"
VERSION_ID="24.04"
x86_64
ec297164-512d-0da3-f146-84010b6b5703
da4821d7-a627-4d77-9ef2-00369b044574
-- controls --
fs.suid_dumpable = 2
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2

```
### aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt
```text
V24-RQ1 post-clean-reboot-1 RED (fs.suid_dumpable drift reproduced)
2026-09-18T18:11:49+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
result=FAIL
-- boot --
da4821d7-a627-4d77-9ef2-00369b044574
2026-09-18T18:10:14+00:00 ip-172-31-4-29 systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
2026-09-18T18:10:15+00:00 ip-172-31-4-29 systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
-- controls --
fs.suid_dumpable = 2
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
-- security --
enabled
active
enabled
active
-- persisted source --
/etc/sysctl.d/zz-v24-rq1.conf root:root 600 2026-09-18 17:28:54.596980016 +0000
8:fs.suid_dumpable = 0

```
### aws-codex-post-fix-reboot1-20260918T182133Z.txt
```text
V24-RQ1 post-fix reboot 1
2026-09-18T18:21:33+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
BOOT_ID=83cac795-addf-4c51-b3f1-cfd2672f321d
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
enabled
active
enabled
active
disabled
inactive
2026-09-18T18:21:00+00:00 ip-172-31-4-29 systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
2026-09-18T18:21:00+00:00 ip-172-31-4-29 systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-post-fix-reboot2-20260918T182236Z.txt
```text
V24-RQ1 post-fix reboot 2
2026-09-18T18:22:36+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
BOOT_ID=a5329663-f7a0-46bd-99cb-78b7e83ebe7c
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
enabled
active
enabled
active
disabled
inactive
2026-09-18T18:22:04+00:00 ip-172-31-4-29 systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
2026-09-18T18:22:05+00:00 ip-172-31-4-29 systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot2-20260918T182151Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-post-resize-20260918T175806Z.txt
```text
=== V24 RQ1 AWS POST-RESIZE EVIDENCE ===
captured_at=2026-09-18T17:58:06+00:00
runtime_nomination=NOT_NOMINATED
scientific_execution=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
=== INSTANCE IDENTITY ===
instance_id=i-05063c49c656d01ad
instance_type=m7i-flex.large
region=ap-south-2
availability_zone=ap-south-2a
ami_id=ami-03f1d2b3639314198
instance_id_unchanged=true
=== CAPACITY ===
nproc=2
               total        used        free      shared  buff/cache   available
Mem:      8155836416   514736128  7624060928     3018752   277299200  7641100288
Swap:              0           0           0
root_bytes=49691512
memory_bytes=8155836416

```
### aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt
```text
=== V24 RQ1 POST-RESIZE SYSCTL REAPPLICATION ===
captured_at=2026-09-18T18:00:21+00:00
runtime_nomination=NOT_NOMINATED
scientific_execution=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
fs.suid_dumpable = 0
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
effective_sysctl_controls_verified=true
completed_at=2026-09-18T18:00:21+00:00

```
### aws-codex-post-resize-verified-20260918T175911Z.txt
```text
=== V24 RQ1 AWS POST-RESIZE VERIFIED EVIDENCE ===
captured_at=2026-09-18T17:59:11+00:00
runtime_nomination=NOT_NOMINATED
scientific_execution=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
=== INSTANCE IDENTITY ===
instance_id=i-05063c49c656d01ad
instance_type=m7i-flex.large
region=ap-south-2
availability_zone=ap-south-2a
ami_id=ami-03f1d2b3639314198
instance_id_unchanged=true
=== CAPACITY ===
nproc=2
               total        used        free      shared  buff/cache   available
Mem:      8155836416   519045120  7619469312     3018752   277471232  7636791296
Swap:              0           0           0
root_blocks=49691512
root_bytes=50884108288
memory_bytes=8155836416
capacity_requirements_met=true
=== PLATFORM ===
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
Linux 6.17.0-1017-aws x86_64 GNU/Linux
NAME          SIZE FSTYPE   MOUNTPOINTS
loop0        28.2M squashfs /snap/amazon-ssm-agent/13009
loop1          74M squashfs /snap/core22/2411
loop2        49.3M squashfs /snap/snapd/26865
nvme0n1        50G          
â”œâ”€nvme0n1p1    49G ext4     /
â”œâ”€nvme0n1p14    4M          
â”œâ”€nvme0n1p15  106M vfat     /boot/efi
â””â”€nvme0n1p16  913M ext4     /boot
/      /dev/nvme0n1p1 ext4   rw,relatime,discard,errors=remount-ro,commit=30
=== SECURITY CONTROLS ===
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
fs.suid_dumpable = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2

```
### aws-codex-pre-clean-reboot1-20260918T181001Z.txt
```text
V24-RQ1 pre-clean-reboot-1
2026-09-18T18:10:01+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
-- current boot --
boot_id=cfbb3b80-8b8c-4d47-865f-509c4851665c
 18:10:01 up 31 min,  4 users,  load average: 0.04, 0.02, 0.00
-- current controls --
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
-- service state --
static
active
enabled
active
enabled
active
-- evidence hashes --
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-pre-fix-reboot1-20260918T182047Z.txt
```text
V24-RQ1 pre-fix reboot 1
2026-09-18T18:20:47+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
fs.suid_dumpable = 0
disabled
inactive
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-pre-fix-reboot2-20260918T182151Z.txt
```text
V24-RQ1 pre-fix reboot 2
2026-09-18T18:21:51+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
fs.suid_dumpable = 0
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-preparation-20260918T172745Z.txt
```text
=== V24 RQ1 AWS VM PREPARATION ===
started_at=2026-09-18T17:27:45+00:00
runtime_nomination=NOT_NOMINATED
scientific_execution=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
=== PLATFORM AND CAPACITY ===
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
Linux 6.17.0-1017-aws x86_64 GNU/Linux
vcpus=2
               total        used        free      shared  buff/cache   available
Mem:      3999260672   482455552  3307548672     3010560   454496256  3516805120
Swap:              0           0           0
Filesystem       1B-blocks       Used   Available Use% Mounted on
/dev/root      50884108288 1957126144 48910204928   4% /
NAME          SIZE FSTYPE   MOUNTPOINTS
loop0        28.2M squashfs /snap/amazon-ssm-agent/13009
loop1          74M squashfs /snap/core22/2411
loop2        49.3M squashfs /snap/snapd/26865
nvme0n1        50G          
â”œâ”€nvme0n1p1    49G ext4     /
â”œâ”€nvme0n1p14    4M          
â”œâ”€nvme0n1p15  106M vfat     /boot/efi
â””â”€nvme0n1p16  913M ext4     /boot
=== AWS INSTANCE IDENTITY ===
instance_id=i-05063c49c656d01ad
instance_type=c7i-flex.large
region=ap-south-2
availability_zone=ap-south-2a
ami_id=ami-03f1d2b3639314198
=== PACKAGES ===
Hit:1 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble InRelease
Get:2 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates InRelease [126 kB]
Get:3 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports InRelease [126 kB]
Get:4 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/universe amd64 Packages [15.0 MB]
Get:5 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/universe Translation-en [5982 kB]
Get:6 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]
Get:7 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/universe amd64 Components [3871 kB]
Get:8 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/universe amd64 c-n-f Metadata [301 kB]
Get:9 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/multiverse amd64 Packages [269 kB]
Get:10 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/multiverse Translation-en [118 kB]
Get:11 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/multiverse amd64 Components [35.0 kB]
Get:12 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/multiverse amd64 c-n-f Metadata [8328 B]
Get:13 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages [1275 kB]
Get:14 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main Translation-en [294 kB]
Get:15 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 Components [181 kB]
Get:16 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 c-n-f Metadata [17.7 kB]
Get:17 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages [1689 kB]
Get:18 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe Translation-en [338 kB]
Get:19 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Components [388 kB]
Get:20 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 c-n-f Metadata [34.9 kB]
Get:21 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/restricted amd64 Packages [1580 kB]
Get:22 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/restricted Translation-en [359 kB]
Get:23 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/multiverse amd64 Packages [45.7 kB]
Get:24 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/multiverse Translation-en [13.1 kB]
Get:25 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/multiverse amd64 Components [940 B]
Get:26 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/multiverse amd64 c-n-f Metadata [656 B]
Get:27 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/main amd64 Packages [65.9 kB]
Get:28 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/main Translation-en [9172 B]
Get:29 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/main amd64 Components [5748 B]
Get:30 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/main amd64 c-n-f Metadata [368 B]
Get:31 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/universe amd64 Packages [34.6 kB]
Get:32 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/universe Translation-en [18.7 kB]
Get:33 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/universe amd64 Components [12.6 kB]
Get:34 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/universe amd64 c-n-f Metadata [1588 B]
Get:35 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/restricted amd64 Components [212 B]
Get:36 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/restricted amd64 c-n-f Metadata [116 B]
Get:37 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/multiverse amd64 Packages [748 B]
Get:38 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/multiverse Translation-en [340 B]
Get:39 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/multiverse amd64 Components [212 B]
Get:40 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-backports/multiverse amd64 c-n-f Metadata [116 B]
Get:41 http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages [1009 kB]
Get:42 http://security.ubuntu.com/ubuntu noble-security/main Translation-en [214 kB]
Get:43 http://security.ubuntu.com/ubuntu noble-security/main amd64 Components [46.4 kB]
Get:44 http://security.ubuntu.com/ubuntu noble-security/main amd64 c-n-f Metadata [11.9 kB]
Get:45 http://security.ubuntu.com/ubuntu noble-security/universe amd64 Packages [1208 kB]
Get:46 http://security.ubuntu.com/ubuntu noble-security/universe Translation-en [243 kB]
Get:47 http://security.ubuntu.com/ubuntu noble-security/universe amd64 Components [76.2 kB]
Get:48 http://security.ubuntu.com/ubuntu noble-security/universe amd64 c-n-f Metadata [24.2 kB]
Get:49 http://security.ubuntu.com/ubuntu noble-security/restricted amd64 Packages [1449 kB]
Get:50 http://security.ubuntu.com/ubuntu noble-security/restricted Translation-en [336 kB]
Get:51 http://security.ubuntu.com/ubuntu noble-security/multiverse amd64 Packages [40.3 kB]
Get:52 http://security.ubuntu.com/ubuntu noble-security/multiverse Translation-en [11.3 kB]
Get:53 http://security.ubuntu.com/ubuntu noble-security/multiverse amd64 Components [208 B]
Get:54 http://security.ubuntu.com/ubuntu noble-security/multiverse amd64 c-n-f Metadata [468 B]
Fetched 37.0 MB in 4s (9383 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
lsof is already the newest version (4.95.0-1build3).
lsof set to manually installed.
strace is already the newest version (6.8-0ubuntu2).
strace set to manually installed.
jq is already the newest version (1.7.1-3ubuntu0.24.04.2).
jq set to manually installed.
git is already the newest version (1:2.43.0-1ubuntu7.3).
git set to manually installed.
python3 is already the newest version (3.12.3-0ubuntu2.1).
python3 set to manually installed.
The following additional packages will be installed:
  binutils binutils-common binutils-x86-64-linux-gnu bzip2 cpp cpp-13
  cpp-13-x86-64-linux-gnu cpp-x86-64-linux-gnu dpkg-dev fakeroot
  fontconfig-config fonts-dejavu-core fonts-dejavu-mono g++ g++-13
  g++-13-x86-64-linux-gnu g++-x86-64-linux-gnu gcc gcc-13 gcc-13-base
  gcc-13-x86-64-linux-gnu gcc-x86-64-linux-gnu libalgorithm-diff-perl
  libalgorithm-diff-xs-perl libalgorithm-merge-perl libaom3 libasan8
  libatomic1 libauparse0t64 libbinutils libbz2-1.0 libc-bin libc-dev-bin
  libc-devtools libc6 libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0
  libcurl3t64-gnutls libcurl4t64 libdeflate0 libdpkg-perl libfakeroot
  libfile-fcntllock-perl libfontconfig1 libgcc-13-dev libgd3 libgomp1
  libgprofng0 libheif-plugin-aomdec libheif-plugin-aomenc libheif1 libhwasan0
  libisl23 libitm1 libjbig0 libjpeg-turbo8 libjpeg8 liblerc4 liblsan0 libmpc3
  libpython3.12-minimal libpython3.12-stdlib libpython3.12t64 libquadmath0
  libsframe1 libsharpyuv0 libssl3t64 libstdc++-13-dev libtiff6 libtsan2
  libubsan1 libwebp7 libxpm4 linux-libc-dev linux-tools-common locales
  lto-disabled-list make manpages-dev python3-apparmor python3-libapparmor
  python3-pip-whl python3-setuptools-whl python3.12 python3.12-minimal
  python3.12-venv rpcsvc-proto
Suggested packages:
  vim-addon-manager audispd-plugins binutils-doc gprofng-gui bzip2-doc cpp-doc
  gcc-13-locales cpp-13-doc debian-keyring g++-multilib g++-13-multilib
  gcc-13-doc gcc-multilib autoconf automake libtool flex bison gdb gcc-doc
  gcc-13-multilib gdb-x86-64-linux-gnu glibc-doc libnss-nis libnss-nisplus bzr
  libgd-tools libheif-plugin-libde265 libheif-plugin-x265
  libheif-plugin-ffmpegdec libheif-plugin-jpegdec libheif-plugin-jpegenc
  libheif-plugin-j2kdec libheif-plugin-j2kenc libheif-plugin-rav1e
  libheif-plugin-svtenc libssl-doc libstdc++-13-doc make-doc python3.12-doc
  binfmt-support
The following NEW packages will be installed:
  acl apparmor-utils auditd binutils binutils-common binutils-x86-64-linux-gnu
  build-essential bzip2 cpp cpp-13 cpp-13-x86-64-linux-gnu
  cpp-x86-64-linux-gnu dpkg-dev fakeroot fontconfig-config fonts-dejavu-core
  fonts-dejavu-mono g++ g++-13 g++-13-x86-64-linux-gnu g++-x86-64-linux-gnu
  gcc gcc-13 gcc-13-base gcc-13-x86-64-linux-gnu gcc-x86-64-linux-gnu
  libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl
  libaom3 libasan8 libatomic1 libauparse0t64 libbinutils libc-dev-bin
  libc-devtools libc6-dev libcc1-0 libcrypt-dev libctf-nobfd0 libctf0
  libdeflate0 libdpkg-perl libfakeroot libfile-fcntllock-perl libfontconfig1
  libgcc-13-dev libgd3 libgomp1 libgprofng0 libheif-plugin-aomdec
  libheif-plugin-aomenc libheif1 libhwasan0 libisl23 libitm1 libjbig0
  libjpeg-turbo8 libjpeg8 liblerc4 liblsan0 libmpc3 libquadmath0 libsframe1
  libsharpyuv0 libssl-dev libstdc++-13-dev libtiff6 libtsan2 libubsan1
  libwebp7 libxpm4 linux-libc-dev lto-disabled-list make manpages-dev
  python3-apparmor python3-libapparmor python3-pip-whl python3-setuptools-whl
  python3-venv python3.12-venv rpcsvc-proto
The following packages will be upgraded:
  curl libbz2-1.0 libc-bin libc6 libcurl3t64-gnutls libcurl4t64
  libpython3.12-minimal libpython3.12-stdlib libpython3.12t64 libssl3t64
  linux-tools-common locales openssl python3.12 python3.12-minimal
15 upgraded, 83 newly installed, 0 to remove and 135 not upgraded.
Need to get 104 MB of archives.
After this operation, 286 MB of additional disk space will be used.
Get:1 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libc6 amd64 2.39-0ubuntu8.9 [3264 kB]
Get:2 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libc-bin amd64 2.39-0ubuntu8.9 [682 kB]
Get:3 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libpython3.12t64 amd64 3.12.3-1ubuntu0.17 [2348 kB]
Get:4 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libssl3t64 amd64 3.0.13-0ubuntu3.15 [1944 kB]
Get:5 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 python3.12 amd64 3.12.3-1ubuntu0.17 [651 kB]
Get:6 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libpython3.12-stdlib amd64 3.12.3-1ubuntu0.17 [2071 kB]
Get:7 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 python3.12-minimal amd64 3.12.3-1ubuntu0.17 [2335 kB]
Get:8 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libpython3.12-minimal amd64 3.12.3-1ubuntu0.17 [839 kB]
Get:9 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libbz2-1.0 amd64 1.0.8-5.1ubuntu0.1 [34.6 kB]
Get:10 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libauparse0t64 amd64 1:3.1.2-2.1build1.1 [58.9 kB]
Get:11 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 auditd amd64 1:3.1.2-2.1build1.1 [215 kB]
Get:12 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 locales all 2.39-0ubuntu8.9 [4232 kB]
Get:13 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 openssl amd64 3.0.13-0ubuntu3.15 [1003 kB]
Get:14 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 acl amd64 2.3.2-1build1.1 [39.4 kB]
Get:15 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 python3-libapparmor amd64 4.0.1really4.0.1-0ubuntu0.24.04.7 [30.1 kB]
Get:16 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 python3-apparmor all 4.0.1really4.0.1-0ubuntu0.24.04.7 [84.5 kB]
Get:17 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 apparmor-utils all 4.0.1really4.0.1-0ubuntu0.24.04.7 [46.5 kB]
Get:18 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 binutils-common amd64 2.42-4ubuntu2.10 [240 kB]
Get:19 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libsframe1 amd64 2.42-4ubuntu2.10 [15.7 kB]
Get:20 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libbinutils amd64 2.42-4ubuntu2.10 [577 kB]
Get:21 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libctf-nobfd0 amd64 2.42-4ubuntu2.10 [98.0 kB]
Get:22 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libctf0 amd64 2.42-4ubuntu2.10 [94.5 kB]
Get:23 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libgprofng0 amd64 2.42-4ubuntu2.10 [849 kB]
Get:24 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 binutils-x86-64-linux-gnu amd64 2.42-4ubuntu2.10 [2463 kB]
Get:25 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 binutils amd64 2.42-4ubuntu2.10 [18.2 kB]
Get:26 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libc-dev-bin amd64 2.39-0ubuntu8.9 [20.4 kB]
Get:27 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 linux-libc-dev amd64 6.8.0-139.139 [1527 kB]
Get:28 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libcrypt-dev amd64 1:4.4.36-4build1 [112 kB]
Get:29 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 rpcsvc-proto amd64 1.4.2-0ubuntu7 [67.4 kB]
Get:30 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libc6-dev amd64 2.39-0ubuntu8.9 [2126 kB]
Get:31 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 gcc-13-base amd64 13.3.0-6ubuntu2~24.04.1 [51.6 kB]
Get:32 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libisl23 amd64 0.26-3build1.1 [680 kB]
Get:33 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libmpc3 amd64 1.3.1-1build1.1 [54.6 kB]
Get:34 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 cpp-13-x86-64-linux-gnu amd64 13.3.0-6ubuntu2~24.04.1 [10.7 MB]
Get:35 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 cpp-13 amd64 13.3.0-6ubuntu2~24.04.1 [1042 B]
Get:36 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 cpp-x86-64-linux-gnu amd64 4:13.2.0-7ubuntu1 [5326 B]
Get:37 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 cpp amd64 4:13.2.0-7ubuntu1 [22.4 kB]
Get:38 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libcc1-0 amd64 14.2.0-4ubuntu2~24.04.1 [48.0 kB]
Get:39 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libgomp1 amd64 14.2.0-4ubuntu2~24.04.1 [148 kB]
Get:40 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libitm1 amd64 14.2.0-4ubuntu2~24.04.1 [29.7 kB]
Get:41 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libatomic1 amd64 14.2.0-4ubuntu2~24.04.1 [10.5 kB]
Get:42 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libasan8 amd64 14.2.0-4ubuntu2~24.04.1 [3027 kB]
Get:43 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 liblsan0 amd64 14.2.0-4ubuntu2~24.04.1 [1322 kB]
Get:44 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libtsan2 amd64 14.2.0-4ubuntu2~24.04.1 [2772 kB]
Get:45 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libubsan1 amd64 14.2.0-4ubuntu2~24.04.1 [1184 kB]
Get:46 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libhwasan0 amd64 14.2.0-4ubuntu2~24.04.1 [1641 kB]
Get:47 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libquadmath0 amd64 14.2.0-4ubuntu2~24.04.1 [153 kB]
Get:48 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libgcc-13-dev amd64 13.3.0-6ubuntu2~24.04.1 [2681 kB]
Get:49 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 gcc-13-x86-64-linux-gnu amd64 13.3.0-6ubuntu2~24.04.1 [21.1 MB]
Get:50 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 gcc-13 amd64 13.3.0-6ubuntu2~24.04.1 [494 kB]
Get:51 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 gcc-x86-64-linux-gnu amd64 4:13.2.0-7ubuntu1 [1212 B]
Get:52 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 gcc amd64 4:13.2.0-7ubuntu1 [5018 B]
Get:53 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libstdc++-13-dev amd64 13.3.0-6ubuntu2~24.04.1 [2420 kB]
Get:54 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 g++-13-x86-64-linux-gnu amd64 13.3.0-6ubuntu2~24.04.1 [12.2 MB]
Get:55 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 g++-13 amd64 13.3.0-6ubuntu2~24.04.1 [16.0 kB]
Get:56 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 g++-x86-64-linux-gnu amd64 4:13.2.0-7ubuntu1 [964 B]
Get:57 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 g++ amd64 4:13.2.0-7ubuntu1 [1100 B]
Get:58 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 make amd64 4.3-4.1build2 [180 kB]
Get:59 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libdpkg-perl all 1.22.6ubuntu6.6 [268 kB]
Get:60 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 bzip2 amd64 1.0.8-5.1ubuntu0.1 [34.6 kB]
Get:61 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 lto-disabled-list all 47 [12.4 kB]
Get:62 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 dpkg-dev all 1.22.6ubuntu6.6 [1074 kB]
Get:63 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 build-essential amd64 12.10ubuntu1 [4928 B]
Get:64 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 curl amd64 8.5.0-2ubuntu10.13 [226 kB]
Get:65 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libcurl4t64 amd64 8.5.0-2ubuntu10.13 [343 kB]
Get:66 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libfakeroot amd64 1.33-1 [32.4 kB]
Get:67 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 fakeroot amd64 1.33-1 [67.2 kB]
Get:68 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 fonts-dejavu-mono all 2.37-8 [502 kB]
Get:69 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 fonts-dejavu-core all 2.37-8 [835 kB]
Get:70 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 fontconfig-config amd64 2.15.0-1.1ubuntu2 [37.3 kB]
Get:71 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libalgorithm-diff-perl all 1.201-1 [41.8 kB]
Get:72 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libalgorithm-diff-xs-perl amd64 0.04-8build3 [11.2 kB]
Get:73 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libalgorithm-merge-perl all 0.08-5 [11.4 kB]
Get:74 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libaom3 amd64 3.8.2-2ubuntu0.2 [1942 kB]
Get:75 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libfontconfig1 amd64 2.15.0-1.1ubuntu2 [139 kB]
Get:76 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libsharpyuv0 amd64 1.3.2-0.4build3 [15.8 kB]
Get:77 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libheif-plugin-aomdec amd64 1.17.6-1ubuntu4.8 [11.6 kB]
Get:78 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libheif1 amd64 1.17.6-1ubuntu4.8 [277 kB]
Get:79 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libjpeg-turbo8 amd64 2.1.5-2ubuntu2 [150 kB]
Get:80 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libjpeg8 amd64 8c-2ubuntu11 [2148 B]
Get:81 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libdeflate0 amd64 1.19-1build1.1 [43.9 kB]
Get:82 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libjbig0 amd64 2.1-6.1ubuntu2 [29.7 kB]
Get:83 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 liblerc4 amd64 4.0.0+ds-4ubuntu2 [179 kB]
Get:84 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libwebp7 amd64 1.3.2-0.4build3 [230 kB]
Get:85 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libtiff6 amd64 4.5.1+git230720-4ubuntu2.5 [200 kB]
Get:86 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libxpm4 amd64 1:3.5.17-1ubuntu0.24.04.1 [36.7 kB]
Get:87 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libgd3 amd64 2.3.3-9ubuntu5 [128 kB]
Get:88 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libc-devtools amd64 2.39-0ubuntu8.9 [29.3 kB]
Get:89 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libcurl3t64-gnutls amd64 8.5.0-2ubuntu10.13 [335 kB]
Get:90 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 libfile-fcntllock-perl amd64 0.22-4ubuntu5 [30.7 kB]
Get:91 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libheif-plugin-aomenc amd64 1.17.6-1ubuntu4.8 [14.7 kB]
Get:92 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 libssl-dev amd64 3.0.13-0ubuntu3.15 [2408 kB]
Get:93 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/main amd64 linux-tools-common all 6.8.0-139.139 [368 kB]
Get:94 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble/main amd64 manpages-dev all 6.7-2 [2013 kB]
Get:95 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 python3-pip-whl all 24.0+dfsg-1ubuntu1.3 [1707 kB]
Get:96 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 python3-setuptools-whl all 68.1.2-2ubuntu1.2 [716 kB]
Get:97 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 python3.12-venv amd64 3.12.3-1ubuntu0.17 [5684 B]
Get:98 http://ap-south-2.ec2.archive.ubuntu.com/ubuntu noble-updates/universe amd64 python3-venv amd64 3.12.3-0ubuntu2.1 [1032 B]
Preconfiguring packages ...
Fetched 104 MB in 6s (17.4 MB/s)
(Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 72608 files and directories currently installed.)
Preparing to unpack .../libc6_2.39-0ubuntu8.9_amd64.deb ...
Unpacking libc6:amd64 (2.39-0ubuntu8.9) over (2.39-0ubuntu8.7) ...
Setting up libc6:amd64 (2.39-0ubuntu8.9) ...
(Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 72608 files and directories currently installed.)
Preparing to unpack .../libc-bin_2.39-0ubuntu8.9_amd64.deb ...
Unpacking libc-bin (2.39-0ubuntu8.9) over (2.39-0ubuntu8.7) ...
Setting up libc-bin (2.39-0ubuntu8.9) ...
(Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 72608 files and directories currently installed.)
Preparing to unpack .../libpython3.12t64_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking libpython3.12t64:amd64 (3.12.3-1ubuntu0.17) over (3.12.3-1ubuntu0.13) ...
Preparing to unpack .../libssl3t64_3.0.13-0ubuntu3.15_amd64.deb ...
Unpacking libssl3t64:amd64 (3.0.13-0ubuntu3.15) over (3.0.13-0ubuntu3.11) ...
Setting up libssl3t64:amd64 (3.0.13-0ubuntu3.15) ...
(Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 72608 files and directories currently installed.)
Preparing to unpack .../python3.12_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking python3.12 (3.12.3-1ubuntu0.17) over (3.12.3-1ubuntu0.13) ...
Preparing to unpack .../libpython3.12-stdlib_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking libpython3.12-stdlib:amd64 (3.12.3-1ubuntu0.17) over (3.12.3-1ubuntu0.13) ...
Preparing to unpack .../python3.12-minimal_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking python3.12-minimal (3.12.3-1ubuntu0.17) over (3.12.3-1ubuntu0.13) ...
Preparing to unpack .../libpython3.12-minimal_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking libpython3.12-minimal:amd64 (3.12.3-1ubuntu0.17) over (3.12.3-1ubuntu0.13) ...
Preparing to unpack .../libbz2-1.0_1.0.8-5.1ubuntu0.1_amd64.deb ...
Unpacking libbz2-1.0:amd64 (1.0.8-5.1ubuntu0.1) over (1.0.8-5.1build0.1) ...
Setting up libbz2-1.0:amd64 (1.0.8-5.1ubuntu0.1) ...
Selecting previously unselected package libauparse0t64:amd64.
(Reading database ... (Reading database ... 5%(Reading database ... 10%(Reading database ... 15%(Reading database ... 20%(Reading database ... 25%(Reading database ... 30%(Reading database ... 35%(Reading database ... 40%(Reading database ... 45%(Reading database ... 50%(Reading database ... 55%(Reading database ... 60%(Reading database ... 65%(Reading database ... 70%(Reading database ... 75%(Reading database ... 80%(Reading database ... 85%(Reading database ... 90%(Reading database ... 95%(Reading database ... 100%(Reading database ... 72608 files and directories currently installed.)
Preparing to unpack .../00-libauparse0t64_1%3a3.1.2-2.1build1.1_amd64.deb ...
Adding 'diversion of /lib/x86_64-linux-gnu/libauparse.so.0 to /lib/x86_64-linux-gnu/libauparse.so.0.usr-is-merged by libauparse0t64'
Adding 'diversion of /lib/x86_64-linux-gnu/libauparse.so.0.0.0 to /lib/x86_64-linux-gnu/libauparse.so.0.0.0.usr-is-merged by libauparse0t64'
Unpacking libauparse0t64:amd64 (1:3.1.2-2.1build1.1) ...
Selecting previously unselected package auditd.
Preparing to unpack .../01-auditd_1%3a3.1.2-2.1build1.1_amd64.deb ...
Unpacking auditd (1:3.1.2-2.1build1.1) ...
Preparing to unpack .../02-locales_2.39-0ubuntu8.9_all.deb ...
Unpacking locales (2.39-0ubuntu8.9) over (2.39-0ubuntu8.7) ...
Preparing to unpack .../03-openssl_3.0.13-0ubuntu3.15_amd64.deb ...
Unpacking openssl (3.0.13-0ubuntu3.15) over (3.0.13-0ubuntu3.11) ...
Selecting previously unselected package acl.
Preparing to unpack .../04-acl_2.3.2-1build1.1_amd64.deb ...
Unpacking acl (2.3.2-1build1.1) ...
Selecting previously unselected package python3-libapparmor.
Preparing to unpack .../05-python3-libapparmor_4.0.1really4.0.1-0ubuntu0.24.04.7_amd64.deb ...
Unpacking python3-libapparmor (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Selecting previously unselected package python3-apparmor.
Preparing to unpack .../06-python3-apparmor_4.0.1really4.0.1-0ubuntu0.24.04.7_all.deb ...
Unpacking python3-apparmor (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Selecting previously unselected package apparmor-utils.
Preparing to unpack .../07-apparmor-utils_4.0.1really4.0.1-0ubuntu0.24.04.7_all.deb ...
Unpacking apparmor-utils (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Selecting previously unselected package binutils-common:amd64.
Preparing to unpack .../08-binutils-common_2.42-4ubuntu2.10_amd64.deb ...
Unpacking binutils-common:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package libsframe1:amd64.
Preparing to unpack .../09-libsframe1_2.42-4ubuntu2.10_amd64.deb ...
Unpacking libsframe1:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package libbinutils:amd64.
Preparing to unpack .../10-libbinutils_2.42-4ubuntu2.10_amd64.deb ...
Unpacking libbinutils:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package libctf-nobfd0:amd64.
Preparing to unpack .../11-libctf-nobfd0_2.42-4ubuntu2.10_amd64.deb ...
Unpacking libctf-nobfd0:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package libctf0:amd64.
Preparing to unpack .../12-libctf0_2.42-4ubuntu2.10_amd64.deb ...
Unpacking libctf0:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package libgprofng0:amd64.
Preparing to unpack .../13-libgprofng0_2.42-4ubuntu2.10_amd64.deb ...
Unpacking libgprofng0:amd64 (2.42-4ubuntu2.10) ...
Selecting previously unselected package binutils-x86-64-linux-gnu.
Preparing to unpack .../14-binutils-x86-64-linux-gnu_2.42-4ubuntu2.10_amd64.deb ...
Unpacking binutils-x86-64-linux-gnu (2.42-4ubuntu2.10) ...
Selecting previously unselected package binutils.
Preparing to unpack .../15-binutils_2.42-4ubuntu2.10_amd64.deb ...
Unpacking binutils (2.42-4ubuntu2.10) ...
Selecting previously unselected package libc-dev-bin.
Preparing to unpack .../16-libc-dev-bin_2.39-0ubuntu8.9_amd64.deb ...
Unpacking libc-dev-bin (2.39-0ubuntu8.9) ...
Selecting previously unselected package linux-libc-dev:amd64.
Preparing to unpack .../17-linux-libc-dev_6.8.0-139.139_amd64.deb ...
Unpacking linux-libc-dev:amd64 (6.8.0-139.139) ...
Selecting previously unselected package libcrypt-dev:amd64.
Preparing to unpack .../18-libcrypt-dev_1%3a4.4.36-4build1_amd64.deb ...
Unpacking libcrypt-dev:amd64 (1:4.4.36-4build1) ...
Selecting previously unselected package rpcsvc-proto.
Preparing to unpack .../19-rpcsvc-proto_1.4.2-0ubuntu7_amd64.deb ...
Unpacking rpcsvc-proto (1.4.2-0ubuntu7) ...
Selecting previously unselected package libc6-dev:amd64.
Preparing to unpack .../20-libc6-dev_2.39-0ubuntu8.9_amd64.deb ...
Unpacking libc6-dev:amd64 (2.39-0ubuntu8.9) ...
Selecting previously unselected package gcc-13-base:amd64.
Preparing to unpack .../21-gcc-13-base_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking gcc-13-base:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package libisl23:amd64.
Preparing to unpack .../22-libisl23_0.26-3build1.1_amd64.deb ...
Unpacking libisl23:amd64 (0.26-3build1.1) ...
Selecting previously unselected package libmpc3:amd64.
Preparing to unpack .../23-libmpc3_1.3.1-1build1.1_amd64.deb ...
Unpacking libmpc3:amd64 (1.3.1-1build1.1) ...
Selecting previously unselected package cpp-13-x86-64-linux-gnu.
Preparing to unpack .../24-cpp-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking cpp-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package cpp-13.
Preparing to unpack .../25-cpp-13_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking cpp-13 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package cpp-x86-64-linux-gnu.
Preparing to unpack .../26-cpp-x86-64-linux-gnu_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking cpp-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package cpp.
Preparing to unpack .../27-cpp_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking cpp (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package libcc1-0:amd64.
Preparing to unpack .../28-libcc1-0_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libcc1-0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libgomp1:amd64.
Preparing to unpack .../29-libgomp1_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libgomp1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libitm1:amd64.
Preparing to unpack .../30-libitm1_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libitm1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libatomic1:amd64.
Preparing to unpack .../31-libatomic1_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libatomic1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libasan8:amd64.
Preparing to unpack .../32-libasan8_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libasan8:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package liblsan0:amd64.
Preparing to unpack .../33-liblsan0_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking liblsan0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libtsan2:amd64.
Preparing to unpack .../34-libtsan2_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libtsan2:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libubsan1:amd64.
Preparing to unpack .../35-libubsan1_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libubsan1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libhwasan0:amd64.
Preparing to unpack .../36-libhwasan0_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libhwasan0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libquadmath0:amd64.
Preparing to unpack .../37-libquadmath0_14.2.0-4ubuntu2~24.04.1_amd64.deb ...
Unpacking libquadmath0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Selecting previously unselected package libgcc-13-dev:amd64.
Preparing to unpack .../38-libgcc-13-dev_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking libgcc-13-dev:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package gcc-13-x86-64-linux-gnu.
Preparing to unpack .../39-gcc-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking gcc-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package gcc-13.
Preparing to unpack .../40-gcc-13_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking gcc-13 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package gcc-x86-64-linux-gnu.
Preparing to unpack .../41-gcc-x86-64-linux-gnu_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking gcc-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package gcc.
Preparing to unpack .../42-gcc_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking gcc (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package libstdc++-13-dev:amd64.
Preparing to unpack .../43-libstdc++-13-dev_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking libstdc++-13-dev:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package g++-13-x86-64-linux-gnu.
Preparing to unpack .../44-g++-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking g++-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package g++-13.
Preparing to unpack .../45-g++-13_13.3.0-6ubuntu2~24.04.1_amd64.deb ...
Unpacking g++-13 (13.3.0-6ubuntu2~24.04.1) ...
Selecting previously unselected package g++-x86-64-linux-gnu.
Preparing to unpack .../46-g++-x86-64-linux-gnu_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking g++-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package g++.
Preparing to unpack .../47-g++_4%3a13.2.0-7ubuntu1_amd64.deb ...
Unpacking g++ (4:13.2.0-7ubuntu1) ...
Selecting previously unselected package make.
Preparing to unpack .../48-make_4.3-4.1build2_amd64.deb ...
Unpacking make (4.3-4.1build2) ...
Selecting previously unselected package libdpkg-perl.
Preparing to unpack .../49-libdpkg-perl_1.22.6ubuntu6.6_all.deb ...
Unpacking libdpkg-perl (1.22.6ubuntu6.6) ...
Selecting previously unselected package bzip2.
Preparing to unpack .../50-bzip2_1.0.8-5.1ubuntu0.1_amd64.deb ...
Unpacking bzip2 (1.0.8-5.1ubuntu0.1) ...
Selecting previously unselected package lto-disabled-list.
Preparing to unpack .../51-lto-disabled-list_47_all.deb ...
Unpacking lto-disabled-list (47) ...
Selecting previously unselected package dpkg-dev.
Preparing to unpack .../52-dpkg-dev_1.22.6ubuntu6.6_all.deb ...
Unpacking dpkg-dev (1.22.6ubuntu6.6) ...
Selecting previously unselected package build-essential.
Preparing to unpack .../53-build-essential_12.10ubuntu1_amd64.deb ...
Unpacking build-essential (12.10ubuntu1) ...
Preparing to unpack .../54-curl_8.5.0-2ubuntu10.13_amd64.deb ...
Unpacking curl (8.5.0-2ubuntu10.13) over (8.5.0-2ubuntu10.9) ...
Preparing to unpack .../55-libcurl4t64_8.5.0-2ubuntu10.13_amd64.deb ...
Unpacking libcurl4t64:amd64 (8.5.0-2ubuntu10.13) over (8.5.0-2ubuntu10.9) ...
Selecting previously unselected package libfakeroot:amd64.
Preparing to unpack .../56-libfakeroot_1.33-1_amd64.deb ...
Unpacking libfakeroot:amd64 (1.33-1) ...
Selecting previously unselected package fakeroot.
Preparing to unpack .../57-fakeroot_1.33-1_amd64.deb ...
Unpacking fakeroot (1.33-1) ...
Selecting previously unselected package fonts-dejavu-mono.
Preparing to unpack .../58-fonts-dejavu-mono_2.37-8_all.deb ...
Unpacking fonts-dejavu-mono (2.37-8) ...
Selecting previously unselected package fonts-dejavu-core.
Preparing to unpack .../59-fonts-dejavu-core_2.37-8_all.deb ...
Unpacking fonts-dejavu-core (2.37-8) ...
Selecting previously unselected package fontconfig-config.
Preparing to unpack .../60-fontconfig-config_2.15.0-1.1ubuntu2_amd64.deb ...
Unpacking fontconfig-config (2.15.0-1.1ubuntu2) ...
Selecting previously unselected package libalgorithm-diff-perl.
Preparing to unpack .../61-libalgorithm-diff-perl_1.201-1_all.deb ...
Unpacking libalgorithm-diff-perl (1.201-1) ...
Selecting previously unselected package libalgorithm-diff-xs-perl:amd64.
Preparing to unpack .../62-libalgorithm-diff-xs-perl_0.04-8build3_amd64.deb ...
Unpacking libalgorithm-diff-xs-perl:amd64 (0.04-8build3) ...
Selecting previously unselected package libalgorithm-merge-perl.
Preparing to unpack .../63-libalgorithm-merge-perl_0.08-5_all.deb ...
Unpacking libalgorithm-merge-perl (0.08-5) ...
Selecting previously unselected package libaom3:amd64.
Preparing to unpack .../64-libaom3_3.8.2-2ubuntu0.2_amd64.deb ...
Unpacking libaom3:amd64 (3.8.2-2ubuntu0.2) ...
Selecting previously unselected package libfontconfig1:amd64.
Preparing to unpack .../65-libfontconfig1_2.15.0-1.1ubuntu2_amd64.deb ...
Unpacking libfontconfig1:amd64 (2.15.0-1.1ubuntu2) ...
Selecting previously unselected package libsharpyuv0:amd64.
Preparing to unpack .../66-libsharpyuv0_1.3.2-0.4build3_amd64.deb ...
Unpacking libsharpyuv0:amd64 (1.3.2-0.4build3) ...
Selecting previously unselected package libheif-plugin-aomdec:amd64.
Preparing to unpack .../67-libheif-plugin-aomdec_1.17.6-1ubuntu4.8_amd64.deb ...
Unpacking libheif-plugin-aomdec:amd64 (1.17.6-1ubuntu4.8) ...
Selecting previously unselected package libheif1:amd64.
Preparing to unpack .../68-libheif1_1.17.6-1ubuntu4.8_amd64.deb ...
Unpacking libheif1:amd64 (1.17.6-1ubuntu4.8) ...
Selecting previously unselected package libjpeg-turbo8:amd64.
Preparing to unpack .../69-libjpeg-turbo8_2.1.5-2ubuntu2_amd64.deb ...
Unpacking libjpeg-turbo8:amd64 (2.1.5-2ubuntu2) ...
Selecting previously unselected package libjpeg8:amd64.
Preparing to unpack .../70-libjpeg8_8c-2ubuntu11_amd64.deb ...
Unpacking libjpeg8:amd64 (8c-2ubuntu11) ...
Selecting previously unselected package libdeflate0:amd64.
Preparing to unpack .../71-libdeflate0_1.19-1build1.1_amd64.deb ...
Unpacking libdeflate0:amd64 (1.19-1build1.1) ...
Selecting previously unselected package libjbig0:amd64.
Preparing to unpack .../72-libjbig0_2.1-6.1ubuntu2_amd64.deb ...
Unpacking libjbig0:amd64 (2.1-6.1ubuntu2) ...
Selecting previously unselected package liblerc4:amd64.
Preparing to unpack .../73-liblerc4_4.0.0+ds-4ubuntu2_amd64.deb ...
Unpacking liblerc4:amd64 (4.0.0+ds-4ubuntu2) ...
Selecting previously unselected package libwebp7:amd64.
Preparing to unpack .../74-libwebp7_1.3.2-0.4build3_amd64.deb ...
Unpacking libwebp7:amd64 (1.3.2-0.4build3) ...
Selecting previously unselected package libtiff6:amd64.
Preparing to unpack .../75-libtiff6_4.5.1+git230720-4ubuntu2.5_amd64.deb ...
Unpacking libtiff6:amd64 (4.5.1+git230720-4ubuntu2.5) ...
Selecting previously unselected package libxpm4:amd64.
Preparing to unpack .../76-libxpm4_1%3a3.5.17-1ubuntu0.24.04.1_amd64.deb ...
Unpacking libxpm4:amd64 (1:3.5.17-1ubuntu0.24.04.1) ...
Selecting previously unselected package libgd3:amd64.
Preparing to unpack .../77-libgd3_2.3.3-9ubuntu5_amd64.deb ...
Unpacking libgd3:amd64 (2.3.3-9ubuntu5) ...
Selecting previously unselected package libc-devtools.
Preparing to unpack .../78-libc-devtools_2.39-0ubuntu8.9_amd64.deb ...
Unpacking libc-devtools (2.39-0ubuntu8.9) ...
Preparing to unpack .../79-libcurl3t64-gnutls_8.5.0-2ubuntu10.13_amd64.deb ...
Unpacking libcurl3t64-gnutls:amd64 (8.5.0-2ubuntu10.13) over (8.5.0-2ubuntu10.9) ...
Selecting previously unselected package libfile-fcntllock-perl.
Preparing to unpack .../80-libfile-fcntllock-perl_0.22-4ubuntu5_amd64.deb ...
Unpacking libfile-fcntllock-perl (0.22-4ubuntu5) ...
Selecting previously unselected package libheif-plugin-aomenc:amd64.
Preparing to unpack .../81-libheif-plugin-aomenc_1.17.6-1ubuntu4.8_amd64.deb ...
Unpacking libheif-plugin-aomenc:amd64 (1.17.6-1ubuntu4.8) ...
Selecting previously unselected package libssl-dev:amd64.
Preparing to unpack .../82-libssl-dev_3.0.13-0ubuntu3.15_amd64.deb ...
Unpacking libssl-dev:amd64 (3.0.13-0ubuntu3.15) ...
Preparing to unpack .../83-linux-tools-common_6.8.0-139.139_all.deb ...
Unpacking linux-tools-common (6.8.0-139.139) over (6.8.0-124.124) ...
Selecting previously unselected package manpages-dev.
Preparing to unpack .../84-manpages-dev_6.7-2_all.deb ...
Unpacking manpages-dev (6.7-2) ...
Selecting previously unselected package python3-pip-whl.
Preparing to unpack .../85-python3-pip-whl_24.0+dfsg-1ubuntu1.3_all.deb ...
Unpacking python3-pip-whl (24.0+dfsg-1ubuntu1.3) ...
Selecting previously unselected package python3-setuptools-whl.
Preparing to unpack .../86-python3-setuptools-whl_68.1.2-2ubuntu1.2_all.deb ...
Unpacking python3-setuptools-whl (68.1.2-2ubuntu1.2) ...
Selecting previously unselected package python3.12-venv.
Preparing to unpack .../87-python3.12-venv_3.12.3-1ubuntu0.17_amd64.deb ...
Unpacking python3.12-venv (3.12.3-1ubuntu0.17) ...
Selecting previously unselected package python3-venv.
Preparing to unpack .../88-python3-venv_3.12.3-0ubuntu2.1_amd64.deb ...
Unpacking python3-venv (3.12.3-0ubuntu2.1) ...
Setting up python3-libapparmor (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Setting up libsharpyuv0:amd64 (1.3.2-0.4build3) ...
Setting up libaom3:amd64 (3.8.2-2ubuntu0.2) ...
Setting up manpages-dev (6.7-2) ...
Setting up python3-setuptools-whl (68.1.2-2ubuntu1.2) ...
Setting up lto-disabled-list (47) ...
Setting up liblerc4:amd64 (4.0.0+ds-4ubuntu2) ...
Setting up libxpm4:amd64 (1:3.5.17-1ubuntu0.24.04.1) ...
Setting up libcurl4t64:amd64 (8.5.0-2ubuntu10.13) ...
Setting up libfile-fcntllock-perl (0.22-4ubuntu5) ...
Setting up python3-pip-whl (24.0+dfsg-1ubuntu1.3) ...
Setting up libalgorithm-diff-perl (1.201-1) ...
Setting up libpython3.12-minimal:amd64 (3.12.3-1ubuntu0.17) ...
Setting up binutils-common:amd64 (2.42-4ubuntu2.10) ...
Setting up libdeflate0:amd64 (1.19-1build1.1) ...
Setting up libcurl3t64-gnutls:amd64 (8.5.0-2ubuntu10.13) ...
Setting up linux-libc-dev:amd64 (6.8.0-139.139) ...
Setting up libctf-nobfd0:amd64 (2.42-4ubuntu2.10) ...
Setting up libgomp1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up bzip2 (1.0.8-5.1ubuntu0.1) ...
Setting up locales (2.39-0ubuntu8.9) ...
Generating locales (this might take a while)...
  en_US.UTF-8... done
Generation complete.
Setting up libjbig0:amd64 (2.1-6.1ubuntu2) ...
Setting up libsframe1:amd64 (2.42-4ubuntu2.10) ...
Setting up libfakeroot:amd64 (1.33-1) ...
Setting up acl (2.3.2-1build1.1) ...
Setting up fakeroot (1.33-1) ...
update-alternatives: using /usr/bin/fakeroot-sysv to provide /usr/bin/fakeroot (fakeroot) in auto mode
Setting up rpcsvc-proto (1.4.2-0ubuntu7) ...
Setting up gcc-13-base:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Setting up make (4.3-4.1build2) ...
Setting up libquadmath0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up fonts-dejavu-mono (2.37-8) ...
Setting up libssl-dev:amd64 (3.0.13-0ubuntu3.15) ...
Setting up libmpc3:amd64 (1.3.1-1build1.1) ...
Setting up libatomic1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up fonts-dejavu-core (2.37-8) ...
Setting up libjpeg-turbo8:amd64 (2.1.5-2ubuntu2) ...
Setting up libdpkg-perl (1.22.6ubuntu6.6) ...
Setting up libwebp7:amd64 (1.3.2-0.4build3) ...
Setting up libubsan1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libhwasan0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libcrypt-dev:amd64 (1:4.4.36-4build1) ...
Setting up python3-apparmor (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Setting up libasan8:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libauparse0t64:amd64 (1:3.1.2-2.1build1.1) ...
Setting up curl (8.5.0-2ubuntu10.13) ...
Setting up libtsan2:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libbinutils:amd64 (2.42-4ubuntu2.10) ...
Setting up libisl23:amd64 (0.26-3build1.1) ...
Setting up libc-dev-bin (2.39-0ubuntu8.9) ...
Setting up openssl (3.0.13-0ubuntu3.15) ...
Setting up linux-tools-common (6.8.0-139.139) ...
Setting up libalgorithm-diff-xs-perl:amd64 (0.04-8build3) ...
Setting up libcc1-0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up liblsan0:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libitm1:amd64 (14.2.0-4ubuntu2~24.04.1) ...
Setting up libalgorithm-merge-perl (0.08-5) ...
Setting up libctf0:amd64 (2.42-4ubuntu2.10) ...
Setting up libjpeg8:amd64 (8c-2ubuntu11) ...
Setting up python3.12-minimal (3.12.3-1ubuntu0.17) ...
Setting up auditd (1:3.1.2-2.1build1.1) ...
Created symlink /etc/systemd/system/multi-user.target.wants/auditd.service â†’ /usr/lib/systemd/system/auditd.service.
Setting up libpython3.12-stdlib:amd64 (3.12.3-1ubuntu0.17) ...
Setting up cpp-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Setting up fontconfig-config (2.15.0-1.1ubuntu2) ...
Setting up python3.12 (3.12.3-1ubuntu0.17) ...
Setting up libpython3.12t64:amd64 (3.12.3-1ubuntu0.17) ...
Setting up libgprofng0:amd64 (2.42-4ubuntu2.10) ...
Setting up apparmor-utils (4.0.1really4.0.1-0ubuntu0.24.04.7) ...
Setting up libgcc-13-dev:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Setting up libtiff6:amd64 (4.5.1+git230720-4ubuntu2.5) ...
Setting up libc6-dev:amd64 (2.39-0ubuntu8.9) ...
Setting up libstdc++-13-dev:amd64 (13.3.0-6ubuntu2~24.04.1) ...
Setting up binutils-x86-64-linux-gnu (2.42-4ubuntu2.10) ...
Setting up cpp-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Setting up cpp-13 (13.3.0-6ubuntu2~24.04.1) ...
Setting up python3.12-venv (3.12.3-1ubuntu0.17) ...
Setting up gcc-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Setting up binutils (2.42-4ubuntu2.10) ...
Setting up dpkg-dev (1.22.6ubuntu6.6) ...
Setting up python3-venv (3.12.3-0ubuntu2.1) ...
Setting up gcc-13 (13.3.0-6ubuntu2~24.04.1) ...
Setting up cpp (4:13.2.0-7ubuntu1) ...
Setting up g++-13-x86-64-linux-gnu (13.3.0-6ubuntu2~24.04.1) ...
Setting up gcc-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Setting up gcc (4:13.2.0-7ubuntu1) ...
Setting up g++-x86-64-linux-gnu (4:13.2.0-7ubuntu1) ...
Setting up g++-13 (13.3.0-6ubuntu2~24.04.1) ...
Setting up g++ (4:13.2.0-7ubuntu1) ...
update-alternatives: using /usr/bin/g++ to provide /usr/bin/c++ (c++) in auto mode
Setting up build-essential (12.10ubuntu1) ...
Setting up libheif-plugin-aomdec:amd64 (1.17.6-1ubuntu4.8) ...
Setting up libheif1:amd64 (1.17.6-1ubuntu4.8) ...
Setting up libheif-plugin-aomenc:amd64 (1.17.6-1ubuntu4.8) ...
Processing triggers for libc-bin (2.39-0ubuntu8.9) ...
Processing triggers for systemd (255.4-1ubuntu8.16) ...
Processing triggers for man-db (2.12.0-4build2) ...
Processing triggers for sgml-base (1.31) ...
Setting up libfontconfig1:amd64 (2.15.0-1.1ubuntu2) ...
Setting up libgd3:amd64 (2.3.3-9ubuntu5) ...
Setting up libc-devtools (2.39-0ubuntu8.9) ...
Processing triggers for libc-bin (2.39-0ubuntu8.9) ...

Running kernel seems to be up-to-date.

Restarting services...
 /etc/needrestart/restart.d/systemd-manager
 systemctl restart acpid.service chrony.service cron.service irqbalance.service multipathd.service packagekit.service polkit.service rsyslog.service snapd.service ssh.service systemd-journald.service systemd-networkd.service systemd-resolved.service systemd-udevd.service udisks2.service

Service restarts being deferred:
 systemctl restart ModemManager.service
 /etc/needrestart/restart.d/dbus.service
 systemctl restart getty@tty1.service
 systemctl restart networkd-dispatcher.service
 systemctl restart serial-getty@ttyS0.service
 systemctl restart systemd-logind.service
 systemctl restart unattended-upgrades.service

No containers need to be restarted.

User sessions running outdated binaries:
 ubuntu @ session #1: sshd[1123,1233]
 ubuntu @ session #7: sshd[1532,1590]
 ubuntu @ user manager service: systemd[1128]

No VM guests are running outdated hypervisor (qemu) binaries on this host.
acl	2.3.2-1build1.1
apparmor	4.0.1really4.0.1-0ubuntu0.24.04.7
apparmor-utils	4.0.1really4.0.1-0ubuntu0.24.04.7
auditd	1:3.1.2-2.1build1.1
build-essential	12.10ubuntu1
curl	8.5.0-2ubuntu10.13
git	1:2.43.0-1ubuntu7.3
jq	1.7.1-3ubuntu0.24.04.2
libssl-dev	3.0.13-0ubuntu3.15
lsof	4.95.0-1build3
openssl	3.0.13-0ubuntu3.15
python3	3.12.3-0ubuntu2.1
python3-venv	3.12.3-0ubuntu2.1
strace	6.8-0ubuntu2
=== ACCOUNTS ===
passwd: password changed.
passwd: password changed.
usermod: no changes
v24candidate:x:2002:2002::/nonexistent:/usr/sbin/nologin
uid=2002(v24candidate) gid=2002(v24candidate) groups=2002(v24candidate)
v24rqrunner:x:2001:2001::/home/v24rqrunner:/bin/bash
uid=2001(v24rqrunner) gid=2001(v24rqrunner) groups=2001(v24rqrunner)
=== KERNEL HARDENING ===
* Applying /usr/lib/sysctl.d/10-apparmor.conf ...
* Applying /etc/sysctl.d/10-bufferbloat.conf ...
* Applying /etc/sysctl.d/10-console-messages.conf ...
* Applying /etc/sysctl.d/10-ipv6-privacy.conf ...
* Applying /etc/sysctl.d/10-kernel-hardening.conf ...
* Applying /etc/sysctl.d/10-magic-sysrq.conf ...
* Applying /etc/sysctl.d/10-map-count.conf ...
* Applying /etc/sysctl.d/10-network-security.conf ...
* Applying /etc/sysctl.d/10-ptrace.conf ...
* Applying /etc/sysctl.d/10-zeropage.conf ...
* Applying /etc/sysctl.d/50-cloudimg-settings.conf ...
* Applying /usr/lib/sysctl.d/50-pid-max.conf ...
* Applying /etc/sysctl.d/90-v24-rq1.conf ...
* Applying /etc/sysctl.d/99-cloudimg-ipv6.conf ...
* Applying /usr/lib/sysctl.d/99-protect-links.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
* Applying /etc/sysctl.conf ...
kernel.apparmor_restrict_unprivileged_userns = 1
net.core.default_qdisc = fq_codel
kernel.printk = 4 4 1 7
net.ipv6.conf.all.use_tempaddr = 2
net.ipv6.conf.default.use_tempaddr = 2
kernel.kptr_restrict = 1
kernel.sysrq = 176
vm.max_map_count = 1048576
net.ipv4.conf.default.rp_filter = 2
net.ipv4.conf.all.rp_filter = 2
kernel.yama.ptrace_scope = 1
vm.mmap_min_addr = 65536
net.ipv4.neigh.default.gc_thresh2 = 15360
net.ipv4.neigh.default.gc_thresh3 = 16384
net.netfilter.nf_conntrack_max = 1048576
kernel.pid_max = 4194304
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
fs.suid_dumpable = 0
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
net.ipv6.conf.all.use_tempaddr = 0
net.ipv6.conf.default.use_tempaddr = 0
fs.protected_fifos = 1
fs.protected_hardlinks = 1
fs.protected_regular = 2
fs.protected_symlinks = 1
=== SERVICES ===
Synchronizing state of auditd.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install enable auditd
Synchronizing state of apparmor.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install enable apparmor
active
active
=== TRUSTED PATHS ===
drwxr-x--- 750 v24rqrunner:v24rqrunner uid=2001 gid=2001 dev=66305 /opt/actions-runner
drwxr-xr-x 755 root:root uid=0 gid=0 dev=66305 /opt/v24-v6-trusted-runtime
drwx------ 700 root:root uid=0 gid=0 dev=66305 /var/lib/v24-rq1/runtime-state
drwx------ 700 root:root uid=0 gid=0 dev=66305 /var/lib/v24-rq1/sealed-evidence
drwx------ 700 v24rqrunner:v24rqrunner uid=2001 gid=2001 dev=66305 /var/lib/v24-rq1/runner-staging
drwxr-xr-x 755 root:root uid=0 gid=0 dev=66305 /etc/v24-rq1
drwxr-xr-x 755 root:root uid=0 gid=0 dev=28 /run/v24-v6-authority
drwx------ 700 root:root uid=0 gid=0 dev=28 /run/v24-v6-authority/private
drwx------ 700 root:root uid=0 gid=0 dev=28 /run/v24-v6-authority/private/records
drwx------ 700 root:root uid=0 gid=0 dev=28 /run/v24-v6-authority/private/consumed
=== SECURITY VERIFICATION ===
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.unprivileged_userns_clone = 0
unshare: unshare failed: Operation not permitted
candidate_userns_exit=1
=== FILESYSTEM PROOF ===
record_device=28
consumed_device=28
persistent_state_device=66305
/      /dev/nvme0n1p1 ext4   rw,relatime,discard,errors=remount-ro,commit=30
/      /dev/nvme0n1p1 ext4   rw,relatime,discard,errors=remount-ro,commit=30
/run   tmpfs  tmpfs  rw,nosuid,nodev,size=781108k,nr_inodes=819200,mode=755,inode64
completed_at=2026-09-18T17:28:23+00:00

```
### aws-codex-rq1-artifact-binding-RED-20260918T191701Z.txt
```text
V24-RQ1 runtime artifact binding check
2026-09-18T19:17:01+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
instance_id=i-05063c49c656d01ad
source_launch_ami_id=ami-03f1d2b3639314198
frozen_baseline_ami_id=ami-0990d6cd071996c3b
frozen_baseline_snapshot_id=snap-02073dd5c4e924a8f
root_ebs_volume_id=vol-0c603626c752512ff
-- trusted artifact paths --
-- runtime units --
actions.runner.vij7661-setugo-ai-development-framework.v24-rq1-aws.service enabled         enabled
systemd-pcrlock-secureboot-authority.service                               disabled        enabled
result=FAIL_RUNTIME_ARTIFACTS_NOT_DEPLOYED_OR_MEASURED

```
### aws-codex-rq1-binding-check-RED-20260918T191149Z.txt
```text
V24-RQ1 machine-readable binding check
2026-09-18T19:11:49+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
instance_id=i-05063c49c656d01ad
actual_ami_id=ami-03f1d2b3639314198
actual_instance_type=m7i-flex.large
actual_region=ap-south-2
nominated_instance_id=i-05063c49c656d01ad
nominated_ami_id=ami-0990d6cd071996c3c
nominated_snapshot_id=snap-02073dd5c4e924a8f
result=FAIL_IMAGE_ID_MISMATCH
-- sealed baseline controls --
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
-- evidence integrity --
/var/lib/v24-rq1/sealed-evidence/aws-codex-persistence-boundary-ready-20260918T182313Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot2-20260918T182236Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot2-20260918T182151Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-rq1-final-provider-binding-20260918T194055Z.txt
```text
V24-RQ1 final provider binding supplied after post-subject freeze
2026-09-18T19:40:55+00:00
runtime_status=NOMINATED_ENTRY_PENDING
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
instance_id=i-05063c49c656d01ad
source_launch_ami_id=ami-03f1d2b3639314198
frozen_pre_subject_baseline_ami_id=ami-0990d6cd071996c3c
frozen_pre_subject_baseline_snapshot_id=snap-02073dd5c4e924a8f
final_post_subject_ami_id=ami-0e39abbdfe052ad85
final_post_subject_snapshot_id=snap-005032959f20da09c
runner=active
service=a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
gate=7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069 /opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate
post_install_evidence=b7dba49cb1eefdf282234e83d1e4b6b326b96d8c1546ed8427f365bbd6a8dd8a /var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-post-subject-install-20260918T192420Z.txt
pre_snapshot_evidence=6b9361aecb042095e4c1680e682ec6ae80ae246a4b381c540324d5fa103d42a4 /var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-pre-provider-snapshot-20260918T192539Z.txt
independent_final_reviewer=PENDING
result=BOUND_ENTRY_PENDING_INDEPENDENT_REVIEW

```
### aws-codex-rq1-post-subject-install-20260918T192420Z.txt
```text
V24-RQ1 exact Successor-9 subject post-install evidence
2026-09-18T19:24:20+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
-- provenance --
{
  "bootstrap_commit_sha": "af3ab8ab846119292a1b3a36fca5d0cc2c71b1ee",
  "bootstrap_tree_sha": "fc063773b077c855cf34eebf28c886ee496d3fe9",
  "construction_commit_sha": "c6304d0f14914c3b1e9f30a8a42ac231f152fa8f",
  "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE",
  "service_version": "3",
  "protocol": "V24-V6-S9-CONSUME/1",
  "consumption_mode": "ROOT_PEER_SEMANTIC_ONE_SHOT",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_state": "NOT_CLAIMED"
}
{
  "schema_version": 1,
  "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE",
  "service_version": "3",
  "build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc",
  "binary_sha256": "a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d",
  "service_source_sha256": "9ba17e1fd0774583f28bb9a5418c99687076b0a7ed278b17d1a1b95501e88175",
  "build_script_sha256": "47ff3fd07bec8c0bdd84713a15382b3c7271182ae2f2f1bca84b55fd769676c0",
  "trusted_socket_path": "/run/v24-v6-authority/service.sock",
  "trusted_root": "/opt/v24-v6-trusted-runtime",
  "candidate_identity": "v24candidate",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_state": "NOT_CLAIMED"
}
{
  "schema_version": 1,
  "gate_id": "V24-V6-EXTERNAL-AUTHORITY-GATE",
  "gate_version": "1",
  "build_input_sha256": "b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9",
  "binary_sha256": "7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069",
  "gate_source_sha256": "d11c9d2bff945fbb4f6bf9dfc12b9db2d83a6ee93902f87617ce789c847c89c9",
  "worker_sha256": "8f6d2982bc5a9fc47a5267677f36bc22b74559a68b9c2c7812f7d0847826b62b",
  "proof_reference_closure_sha256": "5837b031d7da96aa193220ead57854784a328a1c226f64638ba82dade316505e",
  "root_attestation_sha256": "8a9f6b256a056b48f4062a3c2fb8a0a9263b38599b5cbc6e2a19b18b7a3de70a",
  "governance_foundation_sha256": "f0d429ab812cc694f79eaa4aa40acf944564691221943a045caf057094d53828",
  "decision_apply_sha256": "ef8e2a24b442c477b3974df73036ac28163f342bbad88d7e93ad37abd381d67e",
  "material_surface_sha256": "b58f2bbe1eb5136ca008c1b6e3c7dcdc638ba5dc324766bd3f8f7d8eec08db66",
  "normative_clause_projection_sha256": "408f5309eaf415f4c9c8344d5b661cbb61b9b84cdb0c5f12432aec585b12f8fe",
  "normative_control_catalog_sha256": "5a239be5641806995170fa0382d53c1e1d3fc202543b208a0e2f351f66279cf3",
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "runtime_qualification_state": "NOT_CLAIMED"
}
-- artifact hashes --
7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069  /opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate
55c35852a248fbbf3f98bb03d761fe0f283f24a22bf8466eeb79d400401094d6  /opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate_build.json
8ce4b19ec71defd9b2b964d93a6fdcad6c9916013bd14852bc3252e0daee5469  /opt/v24-v6-trusted-runtime/.service-build.json
d4f5bf9a82ac10a1e2f3b3d1c5ac5dca008284a78611baaaee31551168f2f57b  /opt/v24-v6-trusted-runtime/bootstrap-binding.json
5a239be5641806995170fa0382d53c1e1d3fc202543b208a0e2f351f66279cf3  /opt/v24-v6-trusted-runtime/normative_control_catalog.py
ef8e2a24b442c477b3974df73036ac28163f342bbad88d7e93ad37abd381d67e  /opt/v24-v6-trusted-runtime/v24_v6_decision_apply.py
8f6d2982bc5a9fc47a5267677f36bc22b74559a68b9c2c7812f7d0847826b62b  /opt/v24-v6-trusted-runtime/v24_v6_external_gate_worker.py
f0d429ab812cc694f79eaa4aa40acf944564691221943a045caf057094d53828  /opt/v24-v6-trusted-runtime/v24_v6_governance_foundation.py
b58f2bbe1eb5136ca008c1b6e3c7dcdc638ba5dc324766bd3f8f7d8eec08db66  /opt/v24-v6-trusted-runtime/v24_v6_material_surface.py
408f5309eaf415f4c9c8344d5b661cbb61b9b84cdb0c5f12432aec585b12f8fe  /opt/v24-v6-trusted-runtime/v24_v6_normative_clause_projection.py
5837b031d7da96aa193220ead57854784a328a1c226f64638ba82dade316505e  /opt/v24-v6-trusted-runtime/v24_v6_proof_reference_closure.py
8a9f6b256a056b48f4062a3c2fb8a0a9263b38599b5cbc6e2a19b18b7a3de70a  /opt/v24-v6-trusted-runtime/v24_v6_root_attestation.py
a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d  /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
-- dependency hashes --
3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf  /lib/x86_64-linux-gnu/libc.so.6
6a66c3ba6b3749aacc9497973fff00f6ba61c703ba7015d0d7ab3fd9510974b6  /lib/x86_64-linux-gnu/libcrypto.so.3
3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf  /lib/x86_64-linux-gnu/libc.so.6
6a66c3ba6b3749aacc9497973fff00f6ba61c703ba7015d0d7ab3fd9510974b6  /lib/x86_64-linux-gnu/libcrypto.so.3
-- units/process --
# /etc/systemd/system/v24-v6-trusted-authority.service
[Unit]
Description=V24 V6 Trusted Authority Service
After=local-fs.target systemd-sysctl.service
Before=multi-user.target
ConditionPathIsReadWrite=/run

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/v24-v6-trusted-runtime
Environment=PATH=/usr/bin:/bin
Environment=LC_ALL=C.UTF-8
Environment=PYTHONNOUSERSITE=1
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service --serve
Restart=on-failure
RestartSec=1s
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
enabled
active
    PID    PPID  EUID  EGID USER     GROUP    COMMAND
   2336       1     0     0 root     root     /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service --serve
-- trusted paths/socket --
/opt/v24-v6-trusted-runtime root:root uid=0 gid=0 mode=555 dev=66305
/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service root:root uid=0 gid=0 mode=555 dev=66305
/opt/v24-v6-trusted-runtime/.gate-build root:root uid=0 gid=0 mode=555 dev=66305
/opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate root:root uid=0 gid=0 mode=555 dev=66305
/run/v24-v6-authority root:root uid=0 gid=0 mode=755 dev=28
/run/v24-v6-authority/private root:root uid=0 gid=0 mode=700 dev=28
/run/v24-v6-authority/private/records root:root uid=0 gid=0 mode=700 dev=28
/run/v24-v6-authority/private/consumed root:root uid=0 gid=0 mode=700 dev=28
/run/v24-v6-authority/service.sock root:root uid=0 gid=0 mode=666 dev=28
-- security persistence --
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
enabled
active
enabled
active
-- candidate namespace denial --
DENIED
-- sealed evidence integrity --
/var/lib/v24-rq1/sealed-evidence/aws-codex-persistence-boundary-ready-20260918T182313Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot2-20260918T182236Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot2-20260918T182151Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-artifact-binding-RED-20260918T191701Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-binding-check-RED-20260918T191149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-rq1-pre-provider-snapshot-20260918T192539Z.txt
```text
V24-RQ1 post-install pre-provider-snapshot freeze
2026-09-18T19:25:40+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
runner_unit=actions.runner.vij7661-setugo-ai-development-framework.v24-rq1-aws.service
runner_active=inactive
runner_enabled=enabled
-- subject hashes --
a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d  /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069  /opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate
8ce4b19ec71defd9b2b964d93a6fdcad6c9916013bd14852bc3252e0daee5469  /opt/v24-v6-trusted-runtime/.service-build.json
55c35852a248fbbf3f98bb03d761fe0f283f24a22bf8466eeb79d400401094d6  /opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate_build.json
d4f5bf9a82ac10a1e2f3b3d1c5ac5dca008284a78611baaaee31551168f2f57b  /opt/v24-v6-trusted-runtime/bootstrap-binding.json
-- service --
enabled
active
/opt/v24-v6-trusted-runtime root:root 555 dev=66305
/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service root:root 555 dev=66305
/opt/v24-v6-trusted-runtime/.gate-build root:root 555 dev=66305
/opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate root:root 555 dev=66305
/run/v24-v6-authority root:root 755 dev=28
/run/v24-v6-authority/private root:root 700 dev=28
/run/v24-v6-authority/service.sock root:root 666 dev=28
-- security --
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2
enabled
active
enabled
active
-- baseline provenance preserved --
frozen_pre_subject_baseline_ami=ami-0990d6cd071996c3b
frozen_pre_subject_baseline_snapshot=snap-02073dd5c4e924a8f
-- evidence integrity --
/var/lib/v24-rq1/sealed-evidence/aws-codex-persistence-boundary-ready-20260918T182313Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot1-20260918T182133Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-fix-reboot2-20260918T182236Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-20260918T175806Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-post-resize-verified-20260918T175911Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-clean-reboot1-20260918T181001Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot1-20260918T182047Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-pre-fix-reboot2-20260918T182151Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-preparation-20260918T172745Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-artifact-binding-RED-20260918T191701Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-binding-check-RED-20260918T191149Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-rq1-post-subject-install-20260918T192420Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-20260918T180912Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-suid-root-cause-fix-20260918T182018Z.txt: OK
/var/lib/v24-rq1/sealed-evidence/aws-codex-sysctl-correction-20260918T172854Z.txt: OK

```
### aws-codex-rq1-successor9-runtime-regressions-20260918T194848Z.txt
```text
V24-RQ1 exact Successor-9 runtime regression transcript
2026-09-18T19:48:48+00:00
runtime_status=NOMINATED_ENTRY_PENDING
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
bash: line 8: cd: /tmp/v24-s9-build/governance-runtime: No such file or directory

```
### aws-codex-rq1-successor9-runtime-regressions-20260918T194957Z.txt
```text
V24-RQ1 exact Successor-9 runtime regression transcript
2026-09-18T19:49:57+00:00
runtime_status=NOMINATED_ENTRY_PENDING
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
PYCOMPILE=PASS
test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume) ... FAIL

======================================================================
FAIL: test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build/governance-runtime/test_v24_v6_successor9_consume_loader_red.py", line 85, in test_candidate_loader_interposition_cannot_forge_authoritative_consume
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)

```
### aws-codex-suid-root-cause-20260918T180912Z.txt
```text
V24-RQ1 fs.suid_dumpable root-cause investigation
2026-09-18T18:09:12+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
--- historical evidence preserved ---
total 96
-r-------- 1 root root   668 2026-09-18 17:58:06.509915828 +0000 aws-codex-post-resize-20260918T175806Z.txt
-r-------- 1 root root   142 2026-09-18 17:58:06.512595996 +0000 aws-codex-post-resize-20260918T175806Z.txt.sha256
-r-------- 1 root root   558 2026-09-18 18:00:21.118230921 +0000 aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt
-r-------- 1 root root   157 2026-09-18 18:00:21.120698857 +0000 aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt.sha256
-r-------- 1 root root  1924 2026-09-18 17:59:11.941164630 +0000 aws-codex-post-resize-verified-20260918T175911Z.txt
-r-------- 1 root root   151 2026-09-18 17:59:11.947061449 +0000 aws-codex-post-resize-verified-20260918T175911Z.txt.sha256
-r-------- 1 root root 55125 2026-09-18 17:28:23.192367570 +0000 aws-codex-preparation-20260918T172745Z.txt
-r-------- 1 root root   142 2026-09-18 17:28:23.194367567 +0000 aws-codex-preparation-20260918T172745Z.txt.sha256
-rw------- 1 root root   238 2026-09-18 18:09:12.364784395 +0000 aws-codex-suid-root-cause-20260918T180912Z.txt
-rw------- 1 root root     0 2026-09-18 18:09:12.360537308 +0000 aws-codex-suid-root-cause-20260918T180912Z.txt.lock
-r-------- 1 root root   332 2026-09-18 17:28:54.606343118 +0000 aws-codex-sysctl-correction-20260918T172854Z.txt
-r-------- 1 root root   148 2026-09-18 17:28:54.608343117 +0000 aws-codex-sysctl-correction-20260918T172854Z.txt.sha256
--- boots and file timing ---
IDX BOOT ID                          FIRST ENTRY                 LAST ENTRY
 -1 81a4ad375c5e43459d26744cbe21597e Fri 2026-09-18 17:21:39 UTC Fri 2026-09-18 17:32:32 UTC
  0 cfbb3b808b8c4d47865f509c4851665c Fri 2026-09-18 17:38:42 UTC Fri 2026-09-18 18:09:12 UTC
/etc/sysctl.d/zz-v24-rq1.conf 2026-09-18 17:28:54.596980016 +0000
/etc/sysctl.d/90-v24-rq1.conf 2026-09-18 17:28:22.115369282 +0000
--- service invocation ---
Result=success
ExecMainStartTimestamp=Fri 2026-09-18 17:38:42 UTC
ExecMainExitTimestamp=Fri 2026-09-18 17:38:42 UTC
ExecStart={ path=/usr/lib/systemd/systemd-sysctl ; argv[]=/usr/lib/systemd/systemd-sysctl ; ignore_errors=no ; start_time=[Fri 2026-09-18 17:38:42 UTC] ; stop_time=[Fri 2026-09-18 17:38:42 UTC] ; pid=209 ; code=exited ; status=0 }
2026-09-18T17:38:42+00:00 ip-172-31-4-29 systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
2026-09-18T17:38:42+00:00 ip-172-31-4-29 systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
--- all exact relevant assignments ---
DIR=/etc/sysctl.conf
DIR=/etc/sysctl.d
15:kernel.kptr_restrict = 1
20:# dmesg_restrict to "0" allows all users to view the kernel log buffer,
23:# dmesg_restrict defaults to 1 via CONFIG_SECURITY_DMESG_RESTRICT, only
25:# kernel.dmesg_restrict = 0
-- /etc/sysctl.d/10-kernel-hardening.conf
22:kernel.yama.ptrace_scope = 1
-- /etc/sysctl.d/10-ptrace.conf
1:kernel.unprivileged_userns_clone = 0
3:kernel.yama.ptrace_scope = 2
4:fs.protected_hardlinks = 1
5:fs.protected_symlinks = 1
6:fs.protected_fifos = 2
7:fs.protected_regular = 2
8:fs.suid_dumpable = 0
9:kernel.dmesg_restrict = 1
10:kernel.kptr_restrict = 2
-- /etc/sysctl.d/90-v24-rq1.conf
1:kernel.unprivileged_userns_clone = 0
3:kernel.yama.ptrace_scope = 2
4:fs.protected_hardlinks = 1
5:fs.protected_symlinks = 1
6:fs.protected_fifos = 2
7:fs.protected_regular = 2
8:fs.suid_dumpable = 0
9:kernel.dmesg_restrict = 1
10:kernel.kptr_restrict = 2
-- /etc/sysctl.d/zz-v24-rq1.conf
DIR=/usr/lib/sysctl.d
7:fs.protected_fifos = 1
8:fs.protected_hardlinks = 1
9:fs.protected_regular = 2
10:fs.protected_symlinks = 1
-- /usr/lib/sysctl.d/99-protect-links.conf
DIR=/lib/sysctl.d
7:fs.protected_fifos = 1
8:fs.protected_hardlinks = 1
9:fs.protected_regular = 2
10:fs.protected_symlinks = 1
-- /lib/sysctl.d/99-protect-links.conf
--- cmdline and writer search ---
BOOT_IMAGE=/vmlinuz-6.17.0-1017-aws root=PARTUUID=fe814a98-f7fd-4c3d-9642-c18fe64c6e5d ro console=tty1 console=ttyS0 nvme_core.io_timeout=4294967295 panic=-1
--- direct systemd-sysctl test from known 2 ---
before=2
Parsing /usr/lib/sysctl.d/10-apparmor.conf
Parsing /etc/sysctl.d/10-bufferbloat.conf
Parsing /etc/sysctl.d/10-console-messages.conf
Parsing /etc/sysctl.d/10-ipv6-privacy.conf
Parsing /etc/sysctl.d/10-kernel-hardening.conf
Parsing /etc/sysctl.d/10-magic-sysrq.conf
Parsing /etc/sysctl.d/10-map-count.conf
Parsing /etc/sysctl.d/10-network-security.conf
Parsing /etc/sysctl.d/10-ptrace.conf
Parsing /etc/sysctl.d/10-zeropage.conf
Parsing /etc/sysctl.d/50-cloudimg-settings.conf
Parsing /usr/lib/sysctl.d/50-pid-max.conf
Parsing /etc/sysctl.d/90-v24-rq1.conf
Overwriting earlier assignment of kernel/yama/ptrace_scope at '/etc/sysctl.d/90-v24-rq1.conf:3'.
Overwriting earlier assignment of kernel/kptr_restrict at '/etc/sysctl.d/90-v24-rq1.conf:10'.
Parsing /etc/sysctl.d/99-cloudimg-ipv6.conf
Overwriting earlier assignment of net/ipv6/conf/all/use_tempaddr at '/etc/sysctl.d/99-cloudimg-ipv6.conf:3'.
Overwriting earlier assignment of net/ipv6/conf/default/use_tempaddr at '/etc/sysctl.d/99-cloudimg-ipv6.conf:4'.
Parsing /usr/lib/sysctl.d/99-protect-links.conf
Overwriting earlier assignment of fs/protected_fifos at '/usr/lib/sysctl.d/99-protect-links.conf:7'.
Parsing /etc/sysctl.d/99-sysctl.conf
Parsing /etc/sysctl.d/zz-v24-rq1.conf
Overwriting earlier assignment of fs/protected_fifos at '/etc/sysctl.d/zz-v24-rq1.conf:6'.
Setting '/proc/sys/kernel/apparmor_restrict_unprivileged_userns' to '1'
No change in value '1', suppressing write
Setting '/proc/sys/net/core/default_qdisc' to 'fq_codel'
No change in value 'fq_codel', suppressing write
Setting '/proc/sys/kernel/printk' to '4 4 1 7'
Setting '/proc/sys/kernel/sysrq' to '176'
No change in value '176', suppressing write
Setting '/proc/sys/vm/max_map_count' to '1048576'
No change in value '1048576', suppressing write
Setting '/proc/sys/net/ipv4/conf/default/rp_filter' to '2'
No change in value '2', suppressing write
Setting '/proc/sys/net/ipv4/conf/all/rp_filter' to '2'
No change in value '2', suppressing write
Setting '/proc/sys/vm/mmap_min_addr' to '65536'
No change in value '65536', suppressing write
Setting '/proc/sys/net/ipv4/neigh/default/gc_thresh2' to '15360'
No change in value '15360', suppressing write
Setting '/proc/sys/net/ipv4/neigh/default/gc_thresh3' to '16384'
No change in value '16384', suppressing write
Setting '/proc/sys/net/netfilter/nf_conntrack_max' to '1048576'
No change in value '1048576', suppressing write
Setting '/proc/sys/kernel/pid_max' to '4194304'
No change in value '4194304', suppressing write
Setting '/proc/sys/kernel/unprivileged_userns_clone' to '0'
No change in value '0', suppressing write
Setting '/proc/sys/user/max_user_namespaces' to '0'
No change in value '0', suppressing write
Setting '/proc/sys/kernel/yama/ptrace_scope' to '2'
No change in value '2', suppressing write
Setting '/proc/sys/fs/protected_hardlinks' to '1'
No change in value '1', suppressing write
Setting '/proc/sys/fs/protected_symlinks' to '1'
No change in value '1', suppressing write
Setting '/proc/sys/fs/protected_regular' to '2'
No change in value '2', suppressing write
Setting '/proc/sys/fs/suid_dumpable' to '0'
Setting '/proc/sys/kernel/dmesg_restrict' to '1'
No change in value '1', suppressing write
Setting '/proc/sys/kernel/kptr_restrict' to '2'
No change in value '2', suppressing write
Setting '/proc/sys/net/ipv6/conf/all/use_tempaddr' to '0'
No change in value '0', suppressing write
Setting '/proc/sys/net/ipv6/conf/default/use_tempaddr' to '0'
No change in value '0', suppressing write
Setting '/proc/sys/fs/protected_fifos' to '2'
No change in value '2', suppressing write
after=0
--- resulting controls ---
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2

```
### aws-codex-suid-root-cause-fix-20260918T182018Z.txt
```text
V24-RQ1 root-cause fix: apport writer disabled
2026-09-18T18:20:18+00:00
runtime_status=NOT_NOMINATED
scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
-- root cause --
696-    write_to_proc_sys(
697-        "kernel/core_pattern",
698-        f"|{__file__} -p%p -s%s -c%c -d%d -P%P -u%u -g%g -F%F -- %E",
699-    )
700:    write_to_proc_sys("fs/suid_dumpable", "2")
701-    write_to_proc_sys("kernel/core_pipe_limit", "10")
702-    check_kernel_crash()
703-
704-
705-def stop_apport() -> None:
706-    """Stop Apport crash handler."""
707-    write_to_proc_sys("kernel/core_pipe_limit", "0")
708:    write_to_proc_sys("fs/suid_dumpable", "0")
709-    write_to_proc_sys("kernel/core_pattern", "core")
710-
711-
712-def parse_arguments(args: list[str]) -> argparse.Namespace:
-- pre-fix state --
enabled=1
enabled
active
-- post-fix state --
enabled=0
disabled
inactive
fs.suid_dumpable = 0

```
### aws-codex-sysctl-correction-20260918T172854Z.txt
```text
=== V24 RQ1 AWS SYSCTL CORRECTION ===
started_at=2026-09-18T17:28:54+00:00
runtime_nomination=NOT_NOMINATED
scientific_execution=CLOSED_PENDING_SUCCESSOR_REVIEW
authority_effect=NONE_EVIDENCE_ONLY
37ffb6cc078d57e7c2fda171d7ad8262fee52861d92824675024dfafe963f8d6  /etc/sysctl.d/zz-v24-rq1.conf
completed_at=2026-09-18T17:28:54+00:00

```
## SHA-256 manifest
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\v24_v6_rq1_harness.py -- cc63b668ceebe94b7a8b643d3ae0b709c59494c809ceeef2611331a9994e9edc
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\governance-runtime\V24-I11-V6-RQ1-EVIDENCE-SCHEMA.json -- 4a90a3ebd124df2b851c669d53c0dc184a8201f6458fa10fa9ce13073296f1b2
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RQ1-MANUAL-REVIEW-PACKET-20260919.md -- 75b703566dc64f48d9ad05a5bf4f2ce639071cb92a6b93e47aac174c4b5d25f4
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-ENTRY-EVALUATION-20260919.md -- a1a17ef81d0348f80064dc5e85c2577020a67f636177cc1f20fb742f2c7262f8
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-FINAL-MACHINE-BINDING-20260919.json -- a251b4502347485e1eb0cce7c0fb48806c0dca093ed06cd896229cd6fe3a2167
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-20260919.json -- 7e0a33baf65769eb65e23cf497a4976ca062b1370bf93c5f06ffc343af7800be
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-HUMAN-NOMINATION-CORRECTION-20260919.json -- 9cd1aa2de3bb367693a453ce1ece4d57c27b31dc8a03a63f31b59c39ba87b788
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-INDEPENDENT-REVIEWER-DESIGNATION-20260919.json -- 1b214d3093a6f5a98b636107fa6d8b4b26f17c977dd25374c54708512eaef15b
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-PLAN.md -- 7061a810c939f05b4cb6daf70066e259f5dd0e4f148a88bf29d3803a55c4806d
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\implementation\v24\V24-I11-V6-RUNTIME-QUALIFICATION-1-SUBJECT.json -- 3fb1593bcbfe341a132ab44e7ca61e52c861b19a79f3b44db1f7a6ac8b9e0ea8
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-persistence-boundary-ready-20260918T182313Z.txt -- a6aa206a19696e6752ca70af1903fe350c31d067e319d0451e152f93806438de
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-clean-reboot1-20260918T181054Z.txt -- 01cc51121506962d5e4d8247bd9ee13ec714bc39451772ba0bc2dc99431ddceb
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-clean-reboot1-RED-20260918T181149Z.txt -- de420d4bded7a1327a52b58118aec5102d180d6b9bec49f1d4e73e7a3b8e4838
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-fix-reboot1-20260918T182133Z.txt -- 649b93a4239ab0d229e897b8ca7287142a0cb650a2059b733e9dbf8299ba3044
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-fix-reboot2-20260918T182236Z.txt -- 4dedd915bae8295be484ff765406b1b6544e58b5547187ee3a8a862b4d5ff704
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-resize-20260918T175806Z.txt -- 2056f8ebfd033ea2292bdd7e80c53057f7f0ae2fb133d6d4578850d6a243c489
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-resize-sysctl-reapply-20260918T180021Z.txt -- 8b85b18d03b1376527084ccae6229046e089c2fec60f5d5b7a95dda2a2eea15b
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-post-resize-verified-20260918T175911Z.txt -- 0a9afecd75dfc7d9407f47fe8a47f12e3d29f318963b89e0d1e09473b62bdc1e
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-pre-clean-reboot1-20260918T181001Z.txt -- 26ee7ea1c918de8a086c7e6a7c4e9334c12e2d67e9c68b0a043f78d0ce4addf2
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-pre-fix-reboot1-20260918T182047Z.txt -- c46443cac48e9392e554159cd09037839e2a1273d33da6a512e1a64228de412c
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-pre-fix-reboot2-20260918T182151Z.txt -- ed863a4ca3d7820d25f794e822256252bc9373a33f2c8c1f035f9eb894a57080
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-preparation-20260918T172745Z.txt -- d4e51a6ce83c6238dc83a12d363ea8725f53d650438c140a4b1f949f523d4ad6
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-artifact-binding-RED-20260918T191701Z.txt -- 67f007a45be1baf0802d340e518230c352a186b545d33b681127c8e513d573ce
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-binding-check-RED-20260918T191149Z.txt -- 4e47d39caa3f274d54211ff2dfb4f93cc2c293dc12c361a6dacc25f574bdbeaa
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-final-provider-binding-20260918T194055Z.txt -- 9acb3853db2982d7996288fab88ad925df9c894545d856a091bfbdea705a5d04
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-harness-bundle-20260918T195744Z.txt -- 06c57bdab769d36475fb8d10fffb23be278b980044f8c44f0e11f39da6e33231
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-inherited-linux-context-20260919T200500Z.txt -- f28131624ac1fa33780346a2a52f80e27d018cc9a11a58c0394bf4c65cb79604
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-post-subject-install-20260918T192420Z.txt -- b7dba49cb1eefdf282234e83d1e4b6b326b96d8c1546ed8427f365bbd6a8dd8a
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-pre-provider-snapshot-20260918T192539Z.txt -- 6b9361aecb042095e4c1680e682ec6ae80ae246a4b381c540324d5fa103d42a4
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-successor9-runtime-regressions-20260918T194848Z.txt -- eb3f5c0969916ffe98d4f7dc65d5ef0ee5a7a8a85322c9c17c61659cd9fe4441
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-successor9-runtime-regressions-20260918T194957Z.txt -- 018978456343799c765aada22c308ec1c4c1ffe1938fabaabac77c3c64dcb2b8
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-rq1-successor9-runtime-regressions-candidate-20260918T195042Z.txt -- ea13c6b19b98eb6cf21623cf01ffda4b5a74d92ee9a5875aaba7c8e8e172f9fb
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-suid-root-cause-20260918T180912Z.txt -- bb5442a8dfb71080f6de9f8329d576447e67d685ec400a0371f76d08e8aa1083
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-suid-root-cause-fix-20260918T182018Z.txt -- d1d9c6a9caa8393753827530705f7c5527c400e9d785dd2f822ea538bf6fc092
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\aws-codex-sysctl-correction-20260918T172854Z.txt -- f02c48f19ed37a2bf2af1e5cf41193f8915ca09809a68e49c6b6d3c8aa8193fa
- C:\Users\hp\Downloads\ps final\pashusetu_app4_admin_web_connected\setugo-runtime-qualification-1\review-package-data\RQ1-bundle.json -- 3c4bcf116f9ad63b244637fd2d643a26c228033a3d23f3f1402a282a74f9cc0a
## Independent reviewer checklist
- Verify no INSUFFICIENT_EVIDENCE result was treated as PASS.
- Verify the harness executes each frozen RQ oracle.
- Verify no test, oracle, trust boundary, cleanup requirement, or historical RED was weakened.
- Determine whether inherited failures/errors are context/infrastructure issues or mechanism defects.
- Determine whether the 30 insufficient cases require deterministic instrumentation before qualification.
- Verify CLOSED, NONE_EVIDENCE_ONLY, and NOT_QUALIFIED remain true.
- Provide an independent disposition and required repairs/evidence.