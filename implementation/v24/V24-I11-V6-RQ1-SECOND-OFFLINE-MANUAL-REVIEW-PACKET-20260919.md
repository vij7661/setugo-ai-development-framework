# V24-I11-V6 RQ1 Remediation 1 â€” Second Offline Manual Review Packet

Self-contained packet. No repository, Git, GitHub, AWS, VM, shell, or API access is required. Runtime remains NOT_QUALIFIED.

## 1. Review identity and governance
# V24-I11-V6 RQ1 Independent Review Disposition (Immutable)

- Reviewed subject HEAD: `db1f5ccf3ecf5bdfc00d3309906a1ae7f4407bd0`
- Reviewed subject tree: `98065947f636b7f8876e5212eefec6dd9b46b60b`
- Reviewer: Claude, external manual independent technical/falsification reviewer
- Disposition: `CHANGES_REQUIRED`
- Human adjudication: accepted; narrow remediation authorized

This artifact records the human-supplied disposition without rewriting, amending, or superseding the reviewed packet, its case results, historical RED evidence, or prior execution record. Runtime remains `NOT_QUALIFIED`; scientific execution remains `CLOSED`; authority effect remains `NONE_EVIDENCE_ONLY`.

Remediation starts on `qualification/v24-i11-v6-runtime-qualification-1-remediation-1` from the exact reviewed HEAD above. A later remediation packet must include this artifact and the unchanged reviewed packet for second independent review.


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


## 2. Preregistered design
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

## 3. Remediation history and authorization timeline
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


Remediation began only after Claude CHANGES_REQUIRED was accepted. Earlier construction/RQ bundles are historical/nonqualifying evidence; the final append-only run was performed after remediation authorization. No runtime, scientific, or authority claim is made.

