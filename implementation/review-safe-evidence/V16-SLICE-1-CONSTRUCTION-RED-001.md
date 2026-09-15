# V16 Slice 1 — Construction RED 001

Status: **PRESERVED RED HISTORY / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This record preserves five failed construction runs produced while repairing the Slice 1 internal-adversarial findings. No later green run erases any of them.

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

## RED-D — currentness-anchor implementation landed before harness migration

- workflow run: `34978768057`
- candidate commit: `0e06a2648b0fbe08ed10ad902b5df2ca87460517`
- candidate tree: `a8585192f7e90792d4031449fd2a483d4b192be6`
- job: `104413262572`
- conclusion: `failure`
- classification: `HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

The second internal-adversarial repair made `expected_current_registry_head` mandatory for current-authority verification. The pre-migration 38-test harness still invoked `verify_signed_governance_record()` and its JSON ingress helper without that required currentness anchor. Fourteen signed-record tests therefore errored at the API boundary before their intended mechanism endpoints.

Observed raw summary:

- `Ran 38 tests in 0.037s`
- `FAILED (errors=14)`
- representative error: `TypeError: verify_signed_governance_record() missing 1 required keyword-only argument: 'expected_current_registry_head'`

This is a harness-transition RED, not evidence that the pinned-head mechanism itself failed. It remains preserved.

## RED-E — 42 repaired mechanism tests green while mandatory manifest/workflow still declared 38

- workflow run: `34978912523`
- candidate commit: `49a84eb692ec3ec6d966e5d22623e637b4e7478c`
- candidate tree: `9611d821e3353a8bbdf9ec126d29f1f238f7c680`
- job: `104413765694`
- conclusion: `failure`
- classification: `HARNESS_DEFECT_BEFORE_INTENDED_ENDPOINT`

The migrated and expanded source executed **42 tests and all 42 passed**. The added regressions exercised lone-surrogate rejection, governance-key public-key alias rejection, stale registry-prefix rejection against a newer pinned head, and pinned-head trust-set mismatch.

The governed test-set verification then failed because the stable mandatory manifest and workflow still declared 38 tests.

Observed raw summary:

- `Ran 42 tests in 0.055s`
- `OK`
- manifest/source/execution gate failed with `AssertionError: 42`

This run is not green construction evidence even though every mechanism test passed; the stable mandatory-test-set binding remained stale.

## Historical rule

Any later successful run must preserve RED-A through RED-E. None may be described as if it never occurred, and none may be used to claim implementation or runtime qualification.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
