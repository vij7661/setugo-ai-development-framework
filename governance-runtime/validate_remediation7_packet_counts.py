#!/usr/bin/env python3
"""Fail-closed consistency check for the current F-02 review packet."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: validate_remediation7_packet_counts.py PACKET TEST_OUTPUT MUTATION_JSON")
    packet = Path(sys.argv[1]).read_text(encoding="utf-8")
    test_output = Path(sys.argv[2]).read_text(encoding="utf-8")
    mutation = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    match = re.search(r"Ran (\d+) tests? in ", test_output)
    if not match or not test_output.rstrip().endswith("OK"):
        raise SystemExit("behavioral output is not successful")
    tests = int(match.group(1))
    total, rejected, surviving = (mutation["total_mutations"], mutation["rejected_mutations"], mutation["surviving_mutations"])
    checks = mutation.get("checks", [])
    if total != len(checks) or rejected != sum(1 for c in checks if not c.get("pass")) or surviving != total - rejected or mutation["all_rejected"] != (surviving == 0):
        raise SystemExit("mutation arithmetic mismatch")
    current = packet.split("## Historical superseded review material (non-authoritative)", 1)[0]
    required = [f"behavioral_tests_total={tests}", f"behavioral_tests_passed={tests}", f"mutation_total={total}", f"mutation_rejected={rejected}", f"mutation_surviving={surviving}", f"all_rejected={'true' if surviving == 0 else 'false'}"]
    for item in required:
        if item not in current:
            raise SystemExit(f"missing current count: {item}")
    for stale in ("8/8", "46/46", "46 checks", "46 mutations"):
        if stale in current:
            raise SystemExit(f"unlabeled stale count in current packet: {stale}")
    historical = packet.split("## Historical superseded review material (non-authoritative)", 1)
    nonhistorical = historical[0]
    if len(historical) == 2:
        tail = historical[1].split("\n## Included source SHA-256\n", 1)
        nonhistorical += tail[-1]
    for forbidden in ("scientific_rerun=true", "RQ16_started=true"):
        if forbidden in nonhistorical:
            raise SystemExit(forbidden)
    print(json.dumps({"status":"PASS","behavioral_tests":tests,"mutation_total":total,"mutation_rejected":rejected,"mutation_surviving":surviving,"historical_section_labeled":True}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
