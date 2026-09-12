# V9 Composite Precedence and Coverage Map

Status: **PROPOSED V9 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 base -> V6 hardening -> V7 hardening/map -> V8 hardening/map -> V9 hardening/map`

V9 candidate build MUST include all active prior artifacts plus:

- `standards/conversation-drift-parent-child-impact-control-v9-hardening.md`
- this map
- `experiments/governed-platform/conversation-drift-parent-child-falsification-v9-extension.md`

The CompositePrecedenceAudit is authoritative for map completeness, not this prose table alone.

## 2. V8 findings narrowed by V9

| Prior area | V9 disposition |
|---|---|
| V8-C02 precedence extraction | `NARROWED_BY V9-C02` — triple-source NormativeClauseRegistry + adversarial extraction corpus |
| V8-C03 genesis trust | `NARROWED_BY V9-C03` — explicit GenesisQualificationRecord gate |
| V8-C04 consequence/effector default deny | `NARROWED_BY V9-C04/C05/C13` — independent consequence classification + mandatory egress + enforcement attestation |
| V8-C05 emergency constraints | `NARROWED_BY V9-C08` — executable trigger registry + atomic invocation ledger |
| V8-C06 predicate auditor independence | `NARROWED_BY V9-C07` — proof against every root-threshold-capable subset |
| V8-C07 OUTCOME_UNKNOWN | `NARROWED_BY V9-C06` — observation authority registry + freshness/independence |
| V8-C08 grandfathering | `NARROWED_BY V9-C10` — CriterionMigrationRegistry; default non-grandfatherable |
| V8-C10 policy rebind | `NARROWED_BY V9-C11` — WSA LiveAuthorityObjectInventory exact-set comparison |
| V8-C11 cross-standard ordering | `NARROWED_BY V9-C12` — CausalEvidenceRegistry and ambiguity fail-closed |
| V8-C13 evidence profiles | `NARROWED_BY V9-C09` — CaseRegistry set equality + executor cannot remove profiles |
| V8-C14 compound positive | `NARROWED_BY V9-C14` — per-mechanism negative/positive/compound/recovery coverage gate |
| V8-C15 frozen interpretation | `NARROWED_BY V9-C15` — expanded frozen registry digest set |
| V8-M06 human section traceability | `NARROWED_BY V9-C16` — machine-only legacy keys |

All other V8/V7/V6/V5 rules remain active unless mechanically dispositioned by CompositePrecedenceAudit.

## 3. Mechanism coverage IDs

Critical mechanism IDs for V9 qualification:

- `MECH-PRECEDENCE`
- `MECH-GENESIS`
- `MECH-ROOT-REGISTRY`
- `MECH-CONSEQUENCE-CLASS`
- `MECH-EGRESS`
- `MECH-EFFECTOR-FENCING`
- `MECH-PROVIDER-OBSERVATION`
- `MECH-PREDICATE-INDEPENDENCE`
- `MECH-EMERGENCY`
- `MECH-EVIDENCE-PROFILE`
- `MECH-GRANDFATHER`
- `MECH-REBIND-INVENTORY`
- `MECH-CROSS-STANDARD-ORDERING`
- `MECH-TEST-ORACLE`
- `MECH-GEL-WAS`
- `MECH-WSA-DGV`
- `MECH-RCB-PROVENANCE`
- `MECH-DISCLOSURE-APPROVAL`

Every mechanism must satisfy V9-C14 coverage categories before execution freeze.

## 4. Evidence-profile additions

V9 adds mandatory evidence profiles:

- `EP-NORMATIVE-EXTRACTION`
- `EP-GENESIS-QUALIFICATION`
- `EP-CONSEQUENCE-CLASSIFICATION`
- `EP-EGRESS-MEDIATION`
- `EP-OBSERVATION-AUTHORITY`
- `EP-PREDICATE-ROOT-INDEPENDENCE`
- `EP-EMERGENCY-INVOCATION`
- `EP-CASE-REGISTRY`
- `EP-CRITERION-MIGRATION`
- `EP-LIVE-OBJECT-INVENTORY`
- `EP-CAUSAL-EVIDENCE`
- `EP-EFFECTOR-ATTESTATION`
- `EP-MECHANISM-COVERAGE`

Every WDPC-153 onward case has an explicit profile mapping in the V9 extension. Prior cases referenced by V9 tightening must inherit the new profile in addition to their V8 profile set.

## 5. Prior case remapping

The following earlier cases are explicitly tightened by V9 and MUST include these additional profiles:

- WDPC-06 -> `EP-CRITERION-MIGRATION`
- WDPC-69 -> `EP-LIVE-OBJECT-INVENTORY`
- WDPC-96,137,148 -> `EP-GENESIS-QUALIFICATION`
- WDPC-101,119,120,140 -> `EP-PREDICATE-ROOT-INDEPENDENCE`
- WDPC-116,138,152 -> `EP-CONSEQUENCE-CLASSIFICATION + EP-EGRESS-MEDIATION + EP-EFFECTOR-ATTESTATION`
- WDPC-122,141,151 -> `EP-OBSERVATION-AUTHORITY`
- WDPC-126,139,150 -> `EP-EMERGENCY-INVOCATION`
- WDPC-136,149 -> `EP-NORMATIVE-EXTRACTION`
- WDPC-143 -> `EP-CAUSAL-EVIDENCE`
- WDPC-144 -> `EP-CRITERION-MIGRATION`
- WDPC-146 -> `EP-LIVE-OBJECT-INVENTORY`
- WDPC-147 -> `EP-CASE-REGISTRY`
- WDPC-142 -> `EP-MECHANISM-COVERAGE`

## 6. Mechanical completeness rule

Candidate build/freeze compares:

1. parsed case IDs from all active falsification files;
2. CaseRegistry IDs;
3. CaseEvidenceProfileMap IDs;
4. endpoint references from all cases;
5. EndpointSchemaRegistry IDs;
6. normative clause/reference manifests;
7. active-clause dispositions.

Any set mismatch is a signed fail-closed endpoint. No reviewer discretion can waive it.

## 7. Authority limitation

This map is design evidence only.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`