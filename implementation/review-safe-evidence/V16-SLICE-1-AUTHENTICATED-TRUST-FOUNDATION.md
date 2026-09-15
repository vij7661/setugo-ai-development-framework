# V16 Slice 1 — Authenticated Provenance and Root-of-Trust Foundation

Status: **CONSTRUCTION IMPLEMENTATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This slice repairs the V15 self-hash/caller-declaration trust failure at the construction layer. It separates SHA-256 content integrity from Ed25519 issuer authentication, registry-backed role authorization, exact governance-state binding, and out-of-band trust/currentness provisioning.

The current construction model requires:

- an independently provisioned `PinnedBootstrapTrustSet` with threshold roots across distinct declared control domains;
- a canonical `trust_set_digest` over the complete bootstrap trust policy: label, threshold, canonical root descriptors and candidate-controlled-domain exclusions;
- bootstrap signatures bound to the exact `trust_set_digest`, root/key/control-domain identity and exact registry digest, so a reused human label cannot silently downgrade threshold/membership/exclusions;
- unique bootstrap and governance public-key material so one private key cannot masquerade as multiple nominal identities;
- append-preserved registry history with exact predecessor chaining, key first-appearance rules, irreversible revocation and new generation IDs for updates;
- an independently provisioned `PinnedRegistryHead` binding trust-set ID and digest, authority-policy digest, registry ID, candidate, sequence, generation and exact current registry digest;
- a canonical, machine-enforced `RECORD_TYPE_REQUIRED_ROLE` policy with a canonical `authority_policy_digest`; every registry snapshot carries a policy digest and current verification requires exact equality among local policy, current registry, pinned head and signed envelope;
- signed governance envelopes binding candidate, generation, trust-set ID and digest, authority-policy digest, exact issuance registry sequence/digest, optional snapshot context, issuer/key identity, canonical required role and payload digest;
- rejection of non-NFC load-bearing identifiers before uniqueness/counting/lookup rather than silently normalizing identity strings;
- exact-integer validation (`bool` is not accepted as an integer governance field), including schema versions, registry/currentness sequences and key validity/revocation sequences;
- strict JSON ingress rejecting duplicate/normalized-duplicate keys, floats, out-of-range integers and lone UTF-16 surrogates.

A policy change cannot retroactively reinterpret an old signed object: a different record-type→role mapping changes `authority_policy_digest`, so the current registry/head/envelope binding fails until a new registry generation and newly signed current objects are established. Historical registry snapshots may retain their prior policy digest, but the current snapshot must match the verifier's exact current policy digest.

The construction code verifies that a supplied chain matches a supplied pinned current head. It **does not prove that the embedding host independently provisioned or refreshed either the bootstrap trust set or the current-head pin**. Those remain external qualification boundaries. The trust-set digest proves exact content identity, not real-world ownership or provisioning provenance. Control-domain ancestry/shared-ancestor proof also remains for a later V16 slice.

A SHA-256 digest never authenticates an issuer. A valid Ed25519 signature does not grant authority unless the signer is present, active and role-qualified in the exact pinned current registry state. A signed record cannot cross registry forks because the exact issuance registry digest is inside the signed envelope.

The stable mandatory test manifest is `governance-runtime/review-safe-evidence-v16-slice1-test-manifest.json`. CI requires exact equality among manifest IDs, source test IDs, and raw `unittest` `... ok` IDs. Historical REDs remain preserved separately and later green runs do not erase them.

Known residuals remain explicit: dependency artifacts/transitives are not yet hash-locked; bootstrap/current-head real-world provisioning and freshness are not proven; downstream V15 surfaces are not yet migrated; control-domain ancestry is not yet integrated; effect authority remains closed.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
