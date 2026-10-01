# Q14 — Permanent-Invariant Implementation

Tracker: GitHub issue #61

Source design/orchestration head:
- branch: integration/r8-v15-r1-post-sg1-successor3-2026-09-26
- commit: 50c3ec6e19750b1f952e4b5618e1cf65807ad386
- tree: d825ec1cd7bbc4a05bce5119d2471fa3be09a7f5

This file is orchestration metadata only. All substantive implementation, repair, tests, invariant completion, and validation on this branch are assigned to Codex.

Codex must:
- inspect issue #61 in full;
- independently inspect the current proposed standards/code;
- repair/finish them rather than assuming they are correct;
- preserve provider-facing API request semantics for governance-only changes;
- enforce complete reviewer evidence delivery;
- require reviewer remediation/test proposals but treat them as advisory;
- close the latest Successor-2 findings structurally;
- update the machine-readable queue/manifest if required;
- run the complete required local/static/unit test matrix;
- report exact final HEAD/tree/changed paths;
- stop before freeze/evidence/review/merge/authority operations.

Authority effect: NONE.
Fallback-to-3 remains ACTIVE.
Six-slice cadence remains NOT restored.


## Added reviewer source-delivery modes

Codex must extend the reviewer-evidence delivery design to support these governed modes:

1. AUTHENTICATED_GITHUB_MCP_READ_ONLY
   - preferred when the reviewer/provider supports authenticated GitHub MCP access;
   - exact repository + immutable commit SHA + exact path/object binding;
   - GitHub access must be read-only;
   - model/reviewer must not receive raw GitHub credentials;
   - execution evidence must record every GitHub object/tool result actually consumed;
   - mutable branch names such as main are not sufficient review identity.

2. PROVIDER_URL_CONTEXT
   - allowed only when the provider explicitly supports URL fetching/context;
   - public GitHub only unless authenticated access is independently proven;
   - use immutable commit-addressed URLs, not moving branch URLs;
   - record fetched URL/object identity and verify the exact content delivered.

3. PLATFORM_MATERIALIZED_CONTENT
   - platform fetches exact GitHub objects itself;
   - verifies repo/commit/path/blob/content identity;
   - sends exact content/file/chunks to the reviewer;
   - preferred fallback for providers without native GitHub/MCP access.

4. URL_ONLY
   - locator only;
   - must never count by itself as evidence that the reviewer actually received or reviewed the repository content.

For GitHub MCP or URL-context modes, add a reviewer access manifest that records:
- provider/reviewer identity;
- delivery mode;
- repository;
- exact commit SHA;
- exact path/object/tool accessed;
- Git blob/object identity where available;
- content SHA-256/byte count where materialized;
- access/result status;
- whether the access was read-only;
- whether all mandatory review subjects were actually covered.

No raw access token, bearer token, GitHub PAT, or other credential may be placed in prompts, model-visible review content, persisted evidence, or fingerprints.

These modes extend the existing reviewer-evidence-delivery invariant; they do not weaken complete-delivery requirements.
