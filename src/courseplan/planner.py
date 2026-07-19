"""Transparent semester planning and schedule-conflict detection."""

from __future__ import annotations

import pandas as pd

from courseplan.prerequisites import completed_courses, parse_prerequisites, required_courses_for_program


def build_course_recommendations(
    students: pd.DataFrame,
    catalog: pd.DataFrame,
    professors: pd.DataFrame,
    sections: pd.DataFrame,
    transcripts: pd.DataFrame,
) -> pd.DataFrame:
    """Build advisor-reviewable next-term course recommendations.

    The planner is rule-based and transparent. It does not register students; it
    creates recommendations for human advisors to inspect.
    """
    section_catalog = sections.merge(catalog, on="course_id", how="left").merge(professors, on="professor_id", how="left")
    rows = []
    for student in students.itertuples(index=False):
        done = completed_courses(transcripts, student.student_id)
        required = required_courses_for_program(catalog, student.goal_program)
        remaining_ids = [cid for cid in required["course_id"].tolist() if cid not in done]
        candidates = section_catalog.loc[section_catalog["course_id"].isin(remaining_ids)].copy()
        if candidates.empty:
            continue
        candidates["missing_prerequisites"] = candidates["prerequisites"].apply(lambda p: "|".join([c for c in parse_prerequisites(p) if c not in done]))
        candidates["prerequisite_met"] = candidates["missing_prerequisites"].eq("")
        candidates["capacity_status"] = candidates.apply(lambda r: _capacity_status(int(r.available_seats), int(r.capacity)), axis=1)
        candidates["bottleneck_score"] = candidates.apply(_bottleneck_score, axis=1)
        candidates["planning_score"] = candidates.apply(lambda r: _planning_score(r, student.year_level), axis=1)
        selected: list[dict] = []
        used_credits = 0
        for row in candidates.sort_values("planning_score", ascending=False).itertuples(index=False):
            blocking = []
            if not bool(row.prerequisite_met):
                blocking.append("missing_prerequisite")
            if int(row.available_seats) <= 0:
                blocking.append("course_full")
            if any(_clashes(row, chosen) for chosen in selected):
                blocking.append("schedule_clash")
            if used_credits + int(row.credits) > int(student.max_next_term_credits):
                blocking.append("credit_overload")
            status = "recommended" if not blocking and len(selected) < 5 else "blocked"
            if status == "recommended":
                selected.append(row._asdict())
                used_credits += int(row.credits)
            rows.append({
                "student_id": student.student_id,
                "goal_program": student.goal_program,
                "student_group": student.student_group,
                "section_id": row.section_id,
                "course_id": row.course_id,
                "course_title": row.course_title,
                "credits": int(row.credits),
                "professor_id": row.professor_id,
                "professor_name": row.professor_name,
                "days": row.days,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "available_seats": int(row.available_seats),
                "capacity_status": row.capacity_status,
                "professor_availability_match": int(row.professor_availability_match),
                "prerequisite_met": bool(row.prerequisite_met),
                "missing_prerequisites": row.missing_prerequisites,
                "planning_score": round(float(row.planning_score), 4),
                "bottleneck_score": round(float(row.bottleneck_score), 4),
                "recommendation_status": status,
                "blocking_reasons": "|".join(blocking),
                "advisor_note": _advisor_note(status, blocking),
            })
    return pd.DataFrame(rows).sort_values(["student_id", "recommendation_status", "planning_score"], ascending=[True, False, False]).reset_index(drop=True)


def student_plan_summary(recommendations: pd.DataFrame) -> pd.DataFrame:
    """Summarize recommended credits and blockers by student."""
    if recommendations.empty:
        return pd.DataFrame(columns=["student_id", "recommended_courses", "recommended_credits", "blocked_options", "prerequisite_blockers", "capacity_blockers", "schedule_blockers"])
    rec = recommendations.assign(is_recommended=recommendations["recommendation_status"].eq("recommended"))
    return rec.groupby("student_id").agg(
        recommended_courses=("is_recommended", "sum"),
        recommended_credits=("credits", lambda s: int(s[rec.loc[s.index, "is_recommended"]].sum())),
        blocked_options=("recommendation_status", lambda s: int((s == "blocked").sum())),
        prerequisite_blockers=("blocking_reasons", lambda s: int(s.str.contains("missing_prerequisite", regex=False).sum())),
        capacity_blockers=("blocking_reasons", lambda s: int(s.str.contains("course_full", regex=False).sum())),
        schedule_blockers=("blocking_reasons", lambda s: int(s.str.contains("schedule_clash", regex=False).sum())),
    ).reset_index()


def _planning_score(row, year_level: int) -> float:
    score = 0.32
    score += 0.18 if bool(row.prerequisite_met) else -0.35
    score += 0.18 if int(row.available_seats) > 0 else -0.30
    score += 0.12 if int(row.professor_availability_match) else -0.05
    score += min(0.20, float(row.level) / 2000.0 + 0.04 * year_level)
    score += float(row.bottleneck_score)
    return max(0.0, min(1.0, score))


def _bottleneck_score(row) -> float:
    term_boost = 0.10 if row.term_offered in {"Fall", "Spring"} else 0.04
    seat_pressure = 0.12 if int(row.available_seats) <= max(3, int(row.capacity) * 0.12) else 0.02
    level_pressure = 0.08 if int(row.level) >= 300 else 0.03
    return min(0.30, term_boost + seat_pressure + level_pressure)


def _capacity_status(available_seats: int, capacity: int) -> str:
    if available_seats <= 0:
        return "full"
    if available_seats <= max(3, int(capacity * 0.12)):
        return "nearly_full"
    return "open"


def _clashes(row, chosen: dict) -> bool:
    if set(str(row.days)) .isdisjoint(set(str(chosen["days"]))):
        return False
    return _minutes(row.start_time) < _minutes(chosen["end_time"]) and _minutes(chosen["start_time"]) < _minutes(row.end_time)


def _minutes(value: str) -> int:
    hour, minute = [int(part) for part in str(value).split(":")]
    return hour * 60 + minute


def _advisor_note(status: str, blocking: list[str]) -> str:
    if status == "recommended":
        return "Eligible option for advisor review; verify student goals and workload before registration."
    if not blocking:
        return "Lower-priority option; not selected because recommended set is already full."
    return "Blocked for advisor review: " + ", ".join(blocking)
