# EXP-M Self-Adjudication Record

## Status

`SELF_ADJUDICATION_COMPLETE_NO_OPEN_CRITICAL_OR_HIGH_DESIGN_FINDINGS`

Scope: preregistration/design review of EXP-M Review Evidence Delivery & Reviewer Context Integrity. No EXP-M scientific execution has occurred. No provider capability is qualified by this record.

Reviewed source commit before this adjudication record:

- branch: `experiment/exp-m-review-evidence-delivery-integrity`
- reviewed source commit: `2bbdf58f227103e8fae3aead8c7629dcfc9a41d0`
- reviewed source tree: `4e18f228d110eb0c03152cd0ab2a090cacaa43a5`
- base main commit: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`

Reviewed source identities:

- `standards/review-evidence-delivery-integrity.md` — Git blob `bcf1acbba9aceb6f1f8305396bdb4f61a1e054ff`
- `experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md` — Git blob `2ee6c15750cbe5344a296f6f9448566b72bac90b`
- `experiments/governed-platform/EXP-M-TEST-MATRIX.md` — Git blob `df3d8e045a321637102184ddeef0436888a99573`
- `governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md` — Git blob `e8434ed6b77f3355b554bdfed0305f9551ce792c`

## Method

The authoring model performed repeated adversarial self-review under a false-green posture:

1. identify a concrete authority or evidence-delivery bypass;
2. classify severity;
3. apply a narrow preregistration/design repair;
4. add a falsification invariant/test family;
5. repeat;
6. stop only when a fresh pass found no remaining Critical or High design defect in the preregistered boundary.

This is not independent review and cannot substitute for the requested external review.

## Round 1

### SA-M-C01 — Required-evidence self-selection

Severity: Critical.

Failure path: a delivery manifest could silently omit decisive evidence or mark it optional and still prove itself complete.

Repair:
- requiredness is now derived from governed ReviewRequest/dimensions/evidence refs/standards;
- delivery manifest cannot define its own required set;
- required/materialized/manifest closure is load-bearing;
- mutation/test added for required→optional downgrade and missing governed ref.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-C02 — Chunking falsely treated as context expansion

Severity: Critical.

Failure path: sending many individually valid chunks could exceed the model's final context and evict early mandatory evidence while the platform still reports completeness.

Repair:
- chunking is explicitly transport only;
- final adjudication must fit a qualified cumulative context or use a qualified persistent file/retrieval mechanism;
- decomposed review requires a governed aggregation/cross-interaction protocol;
- context-eviction tests added.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-C03 — Reviewer receipt/self-attestation used as delivery proof

Severity: Critical.

Failure path: a model can say `received_all=true` without having access to all mandatory content.

Repair:
- reviewer receipt is diagnostic and non-dispositive;
- platform delivery records and provider capability profile remain authoritative;
- fresh unpredictable witness probes were introduced for modes where remote accessibility otherwise cannot be evidenced;
- copied evidence IDs/hashes are explicitly not valid access witnesses.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H01 — Manifest intent not bound to actual API wire request

Severity: High.

Failure path: manifest contains all evidence, but trusted adapter serializes an API request that omits or changes one item.

Repair:
- WireDeliveryRecord binds manifest to exact semantic request payload;
- adapter identity/version, included evidence IDs, request-body hash, provider IDs and retry identity retained;
- wire omission/retry mutation tests added.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H02 — Provider capability profile could be untrusted or stale

Severity: High.

Failure path: candidate or stale profile asserts unsupported formats/context are safe.

Repair:
- provider capability profile is platform-owned, version/endpoint/model/account bound and expiring;
- candidate cannot widen its own review profile;
- repeated fresh probes and conservative safety margin required;
- model/backend/endpoint/profile-drift tests added.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H03 — Representation transformation and confidentiality/egress gap

Severity: High.

Failure path: lossy conversion/summary silently substitutes for required raw evidence, or sensitive evidence is sent to an unapproved provider.

Repair:
- source→representation transformation record with tool identity/hash, range coverage and loss classification;
- platform-owned transformation tooling requirement;
- data classification and egress authorization bound to delivery manifest;
- redaction/transformation cannot silently change load-bearing evidence.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H04 — Prompt-injection and decomposed-review dependency overclaim

Severity: High.

Failure path: perfect evidence delivery could be mistaken for a qualified material review even while candidate evidence can hijack prompts, or several narrow subreviews are aggregated without cross-evidence interaction review.

Repair:
- EXP-L/successor prompt/evidence isolation is an explicit production dependency;
- decomposed review cannot mint a global disposition without governed aggregation/cross-interaction coverage.

Status: RESOLVED_IN_PREREGISTRATION.

## Round 2

### SA-M-C04 — Candidate controls its own delivery governor

Severity: Critical.

Failure path: candidate under review modifies materializer, manifest builder, capability reader, completeness validator or verdict-admissibility code to omit its own decisive evidence and self-report complete delivery.

Repair:
- delivery-governor trust root explicitly placed outside candidate self-approval;
- materializer, transformer, manifest builder, preflight, provider adapter, completeness validator, insufficiency adjudicator and verdict-admissibility validator must execute from a pinned independently governed platform implementation;
- candidate-governor override tests added.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H05 — Single lucky provider call overqualifies context capability

Severity: High.

Failure path: one successful near-limit call widens a provider capability bound despite intermittent truncation.

Repair:
- repeated fresh witness trials;
- conservative qualified safe limit and safety margin;
- flaky-near-limit tests.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H06 — Endpoint/account/model drift and fallback reuses wrong capability

Severity: High.

Failure path: provider alias/backend/region/account or fallback model changes but old capability profile remains accepted.

Repair:
- profile/wire records bind account/tenant, endpoint/region, requested and reported model/deployment where available;
- material drift invalidates profile;
- automatic fallback creates a new delivery context/profile/attempt.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H07 — Candidate-controlled parser/archive attack surface

Severity: High.

Failure path: candidate parser transforms its own evidence favorably; archive path traversal, symlink escape, duplicate names, decompression bombs or parser exhaustion compromise materialization.

Repair:
- transformation/parser implementation must be platform-owned/pinned;
- bounded safe extraction/materialization requirements;
- archive traversal/resource-bomb/duplicate-name tests.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H08 — Evidence ID collision and provider file readiness ambiguity

Severity: High.

Failure path: one required artifact replaces another under colliding ID, or file upload success is treated as file-ready/model-accessible.

Repair:
- stable evidence ID derives from governed source identity + content hash;
- collisions/rebinding rejected;
- provider file qualification includes ingestion/processing readiness, retrieval coverage and expiry semantics.

Status: RESOLVED_IN_PREREGISTRATION.

## Round 3

### SA-M-H09 — Manifest-to-wire TOCTOU

Severity: High.

Failure path: platform hashes one source byte set during preflight, then reopens a mutable pathname and sends changed bytes.

Repair:
- wire serialization uses frozen representation bytes/chunks;
- immediate pre-dispatch revalidation;
- capability/egress/session validity rechecked;
- post-manifest source/representation mutation tests.

Status: RESOLVED_IN_PREREGISTRATION.

### SA-M-H10 — Reviewer silently widens evidence via web/tools

Severity: High.

Failure path: reviewer uses web/search/plugin/tool evidence not in the governed corpus and treats it as frozen review evidence.

Repair:
- reviewer tools disabled or explicitly governed;
- supplemental evidence requires provenance and explicit new/supplemental boundary;
- model recollection remains non-authoritative;
- tool access/version/provenance tests added.

Status: RESOLVED_IN_PREREGISTRATION.

## Round 4 — fresh adversarial pass

A fresh review was performed after the Round 3 repairs.

Result:

- open Critical design findings: 0
- open High design findings: 0

No remaining Critical/High false-green path was identified in the **preregistered design**.

The following are deliberately not claimed closed by design alone:

1. No EXP-M mechanism has yet been implemented or scientifically executed.
2. No real provider/model/API capability profile has yet been qualified under EXP-M.
3. Exact statistical/repetition thresholds for each live provider capability pilot remain to be fixed in the execution contract before those pilots.
4. Exact organization data-classification/egress policy content remains an implementation/governance prerequisite.
5. Current production review code on `main` does not become EXP-M-qualified merely because this branch defines the standard.
6. This self-adjudication is proposer/model self-review and has no independent-review authority.

These are execution/qualification prerequisites or Medium/Low design detail, not unresolved Critical/High defects in the preregistered boundary.

## Self-adjudication disposition

`SELF_REVIEW_BOUNDED_PASS_FOR_EXTERNAL_REVIEW`

Meaning:

- the design is ready to be challenged by an independent reviewer;
- EXP-M itself is NOT qualified;
- no provider review path gains authority;
- no current review verdict is retroactively upgraded;
- no implementation or promotion is authorized by this record.
