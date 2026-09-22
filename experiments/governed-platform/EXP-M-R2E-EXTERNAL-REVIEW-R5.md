# Independent External Static Review — EXP-M R2E — R5

Reviewer channel: DeepSeek no-Git static review

Preservation note: The review below is preserved verbatim from the independent reviewer response. Git/runtime provenance limitations stated by the reviewer remain part of the record.

A. Overall disposition: **CHANGES_REQUIRED**

Static review found material false-green paths remaining in the supplied source snapshot. The supplied PASS labels and self-verifiers cannot be accepted as closure evidence. Git-dependent provenance claims remain unverified.

B. Critical findings

1. **Ambient source-freeze state remains authoritative in the authority/expectation loader.**
   - `source/governance-runtime/exp_m_expectation_authority.py`
   - `AuthorityHandle._source_freeze()` reads `ROOT / "experiments" / "governed-platform" / "EXP-M-SOURCE-FREEZE.json"` from the ambient filesystem.
   - `resolve_reviewed_commit()`, `resolve_reviewed_tree()`, and `expected_delivery()` consume that ambient file.
   - `load_predicate_context()` calls `resolve_reviewed_commit()` / `resolve_reviewed_tree()`.
   - `authority_context_valid()` calls those methods again.
   - `evaluate_admissibility()` relies on `authority_context_valid()`.
   - Impact: an attacker who can alter the on-disk `EXP-M-SOURCE-FREEZE.json` (and matching working-tree source files) can redirect the production authority’s expected reviewed commit / delivery binding. The S-E-P-Q verifier reads the freeze from the E Git object, but production admissibility reads the working tree. This is a split-brain false-green path and was not remediated by R4.

2. **Self-falsification suite overrides context and authority, so many cases do not test what they claim.**
   - `source/governance-runtime/self_falsify_exp_m.py`
   - `def context_from_state(_state): return AUTHORITY_CONTEXT`
   - `def evaluate_admissibility(bundle, context=None, registry=None): return _production_evaluate_admissibility(bundle, AUTHORITY_CONTEXT, registry, authority=AUTHORITY)`
   - Cases such as `self_derived_context`, `forged_delivery_result`, `witness_without_expected_answer`, and `accessibility_valid_only` pass `context_from_state({...})` or no context, but `evaluate_admissibility` ignores the supplied context and always uses `AUTHORITY_CONTEXT`.
   - Impact: the self-falsification suite can report `rejected: true` without exercising the intended context/authority attack. This is a critical false-green in self-falsification evidence.

3. **The test-integrity gate is bypassable.**
   - `source/governance-runtime/verify_exp_m_test_integrity.py`
   - `_method_calls()` and `REQUIRED_CALLS` only check that required function names appear in the CA test AST. They do not require assertions, rejection checks, or actual attack failure.
   - `source/governance-runtime/run_reviewer_compound_attacks.py`
   - `CaptureResult.addSuccess()` records `{"rejected": True}` for any test that passes.
   - Impact: an authoritative CA test could call the required production function but omit assertions; `unittest` would pass, and the compound runner would mark the attack rejected. The integrity gate would not detect this.
   - Additionally, `_shortcut_references()` only inspects `ast.Name`, `ast.Attribute`, and `ast.Call`. It ignores string constants. A call such as `getattr(authority, "with_missing_r5_protocol_for_test")()` would evade the forbidden-shortcut scan.

C. High findings

1. **`verify_reviewer_suite_frozen()` does not self-bind `source_files` to `source_commit`.**
   - `source/governance-runtime/verify_exp_m_sep_sequence.py`
   - The function uses `source_files.get(path)` as the expected hash and compares it to `_git_bytes(source_commit, path)`.
   - It does not require that `source_files` were derived from `source_commit`.
   - CA-8 in `reviewer_exp_m_r2e_mechanism_suite.py` passes original `source_files` with `source_commit=mutant`, so it detects drift. But the verifier function itself is not self-contained; it relies on the caller to bind the map correctly.

