# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-4

## A. Overall disposition

**CHANGES_REQUIRED**

Successor-4 fixes the specific caller-writable environment-anchor defect from Successor-3, and its asymmetric signature verification is materially stronger. However, PRC-1 remains systemically open because the root-verification decision itself is still ordinary mutable Python state inside the same process as the caller/candidate.

The frozen candidate therefore does not yet satisfy its own invariant that the caller cannot mint, replace, or bypass the construction root.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.

## B. Candidate and package identity

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-4`
- frozen candidate commit: `ef30eba1dfbe5ccf0ec6edb9e8d1295da5c70ddb`
- frozen candidate tree: `bfbf49021514240668b24612d53ea790bcdf0baa`
- exact final-head run: `35324254339`
- integration binding digest: `f55d1354bb3c012d59711b4cd2dac6a7fb334387adc38ed506ee2f595043e348`
- verification artifact: `10539040564`
- verification artifact digest: `sha256:50f9e004b13de66cdd19f6ae8aa6310dc45e2a7769dd0aaa259d355f2d42a2f7`
- verification JSON SHA-256: `e1492d7fd035085591ea5d29d21231180f9aac4f417d0d8da898c4e8e81afe54`
- clean review package branch head: `17a3bfc67babf22d8836c6bfaca146cc007a2b9b`
- clean review package run: `35324979097`
- clean review package artifact: `10539156596`
- clean review package digest: `sha256:fa4d968026e886273e23102604193fd6bcce47a67d97dcaed704071cc1c28229`

Pinned construction trust:

- trust branch: `trust/v24-v6-construction-root-attestation-v3`
- trust commit: `2515582a5e2f0e1041bf5cc83523ffa732620724`
- trust tree: `1c2a1d0f60d3e2a62a2355831dc46f76ff72df7e`
- public-root blob: `7722a5725324fb805283bce9764b2d151a774ec2`
- signature-bundle blob: `b16e2a2bfac013e6e600cf9944595a88eefd2ca8`
- signing-ceremony blob: `cc2d8bec17b6775392094920f9549ca2e5174d44`
- public-key DER SHA-256: `fbb2cea7474505f0c0d8f77be81c97a949d4ea70eb38b7caef4ffd0e9606f61c`

## C. Critical findings

### C-01 — PRC-1 remains bypassable by same-process verifier substitution

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** `v24_v6_proof_reference_closure.py -> validate_proof_context() -> validate_root_attestation()`

#### Concrete failure path

The frozen candidate imports the verifier into mutable module-global Python state:

```python
from v24_v6_root_attestation import validate_root_attestation
```

Every proof resolver reaches `_build_resolver()`, which calls `validate_proof_context()`. That function invokes the mutable global name `validate_root_attestation`.

A same-process caller can therefore replace the verifier before invoking a resolver:

```python
import v24_v6_proof_reference_closure as prc
from test_v24_v6_successor4_external_anchor_red import (
    attacker_constructed_bundle,
    TARGET_CONTENT,
)

context, boundary, leaf_ref = attacker_constructed_bundle()

prc.validate_root_attestation = lambda *args, **kwargs: []

