# V24 I11 V4 Manual Verification Checklist

Status: **REVIEW SUPPORT ONLY / NO EXECUTION AUTHORITY**

A qualifying manual reviewer must use actual repository/file artifacts, not copied chat text.

1. Read `testing/v24/WDPC-V24-I11-FALSIFICATION-PLAN-V4-PACKET.gz.b64`, base64-decode, then gzip-decompress it to reconstruct the exact packet.
2. Compute packet SHA-256; expected `9b48a1ec64bb083446a799401e833201e3c54e21ea2410c6f81269d55d62a847`.
3. Split after the wrapper delimiter and compute exact body SHA-256; expected `40bc0a09b0bcf31300ddc1c55cee185f5b19ae156c896571cb72dd4e3d16b24c`.
4. Verify these values against `testing/v24/V24-I11-FALSIFICATION-PLAN-V4-REVIEW-BINDING.json`.
5. Verify `testing/v24/v24_i11_harness_contract_v2.py` Git blob equals `610093185437a48d8fd51b8db62c52b7c0fa2b3e` and version `1.1.0-PLAN-REVIEW`.
6. Verify frozen V24 design commit `db9e4b349fd26e128f4486878a4af64929000a7c` has tree `7986f7a016d97e6c9bbd03c035b3e9c63effda75`.
7. Verify frozen I10 implementation commit `9836dc3ff233cca582f485434fc1c6494cf7eb05` has tree `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`.
8. Verify the four V24 falsification source blobs listed in the V4 packet.
9. Do **not** open prior V1/V2/V3 review/adjudication files during clean substantive review.
10. If any required repository/object check is unavailable, return `INSUFFICIENT_TO_ASSESS`.

Example reconstruction command (one possible method):
`base64 -d WDPC-V24-I11-FALSIFICATION-PLAN-V4-PACKET.gz.b64 | gzip -dc > /tmp/v24-i11-v4.md`

This checklist is procedure only and creates no authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
