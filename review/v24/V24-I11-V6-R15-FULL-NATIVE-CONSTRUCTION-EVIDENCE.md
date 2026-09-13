# V24-I11-V6-R15 — Full Native Construction Evidence

Status: **FULL CONSTRUCTION PASS / STRONGER FALSIFICATION AND MANUAL SUCCESSOR REVIEW STILL REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Frozen candidate

- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- implementation branch: `implementation/v24-i11-v6-r15-path-normalization`
- review branch: `review/v24-i11-v6-r15-path-normalization`
- predecessor R14 candidate: `5a1fb005e9c58e30b1dcfaa473d603dde90df72c`
- predecessor R14 falsification run: `34775597496`
- predecessor R14 classification: `FAIL_CODE_DEFECT`

## Preserved R15 RED history

### RED 001 — intended endpoint not externally observable

- run: `34775801974`
- classification: `PROBE_OBSERVABILITY_DEFECT_BEFORE_INTENDED_ENDPOINT_PROOF`
- record: `V24-I11-V6-R15-CONSTRUCTION-RED-001.md`

All seven attacks returned non-zero and emitted no authenticated observation, but the inherited child wrapper hid the underlying audit exception behind generic import failure. The policy was not weakened; a trusted native diagnostic was added at the exact R15 rejection point.

### RED 002 — full construction oracle CLI mismatch

- run: `34776044993`
- classification: `FULL_CONSTRUCTION_WORKFLOW_ARGUMENT_MISMATCH_BEFORE_ORACLE_ENDPOINT`
- record: `V24-I11-V6-R15-CONSTRUCTION-RED-002.md`

The full construction passed pinning, historical attack rejection, all seven R15 path regressions and launcher probes, but the workflow supplied unsupported runtime-binding CLI options to the inherited trusted oracle. The oracle endpoint was never reached. Candidate/native enforcement was unchanged; only the invocation was corrected.

## Successful full construction V2

- workflow: `V24 V6 R15 Full Native Construction V2`
- workflow run: `34776147253`
- workflow/review commit: `c93a533cfb4a45325670c0333d3241b18be259c4`
- workflow review tree: `25be8bfb7a1f86a68cea88761b0f59014c92bd16`
- conclusion: `SUCCESS`
- Python: `3.12.14`

All substantive endpoints passed:

1. exact candidate and external authority objects bound;
2. R15 native observer compiled with exact CPython home/program binding;
3. external exact-file pinset built, source verified, staged and sandbox verified;
4. exact-file production/support/unpinned/symlink substitutions rejected;
5. isolated interpreter and environment digests bound;
6. normal candidate request succeeded through the native boundary;
7. historical R13/native-boundary attacks rejected;
8. all seven R15 path/memory attacks rejected at the exact R15 audit-policy endpoint;
9. launcher without required isolation rejected;
10. optimized launcher rejected;
11. six external oracle checks passed through R15 native observations;
12. candidate-side structural evidence validator accepted the exact external bundle while remaining `qualified = false`;
13. native-binary substitution evidence rejected;
14. post-execution sandbox exactness remained unchanged;
15. one construction artifact bound the pinset, R13 regression, R15 path regression, oracle evidence and construction record.

## Exact construction identities

- R15 native observer source Git blob: `bfd16c1f3b7103b25c2f1abee536ebceb199e295`
- R15 external guard Git blob: `988a69decfb8f02f20b89bdee74da7b8a48ad51d`
- Python-home binding source Git blob: `6e5f3e02146adff92c70bdd12199644b35656721`
- inherited trusted oracle Git blob: `9b9e2714ef9f71aefe99ceb62e8eac25319fdf10`
- inherited scenario-library Git blob: `f0f72ca65eb443fd2db2917622a327256d15db05`
- native binary SHA-256: `6bfb7c6ce0db74a0a3d8b8fc6229a84dc229ac481f5212ae057918b07fa44eee`
- compiler digest: `153246e96a6b5d9d1856762a6171db87c8f4c218c0481e66c0d8c443bbcde233`
- Python program SHA-256: `bef88f140b625959f8af25c7b75cce2cd5d4b29cc2f2b079befd7f68eda4dba0`
- interpreter contract digest: `eed7733f7032dd1f588cd048469130e52487335d2a7f32d2016cbc1d883d206b`
- environment digest: `afefcc6f01255ace8f35125be4810180d5aa1aecd4e3a4dfce21f315eb96af1e`

