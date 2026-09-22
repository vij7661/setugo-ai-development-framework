# EXP-M R2E External Review R2 — Remediation Adjudication

Status: **REMEDIATED_PENDING_FRESH_S_E_P_Q_AND_INDEPENDENT_REVIEW**

Authority effect: **NONE**

EXP-M state: **NOT_QUALIFIED**

Live provider/API execution: **false / unauthorized**

This record maps every finding from `EXP-M-R2E-EXTERNAL-REVIEW-R2.md` to the narrow remediation implemented after that review. It is internal remediation evidence only. It does not convert the external CHANGES_REQUIRED disposition into PASS. Closure requires a fresh immutable S -> E -> P -> Q sequence, successful offline falsification and bundle verification, followed by independent review of that fresh bundle.

## R2-F1 — Unrecorded result post-processing

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- Removed the evidence-generator post-processing step that mutated self-falsification after command execution.
- `self_falsify_exp_m.py` now consumes the already source-bound CA-1..CA-10 result inside the governed command, verifies its S commit/tree and zero-survivor closure, and emits the final CA-inclusive self-falsification JSON itself.
- Result-producing commands are now required to have raw stdout bytes exactly equal to the final result artifact bytes.
- Command capture schema v2 records command-source path/SHA-256, S commit/tree, stdout/stderr hashes and sizes, result SHA-256/size at command exit, and the exact stdout/result equality flag.
- Evidence generation fails closed on any result/stdout mismatch; S-E-P verification independently rechecks those bindings.

Residual authority: NONE.

## R2-F2 — Conflicting delivery-authority records

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- A preregistered authority-root-v2 commit was created before the dependent implementation changes: `251647e5f44d394b761f1c6cdbb02a779901bc43`.
- Root v2 removes the legacy delivery ledger from current authority and freezes a deterministic current-S delivery-binding policy.
- The legacy signed `reviewed_commit=2814499a...` remains only a signed expectation sentinel and is explicitly labeled `LEGACY_SIGNED_EXPECTATION_SENTINEL_ONLY`.
- `EXP-M-SOURCE-FREEZE.json` no longer contains a field named delivery authority. It records `delivery_binding` with `role=DERIVED_BINDING_EVIDENCE` and `authoritative=false`.
- The production authority loader derives the current-S delivery expectation from the preregistered root policy plus the independently verified S identity. It rejects source-freeze policy/root substitution.
- The S-E-P verifier independently resolves authority root v2 and recomputes the same delivery binding.

Residual authority: authority remains solely the preregistered root policy; source freeze grants none.

## R2-F3 — Missing source-freeze generation provenance

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_EVIDENCE**

Remediation:
- `freeze_source.py` is now the first governed evidence command.
- It prints the exact final `EXP-M-SOURCE-FREEZE.json` bytes to stdout.
- Evidence capture records its S commit/tree, exact command, command-source SHA-256, stdout/stderr hashes/sizes, result SHA-256/size, exit code, and exact stdout/result equality.
- Source freeze remains an E artifact and the verifier independently validates its result/capture/source bindings.

## R2-F4 — Incomplete Q / S-E-P-Q verification

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_SEQUENCE**

Remediation:
- `verify_exp_m_sep_sequence.py` now accepts `--handoff Q`.
- It resolves and reports Q commit/tree/parent, requires Q parent=P, and requires P->Q to change only the review-handoff document.
- The verifier records its own S path/SHA-256.
- Final workflows produce an explicit S-E-P-Q verification JSON.
- The portable bundle generates a post-Q `FINAL-REVIEW-HANDOFF.md` containing exact S/E/P/Q commit/tree identities, avoiding commit self-reference.

## R2-F5 — Full mutation/self-falsification results unavailable

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_PACKET**

Remediation:
- P now embeds the full mutation-results JSON and the full self-falsification-results JSON, not only summaries.
- E still hash/size binds those complete artifacts.
- The portable review bundle includes the complete E artifacts and manifest.

## R2-F6 — Misleading CA-9 field name

Adjudication: **REMEDIATED**

Remediation:
- Compound schema bumped to v2.
- `rejection_reason` renamed to `blocking_guard`.
- `rejection_reason_semantics` renamed to `blocking_guard_semantics`.
- CA-9/CA-10 explanatory semantics remain preserved.

## R2-F7 — Handoff alone cannot verify Git objects/hashes

Adjudication: **REMEDIATED_IN_DESIGN_PENDING_FRESH_BUNDLE**

Remediation:
- The portable bundle now includes a nested Git bundle containing S/E/P/Q, preregistered authority, and indexed historical commits.
- It includes `VERIFY-BUNDLE.py`, which verifies every outer bundle manifest entry, verifies the nested Git bundle, fetches the custom review refs into a temporary repository, recomputes commit/tree identities, recomputes each recorded Git blob identity, and checks included bytes against Git objects.
- It includes `OFFLINE-VERIFY.md` with no-network verification steps.
- It includes explicit S-E-P-Q verification output and `FINAL-REVIEW-HANDOFF.md`.
- `BUNDLE-MANIFEST.json` attests every other outer archive entry; its own exclusion is explicit to avoid recursive self-hashing.

## Closure rule

No finding above is externally closed by this adjudication. The next allowed sequence is:
1. run the full offline falsification/preflight against the exact latest source;
2. if green, freeze a new S;
3. generate fresh E, P, Q and portable review bundle;
4. independently verify the bundle and S-E-P-Q capture;
5. send that fresh bundle to an independent reviewer.

Until step 5 returns an independent acceptable disposition:

- EXP-M = NOT_QUALIFIED
- Authority effect = NONE
- Live provider/API execution = false / unauthorized
