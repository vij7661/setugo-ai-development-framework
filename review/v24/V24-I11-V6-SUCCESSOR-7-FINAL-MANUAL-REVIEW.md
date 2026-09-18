# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-7

## A. Overall disposition

**CHANGES_REQUIRED**

Successor-7 materially improves the construction boundary. The authority gate is no longer launched by candidate Python, a root-owned service now mediates the authority path, candidate loader/environment injection does not cross the tested IPC boundary, gate scratch state is moved into a root-private directory, and the bootstrap v3 trust object independently pins the source/build identities before installation.

The remaining blocker is service identity itself. The candidate-visible client treats a pathname-selected Unix socket plus `SO_PEERCRED.uid == 0` and self-declared service labels as sufficient proof that a response came from the trusted service. That identity check is namespace-relative and the response is not cryptographically authenticated. Under Linux configurations that permit unprivileged user and mount namespaces, candidate code can construct a private namespace view in which candidate-controlled code is UID 0, replace the visible `/run/v24-v6-authority` mount with candidate-controlled storage, run a fake socket server at the fixed pathname, and return an arbitrary authoritative-looking ALLOW without modifying the genuine host root service or trusted runtime.

The current candidate neither prohibits/binds such namespace creation as a trusted host policy nor provides a service-held signature/MAC/capability that a trusted consumer outside candidate control validates.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.

