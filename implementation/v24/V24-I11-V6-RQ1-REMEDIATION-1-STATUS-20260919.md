# RQ1 Remediation 1 Status (not qualification)

Remediation branch: `qualification/v24-i11-v6-runtime-qualification-1-remediation-1`

Immutable starting review: Claude `CHANGES_REQUIRED`, reviewed HEAD `db1f5ccf3ecf5bdfc00d3309906a1ae7f4407bd0`, tree `98065947f636b7f8876e5212eefec6dd9b46b60b`. The original packet, results, RED evidence, and disposition are unchanged.

## Narrow repairs made

- PASS now requires an independently written raw artifact whose JSON content binds both `case_id` and the exact oracle; a result file cannot self-reference as evidence.
- Static self-tests cover exact 32-ID closure, unknown-ID rejection, evidence-less PASS rejection, self-reference rejection, cleanup/governance fail-closed state, and unimplemented-mode PASS prohibition.
- RQ-01/RQ-02 now perform candidate-side raw trusted-socket attempts with poisoned loader variables.
- RQ-03/RQ-04 exercise candidate-side raw root-control/socket attempts; RQ-23 performs a candidate user/mount-namespace bind attack.
- All other not-yet-materialized deployed-runtime triggers are explicitly `HARNESS_DEFECT`, never PASS.

## Remediation execution

Remediated harness self-test: PASS; 32 IDs; state remained `CLOSED_PENDING_SUCCESSOR_REVIEW`, `NONE_EVIDENCE_ONLY`, `NOT_QUALIFIED`.

Remediated VM bundle: `/var/lib/v24-rq1/rq1-remediation-run-20260919c/RQ1-bundle.json`; SHA-256 `94ab1589ff04b28aba53740c08111980aba924493da3fd7ddf4e55a01f94a326`.

Result: 32 cases, `PASS=5`, `HARNESS_DEFECT=27`, `RED=0`, `INSUFFICIENT_EVIDENCE=0`. The 27 defects explicitly state that a real deployed-runtime trigger is not materialized. This is not a qualification result.

Unchanged Successor-9 candidate regression rerun: exit 0, one test `OK`; sealed transcript `aws-codex-rq1-remediation-successor9-candidate-20260919T210000Z.txt` with its sidecar hash on the VM.

Inherited reruns were sealed in both contexts:

- candidate transcript SHA-256 `c398b0564cb06408e90825274b669f8d502d411cab7573d31d13f0c7f401d63c`;
- root transcript SHA-256 `f858334a9040d0126785ca23be638bc44f8550948e72ee9809969159bd33ae6c`.

The inherited failures/errors remain adjudication inputs, not silently converted to PASS. In particular, candidate-private socket visibility, root-only setup, gate digest/ownership assertions, and lifecycle assumptions are recorded in the raw transcripts for independent classification.

Runtime remains `NOT_QUALIFIED`; scientific execution remains `CLOSED`; authority effect remains `NONE_EVIDENCE_ONLY`. This remediation is incomplete and must not be presented as a qualification claim.

## Instrumented rerun and RQ-32 boundary

The prior empty-directory timeout is preserved as historical harness-defect evidence. Per-case JSONL logging then isolated the stall at `RQ-08`: candidate diagnostic/consume transport blocked until the bounded subprocess timeout. The instrumented run reached all 32 cases and produced bundle SHA-256 `27c774c93fccf097febc28655f91d6df6f215804ddb3a397bb4ab60d0753e417`. Counts were `PASS=19`, `HARNESS_DEFECT=13`, `RED=0`; unresolved IDs: `RQ-01`, `RQ-02`, `RQ-04`, `RQ-08`, `RQ-09`, `RQ-10`, `RQ-12`, `RQ-16`, `RQ-24`, `RQ-25`, `RQ-28`, `RQ-29`, `RQ-31`. The timeout and every case start/end timestamp remain append-only on the VM.

The authorized real RQ-32 reboot was executed. Pre-reboot and post-reboot transcripts are sealed on the VM. Post-reboot evidence revalidated service binary SHA-256 `a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d`, active/enabled service, socket listener, AppArmor/auditd, and all load-bearing sysctls. This is runtime evidence only; it does not qualify the subject.
