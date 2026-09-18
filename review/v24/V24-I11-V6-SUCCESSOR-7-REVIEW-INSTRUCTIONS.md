# Successor-7 Independent Manual Review Instructions

Review only the exact frozen candidate bound by `V24-I11-V6-SUCCESSOR-7-FROZEN-BINDING.json`.

Required posture:
- treat the candidate as untrusted until independently justified;
- preserve all prior RED and `CHANGES_REQUIRED` evidence;
- do not infer authority from GREEN CI alone;
- inspect whether candidate execution can influence the root authority service, its executable, endpoint, process state, private scratch/result channel, loader state, or the exact gate/worker/source set;
- inspect whether the external bootstrap actually derives trusted installation identity from the independently frozen v3 trust artifact rather than candidate-generated build metadata;
- inspect Unix-socket peer identity enforcement and whether another principal/process can impersonate the authorized candidate or counterfeit a service response;
- inspect parsing of gate/service output for false-positive or injection paths;
- explicitly re-evaluate PRC-1, DA-1, and NCP-1 including compound attacks;
- distinguish construction evidence from runtime/scientific qualification;
- do not open scientific execution or claim runtime qualification.

Required disposition:
- `PASS_FOR_BOUNDED_CONSTRUCTION_REVIEW`, or
- `CHANGES_REQUIRED`.

Any blocking finding must include the concrete false-green/failure path, why existing controls do not close it, and the narrowest required repair.

The package must preserve the frozen candidate, final-head verification, Successor-7 external bootstrap v3 trust artifacts, Successor-4 root-attestation trust artifacts, predecessor Successor-6 review, exact approved V6 design bytes, and deterministic package manifest/binding.