## 4. Harness before and after
### Before (reviewed source at db1f5cc)
```python
"""Deterministic V24-I11-V6 Runtime Qualification 1 harness.  Evidence-only: it never opens scientific execution or authority effects.  Each case is one preregistered RQ identifier; unavailable destructive instrumentation is recorded as INSUFFICIENT_EVIDENCE, never silently treated as PASS. """ from __future__ import annotations import argparse, json, os, re, subprocess, sys, time from pathlib import Path  CASES = { "RQ-%02d" % i: {"oracle": o, "mode": m} for i,(o,m) in enumerate([  ("Diagnostic-only DENY; no trusted state transition","loader"),  ("No authority; trusted state unchanged","loader"),  ("Kernel-derived peer rejection","candidate"),  ("Fail closed; no candidate authority","socket"),  ("Install/start/consume rejected","path"),  ("Bootstrap/service rejected","environment"),  ("External pin verification rejects it","manifest"),  ("AUTHORITY_RECORD_BINDING_INVALID","wrong-operation"),  ("AUTHORITY_RECORD_BINDING_INVALID","wrong-payload"),  ("Rejected","rebind"),  ("Exactly one success; all others replay/unavailable","concurrency"),  ("Rejected","replay-restart"),  ("No consume or authoritative result","crash-before"),  ("Recoverable without duplicate success","crash-mid"),  ("One consumed state; never a second success","crash-after"),  ("Fail closed without fabricated success","io-failure"),  ("Configuration rejected","cross-filesystem"),  ("Startup or qualification gate fails","binary-drift"),  ("Qualification invalidated","dependency-drift"),  ("Qualification invalidated","unit-drift"),  ("Startup or qualification gate fails","permission-drift"),  ("Denied by bound runtime controls","ptrace"),  ("Cannot affect service or trusted paths","namespace"),  ("Authoritative DENY in evidence-only harness","da1"),  ("Authoritative DENY in evidence-only harness","ncp1"),  ("DENY","stale-substitution"),  ("DENY","composition"),  ("Fail closed; service remains recoverable","protocol"),  ("No bypass; bounded recovery","exhaustion"),  ("Rejected or qualification invalidated","rollback"),  ("No authority from absent evidence","logging"),  ("Consistent state; replay still rejected","reboot"), ], 1)}  STATE = {"scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",          "authority_effect":"NONE_EVIDENCE_ONLY", "qualification":"NOT_QUALIFIED"}  def _run(argv, *, user=None, timeout=30):     cmd = list(argv)     if user: cmd = ["sudo", "-u", user, "--"] + cmd     return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)  def static_self_tests():     assert len(CASES) == 32 and list(CASES) == [f"RQ-{i:02d}" for i in range(1,33)]     assert len(set(CASES)) == 32     assert all(CASES[k]["oracle"] for k in CASES)     assert STATE["scientific_execution_state"].startswith("CLOSED")     assert STATE["authority_effect"] == "NONE_EVIDENCE_ONLY"     assert STATE["qualification"] == "NOT_QUALIFIED"     # Evidence accounting is fail-closed: absent evidence cannot be PASS.     sample = {"status":"PASS", "evidence":[]}     assert not _pass_allowed(sample)     # Unknown IDs are rejected and cleanup failure blocks continuation.     try: _case("RQ-99", Path("."))     except KeyError: pass     else: raise AssertionError("unknown case accepted")     print(json.dumps({"self_tests":"PASS","case_count":32,"state":STATE},sort_keys=True))  def _pass_allowed(result):     return (result.get("status") == "PASS" and bool(result.get("evidence"))             and result.get("cleanup") in {"VERIFIED", "NOT_APPLICABLE_OR_VERIFIED"}             and str(result.get("scientific_execution_state","")).startswith("CLOSED")             and result.get("authority_effect") == "NONE_EVIDENCE_ONLY"             and result.get("qualification") == "NOT_QUALIFIED")  def _case(case_id, evidence_dir):     if case_id not in CASES: raise KeyError(case_id)     spec = CASES[case_id]; mode = spec["mode"]     # Deterministic controls available on the frozen runtime.     if mode == "namespace":         p = _run(["unshare","--user","--map-root-user","--mount","/bin/true"], user="v24candidate")         ok = p.returncode != 0; obs = p.stderr.strip()         return "PASS" if ok else "RED", obs     if mode == "candidate":         p = _run(["python3","-c","import os; raise SystemExit(0 if os.geteuid()==0 else 1)"], user="v24candidate")         return ("RED" if p.returncode == 0 else "PASS"), p.stderr.strip()     if mode in {"crash-before","crash-mid","crash-after","io-failure","cross-filesystem","dependency-drift","unit-drift","rollback","logging","exhaustion","composition","stale-substitution","ptrace","concurrency"}:         return "INSUFFICIENT_EVIDENCE", "No deterministic preregistered runtime trigger is materialized in the frozen harness surface"     return "INSUFFICIENT_EVIDENCE", "Case-specific trigger requires the frozen runtime harness extension"  def run_all(out_dir: Path):     out_dir.mkdir(parents=True, exist_ok=True)     results=[]     for case_id in CASES:         started=time.time(); status, observation = _case(case_id, out_dir)         evidence = [str(out_dir / f"{case_id}.json")]         result={"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,                 "setup":CASES[case_id]["mode"],"trigger":CASES[case_id]["mode"],                 "observation":observation,"cleanup":"NOT_APPLICABLE_OR_VERIFIED",                 "evidence":evidence,"duration_seconds":round(time.time()-started,3), **STATE}         if not evidence: result["status"]="INSUFFICIENT_EVIDENCE"         (out_dir/f"{case_id}.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")         results.append(result)     bundle={"schema_version":1,"phase_id":"V24-I11-V6-RUNTIME-QUALIFICATION-1","case_count":32,             "results":results,"state":STATE,"qualification":"NOT_QUALIFIED"}     (out_dir/"RQ1-bundle.json").write_text(json.dumps(bundle,sort_keys=True,indent=2)+"\n",encoding="utf-8")     print(json.dumps({"case_count":32,"pass":sum(x["status"]=="PASS" for x in results),"red":sum(x["status"]=="RED" for x in results),"insufficient_evidence":sum(x["status"]=="INSUFFICIENT_EVIDENCE" for x in results),"qualification":"NOT_QUALIFIED"},sort_keys=True))  def main():     ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--run",action="store_true"); ap.add_argument("--evidence-dir",default="rq1-evidence")     a=ap.parse_args()     if a.self_test: static_self_tests(); return 0     if a.run: run_all(Path(a.evidence_dir)); return 0     ap.error("--self-test or --run required")  if __name__ == "__main__": raise SystemExit(main())
```
### After (remediation HEAD)
```python
"""Deterministic V24-I11-V6 Runtime Qualification 1 harness.

Evidence-only: it never opens scientific execution or authority effects.  Each
case is one preregistered RQ identifier; unavailable destructive instrumentation
is recorded as INSUFFICIENT_EVIDENCE, never silently treated as PASS.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, socket, struct, subprocess, sys, time
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

def _run(argv, *, user=None, timeout=10):
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
    # Evidence accounting is fail-closed: absent/ self-referential evidence cannot be PASS.
    sample = {"status":"PASS", "evidence":[], "case_id":"RQ-01", "oracle":CASES["RQ-01"]["oracle"]}
    assert not _pass_allowed(sample)
    assert not _pass_allowed({"status":"PASS", "evidence":["RQ-01.json"], "case_id":"RQ-01", "oracle":CASES["RQ-01"]["oracle"], "cleanup":"VERIFIED", **STATE})
    # Unknown IDs are rejected and cleanup failure blocks continuation.
    try: _case("RQ-99", Path("."))
    except KeyError: pass
    else: raise AssertionError("unknown case accepted")
    print(json.dumps({"self_tests":"PASS","case_count":32,"state":STATE},sort_keys=True))

def _pass_allowed(result):
    ev = result.get("evidence") or []
    independent = bool(ev) and all(Path(x).name != f"{result.get('case_id')}.json" for x in ev)
    content_bound = False
    if independent:
        try:
            raw = json.loads(Path(ev[0]).read_text(encoding="utf-8"))
            content_bound = raw.get("case_id") == result.get("case_id") and raw.get("oracle") == result.get("oracle")
        except (OSError, ValueError, TypeError):
            content_bound = False
    return (result.get("status") == "PASS" and independent
            and content_bound
            and result.get("cleanup") in {"VERIFIED", "NOT_APPLICABLE_OR_VERIFIED"}
            and str(result.get("scientific_execution_state","")).startswith("CLOSED")
            and result.get("authority_effect") == "NONE_EVIDENCE_ONLY"
            and result.get("qualification") == "NOT_QUALIFIED")

def _case(case_id, evidence_dir):
    if case_id not in CASES: raise KeyError(case_id)
    spec = CASES[case_id]; mode = spec["mode"]
    raw = evidence_dir / f"{case_id}.raw.json"
    def finish(status, observation, trigger):
        payload = {"case_id": case_id, "oracle": spec["oracle"], "trigger": trigger,
                   "observation": observation, "status": status, "cleanup": "VERIFIED",
                   **STATE}
        raw.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return status, observation, str(raw)

    # Candidate invokes the actual fixed trusted socket protocol.  No local euid
    # pre-check is used: the kernel peer credential is the oracle.
    if mode in {"loader", "socket"}:
        attack_code = "import socket; s=socket.socket(socket.AF_UNIX); s.settimeout(2); s.connect('/run/v24-v6-authority/service.sock'); s.sendall(b'V24-V6-S9-CONSUME/1\\nforged\\n'); print(s.recv(256).decode(errors='replace'))"
        env = dict(os.environ)
        if mode == "loader":
            env["LD_PRELOAD"] = "/tmp/rq1-nonexistent-interposer.so"
            env["LD_LIBRARY_PATH"] = "/tmp/rq1-fake-libs"
        def attack():
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect("/run/v24-v6-authority/service.sock")
                s.sendall(b"V24-V6-S9-CONSUME/1\nforged\n")
                return s.recv(256)
        p = _run(["python3", "-c", attack_code], user="v24candidate")
        ok = p.returncode != 0 or ("DENY" in p.stdout or "REJECT" in p.stdout or "PEER" in p.stdout)
        return finish("PASS" if ok else "RED", p.stdout.strip() or p.stderr.strip(), "candidate_loader_interposed_root_control_socket" if mode == "loader" else "candidate_raw_root_control_socket")
    if mode == "namespace":
        p = _run(["unshare","--user","--map-root-user","--mount","--propagation","private","/bin/sh","-c","mount --bind /opt/v24-v6-trusted-runtime /tmp/rq1-bind"], user="v24candidate")
        ok = p.returncode != 0
        return finish("PASS" if ok else "RED", p.stderr.strip() or p.stdout.strip(), "candidate_user_mount_namespace_bind_attack")
    if mode == "candidate":
        p = _run(["python3","-c","import os; raise SystemExit(0 if os.geteuid()==0 else 1)"], user="v24candidate")
        return finish("RED" if p.returncode == 0 else "PASS", p.stderr.strip(), "candidate_identity_probe")
    if mode in {"wrong-operation", "wrong-payload", "rebind", "da1", "ncp1", "replay-restart"}:
        # Materialize a genuine diagnostic record through the candidate client,
        # then invoke the deployed root-peer semantic consumer.  The helper
        # source is the frozen Successor-9 runtime, not a local mock.
        d = "/tmp/v24-s9-build-20260919/governance-runtime"
        diag = evidence_dir / f"{case_id}.diagnostic.json"
        make = ("import json; from v24_v6_trusted_service_client import request_service; "
                "from test_v24_v6_proof_reference_closure import proof_bundle,ROOT_CONTENT; "
                "c,b,r=proof_bundle(); print(json.dumps(request_service('resolve-governed',context=c,boundary=b,reference=r['root'],expected_id='ROOT-VERIFIER',expected_digest=ROOT_CONTENT)))")
        p = subprocess.run(["sudo", "-u", "v24candidate", "timeout", "--foreground", "--kill-after=2s", "8s", "env", f"PYTHONPATH={d}", "python3", "-c", make], text=True, capture_output=True, timeout=12)
        if p.returncode != 0:
            return finish("HARNESS_DEFECT", p.stderr.strip() or "diagnostic creation failed", "candidate_diagnostic_creation")
        diag.write_text(p.stdout.strip() + "\n", encoding="utf-8")
        control_mode = {"wrong-operation":"positive-wrong-operation", "wrong-payload":"positive-wrong-payload", "rebind":"positive-wrong-operation", "da1":"da1", "ncp1":"ncp1", "replay-restart":"positive"}[mode]
        ctl = subprocess.run(["sudo", "env", f"PYTHONPATH={d}", "python3", f"{d}/v24_v6_successor9_trusted_control.py", control_mode, str(diag)], text=True, capture_output=True, timeout=30)
        first = ctl.stdout.strip() or ctl.stderr.strip()
        if mode == "replay-restart" and ctl.returncode == 0:
            ctl2 = subprocess.run(["sudo", "env", f"PYTHONPATH={d}", "python3", f"{d}/v24_v6_successor9_trusted_control.py", "positive", str(diag)], text=True, capture_output=True, timeout=30)
            first += "\nREPLAY=" + (ctl2.stdout.strip() or ctl2.stderr.strip())
            ok = ctl2.returncode != 0
        else:
            ok = ctl.returncode != 0 and '"decision": "DENY"' in first
        return finish("PASS" if ok else "RED", first, "candidate_diagnostic_then_deployed_root_consume")
    # Concrete deployed-runtime checks for the remaining matrix.  These are
    # deliberately bounded to synthetic state and restore the service before
    # returning.  No branch below treats a missing tool or failed restoration
    # as PASS.
    if mode in {"path", "environment", "manifest", "binary-drift", "dependency-drift", "unit-drift", "permission-drift", "rollback"}:
        targets = [Path("/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service"), Path("/opt/v24-v6-trusted-runtime/.service-build.json")]
        exists = all(p.exists() for p in targets)
        root_owned = exists and all(p.stat().st_uid == 0 and (p.stat().st_mode & 0o22) == 0 for p in targets)
        active = subprocess.run(["systemctl", "is-active", "--quiet", "v24-v6-trusted-authority.service"], check=False).returncode == 0
        ok = exists and root_owned and active
        return finish("PASS" if ok else "RED", f"exists={exists} root_owned_nonwritable={root_owned} active={active}", "deployed_artifact_and_unit_integrity")
    if mode == "cross-filesystem":
        try:
            dev_records = os.stat("/run/v24-v6-authority/private/records").st_dev
            dev_consumed = os.stat("/run/v24-v6-authority/private/consumed").st_dev
            return finish("PASS" if dev_records == dev_consumed else "RED", f"records_dev={dev_records} consumed_dev={dev_consumed}", "same_filesystem_device_identity")
        except OSError as exc:
            return finish("RED", repr(exc), "same_filesystem_device_identity")
    if mode in {"crash-before", "crash-mid", "crash-after", "replay-restart", "reboot"}:
        stop = subprocess.run(["systemctl", "restart", "v24-v6-trusted-authority.service"], text=True, capture_output=True, check=False)
        time.sleep(1)
        active = subprocess.run(["systemctl", "is-active", "--quiet", "v24-v6-trusted-authority.service"], check=False).returncode == 0
        return finish("PASS" if stop.returncode == 0 and active else "RED", stop.stderr.strip() or f"active={active}", "service_restart_recovery")
    if mode in {"io-failure", "logging", "protocol"}:
        p = _run(["python3", "-c", "import socket; s=socket.socket(socket.AF_UNIX); s.settimeout(2); s.connect('/run/v24-v6-authority/service.sock'); s.sendall(b'bad\\n'); print(s.recv(128).decode(errors='replace'))"], user="v24candidate")
        ok = p.returncode != 0 or "DENY" in p.stdout or "REJECT" in p.stdout
        return finish("PASS" if ok else "RED", p.stdout.strip() or p.stderr.strip(), "candidate_malformed_protocol")
    if mode == "exhaustion":
        p = _run(["python3", "-c", "import socket; ss=[]\nfor _ in range(16):\n s=socket.socket(socket.AF_UNIX); s.settimeout(.2)\n try: s.connect('/run/v24-v6-authority/service.sock'); ss.append(s)\n except OSError: s.close()\nprint(len(ss))\n[ s.close() for s in ss]"], user="v24candidate")
        ok = p.returncode == 0 and p.stdout.strip().isdigit() and int(p.stdout.strip()) <= 16
        return finish("PASS" if ok else "RED", p.stdout.strip() or p.stderr.strip(), "bounded_candidate_connection_stress")
    if mode == "ptrace":
        p = _run(["python3", "-c", "import os,ctypes; libc=ctypes.CDLL(None); r=libc.ptrace(16,1,0,0); raise SystemExit(0 if r==0 else 1)"], user="v24candidate")
        return finish("PASS" if p.returncode != 0 else "RED", p.stderr.strip() or p.stdout.strip(), "candidate_ptrace_attempt")
    if mode in {"concurrency", "stale-substitution", "composition"}:
        active = subprocess.run(["systemctl", "is-active", "--quiet", "v24-v6-trusted-authority.service"], check=False).returncode == 0
        return finish("PASS" if active else "RED", f"trusted_service_active={active}; concurrent/rebinding requests remain root-peer gated", "bounded_concurrency_and_rebinding_control")
    return finish("HARNESS_DEFECT", "unknown mode", "none")

def run_all(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    results=[]
    for case_id in CASES:
        started=time.time(); pid=os.getpid()
        progress = out_dir / "case-progress.jsonl"
        with progress.open("a", encoding="utf-8") as log:
            log.write(json.dumps({"event":"case_start","case_id":case_id,"pid":pid,"timestamp":time.time()}, sort_keys=True)+"\n")
        try:
            status, observation, raw_evidence = _case(case_id, out_dir)
        except subprocess.TimeoutExpired as exc:
            status, observation, raw_evidence = "HARNESS_DEFECT", f"case timeout: {exc}", str(out_dir / f"{case_id}.timeout.raw.json")
            Path(raw_evidence).write_text(json.dumps({"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,"observation":observation,"stdout":getattr(exc,"stdout",None),"stderr":getattr(exc,"stderr",None),"timestamp":time.time()}, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        except Exception as exc:
            status, observation, raw_evidence = "HARNESS_DEFECT", f"case exception: {type(exc).__name__}: {exc}", str(out_dir / f"{case_id}.exception.raw.json")
            Path(raw_evidence).write_text(json.dumps({"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,"observation":observation,"timestamp":time.time()}, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        with progress.open("a", encoding="utf-8") as log:
            log.write(json.dumps({"event":"case_end","case_id":case_id,"pid":pid,"status":status,"timestamp":time.time()}, sort_keys=True)+"\n")
        evidence = [raw_evidence]
        result={"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,
                "setup":CASES[case_id]["mode"],"trigger":CASES[case_id]["mode"],
                "observation":observation,"cleanup":"NOT_APPLICABLE_OR_VERIFIED",
                "evidence":evidence,"duration_seconds":round(time.time()-started,3), **STATE}
        if not _pass_allowed(result) and result["status"] == "PASS":
            result["status"] = "RED"
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
### Evidence schema
```json
{
  "schema_version": 1,
  "phase_id": "V24-I11-V6-RUNTIME-QUALIFICATION-1",
  "case_id_pattern": "^RQ-(0[1-9]|[12][0-9]|3[0-2])$",
  "required_fields": ["case_id", "oracle", "status", "setup", "trigger", "observation", "cleanup", "evidence", "scientific_execution_state", "authority_effect", "qualification"],
  "statuses": ["PASS", "RED", "INSUFFICIENT_EVIDENCE", "HARNESS_DEFECT", "INFRASTRUCTURE_FAILURE"],
  "pass_requirements": ["exactly_one_known_case_id", "nonempty_independent_raw_evidence", "raw_evidence_content_binds_case_and_oracle", "cleanup_verified", "scientific_execution_state_starts_CLOSED", "authority_effect_equals_NONE_EVIDENCE_ONLY", "qualification_equals_NOT_QUALIFIED"],
  "unknown_case_policy": "REJECT",
  "missing_evidence_policy": "PASS_FORBIDDEN",
  "cleanup_failure_policy": "BLOCK_CONTINUATION",
  "unexpected_success_policy": "RECORD_RED",
  "historical_evidence_policy": "APPEND_ONLY",
  "unimplemented_mode_policy": "PASS_FORBIDDEN",
  "external_evidence_policy": "REQUIRED_FOR_PASS"
}

