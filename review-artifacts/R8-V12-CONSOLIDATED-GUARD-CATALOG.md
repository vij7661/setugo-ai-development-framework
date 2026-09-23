# R8 v12 Consolidated Guard Catalog — GCC-1 Generated View

Status: REVIEW_SUPPORT / NON_AUTHORITATIVE_BY_ITSELF
Authority effect: NONE

Generation rule:
- Source designs: canonical R8 v4 through v12 commits.
- For duplicate guard definitions, the latest design-layer occurrence wins.
- Expected contiguous range: G001-G130.
- Missing/duplicate-conflict checks are performed before packet freeze.
- Case semantics remain defined by their canonical source designs; this table is a deterministic review index.

Missing guards: NONE

| Guard | Mechanism | Positive | Negatives with fault-proof class | Source |
|---|---|---|---|---|
| G001 | EBA ControllerAttestation verification | V4-001 | V4-002 FP0; V4-003 FP1 | v7 `fad366add685…` |
| G002 | BootstrapAuthorization + singleton CAS | V4-004 | V4-005 FP5; V4-006 FP2 | v7 `fad366add685…` |
| G003 | Root quorum independence | V4-007 | V4-008 FP1; V4-009 FP1 | v7 `fad366add685…` |
| G004 | Recovery quorum + trigger proof | V4-010 | V4-011 FP1; V4-012 FP5 | v7 `fad366add685…` |
| G005 | Anchor quorum + witness | V4-013 | V4-014 FP1; V4-015 FP1; V4-016 FP1 | v7 `fad366add685…` |
| G006 | Atomic CAS_APPEND | V4-017 | V4-018 FP2; V4-019 FP1 | v7 `fad366add685…` |
| G007 | Constitutional semantic digest gate | V4-020 | V4-021 FP5; V4-022 FP5 | v7 `fad366add685…` |
| G008 | GCP-1 canonicalization/parser | V4-023 | V4-024 FP0; V4-025 FP0; V4-026 FP0; V4-027 FP0; V4-028 FP0; V4-029 FP5; V4-030 FP5 | v7 `fad366add685…` |
| G009 | SPR lifecycle/stable primitive IDs | V4-031 | V4-032 FP5; V4-033 FP0 | v7 `fad366add685…` |
| G010 | Reviewer independence/two-channel review | V4-034 | V4-035 FP5; V4-036 FP1; V4-037 FP5 | v7 `fad366add685…` |
| G011 | Issuer separation of duties | V4-038 | V4-039 FP1; V4-040 FP5 | v7 `fad366add685…` |
| G012 | Revocation monotonic use-time validation | V4-041 | V4-042 FP1; V4-043 FP1 | v7 `fad366add685…` |
| G013 | Context-bound time quorum | V4-044 | V4-045 FP1; V4-046 FP1; V4-047 FP1 | v7 `fad366add685…` |
| G014 | Materiality field-mask classifier | V4-048 | V4-049 FP5; V4-050 FP5 | v7 `fad366add685…` |
| G015 | QualifiedEvidenceProducer strong evidence | V4-051 | V4-052 FP5; V4-053 FP4; V4-054 FP5 | v7 `fad366add685…` |
| G016 | Stable tenant/authority IDs | V4-055 | V4-056 FP0; V4-057 FP5 | v7 `fad366add685…` |
| G017 | Checkpoint producer/immediate anchor | V4-058 | V4-059 FP1; V4-060 FP2 | v7 `fad366add685…` |
| G018 | State-root mutation detection | V4-061 | V4-062 FP3; V4-063 FP3 | v7 `fad366add685…` |
| G019 | Registry/head rollback-fork guard | V4-064 | V4-065 FP1; V4-066 FP1 | v7 `fad366add685…` |
| G020 | Recovery blocked-state bypass | V4-067 | V4-068 FP5; V4-069 FP5 | v7 `fad366add685…` |
| G021 | Repository/history migration anchor | V4-070 | V4-071 FP5; V4-072 FP5 | v7 `fad366add685…` |
| G022 | Evidence transition closed table | V4-073 | V4-074 FP5; V4-075 FP5 | v7 `fad366add685…` |
| G023 | PLATFORM_POLICY exact-condition issuer | V4-076 | V4-077 FP1; V4-078 FP5 | v7 `fad366add685…` |
| G024 | Constitutional unrecoverable boundary | V4-079 | V4-080 FP1 | v7 `fad366add685…` |
| G025 | Mechanism-proof adjudicator | V4-081 | V4-082 FP5; V4-083 FP5; V4-084 FP5 | v7 `fad366add685…` |
| G026 | T0 manifest pin/rotation/rollback | V5-001 | V5-002 FP5; V5-003 FP1; V5-004 FP1 | v7 `fad366add685…` |
| G027 | BTW pinned STH/consistency/split-view | V5-005 | V5-006 FP1; V5-007 FP1; V5-008 FP1 | v7 `fad366add685…` |
| G028 | BootstrapAuthorization->GenesisDescriptor | V5-009 | V5-010 FP5; V5-011 FP1; V5-012 FP1 | v7 `fad366add685…` |
| G029 | LAS majority linearization/CommitCertificate | V5-013 | V5-014 FP2; V5-015 FP1; V5-016 FP1 | v7 `fad366add685…` |
| G030 | LAS idempotency/retry | V5-017 | V5-018 FP2 | v7 `fad366add685…` |
| G031 | CSM semantic dependency closure | V5-019 | V5-020 FP5; V5-021 FP5 | v7 `fad366add685…` |
| G032 | Runtime dependency attestation | V5-022 | V5-023 FP4 | v7 `fad366add685…` |
| G033 | GCP escape/null/extension/vector closure | V5-024 | V5-025 FP0; V5-026 FP0; V5-027 FP5 | v7 `fad366add685…` |
| G034 | Anchor/witness rotation/freshness | V5-028 | V5-029 FP1; V5-030 FP1 | v7 `fad366add685…` |
| G035 | Time nonce/rotation | V5-031 | V5-032 FP1; V5-033 FP1 | v7 `fad366add685…` |
| G036 | Issuer rotation/parent compromise | V5-034 | V5-035 FP1; V5-036 FP1 | v7 `fad366add685…` |
| G037 | Producer temporal revocation | V5-037 | V5-038 FP1; V5-039 FP1 | v7 `fad366add685…` |
| G038 | Materiality mask/extractor integrity | V5-040 | V5-041 FP5; V5-042 FP4 | v7 `fad366add685…` |
| G039 | Tenant migration/non-inheritance | V5-043 | V5-044 FP5; V5-045 FP5 | v7 `fad366add685…` |
| G040 | Recovery semantic self-protection | V5-046 | V5-047 FP5; V5-048 FP1 | v7 `fad366add685…` |
| G041 | VerifiedStateSeal TOCTOU | V5-049 | V5-050 FP2; V5-051 FP5 | v7 `fad366add685…` |
| G042 | Constitutional Channel X attestation | V5-052 | V5-053 FP1; V5-054 FP1 | v7 `fad366add685…` |
| G043 | MTR T0 monotonic high-water | V6-001 | V6-002 FP3; V6-003 FP1 | v7 `fad366add685…` |
| G044 | Admin-domain lifecycle/quorum | V6-004 | V6-005 FP1 | v7 `fad366add685…` |
| G045 | Scoped ControllerAttestation revocation | V6-006 | V6-007 FP0; V6-008 FP1 | v7 `fad366add685…` |
| G046 | Canonical LineageGraph | V6-009 | V6-010 FP5; V6-011 FP5 | v7 `fad366add685…` |
| G047 | MTR+BTW first-seen bootstrap | V6-012 | V6-013 FP1 | v7 `fad366add685…` |
| G048 | GGS atomic constitution genesis | V6-014 | V6-015 FP2; V6-016 FP2 | v7 `fad366add685…` |
| G049 | LASHardState rollback resistance | V6-017 | V6-018 FP3; V6-019 FP1 | v7 `fad366add685…` |
| G050 | Atomic LAS StreamHeadMap CAS | V6-020 | V6-021 FP2; V6-022 FP1 | v7 `fad366add685…` |
| G051 | AIM/AuthorityInputGateway default-deny | V6-023 | V6-024 FP4; V6-025 FP5 | v7 `fad366add685…` |
| G052 | CSM-2 canonical closure | V6-026 | V6-027 FP0 | v7 `fad366add685…` |
| G053 | GCP Unicode/key collision closure | V6-028 | V6-029 FP0; V6-030 FP0 | v7 `fad366add685…` |
| G054 | WorkloadAttestation runtime identity | V6-031 | V6-032 FP4; V6-033 FP4 | v7 `fad366add685…` |
| G055 | Revocation high-water/undo | V6-034 | V6-035 FP1; V6-036 FP1 | v7 `fad366add685…` |
| G056 | LAS NonceLedger/time status | V6-037 | V6-038 FP1; V6-039 FP1 | v7 `fad366add685…` |
| G057 | Qualified producer execution proof | V6-040 | V6-041 FP4; V6-042 FP5 | v7 `fad366add685…` |
| G058 | Review-influence materiality | V6-043 | V6-044 FP5 | v7 `fad366add685…` |
| G059 | Migration RequalificationProof | V6-045 | V6-046 FP5; V6-047 FP5 | v7 `fad366add685…` |
| G060 | Signed Channel H | V6-048 | V6-049 FP0; V6-050 FP1 | v7 `fad366add685…` |
| G061 | AuthorityReadSet/derived seal | V6-051 | V6-052 FP4; V6-053 FP5 | v7 `fad366add685…` |
| G062 | Atomic COMMIT_WITH_SEAL | V6-054 | V6-055 FP2; V6-056 FP3 | v7 `fad366add685…` |
| G063 | RecoveryContext anti-replay | V6-057 | V6-058 FP1 | v7 `fad366add685…` |
| G064 | TRUST_DOMAIN_UNRECOVERABLE boundary | V6-059 | V6-060 FP5 | v7 `fad366add685…` |
| G065 | RG-1 proposed-semantics exclusion | V6-061 | V6-062 FP5 | v7 `fad366add685…` |
| G066 | Per-guard fault proof/anti-constant-reject | V6-063 | V6-064 FP5; V6-065 FP5 | v7 `fad366add685…` |
| G067 | MTR live freshness challenge | V7-001 | V7-002 FP1; V7-003 FP1; V7-004 FP3 | v7 `fad366add685…` |
| G068 | Atomic T0 successor reservation | V7-005 | V7-006 FP2; V7-007 FP1 | v7 `fad366add685…` |
| G069 | GGS hard-state rollback resistance | V7-008 | V7-009 FP3; V7-010 FP1 | v7 `fad366add685…` |
| G070 | LAS joint-consensus configuration rotation | V7-011 | V7-012 FP1; V7-013 FP3 | v7 `fad366add685…` |
| G071 | ACTIVE domain + canonical subject independence | V7-014 | V7-015 FP1; V7-016 FP1 | v7 `fad366add685…` |
| G072 | AIEP-1 broker-only authority input enforcement | V7-017 | V7-018 FP4; V7-019 FP4 | v7 `fad366add685…` |
| G073 | CSM lifecycle/AIM resolution | V7-020 | V7-021 FP5; V7-022 FP5 | v7 `fad366add685…` |
| G074 | Universal revocation rollback protection | V7-023 | V7-024 FP1 | v7 `fad366add685…` |
| G075 | Runtime attestation claim-mode restriction | V7-025 | V7-026 FP4 | v7 `fad366add685…` |
| G076 | Schema provenance/RG-1 | V7-027 | V7-028 FP5; V7-029 FP5 | v7 `fad366add685…` |
| G077 | External effect execution/reconciliation | V7-030 | V7-031 FP6; V7-032 FP6; V7-033 FP6 | v7 `fad366add685…` |
| G078 | Migration object completeness | V7-034 | V7-035 FP5 | v7 `fad366add685…` |
| G079 | ReviewPresentationSchema materiality | V7-036 | V7-037 FP5 | v7 `fad366add685…` |
| G080 | Trust-loss declaration boundary | V7-038 | V7-039 FP1; V7-040 FP5 | v7 `fad366add685…` |
| G081 | Time decision-preseal binding | V7-041 | V7-042 FP1 | v7 `fad366add685…` |
| G082 | Authorized T0 successor reservation | V8-001 | V8-002 FP1; V8-003 FP2; V8-004 FP5 | v8 `58e95ca8cc8b…` |
| G083 | MTR response high-water/challenge rollback | V8-005 | V8-006 FP3; V8-007 FP1; V8-008 FP3 | v8 `58e95ca8cc8b…` |
| G084 | GGS-3 configuration rotation | V8-009 | V8-010 FP3; V8-011 FP1 | v8 `58e95ca8cc8b…` |
| G085 | Attested AuthorityInputGateway | V8-012 | V8-013 FP4; V8-014 FP1 | v8 `58e95ca8cc8b…` |
| G086 | Complete decision-preseal context | V8-015 | V8-016 FP5; V8-017 FP1 | v8 `58e95ca8cc8b…` |
| G087 | Attested SPM generator | V8-018 | V8-019 FP4; V8-020 FP5 | v8 `58e95ca8cc8b…` |
| G088 | CSM applicable-scope resolution | V8-021 | V8-022 FP5; V8-023 FP5 | v8 `58e95ca8cc8b…` |
| G089 | Effect executor revocation/reconciliation | V8-024 | V8-025 FP1; V8-026 FP6; V8-027 FP6 | v8 `58e95ca8cc8b…` |
| G090 | Migration destination-policy freshness | V8-028 | V8-029 FP2; V8-030 FP5 | v8 `58e95ca8cc8b…` |
| G091 | Inherited-v4 packet completeness | V8-031 | V8-032 FP5 | v8 `58e95ca8cc8b…` |
| G092 | CSRULE-2 revoked-specific anti-fallback | V9-001 | V9-002 FP5; V9-003 FP5; V9-004 FP5 | v9 `0948ed0e83d9…` |
| G093 | ANYScopePermission registration | V9-005 | V9-006 FP5; V9-007 FP5 | v9 `0948ed0e83d9…` |
| G094 | LAS-3 idempotency-ledger rotation continuity | V9-008 | V9-009 FP3; V9-010 FP2 | v9 `0948ed0e83d9…` |
| G095 | GGS-3 CTS-1 JOINT race | V9-011 | V9-012 FP2; V9-013 FP2 | v9 `0948ed0e83d9…` |
| G096 | LAS-3 CTS-1 JOINT race | V9-014 | V9-015 FP2; V9-016 FP2 | v9 `0948ed0e83d9…` |
| G097 | SGHVP-1 generator historical validity | V9-017 | V9-018 FP1; V9-019 FP1; V9-020 FP5 | v9 `0948ed0e83d9…` |
| G098 | Effect reconciler independence | V9-021 | V9-022 FP1; V9-023 FP6 | v9 `0948ed0e83d9…` |
| G099 | LAS-3 semantic-version identity | V9-024 | V9-025 FP5 | v9 `0948ed0e83d9…` |
| G100 | CSM-3 multi-entry scoped semantic envelope | V10-001 | V10-002 FP0; V10-003 FP5 | v10 `2e85384f7593…` |
| G101 | CSRULE-2 valid successor/replacement mapping | V10-004 | V10-005 FP5; V10-006 FP5 | v10 `2e85384f7593…` |
| G102 | Cross-lineage transition control | V10-007 | V10-008 FP5 | v10 `2e85384f7593…` |
| G103 | ANYScopePermission constitutional boundary | V10-009 | V10-010 FP5; V10-011 FP5 | v10 `2e85384f7593…` |
| G104 | LAS-3 STC-1 continuity | V10-012 | V10-013 FP3; V10-014 FP5 | v10 `2e85384f7593…` |
| G105 | GGS-3 STC-1 continuity | V10-015 | V10-016 FP3; V10-017 FP5 | v10 `2e85384f7593…` |
| G106 | CTS-2 JOINT/ACTIVATE exact binding | V10-018 | V10-019 FP2; V10-020 FP2; V10-021 FP5 | v10 `2e85384f7593…` |
| G107 | Blind packet semantic projection integrity | V10-022 | V10-023 FP5 | v10 `2e85384f7593…` |
| G108 | CSM-4 full scope and canonical mapping objects | V11-001 | V11-002 FP5; V11-003 FP5 | v11 `3d6a0820d851…` |
| G109 | CSRULE-3 cross-lineage mapped traversal | V11-004 | V11-005 FP5; V11-006 FP5 | v11 `3d6a0820d851…` |
| G110 | Successor graph determinism | V11-007 | V11-008 FP5; V11-009 FP5 | v11 `3d6a0820d851…` |
| G111 | ANY reevaluation blocks Smax fallback | V11-010 | V11-011 FP5; V11-012 FP5 | v11 `3d6a0820d851…` |
| G112 | AIM-2/CSRULE-3 single resolution path | V11-013 | V11-014 FP4 | v11 `3d6a0820d851…` |
| G113 | RBP-1 post-snapshot write freeze | V11-015 | V11-016 FP2; V11-017 FP3 | v11 `3d6a0820d851…` |
| G114 | STC-2 unique linearized transfer certificate | V11-018 | V11-019 FP2; V11-020 FP5 | v11 `3d6a0820d851…` |
| G115 | CTS-3 exact JOINT/ACTIVATE binding | V11-021 | V11-022 FP2; V11-023 FP5 | v11 `3d6a0820d851…` |
| G116 | BSP-1 residual prior-review metadata rejection | V11-024 | V11-025 FP5 | v11 `3d6a0820d851…` |
| G117 | Full-scope collision isolation | V11-026 | V11-027 FP5 | v11 `3d6a0820d851…` |
| G118 | current semantic_state_sequence binding | V12-001 | V12-002 FP1; V12-003 FP5 | v12 `8250f35acb37…` |
| G119 | AIM-3 append-only descriptor authority | V12-004 | V12-005 FP5; V12-006 FP5 | v12 `8250f35acb37…` |
| G120 | ResolverPolicy/implementation binding | V12-007 | V12-008 FP4; V12-009 FP5 | v12 `8250f35acb37…` |
| G121 | resolver-time ANY revalidation | V12-010 | V12-011 FP1; V12-012 FP5 | v12 `8250f35acb37…` |
| G122 | explicit semantic heads in LAS authority root | V12-013 | V12-014 FP5; V12-015 FP3 | v12 `8250f35acb37…` |
| G123 | RBP-2 semantic registry freeze | V12-016 | V12-017 FP2; V12-018 FP5 | v12 `8250f35acb37…` |
| G124 | one barrier one rotation | V12-019 | V12-020 FP2; V12-021 FP2 | v12 `8250f35acb37…` |
| G125 | ScopeReplacementTruthTable | V12-022 | V12-023 FP5; V12-024 FP5 | v12 `8250f35acb37…` |
| G126 | DecisionPresealContext-v3 semantic binding | V12-025 | V12-026 FP1; V12-027 FP2 | v12 `8250f35acb37…` |
| G127 | BSP-2 prior-outcome blindness | V12-028 | V12-029 FP5; V12-030 FP5 | v12 `8250f35acb37…` |
| G128 | GCC-1 consolidated guard compilation | V12-031 | V12-032 FP5; V12-033 FP5 | v12 `8250f35acb37…` |
| G129 | ANY_SCOPE_PERMISSION_AMENDMENT authority | V12-034 | V12-035 FP5 | v12 `8250f35acb37…` |
| G130 | PDF non-authoritative projection boundary | V12-036 | V12-037 FP5 | v12 `8250f35acb37…` |
