# Configuration Secret Boundary Status

Validated implementation SHA: `3404c1eef9ad085a2502f65655a0848c8191f334`

Exact-head GitHub Actions run: `33989417254` — **SUCCESS**.

## Enforced contract

The Review Engine configuration is now a fail-closed schema rather than an open JSON bag:

- root fields are limited to `providers`, `reviewers`, and `qualifications`;
- reviewer roles are limited to R1/R2/R3;
- reviewer objects accept only the current declared reviewer configuration fields;
- qualification records accept only current qualification fields;
- each supported provider adapter has an explicit allowed field set;
- unknown fields are rejected instead of silently persisted/ignored;
- credential-shaped field names are normalized before checking, so aliases such as `apiKey`, `api-key`, `access_token`, `bearerToken`, `client_secret`, `authorization`, `password`, and `credentials` fail closed;
- nested authorization headers are rejected;
- `api_key_env` remains an allowed secret reference and raw API-key values are not part of the configuration contract.

## Regression evidence

`test_configuration.py` now includes regressions for:

- common raw-credential aliases,
- custom authorization headers,
- unknown provider fields,
- unknown reviewer fields,
- unknown root fields,
- unknown qualification fields,
- continued acceptance of an environment-variable secret reference.

## Non-claims

This protects the Review Engine's declared JSON configuration schema. It does not claim that arbitrary unrelated files, process environments, operating-system secret stores, provider infrastructure, or privileged filesystem access are governed by this parser.