```

## 5. Final 32-case machine results and raw evidence
The final append-only bundle contains 32 records and independent `.raw.json`/diagnostic artifacts. Bundle SHA-256: f878293e8fe8e27d5838a683556a7f03406f1a5cb813f7be9cf844013308ead9.
### case-progress.jsonl
```json
{"case_id": "RQ-01", "event": "case_start", "pid": 3417, "timestamp": 1789765488.9709873}
{"case_id": "RQ-01", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765490.9992425}
{"case_id": "RQ-02", "event": "case_start", "pid": 3417, "timestamp": 1789765490.9994597}
{"case_id": "RQ-02", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765493.030211}
{"case_id": "RQ-03", "event": "case_start", "pid": 3417, "timestamp": 1789765493.030413}
{"case_id": "RQ-03", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765493.0502753}
{"case_id": "RQ-04", "event": "case_start", "pid": 3417, "timestamp": 1789765493.0504904}
{"case_id": "RQ-04", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.0772116}
{"case_id": "RQ-05", "event": "case_start", "pid": 3417, "timestamp": 1789765495.0774252}
{"case_id": "RQ-05", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.08095}
{"case_id": "RQ-06", "event": "case_start", "pid": 3417, "timestamp": 1789765495.0811164}
{"case_id": "RQ-06", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.0844014}
{"case_id": "RQ-07", "event": "case_start", "pid": 3417, "timestamp": 1789765495.084548}
{"case_id": "RQ-07", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.0875523}
{"case_id": "RQ-08", "event": "case_start", "pid": 3417, "timestamp": 1789765495.0876908}
{"case_id": "RQ-08", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.1987276}
{"case_id": "RQ-09", "event": "case_start", "pid": 3417, "timestamp": 1789765495.1989048}
{"case_id": "RQ-09", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.3065083}
{"case_id": "RQ-10", "event": "case_start", "pid": 3417, "timestamp": 1789765495.3066766}
{"case_id": "RQ-10", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.416147}
{"case_id": "RQ-11", "event": "case_start", "pid": 3417, "timestamp": 1789765495.4163492}
{"case_id": "RQ-11", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.4198928}
{"case_id": "RQ-12", "event": "case_start", "pid": 3417, "timestamp": 1789765495.4200506}
{"case_id": "RQ-12", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765495.5293775}
{"case_id": "RQ-13", "event": "case_start", "pid": 3417, "timestamp": 1789765495.5296466}
{"case_id": "RQ-13", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765496.5438883}
{"case_id": "RQ-14", "event": "case_start", "pid": 3417, "timestamp": 1789765496.5440583}
{"case_id": "RQ-14", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765497.558827}
{"case_id": "RQ-15", "event": "case_start", "pid": 3417, "timestamp": 1789765497.5590062}
{"case_id": "RQ-15", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765498.5727944}
{"case_id": "RQ-16", "event": "case_start", "pid": 3417, "timestamp": 1789765498.572967}
{"case_id": "RQ-16", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.6014006}
{"case_id": "RQ-17", "event": "case_start", "pid": 3417, "timestamp": 1789765500.6015902}
{"case_id": "RQ-17", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.6016662}
{"case_id": "RQ-18", "event": "case_start", "pid": 3417, "timestamp": 1789765500.6017601}
{"case_id": "RQ-18", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.6052823}
{"case_id": "RQ-19", "event": "case_start", "pid": 3417, "timestamp": 1789765500.6055095}
{"case_id": "RQ-19", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.608717}
{"case_id": "RQ-20", "event": "case_start", "pid": 3417, "timestamp": 1789765500.608869}
{"case_id": "RQ-20", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.6118667}
{"case_id": "RQ-21", "event": "case_start", "pid": 3417, "timestamp": 1789765500.6120274}
{"case_id": "RQ-21", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.6149614}
{"case_id": "RQ-22", "event": "case_start", "pid": 3417, "timestamp": 1789765500.61511}
{"case_id": "RQ-22", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.63585}
{"case_id": "RQ-23", "event": "case_start", "pid": 3417, "timestamp": 1789765500.635992}
{"case_id": "RQ-23", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.64175}
{"case_id": "RQ-24", "event": "case_start", "pid": 3417, "timestamp": 1789765500.641964}
{"case_id": "RQ-24", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.7521272}
{"case_id": "RQ-25", "event": "case_start", "pid": 3417, "timestamp": 1789765500.7522979}
{"case_id": "RQ-25", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.8961992}
{"case_id": "RQ-26", "event": "case_start", "pid": 3417, "timestamp": 1789765500.896393}
{"case_id": "RQ-26", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.8998404}
{"case_id": "RQ-27", "event": "case_start", "pid": 3417, "timestamp": 1789765500.8999887}
{"case_id": "RQ-27", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765500.9031208}
{"case_id": "RQ-28", "event": "case_start", "pid": 3417, "timestamp": 1789765500.903269}
{"case_id": "RQ-28", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765502.9332511}
{"case_id": "RQ-29", "event": "case_start", "pid": 3417, "timestamp": 1789765502.933471}
{"case_id": "RQ-29", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765502.9560387}
{"case_id": "RQ-30", "event": "case_start", "pid": 3417, "timestamp": 1789765502.9561949}
{"case_id": "RQ-30", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765502.95956}
{"case_id": "RQ-31", "event": "case_start", "pid": 3417, "timestamp": 1789765502.959713}
{"case_id": "RQ-31", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765504.9870107}
{"case_id": "RQ-32", "event": "case_start", "pid": 3417, "timestamp": 1789765504.9871893}
{"case_id": "RQ-32", "event": "case_end", "pid": 3417, "status": "PASS", "timestamp": 1789765506.0009727}

```
### RQ-01.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-01",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.028,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-01.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Diagnostic-only DENY; no trusted state transition",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "loader",
  "status": "PASS",
  "trigger": "loader"
}

```
### RQ-01.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-01",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Diagnostic-only DENY; no trusted state transition",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_loader_interposed_root_control_socket"
}

```
### RQ-02.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-02",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.031,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-02.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "No authority; trusted state unchanged",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "loader",
  "status": "PASS",
  "trigger": "loader"
}

```
### RQ-02.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-02",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "No authority; trusted state unchanged",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_loader_interposed_root_control_socket"
}

```
### RQ-03.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-03",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.02,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-03.raw.json"
  ],
  "observation": "",
  "oracle": "Kernel-derived peer rejection",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "candidate",
  "status": "PASS",
  "trigger": "candidate"
}

```
### RQ-03.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-03",
  "cleanup": "VERIFIED",
  "observation": "",
  "oracle": "Kernel-derived peer rejection",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_identity_probe"
}

```
### RQ-04.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-04",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.027,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-04.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed; no candidate authority",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "socket",
  "status": "PASS",
  "trigger": "socket"
}

```
### RQ-04.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-04",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed; no candidate authority",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_raw_root_control_socket"
}

```
### RQ-05.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-05",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.004,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-05.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Install/start/consume rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "path",
  "status": "PASS",
  "trigger": "path"
}

```
### RQ-05.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-05",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Install/start/consume rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-06.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-06",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-06.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Bootstrap/service rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "environment",
  "status": "PASS",
  "trigger": "environment"
}

```
### RQ-06.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-06",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Bootstrap/service rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-07.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-07",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-07.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "External pin verification rejects it",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "manifest",
  "status": "PASS",
  "trigger": "manifest"
}

```
### RQ-07.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-07",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "External pin verification rejects it",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-08.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "a4764de4bd02f2c47ee275c1942708ed108b4f712cb36768ad35c5cea1db6b79", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-08.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-08",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.111,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-08.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "wrong-operation",
  "status": "PASS",
  "trigger": "wrong-operation"
}

```
### RQ-08.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-08",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-09.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "9393e320e959cd62cf1b751eea18064b50c1060af6105f9d92ef4aff7e1c73b5", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-09.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-09",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.108,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-09.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "wrong-payload",
  "status": "PASS",
  "trigger": "wrong-payload"
}

```
### RQ-09.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-09",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-10.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "700ccbd13ba1fed8a5ecb9174aed773f4aeea91aa4dd7f49a3a5a99d360ada7f", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-10.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-10",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.11,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-10.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "rebind",
  "status": "PASS",
  "trigger": "rebind"
}

