# EXP-L — Adaptive Review Triggering with Semantic Uncertainty

Status: **PRE-REGISTERED / NOT YET SCIENTIFICALLY ADJUDICATED**

## Research basis

EXP-L is motivated by two complementary findings:

1. Semantic-entropy work shows that within-model uncertainty is better assessed over **meanings** than lexical/token variation, and that a discrete black-box approximation can be estimated from repeated outputs grouped by semantic equivalence. It also explicitly does **not** solve stable/systematic wrong answers.
2. Conditional cross-model verification work suggests an inexpensive uncertainty stage can be used to decide when a second verifier is worth calling, rather than verifying every output.

The governed-platform hypothesis goes further: semantic instability is only one signal. Risk, materiality, evidence completeness, invariant conflict, reviewer qualification and authority remain platform-owned constraints.

## Primary question

Can platform-owned semantic uncertainty and counterfactual-instability signals reduce unnecessary independent reviews while preserving protected correctness relative to always-review baselines?

## Arms

- **L0 — R1 only**: no uncertainty probe, no independent reviewer.
- **L1 — Self-report**: R1 self-reported confidence only.
- **L2 — Semantic probe only**: repeated black-box R1 generations clustered by semantic meaning; no R2.
- **L3 — Semantic probe → conditional R2**: R2 called only when semantic/refusal/counterfactual signal crosses the pre-registered policy threshold, except governance overrides.
- **L4 — Always R1+R2**: independent R2 for every eligible case.
- **L5 — Conditional R2 → adaptive R3**: R2 as in L3; R3 only for material disagreement/revision/high finding/independence policy.
- **L6 — Always R1+R2+R3**: cost/quality upper-comparison arm, not presumed optimal.

## Mandatory case families

1. unstable + wrong R1;
2. stable + wrong R1;
3. stable + correct R1;
4. lexical variation but same semantic answer;
5. subtle semantic difference that materially matters;
6. refusal/unknown-dominant samples;
7. counterfactual perturbation exposes brittle conclusion;
8. low semantic uncertainty on HIGH-risk task (must still review by governance policy);
9. R2 adds a true material finding;
10. R2 adds only false positives;
11. R3 overturns an incorrect R1/R2 consensus;
12. R3 makes a correct result worse;
13. ambiguous authoritative requirement (must not be resolved by model consensus);
14. qualified-reviewer unavailable/provider failure.

## Semantic-probe protocol

- Sample multiple black-box R1 outputs under a frozen prompt/case binding.
- Do not use lexical difference as disagreement.
- Cluster outputs by context-sensitive semantic equivalence.
- Compute a discrete empirical distribution over semantic clusters.
- Compute normalized Shannon entropy over cluster proportions.
- Track refusal/unknown/unclear samples separately.
- Thresholds are **versioned policy inputs**. The harness must not invent production thresholds from intuition.
- A low semantic-uncertainty score is never evidence of truth and never overrides a policy-required independent review.

## Counterfactual cross-examination

For selected arms/cases, ask controlled perturbations such as:

- what evidence would falsify the current classification?
- if the competing classification were true, what evidence should exist?
- assume one disputed premise is false; does the conclusion change?

Counterfactual instability is a review-trigger signal, not authority.

## Metrics

- protected false-green rate;
- missed required R2 escalations;
- unnecessary R2 escalations;
- R2 marginal true findings;
- R2 false-positive rate;
- R3 marginal true findings / harmful reversals;
- semantic-probe AUROC/AURAC-style discrimination where ground truth supports it;
- escalation accuracy as increasingly uncertain cases are routed away from R1-only finalization;
- total calls, input/output tokens, latency and cost;
- cost per additional independently adjudicated true finding;
- stable-wrong rate (critical limitation metric).

## Decision discipline

No scientific PASS threshold is declared before pilot effect-size and calibration data exist. A pilot may be directional/inconclusive/failed. Any semantic threshold used in a pilot must be retained with policy version, case bindings and raw samples.

## Non-authority rule

Semantic entropy, self-confidence, cross-model agreement and reviewer count are evidence signals only. They cannot create release, mutation or completion authority.
