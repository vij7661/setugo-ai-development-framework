# Successor-5 Independent Manual Review Instructions

Review only the exact frozen candidate bound by `V24-I11-V6-SUCCESSOR-5-FROZEN-BINDING.json`.

Required posture:
- treat the candidate as untrusted until independently justified;
- preserve all prior RED and CHANGES_REQUIRED evidence;
- do not infer authority from GREEN CI alone;
- inspect whether candidate-mutable Python can still replace, bypass, or counterfeit any load-bearing verifier, key, worker, payload binding, verdict, or authority decision;
- inspect the native gate source/build path and every pinned transitive production dependency;
- explicitly re-evaluate PRC-1, DA-1, and NCP-1, including compound attacks;
- distinguish construction evidence from runtime/scientific qualification;
- do not open scientific execution or claim runtime qualification.

Required disposition:
- `PASS_FOR_BOUNDED_CONSTRUCTION_REVIEW`, or
- `CHANGES_REQUIRED`.

Any blocking finding must include the concrete false-green/failure path, why existing controls do not close it, and the narrowest required repair.

The frozen candidate, final-head verification, external trust artifacts, predecessor Successor-4 review, approved V6 design bytes, and deterministic package manifest are included in the clean review package.
