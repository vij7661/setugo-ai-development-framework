# Durable Atomic Claim Coverage Inventory — Status

## Verified implementation baseline

- Implementation SHA: `ccae44e4d9a4bf435167b34bc193a4b7c4ee39d6`
- Exact-head GitHub Actions run: `33987983077`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The successful exact-head run covered the Review Engine system regressions plus the existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control implemented

`SQLiteExtractionWorkRegistry` now retains admitted claim-coverage inventories in the same single-node SQLite ledger as extraction work state.

For each admitted inventory the ledger durably retains:

- inventory ID;
- exact artifact SHA-256;
- work-order binding;
- complete structured extractor identity;
- extractor qualification reference and epoch;
- provenance;
- completeness state;
- ordered claim text, claim type, materiality and fingerprint.

`consume_for_inventory` performs all of the following inside one `BEGIN IMMEDIATE` transaction:

1. load and validate the unconsumed work order;
2. validate exact artifact/extractor/qualification bindings;
3. recheck current extractor qualification for the retained work risk/task scope;
4. persist the complete claim-coverage inventory and claims;
5. mark the single-use work order consumed.

If inventory persistence conflicts or fails, the transaction rolls back and the work order remains unconsumed.

`SQLiteWorkOrderBoundClaimCoverageRegistry` reconstructs coverage assessments from the durable retained inventories rather than an in-memory cache. `ReviewEngineApp` refuses GOVERNED claim-coverage assurance unless all of the following are enforced:

1. qualified extractor admission;
2. platform-issued extraction scope binding;
3. durable extraction work replay protection;
4. durable retained inventory state;
5. atomic inventory admission and work consumption.

## Falsification coverage

`test_sqlite_extraction_work.py` verifies:

1. issued work survives restart;
2. consumed state survives restart and blocks replay;
3. admitted inventory survives restart and reconstructs exact coverage;
4. invalid inventory admission leaves no retained inventory and does not consume work;
5. a retained-inventory conflict rolls back the losing work order consumption;
6. extractor revocation after work issuance is rechecked before atomic admission;
7. concurrent attempts cannot both spend one work order;
8. concurrent same-extractor inventories for one artifact produce one retained winner and leave the losing work order unconsumed.

The governed application regression also verifies that a durable work-order ledger paired with the old in-memory inventory view is rejected, while `SQLiteWorkOrderBoundClaimCoverageRegistry` is accepted and exposes both durable-inventory and atomic-admission health signals.

## What this does not prove

This milestone is deliberately limited to **single-node durable transactional claim-coverage inventory admission**. It does not claim:

- distributed consensus or multi-node linearizability;
- external/WORM immutability;
- protection from a privileged SQLite database rewrite;
- cryptographically signed extraction capabilities;
- cryptographic proof of remote provider/model runtime identity;
- semantic completeness or truth of the extracted inventory;
- authenticity of any external evidence source used by an extractor;
- that a qualification revocation must or must not retroactively invalidate already-admitted inventories.

Qualification-revocation semantics for already-retained claim coverage remain a separate policy/control question and must not be inferred from this milestone.
