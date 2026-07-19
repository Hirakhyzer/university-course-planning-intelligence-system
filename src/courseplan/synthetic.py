"""Deterministic synthetic university course planning data.

All students, courses, professors, schedules, and advising outcomes are fictional.
The data exists to test academic planning logic without exposing real student
records or institutional scheduling information.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

PROGRAMS = ["Computer Science", "Data Science", "Cybersecurity", "Information Systems"]
TERMS = ["Fall 2026", "Spring 2027", "Fall 2027", "Spring 2028"]
GROUPS = ["standard", "first_generation", "transfer", "working_student"]


@dataclass(frozen=True)
class SyntheticCourseConfig:
    students: int = 80
    seed: int = 42

    def __post_init__(self) -> None:
        if self.students < 12:
            raise ValueError("Use at least 12 students for subgroup and program-level audits.")


def generate_synthetic_university_data(config: SyntheticCourseConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate a complete synthetic advising dataset."""
    cfg = config or SyntheticCourseConfig()
    rng = np.random.default_rng(cfg.seed)
    catalog = _course_catalog()
    professors = _professors(rng)
    sections = _sections(catalog, professors, rng)
    students = _students(cfg, rng)
    transcripts = _transcripts(students, catalog, rng)
    return {
        "catalog": catalog,
        "professors": professors,
        "sections": sections,
        "students": students,
        "transcripts": transcripts,
    }


def _course_catalog() -> pd.DataFrame:
    rows = [
        ("UNI101", "Academic Success Seminar", "Core", 1, 100, "Both", "", "Computer Science|Data Science|Cybersecurity|Information Systems"),
        ("MATH110", "College Algebra", "Core", 3, 100, "Both", "", "Computer Science|Data Science|Cybersecurity|Information Systems"),
        ("MATH210", "Discrete Mathematics", "Core", 3, 200, "Both", "MATH110", "Computer Science|Data Science|Cybersecurity"),
        ("STAT220", "Applied Statistics", "Core", 3, 200, "Both", "MATH110", "Data Science|Information Systems"),
        ("CS101", "Programming Fundamentals", "Computer Science", 3, 100, "Both", "", "Computer Science|Data Science|Cybersecurity|Information Systems"),
        ("CS201", "Data Structures", "Computer Science", 3, 200, "Both", "CS101", "Computer Science|Data Science|Cybersecurity"),
        ("CS220", "Software Engineering", "Computer Science", 3, 200, "Spring", "CS201", "Computer Science|Information Systems"),
        ("CS310", "Algorithms", "Computer Science", 3, 300, "Fall", "CS201|MATH210", "Computer Science|Data Science"),
        ("CS330", "Databases", "Computer Science", 3, 300, "Both", "CS201", "Computer Science|Data Science|Information Systems"),
        ("CS410", "Distributed Systems", "Computer Science", 3, 400, "Spring", "CS310|CS330", "Computer Science"),
        ("DS101", "Data Literacy", "Data Science", 3, 100, "Both", "", "Data Science|Information Systems"),
        ("DS210", "Data Wrangling", "Data Science", 3, 200, "Fall", "CS101|STAT220", "Data Science"),
        ("DS320", "Machine Learning", "Data Science", 3, 300, "Spring", "DS210|MATH210", "Data Science|Computer Science"),
        ("DS430", "Responsible AI Analytics", "Data Science", 3, 400, "Fall", "DS320", "Data Science"),
        ("CY101", "Cybersecurity Foundations", "Cybersecurity", 3, 100, "Both", "", "Cybersecurity|Computer Science"),
        ("CY220", "Network Security", "Cybersecurity", 3, 200, "Fall", "CY101|CS101", "Cybersecurity"),
        ("CY330", "Secure Systems", "Cybersecurity", 3, 300, "Spring", "CY220|CS201", "Cybersecurity"),
        ("CY440", "Security Governance", "Cybersecurity", 3, 400, "Fall", "CY330", "Cybersecurity|Information Systems"),
        ("IS101", "Information Systems Foundations", "Information Systems", 3, 100, "Both", "", "Information Systems"),
        ("IS220", "Business Process Analysis", "Information Systems", 3, 200, "Spring", "IS101", "Information Systems"),
        ("IS310", "Enterprise Systems", "Information Systems", 3, 300, "Fall", "IS220|CS330", "Information Systems"),
        ("IS420", "IT Strategy and Governance", "Information Systems", 3, 400, "Spring", "IS310", "Information Systems"),
        ("ETH300", "Technology Ethics", "Core", 3, 300, "Both", "UNI101", "Computer Science|Data Science|Cybersecurity|Information Systems"),
        ("CAP499", "Senior Capstone", "Core", 3, 400, "Both", "CS220|ETH300", "Computer Science|Data Science|Cybersecurity|Information Systems"),
    ]
    return pd.DataFrame(rows, columns=["course_id", "course_title", "department", "credits", "level", "term_offered", "prerequisites", "required_for_programs"])


