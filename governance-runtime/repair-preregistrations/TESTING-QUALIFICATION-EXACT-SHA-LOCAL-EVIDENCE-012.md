# TESTING Qualification Exact-SHA Local Evidence Coverage 012

Status: FROZEN_BEFORE_REPAIR
Authority effect: NONE_EVIDENCE_ONLY
Exposed candidate SHA: `f9615469a2faea8696950974de2182972edf81bf`

## Observed gap

R11-10 requires fresh exact-SHA local and external evidence before fresh independent re-review. The candidate TESTING workflow's push path filter enumerates older governance files and does not include the R11 preservation/preregistration paths that produced `f9615469...`. Consequently the exact merged successor obtained external evidence but did not automatically obtain a local post-merge TESTING run.

## Frozen repair boundary

1. Preserve the absence of exact-SHA local evidence for `f9615469...`; do not reinterpret prior PR-head CI as post-merge exact-SHA evidence.
2. Repair only workflow trigger coverage so future material TESTING governance changes, including repair preregistrations/failure evidence, trigger the local qualification workflow on `phase/testing` pushes.
3. The repair must not weaken test commands, required checks, authority rules, exact-SHA recording, or external governance verification.
4. The workflow-change successor must receive fresh exact-SHA local evidence and fresh exact-SHA external App evidence before independent review.
5. Earlier external PASS evidence remains evidence only and cannot authorize promotion.
6. Unknown or missing required evidence fails closed.
