# V24-I11-V6-R15 — Alias/Representation Falsification RED 003

Status: **PRESERVED PARTIAL FALSIFICATION PASS / SYMLINK PROBE HARNESS PATH DEFECT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow run: `34776271310`
- workflow head: `d170a653b0945510b1c0eaecf93dccf189a51e81`
- candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- native observer SHA-256: `6bfb7c6ce0db74a0a3d8b8fc6229a84dc229ac481f5212ae057918b07fa44eee`

## Conclusive falsification results

The following five alternate representations reached the intended R15 policy endpoint and were rejected with no authenticated observation:

1. `/proc//self/mem` double-slash lexical variant;
2. `/proc/self/../self/mem` dot-dot lexical variant;
3. `pathlib.Path('/proc/self/mem').open(...)`;
4. custom `os.PathLike` returning `bytes` for `/proc/self/mem`;
5. integer file-descriptor representation, rejected fail-closed as `R15_AUDIT_PATH_REPRESENTATION_FORBIDDEN`.

The first four emitted `R15_AUDIT_FORBIDDEN_NORMALIZED_PATH`. The integer-fd case emitted `R15_AUDIT_PATH_REPRESENTATION_FORBIDDEN`.

## Non-conclusive symlink probes

Three symlink probes returned non-zero and emitted no authenticated observation, but did not expose the required R15 path-policy diagnostic:

- `SYMLINK_FILE_UNICODE`
- `SYMLINK_FILE_BYTES`
- `SYMLINK_DIRECTORY_PROC_MAPS`

The probe inserted code opening relative paths such as `governance-runtime/r15_mem_alias`, while the native child does not change its process working directory to the candidate sandbox. The symlink itself was created inside the sandbox. Consequently the candidate attempted to open a relative path in the workflow/native working directory, not the sandbox symlink. The operation failed during candidate import before the intended symlink/`realpath()` policy endpoint.

## Classification

`SYMLINK_ATTACK_HARNESS_PATH_DEFECT_BEFORE_REALPATH_ENDPOINT`

This run does not show a symlink bypass. It also does not prove the R15 `realpath()` alias defense. The three symlink cases must be rerun using an absolute alias path derived from candidate `__file__` so the symlink inside the exact attack sandbox is actually opened.

No candidate or R15 enforcement change is justified by this RED.

Scientific execution remains closed. Runtime qualification remains not claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