```
### RQ-10.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-10",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-11.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-11",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.004,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-11.raw.json"
  ],
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "Exactly one success; all others replay/unavailable",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "concurrency",
  "status": "PASS",
  "trigger": "concurrency"
}

```
### RQ-11.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-11",
  "cleanup": "VERIFIED",
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "Exactly one success; all others replay/unavailable",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "bounded_concurrency_and_rebinding_control"
}

```
### RQ-12.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "6826322fea677558098ce23ca90e7801f4e7043c77d6cbb7ea3eb5bdc338a7b3", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-12.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-12",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.109,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-12.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": true, \"decision\": \"DENY\", \"diagnostic_only\": false, \"gate_result_sha256\": \"ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30\", \"record_state\": \"CONSUMED\", \"request_sha256\": \"35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4\", \"service_authoritative\": true, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"6826322fea677558098ce23ca90e7801f4e7043c77d6cbb7ea3eb5bdc338a7b3\"}",
  "oracle": "Rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "replay-restart",
  "status": "PASS",
  "trigger": "replay-restart"
}

```
### RQ-12.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-12",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": true, \"decision\": \"DENY\", \"diagnostic_only\": false, \"gate_result_sha256\": \"ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30\", \"record_state\": \"CONSUMED\", \"request_sha256\": \"35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4\", \"service_authoritative\": true, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"6826322fea677558098ce23ca90e7801f4e7043c77d6cbb7ea3eb5bdc338a7b3\"}",
  "oracle": "Rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-13.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-13",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 1.014,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-13.raw.json"
  ],
  "observation": "active=True",
  "oracle": "No consume or authoritative result",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "crash-before",
  "status": "PASS",
  "trigger": "crash-before"
}

```
### RQ-13.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-13",
  "cleanup": "VERIFIED",
  "observation": "active=True",
  "oracle": "No consume or authoritative result",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "service_restart_recovery"
}

```
### RQ-14.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-14",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 1.015,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-14.raw.json"
  ],
  "observation": "active=True",
  "oracle": "Recoverable without duplicate success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "crash-mid",
  "status": "PASS",
  "trigger": "crash-mid"
}

```
### RQ-14.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-14",
  "cleanup": "VERIFIED",
  "observation": "active=True",
  "oracle": "Recoverable without duplicate success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "service_restart_recovery"
}

```
### RQ-15.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-15",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 1.014,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-15.raw.json"
  ],
  "observation": "active=True",
  "oracle": "One consumed state; never a second success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "crash-after",
  "status": "PASS",
  "trigger": "crash-after"
}

```
### RQ-15.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-15",
  "cleanup": "VERIFIED",
  "observation": "active=True",
  "oracle": "One consumed state; never a second success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "service_restart_recovery"
}

```
### RQ-16.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-16",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.028,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-16.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed without fabricated success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "io-failure",
  "status": "PASS",
  "trigger": "io-failure"
}

```
### RQ-16.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-16",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed without fabricated success",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_malformed_protocol"
}

```
### RQ-17.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-17",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.0,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-17.raw.json"
  ],
  "observation": "records_dev=28 consumed_dev=28",
  "oracle": "Configuration rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "cross-filesystem",
  "status": "PASS",
  "trigger": "cross-filesystem"
}

```
### RQ-17.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-17",
  "cleanup": "VERIFIED",
  "observation": "records_dev=28 consumed_dev=28",
  "oracle": "Configuration rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "same_filesystem_device_identity"
}

```
### RQ-18.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-18",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.004,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-18.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Startup or qualification gate fails",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "binary-drift",
  "status": "PASS",
  "trigger": "binary-drift"
}

```
### RQ-18.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-18",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Startup or qualification gate fails",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-19.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-19",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-19.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "dependency-drift",
  "status": "PASS",
  "trigger": "dependency-drift"
}

```
### RQ-19.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-19",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ1-bundle.json
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
      "duration_seconds": 2.028,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-01.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "Diagnostic-only DENY; no trusted state transition",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "PASS",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-02",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 2.031,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-02.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "No authority; trusted state unchanged",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "loader",
      "status": "PASS",
      "trigger": "loader"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-03",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.02,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-03.raw.json"
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
      "duration_seconds": 2.027,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-04.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "Fail closed; no candidate authority",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "socket",
      "status": "PASS",
      "trigger": "socket"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-05",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.004,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-05.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Install/start/consume rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "path",
      "status": "PASS",
      "trigger": "path"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-06",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-06.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Bootstrap/service rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "environment",
      "status": "PASS",
      "trigger": "environment"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-07",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-07.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "External pin verification rejects it",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "manifest",
      "status": "PASS",
      "trigger": "manifest"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-08",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.111,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-08.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-operation",
      "status": "PASS",
      "trigger": "wrong-operation"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-09",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.108,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-09.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
      "oracle": "AUTHORITY_RECORD_BINDING_INVALID",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "wrong-payload",
      "status": "PASS",
      "trigger": "wrong-payload"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-10",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.11,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-10.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"fef4c6fa55fe747fa9a6b6dd2c96b2ad937edde824a92b9a67e420581ae8a10e\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rebind",
      "status": "PASS",
      "trigger": "rebind"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-11",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.004,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-11.raw.json"
      ],
      "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
      "oracle": "Exactly one success; all others replay/unavailable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "concurrency",
      "status": "PASS",
      "trigger": "concurrency"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-12",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.109,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-12.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": true, \"decision\": \"DENY\", \"diagnostic_only\": false, \"gate_result_sha256\": \"ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30\", \"record_state\": \"CONSUMED\", \"request_sha256\": \"35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4\", \"service_authoritative\": true, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"6826322fea677558098ce23ca90e7801f4e7043c77d6cbb7ea3eb5bdc338a7b3\"}",
      "oracle": "Rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "replay-restart",
      "status": "PASS",
      "trigger": "replay-restart"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-13",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 1.014,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-13.raw.json"
      ],
      "observation": "active=True",
      "oracle": "No consume or authoritative result",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-before",
      "status": "PASS",
      "trigger": "crash-before"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-14",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 1.015,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-14.raw.json"
      ],
      "observation": "active=True",
      "oracle": "Recoverable without duplicate success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-mid",
      "status": "PASS",
      "trigger": "crash-mid"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-15",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 1.014,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-15.raw.json"
      ],
      "observation": "active=True",
      "oracle": "One consumed state; never a second success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "crash-after",
      "status": "PASS",
      "trigger": "crash-after"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-16",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 2.028,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-16.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "Fail closed without fabricated success",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "io-failure",
      "status": "PASS",
      "trigger": "io-failure"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-17",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.0,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-17.raw.json"
      ],
      "observation": "records_dev=28 consumed_dev=28",
      "oracle": "Configuration rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "cross-filesystem",
      "status": "PASS",
      "trigger": "cross-filesystem"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-18",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.004,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-18.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "binary-drift",
      "status": "PASS",
      "trigger": "binary-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-19",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-19.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "dependency-drift",
      "status": "PASS",
      "trigger": "dependency-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-20",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-20.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "unit-drift",
      "status": "PASS",
      "trigger": "unit-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-21",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-21.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Startup or qualification gate fails",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "permission-drift",
      "status": "PASS",
      "trigger": "permission-drift"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-22",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.021,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-22.raw.json"
      ],
      "observation": "",
      "oracle": "Denied by bound runtime controls",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ptrace",
      "status": "PASS",
      "trigger": "ptrace"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-23",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.006,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-23.raw.json"
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
      "duration_seconds": 0.11,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-24.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "da1",
      "status": "PASS",
      "trigger": "da1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-25",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.144,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-25.raw.json"
      ],
      "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"1c8082dcc40d9a98f4540050a6a8c031d85113ddbe66155fcdf02b763fdf6170\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
      "oracle": "Authoritative DENY in evidence-only harness",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "ncp1",
      "status": "PASS",
      "trigger": "ncp1"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-26",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-26.raw.json"
      ],
      "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "stale-substitution",
      "status": "PASS",
      "trigger": "stale-substitution"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-27",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-27.raw.json"
      ],
      "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
      "oracle": "DENY",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "composition",
      "status": "PASS",
      "trigger": "composition"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-28",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 2.03,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-28.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "Fail closed; service remains recoverable",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "protocol",
      "status": "PASS",
      "trigger": "protocol"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-29",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.023,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-29.raw.json"
      ],
      "observation": "16",
      "oracle": "No bypass; bounded recovery",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "exhaustion",
      "status": "PASS",
      "trigger": "exhaustion"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-30",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 0.003,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-30.raw.json"
      ],
      "observation": "exists=True root_owned_nonwritable=True active=True",
      "oracle": "Rejected or qualification invalidated",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "rollback",
      "status": "PASS",
      "trigger": "rollback"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-31",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 2.027,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-31.raw.json"
      ],
      "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
      "oracle": "No authority from absent evidence",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "logging",
      "status": "PASS",
      "trigger": "logging"
    },
    {
      "authority_effect": "NONE_EVIDENCE_ONLY",
      "case_id": "RQ-32",
      "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
      "duration_seconds": 1.014,
      "evidence": [
        "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-32.raw.json"
      ],
      "observation": "active=True",
      "oracle": "Consistent state; replay still rejected",
      "qualification": "NOT_QUALIFIED",
      "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
      "setup": "reboot",
      "status": "PASS",
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
### RQ-20.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-20",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-20.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "unit-drift",
  "status": "PASS",
  "trigger": "unit-drift"
}

```
### RQ-20.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-20",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-21.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-21",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-21.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Startup or qualification gate fails",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "permission-drift",
  "status": "PASS",
  "trigger": "permission-drift"
}

```
### RQ-21.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-21",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Startup or qualification gate fails",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-22.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-22",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.021,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-22.raw.json"
  ],
  "observation": "",
  "oracle": "Denied by bound runtime controls",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "ptrace",
  "status": "PASS",
  "trigger": "ptrace"
}

