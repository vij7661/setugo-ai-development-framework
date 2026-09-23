# R8 v15-r1 — SPG-1 Candidate Qualification Preregistration

Status: **PREREGISTERED_CONSTRUCTION_TEST_PLAN — NONAUTHORITATIVE**
Authority effect: **NONE**

Frozen semantic source:
- semantic candidate commit: `c721b38cf8b00294797300b526596ce723a47ff8`
- semantic freeze: `R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE-001`
- current gate: `SCHEMA_ARTIFACT_FREEZE_BLOCKED_PENDING_SPG_QUALIFICATION`

## 1. Objective

Construct and falsify a candidate enforcement layer for the inherited schema-provenance requirements before any authority-bearing executable schema is emitted.

This candidate does **not** satisfy SPG-1 qualification by itself.

## 2. Frozen inherited requirements

### R8V7-I030 — SPM-1
Every machine-readable schema element generated for schema freeze must have provenance containing:
- schema artifact ID/digest;
- JSON pointer / field / rule ID;
- semantic purpose;
- authoritative source design ID(s);
- source commit/blob;
- transformation/generator identity;
- generator RuntimeManifest digest;
- reviewer status where required.

### R8V7-I031 — RG-1
Schema freeze rejects:
- any element with no SPM-1 entry;
- any element whose only source is non-authoritative;
- any manual rule with no governed incorporation source.

Failure: `UNAUTHORIZED_SEMANTIC_SOURCE`.

### R8V8-I020 — SPG-1 enrollment
Any generator that emits schema artifacts or SPM-1 entries must be enrolled as `SchemaProvenanceGenerator` and bound to:
- generator_id;
- executable/image digest;
- RuntimeManifest;
- WorkloadAttestation policy;
- allowed input design artifacts;
- allowed output schema classes;
- signing credential;
- revocation status.

### R8V8-I021 — output proof
Each schema/SPM output must bind:
- exact input design commit/blob IDs;
- generator executable/runtime digest;
- generator workload attestation;
- generation event ID;
- output schema digest;
- provenance-map digest;
- signature.

Unattested/drifted/unregistered provenance is invalid.

## 3. Candidate scope

The first candidate is a **provenance coverage validator only**.

It may:
- validate a proposed schema plan;
- enumerate every schema JSON node pointer deterministically;
- verify exact provenance coverage;
- verify source refs against the frozen allowlist;
- reject non-authoritative-only sources;
- reject missing generator/runtime/attestation/signing metadata;
- emit a NONAUTHORITATIVE validation report.

It may not:
- claim SPG-1 qualification;
- mint a schema freeze;
- create a workload attestation;
- fabricate a signature;
- substitute a transport digest for GCP-1 authority digest;
- authorize implementation.

## 4. Required deterministic checks

- **SPG-C01** root and every recursively addressable schema node have provenance.
- **SPG-C02** no provenance pointer names a node absent from the schema.
- **SPG-C03** each provenance entry has non-empty semantic purpose and source design IDs.
- **SPG-C04** every source `path + blob` exists in the frozen allowlist.
- **SPG-C05** at least one authoritative source exists for every schema node.
- **SPG-C06** semantic candidate commit equals the frozen candidate.
- **SPG-C07** schema class is explicitly allowed.
- **SPG-C08** generator_id, executable digest, RuntimeManifest digest, WorkloadAttestation digest, signing credential ID, and generation_event_id are present.
- **SPG-C09** unknown top-level plan fields reject.
- **SPG-C10** duplicate provenance pointers reject.
- **SPG-C11** arrays are traversed through schema structure, including `items`, `prefixItems`, `oneOf`, `anyOf`, `allOf`, `required`, and enum values as ordinary nodes.
- **SPG-C12** report is deterministic for identical input bytes.

## 5. Preregistered positive controls

- **SPG-P01** minimal object schema with full root/property provenance -> VALID_CANDIDATE_PLAN.
- **SPG-P02** nested object/array schema with full coverage -> VALID_CANDIDATE_PLAN.
- **SPG-P03** one node with two authoritative source refs -> VALID_CANDIDATE_PLAN.
- **SPG-P04** identical input evaluated twice -> byte-identical canonical report.

## 6. Preregistered adversarial cases

- **SPG-N01** missing one node provenance -> PROVENANCE_COVERAGE_MISSING.
- **SPG-N02** provenance pointer does not exist -> PROVENANCE_POINTER_UNKNOWN.
- **SPG-N03** duplicate pointer -> PROVENANCE_POINTER_DUPLICATE.
- **SPG-N04** source blob/path not in frozen allowlist -> UNAUTHORIZED_SEMANTIC_SOURCE.
- **SPG-N05** only non-authoritative source -> UNAUTHORIZED_SEMANTIC_SOURCE.
- **SPG-N06** candidate commit differs -> FROZEN_CANDIDATE_MISMATCH.
- **SPG-N07** schema class outside enrolled output classes -> OUTPUT_SCHEMA_CLASS_UNAUTHORIZED.
- **SPG-N08** missing RuntimeManifest digest -> GENERATOR_BINDING_INCOMPLETE.
- **SPG-N09** missing WorkloadAttestation digest -> GENERATOR_BINDING_INCOMPLETE.
- **SPG-N10** missing signing credential ID -> GENERATOR_BINDING_INCOMPLETE.
- **SPG-N11** unknown plan field -> PLAN_SCHEMA_INVALID.
- **SPG-N12** candidate attempts `qualified=true` or authority-bearing disposition -> PLAN_SCHEMA_INVALID.

## 7. Qualification boundary

Passing these tests establishes only that the candidate provenance validator enforces the preregistered structural rules.

Actual SPG-1 qualification remains blocked until there is independently verifiable:
- enrolled SchemaProvenanceGenerator registry state;
- exact executable/runtime identity;
- qualified WorkloadAttestation;
- allowed input/output binding;
- signing credential binding;
- independent review of the candidate and qualification evidence.

No schema artifact may be frozen before that boundary closes.
