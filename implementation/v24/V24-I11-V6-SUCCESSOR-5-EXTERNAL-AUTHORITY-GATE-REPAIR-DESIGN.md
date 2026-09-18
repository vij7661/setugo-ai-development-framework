# V24-I11-V6 Successor-5 — External Authority Gate Repair Design

Status: **IMPLEMENTED / ALL-UP GREEN / EXACT FINAL-HEAD FREEZE PENDING**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and blocking review

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-4`
- commit: `ef30eba1dfbe5ccf0ec6edb9e8d1295da5c70ddb`
- tree: `bfbf49021514240668b24612d53ea790bcdf0baa`
- exact final-head run: `35324254339`
- V24-V6 all-up evidence: `209/209 GREEN`
- final manual-review record commit: `32faf45bd82c5cd0c29700d7cc239b1935be24ba`
- manual review disposition: `CHANGES_REQUIRED`

The Successor-4 GREEN evidence remains valid bounded construction evidence. It does not erase or override the manual-review finding.

## 2. Preserved finding to falsify

Critical finding `C-01 / PRC-1`:

Successor-4 externalized the signing private key but left the final root-verification decision inside ordinary mutable Python state. In the frozen candidate, `v24_v6_proof_reference_closure.py` imports:

```python
from v24_v6_root_attestation import validate_root_attestation
```

A same-process caller can replace that module-global function before invoking a proof resolver. The structurally valid attacker context already preserved from Successor-4's predecessor attack can then reach the normal resolver path.

The first Successor-5 regression attempted this exact substitution against production code and is now permanently preserved RED.

Preserved Successor-5 RED:
- branch head tested: `2531bd4f619a4c2d4c57cc44369a063fe1c92acd`
- workflow: `V24 V6 Successor-5 Mutable Verifier RED`
- workflow run: `35326754734`
- job: `105541474606`
- test: `test_same_process_imported_verifier_substitution_cannot_self_grant`
- compile step: `GREEN`
- attack regression: `RED`
- observed result: `qualified=True`, `state=PROOF_REFERENCE_CLOSED`, `problems=[]`
- observed forged reference digest: `aa33564e090c903d68d4189c5ffe75ee86d2671c0193ae73dc940d6e344fab84`

This is a genuine mechanism defect. It is not a fixture defect and MUST NOT be relabeled as PASS.

## 3. Root cause

Successor-4 changed:

`caller-controlled digest -> caller-writable environment -> Python validator`

into:

`externally signed context -> pinned public key -> Python verifier -> Python authority decision`

The signing root is external, but the load-bearing decision remains mutable by the same interpreter the threat model treats as untrusted.

An asymmetric signature is therefore insufficient when the adversary can replace the function, key state, verification helper, or final authority gate that interprets that signature.

## 4. Required Successor-5 invariant

No state or return value produced solely inside candidate-mutable Python may create authoritative proof closure.

The authority-bearing path MUST be:

`exact context bytes + exact attestation -> external trusted verifier/gate -> externally enforced verdict -> downstream authority-bearing consumer`

and MUST satisfy all of the following:

1. Candidate Python is treated as untrusted execution.
2. The pinned verification root is held by an external verifier/gate that is not mutable through candidate Python module state.
3. The external verifier independently validates:
   - attestation schema/version;
   - fixed key identity and algorithm;
   - exact governance generation;
   - exact proof-context digest;
   - exact genesis trusted-scope digest;
   - detached signature over canonical material.
4. The external verifier verdict is bound to the exact context bytes/digest, scope digest, generation, verifier identity/version, and decision.
5. The authority-bearing consumer validates/enforces that verdict outside candidate-mutable Python state.
6. Candidate Python cannot replace:
   - the verifier implementation;
   - pinned public key/root identity;
   - verifier helper;
   - verdict validator;
   - authority gate;
   - exact input binding.
7. Direct calls to the Python proof resolver are construction diagnostics only unless accompanied by a valid externally enforced gate result.
8. Failure, timeout, malformed output, unavailable verifier, mismatched binding, replay, or unknown verifier identity MUST fail closed.

## 5. Construction architecture direction

Successor-5 MUST use the already-established trusted-parent/native-oracle direction rather than another Python-local pin.

The construction reference shape is:

1. A trusted external parent/gate receives the exact proof context and trusted-boundary/attestation material.
2. The gate verifies the detached root attestation using a pinned verification root outside candidate Python mutable state.
3. Only after successful external verification may the candidate Python resolver be invoked for structural/dependency resolution.
4. The gate binds the candidate resolver result to the exact externally verified context identity.
5. The final construction verdict is emitted/enforced by the external gate, not by candidate Python.
6. A direct Python `qualified=True` result without the gate's valid exact binding is explicitly non-authoritative.

The implementation may use a small separately built native verifier/parent for the bounded construction mechanism. A Python subprocess that imports the same mutable verifier code does not satisfy this invariant.

## 6. Prohibited repair shapes

The following do **not** close PRC-1:

- importing the verifier under a different Python name;
- using `importlib` dynamically;
- freezing a Python dataclass/tuple/module convention;
- storing the key in another Python module;
- another environment variable;
- a Python-only singleton or closure;
- hashing the verifier source and checking that hash from the same candidate interpreter;
- a Python child process whose authority result is trusted by the same untrusted Python caller;
- a subprocess path, callback, socket response, or verdict that candidate Python can replace and then self-accept;
- a caller-supplied verifier executable/path/public key;
- a signed result that is validated only by candidate Python;
- documentation-only threat-model narrowing after exposure;
- weakening the same-process attacker model merely to recover GREEN.

## 7. Mandatory permanent regressions

At minimum Successor-5 MUST freeze these cases:

1. `SAME_PROCESS_IMPORTED_VERIFIER_SUBSTITUTION_REJECTED`
   - use the preserved attacker-built context;
   - replace `v24_v6_proof_reference_closure.validate_root_attestation` with a success stub;
   - authoritative gate result MUST remain rejected.

2. `SAME_PROCESS_ROOT_KEY_SUBSTITUTION_REJECTED`
   - mutate Python verifier key globals/modulus/exponent;
   - authoritative gate result MUST remain rejected.

3. `SAME_PROCESS_RSA_HELPER_SUBSTITUTION_REJECTED`
   - replace the Python RSA verification helper with an unconditional success function;
   - authoritative gate result MUST remain rejected.

4. `DIRECT_PYTHON_QUALIFIED_IS_NONAUTHORITATIVE`
   - force or obtain `qualified=True` from the Python resolver without a valid external gate verdict;
   - construction authority MUST remain denied.

5. `FORGED_EXTERNAL_VERDICT_REJECTED`
   - fabricate external-verdict fields/bytes in candidate Python;
   - authority gate MUST reject.

6. `VERDICT_CONTEXT_REBIND_REJECTED`
   - reuse a valid verdict for context A with context B;
   - reject.

7. `VERDICT_SCOPE_OR_GENERATION_REBIND_REJECTED`
   - reuse a verdict across genesis scope or governance generation;
   - reject.

8. `VERIFIER_IDENTITY_VERSION_REBIND_REJECTED`
   - changed verifier identity/version/build digest with an old verdict;
   - reject.

9. `EXTERNAL_GATE_FAILURE_FAILS_CLOSED`
   - verifier crash, timeout, unavailable executable, malformed output, or nonzero exit;
   - reject and never fall back to Python-local approval.

10. `EXTERNALLY_VERIFIED_SIGNED_CONTEXT_POSITIVE`
    - exact pre-attested construction fixture through the external gate;
    - proof closure succeeds.

11. Existing Successor-4 root-attestation regressions remain mandatory.

12. Existing DA-1 and NCP-1 compound regressions remain mandatory after PRC-1 is externally closed.

## 8. DA-1 and NCP-1 progression

Successor-4's local DA-1 and NCP-1 repairs remain preserved but are transitively open while PRC-1 is open.

After the external gate is implemented, Successor-5 MUST rerun:

- fresh decision -> effect-path/target/effect-class attacker binding;
- stale decision/effect binding substitution;
- fresh clause -> control reassignment;
- stale clause/control substitution;
- cross-control composition.

No DA-1 or NCP-1 closure claim is allowed solely from their local checks.

## 9. R9 / integrated-freeze impact

The external authority gate and all load-bearing verifier artifacts become integrated successor dependencies.

The Successor-5 manifest/final-head evidence MUST bind at least:

- exact gate source/build inputs;
- exact gate executable/build artifact digest;
- exact external public-root identity;
- exact verifier protocol/schema version;
- exact candidate Python production files;
- exact mandatory adversarial regression set.

Final-head CI MUST rebuild or independently verify the exact trusted gate artifact before packaging the candidate for manual review.

## 10. Claim boundary

Successor-5 remains construction-only.

A bounded construction pass would support only that, under the frozen test environment, candidate-mutable Python could not create authoritative proof closure by replacing its local verifier/key/helper or fabricating/rebinding the external-gate verdict.

It does not establish production HSM/KMS custody, OS hardening, hostile-host resistance, production IAM, remote-service security, scientific WDPC outcomes, release/deploy authority, or general native-code memory safety.

Scientific execution remains closed. Runtime qualification remains unclaimed.

## 11. Progression rule

Successor-5 may proceed to implementation only after the direct same-process verifier-substitution attack is preserved as RED against the frozen Successor-4 mechanism.

Successor-5 may be frozen for independent manual review only after:

- preserved Successor-4 review remains historical;
- Successor-5 RED remains historical and is never relabeled;
- all mandatory external-gate regressions are GREEN;
- complete R1-R9/proof-resolution suite is GREEN;
- complete inherited V24 suite is GREEN;
- DA-1 and NCP-1 compound attacks are rerun through the new external boundary;
- exact external gate artifact/build identity is frozen;
- scientific execution remains closed;
- runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 12. Implemented construction evidence

The preregistered repair has now been implemented without reclassifying the preserved RED.

All-up implementation evidence:
- branch head tested: `c2a1c8215b755ac2aee9fe007c5b1b6fe159e246`
- workflow: `V24 V6 Successor-5 External Authority Gate`
- workflow run: `35331004892`
- job: `105555085219`
- Successor-5 + inherited Successor-4 external-gate regressions: `21/21 GREEN`
- complete V24-V6 R1-R9 regressions: `199/199 GREEN`
- inherited V24 construction regressions: `90/90 GREEN`
- total tests in the all-up gate: `310/310 GREEN`
- gate build input SHA-256: `0065c4334cd23c55f241aeb7f7e221a414b2e5d01ba74bb85cd0968557ecff84`
- native gate binary SHA-256: `e2145e97c96e1af335234c2d58b4a9c0be2bba5e32da696bb36bc38b28f6ca5a`
- gate artifact: `10541365345`
- gate artifact digest: `sha256:cd0e509bc290b87acbd1ad456447689718d1ed7e38fbb57c3f6206765ae3cac3`

The external gate pins the worker plus all load-bearing Python dependencies used by proof resolution, DA-1, and NCP-1. The native parent performs an externally enforced context/attestation probe, executes the downstream operation in a clean interpreter, and independently verifies exact context, scope, generation, payload, gate identity/version, and worker-result binding before emitting `ALLOW`.

Compound falsification evidence:
- `test_da1_same_process_fresh_effect_path_self_grant_rejected_by_external_gate` — GREEN.
- `test_ncp1_same_process_fresh_clause_control_self_grant_rejected_by_external_gate` — GREEN.
- each test first demonstrates a local same-process Python false-green after deliberate mutation, then proves that the native gate rejects the identical attacked payload.

This evidence remains construction-only. Scientific execution remains closed and runtime qualification remains `NOT_CLAIMED`.

The next permitted step is exact final-head freeze and independent manual review.

