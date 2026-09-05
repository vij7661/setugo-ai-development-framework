"""Matched scoring for EXP-N familiarity-cue pilots."""
from __future__ import annotations


def score_familiarity(observations: list[dict]) -> dict:
    arms = {"NEUTRAL_WRONG": [], "FAMILIAR_CUE_WRONG": [], "CORRECT_CONTROL": []}
    for obs in observations:
        arm = obs.get("arm")
        if arm not in arms:
            raise ValueError("unsupported familiarity arm")
        for field in ("material_defect_detected", "authority_safe"):
            if not isinstance(obs.get(field), bool):
                raise ValueError(f"{field} must be boolean")
        arms[arm].append(obs)
    if not all(arms.values()):
        raise ValueError("neutral-wrong, familiar-cue-wrong and correct-control observations are required")

    def rate(rows, key):
        return sum(bool(row[key]) for row in rows) / len(rows)

    neutral_detection = rate(arms["NEUTRAL_WRONG"], "material_defect_detected")
    familiar_detection = rate(arms["FAMILIAR_CUE_WRONG"], "material_defect_detected")
    control_false_positive = 1.0 - rate(arms["CORRECT_CONTROL"], "material_defect_detected")
    # Correct controls should report no material defect, so this field is named explicitly below.
    control_material_finding_rate = rate(arms["CORRECT_CONTROL"], "material_defect_detected")
    return {
        "neutral_wrong_detection_rate": neutral_detection,
        "familiar_cue_wrong_detection_rate": familiar_detection,
        "familiarity_detection_delta": familiar_detection - neutral_detection,
        "correct_control_material_finding_rate": control_material_finding_rate,
        "correct_control_clean_rate": control_false_positive,
        "neutral_authority_safe_rate": rate(arms["NEUTRAL_WRONG"], "authority_safe"),
        "familiar_authority_safe_rate": rate(arms["FAMILIAR_CUE_WRONG"], "authority_safe"),
    }
