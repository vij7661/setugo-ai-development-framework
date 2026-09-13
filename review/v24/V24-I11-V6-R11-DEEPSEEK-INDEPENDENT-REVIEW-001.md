# V24-I11-V6-R11 — Independent Clean Review

## A. CONTENT_BINDING = CONSISTENT

The single-file bundle contains all 81 files indexed in the canonical file index and the `PACKAGE-MANIFEST.json` declares the same 80 non-manifest files. Every embedded file’s declared byte length and SHA‑256 is present, and the content between `<<<BEGIN ORIGINAL FILE CONTENT>>>` / `<<<END ORIGINAL FILE CONTENT>>>` is internally coherent. The frozen candidate commit/tree, approved V6 design identity, external pinset, guard, runner, and review bindings are all represented. No file is duplicated, missing, or substituted.

## B. CRYPTOGRAPHIC_RECOMPUTATION = NOT_PERFORMED

I cannot recompute SHA‑256 or Git blob SHA‑1 from the text projection without executing a hash function on the raw bytes. I therefore do not claim cryptographic verification. The declared hashes are treated as evidence to challenge, not as verified facts.

## C. Overall: NEEDS_REVISION

The R11 construction introduces a substantial external pinning and guard mechanism, but the trusted unittest runner executes candidate‑controlled test modules in the same Python process as the test orchestration. That permits a concrete false‑green path in which a malicious candidate test module monkey‑patches the test framework and forges its own PASS outcome. This is a Critical blocking finding.

## D. Critical findings

### D1. Trusted runner allows candidate test modules to forge test outcomes by in‑process monkey‑patching

**Exact mechanism**  
`external/r11_trusted_unittest_runner.py` performs:

```python
sys.path.insert(0, str(subject))
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
result = unittest.TextTestRunner(verbosity=2).run(suite)
```

The candidate test modules are imported into the runner’s own process. Module‑level code executes during `loadTestsFromNames`. After that, the runner uses `unittest.TextTestRunner` to run the suite.

**Concrete bypass**  
A pinned candidate test module can contain, at module level:

```python
import unittest

class _FakeResult:
    def __init__(self, *a, **k): pass
    def wasSuccessful(self): return True
    def __str__(self): return "<unittest.runner.TextTestResult run=0 errors=0 failures=0>"

class _FakeRunner:
    def __init__(self, *a, **k): pass
    def run(self, suite): return _FakeResult()

unittest.TextTestRunner = _FakeRunner

class T(unittest.TestCase):
    def test_should_fail(self):
        self.fail("this should fail")
```

The runner imports this module, the module replaces `unittest.TextTestRunner`, and the runner’s subsequent `unittest.TextTestRunner(...).run(suite)` returns a fake successful result. The runner exits 0. The external guard’s sandbox verification still passes because the file bytes are unchanged. The false PASS is reported as external authority evidence.

**Governing rule**  
- R11‑A requires qualification‑contributing Python execution to be structurally independent from candidate startup/import control and requires that a malicious candidate cannot control or forge its own test outcome.  
- V6 design Section 15 prohibits runtime/test artifact coupling and candidate self‑created authority.  
- The R11 execution contract requires the trusted runner to be outside the candidate tree and requires fail‑closed isolation before any result can count.

**Narrow missing enforcement point**  
The runner must not execute candidate code in the same process as the test orchestration. It must either:

1. run each test module in a subprocess launched with a clean interpreter and collect structured results (e.g., JSON lines or exit codes) from that subprocess, or  
2. use a test orchestrator that never imports candidate code into its own process (e.g., a separate process that receives only serialized test outcomes).

The current in‑process design cannot prevent candidate code from monkey‑patching `unittest`, the result class, `sys.stdout`, `os._exit`, or any other in‑process state.

## E. High / Medium / Low findings

### High

**H1. External authority branch isolation cannot be independently verified from the package.**  
The package asserts that the pinset, guard, and runner originate from review‑branch commit `f560d39f…` and are not editable by the candidate. The package contains both candidate and external files, but no branch/commit history or repository access. From the single‑file projection alone, I cannot verify that later review‑branch commits do not re‑authorize different bytes. This is `INSUFFICIENT_TO_ASSESS` for the branch‑isolation part of R11‑Q.

### Medium

**M1. Runner does not verify the actual interpreter isolation flags.**  
The runner checks `sys.path` for candidate paths at startup, but it does not check `sys.flags.isolated` or `sys.flags.no_site`. If the CI workflow launches the runner without `-I -S`, the runner will proceed. The pinset’s `interpreter_contract` is asserted but not independently enforced by the runner. The CI workflow is not in the package, so the actual invocation cannot be assessed.

