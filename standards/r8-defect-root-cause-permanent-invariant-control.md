# R8 Defect Root-Cause and Permanent-Invariant Control

Status: SUCCESSOR-3 GOVERNANCE DESIGN — NOT MERGE AUTHORITY

## Purpose

Repeated independent-review findings showed that repairing one literal defect at a time is insufficient. A finding is closed only when the defect family is represented as a permanent invariant with a regression/falsification family.

This document applies to the post-SG1 convergence/successor line and to future API-governed platform work.

## Permanent invariant families

### 1. Review grammar, not punctuation patches
- Review parsing is structural.
- Critical/High findings outside their dedicated sections are rejected by grammar, not by an allowlist of literal punctuation examples.
- C/D headings are exact.
- Controlled activation/authority declarations are reserved semantic fields and may not be embedded in headings or prose.
- Harmless presentation differences must not change semantic meaning.
- Contradictory or ambiguous authority declarations fail closed.

### 2. Controlled authority fields
- Activation and broader-authority declarations have one parser owner.
- Missing, duplicate, contradictory, embedded, malformed, or relocated declarations are non-promotable.
- Formatting tolerance must never become semantic ambiguity.

### 3. Workflow command contracts
- Every governance workflow command must be executable as written.
- Static checks must validate command/CLI compatibility, not merely search for keywords.
- Exact-artifact identity checking belongs in the exact-binding preflight path unless another component is explicitly assigned that responsibility.

### 4. Canonical semantic verification
- Generated semantic inventories are not authoritative merely because their self-hash is internally consistent.
- Verification must recompute and compare the entire canonical semantic result.
- Historical Stage1-bound evidence must remain explicitly distinguished from current candidate evidence.

### 5. Complete evidence identity
A strict evidence verification tuple is atomic:
- schema
- archive format
- run
- job
- workflow
- exact candidate/head
- exact inputs
- archive digest
- activation-verification evidence
- authority effect

Adding/checking only a subset is not sufficient lineage proof.

### 6. Queue/ledger completeness
- Every governed Q-task file must have one machine-readable ledger record or an explicit governed exemption.
- State vocabulary, dependency vocabulary, manual-intervention requirements, provenance classes, and all-false authority fields are schema-level invariants.
- Blocking states require structured manual records; runnable/completed states do not require artificial blockers.

### 7. Filesystem confinement
- One caller-supplied fixed root defines the trust boundary.
- Root/path identity is captured once for a read operation.
- Descriptor-safe traversal, symlink rejection, non-regular-object rejection, lexical parent-traversal rejection, descriptor cleanup, and primary-error preservation are tested at each public helper boundary.

### 8. Review packet = deterministic projection
A review packet is not manually authored evidence.
It must be generated from one immutable candidate SHA/tree and must derive:
- changed-file count
- file blobs
- raw digests
- file contents
- complete diff
- test results
- run/job identities

No hand-copied test count or moving-branch identity may be authoritative.

### 9. Cross-component dependency equality
When component B consumes a load-bearing implementation from component A:
- the candidate tree contains one selected implementation;
- B must consume that implementation from the same tree;
- blob/interface equality must be an explicit invariant where duplication is possible.

### 10. API request contract preservation
Governance/evidence/review/package changes must not mutate provider-facing request semantics unless the defect explicitly concerns provider request semantics and the request change is separately reviewed.

Classify every material governance change as one or more:
- CONTROL_PLANE_ONLY
- EVIDENCE_ONLY
- API_ADMISSION_EFFECT
- API_REQUEST_SCHEMA_CHANGE
- API_EXECUTION_BEHAVIOR_CHANGE

The default for governance remediation is CONTROL_PLANE_ONLY and/or EVIDENCE_ONLY.

A governance-only repair must fail if it changes the canonical provider-request fingerprint for the same admitted user request.

## Change-induced-defect rule

Every remediation must answer before coding:
1. What invariant was violated?
2. Is the proposed change local or cross-component?
3. What other component consumes this contract?
4. What existing valid behavior could this change reject?
5. What permanent regression proves both the repair and the preserved valid behavior?

A reviewer example is never, by itself, the complete regression contract.

## Candidate rule

Once frozen, a candidate is immutable.
A genuine finding creates a successor candidate.
The previous candidate and failed evidence remain preserved.