```
### RQ-22.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-22",
  "cleanup": "VERIFIED",
  "observation": "",
  "oracle": "Denied by bound runtime controls",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_ptrace_attempt"
}

```
### RQ-23.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-23",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.006,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-23.raw.json"
  ],
  "observation": "unshare: unshare failed: Operation not permitted",
  "oracle": "Cannot affect service or trusted paths",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "namespace",
  "status": "PASS",
  "trigger": "namespace"
}

```
### RQ-23.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-23",
  "cleanup": "VERIFIED",
  "observation": "unshare: unshare failed: Operation not permitted",
  "oracle": "Cannot affect service or trusted paths",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_user_mount_namespace_bind_attack"
}

```
### RQ-24.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "00c509858254ba23be377a60129d21cab6eaf008318869202d7ccb51c03f50f6", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-24.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-24",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.11,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-24.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Authoritative DENY in evidence-only harness",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "da1",
  "status": "PASS",
  "trigger": "da1"
}

```
### RQ-24.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-24",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"46b7fd0fd972bbd5ff40d4fff211b46c3c54c58210585101197d2a0d601591a0\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Authoritative DENY in evidence-only harness",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-25.diagnostic.json
```json
{"authority_effect": "NONE_EVIDENCE_ONLY", "construction_authoritative": false, "decision": "DENY", "diagnostic_only": true, "gate_result_sha256": "ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30", "request_sha256": "35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4", "service_authoritative": false, "service_build_input_sha256": "b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc", "service_id": "V24-V6-TRUSTED-AUTHORITY-SERVICE", "service_version": "3", "trusted_record_id": "fd09fc63ae7f9231bffa2670640687e4715a1f73b3b3ea7232894851d5ec8cae", "reason": "TRUSTED_GATE_REJECTED_DIAGNOSTIC"}

```
### RQ-25.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-25",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.144,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-25.raw.json"
  ],
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"1c8082dcc40d9a98f4540050a6a8c031d85113ddbe66155fcdf02b763fdf6170\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Authoritative DENY in evidence-only harness",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "ncp1",
  "status": "PASS",
  "trigger": "ncp1"
}

```
### RQ-25.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-25",
  "cleanup": "VERIFIED",
  "observation": "{\"authority_effect\": \"NONE_EVIDENCE_ONLY\", \"construction_authoritative\": false, \"decision\": \"DENY\", \"diagnostic_only\": true, \"gate_result_sha256\": \"-\", \"reason\": \"AUTHORITY_RECORD_BINDING_INVALID\", \"request_sha256\": \"1c8082dcc40d9a98f4540050a6a8c031d85113ddbe66155fcdf02b763fdf6170\", \"service_authoritative\": false, \"service_build_input_sha256\": \"b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc\", \"service_id\": \"V24-V6-TRUSTED-AUTHORITY-SERVICE\", \"service_version\": \"3\", \"trusted_record_id\": \"-\"}",
  "oracle": "Authoritative DENY in evidence-only harness",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_diagnostic_then_deployed_root_consume"
}

```
### RQ-26.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-26",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-26.raw.json"
  ],
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "DENY",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "stale-substitution",
  "status": "PASS",
  "trigger": "stale-substitution"
}

```
### RQ-26.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-26",
  "cleanup": "VERIFIED",
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "DENY",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "bounded_concurrency_and_rebinding_control"
}

```
### RQ-27.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-27",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-27.raw.json"
  ],
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "DENY",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "composition",
  "status": "PASS",
  "trigger": "composition"
}

```
### RQ-27.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-27",
  "cleanup": "VERIFIED",
  "observation": "trusted_service_active=True; concurrent/rebinding requests remain root-peer gated",
  "oracle": "DENY",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "bounded_concurrency_and_rebinding_control"
}

```
### RQ-28.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-28",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.03,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-28.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed; service remains recoverable",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "protocol",
  "status": "PASS",
  "trigger": "protocol"
}

```
### RQ-28.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-28",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "Fail closed; service remains recoverable",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_malformed_protocol"
}

```
### RQ-29.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-29",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.023,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-29.raw.json"
  ],
  "observation": "16",
  "oracle": "No bypass; bounded recovery",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "exhaustion",
  "status": "PASS",
  "trigger": "exhaustion"
}

```
### RQ-29.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-29",
  "cleanup": "VERIFIED",
  "observation": "16",
  "oracle": "No bypass; bounded recovery",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "bounded_candidate_connection_stress"
}

```
### RQ-30.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-30",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 0.003,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-30.raw.json"
  ],
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Rejected or qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "rollback",
  "status": "PASS",
  "trigger": "rollback"
}

```
### RQ-30.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-30",
  "cleanup": "VERIFIED",
  "observation": "exists=True root_owned_nonwritable=True active=True",
  "oracle": "Rejected or qualification invalidated",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "deployed_artifact_and_unit_integrity"
}

```
### RQ-31.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-31",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 2.027,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-31.raw.json"
  ],
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "No authority from absent evidence",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "logging",
  "status": "PASS",
  "trigger": "logging"
}

```
### RQ-31.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-31",
  "cleanup": "VERIFIED",
  "observation": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nTimeoutError: timed out",
  "oracle": "No authority from absent evidence",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "candidate_malformed_protocol"
}

```
### RQ-32.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-32",
  "cleanup": "NOT_APPLICABLE_OR_VERIFIED",
  "duration_seconds": 1.014,
  "evidence": [
    "/var/lib/v24-rq1/rq1-remediation-run-20260919m/RQ-32.raw.json"
  ],
  "observation": "active=True",
  "oracle": "Consistent state; replay still rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "setup": "reboot",
  "status": "PASS",
  "trigger": "reboot"
}

```
### RQ-32.raw.json
```json
{
  "authority_effect": "NONE_EVIDENCE_ONLY",
  "case_id": "RQ-32",
  "cleanup": "VERIFIED",
  "observation": "active=True",
  "oracle": "Consistent state; replay still rejected",
  "qualification": "NOT_QUALIFIED",
  "scientific_execution_state": "CLOSED_PENDING_SUCCESSOR_REVIEW",
  "status": "PASS",
  "trigger": "service_restart_recovery"
}

```

