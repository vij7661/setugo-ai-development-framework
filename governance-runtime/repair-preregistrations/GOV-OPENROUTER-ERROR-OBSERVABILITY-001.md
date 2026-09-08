# GOV-OPENROUTER-ERROR-OBSERVABILITY-001

## Triggering evidence
Clean Slice5 integration R2 run `34245299365` on request `REV-MVP-SLICE5-INTEGRATION-R2-001` failed after OpenRouter returned an HTTP response body whose `model` field was absent. Runner v4 reported only `OpenRouter returned model mismatch ... returned=None`, discarding the provider body's actual error semantics before evidence persistence.

## Classification
Runner observability / provider-error classification defect. Candidate `c79c0bcf56717b7c27e89280cf65461b48ce479c` is unchanged. Review authority effect remains NONE.

## Frozen repair contract
1. Preserve v4 unchanged as historical runner evidence.
2. Add v5 as a narrow OpenRouter error-observability repair.
3. Parse OpenRouter response JSON before model verification.
4. If the response contains an `error` object, raise a provider error containing its code/type/message and do not misclassify it as a model substitution.
5. Persist the raw provider response body to the evidence directory before semantic/model validation whenever an HTTP response body was received.
6. Exact returned-model equality remains mandatory for non-error responses.
7. No request evidence, review dimensions, candidate binding, or provider/model binding may be weakened.
8. Existing Gemini/Groq behavior remains unchanged.
9. Deterministic tests must cover error-body classification, raw-body persistence helper behavior, exact model match, and actual model mismatch.
10. No deterministic test may call a real provider.

## Promotion effect
None. This repair only improves fail-closed diagnosis and evidence retention. The same frozen R2 request must be rerun after qualification.
