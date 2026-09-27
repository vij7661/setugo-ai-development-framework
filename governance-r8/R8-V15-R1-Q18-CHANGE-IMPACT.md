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

The trusted verifier root is explicitly pinned to commit `f71139a937be23bd5f4c545d3b3dc2199b47bc06` and tree `e7d311e25e2232452dd5c209d0825d277f487756`, independent of the final workflow head. Manual eligibility consumes only the receipt downloaded from the trusted artifact and its trusted proof; evidence-ref receipt and expected-identity files cannot select verifier authority or receipt truth.