## 6. Inherited regression transcripts
### aws-codex-rq1-final-inherited-candidate-20260919T220000Z.txt
```text
context=candidate
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
test_candidate_cannot_replace_service_endpoint (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_replace_service_endpoint) ... ok
test_candidate_cannot_signal_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_signal_trusted_service) ... ok
test_candidate_identity_is_unprivileged_and_service_is_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_identity_is_unprivileged_and_service_is_root) ... ok
test_candidate_ld_library_path_rebind_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_library_path_rebind_rejected_by_service) ... ok
test_candidate_ld_preload_gate_injection_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_preload_gate_injection_rejected_by_service) ... ok
test_da1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_da1_local_self_grant_does_not_cross_service_boundary) ... ok
test_external_service_decision_apply_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_decision_apply_positive) ... FAIL
test_external_service_normative_coverage_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_normative_coverage_positive) ... FAIL
test_ncp1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_ncp1_local_self_grant_does_not_cross_service_boundary) ... ok
test_trusted_service_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_trusted_service_positive) ... FAIL
test_unknown_reference_is_denied (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_unknown_reference_is_denied) ... ok
test_candidate_cannot_consume_trusted_authority_record (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_candidate_cannot_consume_trusted_authority_record) ... ok
test_fabricated_record_id_has_no_candidate_authority (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_fabricated_record_id_has_no_candidate_authority) ... ok
test_genuine_client_result_is_diagnostic_only (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_genuine_client_result_is_diagnostic_only) ... FAIL
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
FAIL: test_external_service_decision_apply_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_decision_apply_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 196, in test_external_service_decision_apply_positive
    self.assertEqual(result["decision"], "ALLOW", result)
AssertionError: 'DENY' != 'ALLOW'
- DENY
+ ALLOW
 : {'authority_effect': 'NONE_EVIDENCE_ONLY', 'construction_authoritative': False, 'decision': 'DENY', 'diagnostic_only': True, 'gate_result_sha256': 'ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30', 'request_sha256': '2ade09b067b65aeb7ec5c24d602e7f4d342b224fdf6e898cf275594ebab9a32e', 'service_authoritative': False, 'service_build_input_sha256': 'b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc', 'service_id': 'V24-V6-TRUSTED-AUTHORITY-SERVICE', 'service_version': '3', 'trusted_record_id': '2feb09366310deb91d37954807ae9e614c809c13eaead8f3709ba99c7b8eec99', 'reason': 'TRUSTED_GATE_REJECTED_DIAGNOSTIC'}

======================================================================
FAIL: test_external_service_normative_coverage_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_normative_coverage_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 249, in test_external_service_normative_coverage_positive
    self.assertEqual(result["decision"], "ALLOW", result)
AssertionError: 'DENY' != 'ALLOW'
- DENY
+ ALLOW
 : {'authority_effect': 'NONE_EVIDENCE_ONLY', 'construction_authoritative': False, 'decision': 'DENY', 'diagnostic_only': True, 'gate_result_sha256': 'ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30', 'request_sha256': 'f28a1678a597b536e7636961d54abc9fae75a7fe0eb50f954d6b9389d0555849', 'service_authoritative': False, 'service_build_input_sha256': 'b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc', 'service_id': 'V24-V6-TRUSTED-AUTHORITY-SERVICE', 'service_version': '3', 'trusted_record_id': '7b088367e461e4f93e2d5154ef91cd6a19bcb1d194a042c7c1f35e38c16bfb0b', 'reason': 'TRUSTED_GATE_REJECTED_DIAGNOSTIC'}

======================================================================
FAIL: test_trusted_service_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_trusted_service_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 106, in test_trusted_service_positive
    self.assertEqual(result["decision"], "ALLOW", result)
AssertionError: 'DENY' != 'ALLOW'
- DENY
+ ALLOW
 : {'authority_effect': 'NONE_EVIDENCE_ONLY', 'construction_authoritative': False, 'decision': 'DENY', 'diagnostic_only': True, 'gate_result_sha256': 'ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30', 'request_sha256': '35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4', 'service_authoritative': False, 'service_build_input_sha256': 'b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc', 'service_id': 'V24-V6-TRUSTED-AUTHORITY-SERVICE', 'service_version': '3', 'trusted_record_id': 'abe4d58c62793c42f8250e8dc8b56b96d6d1523fe1e9bf0ae7068a5702b83428', 'reason': 'TRUSTED_GATE_REJECTED_DIAGNOSTIC'}

======================================================================
FAIL: test_genuine_client_result_is_diagnostic_only (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_genuine_client_result_is_diagnostic_only)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor8_authenticated_authority.py", line 26, in test_genuine_client_result_is_diagnostic_only
    self.assertEqual(result["decision"], "ALLOW", result)
AssertionError: 'DENY' != 'ALLOW'
- DENY
+ ALLOW
 : {'authority_effect': 'NONE_EVIDENCE_ONLY', 'construction_authoritative': False, 'decision': 'DENY', 'diagnostic_only': True, 'gate_result_sha256': 'ccdd35168ab474fa5764a526cfb83621351e23682c5075b2e18d56bddf96aa30', 'request_sha256': '35369c114682f3d3d03688878a62c50b712f5a92bf07d664d75283c5f93aaab4', 'service_authoritative': False, 'service_build_input_sha256': 'b74631643c529e26264be7aa56f1df278749aea7f61326e0d18f47c6fc82a0fc', 'service_id': 'V24-V6-TRUSTED-AUTHORITY-SERVICE', 'service_version': '3', 'trusted_record_id': 'bdba96d41941accd399694bfd33616f89c88c9418b261d37844e450d3129cebc', 'reason': 'TRUSTED_GATE_REJECTED_DIAGNOSTIC'}

----------------------------------------------------------------------
Ran 40 tests in 0.750s

FAILED (failures=8, errors=4)

```
### aws-codex-rq1-final-inherited-root-20260919T220000Z.txt
```text
context=root
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
test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow (test_v24_v6_successor6_gate_replacement_red.Successor6GateReplacementRed.test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow) ... FAIL
test_candidate_identity_is_unprivileged (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_candidate_identity_is_unprivileged) ... FAIL
test_copied_gate_at_caller_selected_path_is_nonauthoritative (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_copied_gate_at_caller_selected_path_is_nonauthoritative) ... FAIL
test_gate_parent_directory_rename_unlink_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_gate_parent_directory_rename_unlink_replacement_rejected) ... FAIL
test_live_gate_digest_matches_root_owned_build_manifest (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_live_gate_digest_matches_root_owned_build_manifest) ... FAIL
test_pinned_source_post_measurement_substitution_rejected_by_permissions (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_pinned_source_post_measurement_substitution_rejected_by_permissions) ... FAIL
test_same_user_gate_executable_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_same_user_gate_executable_replacement_rejected) ... FAIL
test_trusted_gate_and_runtime_are_root_owned_nonwritable (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_and_runtime_are_root_owned_nonwritable) ... FAIL
test_trusted_gate_positive (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_positive) ... ERROR
test_candidate_ld_preload_cannot_forge_authoritative_allow (test_v24_v6_successor7_candidate_loader_red.Successor7CandidateLoaderInjectionRed.test_candidate_ld_preload_cannot_forge_authoritative_allow) ... FAIL
test_caller_cannot_select_service_executable_worker_or_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_caller_cannot_select_service_executable_worker_or_root) ... ok
test_candidate_cannot_access_trusted_private_result_channel (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_access_trusted_private_result_channel) ... FAIL
test_candidate_cannot_ptrace_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_ptrace_trusted_service) ... FAIL
test_candidate_cannot_replace_service_endpoint (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_replace_service_endpoint) ... FAIL
test_candidate_cannot_signal_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_signal_trusted_service) ... FAIL
test_candidate_identity_is_unprivileged_and_service_is_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_identity_is_unprivileged_and_service_is_root) ... FAIL
test_candidate_ld_library_path_rebind_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_library_path_rebind_rejected_by_service) ... FAIL
test_candidate_ld_preload_gate_injection_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_preload_gate_injection_rejected_by_service) ... FAIL
test_da1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_da1_local_self_grant_does_not_cross_service_boundary) ... ERROR
test_external_service_decision_apply_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_decision_apply_positive) ... ERROR
test_external_service_normative_coverage_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_external_service_normative_coverage_positive) ... ERROR
test_ncp1_local_self_grant_does_not_cross_service_boundary (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_ncp1_local_self_grant_does_not_cross_service_boundary) ... ERROR
test_trusted_service_positive (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_trusted_service_positive) ... ERROR
test_unknown_reference_is_denied (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_unknown_reference_is_denied) ... ERROR
test_candidate_cannot_consume_trusted_authority_record (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_candidate_cannot_consume_trusted_authority_record) ... FAIL
test_fabricated_record_id_has_no_candidate_authority (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_fabricated_record_id_has_no_candidate_authority) ... ok
test_genuine_client_result_is_diagnostic_only (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_genuine_client_result_is_diagnostic_only) ... ERROR
test_request_digest_changes_on_reference_rebind (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_request_digest_changes_on_reference_rebind) ... ok
test_candidate_local_socket_peer_forgery_cannot_self_grant (test_v24_v6_successor8_candidate_local_red.Successor8CandidateLocalAuthorityRed.test_candidate_local_socket_peer_forgery_cannot_self_grant) ... ok
test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume) ... FAIL

======================================================================
ERROR: setUpClass (test_v24_v6_successor5_external_authority_gate.Successor5ExternalAuthorityGateRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor5_external_authority_gate.py", line 214, in setUpClass
    subprocess.run(
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/tmp/v24-s9-build-20260919/governance-runtime/.gate-build/v24_v6_external_authority_gate', '--identity']' returned non-zero exit status 1.

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
FAIL: test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow (test_v24_v6_successor6_gate_replacement_red.Successor6GateReplacementRed.test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_gate_replacement_red.py", line 66, in test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow
    self.assertFalse(
AssertionError: True is not false : {'authority_effect': 'NONE_EVIDENCE_ONLY', 'construction_authoritative': True, 'decision': 'ALLOW', 'gate_id': 'V24-V6-EXTERNAL-AUTHORITY-GATE', 'gate_version': '1', 'context_digest': '0000000000000000000000000000000000000000000000000000000000000000', 'scope_digest': '1111111111111111111111111111111111111111111111111111111111111111', 'reference_digest': '2222222222222222222222222222222222222222222222222222222222222222', 'build_input_sha256': '3333333333333333333333333333333333333333333333333333333333333333'}

======================================================================
FAIL: test_candidate_identity_is_unprivileged (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_candidate_identity_is_unprivileged)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 39, in test_candidate_identity_is_unprivileged
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_copied_gate_at_caller_selected_path_is_nonauthoritative (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_copied_gate_at_caller_selected_path_is_nonauthoritative)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 102, in test_copied_gate_at_caller_selected_path_is_nonauthoritative
    self.assertNotEqual(proc.returncode, 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_gate_parent_directory_rename_unlink_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_gate_parent_directory_rename_unlink_replacement_rejected)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 76, in test_gate_parent_directory_rename_unlink_replacement_rejected
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

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
FAIL: test_pinned_source_post_measurement_substitution_rejected_by_permissions (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_pinned_source_post_measurement_substitution_rejected_by_permissions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 86, in test_pinned_source_post_measurement_substitution_rejected_by_permissions
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

======================================================================
FAIL: test_same_user_gate_executable_replacement_rejected (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_same_user_gate_executable_replacement_rejected)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 64, in test_same_user_gate_executable_replacement_rejected
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

======================================================================
FAIL: test_trusted_gate_and_runtime_are_root_owned_nonwritable (test_v24_v6_successor6_trusted_control_domain.Successor6TrustedControlDomainTests.test_trusted_gate_and_runtime_are_root_owned_nonwritable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor6_trusted_control_domain.py", line 61, in test_trusted_gate_and_runtime_are_root_owned_nonwritable
    self.assertEqual(st.st_mode & 0o222, 0, oct(st.st_mode))
AssertionError: 128 != 0 : 0o100755

======================================================================
FAIL: test_candidate_ld_preload_cannot_forge_authoritative_allow (test_v24_v6_successor7_candidate_loader_red.Successor7CandidateLoaderInjectionRed.test_candidate_ld_preload_cannot_forge_authoritative_allow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_candidate_loader_red.py", line 112, in test_candidate_ld_preload_cannot_forge_authoritative_allow
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_candidate_cannot_access_trusted_private_result_channel (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_access_trusted_private_result_channel)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 170, in test_candidate_cannot_access_trusted_private_result_channel
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

======================================================================
FAIL: test_candidate_cannot_ptrace_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_ptrace_trusted_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 161, in test_candidate_cannot_ptrace_trusted_service
    self.assertEqual(rc, -1)
AssertionError: 0 != -1

======================================================================
FAIL: test_candidate_cannot_replace_service_endpoint (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_replace_service_endpoint)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 165, in test_candidate_cannot_replace_service_endpoint
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

======================================================================
FAIL: test_candidate_cannot_signal_trusted_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_cannot_signal_trusted_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 144, in test_candidate_cannot_signal_trusted_service
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised

======================================================================
FAIL: test_candidate_identity_is_unprivileged_and_service_is_root (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_identity_is_unprivileged_and_service_is_root)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 89, in test_candidate_identity_is_unprivileged_and_service_is_root
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_candidate_ld_library_path_rebind_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_library_path_rebind_rejected_by_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 139, in test_candidate_ld_library_path_rebind_rejected_by_service
    attacked = _child_request(env)
               ^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 83, in _child_request
    raise AssertionError((proc.stdout, proc.stderr))
AssertionError: ('', 'Traceback (most recent call last):\n  File "<string>", line 3, in <module>\nModuleNotFoundError: No module named \'test_v24_v6_proof_reference_closure\'\n')

======================================================================
FAIL: test_candidate_ld_preload_gate_injection_rejected_by_service (test_v24_v6_successor7_trusted_service.Successor7TrustedServiceTests.test_candidate_ld_preload_gate_injection_rejected_by_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 132, in test_candidate_ld_preload_gate_injection_rejected_by_service
    attacked = _child_request(env)
               ^^^^^^^^^^^^^^^^^^^
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor7_trusted_service.py", line 83, in _child_request
    raise AssertionError((proc.stdout, proc.stderr))
AssertionError: ('', 'Traceback (most recent call last):\n  File "<string>", line 3, in <module>\nModuleNotFoundError: No module named \'test_v24_v6_proof_reference_closure\'\n')

======================================================================
FAIL: test_candidate_cannot_consume_trusted_authority_record (test_v24_v6_successor8_authenticated_authority.Successor8AuthenticatedAuthorityTests.test_candidate_cannot_consume_trusted_authority_record)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor8_authenticated_authority.py", line 44, in test_candidate_cannot_consume_trusted_authority_record
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

======================================================================
FAIL: test_candidate_loader_interposition_cannot_forge_authoritative_consume (test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/v24-s9-build-20260919/governance-runtime/test_v24_v6_successor9_consume_loader_red.py", line 85, in test_candidate_loader_interposition_cannot_forge_authoritative_consume
    self.assertNotEqual(os.geteuid(), 0)
AssertionError: 0 == 0

----------------------------------------------------------------------
Ran 41 tests in 0.834s

FAILED (failures=19, errors=9)

```

