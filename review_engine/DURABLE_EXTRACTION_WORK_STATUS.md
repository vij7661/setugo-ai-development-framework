# Durable Extraction Work Replay Protection — Status

## Verified implementation baseline

- Implementation SHA: `673ffd313230a4eade5eead37e66c116e2873612`
- Exact-head GitHub Actions run: `33985367428`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The successful exact-head run covered the Review Engine system regressions plus the existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

`SQLiteExtractionWorkRegistry` provides single-node durable replay state for platform-issued claim-extraction work orders.

The retained work order binds:

- exact artifact SHA-256;
- risk;
- task type;
- extractor identity;
- extractor qualification reference;
- extractor qualification epoch.

Inventory admission revalidates the extractor qualification against the retained work-order scope. Consumption is transactional with `BEGIN IMMEDIATE` and an update conditioned on `consumed_at IS NULL`, preventing two concurrent SQLite consumers from both spending the same work order.

`WorkOrderBoundClaimCoverageRegistry` exposes durable replay protection only when its underlying work registry provides that durable control. `ReviewEngineApp` refuses GOVERNED claim-coverage assurance unless all of the following are enforced:

1. qualified extractor admission;
2. platform-issued extraction scope binding;
3. durable extraction work replay protection.

## Falsification coverage

`test_sqlite_extraction_work.py` verifies:

1. issued work survives a new registry/process instance;
2. consumed state survives restart and blocks replay;
3. an invalid inventory rolls back without consuming valid work;
4. extractor revocation after issuance is rechecked during atomic consume;
5. two concurrent consumers cannot both spend one work order.

The governed application regression also verifies that the old in-memory work-order registry is rejected while the SQLite-backed registry is accepted.

## Earlier false-green transition failure retained as evidence

When durable replay protection first became mandatory, the existing governed-application test still expected the in-memory work registry to be accepted. CI correctly failed at `fe966cde81abe178a39ff8c7f9542a3288ed3bbc` instead of allowing the stronger assurance label to pass with an obsolete test expectation.

A later regression run also exposed an observability-name mismatch: durable replay was enforced but the health response did not expose the new explicit `claim_coverage_durable_replay_protection` field. The implementation was corrected rather than weakening the regression.

## What this does not prove

This milestone is deliberately limited to **single-node durable transactional replay protection**. It does not claim:

- distributed consensus or multi-node linearizability;
- external/WORM immutability;
- protection from a privileged SQLite database rewrite;
- cryptographically signed extraction capabilities;
- cryptographic proof of remote provider/model runtime identity;
- semantic completeness or truth of the extracted claim inventory.

A privileged writer can still rewrite the SQLite database. Provider runtime attestation and externally anchored evidence remain separate integration boundaries.