## B. Candidate and package identity

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-7`
- frozen candidate commit: `167a54a9bece04a2470fa1fca03009f7cf627d71`
- frozen candidate tree: `e2b89458dc0c3f1885a7dddc8f9e8de1d51e0c3d`
- exact final-head run: `35340932149`
- exact final-head job: `105586420882`
- integration binding digest: `babd20185eda9395935e34ad95c01d374066df50273e01276eae728cdf2410fc`
- bound file count: `28`
- preserved Successor-7 loader-injection RED: `35336888966`
- integrated all-up run: `35340391007`
- all-up tests: `332/332 GREEN`
- final-head verification artifact: `10544473501`
- final-head verification artifact digest: `sha256:ab7d96f3daf583ae3875e6fc15438c5aa2852f68314df082d9ee5783c31dce12`
- clean review package run: `35341350001`
- clean review package artifact: `10545342125`
- clean review package artifact digest: `sha256:e7ff97c196e2fcf92da41d4eb987e1931106279b7b32650560fc20fd54a37dec`
- deterministic package ZIP SHA-256: `429a9158cab5bfb30403ea77af5e983a8a811657df0a8e18ea2851d41c417f2a`
- package manifest SHA-256: `f3edb3caf536f5d11650bf0c078befabbb2edf361167263cfed7a1d253cb6850`
- verification JSON SHA-256: `40563a48db198871f0cbb40a69cb79e264418900a556255933d68e1d07948202`
- bootstrap trust commit: `ffd215e0c73b1ca0294cbd06ddd8ddac77007b2a`
- bootstrap trust tree: `8bff10c7601d0472e8d20966fe789d8e5a63bca4`
- bootstrap manifest blob: `ccfa227d511934b8c5068ee395604f06d7097aed`
- bootstrap script blob: `1ed659e082fec1e4c1d2f22b7137ab4223d3176e`
- hardened gate binary SHA-256: `7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`
- trusted service binary SHA-256: `34f1190c11e78a4db693b16f93dc4f6a72e618ff99ab764c5471db3c1596dc8a`

The GREEN evidence remains valid bounded construction evidence. It does not override the finding below.

## C. Critical finding

### C-01 — Namespace-relative root/socket identity can be counterfeited by candidate code

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** candidate process -> `v24_v6_trusted_service_client.py` -> Unix socket pathname -> `SO_PEERCRED` -> returned service JSON

The candidate client connects to the fixed pathname:

`/run/v24-v6-authority/service.sock`

and treats the peer as trusted when:

1. the kernel-reported peer UID is numeric `0`; and
2. the returned JSON contains the expected `service_id`, `service_version`, and `service_authoritative=true`.

The client does not bind the peer to the host user/mount namespace, the frozen service executable, an externally measured process identity, or a service-held cryptographic key.

A concrete false-green path exists on hosts where unprivileged user/mount namespaces are available:

1. candidate execution enters a new user namespace and maps itself to namespace UID 0;
2. candidate execution enters a private mount namespace;
3. it overlays the visible `/run/v24-v6-authority` path with a candidate-controlled tmpfs/bind-mounted directory;
4. it starts a fake Unix-socket server at the same fixed pathname inside that namespace;
5. the candidate client runs in the same namespace and connects to the fake endpoint;
6. `SO_PEERCRED` reports the fake peer as UID 0 in that namespace;
7. the fake server emits:
   - `service_id=V24-V6-TRUSTED-AUTHORITY-SERVICE`;
   - `service_version=1`;
   - `service_authoritative=true`;
   - `construction_authoritative=true`;
   - `decision=ALLOW`;
8. the candidate client accepts and returns the forged result.

The genuine root-owned service, gate binary, worker set, private scratch directory, and bootstrap trust objects never need to be modified.

This is the same class of trust failure Successor-7 was intended to close: candidate-controlled execution can construct an object that the candidate-visible authority path accepts as the external authority.

#### Why current controls do not close it

Current Successor-7 regressions establish that, in the host namespace used by the workflow:

- candidate code cannot unlink the genuine socket;
- candidate code cannot signal or ptrace the genuine root service;
- candidate code cannot access the genuine root-private scratch directory;
- candidate `LD_PRELOAD` / `LD_LIBRARY_PATH` does not affect the already-running root service;
- an unauthorized root client is rejected by the genuine service;
- coherent source/build-manifest substitution is rejected by bootstrap v3.

Those controls do not authenticate the service endpoint across candidate-created namespace views.

The frozen host contract also does not pin and attest a policy that disables unprivileged user/mount namespaces, nor does it bind the client to the service's host namespace or executable identity.

#### Narrow required repair

The next successor must make service identity unforgeable from candidate-controlled namespaces. A bounded repair may use one or more of these shapes:

1. a trusted parent passes an already-open capability/socket file descriptor to candidate execution, so candidate path/mount lookup cannot select the authority endpoint;
2. the trusted service emits a receipt signed/MACed with service-held key material unavailable to candidate execution, and a trusted consumer outside candidate control validates that receipt and exact request binding;
3. the authority-bearing consumer remains entirely inside the trusted service/control domain instead of trusting a candidate-local Python dictionary;
4. if Linux namespace prohibition is intentionally part of the bounded model, the prohibition must be enforced and independently attested as a load-bearing host policy, not merely assumed.

Permanent regression coverage must attempt a candidate-created user/mount namespace with a fake service endpoint where the host permits it, and must prove that no authoritative ALLOW is accepted. If the host forbids the primitive, that prohibition itself must be measured/frozen and fail closed when absent.

## D. High findings

### H-01 — Client-visible verdict authenticity remains candidate-local

The service response contains `request_sha256` and `gate_result_sha256`, but `request_service()` does not independently recompute and bind the request digest, validate a service signature/MAC, or produce an externally verifiable receipt. It returns an ordinary Python dictionary after checking numeric peer UID and self-declared labels.

Candidate Python can replace or bypass the client function and manufacture the same dictionary shape. That does not alter what the genuine root service actually decided, but it means a later consumer cannot safely treat a candidate-presented result object as proof of the service decision.

**Blocking:** Yes for any progression that treats the client-visible result as authority-bearing evidence.

Narrow repair: keep the effect/consumer inside the trusted service or introduce a cryptographically authenticated, request-bound receipt whose validation occurs outside candidate-mutable Python.

### H-02 — DA-1 remains transitively open through service impersonation

The DA-1 compound regression correctly shows that a Python-local fresh effect-path self-grant is rejected by the genuine Successor-7 service.

C-01 permits a candidate-visible fake service endpoint to return ALLOW for that same attacker-selected payload without the genuine service evaluating it.

**DA-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

### H-03 — NCP-1 remains transitively open through service impersonation

The NCP-1 compound regression likewise depends on the candidate reaching the genuine service endpoint. A namespace-local fake service can return ALLOW for an attacker-selected clause/control binding.

**NCP-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

## E. Positive findings

The following controls are materially stronger and should be preserved:

- the Successor-7 loader-injection attack is preserved as genuine RED and is not relabeled;
- the genuine authority service runs under root rather than the candidate UID;
- candidate loader variables do not propagate into the already-running service;
- candidate signal and ptrace attempts against the genuine root service are rejected in the frozen environment;
- the genuine service endpoint resides under a root-owned host directory and cannot be unlinked by the candidate in that namespace;
- authority-bearing scratch files are moved to `/run/v24-v6-authority/private`, root-owned mode `0700`;
- the gate uses the trusted-private scratch path when running as root;
- bootstrap v3 independently pins Git blob identities for the source/build set;
- candidate-selected trusted-root rebinding is rejected;
- coherent gate/service/source plus self-generated build metadata substitution is rejected;
- the frozen gate and service binaries are reproducibly bound by SHA-256;
- Successor-6 static replacement regressions remain preserved;
- Successor-5 verifier/key/helper regressions remain preserved;
- Successor-4 root-attestation regressions remain preserved;
- DA-1 and NCP-1 compound attacks are exercised through the genuine service boundary;
- exact final-head and clean package identities are frozen deterministically.

## F. Bounded observations

The bootstrap deliberately relies on the trusted host toolchain and privileged deployment environment for `git`, `jq`, `sha256sum`, `gcc`, `bash`, and system libraries. That is acceptable only within the stated construction boundary and is not production deployment qualification.

The native service currently validates the child gate result using exact pinned gate code plus fixed substring checks. No candidate-controlled gate-output injection route was identified in the frozen design because the gate binary/source/worker set is independently pinned and root-controlled; nevertheless, a future protocol should prefer structural parsing of one exact result object over substring recognition.

## G. Explicit blocker adjudication

- **PRC-1:** **OPEN / CRITICAL / BLOCKING** at service endpoint/namespace authenticity.
- **DA-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.
- **NCP-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.

## H. Evidence and claim boundary

This review is construction-level only.

It does not claim:

- hostile-root resistance;
- production IAM/HSM/KMS custody;
- production namespace/sandbox policy;
- deployment/release authority;
- remote-service security;
- scientific WDPC outcomes;
- general native-code memory safety.

No earlier failure is reclassified. Successor-7's preserved loader-injection RED remains a genuine mechanism failure. The later 332/332 GREEN all-up run and exact-final-head GREEN remain valid bounded evidence for the specific host-namespace service and bootstrap surfaces they actually exercise.

## I. Final progression statement

**Successor-7 may not progress.**

A new repair/refreeze/re-review cycle is required.

The next successor should preserve the root service, private scratch path, external bootstrap v3, and predecessor regressions, while replacing namespace-relative pathname/UID service identity with an unforgeable authority channel.

At minimum, the next cycle should permanently cover:

1. candidate user-namespace UID-0 impersonation;
2. candidate mount-namespace replacement of the fixed service pathname;
3. fake service JSON with correct ID/version/authority labels;
4. replay/rebinding of a genuine service receipt to a different request;
5. direct candidate replacement/bypass of the Python service client;
6. DA-1 and NCP-1 compound attacks through the hardened authority channel.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**.  
Runtime qualification remains **NOT_CLAIMED**.  
Authority effect remains **NONE_EVIDENCE_ONLY**.
