# V15 Manual Independent Evidence Review — Partial 001

Status: **PARTIAL / INSUFFICIENT_TO_ASSESS / CRITICAL FINDING PRESENT**

This record preserves the manually returned independent review verbatim in substance. It has no authority effect.

## Reviewer output

A. `CONTENT_BINDING = CONSISTENT` (internal only)

All 30 `candidate_files` in `PACKAGE-MANIFEST.json` match their listed `sha256` and `git_blob_sha1` exactly when recomputed locally. This proves the package is internally self-consistent — it does *not* prove these are really the files at commit `380e1d9d…` in `vij7661/setugo-ai-development-framework`, since the reviewer had no network access to the origin repo and the package contains no signed/independently-witnessed commit object.

B. `CRYPTOGRAPHIC_RECOMPUTATION = INSUFFICIENT_TO_ASSESS`

Blob hashes check out, but tree/commit-level recomputation against the real repo was not possible offline, and nothing in the package independently attests "these bytes = what GitHub has" other than the package's own manifest.

C. `IMPLEMENTATION_SCOPE = INCOMPLETE (for this review)`

All 30 files compile cleanly (`py_compile`, zero errors). The reviewer read 2 of 9 runtime modules in depth (`_authority.py`, `_effects.py`) plus the shared core (`review_safe_evidence_v15.py`); the reviewer did not do adversarial-depth reads of `_evidence.py`, `_governance.py`, `_monitors.py`, `_projection.py`, `_review.py`, `_universe.py`, the schema registry, or the workflow YAMLs, nor execute any test.

D. Overall = `INSUFFICIENT_TO_ASSESS`

The reviewer declined to issue `IMPLEMENTATION_BOUNDED_PASS` on a partial read without test execution.

## Critical finding reported

The reviewer identified a load-bearing authenticity gap: `record_digest`, `registry_digest`, `token_digest`, and `issuance_digest` are computed as SHA-256 over caller-supplied records with the digest field omitted, without HMAC/asymmetric authentication or an externally anchored authority object enforced within the reviewed validators. The reviewer specifically flagged caller-controlled fields such as `candidate_controlled`, `self_qualified_by_descendant_machinery`, and `effect_fenceable` as potentially self-asserted because the same caller can construct the record and recompute its digest.

The reviewer stated that this may be intentional at construction stage because `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`, but that any future authority-bearing use depends on an out-of-band trust anchor not established by the reviewed package.

## Reviewer continuation request

The reviewer offered to continue module-by-module and asked whether to inspect `_monitors.py` or `_governance.py` next.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
