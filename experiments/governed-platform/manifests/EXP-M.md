# EXP-M — Reviewer Blinding, Majority Pressure and Pair Effects

Status: **PRE-REGISTERED / NOT YET SCIENTIFICALLY ADJUDICATED**

## Motivation

Multi-agent review can fail when later reviewers are anchored by prior conclusions, confidence claims, vote counts or correlated model lineage. EXP-M tests whether staged disclosure preserves independent error detection better than immediate shared-consensus context.

## Primary questions

1. Does exposing prior reviewer conclusions before an independent position is frozen increase correlated misses or incorrect-consensus adherence?
2. Does exposing confidence/majority information worsen that effect?
3. Do reviewer-target model-family pairs show materially different review performance?
4. Can staged disclosure preserve useful adjudication while reducing anchoring?

## Arms

- **M0 — Blinded independent review**: requirements + case + frozen artifact only; no prior conclusions/confidence/votes.
- **M1 — Prior conclusion visible**: prior reviewer conclusion disclosed before independent position.
- **M2 — Prior conclusion + confidence visible**.
- **M3 — Prior conclusion + majority/vote signal visible**.
- **M4 — Staged disclosure**: reviewer first freezes an independent position; then receives frozen prior reviews for explicit adjudication.
- **M5 — Same-lineage/correlated reviewer control**.
- **M6 — Different-lineage reviewer control**.

## Mandatory case families

- incorrect R1 consensus that a later reviewer can correct;
- correct minority reviewer facing incorrect majority;
- clean case where dissent would be false positive;
- same-foundation reviewers exposed as nominally separate providers;
- different-lineage reviewers;
- high-confidence wrong prior reviewer;
- low-confidence correct prior reviewer;
- reviewer-target pair reversal (A reviews B; B reviews A);
- material vs non-material disagreement;
- ambiguous requirement where no reviewer majority may create authority.

## Staged-disclosure rule

Before a reviewer freezes an independent position, context may contain authoritative requirements, project context, the exact frozen artifact and evidence explicitly permitted by policy. It must not contain:

- prior reviewer final conclusions;
- prior reviewer confidence scores;
- vote/majority counts;
- private chain-of-thought/reasoning;
- protected ground truth.

After the independent position is hash-frozen, prior **final** reviews may be disclosed for adjudication. Private reasoning and protected truth remain forbidden.

## Metrics

- true defect discovery;
- false-positive rate;
- correlated miss rate;
- incorrect-consensus adherence;
- correct-minority preservation;
- position switching before/after disclosure;
- reviewer-target pair performance;
- same-lineage vs different-lineage marginal detection;
- cost/latency impact of staged disclosure.

## Decision discipline

Reviewer agreement is evidence only. The experiment must not treat consensus as ground truth. Protected/external adjudication determines whether switching was corrective or harmful.
