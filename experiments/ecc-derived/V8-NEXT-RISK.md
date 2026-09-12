# ECC-Derived V8 Next Exposed Risk

Status: `NEXT_FALSIFICATION_REQUIRED`

Authority effect: `NONE_EVIDENCE_ONLY`

V8 remains a bounded 170/170 green for the exact frozen V8 suite. This record does not rewrite that result.

## Newly exposed boundary

The V8 closure-held runtime verifier captures Python module objects such as `marshal`, `hashlib`, `json`, and `sys`. Those objects are the same mutable module objects reachable through ordinary module attributes on `ecc_candidate_boundary`.

Therefore ordinary monkeypatching can potentially alter verifier primitives without reflective closure extraction. A concrete attack candidate is:

1. replace a strict-core or reference-evidence function with a favorable malicious function;
2. monkeypatch `marshal.dumps` so the malicious function's code object serializes to the original trusted function's code bytes for verifier hashing;
3. leave repository files unchanged;
4. allow the captured verifier to compute the expected runtime code digest while candidate entrypoints execute the substituted function; and
5. attempt to obtain a sealed candidate-eligible result.

This attack is within V8's declared ordinary-module/ordinary-monkeypatch threat model. It therefore requires a new falsification family before external engineering re-review.

Proposed next family: `V9_VERIFIER_PRIMITIVE_INTEGRITY`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
