# V24 I11 V4 Manual Verification Checklist

Status: **REVIEW SUPPORT ONLY / NO EXECUTION AUTHORITY**

A qualifying manual reviewer must use actual repository/file artifacts, not copied chat text.

1. Read `testing/v24/WDPC-V24-I11-FALSIFICATION-PLAN-V4-PACKET-MANIFEST.json`.
2. Verify each listed chunk SHA-256, concatenate chunks in manifest order, base64-decode, then gzip-decompress to reconstruct the exact packet.
3. Verify gzip SHA-256 `b2dad4aafc31b5998bc255a1cc5934b32f927303b538b5f9b0744b6785120644` and packet SHA-256 `c48925e8caf561df01932a10b9aa62953f01e8e30c8afd8cb4ed8006a164d6d4`.
4. Split after the wrapper delimiter and compute body SHA-256 `a3875a9f50b399ba6e990e6338bda4b97a69620298df9c514817b1aaaa32f79a`.
5. Verify values against `testing/v24/V24-I11-FALSIFICATION-PLAN-V4-REVIEW-BINDING.json`.
6. Verify harness blob `610093185437a48d8fd51b8db62c52b7c0fa2b3e` / version `1.1.0-PLAN-REVIEW`.
7. Verify V24 design commit `db9e4b349fd26e128f4486878a4af64929000a7c` tree `7986f7a016d97e6c9bbd03c035b3e9c63effda75`.
8. Verify I10 implementation commit `9836dc3ff233cca582f485434fc1c6494cf7eb05` tree `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`.
9. Verify all four frozen V24 falsification source blobs from the packet.
10. Do not open prior V1/V2/V3 review/adjudication artifacts during clean substantive review.
11. If any required object check is unavailable, return `INSUFFICIENT_TO_ASSESS`.

This checklist creates no authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
