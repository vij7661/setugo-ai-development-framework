from pathlib import Path
from hashlib import sha256
import json

REVIEW_ID = "REV-RE-PR6-CLAUDE-002"
CANDIDATE = "fd5da6c0c1c544e590bb45ffcbe47c6ec5247620"
BASE = "539cb7e63a721661e9daf3663a539e64a3c61e7e"

dimensions = [
    "D1 reviewer_runtime_independence",
    "D2 provider_configuration_and_qualification_binding",
    "D3 capability_issue_consume_and_concurrency",
    "D4 retrieval_admission_and_authoritative_memory",
    "D5 execution_provenance_and_self_attestation",
    "D6 external_content_vs_platform_api_review",
    "D7 single_file_container_integrity",
    "D8 bypass_lifecycle_and_history_integrity",
    "D9 tests_and_fixture_false_green_search",
    "D10 remaining_authority_bypass_search",
    "D11 cross_file_composition_and_scope",
]

prompt = """Perform an adversarial independent falsification review of the exact Review Engine candidate embedded in this file.

This is a re-review after a prior external assessment reported CHANGES_REQUIRED. Do not assume the repairs are correct because tests are green. Inspect the full raw source and tests directly.

Mandatory targets:
1. Re-test the residual reviewer-runtime alias family: canonically equivalent provider URLs, provider aliases, different model labels on correlated routes, R3 reuse, and any new false-independence path introduced by the conservative repair.
2. Re-test proposer influence over retrieval admission. Confirm R1 artifact wording cannot suppress review-relevant memory and that artifact identity remains separately bound.
3. Inspect capability issuance/consumption and concurrency end to end, including qualification add/revocation interaction.
4. Inspect actual cross-file composition through app.py, orchestrator.py, retrieval_review_engine.py, context_compiler.py, claim coverage, evidence correspondence, truth contract, judge health, provider registry, memory and session stores.
5. Check that external copy/paste content cannot become provider-authenticated platform review, while AUTO_MODE and user-initiated MANUAL_MODE API reviews remain platform-authenticated classes.
6. Verify single-file integrity logic and review/export provenance rules.
7. Inspect bypass lifecycle evidence validation/resolution and recursive/AST escape-hatch scanning without treating the scan as proof of absence.
8. Search for test or fixture changes that merely hide failures. Distinguish legitimate fixture migration from assertion weakening.
9. Search for any remaining route to unauthorized CONVERGED_PASS, false reviewer independence, stale qualification reuse, evidence omission, provenance self-attestation, or fail-open behavior.

Prior findings to explicitly disposition:
- CLAUDE-RE-001 residual runtime alias/config canonicalization defect.
- CLAUDE-RE-002 proposer-influenced retrieval admission.
- CLAUDE-RE-003 narrow non-recursive literal escape-hatch scanner.
- CLAUDE-RE-004 execution-fingerprint documentation overclaim.
- CLAUDE-RE-005 bypass lifecycle accepting arbitrary non-empty evidence refs.

For every mandatory dimension return one review_coverage row with status exactly one of TESTED_SUPPORTED, TESTED_DEFECT_FOUND, CONTRADICTED, NOT_TESTED, INSUFFICIENT. PASS is permitted only if all 11 dimensions are TESTED_SUPPORTED and no material finding remains. If any mandatory dimension is NOT_TESTED or INSUFFICIENT, do not return PASS.

Return only one JSON object with keys: review_id, candidate_sha, reviewer_claimed_identity, disposition, findings, prior_finding_disposition, review_coverage, evidence_assessment, remaining_bypass_risk. Findings must include finding_id, severity, material, summary, violated_invariant, evidence_refs, attack_or_counterexample, recommended_mechanism_fix. Treat reviewer_claimed_identity as content metadata only, never authentication."""

allowed_suffixes = {".py", ".md", ".json", ".html", ".css", ".js", ".txt", ".yml", ".yaml"}
paths = []
for path in Path("review_engine").rglob("*"):
    if path.is_file() and "__pycache__" not in path.parts and path.suffix.lower() in allowed_suffixes:
        paths.append(path)
