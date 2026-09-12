# V17 Threshold Ledger and Canonical Conflict Map

Status: **PROPOSED V17 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13 -> V14 -> V15 -> V16 -> V17`

## 2. Active V17 mechanisms

- `MECH-THRESHOLD-ATOMIC-COMMIT-ONLY`
- `MECH-THRESHOLD-CONSUMPTION-LEDGER`
- `MECH-CROSS-GATE-REUSE-POLICY`
- `MECH-NRVA-REGISTRY`
- `MECH-NRVA-RPAA-JOINT-INDEPENDENCE`
- `MECH-CANONICAL-CONFLICT-PRECEDENCE`
- `MECH-CANONICAL-CORPUS-LIVENESS`
- `MECH-ENDPOINT-EXPORT-EXACT-COMMIT`
- `MECH-PACKET-GENERATION-ANTI-FORK`
- `MECH-V17-PROOF-VIEW-COMPLETENESS`

## 3. Evidence profiles

- `EP-THRESHOLD-ATOMIC-COMMIT-ONLY`
- `EP-THRESHOLD-CONSUMPTION-LEDGER`
- `EP-CROSS-GATE-REUSE-POLICY`
- `EP-NRVA-REGISTRY`
- `EP-NRVA-RPAA-JOINT-INDEPENDENCE`
- `EP-CANONICAL-CONFLICT-PRECEDENCE`
- `EP-CANONICAL-CORPUS-LIVENESS`
- `EP-ENDPOINT-EXPORT-EXACT-COMMIT`
- `EP-PACKET-GENERATION-ANTI-FORK`
- `EP-V17-PROOF-VIEW-COMPLETENESS`

## 4. Prior-case tightening

- WDPC-237,250,257 -> all V17 atomic-count, reuse, NRVA, canonical, endpoint-export, and packet-lineage predicates.
- WDPC-246,251 -> no detached recheck path; atomic transaction/consensus consumption only.
- WDPC-252,258 -> root-governed NRVA registry + NRVA/RPAA joint independence.
- WDPC-253 -> canonical conflict fail-closed + corpus currentness.
- WDPC-256 -> exact candidate-commit export binding even when content digests match.
- WDPC-259 -> packet-generation lineage/anti-fork ledger.
- WDPC-240,244 remain `DUPLICATIVE_BUT_USEFUL` and count as one unique enforcement path.

## 5. Threshold counting rule

A threshold count exists only as a committed `ReviewThresholdRecord` in the authoritative `ReviewThresholdConsumptionLedger` produced by the same atomic operation that revalidates the exact qualification snapshot.

No earlier recheck or detached proof substitutes for atomic consumption.

## 6. Canonical conflict rule

Contradictory canonical evidence is not resolved by choosing a permissive interpretation. It becomes `CANONICAL_SEMANTIC_CONFLICT`, contributes no qualification, and requires a new governed corpus/algorithm proof generation.

## 7. Packet lineage rule

Packet generation is a single append-only lineage per governed candidate/projection review stream. Only lineage genesis has no predecessor. Reset/fork attempts cannot become current.

## 8. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
