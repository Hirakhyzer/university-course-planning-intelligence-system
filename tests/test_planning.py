from courseplan.planner import build_course_recommendations, student_plan_summary
from courseplan.prerequisites import prerequisite_audit
from courseplan.risk import graduation_risk_table
from courseplan.synthetic import SyntheticCourseConfig, generate_synthetic_university_data


def _sample():
    data = generate_synthetic_university_data(SyntheticCourseConfig(students=20, seed=5))
    return data["students"], data["catalog"], data["professors"], data["sections"], data["transcripts"]


def test_recommendations_respect_capacity_and_credit_limit():
    students, catalog, professors, sections, transcripts = _sample()
    recs = build_course_recommendations(students, catalog, professors, sections, transcripts)
    assert not recs.empty
    chosen = recs.loc[recs["recommendation_status"] == "recommended"]
    assert (chosen["available_seats"] > 0).all()
    summary = student_plan_summary(recs)
    merged = summary.merge(students[["student_id", "max_next_term_credits"]], on="student_id")
    assert (merged["recommended_credits"] <= merged["max_next_term_credits"]).all()


def test_prerequisite_and_risk_tables_have_expected_columns():
    students, catalog, professors, sections, transcripts = _sample()
    prereqs = prerequisite_audit(students, catalog, sections, transcripts)
    risk = graduation_risk_table(students, catalog, sections, transcripts)
    assert {"student_id", "course_id", "prerequisite_met", "capacity_status"}.issubset(prereqs.columns)
    assert {"student_id", "graduation_risk_score", "graduation_risk_band", "risk_drivers"}.issubset(risk.columns)
    assert risk["graduation_risk_score"].between(0, 1).all()
