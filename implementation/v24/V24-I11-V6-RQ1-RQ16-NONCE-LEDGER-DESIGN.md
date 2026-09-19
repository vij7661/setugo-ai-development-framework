# Durable authorization nonce design

No live nonce is created in preregistration. Future authorization must use a root-owned, trusted append-only nonce ledger outside the candidate workspace. Consumption is an atomic create-with-exclusive semantics operation containing the nonce, authorization hash, arm, and timestamp. A second consume attempt fails closed as replay. The ledger must survive process restart, be non-candidate-writable, and be independently observed before and after use.

The JSON token is not authoritative by itself. The trusted issuer/reviewer artifact hash, exact plan/contract/runtime bindings, and root-owned source path must all validate before the nonce ledger is touched. No trusted issuer mechanism is available on this planning host, so future authorization remains `MANUAL_REVIEW_REQUIRED`.
