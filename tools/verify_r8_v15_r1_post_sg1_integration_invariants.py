"""Candidate-level invariant gate for the single post-SG1 convergence tree."""
from __future__ import annotations
import ast, hashlib, importlib.util, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "7cd2787d85b189a4161f271ee131e42bd961140a"
EXPECTED_RUNTIME_BLOB = "0f2e7f7a917adc584fb79d91a60f708713becd35"

def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def expect_reject(parser, text: str):
    try:
        parser(text)
    except ValueError:
        return
    raise AssertionError("structured hidden finding declaration was accepted")

def review_doc(extra_e: str = "") -> str:
    return (
        "A. OVERALL_DISPOSITION\nBOUNDED_PASS\n"
        "B. IDENTITY\nproposal\n"
        "C. CRITICAL_FINDINGS\nNONE.\n"
        "D. HIGH_FINDINGS\nNONE.\n"
        f"E. MEDIUM_LOW_FINDINGS\n{extra_e or 'None.'}\n"
        "F. ASSESSMENT\npass\n"
        "G. BOUNDARY\nLOCAL\n"
        "H. FINAL_GATE\n"
        "Stage2 SG-1 may be explicitly activated by user: YES\n"
        "Broader Stage2 semantic authority granted: NO\n"
    )

def main():
    head = run("git","rev-parse","HEAD")
    tree = run("git","rev-parse","HEAD^{tree}")
    changed = run("git","diff","--name-only",f"{BASE}..HEAD").splitlines()

    manifest = json.loads((ROOT/"governance-r8/R8-V15-R1-POST-SG1-CONVERGENCE-MANIFEST.json").read_text())
    assert manifest["status"] == "OPEN_CONVERGENCE_NOT_FROZEN"
    assert manifest["authority_effect"] == "NONE"
    assert all(v is False for v in manifest["grants"].values())
    assert manifest["fallback_to_3"] == "ACTIVE"
    assert manifest["six_slice_cadence_restored"] is False
    assert manifest["expected_changed_file_count"] == 29
    assert len(changed) == manifest["expected_changed_file_count"], (len(changed), manifest["expected_changed_file_count"])
    assert manifest["semantic_gap_inventory"]["classification"] == "HISTORICAL_STAGE1_BOUND_EVIDENCE"
    assert manifest["semantic_gap_inventory"]["candidate_commit"] == "4984f06a4420b76ad1ad475751aebda04a2d2c5c"
    assert manifest["semantic_gap_inventory"]["base_commit"] == "751162ee42c603cb6c84ee12021d16bab6fa626b"
    assert manifest["semantic_gap_inventory"]["not_regenerated_from_successor"] is True

    # One-tree composition: #44 is the single runtime winner; stale packet artifacts are excluded.
    runtime_blob = run("git","rev-parse","HEAD:governance-runtime/r8_v15_r1_frozen_schema_runtime.py")
    assert runtime_blob == EXPECTED_RUNTIME_BLOB, (runtime_blob, EXPECTED_RUNTIME_BLOB)
    evidence_src = (ROOT/"tools/r8_evidence_bundle_integrity.py").read_text()
    assert "from r8_v15_r1_frozen_schema_runtime import read_confined_file" in evidence_src
    for forbidden in manifest["excluded_historical_packet_artifacts"]:
        assert forbidden not in changed, f"historical packet artifact leaked into candidate: {forbidden}"

    # Parser invariant: structured line-start declarations outside C/D are always rejected.
    sys.path.insert(0, str(ROOT/"tools"))
    import r8_v15_r1_review_contract_parser as rp
    structured = [
        "CRITICAL:hidden",
        "HIGH:hidden",
        "CRITICAL: hidden",
        "HIGH: hidden",
        "CRITICAL-hidden",
        "HIGH — hidden",
        "CRITICAL FINDING hidden",
        "HIGH FINDING hidden",
        "- CRITICAL hidden",
        "* HIGH FINDING hidden",
    ]
    for marker in structured + [
        "CRITICAL_FINDING: hidden",
        "HIGH_FINDING: hidden",
        "1. CRITICAL: hidden",
        "1) HIGH hidden",
        "• HIGH: hidden",
        "[ ] CRITICAL hidden",
        "> HIGH hidden",
        "*** CRITICAL hidden",
        "CRITICAL:\nhidden",
        "HIGH:\nhidden",
    ]:
        expect_reject(rp.parse_review_contract, review_doc(marker))

    # Non-C/D heading lines cannot smuggle findings.
    base_doc = review_doc()
    for original, injected in (
        ("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION CRITICAL: hidden"),
        ("B. IDENTITY", "B. IDENTITY HIGH: hidden"),
        ("E. MEDIUM_LOW_FINDINGS", "E. MEDIUM_LOW_FINDINGS CRITICAL: hidden"),
        ("F. ASSESSMENT", "F. ASSESSMENT HIGH: hidden"),
        ("G. BOUNDARY", "G. BOUNDARY CRITICAL: hidden"),
        ("H. FINAL_GATE", "H. FINAL_GATE HIGH: hidden"),
    ):
        expect_reject(rp.parse_review_contract, base_doc.replace(original, injected, 1))

    # Controlled declarations cannot be hidden in headings or prose.
    for malformed in (
        base_doc.replace(
            "H. FINAL_GATE",
            "H. FINAL_GATE Stage2 SG-1 may be explicitly activated by user: NO",
            1,
        ),
        base_doc.replace(
            "H. FINAL_GATE",
            "H. FINAL_GATE Broader Stage2 semantic authority granted: YES",
            1,
        ),
        base_doc.replace(
            "E. MEDIUM_LOW_FINDINGS\nNone.",
            "E. MEDIUM_LOW_FINDINGS\nNote: Stage2 SG-1 may be explicitly activated by user: NO",
            1,
        ),
        base_doc.replace(
            "E. MEDIUM_LOW_FINDINGS\nNone.",
            "E. MEDIUM_LOW_FINDINGS\nHowever, Broader Stage2 semantic authority granted: YES",
            1,
        ),
    ):
        expect_reject(rp.parse_review_contract, malformed)

    # Ordinary inline prose is not a machine-readable finding declaration.
    rp.parse_review_contract(review_doc("The parser rejects CRITICAL: labels in structured line-start form."))

    # Historical exact review regression.
    for name in (
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt",
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt",
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt",
    ):
        rp.parse_review_contract((ROOT/"governance-r8"/name).read_text(encoding="utf-8"))

    # Preflight must parse/hash one byte stream: no parse_review_file call; exactly one read_bytes in validate_artifact.
    preflight_path = ROOT/"tools/preflight_r8_v15_r1_stage2_sg1_review.py"
    tree_ast = ast.parse(preflight_path.read_text())
    fn = next(n for n in tree_ast.body if isinstance(n, ast.FunctionDef) and n.name == "validate_artifact")
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
    assert not any(isinstance(c.func, ast.Name) and c.func.id == "parse_review_file" for c in calls)
    read_bytes_calls = [c for c in calls if isinstance(c.func, ast.Attribute) and c.func.attr == "read_bytes"]
    assert len(read_bytes_calls) == 1, len(read_bytes_calls)

    # Every workflow preflight command must pin raw SHA-256 and Git blob on the same shell command block.
    for wf in (
        ".github/workflows/r8-v15-r1-stage2-sg1-review-packet.yml",
        ".github/workflows/r8-v15-r1-stage2-sg1-review003-remediation-packet.yml",
        ".github/workflows/r8-v15-r1-stage2-sg1-review004-remediation-packet.yml",
    ):
        text = (ROOT/wf).read_text()
        starts = [m.start() for m in re.finditer(r"python3 tools/preflight_r8_v15_r1_stage2_sg1_review\.py", text)]
        assert starts, wf
        for s in starts:
            block = text[s:text.find("\n\n", s) if text.find("\n\n", s) != -1 else len(text)]
            assert "--expected-sha256" in block and "--expected-blob" in block, (wf, block)
        validator_lines = [line for line in text.splitlines() if "python3 tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py" in line]
        assert validator_lines
        assert all("--expected-sha256" not in line and "--expected-blob" not in line for line in validator_lines)
        assert all("--review " in line for line in validator_lines), (wf, validator_lines)

    # Semantic inventory must verify the complete canonical scan, not self-hash/subsets.
    import r8_v15_r1_stage2_semantic_gap_inventory as inv
    inventory_path = ROOT/"governance-r8/R8-V15-R1-STAGE2-SEMANTIC-GAP-INVENTORY.json"
    assert inv.verify_inventory(inventory_path)
    tampered = json.loads(inventory_path.read_text())
    assert tampered["items"]
    tampered["items"][0]["classification"] = "tampered"
    data = dict(tampered)
    data.pop("inventory_sha256", None)
    raw = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    tampered["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
    with tempfile.TemporaryDirectory(prefix="r8-invariant-inventory-") as td:
        p = Path(td) / "inventory.json"
        p.write_text(json.dumps(tampered, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        assert inv.verify_inventory(p) is False

    # Evidence verifier must be strict: missing independent expected identities must fail.
    import r8_evidence_bundle_integrity as ev
    with tempfile.TemporaryDirectory(prefix="r8-invariant-evidence-") as td:
        root = Path(td)
        fixture = root / "_invariant-gate-file"
        fixture.write_text("ok", encoding="utf-8")
        parent_alias = root / "a" / ".." / "_invariant-gate-file"
        try:
            ev.file_digest(root, parent_alias)
        except (ValueError, RuntimeError):
            pass
        else:
            raise AssertionError("direct parent traversal alias was accepted")
        assert ev.file_digest(root, root / "." / "_invariant-gate-file") == ev.file_digest(root, fixture)
    sig = __import__("inspect").signature(ev.verify_bundle)
    required_expected = {
        "expected_run_id","expected_job_id","expected_workflow","expected_head",
        "expected_inputs","expected_archive_sha256","expected_activation_verification",
        "expected_schema","expected_archive_format"
    }
    assert required_expected.issubset(sig.parameters)
    assert "expected_schema" in sig.parameters and "expected_archive_format" in sig.parameters

    # Queue manifest/tool validation must succeed and preserve all-false authority.
    import r8_work_queue as wq
    q = wq.load()
    assert all(v is False for v in q["authority"].values())
    manifest_ids = {task["id"] for task in q["tasks"]}
    task_ids = {
        p.name.split("-", 1)[0]
        for p in (ROOT/"governance-r8/codex-work-queue").glob("Q[0-9][0-9]-*.md")
    }
    assert task_ids - manifest_ids == set(), (task_ids - manifest_ids)

    # Direct governed runtime lexical parent traversal must fail closed.
    runtime = load_module(
        "r8_v15_r1_frozen_schema_runtime_invariant",
        ROOT/"governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
    )
    with tempfile.TemporaryDirectory(prefix="r8-runtime-parent-alias-") as td:
        root = Path(td)
        (root/"file").write_bytes(b"ok")
        try:
            runtime.read_confined_file(root, root/"nested"/".."/"file")
        except runtime.FrozenSchemaError as exc:
            assert exc.code == "ARTIFACT_PATH_INVALID"
        else:
            raise AssertionError("runtime lexical parent traversal alias was accepted")
    gate_text = (ROOT/".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml").read_text(encoding="utf-8")
    assert 'read_text(encoding="utf-8")' in gate_text
    assert "root_abs = root_dir.absolute()" in (ROOT/"governance-runtime/r8_v15_r1_frozen_schema_runtime.py").read_text(encoding="utf-8")

    print(json.dumps({
        "status":"R8_POST_SG1_SINGLE_CANDIDATE_INVARIANTS_PASS",
        "head":head,
        "tree":tree,
        "changed_paths":len(changed),
        "authority_effect":"NONE",
        "fallback_to_3":"ACTIVE",
        "six_slice_cadence_restored":False,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
