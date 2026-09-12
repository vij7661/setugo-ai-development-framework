# Workflow Drift and Parent-Child Impact Control — V24 Bootstrap and Admission-Perimeter Enforcement Addendum

Status: **PROPOSED V24 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This addendum adopts the platform V24 bootstrap/perimeter enforcement rules for WDPC.

## V24-B01 — WDPC admission is deny-by-default at authority boundaries

WDPC admission is enforced at every authority sink/effect boundary. Current qualifying admission is required for participating writers/effectors, authority decision inputs, evidence/source classes, controls/predicates, and other authority-affecting identities.

Discovery/inventory completeness alone cannot establish this boundary. For sinks where non-admitted direct write/effect remains physically/equivalently possible, the affected authority path remains `INSUFFICIENT_EVIDENCE` and cannot qualify.

## V24-B02 — WDPC perimeter enforcement records

Every material WDPC authority sink/effect family requires a current independently qualified `AdmissionPerimeterEnforcementRecord` binding exact sink identity, admitted writer set, IAM/capability/ACL or equivalent enforcement configuration, credential/recovery paths, deny-by-default result, independent evidence, and drift/currentness.

Credential/configuration/perimeter drift stales the record before further authority apply.

## V24-B03 — WDPC bootstrap completeness authority set

The V24 governance-generation genesis binds exact initial completeness authorities, their powers, thresholds/diversity, keys/identities, subject classes, external source contracts, and declared control-domain separation in `BootstrapCompletenessAuthoritySet`.

Those authorities are established by the out-of-band generation bootstrap. They do not self-qualify using the descendant V24 completeness machinery they initialize.

## V24-B04 — Required external independence cannot be satisfied by relabeling root

Where a WDPC completeness predicate requires independence outside the root operational set, the genesis bootstrap must contain the qualifying external domain. Root guardians/operators are not automatically independent completeness authorities.

If the required external domain/source is unavailable or its independence cannot be established, affected completeness remains `INSUFFICIENT_EVIDENCE`.

## V24-B05 — Bootstrap source and lineage continuity

Bootstrap completeness subject classes have exact source/evidence contracts. Candidate-self-report alone cannot satisfy an independent completeness source requirement.

Ordinary IUDA lineages must descend from the bootstrap set or from later properly governed V24 additions/rotations. Null-parent reset, hidden sibling bootstrap, or in-generation power broadening is rejected under the applicable root/meta-governance endpoint.

## V24-B06 — Apply-time enforcement

The WDPC guarded writer/effector revalidates current `AdmissionPerimeterEnforcementRecord`, exact admission/completeness records, and relevant IAM/capability state atomically/CAS/fencing with authority apply.

A relevant perimeter change after kernel decision issuance stales the decision and blocks apply.

## V24-B07 — Review/freeze rule

The clean V24 review must attack discovery-only admission, direct unadmitted sink access, perimeter drift, IUDA bootstrap recursion, root-as-independent relabeling, self-source bootstrap proofs, and hidden IUDA lineage resets.

This artifact is design-only and grants no implementation/falsification/execution freeze.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
