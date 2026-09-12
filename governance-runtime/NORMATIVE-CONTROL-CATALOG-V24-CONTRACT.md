# V24 Normative Control Catalog Construction Contract

Status: `IMPLEMENTATION_CONSTRUCTION — NON-AUTHORITATIVE`

Authority effect: `NONE_EVIDENCE_ONLY`

This contract implements the first mechanism of V24-I1. It is subordinate to frozen V24 design candidate `db9e4b349fd26e128f4486878a4af64929000a7c` and specifically to P24-16, P24-R06 and P24-R07.

## 1. Purpose

Prevent a false-green in which an incomplete or stale set of governance prose is treated as a complete machine-readable normative catalog.

The mechanism is closed-world over three explicit inputs:

1. `NormativeArtifactManifest` — exact artifact paths/blob identities and explicit clause locators;
2. `NormativeControlCatalog` — machine-readable descriptors for every declared authoritative clause locator;
3. `LegacyNormativeControlQualification` — explicit status for every inherited legacy clause in the independently supplied legacy inventory.

No natural-language parser may silently expand or repair these inputs at qualification time.

## 2. Artifact classifications

Every artifact in the manifest is exactly one of:

- `AUTHORITATIVE_DESCRIPTOR_REQUIRED`
- `NONAUTHORITATIVE_REFERENCE`

An authoritative artifact must declare at least one exact required clause locator. A reference artifact may not declare normative locators and may not receive a `ControlDescriptor`.

This is a construction mechanism only. Actual V24 activation additionally requires admission/completeness qualification under the later V24 slices.

## 3. Exact artifact binding

Each manifest artifact binds:

- repository-relative path;
- exact Git blob SHA;
- classification;
- explicit required clause locators.

The validator recomputes Git blob identity from local bytes and fails closed on mismatch, missing artifact, non-UTF-8 normative content, duplicate artifact path, unsafe path, or invalid classification.

## 4. Exact clause binding

Each required clause locator binds:

- stable locator ID;
- exact Markdown heading;
- SHA-256 of the exact section from that heading through the next same/higher-level heading.

A missing, duplicated, moved-without-update, or byte-changed clause fails qualification.

This clause digest is additional construction hardening beyond P24-R06's minimum exact locator requirement.

## 5. ControlDescriptor minimum fields

Every descriptor binds:

- `control_id`;
- `normative_artifact_path`;
- `normative_artifact_blob_sha`;
- `clause_locator`;
- `clause_sha256`;
- `inherited_predecessor_control_ids`;
- `authority_bearing_predicate_ids`;
- `phase_severity_endpoint_mappings`;
- `applicability_rules`;
- `required_proof_fields`;
- `protected_mutation_strength_class`;
- `effective_generation`;
- `effective_sequence`.

Every required manifest clause locator must map to exactly one descriptor. Duplicate control IDs, zero mappings, multi-mappings, generation drift, artifact/blob drift, or locator drift fail closed.

## 6. LegacyNormativeControlQualification

The legacy input contains:

- `legacy_clause_inventory` — independently supplied exact legacy artifact/locator identities;
- `records` — exactly one disposition per inventory identity.

Allowed dispositions:

- `ACTIVE_MAPPED` — requires a target control ID that exists in the current catalog;
- `SUPERSEDED` — must not claim a current target;
- `REFERENCE_ONLY` — must not claim a current target.

An inventory item without a record, a record outside the inventory, duplicate identity, unknown target, or malformed status fails qualification.

The validator intentionally does not infer legacy status from prose. Repository lineage/active-clause maps must be converted into an explicit inventory/qualification artifact before I1 can be considered complete.

## 7. Result states

- `NORMATIVE_CONTROL_CATALOG_QUALIFIED`
- `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`

A positive result is construction evidence only. It does not admit the catalog into an active governance generation, establish IUDA independence, prove completeness, or grant implementation/release/production authority.

## 8. Preserved false-green protections

The validator must reject at minimum:

- missing descriptor for a declared authoritative clause;
- descriptor attached to a non-authoritative reference artifact;
- artifact Git blob mismatch;
- clause digest mismatch;
- duplicate control ID;
- duplicate or multiply mapped locator;
- generation mismatch;
- path traversal/escape;
- incomplete legacy inventory qualification;
- active legacy mapping to an unknown current control;
- non-active legacy clause that improperly claims a current target.

## 9. I1 construction boundary

The current mechanism is not enough to exit I1.

I1 remains incomplete until the repository-bound V5–V24 normative artifact manifest, exact active/superseded/reference legacy clause inventory, machine-readable descriptor bundle, and legacy qualification mapping are built and validated against exact repository bytes.

No gateway, sink, capability, completeness, endpoint, proof-view, or runtime-authority behavior is changed by this mechanism.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
