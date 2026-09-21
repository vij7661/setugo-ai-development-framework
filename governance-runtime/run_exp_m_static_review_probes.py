"""Deterministic clarification probes for R2E static-review findings SR-1/SR-2.

These probes do not grant authority and are not a substitute for the
preregistered reviewer suites. They expose the exact production semantics that
were ambiguous in the prior handoff.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-R2E-CLARIFICATION-PROBES.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp_m_deterministic import EvidenceBundle, evaluate_admissibility  # noqa: E402
from exp_m_expectation_authority import load_default_authority, load_predicate_context  # noqa: E402


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def run() -> dict:
    authority = load_default_authority()
    context = load_predicate_context(authority)

    verdict = evaluate_admissibility(
        EvidenceBundle({"disposition": "PASS"}),
        context,
        authority=authority,
    )
    underlying = {
        key: bool(value)
        for key, value in verdict.predicate_results.items()
        if key != "disposition_promotable"
    }
    derived_disposition = "PASS" if underlying and all(underlying.values()) else "CHANGES_REQUIRED"
    ca9 = {
        "caller_disposition": "PASS",
        "derived_disposition": derived_disposition,
        "admissible": verdict.admissible,
        "verdict_reasons": list(verdict.reasons),
        "failed_predicates": [key for key, value in verdict.predicate_results.items() if not value],
        "disposition_promotable_value": verdict.predicate_results.get("disposition_promotable"),
        "interpretation": "disposition_promotable is a predicate name. False means the derived disposition is not promotable or conflicts with the caller-supplied disposition; it is not a positive rejection status.",
    }
    if ca9["admissible"] or ca9["disposition_promotable_value"] is not False or derived_disposition != "CHANGES_REQUIRED":
        raise SystemExit("ca9_clarification_probe_failed")

    real_protocol = authority.load_r5_protocol()
    injected = authority.with_missing_r5_protocol_for_test()
    injected_error = None
    try:
        injected.load_r5_protocol()
    except ValueError as exc:
        injected_error = str(exc)
    ca10 = {
        "real_protocol_available": True,
        "real_protocol_id": real_protocol.get("protocol_id"),
        "real_protocol_version": real_protocol.get("protocol_version"),
        "real_protocol_live_provider_execution_authorized": real_protocol.get("live_provider_execution_authorized"),
        "fault_injection_method": "AuthorityHandle.with_missing_r5_protocol_for_test()",
        "fault_injected_protocol_available": injected.protocol_available,
        "fault_injected_error": injected_error,
        "interpretation": "CA-10 deliberately removes protocol availability only from the test AuthorityHandle; it does not assert that the real authority root lacks the frozen R5 protocol.",
    }
    if not ca10["real_protocol_available"] or ca10["fault_injected_protocol_available"] is not False or injected_error != "r5_protocol_unavailable":
        raise SystemExit("ca10_clarification_probe_failed")

    return {
        "schema": "EXP-M-R2E-STATIC-REVIEW-PROBES/v1",
        "execution": {
            "source_commit": _git("rev-parse", "HEAD"),
            "source_tree": _git("rev-parse", "HEAD^{tree}"),
            "utc": datetime.now(timezone.utc).isoformat(),
            "command": "python governance-runtime/run_exp_m_static_review_probes.py",
            "interpreter": sys.executable,
        },
        "sr_1_ca9": ca9,
        "sr_2_ca10": ca10,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }


def main() -> int:
    payload = run()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