**M2. Guard stdlib‑shadow check uses the host Python’s `sys.stdlib_module_names`.**  
If the host Python version differs from the target Python version, some stdlib shadows could be missed. The evidence claims exact Python 3.12.7, so this is likely correct in practice, but it is a cross‑version fragility.

### Low

None identified beyond the above.

## F. R11‑A interpreter/test‑runner independence audit

**Trusted guard/runner absent from frozen candidate:** Yes. The candidate manifest lists 69 files; neither `r11_trusted_external_guard.py` nor `r11_trusted_unittest_runner.py` is among them.

**Interpreter startup uses isolated semantics:** Claimed (`-I -S`, cleared environment). The runner checks `sys.path` for candidate paths at startup and rejects them. It does not independently verify `sys.flags.isolated` / `sys.flags.no_site`.

**Candidate/sandbox paths absent from startup `sys.path`:** The runner checks this explicitly and fails closed.

**stdlib `unittest` resolved before candidate paths inserted:** The runner imports `unittest` at the top, checks `unittest_path.is_relative_to(sandbox)` before inserting candidate paths, and only then inserts the candidate path.

**Bootstrap shadow names, inherited `PYTHONPATH`, user‑site customization, cwd insertion:** The guard rejects `unittest.py`, `sitecustomize.py`, `usercustomize.py`, and stdlib shadow names in the pinset and sandbox. The runner’s isolated startup prevents `PYTHONPATH` influence. `cwd` is not on `sys.path` for isolated script execution.

**Failure to establish isolation fails closed before results count:** The runner raises `SystemExit` on startup‑path or unittest‑location violations.

**Post‑execution bytecode/cache generation:** `sys.dont_write_bytecode = True` is set before candidate imports. Sandbox verification post‑execution checks for new files.

**Concrete malicious candidate:** A pinned test module can monkey‑patch `unittest.TextTestRunner` at import time and force a successful result. This is a concrete, reproducible bypass. The runner cannot prevent it because it imports candidate code into its own process.

**R11‑A conclusion:** **NOT SATISFIED.** The runner does not achieve structural independence from candidate‑controlled test code. The in‑process execution boundary is the missing enforcement point.

## G. R11‑B external exact‑file pinning audit

**Exact candidate commit/tree binding:** Present. The pinset binds `candidate_commit` and `candidate_tree`; the guard verifies them against arguments.

**Complete enumeration of admitted execution files:** The pinset lists 69 files. The guard’s `source_rows` enforces exactly 69 admitted files.

**Exact path + Git blob SHA‑1 + raw SHA‑256 + role binding:** Present for every admitted file. The guard verifies each against the actual bytes.

**All executed test modules pinned as tests:** The pinset’s `executed_tests` lists 19 test modules, each pinned with role `test`. The guard enforces this.

**All test‑read support objects pinned as support:** The pinset’s `required_support_files` lists 10 support files, each pinned with role `support`. The guard enforces this.

**Candidate cannot edit both admitted content and authorizing digest/pin:** The pinset is external. The guard verifies source binding before staging and sandbox binding before and after execution.

**Missing/added/swapped/stale/same‑name‑different‑byte/symlink/alternate‑path/post‑check mutation:** The guard checks all of these. Symlinks are rejected. Unpinned files are rejected. Same‑path different‑byte substitutions fail hash checks.

**Staged sandbox fileset equals pinset before and after execution:** The guard verifies `verify-sandbox` pre‑ and post‑execution. Bytecode writes are disabled.

**Pinset bytes remain unchanged across execution:** The guard checks pinset identity and immutability.

**Executed‑test selection originates from external pinset:** The runner reads `executed_tests` from the pinset, not from candidate metadata.

**Admitted runtime dependencies outside the pinset:** The pinset includes all `.py` files under `governance-runtime/` and the required support files. Non‑`.py` files in `governance-runtime/` are not pinned, but they are not imported as Python modules. Tests that read support files use the pinned support files. The only remaining influences are the Python interpreter and OS environment, which are controlled by the external CI.

**R11‑B conclusion:** **SATISFIED** with respect to pinning. The pinning mechanism is thorough and fail‑closed. However, R11‑B does not mitigate the in‑process execution bypass (D1).

## H. ABGOU/meta‑closure audit

The generic qualification foundation (`v24_v6_governance_foundation.py`) prohibits self‑authority and self‑verifier, requires independent qualification records, enforces currentness, and provides a completeness derivation graph with universal allowed‑root closure. The genesis trusted scope is exact‑pair bound. There is no residual bootstrap path that grants self‑qualification. **Satisfied.**

## I. Completeness derivation/root audit

