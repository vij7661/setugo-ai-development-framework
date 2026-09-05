# Claude Stage A — Independent Adversarial Review Brief

Review the **frozen Review Engine MVP v0.1 implementation** at commit:

`5fda61c3078c80ac0d607f546f40db316f2c9b6d`

Do not review the moving branch head. Do not assume the design is correct because tests are green.

## Role

Act as an independent adversarial architecture, security, correctness and governance reviewer. Your objective is to **falsify the system**, identify missing controls and produce reproducible findings. Do not optimize for agreement with the authors.

## System goal

The product is a model-neutral governed multi-LLM review engine:

`User -> R1 Interpreter/Builder -> platform review decision -> optional independent R2 Detector/Challenger -> scoped R1 correction -> optional blinded R3 Verifier/Adjudicator -> convergence or HUMAN_REQUIRED`

The platform, not any model, owns routing, authority, context visibility, qualification, convergence and termination.

Read `review_engine/MVP_V0_1_FREEZE.md` for the product contract and declared MVP boundaries. Treat those declared boundaries as scope constraints, but challenge any implementation that violates the stated contract even if it is described as an MVP.

## Required attack areas

Inspect the code and tests, then actively look for concrete paths that could cause:

- R1 bypassing a required R2/R3 review;
- risk/materiality under-classification or a model lowering platform-owned floors;
- qualification bypass, stale qualification, reviewer substitution, wrong role/task/risk binding;
- same/correlated reviewer being treated as independent;
- stale, superseded or revoked shared memory contaminating a decision;
- private reasoning, protected truth, prior confidence or majority signals leaking into a blinded reviewer stage;
- prompt injection through user input, memory, frozen artifacts or reviewer findings that changes governance behavior;
- R2 false positives causing unauthorized or over-broad correction;
- scoped correction changing unaffected content without detection;
- stale artifact/revision/hash TOCTOU or review of the wrong artifact version;
- malformed/truncated/provider-error output being treated as complete evidence;
- R3 anchoring, majority voting by another name, premature convergence or unresolved dissent being lost;
- replay/idempotency/concurrent duplicate-session behavior producing inconsistent authoritative history;
- concurrent memory/session writes causing stale decisions or races;
- evidence-chain gaps, event omissions, privileged tampering not detected as claimed, or dashboard state differing from authoritative evidence;
- API key/secret leakage through configuration, exception paths, request bodies, logs, memory, evidence or frontend assets;
- HTTP/UI trust-boundary issues that let client-controlled values become governance authority;
- provider identity/model-response claims being trusted beyond retained platform evidence;
- provider failure/failover paths silently changing reviewer identity or weakening qualification;
- termination loops, correction/review oscillation, or a review budget ceiling turning into false PASS;
- right final answer reached through invalid reasoning/process where the system should not converge;
- any important requirement, state transition, invariant, security control or evidence field that the implementation simply forgot.

Do not limit yourself to this list.

## Review method

Prefer concrete source-backed findings over general recommendations. For each material finding provide:

1. **Finding ID and title**
2. **Severity:** CRITICAL / HIGH / MEDIUM / LOW
3. **Affected file/function/state transition**
4. **Exact attack/failure path**
5. **Why existing code/tests do not stop it**
6. **Minimal reproduction or test scenario**
7. **Expected safe behavior**
8. **Recommended fix**
9. **Regression test to add**
10. **Confidence and any assumption**

Also list suspected issues that you cannot prove separately as `NEEDS EVIDENCE` rather than presenting them as confirmed defects.

## Additional tasks

- Identify important missing tests even where you cannot prove a production defect.
- Identify overclaims in the product contract or README, if any.
- Check whether tests accidentally validate mocks/assumptions rather than the actual cross-component contract.
- Rank the **top five attack paths** most likely to produce a false-green or wrong-scope correction.
- Give a final verdict for this frozen MVP only:
  - `KEEP MVP BASELINE`
  - `KEEP WITH REQUIRED FIXES`
  - `REOPEN CORE DESIGN`
  - `BLOCK SYSTEM-LEVEL EXPERIMENTS`

Do not grant release or production authority. The review itself is candidate evidence and will be independently adjudicated.