2. **CA-7/CA-8 real-path execution cannot be independently verified from static text alone.**
   - `source/governance-runtime/reviewer_exp_m_r2e_mechanism_suite.py`
   - `_synthetic_commit()` uses Git plumbing (`read-tree`, `update-index`, `write-tree`, `commit-tree`).
   - Without Git execution, the synthetic commits, strict-ancestor checks, and deletion/mutation detection cannot be independently reproduced.

3. **Mutation harness uses isolated subprocesses, but static review cannot prove runtime isolation or absence of shared state.**
   - `source/governance-runtime/run_exp_m_mutations.py`
   - `isolated_mutant_result()` uses `pickle` and a subprocess worker.
   - `_mutated_evaluate()` monkey-patches `production._predicate_validators`.
   - Statically this is better than same-process mutation, but execution integrity remains unverified without Git/runtime.

D. Medium findings

1. **`verify_exp_m_sep_sequence.py` still contains Git-dependent checks that cannot be validated in no-Git mode.**
   - `_is_strict_ancestor()`, `_git_bytes()`, `_diff_paths()`.
   - These are packet assertions for this review.

2. **`exp_m_expectation_authority.py::_source_freeze()` allows a missing working-tree file if the Git object exists.**
   - It checks `working.exists() and _sha256(...) != expected`.
   - If a working-tree file is absent, it does not fail. This may be benign for clean-checkout verification, but it weakens the ambient-binding check.

3. **`run_reviewer_compound_attacks.py` treats any passing CA test as a rejected attack.**
   - It does not distinguish “test passed because attack was rejected” from “test passed because the test made no meaningful assertion.”

E. Reproduction / static proof for every material finding

1. **Ambient authority source-freeze**
   - File: `source/governance-runtime/exp_m_expectation_authority.py`
   - Function: `AuthorityHandle._source_freeze`
   - Evidence:
     ```python
     path = ROOT / "experiments" / "governed-platform" / "EXP-M-SOURCE-FREEZE.json"
     if not path.exists():
         return None
     data = json.loads(path.read_text(encoding="utf-8"))
     ```
   - Used by:
     ```python
     def resolve_reviewed_commit(self) -> str:
         freeze = self._source_freeze()
         if freeze is not None:
             return str(freeze["source_commit"])
     ```
   - Used by:
     ```python
     def resolve_reviewed_tree(self) -> str:
         freeze = self._source_freeze()
         if freeze is not None:
             return str(freeze["source_tree"])
     ```
   - Used by:
     ```python
     def expected_delivery(self, request_id: str) -> Mapping[str, Any]:
         ...
         freeze = self._source_freeze()
         ...
     ```
   - Called from `load_predicate_context()` and `authority_context_valid()`.

2. **Self-falsification context override**
   - File: `source/governance-runtime/self_falsify_exp_m.py`
   - Functions:
     ```python
     def context_from_state(_state):
         return AUTHORITY_CONTEXT
     ```
     ```python
     def evaluate_admissibility(bundle, context=None, registry=None):
         return _production_evaluate_admissibility(bundle, AUTHORITY_CONTEXT, registry, authority=AUTHORITY)
     ```
   - Example case:
     ```python
     case("self_derived_context",
          not evaluate_admissibility(
              bundle_from_state({"review_request": {"current": True, "request_id": "attacker"}, "disposition": "PASS"}),
              context_from_state({"expected_request_id": "r"})
          ).admissible)
     ```
   - The supplied `context` argument is ignored.

3. **Test-integrity bypass**
   - File: `source/governance-runtime/verify_exp_m_test_integrity.py`
   - `_method_calls()` extracts only call names.
   - `REQUIRED_CALLS` only checks presence of call names.
   - `_shortcut_references()`:
     ```python
     if isinstance(node, ast.Call):
         names.append(_call_name(node))
     elif isinstance(node, ast.Name):
         names.append(node.id)
     elif isinstance(node, ast.Attribute):
         names.append(node.attr)
     ```
     It does not inspect `ast.Constant` string values.
   - File: `source/governance-runtime/run_reviewer_compound_attacks.py`
     ```python
     def addSuccess(self, test):
         super().addSuccess(test)
         self.case_outcomes[self._name(test)] = {"rejected": True}
     ```

