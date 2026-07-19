"""Visualization helpers for synthetic course-planning outputs."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def _save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_graduation_risk(risk: pd.DataFrame, path: Path) -> None:
    counts = risk["graduation_risk_band"].value_counts().reindex(["low", "medium", "high"]).fillna(0)
    plt.figure(figsize=(7, 4))
    counts.plot(kind="bar")
    plt.title("Synthetic graduation risk bands")
    plt.xlabel("Risk band")
    plt.ylabel("Students")
    _save(path)


def plot_recommended_credits(plan_summary: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(7, 4))
    plan_summary["recommended_credits"].plot(kind="hist", bins=8)
    plt.title("Recommended next-term credits")
    plt.xlabel("Credits")
    plt.ylabel("Students")
    _save(path)


def plot_capacity_pressure(sections: pd.DataFrame, path: Path) -> None:
    frame = sections.copy()
    frame["fill_rate"] = frame["enrolled"] / frame["capacity"]
    top = frame.sort_values("fill_rate", ascending=False).head(12)
    plt.figure(figsize=(9, 4))
    plt.bar(top["section_id"], top["fill_rate"])
    plt.title("Highest section capacity pressure")
    plt.xlabel("Section")
    plt.ylabel("Fill rate")
    plt.xticks(rotation=45, ha="right")
    _save(path)


def plot_fairness_gaps(audit: pd.DataFrame, path: Path) -> None:
    grouped = audit.groupby("audit_dimension")["risk_gap"].max().sort_values(ascending=False)
    plt.figure(figsize=(7, 4))
    grouped.plot(kind="bar")
    plt.title("Maximum graduation-risk gap by audit dimension")
    plt.xlabel("Audit dimension")
    plt.ylabel("Risk gap")
    plt.xticks(rotation=30, ha="right")
    _save(path)


def plot_bottleneck_courses(recommendations: pd.DataFrame, path: Path) -> None:
    blocked = recommendations.loc[recommendations["recommendation_status"] == "blocked"]
    if blocked.empty:
        counts = pd.Series(dtype=float)
    else:
        counts = blocked["course_id"].value_counts().head(12)
    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar")
    plt.title("Most frequent blocked course options")
    plt.xlabel("Course")
    plt.ylabel("Blocked recommendations")
    plt.xticks(rotation=45, ha="right")
    _save(path)