`validate_completeness_derivation_graph` rejects cycles, disallowed terminals/sources, non‑terminal source surfaces, and subjects not universally rooted in allowed roots. The adversarial tests cover mixed allowed/disallowed terminals, transitive mutual omission cycles, and disallowed non‑terminal sources. **Satisfied.**

## J. Genesis trusted‑scope audit

`validate_genesis_trusted_scope` binds exact `{object_id, content_digest}` pairs, rejects duplicate object IDs, verifies the pair‑set digest, and `genesis_scope_match` rejects cross‑pair combinations. **Satisfied.**

## K. Endpoint/predicate/evaluator/condition/evidence audit

`v24_v6_endpoint_projection.py` implements qualified endpoint‑table compilation, omission‑sensitive `ApplicablePredicateUniverse` with completeness, one evaluator contract per applicable predicate, registered TRUE condition schemas, governed FALSE negative evidence, producer‑selected N/A rejection, and deterministic earliest‑failure endpoint selection. **Satisfied.**

## L. Revalidation snapshot + decision/apply latch audit

`v24_v6_decision_apply.py` requires a qualified, independent, current snapshot source; binds all load‑bearing digests; rejects mixed snapshots; requires a new exact‑current reevaluated decision on any drift; and checks the material effect path against the same snapshot head. **Satisfied.**

## M. Material surface/effect‑class/ledger audit

`v24_v6_material_surface.py` and `v24_v6_effect_ledger_closure.py` implement append‑only observation ledgers, durable storage/anchor classes, independent witnesses, fork/rollback detection, two independent material‑surface derivations, omission‑sensitive effect‑class registry with independent obligation derivation, and durable governance ledgers with witness currentness. **Satisfied.**

## N. Atomic‑mode audit

`v24_v6_atomic_binding_modes.py` derives the obligation set independently from contracts and mechanisms, enforces exact registry set equality, binds proof schema/verifier/qualification, and rejects unknown modes, schema substitution, missing fields, and replay across evaluation/condition/decision contexts. **Satisfied.**

## O. Normative/anti‑false‑green audit

`v24_v6_normative_clause_projection.py` enumerates structural candidates from exact artifact bytes without using catalog locators, requires one governed disposition per candidate, and binds dispositions to exact candidate/authority/evidence. `v24_v6_qualification_integrity.py` implements static and runtime anti‑false‑green gates rejecting WDPC literals, fixture branch IDs, expected endpoints, reviewer finding IDs, test artifact coupling, diagnostic‑string endpoint derivation, and self‑created independence proofs. **Satisfied.**

## P. Result‑accounting/historical‑result audit

`compile_qualification_summary` counts only valid current‑round `EXECUTED` terminal `PASS` with exact candidate/tree/environment binding and valid record digests. Missing cases block the summary. Later resolution records cannot rewrite the same round. Historical PASS counts are preserved. **Satisfied.**

## Q. External‑authority/recovery integrity audit

The pinset, guard, and runner are present as external objects. The guard enforces source binding, sandbox binding pre/post, symlink rejection, bootstrap shadow rejection, stdlib shadow rejection, unpinned file rejection, and exact file‑set equality. The runner enforces isolated startup checks. **However**, the in‑process execution model (D1) allows candidate‑controlled test modules to forge outcomes, which undermines the external authority’s ability to qualify the candidate. The external authority’s verification results cannot be trusted if the runner can be fooled by candidate code. **NOT SATISFIED** due to D1.

## R. Exact candidate/package binding audit

The package contains the frozen candidate files, the approved V6 design, the external pinset/guard/runner, review bindings, and construction evidence. The manifest lists 80 files (excluding itself), and the bundle contains 81 files. The candidate manifest declares the frozen candidate commit/tree. The external pinset binds the candidate commit/tree and the 69 admitted files. The review instructions are present. **Structurally CONSISTENT.** Cryptographic recomputation was not performed.

## S. Remaining concrete bypass paths

1. **In‑process test‑runner monkey‑patching (Critical, D1).** A pinned candidate test module can replace `unittest.TextTestRunner` at import time and force a successful result. The runner reports PASS, and the external guard’s sandbox verification still passes.
2. **Unverified `-I -S` flags (Medium, M1).** If the CI workflow launches the runner without isolated/no‑site flags, the runner does not detect this. The actual invocation is not in the package.
3. **Host‑Python stdlib shadow check (Medium, M2).** The guard’s stdlib shadow detection depends on the host Python’s `sys.stdlib_module_names`. A version mismatch could miss a shadow.
4. **Branch‑isolation verification gap (High, H1).** The package cannot prove that the external pinset/guard/runner are on a separate branch that the candidate cannot edit. This is a limitation of the single‑file projection, not necessarily an implementation defect, but it means the external authority identity cannot be fully verified from the supplied bytes alone.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`