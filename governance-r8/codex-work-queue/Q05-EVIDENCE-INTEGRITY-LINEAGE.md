# Q05 — Evidence bundle integrity, lineage and closure tooling

## Global execution rules

- Base truth is the SG-1 bounded closure at commit `7cd2787d85b189a4161f271ee131e42bd961140a`.
- Do not weaken existing tests, governance oracles, authority boundaries, failure preservation, exact-SHA binding, or independent-review requirements.
- Do not grant runtime/release/deployment/production/policy/constitutional/root/terminal authority.
- Do not restore six-slice cadence automatically; fallback-to-3 remains ACTIVE unless a separately authorized human action changes it.
- Preserve all RED/failure history.
- Add deterministic tests for every new mechanism and negative/bypass tests for every load-bearing guard.
- Keep changes scoped to this PR. If a prerequisite requires human approval/review/credentials/external infrastructure, implement everything possible up to that boundary, record `MANUAL_INTERVENTION_REQUIRED` with exact reason/evidence, and do not wait.
- Never stop the overall work queue because this PR is blocked; the master Codex queue must continue to the next PR.
- Do not merge the PR. Leave it ready for later human review.


## Objective

Close recurring evidence-packaging weaknesses surfaced by SG-1 reviews and make future gates easier to audit.

## Required coding

1. Add per-file SHA-256 digests for uploaded result artifacts, not only archive digest.
2. Add a reusable verifier that binds:
   - run ID/job ID;
   - workflow/head SHA;
   - exact input blobs;
   - exact output-file hashes;
   - artifact archive digest;
   - authority boundary.
3. Preserve and surface activation-verification evidence in post-run packets.
4. Reconcile/document the Stage1 `changed_paths=121` vs `reviewed_allowlisted_entries=120` accounting in deterministic code/evidence.
5. Make execution-evidence summaries self-identifying by including their own externally computed Git blob/raw hash in the containing closure/packet where circularity permits; document self-hash boundaries where not possible.
6. Add generic packet builders and consistency verifiers so future gates do not duplicate hand-coded evidence assembly.
7. Add corruption/staleness/substitution negative tests.

## Done when

- A future reviewer can deterministically verify every included evidence file and its lineage.
- Known SG-1 Low traceability findings have machine-checkable treatment without rewriting historical reviews.
