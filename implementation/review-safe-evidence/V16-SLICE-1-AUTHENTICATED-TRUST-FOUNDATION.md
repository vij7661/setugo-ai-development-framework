# V16 Slice 1 — Authenticated Provenance and Root-of-Trust Foundation

Status: **CONSTRUCTION IMPLEMENTATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

This slice repairs the V15 self-hash/caller-declaration trust failure at the construction layer. It separates SHA-256 content integrity from Ed25519 issuer authentication, registry-backed role authorization, exact governance-state binding, and out-of-band trust/currentness provisioning.

The current construction model requires:

- an independently provisioned `PinnedBootstrapTrustSet` with threshold roots across distinct declared control domains;
- unique bootstrap and governance public-key material so one private key cannot masquerade as multiple nominal identities;
- bootstrap signatures bound to trust-set/root/key/control-domain identity and exact registry digest;
- append-preserved registry history with exact predecessor chaining, key first-appearance rules, irreversible revocation and new generation IDs for updates;
- an independently provisioned `PinnedRegistryHead` binding registry ID, candidate, sequence, generation and exact current registry digest;
- a canonical `RECORD_TYPE_REQUIRED_ROLE` policy so callers cannot choose the authority role required for a governance action;
- signed governance envelopes binding candidate, generation, trust-set ID, exact issuance registry sequence and exact issuance registry digest, optional snapshot context, issuer/key identity, canonical required role and payload digest;
- exact-integer validation (`bool` is not accepted as an integer governance field);
- strict JSON ingress rejecting duplicate/normalized-duplicate keys, floats, out-of-range integers and lone UTF-16 surrogates.

The construction code verifies that a supplied chain matches a supplied pinned current head. It **does not prove that the embedding host independently provisioned or refreshed either the bootstrap trust set or the current-head pin**. Those remain external qualification boundaries. Control-domain ancestry/shared-ancestor proof also remains for a later V16 slice.

A SHA-256 digest never authenticates an issuer. A valid Ed25519 signature does not grant authority unless the signer is present, active and role-qualified in the exact pinned current registry state. A signed record cannot cross registry forks because the exact issuance registry digest is inside the signed envelope.

The stable mandatory test manifest is `governance-runtime/review-safe-evidence-v16-slice1-test-manifest.json`. CI requires exact equality among manifest IDs, source test IDs, and raw `unittest` `... ok` IDs. Historical REDs remain preserved separately and later green runs do not erase them.

Known residuals remain explicit: dependency artifacts/transitives are not yet hash-locked; bootstrap/current-head real-world provisioning and freshness are not proven; downstream V15 surfaces are not yet migrated; control-domain ancestry is not yet integrated; effect authority remains closed.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
