# EXP-M R2E Internal Adjudication R3

Status: **REMEDIATED_PENDING_FRESH_GREEN_CHAIN**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This is an additional adversarial internal adjudication loop requested after the R2 remediation reached a green preflight. It does not replace independent external review and cannot grant qualification.

## IA-R3-01 — Candidate-selectable authority root / missing temporal preregistration proof

Severity: **Critical**

### Failure path

The candidate source contained `DEFAULT_AUTHORITY_COMMIT`, while the S-E-P verifier also contained a matching authority-root constant. The preregistered reviewer-authority suite exercised `load_default_authority()` but did not itself freeze the exact permitted authority-root commit. A coordinated candidate change could therefore redirect both loader and verifier to a candidate-selected historical Git object while preserving self-consistency.

The verifier also compared reviewer-suite bytes to named preregistration commits but did not require those commits to be strict ancestors of source S. A candidate could therefore point a "preregister" anchor at S itself or at a non-prior object.

### Remediation

1. Created authority root v3 at immutable commit:
   `f0792cc01915eb3accd893aba2ed107bed9ec560`.
2. Root v3 removes reviewer-suite back-pointers, avoiding circular trust. It states that reviewer suites are preregistered separately after the root and before candidate S.
3. Created reviewer-authority preregistration commit:
   `aae96510eb1ac05b45b961b62a5ea2b010ad6b32`.
4. That preregistered suite contains the literal:
   `EXPECTED_AUTHORITY_ROOT_COMMIT = "f0792cc01915eb3accd893aba2ed107bed9ec560"`
   and tests that both `DEFAULT_AUTHORITY_COMMIT` and the loaded authority handle equal it.
5. The S-E-P-Q verifier requires:
   - current reviewer-authority suite bytes equal the preregistered suite bytes;
   - the suite literal equals the verifier's preregistered root;
   - every reviewer-suite preregistration commit is a strict ancestor of S;
   - authority root v3 is a strict ancestor of the reviewer-authority preregistration commit;
   - authority root v3 is a strict ancestor of S.
6. Current candidate loader, source-freeze generation, packet builder, portable-bundle builder and S-E-P-Q verifier all consume authority root v3.

Adjudication: **REMEDIATED_IN_DESIGN; requires fresh green evidence and independent review.**

## IA-R3-02 — Unfrozen local dependency / dynamic-load provenance bypass

Severity: **High**

### Failure path

The source freeze selected EXP-M-named Python files plus explicit files. The reproducibility import audit classified repository-local imports as "local" but did not require every imported local module to be present in the source-freeze map. A candidate could move load-bearing logic into a differently named local Python module, import it, and influence evidence while the helper remained outside the frozen source set.

Likewise, a non-literal `__import__` / `importlib.import_module` or dynamic `eval` / `exec` path could evade the static import closure. Top-level evidence commands also recorded their script hash but the verifier did not require that command source path itself be in the source-freeze map.

### Remediation

1. Reproducibility audit now maps local module names to repository paths and records `unfrozen_local_imports`.
2. Evidence generation fails closed if any imported local Python module is not in the source-freeze set.
3. Literal `__import__("module")` calls are included in the dependency set.
4. Non-literal `__import__` and `importlib.import_module` calls fail closed as `dynamic_import_not_statically_bound`.
5. `eval` and `exec` calls in the governed source surface fail closed as `dynamic_code_execution_not_allowed`.
6. S-E-P-Q verification requires every captured evidence-command `command_source_path` to be present in `EXP-M-SOURCE-FREEZE.json` and requires the source-freeze hash, capture hash and Git S hash to agree.
7. Offline CI now creates adversarial temporary local modules and proves:
   - an unfrozen local import is detected;
   - a non-literal dynamic import is detected;
   - same-commit "preregistration" is not considered a strict ancestor;
   - the authority root is a strict ancestor of the candidate.

Adjudication: **REMEDIATED_IN_DESIGN; requires fresh green evidence and independent review.**

## IA-R3-03 — Remediation implementation defect found by the loop

Severity: **Implementation defect, fail-closed**

During the first post-remediation offline run, the new command-source provenance check referenced `source_files` before binding it from the evidence source-freeze artifact. The verifier crashed with `NameError` rather than yielding a false PASS.

Remediation:
- `verify_exp_m_sep_sequence.py` now binds and validates `source_files = freeze["source_files"]` immediately after loading the E source-freeze artifact.
- Missing/empty source-file maps are explicit verification failures.

Adjudication: **FIXED; no false green occurred.**

## R3 closure rule

This internal adjudication is not a PASS authority. Closure of R3 requires:
1. latest offline falsification run succeeds on the exact post-R3 source;
2. local S -> E -> P -> Q construction and explicit verification succeed;
3. portable review bundle and nested Git-object verifier succeed outside the repository worktree;
4. no live provider/API execution occurs;
5. after final source freeze, a fresh governed remote S -> E -> P -> Q sequence is produced;
6. the resulting bundle is sent to an independent external reviewer.

Until independent review:
- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized
