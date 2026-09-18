# V24-I11-V6 Successor-3 — Independent Review Adjudication

Status: **CHANGES_REQUIRED / SCIENTIFIC EXECUTION REMAINS CLOSED**

Reviewed subject:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-3`
- commit: `b4b91dcf5855ae2bb7162c0b94d1a79a8a64e171`
- tree: `a81204c73016243556c6eefd711bc91c37adda49`
- exact final-head run: `35072181274`
- raw independent review preserved verbatim in `review/v24/V24-I11-V6-SUCCESSOR-3-FINAL-INDEPENDENT-MANUAL-REVIEW.md`

## Adjudication

### PRC-1 — CONFIRMED / CRITICAL / BLOCKING

The successor-3 repair changed the root check from a boundary derived directly from the proof context to an environment-provided SHA-256 anchor. That remains self-grantable by a caller in the same process:

1. construct an arbitrary valid-looking proof context and trusted boundary;
2. compute `trusted_boundary_anchor_digest(attacker_boundary)` using exported production code;
3. assign that digest to `V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256`;
4. call the normal production resolver.

Independent reproduction against the exact frozen package returned:

```text
qualified = True
state = PROOF_REFERENCE_CLOSED
problems = []
```

The existing successor-3 regression only restores the old anchor before testing the forged boundary, so it proves stale-anchor mismatch rejection but does not test same-process anchor replacement.

The approved V6 design requires exact genesis/root artifacts and a durable anchor. A mutable caller-set environment digest is not an independently anchored root.

### DA-1 — LOCAL REPAIR CONFIRMED; SYSTEMIC CLOSURE BLOCKED BY PRC-1

The successor-3 decision digest now binds:
- exact authorized effect path ID;
- exact effect-path content digest;
- exact effect class.

Apply-time target substitution with stale qualification is rejected. No independent DA-1 tuple/join defect was reproduced after the local repair.

However, the qualification covering the repaired decision digest is resolved through PRC-1. A caller that self-grants the root can mint a new qualification for an attacker-selected decision/path pair. Therefore DA-1 cannot be considered systemically closed until PRC-1 is closed.

### NCP-1 — LOCAL REPAIR CONFIRMED; SYSTEMIC CLOSURE BLOCKED BY PRC-1

The successor-3 catalog-control binding digest now covers the exact clause/control/artifact/span tuple, and a stale proof cannot authorize a changed `control_id`.

However, the fresh qualification required for the new tuple is also resolved through PRC-1. A caller that self-grants the root can mint a qualification over an unauthorized clause→control mapping. Therefore NCP-1 cannot be considered systemically closed until PRC-1 is closed.

## Required successor-4 repair property

The next repair MUST NOT use:
- a caller-writable environment variable;
- a caller-supplied digest;
- a candidate-supplied trusted-boundary object;
- a same-address-space secret/MAC key available to candidate Python;
- documentation-only separation.

The authority-bearing root/anchor decision must come from a trust boundary that candidate/caller Python cannot mint or rewrite. The existing R14/R16 design line already captures the required architectural principle: trusted observation/authority material must be derived outside candidate mutable Python state/address space, and no authority secret may exist in candidate-readable memory.

At minimum, the permanent regression must demonstrate that:
- the attacker constructs the context and boundary;
- the attacker computes the matching digest;
- the attacker rewrites the old environment anchor to that matching digest;
- the production authority path still rejects the context.

A repair that merely renames the environment variable, moves the digest helper, or pins another caller-mutable value is insufficient.

## Historical preservation

Preserve without reclassification:
- successor-2 manual review: CHANGES_REQUIRED;
- `35070903107`: genuine pre-successor-3 RED;
- `35071250976`, `35071608899`: tooling/preflight failures only;
- `35071757663`, `35071849800`, `35072081665`, `35072181274`: genuine GREEN for the tests they executed, but not evidence against the newly exposed self-updating-anchor attack.

## Authority boundary

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_EXECUTION = CLOSED_PENDING_SUCCESSOR_REVIEW`
