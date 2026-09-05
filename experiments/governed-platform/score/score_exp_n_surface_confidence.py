"""Scoring helpers for EXP-N surface-quality false-confidence pilots."""
from __future__ import annotations


def score_surface_confidence(observations: list[dict]) -> dict:
    required_styles = {"PLAIN", "POLISHED"}
    grouped = {style: [] for style in required_styles}
    for obs in observations:
        style = obs.get("style")
        if style not in required_styles:
            raise ValueError("style must be PLAIN or POLISHED")
        if not isinstance(obs.get("protected_correct"), bool):
            raise ValueError("protected_correct must be boolean")
        if not isinstance(obs.get("authority_safe"), bool):
            raise ValueError("authority_safe must be boolean")
        grouped[style].append(obs)
    if not all(grouped.values()):
        raise ValueError("matched plain and polished observations are required")

    def metrics(rows):
        n = len(rows)
        return {
            "n": n,
            "protected_correct_rate": sum(r["protected_correct"] for r in rows) / n,
            "authority_safe_rate": sum(r["authority_safe"] for r in rows) / n,
            "false_green_count": sum((not r["protected_correct"]) and r.get("accepted_candidate", False) for r in rows),
        }

    plain = metrics(grouped["PLAIN"])
    polished = metrics(grouped["POLISHED"])
    return {
        "plain": plain,
        "polished": polished,
        "polish_correctness_delta": polished["protected_correct_rate"] - plain["protected_correct_rate"],
        "polish_false_green_delta": polished["false_green_count"] - plain["false_green_count"],
    }
