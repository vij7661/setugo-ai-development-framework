# V16 Slice 1 — Construction RED 001

Status: **PRESERVED RED HISTORY / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This record preserves three failed construction runs produced while repairing the Slice 1 internal-adversarial findings. No later green run erases any of them.

## RED-A — implementation/test harness transition mismatch

- workflow run: `34977136315`
- candidate commit: `25fbb02a2f5b15caad7e99aa56d3fbc45b65a331`
- candidate tree: `accbe09ff5a450c09ac777b97c217447e6edd297`
- job: `104407613808`
- conclusion: `failure`
- classification: `HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

The trust implementation changed `registry_signature_message()` so bootstrap signatures bind the trust-set/root/key/control-domain identity. The pre-repair test fixture still called the old one-argument API. CI compiled successfully, then 21 of the 30 tests errored before reaching their intended mechanism with:

`TypeError: registry_signature_message() missing 4 required keyword-only arguments: 'trust_set_id', 'root_id', 'key_id', and 'control_domain_id'`

Observed raw summary:

- `Ran 30 tests`
- `FAILED (errors=21)`

This RED does not prove a V16 trust-mechanism defect because the failing fixtures did not construct a valid post-repair registry signature. It does prove that implementation and harness were temporarily inconsistent and must remain in the historical record.

## RED-B — stable mandatory-test manifest lagged expanded adversarial source

- workflow run: `34977289133`
- candidate commit: `dbdf404ebf6a291b6169522f69021637cffb99df`
- candidate tree: `a171e486dcedcb6589d2ee9709f49f963fea2613`
- job: `104408147765`
- conclusion: `failure`
- classification: `HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

The repaired/expanded test source executed **38 tests and all 38 passed**, including the new regressions for bootstrap-key reuse, root-signature identity binding, registry key backdating, generation reuse, stale-generation currentness, current-generation success, strict serialized ingress, and canonical integer bounds.

The workflow then correctly failed its manifest/source/execution equality gate because the stable manifest and hard count still declared 30 tests. Raw output records:

- `Ran 38 tests in 0.031s`
- `OK`
- manifest-verification `AssertionError: 38`

This run is **not green construction evidence**. The mechanism tests were green, but the governed mandatory-test-set binding failed.

## RED-C — manifest updated to 38 while workflow hard-count still expected 30

- workflow run: `34978155073`
- candidate commit: `c609b7c982a7d712c8e3265880c77e593ac35b0d`
- candidate tree: `16ecc0fdeb6a731803399e815d19cdc925e8f5a2`
- job: `104411135618`
- conclusion: `failure`
- classification: `HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

This sequential-update run had the repaired code, the expanded 38-test source, and the expanded 38-entry manifest. All **38 mechanism tests passed**. The workflow itself still contained the old hard assertions `len(...) == 30`, so the manifest/source/execution verification step failed with `AssertionError: 38` before the construction boundary could emit PASS.

Observed raw summary:

- `Ran 38 tests in 0.031s`
- `OK`
- verification step failed on the stale hard-count assertion.

This RED is distinct from RED-B: RED-B had an outdated 30-entry manifest; RED-C had the correct 38-entry manifest but an outdated workflow verifier. It is preserved because the implementation workflow was temporarily inconsistent during sequential repository updates.

## Historical rule

Any later successful run must preserve RED-A, RED-B, and RED-C. None may be described as if it never occurred, and none may be used to claim implementation or runtime qualification.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