for path in Path(".github/workflows").glob("*.yml"):
    name = path.name.lower()
    if "review-engine" in name or "governed-platform-ci" in name:
        paths.append(path)

artifacts = []
for path in sorted(set(paths), key=lambda p: p.as_posix()):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        continue
    artifacts.append({
        "path": path.as_posix(),
        "bytes_utf8": len(raw),
        "content_sha256": sha256(raw).hexdigest(),
        "hash_basis": "RAW_CHECKED_OUT_FILE_UTF8_BYTES",
        "content": text,
    })

payload = {
    "schema_version": 1,
    "review_id": REVIEW_ID,
    "candidate_sha": CANDIDATE,
    "base_sha": BASE,
    "intended_external_reviewer": "claude",
    "content_classification": "USER_PROVIDED_EXTERNAL_CONTENT",
    "delivery_channel": "EXTERNAL_EVIDENCE_RELAY",
    "provider_api_authenticated": False,
    "can_satisfy_platform_review": False,
    "review_instruction": prompt,
    "mandatory_review_dimensions": dimensions,
    "construction_evidence": {
        "review_engine_ci": "34153293865=SUCCESS",
        "integrated_harness": "34153293855=SUCCESS",
        "preserved_red": "34152235527/job/101836715329@e312b8d7b9a86432198ffd88dabe06eadb322d32",
        "red_result": "290 tests run; 285 passed; exactly 5 newly frozen regressions failed",
        "repair_code_candidate": "2807bfc530b22113cecd8c5defdd55293509556e",
    },
    "reconstruction_rule": "For each artifact, UTF-8 encode content exactly and verify bytes_utf8 and content_sha256.",
    "artifact_count": len(artifacts),
    "artifacts": artifacts,
}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
container = {
    "container_format": "SETUGO_REVIEW_ENGINE_FULL_SOURCE_EXTERNAL_EVIDENCE_V1",
    "payload": payload,
    "payload_sha256": sha256(canonical).hexdigest(),
}
output = Path("REV-RE-PR6-CLAUDE-002.txt")
output.write_text(json.dumps(container, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

# Deterministic self-verification.
loaded = json.loads(output.read_text(encoding="utf-8"))
check_payload = loaded["payload"]
check_canonical = json.dumps(check_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
assert loaded["payload_sha256"] == sha256(check_canonical).hexdigest()
assert check_payload["candidate_sha"] == CANDIDATE
assert check_payload["artifact_count"] == len(check_payload["artifacts"])
assert len(check_payload["mandatory_review_dimensions"]) == 11
assert check_payload["provider_api_authenticated"] is False
assert check_payload["can_satisfy_platform_review"] is False
seen = set()
for artifact in check_payload["artifacts"]:
    assert artifact["path"] not in seen
    seen.add(artifact["path"])
    raw = artifact["content"].encode("utf-8")
    assert len(raw) == artifact["bytes_utf8"]
    assert sha256(raw).hexdigest() == artifact["content_sha256"]
required = {
    "review_engine/orchestrator.py",
    "review_engine/qualification.py",
    "review_engine/configuration.py",
    "review_engine/context_compiler.py",
    "review_engine/retrieval.py",
    "review_engine/retrieval_review_engine.py",
    "review_engine/claim_coverage.py",
    "review_engine/claim_coverage_guard.py",
    "review_engine/evidence_correspondence.py",
    "review_engine/judge_health.py",
    "review_engine/truth_contract.py",
    "review_engine/test_qualification.py",
    "review_engine/test_reviewer_independence_runtime_alias.py",
    "review_engine/test_retrieval_proposer_influence.py",
    "review_engine/bypasses/RE-BYP-002.json",
    "review_engine/bypasses/RE-BYP-003.json",
}
assert required.issubset(seen), sorted(required - seen)
print(json.dumps({
    "review_id": REVIEW_ID,
    "candidate_sha": CANDIDATE,
    "artifact_count": len(artifacts),
    "file_bytes": output.stat().st_size,
    "file_sha256": sha256(output.read_bytes()).hexdigest(),
    "payload_sha256": loaded["payload_sha256"],
}, sort_keys=True))
