# EXP-P Pilot 1 — Governed Review Latency Preregistration

## Purpose
Measure user-facing latency of the three governed sequential review paths discussed for production readiness, without changing EXP-I safety conclusions.

## Frozen paths
1. `R1-R2-R1`
2. `R1-R2-R1-R3`
3. `R1-R2-R1-R3-R1`

Each path is sequential. Later stages receive the frozen representative case plus the immediately prior stage output. No stage is parallelized for this pilot.

## Frozen first-run role mapping
- R1: Groq / `openai/gpt-oss-20b`
- R2: Gemini OpenAI-compatible endpoint / `gemini-3.8-flash`
- R3: Mistral / `mistral-small-latest`

This mapping is a performance candidate only. It grants no model qualification, reviewer authority, release authority, or production authorization.

## Frozen representative workload
- Case: `EXP-C-004`
- Temperature: `0.0`
- Maximum completion tokens: `600`
- Timeout per call: `120s`
- First scientific sample count: `10` complete iterations per path.
- Sequential stage timing measured with `time.perf_counter_ns()` around the HTTP operation.

## Endpoints
For each path report:
- successful complete-path sample count;
- failed/incomplete sample count;
- P50 end-to-end latency;
- P95 end-to-end latency using nearest-rank percentile;
- maximum end-to-end latency;
- P50/P95 by role occurrence/stage position;
- prompt/completion tokens when returned by provider;
- provider attempt count / retry incidence;
- exact provider/model mapping;
- execution SHA and workflow run ID.

## Separation of measurements
- `healthy_first_attempt`: every stage completed on its first provider HTTP attempt.
- `recovered_retry`: at least one stage required an HTTP retry.
- `failed_path`: a stage exhausted or returned an unusable/nonterminal completion.

Primary latency statistics MUST use only `healthy_first_attempt` samples. Retry and failure latency are reported separately and may not be silently mixed into the healthy distribution.

## Percentile rule
Nearest-rank percentile: after sorting N values ascending, percentile p selects rank `ceil(p*N)`, 1-indexed. With N=10, P95 is the 10th observation. This limitation must be stated; production readiness requires a larger later sample.

## First-run acceptance / interpretation
This is a measurement experiment, not a speed pass/fail gate. The first run is scientifically usable only if:
- all three paths are attempted exactly 10 times;
- every recorded stage has monotonic start/end timing and nonnegative duration;
- output identifies failed/retried paths instead of dropping them;
- no path is called "production ready" from this pilot alone.

## Cost/safety boundary
Exactly 120 stage calls are scheduled by the frozen 10-iteration matrix if no retry occurs: 30 calls for R1-R2-R1, 40 for R1-R2-R1-R3, and 50 for R1-R2-R1-R3-R1. Provider-internal retries may increase HTTP attempts and must be recorded.

## Bounded conclusion
A clean run establishes measured latency only for this provider/model mapping, workload, output cap, runner region, provider conditions, and sampling window. It does not establish universal latency, SLA/SLO compliance, or production authorization.
