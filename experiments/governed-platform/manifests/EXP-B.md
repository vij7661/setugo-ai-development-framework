# EXP-B — Semantic False-Green

Status: **PRE-REGISTERED PILOT — NOT YET RUN**

## Hypothesis

Preserved source intent plus structured constraints/invariants and boundary examples can detect cases where implementation, tests, and CI are internally green but encode the wrong behavioral interpretation.

## Required case families

- R' differs from R.
- R' is narrower than R (under-permission/over-restriction).
- R' is broader than R (over-permission/under-restriction).
- Inclusive/exclusive boundary ambiguity.
- Terminology substitution hiding an invariant conflict.
- Omitted condition or exception.
- Test-input selection that hides semantic divergence.

## Arms

A. Technical contract + code/tests only.

B. Preserved original intent + technical contract.

C. Preserved intent + structured constraint/invariant representation + examples/counterexamples + independent semantic challenge.

## Primary outcomes

- Semantic divergence detected before acceptance.
- False-green accepted despite R != R'.
- False-positive semantic blocker when behavior is actually consistent.

## Secondary outcomes

- Cost, latency, model/tool calls.
- Which semantic defect families remain systematically missed.
- Whether the extra interpretation controls add independent information or merely repeat the same misunderstanding.

## Ground truth

The intended behavior and controlled divergence must be established independently of the system under evaluation. Human/domain adjudication is acceptable for pilot ground truth but must be recorded and separated from model-visible inputs.
