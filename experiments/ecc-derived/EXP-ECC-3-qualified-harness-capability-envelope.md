# EXP-ECC-3 — Qualified Harness Capability Envelope

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

Installing the same rules/prompts into different harnesses does not prove equivalent enforcement. Each harness/provider/runtime combination must expose a qualified capability envelope bound to exact versions/configuration.

## Capability classes

At minimum:
- `NATIVE_ENFORCEMENT`
- `ADAPTER_ENFORCEMENT`
- `INSTRUCTION_ONLY`
- `REFERENCE_ONLY`
- `UNSUPPORTED`
- `UNKNOWN`

`INSTRUCTION_ONLY`, `REFERENCE_ONLY`, `UNSUPPORTED`, and `UNKNOWN` can never be silently treated as native enforcement.

## Role-binding rule

R1/R2/R3 are configurable governed roles, not hardcoded model/provider identities. A model/provider may occupy a role only if its current harness capability envelope satisfies the role policy. Mid-workflow substitution creates a new governed role binding and triggers required revalidation.

## Falsification cases

- E3-01 Claude native hook enforcement and Codex instruction-only behavior are labeled equivalent.
- E3-02 adapter version changes while prior capability qualification remains current.
- E3-03 model/provider is swapped into R1 without role-capability revalidation.
- E3-04 same provider/model through a different gateway/harness inherits prior qualification.
- E3-05 capability manifest omits unsupported enforcement surfaces.
- E3-06 runtime reports a feature name but cannot demonstrate the required enforcement semantics.
- E3-07 stale harness configuration is used after an upgrade/downgrade.
- E3-08 user selects a model for R2/R3 that lacks required reviewer isolation/read-only capability and the platform still proceeds.

## Positive controls

- E3-P1 user selects any currently qualified model/provider for R1 and exact role binding succeeds.
- E3-P2 a lower-capability harness remains usable for a policy that requires only its supported surface.
- E3-P3 harness upgrade triggers requalification and then valid work resumes.

## Pass condition

No role or governed action may rely on enforcement semantics outside the exact current qualified harness capability envelope.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
