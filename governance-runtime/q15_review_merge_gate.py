"""Q15 review/merge evidence gate. This module grants no merge authority."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from freeze_attestation import load_and_verify  # noqa: E402
from r8_v15_r1_independent_review_parser import (  # noqa: E402
    eligible_for_bounded_merge,
    parse_independent_review_file,
)


def review_merge_evidence_eligible(*, review_path: Path, freeze_attestation_path: Path, root: Path = ROOT) -> bool:
    parsed = parse_independent_review_file(review_path)
    load_and_verify(freeze_attestation_path, root=root)
    return eligible_for_bounded_merge(parsed, freeze_verified=True)