## Exact-file pinset

- admitted files: `190`
- pinset SHA-256: `e2f7689d4b9902823d94fe11e87c895e4036a080e0795aacfd9070354cf134b9`
- R15 execution contract is included in the external support set.
- post-execution exact sandbox check passed unchanged.

## Adversarial evidence

Historical R13/native-boundary regression object:
- SHA-256: `895af7dadf0018203c25b67ee2ab77c8395bbedd2325f0bf88ae0f493a1a374a`
- all seven historical attacks rejected;
- no rejected attack emitted an authenticated observation.

R15 path/memory regression object:
- SHA-256: `3534babb7e03308630a6c07e42779372379d3e725e8b0839be1593e1888bead3`
- seven of seven mandatory attacks rejected at `R15_AUDIT_FORBIDDEN_NORMALIZED_PATH`;
- no rejected attack emitted an authenticated observation.

External oracle evidence:
- six records;
- SHA-256: `99802aabf7b6d1451a7e698aaa6b540592a036f4870366fbe3fd577a333aebd8`
- evidence-set digest: `c02083d52178089b8c6c4ecd43912b254332081bd38748eea973a54b5500b6de`
- run ID: `34776147253`
- round: `R15-NATIVE-ROUND-2`
- candidate-side unittest role: `NON_AUTHORITATIVE_DIAGNOSTIC_ONLY`
- oracle decision origin: `TRUSTED_EXTERNAL_ORACLE`
- native parent initializes Python: `false`
- candidate Python executes only in forked child: `true`

Construction record:
- SHA-256: `08e8972dc759b7b08b5fd31f552e50d19b7b8c4e4a2d7d67bfdf62c0ca001494`

## Artifact binding and independent recomputation

- artifact ID: `10324065691`
- artifact name: `v24-v6-r15-full-native-construction-v2-evidence`
- artifact bytes: `20862`
- GitHub artifact SHA-256: `0c16e6e523ce5b4d5e4da38ff01e0ed00f4024891554d5665c1a548fc5a02601`
- independent post-download SHA-256: `0c16e6e523ce5b4d5e4da38ff01e0ed00f4024891554d5665c1a548fc5a02601`
- outer digest match: `VERIFIED`

Contained files independently recomputed:

- `pin.json` — SHA-256 `e2f7689d4b9902823d94fe11e87c895e4036a080e0795aacfd9070354cf134b9`
- `r13.json` — SHA-256 `895af7dadf0018203c25b67ee2ab77c8395bbedd2325f0bf88ae0f493a1a374a`
- `path.json` — SHA-256 `3534babb7e03308630a6c07e42779372379d3e725e8b0839be1593e1888bead3`
- `oracle.json` — SHA-256 `99802aabf7b6d1451a7e698aaa6b540592a036f4870366fbe3fd577a333aebd8`
- `construction.json` — SHA-256 `08e8972dc759b7b08b5fd31f552e50d19b7b8c4e4a2d7d67bfdf62c0ca001494`

All construction-record digest references match the independently recomputed contained objects.

## Construction-only disposition

This is not successor acceptance. Before any manual review package is frozen, R15 still requires stronger falsification of alternate path representations/aliases such as symlink-resolved aliases and lexical variants. A clean manual successor review is required after falsification closure.

- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`
- manual successor review: `NOT_YET_OPEN`
- automated external reviewer/provider API calls during TESTING/FALSIFICATION: `PROHIBITED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