def _professors(rng: np.random.Generator) -> pd.DataFrame:
    names = ["Ada Rahman", "Nadia Brooks", "Omar Chen", "Lina Patel", "Jonas Reed", "Fatima Noor", "Mateo Silva", "Sara Kim", "Amina Lewis", "Theo Wright"]
    specialties = ["Computer Science", "Data Science", "Cybersecurity", "Information Systems", "Core"]
    rows = []
    for idx, name in enumerate(names):
        rows.append({
            "professor_id": f"P-{idx+1:02d}",
            "professor_name": name,
            "specialty": specialties[idx % len(specialties)],
            "max_sections": int(rng.integers(2, 5)),
            "availability_pattern": str(rng.choice(["MW", "TR", "MWF", "evening"])),
            "advising_load": int(rng.integers(8, 28)),
        })
    return pd.DataFrame(rows)


def _sections(catalog: pd.DataFrame, professors: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    days_options = ["MW", "TR", "MWF", "TR", "MW"]
    starts = ["09:00", "10:30", "12:00", "14:00", "16:00", "18:00"]
    fall_courses = catalog.loc[catalog["term_offered"].isin(["Both", "Fall"])].reset_index(drop=True)
    for idx, course in fall_courses.iterrows():
        section_count = 2 if course.level <= 200 and rng.random() < 0.65 else 1
        for sec in range(section_count):
            professor_pool = professors.loc[(professors["specialty"].isin([course.department, "Core"])) | (course.department == "Core")]
            professor = professor_pool.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
            capacity = int(rng.integers(18, 45))
            enrolled = int(np.clip(rng.normal(capacity * 0.78, 8), 5, capacity + 8))
            days = str(rng.choice(days_options))
            start = str(rng.choice(starts))
            rows.append({
                "section_id": f"{course.course_id}-{sec+1}",
                "course_id": course.course_id,
                "term": "Fall 2026",
                "professor_id": professor.professor_id,
                "days": days,
                "start_time": start,
                "end_time": _end_time(start),
                "capacity": capacity,
                "enrolled": enrolled,
                "available_seats": max(0, capacity - enrolled),
                "professor_availability_match": int(days == professor.availability_pattern or professor.availability_pattern == "evening" and start >= "16:00"),
            })
    return pd.DataFrame(rows)


def _students(cfg: SyntheticCourseConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(cfg.students):
        program = PROGRAMS[idx % len(PROGRAMS)]
        year = int(rng.choice([1, 2, 3, 4], p=[0.22, 0.30, 0.30, 0.18]))
        target_index = int(np.clip(5 - year + rng.integers(0, 2), 1, len(TERMS) - 1))
        group = str(rng.choice(GROUPS, p=[0.46, 0.18, 0.18, 0.18]))
        rows.append({
            "student_id": f"S-{idx+1:04d}",
            "goal_program": program,
            "student_group": group,
            "year_level": year,
            "current_gpa": round(float(np.clip(rng.normal(3.05 - 0.08 * (group == "working_student"), 0.42), 1.7, 4.0)), 2),
            "max_next_term_credits": int(rng.choice([9, 12, 15, 18], p=[0.14, 0.28, 0.42, 0.16])),
            "target_graduation_term": TERMS[target_index],
            "advisor_id": f"ADV-{idx % 6 + 1:02d}",
            "financial_aid_sensitive": int(rng.random() < 0.34),
        })
    return pd.DataFrame(rows)


def _transcripts(students: pd.DataFrame, catalog: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    term_history = ["Fall 2024", "Spring 2025", "Fall 2025", "Spring 2026"]
    for student in students.itertuples(index=False):
        program_courses = catalog.loc[catalog["required_for_programs"].str.contains(student.goal_program, regex=False)].copy()
        completion_prob = {1: 0.18, 2: 0.38, 3: 0.58, 4: 0.76}[student.year_level]
        for course in program_courses.itertuples(index=False):
            level_factor = max(0.15, 1.15 - course.level / 420)
            if rng.random() < completion_prob * level_factor:
                rows.append({
                    "student_id": student.student_id,
                    "course_id": course.course_id,
                    "completed_term": str(rng.choice(term_history)),
                    "grade_points": round(float(np.clip(rng.normal(student.current_gpa, 0.35), 1.0, 4.0)), 2),
                    "credits_earned": int(course.credits),
                })
    return pd.DataFrame(rows)


def _end_time(start: str) -> str:
    hour, minute = [int(part) for part in start.split(":")]
    total = hour * 60 + minute + 75
    return f"{total // 60:02d}:{total % 60:02d}"
