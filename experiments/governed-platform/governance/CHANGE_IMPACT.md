# Change Impact and Traceability — EXP-E Minimum

Status: **experimental implementation for EXP-E**

## Purpose

Provide the smallest deterministic substrate needed to falsify accepted-baseline change handling without pretending graph reachability can solve natural-language semantics by itself.

## Design basis

NASA requirements-management guidance emphasizes bidirectional traceability, evaluating changes against higher/lower requirements and downstream architecture/design/interfaces/tests, keeping traceability current, and documenting impact-analysis results. The EXP-E graph adopts those principles in a deliberately small machine-checkable form.

Primary references:
- https://www.nasa.gov/reference/6-2-requirements-management/
- https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604509/SWE-053+-+Manage+Requirements+Changes
- https://swehb.nasa.gov/spaces/7150/pages/16449705/SWE-080+-+Track+and+Evaluate+Changes

## Graph convention

Each edge points from the dependent artifact to the artifact it depends on. Example:

`TEST -> CODE -> REQUIREMENT -> INVARIANT`

A changed dependency invalidates all transitive dependents unless stronger evidence proves otherwise.

## What the deterministic layer does

- rejects duplicate node IDs, dangling edges, self-edges and duplicate edges;
- computes transitive reverse impact from changed nodes;
- identifies accepted evidence that becomes stale because its artifact is changed/impacted;
- detects a missing graph edge only when authoritative evidence explicitly declares the relationship;
- fails closed on unknown changed-node identifiers.

## What it deliberately does not do

- infer semantic contradiction from text by graph traversal alone;
- invent missing dependencies without evidence;
- treat lexical similarity as semantic equivalence;
- automatically approve requirement changes;
- silently discard old evidence instead of retaining it as historical-but-stale evidence.

Semantic change classification remains separately falsifiable in EXP-E. The graph provides traceability and deterministic invalidation once the changed/affected relationship is established.

## Required EXP-E measurements

For each case retain:
- proposed change classification;
- affected invariant detection;
- contradiction detection where applicable;
- expected vs selected impacted artifacts;
- stale-evidence invalidation;
- unnecessary invalidation;
- lifecycle re-entry decision;
- missing/incorrect dependency-edge detection when the case contains such evidence.

No headline acceptance threshold is invented before the directional pilot is observed.
