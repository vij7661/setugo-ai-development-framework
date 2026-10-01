# Q18 Change-Impact Record

| Finding | Adjudication | Files changed | Root cause closed / regression | API effect |
|---|---|---|---|---|
| H-01 | ACCEPTED_AS_PROPOSED | `governance-runtime/github_evidence_ingestion.py`, ref tests | Canonical heads/ normalization; malformed/tag/traversal refs fail before HTTP | Control/evidence only |
| H-02 | ACCEPTED_AS_PROPOSED | receipt/manual workflows, `stage_evidence_data.py`, staging tests | Immutable trusted checkout executes code; evidence-ref is allowlisted data only; code substitution and symlink regressions | Control/evidence only |
| H-03 | ACCEPTED_WITH_SEVERITY_ADJUSTMENT (MEDIUM) | historical Review003/004 workflows and preflight tests | Real command separation replaces literal `\\n\\n`; structural fixture rejects packaging defect | Control/evidence only |
| M-01 | ACCEPTED_AS_PROPOSED | pinned-action verifier/tests | Comments, quoting, whitespace, and Docker refs are parsed structurally and require immutable pins | Control/evidence only |
| L-01 | ACCEPTED_AND_SUBSUMED_BY_H-03 | preflight tests | Command separation is load-bearing, not proximity-based | Control/evidence only |
| L-02 | ACCEPTED_AS_PROPOSED_WITH_STRONGER_DESIGN | invariant workflow and verifier/tests | Exact step-name/run contract rejects echo, printf, heredoc, exit, conditional, and continue-on-error spoofing | Control/evidence only |
| L-03 | ACCEPTED_WITH_ALTERNATIVE_SOLUTION | queue and queue tests | Committed SHA/blob and original-upload SHA are separate; original upload is external-receipt-only | Control/evidence only |
| I-01 | ACCEPTED_AS_IMPLEMENTER_DISCOVERED (HIGH/blocking) | `governed_evidence_receipt.py`, GitHub adapter, v2 receipt tests | GitHub-downloaded ZIP archive/member/statement/run/job/workflow identities are cross-bound; duplicate/traversal/member substitution fails | Control/evidence only |

The v2 receipt explicitly separates GitHub archive digest from contained member digest. It fails closed on v1/ambiguous receipts in the Q18 eligibility path. Q17/Q16 frozen history remains immutable.

No repair changes Gemini endpoint, method, model, prompt, payload, provider parameters, timeout, retry, streaming, or response semantics. Authority effect remains `NONE`; fallback-to-3 remains active; six-slice cadence remains not restored.

Q18 pre-freeze adversarial remediation strengthens the same families: manual eligibility now requires a trusted GitHub-artifact receipt proof; verifier SHA/tree is checked at both ingestion and eligibility; review committed SHA is checked against exact GitHub content bytes and Git blob; governed action inventory parses block and flow YAML; and load-bearing steps reject unapproved shell semantics. These repairs remain evidence/control-plane only.

The trusted verifier root is explicitly pinned to commit `698d390dee9f062c984be8663aafc7994d009542` and tree `b5f89c29d91a2b55caec1815009d414e162bef11`, independent of the final workflow head. Manual eligibility consumes only the receipt downloaded from the trusted artifact and its trusted proof; evidence-ref receipt and expected-identity files cannot select verifier authority or receipt truth.

## PF2 pre-freeze remediation

| Finding | Root cause closed | Load-bearing regression | API effect |
|---|---|---|---|
| PF2-H01 | Receipt producer is fixed to the governed workflow path, `receipt-only` job, repository, exact run head, and artifact association; caller-selected workflow identifiers are ignored. | Wrong workflow, producer head, job, artifact, candidate, and replayed receipt tests fail before trust. | Control/evidence only |
| PF2-H02 | Manual ingestion grants only `contents: read` and `actions: read`, and supplies `github.token` only to the trusted fetch step. | Structural workflow check rejects missing token/permission and any write permission. | Control/evidence only |
| PF2-H03 | Committed review is fetched read-only from GitHub at an immutable revision/path and checked against receipt SHA/blob; verifier checkout is never used as review storage. | Wrong revision/path/blob/bytes and traversal tests fail. | Control/evidence only |
| PF2-H04 | Eligibility parses the receipt-bound committed review bytes; evidence-ref review text is not authoritative. | BOUNDED_PASS/CHANGES_REQUIRED split-brain and provenance mismatch cases fail. | Control/evidence only |
| PF2-M01 | Action lint rejects quoted-key/alias bypasses and discovers the complete governed workflow population. | Quoted flow keys, mutable Docker refs, local traversal, and omitted workflow tests fail. | Control/evidence only |
| PF2-M02 | Invariant step lint rejects quoted executable-control keys and unsupported YAML mappings. | Quoted shell/if/continue-on-error/run substitutions fail. | Control/evidence only |

All repairs preserve the provider request contract and keep `AUTHORITY_EFFECT = NONE`.

## PF4 pre-freeze remediation

| Finding | Status | Repair / invariant | Regression | API effect |
|---|---|---|---|---|
| PF4-H01 | CLOSED_AFTER_AUTHORIZED_PROMOTION | The independently authorized trusted verifier root is exactly commit `698d390dee9f062c984be8663aafc7994d009542`, tree `b5f89c29d91a2b55caec1815009d414e162bef11`; it provides the v2 gate and remains independent of the Q18 workflow HEAD. Historical blocked-state evidence is preserved above and in prior review records. | Exact-root declaration, v2 trusted receipt tests, and the Ubuntu invariant matrix bind the promoted root without substituting candidate HEAD. | Control/evidence only |
| PF4-C01 | ACCEPTED | Invariant workflow is a closed structural contract: exact top-level/triggers/permissions/env, one job, exact ordered steps, no extra/unnamed/duplicate steps, and no execution-environment controls. | Structural adversarial tests reject attacker jobs, write permissions, altered runner, env/defaults/container, unnamed/extra/duplicate steps. | Control/evidence only |
| PF4-H02 | ACCEPTED | Action lint rejects unsupported block scalars and escaped/aliased/tagged/quoted mapping representations; governed workflow inventory is exhaustive. | Mutable block-scalar actions, flow/quoted/escaped keys, Docker tags, traversal locals, and omitted workflows fail closed. | Control/evidence only |

PF4-H01 was previously blocked pending promotion and is now closed after the explicit authorization recorded for the exact successor root above. The trusted root remains independent of Q18 candidate HEAD `8326cd2599d274e2e1f2b87ca0ae1d8b0a226283`. `AUTHORITY_EFFECT = NONE`; fallback-to-3 remains active; six-slice cadence remains not restored. Frozen Q17 and all earlier history remain unchanged.
