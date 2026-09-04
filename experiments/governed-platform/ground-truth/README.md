# Protected Ground Truth — Pilot #1

Real Pilot #1 ground truth MUST NOT be committed to this model-visible repository when evaluated mechanisms can read repository contents.

## Local/private layout

Create a private directory outside the repository, for example:

```text
<private-root>/governed-platform-pilot-1/
  truth/
    EXP-A-001.json
    EXP-B-001.json
    ...
  adjudication/
  runs/
  scores/
```

The public case's `ground_truth_ref` is an opaque locator only. The runner/scorer receives the private truth path separately after evaluated output has been captured.

## Ground-truth record

Each private record should contain at minimum:

```json
{
  "case_id": "EXP-X-000",
  "case_version": "1.0",
  "truth_version": "1.0",
  "defects": [
    {
      "defect_id": "D1",
      "class": "CODE DEFECT",
      "severity": "HIGH",
      "required_concept": "plain-language condition for credit",
      "acceptable_authority": ["production:bounded-scope"],
      "forbidden_authority": ["tests", "requirements"]
    }
  ],
  "clean_control": false,
  "notes": "private adjudication notes"
}
```

## Protection rule

Ground truth must be established before evaluated runs and hash-bound to the case/truth version. It may be corrected only through an explicit ground-truth correction record; never rewrite it after seeing a model result merely to improve a score.

The public repository may contain schemas/templates/examples, but not the answers for active blinded cases.
