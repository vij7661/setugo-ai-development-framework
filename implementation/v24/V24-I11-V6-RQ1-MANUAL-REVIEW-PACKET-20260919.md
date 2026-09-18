# V24-I11-V6 Runtime Qualification 1 — Independent Review Packet

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
