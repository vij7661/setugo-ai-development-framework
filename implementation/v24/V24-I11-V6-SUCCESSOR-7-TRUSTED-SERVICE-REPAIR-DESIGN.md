# V24-I11-V6 Successor-7 — Trusted Service Execution and Bootstrap Repair Design

Status: **IMPLEMENTED / ALL-UP GREEN / EXACT FINAL-HEAD FREEZE PENDING**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and blocking review

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-6`
- commit: `f4b81c2ec9535c44af6fd4f18f2dcd62eddd1e78`
- tree: `ffa4bf6be27c5c58536b151cc596d58baf33925c`
- exact final-head run: `35335403525`
- exact integration binding digest: `c5984e2602334ee04b49fd3c943546bf5404e0cc1bb0e4b7d881772ac6faec07`
- bounded all-up evidence: `318/318 GREEN`
- final manual-review commit: `15678f4416a1b35b71e5fd7877edd5b64c8c4e9a`
- disposition: `CHANGES_REQUIRED`

Successor-6 GREEN evidence remains valid bounded evidence for the static file-replacement surfaces it actually exercises. It is not reclassified.

## 2. Findings to falsify

### PRC-1C — live gate executes under candidate UID

Successor-6 makes the gate executable and worker/source tree root-owned and candidate-nonwritable, but the candidate invokes the gate directly. The gate process therefore runs with the same effective UID as the candidate caller.

Static file ownership does not create a process authority boundary. Candidate-controlled process surfaces can still influence a same-UID child process before or during authority evaluation.

A deterministic first attack for Successor-7 is dynamic-loader injection. The gate is a normal dynamically linked executable, not a privileged secure-execution binary. A candidate caller can launch it with `LD_PRELOAD` pointing to candidate-controlled code. That preloaded code executes inside the authority-gate process before `main()` and can interpose process behavior such as the worker `execve()` call.

### PRC-1D — candidate-owned temporary decision channel

The gate writes worker/probe JSON to `mkstemp("/tmp/v24-v6-gate-worker-XXXXXX")` and later reparses it via `jq` by pathname. Because the gate runs under the candidate UID, those temporary files are owned and writable by the candidate UID.

A same-UID concurrent process can therefore substitute authority-bearing intermediate JSON after capture and before parse.

### PRC-1E — trusted installer self-describes trusted bytes

The root installer obtains expected gate/source digests from the candidate-generated `.gate-build/v24_v6_external_authority_gate_build.json`. One-sided binary corruption is rejected, but coherent substitution of both the artifact and the manifest remains self-consistent.

The bootstrap that decides which bytes become root-owned trusted bytes therefore lacks an independent expected digest/root outside the candidate tree.

## 3. Required Successor-7 invariant

The authority-bearing decision must execute in a process/control domain that candidate execution cannot directly launch with attacker-selected loader state, debug, mutate, or impersonate.

The bounded construction authority path MUST satisfy all of the following:

1. Candidate execution communicates with a fixed trusted service/parent endpoint; it does not directly execute the authority binary.
2. The trusted service runs under an OS identity/control domain distinct from the candidate identity.
3. The candidate cannot supply `LD_PRELOAD`, `LD_LIBRARY_PATH`, interpreter path, worker path, executable path, trusted root, or service startup environment.
4. The trusted service owns the gate logic, exact root-verification identity, parser/result channel, and final construction decision.
5. Authority-bearing intermediate results are never written to candidate-owned pathname-addressable files.
6. Worker/parser communication uses trusted in-memory parsing, pipes/file descriptors, sealed memory, or a trusted-private directory inaccessible to candidate execution.
7. The service fails closed on malformed IPC, unavailable worker, timeout, unexpected peer identity, unexpected service identity/version/build, or internal parser failure.
8. The trusted bootstrap independently pins/authenticates the exact service/gate/worker/build identities before installation.
9. Candidate-generated build metadata cannot be the sole authority for the bytes that become trusted.
10. Direct execution of a copied or candidate-built gate remains non-authoritative.

## 4. First mandatory preserved RED

The first Successor-7 RED MUST target the frozen Successor-6 gate without changing its production bytes.

The attack MUST:

1. use a valid externally signed Successor-6 proof context/boundary;
2. select a syntactically valid but unknown qualification reference that the genuine worker rejects;
3. launch the frozen root-owned gate under the candidate UID with candidate-controlled `LD_PRELOAD`;
4. have the preload library interpose the worker `execve()` and substitute an attacker worker result bound to the exact input fields;
5. demonstrate that the native gate emits `construction_authoritative=true, decision=ALLOW` for the unknown reference;
6. assert that such an ALLOW must be impossible.

The attack produced ALLOW and is now permanently preserved as a genuine mechanism RED.

Preserved Successor-7 RED:
- branch head tested: `1837fab5e3a15e5fabebdedfaccc259a2a350227`
- workflow: `V24 V6 Successor-7 Candidate Loader RED`
- workflow run: `35336888966`
- job: `105573671594`
- test: `test_candidate_ld_preload_cannot_forge_authoritative_allow`
- setup/build/install/candidate-staging steps: `GREEN`
- attack regression: `RED`
- observed authoritative result: `construction_authoritative=True`, `decision=ALLOW`
- forged unknown reference: `ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`
- gate build-input SHA-256 observed: `4e76eeaf554293d7f3a1faa615aec6c422c4b37d9b1677b94cdf1279fdcee818`
- forged worker-result SHA-256: `e722a643e11f1cdbe4d307c925d8b388cf0c81c675fe3f688e9ae3324eca95f0`

The baseline unmodified invocation rejected the unknown reference. Only the candidate-controlled dynamic-loader injection changed the authority outcome to ALLOW. This is a mechanism defect, not a fixture or expectation defect, and must never be relabeled as PASS.

## 5. Mandatory permanent regressions

Successor-7 MUST freeze at least:

1. `CANDIDATE_LD_PRELOAD_GATE_INJECTION_REJECTED`
2. `CANDIDATE_LD_LIBRARY_PATH_REBIND_REJECTED`
3. `SAME_UID_GATE_PROCESS_TRACE_OR_INJECTION_REJECTED`
4. `CANDIDATE_TEMP_RESULT_SUBSTITUTION_REJECTED`
5. `TRUSTED_SERVICE_PEER_IDENTITY_ENFORCED`
6. `CALLER_CANNOT_SELECT_SERVICE_EXECUTABLE_OR_WORKER`
7. `COHERENT_GATE_AND_BUILD_MANIFEST_SUBSTITUTION_REJECTED`
8. `CANDIDATE_SELECTED_TRUSTED_ROOT_REJECTED`
9. `TRUSTED_SERVICE_POSITIVE`
10. all Successor-6 static replacement regressions remain mandatory;
11. all Successor-5 verifier/key/helper regressions remain mandatory;
12. DA-1 and NCP-1 compound attacks are rerun through the trusted service boundary.

## 6. Prohibited repair shapes

The following are insufficient:

- clearing `LD_PRELOAD` only inside the already candidate-launched gate;
- another file-mode or ownership check while the gate still runs under candidate UID;
- another candidate-owned `/tmp` file with a harder-to-guess name;
- rehashing a temporary result before reopening the same candidate-writable pathname;
- trusting a build JSON whose expected digest is defined only by the candidate build itself;
- a root-owned wrapper that accepts candidate-selected executable or worker paths;
- a service socket whose peer identity is not checked;
- a service process launched by candidate code with candidate-controlled environment;
- documentation-only narrowing of the same-UID attacker model.

## 7. Bounded construction direction

The preferred construction shape is a separately launched trusted parent/service under a distinct OS identity, with:

- fixed root-owned executable and startup configuration;
- fixed trusted root and service endpoint;
- candidate-to-service IPC over a Unix-domain socket or equivalent;
- peer credential checks;
- no candidate-controlled dynamic-loader environment;
- trusted parent invocation of exact pinned worker logic under a separate verifier identity if Python remains necessary;
- pipe/descriptor/in-memory result transfer with no candidate-writable intermediate pathname;
- externally pinned/signed bootstrap manifest for service/gate/worker identities.

The service may remain local for construction falsification. This does not claim production deployment readiness.

## 8. Bootstrap direction

Successor-7 must separate *candidate build description* from *trusted installation authority*.

At minimum, the trusted bootstrap must receive an independently frozen expected manifest digest or signed bundle whose authority does not come from the candidate files being installed.

The bootstrap must validate:
- exact installer/service identity;
- exact gate/service binary digest or reproducible build identity;
- exact worker/source digests;
- exact service protocol/version;
- exact trusted destination;
- no symlink/path redirection;
- no caller-selected root.

## 9. DA-1 and NCP-1 progression

DA-1 and NCP-1 remain locally repaired but transitively open while PRC-1 is open.

After service isolation, rerun:
- fresh decision -> effect-path/target/effect-class self-grant;
- stale decision/effect substitution;
- fresh clause -> control reassignment;
- stale clause/control substitution;
- cross-control composition;
- live IPC/result-channel substitution attempts.

No DA-1 or NCP-1 closure claim is allowed solely from local Python checks.

## 10. Claim boundary

Successor-7 remains construction-only.

It does not establish production HSM/KMS custody, hostile-root resistance, production IAM, remote-service security, deployment authority, scientific WDPC outcomes, or general native memory safety.

Scientific execution remains closed. Runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 11. Progression rule

Successor-7 may proceed to implementation only after the deterministic candidate-loader injection is preserved RED against the frozen Successor-6 mechanism.

Successor-7 may be frozen for independent manual review only after:

- Successor-6 final review remains historical;
- the new Successor-7 RED remains historical and is never relabeled;
- the gate decision executes under a separate trusted service/OS identity;
- candidate loader/debug/process injection cannot alter the trusted service;
- candidate-owned temporary result channels are removed from authority-bearing paths;
- bootstrap manifest authority is independent of candidate-generated build metadata;
- all mandatory Successor-7 regressions are GREEN;
- all inherited Successor-6/5/4 regressions are GREEN;
- complete V24-V6 R1-R9 and inherited V24 suites are GREEN;
- DA-1/NCP-1 compound attacks are rerun through the service boundary;
- scientific execution remains closed;
- runtime qualification remains `NOT_CLAIMED`.


## 12. Implemented construction evidence

Successor-7 now has a separately controlled root authority service, a root-private authority result channel, and an external bootstrap authority that independently pins the exact source/build identities before installation.

Preserved historical failures remain unchanged:
- Successor-7 loader-injection RED: run `35336888966`;
- initial trusted-service mechanism failure: run `35338295835`;
- external-bootstrap v1 trust-manifest mismatch: run `35339093613`;
- hardened-v3 pre-integrated-binding run: `35340164729`, which failed only because the integrated manifest still bound the predecessor gate-source blob.

Final integrated all-up evidence before exact final-head freeze:
- remediation head tested: `f4f0f8d55dd7a525efed5a5626b9cfe1456b17a5`;
- workflow: `V24 V6 Successor-7 External Bootstrap All-Up`;
- workflow run: `35340391007`;
- job: `105584706975`;
- Successor-7 plus inherited authority regressions: `43/43 GREEN`;
- complete V24-V6 R1-R9 regressions: `199/199 GREEN`;
- inherited V24 regressions: `90/90 GREEN`;
- total: `332/332 GREEN`;
- evidence artifact: `10544906479`;
- evidence artifact digest: `sha256:d0d8dba5dded21669f3d86cb7811f5a7d438e0ee0c87a209ea303ba9761fa3fe`;
- external bootstrap trust commit: `ffd215e0c73b1ca0294cbd06ddd8ddac77007b2a`;
- trust tree: `8bff10c7601d0472e8d20966fe789d8e5a63bca4`;
- bootstrap manifest blob: `ccfa227d511934b8c5068ee395604f06d7097aed`;
- bootstrap script blob: `1ed659e082fec1e4c1d2f22b7137ab4223d3176e`;
- hardened gate build-input SHA-256: `b0f0b0f91c88b1746d6bffa7d3b4955aa6f494cc525de45d7435582dfb77f1b9`;
- hardened gate binary SHA-256: `7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`;
- trusted service build-input SHA-256: `b3016817f1587d6282ef5a41e2b9b48d49a5461fa5845d9af59c19bbcb509383`;
- trusted service binary SHA-256: `34f1190c11e78a4db693b16f93dc4f6a72e618ff99ab764c5471db3c1596dc8a`.

This is bounded construction evidence only. It does not open scientific execution and does not claim runtime qualification.

The next permitted step is exact final-head freeze followed by independent manual review.
