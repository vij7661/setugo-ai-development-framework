# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-6

## A. Overall disposition

**CHANGES_REQUIRED**

Successor-6 materially improves the static construction trust boundary. The native authority gate and measured worker/source set are installed into a root-owned, candidate-nonwritable runtime, caller-selected copied gate paths are rejected, the preserved Successor-5 file-replacement class is addressed for the installed filesystem objects, and the exact final-head evidence is cleanly bound.

However, the live authority decision is still executed under the candidate operating-system identity. The frozen tests launch the root-owned gate as a subprocess of the unprivileged candidate process. The native gate then writes worker/probe JSON into ordinary `mkstemp()` files under `/tmp`, owned by that same candidate identity, and later reopens those files through `jq` by pathname. A concurrent same-UID attacker can therefore modify the gate's intermediate decision material after capture and before parse. Static root ownership of the executable/source tree does not make the running gate process, its worker, or its temporary decision channel a separate trusted control domain.

A second independent bootstrap weakness remains: the root installer accepts the candidate-generated build manifest as the source of the expected gate/source hashes. A coherent substitution of both the build artifact and its build manifest can therefore be root-installed as a self-consistent "trusted" runtime unless an external trusted bootstrap pins the expected digest independently of the candidate tree.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.

## B. Candidate identity

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-6`
- frozen candidate commit: `f4b81c2ec9535c44af6fd4f18f2dcd62eddd1e78`
- frozen candidate tree: `ffa4bf6be27c5c58536b151cc596d58baf33925c`
- exact final-head run: `35335403525`
- integration binding digest: `c5984e2602334ee04b49fd3c943546bf5404e0cc1bb0e4b7d881772ac6faec07`
- bound file count: `26`
- preserved Successor-6 RED run: `35333023688`
- Successor-6 all-up run: `35334689053`
- manifest-bound all-up run: `35335100210`
- clean review package run: `35335859872`
- clean review package artifact: `10542647974`
- clean review package artifact digest: `sha256:54495c449e8eed4090e54f272eb60469e05a1d313d8453816166dd666e4f90bf`
- deterministic package ZIP SHA-256: `84c74585304ccc58ddb250414e79e3853295c4fcbcc7e9b0845c97af73edd60d`
- package manifest SHA-256: `7de55ed3ac0cbee3b729455561238aa5dffac6f6ccb4dde8e50288088ce66a90`
- verification JSON SHA-256: `4dfeeb4ab6bc44e2160e78458c0024f7483f9b3c64c702b3fb9bc8463409445b`
- gate build-input SHA-256: `4e76eeaf554293d7f3a1faa615aec6c422c4b37d9b1677b94cdf1279fdcee818`
- frozen native gate SHA-256: `724543687125ae63c62d801bd9e77721adaccc8b8c9726b1b3730b2368e7af5b`
- exact final-head verification artifact: `10543575550`
- verification artifact digest: `sha256:d2a7203a76ecd5912270133a552991d3a66899349f22bcca90a231f17b5ae79d`
- all-up tests: `318/318 GREEN`

The GREEN evidence remains valid bounded construction evidence. It does not override the findings below.

## C. Critical findings

### C-01 — The native authority gate executes inside the candidate OS identity

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** candidate test/runtime process -> native authority gate -> external gate worker -> final construction ALLOW/DENY

The Successor-6 workflow explicitly runs the authority regressions as:

`sudo -u v24candidate -- ... python -m unittest ...`

and the Python test helpers invoke the gate directly with `subprocess.run(...)`. The child gate therefore inherits the same effective UID as the candidate process.

The executable bytes are root-owned and nonwritable, but the running authority process is not a separately controlled service or parent identity. The candidate is the parent/caller of the process that is supposed to constrain it.

This matters because filesystem immutability is only one part of the control domain. Same-UID process execution still leaves candidate-controlled process-level surfaces, including same-UID files, process coordination and—depending on host policy—debug/trace controls. Successor-6 does not establish a trusted service identity, privileged parent, protected IPC channel, or separately enforced consumer outside the candidate UID.

The current tests prove that the candidate cannot rewrite the installed executable/source files. They do not prove that the live authority process is outside candidate control.

#### Narrow required repair

Run the authority gate as a separately controlled trusted parent/service identity that the candidate cannot impersonate, debug, signal into a false-green state, or replace. The candidate should submit exact inputs over a narrowly defined IPC boundary to a fixed trusted endpoint. The trusted service must own the gate, worker/logic, temporary state, and final verdict consumption path.

The candidate process must not be the process parent or execution identity of the authority gate.

### C-02 — Candidate-owned temporary decision files reintroduce a concrete hash/use-style race

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** `write_temp_json()` -> `/tmp/v24-v6-gate-worker-XXXXXX` -> `run_jq(..., path)`

The native gate captures worker output in memory, then calls:

`mkstemp("/tmp/v24-v6-gate-worker-XXXXXX")`

and writes the JSON result to that pathname. Because the gate runs under `v24candidate`, the temporary file is owned by the candidate UID. The gate subsequently invokes `jq` to reopen and parse that file by pathname.

The same pattern is used for proof-resolution worker output and downstream worker output, and the downstream path also materializes the nested context-probe result before parsing.

A concurrent process under the same candidate UID can watch `/tmp` for the known filename prefix and overwrite the temporary JSON between the gate's write and the later `jq` open. The attacker does not need to alter the root-owned gate executable or trusted Python source tree.

For proof-resolution worker output, an attacker can substitute fields matching the exact command inputs:

- `qualified=true`;
- `state=PROOF_REFERENCE_CLOSED`;
- expected reference digest;
- expected generation/context/scope/subject bindings;
- `authority_effect=NONE_EVIDENCE_ONLY`.

For the downstream DA-1/NCP-1 path, the attacker can similarly emit `success=true` plus the exact context/scope/generation and payload SHA-256. Those values are either caller inputs or directly computable from caller-controlled payload bytes.

The native parent will then parse attacker-controlled temporary bytes and can emit `construction_authoritative=true, decision=ALLOW`.

This is a direct false-green route through the live gate without changing any root-owned installed artifact.

#### Why existing controls do not close it

The permanent Successor-6 regressions test:

- chmod/unlink/write denial on trusted files;
- parent-directory rename/replacement denial;
- copied caller-selected gate rejection;
- live gate digest match;
- source write denial;
- positive trusted gate execution.

They do not attempt modification of the gate's runtime-created temporary decision files or concurrent same-UID substitution between write and parse.

The filesystem ownership checks on the trusted runtime do not apply to these `/tmp` objects.

#### Narrow required repair

Do not materialize authority-bearing intermediate results into candidate-owned pathname-addressable files.

Use one of these bounded shapes:

1. parse the captured JSON directly in trusted native memory;
2. feed the exact captured bytes to a fixed parser over an already-open pipe/file descriptor without a reopen-by-path step;
3. use a sealed `memfd` or equivalent immutable descriptor owned by the trusted service;
4. if files are unavoidable, create them inside a trusted-private directory owned by the separate gate service identity and inaccessible to the candidate.

A permanent regression must deterministically attempt post-write/pre-parse substitution and prove no ALLOW can result.

### C-03 — Trusted installation is self-referential to candidate-generated build metadata

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** candidate build output + `.gate-build/v24_v6_external_authority_gate_build.json` -> root installer -> trusted runtime

The trusted installer obtains its expected binary digest from the candidate-side build manifest:

`expected_binary="$(jq -r '.binary_sha256' "$BUILD_JSON")"`

It then validates the copied gate against that same manifest. The expected worker and dependency hashes are also read from the same candidate-generated build JSON.

This rejects a one-sided binary mutation, which is what the current all-up tamper test exercises.

It does not reject a coherent substitution where an attacker or candidate-controlled build step changes both:

1. the gate/worker/source bytes; and
2. the build manifest hashes describing those altered bytes.

The installer then observes a self-consistent pair and can install the substituted bytes as root-owned, nonwritable trusted-runtime artifacts. Once installed, the filesystem ownership checks only prove that the substituted objects are now root-owned; they do not prove that they are the independently frozen objects.

The exact final-head CI and review package record the legitimate digest, but the installer does not receive that frozen digest from a trust source independent of the candidate build tree.

The bootstrap also executes the candidate-contained installer itself with `sudo bash governance-runtime/install_v24_v6_trusted_authority_gate.sh`. There is no separate preexisting trusted bootstrap component that authenticates the candidate installer and build manifest before granting them root installation effect.

#### Why existing controls do not close it

The all-up regression corrupts only the gate binary and deliberately leaves the build JSON unchanged. Failure in that case proves mismatch detection, not independent trust anchoring.

A self-consistent malicious binary + malicious build JSON has not been tested or structurally prevented.

#### Narrow required repair

Move trusted installation/bootstrap authority outside the candidate tree.

The trusted bootstrap must independently pin or authenticate:

- installer identity/version;
- exact gate binary or reproducible build identity;
- exact worker/source set;
- expected build manifest digest;
- trusted destination/root identity.

The expected digests must arrive from a separately controlled, frozen/signed authority artifact—not from the files being installed.

The candidate must not be able to choose the trusted root through an environment variable accepted by the authority bootstrap. Any configurable destination must be selected by the trusted deployment authority and have its full parent/control chain validated.

## D. High findings

### H-01 — PRC-1 remains open at the live execution/control-domain boundary

Successor-6 repairs the static same-user file replacement exposed in Successor-5, but PRC-1 remains exploitable through the candidate-UID gate process and candidate-owned temporary result channel.

**PRC-1: OPEN / CRITICAL / BLOCKING.**

### H-02 — DA-1 remains transitively open through the live gate result channel

The DA-1 compound regression correctly rejects a Python-local forged effect path when the native gate and its intermediate result channel remain unmodified.

C-02 permits the downstream worker result to be substituted after worker execution, allowing a candidate-selected decision/effect payload to be represented to the native parent as a successful externally gated result.

**DA-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

### H-03 — NCP-1 remains transitively open through the live gate result channel

The NCP-1 compound regression likewise depends on the native parent's later parse of same-UID temporary worker output. C-02 can therefore restore an externally shaped success for attacker-selected clause/control bindings.

**NCP-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

## E. Positive findings

The following controls appear sound within the bounded model where the installed gate process and its runtime-created decision channel are not attacked:

- the preserved Successor-6 gate-replacement RED remains historical and is not relabeled;
- the installed gate executable and pinned Python source set are root-owned and candidate-nonwritable;
- candidate chmod/unlink/write attempts against the trusted gate are rejected;
- trusted gate parent-directory rename/replacement attempts are rejected under the tested default `/opt` layout;
- copied gate execution under an ordinary candidate-owned path is rejected;
- live installed gate digest matches the recorded trusted build manifest;
- native root-attestation verification remains intact;
- direct Python `qualified=True` remains non-authoritative within the tested path;
- Successor-5 verifier/key/helper substitution regressions remain GREEN;
- DA-1 and NCP-1 compound regressions remain GREEN when the native gate's live result path is unmodified;
- exact final-head CI binds 26 load-bearing files;
- external trust commit/tree/blob identities remain frozen;
- the clean review package deterministically preserves predecessor review and exact design bytes;
- scientific execution remains closed and runtime qualification remains unclaimed.

These controls should be preserved in the next successor.

## F. Additional bounded observations

The gate's control-domain check uses numeric `st_uid == 0` and local mode bits rather than an independently authenticated service identity or full mount/namespace provenance. That is adequate only under a bounded host model in which candidate execution cannot create a namespace or filesystem view that makes candidate-controlled objects appear UID 0. Successor-6 does not claim hostile-host resistance, so this is not promoted to a separate blocking finding here; the next repair should nevertheless avoid relying on namespace-relative UID labels as the sole trust primitive.

The installer also accepts `V24_V6_TRUSTED_ROOT` as a destination override. The current final-head workflow uses the default `/opt/v24-v6-trusted-runtime` for the real trusted install, but a production trusted bootstrap must not accept a destination chosen by the untrusted candidate and should validate the full parent directory/control chain.

## G. Evidence and claim boundary

This review is construction-level only.

It does not claim:

- hostile-host or malicious-root resistance;
- production IAM/HSM/KMS custody;
- deployment/release authority;
- remote-service security;
- production process supervision;
- scientific WDPC outcomes;
- general native-code memory safety.

No earlier failure is reclassified.

The preserved Successor-6 gate-replacement RED remains a genuine mechanism failure. The later 318/318 GREEN runs and exact final-head GREEN remain valid bounded evidence for the specific static replacement and regression surfaces they actually exercise.

## H. Final progression statement

**Successor-6 may not progress.**

A new repair/refreeze/re-review cycle is required.

The next successor should preserve the root-owned immutable artifact improvements but move the live gate execution and verdict consumption into a separately controlled trusted service/parent identity, eliminate pathname-reopened candidate-owned temporary decision files, and externalize the installation/bootstrap manifest so the candidate cannot self-describe the bytes that become trusted.

Permanent new regressions should include:

1. same-UID temporary worker-result substitution between capture and parse;
2. same-UID live gate process manipulation/trace attempt, with fail-closed service isolation;
3. coherent gate-binary + build-manifest substitution before trusted installation;
4. candidate-selected trusted-root/destination rebinding;
5. DA-1 and NCP-1 compound attacks repeated through the separately controlled service boundary.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**.  
Runtime qualification remains **NOT_CLAIMED**.  
Authority effect remains **NONE_EVIDENCE_ONLY**.
