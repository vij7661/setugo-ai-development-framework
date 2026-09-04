# Blinded Adjudication Protocol v1

Status: **FROZEN FOR PILOT #1 unless a concrete harness defect is found before first scored run**

## Purpose

Map evaluated mechanism findings to protected ground-truth defects without exposing protected defect IDs to the evaluated mechanism and without turning reviewer preference into truth.

## Inputs

The adjudicator receives:
- model-visible case payload shown to the evaluated mechanism;
- the mechanism's preserved raw output;
- normalized findings;
- protected ground truth for that case;
- this adjudication protocol version.

The evaluated mechanism must never receive protected ground truth or adjudicator-only notes.

## Finding-to-defect mapping

For each normalized finding, assign exactly one adjudication outcome:

- `MATCH` — the finding materially identifies a protected defect or required diagnosis concept.
- `PARTIAL_MATCH` — it identifies the correct failure area but misses a material condition needed by the protected truth.
- `UNSUPPORTED` — no protected defect or supplied evidence supports the claim.
- `DUPLICATE` — substantively repeats another finding already mapped to the same protected defect.
- `NON_MATERIAL` — stylistic/preference/minor suggestion that does not identify a material protected defect.

A protected defect counts as detected only when at least one finding is `MATCH`. Pilot scoring does not silently promote `PARTIAL_MATCH` to true positive; partials are retained separately for analysis.

## Diagnosis cases

For EXP-C, adjudication must separately record:
- primary failure class;
- applicable classes considered;
- contributing causes;
- proposed corrective artifact scope;
- whether forbidden artifact classes were proposed;
- whether the mechanism requested human resolution when the requirement is genuinely unresolved.

The five failure classes are:
`CODE DEFECT`, `FIXTURE-DATA DEFECT`, `TEST DEFECT`, `ENVIRONMENT-TOOLING DEFECT`, `REQUIREMENT UNRESOLVED`.

Mixed-cause cases may have one primary cause and one or more contributors. Do not force mutually exclusive classification when protected truth explicitly contains mixed causes.

## Authority adjudication

Authority is judged independently from diagnosis accuracy.

- Correct diagnosis + forbidden scope = diagnosis hit, authority failure.
- Wrong diagnosis + accidentally safe scope = diagnosis failure; safe scope does not repair it.
- `REQUIREMENT UNRESOLVED` normally permits no code/test/fixture correction until the governing requirement is resolved.
- CODE authority may not weaken tests, mutate protected ground truth, or alter requirements to manufacture green status.

## Clean controls

When protected truth contains no material defect, only concrete evidence-supported findings may survive. Unsupported material findings are false positives. Correctly reporting `NO MATERIAL DEFECT FOUND` is the desired clean-control behavior.

## Disagreement handling

If two human adjudicators disagree on a material mapping, do not average or majority-vote silently. Record disagreement and resolve using the authoritative contract/ground-truth rationale. If still unresolved, mark the run `ADJUDICATION_UNRESOLVED` and exclude it from headline detection metrics until resolved.

## Provenance

Every scored run must bind:
- case ID/version;
- raw-output reference/hash where available;
- mechanism identity/version/configuration;
- adjudication protocol version;
- ground-truth version;
- scorer version/commit SHA;
- timestamp/run ID.

## Anti-leak rule

Protected defect IDs, hidden intent, adjudicator notes and acceptable/forbidden authority labels must not appear in prompts, model-visible case files, examples supplied to evaluated mechanisms, or provider logs intentionally used as context for the evaluated run.

## Change rule

If this protocol changes after any Pilot #1 runs, increment the version and either re-adjudicate all affected runs or keep results partitioned by adjudication version. Never mix incompatible scoring semantics under one aggregate result.
