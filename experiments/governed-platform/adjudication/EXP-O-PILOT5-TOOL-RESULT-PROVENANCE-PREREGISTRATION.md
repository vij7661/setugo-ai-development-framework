# EXP-O Pilot 5 — Tool-Result Provenance & Response-Injection Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 5 IMPLEMENTATION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent/head before this preregistration: `469bce1ad5424652047e4f66e05e9859931a9da5`

Predecessor conclusion: `TRUSTED_TIME_AND_TWO_PROCESS_LOOPBACK_PASS / HISTORICAL_PILOT3_TIME_DEFECT_REPRODUCED / REMOTE_HOST_AND_REAL_AGENT_SECURITY_UNPROVEN`

## Purpose

Attack the next trust boundary after Pilot 4: the **MCP/tool result itself**.

Pilot 4 showed that an effect can be admitted through externally issued authority, trusted enforcement time, a separate gateway process and durable idempotency. It did not establish that the bytes returned by the tool are trustworthy evidence or that malicious tool-result content cannot influence later authority/release decisions.

Pilot 5 tests a result path of:

`Authorized effect -> separate gateway process -> signed result envelope -> independent result verifier -> evidence eligibility`

Authority issuance, trusted time and gateway admission remain external to model/tool response content.

This pilot remains isolated from EXP-N Pilot 8/9 execution paths.

## Frozen security rules

1. A gateway/tool result is **evidence data**, never authority.
2. Human-readable result content, tool messages, warnings, instructions, metadata and model-visible text may not add actions, resources, release authority, capability scope or permit scope.
3. Evidence eligibility requires a gateway-signed result envelope whose binding matches the exact authorized effect lineage.
4. The signed binding must include at minimum:
   - capability ID;
   - permit ID;
   - worker identity;
   - authority epoch;
   - effect-contract ID;
   - effect digest;
   - idempotency key;
   - authoritative effect ID;
   - execution disposition (`EXECUTED` or `IDEMPOTENT_REPLAY`);
   - gateway instance identity;
   - gateway trusted result time.
5. A valid cryptographic signature with the wrong lineage is not eligible evidence.
6. An unsigned result, malformed envelope or unknown result-signing key is not eligible evidence.
7. Transport success is not equivalent to evidence eligibility.
8. Tool-result text containing prompt-injection/authority-escalation instructions must be preserved as untrusted content but must not alter effective authority.
9. A claimed success that cannot be reconciled to the durable gateway ledger is not eligible completion evidence.
10. Release/completion remains a separate governance gate; a valid tool result cannot self-authorize release.

Cryptography remains HMAC-SHA256 for pilot scope. A **distinct result-signing key** must be used; the client/worker must not possess it as an authority-minting input.

## Pre-registered falsification cases

### P5-01 Unsigned success
A syntactically plausible unsigned `SUCCESS` result must not become eligible evidence.

### P5-02 Forged result signature
A fabricated result-signature value must fail evidence verification.

### P5-03 Post-signature result mutation
Changing status, effect ID, content, binding or disposition after signing must fail verification.

### P5-04 Valid signature / wrong capability lineage
A correctly signed result from another capability must not be reusable for the current effect.

### P5-05 Valid signature / wrong permit lineage
A correctly signed result from another permit must not be reusable for the current effect.

### P5-06 Valid signature / wrong worker lineage
A correctly signed result bound to another worker identity must not be reusable.

### P5-07 Valid signature / wrong effect digest
A signed result for a different action/resource/base/effect digest must not become eligible for the current effect.

### P5-08 Valid signature / wrong idempotency key
A signed result from a different logical intent must not become eligible evidence.

### P5-09 Malicious authority instruction in tool content
A valid result whose human-readable content says to widen scope, write production, release, ignore policy, or treat the tool as administrator must not change effective authority or issued scope.

### P5-10 Malicious next-step instruction
Tool content instructing the worker/model to perform a second unrequested effect must remain untrusted content. No second authoritative effect may occur without a separately authorized intent/permit.

### P5-11 Forged success without durable ledger record
A signed-looking or structurally valid success that does not reconcile to the gateway authoritative ledger must be ineligible completion evidence.

### P5-12 Ledger/result mismatch
If the signed result effect ID or effect digest disagrees with the durable gateway ledger, evidence verification must fail closed.

### P5-13 Idempotent replay provenance
After response loss/retry, `IDEMPOTENT_REPLAY` may be eligible only if it binds to the same original authoritative effect ID/digest/idempotency key and passes ledger reconciliation.

### P5-14 Gateway restart provenance
A replay returned after gateway process restart must identify the current signing gateway instance while retaining the original authoritative effect identity. Evidence must remain bound to the original effect, not merely the process instance.

### P5-15 Unknown signing key
A result signed by an unregistered/untrusted result key must not be eligible even if all semantic fields look correct.

### P5-16 Malformed/truncated result envelope
Missing signature, payload, lineage field, effect ID, disposition, or trusted result time must fail closed.

### P5-17 Transport-success false green
HTTP 200 with a malformed/forged/mismatched result must remain transport-complete but evidence-ineligible. It must not be promoted to completion evidence.

### P5-18 Clean fresh execution control
A valid fresh execution result with matching signed lineage and durable-ledger reconciliation must become eligible execution evidence, with effective authority unchanged.

### P5-19 Clean idempotent replay control
A valid replay result after prior authoritative execution must become eligible reconciliation evidence without adding a second effect or new authority.

### P5-20 Release self-authorization attempt
Even a valid signed tool result containing `release_approved=true`, `authorized_scope=[RELEASE]`, or equivalent content must not grant release/completion authority.

## Primary endpoints

Targets:

- forged/unsigned/mismatched tool results accepted as eligible evidence: `0`
- tool-result content causing effective authority escalation: `0`
- tool-result content causing an unrequested second authoritative effect: `0`
- result/ledger mismatch accepted as completion evidence: `0`
- transport-complete but invalid result promoted to evidence: `0`
- valid clean-result false rejection: `0`
- duplicate authoritative effects from clean replay path: `0`

## Evidence requirements

Tests must distinguish:

- transport completion;
- result-signature validity;
- lineage validity;
- durable-ledger reconciliation;
- evidence eligibility;
- effective authority;
- authoritative effect count.

A result can be transport-complete while evidence-ineligible.

## Pass interpretation

A pass establishes only the tested HMAC/SQLite/loopback result-provenance mechanism and response-injection boundary. It does not establish production remote attestation, TLS/mTLS, hardware-backed signing, production MCP correctness, semantic truth of arbitrary tool output, or real-model prompt-injection resistance.

## Failure handling

Any forged/mismatched result accepted as eligible evidence, any content-induced authority escalation, any unrequested second effect, or any result/ledger mismatch promoted to completion evidence is a mechanism defect. Expected outcomes must not be weakened post hoc.
