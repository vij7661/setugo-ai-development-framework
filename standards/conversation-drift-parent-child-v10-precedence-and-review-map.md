# V10 Composite Precedence and Review-Evidence Map

Status: **PROPOSED V10 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10`

V10 narrows V9 without silently deleting prior history.

## 2. V9 findings narrowed by V10

| V9/R3 area | V10 disposition |
|---|---|
| V9 packet provenance ambiguity | `NARROWED_BY V10-C02` exact embedded-byte/source-blob equality |
| NCR completeness overclaim | `NARROWED_BY V10-C03` corpus-bounded coverage statement |
| CompositeAuditAuthority independence | `NARROWED_BY V10-C04` candidate-author independence record |
| Multi-policy emergency composition | `NARROWED_BY V10-C05` aggregate emergency ledger |
| Genesis qualification expiry | `NARROWED_BY V10-C06` recheck at every freeze/terminal transition |
| Effector implementation changes | `NARROWED_BY V10-C07` automatic re-attestation requirement |
| Independent R3 contamination | `NARROWED_BY V10-C08/C09` reviewer-independence evidence and contamination rule |

All other active V5–V9 rules remain active unless mechanically superseded.

## 3. Review evidence classes

Independent-review counting requires all of:

- exact candidate binding;
- exact ReviewPacketManifest;
- eligible reviewer evidence class under active policy;
- clean ReviewerIndependenceRecord;
- no prohibited prior-review exposure before authorized cross-review;
- preserved raw review output.

`CONTAMINATED` and `INSUFFICIENT_EVIDENCE` reviews may inform engineering but count as zero toward independent-review threshold.

## 4. New mechanism IDs

- `MECH-PACKET-PROVENANCE`
- `MECH-NCR-BOUNDED-COVERAGE`
- `MECH-COMPOSITE-AUDIT-INDEPENDENCE`
- `MECH-AGGREGATE-EMERGENCY`
- `MECH-GENESIS-LIVENESS`
- `MECH-EFFECTOR-REATTESTATION`
- `MECH-REVIEWER-INDEPENDENCE`

## 5. Evidence profiles

V10 adds:

- `EP-PACKET-PROVENANCE`
- `EP-NCR-BOUNDED-COVERAGE`
- `EP-COMPOSITE-AUDIT-INDEPENDENCE`
- `EP-AGGREGATE-EMERGENCY`
- `EP-GENESIS-LIVENESS`
- `EP-EFFECTOR-REATTESTATION`
- `EP-REVIEWER-INDEPENDENCE`

WDPC-172 onward must include the profiles listed in the V10 extension.

## 6. Prior-case tightening

- WDPC-136/149/153/154 -> add `EP-NCR-BOUNDED-COVERAGE`
- WDPC-137/148/155 -> add `EP-GENESIS-LIVENESS`
- WDPC-139/150/161/162 -> add `EP-AGGREGATE-EMERGENCY`
- WDPC-152/167/171 -> add `EP-EFFECTOR-REATTESTATION`
- all independent reviewer-isolation cases, including WDPC-07/19/53/68/78/106/115/125 -> add `EP-REVIEWER-INDEPENDENCE`
- any external review packet qualification path -> add `EP-PACKET-PROVENANCE`

## 7. Authority limitation

This map grants no terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
