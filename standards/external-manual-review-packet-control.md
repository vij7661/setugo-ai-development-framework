# External Manual Review Packet Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: ensure an external/manual reviewer can review the exact frozen candidate without requiring repository, GitHub, local filesystem, API, or prior-chat access, and ensure future authority-bearing reviews explicitly test root/meta-governance closure rather than only the immediate subsystem clauses.

## 1. Self-contained packet rule

When an external reviewer does not have verified access to the authoritative repository or source system, the review request must be delivered as a self-contained packet.

The packet must include:

- the exact frozen candidate artifact contents required for review;
- the frozen candidate identifier, commit SHA and/or artifact digest;
- the review scope;
- the complete external review prompt;
- explicit evidence-only / authority limitation;
- any preregistered falsification matrix or acceptance criteria required to evaluate the candidate.

A repository URL, PR number, branch name, file path, or SHA by itself is not sufficient evidence delivery when the reviewer cannot access the repository.

## 2. Prompt accompanies every external review

Every external/manual review request must include the review prompt together with the candidate packet. The prompt must not be supplied only by conversational reference such as “use the previous prompt.”

The prompt must state the reviewer posture, required output structure, scope, and authority effect.

## 3. Exact candidate binding

The packet must identify the exact candidate revision being reviewed. If the candidate changes after packet creation, the packet becomes stale and must not be reused as review evidence for the new candidate.

Any review returned against a stale packet remains evidence only for the exact candidate represented in that packet.

## 4. No hidden dependency on reviewer access

Packet construction must assume the external reviewer has no access to:

- GitHub or repository contents;
- prior ChatGPT conversations;
- local development files;
- connected applications;
- internal APIs;
- other reviewers’ findings.

If any external dependency is required, it must be explicitly included in the packet or the review must be marked `INSUFFICIENT_EVIDENCE` for that dependency.

## 5. Reviewer isolation

For independent reviews, a packet must not contain substantive findings, conclusions, scores, or dispositions from another reviewer unless the governing protocol explicitly defines a cross-review stage.

Status metadata may state that other reviews exist or are pending only when necessary for workflow coordination and without exposing their conclusions.

## 6. Delivery format

Use a directly readable, self-contained file format. Do not package the review packet as a ZIP archive unless the user explicitly requests ZIP.

A single Markdown, text, PDF, or other directly readable document is preferred when feasible.

## 7. Integrity check before delivery

Before presenting the packet, verify:

1. all required candidate files are included in full;
2. the frozen candidate identifier matches the source artifact;
3. the complete review prompt is present;
4. no required content depends on inaccessible links;
5. no prior reviewer findings have contaminated an independent-review packet;
6. authority remains `NONE_EVIDENCE_ONLY` unless a separate qualified governance rule explicitly says otherwise;
7. when the candidate contains or affects authority-bearing behavior, the applicable platform root/meta-governance standard is included in full or its exact required content is otherwise self-contained in the packet;
8. the review prompt explicitly requires root/meta-governance closure attacks rather than merely clause-by-clause review.

## 8. Operating rule

For this project, when the user asks for an external review packet, default to:

`EXACT FROZEN ARTIFACT(S) + COMPLETE REVIEW PROMPT + AUTHORITY LIMITATION`

and assume **NO GITHUB ACCESS** unless access has been explicitly established.

## 9. Platform-wide root/meta-governance closure review requirement

For every future independent review of a candidate that creates, changes, qualifies, interprets, publishes, consumes, or can suppress authority-bearing state, the clean packet and prompt must apply the active platform root/meta-governance closure standard.

At minimum, the reviewer must independently attack:

- root bootstrap/genesis completeness and residual trust assumptions;
- root-kernel or constitutional-rule in-place self-amendment;
- mutation or substitution of the strength predicate/strength contract;
- omission of a new authority-affecting object or policy from governance protection;
- authority dependency cycles, self-parenting, or descendant control over an ancestor;
- caller/candidate/beneficiary/reviewer-subject self-selection or self-qualification;
- rename/reclassification/split/merge/migration identity escape;
- cryptographically valid but non-qualifying, revoked, expired, compromised, wrong-generation, wrong-class, or wrong-bound evidence;
- unsigned or insufficiently bound authority-bearing decision outputs;
- conflict-resolution policy weakening;
- retroactive authorization/scope broadening;
- emergency, recovery, migration, repair, reset, and bootstrap bypasses;
- proof-view omissions that could conceal any of these paths.

The reviewer must not assume a manually enumerated protected-policy list is exhaustive. It must look for additional authority-affecting surfaces functionally and transitively.

If the reviewer cannot determine where governance recursion terminates, cannot inspect the exact terminal trust assumption, or cannot determine whether a material authority cycle/self-grant path exists, the result for that boundary must be `INSUFFICIENT_EVIDENCE`, not PASS.

## 10. Cross-phase applicability

The root/meta-governance closure attack applies to architecture/design review, implementation review, testing/falsification review, qualification review, release/promotion review, and any later governed phase where the reviewed candidate can affect authority.

A PASS from one phase does not waive root/meta-governance closure checks for a later changed candidate or later authority surface. Exact-artifact binding and review freshness still apply.

## 11. Nonclaims

This document does not itself approve the platform root/meta-governance design or any candidate that inherits it. It defines review-packet behavior only.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
