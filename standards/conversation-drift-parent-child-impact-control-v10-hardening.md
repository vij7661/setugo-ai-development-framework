# Workflow Drift and Parent-Child Impact Control — V10 Hardening Overlay

Status: **PROPOSED V10 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V10-C01 — Exact base binding

V10 is an additive hardening layer over exact V9 candidate:

- V9 candidate commit: `c605b4540fcfaa053072fcb8fee6c281c8b44121`
- V9 hardening blob: `5a2c6a362c748bafef2a6a09e7af78c58831eab3`
- V9 precedence/coverage blob: `79b8e328d4f7d1b138fd5d60f34489e5da0bb056`
- V9 falsification extension blob: `9319fd789d1a0ba28cb4a43a4269c69a94719c91`

V5–V9 remain active only as mechanically resolved by the composite precedence machinery plus this V10 overlay. Where V10 is stricter, V10 controls.

V10 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V10-C02 — Exact review-packet artifact provenance

A review cannot qualify against a candidate artifact whose embedded bytes cannot be proven to correspond to the claimed frozen source artifact.

Every externally delivered review packet MUST contain a signed `ReviewPacketManifest` with, for every candidate artifact:

- repository/source identity;
- exact candidate commit;
- repository path;
- authoritative Git blob SHA or equivalent content-addressed source digest;
- byte length;
- SHA-256 of the exact embedded bytes;
- packet-local artifact ordinal;
- role `CANDIDATE | REFERENCE_ONLY`;
- provenance acquisition method;
- manifest predecessor digest;
- packet ID;
- packet-authority signature.

The packet builder MUST construct candidate artifacts from exact source bytes, not a presentation-normalized rendering.

For a Git-backed artifact, packet qualification requires:

`git_blob_sha(embedded_bytes) == authoritative_source_blob_sha`

A decoded/normalized representation whose bytes do not reproduce the source blob is not an exact candidate artifact and MUST NOT be represented as such.

If any candidate artifact fails the exact-byte check, packet issuance is blocked with `REVIEW_PACKET_PROVENANCE_MISMATCH`.

Reference-only material may use separately declared normalized representations, but must not be confused with candidate bytes.

A reviewer output based on a packet that later proves provenance-mismatched is preserved as historical feedback but is ineligible as exact-candidate review evidence.

## V10-C03 — NCR coverage is explicitly corpus-bounded

V9 NormativeClauseRegistry remains required, but V10 prohibits claiming that finite extraction proves semantic completeness over all possible future natural-language formulations.

`NormativeCoverageStatement` MUST state:

- exact extraction algorithm/version;
- exact adversarial corpus/version;
- known normative-form categories covered;
- known out-of-scope or unproven categories;
- corpus expansion history;
- latest independent corpus review identity;
- candidate binding;
- result `BOUNDED_COVERAGE_ACCEPTED | COVERAGE_INSUFFICIENT`.

The freeze report MUST say that NCR coverage is **bounded by the frozen extraction algorithm and adversarial corpus**, not absolute semantic completeness.

A new normative-evasion pattern discovered after freeze becomes a new falsification input and cannot retroactively turn an earlier bounded result into an absolute guarantee.

If the freeze report claims complete semantic coverage without the bounded statement, emit `NORMATIVE_COVERAGE_OVERCLAIM_REJECTED`.

## V10-C04 — CompositeAuditAuthority independence

`CompositeAuditAuthority` (`CAA`) must be independent of candidate-authoring principals and beneficiaries.

RGA maintains a `CompositeAuditIndependenceRecord` binding:

- candidate commit/artifact set;
- candidate authoring principals and service identities;
- CAA principals/keys;
- control, administrative, credential-admin, recovery-admin, beneficial-owner and service-account alias domains;
- independence proof;
- activation sequence;
- expiry/recheck sequence;
- root-governed signature.

No candidate author, candidate-author-controlled service account, or principal sharing a disallowed control/admin/credential/recovery/beneficial-owner domain may satisfy the CAA quorum for that candidate.

Failure emits `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED` and no precedence/NCR PASS may qualify.

CAA independence is rechecked at candidate freeze and whenever the candidate-author set or CAA control facts change.

## V10-C05 — Aggregate emergency-scope ceiling

Per-policy emergency invocation ceilings remain required. V10 adds a root-governed `AggregateEmergencyScopeRegistry` and durable `AggregateEmergencyLedger`.

The aggregate registry defines, per workflow/root/consequence class/time window:

- maximum simultaneous emergency policies;
- maximum aggregate invocation count;
- maximum aggregate duration;
- maximum aggregate affected action classes;
- maximum aggregate irreversible/external consequence budget;
- explicitly forbidden policy combinations;
- reset/decay rules;
- root-governed version and activation sequence.

