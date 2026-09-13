# V24-I11-V6-R16 — Full Native Construction RED 002

Status: **PRESERVED RED / FALSIFICATION-HARNESS EXPECTATION DEFECT; KERNEL DENIAL OCCURRED EARLIER THAN EXPECTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow: `V24 V6 R16 Full Native Construction`
- run: `34778157500`
- review-authority head: `394a98e9f8f4ee6caaba6844d724207f83a3a042`
- frozen R16 candidate commit: `7c8ae745ff8270122c0cf05e123b8108af04eaad`
- frozen R16 candidate tree: `9d8db8766fee1eb76e24d62ca88d8b04ea8e3b58`

## Completed before failure

The following completed successfully:

1. exact 193-file candidate/support pinset and staging;
2. five-source trusted authority inventory and scenario-library binding;
3. hardened native build and environment binding;
4. native binary SHA-256 `871a64b015f157ab2f5283b7819641a0247d2fc015a22aac5d5921b1556e5e01`;
5. compiler digest `44d87d41d8e9a03b70e12ab88deb78a73e6dc0257b91ac5aa87f4744481f4753`;
6. interpreter digest `a942f4081cd12e67a4f9accb838926ece5e61d9ee641c530cac434ec27e0982b`;
7. environment digest `fe6dc3084a5a4e2aea918a13b215b33adb2065caf98888c1ee953482f6425f6a`;
8. all six randomized trusted external-oracle scenarios PASS, evidence SHA-256 `45b913536e2f60d6a533996ca848debbfa036c9bf14236515a11c87fe76d35af`.

## Failure endpoint

The first frozen falsification probe, `OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED`, attempted to construct the historical R15 bypass by first executing:

`root = os.open('/', os.O_RDONLY | os.O_DIRECTORY)`

The R16 Landlock policy denied this operation immediately with `PermissionError: [Errno 13] Permission denied: '/'`.

The falsification helper had placed the root-directory open outside its expected-denial `try` block and therefore expected a normal returned probe payload. It classified the candidate observation as an unexpected EXCEPTION and stopped the probe sequence.

## Classification

`FALSIFICATION_HARNESS_EXPECTATION_DEFECT_STRONGER_KERNEL_DENIAL_BEFORE_DIRFD_TARGET`

This run does **not** establish a mechanism defect. The tested attack was blocked earlier than the harness expected. It also does not count the remaining fourteen probes as PASS; they were not executed.

## Narrow repair

Keep the R16 mechanism unchanged. Modify only the falsification probe so that:

- it obtains a directory fd for the allowed candidate sandbox/current directory;
- constructs a relative `..` path from that allowed directory toward `/proc/self/mem`, `/proc/self/maps`, or `/proc/self/fd`;
- uses `os.open(relative_path, ..., dir_fd=allowed_dirfd)` to exercise true directory-relative kernel resolution;
- treats kernel `PermissionError` at either directory-fd acquisition or target resolution as denial, while requiring the attack to exercise an allowed directory fd where possible;
- retain the separate inherited-root-directory-fd probe for a pre-opened privileged descriptor.

Do not weaken Landlock, seccomp, exact-file admission, source binding, oracle binding, or secret separation.

- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
