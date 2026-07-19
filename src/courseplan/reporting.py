"""Markdown report generation for advisor-facing course planning outputs."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def write_report(
    path: str | Path,
    summary: dict,
    risk: pd.DataFrame,
    recommendations: pd.DataFrame,
    plan_summary: pd.DataFrame,
    fairness: pd.DataFrame,
) -> None:
    """Write a compact synthetic advising report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    high_risk = risk.head(12)
    recommended = recommendations.loc[recommendations["recommendation_status"] == "recommended"].head(15)
    lines = [
        "# Synthetic University Course Planning Report",
        "",
        "> Research decision-support output using fictional data only. Human advisor review is required before any real registration or degree-planning action.",
        "",
        "## Summary",
        "",
        pd.DataFrame([summary]).to_markdown(index=False),
        "",
        "## Highest graduation-risk students",
        "",
        high_risk[["student_id", "goal_program", "student_group", "remaining_required_credits", "graduation_risk_score", "graduation_risk_band", "risk_drivers"]].to_markdown(index=False),
        "",
        "## Sample recommended courses",
        "",
        recommended[["student_id", "course_id", "course_title", "credits", "days", "start_time", "available_seats", "planning_score", "advisor_note"]].to_markdown(index=False) if not recommended.empty else "No recommendations generated.",
        "",
        "## Plan summary sample",
        "",
        plan_summary.head(12).to_markdown(index=False) if not plan_summary.empty else "No plan summaries generated.",
        "",
        "## Fairness audit sample",
        "",
        fairness.head(12).to_markdown(index=False) if not fairness.empty else "No fairness audit generated.",
        "",
        "## Governance notes",
        "",
        "- Recommendations are not automatic enrollment decisions.",
        "- Advisors should review goals, student workload, financial-aid constraints, accessibility needs, and course substitutions.",
        "- Real deployment requires FERPA/privacy review, institutional policy review, and human appeal mechanisms.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
