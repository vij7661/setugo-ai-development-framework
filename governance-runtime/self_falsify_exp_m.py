"""Self-falsification gate for deterministic EXP-M implementation."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceDeliveryManifest, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, ProviderCapabilityProfile, EvidenceChunk,
    admissibility_registry, complete_delivery, digest, evaluate_admissibility,
    preflight_delivery, validate_attempt_ledger, validate_chunks,
    validate_retry_transparency, validate_witness,
)
from run_exp_m_mutations import run as run_mutations

ROOT = Path(__file__).resolve().parents[1]


def run():
    snap = GovernanceAuthoritySnapshot("s", "1", "h", True)
    contract = RequiredEvidenceContract("c", "s", ("a",))
    interactions = RequiredInteractionContract("i", "s", (("a",),))
    items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze("r", "commit", items)
    provider = ProviderCapabilityProfile("fake", "m", "v", "p", True)
    cases = []
    def case(name, rejected): cases.append({"id": name, "rejected": bool(rejected)})
    case("manifest_byte_mutation", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, {"a": b"x"}).allowed)
    case("candidate_writable_snapshot", not preflight_delivery(GovernanceAuthoritySnapshot("s", "1", "h", False), contract, interactions, manifest, "r", provider, items).allowed)
    state = {p: True for p in admissibility_registry().predicate_ids}; state["delivery_complete"] = False
    case("admissibility_predicate_removed", not evaluate_admissibility(state).admissible)
    case("missing_chunk", not validate_chunks([EvidenceChunk.create("r", digest(b"ab"), 0, 2, b"a")], request_id="r", corpus_hash=digest(b"ab"))[0])
    case("retry_hidden", not validate_retry_transparency(({"attempt_id":"a", "wire_hash":"w"},), automatic_retry_hidden=True)[0])
    case("attempt_set_open", not validate_attempt_ledger(("a", "b"), ("a",), ())[0])
    case("witness_over_budget", not validate_witness("c", "0123456789", max_response_bytes=2)[0])
    case("empty_witness", not validate_witness("", "", max_response_bytes=2)[0])
    mutation_result = run_mutations()
    for mutation in mutation_result["mutations"]:
        case(f"mutation:{mutation['id']}", mutation["killed"])
    survivors = [c for c in cases if not c["rejected"]]
    return {"cases": cases, "total": len(cases), "surviving_critical": len(survivors), "surviving_high": len(survivors), "all_rejected": not survivors}


if __name__ == "__main__":
    result = run()
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
