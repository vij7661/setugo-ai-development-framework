# V16 Slice 1 — Internal Adversarial Review 004

Status: **NEW LOAD-BEARING DEFECTS FOUND / REPAIR REQUIRED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound green construction candidate

- candidate commit: `a22c20129a75a660ea200427c47f4e9fea78e026`
- candidate tree: `4491aea4846d63a1d42584c6dd4c145e41bc9fa6`
- construction run: `34980271907`
- mandatory tests: `50/50 PASS`
- manifest/source/execution equality: `PASS`

The 50-test green is preserved as construction evidence only. This fourth internal pass attacks trust-policy identity and cross-implementation identifier semantics not falsified by the 50-test set.

## Overall disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

## Critical finding V16-S1-IAR4-001 — `trust_set_id` does not bind the contents or threshold policy of the bootstrap trust set

### Mechanism

`PinnedBootstrapTrustSet` contains an arbitrary string `trust_set_id`, a threshold, roots and candidate-controlled-domain exclusions. Root signatures bind the string `trust_set_id` plus each signing root's identity and the registry digest, but they do **not** bind a digest of the complete trust-set policy.

Nothing currently requires two trust-set objects with the same `trust_set_id` to contain the same:

- threshold;
- root membership;
- root control-domain assignments;
- candidate-controlled-domain exclusion set.

### Concrete false-green path

1. A legitimate pinned trust set `T` has `trust_set_id = X`, roots A/B/C and threshold 3.
2. A registry has valid signatures from A and B but not C, so it is insufficient under T.
3. A changed/replayed configuration presents another trust-set object with the same `trust_set_id = X`, roots A/B and threshold 2.
4. The existing A/B signatures still verify because their signed messages bind the unchanged label X and their own root identities, not the complete threshold/membership policy.
5. The same registry can now satisfy the downgraded threshold without any new registry generation or signature.

A similar path exists if `candidate_control_domain_ids` is weakened while preserving `trust_set_id`.

### Governing rule violated

A load-bearing trust-policy identity must be content-bound. A stable human label cannot stand in for the exact root/threshold/exclusion policy that determines authority.

### Narrow repair

1. Define a canonical bootstrap-trust-set policy digest over exact threshold, ordered/canonical root descriptors and candidate-controlled-domain exclusions.
2. Require a pinned `trust_set_digest` to match that recomputation.
3. Bind the digest, not merely the label, into bootstrap registry-signature messages, signed governance envelopes and pinned current-head context.
4. Add regressions for threshold downgrade, root-set change and exclusion-set change under a reused `trust_set_id`.
5. Continue to state that real-world provisioning/ownership of the pinned trust set is external and unproven; this repair is content identity, not provenance of the provisioning channel.

## Critical finding V16-S1-IAR4-002 — Canonical authority-policy semantics are code-local but not version/digest bound to signed state

### Mechanism

`RECORD_TYPE_REQUIRED_ROLE` correctly prevents a caller from selecting the role at runtime, but the mapping exists only as local verifier code. Neither the bootstrap-signed key registry, the pinned current head nor the signed governance envelope binds the exact authority-policy mapping/version used to interpret `record_type`.

### Concrete false-green path

1. Version P1 maps `BLOCKER_RESOLUTION -> BLOCKER_RESOLUTION_AUTHORITY`.
2. A raw-evidence-only key signs a `BLOCKER_RESOLUTION` envelope declaring `RAW_EVIDENCE_CAPTURE_AUTHORITY`; P1 correctly rejects it.
3. Later verifier code changes the mapping to `BLOCKER_RESOLUTION -> RAW_EVIDENCE_CAPTURE_AUTHORITY` without changing the already signed registry history/generation.
4. The old envelope can now become valid solely because local interpretation changed.

The signed bytes did not change. Authority semantics changed outside the authenticated governance state.

### Governing rule violated

Load-bearing policy changes must create governed state/generation change and must not retroactively reinterpret previously signed authority-bearing objects.

### Narrow repair

1. Compute a canonical `authority_policy_digest` from the complete record-type → role mapping.
2. Add it to every registry snapshot so bootstrap signatures authenticate the policy under which roles are interpreted.
3. Bind it into `PinnedRegistryHead` and every signed governance envelope.
4. Current-authority verification must require exact equality among verifier policy digest, current registry policy digest, pinned-head policy digest and signed-envelope policy digest.
5. A policy change therefore requires a new registry snapshot/new generation and newly signed current objects.
6. Add a regression demonstrating that a record signed under policy digest P1 cannot become valid under P2 solely because verifier code changed.

## High finding V16-S1-IAR4-003 — Identifier uniqueness/comparison is not normalized even though signature canonicalization is NFC-normalized

### Mechanism

Canonical serialization NFC-normalizes string values, but semantic uniqueness and lookup logic generally compares the original Python strings. Unicode-equivalent identifiers such as composed `é` and decomposed `e + combining acute` can therefore be different keys/IDs to the validator while canonicalizing to the same logical text in signed bytes.

Affected identity classes include bootstrap root/key/domain IDs and governance issuer/key/domain identifiers; similar ambiguity applies to registry/candidate/generation/record identifiers.

### False-green consequence

Two nominal identities that another implementation or normalization boundary treats as the same can be counted or looked up as distinct locally. This is a cross-implementation alias surface at the root/authority boundary.

### Narrow repair

Require every load-bearing identifier to already be canonical NFC and reject non-canonical spellings rather than silently normalizing them during semantic comparison. Apply the rule before uniqueness/counting/indexing. Add regressions for normalized-equivalent bootstrap root IDs, governance key IDs and control-domain IDs.

## Medium finding V16-S1-IAR4-004 — `schema_version == 1` still accepts Python boolean `True`

The exact-integer repair covered sequence/currentness fields, but equality checks such as `record.get("schema_version") != 1` permit `True` because `True == 1` in Python. This does not currently create a direct authority escalation by itself, but it violates machine-enforceable canonical schema semantics and can create cross-language disagreement.

Narrow repair: require `type(schema_version) is int and schema_version == 1` for registry and signed-record schemas and add regressions.

## Previously declared residuals remain open

- bootstrap/current-head real-world provisioning and freshness are still external and unproven;
- control-domain ancestry/shared-root resolution remains a later V16 slice;
- Python dependency artifacts/transitives remain version-observed but not hash-locked;
- downstream V15 governance surfaces are not yet migrated.

## Stopping rule

Do not start Slice 2. Repair IAR4-001 through IAR4-004 atomically with source/tests/manifest/workflow/contract, preserve any resulting RED, obtain another governed green, then perform another internal adversarial pass.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
