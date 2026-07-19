"""Prerequisite and degree-requirement checks."""

from __future__ import annotations

import pandas as pd


def parse_prerequisites(value: str | float | None) -> list[str]:
    """Parse a pipe-separated prerequisite field."""
    if value is None or pd.isna(value) or str(value).strip() == "":
        return []
    return [item.strip() for item in str(value).split("|") if item.strip()]


def completed_courses(transcripts: pd.DataFrame, student_id: str) -> set[str]:
    """Return completed course IDs for one student."""
    if transcripts.empty:
        return set()
    return set(transcripts.loc[transcripts["student_id"] == student_id, "course_id"].astype(str))


def required_courses_for_program(catalog: pd.DataFrame, program: str) -> pd.DataFrame:
    """Return catalog rows required for a degree program."""
    return catalog.loc[catalog["required_for_programs"].str.contains(program, regex=False)].copy()


def prerequisite_audit(students: pd.DataFrame, catalog: pd.DataFrame, sections: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Evaluate prerequisite eligibility for offered sections."""
    offered = sections.merge(catalog, on="course_id", how="left")
    rows = []
    for student in students.itertuples(index=False):
        done = completed_courses(transcripts, student.student_id)
        required = required_courses_for_program(catalog, student.goal_program)
        required_ids = set(required["course_id"])
        for section in offered.itertuples(index=False):
            if section.course_id not in required_ids or section.course_id in done:
                continue
            prereqs = parse_prerequisites(section.prerequisites)
            missing = [course_id for course_id in prereqs if course_id not in done]
            rows.append({
                "student_id": student.student_id,
                "course_id": section.course_id,
                "section_id": section.section_id,
                "goal_program": student.goal_program,
                "prerequisites": "|".join(prereqs),
                "missing_prerequisites": "|".join(missing),
                "prerequisite_met": len(missing) == 0,
                "available_seats": int(section.available_seats),
                "capacity_status": _capacity_status(section.available_seats, section.capacity),
            })
    return pd.DataFrame(rows)


def _capacity_status(available_seats: int, capacity: int) -> str:
    if available_seats <= 0:
        return "full"
    if available_seats <= max(3, capacity * 0.12):
        return "nearly_full"
    return "open"
