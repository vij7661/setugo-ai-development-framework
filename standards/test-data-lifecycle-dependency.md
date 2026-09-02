# Test Data Lifecycle & Dependency Integrity

Every automated test or manual-QA case must declare the authoritative starting state and the data prerequisites required for the behavior under test. Validate those preconditions before executing state-changing actions.

- Eliminate accidental dependencies between tests. A test must not pass only because another test happened to leave mutable database state behind. Use isolated data, deterministic setup, or explicit reset/reseed where independence is required.
- Model legitimate workflow dependencies explicitly. When one step produces identifiers or state required by a later step, capture and propagate that authoritative output rather than reconstructing or hard-coding it.
- When a test mutates persistent lifecycle state, later tests must respect the resulting state. The same identity or record must not be treated as though it remained in an earlier state unless a controlled reset/reseed restored that precondition.
- Test fixtures must represent real contract-defined business states, including prerequisite records, valid relationships, lifecycle checkpoint, and allowed next actions.
- For stateful fixtures define a reuse policy: stable read-only, stable until mutated, disposable/consumable, or reset-required.
- A precondition mismatch must be surfaced and classified rather than bypassed to force the desired path.

## Required stateful test declaration

For stateful workflows record:

`starting state -> prerequisites -> action -> authoritative transition -> resulting state -> reuse/reset policy`

The governing principle is: **eliminate accidental dependencies; explicitly model legitimate dependencies.**
