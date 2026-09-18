# V24-I11-V6 Successor-8 — Authenticated Authority Channel Repair Design

Status: **PREREGISTERED AFTER SUCCESSOR-7 MANUAL REVIEW / RED EXECUTION PENDING**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and blocking review

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-7`
- commit: `167a54a9bece04a2470fa1fca03009f7cf627d71`
- tree: `e2b89458dc0c3f1885a7dddc8f9e8de1d51e0c3d`
- exact final-head run: `35340932149`
- integrated all-up: `332/332 GREEN`
- clean package run: `35341350001`
- final manual-review commit: `3cb3a9efb82f58bca9fb7734b285e2e2d8a2bde1`
- disposition: `CHANGES_REQUIRED`

Successor-7 GREEN evidence remains valid bounded construction evidence for the genuine host-namespace service/bootstrap path. It is not reclassified.

## 2. Findings to falsify

### PRC-1F — namespace-relative service identity is candidate-constructible

Successor-7 authenticates the candidate-visible endpoint with a pathname plus numeric `SO_PEERCRED.uid == 0`.

That identity is not bound to:
- the host user namespace;
- the host mount namespace;
- the frozen service executable;
- a service-held signing key;
- a trusted consumer outside candidate control.

Where unprivileged user/mount namespaces are available, candidate execution can potentially construct a private namespace view with a fake root peer and fake service pathname.

### PRC-1G — candidate-local client result is ordinary mutable data

`v24_v6_trusted_service_client.request_service()` returns an ordinary Python dictionary after candidate-local socket, peer-credential, JSON, and label checks.

A candidate controlling the same interpreter can replace the socket implementation, peer-credential result, JSON response, client helper, or returned dictionary. The current result contains no unforgeable service receipt whose validation occurs outside candidate-mutable Python.

## 3. Required Successor-8 invariant

No candidate-local pathname, numeric UID, Python object, or self-declared service label may constitute authority.

The bounded authority channel MUST satisfy all of the following:

1. The genuine trusted service remains separately launched under the trusted OS identity.
2. Candidate-visible service output is explicitly non-authoritative unless bound to a trusted receipt/effect outside candidate Python.
3. The genuine service produces a request-bound authority record that candidate code cannot forge.
4. The authority record binds at least:
   - protocol/version;
   - exact request digest;
   - exact decision;
   - service identity/version/build;
   - gate result identity/digest;
   - governance generation/context/scope identity where applicable.
5. Candidate code cannot create an authoritative record merely by:
   - replacing `request_service`;
   - replacing `socket.socket`;
   - forging `SO_PEERCRED`;
   - constructing a fake namespace-local endpoint;
   - replaying a valid record onto another request;
   - changing the service path or executable.
6. The authority-bearing consumer/ledger/receipt verifier is outside candidate-mutable Python.
7. A fake namespace-local service may fool an untrusted client copy, but it MUST NOT create the trusted authority record/effect.
8. Failure to obtain/validate the trusted authority record fails closed.
9. Successor-7 bootstrap v3, root service, private scratch, and inherited gate/root-attestation controls remain preserved.

## 4. First mandatory preserved RED

The first deterministic Successor-8 RED MUST prove that candidate-local client verification can still self-grant without modifying the genuine service.

Attack shape:

1. import the production `v24_v6_trusted_service_client` module in candidate Python;
2. replace the candidate-local socket object with an attacker implementation;
3. report fake peer credentials containing UID 0;
4. return an attacker JSON response containing the exact expected service ID/version and:
   - `service_authoritative=true`;
   - `construction_authoritative=true`;
   - `decision=ALLOW`;
5. call the unmodified production `request_service()`;
6. demonstrate that the forged ALLOW is returned as if it came from the trusted service;
7. assert that candidate-local replacement must never be sufficient to create an authoritative result.

This RED is intentionally deterministic and does not depend on whether the current CI host permits unprivileged user namespaces. A separate permanent namespace regression remains mandatory.

## 5. Mandatory permanent regressions

Successor-8 MUST freeze at least:

1. `CANDIDATE_LOCAL_SOCKET_PEER_FORGERY_REJECTED`
2. `CANDIDATE_REQUEST_SERVICE_REPLACEMENT_NONAUTHORITATIVE`
3. `NAMESPACE_LOCAL_FAKE_SERVICE_NONAUTHORITATIVE`
4. `AUTHORITY_RECORD_REQUEST_BINDING_ENFORCED`
5. `AUTHORITY_RECORD_REPLAY_REJECTED`
6. `AUTHORITY_RECORD_SERVICE_BUILD_BINDING_ENFORCED`
7. `AUTHORITY_RECORD_GATE_RESULT_BINDING_ENFORCED`
8. `TRUSTED_AUTHORITY_RECORD_POSITIVE`
9. all Successor-7 service/bootstrap regressions remain mandatory;
10. all Successor-6/5/4 regressions remain mandatory;
11. DA-1 and NCP-1 compound attacks are rerun against the authenticated authority record/effect.

## 6. Prohibited repair shapes

The following are insufficient:

- another Python-only check of `SO_PEERCRED`;
- checking more service JSON labels in candidate Python;
- comparing `request_sha256` only inside candidate Python;
- moving the socket pathname while retaining candidate-selected path lookup;
- another numeric UID/GID check without namespace provenance;
- signing a receipt whose validation is only candidate-mutable Python;
- a candidate-generated HMAC/MAC key;
- a service-held secret copied into candidate-readable files;
- documentation-only assumption that user/mount namespaces are disabled;
- treating a fake-client-resistant unit test as proof of a trusted external consumer.

## 7. Bounded construction direction

Preferred shapes include:

### A. Trusted authority ledger/effect

The genuine root service records the exact decision and request binding into root-only state, and the trusted authority consumer reads/enforces that state directly. Candidate-visible JSON is diagnostic only.

### B. Service-authenticated receipt plus trusted verifier

The genuine service creates a receipt authenticated with key material unavailable to candidate execution. A separately trusted verifier/consumer validates the receipt and exact request binding outside candidate Python.

### C. Trusted-parent capability channel

A trusted parent supplies a pre-established capability/FD and consumes the authority result itself. Candidate path/mount lookup never selects the service endpoint.

The chosen construction mechanism may combine these shapes.

## 8. Namespace requirement

If the construction environment relies on disabling unprivileged user/mount namespaces, that policy becomes load-bearing and MUST be:

- explicitly enforced;
- independently measured;
- included in the frozen evidence;
- fail-closed when absent.

Otherwise, the authority mechanism must remain safe even when candidate code can create a private user/mount namespace.

## 9. DA-1 and NCP-1 progression

DA-1 and NCP-1 remain locally repaired but transitively open while PRC-1 is open.

After Successor-8 authority-record closure, rerun:

- fresh decision -> effect-path/target/effect-class self-grant;
- stale decision/effect substitution;
- fresh clause -> control reassignment;
- stale clause/control substitution;
- cross-control composition;
- fake client/service response substitution;
- authority-record replay/rebinding.

## 10. Claim boundary

Successor-8 remains construction-only.

It does not establish hostile-root resistance, production IAM/HSM/KMS custody, production namespace policy, deployment/release authority, remote-service security, scientific WDPC outcomes, or general native-code memory safety.

Scientific execution remains closed. Runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 11. Progression rule

Successor-8 may proceed to implementation only after the candidate-local service-client self-grant is preserved RED against the frozen Successor-7 mechanism.

Successor-8 may be frozen for independent manual review only after:

- Successor-7 final review remains historical;
- Successor-8 RED remains historical and is never relabeled;
- candidate-local client/path/UID fabrication cannot create the trusted authority record/effect;
- namespace-local fake service results cannot create the trusted authority record/effect;
- trusted authority records are exact-request bound and replay resistant;
- the authority-bearing consumer is outside candidate-mutable Python;
- all mandatory Successor-8 regressions are GREEN;
- all inherited Successor-7/6/5/4 regressions are GREEN;
- complete V24-V6 R1-R9 and inherited V24 suites are GREEN;
- DA-1/NCP-1 compound attacks are rerun through the authenticated authority channel;
- scientific execution remains closed;
- runtime qualification remains `NOT_CLAIMED`.
