# V24-I11-V6-R12 — Mandatory Adversarial Evidence Contract

Status: **CONSTRUCTION-ONLY / EXTERNAL EVIDENCE REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

The legacy `mandatory_v6_adversarial_checks` string list remains only an expected-universe declaration. It is not execution evidence and cannot satisfy integrated-successor validity by itself.

For every required adversarial check, R12 requires exactly one externally supplied record bound to:

- exact check ID;
- exact candidate commit;
- exact candidate tree;
- exact environment/interpreter contract digest;
- exact run ID;
- exact round ID;
- `terminal_state = EXECUTED`;
- `result = PASS`;
- execution evidence digest;
- producer identity;
- independent witness identity;
- `authority_origin = EXTERNAL_REVIEW_BRANCH`;
- `candidate_self_authored = false`;
- `currentness_state = CURRENT`;
- recomputable record digest.

Missing, duplicate, unknown, stale, replayed, cross-candidate, cross-tree, cross-environment, cross-run, cross-round, self-authored, non-executed, non-PASS, or digest-mismatched records fail closed.

The integrated successor binding digest commits to the normalized evidence records and their binding digest. The validator remains construction evidence only and always returns `qualified = false`.

Scientific execution remains `CLOSED_PENDING_R12_SUCCESSOR_REVIEW`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
