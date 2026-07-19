"""Graduation-risk and bottleneck analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from courseplan.prerequisites import completed_courses, parse_prerequisites, required_courses_for_program


def graduation_risk_table(students: pd.DataFrame, catalog: pd.DataFrame, sections: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Estimate graduation risk from remaining credits, GPA, bottlenecks, and next-term access."""
    offered_ids = set(sections["course_id"].astype(str))
    rows = []
    for student in students.itertuples(index=False):
        required = required_courses_for_program(catalog, student.goal_program)
        done = completed_courses(transcripts, student.student_id)
        remaining = required.loc[~required["course_id"].isin(done)].copy()
        earned = transcripts.loc[transcripts["student_id"] == student.student_id, "credits_earned"].sum() if not transcripts.empty else 0
        avg_grade = transcripts.loc[transcripts["student_id"] == student.student_id, "grade_points"].mean() if not transcripts.empty else np.nan
        remaining_credits = int(remaining["credits"].sum())
        not_offered_required = int((~remaining["course_id"].isin(offered_ids)).sum())
        prereq_locked = 0
        for course in remaining.itertuples(index=False):
            missing = [pr for pr in parse_prerequisites(course.prerequisites) if pr not in done]
            prereq_locked += int(len(missing) > 0)
        pace_pressure = min(1.0, remaining_credits / max(float(student.max_next_term_credits) * 4.0, 1.0))
        gpa_pressure = max(0.0, (2.7 - float(student.current_gpa)) / 1.4)
        bottleneck_pressure = min(1.0, (not_offered_required + prereq_locked) / max(len(remaining), 1))
        workload_pressure = 0.18 if int(student.max_next_term_credits) <= 12 else 0.05
        risk = float(np.clip(0.42 * pace_pressure + 0.24 * gpa_pressure + 0.24 * bottleneck_pressure + 0.10 * workload_pressure, 0, 1))
        rows.append({
            "student_id": student.student_id,
            "goal_program": student.goal_program,
            "student_group": student.student_group,
            "year_level": int(student.year_level),
            "current_gpa": float(student.current_gpa),
            "credits_completed": int(earned),
            "remaining_required_courses": int(len(remaining)),
            "remaining_required_credits": remaining_credits,
            "not_offered_required_courses": not_offered_required,
            "prerequisite_locked_courses": prereq_locked,
            "max_next_term_credits": int(student.max_next_term_credits),
            "target_graduation_term": student.target_graduation_term,
            "graduation_risk_score": round(risk, 4),
            "graduation_risk_band": _risk_band(risk),
            "risk_drivers": _risk_drivers(pace_pressure, gpa_pressure, bottleneck_pressure, workload_pressure),
        })
    return pd.DataFrame(rows).sort_values("graduation_risk_score", ascending=False).reset_index(drop=True)


def summarize_risk(risk: pd.DataFrame) -> dict[str, float | int | str]:
    """Return compact risk summary."""
    return {
        "student_count": int(len(risk)),
        "high_graduation_risk_count": int((risk["graduation_risk_band"] == "high").sum()) if len(risk) else 0,
        "mean_graduation_risk_score": float(risk["graduation_risk_score"].mean()) if len(risk) else 0.0,
        "mean_remaining_required_credits": float(risk["remaining_required_credits"].mean()) if len(risk) else 0.0,
        "data_origin": "synthetic fictional university advising records",
        "decision_boundary": "advisor decision support only; not automatic enrollment or degree certification",
    }


def _risk_band(score: float) -> str:
    if score >= 0.68:
        return "high"
    if score >= 0.42:
        return "medium"
    return "low"


def _risk_drivers(pace: float, gpa: float, bottleneck: float, workload: float) -> str:
    drivers = []
    if pace >= 0.55:
        drivers.append("remaining_credits")
    if gpa >= 0.25:
        drivers.append("gpa_pressure")
    if bottleneck >= 0.35:
        drivers.append("course_bottlenecks")
    if workload >= 0.15:
        drivers.append("limited_credit_load")
    return "|".join(drivers) if drivers else "on_track"
