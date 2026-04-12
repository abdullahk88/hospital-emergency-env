"""
graders.py
Deterministic scoring for all 3 tasks.
Only counts FIRST action per patient.
Scores are STRICTLY within (0, 1).
"""

from tasks import (
    EASY_CORRECT_ANSWERS,
    MEDIUM_CORRECT_ANSWERS,
    MEDIUM_RESOURCES,
    HARD_CORRECT_ANSWERS,
    HARD_RESOURCES,
    SEVERITY_WEIGHTS,
    HARD_INITIAL_PATIENTS,
    HARD_ARRIVING_PATIENTS,
)


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def _first_actions(episode_actions: list[dict]) -> dict:
    seen = {}
    for action in episode_actions:
        pid = action.get("patient_id")
        if pid and pid not in seen:
            seen[pid] = action
    return seen


def _is_one_level_off(chosen: str, correct: str) -> bool:
    hierarchy = ["assign_icu", "assign_ventilator", "assign_doctor", "defer", "discharge"]
    if chosen not in hierarchy or correct not in hierarchy:
        return False
    return abs(hierarchy.index(chosen) - hierarchy.index(correct)) == 1


def _finalize_score(total_score: float, max_score: float) -> float:
    if max_score <= 0:
        return 0.01

    # Clamp numerator FIRST to prevent invalid ratios
    total_score = max(0.0, min(max_score, total_score))

    score = total_score / max_score

    # Strict open interval (0,1)
    if score <= 0.0:
        score = 0.01
    elif score >= 1.0:
        score = 0.99

    return round(score, 4)


# ─────────────────────────────────────────
# EASY
# ─────────────────────────────────────────
def grade_easy(episode_actions: list[dict]) -> float:
    if not episode_actions:
        return 0.01

    first = _first_actions(episode_actions)
    total_score = 0.0
    max_score = float(len(EASY_CORRECT_ANSWERS))

    for pid, correct in EASY_CORRECT_ANSWERS.items():
        action = first.get(pid)

        if action is None:
            total_score -= 0.3
            continue

        chosen = action.get("action_type")

        if chosen == correct:
            total_score += 1.0
        elif _is_one_level_off(chosen, correct):
            total_score += 0.4
        elif correct in ("assign_icu", "assign_ventilator") and chosen == "defer":
            total_score -= 0.3

    return _finalize_score(total_score, max_score)


# ─────────────────────────────────────────
# MEDIUM
# ─────────────────────────────────────────
def grade_medium(episode_actions: list[dict]) -> float:
    if not episode_actions:
        return 0.01

    first = _first_actions(episode_actions)
    total_score = 0.0
    max_score = float(len(MEDIUM_CORRECT_ANSWERS))

    resource_usage = {"assign_icu": 0, "assign_doctor": 0, "assign_ventilator": 0}
    resource_limits = {
        "assign_icu": MEDIUM_RESOURCES["icu_beds"],
        "assign_doctor": MEDIUM_RESOURCES["doctors"],
        "assign_ventilator": MEDIUM_RESOURCES["ventilators"],
    }

    for pid, correct in MEDIUM_CORRECT_ANSWERS.items():
        action = first.get(pid)

        if action is None:
            if correct in ("assign_icu", "assign_ventilator"):
                total_score -= 0.4
            continue

        chosen = action.get("action_type")

        over_limit = False
        if chosen in resource_usage:
            resource_usage[chosen] += 1
            over_limit = resource_usage[chosen] > resource_limits.get(chosen, 999)

        if over_limit:
            continue
        elif chosen == correct:
            total_score += 1.0
        elif _is_one_level_off(chosen, correct):
            total_score += 0.4
        elif correct in ("assign_icu", "assign_ventilator") and chosen == "defer":
            total_score -= 0.4

    return _finalize_score(total_score, max_score)


# ─────────────────────────────────────────
# HARD
# ─────────────────────────────────────────
def grade_hard(episode_actions: list[dict]) -> float:
    if not episode_actions:
        return 0.01

    first = _first_actions(episode_actions)

    all_patients = HARD_INITIAL_PATIENTS + HARD_ARRIVING_PATIENTS
    severity_lookup = {p["patient_id"]: p["current_severity"] for p in all_patients}

    resource_usage = {"assign_icu": 0, "assign_doctor": 0, "assign_ventilator": 0}
    resource_limits = {
        "assign_icu": HARD_RESOURCES["icu_beds"],
        "assign_doctor": HARD_RESOURCES["doctors"],
        "assign_ventilator": HARD_RESOURCES["ventilators"],
    }

    total_score = 0.0
    max_score = 0.0

    for pid, correct in HARD_CORRECT_ANSWERS.items():
        severity = severity_lookup.get(pid, "minor")
        weight = SEVERITY_WEIGHTS.get(severity, 1.0)
        max_score += weight

        action = first.get(pid)

        if action is None:
            if severity == "critical":
                total_score -= 0.3 * weight
            continue

        chosen = action.get("action_type")

        over_limit = False
        if chosen in resource_usage:
            resource_usage[chosen] += 1
            over_limit = resource_usage[chosen] > resource_limits.get(chosen, 999)

        if over_limit:
            continue
        elif chosen == correct:
            total_score += 1.0 * weight
        elif _is_one_level_off(chosen, correct):
            total_score += 0.4 * weight
        elif severity == "critical" and chosen == "defer":
            total_score -= 0.5 * weight

    return _finalize_score(total_score, max_score)