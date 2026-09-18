# Successor-8 Independent Manual Review Instructions

Review only the exact frozen candidate bound by `V24-I11-V6-SUCCESSOR-8-FROZEN-BINDING.json`.

Required posture:
- treat the candidate as untrusted until independently justified;
- preserve all prior RED and `CHANGES_REQUIRED` evidence;
- do not infer authority from GREEN CI alone;
- inspect whether candidate-local Python, socket/path substitution, namespace views, fake service JSON, or direct client replacement can create an authority-bearing effect;
- distinguish candidate-visible diagnostic responses from the root-only authority-record consume path;
- inspect the exact request binding, service-build binding, gate-result binding, one-shot replay semantics, record file creation/consumption, and root-private state;
- inspect whether a candidate can fabricate, replace, rebind, replay, pre-create, overwrite, rename, or otherwise influence pending/consumed authority records;
- inspect whether numeric root/effective-UID checks or namespace assumptions can make the root-only consumer candidate-reachable;
- treat `UNPRIVILEGED_USER_NAMESPACE_PROHIBITION_ENFORCED` as a load-bearing bounded-host condition and verify that the candidate fails closed when that condition is absent;
- inspect whether the Successor-8 external bootstrap v4 independently pins the exact gate/service/source identities rather than accepting candidate-generated trust metadata;
- explicitly re-evaluate PRC-1, DA-1, and NCP-1 including compound attacks through authority-record consumption;
- distinguish construction evidence from runtime/scientific qualification;
- do not open scientific execution or claim runtime qualification.

Required disposition:
- `PASS_FOR_BOUNDED_CONSTRUCTION_REVIEW`, or
- `CHANGES_REQUIRED`.

Any blocking finding must include the concrete false-green/failure path, why existing controls do not close it, and the narrowest required repair.

The package must preserve the frozen candidate, exact final-head verification, Successor-8 external bootstrap v4 trust artifacts, Successor-4 root-attestation trust artifacts, predecessor Successor-7 final manual review, exact approved V6 design bytes, namespace-policy evidence, preserved Successor-8 RED, and deterministic package manifest/binding.
