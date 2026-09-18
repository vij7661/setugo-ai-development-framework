# V24-I11-V6 Successor-9 — Trusted In-Service Consume and Semantic Binding Repair Design

Status: **PREREGISTERED AFTER SUCCESSOR-8 MANUAL REVIEW / RED EXECUTION PENDING**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and blocking review

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-8`
- commit: `2accab62a8437b74c5ad599f0c3d338b7825bbbf`
- tree: `36f020a7f1553259cc4dd76253e9fc0850a59974`
- exact final-head run: `35345890327`
- integrated all-up: `337/337 GREEN`
- clean package run: `35346388071`
- final manual-review commit: `0bf1a4f08add3a25452f01a85750351112feb430`
- disposition: `CHANGES_REQUIRED`

Successor-8 GREEN evidence remains valid bounded construction evidence for the authority-record, replay, bootstrap and namespace surfaces it actually exercises. It is not reclassified.

## 2. Findings to falsify

### PRC-1H — candidate-launchable consume process remains loader-mutable

Successor-8 makes candidate-visible service responses diagnostic-only and moves authority into a root-only `--consume-record` path.

However, `--consume-record` is implemented by the same ordinary dynamically linked executable that candidate code can launch directly. The candidate-launched process internally decides whether it is trusted using `geteuid()` and root-filesystem checks.

The root-owned executable bytes are immutable to the candidate, but a candidate-launched non-setuid process still honors candidate-controlled dynamic-loader state. Interposition can therefore target the consume process itself before `main()`.

### PRC-1I — consume validates an opaque caller-supplied digest, not the trusted intended request

The record commits the request only through `request_sha256`. At consume time the native consumer receives only record ID plus `EXPECTED_REQUEST_SHA256`.

The consumer does not reconstruct that digest from the trusted intended operation/context/payload/effect. Therefore it proves token equality but not end-to-end semantic identity of the authority action.

## 3. Required Successor-9 invariant

The authority-bearing consume/effect transition MUST remain inside an already-running trusted process/control domain that candidate code cannot directly launch with candidate-selected loader state.

The bounded mechanism MUST satisfy all of the following:

1. Candidate code cannot directly execute any authority-bearing consume helper.
2. Direct candidate execution of the service binary, copied binary, wrapper or helper can produce diagnostic data only and never an authoritative effect.
3. Record consumption occurs inside the separately launched trusted root service or an equivalently protected trusted parent.
4. The trusted consume endpoint is inaccessible to the candidate identity and is not selected by candidate path/environment input.
5. The trusted consumer independently derives the expected request digest from canonical trusted request material; the candidate may not choose both the record token and the value used to validate it.
6. The trusted consume path binds operation, reference/subject identity, context, boundary, payload/effect identity, service build, gate result, record schema and decision.
7. One-shot replay protection remains preserved.
8. Candidate loader variables, interposition, fake `geteuid`, fake filesystem helpers, fake namespace-local paths and fabricated JSON cannot create authoritative output/effect.
9. DA-1/NCP-1 authoritative outcomes are consumed only after trusted-side semantic request reconstruction.
10. Successor-8 bootstrap v4, root-private records, namespace condition and all predecessor regressions remain historical and preserved.

## 4. First mandatory preserved RED

Before production repair, Successor-9 MUST preserve a deterministic attack against the frozen Successor-8 consume mechanism.

The attack MUST:

1. execute the frozen root-owned service binary directly as the unprivileged candidate;
2. supply candidate-controlled `LD_PRELOAD`;
3. interpose the consume path's trust checks, including `geteuid` and root-filesystem-facing functions;
4. redirect the record read to a candidate-controlled record containing the publicly known service/build/request fields;
5. bypass the pathname consume transition locally;
6. demonstrate that the candidate-launched process emits `construction_authoritative=true, decision=ALLOW`;
7. assert that candidate execution must never be able to create such an authoritative result.

If observed, this is a genuine mechanism failure and MUST remain permanently RED.

## 5. Mandatory permanent regressions

Successor-9 MUST freeze at least:

1. `CANDIDATE_LD_PRELOAD_CONSUMER_INTERPOSITION_REJECTED`
2. `CANDIDATE_FAKE_EUID_CONSUMER_REJECTED`
3. `CANDIDATE_FAKE_RECORD_FILESYSTEM_CONSUMER_REJECTED`
4. `DIRECT_CANDIDATE_CONSUMER_OUTPUT_NONAUTHORITATIVE`
5. `TRUSTED_CONSUME_ENDPOINT_CANDIDATE_INACCESSIBLE`
6. `TRUSTED_CONSUMER_RECOMPUTES_EXACT_REQUEST_BINDING`
7. `GENUINE_ALLOW_RECORD_WRONG_OPERATION_REJECTED`
8. `GENUINE_ALLOW_RECORD_WRONG_PAYLOAD_EFFECT_REJECTED`
9. `AUTHORITY_RECORD_REPLAY_REJECTED`
10. `TRUSTED_IN_SERVICE_CONSUME_POSITIVE`
11. all Successor-8 authority-record and namespace regressions remain mandatory;
12. all Successor-7/6/5/4 regressions remain mandatory;
13. DA-1 and NCP-1 compound attacks are rerun through the trusted in-service consume boundary.

## 6. Prohibited repair shapes

The following do **not** close the finding:

- clearing `LD_PRELOAD` inside an already candidate-launched consume process;
- another `geteuid()` or UID/GID check in the candidate-launched helper;
- root ownership or mode bits alone on an executable the candidate can execute;
- trusting a candidate-presented `construction_authoritative=true` JSON result;
- accepting record ID plus candidate-supplied request digest without trusted-side request reconstruction;
- another candidate-visible socket/CLI path whose result itself is treated as authority;
- signing/MACing a receipt when verification remains only in candidate-mutable Python;
- documentation-only assumptions about trusted invocation provenance.

## 7. Bounded construction direction

Preferred construction shape:

1. Keep the existing genuine root service separately launched under the trusted OS identity.
2. Keep the candidate-facing request socket diagnostic-only.
3. Add a separate root-only consume/control endpoint inside the already-running service, or an inherited trusted file descriptor/capability owned by the trusted parent.
4. The trusted caller submits the record ID together with the exact intended canonical request/effect material.
5. The trusted service independently recomputes the request digest and compares it to the root-private record.
6. The service performs the atomic one-shot transition internally.
7. The final authority-bearing effect/result is delivered only over the trusted control channel; candidate-local process output remains non-authoritative.
8. Remove or permanently de-authorize the candidate-launchable `--consume-record` CLI.

## 8. DA-1 and NCP-1 progression

DA-1 and NCP-1 remain locally repaired but transitively open while PRC-1 is open.

After in-service consume repair, rerun:
- fresh decision -> effect-path/target/effect-class self-grant;
- stale decision/effect substitution;
- fresh clause -> control reassignment;
- stale clause/control substitution;
- cross-control composition;
- genuine ALLOW record substituted across operations;
- genuine ALLOW record substituted across payload/effect identity;
- direct candidate consume-output forgery.

## 9. Claim boundary

Successor-9 remains construction-only.

It does not establish hostile-root resistance, production IAM/HSM/KMS custody, production namespace policy, deployment/release authority, remote-service security, scientific WDPC outcomes, or general native-code memory safety.

Scientific execution remains closed. Runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 10. Progression rule

Successor-9 may proceed to production implementation only after the candidate-loader consume attack is preserved RED against the frozen Successor-8 mechanism.

Successor-9 may be frozen for independent manual review only after:
- Successor-8 final review remains historical;
- the new Successor-9 RED remains historical and is never relabeled;
- candidate-launchable consume execution is permanently non-authoritative;
- the authority-bearing consume transition runs inside an already-running trusted control domain;
- trusted-side semantic request/effect reconstruction is enforced;
- record replay/rebind protections remain GREEN;
- all mandatory Successor-9 and inherited regressions are GREEN;
- complete V24-V6 R1-R9 and inherited V24 suites are GREEN;
- DA-1/NCP-1 compound attacks are rerun through the new consume boundary;
- scientific execution remains closed;
- runtime qualification remains `NOT_CLAIMED`.
