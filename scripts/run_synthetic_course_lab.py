"""Run the complete synthetic university course-planning intelligence lab.

The command uses only fictional student, course, professor, capacity, and schedule
records. It demonstrates prerequisite checking, section-capacity analysis,
professor availability, personalized semester planning, graduation-risk scoring,
fairness auditing, reporting, figures, and a hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from courseplan.audit import append_record, verify_log
from courseplan.config import ensure_output_dirs, set_seed
from courseplan.fairness import fairness_audit, fairness_summary
from courseplan.planner import build_course_recommendations, student_plan_summary
from courseplan.prerequisites import prerequisite_audit
from courseplan.reporting import write_report
from courseplan.risk import graduation_risk_table, summarize_risk
from courseplan.synthetic import SyntheticCourseConfig, generate_synthetic_university_data
from courseplan.visualization import plot_bottleneck_courses, plot_capacity_pressure, plot_fairness_gaps, plot_graduation_risk, plot_recommended_credits


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic university course-planning intelligence lab.")
    parser.add_argument("--students", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_university_data(SyntheticCourseConfig(students=args.students, seed=args.seed))
    catalog = data["catalog"]
    professors = data["professors"]
    sections = data["sections"]
    students = data["students"]
    transcripts = data["transcripts"]

    prereqs = prerequisite_audit(students, catalog, sections, transcripts)
    recommendations = build_course_recommendations(students, catalog, professors, sections, transcripts)
    plan_summary = student_plan_summary(recommendations)
    risk = graduation_risk_table(students, catalog, sections, transcripts)
    fairness = fairness_audit(students, risk, recommendations)

    summary = summarize_risk(risk)
    summary.update(fairness_summary(fairness))
    summary.update({
        "seed": args.seed,
        "course_count": int(len(catalog)),
        "section_count": int(len(sections)),
        "professor_count": int(len(professors)),
        "recommendation_count": int((recommendations["recommendation_status"] == "recommended").sum()) if not recommendations.empty else 0,
        "blocked_option_count": int((recommendations["recommendation_status"] == "blocked").sum()) if not recommendations.empty else 0,
    })

    catalog.to_csv(outputs["results"] / "synthetic_course_catalog.csv", index=False)
    professors.to_csv(outputs["results"] / "synthetic_professors.csv", index=False)
    sections.to_csv(outputs["results"] / "synthetic_sections.csv", index=False)
    students.to_csv(outputs["results"] / "synthetic_students.csv", index=False)
    transcripts.to_csv(outputs["results"] / "synthetic_transcripts.csv", index=False)
    prereqs.to_csv(outputs["results"] / "synthetic_prerequisite_audit.csv", index=False)
    recommendations.to_csv(outputs["results"] / "synthetic_course_recommendations.csv", index=False)
    plan_summary.to_csv(outputs["results"] / "synthetic_student_plan_summary.csv", index=False)
    risk.to_csv(outputs["results"] / "synthetic_graduation_risk.csv", index=False)
    fairness.to_csv(outputs["results"] / "synthetic_fairness_audit.csv", index=False)

    audit_path = outputs["audit"] / "course_planning_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "synthetic advisor decision support only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_course_planning_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_course_planning_report.md", summary, risk, recommendations, plan_summary, fairness)
    plot_graduation_risk(risk, outputs["figures"] / "synthetic_graduation_risk.png")
    plot_recommended_credits(plan_summary, outputs["figures"] / "synthetic_recommended_credits.png")
    plot_capacity_pressure(sections, outputs["figures"] / "synthetic_capacity_pressure.png")
    plot_fairness_gaps(fairness, outputs["figures"] / "synthetic_fairness_gaps.png")
    plot_bottleneck_courses(recommendations, outputs["figures"] / "synthetic_bottleneck_courses.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
