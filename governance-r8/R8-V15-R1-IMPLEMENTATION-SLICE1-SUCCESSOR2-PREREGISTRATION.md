# R8 v15-r1 — Implementation Slice 1 Successor 2 Repair Preregistration

Status: **PREREGISTERED BEFORE SUCCESSOR 2 HARNESS OR MECHANISM CHANGE**

## 1. Lineage

Predecessor implementation candidate:
`2cf7adce8bdd67c8b78659d9359c178535af1d73`

Predecessor independent review:
`governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-INDEPENDENT-REVIEW-001.txt`

Adjudication:
`governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-REVIEW-001-ADJUDICATION.json`

Frozen executable-schema candidate remains:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

No frozen executable-schema bytes or semantic-source bytes may change in this successor.

## 2. Confirmed repair scope

Successor 2 may change only the bounded Slice 1 implementation/tests/control surface required to close:

1. **Nested negative-zero ambiguity** — preserve integer lexical tokens in generic JSON parsing so nested `-0` rejects before it can normalize to integer zero.
2. **Filesystem path identity** — reject symlinked frozen artifacts or symlink components and require resolved artifact files to remain directly under the resolved frozen schema directory.
3. **Full-path source-map binding** — convert source-map artifact keys to their exact frozen schema relative paths and require set equality against the SPM artifact paths.
4. **Artifact shape validation** — require non-empty artifact IDs and lowercase 64-hex artifact SHA-256 values during direct SPM validation.
5. **Trigger-test completeness** — assert the original Slice 1 preregistration remains covered by the governed workflow trigger.
6. **Symlink-test coverage** — prove a symlink to an external file containing the exact expected bytes still rejects.
7. **Review transport reduction** — next review transport must use at most six attachments: one CORE evidence file, one NON-SPM schema file, and four exact SPM chunks. The CORE file must contain instructions, exhaustive schema index, exact candidate bytes, every workflow-invoked regression source, construction evidence, and all transport hashes.

The exact frozen SPM intentionally contains catalog refs not used by entry rows. Successor 2 MUST NOT invent a rule requiring every source-ref catalog member to appear in an entry.

## 3. Frozen Successor 2 invariants

**S1R2-I01 Nested integer lexical integrity** — generic JSON parsing preserves the lexical token for every integer until governance lexical checks run.

**S1R2-I02 Nested negative zero rejects** — `{"n":-0}`, `[-0]`, and equivalent nested integer positions reject as `GCP_REJECT_NEGATIVE_ZERO`; they must never canonicalize to zero.

**S1R2-I03 Existing integer semantics preserved** — nested signed-int64 min/max remain accepted, min-1/max+1 reject, and existing top-level integer rejection codes remain unchanged.

**S1R2-I04 No symlink substitution** — no required frozen core file or SPM-covered artifact may be a symlink or traverse a symlink component. Same-byte symlink targets do not qualify.

**S1R2-I05 Resolved path confinement** — every SPM-covered artifact resolves to a regular file whose resolved parent is exactly the resolved `schemas/governance-r8/v15-r1` directory.

**S1R2-I06 Full-path source-map equality** — the exact set of SPM artifact paths equals `schemas/governance-r8/v15-r1/<source-map artifact key>` for every source-map artifact key.

**S1R2-I07 Artifact shape closure** — every SPM artifact ID is a non-empty string and every artifact SHA-256 is exactly 64 lowercase hexadecimal characters.

**S1R2-I08 Prior boundaries remain intact** — original I1-01..I1-16 and S1R-01..S1R-08 remain green, exact frozen schema bytes remain unchanged, and authority remains bounded to construction only.

## 4. Frozen Successor 2 acceptance cases

- **S1R2-01** nested object negative zero rejects with `GCP_REJECT_NEGATIVE_ZERO`.
- **S1R2-02** nested array negative zero rejects with `GCP_REJECT_NEGATIVE_ZERO`; nested min/max still canonicalize exactly.
- **S1R2-03** a frozen artifact replaced by a symlink to an external same-byte file rejects before a usable bundle returns.
- **S1R2-04** direct source-map/SPM validation rejects a source-map artifact key set that does not map exactly to the frozen full SPM artifact paths.
- **S1R2-05** direct SPM validation rejects empty artifact IDs and malformed artifact SHA-256 values.
- **S1R2-06** governed workflow trigger coverage explicitly includes the original and both successor preregistration/test/control paths.
- **S1R2-07** the frozen schema directory remains byte-identical to frozen candidate `f93ca269...`.
- **S1R2-08** original I1 + Successor 1 S1R + Successor 2 S1R2 + applicable post-freeze regressions all pass on one exact candidate.

## 5. Construction sequence

1. Commit this preregistration.
2. Extend workflow branch/path coverage to Successor 2 without changing mechanism semantics.
3. Add/freeze Successor 2 repair harness while the predecessor mechanism remains unchanged.
4. Preserve the expected RED result for nested negative zero / symlink / full-path / artifact-shape gaps.
5. Apply only the narrow mechanism repair.
6. Require original I1-01..I1-16 + S1R-01..S1R-08 + S1R2-01..S1R2-08 + applicable post-freeze regressions to pass.
7. Update lifecycle marker and rerun the exact marker candidate.
8. Freeze one exact Successor 2 implementation candidate SHA.
9. Build the <=6-file byte-complete fresh blind review transport.
10. Require fresh blind independent review before bounded Slice 1 adjudication.

## 6. Claim boundary

Successor 2 construction remains repository-local implementation evidence only. It grants no runtime qualification, release, deployment, production, policy, or terminal authority.
