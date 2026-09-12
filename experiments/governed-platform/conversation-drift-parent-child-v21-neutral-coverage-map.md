# WDPC V21 Neutral Coverage Map

Status: **DESIGN MAP — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Exact V20 base: `cbe00858fea092d278772671f2328da2b771ac73`.

This map contains no prior reviewer disposition and grants no authority.

| V21 control | Covered boundary | Primary falsification cases |
|---|---|---|
| V21-C02 | immutable governed-object identity / anti-reclassification | WDPC-327, WDPC-328, WDPC-341 |
| V21-C03 | authority-meta-policy non-weakening | WDPC-335, WDPC-336, WDPC-337, WDPC-340, WDPC-345 |
| V21-C04 | independent reconciliation evaluator / authenticated evidence | WDPC-329, WDPC-330, WDPC-331, WDPC-342 |
| V21-C05 | publication registry integrity / runtime consultation | WDPC-310 (narrowed), WDPC-332, WDPC-333, WDPC-343 |
| V21-C06 | dependency-universe authority independence | WDPC-311 (narrowed), WDPC-334, WDPC-344 |
| V21-C07 | witness-quorum policy anti-weakening | WDPC-335, WDPC-345 |
| V21-C08 | attestation-issuer policy anti-weakening | WDPC-336, WDPC-345 |
| V21-C09 | activation-schema integrity / non-retroactive scope | WDPC-337, WDPC-345 |
| V21-C10 | credential-fingerprint non-reversibility | WDPC-338 |
| V21-C11 | independent-support conflict determinism | WDPC-318 (narrowed), WDPC-339, WDPC-346 |
| V21-C12 | deterministic inherited endpoint semantics | WDPC-310, WDPC-311, WDPC-318 |
| V21-C13 | V21 proof-view additions | reviewability of WDPC-327…346 |
| V21-C15 | deferred boundaries / role neutrality / design freeze | EXP-ECC-6/7 deferred; R1/R2/R3 provider-neutral |

## Precedence

- WDPC-01…326 remain inherited and historically preserved.
- V21 narrows active prospective semantics only for WDPC-310, WDPC-311, and WDPC-318.
- WDPC-327…346 are new V21 cases.
- No historical RED/PASS result or earlier falsification definition is rewritten.

## Unique enforcement-path accounting

The active V21 design requires separate authority-bearing enforcement paths for:

1. governed-object identity and ancestry;
2. root/meta-policy strength comparison;
3. reconciliation-evaluator qualification and evidence authentication;
4. publication-classification registry mutation/runtime consultation;
5. dependency-universe authority independence;
6. witness-quorum policy strength;
7. attestation-issuer policy strength;
8. activation-schema policy integrity;
9. credential-fingerprint scheme qualification;
10. independent-support conflict resolution.

A PASS in one path cannot substitute for another path's missing evidence. Duplicate case coverage does not inflate unique enforcement-path coverage.

## Role neutrality

R1/R2/R3 remain governed roles. Nothing in V21 hardcodes Claude, GPT, Gemini, DeepSeek, or any other provider/model to a role.

## Nonclaims

V21 is design-only. No V21 falsification case has been executed. No live provider/manual-review integration, production trust-root separation, deployment readiness, or terminal authority is claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
