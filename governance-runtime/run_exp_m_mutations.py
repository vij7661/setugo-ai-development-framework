"""Unified deterministic EXP-M data/state and validator-logic mutations."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, admissibility_registry,
    complete_delivery, evaluate_admissibility, digest, validate_chunks,
)

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict:
    reg = admissibility_registry()
    mutations = []
    base = {p: True for p in reg.predicate_ids}
    for predicate in reg.logic_mutation_ids:
        mutated = dict(base); mutated[predicate] = False
        result = evaluate_admissibility(mutated, reg)
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "expected": "REJECT", "actual": "REJECT" if not result.admissible else "PASS", "killed": not result.admissible})
    corpus = b"abcdefghij"; corpus_hash = digest(corpus)
    chunks = [EvidenceChunk.create("request", corpus_hash, 0, 2, corpus[:5]), EvidenceChunk.create("request", corpus_hash, 1, 2, corpus[5:])]
    data_mutations = [
        ("missing_chunk", chunks[:1]),
        ("wrong_request", [EvidenceChunk.create("other", corpus_hash, 0, 2, corpus[:5]), chunks[1]]),
        ("wrong_corpus", [EvidenceChunk.create("request", "wrong", 0, 2, corpus[:5]), chunks[1]]),
        ("duplicate_index", [chunks[0], chunks[0]]),
        ("corrupt_chunk", [EvidenceChunk("request", corpus_hash, 0, 2, b"xxxxx", chunks[0].chunk_hash), chunks[1]]),
        ("empty_chunk", [EvidenceChunk.create("request", corpus_hash, 0, 2, b""), chunks[1]]),
    ]
    for name, candidate in data_mutations:
        ok = validate_chunks(candidate, request_id="request", corpus_hash=corpus_hash)[0]
        mutations.append({"id": f"TM-G-{name}", "family": "data_state", "target": name, "expected": "REJECT", "actual": "PASS" if ok else "REJECT", "killed": not ok})
    rejected = sum(1 for m in mutations if m["killed"])
    return {"experiment": "EXP-M", "total_mutations": len(mutations), "rejected_mutations": rejected, "surviving_mutations": len(mutations) - rejected, "all_rejected": rejected == len(mutations), "mutations": mutations}


if __name__ == "__main__":
    result = run()
    path = ROOT / "experiments" / "governed-platform" / "EXP-M-MUTATION-RESULTS.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
