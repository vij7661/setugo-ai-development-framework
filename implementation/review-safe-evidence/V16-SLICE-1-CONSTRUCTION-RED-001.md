# V16 Slice 1 — Construction RED 001

Status: **PRESERVED RED HISTORY / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This record preserves two failed construction runs produced while repairing the Slice 1 internal-adversarial findings. Neither RED is erased by a later green run.

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

This run is **not green construction evidence**. The mechanism tests were green, but the governed mandatory-test-set binding failed. The repair is to update the stable manifest and workflow count to exactly the expanded 38-test set without changing the already-passing mechanisms merely to force green.

## Historical rule

Any later successful run must preserve both RED-A and RED-B. Neither may be described as if it never occurred, and neither may be used to claim implementation or runtime qualification.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