Before any emergency invocation is committed, the ledger atomically computes the resulting aggregate state across all active emergency policies.

If the aggregate limit would be exceeded, emit `AGGREGATE_EMERGENCY_LIMIT_BLOCKED` even when every individual emergency policy is valid and within its own local budget.

Multiple narrow policies cannot compose into authority that one policy could not hold alone.

## V10-C06 — Genesis qualification must be live at every freeze

A `GenesisQualificationRecord` is not checked only at initial bootstrap.

Every candidate freeze, root-governance rotation, and terminal qualification transition MUST revalidate:

- record status is `ACCEPTED_OUT_OF_BAND_ASSUMPTION`;
- record has not expired;
- scope covers the exact root/key-storage architecture currently active;
- guardian/notary/control facts have not materially changed;
- required independent manual-review evidence remains valid where policy requires it.

Missing, expired, scope-mismatched, or stale genesis qualification emits `GENESIS_QUALIFICATION_STALE` and blocks freeze/terminal transition.

No prior accepted record is implicitly evergreen.

## V10-C07 — Effector implementation change invalidates attestation

Every `EffectorEnforcementAttestation` is bound to exact enforcement implementation/configuration digests.

Any change to:

- token-validation implementation;
- gateway implementation;
- downstream provider adapter;
- credential path;
- network/egress mediation;
- consequence-classification binding;
- fencing schema/version;
- provider endpoint/capability affecting enforcement;

automatically places the effector in `RE_ATTESTATION_REQUIRED`.

Until a new independent attestation is accepted, dispatch is blocked with `EFFECTOR_REATTESTATION_REQUIRED`.

A deployment pipeline MUST compare active deployment digests with attested digests before enabling consequential traffic.

## V10-C08 — Independent-review isolation is an evidence property

A reviewer being labeled `R2` or `R3` does not prove independence.

Every independent-review result requires a signed `ReviewerIndependenceRecord` binding:

- reviewer role/identity;
- packet ID/candidate;
- exact delivered context digest;
- allowed source set;
- prohibited source set;
- reviewer declaration of sources actually used;
- platform-observed context provenance where available;
- contamination status `CLEAN | CONTAMINATED | INSUFFICIENT_EVIDENCE`;
- contamination reason/event IDs;
- deciding isolation authority.

If the review output explicitly references, relies on, summarizes, or treats another review as a baseline before cross-review/adjudication authorization, the review is `CONTAMINATED`.

A contaminated review:

- is preserved unchanged;
- may be used as engineering/falsification feedback;
- cannot count toward independent-review thresholds;
- cannot be relabeled clean by later agreement;
- requires a new isolated review of the current exact candidate if independent R2/R3 evidence is still required.

Violation emits `INDEPENDENT_REVIEW_CONTAMINATED`.

## V10-C09 — R3 role binding

Where policy requires `R3`, the review evidence must carry role `R3` and a `ReviewerIndependenceRecord` for the exact candidate.

An R3 review that is AI-generated remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` unless policy explicitly permits model-generated independent review for that gate.

A review that both claims packet-only isolation and states that it used a prior review as baseline is deterministically contaminated, regardless of the quality of its technical findings.

## V10-C10 — Frozen interpretation extends to review provenance

The frozen-start interpretation set now includes:

- ReviewPacketManifest digest;
- reviewer-context digest;
- ReviewerIndependenceRecord schema/version;
- CAA independence record;
- NormativeCoverageStatement;
- AggregateEmergencyScopeRegistry;
- live GenesisQualificationRecord;
- active EffectorEnforcementAttestation digests.

Later provenance repairs, reviewer relabeling, or registry changes cannot retroactively convert an ineligible review/run into qualifying evidence.

## V10-C11 — New endpoints

V10 adds owner-bound endpoint schemas for:

- `REVIEW_PACKET_PROVENANCE_MISMATCH`
- `NORMATIVE_COVERAGE_OVERCLAIM_REJECTED`
- `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED`
- `AGGREGATE_EMERGENCY_LIMIT_BLOCKED`
- `GENESIS_QUALIFICATION_STALE`
- `EFFECTOR_REATTESTATION_REQUIRED`
- `INDEPENDENT_REVIEW_CONTAMINATED`

All must exist in EndpointSchemaRegistry before associated cases execute.

## V10-C12 — Freeze rule

V10 cannot freeze for execution while any unresolved Critical/High design finding remains under the governing review policy.

A contaminated or provenance-ineligible review cannot satisfy an independent-review threshold.

AI/model engineering feedback remains evidence-only unless the active policy explicitly qualifies that evidence class.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
