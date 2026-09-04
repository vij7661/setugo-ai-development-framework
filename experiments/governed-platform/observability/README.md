# Execution Observability — MVP

Execution observability is part of governed autonomous execution, not cosmetic UI.

## Principle

The dashboard must render authoritative execution state. It must never infer that work is running merely because a model, chat, or previous workflow said so.

Authoritative inputs are execution events and evidence from the execution system (currently GitHub Actions), exact branch/SHA, case identity, provider/job status, continuation decision, repair attempt, and human-intervention state.

## MVP status model

Each execution exposes:

- campaign and experiment
- current case
- exact branch and SHA
- execution/run ID
- provider/agent/tool jobs and statuses
- evidence status
- failure classification when present
- automatic action/continuation decision
- repair attempt and repair budget
- next eligible work
- human intervention required: yes/no + reason
- timestamps

Scientific status is separate from execution status. A green workflow means execution succeeded; it does not mean the experiment scientifically passed until evidence is adjudicated.

## Initial view

```text
Governed Platform — Execution

Campaign      Experimental Baseline 1
Experiment    EXP-B
Case          EXP-B-003
Execution     COMPLETE
Scientific    AWAITING/REQUIRES ADJUDICATION
Human action  NOT REQUIRED

Jobs
  Groq        COMPLETE
  OpenRouter  COMPLETE
  Continuation COMPLETE

Exact SHA     <authoritative execution SHA>
Run ID        <GitHub Actions run ID>
Next          <controller decision>
```

## Architecture

```text
Execution events (GitHub/agents/tests)
        |
        v
Event Gateway / Normalizer
        |
        v
Authoritative Execution State
        |--------------------|
        v                    v
Continuation Controller   Status Renderer/API
        |                    |
        v                    v
Authority + next action    Dashboard / notifications
```

The dashboard and controller must consume the same normalized authoritative state to prevent display/control drift.

## MVP implementation sequence

1. Normalize GitHub workflow/job events into an execution-status document.
2. Verify branch, exact SHA, case ID and run ID before accepting an event.
3. Persist current state plus append-only event history/evidence references.
4. Render a repository-hosted status summary first.
5. Add a small web status page/API only after state correctness is tested.
6. Add push/live refresh later; polling is acceptable only as a display fallback, not as authoritative execution logic.

## Safety / governance

- Do not expose API keys, tokens, prompts containing secrets, or protected experiment truth.
- Do not let dashboard controls bypass the Corrective Authority Gate.
- Stale/out-of-scope events must be marked ignored, not overwrite current state.
- Provider/model capability never implies modification authority.
- Failed provider execution is not a semantic case verdict.
