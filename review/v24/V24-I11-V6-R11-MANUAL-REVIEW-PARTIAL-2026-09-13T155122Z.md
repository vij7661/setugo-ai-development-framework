Matches §3 exactly (19297 bytes, raw SHA-256 `96ec464f...`). Now the external authority objects and plan-body hash.## §3/§4 Identity Verification (checkpoint from last turn) — all VERIFIED

- Approved-design object: 19,297 bytes, raw SHA-256 `96ec464f...`, git blob SHA-1 `4a15d50a...` — **exact match**.
- Plan-body hash: the design file states its own extraction rule (body = everything after the first `---\n\n` separator). Applying that rule to the actual bytes yields SHA-256 `286217399947...ad5` — **exact match** to the declared `PLAN_BODY_SHA256`.
- External guard blob SHA-1 `d8792e90...`, runner blob SHA-1 `1773c33e...`, pinset SHA-256 `dfd5663e...` — **all exact matches**.
- The two "verification" JSON files hash to exactly the `static_verification_sha256` (`bb978666...`) and `generated_verification_sha256` (`27e524dc...`) declared in the manifest.

So every identity claim in §3/§4 is cryptographically consistent. **B. CRYPTOGRAPHIC_RECOMPUTATION = VERIFIED** (fully, not just partially).

One thing worth flagging on its own: the two "external verification" JSON files are hand-written PASS/PASS/PASS attestations with no attached execution log, stdout capture, or timestamped run artifact — they assert outcomes rather than showing evidence of them. Per your own §5 ("green tests... are evidence to challenge, not authority to qualify"), these files' *existence and hash-stability* is verified, but their *truth content* isn't self-evidencing — that's exactly what R11-A/B below have to establish independently.

## F. R11-A — interpreter/test-runner independence audit

I read `r11_trusted_unittest_runner.py` and `r11_trusted_external_guard.py` in full.

**What's actually enforced:**

- Runner rejects if `""`, the sandbox, or the candidate subdirectory are already on `sys.path` at startup, and rejects if `unittest.__file__` resolves from inside the sandbox — a real (if partial) check against path-based shadowing.
- Guard rejects symlinks, rejects any `.py` file named `unittest.py`/`sitecustomize.py`/`usercustomize.py`, and rejects any file whose stem collides with `sys.stdlib_module_names` — both in the source tree and in the staged sandbox, both pre- and post-execution.
- `sys.dont_write_bytecode = True` before candidate import, and `verify_sandbox` re-walks the whole sandbox afterward and fails closed on any file not in the pinset — this does cover "post-execution bytecode/cache expansion."

**Blocking finding — interpreter isolation is declared, not verified:**

`build_pinset()` writes an `interpreter_contract` block into the pinset with `isolated_mode`, `no_site`, `ignore_environment`, `safe_path` all hardcoded to `True` — unconditionally, regardless of how the interpreter is actually invoked. Neither the guard nor the runner ever calls `sys.flags.isolated`, `sys.flags.no_site`, or `sys.flags.ignore_environment` to check that the process running *right now* was actually started with `-I`/`-S`/`-E`. If someone (or some CI step) invokes `python3 r11_trusted_unittest_runner.py ...` without those flags, `site.py` still runs before this script's own checks execute, meaning a `sitecustomize.py`/`usercustomize.py` reachable via `PYTHONPATH` or user-site could already have executed arbitrary code by the time the path checks fire. The pinset would still faithfully report `"isolated_mode": true` — a false attestation with nothing to catch it.

- **Governing rule:** §6, "interpreter startup uses isolated semantics... before candidate bytes become importable."
- **Bypass:** run the trusted runner without `-I -S -E`; the interpreter_contract claim goes unchallenged.
- **Narrow fix:** at the top of `main()` in the runner, assert `sys.flags.isolated` (or the `-S`+`-E`+`safe_path` equivalent) and `SystemExit` if false, rather than only writing the claim into the pinset at build time.

**Blocking finding — concrete malicious-candidate construction (the required §6 exploit):**

Candidate "dependency" modules (e.g. any `v24_v6_*.py`) run with full interpreter privilege in the same process as the test runner — there's no subprocess boundary, no restricted import, no protection of the `unittest` module's own class objects. A malicious candidate module needs only top-level code such as:

```python
import unittest
unittest.TestResult.wasSuccessful = lambda self: True

```

Any pinned test file that does `from v24_v6_governance_foundation import ...` (all of them do) triggers this at import time, before a single test runs. `result.wasSuccessful()` in the runner's `main()` then always returns `True`, and the process exits 0 regardless of actual failures. Byte-pinning the file's *identity* (which the guard does correctly) does nothing to constrain what that byte-identical file *does* when executed — pinning proves which bytes ran, not that they behaved. I did not find any hook, restricted-import mechanism, or process isolation anywhere in guard/runner that would prevent this.

- **Answer to §6's mandatory question: yes, a candidate can still control/forge its own test outcome.**
- **Narrow fix:** run candidate-imported code and result-collection in genuinely separate address spaces (e.g. execute tests in a subprocess and have the *trusted* parent process independently re-derive pass/fail from the subprocess's raw stdout/exit code, never trusting an in-process `TestResult` object the candidate process could have touched), or at minimum snapshot and restore critical `unittest` attributes after each module import and before invoking the runner.

## G. R11-B — external exact-file pinning audit

This part is solid. `checked_file`/`source_rows`/`sandbox_rows` bind exact path + git blob SHA-1 + raw SHA-256 + role for all 69 admitted files (verified: 69 exactly, matching manifest); `verify_source`, `stage`, and `verify_sandbox` each independently re-hash and fail closed on any missing/extra/changed/symlinked file, both before and after staging. `EXECUTED_TESTS` (19) and `SUPPORT` (10) are hardcoded in the guard script itself — not read from candidate-supplied metadata — so the candidate cannot expand or redirect its own admitted test/support surface. This satisfies adversarial invariants #8–#10 from §9 (changed pinned file, added unpinned file, symlink substitution) as far as the *pinning* mechanism goes. It does **not**, and cannot, defend against the R11-A monkeypatch finding above — pinning is orthogonal to runtime behavior.

## H–Q (systemic V6 audits)

I spot-checked `v24_v6_governance_foundation.py` in full: it's pure schema/digest validation logic (record shape checks, SHA-256 field validation, canonical-JSON digest recomputation for tamper-evidence) with no I/O, no privilege grants, and an explicit `AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"` constant threaded through every return value — consistent with its claimed "construction-only" status. I have **not yet** read the other nine `v24_v6_*.py` modules (decision/apply, material surface, atomic binding modes, endpoint projection, normative clause projection, qualification integrity, external execution binding, integrated successor) or the supporting `v24_authority_universe.py` / `v24_effective_control.py` / `v24_admission_application_witness.py` files that H–Q require. Reporting PASS on those sections now would be exactly the test-name/absence-of-evidence inference §5 prohibits, so: **H–Q = INSUFFICIENT_TO_ASSESS pending that reading.**

Given the size (10 more substantial source files plus their tests), want me to keep going through H–Q now, or pick specific sections to prioritize first (e.g., M/Q since they're the ones most load-bearing for "can a candidate grant itself authority")?