# Web-First Production Readiness — Test-to-Production Promotion Boundary

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Base: `f67e0dfb4fe9b4bb67c76dbd43f1485861c96fc0` (Slice1→Slice5 clean integration on `main`).

## 1. Product posture

The governed AI platform is **web-first**. The initial production product surface is a responsive web application backed by governed APIs/runtime services. Native mobile applications are not part of this boundary.

## 2. Goal

Falsify whether one exact tested artifact can cross an explicit environment boundary:

`TESTING → RELEASE_CANDIDATE → PRODUCTION`

without allowing branch labels, workflow green status, model/reviewer claims, environment-name substitution, rebuilds, missing provenance, stale evidence, or test credentials to manufacture production authority.

## 3. Core rule

**Build once, promote the same artifact.**

A production promotion must bind the exact source commit SHA and exact immutable artifact digest that were qualified in testing and admitted as a release candidate. Production must never rebuild from source and then assume equivalence.

## 4. Environment states

- `TESTING`: experiments, integration tests, provider/reviewer qualification, migrations and deployment rehearsal. No production authority.
- `RELEASE_CANDIDATE`: exact artifact frozen after mandatory qualification. Still no production deployment authority.
- `PRODUCTION`: reachable only through a valid production authorization record for the exact release-candidate identity.

Environment names are data, not authority. Merely setting `environment=production` cannot grant authority.

## 5. Frozen records

### Promotion Manifest
Must bind at least:
- `promotion_id`
- `source_commit_sha`
- `artifact_digest`
- `artifact_type`
- `build_provenance_digest`
- `testing_run_ids`
- `testing_evidence_digest`
- `review_evidence_digest`
- `final_adjudication_digest`
- `from_environment`
- `to_environment`
- `prior_promotion_digest` when advancing from release candidate
- `manifest_digest`

### Production Authorization
Must bind at least:
- `authorization_id`
- `promotion_id`
- `source_commit_sha`
- `artifact_digest`
- `release_candidate_manifest_digest`
- `authorized_environment = PRODUCTION`
- `authorization_evidence_digest`
- `expires_at` or explicit non-expiring policy
- `authorization_digest`

Neither record may be created or widened by model/tool output.

## 6. Authority invariants

**PB-I01 Exact artifact continuity** — source SHA and artifact digest must remain identical from testing through release candidate through production.

**PB-I02 No rebuild laundering** — a different artifact digest from the same source SHA is a different artifact and requires fresh qualification.

**PB-I03 Exact evidence binding** — testing, review and final-adjudication evidence must bind the exact source SHA/artifact digest.

**PB-I04 Stale evidence denial** — evidence for another SHA, artifact, request, review or run cannot authorize the candidate.

**PB-I05 Ordered transition** — `TESTING → PRODUCTION` direct promotion is forbidden; production requires a prior valid `RELEASE_CANDIDATE` manifest.

**PB-I06 Production authorization separation** — release-candidate qualification alone does not authorize production.

**PB-I07 Environment substitution denial** — changing an environment label or workflow input cannot widen authority.

**PB-I08 Credential-domain separation** — testing/staging credentials are never accepted as production authorization evidence.

**PB-I09 Model/reviewer non-authority** — model output, reviewer PASS or workflow success are evidence inputs only; deterministic policy decides promotion eligibility.

**PB-I10 Exact-head/freeze** — source branch/head movement after qualification invalidates promotion unless a new exact candidate is frozen and requalified.

**PB-I11 Replay/idempotency** — replaying the same exact valid promotion converges to the same result; rebinding a promotion ID to another artifact fails closed.

**PB-I12 Provenance completeness** — missing source, artifact, build provenance, test evidence, review evidence or adjudication evidence blocks promotion.

**PB-I13 Production rollback identity** — rollback target must itself be a previously authorized production artifact; arbitrary historical SHA rollback is forbidden.

**PB-I14 Auditability** — every accepted/denied promotion produces deterministic evidence describing exact identities and denial reasons.

## 7. Frozen acceptance cases

- `PB-01` exact qualified TESTING artifact becomes RELEASE_CANDIDATE.
- `PB-02` same release candidate + exact production authorization becomes PRODUCTION-eligible.
- `PB-03` direct TESTING→PRODUCTION is denied.
- `PB-04` source SHA substitution is denied.
- `PB-05` artifact digest substitution/rebuild is denied.
- `PB-06` testing evidence for another artifact is denied.
- `PB-07` review/adjudication evidence for another candidate is denied.
- `PB-08` environment label substitution cannot grant authority.
- `PB-09` missing production authorization is denied.
- `PB-10` production authorization for another artifact is denied.
- `PB-11` model/reviewer claim of production readiness cannot bypass deterministic denial.
- `PB-12` exact promotion replay is idempotent; promotion-ID rebinding is denied.
- `PB-13` rollback only accepts a previously production-authorized artifact.
- `PB-14` incomplete provenance fails closed.
- `PB-15` expired production authorization fails closed.
- `PB-16` denial/acceptance evidence is deterministic for identical inputs.

## 8. Nonclaims

Passing this boundary does not itself create a production hosting environment, managed database, queue, secure sandbox, DNS, TLS, cloud IAM, secret manager, web UI, or deployment runtime. It proves only the deterministic promotion authority boundary. Real environment resources and credentials must later be separately provisioned and qualified.