4. **CA-8 source_files binding**
   - File: `source/governance-runtime/verify_exp_m_sep_sequence.py`
   - `verify_reviewer_suite_frozen()`:
     ```python
     expected = source_files.get(path)
     ...
     actual = hashlib.sha256(source_bytes).hexdigest()
     if actual != expected:
         reasons.append("reviewer_suite_hash_drift")
     ```
   - No check that `source_files` itself is bound to `source_commit`.
   - File: `source/governance-runtime/reviewer_exp_m_r2e_mechanism_suite.py`
   - `test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier` builds `source_files` from `self.source` but passes `source_commit=mutant`.

F. Previous R3 findings disposition

- **CA-7**: **CLOSED** statically. Current `test_ca7_real_deleted_indexed_artifact_reaches_unmodified_prior_verifier` uses `_synthetic_commit()` to delete an indexed artifact and calls `verify_prior_evidence_index()` without a `simulate_*` flag. Runtime/Git execution remains unverified.
- **CA-8**: **CLOSED** statically for the simulated-mutation defect. Current CA-8 uses `_synthetic_commit()` to mutate a reviewer suite and calls `verify_reviewer_suite_frozen()` without `simulate_suite_mutation`. However, the verifier’s reliance on caller-supplied `source_files` is a residual high finding.
- **Ambient reviewer-suite state**: **PARTIALLY_CLOSED**. `verify_reviewer_suite_frozen()` no longer reads `FREEZE_PATH` and now takes explicit `source_commit` and `source_files`. But the authority/expectation loader still reads ambient `EXP-M-SOURCE-FREEZE.json` in `exp_m_expectation_authority.py`, which is a critical remaining ambient-state false-green.
- **Simulated outcome shortcuts**: **PARTIALLY_CLOSED**. CA-7/CA-8 no longer use legacy simulation flags. But the test-integrity gate can be bypassed by omitting assertions or using string-based dynamic calls, so shortcut detection is not closed.
- **Positive controls**: **CLOSED** statically. `verify_exp_m_test_integrity.py` runs positive controls for `reviewer_suite_frozen` and `prior_evidence_index` before accepting negative CA-7/CA-8 evidence.

G. Newly discovered false-green paths

1. Ambient `EXP-M-SOURCE-FREEZE.json` consumption in `exp_m_expectation_authority.py` can redirect production expected reviewed commit / delivery binding.
2. `self_falsify_exp_m.py` forces `AUTHORITY_CONTEXT` and ignores caller-supplied contexts, invalidating many self-falsification cases.
3. `verify_exp_m_test_integrity.py` does not require assertions or actual rejection behavior in authoritative CA tests.
4. `_shortcut_references()` ignores string-based dynamic access, so forbidden shortcut tokens can be invoked via `getattr(..., "with_missing_r5_protocol_for_test")()`.
5. `run_reviewer_compound_attacks.py` marks any passing CA test as a rejected attack without verifying that the test actually asserts rejection.

H. Provenance limitations caused by no Git access

- I did not have Git access and could not execute the nested Git bundle.
- I could not independently verify:
  - Git ancestry of S, E, P, Q, authority, or reviewer-suite preregistration commits;
  - commit/tree identities;
  - changed-path constraints between S→E, E→P, P→Q;
  - Git blob identities;
  - that supplied files truly came from claimed Git objects;
  - strict-ancestor checks;
  - synthetic Git commit creation in CA-7/CA-8;
  - the RSA signature verification over the authority test-expectation manifest;
  - execution of any test, verifier, mutation runner, or self-falsification command.
- All Git-dependent provenance claims remain packet assertions only.
- My static findings are based solely on the supplied textual source snapshot.

I. Final bounded statement

EXP-M = NOT_QUALIFIED
Authority effect = NONE
Live provider/API execution = false / unauthorized