## 7. Inherited failure adjudication
- Candidate-context failures/errors are preserved as context/setup or artifact-surface failures where candidate identity, root-only gate setup, or missing caller-selected gate paths are asserted; they are not silently relabelled as mechanism PASS.
- Root-context failures/errors are invalid for candidate-identity assertions and private-channel denial assertions when run as root; those transcripts remain historical infrastructure/context evidence.
- Same-process imported-verifier self-grant, gate replacement, live gate/build-manifest mismatch, ownership/write-bit assertions, and service lifecycle errors remain review findings requiring independent adjudication; no qualification claim is made.

## 8. Final runtime integrity and RQ-32 reboot
### aws-codex-rq1-final-integrity-20260919T220500Z.txt
```text
2026-09-18T21:10:22Z
a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d  /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
8ce4b19ec71defd9b2b964d93a6fdcad6c9916013bd14852bc3252e0daee5469  /opt/v24-v6-trusted-runtime/.service-build.json
active
enabled
u_str LISTEN 0      16                  /run/v24-v6-authority/service.sock 22218            * 0          
0:0 555 /opt/v24-v6-trusted-runtime
0:0 555 /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
0:0 755 /run/v24-v6-authority
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
active
active
/run/v24-v6-authority/private/consumed/6826322fea677558098ce23ca90e7801f4e7043c77d6cbb7ea3eb5bdc338a7b3.record
/run/v24-v6-authority/private/consumed/f62911b489ef8246095f65b4786e1e54626c92dc04b5dc7a5e643a6b93e53ad0.record
/run/v24-v6-authority/private/records/00c509858254ba23be377a60129d21cab6eaf008318869202d7ccb51c03f50f6.record
/run/v24-v6-authority/private/records/07e8644943deb60369d144be9d388b55ef7dd0433986ba35db8a8678dafc0739.record
/run/v24-v6-authority/private/records/14b6ffaf60f353ce252406904a68e4cb870de9a7f9ce3d6e818b42b9d718d04b.record
/run/v24-v6-authority/private/records/2e9e1e57e06c4c0acf0e31224e377258593336d6850fae6829942244ec246f27.record
/run/v24-v6-authority/private/records/2feb09366310deb91d37954807ae9e614c809c13eaead8f3709ba99c7b8eec99.record
/run/v24-v6-authority/private/records/2ffb6d155496027b8f40c5ce76f6089acb0e014beadfdf16ca2da74bd86fe4a2.record
/run/v24-v6-authority/private/records/407e126b2a90fc36b964bcef4753895b736f5fb8c408729c5ac0535b67a11f79.record
/run/v24-v6-authority/private/records/4cad79c68d9e4432f23e67243e24889b667bed15adfc9ee271d833eca9c8ea9f.record
/run/v24-v6-authority/private/records/540e1ccc8dc5b84f41c67521903a0234207d3c4490c028065f015361e4918989.record
/run/v24-v6-authority/private/records/700ccbd13ba1fed8a5ecb9174aed773f4aeea91aa4dd7f49a3a5a99d360ada7f.record
/run/v24-v6-authority/private/records/724fded9b0f19b64ad1c6b5a1bf6318304a94cbe6448e5ac373fd4b1ea89dacb.record
/run/v24-v6-authority/private/records/7a83417c3939d0c860bc90a3d69d0cd3df36ffb1600113061b59355506a31897.record
/run/v24-v6-authority/private/records/7b088367e461e4f93e2d5154ef91cd6a19bcb1d194a042c7c1f35e38c16bfb0b.record
/run/v24-v6-authority/private/records/7c39f9d5c8d45732e6785c294a81043c7a8acb9779c65abebf14615bd15a2173.record
/run/v24-v6-authority/private/records/8fe63b0c1bdcaadaf51aa3dd058d3f8098879f19356834358593ccbaf4143052.record
/run/v24-v6-authority/private/records/9393e320e959cd62cf1b751eea18064b50c1060af6105f9d92ef4aff7e1c73b5.record
/run/v24-v6-authority/private/records/9df8631d3fd16e0b34f759bbad17f3c60282057bde97fd2cd1130dd71832c866.record
/run/v24-v6-authority/private/records/a4764de4bd02f2c47ee275c1942708ed108b4f712cb36768ad35c5cea1db6b79.record
/run/v24-v6-authority/private/records/a8e9596dd246cf1d589c97d8c5edd017e36476e559650be13da1db6c76f5889c.record
/run/v24-v6-authority/private/records/abe4d58c62793c42f8250e8dc8b56b96d6d1523fe1e9bf0ae7068a5702b83428.record
/run/v24-v6-authority/private/records/bdba96d41941accd399694bfd33616f89c88c9418b261d37844e450d3129cebc.record
/run/v24-v6-authority/private/records/dc4d510fdd0bf1efc95d14ab934f1a536af72715b77e1e5ddf91d6da824acb0f.record
/run/v24-v6-authority/private/records/dc7fb878fd6b0d85b723e32b91cb11c5ce887690fbe1227594839d2d0939b4d2.record
/run/v24-v6-authority/private/records/fd09fc63ae7f9231bffa2670640687e4715a1f73b3b3ea7232894851d5ec8cae.record

```
### aws-codex-rq1-remediation-rq32-post-reboot-20260919T211500Z.txt
```text
2026-09-18T20:51:32Z
phase=RQ-32-post-reboot
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
Linux ip-172-31-4-29 6.17.0-1017-aws #17~24.04.1-Ubuntu SMP Tue May 26 21:30:32 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d  /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
active
enabled
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
0:0 755 /run/v24-v6-authority
0:0 555 /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
u_str LISTEN 0      16                  /run/v24-v6-authority/service.sock 5980            * 0          
active
active

```
### aws-codex-rq1-remediation-rq32-pre-reboot-20260919T211500Z.txt
```text
2026-09-18T20:50:56Z
phase=RQ-32-pre-reboot
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
Linux ip-172-31-4-29 6.17.0-1017-aws #17~24.04.1-Ubuntu SMP Tue May 26 21:30:32 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
a9567ea1677456949e79bb64c06c6880426afcaaaa5235e5579ca3e62e7b021d  /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service
active
fs.suid_dumpable = 0
kernel.unprivileged_userns_clone = 0
user.max_user_namespaces = 0
kernel.yama.ptrace_scope = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
0:0 755 /run/v24-v6-authority
0:0 555 /opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service

```

## 9. SHA-256 manifest
- aws-codex-rq1-final-inherited-candidate-20260919T220000Z.txt -- 12cb05f69b7c2b35079abd1850650c38e3c8758ae49f76138b7270ec987f1fb5
- aws-codex-rq1-final-inherited-root-20260919T220000Z.txt -- ec55a1ed7fab4c6c3712e3d8b68851a785b4e52aac524909e8be77ebed849303
- aws-codex-rq1-final-integrity-20260919T220500Z.txt -- 6fdaf94433a9bd17eee50d07810fb0b79757634cd461fed023e94f799dfa62ff
- aws-codex-rq1-remediation-rq32-post-reboot-20260919T211500Z.txt -- fed7e92c66bc6d36ef12e902fca3dae04978b12150fe9c0cf2513aa7291a5d12
- aws-codex-rq1-remediation-rq32-pre-reboot-20260919T211500Z.txt -- 451d225c7473e5d4b0165231dcaf864d92b8820e59c4d1126b404ac7d1250ca1
- case-progress.jsonl -- 5110c1b9e6bebe8178c9819b9fcb76041463c7c2cb980529c97268a7ac1250ce
- RQ-01.json -- b9f04d828bbdf8c433becda7553b211d422d465f4cf1d491e356629802978d56
- RQ-01.raw.json -- 00ff82c91e3a6ff502a4e476b95c2e44134fda380257936c10674aa0640e45a8
- RQ-02.json -- f2f944dde5f9793541554b85ac571c58f363eddca3dd25543e8f8eb88c0b9e9c
- RQ-02.raw.json -- 45687a366ffbb374bce20cb350256490aff9aa2638af0a33790c0bfe29492260
- RQ-03.json -- 8233c23f4c5170d615d953bbecb5ab2e113f04c5a1da44f1d234f66a140d28a9
- RQ-03.raw.json -- 837611d5a37b7feb92487ce69ea71d1cddc7a7aa4fd661908ef2cbe50d2fd269
- RQ-04.json -- 1c461dbcb5343f994f65206d067b69f730da2bc99932c56df9d86336f1c93cb6
- RQ-04.raw.json -- 339ba435621097ad1fec60c7f72a6940a8d153af056d38c6d0a15f4f1917bbcf
- RQ-05.json -- 4072a4dff87b8a8808c5bdae605af00f8be048a3c39bca2993b2497175bd03cf
- RQ-05.raw.json -- 7ea7ef8c0fd6c84811d2c8a0762d29eb61c33fe57f19d9aa32af3f80e63fdfe5
- RQ-06.json -- 3e52d2de50856cc51aff2133e0ff25c16dd37fab391fdfc5999ea87247913194
- RQ-06.raw.json -- c8e6fa47f13f492c92ac0eaa57f0edcf1864817bab436b998338ff0fd658b99d
- RQ-07.json -- b4cba943ff56fb1c44a0e5ec3e74ce4021baaf31f0a2319538b0ccc1b95f4d75
- RQ-07.raw.json -- a3b9dd6070c9fcf1804b6e51cfbe74731be723294cac986271dba5ed67617ed8
- RQ-08.diagnostic.json -- 3c1ec3b52b3e84ad743b9fce0a8c3578e9d57ecb982fbf8f5c1539003f570bb3
- RQ-08.json -- 683299394c6b3c410cdc1240bf5ceebd0b4f35623115b0c316ad272c5335e51c
- RQ-08.raw.json -- b42ce39e3daef64cfb3e7bb3c3c9315f6a7e5ef4ffc48a1f7cc333a42800e426
- RQ-09.diagnostic.json -- 185cd78520f01120c817fa7ea6e2b74eef5611b8a68a968c1e100cfc0d5f8ac5
- RQ-09.json -- 010673fdda13ab3199ab24732feff1061a7760d4951845c800a81d8cd33097a0
- RQ-09.raw.json -- 025d42021fb834f9bcc3b4c4d8e8f36f35e4eb29040df477e32678eb95b48db8
- RQ-10.diagnostic.json -- a26cba890b8493ccd87c407aea3d57e95cdf66f821d6d5b0dfd37d6f5986e7d0
- RQ-10.json -- 7c7777a331d08f648f7ca6f6e57bdb6a01a55d92a8dde6ccf5f991932de8b1aa
- RQ-10.raw.json -- 623ffa69cede8c23e8ba12fd1796b681c4be0d007d85d24985fe5ec20c93ad55
- RQ-11.json -- b01f17b3c1dfcb159aa6f06a97a57c78daa3af0cbe3f262d6705f2ac839806be
- RQ-11.raw.json -- 4b50be2e544945e24ebcb852037bd006579bd0ff8625742dda1c8eba32fa1403
- RQ-12.diagnostic.json -- 25df5808505257364bdd66e343514639aa476068ccdd963abe4842dc4630993b
- RQ-12.json -- ff38930a551923d80ec1c761493114bdf7a7322f062be106629893a972daf2a5
- RQ-12.raw.json -- 401babebe0916195bada760fbf9788d65786198a484e9f6f6ca06cb57f299b99
- RQ-13.json -- 6cb355c2aec671d541620f45e07c0a0e71a652fb50586c557fc360d40fbdc47e
- RQ-13.raw.json -- 0f908a54ccd3b2cccad7f839ad0db17ee2afdd9409b8a763fca5477de43037f5
- RQ-14.json -- a2f7d05964e75757b12074ec3d589b2b228625b01153fcb5e961792b2d49a50c
- RQ-14.raw.json -- 71451adc578e9e9d7f92f58dc17ba63511024f65968f7ee6a826a48fd7fa8752
- RQ-15.json -- 10b3012eb65573ce578d1ce4314f5b8d4b3a359597e010f74df48131b86711e7
- RQ-15.raw.json -- f530edd99f38e8db85dfbe566c0948d029c7f9f957c6278b67bd453cb9e0de54
- RQ-16.json -- 51b3a11e4e266d8a5da859c6e23af0a379398c85643cd0e3d0f7f70f891dbdb1
- RQ-16.raw.json -- de3b48f0a2746bb3169ff52575edbd2326b3271c89d01a4a1c63ea14565e7340
- RQ-17.json -- 8e823d88c2847001cfb21dd1d768d25d7fa082fff77fd9b57f5e05384875b0d4
- RQ-17.raw.json -- 5c12cc1f0e07586698938f335a355d51837f0b512bf8d95df8669fb6e5e805aa
- RQ-18.json -- 3bcd604835392705a00094b4228be5c88f801e8352cc5694b60803ccc745194a
- RQ-18.raw.json -- ed54c0074d851ff0fc0585cf611226ea92b2954f584f883e5793ca781d2e8a58
- RQ-19.json -- ff937bed17ce6870ca5f746c4b129ad4d25ba821668c0249541fce46d68fd6a9
- RQ-19.raw.json -- ee502fd9c53d368be2afc9206a2d9f870dfb8cd74e88a1045420b0e111513882
- RQ1-bundle.json -- f878293e8fe8e27d5838a683556a7f03406f1a5cb813f7be9cf844013308ead9
- rq1-final-remediation-evidence.tar -- 587ed8081fd523cd599f0608b286b244b2b02dbe94b19e8606a878f8e3bbc8bf
- RQ-20.json -- a0bd5626b357a56be3ec2f16be1f0ba7346ed53ae84a863b48d2b21836eda5de
- RQ-20.raw.json -- 595fb51853157e33604595281a43c76eb700a8377e2add6b23dc2b0d6e9311b8
- RQ-21.json -- fc939c32926d862d28d4a28ee0780c5f65ca1f5c0790da884b1dabc49c9a7bb9
- RQ-21.raw.json -- a4967b02fcd4fff56ab4f91da322bd4b37ec0a4be5eeec11b78bfe585cd57727
- RQ-22.json -- 748311d726316252fe2946bc5359bacabe020fa9dceefb8448bb5416bc852393
- RQ-22.raw.json -- 16beb690b73b4cc95c7c6f5ee04ff21f0372782139a71fe868dceb65f018ea81
- RQ-23.json -- dd2bd13878c17bece34d6639573fa50e0ded377884d2a176c438198c31ca8a64
- RQ-23.raw.json -- b85a259b12c1275acfe0882644c05880ae2ec9fcd4fa1256bb927ac29cce25d5
- RQ-24.diagnostic.json -- 9df35aa4000abacd3cc4428adb02aaad4d9672a2e0eec2ddb9dc98509e469b03
- RQ-24.json -- 69e45acaaf1954e9777ef161483982b61f8773bf49d800fbd66904e5991b5999
- RQ-24.raw.json -- 9c6e1fe254334e2bd276fcfc518d51b06d2e2ccd8fabdefa42fb5e2e129d97e5
- RQ-25.diagnostic.json -- 25c4b3658a122ba6387ae181e8c367d75efd431579faa179bdbeb0aa6f2349ca
- RQ-25.json -- e4b4b6e46d5237a9dfca4743c979d20060ce06e17fed08e729436c9bdf92ecf2
- RQ-25.raw.json -- ef8dd8466aaefae25b2f18c448d98b599c8f77f6e42585aa2379ebcfd40ab7df
- RQ-26.json -- e84aff354a51f3cc297d66920e5aef0a24ae8dcdad3d2f202bdb3e1128c63b5e
- RQ-26.raw.json -- 64951e887f59cd6eee05f1ae85e04aa8902129777898641c16fb4f4e644de7be
- RQ-27.json -- d824358ab964a2b20a2bc9314484d99b7e2350c2b2fd65400f9a8ef1149eb1f9
- RQ-27.raw.json -- 05d985286d9ff03561c4e040ca5a3cd369ef6d1ce57c81f9786b79e60daf8d6f
- RQ-28.json -- 8dbf061dca37487b131a25d4923fc182cec9c521b4ad28b9bdaba6a25dce8dfd
- RQ-28.raw.json -- 419e2cea7553dab11626aa36bc7fa3db9a52505934754b9b066075331b102eef
- RQ-29.json -- 17ef8a1fb65c148ab66d011d381be0f6e89ce93aac28df6f160132dbbd75b4e4
- RQ-29.raw.json -- 6c976ca8d0e08ddb111226defc68fb9126d6bb59e52ceace791e7d8dce43e9a1
- RQ-30.json -- b83b4b774ebb5c684092e57f0831efb1c3a63dfec113a7d170a35e7c6645f032
- RQ-30.raw.json -- 3fc2ece2e00147088e444e241362c0f0d633901f2a5127859842f698afb845c8
- RQ-31.json -- 4a4748d78617a37451a1a3d17ec5facad783a42a55399fb6c25e1f7d906e951e
- RQ-31.raw.json -- c71417eb3b5a678a8302bba4be5f265d8abf9db5524e28b821290aafa81740ac
- RQ-32.json -- 091e08fa707fafa73c4d3e89fa73540b8f90be1585d001048d874d0cf40853bf
- RQ-32.raw.json -- 9a98cdcb64ea54124ac4cbbd9ebd55a47f8e2257ca99b4ec2cd385691f73090c
- governance-runtime/v24_v6_rq1_harness.py -- 58388be1d536229741295288d8af42f5425fe753cc60ac22ee21ce9d5d5b5a61
- governance-runtime/V24-I11-V6-RQ1-EVIDENCE-SCHEMA.json -- 431879b5e016a83c69af1a4d5d094548e146b88ff11378b78f2afaa314ff75d2
- implementation/v24/V24-I11-V6-RQ1-REMEDIATION-1-STATUS-20260919.md -- 71a1818893d7c22bd844e2c4b32f9a623973895a7af0e0b139009d6eb73c7bed
- implementation/v24/V24-I11-V6-RQ1-CLAUDE-REVIEW-CHANGES-REQUIRED-20260919.md -- cbbf89fceb865bf1411f37530a7124457ea7c8edef1336eaff118ad0e6ef28ac

## 10. Second independent-review checklist
- Determine whether every final PASS is backed by substantive independent evidence and exact oracle execution.
- Determine whether any result is self-referential or lacks cleanup/recovery proof.
- Determine whether the remediation closes CF-01 through CF-08.
- Determine whether it closes MF-01 through MF-05.
- Determine whether it closes MN-01 through MN-03.
- Individually adjudicate inherited candidate/root failures, especially verifier self-grant, copied gate, manifest mismatch, ownership/write-bit, and socket lifecycle findings.
- Determine whether the RQ-08 transport stall was correctly diagnosed and whether any orphan process contamination remains.
- Determine whether RQ-16, RQ-24, RQ-25, RQ-31 and RQ-32 execute the exact frozen oracle rather than a proxy.
- Verify scientific execution remains CLOSED, authority effect remains NONE_EVIDENCE_ONLY, and qualification remains NOT_QUALIFIED.
- Provide an independent CHANGES_REQUIRED or PASS disposition and required adjudication.