result = prc.resolve_governed_qualification(
    leaf_ref,
    context,
    boundary,
    expected_subject_id="ATTACK-TARGET",
    expected_subject_content_digest=TARGET_CONTENT,
)
```

The attacker bundle is the already-preserved structurally valid self-grant context used to expose Successor-3. Under the frozen Successor-4 code, the new rejection is introduced by `validate_root_attestation`. Replacing that one mutable function removes the only external-root rejection and returns control to the ordinary resolver path.

The same class of bypass is also possible by mutating verifier module globals such as the pinned RSA modulus/exponent or replacing the RSA verification helper, because those are normal writable Python module attributes.

#### Why existing controls fail

The current regressions test:

- rewrite of the old environment anchor;
- missing attestation;
- wrong-context signature;
- extra caller-supplied modulus/exponent fields;
- scope substitution.

They do **not** test mutation/replacement of the in-process verifier, imported verifier symbol, pinned key globals, or RSA verification helper.

The final-head workflow also checks source text, fixture separation, absence of committed private-key PEM text, and exact trust blobs, but none of those controls makes the live Python verifier immutable to the same process.

This conflicts with the Successor-4 design invariant that the caller may not select or replace the verification root, and with the R14/R16 trust direction already cited by the design: candidate Python is untrusted and authority material/decisions must live outside candidate-mutable Python state/address space.

#### Narrow required repair

Do not attempt another Python-local pin.

Move the authority-bearing root verification/decision outside the mutable candidate interpreter, using the previously established trusted-parent/native-oracle direction. At minimum:

1. the untrusted Python process may submit exact context bytes plus attestation;
2. an external trusted verifier with a pinned key independently verifies signature, canonical material, generation, context digest, and scope digest;
3. the external verifier returns an authenticated verdict bound to those exact bytes/identities;
4. the authority-bearing consumer/gate validates and enforces that verdict outside candidate-mutable Python state;
5. candidate Python cannot replace the verifier, key, verdict validator, or authority gate.

If the intended threat model is only “caller controls input values but cannot execute arbitrary code in the same interpreter,” that narrower threat model must be stated explicitly and the prior “same-process caller/candidate cannot replace the root” claim must be reduced accordingly. Under the current stated posture, the candidate is not closed.

## D. High findings

### H-01 — DA-1 remains transitively exploitable through PRC-1

**Severity:** High  
**Blocking:** Yes

The local decision/effect-path binding repair remains structurally present, but its qualifying proof path still depends on PRC-1. Once the attacker substitutes the root verifier and admits a fresh attacker-built proof context, the attacker can again create a fresh qualification for an attacker-selected decision/effect-path relationship instead of being limited to stale-proof substitution.

Therefore DA-1 is **not independently closed** while C-01 remains open.

**Required repair:** close PRC-1 at an external/non-candidate-mutable authority boundary, then re-run the compound decision -> effect-path/target/effect-class attack.

### H-02 — NCP-1 remains transitively exploitable through PRC-1

**Severity:** High  
**Blocking:** Yes

The local clause/control reassignment checks remain structurally present, but the proof of the required binding still rests on proof-reference closure. With verifier substitution, a caller can admit a fresh attacker-selected binding qualification and restore the compound clause -> control reassignment path.

Therefore NCP-1 is **not independently closed** while C-01 remains open.

**Required repair:** close PRC-1 externally, then re-run fresh-binding, stale-binding, clause/control substitution, and cross-control composition attacks.

## E. Medium findings

None required beyond the Critical systemic root defect above.

## F. Low findings

None required for progression.

## G. Explicit adjudication of previous blockers

- **PRC-1:** **OPEN / CRITICAL / BLOCKING.** The old environment-anchor self-grant is fixed, but the root-verification decision is still replaceable by the same Python process.
- **DA-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.
- **NCP-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.

## H. Positive attacks/controls that appear to hold under an unmodified verifier

Manual inspection and preserved regression evidence support the following bounded positives:

- same-process rewrite of only `V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256` no longer grants closure;
- unsigned contexts are rejected;
- a valid signature from context A does not verify for context B;
- caller-added modulus/exponent fields are rejected by exact attestation-field checking;
- generation/genesis-scope substitution invalidates the attestation/binding;
- the custom RSA PKCS#1 v1.5 verifier compares an exact expected encoded block rather than accepting a loose prefix/suffix form;
- final-head verification pins exact external trust commit/tree/blob identities and checks local trust-fixture byte identity;
- no signing private key is intentionally present in the reviewed candidate surface;
- Successor-4 all-up GREEN (`35323905839`, 209/209 V24-V6 tests) and exact final-head GREEN (`35324254339`) are preserved as construction evidence, not authority.

These positives do not close C-01 because all of them assume the Python verifier implementation itself remains unmodified.

## I. New systemic/transitive finding

**Mutable-verifier root collapse:** an asymmetric signature does not create an external root of trust when the function deciding whether that signature is valid is itself mutable by the threat actor in the same address space.

The load-bearing relationship is not merely:

`context -> signature -> pinned public key`

It is:

`context -> signature -> verifier implementation/key state -> authority decision`

Successor-4 externalized the private signing key but did not externalize the final trust decision. The latter remains candidate-mutable.

## J. Evidence and runtime limitations

This review is construction-level only.

It does not claim or assess production HSM/KMS custody, runtime process isolation, durable external effects, concurrency fencing/idempotency, provider behavior, deployment controls, scientific WDPC outcomes, or durable evidence recovery after process failure.

No earlier failure is reclassified:

- Successor-3 manual review remains `CHANGES_REQUIRED`.
- Successor-3 adjudication remains `3b16e06e8e2d6dc7d5d1f0864b8dea508edada8f`.
- Successor-4 preserved pre-repair self-grant RED remains run `35318618058`.
- Later GREEN runs remain valid bounded evidence but do not erase the false-green path identified here.

## K. Final progression statement

**Successor-4 may not progress.**

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. A new repair/refreeze/re-review cycle is required.

The next successor should preserve Successor-4's asymmetric context binding but move the load-bearing verification/authority decision outside candidate-mutable Python state, then add a permanent regression that attempts direct same-process replacement of the verifier/key/helper and proves that such mutation cannot create authoritative proof closure.
