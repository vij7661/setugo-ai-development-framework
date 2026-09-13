# V24-I11-V6-R15 — Clean Review Package RED 001

Status: **PRESERVED PACKAGE-BUILDER ORDERING DEFECT / NO PACKAGE UPLOADED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow run: `34776512860`
- workflow head: `1f1692bf9075d443eb6d3340f8fff8e4d8729d62`
- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- fixed review metadata commit: `1171b15eae418feb736911e71e975753d67b5a0d`

## Passed before RED

1. exact candidate commit/tree fetch and verification;
2. exact full-construction artifact download and outer SHA-256 verification;
3. exact pinset SHA-256 verification;
4. all 190 admitted candidate files re-read from the frozen commit and independently verified by raw SHA-256, Git blob SHA-1 and byte length;
5. exact construction evidence object hashes verified;
6. trusted/native review-side object Git blob identities verified;
7. approved 19,297-byte V6 design reconstructed and verified by raw SHA-256 and Git blob SHA-1;
8. deterministic ZIP built twice and the two ZIP byte streams matched exactly.

## Failure endpoint

The final ZIP ordering verifier asserted:

`names == sorted(names)`

while the archive input list had been sorted as `pathlib.Path` objects. `Path` ordering is component-wise, while the ZIP verifier sorts flat POSIX path strings. These orderings can differ for path sets containing component-prefix/punctuation relationships even though both are deterministic.

The archive therefore failed the explicit flat-string ordering assertion after the double-build equality check.

No clean-review artifact was uploaded.

## Classification

`PACKAGE_BUILDER_ORDERING_VERIFIER_MISMATCH_AFTER_CONTENT_BINDING`

This is not a candidate, mechanism, falsification, or evidence defect. The narrow repair is to sort staged files by `p.relative_to(stage).as_posix()` before both manifest construction and ZIP emission, then retain the existing flat-string ZIP ordering assertion unchanged.

Scientific execution remains closed. Runtime qualification remains not claimed. Manual review has not yet started.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
