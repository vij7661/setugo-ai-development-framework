# R8 v15-r1 Qualified Executable-Schema v2-r1 — Repair Preregistration

Status: **REPAIR_CANDIDATE — NON_AUTHORITATIVE**
Authority effect: **NONE**

Predecessor exact candidate:
- `dab6c2e2692d7e2061b77af83b43888b84d705ae`
- SFV-45 disposition: `CHANGES_REQUIRED`

Frozen semantic candidate remains:
- `c721b38cf8b00294797300b526596ce723a47ff8`

Permitted repair scope is exactly the independently reviewed/adjudicated defects:
- C-1 review-packet large-SPM materialization defect;
- C-2 SRTT15-R00 outside-table representation;
- C-3 effect-success executor identity;
- H-1 GCP rejection-vector source-case trace;
- H-2 source/crypto-profile digest and stable-ID validator closure without global SHA-256 invention;
- M-1 SRTT RuleRegistry precedence uniqueness/contiguity;
- M-2 SRTT row-ID uniqueness/contiguity;
- M-3 explicit SFV coverage for load-bearing x-validator invariants.

Forbidden:
- semantic design change;
- authority broadening;
- weaker fallback;
- transfer of predecessor SFV-45 review;
- transfer of predecessor SPM exact-byte coverage after schema bytes change;
- manual claim that the repaired candidate is QUALIFIED/FROZEN.

Repair successor must fail closed with SFV-35/SFV-36/SFV-44/SFV-45 open until exact-byte provenance regeneration/requalification and fresh review complete.
