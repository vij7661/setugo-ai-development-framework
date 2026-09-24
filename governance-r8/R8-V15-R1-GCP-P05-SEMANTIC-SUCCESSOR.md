# R8 v15-r1 — GCP P05 Narrow Semantic Successor

Status: **SEMANTIC_SUCCESSOR_CANDIDATE_NON_AUTHORITATIVE**  
Authority effect: **NONE**

Predecessor frozen semantic candidate:

`c721b38cf8b00294797300b526596ce723a47ff8`

## Scope

This successor resolves one contradiction only: the R8V5-I034 int64-boundary reference vector conflicts with the already-frozen GCP-1 object-key ordering rule.

R8V3-I023 requires object keys to be sorted lexicographically by their NFC Unicode scalar sequence. For the keys `max` and `min`, `max` sorts before `min`.

Historical R8V5-I034 froze:

`{"min":-9223372036854775808,"max":9223372036854775807}`

SHA-256:

`906c504c6a5ceabaf14e06e427a9ed6d202a1a014d3c32616b00da5040590cab`

That historical source remains immutable, but its P05 byte/hash pair is superseded for the effective semantic lineage by:

`{"max":9223372036854775807,"min":-9223372036854775808}`

SHA-256:

`161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb`

## Preserved semantics

- R8V3-I023 object-key ordering is unchanged.
- The signed-int64 range is unchanged.
- No other GCP-1 canonicalization rule changes.
- No historical source file is rewritten.
- No implementation, runtime qualification, release, deployment, production, policy, schema-freeze or terminal authority is granted.

## Downstream consequence

Any executable-schema candidate using the old P05 bytes/hash is stale against this semantic successor. GCP-RVM-2, dependent provenance, exact-byte SPG evidence and the final independent executable-schema review must be regenerated/rebound.
