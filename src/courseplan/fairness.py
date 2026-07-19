"""Fairness and access audits for course-planning recommendations."""

from __future__ import annotations

import pandas as pd


def fairness_audit(students: pd.DataFrame, risk: pd.DataFrame, recommendations: pd.DataFrame) -> pd.DataFrame:
    """Audit access and risk differences across synthetic student groups."""
    if recommendations.empty:
        rec_summary = pd.DataFrame(columns=["student_id", "recommended_courses", "recommended_credits", "blocked_options"])
    else:
        rec = recommendations.assign(is_recommended=recommendations["recommendation_status"].eq("recommended"))
        rec_summary = rec.groupby("student_id").agg(
            recommended_courses=("is_recommended", "sum"),
            recommended_credits=("credits", lambda s: int(s[rec.loc[s.index, "is_recommended"]].sum())),
            blocked_options=("recommendation_status", lambda s: int((s == "blocked").sum())),
        ).reset_index()
    frame = students[["student_id", "goal_program", "student_group", "financial_aid_sensitive"]].merge(risk, on=["student_id", "goal_program", "student_group"], how="left").merge(rec_summary, on="student_id", how="left")
    for col in ["recommended_courses", "recommended_credits", "blocked_options"]:
        frame[col] = frame[col].fillna(0)
    rows = []
    for field in ["goal_program", "student_group", "financial_aid_sensitive"]:
        grouped = frame.groupby(field).agg(
            student_count=("student_id", "count"),
            mean_recommended_credits=("recommended_credits", "mean"),
            mean_blocked_options=("blocked_options", "mean"),
            mean_graduation_risk_score=("graduation_risk_score", "mean"),
            high_risk_rate=("graduation_risk_band", lambda s: float((s == "high").mean())),
        ).reset_index().rename(columns={field: "group_value"})
        grouped.insert(0, "audit_dimension", field)
        grouped["recommended_credit_gap"] = float(grouped["mean_recommended_credits"].max() - grouped["mean_recommended_credits"].min()) if len(grouped) else 0.0
        grouped["risk_gap"] = float(grouped["mean_graduation_risk_score"].max() - grouped["mean_graduation_risk_score"].min()) if len(grouped) else 0.0
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def fairness_summary(audit: pd.DataFrame) -> dict[str, float | int]:
    """Compact fairness summary for reports."""
    if audit.empty:
        return {"max_recommended_credit_gap": 0.0, "max_risk_gap": 0.0, "fairness_rows": 0}
    return {
        "max_recommended_credit_gap": float(audit["recommended_credit_gap"].max()),
        "max_risk_gap": float(audit["risk_gap"].max()),
        "fairness_rows": int(len(audit)),
    }
