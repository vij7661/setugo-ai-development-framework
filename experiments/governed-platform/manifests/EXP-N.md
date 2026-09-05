# EXP-N — Claim-Level Review Targeting and Context Reduction

Status: **PRE-REGISTERED / DEFERRED UNTIL EXP-L AND EXP-M PILOTS**

## Motivation

Long-form semantic-uncertainty work shows that whole-paragraph resampling can confuse harmless ordering/wording variation with uncertainty. A more useful unit is often an individual factual or decision proposition. This also aligns with the product goal of reducing reviewer tokens later.

## Primary question

Can the platform decompose a long Reviewer-1 artifact into bound semantic claims and focus Reviewer 2 on high-risk, uncertain, contradictory or evidence-poor claims while preserving material defect detection relative to full-context review?

## Arms

- **N0 — Full artifact review:** R2 receives the complete authorized context and full frozen artifact.
- **N1 — Naive summary:** compressed summary only; expected negative control for omission risk.
- **N2 — Claim-targeted + full artifact available:** authoritative context + claim index + prioritized review targets + exact full-artifact reference/access.
- **N3 — Claim-targeted only:** targeted claims with no full artifact; adversarial control to measure hidden-interaction/omission failures.

## Mandatory safety rules

1. Claim decomposition is a routing/indexing aid, not authority.
2. Every claim must bind to the exact frozen artifact hash and source span/reference.
3. Authoritative requirements/invariants are never removed by token reduction.
4. HIGH/CRITICAL review keeps the full artifact available even when a focused target list is supplied.
5. The reducer may prioritize claims but may not mark omitted claims as verified.
6. Cross-claim interactions must be testable; a defect may exist only in the combination of individually plausible claims.
7. Reviewer 2 must be allowed to report findings outside the prioritized target list.
8. Reduction quality is scored against protected/full-context review, not against token savings alone.

## Mandatory case families

- lexical variants that mean the same thing;
- one unstable proposition inside an otherwise stable long artifact;
- low-uncertainty claim that is nevertheless wrong;
- defect caused by interaction between two claims;
- omitted requirement not represented in R1 claims;
- clean long artifact where targeting should save tokens without creating false positives;
- misleading naive summary;
- reviewer finding outside the target list;
- stale claim index bound to an old artifact hash.

## Metrics

- true material findings retained vs N0;
- false-green rate;
- findings uniquely lost by reduction;
- findings outside target list;
- claim-index precision/recall against independently adjudicated propositions;
- input/output tokens;
- latency and cost;
- cost per retained/additional true finding;
- compression ratio at fixed protected correctness.

## Decision discipline

Token reduction is successful only if it preserves the required protected quality floor. A cheaper arm with higher false-green or omission rate is false efficiency. No production compression threshold is declared before pilot data.
