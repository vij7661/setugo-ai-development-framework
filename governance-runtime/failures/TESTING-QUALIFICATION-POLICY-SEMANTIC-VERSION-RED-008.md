# TESTING Qualification Boundary — Policy Semantic Version RED 008

Status: `PRESERVED_GENUINE_GOVERNANCE_DEFECT`
Authority effect: `NONE_EVIDENCE_ONLY`

During repair of R7-01, the implementation semantics of terminal authority changed from caller-supplied role/provenance/current booleans to signed exact-candidate authority verification, while `_policy_material()` and `POLICY_VERSION=5` would otherwise remain unchanged.

That would allow two materially different authority mechanisms to present the same policy identity/hash. Even though no current v5 terminal attestation is being promoted here, preserving the same policy version across a material authority-semantic change would weaken stale/rebound detection.

Repair requirement: bump the qualification policy version before treating the repaired mechanism as a current policy and update frozen version regressions. Historical v5 evidence remains historical; no earlier evidence is rewritten as current authority.
